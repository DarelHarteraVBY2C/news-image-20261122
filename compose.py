"""Build the news-image entry for Sunday 22 November 2026.

Takes the four photo panels in panels/ (bahrain, cop31deal, israel, asia)
and lays them out as a one-page newspaper front page, with the day's
headlines drawn in PIL so every word is spelled exactly as written here.
The fifth story (Hong Kong) is a text-only brief: the image tool would
not generate a polling-station picture, so that slot carries headline
and standfirst only, as a newspaper brief does. Output is entry.jpg,
1024x1024, under 1 MiB.

Run: python3 compose.py
"""
import os

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
W, H = 1024, 1024
PAPER = (253, 251, 247)
INK = (17, 17, 17)
MUTED = (85, 85, 85)
ACCENT = (155, 44, 44)
RULE = (17, 17, 17)
HAIR = (204, 204, 204)

SERIF_B = '/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf'
SANS = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
SANS_B = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'


def load_font(path, size):
    return ImageFont.truetype(path, size)


def load_panel(name):
    path = os.path.join(HERE, 'panels', f'{name}.webp')
    if not os.path.exists(path):
        raise SystemExit(f'no panel image: {path}')
    return Image.open(path).convert('RGB')


def crop_resize(im, w, h):
    """Center-crop to the target aspect ratio, then resize to w x h."""
    target = w / h
    ratio = im.width / im.height
    if ratio > target:
        nw = int(im.height * target)
        x = (im.width - nw) // 2
        im = im.crop((x, 0, x + nw, im.height))
    else:
        nh = int(im.width / target)
        y = (im.height - nh) // 2
        im = im.crop((0, y, im.width, y + nh))
    return im.resize((w, h), Image.LANCZOS)


def wrap_text(draw, text, fnt, max_w):
    words = text.split()
    lines, cur = [], ''
    for word in words:
        trial = f'{cur} {word}'.strip()
        if draw.textlength(trial, font=fnt) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def build():
    img = Image.new('RGB', (W, H), PAPER)
    d = ImageDraw.Draw(img)
    mx = 16
    cw = W - 2 * mx

    # --- masthead ---
    title = 'THE WORLD IN ONE DAY'
    tf = load_font(SERIF_B, 46)
    d.text(((W - d.textlength(title, font=tf)) / 2, 10), title, font=tf, fill=INK)
    date = 'SUNDAY, 22 NOVEMBER 2026'
    df = load_font(SANS_B, 19)
    d.text(((W - d.textlength(date, font=df)) / 2, 62), date, font=df, fill=INK)
    d.line([(mx, 88), (W - mx, 88)], fill=RULE, width=2)

    # --- lead story: Iran strikes US bases in Bahrain ---
    lead = crop_resize(load_panel('bahrain'), cw, 330)
    img.paste(lead, (mx, 96))
    y = 434
    kf = load_font(SANS_B, 14)
    d.text((mx, y), 'MIDDLE EAST  •  LEAD STORY', font=kf, fill=ACCENT)
    y += 22
    hf = load_font(SERIF_B, 38)
    d.text((mx, y), 'IRAN STRIKES US BASES IN BAHRAIN', font=hf, fill=INK)
    y += 48
    sf = load_font(SANS, 19)
    d.text((mx, y), 'Two waves of drones and missiles hit four bases; defences intercept some, no injuries.', font=sf, fill=MUTED)
    d.line([(mx, 540), (W - mx, 540)], fill=RULE, width=2)

    # --- two-column rows; a None panel means a text-only brief ---
    col_w = (cw - 16) // 2
    col_x = [mx, mx + col_w + 16]
    rows = [
        (548, [
            ('cop31deal', 'COP31 CLOSE TO FINAL DEAL',
             'New package presented overnight; approval session at 06:00 GMT. Not agreed yet.'),
            ('israel', 'EISENKOT INVITES LIKUD TO TALKS',
             'Marathon coalition talks start Sunday; mandate expires 6 December.'),
        ]),
        (772, [
            ('asia', 'AI ROUT SPREADS TO ASIA',
             'Nikkei -5.1%, Kospi -5.5%, SoftBank -14.5%; MSCI Asia at six-year low.'),
            (None, 'HONG KONG ELECTION COMMITTEE VOTES',
             '856 candidates for 723 seats in 31 subsectors; polls open 09:00-18:00.'),
        ]),
    ]
    for top, cols in rows:
        for i, (name, headline, sub) in enumerate(cols):
            x = col_x[i]
            if name is None:
                # Text-only brief: headline at the top of the slot.
                hfont = load_font(SERIF_B, 21)
                d.text((x, top), headline, font=hfont, fill=INK)
                sfont = load_font(SANS, 15)
                for j, line in enumerate(wrap_text(d, sub, sfont, col_w)):
                    d.text((x, top + 28 + j * 19), line, font=sfont, fill=MUTED)
                continue
            pic = crop_resize(load_panel(name), col_w, 118)
            img.paste(pic, (x, top))
            hy = top + 126
            hfont = load_font(SERIF_B, 21)
            d.text((x, hy), headline, font=hfont, fill=INK)
            sfont = load_font(SANS, 15)
            for j, line in enumerate(wrap_text(d, sub, sfont, col_w)):
                d.text((x, hy + 28 + j * 19), line, font=sfont, fill=MUTED)
        d.line([(mx, top + 208), (W - mx, top + 208)], fill=HAIR, width=1)

    # --- bottom strip ---
    strip = "ALSO TODAY:  Three tankers hit near Hormuz  ·  COP31 objections due 03:00 GMT  ·  Change Bloc holds 48 of 120 seats"
    sfont = load_font(SANS, 15)
    d.text(((W - d.textlength(strip, font=sfont)) / 2, 994), strip, font=sfont, fill=INK)

    jpg_path = os.path.join(HERE, 'entry.jpg')
    img.save(jpg_path, quality=92)
    print(f'entry.jpg (q92): {os.path.getsize(jpg_path)} bytes')
    print('limit: 1048576 bytes, 1024x1024')


if __name__ == '__main__':
    build()
