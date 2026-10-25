"""Generate every WAREGRO logo file (SVG) from one source of truth.

Text is shaped with HarfBuzz and converted to outlines, so the SVGs need no
installed fonts.  Run:  python3 waregro/tools/build_logos.py
"""
from pathlib import Path

import uharfbuzz as hb
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont

ROOT = Path(__file__).resolve().parents[1]
FONTS = ROOT / "fonts"
OUT = ROOT / "logo" / "svg"

# ---- Brand constants (identical to the Waresouq system) -------------------
ORANGE = "#FF5300"  # Mystic Red
BROWN = "#952801"   # Deep Ember (secondary / logo dark)
LINEN = "#FFECE5"
WHITE = "#FFFFFF"
BLACK = "#1A1A1A"

NAME_LATIN = "WAREGRO"
NAME_ARABIC = "ويرغرو"  # kashida (ـ) is inserted automatically to justify
LATIN_FONT = FONTS / "Urbanist-800.ttf"
ARABIC_FONT = FONTS / "ReadexPro-700.ttf"

STROKE = 30.26  # same stroke as the original box mark

# Mark geometry (409.3 x 530 box). Same isometric box as Waresouq, but the lid
# is open and a growth arrow rises out of it: Ware + Grow.
MARK_W, MARK_H = 409.3, 530.0
_dy = 61.0
MARK_DARK = [
    ("polyline", [(394.17, 344.45), (204.66, 453.86), (15.13, 346.45)]),   # base
    ("polyline", [(394.14, 125.64), (204.65, 237.01), (15.13, 125.64)]),   # open lid
    ("polyline", [(204.65, 237.01), (204.65, 453.86)]),                    # front edge
]
MARK_ACCENT = [
    ("polyline", [(394.17, 125.64), (394.17, 344.45), (204.65, 237.01),
                  (15.13, 346.45), (15.13, 125.64)]),                      # the W
    ("polyline", [(204.65, 237.01), (204.65, -40.0)]),                     # arrow shaft
    ("polyline", [(130.0, 30.0), (204.65, -45.0), (279.3, 30.0)]),         # arrow head
]


def _pts(points, s=1.0, ox=0.0, oy=0.0):
    return " ".join(f"{ox + x * s:.2f},{oy + (y + _dy) * s:.2f}" for x, y in points)


def mark_svg(dark, accent, s=1.0, ox=0.0, oy=0.0):
    sw = STROKE * s
    common = f'fill="none" stroke-width="{sw:.2f}" stroke-linecap="round" stroke-linejoin="round"'
    out = []
    for color, shapes in ((dark, MARK_DARK), (accent, MARK_ACCENT)):
        for _, pts in shapes:
            out.append(f'<polyline {common} stroke="{color}" points="{_pts(pts, s, ox, oy)}"/>')
    return "\n    ".join(out)


# ---- Text to outlines ------------------------------------------------------
class Shaper:
    def __init__(self, path):
        data = Path(path).read_bytes()
        self.face = hb.Face(data)
        self.font = hb.Font(self.face)
        self.tt = TTFont(path)
        self.upem = self.tt["head"].unitsPerEm
        self.glyphset = self.tt.getGlyphSet()
        self.order = self.tt.getGlyphOrder()

    def shape(self, text, tracking=0):
        buf = hb.Buffer()
        buf.add_str(text)
        buf.guess_segment_properties()
        hb.shape(self.font, buf, {"kern": True, "liga": True})
        glyphs, x = [], 0
        for info, pos in zip(buf.glyph_infos, buf.glyph_positions):
            glyphs.append((self.order[info.codepoint], x + pos.x_offset, pos.y_offset))
            x += pos.x_advance + tracking
        return glyphs, x - tracking

    def path(self, text, size, ox, baseline, tracking=0):
        """SVG path data for text whose left edge is ox and baseline is baseline."""
        glyphs, adv = self.shape(text, tracking)
        s = size / self.upem
        pen = SVGPathPen(self.glyphset)
        for name, gx, gy in glyphs:
            tp = TransformPen(pen, (s, 0, 0, -s, ox + gx * s, baseline - gy * s))
            self.glyphset[name].draw(tp)
        return pen.getCommands(), adv * s

    def ink_bounds(self, text, size, tracking=0):
        from fontTools.pens.boundsPen import BoundsPen
        glyphs, _ = self.shape(text, tracking)
        s = size / self.upem
        bp = BoundsPen(self.glyphset)
        for name, gx, gy in glyphs:
            self.glyphset[name].draw(TransformPen(bp, (s, 0, 0, -s, gx * s, -gy * s)))
        return bp.bounds  # xmin, ymin, xmax, ymax (y down, baseline = 0)


LATIN = Shaper(LATIN_FONT)
ARABIC = Shaper(ARABIC_FONT)


def justified_arabic(width, size):
    """Insert kashidas after joining letters until the Arabic matches width."""
    joiners = "يغبتثجحخسشصضطظعفقكلمنهئ"
    slots = [i + 1 for i, ch in enumerate(NAME_ARABIC[:-1]) if ch in joiners]
    best = NAME_ARABIC
    n = 0
    while n < 60:
        n += 1
        chars = list(NAME_ARABIC)
        for k, slot in enumerate(reversed(slots)):
            count = n // len(slots) + (1 if k < n % len(slots) else 0)
            chars.insert(slot, "ـ" * count)
        cand = "".join(chars)
        b = ARABIC.ink_bounds(cand, size)
        if b[2] - b[0] > width:
            break
        best = cand
    return best


