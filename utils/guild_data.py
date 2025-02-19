class GuildData:
    def __init__(self):
        self.queue: list[dict] = []
        self.playing: dict = {}
        self.player_state: int = 0

    def reset(self):
        self.playing = {}
        self.player_state = 0

    def is_ready(self) -> bool:
        return self.player_state == 0

    def is_playing(self) -> bool:
        return self.player_state == 1
