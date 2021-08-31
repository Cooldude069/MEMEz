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
            memeList = {}
            # Fetching fresh memes.
            # Similar process.
            for subreddit in self.subreddits:
                memes = await self.reddit.subreddit(subreddit)
                hot = memes.top("day", limit=20)
                async for meme in hot:
                    if not meme.url.startswith("https://v.redd.it/"):
                        memeList[meme.title] = {}
                        memeList[meme.title]["score"] = meme.score
                        memeList[meme.title]["url"] = meme.url
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
            channel_is_nsfw = ctx.channel.is_nsfw()
            if not channel_is_nsfw:
                sendable_meme = random.choice(memeList)  # Picking a random meme.
                while memeList[sendable_meme]["nsfw"]:
                    sendable_meme = random.choice(memeList)

            # creating the meme embed.
            embed = discord.Embed(
                description=f"[{sendable_meme}]({memeList[sendable_meme]['url']})",
                colour=discord.Color.from_rgb(255, 93, 68),
            )
            embed.set_image(url=memeList[sendable_meme]["url"])
            embed.set_author(
                name=f'u/{memeList[sendable_meme]["author"]}',
                url=memeList[sendable_meme]["author_url"],
                icon_url=memeList[sendable_meme]["icon_url"],
            )
            embed.add_field(
                name="Votes 🔥",
                value=f'`{memeList[sendable_meme]["score"]}`',
                inline=True,
            )
            embed.add_field(
                name="Comments 💬",
                value=f'`{memeList[sendable_meme]["comments"]}`',
                inline=True,
            )
            embed.add_field(
                name="Upvote ratio ⚖️",
                value=f"`{int(memeList[sendable_meme]['upvote_ratio'] * 100)}%`",
                inline=True,
            )
            embed.set_footer(
                text=f"From r/{memeList[sendable_meme]['sub']}",
                icon_url=memeList[sendable_meme]["sub_icon"],
            )
            embed.timestamp = datetime.datetime.utcfromtimestamp(
                int(memeList[sendable_meme]["ts"])
            )
            await ctx.send(embed=embed)
        else:
            # if the memes have been logged.
            memeList = loggedMemes
            channel_is_nsfw = ctx.channel.is_nsfw()
            if not channel_is_nsfw:
                sendable_meme = random.choice(memeList)  # Picking a random meme.
                while memeList[sendable_meme]["nsfw"]:
                    sendable_meme = random.choice(memeList)
            embed = discord.Embed(
                description=f"[{sendable_meme}]({memeList[sendable_meme]['url']})",
                colour=discord.Color.from_rgb(255, 93, 68),
            )
            embed.set_image(url=memeList[sendable_meme]["url"])
            embed.set_author(
                name=f'u/{memeList[sendable_meme]["author"]}',
                url=memeList[sendable_meme]["author_url"],
                icon_url=memeList[sendable_meme]["icon_url"],
            )
            embed.add_field(
                name="Votes 🔥",
                value=f'`{memeList[sendable_meme]["score"]}`',
                inline=True,
            )
            embed.add_field(
                name="Comments 💬",
                value=f'`{memeList[sendable_meme]["comments"]}`',
                inline=True,
            )
            embed.add_field(
                name="Upvote ratio ⚖️",
                value=f"`{int(memeList[sendable_meme]['upvote_ratio'] * 100)}%`",
                inline=True,
            )
            embed.set_footer(
                text=f"From r/{memeList[sendable_meme]['sub']}",
                icon_url=memeList[sendable_meme]["sub_icon"],
            )
            embed.timestamp = datetime.datetime.utcfromtimestamp(
                int(memeList[sendable_meme]["ts"])
            )
            await ctx.send(embed=embed)


def setup(client):
    # Adding the Cog to the bot client.
    client.add_cog(Memes(client))
