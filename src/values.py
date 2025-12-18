from enum import Enum
from typing import Iterable
from PIL.Image import Image, new as new_image
from PIL.ImageDraw import ImageDraw

from configs import DrawConfig

class Size(list, Enum):
    THT = ["THT"]
    THT_AXIAL = ["THT AXL"]
    THT_RADIAL = ["THT RAD"]

    TO_5 = ["TO-5"]
    TO_92 = ["TO-92"]
    TO_220 = ["TO-220"]
    TO_220_AC = ["TO-220AC"]

    SMD_I01005 = ["I:{01005}", "M:{ 0402}"]
    SMD_I0201 = ["I:{0201}", "M:{0603}"]
    SMD_I0402 = ["I:{0402}", "M:{1005}"]
    SMD_I0603 = ["I:{0603}", "M:{1608}"]
    SMD_I0805 = ["I:{0805}", "M:{2012}"]
    SMD_I1008 = ["I:{1008}", "M:{2520}"]
    SMD_I1206 = ["I:{1206}", "M:{3216}"]
    SMD_I1210 = ["I:{1210}", "M:{3225}"]
    SMD_I1812 = ["I:{1812}", "M:{4532}"]
    SMD_I2010 = ["I:{2010}", "M:{5025}"]
    SMD_I2512 = ["I:{2512}", "M:{6332}"]

    SMD_M0402 = SMD_I01005
    SMD_M0603 = SMD_I0201
    SMD_M1005 = SMD_I0402
    SMD_M1608 = SMD_I0603
    SMD_M2012 = SMD_I0805
    SMD_M2520 = SMD_I1008
    SMD_M3216 = SMD_I1206
    SMD_M3225 = SMD_I1210
    SMD_M4532 = SMD_I1812
    SMD_M5025 = SMD_I2010
    SMD_M6332 = SMD_I2512

    MELF_MMU = ["MELF MMU", "{0102}"]
    MELF_MMA = ["MELF MMA", "{0204}"]
    MELF_MMB = ["MELF MMB", "{0207}"]

    MICRO_MELF = MELF_MMU
    MINI_MELF = MELF_MMA
    MELF = MELF_MMB


class Component:
    def get_image(self, config: DrawConfig) -> Image: ...

class Label(Component):
    def __init__(self, *lines: str, normalize: float=0, align: float=0.5):
        """
        Setting `normalize` will interpolate between all lines having the same font size (1) and all lines being the same width (0).
        Setting `align` will align the lines horizontally: 0 = left, 0.5 = center, 1 = right.
        """
        self.lines = lines
        self.normalize = normalize
        self.align = align

    def get_image(self, config: DrawConfig) -> Image:
        width = config.width_px
        font_default = config.get_value_font()

        scales = []
        for line in self.lines:
            *_, w, h = font_default.getbbox(line)
            scales.append(width / w)

        fsize_scale = min(scales) if scales else 0

        fonts = []
        offsets = []
        height = 0
        for line, width_scale in zip(self.lines, scales):
            scale = self.normalize * fsize_scale + (1 - self.normalize) * width_scale
            font = config.get_value_font(scale)
            *_, w, h = font.getbbox(line)
            if height:
                height += config.gap_text_px
            offsets.append(((width - w) * self.align, height))
            height += h
            fonts.append(font)
            
        img = new_image("1", (width, height), color="white")
        draw = ImageDraw(img)

        for line, font, (x, y) in zip(self.lines, fonts, offsets):
            draw.text((x, y), line, font=font)

        return img

