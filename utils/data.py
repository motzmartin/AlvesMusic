import time
import discord

class PlayerData:
    def __init__(self):
        self.queue: list[dict] = []

        self.state = 0

        self.playing_song = {}
        self.playing_message: discord.Message | None = None
        self.update_playing_message = False

        self.started_at = self.paused_at = self.paused_time = 0

    def reset(self):
        self.state = 0

        self.playing_song.clear()
        self.playing_message = None
        self.update_playing_message = False

        self.started_at = self.paused_at = self.paused_time = 0

    def pause(self):
        self.state = 2

        self.paused_at = time.time()

    def resume(self):
        self.state = 1

        self.update_playing_message = True

        self.paused_time += time.time() - self.paused_at

    def is_ready(self):
        return self.state == 0

    def is_playing(self):
        return self.state == 1

    def is_paused(self):
        return self.state == 2
