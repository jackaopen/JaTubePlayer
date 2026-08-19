from pynput import keyboard
from pynput.keyboard import Key, Listener,GlobalHotKeys
import time
import customtkinter as CTk

VK_SPECIAL = {
    160: "<shift>",
    161: "<shift>",
    162: "<ctrl>",
    163: "<ctrl>",
    164: "<alt>",
    165: "<alt>",
    91:  "<cmd>",    
    92:  "<cmd>",     
    13:  "<enter>",
    9:   "<tab>",
    27:  "<esc>",
    8:   "<backspace>",
    32:  "<space>",
    20:  "<caps_lock>",
    112: "<f1>",
    113: "<f2>",
    114: "<f3>",
    115: "<f4>",
    116: "<f5>",
    117: "<f6>",
    118: "<f7>",
    119: "<f8>",
    120: "<f9>",
    121: "<f10>",
    122: "<f11>",
    123: "<f12>",
    124: "<f13>",
    125: "<f14>",
    126: "<f15>",
    127: "<f16>",
    128: "<f17>",
    129: "<f18>",
    130: "<f19>",
    131: "<f20>",
    132: "<f21>",
    133: "<f22>",
    134: "<f23>",
    135: "<f24>",
    33:  "<page_up>",
    34:  "<page_down>",
    35:  "<end>",
    36:  "<home>",
    37:  "<left>",
    38:  "<up>",
    39:  "<right>",
    40:  "<down>",
    45:  "<insert>",
    46:  "<delete>",
    44:  "<print_screen>",
    145: "<scroll_lock>",
    19:  "<pause>", 
    106: "*",  
    107: "+", 
    109: "-", 
    111: "/",  
    144: "<num_lock>",
    186: ";", 
    187: "=",  
    188: ",", 
    189: "-", 
    190: ".", 
    191: "/", 
    192: "`",  
    219: "[", 
    220: "\\",
    221: "]",  
    222: "'",
    96: "0",  
    97: "1",  
    98: "2",  
    99: "3",  
    100: "4",  
    101: "5",  
    102: "6",  
    103: "7",  
    104: "8",  
    105: "9",
    110: ".", 
}  # https://cherrytree.at/misc/vk.htm



def _get_key_name(key):
    '''
    return a tuple of (string representation of the key, virtual key code)
    put first in name buffer, second is normal buffer
    '''
    vk = None

    # normal char
    if isinstance(key, keyboard.KeyCode):#a~z and 0~9
        vk = key.vk
    # special key231
    elif isinstance(key, keyboard.Key):#shift,ctrl,alt,etc
        vk = key.value.vk

    if vk is None:return None,None
    if vk in VK_SPECIAL:
        return VK_SPECIAL[vk],VK_SPECIAL[vk]

    try:return chr(vk).lower(),chr(vk).lower()
    except:return None

