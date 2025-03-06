import logging
from pymongo import MongoClient, ReadPreference, UpdateOne

from package.setting import DATABASE, HOSTNAME, PASSWORD, USERNAME


class MongoDB:
    def __init__(self):
        self.__client = MongoClient(
            f"mongodb+srv://{USERNAME}:{PASSWORD}@{HOSTNAME}/{DATABASE}",
            read_preference=ReadPreference.SECONDARY_PREFERRED
        )

    def __del__(self):
        self.__client.close()

    def find_one(self, collection, query):
        logging.debug(f"Query {DATABASE}.{collection}: {query}")

        item = self.__client[DATABASE][collection].find_one(query)
        return item if item else {}
    
    def upsert(self, collection, query, update):
        result = self.__client[DATABASE][collection].update_one(query, update, upsert=True)
        # logging.debug(f"Upsert {DATABASE}.{collection}: {query} -> {update}")
        # logging.info(f"{result.raw_result}")
        return result.raw_result
    
    def add_upsert_one(self, collection, query, update):
        # logging.debug(f"Upsert {DATABASE}.{collection}: {query} -> {update}")
        self.request.append(
            UpdateOne(query, update, upsert=True)
        )
    
    def bulk_write(self, collection, requests):
        if len(request) <= 0:
            return {}
        
        result = self.__client[DATABASE][collection].bulk_write(request)
        logging.info(f"Bulk Write: {result.bulk_api_result}")
