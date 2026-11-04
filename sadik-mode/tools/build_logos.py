"""Generate every SADIK MODE logo file (SVG) from one source of truth.

Text is shaped with HarfBuzz and converted to outlines, so the SVGs need no
installed fonts.  Run:  python3 sadik-mode/tools/build_logos.py
"""
from pathlib import Path

import uharfbuzz as hb
from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont

ROOT = Path(__file__).resolve().parents[1]
FONTS = ROOT / "fonts"
OUT = ROOT / "logo" / "svg"

# ---- Brand constants -------------------------------------------------------
NAVY = "#16244F"   # أزرق صادق: trust
GOLD = "#E3A21A"   # ذهبي: value
CREAM = "#FFF6E5"
WHITE = "#FFFFFF"
BLACK = "#111111"

NAME_ARABIC = "صادق مود"
NAME_LATIN = "SADIK MODE"
TAGLINE = "بيجامات وملابس داخلية بالجملة"
ARABIC_FONT = FONTS / "Cairo-900.ttf"
TAGLINE_FONT = FONTS / "Cairo-700.ttf"
LATIN_FONT = FONTS / "Montserrat-800.ttf"

# Mark: a clothes hanger whose hook is drawn as the letter S (Sadik).
STROKE = 26.0
MARK_X0, MARK_Y0, MARK_W, MARK_H = 9.0, -27.0, 382.0, 276.0  # tight box incl. stroke
HOOK = ("M240 6 C230 -8 214 -14 200 -14 C178 -14 162 0 162 18 C162 38 180 46 200 52 "
        "C220 58 238 66 238 86 C238 102 224 112 200 112")
HANGER = "M200 112 L22 236 H378 Z"


def mark_svg(body, hook, s=1.0, ox=0.0, oy=0.0):
    t = f'transform="translate({ox - MARK_X0 * s:.2f},{oy - MARK_Y0 * s:.2f}) scale({s:.4f})"'
    common = f'fill="none" stroke-width="{STROKE}" stroke-linecap="round" stroke-linejoin="round"'
    return (f'<g {t}><path {common} stroke="{hook}" d="{HOOK}"/>'
            f'<path {common} stroke="{body}" d="{HANGER}"/></g>')


# ---- Text to outlines ------------------------------------------------------
class Shaper:
    def __init__(self, path):
        self.font = hb.Font(hb.Face(Path(path).read_bytes()))
        self.tt = TTFont(path)
        self.upem = self.tt["head"].unitsPerEm
        self.glyphset = self.tt.getGlyphSet()
        self.order = self.tt.getGlyphOrder()

    def _shape(self, text, tracking):
        buf = hb.Buffer()
        buf.add_str(text)
        buf.guess_segment_properties()
        hb.shape(self.font, buf, {"kern": True, "liga": True})
        out, x = [], 0
        for info, pos in zip(buf.glyph_infos, buf.glyph_positions):
            out.append((self.order[info.codepoint], x + pos.x_offset, pos.y_offset))
            x += pos.x_advance + tracking
        return out

    def _draw(self, pen, text, size, ox, base, tracking):
        s = size / self.upem
        for name, gx, gy in self._shape(text, tracking):
            self.glyphset[name].draw(TransformPen(pen, (s, 0, 0, -s, ox + gx * s, base - gy * s)))

    def bounds(self, text, size, tracking=0):
        bp = BoundsPen(self.glyphset)
        self._draw(bp, text, size, 0, 0, tracking)
        return bp.bounds  # xmin, ymin, xmax, ymax (y down, baseline 0)

    def block(self, text, size, color, left, top, tracking=0):
        """Path whose ink box starts at (left, top). Returns (svg, width, height)."""
        b = self.bounds(text, size, tracking)
        pen = SVGPathPen(self.glyphset)
        self._draw(pen, text, size, left - b[0], top - b[1], tracking)
        return f'<path fill="{color}" d="{pen.getCommands()}"/>', b[2] - b[0], b[3] - b[1]


AR = Shaper(ARABIC_FONT)
TAG = Shaper(TAGLINE_FONT)
LAT = Shaper(LATIN_FONT)

AR_SIZE = 200.0
_ab = AR.bounds(NAME_ARABIC, AR_SIZE)
AR_W, AR_H = _ab[2] - _ab[0], _ab[3] - _ab[1]


def _fit_tracking(shaper, text, size, width):
    """Letter-spacing so the Latin line is as wide as the Arabic name."""
    lo, hi = 0, 3000
    for _ in range(30):
        mid = (lo + hi) / 2
        b = shaper.bounds(text, size, mid)
        lo, hi = (mid, hi) if b[2] - b[0] < width else (lo, mid)
    return lo


LAT_SIZE = 80.0
LAT_TRACK = _fit_tracking(LAT, NAME_LATIN, LAT_SIZE, AR_W)
TAG_SIZE = 40.0


