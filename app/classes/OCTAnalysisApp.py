import tkinter as tk
from tkinter import ttk
import tkinter.font as tkFont
from classes.TopBar import *
from classes.PatientsListFrame import *
from classes.PatientHistoryFrame import *
from configs.colors import *
from configs.fonts import *
import util.data as data

class OCTAnalysisApp(tk.Tk):
    def __init__(self):
        super(OCTAnalysisApp,self).__init__()
    
        tkFont.nametofont('TkDefaultFont').configure(family=FT_family, size=FT_size)
        
        # configurazione della finestra principale
        self.title('OCT-Analysis')
        self.minsize(SZ_min_window_w, SZ_min_window_h)
        self.centered_geometry(SZ_window_w, SZ_window_h)
        
        # barra superiore
        top_bar = TopBar(self)
        top_bar.grid(row=0, column=0, sticky='nswe')
        
        # retrieve dei dati
        patients_headings, patients_rows = data.retrieve_all_patients()
        
        # frame principale
        self.rowconfigure(1, weight=1)
        self.columnconfigure(0, weight=1)
        frm_patients = PatientsListFrame(self, patients_headings, patients_rows)
        frm_patients.grid(row=1, column=0, sticky='nswe')
        
        # confugurazione degli eventi
        self.bind('<Escape>', self.close_patient_history)
        self.bind('<<PatientRowClicked>>', self.open_patient_history)
        self.bind('<<GoBack>>', self.close_patient_history)
        
        # attributi di classe
        self.top_bar = top_bar
        self.frm_patients = frm_patients
        self.frm_patient_history = None
    
    def centered_geometry(self,window_w, window_h):
        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()
        
        # calcolo della posizione della finestra
        left = (screen_w-window_w)//2
        top  = (screen_h-window_h)//2
        
        # posizionamento centrato
        self.geometry(f'{window_w}x{window_h}+{left}+{top}')
        
    def open_patient_history(self, event):
        
        # ottiene i dati condivisi dal tramite evento se ce ne sono
        patient_dict = event.widget.shared_data
        if patient_dict is None or (not patient_dict): return

        # ottiene lo storico del paziente cercato
        patient_id = patient_dict['id']
        patient_history_headings, patient_history_rows = data.retrieve_one_patient_history(patient_id)
        
        # istanzia il frame del paziente selezionato e lo porta in primo piano
        frm_patient_history = PatientHistoryFrame(self, patient_history_headings, patient_history_rows, patient_dict)
        frm_patient_history.grid(row=1, column=0, sticky='nswe')
        frm_patient_history.tkraise()
        
        # mostra il tasto per tornare indietro
        self.top_bar.show_back_button()
        
        # salva il nuovo frame nell'istanza
        self.frm_patient_history = frm_patient_history
          
    def close_patient_history(self, event):
        # nasconde il tasto per tornare indietro
        self.top_bar.hide_back_button()
        
        # se c'è un frame aperto di uno storico, lo chiude
        if self.frm_patient_history is not None:
            self.frm_patient_history.destroy()
        # resetta l'attributo d'istanza
        self.frm_patient_history = None