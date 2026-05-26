import io

import qrcode
import qrcode.image.svg
from PIL import Image
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.moduledrawers.pil import (
    CircleModuleDrawer,
    RoundedModuleDrawer,
    SquareModuleDrawer,
)

DRAWER_MAP = {
    "square": SquareModuleDrawer,
    "rounded": RoundedModuleDrawer,
    "circle": CircleModuleDrawer,
}


def hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4))


def create_qr_image(
    data: str,
    fg_color: str = "#7c3aed",
    bg_color: str = "#0f1117",
    size: int = 512,
    error_correction: str = "H",
    module_style: str = "square",
    logo_data: bytes | None = None,
    logo_size_pct: int = 20,
) -> Image.Image:
    ec_map = {
        "L": qrcode.constants.ERROR_CORRECT_L,
        "M": qrcode.constants.ERROR_CORRECT_M,
        "Q": qrcode.constants.ERROR_CORRECT_Q,
        "H": qrcode.constants.ERROR_CORRECT_H,
    }
    ec_level = ec_map.get(error_correction, qrcode.constants.ERROR_CORRECT_H)

    qr = qrcode.QRCode(
        version=None,
        error_correction=ec_level,
        box_size=10,
        border=2,
    )
    qr.add_data(data)
    qr.make(fit=True)

    fg_rgb = hex_to_rgb(fg_color)
    bg_rgb = hex_to_rgb(bg_color)

    drawer_cls = DRAWER_MAP.get(module_style, SquareModuleDrawer)

    img = qr.make_image(
        image_factory=StyledPilImage,
        module_drawer=drawer_cls(),
        fill_color=fg_rgb,
        back_color=bg_rgb,
    )
    img = img.convert("RGBA")

    img = img.resize((size, size), Image.Resampling.LANCZOS)

    if logo_data:
        logo_img = Image.open(io.BytesIO(logo_data)).convert("RGBA")
        logo_dim = int(size * logo_size_pct / 100)

        logo_img = logo_img.resize((logo_dim, logo_dim), Image.Resampling.LANCZOS)

        pad = int(logo_dim * 0.12)
        bg_dim = logo_dim + pad * 2
        logo_bg = Image.new("RGBA", (bg_dim, bg_dim), (*bg_rgb, 255))

        logo_bg.paste(logo_img, (pad, pad), logo_img)

        pos = ((size - bg_dim) // 2, (size - bg_dim) // 2)
        img.paste(logo_bg, pos, logo_bg)

    return img


def create_qr_svg(
    data: str,
    fg_color: str = "#7c3aed",
    bg_color: str = "#0f1117",
    size: int = 512,
    error_correction: str = "H",
) -> str:
    ec_map = {
        "L": qrcode.constants.ERROR_CORRECT_L,
        "M": qrcode.constants.ERROR_CORRECT_M,
        "Q": qrcode.constants.ERROR_CORRECT_Q,
        "H": qrcode.constants.ERROR_CORRECT_H,
    }
    ec_level = ec_map.get(error_correction, qrcode.constants.ERROR_CORRECT_H)

    factory = qrcode.image.svg.SvgPathImage
    qr = qrcode.QRCode(
        version=None,
        error_correction=ec_level,
        box_size=10,
        border=2,
    )
    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(
        image_factory=factory,
        fill_color=fg_color,
        back_color=bg_color,
    )

    buffer = io.BytesIO()
    img.save(buffer)
    return buffer.getvalue().decode("utf-8")


