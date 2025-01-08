import datetime

class Live():
    live = {}

    def __init__(self, live: dict) -> None:
        self.live = live

    def getSchedule(self):
        return '\n'.join([str(datetime.datetime.fromtimestamp(schedule['startAt']//1000)) + ' ~ ' + str(datetime.datetime.fromtimestamp(schedule['endAt']//1000)) for schedule in self.live['virtualLiveSchedules']])
    
    def getScheduleTimestamp(self):
        return self.live['virtualLiveSchedules']

    def isMatched(self, now):
        return now in [schedule['startAt'] // 60000 * 60000 for schedule in self.live['virtualLiveSchedules']]

    def getName(self):
        return self.live['name']

    def getID(self):
        return self.live['id']