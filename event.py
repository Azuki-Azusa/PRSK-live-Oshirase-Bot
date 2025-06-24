import datetime

class Event():
    event = {}

    def __init__(self, event: dict) -> None:
        self.event = event

    def getSchedule(self):
        return str(datetime.datetime.fromtimestamp(self.event['startAt']//1000)) + ' ~ ' + str(datetime.datetime.fromtimestamp(self.event['aggregateAt']//1000))
    
    def isMatched(self, now, hour):
        return now == ((self.event['aggregateAt'] + 1000) // 60000 * 60000 - hour * 60 * 60 * 1000)

    def getName(self):
        return self.event['name']

    def getID(self):
        return self.event['id']