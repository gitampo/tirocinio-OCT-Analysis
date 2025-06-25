import tkinter as tk
from configs.colors import *
from configs.sizes import *

class TopBar(tk.Frame):
    
    def __init__(self):
        super(TopBar,self).__init__(height=SZ_topbar_h, bg=CC_cobalt, padx=10, pady=10)
        
        self.pack_propagate(False)
        lbl_username = tk.Label(self, text='Dott. Mario Rossi', bg=CC_cobalt, fg=CC_white)
        lbl_username.pack(side='right', fill='y')