import time
from loader.get_info_loader import get_info_loader_
from utils.check_internet import *
from video_media_control.twitch_handle import twitch_handle

def _create_edl_url(video_url, audio_url, duration=None):
    """
    Creates an mpv EDL URL with correct duration syntax.
    Format: !new_stream;%length%url,start_offset,duration_length
    """
    
    def _format_segment(url, duration_sec):
        escaped_url = f"%{len(url)}%{url}"
        if duration_sec and duration_sec > 0:
            return f"{escaped_url},0,{duration_sec}"
        else:
            return escaped_url

    parts = [
        # --- VIDEO TRACK ---
        "!new_stream",     
        "!no_chapters",    
        _format_segment(video_url, duration),
        
        # --- AUDIO TRACK ---
        "!new_stream",     
        "!no_chapters",
        _format_segment(audio_url, duration)
    ]
    

    return "edl://" + ";".join(parts)

@check_internet
def get_info(
             target_url:str,
             loader:get_info_loader_,
             twitch_handler:twitch_handle=None
             )->tuple[str,dict]:
    '''
    Returns (final_url, info_dict)
    For non-live YouTube with separate video+audio DASH streams, final_url is an EDL URL.
    For single-stream or live, final_url is the direct stream URL.
    '''
    yt_dlp = loader.yt_dlp
    maxres = loader.maxresolution
    deno_path = loader.deno_exe
    log_handler = loader.ytdlp_log_handle
    cookie = loader.cookie
    if cookie:
        log_handler.info(f"Using cookie file ")

    fmt = (
    f"(bv*[height<={maxres}][protocol=https]+ba[protocol=https][ext=m4a])"
    f"/(bv*[height<={maxres}][protocol!=m3u8_native]+ba[protocol!=m3u8_native])"
    f"/(bv*[height<={maxres}][protocol!=m3u8_native]+ba[protocol!=m3u8_native])/b[height<={maxres}]"
    )

    
    ydl_opts = {
        "verbose": True,
        "skip_download": True,
        "ignoreerrors": True,
        "no_color": True,
        "extract_flat": False,
        "logger": log_handler,
        "format": fmt,
        "extractor_args": {
            "youtube": {
                "player_client": ["default", "-android_vr","web_embedded"],
                },
            },
        "js_runtimes": {
            "deno": {"path": deno_path},
        },
        "remote_components": ["ejs:npm"],   

    }
    
    final_url = None
    vid_url = None
    audio_only_url = None

    if "youtube" in target_url:
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                if cookie:
                    scoped_cookie = "; ".join(
                        f"{part.strip()}; Domain=.youtube.com; Path=/; Secure"
                        for part in cookie.split(";") if "=" in part
                    )
                    ydl._load_cookies(scoped_cookie, autoscope=False)
                info = ydl.extract_info(target_url)
                
                if not info:
                    log_handler.error(f'Failed to extract info for {target_url}')
                    return None, {}


                
                available_time = max((fmt.get("available_at",0)
                                     for fmt in info.get('requested_formats', [])),default=0)
                wait_time = available_time - time.time()
                if wait_time > 0:
                    log_handler.info(f"Waiting for {wait_time:.2f} s till avail")
                    time.sleep(wait_time)
                

                if info['live_status'] != 'is_live' and 'requested_formats' in info:
                    fmt = info['requested_formats']
                    if len(fmt) == 2:
                        vid_url = fmt[0]['url']
                        audio_only_url = fmt[1]['url']
                        log_handler.info(f"video formats:\n fps:{fmt[0].get('fps','N/A')}, res:{fmt[0].get('resolution','N/A')}, vcodec:{fmt[0].get('vcodec','N/A')}, tbr:{fmt[0].get('tbr','N/A')}\n audio format: acodec:{fmt[1].get('acodec','N/A')}, abr:{fmt[1].get('abr','N/A')}, fmt {fmt[1].get('container','N/A')}")
                        final_url = _create_edl_url(vid_url, audio_only_url, info.get('duration',''))
                        
                    else:
                        final_url = info['url']
                else:
                    selected_url = info["url"]

                    final_url = (
                        f"edl://!new_stream;!no_clip;!no_chapters;"
                        f"%{len(selected_url)}%{selected_url}"
                    )
            
                print('vid_url:', vid_url,'\n')
                print('audio_only_url:', audio_only_url)

            log_handler.info(f'get_info return { final_url}')
            return final_url, info
        except Exception as e:
            log_handler.error(f'get_info error: {e}')
            return None, {}
        


    elif "twitch" in target_url:
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(target_url, download=True)
                if not info:
                    log_handler.error(f'Failed to extract info for {target_url}')
                    return None, {}
                if info.get('live_status', 'not_live') != 'is_live' and 'requested_formats' in info:
                    fmt = info['requested_formats']
                    if len(fmt) == 2:
                        vid_url = fmt[0]['url']
                        audio_only_url = fmt[1]['url']
                        log_handler.info(f"video formats:\n fps:{fmt[0].get('fps','N/A')}, res:{fmt[0].get('resolution','N/A')}, vcodec:{fmt[0].get('vcodec','N/A')}, tbr:{fmt[0].get('tbr','N/A')}\n audio format: acodec:{fmt[1].get('acodec','N/A')}, abr:{fmt[1].get('abr','N/A')}")
                        
                else:
                    fmt = info.get('formats', [])
                    if fmt:
                        fmt = sorted(fmt,key = lambda x: x.get('height',0) or 0, reverse=True)
                        for f in fmt:
                            if f.get('height',0) <= maxres:
                                break
            
                print('vid_url:', vid_url,'\n')
                print('audio_only_url:', audio_only_url)

            if twitch_handler and "videos" not in target_url:
                streamlink_url = twitch_handler.start_twitch_streamlink(target_url)
            else:
                streamlink_url = target_url

            yt_like_info = {
                'title': info.get('title'),
                'uploader': info.get('uploader'),
                'thumbnail': info.get('thumbnail'),
                'tags': info.get('uploader'),# Twitch API doesn't provide tags in the same way YouTube does, so we'll just use uploader name as a placeholder
                'subtitles': {},# Twitch API doesn't provide subtitles in the same way YouTube does, so we'll leave this empty
                'live_status': info.get('live_status', False),
                'channel': info.get('uploader'),
                'uploader_id': info.get('uploader_id'),
                'upload_date': info.get('upload_date'),
                'original_url': info.get('original_url'),
                'description': info.get('description'),
            }
            cookie = None
            return streamlink_url, yt_like_info
        except Exception as e:
            log_handler.error(f'get_info error: {e}')
            return None, {}
        



