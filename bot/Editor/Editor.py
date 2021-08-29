from PIL import Image, ImageDraw, ImageFont
from io import BytesIO


class Editor:
    def __init__(self) -> None:
        pass

    def lineBreak(self, text: str, start: int, stop: int) -> int:
        _break = start
        for i in range(start, stop):
            if text[i] == " ":
                _break = i

        return _break

    def blitText(
        self,
        text: str,
        start: tuple,
        image: Image,
        charsPerLine: int,
        font: ImageFont.FreeTypeFont = None,
        fontSize=80,
        textColor: tuple = (0, 0, 0),
    ) -> Image:
        if not font:
            font = ImageFont.truetype("bot/fonts/arial.ttf", fontSize)
        img = image
        draw = ImageDraw.Draw(img)
        _increment = int(1.5 * fontSize)
        i = 0
        _start = 0
        stop = charsPerLine
        if len(text) > charsPerLine:
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
