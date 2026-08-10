import ctypes
from ctypes import wintypes
import copy
from tkinter import Tk

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

def get_effective_scaling(hwnd: int, root: Tk, 
                          base_width: float=1320, base_height: float=680)-> float:
    tkinter_scaling = get_window_dpi(hwnd)
    available_width = int(root.winfo_screenwidth() / tkinter_scaling)*0.95 - 32
    available_height = int(root.winfo_screenheight() / tkinter_scaling)*0.95 - 64

    # DO not oversize the real monitor 
    fit_ratio = min( 
    1.0,
    available_width / base_width,
    available_height / base_height,
    )
    return fit_ratio * tkinter_scaling