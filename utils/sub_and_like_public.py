from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import json
import googleapiclient.errors
import os ,time,calendar
import aiohttp
import asyncio
import xml.etree.ElementTree as ET
import json

def dump(filename,content):
    with open(filename,'w') as f:        
           json.dump(content,f,indent=4)

async def fetch_feed(session, item):
    url = f'https://www.youtube.com/feeds/videos.xml?channel_id={item}'
    async with session.get(url) as response:
        text = await response.text()
        try:
            root = ET.fromstring(text)
            feed = root.find('{http://www.w3.org/2005/Atom}author')
            print(feed.find('{http://www.w3.org/2005/Atom}name').text)
            for entry in root.findall('{http://www.w3.org/2005/Atom}entry'):
                updated = entry.find('{http://www.w3.org/2005/Atom}updated').text
                epoch = calendar.timegm(time.strptime(updated, "%Y-%m-%dT%H:%M:%S%z"))
                if epoch < time.time():
                    return [item, epoch]
            return [item, 0]
        except:0

async def get_all_feeds(channel_list,main_dir):
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_feed(session, cid) for cid in channel_list]
        result = await asyncio.gather(*tasks)
        result.sort(key=lambda i: i[1], reverse=True)
        dump(os.path.join(main_dir,'user_data', f'sub.json'), result)


def update_sub_list(api,cred,client_secert_path,main_dir)-> bool | str:
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
                asyncio.run(get_all_feeds(list, main_dir=main_dir))
                return True
        except googleapiclient.errors.HttpError as err:return err



def update_like_list(api,cred,client_secert_path,main_dir) -> bool | str:
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
                dump(os.path.join(main_dir,'user_data',f'liked.json'),list)
                return True
        except Exception as e :return e

def liked_channel(main_dir) -> list | str:
    if not os.path.exists(os.path.join(main_dir,'user_data',f'liked.json')):return 'NONE'
    try:
        with open(os.path.join(main_dir,'user_data',f'liked.json')) as liked:list = json.load(liked)
        return list
    except Exception as e :
        print(e)
        return False


def sub_channel(main_dir) -> list | str:
    if not os.path.exists(os.path.join(main_dir,'user_data',f'sub.json')):
        print('sub.json gone')
        return 'NONE'
    try:
        with open(os.path.join(main_dir,'user_data',f'sub.json')) as sub:
            lst = json.load(sub)
            print('get list ')
            ids = [i[0] for i in lst]
            return ids

    except Exception as e :
        print(e)
        return False
    
if __name__ == '__main__':
    lst = ['UCFiIsVOC1p_gfTYDYXXfl4g']
    asyncio.run(get_all_feeds(lst))