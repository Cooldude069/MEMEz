import discord
from discord.ext import commands


ENABLED = "✓"
DISABLED = "❌"


def arg_parser(args: tuple) -> dict:
    _args = {}
    for arg in args:
        if arg.startswith("--"):
            try:
                _args[arg.lstrip("--")] = args[args.index(arg) + 1]
            except IndexError:
                print(args)

    return _args


class Settings(commands.Cog):
    def __init__(self, client: commands.Bot) -> None:
        self.client = client

    @commands.command(name="settings")
    async def edit_settings(self, ctx, *args):
        argvs = arg_parser(args[0])
        await ctx.send(argvs)


def setup(client: commands.Bot):
    client.add_cog(Settings(client))
