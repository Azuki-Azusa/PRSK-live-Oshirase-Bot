import discord
from discord.ext import tasks
import time
from live import Live
import crawler
from environs import Env

# 加载.env文件
env = Env()
env.read_env()

CHANNEL_ID = int(env("CHANNEL_ID"))

# 创建 Bot 实例并指定所需的权限
intents = discord.Intents.all()
intents.members = True
client = discord.Client(intents=intents)

lives = []

@tasks.loop(minutes=1)
async def remindTask():
    global lives
    channel = client.get_channel(CHANNEL_ID)
    now = time.time() // 60 * 60000
    if env("env") == 'development':
        now = 1683558000 // 60 * 60000
    for live in lives:
        if live.isMatched(now):
            await channel.send(live.getName() + '：ライブの時間だよ！')

@tasks.loop(hours=8)
async def updateLives():
    global lives
    lives = [Live(live) for live in crawler.getLatestLive()]

# 在 Discord Bot 启动时执行的操作
@client.event
async def on_ready():
    print('Logged in as {0.user}'.format(client))
    updateLives.start()
    remindTask.start()

@client.event
async def on_message(message):
    global lives
    if message.author == client.user:
        return
    
    if message.channel.id == CHANNEL_ID:
        if message.content.upper().startswith('$SHOW'):
            for live in lives:
                await message.channel.send(live.getName() + '\n' + live.getSchedule() + '\n')


# 启动 Discord Bot
client.run(env("BOT_TOKEN"))  # 这里的 BOT_TOKEN 是你在 Discord 应用程序中获取的 Bot API 密钥