from typing import Union
import discord
from discord.ext import commands


ENABLED = "✓"
DISABLED = "❌"


def arg_parser(args: Union[tuple, list]) -> dict:
    _args = {}
    print(args)
    for i in range(len(args)):
        arg: str = args[i]
        if arg.startswith("--"):
            try:
                _args[arg.lstrip("--").lower()] = args[i + 1]
            except IndexError:
                print(args)

    return _args


class Settings(commands.Cog):
    def __init__(self, client: commands.Bot) -> None:
        self.client = client

    @commands.command(name="settings")
    async def edit_settings(self, ctx, *args):
        argvs = arg_parser(args)
        await ctx.send(argvs)


def setup(client: commands.Bot):
    client.add_cog(Settings(client))
