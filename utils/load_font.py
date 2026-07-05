import ctypes
import os

FONT_FILE = "Satisfy-Regular.ttf"

def load_private_font(_internal_dir:str) -> bool:
    font_path = os.path.join(_internal_dir, "fonts", FONT_FILE)

    print(f"Loading private font from: {font_path}")
    FR_PRIVATE = 0x10
    loaded_count = ctypes.windll.gdi32.AddFontResourceExW(
        os.path.abspath(font_path),
        FR_PRIVATE,
        0,
    )
    return loaded_count > 0