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
        self.cluster = MongoClient(environ.get("mongo_url"))
        self.subreddits = [
            "dankmemes",
            "memes",
            "wholesomememes",
            "meme",
            "nextfuckinglevel",
        ]
        self.reddit = asyncpraw.Reddit(
            client_id=environ.get("r_client_id"),
            client_secret=environ.get("r_client_secret"),
            username=environ.get("r_username"),
            password=environ.get("r_password"),
            user_agent=environ.get("r_ua"),
        )
        self.updateMeme.start()

    @tasks.loop(minutes=180)
    async def updateMeme(self):
        await self.client.wait_until_ready()
        print("Attempting to log memes")
        memeList = {}

        for subreddit in self.subreddits:
            memes = await self.reddit.subreddit(subreddit)
            hot = memes.top("day", limit=20)
            async for meme in hot:
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

        db = self.cluster["main"]
        collection = db["memes"]
        collection.update_one({"_id": 2}, {"$set": {"memes": memeList}})
        print("Logged Memes")

    @commands.command()
    async def meme(self, ctx):
        db = self.cluster["main"]
        collection = db["memes"]
        loggedMemes = collection.find_one({"_id": 2})["memes"]
        if loggedMemes is None:
            memeList = {}
            for subreddit in self.subreddits:
                memes = await self.reddit.subreddit(subreddit)
                hot = memes.top("day", limit=20)
                async for meme in hot:
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
                name="Votes 🔥", value=memeList[sendable_meme]["score"], inline=True
            )
            embed.add_field(
                name="Comments 💬",
                value=memeList[sendable_meme]["comments"],
                inline=True,
            )
            embed.add_field(
                name="Upvote ratio ⚖️",
                value=memeList[sendable_meme]["upvote_ratio"],
                inline=True,
            )
            embed.set_footer(
                text=f"From r/{memeList[sendable_meme]['sub']}",
                icon_url=memeList[sendable_meme]["sub_icon"],
            )
            embed.timestamp = datetime.datetime.utcnow()
            await ctx.send(embed=embed)
        else:
            memeList = loggedMemes
            sendable_meme = random.choice(list(memeList))
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
                name="Votes 🔥", value=memeList[sendable_meme]["score"], inline=True
            )
            embed.add_field(
                name="Comments 💬",
                value=memeList[sendable_meme]["comments"],
                inline=True,
            )
            embed.add_field(
                name="Upvote ratio ⚖️",
                value=memeList[sendable_meme]["upvote_ratio"],
                inline=True,
            )
            embed.set_footer(
                text=f"From r/{memeList[sendable_meme]['sub']}",
                icon_url=memeList[sendable_meme]["sub_icon"],
            )
            embed.timestamp = datetime.datetime.utcnow()
            await ctx.send(embed=embed)


def setup(client):
    client.add_cog(Memes(client))
