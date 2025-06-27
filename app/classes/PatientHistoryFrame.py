import tkinter as tk
from tkinter import ttk
from configs.colors import *
from configs.sizes import *
from configs.fonts import *
from util.funs import *
from classes.TableFrame import *

class PatientHistoryFrame(TableFrame):
    
    def __init__(self, parent, table_headings, table_rows, patient_dict):
        # stile della Treeview
        stylename = 'PHTreeview'
        style = ttk.Style()
        style.theme_use('clam')
        style.layout(stylename, style.layout('Treeview'))
        style.configure(stylename, rowheight=SZ_tbl_pat_hist_row_h, background='black')
        style.map(stylename,
            background=[('active', CC_tbl_highlight), ('selected', CC_tbl_selected)],
            foreground=[('active', CC_tbl_text_highlight), ('selected', CC_tbl_text_selected)]
        )
        
        # dati del paziente
        nome = patient_dict['nome']
        cognome = patient_dict['cognome']
        
        # supercostruttore
        super(PatientHistoryFrame,self).__init__(
            parent, 
            table_headings, 
            table_rows, 
            f'Storico di {nome} {cognome}', 
            stylename)
        
        # configurazione delle colonne
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=2)
        self.columnconfigure(2, weight=1)
        
        # configurazione delle righe
        self.rowconfigure(0, weight=5)
        self.rowconfigure(1, weight=7)
        self.rowconfigure(2, weight=5)