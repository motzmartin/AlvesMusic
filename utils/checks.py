import discord
from discord.ext import commands

def voice_check():
    """
    Check that ensures the user is in a voice channel and in the same channel as the bot.
    """

    async def predicate(ctx: commands.Context):
        # Check if the user is in a voice channel
        if not ctx.author.voice or not ctx.author.voice.channel:
            raise commands.CheckFailure("You must be in a voice channel to use this command.")

        # Retrieve the bot's current voice connection
        bot_voice: discord.VoiceClient = ctx.guild.voice_client

        # Check if the bot is connected to a voice channel and ensure it's the same as the user's channel
        if bot_voice and bot_voice.channel != ctx.author.voice.channel:
            raise commands.CheckFailure("You must be in the same voice channel as the bot.")

        # The check passes if both conditions are met
        return True

    return commands.check(predicate)
