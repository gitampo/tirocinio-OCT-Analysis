import tkinter as tk
from tkinter import ttk
import tkinter.font as tkFont
from classes.TopBar import *
from classes.PatientsListFrame import *
from classes.PatientHistoryFrame import *
from classes.ReportFrame import *
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
        self.bind('<<PatientRowClicked>>', self.open_patient_history)
        self.bind('<<ReportRowClicked>>', self.open_report)
        self.bind('<<GoBack>>', self.close_active_frame)
        self.bind('<Escape>', self.close_active_frame)
        
        # attributi di classe
        self.top_bar = top_bar
        self.frm_patients = frm_patients
        self.frm_opened_list = []
    
    def centered_geometry(self,window_w, window_h):
        # dimensioni dello schermo
        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()
        
        # calcola la posizione centrata
        left, top = centered_position((screen_w, screen_h), (window_w, window_h))
        
        # posizionamento centrato
        self.geometry(f'{window_w}x{window_h}+{left}+{top}')
        
    def open_patient_history(self, event):
        # ottiene i dati condivisi tramite evento se ce ne sono
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
        
        # aggiunge il nuovo frame aperto in cima alla lista dei frame aperti
        self.frm_opened_list.insert(0, frm_patient_history)
          
    def open_report(self, event):
        # ottiene i dati condivisi tramite evento se ce ne sono
        report_dict = event.widget.shared_data
        if report_dict is None or (not report_dict): return

        # ottiene lo storico del paziente cercato
        report_img = report_dict['oct']
        
        # istanzia il frame del report selezionato e lo porta in primo piano
        frm_report = ReportFrame(self, report_img)
        frm_report.grid(row=1, column=0, sticky='nswe')
        frm_report.tkraise()
          
        # mostra il tasto per tornare indietro
        self.top_bar.show_back_button()
        
        # aggiunge il nuovo frame aperto in cima alla lista dei frame aperti
        self.frm_opened_list.insert(0, frm_report)
          
    def close_active_frame(self, event):
       
        # se c'è un frame aperto, lo chiude
        if len(self.frm_opened_list)!=0:
            top_frame = self.frm_opened_list[0]
            top_frame.destroy()
            if hasfunc(top_frame, 'close_subwindows'): top_frame.close_subwindows()
            self.frm_opened_list.remove(top_frame)
            
        # se non ci sono più ulteriori frame aperti, nasconde il pulsante per tornare indietro
        if len(self.frm_opened_list)==0:
            # nasconde il tasto per tornare indietro
            self.top_bar.hide_back_button()