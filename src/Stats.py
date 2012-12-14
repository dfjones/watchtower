import DB
import math


def updateStats(crawlRecord):
    d = {
        "url": crawlRecord['url'],
        "renderTime": crawlRecord['renderTime'],
        "serverErrors": len(crawlRecord['serverErrors']),
        "browserErrors": len(crawlRecord['browserErrors']),
        "date": crawlRecord["date"]
    }
    DB.url_stats.insert(d)


def getStatsForUrl(url):
    return DB.url_stats.find({"url": url}).sort({"date": DB.DESCENDING}).limit(100)


def getStats(results, countField):
    d = results[countField]
    return {
        "median": percentile(d, 0.5),
        "p95": percentile(d, 0.95),
        "p85": percentile(d, 0.85),
        "p75": percentile(d, 0.75),
        "avg": avg(d)
    }


def avg(N):
    return float(sum(N))/len(N)


def percentile(N, percent):
    if not N:
        return None
    N.sort()
    k = (len(N)-1) * percent
    f = math.floor(k)
    c = math.ceil(k)
    if f == c:
        return N[int(k)]
    d0 = N[int(f)] * (c-k)
    d1 = N[int(c)] * (k-f)
    return d0 + d1

