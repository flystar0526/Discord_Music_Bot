import discord
from discord.ext import commands
from discord import app_commands

class Utils(commands.Cog):
  def __init__(self, bot):
    self.bot = bot

  @app_commands.command(name = "ping", description = "回傳目前延遲")
  async def ping(self, interaction: discord.Interaction):
    await interaction.response.send_message(f"目前延遲 : {round(self.bot.latency * 1000)} ms")

async def setup(bot):
  await bot.add_cog(Utils(bot))
