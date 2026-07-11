"""活动数据。"""

import datetime


class Event:
    """活动对象。"""

    def __init__(self, event: dict) -> None:
        self.event = event

    def getSchedule(self):
        """返回日程文本。"""
        start_at = datetime.datetime.fromtimestamp(self.event['startAt'] // 1000)
        aggregate_at = datetime.datetime.fromtimestamp(self.event['aggregateAt'] // 1000)
        return str(start_at) + ' ~ ' + str(aggregate_at)

    def isMatched(self, now, hour):
        """判断时间是否匹配。"""
        return now == ((self.event['aggregateAt'] + 1000) // 60000 * 60000 - hour * 60 * 60 * 1000)

    def getName(self):
        """返回名称。"""
        return self.event['name']

    def getID(self):
        """返回 ID。"""
        return self.event['id']
