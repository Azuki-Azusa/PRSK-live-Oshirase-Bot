"""Live 数据。"""

import datetime


class Live:
    """Live 对象。"""

    def __init__(self, live: dict) -> None:
        self.live = live

    def getSchedule(self):
        """返回日程文本。"""
        return '\n'.join([
            str(datetime.datetime.fromtimestamp(schedule['startAt'] // 1000))
            + ' ~ '
            + str(datetime.datetime.fromtimestamp(schedule['endAt'] // 1000))
            for schedule in self.live['virtualLiveSchedules']
        ])

    def getScheduleTimestamp(self):
        """返回原始日程。"""
        return self.live['virtualLiveSchedules']

    def isMatched(self, now):
        """判断时间是否匹配。"""
        return now in [schedule['startAt'] // 60000 * 60000 for schedule in self.live['virtualLiveSchedules']]

    def getName(self):
        """返回名称。"""
        return self.live['name']

    def getID(self):
        """返回 ID。"""
        return self.live['id']
