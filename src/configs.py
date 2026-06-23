from PIL.ImageFont import ImageFont, FreeTypeFont, truetype
from functools import cached_property
from abc import abstractmethod
from pathlib import Path

_PATH_SRC = Path(__file__).parent
_PATH_BASE = _PATH_SRC.parent
PATH_DATA = _PATH_BASE / "data"
PATH_FONT = PATH_DATA / "fonts"

AnyFont = ImageFont | FreeTypeFont

class DrawConfig:
    @property
    @abstractmethod
    def width_px(self) -> int:
        raise NotImplementedError()

    @property
    @abstractmethod
    def gap_text_px(self) -> int:
        raise NotImplementedError()

    @property
    @abstractmethod
    def gap_block_px(self) -> int:
        raise NotImplementedError()

    @abstractmethod
    def get_value_font(self, scale: float = 1.0) -> AnyFont:
        raise NotImplementedError()

    @property
    @abstractmethod
    def font_sub_pre(self) -> AnyFont:
        raise NotImplementedError()

    @property
    def font_sub_pre_offset_px(self) -> int:
        return 0

    @property
    @abstractmethod
    def font_sub(self) -> AnyFont:
        raise NotImplementedError()

    @property
    @abstractmethod
    def path_save(self) -> Path:
        raise NotImplementedError()


class PTouchConfig(DrawConfig):
    @property
    def width_px(self):
        return 64 # 9mm at 180dpi
    
    @property
    def gap_text_px(self):
        return 2
    
    @property
    def gap_block_px(self):
        return 6

    _size_cache: dict[float, AnyFont] = {}

    def get_value_font(self, scale: float = 1.0):
        base_size = 14
        size = base_size * scale
        cls = type(self)

        if size in cls._size_cache:
            return cls._size_cache[size]

        return truetype(PATH_FONT / "Roboto-Bold.ttf", size)

    @cached_property
    def _font_sub_pre(self):
        return truetype(PATH_FONT / "PressStart2P.ttf", 8)

    @property
    def font_sub_pre(self):
        return self._font_sub_pre

    @property
    def font_sub_pre_offset_px(self):
        return 3

    @cached_property
    def _font_sub(self):
        return truetype(PATH_FONT / "Greenscreen.ttf", 12)
    
    @property
    def font_sub(self):
        return self._font_sub

    @property
    def path_save(self):
        return PATH_DATA / "label.png"
