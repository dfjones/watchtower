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
    seenUrls = {}
    data = {
        "rows": []
    }
    crawlRecords = DB.getNewestCrawlRecords(limit=50)
    for cr in crawlRecords:
        dashboardRow = {
            "url": cr['url'],
            "renderTime": cr['renderTime'],
            "serverErrors": len(cr['serverErrors']),
            "browserErrors": len(cr['browserErrors'])
        }
        if dashboardRow['url'] not in seenUrls:
            if dashboardRowHasErrors(dashboardRow):
                dashboardRow['warn'] = True
            data['rows'].append(dashboardRow)
            seenUrls[dashboardRow['url']] = True
    return data


def dashboardRowHasErrors(dr):
    return dr['serverErrors'] > 0 or dr['browserErrors'] > 0





if __name__ == '__main__':
    app.run(debug=True)
