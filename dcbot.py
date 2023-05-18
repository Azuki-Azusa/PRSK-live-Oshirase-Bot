import discord
from discord.ext import tasks
import time
from live import Live
import crawler
from environs import Env
import re
from participation import Participation

# Load .env文件
env = Env()
env.read_env()

CHANNEL_ID = int(env("CHANNEL_ID"))

# Create Bot instance and set authority
intents = discord.Intents.all()
intents.members = True
client = discord.Client(intents=intents)

lives = []
participation = Participation(env("MEMBERS").split(','))

@tasks.loop(minutes=1)
async def remindTask():
    global lives
    channel = client.get_channel(CHANNEL_ID)
    now = time.time() // 60 * 60000
    if env("env") == 'development':
        now = 1684414800 // 60 * 60000
    for live in lives:
        if live.isMatched(now):
            mention_list = participation.getMentionList(live.getID())
            if len(mention_list):
                msg = ''
                for member in mention_list:
                    msg += '<@' + str(member) + '> '
                await channel.send(msg + '\n' + str(live.getID()) + ': ' + live.getName() + '：ライブの時間だよ！')

@tasks.loop(hours=8)
async def updateLives():
    global lives, participation
    lives = [Live(live) for live in crawler.getLatestLive()]
    participation.update(lives)

@client.event
async def on_ready():
    print('Logged in as {0.user}'.format(client))
    updateLives.start()
    remindTask.start()

@client.event
async def on_message(message):
    global lives, participation
    if message.author == client.user:
        return
    
    if message.channel.id == CHANNEL_ID:
        if message.content.upper().startswith('$SHOW'):
            for live in lives:
                await message.channel.send(str(live.getID()) + ': ' + live.getName() + '\n' + live.getSchedule() + '\n')
        elif match := re.match(r'\$(\d+)$', message.content):
            live_id = int(match.group(1))
            participation.participate(message.author.id, live_id)



# 启动 Discord Bot
client.run(env("BOT_TOKEN"))  # 这里的 BOT_TOKEN 是你在 Discord 应用程序中获取的 Bot API 密钥