import json

import pymongo
from Zhihu.settings import *
class MongoPipeline(object):
    def open_spider(self, spider):
        self.client = pymongo.MongoClient(host=MONGO_URL, port=MONGO_PROT)
        self.collection = self.client[MONGO_DATABASE]['user']

    def process_item(self, item, spider):
        self.collection.update({'url_token': item['url_token']}, {'$set': item}, True)
        return item

    def close_spider(self, spider):
        self.client.close()

class JsonPipeline(object):
    def open_spider(self, spider):
        self.file = open("users.json", "w")

    def process_item(self, item, spider):
        content = json.dumps(dict(item), ensure_ascii=False) + "\n"
        self.file.write(content)
        return item

    def close_spider(self, spider):
        self.file.close()