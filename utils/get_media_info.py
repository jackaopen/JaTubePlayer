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
        "!no_clip",        
        "!no_chapters",    
        _format_segment(video_url, duration),
        
        # --- AUDIO TRACK ---
        "!new_stream",     
        "!no_clip", 
        "!no_chapters",
        _format_segment(audio_url, duration)
    ]
    

    return "edl://" + ";".join(parts)


def get_info(yt_dlp:object,
             maxres:int,
             target_url:str,
             deno_path:str,
             log_handler:object,
             cookie_path:str=None)->tuple[str,dict]:
    '''
    Returns (final_url, info_dict)
    if normal dash formats are available, final_url will be m3u8 url
    if only separate video and audio formats are available, final_url will be an EDL URL
    '''
    
    ydl_opts = { 
        'skip_download': True,
        'ignoreerrors': True,
        'no_color': True,
        'extract_flat': False,  
        'logger': log_handler,
        'format': f"bv*[height<={maxres}]+ba/best",
        'js-runtimes': f'deno:{deno_path}',
    }
    
    if cookie_path:
        ydl_opts['cookiefile'] =  cookie_path
    log_handler.info(f'get_info called with {target_url}\n yt_dlp version: {yt_dlp.version}\n maxres: {maxres}\n cookie_path: {cookie_path}\n deno: {deno_path}')

    final_url = None
    vid_url = None
    audio_only_url = None

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(target_url, download=True)
            if info['live_status'] != 'is_live' and 'requested_formats' in info:
                fmt = info['requested_formats']
                if len(fmt) == 2:
                    vid_url = fmt[0]['url']
                    audio_only_url = fmt[1]['url']
                    log_handler.info(f"video formats:\n fps:{fmt[0].get('fps','N/A')}, res:{fmt[0].get('resolution','N/A')}, vcodec:{fmt[0].get('vcodec','N/A')}, tbr:{fmt[0].get('tbr','N/A')}\n audio format: acodec:{fmt[1].get('acodec','N/A')}, abr:{fmt[1].get('abr','N/A')}")
                    final_url = _create_edl_url(vid_url, audio_only_url, info.get('duration',''))
                else:
                    final_url = info['url']
            else:
                fmt = info.get('formats', [])
                if fmt:
                    fmt = sorted(fmt,key = lambda x: x.get('height',0) or 0, reverse=True)
                    for f in fmt:
                        if f.get('height',0) <= maxres:
                            final_url = f'edl://!new_stream;!no_clip;!no_chapters;%{len(f["url"])}%{f["url"]}'
                            break
        
            print('vid_url:', vid_url,'\n')
            print('audio_only_url:', audio_only_url)

        log_handler.info(f'get_info return { final_url}')
        return final_url, info
    except Exception as e:
        log_handler.error(f'get_info error: {e}')
        return None, None