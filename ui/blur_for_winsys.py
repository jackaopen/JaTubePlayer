#source: https://github.com/Peticali/PythonBlurBehind/blob/main/blurWindow/blurWindow.py
import ctypes
from ctypes.wintypes import  HWND

user32 = ctypes.windll.user32
dwm = ctypes.windll.dwmapi


class ACCENTPOLICY(ctypes.Structure):#real data structure
    _fields_ = [
        ("AccentState", ctypes.c_uint),
        ("AccentFlags", ctypes.c_uint),
        ("GradientColor", ctypes.c_uint),
        ("AnimationId", ctypes.c_uint)
    ]


class WINDOWCOMPOSITIONATTRIBDATA(ctypes.Structure):#def wat type will be passed
    _fields_ = [
        ("Attribute", ctypes.c_int),
        ("Data", ctypes.POINTER(ctypes.c_int)),
        ("SizeOfData", ctypes.c_size_t)
    ]


SetWindowCompositionAttribute = user32.SetWindowCompositionAttribute # api call
SetWindowCompositionAttribute.argtypes = (HWND, WINDOWCOMPOSITIONATTRIBDATA) # arg types
SetWindowCompositionAttribute.restype = ctypes.c_int # return type

def _HEXtoRGBAint(HEX:str):
    alpha = HEX[7:]
    blue = HEX[5:7]
    green = HEX[3:5]
    red = HEX[1:3]

    gradientColor = alpha + blue + green + red
    return int(gradientColor, base=16)



def blur(hwnd, hexColor: bool = False, Acrylic: bool = False, Dark: bool = False, disable: bool = False):
    accent = ACCENTPOLICY()
    if not disable:
        accent.AccentState = 3 #Default window Blur #ACCENT_ENABLE_BLURBEHIND

        gradientColor = 0
        
        if hexColor != False:
            gradientColor = _HEXtoRGBAint(hexColor)
            accent.AccentFlags = 2 #Window Blur With Accent Color #ACCENT_ENABLE_TRANSPARENTGRADIENT
        
        if Acrylic:
            accent.AccentState = 4 #UWP but LAG #ACCENT_ENABLE_ACRYLICBLURBEHIND
            if hexColor == False: #UWP without color is translucent
                accent.AccentFlags = 2
                gradientColor = _HEXtoRGBAint('#12121240') #placeholder color
        
        accent.GradientColor = gradientColor
    else:
        accent.AccentState = 0 #disable blur
    
    data = WINDOWCOMPOSITIONATTRIBDATA()
    data.Attribute = 19 #WCA_ACCENT_POLICY
    data.SizeOfData = ctypes.sizeof(accent)
    data.Data = ctypes.cast(ctypes.pointer(accent), ctypes.POINTER(ctypes.c_int))

    SetWindowCompositionAttribute(int(hwnd), data)#really call the api

    if Dark:
        data.Attribute = 26 #WCA_USEDARKMODECOLORS
        SetWindowCompositionAttribute(int(hwnd), data)

