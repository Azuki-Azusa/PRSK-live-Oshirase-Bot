class Participation():
    users_log: dict[int, dict[int: bool]] = {}
    members: list[int] = []

    def __init__(self, members: list[str]) -> None:
        self.members = [int(member) for member in members]

    def update(self, lives: list):
        temp: dict[int, dict[str: bool]] = {}
        for live in lives:
            if live.getID() in self.users_log:
                temp[live.getID()] = self.users_log[live.getID()]
            else:
                temp[live.getID()] = {member: False for member in self.members}
        self.users_log = temp
    
    def getMentionList(self, live_id: int):
        if live_id not in self.users_log:
            return []
        return [member for member in self.members if self.users_log[live_id][member] is False]
    
    def participate(self, member: str, live_id: int):
        if live_id in self.users_log :
            self.users_log[live_id][member] = True