import tkinter as tk
from tkinter import ttk
import tkinter.font as tkFont
from classes.TopBar import *
from classes.PatientsFrame import *
from classes.OnePatientFrame import *
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
        top_bar = TopBar()
        top_bar.grid(row=0, column=0, sticky='nswe')
        
        # retrieve dei dati
        patients_headings, patients_rows = data.retrieve_all_patients()
        
        # frame principale
        self.rowconfigure(1, weight=1)
        self.columnconfigure(0, weight=1)
        frm_patients = PatientsFrame(self, patients_headings, patients_rows)
        frm_patients.grid(row=1, column=0, sticky='nswe')
    
    def centered_geometry(self,window_w, window_h):
        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()
        
        # calcolo della posizione della finestra
        left = (screen_w-window_w)//2
        top  = (screen_h-window_h)//2
        
        # posizionamento centrato
        self.geometry(f'{window_w}x{window_h}+{left}+{top}')
        
    def open_patient_frame(self, patient_dict):
        
        patient_id = patient_dict['id']
        
        patient_history_headings, patient_history_rows = data.retrieve_one_patient_history(patient_id)
        print(patient_history_rows)
                
        # istanzia il frame del paziente selezionato e lo porta in primo piano
        frm_one_patient = OnePatientFrame(self, patient_history_headings, patient_history_rows)
        frm_one_patient.grid(row=1, column=0, sticky='nswe')
        frm_one_patient.tkraise()