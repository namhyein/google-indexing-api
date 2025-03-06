from package.database import MongoDB
import logging
import json
import re

from pymongo import UpdateOne
import requests

from package.setting import BING_MAXIMUM_REQUESTS, BING_MAXIMUM_SIZE


class BingIndexnow(MongoDB):
    def __init__(self, domain, token, maximum=BING_MAXIMUM_REQUESTS):
        super().__init__()

        self.domain = domain
        self.service = re.sub(r"[^:]+:|(?:\.)[a-z]+", "", domain)
        
        self.remain = maximum
        self.__credentials = token
        
        self.__batch = []
    
    @property
    def batch_size(self):
        return len(self.__batch)
    
    @staticmethod
    def __head_object(url):
        res = requests.head(url)
        return res.status_code < 300
    
    @staticmethod
    def __parse_slug(url):
        return re.sub("https://[^/]+", "", url)
    
    def __generate_output(self, obj):
        return [
            UpdateOne(
                {"slug": self.__parse_slug(slug)},
                {
                
                    "$set": {"slug": slug},
                    "$currentDate": {"indexnow": True}
                },
                upsert=True
            )
            for slug in obj
        ]

    def url_inspection(self, url):
        if self.remain <= 0:
            logging.error("To Many Requests")
            return 429

        if exists:= self.find_one(self.service, {"slug": self.__parse_slug(url)}):
            if "indexnow" in exists:
                logging.info(f"Indexed Already ({exists['indexnow']}): {url}")
                return 201
        
        if not self.__head_object(url):
            logging.error("Not Found")
            return 404
        
        logging.info(f"Add Indexing Request: {url}")
        if self.batch_size >= BING_MAXIMUM_SIZE:
            self.execute()
        
        self.__batch.append(url)
        return 201
    
    def execute(self):
        for idx in range(0, self.batch_size, BING_MAXIMUM_SIZE):
            try:
                urlset = self.__batch[idx:idx+BING_MAXIMUM_SIZE]
                res = requests.post(
                    "https://www.bing.com/indexnow",
                    json={
                        "key": self.__credentials,
                        "urlList": urlset,
                        "host": f"https://www.{self.domain}",
                        "keyLocation": f"https://www.{self.domain}/indexnow.txt",
                    },
                    headers={
                        "Content-Type": "application/json; charset=utf-8"
                    }
                )
                res.raise_for_status()
                logging.info(f"Bing Indexnow: {res.text}")
                self.bulk_write(
                    self.service,
                    self.__generate_output(urlset)
                )
                
            except Exception as err:
                logging.error(err)
                break
   
        self.__batch = []