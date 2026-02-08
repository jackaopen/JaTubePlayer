def get_info(yt_dlp:object,
             maxres:int,
             target_url:str,
             deno_path:str,
             log_handler:object,
             cookie_path:str=None)->tuple[str,str,dict]:
    '''
    Returns (video_url, audio_url, info_dict)
    if nomral dash formats are available, video_url will be m3u8 url and audio_url will be None
    if only separate video and audio formats are available, video_url and audio_url will be direct urls to the media files
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


    vid_url = None
    audio_only_url = None
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(target_url, download=True)
        fmt = info['formats']#list of dict
        fmt = sorted(fmt,key=lambda x: int(x['height']) if x['height'] else 0,reverse=True)
        
        for f in fmt:
            if not vid_url and f['protocol'] == 'https' and  f['ext'] == 'mp4' and f['audio_ext'] == 'none' and f['vcodec'] != 'none' and f.get('height',0) <= 1080:
                vid_url = f['url']
            if not audio_only_url and f['ext'] == 'm4a' and f['vcodec'] == 'none' and f['acodec'] != 'none' and f['quality'] >= 3.0:
                audio_only_url = f['url']

        if not audio_only_url and not vid_url:
            for f in fmt:
                if f['protocol'] == 'm3u8_native' and f.get('height',0) <= 1080:
                    vid_url = f['url']
                    break
            
    log_handler.info(f'get_info return {vid_url, audio_only_url}')
    
    return vid_url, audio_only_url, info