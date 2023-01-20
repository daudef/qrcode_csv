from dataclasses import dataclass, field
import datetime
from typing import Any, Iterable, Iterator, TypeVar


_SPECIAL_CHAR_MAP = {
    192: "A",
    193: "A",
    194: "A",
    195: "A",
    196: "A",
    197: "A",
    198: "AE",
    199: "C",
    200: "E",
    201: "E",
    202: "E",
    203: "E",
    204: "I",
    205: "I",
    206: "I",
    207: "I",
    208: "D",
    209: "N",
    210: "O",
    211: "O",
    212: "O",
    213: "O",
    214: "O",
    216: "O",
    217: "U",
    218: "U",
    219: "U",
    220: "U",
    221: "Y",
    223: "B",
    224: "a",
    225: "a",
    226: "a",
    227: "a",
    228: "a",
    229: "a",
    230: "ae",
    231: "c",
    232: "e",
    233: "e",
    234: "e",
    235: "e",
    236: "i",
    237: "i",
    238: "i",
    239: "i",
    241: "n",
    242: "o",
    243: "o",
    244: "o",
    245: "o",
    246: "o",
    249: "u",
    250: "u",
    251: "u",
    252: "u",
    253: "y",
    255: "y",
    338: "OE",
    339: "oe",
    ord("Ÿ"): "Y",
}


def char_to_ascii(char: str):
    ascii_num = ord(char)
    if ascii_num < 192:
        return char
    if (s := _SPECIAL_CHAR_MAP.get(ascii_num)) is not None:
        return s
    return " "


@dataclass(kw_only=True)
class ProgressBar:
    name: str = ""
    total: int
    progress: int = field(default=0, init=False)
    unit: str = ""
    start_time: datetime.datetime = field(default_factory=datetime.datetime.now, init=False)
    rank: int = field(default=0, init=False)

    def __post_init__(self):
        assert self.total != 0

    def __enter__(self):
        if self.name != "":
            print(f"{self.name}:", end="", flush=True)
        print(" 0%", end="", flush=True)
        return self

    def update(self, update: int):
        new_progress = self.progress + update
        new_rank = round(20 * new_progress / self.total)
        if self.rank < new_rank:
            new_rank = min(20, new_rank)
            for i in range(self.rank + 1, new_rank + 1):
                if i % 2 == 0:
                    print(f" {5 * i}%", end="", flush=True)
                else:
                    print(f" .", end="", flush=True)
            self.rank = new_rank
        self.progress = new_progress

    @staticmethod
    def _speed_prefix(speed: float):
        for prefix, value in [("M", 1e6), ("k", 1e3)]:
            if speed > value:
                return prefix, speed / value
        return "", speed

    def __exit__(self, *args: Any):
        seconds = (datetime.datetime.now() - self.start_time).total_seconds()
        prefix, speed = self._speed_prefix(self.progress / seconds)
        print(f" [{seconds:2.2f}s | {speed:2.2f} {prefix}{self.unit or 'it'}/s]")


_T = TypeVar("_T")


def iter_track(
    it: Iterable[_T], name: str | None = None, total: int | None = None, unit: str | None = None
) -> Iterator[_T]:
    name = name or ""
    unit = unit or "iter"
    if total is None:
        if (
            (len := getattr(it, "__len__", None)) is not None
            and callable(len)
            and isinstance(length := len(), int)
        ):
            total = length
        else:
            raise ValueError(f"Cannot find the length of {it}")
    with ProgressBar(name=name, total=total, unit=unit) as pb:
        for e in it:
            yield e
            pb.update(1)
