import discord
from discord.ext import commands
from Editor.Editor import Editor
from PIL import Image


class MemeEditor(commands.Cog):
    def __init__(self, client: commands.Bot) -> None:
        self.client = client
        self.dirPath = "bot/Assets/meme-templates/"  # The path to the directory where all memes are stored.

    @commands.command(name="drake")
    async def _drake(self, ctx, *, text: str):
        t1, t2 = text.split(",")  # t1 and t2 are the top and bottom texts in the meme.
        if t2.startswith(" "):
            t2 = t2[1:]

        if len(t1) > 75 or len(t2) > 75:
            await ctx.send(
                "You cannot exceed 75 characters per sentence. Please try again."
            )
            return

        editor = Editor()
        img = Image.open("bot/Assets/meme-templates/drake.jpeg")
        img = editor.blitText(
            t1, (618, 24), img, 20, fontSize=60
        )  # (618, 24) are the coordinates of the point from where the top text should start.
        img = editor.blitText(
            t2, (618, 616), img, 20, fontSize=60
        )  # (618, 616) are the coordinates of the point from where the top text should start.
        img.save(
            "bot/Assets/out/drake.png"
        )  # All the edited memes will be stored in the Assets/out directory.
        await ctx.send(
            file=discord.File("bot/Assets/out/drake.png")
        )  # Sending the edited meme.


def setup(client: commands.Bot):
    """
    Adding the Cog(Class) to the bot client.
    """
    client.add_cog(MemeEditor(client))
