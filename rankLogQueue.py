from collections import deque

class RankLogQueue:
    def __init__(self, max_length=7, delay=10):
        self.queue = deque(maxlen=max_length)
        self.delay = delay

    def add(self, item):
        self.queue.append(item)

    def get(self):
        return list(self.queue)
    
    def getSpeedPerhour(self):
        length = len(self.queue)
        result = {}
        if length > 1:
            for rank in self.queue[0]:
                result[rank] = (self.queue[-1][rank] - self.queue[0][rank])/((length-1)*self.delay)*60
        return result


    def __repr__(self):
        return repr(list(self.queue))
