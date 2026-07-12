
import hashlib
import json
import re
import time
import requests
from Account import account_handle



class innertube_handle:
    def __init__(self,
                 account_handle : account_handle,
                 log_handle:object):
        
        self.ORIGIN = "https://www.youtube.com"
        self.UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/126 Safari/537.36"
        self.PAGES = {
                "home": ("FEwhat_to_watch", f"{self.ORIGIN}/"),
                "recommendations": ("FEwhat_to_watch", f"{self.ORIGIN}/"),
                "subscriptions": ("FEsubscriptions", f"{self.ORIGIN}/feed/subscriptions"),
                "history": ("FEhistory", f"{self.ORIGIN}/feed/history"),
                "liked": ("VLLL", f"{self.ORIGIN}/playlist?list=LL"),
                "playlists": (None, f"{self.ORIGIN}/feed/playlists"),
            }
        self.account_handle = account_handle
        self.log_handle = log_handle
        self.request_session = requests.Session()


        self.cfg = None
        self.version = None
        self.referer = None 
        '''
        Normal YouTube page URL related to the Innertube request.
        This is sent as the HTTP Referer header for youtubei/v1/browse.

        Examples:
        - Home/recommendations: https://www.youtube.com/
        - Subscriptions:        https://www.youtube.com/feed/subscriptions
        - History:              https://www.youtube.com/feed/history
        - Liked videos:         https://www.youtube.com/playlist?list=LL
        - Watch later:          https://www.youtube.com/playlist?list=WL
        - Normal playlist:      https://www.youtube.com/playlist?list=<playlist_id>
        - Playlists:            https://www.youtube.com/feed/playlists
        '''
        self.browse_id = None
        '''
        - Home/recommendations -> FEwhat_to_watch
        - Subscriptions        -> FEsubscriptions
        - History              -> FEhistory
        - Liked videos         -> VLLL
        - Watch later          -> VLWL
        - Playlist PL[abc]     -> VLPL[abc]
        - Playlists             -> None
        '''
        self.innertube_api_key = None
        self.api_headers = None
        self.continuation = None

    def _auth(self,cookie):
        '''
        Extract authorization header from cookie for YouTube requests
        '''
        jar = dict(part.strip().split("=", 1) for part in cookie.split(";") if "=" in part)
        now = str(int(time.time()))
        pairs = (
            ("SAPISIDHASH", "SAPISID"),
            ("SAPISID1PHASH", "__Secure-1PAPISID"),
            ("SAPISID3PHASH", "__Secure-3PAPISID"),
        )
        return " ".join(
            f"{scheme} {now}_{hashlib.sha1(f'{now} {jar[name]} {self.ORIGIN}'.encode()).hexdigest()}"
            for scheme, name in pairs
            if jar.get(name)
        )
    

    def _ytcfg(self,html):
        '''
        Extract  inntertube api key, client version, visitor data, etc.
        '''
        cfg = {}
        decoder = json.JSONDecoder()
        for match in re.finditer(r"ytcfg\.set\(", html):
            try:
                data, _ = decoder.raw_decode(html[match.end():])
                if isinstance(data, dict):
                    cfg.update(data)
            except json.JSONDecodeError:
                pass
        return cfg

    def _get_header(self,
                   option:int,
                   cookie:str, 
                   referer:str,
                   cfg:dict=None, 
                   version:str=None):
        '''
        option: 0 = page, 1 = api
        Build request headers for YouTube requests based on the option and provided parameters
        '''
        header = {
        "Accept-Language": "en-US,en;q=0.9",
        "Cookie": cookie,
        "DNT": "1",
        "Origin": self.ORIGIN,
        "Referer": referer,
        "User-Agent": self.UA,
        "X-Goog-AuthUser": "0",
        "X-Origin": self.ORIGIN,
        }
        if authorization := self._auth(cookie):
            header["Authorization"] = authorization

        if option == 0:
            header.update({
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
                "Sec-Fetch-Dest": "document",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": "same-origin",
                "Sec-Fetch-User": "?1",
                "Upgrade-Insecure-Requests": "1",
                })
    
        elif option == 1:
            if not cfg or not version:
                self.log_handle("cfg or version is None, cannot generate API headers", "error")
                return None
            header.update({
                "Accept": "*/*",
                "Content-Type": "application/json",
                "Sec-Fetch-Dest": "empty",
                "Sec-Fetch-Mode": "same-origin",
                "Sec-Fetch-Site": "same-origin",
                "X-YouTube-Client-Name": str(cfg.get("INNERTUBE_CONTEXT_CLIENT_NAME", "1")),
                "X-YouTube-Client-Version": version,
            })
            if cfg.get("VISITOR_DATA", None):
                header["X-Goog-Visitor-Id"] = cfg["VISITOR_DATA"]
        
        return header


    def _build_payload(self,
                       use_matching_page:bool=False,
                       continuation:str=None,
                       playlist_id:str=None,
                       page:str="home"
                       )->dict:
        '''
        Only build basic payload for innertube requests, additional parameters can be added later
        '''
        cookie = self.account_handle.get_cookie()
        
        if use_matching_page:
            browse_id, referer = (
            (f"VL{playlist_id}", f"{self.ORIGIN}/playlist?list={playlist_id}")
            if playlist_id else self.PAGES.get(page, self.PAGES["home"]))
        
        else:
            referer = f"{self.ORIGIN}/"

        
        response = self.request_session.get(referer, 
                                            headers=self._get_header(0, cookie, referer), 
                                            timeout=20)
        
        response.raise_for_status()
        cfg = self._ytcfg(response.text)

        client = cfg.get("INNERTUBE_CONTEXT", {}).get("client", {})
        version = client.get("clientVersion", cfg.get("INNERTUBE_CLIENT_VERSION", "2.20260706.00.00"))

        payload = {"context": {"client": {
            "clientName": client.get("clientName", "WEB"),
            "clientVersion": version,
            "hl": client.get("hl", cfg.get("HL", "en")),
            "gl": client.get("gl", cfg.get("GL", "US")),
        }}}

        if continuation:
            payload["continuation"] = continuation
        else:
            payload["browseId"] = browse_id
            

        self.cfg, self.version =  cfg, version
        self.referer, self.browse_id = referer, browse_id
        self.innertube_api_key = cfg.get("INNERTUBE_API_KEY")

        self.api_headers = self._get_header(1, cookie, referer, cfg, version)
        return payload

        
    def get_innertube_content(self, 
                              page:str):
        if page not in self.PAGES.keys():
            self.log_handle(f"Page '{page}' is not supported", "error")
            return None
        
        inntertube_URL = f"https://www.youtube.com/youtubei/v1/browse?key={self.innertube_api_key}&prettyPrint=false"
        
        cookie = self.account_handle.get_cookie()
        payload = self._build_payload(use_matching_page=True, page=page)
        self.api_headers = self._get_header(1, cookie, self.referer, self.cfg, self.version)
        
        response = self.request_session.post(
            inntertube_URL,
            headers=self.api_headers,
            json=payload,
            timeout=30,
        )
        if response.status_code != 200:
            self.log_handle(f"Failed to retrieve innertube content for page '{page}': {response.status_code} - {response.text}", "error")
            return None
        print(response.text)
        return response.json()


if __name__ == "__main__":
    import sys
    class _ConsoleMessageBox:
        def showerror_and_wait(self, title, message):
            print(f"{title} ERROR: {message}", file=sys.stderr)

        def showwarning(self, title, message):
            print(f"{title} WARNING: {message}", file=sys.stderr)

    account = account_handle(
        r"C:\Users\yy950\Desktop\JaTubePlayer",
        _ConsoleMessageBox(),
        print,
    )
    print("wowo login omg",account.login_refresh(1))
    log_handle = print
    innertube = innertube_handle(account, log_handle)
    
    # Retrieve content for the 'home' page
    content = innertube.get_innertube_content("home")
    if content:
        print(json.dumps(content, indent=2))