class ValuedComponent(Component):
    def __init__(self, value: str, size: Size):
        self.value = value
        self.size = size

    def get_image(self, config):
        width = config.width_px

        value = self.value
        if self._unit and not value.endswith(self._unit):
            value += self._unit

        font_value = config.get_value_font()
        *_, width_value, height_value = font_value.getbbox(value)
        scale = max(1.0, width / width_value)
        if scale != 1.0:
            font_value = config.get_value_font(scale)
            *_, width_value, height_value = font_value.getbbox(value)

        all_parts = []
        all_widths = []
        all_heights = []

        fonts = [config.font_sub_pre, config.font_sub]
        offsets = [config.font_sub_pre_offset_px, 0]

        for text in self._subtexts:
            parts = self._split_text(text)

            widths = []
            heights = []

            for j, part in enumerate(parts):
                if not part:
                    w, h = 0, 0
                else:
                    *_, w, h = fonts[j%2].getbbox(part)
                    h += offsets[j%2]
                widths.append(w)
                heights.append(h)

            all_parts.append(parts)
            all_widths.append(widths)
            all_heights.append(heights)

        img = new_image("1", (width, height_value + sum(max(h) + config.gap_text_px for h in all_heights)), color="white")
        draw = ImageDraw(img)
        draw.text(((width-width_value)/2, 0), value, font=font_value)

        y = height_value

        for i, (parts, widths, heights) in enumerate(zip(all_parts, all_widths, all_heights)):
            total_width = sum(widths)
            total_height = max(heights)
            x = (width - total_width) / 2
            y += config.gap_text_px

            for j, (part, w, h) in enumerate(zip(parts, widths, heights)):
                if not part:
                    continue

                draw.text((x, y + offsets[j%2]), part, font=fonts[j%2])
                x += w

            y += total_height

        return img

    @property
    def _unit(self) -> str: ...

    @property
    def _subtexts(self) -> Iterable[str]:
        return self.size

    def _split_text(self, text: str) -> Iterable[str]:
        pre, *parts = text.split("{")

        parts = [p for _parts in parts for p in _parts.split("}")]

        return [pre, *parts]

class Resistor(ValuedComponent):
    @property
    def _unit(self):
        return "Ω"

class CapacitorType(str, Enum):
    CERAMIC = "Ceramic"
    ELECTROLYTIC = "E-lyte"
    TANTALUM = "Tantalum"
    POLYPROPYLENE = "PP/MKP"
    MKP = POLYPROPYLENE
    POLYESTER = "PETP/MKT"
    PETP = POLYESTER
    MKT = POLYESTER
    SUPERCAP = "Supercap"
    EDLC = "EDLC"

class Capacitor(ValuedComponent):
    def __init__(self, value: str, size: Size, type: CapacitorType|str|None = None):
        super().__init__(value, size)
        self.type = type

    @property
    def _subtexts(self):
        if self.type:
            return [self.type, *super()._subtexts]
        return super()._subtexts

    @property
    def _unit(self):
        return "F"

class InductorCoreType(str, Enum):
    AIR = "Air"
    FERRITE = "Fer."
    IRON = "Iron"
    POWDER = "Pwd."
    CERAMIC = "Cer."

class InductorType(str, Enum):
    WIREWOUND = "Wiw"
    MULTILAYER = "MLa"
    LAMINATED = "Lam"
    TOROIDAL = "Tor"
    PLANAR = "Pln"


class Inductor(ValuedComponent):
    def __init__(self, value: str, size: Size, core: InductorCoreType|str|None = None, type: InductorType|str|None = None, shielded: bool|None = None):
        super().__init__(value, size)
        self.core = core
        self.type = type
        self.shielded = shielded

    @property
    def _subtexts(self):
        value1 = ""
        value2 = ""
        if self.core:
            value1 += self.core
        if self.type:
            if value1: value1 += "/"
            value1 += self.type

        if self.shielded is not None:
            value2 += "Shielded" if self.shielded else "Unshield"
        
        values = []

        if value1:
            values.append(value1)
        if value2:
            values.append(value2)
        values.extend(super()._subtexts)
        return values

    @property
    def _unit(self):
        return "H"

class Diode(ValuedComponent):
    @property
    def _unit(self):
        return None
