from collections import deque
import matplotlib.pyplot as plt
import io

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

    def getImageOfScore(self): 
        result = [["RANK", "CURRENT", "SPEED"]]
        speedPerhour = self.getSpeedPerhour()
        if len(speedPerhour) != 0: 
            for rank in self.queue[-1]:
                result.append([str(rank),"{:,}".format(int(self.queue[-1][rank])),"{:,}".format(int(speedPerhour[rank]))])
            fig, ax = plt.subplots()
            ax.axis("off")
            table = ax.table(cellText=result, loc='center', cellLoc='center')
            table.set_fontsize(12)
            table.scale(1, 1.5)

            buf = io.BytesIO()
            plt.savefig(buf, format='png', bbox_inches='tight')
            buf.seek(0)

            return buf
        else:
            return False

    def __repr__(self):
        return repr(list(self.queue))
