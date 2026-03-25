import tkinter as tk
from tkinter import simpledialog, messagebox
from configs.colors import *
from configs.sizes import *
from configs.fonts import *
from configs.tables import *
from configs.paths import *
from gui.TableFrame import *
from gui.ImageCanvas import *
from gui.AddReportDialog import *
from utils.funs import *
from database import db_manager

class LoginFrame(tk.Frame):
    
    def __init__(self, parent):
        # supercostruttore
        super(LoginFrame,self).__init__(parent, bg=CC_frm_default)
        
        # contenitore dei widget
        frm_container = tk.Frame(self, bg=CC_frm_default)
        frm_container.pack(expand=True)

        # istanzia il logo e il nome dell'app
        img_canvas = ImageCanvas(frm_container, 
                                 PT_app_logo, 
                                 width=SZ_logo_w,
                                 height=SZ_logo_h,
                                 alt='Logo non trovato...')
        lbl_appname = tk.Label(frm_container, text='OCT-Analysis', fg=CC_appname_fg, bg=CC_frm_default, font=(FT_family, FT_appname_size, 'bold'))
        
        # pulsante di accesso (medico)
        btn_medic_login = tk.Button(frm_container, 
                                    text='Accedi come medico',
                                    width=SZ_btn_login,
                                    fg = CC_btn_login_fg,
                                    bg = CC_btn_login_bg,
                                    command=self.medic_login_check)
        
        # pulsante di accesso (paziente)
        btn_patient_login = tk.Button(frm_container,
                                      text='Accedi come paziente', 
                                      width=SZ_btn_login, 
                                      fg = CC_btn_login_fg,
                                      bg = CC_btn_login_bg,
                                      command=self.patient_login_check)
        
        # posizionamento dei widget
        img_canvas.pack(expand=True)
        lbl_appname.pack(fill='x', expand=True, pady=(0,50))
        btn_medic_login.pack(pady=(0,30))
        btn_patient_login.pack()
        
    def medic_login_check(self):
        ... #TODO: si potrebbe fare un vero login, con un vero check
        self.event_generate('<<DoctorLogged>>')
        
    def patient_login_check(self):
        # Crea una dialog per chiedere nome e cognome
        dlg = tk.Toplevel(self.master)
        dlg.title('Accesso Paziente')
        dlg.geometry('400x280')
        dlg.transient(self.master)
        dlg.grab_set()
        dlg.resizable(False, False)
        
        # Centra la finestra
        dlg.update_idletasks()
        x = self.master.winfo_x() + (self.master.winfo_width() // 2) - (400 // 2)
        y = self.master.winfo_y() + (self.master.winfo_height() // 2) - (280 // 2)
        dlg.geometry(f'+{x}+{y}')
        
        # Frame principale con padding
        frm_main = tk.Frame(dlg)
        frm_main.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Label e Entry per nome
        tk.Label(frm_main, text='Nome:', font=('Arial', 10)).pack(pady=(0, 5))
        entry_nome = tk.Entry(frm_main, width=40, font=('Arial', 10))
        entry_nome.pack(pady=(0, 15))
        entry_nome.focus()
        
        # Label e Entry per cognome
        tk.Label(frm_main, text='Cognome:', font=('Arial', 10)).pack(pady=(0, 5))
        entry_cognome = tk.Entry(frm_main, width=40, font=('Arial', 10))
        entry_cognome.pack(pady=(0, 20))
        
        def on_login():
            nome = entry_nome.get().strip()
            cognome = entry_cognome.get().strip()
            
            if not nome or not cognome:
                messagebox.showerror('Errore', 'Inserisci nome e cognome')
                return
            
            # Cerca il paziente nel database
            try:
                patient_dict = db_manager.get_patient_by_name(nome, cognome)
                if patient_dict is None:
                    messagebox.showerror('Errore', f'Paziente {nome} {cognome} non trovato')
                    return
                
                # Salva i dati del paziente e genera l'evento
                self.patient_data = patient_dict
                dlg.destroy()
                self.event_generate('<<PatientLogged>>')
            except Exception as e:
                messagebox.showerror('Errore', f'Errore nel login: {str(e)}')
        
        # Pulsante di accesso
        btn_login = tk.Button(frm_main, text='Accedi', width=20, font=('Arial', 10), command=on_login)
        btn_login.pack()
        
        dlg.wait_window()