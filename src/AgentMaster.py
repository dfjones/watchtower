import eventlet
import DB
import json
import re
import datetime
from eventlet.green import urllib2
from Config import config

urlRe = re.compile(config['urlFilter'])
agents = config['agents']
agentTimeout = 120

class CrawlJob(object):
    def __init__(self, agentName, agentUrl, url):
        self.agentName = agentName
        self.agentUrl = agentUrl
        self.url = url
        self.success = False


def callAgent(crawlJob):
    print "Fetching from agent: ", crawlJob.agentName, crawlJob.url
    data = "url=" + crawlJob.url
    try:
        request = urllib2.Request(crawlJob.agentUrl, data=data)
        result = urllib2.urlopen(request, timeout=agentTimeout).read()
    except:
        result = None

    return {
        "agentName": crawlJob.agentName,
        "result": result
    }


def tryAddUrlToQueue(url):
    if urlRe.match(url):
        DB.addToCrawlQueue(url)


def processAgentResponse(resp):
    if resp is not None and resp['result'] is not None:
        d = json.loads(resp['result'])
        for outgoing in d['outLinks']:
            tryAddUrlToQueue(outgoing)
        crawlRecord = {
            "url": d['url'],
            "renderTime": d['renderTime'],
            "serverErrors": d['serverErrors'],
            "browserErrors": d['browserErrors'],
            "date": datetime.datetime.utcnow()
        }
        DB.addCrawlRecord(crawlRecord)


def processCrawlJob(crawlJob):
    DB.removeFromCrawlQueue(crawlJob.url)
    resp = callAgent(crawlJob)
    processAgentResponse(resp)
    DB.addToCrawlQueue(crawlJob.url)
    crawlJob.success = True
    return crawlJob


running = True
if __name__ == '__main__':
    pool = eventlet.GreenPool(size=4*len(agents))

    DB.clearCrawlQueue()
    DB.ensure_indexes()
    DB.addToCrawlQueue(config['startUrl'])

    while running:
        jobs = []
        for crawlDoc in DB.getCrawlQueue():
            for agent in agents:
                jobs.append(CrawlJob(agent['name'], agent['url'], crawlDoc['url']))
        for crawlJob in pool.imap(processCrawlJob, jobs):
            if not crawlJob.success:
                print "Error processing Crawl Job: ", crawlJob








