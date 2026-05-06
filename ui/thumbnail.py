import io
import aiohttp
import asyncio
import queue
from PIL import Image, ImageTk
import threading
from typing import Callable

class ThumbnailLoader:
    '''
        Please use lambda for variables, for sync with global variables
        Automatically start it self.
        > we need playing_vid_mode and tkinter_scaling as lambda function for sync
        '''
    def __init__(self, 
                 playing_vid_mode:Callable, #lambda for sync with global variable
                 insert_treeview_quene:object,
                 playlisttreebox:object, 
                 ui_queue:queue.Queue,
                 tkinter_scaling:Callable,  #lambda for sync with global variable
                 log_handle:object,
                 root:object):
        
        self.temp = []
        self.playing_vid_mode_ = playing_vid_mode
        self.insert_treeview_quene = insert_treeview_quene
        self.playlisttreebox = playlisttreebox
        self.ui_queue = ui_queue
        self.tkinter_scaling_ = tkinter_scaling
        self.log_handle = log_handle
        self.root = root
        self.async_task = []
        self.asyncio_session = None #init none, create in async_thumb
        self.asynceventloop = asyncio.new_event_loop()
        # Start the async event loop in a separate thread
        self.root.after(0, self.treeview_queue_GetterLoop)
        threading.Thread(target=self.start_async_eventloop, daemon=True).start()
    
    @property
    def playing_vid_mode(self):
        return self.playing_vid_mode_()
    @property
    def tkinter_scaling(self):
        return self.tkinter_scaling_()
    
    # ─────────────────────────────────────────────────────────────────────────
    # Async Thumbnail Loading
    # ─────────────────────────────────────────────────────────────────────────

    async def load_thumbnail_task(self, session, id, thumburl):
        try:
            if self.playing_vid_mode == 0 or self.playing_vid_mode == 4:
                async with session.get(thumburl) as response:
                    imgdata = await response.read()
                    img = Image.open(io.BytesIO(imgdata))
                    img = img.resize(
                        (int(140 * self.tkinter_scaling / 1.25), int(105 * self.tkinter_scaling / 1.25)),
                        Image.LANCZOS
                    )
                    img1 = img.crop((
                        0,
                        int(14 * self.tkinter_scaling / 1.25),
                        int(140 * self.tkinter_scaling / 1.25),
                        int(90 * self.tkinter_scaling / 1.25)
                    ))
                    thumbnailpic = ImageTk.PhotoImage(img1)
                    self.temp.append(thumbnailpic)
                    self.ui_queue.put(lambda id=id, pic=thumbnailpic: self.playlisttreebox.item(id, image=pic))
        except Exception as e:
            self.log_handle(content=str(e))

    # ─────────────────────────────────────────────────────────────────────────
    # Async Event Loop for Thumbnail Loading
    # ─────────────────────────────────────────────────────────────────────────

    async def async_thumb(self):
        try:
            if not self.asyncio_session:
                self.asyncio_session = aiohttp.ClientSession()
            if self.async_task:
                task_temp = self.async_task.copy()
                await asyncio.gather(*task_temp)
                self.async_task = [item for item in self.async_task if item not in task_temp]
        except Exception:
            pass
        await asyncio.sleep(0.25)
        asyncio.create_task(self.async_thumb())

    def start_async_eventloop(self):
        asyncio.set_event_loop(self.asynceventloop)
        self.asynceventloop.call_soon_threadsafe(lambda: self.asynceventloop.create_task(self.async_thumb()))
        self.asynceventloop.run_forever()

    # ─────────────────────────────────────────────────────────────────────────
    # Thumbnail Loading and Treeview Insertion, put thumbnail loading tasks in async_task list
    # ─────────────────────────────────────────────────────────────────────────
    def clear_thumbnails(self):
        self.playlisttreebox.delete(*self.playlisttreebox.get_children())
        try:
            while True:
                self.insert_treeview_quene.get_nowait()
        except queue.Empty:
            pass
        self.async_task.clear()
        self.temp.clear()
    
    def treeview_queue_GetterLoop(self):
        try:
            while not self.insert_treeview_quene.empty():
                thumb, title, ch = self.insert_treeview_quene.get_nowait()
                id = self.playlisttreebox.insert('', 'end', values=(f'{title}\n{ch}',))
                if self.playing_vid_mode == 0 or self.playing_vid_mode == 4:
                    self.async_task.append(self.load_thumbnail_task(self.asyncio_session, id, thumb))

                if self.playing_vid_mode == 0 or self.playing_vid_mode == 4:
                    self.playlisttreebox.column("#0", width=180, anchor='center')
                else:
                    self.playlisttreebox.column("#0", width=0, anchor='center')
        except Exception as e:
            self.log_handle(content=str(e))
        self.root.after(20, self.treeview_queue_GetterLoop)
    
    def close(self):
        if self.asyncio_session:
            self.asynceventloop.call_soon_threadsafe(lambda: asyncio.create_task(self.asyncio_session.close()))
        self.asynceventloop.call_soon_threadsafe(self.asynceventloop.stop)

    def clear_thumb(self,selected_ID:str):
        self.playlisttreebox.delete(selected_ID)
        