def text_stack(name_col, latin_col, left, top, tagline_col=None, align_w=None):
    """Arabic name over the Latin name (same width), optional tagline. Returns svg, w, h."""
    w = AR_W
    x = left + ((align_w - w) / 2 if align_w else 0)
    ar, _, arh = AR.block(NAME_ARABIC, AR_SIZE, name_col, x, top)
    y = top + arh + 34
    lat, _, lath = LAT.block(NAME_LATIN, LAT_SIZE, latin_col, x, y, LAT_TRACK)
    y += lath
    parts = [ar, lat]
    if tagline_col:
        tb = TAG.bounds(TAGLINE, TAG_SIZE)
        tw = tb[2] - tb[0]
        size = TAG_SIZE * w / tw
        tw = (tb[2] - tb[0]) * size / TAG_SIZE
        y += 30
        tag, _, tagh = TAG.block(TAGLINE, size, tagline_col, x + (w - tw) / 2, y)
        parts.append(tag)
        y += tagh
    return "\n    ".join(parts), w, y - top


def svg_doc(w, h, body, bg=None, title="SADIK MODE"):
    rect = f'<rect width="100%" height="100%" fill="{bg}"/>\n  ' if bg else ""
    return (f'<?xml version="1.0" encoding="UTF-8"?>\n'
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w:.2f} {h:.2f}" '
            f'width="{w:.0f}" height="{h:.0f}">\n  <title>{title}</title>\n  {rect}'
            f'<g>\n    {body}\n  </g>\n</svg>\n')


PAD = 50.0


def horizontal(v, tagline=False):
    """Arabic-first: text block on the left, mark on the right (reads right to left)."""
    body, hook, name, latin, tag, bg = v
    txt, tw, th = text_stack(name, latin, PAD, PAD, tag if tagline else None)
    mh = th * (0.82 if tagline else 1.0)
    s = mh / MARK_H
    mx = PAD + tw + 70
    my = PAD + (th - mh) / 2
    w = mx + MARK_W * s + PAD
    return svg_doc(w, th + 2 * PAD, txt + "\n    " + mark_svg(body, hook, s, mx, my), bg)


def stacked(v, tagline=False):
    body, hook, name, latin, tag, bg = v
    s = 1.15
    mw, mh = MARK_W * s, MARK_H * s
    w = AR_W + 2 * PAD
    txt, _, th = text_stack(name, latin, PAD, PAD + mh + 60, tag if tagline else None)
    h = PAD + mh + 60 + th + PAD
    return svg_doc(w, h, mark_svg(body, hook, s, (w - mw) / 2, PAD) + "\n    " + txt, bg)


def mark_only(v):
    body, hook, _, _, _, bg = v
    return svg_doc(MARK_W + 2 * PAD, MARK_H + 2 * PAD, mark_svg(body, hook, 1, PAD, PAD), bg)


def wordmark(v):
    _, _, name, latin, _, bg = v
    txt, tw, th = text_stack(name, latin, PAD, PAD)
    return svg_doc(tw + 2 * PAD, th + 2 * PAD, txt, bg)


def profile(bg, body, hook, radius=0.0):
    """Square icon for Instagram / WhatsApp; mark fits inside the circle crop."""
    size = 1080.0
    s = 0.58 * size / MARK_W
    ox, oy = (size - MARK_W * s) / 2, (size - MARK_H * s) / 2 + 10
    rect = f'<rect width="{size}" height="{size}" rx="{size * radius:.0f}" fill="{bg}"/>'
    return svg_doc(size, size, rect + "\n    " + mark_svg(body, hook, s, ox, oy))


VARIANTS = {
    # name: (hanger, hook, arabic name, latin name, tagline, background)
    "primary": (NAVY, GOLD, NAVY, GOLD, NAVY, None),
    "on-cream": (NAVY, GOLD, NAVY, GOLD, NAVY, CREAM),
    "on-navy": (WHITE, GOLD, WHITE, GOLD, CREAM, NAVY),
    "on-gold": (NAVY, WHITE, NAVY, WHITE, NAVY, GOLD),
    "white": (WHITE, WHITE, WHITE, WHITE, WHITE, None),
    "black": (BLACK, BLACK, BLACK, BLACK, BLACK, None),
}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    files = {}
    for k, v in VARIANTS.items():
        files[f"sadik-mode-horizontal-{k}.svg"] = horizontal(v)
        files[f"sadik-mode-horizontal-tagline-{k}.svg"] = horizontal(v, tagline=True)
        files[f"sadik-mode-stacked-{k}.svg"] = stacked(v)
        files[f"sadik-mode-stacked-tagline-{k}.svg"] = stacked(v, tagline=True)
        files[f"sadik-mode-mark-{k}.svg"] = mark_only(v)
        files[f"sadik-mode-wordmark-{k}.svg"] = wordmark(v)
    files["sadik-mode-profile-navy.svg"] = profile(NAVY, WHITE, GOLD)
    files["sadik-mode-profile-gold.svg"] = profile(GOLD, NAVY, WHITE)
    files["sadik-mode-profile-cream.svg"] = profile(CREAM, NAVY, GOLD)
    files["sadik-mode-app-icon.svg"] = profile(NAVY, WHITE, GOLD, radius=0.22)
    for name, content in files.items():
        (OUT / name).write_text(content, encoding="utf-8")
    print(f"wrote {len(files)} SVGs to {OUT}")


if __name__ == "__main__":
    main()
