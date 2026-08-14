import math

def lenght_convertor(length):
    hour = math.floor(length// 3600)
    min = math.floor(length%3600//60)
    sec = math.floor(length%60)
    return hour,min,sec