import tkinter as tk
from tkinter import font as tkFont
from tkinter import messagebox
from configs.colors import *
from configs.sizes import *
from configs.fonts import *

class TopBar(tk.Frame):
    
    def __init__(self, parent, user='Anonimo'):
        super(TopBar,self).__init__(parent, height=SZ_topbar_h, bg=CC_topbar, padx=10, pady=10)
        
        # impedisce al 'pack geometry manager' di adattare la dimensione della topbar al contenuto
        self.pack_propagate(False)
        
        # stile sottolineato per la scritta di logout
        underlined = tkFont.Font(family=FT_family, size=FT_logout_size, underline=True)
        
        # nome utente loggato
        lbl_user = tk.Label(self, text='Utente: ', font=(FT_family,FT_size,'bold'), bg=CC_topbar, fg=CC_topbar_text)
        lbl_user_value = tk.Label(self, text=user, bg=CC_topbar, fg=CC_topbar_text, pady=10) 
        lbl_logout = tk.Label(self, text='Logout', bg=CC_topbar, fg=CC_topbar_logout, padx=10, pady=10, font=underlined) 
        
        # posizionamento dei widget
        lbl_logout.pack(side='right')
        lbl_user_value.pack(side='right', padx=(0,10))
        lbl_user.pack(side='right')
        
        # gestione del logout
        lbl_logout.bind('<Button-1>',self.logout)
        
        # pulsante per tornare indietro
        self.btn_back = tk.Button(self, 
                                  text='Indietro (Esc)', 
                                  fg=CC_topbar_btn_back_fg,
                                  bg=CC_topbar_btn_back_bg,
                                  command=lambda: self.btn_back.event_generate('<<GoBack>>'))
        
    def logout(self, event):
        # chiede all'utente se vuole uscire
        want_to_logout = messagebox.askyesno('Logout', 'Sei sicuro di voler uscire dal tuo profilo? \nTornerai alla schermata di Accesso.')
        
        # valuta la risposta dell'utente
        if want_to_logout: self.alert_parent_of_logout()
        
    def alert_parent_of_logout(self):
        self.event_generate('<<Logout>>')
        
    def show_menu(self, event):
        self.menu.tk_popup(event.x_root-20, event.y_root)
        
    def show_back_button(self):
        self.btn_back.pack(side='left')
        
    def hide_back_button(self):
        self.btn_back.pack_forget()