from CTkMessagebox import CTkMessagebox
import queue,time,os,sys,subprocess,threading




class ctk_messagebox(object):
    '''
    A wrapper for CTkMessagebox to make it thread-safe
    if other moduels want to use CTkMessagebox, they should have a root first
    '''
    def __init__(self,
                 master:object,
                 _internal_path:str) -> None:
        self.master = master
        self.queue = queue.Queue()
        self.process_queue()
        self._info_wav  = os.path.join(_internal_path, "info.wav")
        self._error_wav = os.path.join(_internal_path, "err.wav")
        self._warn_wav  = os.path.join(_internal_path, "warn.wav")

    def _play(self, path:str) -> None:
        if not os.path.isfile(path):
            return
        if sys.platform == "win32":
            import winsound
            winsound.PlaySound(path, winsound.SND_FILENAME | winsound.SND_ASYNC | winsound.SND_NODEFAULT)
        else:
            # Linux: aplay (ALSA); macOS: afplay
            cmd = ["afplay", path] if sys.platform == "darwin" else ["aplay", "-q", path]
            threading.Thread(target=subprocess.call, args=(cmd,), daemon=True).start()
    
    def process_queue(self):
        try:
            for _ in range(200):
                f = self.queue.get_nowait()
                try:f()
                except Exception as e:print(e)
        except queue.Empty:
            pass
        self.master.after(20, self.process_queue)

    def showerror(self,title:str,message:str) -> None:
        self._play(self._error_wav)
        self.queue.put(lambda: CTkMessagebox(title=title,message=message,icon="cancel"))
        
    def showinfo(self,title:str,message:str) -> None:
        self._play(self._info_wav)
        self.queue.put(lambda: CTkMessagebox(title=title,message=message,icon="info"))

    def showwarning(self,title:str,message:str) -> None:
        self._play(self._warn_wav)
        self.queue.put(lambda: CTkMessagebox(title=title,message=message,icon="warning"))

    def askquestion(self,title:str,message:str) -> None:
        res = None
        def _ask():
            nonlocal res
            self._play(self._info_wav)
            res = CTkMessagebox(title=title,message=message,icon="question",
            option_1="Yes",option_2="No").get()
        self.queue.put(_ask)
        while res is None:
            self.master.update()
            time.sleep(0.02)
        return res=="Yes"
    def askokcancel(self,title:str,message:str) -> None:
        res = None
        def _ask():
            nonlocal res
            self._play(self._info_wav)
            res = CTkMessagebox(title=title,message=message,icon="question",
            option_1="OK",option_2="Cancel").get()
        self.queue.put(_ask)
        while res is None:
            self.master.update()
            time.sleep(0.02)
        return res=="OK"

    def askyesno(self,title:str,message:str) -> None:
        res = None
        def _ask():
            nonlocal res
            self._play(self._info_wav)
            res = CTkMessagebox(title=title,message=message,icon="question",
            option_1="Yes",option_2="No").get()
        self.queue.put(_ask)
        while res is None:
            self.master.update()
            time.sleep(0.02)
        return res=="Yes"

    def askyesnocancel(self,title:str,message:str) -> None:
        res = None
        def _ask():
            nonlocal res
            self._play(self._info_wav)
            res = CTkMessagebox(title=title,message=message,icon="question",
            option_1="Yes",option_2="No",option_3="Cancel").get()
        self.queue.put(_ask)
        while res is None:
            self.master.update()
            time.sleep(0.02)
        return res=="Yes"

    def askretrycancel(self,title:str,message:str) -> None:
        res = None
        def _ask():
            nonlocal res
            self._play(self._info_wav)
            res = CTkMessagebox(title=title,message=message,icon="question",
            option_1="Retry",option_2="Cancel").get()
        self.queue.put(_ask)
        while res is None:
            self.master.update()
            time.sleep(0.02)
        return res=="Retry"

    def showerror_and_wait(self,title:str,message:str) -> None:
        '''
        show error message and wait for user to close it
        for Fatal Error 
        '''
        res = None
        def _ask():
            nonlocal res
            self._play(self._error_wav)
            res = CTkMessagebox(title=title,message=message,icon="cancel").get()
        self.queue.put(_ask)
        while res is None:
            self.master.update()
            time.sleep(0.02)
        return 
    