import discord
from discord.ext import commands


ENABLED = "✓"
DISABLED = "❌"


def arg_parser(*args) -> dict:
    _args = {}
    print(args)
    for arg in args:
        if arg.startswith("--"):
            _args[arg.lstrip("--")] = args[args.index(arg) + 1]

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
