import tkinter as tk
import tkinter.font as tkFont
from configs.colors import *
from configs.fonts import *
from configs.sizes import *
from configs.paths import *
from utils.funs import * 
from database import db_manager
from datetime import datetime
from tkinter import filedialog, messagebox
from classes.ScrollableFrame import ScrollableFrame

import os
import shutil

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
        self.entered_imagepaths = []

        # imposta il layout (label, text, button...)
        frm_scrollable,  \
        lbl_date_value,  \
        txt_description, \
        lbl_images_values = self.setupLayout()        

        # widget di classe
        self.frm_scrollable = frm_scrollable
        self.lbl_date_value = lbl_date_value
        self.txt_description = txt_description
        self.lbl_images_values = lbl_images_values

    def setupLayout(self):
        
        ### contenitori (frame)
        
        # frame contenitore (principalmente per background)
        frm_scrollable = ScrollableFrame(self, bg=CC_dlg)

        # frame form
        frm_form = frm_scrollable.frm_container
        frm_form.configure(padx=10, pady=10)

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
        lbl_image = self.setupLabel(frm_image, 'Immagini: ')
        
        # dati mostrati (id, nome e cognome del paziente e data di inserimento del report)
        patient_id = str(self.patient_dict['id']).rjust(4,'0')
        patient_name_surname= self.patient_dict['nome'] + " " + self.patient_dict['cognome']
        time_now = datetime.now().strftime('%Y-%m-%d %H:%M')# ottiene il tempo attuale, nel formato corretto
        
        # input dell'utente
        lbl_patient_id_value = self.setupValue(frm_data, f'{patient_id}')
        lbl_patient_name_surname_value = self.setupValue(frm_data, patient_name_surname)
        lbl_date_value = self.setupValue(frm_data, f'{time_now}')
        lbl_images_values = [self.setupValue(frm_image, '. . .')]
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
        frm_scrollable.pack(fill='both', expand=True)
        frm_data.columnconfigure(1, weight=1)
        frm_data.pack(fill='x')
        frm_description.pack(fill='x')
        frm_image.pack(fill='x')

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
        lbl_image.pack(fill='x')
        lbl_images_values[0].pack(fill='x')
        lbl_images_values[0]['anchor'] = 'center'
        frm_image.pack(fill='x')
        
        # pulsante per l'immagine
        btn_image.pack(fill='x')
        
        # pulsante per l'invio dei dati
        btn_submit.pack(fill='x', pady=(30,10))

        return frm_scrollable, lbl_date_value, txt_description, lbl_images_values

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
        submitted_image_paths = self.entered_imagepaths
        
        # controlli sui dati di input
        if not submitted_description:
            messagebox.showwarning('Attenzione!','È necessario inserire una descrizione al Report', parent=self)
            return
        elif len(submitted_image_paths)==0: 
            messagebox.showwarning('Attenzione!','È necessario inserire un\'immagine di un OCT', parent=self)
            return

        # lista dei nomi dei file bscan
        bscans = []

        # per ciascun file controlla se il nome è già preso
        for submitted_image_path in submitted_image_paths:

            # ottiene il nome del file 
            image_filename = os.path.basename(submitted_image_path)
            image_filename = get_available_filename(PT_images_dir, image_filename)

            # aggiunge il nome del file alla lista
            bscans.append(image_filename)

            # copia il file nella cartella delle immagini
            shutil.copy(submitted_image_path, Path(PT_images_dir)/image_filename)

        # aggiunta del nuovo report al database
        db_manager.add_report({
            'paziente':str(self.patient_dict['id']),
            'data':submitted_date,
            'descrizione':submitted_description,
            
        }, bscans)
        
        # avvisa il padre del cambiamento
        self.parent.event_generate('<<AddDialogSuccess>>')
        
        # chiude il dialog
        self.destroy()
    
    def add_image(self):
        imagepaths = filedialog.askopenfilenames(
            parent=self,
            title='Seleziona un immagine',
            filetypes=[
                ('Tutti i file', '*.*'), 
                ('JPG', '*.jpg'),
                ('JPEG', '*.jpeg'),
                ('PNG', '*.png')
            ]
        )
        if not imagepaths: return

        for imagepath in imagepaths:
            # ottiene il nome e l'estensione del file
            _, extension = os.path.splitext(imagepath)
            
            # se l'estensione è valida, accetta il file altrimenti mostra un alert
            valid_extensions = ('.png','.jpg','.jpeg')
            if(extension in valid_extensions):
                self.entered_imagepaths.append(imagepath)
                image_basename = os.path.basename(imagepath)

                # se è il primo file, sostituisce il placeholder
                if len(self.lbl_images_values) == 1 and self.lbl_images_values[0]['text'] == '. . .':
                    self.lbl_images_values[0].destroy()
                    self.lbl_images_values[0] = self.setupValue(self.lbl_images_values[0].master, image_basename)
                    self.lbl_images_values[0].pack(fill='x')
                else:
                    self.lbl_images_values.append(self.setupValue(self.lbl_images_values[0].master, image_basename))
                    self.lbl_images_values[-1].pack(fill='x')
            else:
                messagebox.showwarning('File non valido!', f'Il File selezionato non è tra i seguenti formati:\n {" ".join(valid_extensions)}', parent=self)

        self.frm_scrollable.update_scrollregion()