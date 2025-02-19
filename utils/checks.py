import discord
from discord.ext import commands

def voice_check():
    async def predicate(ctx: commands.Context):
        if not ctx.author.voice or not ctx.author.voice.channel:
            raise commands.CheckFailure("You must be in a voice channel to use this command.")

        voice: discord.VoiceClient = ctx.guild.voice_client

        if voice and voice.channel != ctx.author.voice.channel:
            raise commands.CheckFailure("You must be in the same voice channel as the bot.")

        return True

    return commands.check(predicate)
