import tkinter as tk
from tkinter import ttk
from configs.colors import *
from configs.sizes import *
from configs.fonts import *
from configs.tables import *
from classes.TableFrame import *
from classes.ImageCanvas import *
from classes.AddReportDialog import *
from util.funs import *
from PIL import Image, ImageTk

class LoginFrame(tk.Frame):
    
    def __init__(self, parent):
        # supercostruttore
        super(LoginFrame,self).__init__(parent, bg=CC_frm_default)
        
        # contenitore dei widget
        frm_container = tk.Frame(self, width=100, height=10, bg=CC_frm_default)
        frm_container.pack(expand=True)

        # istanzia il logo e il nome dell'app
        img_canvas = ImageCanvas(frm_container, './assets/app_logo.png', alt='Logo non trovato...')
        lbl_appname = tk.Label(frm_container, text='OCT-Analysis', fg=CC_appname_fg, bg=CC_frm_default, font=(FT_family, FT_appname_size, 'bold'))
        
        # pulsante di accesso (medico)
        btn_medic_login = tk.Button(frm_container, 
                                    text='Accedi come medico',
                                    width=50,
                                    fg = CC_btn_login_fg,
                                    bg = CC_btn_login_bg,
                                    command=self.medic_login_check)
        
        # pulsante di accesso (paziente)
        btn_patient_login = tk.Button(frm_container,
                                      text='Accedi come paziente', 
                                      width=50, 
                                      fg = CC_btn_login_fg,
                                      bg = CC_btn_login_bg,
                                      command=self.patient_login_check)
        
        # posizionamento dei widget
        img_canvas.pack(fill='both', expand=True)
        lbl_appname.pack(fill='x', expand=True, pady=(0,50))
        btn_medic_login.pack(pady=(0,30))
        btn_patient_login.pack()
        
    def medic_login_check(self):
        ... #TODO: si potrebbe fare un vero login, con un vero check
        self.event_generate('<<DoctorLogged>>')
        
    def patient_login_check(self):
        ... #TODO: si potrebbe fare un vero login, con un vero check
        self.event_generate('<<PatientLogged>>')