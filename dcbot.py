"""Discord bot 入口。"""

import datetime
import re
import time
from dataclasses import dataclass, field
from zoneinfo import ZoneInfo

import discord
from discord.ext import tasks

import crawler
from config import load_config
from event import Event
from live import Live
from participation import Participation
from rankLogQueue import RankLogQueue

CONFIG = load_config()

CHANNEL_ID_REMIND = CONFIG.channel_id_remind
CHANNEL_ID_PRSK = CONFIG.channel_id_prsk
CHANNEL_ID_RANK = CONFIG.channel_id_rank
DELAY = CONFIG.delay
LOCAL_TZ = ZoneInfo("Asia/Tokyo")

LIVE_REMINDER_SUFFIX = '：ライブの時間だよ！'
EVENT_REMINDER_TEMPLATE = '：終了{hour}時間前！'
DAILY_LIVE_REMINDER = 'チャレンジライブを忘れずに！'
DATA_NOT_READY_MESSAGE = "Data is not ready yet. Please wait a moment."
RANK_DATA_NOT_ENOUGH_MESSAGE = "Data is not enough. Please wait {delay}min."
UNKNOWN_CHARACTER_MESSAGE = "Unknown Character ID"
INTERNAL_ERROR_MESSAGE = "Internal error. Please check bot logs."


@dataclass
class BotState:
    """Bot 共享状态。"""

    lives: list = field(default_factory=list)
    event: object = None
    participation: Participation = field(default_factory=lambda: Participation(CONFIG.members))
    border_rankings_save_queue: RankLogQueue = field(default_factory=lambda: RankLogQueue(delay=DELAY))
    character_rankings_save_queue: dict = field(default_factory=dict)

    def has_event_ready(self):
        """判断活动数据是否就绪。"""
        return bool(self.event and hasattr(self.event, 'isMatched'))

    def has_border_rank_data(self):
        """判断主榜线是否有数据。"""
        return len(self.border_rankings_save_queue.get()) > 0

    def get_character_rank_queue(self, character_id):
        """获取角色排名队列。"""
        if character_id not in self.character_rankings_save_queue:
            self.character_rankings_save_queue[character_id] = RankLogQueue(delay=DELAY)
        return self.character_rankings_save_queue[character_id]


def create_intents():
    """创建 Discord intents。"""
    if hasattr(discord.Intents, "default"):
        intents = discord.Intents.default()
    else:
        intents = discord.Intents.all()
    intents.message_content = True
    intents.members = True
    return intents


client = discord.Client(intents=create_intents())
state = BotState()


def format_mentions(member_ids):
    """格式化 Discord mention。"""
    return ' '.join(f'<@{member_id}>' for member_id in member_ids)


def parse_live_id_command(content):
    """解析 Live ID 命令。"""
    match = re.match(r'\d+$', content)
    if not match:
        return None
    return int(match.group(0))


def parse_character_score_command(content):
    """解析角色分数命令。"""
    match = re.match(r'SCORE_(\d+)$', content.upper())
    if not match:
        return None
    return int(match.group(1))


def build_live_reminder_message(live, mention_list):
    """构建 Live 提醒消息。"""
    mention_text = format_mentions(mention_list)
    return mention_text + '\n' + str(live.getID()) + ': ' + live.getName() + LIVE_REMINDER_SUFFIX


def build_event_reminder_message(event, hour):
    """构建活动提醒消息。"""
    return str(event.getID()) + ': ' + event.getName() + EVENT_REMINDER_TEMPLATE.format(hour=hour)


def build_schedule_message():
    """构建日程状态消息。"""
    lines = ['■ Live:']
    if state.lives:
        for live in state.lives:
            lines.append(str(live.getID()) + ': ' + live.getName() + '\n' + live.getSchedule())
    else:
        lines.append(DATA_NOT_READY_MESSAGE)

    lines.append('\n■ Event:')
    if state.has_event_ready():
        lines.append(str(state.event.getID()) + ': ' + state.event.getName() + '\n' + state.event.getSchedule())
    else:
        lines.append(DATA_NOT_READY_MESSAGE)
    return '\n'.join(lines)


def get_current_minute_ms():
    """获取当前分钟时间戳。"""
    if CONFIG.is_development:
        # 固定时间戳可以让开发环境中的提醒行为保持可预测。?
        return 1736409600 // 60 * 60000
    return time.time() // 60 * 60000


def has_event_ready():
    """判断活动数据是否就绪。"""
    return state.has_event_ready()


async def send_score_image(message, rank_queue):
    """发送排名图片。"""
    image_buf = rank_queue.getImageOfScore()
    if image_buf:
        file = discord.File(fp=image_buf, filename='table.png')
        await message.channel.send(file=file)
    else:
        await message.channel.send(RANK_DATA_NOT_ENOUGH_MESSAGE.format(delay=DELAY))


