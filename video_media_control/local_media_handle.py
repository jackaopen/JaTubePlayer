from tkinter import filedialog
import tkinter as tk
from ..loader.media_data_list import media_data_list_template
import os


FILE_TYPE_EXT = (
                ".mp4", ".mkv", ".avi", ".mov", ".wmv", ".flv", ".mpeg", ".mpg", ".3gp", ".webm", ".ogv",
                ".ts", ".mts", ".vob", ".mp3", ".wav", ".flac", ".aac", ".ogg", ".wma", ".m4a", ".aiff", ".opus", ".amr"
            )

FILE_TYPE = [
                ("All Supported Files", "*.mp4 *.mkv *.avi *.mov *.wmv *.flv *.mpeg *.mpg *.3gp *.webm *.ogv *.ts *.mts *.vob *.mp3 *.wav *.flac *.aac *.ogg *.wma *.m4a *.aiff *.opus *.amr"),
                ("Video Files", "*.mp4 *.mkv *.avi *.mov *.wmv *.flv *.mpeg *.mpg *.3gp *.webm *.ogv *.ts *.mts *.vob"),
                ("Audio Files", "*.mp3 *.wav *.flac *.aac *.ogg *.wma *.m4a *.aiff *.opus *.amr"),
                ]


class local_media_handle:
    '''
    mainly called by media_list_page_control to handle local files and folders 
    '''
    def __init__(self,
                 log_handle:object,
                 ):
        self.log_handle = log_handle


    def load_local_files(self,
                         mode:int,
                        )->media_data_list_template:
        '''
        mode 0 == single file mode and dnd single file
        mode 1 == folder mode and dnd folder(must have muti files for better single file control balance)
        mode 2 == dnd multi files
        local_folder_path for quick startup local folder and dnd folder
        dnd_files_path_lists for dnd file list
        // only use kwarg
        '''
        media_data_list = media_data_list_template()
        if mode == 0:
            
            local_single_filepath = filedialog.askopenfilename(filetypes = FILE_TYPE)
            
            if local_single_filepath:
                media_data_list.clear()

                media_data_list.vid_url.append(local_single_filepath)
                media_data_list.playlisttitles.append(os.path.basename(local_single_filepath))
                media_data_list.playlist_channel.append("local file")
                media_data_list.playlist_thumbnails.append(None)


        if mode == 1:
                            
            folder_path = filedialog.askdirectory()
            self.log_handle(content=str(folder_path))
            if folder_path:
                media_data_list.playlisttitles.clear()
                media_data_list.playlist_thumbnails.clear()
                media_data_list.vid_url = []
                folder_items = [file for file in os.listdir(folder_path) if file.endswith(FILE_TYPE_EXT)]

                index_for_tree = 1
                for item in folder_items:
                    media_data_list.vid_url.append(os.path.join(folder_path,item))
                    media_data_list.playlisttitles.append(item)
                    index_for_tree += 1
            
