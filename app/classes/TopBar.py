import tkinter as tk
from configs.colors import *
from configs.sizes import *
from configs.fonts import *

class TopBar(tk.Frame):
    
    def __init__(self, parent):
        super(TopBar,self).__init__(height=SZ_topbar_h, bg=CC_topbar, padx=10, pady=10)
        
        # impedisce al 'pack geometry manager' di adattare la dimensione della topbar al contenuto
        self.pack_propagate(False)
        
        lbl_user = tk.Label(self, text='Utente:', font=('',FT_size,'bold'), bg=CC_topbar, fg=CC_topbar_text) # TODO vedi se cambiare il text
        lbl_name = tk.Label(self, text='Dott. Mario Rossi', bg=CC_topbar, fg=CC_topbar_text) # TODO vedi se cambiare il text
        lbl_name.pack(side='right')
        lbl_user.pack(side='right')
        
        # pulsante per tornare indietro
        self.btn_back = tk.Button(self, 
                                  text='Indietro (Esc)', 
                                  fg=CC_topbar_btn_back_fg,
                                  bg=CC_topbar_btn_back_bg,
                                  command=lambda: self.btn_back.event_generate('<<GoBack>>'))
        
    def show_back_button(self):
        self.btn_back.pack(side='left')
        
    def hide_back_button(self):
        self.btn_back.pack_forget()