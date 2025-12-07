import discord
from discord.ext import commands
from discord import FFmpegPCMAudio
import yt_dlp
import asyncio

intents = discord.Intents.default()
intents.message_content = True  # required for commands in some cases

bot = commands.Bot(command_prefix="!", intents=intents)

queues = {}  # { guild_id: [song1, song2] }


def search_yt(query):
    ydl_opts = {
        "format": "bestaudio/best",
        "quiet": True,
        "noplaylist": True
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(f"ytsearch:{query}", download=False)["entries"][0]
    return info["url"], info["title"]


def get_queue(guild_id):
    if guild_id not in queues:
        queues[guild_id] = []
    return queues[guild_id]


def play_next_in_queue(voice, guild_id):
    queue = get_queue(guild_id)

    if not queue:
        return

    song = queue.pop(0)
    url = song["url"]

    audio = FFmpegPCMAudio(url)
    voice.play(audio, after=lambda e: play_next_in_queue(voice, guild_id))


@bot.command()
async def play(ctx, *, query):
    if not ctx.author.voice:
        return await ctx.send("⚠️ Devi essere in un canale vocale.")

    voice = ctx.voice_client
    if not voice:
        voice = await ctx.author.voice.channel.connect()

    ur
