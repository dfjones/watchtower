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
    now = mostRecentSliceEnd(slice, datetime.datetime.utcnow())
    gNext = lambda: now - slice
    for i in range(numSlices):
        next = gNext()
        r.append((next, now))
        now = next
    r.reverse()
    last = r[-1]
    r.append((last[1], datetime.datetime.utcnow()))
    return r


def mostRecentSliceEnd(slice, dt):
    nh = nearestHour(dt)
    while nh < dt:
        p = nh
        nh = nh + slice
    return p


def nearestHour(dt):
    return datetime.datetime(dt.year, dt.month, dt.day, dt.hour)


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
        "max": zeroOrMax(d),
        "median": percentile(d, 0.5),
        "p95": percentile(d, 0.95),
        "p85": percentile(d, 0.85),
        "p75": percentile(d, 0.75),
        "avg": avg(d)
    }


def zeroOrMax(d):
    if len(d) > 0:
        return max(d)
    return 0

def avg(n):
    if len(n) > 0:
        return float(sum(n))/len(n)
    return 0


def percentile(n, percent):
    if not n or len(n) == 0:
        return 0
    n.sort()
    k = (len(n)-1) * percent
    f = math.floor(k)
    c = math.ceil(k)
    if f == c:
        return n[int(k)]
    d0 = n[int(f)] * (c-k)
    d1 = n[int(c)] * (k-f)
    return d0 + d1

