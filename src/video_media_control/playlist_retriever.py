
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
        self.innertube_parser = innertube_parser()

        self.maxresults_recommendation = "100"
        self.maxresults_sub = "100"
        self.maxresults_like = "100"

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
            self.log_handle(
                content=f"Page '{page}' is not supported",
                errtype='error',
                component='playlist',
            )
            return None
        else:
            match page:
                case playlist_type.HOME:
                    maxresults = self.maxresults_recommendation
                case playlist_type.SUBSCRIPTIONS:
                    maxresults = self.maxresults_sub
                case playlist_type.LIKED:
                    maxresults = self.maxresults_like
                case _:
                    maxresults = "5000"


        
        try:
            payload = self.innertube_handle.preInit_buildPayload(use_matching_page=True,
                                                                    playlist_id=playlist_id,
                                                                    page=page.value
                                                                    )
            
            while count < int(maxresults):

                if payload is None:
                    self.log_handle(
                        content=f"Failed to build payload for page '{page}'",
                        errtype='error',
                        component='playlist',
                    )
                    break

                response = self.innertube_handle.get_innertube_response(payload)
                if response is None:
                    self.log_handle(
                        content=f"Failed to retrieve innertube content for page '{page}'",
                        errtype='error',
                        component='playlist',
                    )
                    break

                for media in self.innertube_parser.parse(response, contiunation_page):
                    if media and count < int(maxresults):
                        if (
                            media["url"] not in [
                                "https://www.youtube.com/playlist?list=WL",
                                "https://www.youtube.com/playlist?list=LL",
                            ]
                            and page == playlist_type.PLAYLISTS 
                        ) or (page != playlist_type.PLAYLISTS):
                            if page == playlist_type.PLAYLISTS or (page != playlist_type.PLAYLISTS and "playlist" not in media["url"]):
                                media_data_list.playlisttitles.append(media["title"])
                                media_data_list.vid_url.append(media["url"])
                                media_data_list.playlist_thumbnails.append(media["thumb"])
                                media_data_list.playlist_channel.append(media["channel"])
                                count += 1

                continuation_token = self.innertube_parser.get_continuation_token()
                contiunation_page = True
                if not continuation_token:
                    self.log_handle(
                        content=f"No more continuation token found for page '{page}'",
                        errtype='info',
                        component='playlist',
                    )
                    break
                else:
                    payload["continuation"] = continuation_token
                    payload.pop("browseId", None) # Clear browseId when using continuation token

            return media_data_list
        except Exception as err:
            self.log_handle(
                content=f"An error occurred while retrieving playlist content for page '{page}': {err}",
                errtype='error',
                component='playlist',
            )
            return None



