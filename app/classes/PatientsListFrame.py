import tkinter as tk
from tkinter import ttk
from configs.colors import *
from configs.sizes import *
from configs.fonts import *
from configs.tables import *
from util.funs import *
from classes.TableFrame import *

class PatientsListFrame(TableFrame):
    
    def __init__(self, parent, table_headings, table_rows):        
        
        # supercostruttore
        super(PatientsListFrame,self).__init__(
            parent, 
            table_headings, 
            table_rows, 
            'Lista dei pazienti',
            row=0, column=0,
            columns_anchors_dict=AC_patients_list,
            columns_sizes_dict=CS_patients_list
        )
        
        # dati da condividere con il parent (inizialmente non ci sono dati)
        self.shared_data = None
        
        # associa l'apertura dello storico del paziente, all'evento del click sulla riga
        self.tbl.bind('<Button-1>', self.alert_parent)
        
        # configurazione di righe e colonne
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

    def alert_parent(self, event):
        # se l'utente preme sull'heading, non deve fare niente
        region = self.tbl.identify_region(event.x, event.y)
        if region not in ('cell','tree'): return 

        # ottiene l'iid della riga premuta
        clicked_iid = self.tbl.identify_row(event.y)
        if not clicked_iid: return
        clicked_item = self.tbl.item(clicked_iid)

        # dizionario del paziente composto da chiavi e valori (chiavi=headings, valori=valori dell'item)
        patient_dict = dict(zip(self.tbl['columns'], clicked_item['values']))
    
        # dati condivisi con il parent
        self.shared_data = patient_dict
    
        # genera un evento visibile dal padre e gli passa i dati del paziente cliccato
        self.event_generate('<<PatientRowClicked>>')