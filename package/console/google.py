from datetime import datetime
import logging
import re

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import requests

from package.database import MongoDB
from package.setting import GOOGLE_MAXIMUM_REQUESTS, GOOGLE_SCOPES, GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET



class GoogleSearchConsole(MongoDB):
    def __init__(self, domain, refresh_token, maximum=GOOGLE_MAXIMUM_REQUESTS):
        super().__init__()
        credentials = Credentials.from_authorized_user_info({
            "client_id": GOOGLE_CLIENT_ID,
            "client_secret": GOOGLE_CLIENT_SECRET,
            "refresh_token": refresh_token,
            "token_uri": "https://oauth2.googleapis.com/token"
        }, scopes=GOOGLE_SCOPES)

        self.remain = maximum
        self.domain = f"sc-domain:{domain}"
        self.service = re.sub(r"[^:]+:|(?:\.)[a-z]+", "", domain)

        self.inspection = build('searchconsole', 'v1', credentials=credentials).urlInspection().index()
        self.indexing = build('indexing', 'v3', credentials=credentials)
        
        self.__batch = self.indexing.new_batch_http_request(callback=self.handle_indexing_result)

    @staticmethod
    def __head_object(url):
        res = requests.head(url)
        return res.status_code < 300
    
    @staticmethod
    def __parse_slug(url):
        return re.sub("https://[^/]+", "", url)

    def __upsert_event(self, url, date=None, key="inspection"):
        slug = self.__parse_slug(url)
        if date is None:
            result = self.upsert(
                self.service,
                {"slug": slug},
                {
                    "$set": {"slug": slug},
                    "$currentDate": {key: True},
                }
            )
        else:
            result = self.upsert(
                self.service,
                {"slug": slug},
                {
                    "$set": {
                        "slug": slug,
                        key: datetime.strptime(date, "%Y-%m-%dT%H:%M:%SZ")
                    }
                }
            )

    def handle_indexing_result(self, request_id, response, exception):
        if exception is None:
            logging.info(f"INDEX {request_id}. {response['urlNotificationMetadata']['url']}")
            self.__upsert_event(response["urlNotificationMetadata"]["url"], key="request")
            return 201
        logging.error(f"{request_id}. {exception}")
    
    def url_inspection(self, url):
        if self.remain <= 0:
            logging.error("To Many Requests")
            return 429
        
        if exists:= self.find_one(self.service, {
            "slug": self.__parse_slug(url),
            "$or": [
                {"inspection": {"$exists": True}},
                {"request": {"$exists": True}},
            ]
        }):
            if "inspection" in exists:
                logging.info(f"Indexed Already ({exists['inspection']}): {url}")
                return 201
        
        if not self.__head_object(url):
            logging.error("Not Found")
            return 404

        try:
            result = self.inspection.inspect(body={
              "inspectionUrl": url,
              "siteUrl": self.domain
            }).execute()

            result = result["inspectionResult"]['indexStatusResult']    
            if result["coverageState"] in ["URL is unknown to Google", "Discovered - currently not indexed"]:
                logging.info(f"{result['coverageState']}: {url}")
                self.remain -= 1
                self.__batch.add(
                    self.indexing.urlNotifications().publish(
                        body={"url": url, "type": "URL_UPDATED"}
                    )
                )
            elif result["coverageState"] in ["Submitted and indexed"]:
                logging.warning(f"Indexed Already ({result['lastCrawlTime']}): {url}")
                self.__upsert_event(url, result['lastCrawlTime'])
            else:
                logging.warning(f"{result['coverageState']}: {url}")
            return 201

        except Exception as err:
            logging.error(f"{err}")
            return 500
    
    def execute(self):
        return self.__batch.execute()