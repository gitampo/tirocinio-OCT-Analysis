import tkinter as tk
import tkinter.font as tkFont
from classes.TopBar import *
from classes.LoginFrame import *
from classes.PatientsListFrame import *
from classes.PatientHistoryFrame import *
from classes.ReportFrame import *
from configs.colors import *
from configs.fonts import *
from database import db_manager

class OCTAnalysisApp(tk.Tk):
    def __init__(self):
        super(OCTAnalysisApp,self).__init__()
    
        tkFont.nametofont('TkDefaultFont').configure(family=FT_family, size=FT_size)
        
        # configurazione della finestra principale
        self.title('OCT-Analysis')
        self.minsize(SZ_min_window_w, SZ_min_window_h)
        self.centered_geometry(w_ratio=SZ_window_w_ratio, h_ratio=SZ_window_h_ratio,
                               min_w=SZ_min_window_w, min_h=SZ_min_window_h)
        
        # configurazione degli eventi
        self.bind('<<PatientRowClicked>>', self.open_patient_history)
        self.bind('<<ReportRowClicked>>', self.open_report)
        self.bind('<<ReportRowAdded>>', self.refresh_patient_history)
        self.bind('<<DoctorLogged>>', self.redirect_doctor)
        self.bind('<<PatientLogged>>', self.redirect_patient)
        self.bind('<<GoBack>>', self.close_active_frame)
        self.bind('<Escape>', self.close_active_frame)
        self.bind('<<Logout>>', self.logout)
        
        # attributi di classe
        self.is_user_logged = False
        self.user_dict = None
        self.top_bar = None
        self.frm_opened_list = []
        self.who_is_logged = None
        self.frm_base = None
        
        # schermata di login
        self.frm_login = self.login()  
    
    def centered_geometry(self,
                          window_w = 100, window_h = 100, 
                          w_ratio = 0.1, h_ratio = 0.1, 
                          min_w = 0, min_h = 0, 
                          with_ratio=True):
        # dimensioni dello schermo
        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()
        
        if with_ratio:
            # dimensioni della finestra (in proporzione)
            window_w = int(screen_w * w_ratio if w_ratio>=0.1 else 0.1) # il ratio deve essere almeno 10%
            window_h = int(screen_h * h_ratio if h_ratio>=0.1 else 0.1) # il ratio deve essere almeno 10%

            # controllo sulle dimensioni minime
            if window_w < min_w: window_w = min_w
            if window_h < min_h: window_h = min_h

        # calcola la posizione centrata
        left, top = centered_position((screen_w, screen_h), (window_w, window_h))
        
        # posizionamento centrato
        self.geometry(f'{window_w}x{window_h}+{left}+{top}')
        
    def login(self):                
        # configurazione di righe e colonne
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        
        # schermata di login
        frm_login = LoginFrame(self)
        frm_login.grid(row=0, column=0, sticky='nswe')
        
        return frm_login
        
    def redirect_doctor(self, event):
        # chiude la schermata di login
        self.frm_login.destroy()
        
        # ricorda chi è loggato
        self.who_is_logged = 'doctor'
        
        # configurazione di righe e colonne
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=0)
        self.rowconfigure(1, weight=1)
        
        # ottiene i dati del paziente che sta loggando
        doctor_dict = db_manager.get_doctor(2)
        prefix = 'Dott.' if doctor_dict['sesso']=='M' else 'Dott.ssa'
        
        # barra superiore
        self.top_bar = TopBar(self, f'{prefix} {doctor_dict["nome"]} {doctor_dict["cognome"]}')       
        self.top_bar.grid(row=0, column=0, sticky='we')
        
        # schermata dei pazienti
        self.frm_base = self.open_patients_list()

    def redirect_patient(self, event): 
        # chiude la schermata di login   
        self.frm_login.destroy()

        self.who_is_logged = 'patient'
        
        # configurazione di righe e colonne
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=0)
        self.rowconfigure(1, weight=1)
        
        # ottiene i dati del paziente che sta loggando
        patient_dict = db_manager.get_patient(1)
        
        # barra superiore
        self.top_bar = TopBar(self, f'{patient_dict["nome"]} {patient_dict["cognome"]}')       
        self.top_bar.grid(row=0, column=0, sticky='we')
        
        # dati da trasmettere
        event.widget.shared_data = patient_dict
        
        # schermata dei pazienti
        self.frm_base = self.open_patient_history(event)
        
    def open_patients_list(self):
        # retrieve dei dati
        patients_headings, patients_rows = db_manager.get_all_patients()
        
        # frame della lista di pazienti
        frm_patients = PatientsListFrame(self, patients_headings, patients_rows)
        
        # posiziona il frame
        frm_patients.grid(row=1, column=0, sticky='nswe')
                
        return frm_patients
        
    def open_patient_history(self, event):
        # ottiene i dati condivisi tramite evento se ce ne sono
        patient_dict = event.widget.shared_data
        if patient_dict is None or (not patient_dict): return

        # ottiene lo storico del paziente cercato
        patient_id = patient_dict['id']
        patient_history_headings, patient_history_rows = db_manager.get_patient_history(patient_id)
        
        # istanzia il frame del paziente selezionato e lo porta in primo piano
        frm_patient_history = PatientHistoryFrame(self, patient_history_headings, patient_history_rows, patient_dict, self.who_is_logged)
        frm_patient_history.grid(row=1, column=0, sticky='nswe')
        frm_patient_history.tkraise()
        
        # mostra il tasto per tornare indietro
        if self.who_is_logged == 'doctor':
            self.top_bar.show_back_button()
        
            # aggiunge il nuovo frame aperto in cima alla lista dei frame aperti
            self.frm_opened_list.insert(0, frm_patient_history)
            
        return frm_patient_history
          
    def open_report(self, event):
        # ottiene i dati condivisi tramite evento se ce ne sono
        report_dict = event.widget.shared_data
        if report_dict is None or (not report_dict): return

        # ottiene lo storico del paziente cercato
        report_image_path = Path(PT_images_dir)/report_dict['oct']
        
        # istanzia il frame del report selezionato e lo porta in primo piano
        frm_report = ReportFrame(self, report_image_path)
        frm_report.grid(row=1, column=0, sticky='nswe')
        frm_report.tkraise()
        
        # mostra il tasto per tornare indietro
        self.top_bar.show_back_button()
        
        # aggiunge il nuovo frame aperto in cima alla lista dei frame aperti
        self.frm_opened_list.insert(0, frm_report)
            
    def close_active_frame(self, event=None):
       
        # se c'è un frame aperto, lo chiude
        if len(self.frm_opened_list)!=0:
            top_frame = self.frm_opened_list[0]
            top_frame.destroy()
            if hasfunc(top_frame, 'close_toplevels'): top_frame.close_toplevels()
            self.frm_opened_list.remove(top_frame)
            
        # se non ci sono più ulteriori frame aperti, nasconde il pulsante per tornare indietro
        if len(self.frm_opened_list)==0:
            # nasconde il tasto per tornare indietro
            self.top_bar.hide_back_button()
            
    def refresh_patient_history(self, event):
        self.close_active_frame()
        self.open_patient_history(event)
        
    def reset_grid(self):
        # per tutti i figli della finestra
        for widget in self.winfo_children():
            # ottiene informazioni sul grid del figlio
            info = widget.grid_info()
            
            if info:
                # resetta tutti i 'weight' delle righe e delle colonne usate
                self.rowconfigure(info['row'], weight=0)
                self.columnconfigure(info['column'], weight=0)
        
    def close_all(self):    
        # chiude tutti i frame aperti
        for frm in self.frm_opened_list:
            frm.destroy()
        
        # chiude il frame 'home'
        self.frm_base.destroy()
    
    def logout(self, event):    

        self.reset_grid()
        self.close_all()
        self.frm_login = self.login()