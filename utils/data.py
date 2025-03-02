import time
import discord

class PlayerData:
    def __init__(self):
        self.queue: list[dict] = []

        self.state = 0

        self.playing_song = {}
        self.playing_embed: discord.Message | None = None
        self.update_playing_embed = False

        self.started_at = self.paused_at = self.paused_time = 0

    def reset(self):
        self.state = 0

        self.playing_song.clear()
        self.playing_embed = None
        self.update_playing_embed = False

        self.started_at = self.paused_at = self.paused_time = 0

    async def pause(self):
        from . import edit_playing_embed

        self.state = 2

        self.update_playing_embed = False

        self.paused_at = time.time()

        await edit_playing_embed(self, 4)

    def resume(self):
        self.state = 1

        self.update_playing_embed = True

        self.paused_time += time.time() - self.paused_at

    def is_ready(self):
        return self.state == 0

    def is_playing(self):
        return self.state == 1

    def is_paused(self):
        return self.state == 2

    def is_active(self):
        return self.is_playing() or self.is_paused()
