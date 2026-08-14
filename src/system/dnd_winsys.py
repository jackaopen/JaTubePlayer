import ctypes
from ctypes import  wintypes
import os
import time
import queue
import threading

from video_media_control.media_list_page_control import MediaList_PageControl_
from loader.media_data_list import media_data_list_template

import pythoncom
import win32clipboard
import win32con
from win32com.server.policy import DesignatedWrapPolicy
from notification.ctkmessagebox import ctk_messagebox

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

class URL_DropHandler(DesignatedWrapPolicy):
    '''
    Refering to lots of microsoft docs
    which are ass

    please use the CoUninitialize() after destroying this object
    '''    

    def __init__(self, log_handle):
        self.log_handle = log_handle

        self.DROPEFFECT_COPY = 1
        self.DROPEFFECT_NONE = 0
        self.lindexALL = -1

        self._com_interfaces_ = [pythoncom.IID_IDropTarget]
        self._public_methods_ = ["DragEnter", "DragOver", "DragLeave", "Drop"]

        self.CF_URL = win32clipboard.RegisterClipboardFormat("UniformResourceLocatorW")
        self.formats = [
            (self.CF_URL, "utf-16-le"),
            (win32con.CF_UNICODETEXT, "utf-16-le"),
        ]
        self.url_queue = queue.Queue()
        self._wrap_(self)



    def DragEnter(self, pDataObj, grfKeyState, pt, pdwEffect):
      return self.DROPEFFECT_COPY

    def DragOver(self, grfKeyState, pt, pdwEffect):
        return self.DROPEFFECT_COPY

    def DragLeave(self):
        return self.DROPEFFECT_NONE

    def Drop(self, pDataObj, grfKeyState, pt, pdwEffect):
        url = self.get_url(pDataObj)
        if url:
            self.url_queue.put(url)
            self.log_handle(
                content=f"URL put in queue: {url}",
                errtype='info',
                component='drag_drop',
            )
            return self.DROPEFFECT_COPY
        return self.DROPEFFECT_NONE

    def get_url(self,pDataObj):
        
        for format, encode in self.formats:
            try:
                fmt_tuple = (format,
                            None,
                            pythoncom.DVASPECT_CONTENT,
                            self.lindexALL,
                            pythoncom.TYMED_HGLOBAL)
                
                self.log_handle(
                    content=f"Trying format: {format}, encode: {encode}",
                    errtype='info',
                    component='drag_drop',
                )
                pDataObj.QueryGetData(fmt_tuple)
                data = pDataObj.GetData(fmt_tuple)

                url = data.data.decode(encode, errors="ignore").replace("\x00", " ")
                if url:
                    self.log_handle(
                        content=f"URL obtained: {url}",
                        errtype='info',
                        component='drag_drop',
                    )
                    return url
            except pythoncom.com_error:
                self.log_handle(
                    content=f"Unsupported format, might be path",
                    errtype='warning',
                    component='drag_drop',
                )

            except Exception as e:
                self.log_handle(
                    content=f"Failed to get data for format {format}: {e}",
                    errtype='error',
                    component='drag_drop',
                )
        return None
        

        
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
                 Chrome_ext_server_ui_functions:object,
                 messagebox:ctk_messagebox,
                 root)->None:
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
        self.ext_ui_functions = Chrome_ext_server_ui_functions

        self.URL_DropHandler = URL_DropHandler(
            log_handle=log_handle
        )
        

        self.handler = None
        self.original_handler = None
        self._init_dnd_handle()
        self.messagebox = messagebox

        threading.Thread(target=self._dnd_listener, daemon=True).start()
        self.valid_domains = ["youtube.com","youtu.be","music.youtube.com","twitch.tv","bilibili"]

    def _init_dnd_handle(self):
        hwnd = self.root.winfo_id()
        shell32.DragAcceptFiles(hwnd, True)
        self.handler = WindowProc(self.on_file_drop)
        self.original_handler = user32.SetWindowLongPtrW(hwnd, -4, self.handler)

    def init_URL_handler(self):
        pythoncom.OleInitialize()
        self.target_com = pythoncom.WrapObject(
            self.URL_DropHandler,
            pythoncom.IID_IDropTarget,
            pythoncom.IID_IDropTarget
        )
        pythoncom.RegisterDragDrop(self.root.winfo_id(), self.target_com)


    def close(self):
        pythoncom.RevokeDragDrop(self.root.winfo_id())
        pythoncom.OleUninitialize()



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
                    self.log_handle(
                        content=f"File dropped: {buffer.value}",
                        errtype='info',
                        component='drag_drop',
                    )
                    files.append(f"{buffer.value}")
                except Exception as e:  
                    self.log_handle(
                        content=f"Error retrieving file {i}: {e}",
                        errtype='error',
                        component='drag_drop',
                    )
            
            shell32.DragFinish(drop)
            self.handle_file_drop(file_paths=files)
            return 0
        # Other messages: not our job, pass to original
        return user32.CallWindowProcW(self.original_handler, hwnd, msg, wparam, lparam)


    def _dnd_listener(self):       

            '''
            if the dropped file is valid, return the list of file paths
            valid file: return a single folder or multiple files
            
            also listen to the URL drop, and call the handle_url_drop function in the main thread
            '''
            self.log_handle(
                content="DnD listener initialized",
                errtype='info',
                component='drag_drop',
            )
            
            while True:
                try:
                    try:
                        file_paths = self.dnd_path_queue.get_nowait()
                    except queue.Empty:
                        file_paths = None

                    try:
                        dropped_url = self.URL_DropHandler.url_queue.get_nowait() 
                    except queue.Empty:
                        dropped_url = None

                
                    if file_paths:
                        self.selected_song_number = None
                        self.media_data_list.clear()
                        
                        try:

                            
                            self.log_handle(
                                content=f"Valid files/folder dropped: {file_paths}",
                                errtype='info',
                                component='drag_drop',
                            )

                            if len(file_paths) == 1:
                                if os.path.isfile(file_paths[0]):
                                    file_ext = os.path.splitext(os.path.basename(file_paths[0]))[1]

                                    if not file_ext or file_ext not in FILE_TYPE_EXT:
                                        self.log_handle(
                                            content=f"Invalid file or file type:  {file_paths[0]}",
                                            errtype='errir',
                                            component='drag_drop',
                                        )
                                        self.messagebox.showerror(
                                            "JatubePlayer",
                                            f"Invalid file or file type:  {file_paths[0]} WITH {file_ext}"
                                        )
                                        continue
                                    self.log_handle(
                                        content=f"Single file dropped: {file_paths[0]}",
                                        errtype='info',
                                        component='drag_drop',
                                    )
                                    

                                    self.media_data_list.vid_url.append(file_paths[0])
                                    self.media_data_list.playlisttitles.append(os.path.basename(file_paths[0]))
                                    self.media_data_list.playlist_channel.append("local file")
                                    self.media_data_list.playlist_thumbnails.append("")

                                    self.media_list_page_control.local_files_init_and_reload(media_data_list=self.media_data_list,
                                                                                            dnd_mode=True)#still put a file into it
                                    self.selected_song_number_status_changer(1)
                                elif os.path.isdir(file_paths[0]):
                                    self.log_handle(
                                        content=f"Folder dropped: {file_paths[0]}",
                                        errtype='info',
                                        component='drag_drop',
                                    )
                                    for dir,_,files in os.walk(file_paths[0]):
                                        self.log_handle(
                                            content=f": {files}",
                                            errtype='info',
                                            component='drag_drop',
                                        )
                                        for file in files:
                                            if os.path.splitext(file)[1].lower() in FILE_TYPE_EXT:
                                                
                                                self.media_data_list.vid_url.append(os.path.join(dir,file))
                                                self.media_data_list.playlisttitles.append(file)
                                                self.media_data_list.playlist_channel.append("local file")
                                                self.media_data_list.playlist_thumbnails.append("")
                                        break
                                    self.selected_song_number_status_changer(2)
                                    self.media_list_page_control.local_files_init_and_reload(media_data_list=self.media_data_list,
                                                                                            dnd_mode=True)
                            elif len(file_paths) > 0:
                                for file in file_paths:
                                    if os.path.isfile(file) and os.path.splitext(file)[1].lower() in FILE_TYPE_EXT:
                                        self.media_data_list.vid_url.append(file)
                                        self.media_data_list.playlisttitles.append(os.path.basename(file))
                                        self.media_data_list.playlist_channel.append("local file")
                                        self.media_data_list.playlist_thumbnails.append("")
                                
                                self.selected_song_number_status_changer(2)
                                self.media_list_page_control.local_files_init_and_reload(media_data_list=self.media_data_list,
                                                                                        dnd_mode=True)
                        finally:
                            time.sleep(0.5)

                    if dropped_url:
                        for domain in self.valid_domains:
                            if domain in dropped_url:
                                self.log_handle(
                                    content=f"Valid URL dropped: {dropped_url}",
                                    errtype='info',
                                    component='drag_drop',
                                )
                               
                                self.media_list_page_control.handle_url_drop(dropped_url.strip().split("&")[0])
                                self.log_handle(
                                    content=f" see url : {dropped_url}",
                                    errtype='info',
                                    component='drag_drop',
                                )
                                while not self.URL_DropHandler.url_queue.empty():
                                    self.URL_DropHandler.url_queue.get()
                                self.ext_ui_functions.direct_url(reset_star = False)
                                break
                        else:
                            self.log_handle(
                                content=f"Invalid URL dropped: {dropped_url}",
                                errtype='warning',
                                component='drag_drop',
                            )
                            self.ui_queue.put(self.messagebox.showerror(f'JaTubePlayer ',f'Invalid URL dropped!'))
                            
                    time.sleep(0.5)
                except Exception as err:
                    self.log_handle(
                        content=f"Error in DnD listener: {err}",
                        errtype='error',
                        component='drag_drop',
                    )
                
