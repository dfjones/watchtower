from Config import config
import datetime
from pymongo import MongoClient, DESCENDING, ASCENDING

connection = MongoClient(config['mongo'][0], config['mongo'][1])

db = connection['Watchtower']
crawl_queue = db.crawl_queue
crawl_records = db.crawl_records

def ensure_indexes():
    crawl_queue.create_index([("url", ASCENDING), ("date", ASCENDING)])
    crawl_records.create_index([("url", ASCENDING), ("date", DESCENDING)])
    crawl_records.create_index([("date", DESCENDING)])

def addToCrawlQueue(url, date=datetime.datetime.utcnow()):
    if not inCrawlQueue(url):
        d = {
            "url": url,
            "date": date
        }
        return crawl_queue.insert(d)
    return None

def inCrawlQueue(url):
    return crawl_queue.find({"url": url}).count() > 0

def removeFromCrawlQueue(url):
    return crawl_queue.remove({"url": url})

def getCrawlQueue():
    return crawl_queue.find().sort("date")

def clearCrawlQueue():
    return crawl_queue.drop()

def addCrawlRecord(record):
    return crawl_records.insert(record)

def getCrawlRecords():
    pass

