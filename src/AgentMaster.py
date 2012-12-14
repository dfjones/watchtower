import eventlet
import DB
import Stats
import json
import re
import datetime
from eventlet.green import urllib2
from Config import config

urlRe = re.compile(config['urlFilter'])
agents = config['agents']
agentTimeout = 300

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
    except Exception as e:
        print "Error fetching from agent: ", crawlJob.agentName, crawlJob.url
        print "Error was: ", e
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
        updateCrawlRecordErrors(crawlRecord)
        DB.addCrawlRecord(crawlRecord)
        Stats.updateStats(crawlRecord)

def updateCrawlRecordErrors(cr):
    cr['errorsPresent'] = False
    if len(cr['serverErrors']) > 0 or len(cr['browserErrors']) > 0:
        cr['errorsPresent'] = True


def processCrawlJob(crawlJob):
    DB.removeFromCrawlQueue(crawlJob.url)
    resp = callAgent(crawlJob)
    processAgentResponse(resp)
    DB.addToCrawlQueue(crawlJob.url)
    crawlJob.success = True
    return crawlJob


running = True
if __name__ == '__main__':
    pool = eventlet.GreenPool(size=10*len(agents))

    DB.ensure_indexes()
    DB.addToCrawlQueue(config['startUrl'])

    while running:
        for crawlDoc in DB.getCrawlQueue():
            for agent in agents:
                job = CrawlJob(agent['name'], agent['url'], crawlDoc['url'])
                pool.spawn(processCrawlJob, job)
