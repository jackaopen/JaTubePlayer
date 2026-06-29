import ctypes
from ctypes import  wintypes
import os
from tkinter import messagebox
import time
import queue
import threading
from video_media_control.media_list_page_control import MediaList_PageControl_
from loader.media_data_list import media_data_list_template




FILE_TYPE_EXT = [
                ".mp4", ".mkv", ".avi", ".mov", ".wmv", ".flv", ".mpeg", ".mpg", ".3gp", ".webm", ".ogv",
                ".ts", ".mts", ".vob", ".mp3", ".wav", ".flac", ".aac", ".ogg", ".wma", ".m4a", ".aiff", ".opus", ".amr"
]



user32 = ctypes.windll.user32
shell32 = ctypes.windll.shell32




# Define type
WindowProc = ctypes.WINFUNCTYPE(ctypes.c_long, 
                                wintypes.HWND,wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM)


shell32.DragQueryFileW.argtypes = [wintypes.HANDLE, 
                                   wintypes.UINT, 
                                   wintypes.LPWSTR, 
                                   wintypes.UINT]
shell32.DragQueryFileW.restype = wintypes.UINT
'''
UINT DragQueryFileW(
    HDROP hDrop,
    UINT iFile,
    LPWSTR lpszFile,
    UINT cch
);
'''
user32.SetWindowLongPtrW.restype  = ctypes.c_void_p           # LONG_PTR
user32.SetWindowLongPtrW.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_void_p]

user32.CallWindowProcW.restype    = ctypes.c_longlong
user32.CallWindowProcW.argtypes   = [ctypes.c_void_p, wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM]
shell32.DragFinish.argtypes = [wintypes.HANDLE]
shell32.DragAcceptFiles.argtypes = [wintypes.HWND, wintypes.BOOL]

handler = None

