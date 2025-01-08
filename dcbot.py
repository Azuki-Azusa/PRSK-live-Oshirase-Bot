import discord
from discord.ext import tasks
import time
from live import Live
from event import Event
import crawler
from environs import Env
import re
from participation import Participation

# Load .env文件
env = Env()
env.read_env()

CHANNEL_ID_REMIND = int(env("CHANNEL_ID_REMIND"))
CHANNEL_ID_PRSK = int(env("CHANNEL_ID_PRSK"))

# Create Bot instance and set authority
intents = discord.Intents.all()
intents.members = True
client = discord.Client(intents=intents)

lives = []
event = {}
participation = Participation(env("MEMBERS").split(','))

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

@client.event
async def on_message(message):
    global lives, event, participation
    if message.author == client.user:
        return
    
    if message.channel.id == CHANNEL_ID_REMIND:
        if message.content.upper().startswith('$SHOW'):
            await message.channel.send('■ Live:\n')
            for live in lives:
                await message.channel.send(str(live.getID()) + ': ' + live.getName() + '\n' + live.getSchedule() + '\n')
            await message.channel.send('\n■ Event:\n')
            await message.channel.send(str(event.getID()) + ': ' + event.getName() + '\n' + event.getSchedule() + '\n')

        elif match := re.match(r'\$(\d+)$', message.content):
            live_id = int(match.group(1))
            participation.participate(message.author.id, live_id)



# 启动 Discord Bot
client.run(env("BOT_TOKEN"))  # 这里的 BOT_TOKEN 是你在 Discord 应用程序中获取的 Bot API 密钥