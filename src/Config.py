config = {
    "agentDir": "../scripts/agent",
    "agent": "./run-phantom-agent",
    "agents": [
        {
            "name": "New York",
            "url": "http://localhost:8000/crawl"
        },
        {
            "name": "San Francisco",
            "url": "http://localhost:8000/crawl"
        }
    ],
    "startUrl": "http://www.squarespace.com",
    "urlFilter": '.*squarespace.com.*',
    "urlExcludes": [
        "answers.squarespace.com"
    ],
    "mongo": ('localhost', 27017)
}