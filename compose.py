"""Compose the 22 November 2026 news-image entry.

Four photo panels sit in panels/ (bahrain, cop31deal, israel, asia).
The fifth story, Hong Kong's Election Committee vote, is a text brief:
no polling-station picture could be generated, so that slot carries
headline and standfirst only. This script draws the whole front page
with PIL, so every word is exactly as written below, and saves it as
entry.jpg, 1024 by 1024, under one mebibyte.

Run it with: python3 compose.py
"""
import os

from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.abspath(__file__))
SIZE = 1024
EDGE = 16
SPAN = SIZE - 2 * EDGE

BG = (253, 251, 247)
FG = (17, 17, 17)
GREY = (85, 85, 85)
RED = (155, 44, 44)
LINE = (17, 17, 17)
FAINT = (204, 204, 204)

SERIF = '/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf'
SANS = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
SANSB = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'


class FrontPage:
    def __init__(self):
        self.sheet = Image.new('RGB', (SIZE, SIZE), BG)
        self.pen = ImageDraw.Draw(self.sheet)

    def typeface(self, path, size):
        return ImageFont.truetype(path, size)

    def photo(self, name):
        path = os.path.join(ROOT, 'panels', name + '.webp')
        if not os.path.exists(path):
            raise SystemExit('missing panel: ' + path)
        return Image.open(path).convert('RGB')

    def shape(self, image, width, height):
        """Trim the picture to the wanted proportions, then scale it."""
        want = width / height
        have = image.width / image.height
        if have > want:
            keep = int(image.height * want)
            cut = (image.width - keep) // 2
            image = image.crop((cut, 0, cut + keep, image.height))
        else:
            keep = int(image.width / want)
            cut = (image.height - keep) // 2
            image = image.crop((0, cut, image.width, cut + keep))
        return image.resize((width, height), Image.LANCZOS)

    def fold(self, text, fnt, width):
        """Split text into lines that fit inside width, using the font."""
        out = []
        rest = text
        while rest:
            words = rest.split(' ')
            line = ''
            used = 0
            for word in words:
                trial = (line + ' ' + word).strip()
                if self.pen.textlength(trial, font=fnt) <= width:
                    line = trial
                    used += 1
                else:
                    break
            if not line:
                line = words[0]
                used = 1
            out.append(line)
            rest = ' '.join(words[used:]).strip()
        return out

    def masthead(self):
        title = 'THE WORLD IN ONE DAY'
        tf = self.typeface(SERIF, 46)
        self.pen.text(((SIZE - self.pen.textlength(title, font=tf)) / 2, 10),
                      title, font=tf, fill=FG)
        day = 'SUNDAY, 22 NOVEMBER 2026'
        df = self.typeface(SANSB, 19)
        self.pen.text(((SIZE - self.pen.textlength(day, font=df)) / 2, 62),
                      day, font=df, fill=FG)
        self.pen.line([(EDGE, 88), (SIZE - EDGE, 88)], fill=LINE, width=2)

    def lead(self):
        self.sheet.paste(self.shape(self.photo('bahrain'), SPAN, 330), (EDGE, 96))
        self.pen.text((EDGE, 434), 'MIDDLE EAST  •  LEAD STORY',
                      font=self.typeface(SANSB, 14), fill=RED)
        self.pen.text((EDGE, 456), 'IRAN STRIKES US BASES IN BAHRAIN',
                      font=self.typeface(SERIF, 38), fill=FG)
        self.pen.text((EDGE, 504),
                      'Two waves of drones and missiles hit four bases; defences intercept some, no injuries.',
                      font=self.typeface(SANS, 19), fill=GREY)
        self.pen.line([(EDGE, 540), (SIZE - EDGE, 540)], fill=LINE, width=2)

    def small(self, top, x, image_name, headline, standfirst):
        """One of the four smaller stories, photo on top, text below."""
        half = (SPAN - 16) // 2
        if image_name is not None:
            self.sheet.paste(self.shape(self.photo(image_name), half, 118), (x, top))
            text_y = top + 126
        else:
            # Text-only brief: headline starts at the top of the slot.
            text_y = top
        self.pen.text((x, text_y), headline,
                      font=self.typeface(SERIF, 21), fill=FG)
        y = text_y + 28
        for line in self.fold(standfirst, self.typeface(SANS, 15), half):
            self.pen.text((x, y), line, font=self.typeface(SANS, 15), fill=GREY)
            y += 19
        self.pen.line([(EDGE, top + 208), (SIZE - EDGE, top + 208)],
                      fill=FAINT, width=1)

    def strip(self):
        text = ("ALSO TODAY:  Three tankers hit near Hormuz  ·  "
                "COP31 objections due 03:00 GMT  ·  "
                "Change Bloc holds 48 of 120 seats")
        fnt = self.typeface(SANS, 15)
        self.pen.text(((SIZE - self.pen.textlength(text, font=fnt)) / 2, 994),
                      text, font=fnt, fill=FG)

    def save(self):
        out = os.path.join(ROOT, 'entry.jpg')
        self.sheet.save(out, quality=92)
        print('entry.jpg (q92): {} bytes'.format(os.path.getsize(out)))
        print('limit: 1048576 bytes, 1024x1024')


def main():
    page = FrontPage()
    page.masthead()
    page.lead()
    half = (SPAN - 16) // 2
    page.small(548, EDGE, 'cop31deal', 'COP31 CLOSE TO FINAL DEAL',
               'New package presented overnight; approval session at 06:00 GMT. Not agreed yet.')
    page.small(548, EDGE + half + 16, 'israel', 'EISENKOT INVITES LIKUD TO TALKS',
               'Marathon coalition talks start Sunday; mandate expires 6 December.')
    page.small(772, EDGE, 'asia', 'AI ROUT SPREADS TO ASIA',
               'Nikkei -5.1%, Kospi -5.5%, SoftBank -14.5%; MSCI Asia at six-year low.')
    page.small(772, EDGE + half + 16, None, 'HONG KONG ELECTION COMMITTEE VOTES',
               '856 candidates for 723 seats in 31 subsectors; polls open 09:00-18:00.')
    page.strip()
    page.save()


if __name__ == '__main__':
    main()
