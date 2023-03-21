import datetime

class Live():
    AF = {
        'start': 22,
        'shift': [0, 1, 2, 3, 4, 10, 14, 20, 21, 22, 23]
    }
    BD = {
        'start': 0,
        'shift': [0, 1, 2, 8, 12, 18, 19, 20, 21, 22, 23]
    }
    SP = {
        'start': 0,
        'shift': [0, 1, 2, 8, 12, 18, 19, 20, 21, 22, 23, 24, 25, 26, 32, 36, 42, 43, 44, 45, 46, 47]
    }

    def __init__(self, name, type, start_date) -> None:
        dt = datetime.datetime.strptime(start_date, '%Y/%m/%d')
        self.type = type
        self.name = name
        if type == 'AF':
            start_time = dt + datetime.timedelta(hours=22)
            self.show_time = [(start_time + datetime.timedelta(hours=shift)).strftime("%Y/%m/%d %H") for shift in self.AF['shift']]
        elif type == 'BD':
            start_time = dt
            self.show_time = [(start_time + datetime.timedelta(hours=shift)).strftime("%Y/%m/%d %H") for shift in self.BD['shift']]
        elif type == 'SP':
            start_time = dt
            self.show_time = [(start_time + datetime.timedelta(hours=shift)).strftime("%Y/%m/%d %H") for shift in self.SP['shift']]    

    def getSchedule(self):
        return ', '.join([show_time for show_time in self.show_time])

    def isMatched(self, now):
        return now in self.show_time