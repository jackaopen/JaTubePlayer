import ctypes
from ctypes import wintypes

# Enable DPI awareness so we get the real DPI value
def get_window_dpi(hwnd):
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(2)  # Per-monitor DPI awareness
    except:
        pass
    dpi_x = ctypes.windll.user32.GetDpiForWindow(wintypes.HWND(hwnd))  # LOGPIXELSX = 88
    dpi_scaling = dpi_x / 96  # Convert DPI to percentage scaling
    print(dpi_scaling)
    return dpi_scaling
##### code from chatgpt not me bc idk ctype :>>>>>