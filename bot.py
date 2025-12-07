import discord
from discord.ext import commands
from discord import FFmpegPCMAudio
import yt_dlp
import asyncio
import os

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

queues = {}  # { guild_id: [songs] }


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


def play_next(voice, guild_id):
    queue = get_queue(guild_id)
    if not queue:
        return

    song = queue.pop(0)
    audio = FFmpegPCMAudio(song["url"])
    voice.play(audio, after=lambda e: play_next(voice, guild_id))


@bot.command()
async def play(ctx, *, query):
    if not ctx.author.voice:
        return await ctx.send("⚠️ Devi essere in un canale vocale.")

    voice = ctx.voice_client
    if not voice:
        voice = await ctx.author.voice.channel.connect()

    url, title = search_yt(query)
    queue = get_queue(ctx.guild.id)

    if voice.is_playing() or voice.is_paused():
        queue.append({"url": url, "title": title})
        return await ctx.send(f"➕ Aggiunto in coda: **{title}**")

    audio = FFmpegPCMAudio(url)
    voice.play(audio, after=lambda e: play_next(voice, ctx.guild.id))
    await ctx.send(f"▶️ Riproduzione: **{title}**")


@bot.command()
async def pause(ctx):
    if ctx.voice_client and ctx.voice_client.is_playing():
        ctx.voice_client.pause()
        return await ctx.send("⏸️ Musica in pausa.")
    await ctx.send("⚠️ Nessuna musica in riproduzione.")


@bot.command()
async def resume(ctx):
    if ctx.voice_client and ctx.voice_client.is_paused():
        ctx.voice_client.resume()
        return await ctx.send("▶️ Ripresa.")
    await ctx.send("⚠️ La musica non è in pausa.")


@bot.command()
async def skip(ctx):
    if ctx.voice_client and ctx.voice_client.is_playing():
        ctx.voice_client.stop()
        return await ctx.send("⏭️ Brano saltato.")
    await ctx.send("⚠️ Nulla da saltare.")


@bot.command()
async def queue(ctx):
    queue = get_queue(ctx.guild.id)
    if not queue:
        return await ctx.send("📭 La coda è vuota.")

    msg = "\n".join([f"{i+1}. {s['title']}" for i, s in enumerate(queue)])
    await ctx.send(f"📜 **Coda:**\n{msg}")


@bot.command()
async def leave(ctx):
    if ctx.voice_client:
        queues[ctx.guild.id] = []
        await ctx.voice_client.disconnect()
        return await ctx.send("👋 Uscito dal canale.")
    await ctx.send("⚠️ Non sono in un canale vocale.")


# ✅ AVVIO DEL BOT CON TOKEN DA RAILWAY
bot.run(os.getenv("TOKEN"))
