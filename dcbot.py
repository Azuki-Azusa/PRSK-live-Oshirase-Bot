import discord
from discord.ext import tasks
import time
from live import Live
from event import Event
import crawler
from environs import Env
import re
from participation import Participation
from rankLogQueue import RankLogQueue

# Load .env文件
env = Env()
env.read_env()

CHANNEL_ID_REMIND = int(env("CHANNEL_ID_REMIND"))
CHANNEL_ID_PRSK = int(env("CHANNEL_ID_PRSK"))
CHANNEL_ID_RANK = int(env("CHANNEL_ID_RANK"))
DELAY = int(env("DELAY"))

# Create Bot instance and set authority
intents = discord.Intents.all()
intents.members = True
client = discord.Client(intents=intents)

lives = []
event = {}
participation = Participation(env("MEMBERS").split(','))
border_rankings_save_queue = RankLogQueue(delay=DELAY)
character_rankings_save_queue = {}

# 每分钟执行一次
@tasks.loop(minutes=1)
async def remindTask():
    global lives, event
    channel_remind = client.get_channel(CHANNEL_ID_REMIND)
    channel_prsk = client.get_channel(CHANNEL_ID_PRSK)
    # 取得当前时间的整分级时间戳
    now = time.time() // 60 * 60000
    if env("env") == 'development':
        now = 1736409600 // 60 * 60000

    # 提醒live
    for live in lives:
        if live.isMatched(now):
            mention_list = participation.getMentionList(live.getID())
            if len(mention_list):
                msg = ''
                for member in mention_list:
                    msg += '<@' + str(member) + '> '
                await channel_remind.send(msg + '\n' + str(live.getID()) + ': ' + live.getName() + '：ライブの時間だよ！')

    # 提醒event
    for hour in range(1, 4):
        if event.isMatched(now, hour):
            await channel_prsk.send(str(event.getID()) + ': ' + event.getName() + '：終了' + str(hour) + '時間前！')
            break

@tasks.loop(minutes=DELAY)
async def updateRank():
    global border_rankings_save_queue, character_rankings_save_queue, DELAY
    border_rankings_result, character_rankings_result = crawler.getCurrentRank()
    if len(border_rankings_result) > 0:
        border_rankings_save_queue.add(border_rankings_result)
    for character_id in character_rankings_result:
        if character_id not in character_rankings_save_queue:
            character_rankings_save_queue[character_id] = RankLogQueue(delay=DELAY)
        character_rankings_save_queue[character_id].add(character_rankings_result[character_id])
            

@tasks.loop(hours=8)
async def updateLives():
    global lives, participation
    lives = [Live(live) for live in crawler.getLatestLive()]
    participation.update(lives)

@tasks.loop(hours=24)
async def updateEvent():
    global event
    event = Event(crawler.getCurrentEvent())

@client.event
async def on_ready():
    print('Logged in as {0.user}'.format(client))
    updateLives.start()
    updateEvent.start()
    remindTask.start()
    updateRank.start()

@client.event
async def on_message(message):
    global lives, event, participation, border_rankings_save_queue, character_rankings_save_queue, DELAY
    if message.author == client.user:
        return
    
    if message.channel.id == CHANNEL_ID_REMIND:
        if message.content.upper().startswith('SHOW'):
            await message.channel.send('■ Live:\n')
            for live in lives:
                await message.channel.send(str(live.getID()) + ': ' + live.getName() + '\n' + live.getSchedule() + '\n')
            await message.channel.send('\n■ Event:\n')
            await message.channel.send(str(event.getID()) + ': ' + event.getName() + '\n' + event.getSchedule() + '\n')

        elif match := re.match(r'(\d+)$', message.content):
            live_id = int(match.group(1))
            participation.participate(message.author.id, live_id)
    
    if message.channel.id == CHANNEL_ID_RANK:
        if message.content.upper().startswith('SCORE_ALL'):
            await message.channel.send("MAIN: " + str(border_rankings_save_queue.get()[-1]))
            for rank in character_rankings_save_queue:
                await message.channel.send(str(rank) + ": " + str(character_rankings_save_queue[rank].get()[-1]))

        elif message.content.upper().startswith('SCORE_MAIN'):
            image_buf = border_rankings_save_queue.getImageOfScore()
            if image_buf: 
                file = discord.File(fp=image_buf, filename='table.png')
                await message.channel.send(file=file)
            else:
                await message.channel.send("Data is not enough. Please wait " + str(DELAY) + "min.")

        elif match := re.match(r'SCORE\_(\d+)$', message.content):
            character_id = int(match.group(1))
            if character_id in character_rankings_save_queue:
                border_rankings_cha_queue = character_rankings_save_queue[character_id]
                image_buf = border_rankings_cha_queue.getImageOfScore()
                if image_buf: 
                    file = discord.File(fp=image_buf, filename='table.png')
                    await message.channel.send(file=file)
                else:
                    await message.channel.send("Data is not enough. Please wait " + str(DELAY) + "min.")
            else:
                await message.channel.send("Unknown Character ID")



# 启动 Discord Bot
client.run(env("BOT_TOKEN"))  # 这里的 BOT_TOKEN 是你在 Discord 应用程序中获取的 Bot API 密钥