# ---- Lockups ---------------------------------------------------------------
LATIN_SIZE = 100.0
LATIN_TRACK = 40
lat_b = LATIN.ink_bounds(NAME_LATIN, LATIN_SIZE, LATIN_TRACK)
LAT_W = lat_b[2] - lat_b[0]
LAT_CAP = -lat_b[1]
ARABIC_TEXT = justified_arabic(LAT_W, 112.0)
ar_b = ARABIC.ink_bounds(ARABIC_TEXT, 112.0)
AR_W = ar_b[2] - ar_b[0]


def latin_block(color, ox, top):
    d, _ = LATIN.path(NAME_LATIN, LATIN_SIZE, ox - lat_b[0], top + LAT_CAP, LATIN_TRACK)
    return f'<path fill="{color}" d="{d}"/>', LAT_CAP


def arabic_block(color, right, top, width=None):
    # Arabic is right-aligned to the Latin block edge
    ox = right - AR_W - ar_b[0]
    d, _ = ARABIC.path(ARABIC_TEXT, 112.0, ox, top - ar_b[1])
    return f'<path fill="{color}" d="{d}"/>', ar_b[3] - ar_b[1]


def svg_doc(w, h, body, bg=None, title="WAREGRO"):
    rect = f'<rect width="100%" height="100%" fill="{bg}"/>\n  ' if bg else ""
    return (f'<?xml version="1.0" encoding="UTF-8"?>\n'
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w:.2f} {h:.2f}" '
            f'width="{w:.0f}" height="{h:.0f}">\n  <title>{title}</title>\n  {rect}'
            f'<g>\n    {body}\n  </g>\n</svg>\n')


def horizontal(dark, accent, text, bg=None):
    pad = 40.0
    gap_text = 26.0
    lat, cap = latin_block(text, 0, 0)  # measure only
    _, arh = arabic_block(text, 0, 0)
    text_h = cap + gap_text + arh
    mark_s = (text_h * 1.32) / MARK_H
    mw, mh = MARK_W * mark_s, MARK_H * mark_s
    h = mh + 2 * pad
    tx = pad + mw + 70.0
    ty = pad + (mh - text_h) / 2 + mh * 0.06
    lat, _ = latin_block(text, tx, ty)
    ara, _ = arabic_block(text, tx + LAT_W, ty + cap + gap_text)
    w = tx + LAT_W + pad
    body = mark_svg(dark, accent, mark_s, pad, pad) + "\n    " + lat + "\n    " + ara
    return svg_doc(w, h, body, bg)


def stacked(dark, accent, text, bg=None):
    pad = 40.0
    mark_s = 0.62
    mw, mh = MARK_W * mark_s, MARK_H * mark_s
    w = LAT_W + 2 * pad
    mx = (w - mw) / 2
    ty = pad + mh + 50.0
    lat, cap = latin_block(text, pad, ty)
    ara, arh = arabic_block(text, pad + LAT_W, ty + cap + 26.0)
    h = ty + cap + 26.0 + arh + pad
    body = mark_svg(dark, accent, mark_s, mx, pad) + "\n    " + lat + "\n    " + ara
    return svg_doc(w, h, body, bg)


def mark_only(dark, accent, bg=None, pad=40.0):
    body = mark_svg(dark, accent, 1.0, pad, pad)
    return svg_doc(MARK_W + 2 * pad, MARK_H + 2 * pad, body, bg)


def app_icon(dark, accent, bg):
    size = 1024.0
    s = 0.62 * size / MARK_H
    ox = (size - MARK_W * s) / 2
    oy = (size - MARK_H * s) / 2
    body = (f'<rect width="{size}" height="{size}" rx="{size*0.22:.0f}" fill="{bg}"/>\n    '
            + mark_svg(dark, accent, s, ox, oy))
    return svg_doc(size, size, body)


def wordmark_latin(color, bg=None):
    pad = 30.0
    lat, cap = latin_block(color, pad, pad)
    return svg_doc(LAT_W + 2 * pad, cap + 2 * pad, lat, bg)


def wordmark_arabic(color, bg=None):
    pad = 30.0
    ara, arh = arabic_block(color, pad + AR_W, pad)
    return svg_doc(AR_W + 2 * pad, arh + 2 * pad, ara, bg)


VARIANTS = {
    # name: (dark, accent, text, background)
    "primary": (BROWN, ORANGE, BROWN, None),
    "on-linen": (BROWN, ORANGE, BROWN, LINEN),
    "on-orange": (WHITE, BROWN, WHITE, ORANGE),
    "on-brown": (LINEN, ORANGE, LINEN, BROWN),
    "white": (WHITE, WHITE, WHITE, None),
    "black": (BLACK, BLACK, BLACK, None),
    "orange": (ORANGE, ORANGE, ORANGE, None),
}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    files = {}
    for v, (dark, accent, text, bg) in VARIANTS.items():
        files[f"waregro-horizontal-{v}.svg"] = horizontal(dark, accent, text, bg)
        files[f"waregro-stacked-{v}.svg"] = stacked(dark, accent, text, bg)
        files[f"waregro-mark-{v}.svg"] = mark_only(dark, accent, bg)
        files[f"waregro-wordmark-latin-{v}.svg"] = wordmark_latin(text, bg)
        files[f"waregro-wordmark-arabic-{v}.svg"] = wordmark_arabic(text, bg)
    files["waregro-app-icon-orange.svg"] = app_icon(WHITE, BROWN, ORANGE)
    files["waregro-app-icon-linen.svg"] = app_icon(BROWN, ORANGE, LINEN)
    files["waregro-app-icon-brown.svg"] = app_icon(LINEN, ORANGE, BROWN)
    for name, content in files.items():
        (OUT / name).write_text(content, encoding="utf-8")
    print(f"wrote {len(files)} SVGs to {OUT}  (arabic: {ARABIC_TEXT})")


if __name__ == "__main__":
    main()
