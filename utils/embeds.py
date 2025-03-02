import time
import discord
from discord.ext import commands

from . import PlayerData, to_timecode

COLOR = "#73BCFF"

def get_inline_details(song: dict, index: int = 0, include_author: bool = True):
    line = ""

    if index > 0:
        line += "**{}.** ".format(index)

    title: str = song["title"]

    if len(title) > 30:
        title = title[:30] + "..."

    title = title.replace("[", "(")

    line += "[**{}**]({})".format(title, song["url"])

    if song["duration"]:
        line += " ({})".format(to_timecode(song["duration"]))

    if include_author:
        ctx: commands.Context = song["context"]

        if ctx.author:
            line += " {}".format(ctx.author.mention)

    return line

def get_base_embed(title: str = ""):
    embed = discord.Embed()
    embed.color = discord.Color.from_str(COLOR)

    if title:
        embed.title = title

    return embed

def get_media_embed(media: dict, embed_type: int, player: PlayerData | None = None):
    """
    embed_type (int):
        0 - Added to queue (single song)
        1 - Added to queue (playlist)
        2 - Pending
        3 - Finished
        4 - Playing
    """
    link = "[**{}**]({})".format(media["title"], media["url"])

    match embed_type:
        case 0:
            embed = get_base_embed("📌 Added to queue")
            embed.description = "The song {} has been added to the queue at **{}.**".format(link, media["position"])
        case 1:
            embed = get_base_embed("💿 Tracks added to queue")
            embed.description = "The **{}** remaining tracks from the playlist {} have been added to the queue.\n\n{}".format(media["count"], link, media["preview"])
        case 2:
            embed = get_base_embed("🕐 Pending...")
            embed.description = "The remaining tracks in the playlist {} are still pending... Please be patient.".format(link)
        case 3:
            embed = get_base_embed("🙌 Finished")
            embed.description = "The song {} has ended.".format(link)
        case 4:
            embed = get_base_embed("⏸️ Paused" if player.is_paused() else "🎶 Now Playing")
            embed.description = link

            if media["duration"]:
                delta = player.started_at + player.paused_time

                if player.is_paused():
                    delta = player.paused_at - delta
                else:
                    delta = time.time() - delta

                point_index = int(15 * (delta / media["duration"]))
                progress_bar = ["🔘" if i == point_index else "▬" for i in range(15)]

                embed.add_field(name="Progress Bar", value="{} {}/{}".format("".join(progress_bar), to_timecode(delta), to_timecode(media["duration"])), inline=False)

    if media["channel"] and media["channel_url"]:
        embed.add_field(name="Channel", value="[**{}**]({})".format(media["channel"], media["channel_url"]))

    if media["view_count"]:
        embed.add_field(name="Views", value="{:,}".format(media["view_count"]).replace(",", " "))

    if embed_type != 4 and media["duration"]:
        embed.add_field(name="Total Duration" if embed_type == 1 else "Duration", value=to_timecode(media["duration"]))

    if media["thumbnail"]:
        embed.set_thumbnail(url=media["thumbnail"])

    ctx: commands.Context = media["context"]

    if ctx.author:
        embed.set_footer(text="Requested by {}".format(ctx.author.global_name), icon_url=ctx.author.avatar.url)

    return embed

async def edit_playing_embed(player: PlayerData, embed_type: int):
    embed = get_media_embed(player.playing_song, embed_type, player=player)

    try:
        await player.playing_embed.edit(embed=embed)
    except discord.NotFound:
        player.update_playing_embed = False
