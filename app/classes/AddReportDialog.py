import tkinter as tk
from tkinter import ttk
import tkinter.font as tkFont
from configs.colors import *
from configs.fonts import *
from configs.sizes import *
from util.funs import * 
from datetime import datetime
from tkinter import filedialog, messagebox
from shutil import copy
import os

class AddReportDialog(tk.Toplevel):
    
    def __init__(self, parent):
        super(AddReportDialog,self).__init__()
        
        # il font di default del dialog
        tkFont.nametofont('TkDefaultFont').configure(family=FT_family, size=FT_size)
        
        # conifigurazione del dialog
        self.title('Aggiungi un nuovo Report')
        self.minsize(SZ_min_dialog_w, SZ_min_dialog_h)
        self.centered_geometry(SZ_dialog_w, SZ_dialog_h)
        
        self.added_image = None
        
        # imposta il layout (label, button, text...)
        self.lbl_image_value = self.setupLayout()        

    def setupLayout(self):
        
        ### contenitori (frame)
        
        # frame principale che contiene tutti i widget
        frm_container = tk.Frame(self, bg=CC_dlg, padx=20, pady=20)
        frm_container.pack(fill='both', expand=True)
               
        # sotto-frame per i campi
        frm_date = tk.Frame(frm_container, bg=CC_dlg_field)
        frm_description = tk.Frame(frm_container, bg=CC_dlg_field)
        frm_image = tk.Frame(frm_container, bg=CC_dlg_field)
               
        ### widget
        
        # etichette degli input
        lbl_date = self.setupLabel(frm_date, 'Data: ')
        lbl_description = self.setupLabel(frm_description, 'Descrizione: ')
        lbl_image = self.setupLabel(frm_image, 'Immagine: ')   
        
        # input dell'utente
        time_now = datetime.now().strftime('%Y-%m-%d %H:%M')# ottiene il tempo attuale, nel formato corretto
        lbl_date_value = self.setupLabel(frm_date, f'{time_now}', (FT_family, FT_size, ''))
        lbl_image_value = self.setupLabel(frm_image, '...', (FT_family, FT_size, ''))
        txt_description = tk.Text(frm_description, relief='flat', height=3)
        btn_image = tk.Button(frm_container, text='Inserisci immagine +', command=self.add_image, fg=CC_btn_image_fg, bg=CC_btn_image_bg, relief='flat')
        btn_submit = tk.Button(frm_container, text='Aggiungi questo Report', fg=CC_btn_submit_fg, bg=CC_btn_submit_bg, height=2)
        
        ### posizionamento dei widget
        
        # data
        lbl_date.pack(side='left',fill='x')
        lbl_date_value.pack(side='left',fill='x', expand=True)
        frm_date.pack(fill='both', expand=True)
        
        # descrizione
        lbl_description.pack(fill='both', expand=True)
        txt_description.pack(fill='both', expand=True, pady=(5,10), padx=5)
        frm_description.pack(fill='both', expand=True, pady=10)
        
        # immagine
        lbl_image.pack(side='left', fill='x')
        lbl_image_value.pack(side='left',fill='x', expand=True)
        frm_image.pack(fill='both', expand=True)
        
        # pulsante per l'immagine
        btn_image.pack(fill='both', expand=True)
        
        # pulsante per l'invio dei dati
        btn_submit.pack(fill='both', expand=True, pady=(30,10))
        
        return lbl_image_value
    
    def setupLabel(self, parent, text, font_specs = (FT_family, FT_size, 'bold')):
        return tk.Label(parent, 
            text=text, 
            anchor='w', 
            justify='left',
            bg=CC_dlg_field,
            padx=5, pady=5,
            font=font_specs)
        
    def centered_geometry(self,window_w, window_h):
        # dimensioni dello schermo
        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()
        
        # calcola la posizione centrata
        left, top = centered_position((screen_w, screen_h), (window_w, window_h))
        
        # posizionamento centrato
        self.geometry(f'{window_w}x{window_h}+{left}+{top}')
        
    def add_image(self):
        imagepath = filedialog.askopenfilename(
            title='Seleziona un immagine',
            filetypes=[
                ('Tutti i file', '*.*'), 
                ('JPG', '*.jpg'),
                ('JPEG', '*.jpeg'),
                ('PNG', '*.png')
            ]
        )
        
        # ottiene il nome e l'estensione del file
        # TODO copy(imagepath, './images')
        self.added_image, extension = os.path.splitext(imagepath)
        
        # se l'estensione è valida, accetta il file
        valid_extensions = ('.png','.jpg','.jpeg')
        if(extension in valid_extensions):
            self.lbl_image_value['text'] = self.added_image
        else:
            messagebox.showwarning('File non valido!', f'Il File selezionato non è tra i seguenti tipi: {", ".join(valid_extensions)}')
            
        