class KeyMemHotkeys_class:
    def __init__(self,keymem_dict:dict,
                 command_dict:dict,
                 root:object,
                 icondir:str=None):
        '''
        Keymem_key = {func_name:str : key_combination:str}
        hotkey_dict = {func_name:str : function:Callable}
        Note both dicts should have matching keys
        This means that long running procedures and blocking operations should not be invoked from the callback, as this risks freezing input for all processes.
        root:required to build toplvl window
        '''

        self.set_keymem_buffer = set()
        self.set_keymem_name_buffer = set()
        self.root = root
        self.icondir = icondir
        self.is_setting_keymem = False
        self.keymem_dict = keymem_dict
        self.newhotkey = None   
        self.hotkey_dict = {}

        for funname in keymem_dict.keys():
            if funname in command_dict.keys():
                self.hotkey_dict[keymem_dict[funname]] = command_dict[funname]
            

        print(self.hotkey_dict)
        self.hotkey = GlobalHotKeys(self.hotkey_dict)
        self.hotkey.start()
    
    def set_keymem_onpress(self,key):
        
        name,vk = _get_key_name(key)
        print(f"Key pressed: {key}")
        if self.is_setting_keymem and name == "<enter>":
            self.is_setting_keymem = False
        if name not in self.set_keymem_buffer and name != "<enter>":
            self.set_keymem_buffer.add(vk)
            self.set_keymem_name_buffer.add(name)

    def set_keymem_onrelease(self,key):
        try:
            name,vk = _get_key_name(key)
            self.set_keymem_buffer.remove(vk)
            self.set_keymem_name_buffer.remove(name)
            print(self.set_keymem_buffer)
        except KeyError:
            pass
        
    def destory_global_hotkeys(self):
        try:
            self.hotkey.stop()
        except KeyError:
            pass





    def set_keymem(self,func_name):

        toplvl = CTk.CTkToplevel(self.root)
        toplvl.title("Hotkey Configuration")
        toplvl.geometry("550x520")
        if self.icondir:self.root.after(400, lambda: toplvl.iconbitmap(self.icondir))
        toplvl.attributes('-topmost', True)
        toplvl.resizable(False, False)
        toplvl.configure(fg_color='#1a1a1a')
        
        def on_close():
            self.is_setting_keymem = False
            self.newhotkey = None
            print(self.hotkey_dict)
            self.hotkey = GlobalHotKeys(self.hotkey_dict)
            self.set_keymem_listener.stop()
            self.hotkey.start()
            toplvl.destroy()
       
        toplvl.wm_protocol("WM_DELETE_WINDOW", on_close)

        # Main container with padding
        main_container = CTk.CTkFrame(toplvl, fg_color='transparent')
        main_container.pack(fill='both', expand=True, padx=20, pady=20)

        # Header frame with gradient-like effect
        header_frame = CTk.CTkFrame(main_container, fg_color='#2b5278', corner_radius=12, border_width=2, )
        header_frame.pack(pady=(0,15), fill='x')
        
        title_label = CTk.CTkLabel(header_frame, 
                                    font=('Segoe UI', 15, 'bold'), 
                                    text=f"Set Hotkey",
                                    text_color='white')
        title_label.pack(pady=6)
        
        function_label = CTk.CTkLabel(header_frame,
                                      font=('Arial', 14 , 'bold'),
                                      text=f"Function: {func_name}",
                                      text_color="#87EBD5")
        function_label.pack(pady=(0,12))
        
        # Instructions frame with better styling
        instructions_frame = CTk.CTkFrame(main_container, fg_color='#252525', corner_radius=12, border_width=1, border_color='#404040')
        instructions_frame.pack(pady=(0,15), fill='x')
        
        instruction_title = CTk.CTkLabel(instructions_frame,
                                        font=('Segoe UI', 13, 'bold'),
                                        text="📋 Instructions",
                                        text_color='#FFA500',
                                        anchor='w')
        instruction_title.pack(pady=(10,5), padx=20, anchor='w')
        
        instructions = [
            "▸ Press your desired key combination",
            "▸ Press Enter when finished to save",
            "▸ Avoid using Enter in the combination",
            "▸ ⚠️ Numpad keys are not supported"
        ]
        
        for instruction in instructions:
            inst_label = CTk.CTkLabel(instructions_frame,
                                     font=('Segoe UI', 14), 
                                     text=instruction,
                                     anchor='w',
                                     text_color='#CCCCCC')
            inst_label.pack(pady=1, padx=25, anchor='w')
        
        CTk.CTkLabel(instructions_frame, text="").pack(pady=5)  # Spacer

        # Current keys display frame with modern look
        keys_display_frame = CTk.CTkFrame(main_container, fg_color='#0a0a0a', corner_radius=12, border_width=2, border_color="#6E6E6E")
        keys_display_frame.pack(pady=(0,10), fill='x')
        

        
        keys_title = CTk.CTkLabel(keys_display_frame,
                                  font=('Segoe UI', 12, 'bold'),
                                  text="ACTIVE KEYS",
                                  text_color='#00FF00')
        keys_title.pack(pady=8)

        
        keypressed_label = CTk.CTkLabel(keys_display_frame,
                                        font=('Consolas', 16, 'bold'),
                                        text="[ Waiting... ]",
                                        text_color='#888888',
                                        height=40)  
        keypressed_label.pack(pady=15, padx=20)

        self.newhotkey = None
        self.is_setting_keymem = True
        
        self.set_keymem_buffer.clear()
        self.hotkey.stop()
        self.set_keymem_listener = Listener(on_press=self.set_keymem_onpress,
                    on_release=self.set_keymem_onrelease)
        self.set_keymem_listener.start()

        old_keyset = self.keymem_dict.get(func_name,"")
        while self.is_setting_keymem:
            try:
                toplvl.update()
                better_keyset = str(sorted(self.set_keymem_name_buffer)).replace('[','').replace(']','').replace("'",'').replace(',', ' + ')
                if self.set_keymem_name_buffer:
                    keypressed_label.configure(text=f"[ {better_keyset} ]", text_color='#00FF00')
                else:
                    keypressed_label.configure(text="[ Waiting... ]", text_color='#888888')

                time.sleep(0.01)
            except:
                    break
        # Print final result on a new line
        if toplvl.winfo_exists():
            keyset = "+".join(str(i) for i in self.set_keymem_buffer)
                
            self.newhotkey = keyset## use this to update the keymem_dict in caller
            self.keymem_dict[func_name] = keyset
            self.set_keymem_listener.stop()
            if self.newhotkey:self.hotkey_dict[self.keymem_dict[func_name]] = self.hotkey_dict.pop(old_keyset,None)
            
            print(f"Hotkey for {func_name} set to: {self.keymem_dict[func_name]}")
            self.is_setting_keymem = False
            
            self.set_keymem_buffer.clear()
            self.set_keymem_name_buffer.clear()
            self.hotkey = GlobalHotKeys(self.hotkey_dict)
            self.hotkey.start()
            self.set_keymem_listener.stop()
            toplvl.destroy()
            

        
def _test_func1():
    print("Function 1 triggered!")


if __name__ == "__main__":
    a = KeyMemHotkeys_class({"func1":'<ctrl>+j+1',},{
        'func1': lambda: _test_func1(),}, root=CTk.CTk())
    a.set_keymem("func1")

    while True:
        time.sleep(1)
        