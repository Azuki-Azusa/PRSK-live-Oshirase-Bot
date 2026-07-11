"""排名队列。"""

from collections import deque
import io

import matplotlib.pyplot as plt


class RankLogQueue:
    """排名快照队列。"""

    def __init__(self, max_length=7, delay=10):
        self.queue = deque(maxlen=max_length)
        self.delay = delay

    def add(self, item):
        """追加一份快照。"""
        self.queue.append(item)

    def get(self):
        """返回队列内容。"""
        return list(self.queue)

    def getSpeedPerhour(self):
        """计算每小时涨分。"""
        length = len(self.queue)
        result = {}
        if length > 1:
            common_ranks = set(self.queue[0]) & set(self.queue[-1])
            for rank in common_ranks:
                delta = self.queue[-1][rank] - self.queue[0][rank]
                speed = delta / ((length - 1) * self.delay) * 60
                result[rank] = speed
        return result

    def getImageOfScore(self):
        """渲染排名图片。"""
        result = [["RANK", "CURRENT", "SPEED"]]
        speedPerhour = self.getSpeedPerhour()
        if len(speedPerhour) == 0:
            return False

        for rank in self.queue[-1]:
            if rank in speedPerhour:
                result.append([
                    str(rank),
                    "{:,}".format(int(self.queue[-1][rank])),
                    "{:,}".format(int(speedPerhour[rank])),
                ])
            else:
                result.append([
                    str(rank),
                    "{:,}".format(int(self.queue[-1][rank])),
                    "N/A",
                ])

        fig, ax = plt.subplots()
        try:
            ax.axis("off")
            table = ax.table(cellText=result, loc='center', cellLoc='center')
            table.set_fontsize(12)
            table.scale(1, 1.5)

            buf = io.BytesIO()
            plt.savefig(buf, format='png', bbox_inches='tight')
            buf.seek(0)
            return buf
        finally:
            # 长时间运行的 bot 不应该累积 matplotlib figure。
            plt.close(fig)

    def __repr__(self):
        return repr(list(self.queue))
