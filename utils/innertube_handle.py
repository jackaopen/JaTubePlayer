
import hashlib
import json
import re
import time
import requests
from account.Account import account_handle

class innertube_handle:
    def __init__(self,
                 account_handle : account_handle,
                 log_handle:object):
        
        self.ORIGIN = "https://www.youtube.com"
        self.UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/126 Safari/537.36"

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
        - Home:                 https://www.youtube.com/
        - Subscriptions:        https://www.youtube.com/feed/subscriptions
        - History:              https://www.youtube.com/feed/history
        - Liked videos:         https://www.youtube.com/playlist?list=LL
        - Watch later:          https://www.youtube.com/playlist?list=WL
        - Normal playlist:      https://www.youtube.com/playlist?list=<playlist_id>
        - Playlists:            https://www.youtube.com/feed/playlists
        '''
        self.browse_id = None
        '''
        - Home                 -> FEwhat_to_watch
        - Subscriptions        -> FEsubscriptions
        - History              -> FEhistory
        - Liked videos         -> VLLL
        - Watch later          -> VLWL
        - Playlist PL[abc]     -> VLPL[abc]
        - Playlists            -> None
        '''
        self.innertube_api_key = None
        self.api_headers = None

    def _build_refer_and_browse_id(self, 
                                page:str,
                                playlist_id:str=None)->tuple[str,str]:
        match page:
            case "home" :
                return "FEwhat_to_watch", f"{self.ORIGIN}/"
            case "subscriptions":
                return "FEsubscriptions", f"{self.ORIGIN}/feed/subscriptions"
            case "history":
                return "FEhistory", f"{self.ORIGIN}/feed/history"
            case "liked":
                return "VLLL", f"{self.ORIGIN}/playlist?list=LL"
            case "playlists":
                return "FEplaylist_aggregation", f"{self.ORIGIN}/feed/playlists"
            case "playlist":
                if playlist_id:
                    return f"VL{playlist_id}", f"{self.ORIGIN}/playlist?list={playlist_id}"
        return None, f"{self.ORIGIN}/"
    

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


    def preInit_buildPayload(self,
                        page:str,
                       use_matching_page:bool=False,
                       playlist_id:str=None,
                       refresh_retry:bool=False

                       )->dict:
        '''
        build payload for innertube requests, additional parameters can be added later\n
        will setup self.cfg, self.version, self.referer, self.browse_id, self.innertube_api_key, self.api_headers\n
        return payload dict\n
        NOTE: DO NOT USE refresh_retry\n
        will refresh cookie if not logged in, and retry once
        '''
        cookie = self.account_handle.get_cookie()
        
        if use_matching_page:
            browse_id, referer = self._build_refer_and_browse_id(page, playlist_id)
        
        else:
            referer = f"{self.ORIGIN}/"

        
        response = self.request_session.get(referer, 
                                            headers=self._get_header(0, cookie, referer), 
                                            timeout=20)
        
        response.raise_for_status()
        cfg = self._ytcfg(response.text)
        if cfg.get("LOGGED_IN") is False:
            if not refresh_retry :
                self.log_handle("refreshing cookie...")
                self.account_handle.login_refresh(1,
                                                should_update_avator=False)

                return self.preInit_buildPayload(use_matching_page=use_matching_page, 
                                                playlist_id=playlist_id, 
                                                page=page,
                                                refresh_retry=True)
            else:
                self.log_handle("Failed to refresh cookie, please check your account status.", "error")
                return None
        
        client = cfg.get("INNERTUBE_CONTEXT", {}).get("client", {})
        version = client.get("clientVersion", cfg.get("INNERTUBE_CLIENT_VERSION", "2.20260706.00.00"))

        payload = {"context": {"client": {
            "clientName": client.get("clientName", "WEB"),
            "clientVersion": version,
            "hl": client.get("hl", cfg.get("HL", "en")),
            "gl": client.get("gl", cfg.get("GL", "US")),
        }}}


        payload["browseId"] = browse_id
            

        self.cfg, self.version =  cfg, version
        self.referer, self.browse_id = referer, browse_id
        self.innertube_api_key = cfg.get("INNERTUBE_API_KEY")
        self.api_headers = self._get_header(1, cookie, referer, cfg, version)

        return payload

    
    def get_innertube_response(self, 
                              payload:dict,
                              get_account:bool=False
                              )->dict|None:
        '''
        send innertube request and return response json, or None if failed
        will need to build payload first using preInit_buildPayload outside
        the preInit_buildPayload will sets up the necessary headers and API key for the request.
        
        '''

        # preInit_buildPayload reads the current API key from the YouTube page.
        if not get_account:
            inntertube_URL = f"https://www.youtube.com/youtubei/v1/browse?key={self.innertube_api_key}&prettyPrint=false"
        else:
            inntertube_URL = (
                            "https://www.youtube.com/youtubei/v1/account/account_menu"
                            f"?key={self.innertube_api_key}"
                            "&prettyPrint=false"
                        )

        response = self.request_session.post(
            inntertube_URL,
            headers=self.api_headers,
            json=payload,
            timeout=30,
        )
        if response.status_code != 200:
            self.log_handle(f"Failed to retrieve innertube content for page '{payload.get('browseId', '_')}': {response.status_code} - {response.text}", "error")
            return None
        
        return response.json()

