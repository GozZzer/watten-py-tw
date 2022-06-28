class Packet:
    def __init__(self, task_type: str, **kwargs):
        self.task_type = task_type
        self.data = kwargs

    def __str__(self):
        return f'<Packet task_type: "{self.task_type}">'


class GamePacket(Packet):
    def __init__(self, move_type: str, **kwargs):
        self.move_type = move_type
        super().__init__("GAME", **kwargs)

    def __str__(self):
        return f'<GamePacket move_type: "{self.move_type}">'
