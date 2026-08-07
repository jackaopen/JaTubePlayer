
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


class playlist_retriever:
    def __init__(self, 
                 innertube_handle: innertube_handle,
                 log_handle: object):
        
        self.innertube_handle = innertube_handle
        self.log_handle = log_handle
        self.media_data_list = media_data_list_template()
        self.maxresults = 100
        self.innertube_parser = innertube_parser()

    def get_playlist_content(self, 
                             page: playlist_type, 
                             playlist_id: str=None)->media_data_list_template|None:
        '''
        page: playlist_type Enum, specify which page to retrieve content from
        '''
        self.media_data_list.clear()
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
            if page in [playlist_type.HOME, playlist_type.SUBSCRIPTIONS, playlist_type.HISTORY]: 
                self.maxresults = 100
            else: 
                self.maxresults = 5000


        
        try:
            while count < self.maxresults:
                payload = self.innertube_handle.preInit_buildPayload(use_matching_page=True,
                                                        continuation=continuation_token,
                                                        playlist_id=playlist_id,
                                                        page=page.value
                                                        )

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
                    if media and count < self.maxresults:
                        self.media_data_list.playlisttitles.append(media["title"])
                        self.media_data_list.vid_url.append(media["url"])
                        self.media_data_list.playlist_thumbnails.append(media["thumb"])
                        self.media_data_list.playlist_channel.append(media["channel"])
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
            return self.media_data_list
        except Exception as e:
            self.log_handle(
                content=f"An error occurred while retrieving playlist content for page '{page}': {e}",
                errtype='error',
                component='playlist',
            )
            return None



if __name__ == "__main__":
    import os
    import sys

    class _ConsoleMessageBox:
        """Small stand-in for the GUI message box used by account_handle."""

        def showerror_and_wait(self, title, message):
            print(f"{title} ERROR: {message}", file=sys.stderr)

        def showwarning(self, title, message):
            print(f"{title} WARNING: {message}", file=sys.stderr)

    def console_log(message, level="info"):
        print(f"[{level}] {message}")

    app_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    account = account_handle(app_root, _ConsoleMessageBox(), console_log)
    innertube = innertube_handle(account, console_log)
    retriever = playlist_retriever(innertube, console_log)
    # Keep the demo short. Increase this to exercise more continuation pages.
    home = retriever.get_playlist_content(playlist_type.SUBSCRIPTIONS
                                          ,playlist_id="PLg-S_KMDBWGfSi3uIGXbuh1Pd_9rNbsZw"
                                          )

    print(f"Retrieved {len(home.vid_url)} Home items")
    for index, (title, url, channel) in enumerate(
        zip(home.playlisttitles, home.vid_url, home.playlist_channel),
        start=1,
    ):
        print(f"{index:>2}. {title} | {channel or 'Unknown channel'}")
        print(f"    {url}")
