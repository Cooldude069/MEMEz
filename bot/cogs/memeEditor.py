import discord
from discord.ext import commands
from Editor.Editor import Editor
from PIL import Image


class MemeEditor(commands.Cog):
    def __init__(self, client: commands.Bot) -> None:
        self.client = client
        self.dirPath = "bot/Assets/meme-templates/"

    @commands.command(name="drake")
    async def _drake(self, ctx, *, text: str):
        t1, t2 = text.split(",")
        if t2.startswith(" "):
            t2 = t2[1:]

        if len(t1) > 75 or len(t2) > 75:
            await ctx.send(
                "You cannot exceed 75 characters per sentence. Please try again."
            )
            return

        editor = Editor()
        img = Image.open("bot/Assets/meme-templates/drake.jpeg")
        img = editor.blitText(t1, (618, 24), img, 20, fontSize=60)
        img = editor.blitText(t2, (618, 616), img, 20, fontSize=60)
        img.save("bot/Assets/out/drake.png")
        await ctx.send(file=discord.File("bot/Assets/out/drake.png"))


def setup(client: commands.Bot):
    client.add_cog(MemeEditor(client))
