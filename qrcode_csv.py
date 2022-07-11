from argparse import ArgumentParser
from dataclasses import dataclass
from pathlib import Path
import csv
from qrcode.main import QRCode
import qrcode.constants
from PIL import Image, ImageFont, ImageDraw
from tqdm import tqdm

BOX_COUNT = 21

BOX_SIZE_DEFAULT = 30
TOP_PADDING_DEFAULT = 170
SIDE_PADDING_DEFAULT = 170
BOTTOM_PADDING_DEFAULT = 340
TEXT_SIZE_DEFAULT = 100
TEXT_FONT_DEFAULT = "Arial"
FRONT_COLOR_DEFAULT = "black"
BACKGROUND_COLOR_DEFAULT = "transparent"


@dataclass(frozen=True, kw_only=True)
class Options:
    input_csv_file_path: Path
    output_dir_path: Path
    box_size: int
    top_padding: int
    side_padding: int
    bottom_padding: int
    text_size: int
    text_font: str
    front_color: str
    background_color: str

    @classmethod
    def from_argv(cls):
        parser = ArgumentParser(description="Generate QR code from CSV file")
        parser.add_argument(
            "input_csv_file_path", type=Path, help="Path to a CSV file with the list of labels"
        )
        parser.add_argument(
            "output_dir_path", type=Path, help="Path to a directory to save QR codes"
        )
        parser.add_argument(
            "--box-size",
            type=int,
            default=BOX_SIZE_DEFAULT,
            help="Size of the QR code boxes in pixels",
        )
        parser.add_argument(
            "--top-padding",
            type=int,
            default=TOP_PADDING_DEFAULT,
            help="Padding on top of the QR code in pixels",
            dest="top_padding",
        )
        parser.add_argument(
            "--side-padding",
            type=int,
            default=SIDE_PADDING_DEFAULT,
            help="Padding on the sides of the QR code in pixels",
            dest="side_padding",
        )
        parser.add_argument(
            "--bottom-padding",
            type=int,
            default=BOTTOM_PADDING_DEFAULT,
            help="Padding under the QR code in pixels",
            dest="bottom_padding",
        )
        parser.add_argument(
            "--text-size",
            type=int,
            default=TEXT_SIZE_DEFAULT,
            help="Size of the font used to write the text under the QR code",
            dest="text_size",
        )
        parser.add_argument(
            "--text-font",
            type=str,
            default=TEXT_FONT_DEFAULT,
            help="Name of the font used to write the text under the QR code",
            dest="text_font",
        )
        parser.add_argument(
            "--front-color",
            type=str,
            default=FRONT_COLOR_DEFAULT,
            help="Front color of the image",
            dest="front_color",
        )
        parser.add_argument(
            "--background-color",
            type=str,
            default=BACKGROUND_COLOR_DEFAULT,
            help="Background color of the image",
            dest="background_color",
        )
        return cls(**vars(parser.parse_args()))


def make_img(code: str, options: Options):
    qr = QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=BOX_SIZE_DEFAULT,
        border=0,
    )
    qr.add_data(code)
    qr.make(fit=True)
    code_img = qr.make_image(fill_color=options.front_color, back_color=options.background_color)

    code_width = BOX_COUNT * options.box_size
    code_height = BOX_COUNT * options.box_size

    img = Image.new(
        "RGBA",
        (
            code_width + 2 * options.side_padding,
            code_height + options.top_padding + options.bottom_padding,
        ),
        color=options.background_color
        if options.background_color != "transparent"
        else (0, 0, 0, 0),
    )
    img.paste(code_img, (options.side_padding, options.top_padding))

    fnt = ImageFont.truetype(options.text_font, options.text_size)
    d = ImageDraw.Draw(img)

    d.text(
        (
            options.side_padding + code_width / 2,
            options.top_padding + code_height + options.bottom_padding / 2,
        ),
        code,
        font=fnt,
        fill=options.front_color,
        align="center",
        anchor="mm",
    )
    return img


# def resolve_cwd_path(p: Path):
#     if p.is_absolute():
#         return p
#     print(Path.cwd())
#     return Path.cwd() / p


def main():
    options = Options.from_argv()
    with options.input_csv_file_path.resolve().open(mode="r", encoding="utf-8") as input_file:
        codes = [row[0] for row in csv.reader(input_file)]
        for code in tqdm(
            codes,
            total=len(codes),
            unit="qrcode",
        ):
            img = make_img(code, options)
            img.save(options.output_dir_path.resolve() / f"{code}.png")


if __name__ == "__main__":
    main()
