import ctypes
from ctypes.wintypes import  HWND
user32 = ctypes.windll.user32
dwm = ctypes.windll.dwmapi

def _HEXtoRGBAint(HEX:str):
    alpha = HEX[7:]
    blue = HEX[5:7]
    green = HEX[3:5]
    red = HEX[1:3]

    gradientColor = alpha + blue + green + red
    return int(gradientColor, base=16)

class ACCENTPOLICY(ctypes.Structure):#real data structure
    _fields_ = [
        ("AccentState", ctypes.c_uint),
        ("AccentFlags", ctypes.c_uint),
        ("GradientColor", ctypes.c_uint),
        ("AnimationId", ctypes.c_uint)
    ]

class WINDOWCOMPOSITIONATTRIBDATA(ctypes.Structure):#def wat type will be passed
    _fields_ = [
        ("Attrib", ctypes.c_int),#WINDOWCOMPOSITIONATTRIB enum
        ("pvData", ctypes.c_void_p),#pointer to data
        ("cbData", ctypes.c_size_t)
    ]

SetWindowCompositionAttribute = user32.SetWindowCompositionAttribute # api call
SetWindowCompositionAttribute.argtypes = (HWND, ctypes.POINTER(WINDOWCOMPOSITIONATTRIBDATA)) # arg types
SetWindowCompositionAttribute.restype = ctypes.c_bool # return type

WCA_ACCENT_POLICY = 19
WCA_USEDARKMODECOLORS = 26
ACCENT_DISABLED = 0
ACCENT_ENABLE_ACRYLICBLURBEHIND = 4
Luminosity_border_glow = 0x2

def blur(hwnd, 
        hexColor: str|None = None,
        disable: bool = False):
    
    accent = ACCENTPOLICY()
    if not disable:
        accent.AccentState = ACCENT_ENABLE_ACRYLICBLURBEHIND
        accent.AccentFlags = Luminosity_border_glow                
        accent.GradientColor = _HEXtoRGBAint(hexColor)
    else:
        accent.AccentState = ACCENT_DISABLED
    
    data = WINDOWCOMPOSITIONATTRIBDATA()
    data.Attrib = WCA_ACCENT_POLICY
    data.cbData = ctypes.sizeof(accent)
    data.pvData = ctypes.cast(ctypes.pointer(accent), ctypes.c_void_p)

    SetWindowCompositionAttribute(int(hwnd), ctypes.byref(data))#really call the api

    data.Attrib = WCA_USEDARKMODECOLORS # apply dark 
    SetWindowCompositionAttribute(int(hwnd), ctypes.byref(data))

