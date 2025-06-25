import tkinter as tk
import tkinter.font as tkFont
from classes.TopBar import *
from classes.PatientsFrame import *
from configs.colors import *
from configs.fonts import *

class OCTAnalysisApp(tk.Tk):
    def __init__(self):
        super(OCTAnalysisApp,self).__init__()
    
        tkFont.nametofont('TkDefaultFont').configure(family=FT_family, size=FT_size)
        
        # configurazione della finestra principale
        self.title('OCT-Analysis')
        self.minsize(SZ_min_window_w, SZ_min_window_h)
        self.centered_geometry(SZ_window_w, SZ_window_h)
        
        # barra superiore
        top_bar = TopBar()
        top_bar.grid(row=0, column=0, sticky='nswe')
        
        # frame principale
        self.rowconfigure(1, weight=1)
        self.columnconfigure(0, weight=1)
        frm_patients = PatientsFrame()
        frm_patients.grid(row=1, column=0, sticky='nswe')
        
    def centered_geometry(self,window_w, window_h):
        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()
        
        # calcolo della posizione della finestra
        left = (screen_w-window_w)//2
        top  = (screen_h-window_h)//2
        
        # posizionamento centrato
        self.geometry(f'{window_w}x{window_h}+{left}+{top}')
        