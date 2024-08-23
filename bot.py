import discord
import os
import asyncio
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

intents = discord.Intents.all()
bot = commands.Bot(command_prefix = "/", intents=intents)
token = os.getenv("DISCORD_TOKEN")

@bot.event
async def on_ready():
  slash = await bot.tree.sync()
  print(f"目前登入身份 --> {bot.user}")
  print(f"已載入 {len(slash)} 個斜線指令")

async def main():
  for filename in os.listdir("./commands"):
    if filename.endswith(".py"):
      await bot.load_extension(f"commands.{filename[:-3]}")
  await bot.start(token)

if __name__ == "__main__":
  asyncio.run(main())
