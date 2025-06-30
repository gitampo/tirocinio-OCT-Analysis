import tkinter as tk
from tkinter import ttk
from configs.colors import *
from configs.sizes import *
from configs.fonts import *
from configs.tables import *
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
            table_headings[1:], 
            [t[1:] for t in table_rows], 
            f'Storico di "{nome} {cognome}"', 
            font_specs=(FT_family, FT_h2_size, 'bold'),
            columns_anchors_dict=AC_patient_history,
            columns_sizes_dict=CS_patient_history
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
        # se l'utente preme sull'heading, non deve fare niente
        region = self.tbl.identify_region(event.x, event.y)
        if region == "heading": return "break"

        # ottiene l'item della riga premuta
        item_iid = self.tbl.identify_row(event.y)
        item = self.tbl.item(item_iid)

        # dizionario del report composto da chiavi e valori (chiavi=headings, valori=valori dell'item)
        report_dict = dict(zip(self.tbl['columns'], item['values']))
    
        # dati condivisi con il parent
        self.shared_data = report_dict
    
        # genera un evento visibile dal padre e gli passa i dati dello storico cliccato
        self.event_generate('<<ReportRowClicked>>')