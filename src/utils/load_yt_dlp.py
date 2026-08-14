import sys
def load_yt_dlp(_internal_dir: str)-> tuple[object, object, object]|tuple[None, Exception, None]:
    try:
        if _internal_dir not in sys.path:
            sys.path.insert(0, _internal_dir)
        
        import yt_dlp
        from yt_dlp import utils
        from yt_dlp import version as ver
        return yt_dlp, utils, ver
        
    except Exception as e:
        return None, e, None
    