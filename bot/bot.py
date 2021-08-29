import discord
from discord.ext import commands
import os
from dotenv import load_dotenv


load_dotenv()
client = commands.Bot(command_prefix="!")
# cogs = ["cogs.redditFetcher", "cogs.memeEditor"]
cogs = ["cogs.memeEditor"]


@client.event
async def on_ready():
    print("Bot online!")


for cog in cogs:
    client.load_extension(cog)

client.run(os.environ.get("bot_token"))
