from flask import Flask, request, jsonify, json
import subprocess
from Config import config

app = Flask(__name__)

@app.route("/crawlUrl", methods=['POST'])
def crawlUrl():
    url = request.form['url']
    res = subprocess.check_output([config['agent'], url], cwd=config['agentDir'])
    jsonRes = json.loads(res)
    return jsonify(jsonRes)

if __name__ == '__main__':
    app.run(debug=True)


