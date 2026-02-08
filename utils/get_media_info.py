def get_info(yt_dlp:object,
             maxres:int,
             target_url:str,
             deno_path:str,
             log_handler:object,
             cookie_path:str=None)->dict[str,str,str,dict]:
    
    ydl_opts = { 
        'quiet': True, 
        'skip_download': True,
        'ignoreerrors': True,
        'ignore_no_formats_error': True,
        'no_color': True,
        'extract_flat': False,  
        'logger': log_handler,
        'format': f"bv*[height<={maxres}]+ba/best",
        'js-runtimes': f'deno:{deno_path}',
        'extractor_args': {'youtube': {'skip': ['hls', 'dash']}},
                }
    
    if cookie_path:
        ydl_opts['cookiefile'] =  cookie_path


    m3u8_url = None
    vid_only_url = None
    audio_only_url = None
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(target_url, download=True)
        fmt = info['formats']#list of dict
        fmt = sorted(fmt,key=lambda x: int(x['height']) if x['height'] else 0,reverse=True)
        
        for f in fmt:
            print(f['height'],f['protocol'],f.get('height',0),f['acodec'],f['vcodec'])
            if f['protocol'] == 'm3u8_native' and f.get('height',0) <= 1080:
                m3u8_url = f['url']
                break
                
        if not m3u8_url:
            for f in fmt:
                if not vid_only_url and f['protocol'] == 'https' and f['audio_ext'] == 'none' and f['vcodec'] != 'none' and f.get('height',0) <= 1080:
                    vid_only_url = f['url']
                if not audio_only_url and f['protocol'] == 'https' and f['vcodec'] == 'none' and f['acodec'] != 'none' and f['quality'] >= 3.0:
                    audio_only_url = f['url']
    return m3u8_url, vid_only_url, audio_only_url, info