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


        playlisttreebox.tag_configure("normal", background="#1e1e1e", foreground="#c5c5c5")
        playlisttreebox.tag_configure("playing", background="#CA7E28", foreground="#000000")
    
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
                        (int(121 * self.tkinter_scaling ), int(68 * self.tkinter_scaling )),
                        Image.LANCZOS
                    )
                    img1 = img.crop((
                        0,
                        int(5 * self.tkinter_scaling ),
                        int(121 * self.tkinter_scaling ),
                        int(68 * self.tkinter_scaling )
                    ))
                    thumbnailpic = ImageTk.PhotoImage(img1)
                    self.temp.append(thumbnailpic)
                    self.ui_queue.put(lambda id=id, pic=thumbnailpic: self.playlisttreebox.item(id, image=pic))
        except Exception as e:
            self.log_handle(
                content=str(e),
                errtype='error',
                component='treeview',
            )

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
                    self.playlisttreebox.column("#0", width=int(170*self.tkinter_scaling), anchor='center')
                else:
                    self.playlisttreebox.column("#0", width=0, anchor='center')
        except Exception as e:
            self.log_handle(
                content=str(e),
                errtype='error',
                component='treeview',
            )
        self.root.after(20, self.treeview_queue_GetterLoop)
    

    def select_first_item(self):
        self.root.after(500, self._select_first_item)

    def _select_first_item(self):
        children = self.playlisttreebox.get_children()
        if children:
            self.playlisttreebox.selection_set(children[0])
            self.playlisttreebox.see(children[0])  
        self.log_handle(
            content='selected first item in the playlist',
            errtype='info',
            component='treeview',
        )

    def select_last_item(self):
        self.root.after(500, self._select_last_item)

    def _select_last_item(self):
        children = self.playlisttreebox.get_children()
        if children:
            self.playlisttreebox.selection_set(children[-1])
            self.playlisttreebox.see(children[-1])  

    def select_item(self,idx = int):
        '''
        idx: relative index of the item in the treeview, 0-based, to 50\n
        will skip if out of range\n
        will run in root.after 
        '''
        try:
            self.root.after(500, lambda: self._select_item(idx))
        except Exception as e:
            raise e
        


    def _select_item(self,
                    idx = int):
        
        children = self.playlisttreebox.get_children()
        if 0 <= idx < len(children):
            self.playlisttreebox.selection_set(children[idx])
            self.playlisttreebox.see(children[idx])
    
    def set_item_color(self, 
                       idx = int, 
                       color:str = 'playing',
                       delay:int = 50):
        '''
        idx: relative index of the item in the treeview, 0-based, to 50\n
        will skip if out of range\n
        color: the color to set the item to\n
        will run in root.after 
        '''
        try:
            self.root.after(delay, lambda: self._set_item_color(idx, color))
        except Exception as e:
            self.log_handle(
                content=f"[set_item_color] error: {str(e)}",
                errtype='error',
                component='treeview',
            )
            raise e
        
    def _set_item_color(self, idx = int, color:str = 'playing'):
        children = self.playlisttreebox.get_children()
        if 0 <= idx < len(children):
            self.playlisttreebox.item(children[idx], tags=(color,))
        
    def clear_all_tag(self)->None:
        '''
        clear ALL the tag in current page
        '''
        try:
            children = self.playlisttreebox.get_children()
            for child in children:
                self.playlisttreebox.item(child, tags=("normal",))
                
        except Exception as e:
            self.log_handle(
                content=str(e),
                errtype='error',
                component='treeview',
            )

    def close(self):
        if self.asyncio_session:
            self.asynceventloop.call_soon_threadsafe(lambda: asyncio.create_task(self.asyncio_session.close()))
        self.asynceventloop.call_soon_threadsafe(self.asynceventloop.stop)

    def clear_thumb(self,selected_ID:str):
        self.playlisttreebox.delete(selected_ID)
        