@check_internet
def get_resoltion(target_url:str,
                loader:get_info_loader_,
                )->tuple[str,dict]:
    
    yt_dlp = loader.yt_dlp
    deno_path = loader.deno_exe
    log_handler = loader.ytdlp_log_handle
    cookie = loader.cookie
    try:
        opt = {'quiet': True,
               'skip_download':True,
               "extract_flat": True,
               'ignore_no_formats_error': True,
               'logger': log_handler,
               'js-runtimes':f'deno:{deno_path}' 
               } 
        with yt_dlp.YoutubeDL(opt) as ydl:
            if cookie:
                scoped_cookie = "; ".join(
                    f"{part.strip()}; Domain=.youtube.com; Path=/; Secure"
                    for part in cookie.split(";") if "=" in part
                )
                ydl._load_cookies(scoped_cookie, autoscope=False)
            info = ydl.extract_info(target_url, download=False)
            
        res = []
        for format_info in info['formats']:
            # Check for video formats only
            if format_info.get('vcodec', 'none') != 'none':
                height = format_info.get('height')
                if height and isinstance(height, int):
                    res.append(str(height))
                elif format_info.get('format_note'):
                    # Parse resolution from format_note
                    try:
                        note = format_info.get('format_note', '')
                        if 'p' in note:
                            res_str = note.split('p')[0]
                            if res_str.isdigit():
                                res.append(str(res_str))
                    except (ValueError, IndexError):
                        continue
        
        # Remove duplicates and sort
        res = sorted(list(set(res)))
        
        # Return default if no resolutions found
        if not res:
            log_handler.info("No valid resolutions found, returning defaults")
            return ["480", "720", "1080", "1440", "2160"]
        
        return res
    except Exception as e:
        log_handler.info(f"Error in get_resoltion: {e}")
        # Return default resolutions on any error
        return ["480", "720", "1080", "1440", "2160"]

