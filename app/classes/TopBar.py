import tkinter as tk
from configs.colors import *
from configs.sizes import *

class TopBar(tk.Frame):
    
    def __init__(self, parent):
        super(TopBar,self).__init__(height=SZ_topbar_h, bg=CC_topbar, padx=10, pady=10)
        
        # impedisce al 'pack geometry manager' di adattare la dimensione della topbar al contenuto
        self.pack_propagate(False)
        
        # Nome dell'utente registrato
        lbl_username = tk.Label(self, text='Dott. Mario Rossi', bg=CC_topbar, fg=CC_topbar_text) # TODO vedi se cambiare il text
        lbl_username.pack(side='right')
        
        # pulsante per tornare indietro
        self.btn_back = tk.Button(self, text='Indietro (Esc)', command=lambda: self.btn_back.event_generate('<<GoBack>>'))
        
    def show_back_button(self):
        self.btn_back.pack(side='left')
        
    def hide_back_button(self):
        self.btn_back.pack_forget()