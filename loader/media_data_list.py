class media_data_list_template:
    '''
    ### This class it the loader template for media data for playlisttreebox
    - vid_url
    - playlisttitles
    - playlist_channel
    - playlist_thumbnails
    '''
    def __init__(self):
        self.vid_url = []
        self.playlisttitles = []
        self.playlist_channel = []
        self.playlist_thumbnails = []
        
    def clear(self):
        self.vid_url.clear()
        self.playlisttitles.clear()
        self.playlist_channel.clear()
        self.playlist_thumbnails.clear()

    