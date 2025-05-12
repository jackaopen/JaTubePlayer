from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import json
import googleapiclient.errors
from concurrent.futures import ThreadPoolExecutor
import os ,feedparser,time,calendar

modpath = os.path.dirname(os.path.abspath(__file__))
def dump(filename,content):
    with open(filename,'w') as f:        
           json.dump(content,f,indent=4)

def _get_timestamp_info(item:str) -> list:#get timestamp via rss
    feed = feedparser.parse(f'https://www.youtube.com/feeds/videos.xml?channel_id={item}')
    if feed.entries:
        for entry in feed.entries:
            parsed_time = entry.updated_parsed
            epoch_local = calendar.timegm(parsed_time)
            print(entry.title,parsed_time)
            if epoch_local < time.time():return [item,epoch_local]
            
        return[item,0]
    else:return[item,0]
    

def _get_sub_timestamp(channel_list:list):
    with ThreadPoolExecutor() as executor:
        future = [executor.submit(_get_timestamp_info,item) for item in channel_list]
        result = [f.result() for f in future]
    result.sort(key=lambda i : i[1],reverse=True)
    dump(os.path.join(modpath,f'sub.json'),result)


def update_sub_list(api,cred,client_secert_path)-> bool | str:
    npt = None
    list = []
    if cred == None:
        scopes = ["https://www.googleapis.com/auth/youtube.readonly"]
        flow = InstalledAppFlow.from_client_secrets_file(
            client_secert_path, scopes=scopes)
        credentials = flow.run_local_server(port=0)
    else:credentials= cred

    youtube = build('youtube','V3',developerKey=api,static_discovery = False,credentials=credentials)
    while True:
        try:
            subs = youtube.subscriptions().list(part='snippet', mine=True,maxResults=50,pageToken = npt).execute()
            npt = subs.get('nextPageToken')
            for item in subs['items']:
                list.append(item['snippet']['resourceId']['channelId'])
            if not npt:
                _get_sub_timestamp(list)
                return True
        except googleapiclient.errors.HttpError as err:return err



def update_like_list(api,cred,client_secert_path) -> bool | str:
    npt = None
    list = []
    if cred == None:
        scopes = ["https://www.googleapis.com/auth/youtube.readonly"]
        flow = InstalledAppFlow.from_client_secrets_file(
            client_secert_path, scopes=scopes)
        credentials = flow.run_local_server(port=0)
    else:credentials=cred

    youtube = build('youtube','V3',developerKey=api,static_discovery = False,credentials=credentials)
    while True:
        try:
            playlist_response = youtube.playlistItems().list(
                part='snippet',
                playlistId='LL',
                maxResults=100,
                pageToken=npt
            ).execute()
            
            npt = playlist_response.get('nextPageToken')
            for item in playlist_response['items']:
                list.append(f"https://www.youtube.com/watch?v={item['snippet']['resourceId']['videoId']}")
            if not npt:
                dump(os.path.join(modpath,f'liked.json'),list)
                return True
        except Exception as e :return e

def liked_channel() -> list | str:
    if not os.path.exists(os.path.join(modpath,f'liked.json')):return 'NONE'
    try:
        with open(os.path.join(modpath,f'liked.json')) as liked:list = json.load(liked)
        return list
    except Exception as e :
        print(e)
        return False


def sub_channel() -> list | str:
    if not os.path.exists(os.path.join(modpath,f'sub.json')):
        print('sub.json gone')
        return 'NONE'
    try:
        with open(os.path.join(modpath,f'sub.json')) as sub:
            lst = json.load(sub)
            print('get list ')
            ids = [i[0] for i in lst]
            return ids

    except Exception as e :
        print(e)
        return False