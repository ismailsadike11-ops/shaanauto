"""Generate every SADIK MODE logo file (SVG) from one source of truth.

The emblem is a gold serif S in a Moroccan diamond frame with a needle and
thread (owner's reference, 2026-11-04). Text is shaped with HarfBuzz and
converted to outlines, so the SVGs need no installed fonts.
Run:  python3 sadik-mode/tools/build_logos.py
"""
import math
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
BORDEAUX = "#6E1423"
GOLD = "#C9A45C"      # champagne gold
NEEDLE = "#EAD7A8"
THREAD = "#A3263C"
SLATE = "#1E2230"     # slate navy
CREAM = "#F6EFE6"
WHITE = "#FFFFFF"
BLACK = "#111111"

NAME_LATIN = ("SADIK", "MODE")
NAME_ARABIC = "الصادق مود"
TAGLINE = "بيع فقط بالجملة"
LATIN_FONT = FONTS / "Cinzel-700.ttf"
ARABIC_FONT = FONTS / "Amiri-700.ttf"
TAGLINE_FONT = FONTS / "Cairo-700.ttf"


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
        return bp.bounds

    def block(self, text, size, color, left, top, tracking=0, extra=""):
        """Path whose ink box starts at (left, top). Returns (svg, width, height)."""
        b = self.bounds(text, size, tracking)
        pen = SVGPathPen(self.glyphset)
        self._draw(pen, text, size, left - b[0], top - b[1], tracking)
        return f'<path fill="{color}" {extra} d="{pen.getCommands()}"/>', b[2] - b[0], b[3] - b[1]


LAT = Shaper(LATIN_FONT)
AR = Shaper(ARABIC_FONT)
TAG = Shaper(TAGLINE_FONT)


# ---- Emblem (400 x 400) ----------------------------------------------------
EMB = 400.0


def diamond(r):
    c = EMB / 2
    return f"{c},{c - r} {c + r},{c} {c},{c + r} {c - r},{c}"


def emblem(frame, field, s_col, needle, thread, pattern_col, uid, scale=1.0, ox=0.0, oy=0.0):
    c = EMB / 2
    # 8-point star tile (Moroccan zellige feel), clipped to the inner diamond
    tile = (f'<pattern id="z{uid}" width="40" height="40" patternUnits="userSpaceOnUse">'
            f'<g fill="none" stroke="{pattern_col}" stroke-width="1.3" opacity=".45">'
            '<rect x="10" y="10" width="20" height="20"/>'
            '<rect x="10" y="10" width="20" height="20" transform="rotate(45 20 20)"/>'
            '<path d="M0 0 L10 10 M40 0 L30 10 M0 40 L10 30 M40 40 L30 30"/></g></pattern>'
            f'<clipPath id="c{uid}"><polygon points="{diamond(142)}"/></clipPath>')
    s_svg, sw, sh = LAT.block("S", 210, s_col, 0, 0)
    s_left, s_top = c - sw / 2, c - sh / 2 + 4
    s_svg, _, _ = LAT.block("S", 210, s_col, s_left, s_top,
                            extra=f'stroke="{field}" stroke-width="3" paint-order="stroke"')
    ang = 42
    eye_x = c + 110 * math.sin(math.radians(ang))
    eye_y = c - 110 * math.cos(math.radians(ang))
    needle_svg = (f'<g transform="rotate({ang} {c} {c})">'
                  f'<path d="M200 70 C204 70 206 74 206 80 L203 330 L200 345 L197 330 L194 80 C194 74 196 70 200 70 Z" '
                  f'fill="{needle}" stroke="{field}" stroke-width="2"/>'
                  f'<ellipse cx="200" cy="90" rx="2.4" ry="9" fill="{field}"/></g>')
    thread_svg = (f'<path d="M{eye_x:.1f} {eye_y:.1f} C298 92 344 104 332 140 C322 170 282 162 286 140 '
                  f'C290 120 322 112 352 80" fill="none" stroke="{thread}" stroke-width="3.2" stroke-linecap="round"/>')
    body = (f'<defs>{tile}</defs>'
            f'<polygon points="{diamond(142)}" fill="{field}"/>'
            f'<rect width="{EMB}" height="{EMB}" fill="url(#z{uid})" clip-path="url(#c{uid})"/>'
            f'<polygon points="{diamond(188)}" fill="none" stroke="{frame}" stroke-width="7"/>'
            f'<polygon points="{diamond(166)}" fill="none" stroke="{frame}" stroke-width="2.5"/>'
            f'<polygon points="{diamond(142)}" fill="none" stroke="{frame}" stroke-width="4"/>'
            f'{s_svg}{needle_svg}{thread_svg}')
    return f'<g transform="translate({ox:.2f},{oy:.2f}) scale({scale:.4f})">{body}</g>'


# ---- Lockups ---------------------------------------------------------------
SADIK_SIZE, MODE_SIZE = 200.0, 140.0


def latin_line(color, left, top):
    """'SADIK' large + 'MODE' smaller, sharing the baseline (as in the reference)."""
    b1 = LAT.bounds(NAME_LATIN[0], SADIK_SIZE)
    b2 = LAT.bounds(NAME_LATIN[1], MODE_SIZE)
    h1 = b1[3] - b1[1]
    p1, w1, _ = LAT.block(NAME_LATIN[0], SADIK_SIZE, color, left, top)
    gap = 44
    p2, w2, h2 = LAT.block(NAME_LATIN[1], MODE_SIZE, color, left + w1 + gap, top + h1 - (b2[3] - b2[1]))
    return p1 + p2, w1 + gap + w2, h1


