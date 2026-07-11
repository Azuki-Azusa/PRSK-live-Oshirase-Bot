"""参与状态。"""


class Participation:
    """参与状态对象。"""

    def __init__(self, members: list[str]) -> None:
        self.members = [int(member) for member in members]
        self.users_log: dict[int, dict[int, bool]] = {}

    def update(self, lives: list):
        """更新追踪的 Live。"""
        temp: dict[int, dict[int, bool]] = {}
        for live in lives:
            if live.getID() in self.users_log:
                temp[live.getID()] = self.users_log[live.getID()]
            else:
                temp[live.getID()] = {member: False for member in self.members}
        self.users_log = temp

    def getMentionList(self, live_id: int):
        """返回需要提醒的成员。"""
        if live_id not in self.users_log:
            return []
        return [member for member in self.members if self.users_log[live_id][member] is False]

    def participate(self, member: int, live_id: int):
        """标记成员已参与。"""
        if live_id in self.users_log:
            self.users_log[live_id][member] = True
