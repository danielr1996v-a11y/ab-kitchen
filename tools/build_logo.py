#!/usr/bin/env python3
"""Build the נדל״ן נכון logo suite.

Every Hebrew glyph is converted to vector outlines, so the exported files render
identically everywhere and need no font installed. Run from the repo root:

    python3 tools/build_logo.py

Assets land in brand/logo/svg/ ; rasterise them with tools/render_png.js.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from hebrew_text_to_svg import FontRenderer

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONT_DIR = os.environ.get("NN_FONT_DIR", os.path.join(ROOT, "brand", "fonts"))
OUT = os.path.join(ROOT, "brand", "logo", "svg")

# ---------------------------------------------------------------- palette
SLATE = "#39414E"   # primary dark — brand ink and the dark-background fill
DEEP = "#2E3540"    # deeper slate for icon backgrounds
TERRA = "#D2703C"   # warm accent — the closing full stop
BONE = "#EAE7E1"    # off-white for dark backgrounds
MUTED_DARK = "#8C97A4"   # tagline on dark
MUTED_LIGHT = "#6B7583"  # tagline on light

# ------------------------------------------------------- design constants
# All ratios are relative to the wordmark's font size (the design's "em").
TRACKING = 0.06        # open letter-spacing, in em
WORD_GAP = 0.34        # space between נדל״ן and נכון
DOT_SIZE = 0.135       # side of the accent square
DOT_GAP = 0.11         # space between the accent square and נכון
ROOF_OVERHANG = 1.06   # roofline width relative to the wordmark
ROOF_WEIGHT = 0.050    # roofline stroke width
ROOF_PEAK = 0.78       # peak position along the roofline, from its left end
ROOF_RISE = 0.055      # roof height relative to the roofline width
ROOF_DROP = 0.42       # right end height as a fraction of the peak height
ROOF_GAP = 0.34        # space between the roofline and the top of the letters
LETTER_TOP = 0.72      # letter height above the baseline, in em

_cache = {}


def font(weight):
    if weight not in _cache:
        _cache[weight] = FontRenderer(os.path.join(FONT_DIR, f"Assistant-{weight}.ttf"))
    return _cache[weight]


def wordmark(size, fg, accent, weight=300, tracking=TRACKING, dot=True):
    """The two words plus the accent square, laid out RTL from x=0 on a baseline at y=0."""
    f = font(weight)
    right = f.text_to_path("נדל״ן", size=size, tracking=tracking)
    left = f.text_to_path("נכון", size=size, tracking=tracking)
    dot_s = size * DOT_SIZE
    lead = (dot_s + size * DOT_GAP) if dot else 0.0
    width = lead + left.width + size * WORD_GAP + right.width
    parts = []
    if dot:
        parts.append(f'<rect x="0" y="{-dot_s:.2f}" width="{dot_s:.2f}" '
                     f'height="{dot_s:.2f}" fill="{accent}"/>')
    parts.append(f'<g transform="translate({lead:.2f},0)"><path d="{left.d}" fill="{fg}"/></g>')
    parts.append(f'<g transform="translate({lead + left.width + size*WORD_GAP:.2f},0)">'
                 f'<path d="{right.d}" fill="{fg}"/></g>')
    return "".join(parts), width


def roofline(width, fg, weight, peak=ROOF_PEAK, rise=ROOF_RISE, drop=ROOF_DROP):
    """One thin stroke: a long shallow slope to a peak near the right, then a short fall.

    Drawn with the peak at y=0, so the shape hangs below its own origin.
    """
    h = width * rise
    return (f'<path d="M0,{h:.2f} L{width*peak:.2f},0 L{width:.2f},{h*drop:.2f}" '
            f'fill="none" stroke="{fg}" stroke-width="{weight:.2f}" '
            f'stroke-linecap="round" stroke-linejoin="round"/>'), h


def lockup(size, fg, accent, weight=300, roof_weight=ROOF_WEIGHT, tracking=TRACKING,
           tagline=None, tag_fill=MUTED_LIGHT, dot=True):
    """Roofline over the wordmark. Returns (svg body, width, height) with origin at top-left."""
    body, w = wordmark(size, fg, accent, weight=weight, tracking=tracking, dot=dot)
    roof_w = w * ROOF_OVERHANG
    roof, roof_h = roofline(roof_w, fg, size * roof_weight)
    sw = size * roof_weight / 2  # half stroke, so round caps are not clipped
    baseline = sw + roof_h + size * ROOF_GAP + size * LETTER_TOP
    parts = [f'<g transform="translate({(w - roof_w) / 2:.2f},{sw:.2f})">{roof}</g>',
             f'<g transform="translate(0,{baseline:.2f})">{body}</g>']
    height = baseline + size * 0.06
    if tagline:
        t = font(400).text_to_path(tagline, size=size * 0.225, tracking=0.14)
        ty = baseline + size * 0.42
        parts.append(f'<g transform="translate({w - t.width:.2f},{ty:.2f})">'
                     f'<path d="{t.d}" fill="{tag_fill}"/></g>')
        height = ty + size * 0.10
    return "".join(parts), w, height


def stacked(size, fg, accent, weight=300, tagline=None, tag_fill=MUTED_LIGHT):
    """Roofline + נדל״ן on one line, נכון centred beneath it."""
    f = font(weight)
    top = f.text_to_path("נדל״ן", size=size, tracking=TRACKING)
    bottom = f.text_to_path("נכון", size=size * 0.86, tracking=TRACKING + 0.06)
    dot_s = size * DOT_SIZE * 0.9
    bottom_w = bottom.width + dot_s + size * DOT_GAP
    w = max(top.width, bottom_w)
    roof_w = w * ROOF_OVERHANG
    roof, roof_h = roofline(roof_w, fg, size * ROOF_WEIGHT)
    sw = size * ROOF_WEIGHT / 2
    base1 = sw + roof_h + size * ROOF_GAP + size * LETTER_TOP
    base2 = base1 + size * 0.92
    bx = (w - bottom_w) / 2
    parts = [f'<g transform="translate({(w - roof_w)/2:.2f},{sw:.2f})">{roof}</g>',
             f'<g transform="translate({(w - top.width)/2:.2f},{base1:.2f})">'
             f'<path d="{top.d}" fill="{fg}"/></g>',
             f'<rect x="{bx:.2f}" y="{base2 - dot_s:.2f}" width="{dot_s:.2f}" '
             f'height="{dot_s:.2f}" fill="{accent}"/>',
             f'<g transform="translate({bx + dot_s + size*DOT_GAP:.2f},{base2:.2f})">'
             f'<path d="{bottom.d}" fill="{fg}"/></g>']
    height = base2 + size * 0.06
    if tagline:
        t = font(400).text_to_path(tagline, size=size * 0.225, tracking=0.14)
        ty = base2 + size * 0.44
        parts.append(f'<g transform="translate({(w - t.width)/2:.2f},{ty:.2f})">'
                     f'<path d="{t.d}" fill="{tag_fill}"/></g>')
        height = ty + size * 0.10
    return "".join(parts), w, height


def icon_mark(box, fg, accent, weight=400, with_dot=True, with_roof=True, letter=54):
    """Compact mark for avatars: the roofline sheltering a single נ.

    Drawn inside a `box`×`box` square and optically centred on the inked extent
    of the whole group, not on the type's nominal box.
    """
    unit = box / 100.0
    n = font(weight).text_to_path("נ", size=letter * unit)
    x0, y0, x1, y1 = n.bbox
    dot_s = 7.5 * unit
    dot_gap = 5.5 * unit
    roof_w = 58 * unit
    roof_gap = 12 * unit
    roof, roof_h = roofline(roof_w, fg, 5.5 * unit) if with_roof else ("", 0.0)
    stroke = (5.5 * unit / 2) if with_roof else 0.0

    # total inked height: roof (plus its round cap) + gap + letter
    letter_h = y1 - y0
    group_h = (roof_h + stroke + roof_gap if with_roof else 0) + letter_h
    top = (box - group_h) / 2
    ny = top + (roof_h + stroke + roof_gap if with_roof else 0) - y0

    # centre the letter and its dot together, so the pair sits optically centred
    ink_w = (x1 - x0) + (dot_s + dot_gap if with_dot else 0)
    nx = (box - ink_w) / 2 - x0 + (dot_s + dot_gap if with_dot else 0)
    parts = []
    if with_roof:
        parts.append(f'<g transform="translate({(box - roof_w)/2:.2f},{top + stroke:.2f})">{roof}</g>')
    parts.append(f'<g transform="translate({nx:.2f},{ny:.2f})"><path d="{n.d}" fill="{fg}"/></g>')
    if with_dot:
        parts.append(f'<rect x="{nx + x0 - dot_gap - dot_s:.2f}" y="{ny + y1 - dot_s:.2f}" '
                     f'width="{dot_s:.2f}" height="{dot_s:.2f}" fill="{accent}"/>')
    return "".join(parts)


# ---------------------------------------------------------------- writing
def svg(width, height, body, bg=None, pad=0):
    w, h = width + pad * 2, height + pad * 2
    rect = f'<rect width="{w:.2f}" height="{h:.2f}" fill="{bg}"/>' if bg else ""
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w:.2f}" height="{h:.2f}" '
            f'viewBox="0 0 {w:.2f} {h:.2f}" role="img" aria-label="נדל״ן נכון">'
            f'{rect}<g transform="translate({pad},{pad})">{body}</g></svg>')


def write(name, content):
    os.makedirs(OUT, exist_ok=True)
    path = os.path.join(OUT, name)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(content)
    print(f"  {os.path.relpath(path)}")
    return path


def build():
    SIZE = 100
    PAD = SIZE * 0.34
    TAG = "תיווך והשקעות"

    print("horizontal")
    b, w, h = lockup(SIZE, BONE, TERRA)
    write("logo-horizontal-dark.svg", svg(w, h, b, bg=SLATE, pad=PAD))
    b, w, h = lockup(SIZE, SLATE, TERRA)
    write("logo-horizontal-light.svg", svg(w, h, b, bg="#FFFFFF", pad=PAD))
    write("logo-horizontal-onlight.svg", svg(w, h, b, pad=PAD * 0.2))
    b, w, h = lockup(SIZE, BONE, TERRA)
    write("logo-horizontal-ondark.svg", svg(w, h, b, pad=PAD * 0.2))

    print("horizontal + tagline")
    b, w, h = lockup(SIZE, BONE, TERRA, tagline=TAG, tag_fill=MUTED_DARK)
    write("logo-tagline-dark.svg", svg(w, h, b, bg=SLATE, pad=PAD))
    b, w, h = lockup(SIZE, SLATE, TERRA, tagline=TAG, tag_fill=MUTED_LIGHT)
    write("logo-tagline-light.svg", svg(w, h, b, bg="#FFFFFF", pad=PAD))

    print("stacked")
    b, w, h = stacked(SIZE, BONE, TERRA)
    write("logo-stacked-dark.svg", svg(w, h, b, bg=SLATE, pad=PAD))
    b, w, h = stacked(SIZE, SLATE, TERRA)
    write("logo-stacked-light.svg", svg(w, h, b, bg="#FFFFFF", pad=PAD))

    print("single colour")
    b, w, h = lockup(SIZE, BONE, BONE)
    write("logo-mono-bone.svg", svg(w, h, b, pad=PAD * 0.2))
    b, w, h = lockup(SIZE, SLATE, SLATE)
    write("logo-mono-slate.svg", svg(w, h, b, pad=PAD * 0.2))
    b, w, h = lockup(SIZE, "#000000", "#000000")
    write("logo-mono-black.svg", svg(w, h, b, pad=PAD * 0.2))
    b, w, h = lockup(SIZE, "#FFFFFF", "#FFFFFF")
    write("logo-mono-white.svg", svg(w, h, b, pad=PAD * 0.2))

    print("compact (small sizes: heavier weight, sturdier roof)")
    b, w, h = lockup(SIZE, BONE, TERRA, weight=400, roof_weight=0.065, tracking=0.045)
    write("logo-compact-ondark.svg", svg(w, h, b, pad=PAD * 0.2))
    b, w, h = lockup(SIZE, SLATE, TERRA, weight=400, roof_weight=0.065, tracking=0.045)
    write("logo-compact-onlight.svg", svg(w, h, b, pad=PAD * 0.2))

    print("icon / avatar")
    for name, box, radius, bg, fg in [
        ("icon-square-dark", 512, 96, SLATE, BONE),
        ("icon-square-light", 512, 96, BONE, SLATE),
        ("icon-square-terra", 512, 96, TERRA, BONE),
    ]:
        body = (f'<rect width="{box}" height="{box}" rx="{radius}" fill="{bg}"/>'
                + icon_mark(box, fg, TERRA if bg != TERRA else BONE))
        write(f"{name}.svg", svg(box, box, body))
    body = f'<circle cx="256" cy="256" r="256" fill="{SLATE}"/>' + icon_mark(512, BONE, TERRA)
    write("icon-circle-dark.svg", svg(512, 512, body))
    write("icon-bare-slate.svg", svg(512, 512, icon_mark(512, SLATE, TERRA)))
    write("icon-bare-bone.svg", svg(512, 512, icon_mark(512, BONE, TERRA)))

    print("favicon")
    # Large enough to hold the roof; below ~48px it collapses into a grey smudge,
    # so the small sizes carry the נ monogram alone.
    for name, box, radius in [("favicon-512", 512, 112), ("favicon-180", 180, 40)]:
        body = (f'<rect width="{box}" height="{box}" rx="{radius}" fill="{SLATE}"/>'
                + icon_mark(box, BONE, TERRA, weight=500))
        write(f"{name}.svg", svg(box, box, body))
    for name, box, radius in [("favicon-48", 48, 10), ("favicon-32", 32, 7),
                              ("favicon-16", 16, 3)]:
        body = (f'<rect width="{box}" height="{box}" rx="{radius}" fill="{SLATE}"/>'
                + icon_mark(box, BONE, TERRA, weight=600, with_roof=False,
                            with_dot=box >= 32, letter=62))
        write(f"{name}.svg", svg(box, box, body))

    print("editable (live text — opens in Ploni if you have it installed)")
    write("logo-horizontal-editable.svg", editable(SIZE, SLATE, TERRA))


def editable(size, fg, accent):
    """Live-text version: same layout, but the words stay editable type.

    The font stack asks for Ploni first — with Ploni installed (Canva, Adobe
    Fonts, or a local install) it renders in Ploni. Assistant is embedded as a
    fallback so the file also previews correctly on a machine with neither.
    Ploni's metrics differ from Assistant's, so re-check the roof width and the
    dot position after switching the font.
    """
    import base64

    _, w = wordmark(size, fg, accent)
    roof_w = w * ROOF_OVERHANG
    roof, roof_h = roofline(roof_w, fg, size * ROOF_WEIGHT)
    sw = size * ROOF_WEIGHT / 2
    baseline = sw + roof_h + size * ROOF_GAP + size * LETTER_TOP
    dot_s = size * DOT_SIZE
    pad = size * 0.34
    height = baseline + size * 0.06
    stack = "'Ploni ML v2 AAA','Ploni ML','Ploni','Assistant','Heebo',sans-serif"

    with open(os.path.join(FONT_DIR, "Assistant-300.ttf"), "rb") as fh:
        embedded = base64.b64encode(fh.read()).decode("ascii")
    style = (f'<style>@font-face{{font-family:"Assistant";font-weight:300;font-style:normal;'
             f'src:url(data:font/ttf;base64,{embedded}) format("truetype");}}</style>')

    body = (
        style +
        f'<g transform="translate({(w - roof_w)/2:.2f},{sw:.2f})">{roof}</g>'
        f'<rect x="0" y="{baseline - dot_s:.2f}" width="{dot_s:.2f}" height="{dot_s:.2f}" fill="{accent}"/>'
        # In RTL, "start" is the right-hand edge — anchoring to "end" would send
        # the line off the left of the canvas.
        f'<text x="{w:.2f}" y="{baseline:.2f}" direction="rtl" text-anchor="start" '
        f'font-family="{stack}" font-weight="300" font-size="{size}" '
        f'letter-spacing="{size*TRACKING:.2f}" fill="{fg}">'
        f'נדל״ן נכון</text>'
    )
    return svg(w, height, body, bg="#FFFFFF", pad=pad)


if __name__ == "__main__":
    build()
    print("\ndone →", os.path.relpath(OUT))