async def handle_remind_channel_message(message):
    """处理提醒频道消息。"""
    if message.content.upper().startswith('SHOW'):
        await message.channel.send(build_schedule_message())
        return

    live_id = parse_live_id_command(message.content)
    if live_id is not None:
        state.participation.participate(message.author.id, live_id)


async def handle_rank_channel_message(message):
    """处理排名频道消息。"""
    content = message.content.upper()

    if content.startswith('SCORE_ALL'):
        if not state.has_border_rank_data():
            await message.channel.send(DATA_NOT_READY_MESSAGE)
            return
        await message.channel.send("MAIN: " + str(state.border_rankings_save_queue.get()[-1]))
        for rank in state.character_rankings_save_queue:
            await message.channel.send(str(rank) + ": " + str(state.character_rankings_save_queue[rank].get()[-1]))
        return

    if content.startswith('SCORE_MAIN'):
        await send_score_image(message, state.border_rankings_save_queue)
        return

    character_id = parse_character_score_command(message.content)
    if character_id is None:
        return

    if character_id not in state.character_rankings_save_queue:
        await message.channel.send(UNKNOWN_CHARACTER_MESSAGE)
        return

    await send_score_image(message, state.character_rankings_save_queue[character_id])


@tasks.loop(minutes=1)
async def remindTask():
    """定时发送提醒。"""
    if not has_event_ready():
        return

    channel_remind = client.get_channel(CHANNEL_ID_REMIND)
    channel_prsk = client.get_channel(CHANNEL_ID_PRSK)
    if channel_remind is None or channel_prsk is None:
        print("[WARN] reminder channels are not ready")
        return

    now = get_current_minute_ms()

    for live in state.lives:
        if live.isMatched(now):
            mention_list = state.participation.getMentionList(live.getID())
            if mention_list:
                await channel_remind.send(build_live_reminder_message(live, mention_list))

    for hour in [0.5, 1, 2, 3]:
        if state.event.isMatched(now, hour):
            await channel_prsk.send(build_event_reminder_message(state.event, hour))
            break


@tasks.loop(time=datetime.time(hour=23, minute=0, tzinfo=LOCAL_TZ))
async def remindDaily():
    """发送每日提醒。"""
    try:
        channel_prsk = client.get_channel(CHANNEL_ID_PRSK)
        if channel_prsk is None:
            return
        if not (await crawler.hasCurrentLive()):
            await channel_prsk.send(DAILY_LIVE_REMINDER)
    except Exception as e:
        print(f"[ERROR] remindDaily failed: {e}")


@tasks.loop(minutes=DELAY)
async def updateRank():
    """更新排名数据。"""
    try:
        border_rankings_result, character_rankings_result = await crawler.getCurrentRank()
        if border_rankings_result:
            state.border_rankings_save_queue.add(border_rankings_result)
        for character_id in character_rankings_result:
            state.get_character_rank_queue(character_id).add(character_rankings_result[character_id])
    except Exception as e:
        print(f"[ERROR] updateRank failed: {e}")


@tasks.loop(hours=8)
async def updateLives():
    """更新 Live 数据。"""
    try:
        latest = await crawler.getLatestLive()
        state.lives = [Live(live) for live in latest]
        state.participation.update(state.lives)
    except Exception as e:
        print(f"[ERROR] updateLives failed: {e}")


@tasks.loop(hours=24)
async def updateEvent():
    """更新活动数据。"""
    try:
        current = await crawler.getCurrentEvent()
        if current:
            state.event = Event(current)
    except Exception as e:
        print(f"[ERROR] updateEvent failed: {e}")


@client.event
async def on_ready():
    """Discord 就绪后启动任务。"""
    print('Logged in as {0.user}'.format(client))
    if not updateLives.is_running():
        updateLives.start()
    if not updateEvent.is_running():
        updateEvent.start()
    if not remindTask.is_running():
        remindTask.start()
    if not updateRank.is_running():
        updateRank.start()
    if not remindDaily.is_running():
        remindDaily.start()


@client.event
async def on_message(message):
    """分发 Discord 消息。"""
    try:
        if message.author == client.user:
            return

        if message.channel.id == CHANNEL_ID_REMIND:
            await handle_remind_channel_message(message)
        elif message.channel.id == CHANNEL_ID_RANK:
            await handle_rank_channel_message(message)
    except Exception as e:
        print(f"[ERROR] on_message failed: {e}")
        await message.channel.send(INTERNAL_ERROR_MESSAGE)


def main():
    """启动 bot。"""
    client.run(CONFIG.bot_token)


if __name__ == "__main__":
    main()
