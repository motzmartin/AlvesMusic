import discord

class PlayerData:
    def __init__(self):
        self.queue: list[dict] = []

        self.state: int = 0

        self.playing_song: dict = {}
        self.is_paused: bool = False

        self.playing_message: discord.Message = None
        self.update_playing_message: bool = False

        self.started_at: int = 0
        self.paused_at: int = 0
        self.paused_time: int = 0

    def reset(self):
        self.state = 0

        self.playing_song = {}
        self.is_paused = False

        self.playing_message = None
        self.update_playing_message = False

        self.started_at = 0
        self.paused_at = 0
        self.paused_time = 0

    def is_ready(self):
        return self.state == 0

    def is_playing(self):
        return self.state == 1
