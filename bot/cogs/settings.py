import discord
from discord.ext import commands


ENABLED = "✓"
DISABLED = "❌"


class Settings(commands.Cog):
    def __init__(self, client: commands.Bot) -> None:
        self.client = client

    @commands.command(name="settings")
    async def edit_settings(self, ctx, **kwargs):
        print(kwargs)


def setup(client: commands.Bot):
    client.add_cog(Settings(client))
