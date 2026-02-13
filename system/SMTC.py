
from winsdk.windows.media.playback import BackgroundMediaPlayer
from winsdk.windows.media import (
    MediaPlaybackType,
    MediaPlaybackStatus,
    SystemMediaTransportControlsButton
)
from typing import Callable
from winsdk.windows.foundation import Uri
from winsdk.windows.storage.streams import RandomAccessStreamReference


class MediaControlOverlay(object):
    def __init__(self,next_song_fun : Callable = None, prev_song_fun : Callable = None, pause_fun :Callable = None):
        self.smtc = BackgroundMediaPlayer.current.system_media_transport_controls
        self.smtc.is_play_enabled = True
        self.smtc.is_pause_enabled = True
        self.smtc.is_next_enabled = True
        self.smtc.is_previous_enabled = True 
        self.smtc.is_enabled = False
        self.smtc.add_button_pressed(self.on_button_pressed)
        self.is_playing = False

        self.next_song_fun = next_song_fun
        self.prev_song_fun = prev_song_fun
        self.pause_fun = pause_fun
        
        self.updater = self.smtc.display_updater
        self.updater.app_media_id = "Jackaopen.JaTubePlayer"

    def on_button_pressed(self, sender, args):
        btn = args.button
        try:
            print(f"SMTC button pressed: {btn}")
            if btn == SystemMediaTransportControlsButton.PLAY: 
                self.is_playing = True  
                if self.pause_fun:self.pause_fun(1)  
                self.smtc.playback_status = MediaPlaybackStatus.PLAYING 
                
            elif btn == SystemMediaTransportControlsButton.PAUSE: 
                self.is_playing = False  # 
                if self.pause_fun:self.pause_fun(1)  
                self.smtc.playback_status = MediaPlaybackStatus.PAUSED  
                
            elif btn == SystemMediaTransportControlsButton.PREVIOUS:
                if self.prev_song_fun:
                    self.prev_song_fun()
                    
            elif btn == SystemMediaTransportControlsButton.NEXT:
                if self.next_song_fun:
                    self.next_song_fun()
        except Exception as e:
            print(f"Error handling SMTC button press: {e}")
            
    def set_paused(self):
        self.is_playing = False
        self.smtc.playback_status = MediaPlaybackStatus.PAUSED
    def set_playing(self):
        self.is_playing = True
        self.smtc.playback_status = MediaPlaybackStatus.PLAYING

    def update_media_info(self, title, artist, album , thumbnail_url=None ):
        try:
            print("Updating SMTC media info…")
            self.smtc.is_enabled = True
            self.updater.type = MediaPlaybackType.MUSIC
            props = self.updater.music_properties
            props.title = title
            props.artist = artist
            props.album_title = album
            self.is_playing = True
            self.smtc.playback_status = MediaPlaybackStatus.PLAYING
            if thumbnail_url:
                self.updater.thumbnail = RandomAccessStreamReference.create_from_uri(Uri(thumbnail_url))
            self.updater.update()
            print(f"🎵 SMTC {title} - {artist}")
        except Exception as e:
            print(f"Error updating SMTC media info: {e}")


    def destroy(self):
        self.smtc.is_enabled = False# key to show/hide smtc



if __name__ == "__main__":
    smtc = MediaControlOverlay()
    smtc.update_media_info("Test Song", "Test Artist", "Test Album")
    import time
    time.sleep(10)
    smtc.set_paused()
    time.sleep(5)
    smtc.set_playing()
    time.sleep(10)
    smtc.destroy()