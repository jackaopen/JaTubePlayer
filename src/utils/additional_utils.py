import math
import urllib.parse
def lenght_convertor(length):
    hour = math.floor(length// 3600)
    min = math.floor(length%3600//60)
    sec = math.floor(length%60)
    return hour,min,sec
def is_url_valid(url):
    '''
    check if the given string is a URL kind (not a local file path), 
    will not check if the URL is valid or reachable
    '''
    try:
        result = urllib.parse.urlparse(url)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False