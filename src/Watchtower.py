from flask import Flask, render_template, request, jsonify, json
import DB
import Stats
from Config import config

app = Flask(__name__)

@app.route('/')
def dashboard():
    return render_template('dashboard.html', title="Dashboard", data=getDashboardData())

@app.route('/about')
def about():
    return render_template('about.html', title="About")



def getDashboardData():
    data = {
        "errorRows": [],
        "newestRows": []
    }

    errorRecords = DB.getCrawlRecordsWithErrors()
    crawlRecords = DB.getNewestCrawlRecords(limit=50)

    def pr(rows, crawRecords):
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


if __name__ == '__main__':
    app.run(debug=True)
