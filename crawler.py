import requests
import json
import time
from environs import Env

# Load .env文件
env = Env()
env.read_env()

VIRTUAL_LIVE_API = env("VIRTUAL_LIVE_API")
CURRENT_EVENT_API = env("CURRENT_EVENT_API")

GAME_API_URL = env("GAME_API_URL")
GAME_API_PATH = env("GAME_API_PATH")
GAME_API_RANK_PATH1 = env("GAME_API_RANK_PATH1")
GAME_API_RANK_PATH2 = env("GAME_API_RANK_PATH2")
GAME_API_HEADER = env("GAME_API_HEADER")
GAME_API_TOKEN = env("GAME_API_TOKEN")

def getLatestLive():
    url = VIRTUAL_LIVE_API
    response = requests.get(url)
    virtual_lives = json.loads(response.text)
    current_time = time.time() * 1000
    current_lives = [live for live in virtual_lives if live['startAt'] < current_time and live['endAt'] > current_time and live['virtualLiveType'] != 'beginner']
    return current_lives

def getCurrentEvent():
    url = CURRENT_EVENT_API
    response = requests.get(url)
    events = json.loads(response.text)
    current_event = events[-1]
    return current_event

def getCurrentRank():
    current_event = getCurrentEvent()
    event_id = str(current_event["id"])
    url = GAME_API_URL + GAME_API_PATH + GAME_API_RANK_PATH1 + "/" + event_id + GAME_API_RANK_PATH2
    headers = {
        GAME_API_HEADER: GAME_API_TOKEN
    }
    response = requests.get(url, headers=headers)
    ranking_border = json.loads(response.text)

    border_rankings = ranking_border["borderRankings"] if ranking_border["borderRankings"] else False
    user_world_bloom_chapter_ranking_borders = ranking_border["userWorldBloomChapterRankingBorders"] if ranking_border["userWorldBloomChapterRankingBorders"] else []
    border_rankings_result = {user["rank"]: user["score"] for user in border_rankings}
    character_rankings_result = {}
    for character in user_world_bloom_chapter_ranking_borders:
        character_id = character["gameCharacterId"]
        character_rank = {user["rank"]: user["score"] for user in character["borderRankings"]}
        character_rankings_result[character_id] = character_rank
    
    return border_rankings_result, character_rankings_result