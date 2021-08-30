import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import pymongo
from pymongo import MongoClient
from run import start


load_dotenv()  # Loading the environment variables from the .env file.

cluster = MongoClient(os.environ.get("mongo_url"))  # Connecting to MongoDB
DEFAULT_PREFIX = "!"


def get_prefix(client, message: discord.Message):
    """
    Fetching the prefix from the database.
    """
    db = cluster["main"]
    collection = db["prefixes"]
    prefixes = collection.find_one({"_id": 0})
    try:
        if not prefixes:
            return DEFAULT_PREFIX
        if str(message.guild.id) in prefixes.keys():
            return prefixes[str(message.guild.id)]

        return DEFAULT_PREFIX
    except Exception:
        return DEFAULT_PREFIX


client = commands.Bot(command_prefix=get_prefix, case_insensitive=True)
cogs = ["cogs.redditFetcher", "cogs.memeEditor"]  # all the cogs.


@client.event
async def on_ready():
    print("Bot online!")


@client.command(name="prefix")
async def _prefix(ctx, _p: str = None):
    """
    Changing the prefix of the bot.
    """
    if not _p:
        await ctx.send("Please provide a valid prefix.")
        return
    elif _p == get_prefix(client, ctx.message):
        # Prefix is same as the current prefix.
        await ctx.send("Prefix already in use. Please provide a different prefix.")
    db = cluster["main"]
    collection = db["prefixes"]
    prefixes = collection.find_one({"_id": 0})
    if prefixes is None:
        # Prefix not present in database, so adding the server to the database
        collection.insert_one({"_id": 0, str(ctx.guild.id): _p})
        await ctx.send(f"Prefix successfully changed to {_p}")
        return True
    else:
        collection.update_one(
            {"_id": 0}, {"$set": {str(ctx.guild.id): _p}}
        )  # updating prefix
        await ctx.send(f"Prefix successfully changed to {_p}")
        return True


for cog in cogs:
    # Loading all cogs.
    client.load_extension(cog)

start()
client.run(os.environ.get("bot_token"))  # Running the bot.
