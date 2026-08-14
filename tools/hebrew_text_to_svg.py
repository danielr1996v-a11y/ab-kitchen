"""Convert Hebrew (RTL) text into SVG path data using a TrueType font.

Hebrew needs no complex shaping — final letters are separate code points and
there are no required ligatures — so laying glyphs out right-to-left by their
advance widths is enough. Kerning pairs from the font's GPOS table are applied
when present.

Usage:
    from hebrew_text_to_svg import FontRenderer
    f = FontRenderer("fonts/Assistant-700.ttf")
    text = f.text_to_path("נדל״ן", size=100, tracking=-0.01)
    text.d       # SVG path data, baseline at y=0, text starting at x=0
    text.width   # advance width at the requested size
"""

from dataclasses import dataclass

from fontTools.misc.transform import Transform
from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont


@dataclass
class RenderedText:
    d: str
    width: float
    ascender: float
    descender: float
    cap_height: float
    x_height: float
    bbox: tuple = (0.0, 0.0, 0.0, 0.0)  # inked extent in SVG coords: x0, y0, x1, y1

    @property
    def ink_width(self):
        return self.bbox[2] - self.bbox[0]

    @property
    def ink_height(self):
        return self.bbox[3] - self.bbox[1]


class FontRenderer:
    def __init__(self, path):
        self.path = path
        self.font = TTFont(path)
        self.upem = self.font["head"].unitsPerEm
        self.cmap = self.font.getBestCmap()
        self.glyphs = self.font.getGlyphSet()
        self.hmtx = self.font["hmtx"]
        os2 = self.font["OS/2"]
        self.font_ascender = self.font["hhea"].ascender
        self.font_descender = self.font["hhea"].descender
        self.font_cap_height = getattr(os2, "sCapHeight", None) or int(self.upem * 0.7)
        self.font_x_height = getattr(os2, "sxHeight", None) or int(self.upem * 0.5)
        self._kerning = self._load_kerning()

    def _load_kerning(self):
        """Flatten simple pair-positioning kerning into a {(left, right): value} map."""
        kerning = {}
        if "GPOS" not in self.font:
            return kerning
        try:
            gpos = self.font["GPOS"].table
            for lookup in gpos.LookupList.Lookup:
                if lookup.LookupType != 2:
                    continue
                for sub in lookup.SubTable:
                    if sub.Format == 1:
                        for first, pairset in zip(sub.Coverage.glyphs, sub.PairSet):
                            for record in pairset.PairValueRecord:
                                value = getattr(record.Value1, "XAdvance", 0) or 0
                                if value:
                                    kerning[(first, record.SecondGlyph)] = value
                    elif sub.Format == 2:
                        class1 = sub.ClassDef1.classDefs
                        class2 = sub.ClassDef2.classDefs
                        for first in sub.Coverage.glyphs:
                            c1 = class1.get(first, 0)
                            if c1 >= len(sub.Class1Record):
                                continue
                            record1 = sub.Class1Record[c1]
                            for second, c2 in class2.items():
                                if c2 >= len(record1.Class2Record):
                                    continue
                                value = getattr(record1.Class2Record[c2].Value1, "XAdvance", 0) or 0
                                if value:
                                    kerning.setdefault((first, second), value)
        except (AttributeError, IndexError):
            return {}
        return kerning

    def glyph_name(self, char):
        name = self.cmap.get(ord(char))
        if name is None:
            raise KeyError(f"{self.path} has no glyph for U+{ord(char):04X} ({char!r})")
        return name

    def has(self, char):
        return ord(char) in self.cmap

    def text_to_path(self, text, size=100, tracking=0.0, rtl=True):
        """Render `text` to SVG path data.

        The result sits on a baseline at y=0 and starts at x=0, growing to the
        right in SVG coordinates (y down), regardless of writing direction.
        `tracking` is letter-spacing in em units (0.02 = 2% of the font size).
        """
        scale = size / self.upem
        track_units = tracking * self.upem
        chars = [c for c in text if c != "‏"]
        order = list(reversed(chars)) if rtl else chars

        # Lay out left-to-right in font units; for RTL that means walking the
        # string backwards so the first logical character lands on the right.
        placements = []
        pen_x = 0.0
        for i, char in enumerate(order):
            if char == " ":
                pen_x += self.upem * 0.26 + track_units
                continue
            name = self.glyph_name(char)
            if i > 0:
                prev = placements[-1][0] if placements else None
                if prev is not None:
                    pair = (name, prev) if rtl else (prev, name)
                    pen_x += self._kerning.get(pair, 0)
            placements.append((name, pen_x))
            pen_x += self.hmtx[name][0] + track_units
        total = pen_x - (track_units if placements else 0)

        pieces = []
        bounds = BoundsPen(self.glyphs)
        for name, x in placements:
            pen = SVGPathPen(self.glyphs, ntos=lambda v: f"{v:.2f}")
            transform = Transform(scale, 0, 0, -scale, x * scale, 0)
            self.glyphs[name].draw(TransformPen(pen, transform))
            self.glyphs[name].draw(TransformPen(bounds, transform))
            d = pen.getCommands()
            if d:
                pieces.append(d)

        return RenderedText(
            bbox=bounds.bounds or (0.0, 0.0, 0.0, 0.0),
            d=" ".join(pieces),
            width=total * scale,
            ascender=self.font_ascender * scale,
            descender=self.font_descender * scale,
            cap_height=self.font_cap_height * scale,
            x_height=self.font_x_height * scale,
        )
