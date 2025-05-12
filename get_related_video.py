import json,os,random,time
from concurrent.futures import ThreadPoolExecutor
def _dump(internal_dir,filename,content):
    try:
        with open(os.path.join(internal_dir,f'{filename}.json'),'w') as f:
            json.dump(content,f,indent=4)
    except:pass




def save_recent_vid_info(tag:str,channe_url:str,internal_dir:str) -> None:
    with open(os.path.join(internal_dir,'recent_tag.json'),'a+') as tagfile:        
        try:
            tagfile.seek(0) 
            tags = json.load(tagfile)
        except: tags = []
    tag = tag.strip()
    if tag and tag not in tags:
        if len(tags) == 15:
            tags.pop(0)
        tags.append(tag)
    _dump(internal_dir,'recent_tag',tags)

    with open(os.path.join(internal_dir,'recent_channel_url.json'),'a+') as channelfile:            
        try:
            channelfile.seek(0) 
            channellist = json.load(channelfile)
        except: channellist = []
    if channe_url and channe_url not in channellist:
        if len(channellist) == 15:
            channellist.pop(0)
        channellist.append(channe_url)
    _dump(internal_dir,'recent_channel_url',channellist)

def _search(youtubeDL,query,cookiedir):
    time.sleep(random.uniform(0.5, 4.0))
    ydl_opts = {
            'quiet': True,        
            'extract_flat': True, 
            'skip_download':True
        }   
    if cookiedir:ydl_opts['cookiefile'] = cookiedir

    with youtubeDL(ydl_opts) as ydl:
        result = f"ytsearch10:{query}"
        data = ydl.extract_info(result, download=False)
    return data

def _get_channel_video(youtubeDL,id:str,cookiedir):
    opt = {
        "quiet": True,
        "skip_download": True,
        "extract_flat": "in_playlist",
        "playlistend": 2
    }
    if cookiedir:opt['cookiefile'] = cookiedir
    uploadlist = id.replace("UC","UU",1)
    with youtubeDL(opt) as ydl:
        data = ydl.extract_info(f'https://www.youtube.com/playlist?list={uploadlist}', download=False)
    return data



def get_related_video(youtubeDL:object, internal_dir:str,cookiedir:str=None) -> tuple[list, list, list,list]|None:
   
    with open(os.path.join(internal_dir,'recent_channel_url.json')) as channelfile:tempchaurl = json.load(channelfile)
    with open(os.path.join(internal_dir,'recent_tag.json')) as tagfile:temptag = json.load(tagfile)
    
    if len(temptag) >7:tags = random.sample(temptag,7)
    else:tags = temptag

    if len(tempchaurl) >5:channelurl = random.sample(tempchaurl,5)
    else:channelurl = tempchaurl
   
    title_output,channel_output,url_output,thumbnail = [],[],[],[]
    
    with ThreadPoolExecutor() as executor:
        futures = [executor.submit(_search,youtubeDL,tag,cookiedir) for tag in tags]
        for future in futures:
            try:
                entries = future.result().get("entries")
                random.shuffle(entries)
                alldict = entries[:4]
                for infodict in alldict:
                    try:
                        title = f'🛑LIVE {infodict["title"]}' if infodict['live_status'] == 'is_live' else infodict['title']
                    except:title = infodict["title"]
                    title_output.append(title)                    
                    url_output.append(infodict['url'])
                    channel_output.append(infodict['channel'])
                    thumbnail.append(infodict['thumbnails'][0]['url'])
            except Exception as e:print(e)

    with ThreadPoolExecutor() as executor:
        futures = [executor.submit(_get_channel_video,youtubeDL,url,cookiedir) for url in channelurl]

        for future in futures:
            try:
                alldict = future.result()['entries']
                channel = future.result()['channel']
                for infodict in alldict:
                    if infodict['live_status'] != 'is_upcoming':
                        channel_output.append(channel)
                        try:
                            title = f'🛑LIVE {infodict["title"]}' if infodict['live_status'] == 'is_live' else infodict['title']
                        except:title = infodict["title"]
                        title_output.append(title)
                        url_output.append(infodict['url'])
                        thumbnail.append(infodict['thumbnails'][0]['url'])
            except Exception as e:print('cha',e)

    if title_output != [] and url_output != [] and channel_output != [] and thumbnail != []:return title_output,url_output,channel_output,thumbnail
    else:return None

def init_history(internal_dir:str)->tuple[bool,str]:
    try:
        with open(os.path.join(internal_dir,'recent_tag.json'),'w') as f:pass
        with open(os.path.join(internal_dir,'recent_channel_url.json'),'w') as f:pass
        save_recent_vid_info("nocopyrightsounds royaltyfree copyrightfree ","",internal_dir)
        save_recent_vid_info("futurebass thecalling fatrat ","",internal_dir)
        save_recent_vid_info("","UC16niRr50-MSBwiO3YDb3RA",internal_dir)
        save_recent_vid_info("","UCBi2mrWuNuyYy4gbM6fU18Q",internal_dir)
        save_recent_vid_info("","UC-lHJZR3Gqxm24_Vd_AJ5Yw",internal_dir)
        return True,''
    except Exception as e:return False,e


