import discord

class GuildData:
    def __init__(self):
        self.queue: list[dict] = []

        self.player_state: int = 0

        self.playing: dict = {}
        self.playing_message: discord.Message = None

        self.started_at: int = 0
        self.paused_at: int = 0

        self.is_paused: bool = False
        self.paused_time: int = 0

    def reset(self):
        self.player_state = 0

        self.playing = {}

        self.started_at = 0
        self.paused_at = 0

        self.is_paused = False
        self.paused_time = 0

    def is_ready(self):
        return self.player_state == 0

    def is_playing(self):
        return self.player_state == 1
