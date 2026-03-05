# Install: pip install tkinterdnd2
import queue
import platform

class DropHandler(object):
    def __init__(self, dnd_path_queue: queue.Queue = None, root=None) -> None:
        self.root = root
        self.dnd_path_queue = dnd_path_queue

    def handle_file_drop(self, file_paths: list):pass
        

        

    def on_file_drop(self, event):pass
        

    def enable_drop(self, widget):
        pass