import DB
import datetime
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


def getStatsSummary(slice, numSlices):
    dateRanges = genDateRanges(slice, numSlices)
    out = []
    for s,e in dateRanges:
        rs = [x for x in getStatsByDateRange(s,e)]
        out.append(getStatsPackage(rs))
    return out


def getStatsPackage(rawStats):
    stats = {
        "renderTime": getStats(rawStats, 'renderTime'),
        "serverErrors": getStats(rawStats, 'serverErrors'),
        "browserErrors": getStats(rawStats, 'browserErrors')
    }
    return stats


def genDateRanges(slice, numSlices):
    r = []
    now = datetime.datetime.now()
    gNext = lambda: now - slice
    for i in range(numSlices):
        next = gNext()
        r.append((next, now))
        now = next
    r.reverse()
    return r


def getStatsByDateRange(start, end):
    return DB.url_stats.find({"date": {"$gte": start, "$lt": end}}).sort("date", DB.ASCENDING)


def getAllStats(limit=200):
    return DB.url_stats.find().sort("date", DB.DESCENDING).limit(limit)


def getStatsForUrl(url, limit=100):
    return DB.url_stats.find({"url": url}).sort("date", DB.DESCENDING).limit(limit)


def getStats(results, countField):
    d = [r[countField] for r in results]
    return {
        "count": len(d),
        "max": max(d),
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

