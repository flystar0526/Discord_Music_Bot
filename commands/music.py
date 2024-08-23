import discord
from discord.ext import commands
from discord import app_commands
import yt_dlp
import asyncio

ffmpeg_options = {
  "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
  "options": "-vn"
}

yt_dlp_options = {
  "format": "bestaudio/best",
  "noplaylist": True
}

class Music(commands.Cog):
  def __init__(self, bot):
    self.bot = bot
    self.queue = asyncio.Queue()
    self.song_list = []

  @app_commands.command(name = "play", description = "播放音樂")
  @app_commands.describe(url = "Youtube 網址")
  async def play(self, interaction: discord.Interaction, url: str):
    await interaction.response.defer()

    if not interaction.user.voice:
      await interaction.followup.send("你需要在語音頻道裡")
      return

    channel = interaction.user.voice.channel
    voice_client = discord.utils.get(self.bot.voice_clients, guild=interaction.guild)

    if not voice_client:
      voice_client = await channel.connect()

    with yt_dlp.YoutubeDL(yt_dlp_options) as ydl:
      music_info = ydl.extract_info(url, download=False)
      music_url = music_info["url"]
      music_title = music_info["title"]

      self.queue.put_nowait(music_url)
      self.song_list.append(music_title)
      
      if not voice_client.is_playing():
        await self.play_next_song(voice_client)

    await interaction.followup.send(content=f"已加入音樂 : {music_title}")
    
  @app_commands.command(name = "stop", description = "暫停當前音樂")
  async def stop(self, interaction: discord.Interaction):
    voice_client = discord.utils.get(self.bot.voice_clients, guild=interaction.guild)

    if voice_client.is_playing():
      voice_client.pause()
      await interaction.response.send_message("音樂已暫停")
    else:
      await interaction.response.send_message("目前沒有音樂在播放")

  @app_commands.command(name = "resume", description = "恢復播放音樂")
  async def resume(self, interaction: discord.Interaction):
    voice_client = discord.utils.get(self.bot.voice_clients, guild=interaction.guild)

    if voice_client.is_paused():
      voice_client.resume()
      await interaction.response.send_message("音樂繼續播放")
    else:
      await interaction.response.send_message("沒有音樂被暫停")

  @app_commands.command(name = "skip", description = "跳過當前音樂")
  async def skip(self, interaction: discord.Interaction):
    voice_client = discord.utils.get(self.bot.voice_clients, guild=interaction.guild)

    if voice_client and (voice_client.is_playing() or voice_client.is_paused()):
      voice_client.stop()
      await interaction.response.send_message("跳過當前音樂")
    else:
      await interaction.response.send_message("目前沒有音樂在播放")

  @app_commands.command(name = "queue", description = "顯示目前音樂隊列")
  async def queue(self, interaction: discord.Interaction):
    if not self.song_list:
      await interaction.response.send_message("目前音樂隊列為空")
    else:
      queue_text = ""
      for song in self.song_list:
        queue_text += song
        queue_text += "\n"
      await interaction.response.send_message(f"目前音樂隊列為 :\n{queue_text}")

  async def play_next_song(self, voice_client):
    if not self.queue.empty():
      url = await self.queue.get()
      self.song_list.pop(0)
      voice_client.play(discord.FFmpegOpusAudio(url, **ffmpeg_options), after=lambda e: asyncio.run_coroutine_threadsafe(self.play_next_song(voice_client), self.bot.loop))
    else:
      await voice_client.disconnect()

async def setup(bot):
  await bot.add_cog(Music(bot))
