import requests
import re
def get_latest_dlp_version():
    for _ in range(3):
        try:
            response = requests.head('https://github.com/yt-dlp/yt-dlp/releases/latest', timeout=5, allow_redirects=True)
            if response.status_code == 200:
                version = response.url.split('/tag/')[-1]
                return version
        except:
            continue
    return "Unknown"

def get_latest_player_version():
    for _ in range(3):
        try:
            response = requests.head('https://github.com/jackaopen/JaTubePlayer/releases/latest', timeout=5, allow_redirects=True)
            if response.status_code == 200:
                version = response.url.split('/tag/')[-1]
                version = re.sub(r'^v', '', version)  
                return version
        except:
            continue
    return "Unknown"


if __name__ == "__main__":
    import time
    
    for _ in range(100):
        t = time.time()
        print(get_latest_dlp_version())
        print("took", time.time()-t)
