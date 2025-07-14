import tkinter as tk
import tkinter.font as tkFont
from configs.colors import *
from configs.fonts import *
from configs.sizes import *
from util.funs import * 
from datetime import datetime
from tkinter import filedialog, messagebox
import os
import shutil
import pandas as pd

class AddReportDialog(tk.Toplevel):
    
    def __init__(self, parent, patient_dict):
        super(AddReportDialog,self).__init__(parent)
        
        # il font di default del dialog
        tkFont.nametofont('TkDefaultFont').configure(family=FT_family, size=FT_size)
        
        # conifigurazione del dialog
        self.title('Aggiungi un nuovo Report')
        self.centered_geometry(SZ_dialog_w, SZ_dialog_h)
        self.resizable(False, False)
        self.transient(parent)  # Si comporta come finestra figlia
        self.grab_set()         # Blocca l'interazione con la main window
        self.focus_force()      # Forza il focus
        
        # attributi di classe
        self.parent = parent
        self.patient_dict = patient_dict
        self.entered_imagepath = None
        
        # imposta il layout (label, text, button...)
        lbl_date_value, txt_description, lbl_image_value = self.setupLayout()        

        # widget di classe
        self.lbl_date_value = lbl_date_value 
        self.txt_description = txt_description 
        self.lbl_image_value = lbl_image_value

    def setupLayout(self):
        
        ### contenitori (frame)
        
        # frame contenitore (principalmente per background)
        frm_container = tk.Frame(self, bg=CC_dlg)
        
        # frame form
        frm_form = tk.Frame(frm_container, bg=CC_dlg, padx=20, pady=20)
               
        # sotto-frame per i campi
        frm_data = tk.Frame(frm_form, bg=CC_dlg_field)
        frm_description = tk.Frame(frm_form, bg=CC_dlg_field)
        frm_image = tk.Frame(frm_form, bg=CC_dlg_field)
               
        ### widget
        
        # etichette degli input
        lbl_patient_id = self.setupLabel(frm_data, 'ID Paziente: ')
        lbl_patient_name_surname = self.setupLabel(frm_data, 'Nome e Cognome: ')
        lbl_date = self.setupLabel(frm_data, 'Data: ')
        lbl_description = self.setupLabel(frm_description, 'Descrizione: ')
        lbl_image = self.setupLabel(frm_image, 'Immagine: ')
        
        # dati mostrati (id, nome e cognome del paziente e data di inserimento del report)
        patient_id = str(self.patient_dict['id']).rjust(4,'0')
        patient_name_surname= self.patient_dict['nome'] + " " + self.patient_dict['cognome']
        time_now = datetime.now().strftime('%Y-%m-%d %H:%M')# ottiene il tempo attuale, nel formato corretto
        
        # input dell'utente
        lbl_patient_id_value = self.setupValue(frm_data, f'{patient_id}')
        lbl_patient_name_surname_value = self.setupValue(frm_data, patient_name_surname)
        lbl_date_value = self.setupValue(frm_data, f'{time_now}')
        lbl_image_value = self.setupValue(frm_image, '. . .')
        txt_description = tk.Text(frm_description, relief='flat', height=5)
        btn_image = tk.Button(frm_form, 
                            text='Inserisci immagine +', 
                            command=self.add_image, 
                            height=1, 
                            fg=CC_btn_image_fg, bg=CC_btn_image_bg, relief='flat')
        btn_submit = tk.Button(frm_form, 
                            text='Aggiungi questo Report',  
                            command=self.add_report, 
                            height=2, 
                            fg=CC_btn_submit_fg, bg=CC_btn_submit_bg)
        
        ### posizionamento dei widget
        
        # contenitori
        frm_container.pack(fill='both', expand=True)
        frm_form.pack(expand=True)
        frm_data.pack(fill='x')
        frm_data.columnconfigure(1, weight=1)
        
        # campi dei dati
        data_fields = [
            (lbl_patient_id, lbl_patient_id_value),
            (lbl_patient_name_surname, lbl_patient_name_surname_value),
            (lbl_date, lbl_date_value)
            ]
        
        # posiziona etichette e valori, per ogni campo
        for i,(label,value) in enumerate(data_fields):
            label.grid(row=i, column=0, sticky='we')
            value.grid(row=i, column=1, sticky='we')
        
        # descrizione
        lbl_description.pack(fill='x')
        txt_description.pack(pady=(5,10), padx=5, fill='x')
        frm_description.pack(fill='x', pady=10)
        
        # immagine
        lbl_image.pack(side='left', fill='x')
        lbl_image_value.pack(side='left', fill='x', expand=True)
        lbl_image_value['anchor'] = 'center'
        frm_image.pack(fill='x')
        
        # pulsante per l'immagine
        btn_image.pack(fill='x')
        
        # pulsante per l'invio dei dati
        btn_submit.pack(fill='x', pady=(30,10))
        
        return lbl_date_value, txt_description, lbl_image_value
    
    def setupLabel(self, parent, text):
        return tk.Label(parent, 
            text=text, 
            anchor='w', 
            justify='left',
            fg=CC_dlg_label_fg,
            bg=CC_dlg_label_bg,
            padx=5, pady=5,
            font=(FT_family, FT_size, 'bold'))
        
    def setupValue(self, parent, text):
        return tk.Label(parent, 
            text=text, 
            anchor='w', 
            justify='left',
            fg=CC_dlg_value_fg,
            bg=CC_dlg_value_bg,
            padx=5, pady=5)
        
    def centered_geometry(self,window_w, window_h):
        # dimensioni dello schermo
        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()
        
        # calcola la posizione centrata
        left, top = centered_position((screen_w, screen_h), (window_w, window_h))
        
        # posizionamento centrato
        self.geometry(f'{window_w}x{window_h}+{left}+{top}')
        
    def add_report(self):    
        
        # ottiene i valori di input
        submitted_date = self.lbl_date_value['text']
        submitted_description = self.txt_description.get('1.0','end-1c')
        submitted_imagepath = self.entered_imagepath
        
        # controlli sui dati di input
        if not submitted_description:
            messagebox.showwarning('Attenzione!','È necessario inserire una descrizione al Report')
            return
        elif not submitted_imagepath: 
            messagebox.showwarning('Attenzione!','È necessario inserire un\'immagine di un OCT')
            return
                
        # controlla se il nome è già preso
        image_filename = os.path.basename(submitted_imagepath)
        image_filename = get_available_filename('./images/', image_filename)

        # copia il file nella cartella delle immagini
        stored_imagepath = f'./images/{image_filename}'
        shutil.copy(submitted_imagepath, stored_imagepath)
            
        # nuova riga dei report
        new_row = pd.DataFrame([{
            'id_paziente':str(self.patient_dict['id']).rjust(4,'0'),
            'data':submitted_date,
            'descrizione':submitted_description,
            'oct':stored_imagepath,
        }])

        # Salva la riga in modalità append, senza intestazione
        new_row.to_csv('patients_history.csv', mode='a', index=False, header=False)
        
        # avvisa il padre del cambiamento
        self.parent.event_generate('<<AddDialogSuccess>>')
        
        # chiude il dialog
        self.destroy()
    
    def add_image(self):
        imagepath = filedialog.askopenfilename(
            title='Seleziona un immagine',
            filetypes=[
                ('Tutti i file', '*.*'), 
                ('JPG', '*.jpg'),
                ('JPEG', '*.jpeg'),
                ('PNG', '*.png')
            ]
        )
        if not imagepath: return
                
        # ottiene il nome e l'estensione del file
        _, extension = os.path.splitext(imagepath)
        
        # se l'estensione è valida, accetta il file altrimenti mostra un alert
        valid_extensions = ('.png','.jpg','.jpeg')
        if(extension in valid_extensions):
            self.entered_imagepath = imagepath
            self.lbl_image_value['text'] = os.path.basename(self.entered_imagepath)
        else:
            messagebox.showwarning('File non valido!', f'Il File selezionato non è tra i seguenti formati:\n {" ".join(valid_extensions)}')