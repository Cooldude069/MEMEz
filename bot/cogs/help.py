import discord
from discord.ext import commands, menus


class Help(menus.Menu):
    def __init__(self):
        super().__init__(timeout=30.0, clear_reactions_after=True)

    async def send_initial_message(self, ctx, channel):
        return await super().send_initial_message(ctx, channel)
