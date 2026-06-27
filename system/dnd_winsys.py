import ctypes
from ctypes import  wintypes
import os
from tkinter import messagebox
import time
import queue
import threading
from ..video_media_control.media_list_page_control import MediaList_PageControl_


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
                 root=None)->None:
        '''
        MLPC object must be created from JTP
        '''
        self.root = root
        self.log_handle = log_handle
        self.ui_queue = ui_queue
        self.dnd_path_queue = queue.Queue()
        self.media_list_page_control = media_list_page_control
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
            print(f"\n{count} file(s) dropped:")
            files = []
            for i in range(count):
                try:
                    size = shell32.DragQueryFileW(drop, i, None, 0)  # number of characters

                    print(size)
                    buffer = ctypes.create_unicode_buffer(size + 1) # alloc buffer, +1 for null terminator
                    shell32.DragQueryFileW(drop, i, buffer, size + 1) # put file name into buffer
                    files.append(f"{buffer.value}")
                except Exception as e:  
                    print(f"Error retrieving file {i}: {e}")
            
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
            global selected_song_number 

            '''
            if the dropped file is valid, return the list of file paths
            valid file: return a single folder or multiple files
            
            '''
            while True:
                file_paths = self.dnd_path_queue.get()
                if file_paths:
                    try:
                        valid_type = True
                        self.log_handle(content=f"Files dropped: {file_paths}")
                        for i in range(len(file_paths)):# check every file type if its valid
                            if os.path.isdir(file_paths[i]) and len(file_paths)> 1 :
                                self.ui_queue.put(lambda: messagebox.showerror("Jatubeplater drag&drop", "You can only drop a single folder or multiple files at once."))
                                valid_type = False
                                break
                            elif os.path.isfile(file_paths[i]):
                                _,ext = os.path.splitext(file_paths[i])
                                if ext.lower() not in ['.mp4', '.mkv', '.avi', '.mov', '.wmv', '.flv', '.mpeg', '.mpg', '.3gp', '.webm', '.ogv', '.ts', '.mts', '.vob', '.mp3', '.wav', '.flac', '.aac', '.ogg', '.wma', '.m4a', '.aiff', '.opus', '.amr']:
                                    _file_path = file_paths[i]  # Capture for lambda
                                    self.ui_queue.put(lambda fp=_file_path: messagebox.showerror("Jatubeplater drag&drop", f"The file '{fp}' is not contain valid media file."))
                                    valid_type = False
                                    break
                        #call thing to add to playlist
                        #TODO 
                        if valid_type:
                            if len(file_paths) == 1:
                                if os.path.isfile(file_paths[0]):
                                    meload_local_files(mode=0,dnd_single_file_path=file_paths[0])#still put a file into it
                                    selected_song_number = None
                                    load_thread_queue.put((file_paths[0],None))#play the first file
                                elif os.path.isdir(file_paths[0]):
                                    load_local_files(mode=1,local_folder_path=file_paths[0])
                            elif len(file_paths) > 0:
                                load_local_files(mode=2,dnd_files_path_lists=file_paths)
                    finally:
                        time.sleep(0.5)
                else:time.sleep(1)