class DropHandler(object):
    '''
    include the WINAPI , and the listener    
    '''
    def __init__(self,
                 media_list_page_control:MediaList_PageControl_,
                 log_handle:object,
                 ui_queue:queue.Queue,
                 selected_song_number_status_changer:object,
                 playing_vid_mode:int,
                 media_data_list:media_data_list_template,
                 root=None)->None:
        '''
        MLPC object must be created from JTP
        selected song number, playing_vid_mode : for dnd to refresh
        mdl must belong to jtp

        '''
        self.root = root
        self.log_handle = log_handle
        self.ui_queue = ui_queue
        self.dnd_path_queue = queue.Queue()
        self.media_list_page_control = media_list_page_control
        self.selected_song_number_status_changer = selected_song_number_status_changer
        self.playing_vid_mode = playing_vid_mode
        self.media_data_list = media_data_list
        
        threading.Thread(target=self._dnd_path_listener, daemon=True).start()
    
    def handle_file_drop(self,file_paths:list):
        self.dnd_path_queue.put(file_paths)


    def on_file_drop(self,hwnd, msg, wparam, lparam):
        '''
        WPARAM = “some unsigned integer / pointer-sized value”
        LPARAM = “some signed integer / pointer-sized value”

            ---------------
        
        PostMessage(
        (HWND) hWndControl,   // handle to destination control
        (UINT) WM_DROPFILES,  // message ID
        (WPARAM) wParam,      // = (WPARAM) (HDROP) hDrop;
        (LPARAM) lParam       // = 0; not used, must be zero 
        );       


        thus:
            wparam = HDROP
            lparam = 0

            
            ---------------


        UINT DragQueryFileW(
        [in]  HDROP  hDrop,
        [in]  UINT   iFile,     //file index, 0xFFFFFFFF for count
        [out] LPWSTR *lpszFile,  //file name buffer address(wchar_t*)
        [in]  UINT   cch        //file name buffer size in characters
        );

            ---------------

        LRESULT CallWindowProcW(
        WNDPROC lpPrevWndFunc,  // original handler
        HWND    hWnd,           // handle to window
        UINT    Msg,            // message 
        WPARAM  wParam,         // WPARAM
        LPARAM  lParam          // LPARAM
        ); // returns LRESULT
        
        '''
        if msg == 0x233:  # WM_DROPFILES
            drop = wintypes.HANDLE(wparam)
            
            # Get file count
            count = shell32.DragQueryFileW(drop, 0xFFFFFFFF, None, 0)
            files = []
            for i in range(count):
                try:
                    size = shell32.DragQueryFileW(drop, i, None, 0)  # number of characters

                    buffer = ctypes.create_unicode_buffer(size + 1) # alloc buffer, +1 for null terminator
                    shell32.DragQueryFileW(drop, i, buffer, size + 1) # put file name into buffer
                    self.log_handle(content=f"File dropped: {buffer.value}")
                    files.append(f"{buffer.value}")
                except Exception as e:  
                    self.log_handle(content=f"Error retrieving file {i}: {e}")
            
            shell32.DragFinish(drop)
            self.handle_file_drop(file_paths=files)
            return 0
        # Other messages: not our job, pass to original
        return user32.CallWindowProcW(original_handler, hwnd, msg, wparam, lparam)

    def enable_drop(self,hwnd, enable:bool):
        """
        LONG_PTR SetWindowLongPtrW(
        HWND hWnd,         // handle to window
        int nIndex,        // -4 for WndProc
        LONG_PTR dwNewLong // new address
        ); // returns replaced address

        """
        global handler,original_handler
        shell32.DragAcceptFiles(hwnd, enable)
        handler = WindowProc(self.on_file_drop)
        original_handler = user32.SetWindowLongPtrW(hwnd, -4, handler)# redirect WndProc, with our handler

    def _dnd_path_listener(self):       

            '''
            if the dropped file is valid, return the list of file paths
            valid file: return a single folder or multiple files
            
            '''
            while True:
                file_paths = self.dnd_path_queue.get()
                if file_paths:
                    self.selected_song_number = None
                    self.media_data_list.clear()
                    
                    try:

                        
                        self.log_handle(content=f"Valid files/folder dropped: {file_paths}")

                        if len(file_paths) == 1:
                            if os.path.isfile(file_paths[0]):
                                self.log_handle(content=f"Single file dropped: {file_paths[0]}")
                                

                                self.media_data_list.vid_url.append(file_paths[0])
                                self.media_data_list.playlisttitles.append(os.path.basename(file_paths[0]))
                                self.media_data_list.playlist_channel.append("local file")
                                self.media_data_list.playlist_thumbnails.append("")

                                self.media_list_page_control.local_files_init_and_reload(media_data_list=self.media_data_list)#still put a file into it
                                self.selected_song_number_status_changer(1)
                            elif os.path.isdir(file_paths[0]):
                                self.log_handle(content=f"Folder dropped: {file_paths[0]}")
                                for dir,_,files in os.walk(file_paths[0]):
                                    self.log_handle(content=f": {files}")
                                    for file in files:
                                        if os.path.splitext(file)[1].lower() in FILE_TYPE_EXT:
                                            
                                            self.media_data_list.vid_url.append(os.path.join(dir,file))
                                            self.media_data_list.playlisttitles.append(file)
                                            self.media_data_list.playlist_channel.append("local file")
                                            self.media_data_list.playlist_thumbnails.append("")
                                self.selected_song_number_status_changer(2)
                                self.media_list_page_control.local_files_init_and_reload(media_data_list=self.media_data_list)
                        elif len(file_paths) > 0:
                            for file in file_paths:
                                if os.path.isfile(file) and os.path.splitext(file)[1].lower() in FILE_TYPE_EXT:
                                    self.media_data_list.vid_url.append(file)
                                    self.media_data_list.playlisttitles.append(os.path.basename(file))
                                    self.media_data_list.playlist_channel.append("local file")
                                    self.media_data_list.playlist_thumbnails.append("")
                            
                            self.selected_song_number_status_changer(2)
                            self.media_list_page_control.local_files_init_and_reload(media_data_list=self.media_data_list)
                    finally:
                        time.sleep(0.5)
                else:time.sleep(1)