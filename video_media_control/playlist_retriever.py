
import json
from utils.innertube_handle import innertube_handle
from account.Account import account_handle
from loader.media_data_list import media_data_list_template
from utils.parser import innertube_parser
import enum


class playlist_type(enum.Enum):
    HOME = "home"
    SUBSCRIPTIONS = "subscriptions"
    HISTORY = "history"
    LIKED = "liked"
    PLAYLISTS = "playlists"
    PLAYLIST = "playlist"


class playlist_retriever_:
    def __init__(self, 
                 innertube_handle: innertube_handle,
                 log_handle: object):
        
        self.innertube_handle = innertube_handle
        self.log_handle = log_handle
        self.maxresults = 100
        self.innertube_parser = innertube_parser()

    def get_playlist_content(self, 
                             page: playlist_type, 
                             playlist_id: str=None)->media_data_list_template|None:
        '''
        page: playlist_type Enum, specify which page to retrieve content from
        '''
        media_data_list = media_data_list_template()
        count = 0
        continuation_token = None
        contiunation_page = False

        if page not in playlist_type:
            self.log_handle(f"Page '{page}' is not supported", "error")
            return None
        else:
            if page in [playlist_type.HOME, playlist_type.SUBSCRIPTIONS, playlist_type.HISTORY]: 
                self.maxresults = 100
            else: 
                self.maxresults = 5000


        
        try:
            payload = self.innertube_handle.preInit_buildPayload(use_matching_page=True,
                                                                    playlist_id=playlist_id,
                                                                    page=page.value
                                                                    )
            
            while count < self.maxresults:

                if payload is None:
                    self.log_handle(f"Failed to build payload for page '{page}'", "error")
                    break

                response = self.innertube_handle.get_innertube_response(payload)
                if response is None:
                    self.log_handle(f"Failed to retrieve innertube content for page '{page}'", "error")
                    break

                for media in self.innertube_parser.parse(response, contiunation_page):
                    if media and count < self.maxresults:
                        if (
                            media["url"] not in [
                                "https://www.youtube.com/playlist?list=WL",
                                "https://www.youtube.com/playlist?list=LL",
                            ]
                            and page == playlist_type.PLAYLISTS 
                        ) or (page != playlist_type.PLAYLISTS):
                            media_data_list.playlisttitles.append(media["title"])
                            media_data_list.vid_url.append(media["url"])
                            media_data_list.playlist_thumbnails.append(media["thumb"])
                            media_data_list.playlist_channel.append(media["channel"])
                        count += 1

                continuation_token = self.innertube_parser.get_continuation_token()
                contiunation_page = True
                if not continuation_token:
                    self.log_handle(f"No more continuation token found for page '{page}'", "info")
                    break
                else:
                    payload["continuation"] = continuation_token
                    payload.pop("browseId", None) # Clear browseId when using continuation token

            return media_data_list
        except Exception as e:
            self.log_handle(f"An error occurred while retrieving playlist content for page '{page}': {e}", "error")
            return None



