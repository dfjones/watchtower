from flask import Flask, render_template, request, jsonify, json
import datetime
import DB
import Stats
from Config import config

app = Flask(__name__)


@app.route('/')
def dashboard():
    return render_template('dashboard.html', title="Dashboard")


@app.route('/crawlLog')
def crawlLog():
    return render_template('crawlLog.html', title="Crawl Log", data=getCrawlLogData())


@app.route('/about')
def about():
    return render_template('about.html', title="About")


@app.route('/dashboard/stats')
def dashboardStats():
    data = {
        "stats": getDashboardData()
    }
    return jsonify(data)


def getCrawlLogData():
    data = {
        "errorRows": [],
        "newestRows": []
    }

    errorRecords = DB.getCrawlRecordsWithErrors()
    crawlRecords = DB.getNewestCrawlRecords(limit=100)

    def pr(rows, crawlRecords):
        seenUrls = {}
        for cr in crawlRecords:
            dashboardRow = {
                "url": cr['url'],
                "renderTime": cr['renderTime'],
                "serverErrors": len(cr['serverErrors']),
                "browserErrors": len(cr['browserErrors']),
                "errorsPresent": cr['errorsPresent']
            }
            if dashboardRow['url'] not in seenUrls:
                rows.append(dashboardRow)
                seenUrls[dashboardRow['url']] = True
    pr(data['newestRows'], crawlRecords)
    pr(data['errorRows'], errorRecords)
    return data


def getDashboardData():
    stats = Stats.getStatsSummary(datetime.timedelta(minutes=5), 40)
    return stats


if __name__ == '__main__':
    app.run(debug=True)
