import requests
import json
import time

def getLatestLive():
    url = "https://sekai-world.github.io/sekai-master-db-diff/virtualLives.json"
    response = requests.get(url)
    virtual_lives = json.loads(response.text)
    current_time = time.time() * 1000
    current_lives = [live for live in virtual_lives if live['startAt'] < current_time and live['endAt'] > current_time and live['virtualLiveType'] != 'beginner']
    return current_lives