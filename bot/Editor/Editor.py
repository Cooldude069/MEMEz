from PIL import Image, ImageDraw, ImageFont
from io import BytesIO


class Editor:
    """
    This class will do the job of overlaying text/images onto another. Working as
    an editor.
    """

    def __init__(self) -> None:
        pass

    def lineBreak(self, text: str, start: int, stop: int) -> int:
        """
        Finding the index(of the space) at which the line can be broken in two.
        For eg:
        "Hello there" can be broken at the space between the two words.
        It will return the index of the space closest to the end.
        """
        _break = start
        for i in range(start, stop):
            if text[i] == " ":
                _break = i

        return _break

    def blitText(
        self,
        text: str,  # The text to be overlayed.
        start: tuple,  # The coordinates of the start point of the text
        image: Image,  # The Image on which the text will be overlayed
        charsPerLine: int,  # The maximum amount of characters allowed per line
        font: ImageFont.FreeTypeFont = None,  # The font of the text(check bot/fonts)
        fontSize=80,  # The font size of the text.
        textColor: tuple = (0, 0, 0),  # The (r, g, b) value of the text color.
    ) -> Image:
        """
        This function will overlay text onto an Image and return the edited Image.
        """
        if not font:
            font = ImageFont.truetype(
                "bot/fonts/arial.ttf", fontSize
            )  # default font = 'arial'
        img = image
        draw = ImageDraw.Draw(img)
        _increment = int(1.5 * fontSize)  # a rough estimate.
        i = 0
        _start = 0
        stop = charsPerLine
        if len(text) > charsPerLine:
            # Overlaying the characters in lines over the image.
            while len(text) > charsPerLine:
                _stop = self.lineBreak(text, _start, stop)
                txt = text[_start:_stop]
                draw.text((start[0], start[1] + i), txt, textColor, font=font)
                i += _increment
                text = text[_stop + 1 :]

            draw.text((start[0], start[1] + i), text, textColor, font=font)
        else:
            draw.text((start[0], start[1] + i), text, textColor, font=font)

        return img
