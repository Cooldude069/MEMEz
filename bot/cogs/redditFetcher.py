import collections
import discord
from discord.ext import commands, tasks
import pymongo
from pymongo import MongoClient
from os import environ
import asyncpraw
import datetime
import random


class Memes(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client
        self.cluster = MongoClient(
            environ.get("mongo_url")
        )  # Connecting to the MongoDB database.
        self.subreddits = [  # The subreddits from which the bot will fetch memes.
            "dankmemes",
            "memes",
            "wholesomememes",
            "meme",
            "nextfuckinglevel",
        ]
        self.reddit = asyncpraw.Reddit(  # The reddit instance.
            client_id=environ.get("r_client_id"),
            client_secret=environ.get("r_client_secret"),
            username=environ.get("r_username"),
            password=environ.get("r_password"),
            user_agent=environ.get("r_ua"),
        )
        self.updateMeme.start()  # Starting the task to update memes.

    def nextMemeIndex(self, serverID: int) -> int:
        db = self.cluster["main"]
        collection = db["memes-viewed"]
        memeCollection = db["memes"]
        _memes = memeCollection.find_one({"_id": 2})
        totalMemes = len(list(_memes))
        memesViewed: dict = collection.find_one({"_id": 0})
        index = 0
        if str(serverID) in list(memesViewed):
            index = memesViewed[str(serverID)]

        _index = index + 1 if index + 1 < totalMemes else 0
        collection.update_one({"_id": 0}, {"$set": {str(serverID): _index}})
        return index

    @tasks.loop(minutes=180)
    async def updateMeme(self):
        """
        This task repeats itself after 180 minutes. The purpose of it is to speed up the meme command.
        It will log new memes to the MongoDB database and when the meme command is used, it will send a meme
        which is stored in the database, hence speeding up the process by about 8s.
        """
        await self.client.wait_until_ready()  # waiting for the bot client to be online.
        print("Attempting to log memes")
        memeList = {}  # All the memes to be logged will be stored here.

        for subreddit in self.subreddits:
            sub = await self.reddit.subreddit(subreddit)  # fetching the subreddit.
            top = sub.top("day", limit=20)  # fetching the top 20 memes of the day.
            async for meme in top:
                # Adding the memes to the list.
                if not meme.url.startswith("https://v.redd.it/"):
                    memeList[meme.title] = {}
                    memeList[meme.title]["score"] = meme.score
                    memeList[meme.title]["url"] = meme.url
                    memeList[meme.title]["link"] = f"https://reddit.com{meme.permalink}"
                    memeList[meme.title]["comments"] = len(await meme.comments())
                    memeList[meme.title]["sub"] = subreddit
                    memeList[meme.title]["author"] = meme.author.name
                    author = await self.reddit.redditor(meme.author.name)
                    await author.load()
                    memeList[meme.title]["icon_url"] = author.icon_img
                    memeList[meme.title][
                        "author_url"
                    ] = f"https://reddit.com/user/{author.name}"
                    await meme.subreddit.load()
                    memeList[meme.title]["sub_icon"] = meme.subreddit.icon_img
                    memeList[meme.title]["upvote_ratio"] = meme.upvote_ratio
                    memeList[meme.title]["ts"] = meme.created_utc
                    memeList[meme.title]["nsfw"] = meme.over_18

        db = self.cluster["main"]  # establishing a connection to the database.
        collection = db["memes"]
        collection.update_one(
            {"_id": 2}, {"$set": {"memes": memeList}}
        )  # Updating the memes.
        print("Logged Memes")

    @commands.command()
    async def meme(self, ctx):
        """
        This command will return a meme which has been logged to the database. If none have been logged,
        then it will fetch a fresh meme from reddit and send it to the user.
        """
        db = self.cluster["main"]  # Connecting to the database
        collection = db["memes"]
        loggedMemes = collection.find_one({"_id": 2})[
            "memes"
        ]  # Fetching the memes list.
        if not loggedMemes:  # meaning no memes have been logged.
            pass
        else:
            # if the memes have been logged.
            memeList = loggedMemes
            memeIndex = self.nextMemeIndex(ctx.guild.id)
            channel_is_nsfw = ctx.channel.is_nsfw()
            _keys = list(memeList)
            _key = _keys[memeIndex]
            sendable_meme = memeList[_key]  # Picking a random meme.
            if not channel_is_nsfw:
                while sendable_meme["nsfw"]:
                    memeIndex = self.nextMemeIndex(ctx.guild.id)
                    _key = _keys[memeIndex]
                    sendable_meme = memeList[_key]

            embed = discord.Embed(
                description=f"[{sendable_meme}]({sendable_meme['link']})",
                colour=discord.Color.from_rgb(255, 93, 68),
            )
            embed.set_image(url=sendable_meme["url"])
            embed.set_author(
                name=f'u/{sendable_meme["author"]}',
                url=sendable_meme["author_url"],
                icon_url=sendable_meme["icon_url"],
            )
            embed.add_field(
                name="Votes 🔥",
                value=f'`{sendable_meme["score"]}`',
                inline=True,
            )
            embed.add_field(
                name="Comments 💬",
                value=f'`{sendable_meme["comments"]}`',
                inline=True,
            )
            embed.add_field(
                name="Upvote ratio ⚖️",
                value=f"`{int(sendable_meme['upvote_ratio'] * 100)}%`",
                inline=True,
            )
            embed.set_footer(
                text=f"From r/{sendable_meme['sub']}",
                icon_url=sendable_meme["sub_icon"],
            )
            embed.timestamp = datetime.datetime.utcfromtimestamp(
                int(sendable_meme["ts"])
            )
            await ctx.send(embed=embed)


def setup(client):
    # Adding the Cog to the bot client.
    client.add_cog(Memes(client))