def arabic_line(shaper, text, color, center_x, top, width, size):
    b = shaper.bounds(text, size)
    w = b[2] - b[0]
    if w > width:
        size *= width / w
        b = shaper.bounds(text, size)
        w = b[2] - b[0]
    p, _, h = shaper.block(text, size, color, center_x - w / 2, top)
    return p, h


def text_block(latin, arabic, tag, left, top, with_arabic):
    lat, w, h = latin_line(latin, left, top)
    y = top + h + 36
    parts = [lat]
    if with_arabic:
        ar, arh = arabic_line(AR, NAME_ARABIC, arabic, left + w / 2, y, w * 0.62, 96)
        parts.append(ar)
        y += arh + 26
    tg, tgh = arabic_line(TAG, TAGLINE, tag, left + w / 2, y, w * 0.55, 70)
    parts.append(tg)
    y += tgh
    return "".join(parts), w, y - top


def svg_doc(w, h, body, bg=None, title="SADIK MODE"):
    rect = f'<rect width="100%" height="100%" fill="{bg}"/>' if bg else ""
    return (f'<?xml version="1.0" encoding="UTF-8"?>\n'
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w:.2f} {h:.2f}" '
            f'width="{w:.0f}" height="{h:.0f}">\n  <title>{title}</title>\n  {rect}\n  {body}\n</svg>\n')


PAD = 60.0


def horizontal(v, uid, with_arabic=False):
    em, txt = v["emblem"], v["text"]
    tb, tw, th = text_block(*txt, PAD, 0, with_arabic)
    eh = max(th * 1.55, 420)
    h = eh + 2 * PAD
    ty = (h - th) / 2
    tb, tw, th = text_block(*txt, PAD, ty, with_arabic)
    ex = PAD + tw + 80
    body = tb + emblem(*em, uid, eh / EMB, ex, PAD)
    return svg_doc(ex + eh + PAD, h, body, v["bg"])


def stacked(v, uid, with_arabic=False):
    em, txt = v["emblem"], v["text"]
    _, tw, _ = latin_line(txt[0], 0, 0)
    w = tw + 2 * PAD
    es = 560.0
    tb, _, th = text_block(*txt, PAD, PAD + es + 50, with_arabic)
    body = emblem(*em, uid, es / EMB, (w - es) / 2, PAD) + tb
    return svg_doc(w, PAD + es + 50 + th + PAD, body, v["bg"])


def emblem_only(v, uid):
    return svg_doc(EMB + 40, EMB + 40, emblem(*v["emblem"], uid, 1, 20, 20), v["bg"])


def profile(v, uid):
    size = 1080.0
    es = size * 0.8
    return svg_doc(size, size, emblem(*v["emblem"], uid, es / EMB, (size - es) / 2, (size - es) / 2),
                   v["bg"] or CREAM)


def wordmark(v):
    tb, tw, th = text_block(*v["text"], PAD, PAD, False)
    return svg_doc(tw + 2 * PAD, th + 2 * PAD, tb, v["bg"])


# emblem colours: (frame, field, S, needle, thread, pattern); text: (latin, arabic, tagline)
FULL = (GOLD, BORDEAUX, GOLD, NEEDLE, THREAD, GOLD)
VARIANTS = {
    "primary": {"emblem": FULL, "text": (BORDEAUX, BORDEAUX, GOLD), "bg": None},
    "on-cream": {"emblem": FULL, "text": (BORDEAUX, BORDEAUX, GOLD), "bg": CREAM},
    "on-slate": {"emblem": FULL, "text": ("#B23A4E", GOLD, GOLD), "bg": SLATE},
    "on-bordeaux": {"emblem": (GOLD, BORDEAUX, GOLD, NEEDLE, NEEDLE, GOLD), "text": (GOLD, GOLD, CREAM), "bg": BORDEAUX},
    "gold": {"emblem": (GOLD, "none", GOLD, GOLD, GOLD, GOLD), "text": (GOLD, GOLD, GOLD), "bg": None},
    "white": {"emblem": (WHITE, "none", WHITE, WHITE, WHITE, WHITE), "text": (WHITE, WHITE, WHITE), "bg": None},
    "black": {"emblem": (BLACK, "none", BLACK, BLACK, BLACK, BLACK), "text": (BLACK, BLACK, BLACK), "bg": None},
}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for old in OUT.glob("*.svg"):
        old.unlink()
    files = {}
    for i, (k, v) in enumerate(VARIANTS.items()):
        files[f"sadik-mode-horizontal-{k}.svg"] = horizontal(v, f"h{i}")
        files[f"sadik-mode-horizontal-arabic-{k}.svg"] = horizontal(v, f"ha{i}", True)
        files[f"sadik-mode-stacked-{k}.svg"] = stacked(v, f"s{i}")
        files[f"sadik-mode-stacked-arabic-{k}.svg"] = stacked(v, f"sa{i}", True)
        files[f"sadik-mode-emblem-{k}.svg"] = emblem_only(v, f"e{i}")
        files[f"sadik-mode-wordmark-{k}.svg"] = wordmark(v)
    files["sadik-mode-profile-cream.svg"] = profile(VARIANTS["primary"], "p1")
    files["sadik-mode-profile-slate.svg"] = profile(VARIANTS["on-slate"], "p2")
    files["sadik-mode-profile-bordeaux.svg"] = profile(VARIANTS["on-bordeaux"], "p3")
    files["sadik-mode-app-icon.svg"] = profile(VARIANTS["on-slate"], "p4")
    for name, content in files.items():
        (OUT / name).write_text(content, encoding="utf-8")
    print(f"wrote {len(files)} SVGs to {OUT}")


if __name__ == "__main__":
    main()
