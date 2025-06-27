import tkinter as tk
from tkinter import ttk
from configs.colors import *
from configs.sizes import *
from configs.fonts import *
from util.funs import *
from classes.TableFrame import *

class PatientsListFrame(TableFrame):
    
    def __init__(self, parent, table_headings, table_rows):        
        
        # supercostruttore
        super(PatientsListFrame,self).__init__(
            parent, 
            table_headings, 
            table_rows, 
            'Lista dei pazienti'
        )
        
        # dati da condividere con il parent (inizialmente non ci sono dati)
        self.shared_data = None
        
        # associa l'apertura dello storico del paziente, all'evento del click sulla riga
        self.tbl.bind('<Button-1>', self.alert_parent)
        
        # configurazione delle colonne
        self.columnconfigure(1, weight=1)
        
        # configurazione delle righe
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=10)

    def alert_parent(self, event):
        region = self.tbl.identify_region(event.x, event.y)
        if region == "heading": return "break"


        # ottiene l'id del paziente 
        item_iid = self.tbl.identify_row(event.y)
        item = self.tbl.item(item_iid)

        # dizionario del paziente composto da chiavi e valori (chiavi=headings, valori=valori dell'item)
        patient_dict = dict(zip(self.tbl['columns'], item['values']))
    
        # dati condivisi con il parent
        self.shared_data = patient_dict
    
        # genera un evento visibile dal padre e gli passa i dati del paziente cliccato
        self.event_generate('<<PatientRowClicked>>')