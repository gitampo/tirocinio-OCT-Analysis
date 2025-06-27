import tkinter as tk
from tkinter import ttk
from configs.colors import *
from configs.sizes import *
from configs.fonts import *
from util.funs import *
from classes.TableFrame import *

class PatientHistoryFrame(TableFrame):
    
    def __init__(self, parent, table_headings, table_rows, patient_dict):
       
        # dati del paziente
        nome = patient_dict['nome']
        cognome = patient_dict['cognome']
        
        # supercostruttore
        super(PatientHistoryFrame,self).__init__(
            parent, 
            table_headings, 
            table_rows, 
            f'Storico di {nome} {cognome}', 
            font_specs=(FT_family, FT_h2_size, 'bold')
        )
        
        # configurazione delle colonne
        self.columnconfigure(1, weight=1)
        
        # configurazione delle righe
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=10)