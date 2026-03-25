import tkinter as tk
from tkinter import ttk, messagebox
from gui.ReportFrame import ReportFrame
from deeplearning.datasets.OCTDL import labels as disease_labels
from configs.colors import *
from database import db_manager

class ValidatedReportFrame(ReportFrame):
    
    def __init__(self, parent, report_id, who_is_logged='doctor'):
        self.who_is_logged = who_is_logged
        # Chiama il costruttore della classe originale (che caricherà anche le B-scan)
        super().__init__(parent, report_id)

    def setUpBscanPreview(self, parent, bscan):
        # 1. Fa eseguire tutto il lavoro di disegno grafico alla classe originale
        super().setUpBscanPreview(parent, bscan)
        
        # 2. Recupera il container della b-scan appena creato (è l'ultimo figlio aggiunto al parent)
        bscan_container = parent.winfo_children()[-1]
        
        # 3. Aggiunge i tasti di validazione SOLO se l'utente è un medico e se c'è una predizione
        if self.who_is_logged == 'doctor' and bscan['malattia_predetta']:
            self.add_validation_widgets(bscan_container, bscan)

    def add_validation_widgets(self, container, bscan):
        # Frame orizzontale per contenere i pulsanti
        frm_actions = tk.Frame(container, bg=CC_frm_report_bg)
        frm_actions.pack(fill="x", pady=10, padx=10)

        # Pulsante "Approva"
        btn_approve = tk.Button(frm_actions, text="✓ Approva", bg=CC_green, fg=CC_black, relief='flat',
                                command=lambda: self.submit_validation(bscan['id'], 'Approvato', bscan['malattia_predetta'], frm_actions))
        btn_approve.pack(side="left", expand=True, fill="x", padx=5)

        # Pulsante "Rifiuta"
        btn_reject = tk.Button(frm_actions, text="✗ Rifiuta", bg=CC_red, fg=CC_white, relief='flat',
                               command=lambda: self.submit_validation(bscan['id'], 'Rifiutato', None, frm_actions))
        btn_reject.pack(side="left", expand=True, fill="x", padx=5)

        # Pulsante "Correggi"
        btn_correct = tk.Button(frm_actions, text="✎ Correggi", bg=CC_light_cobalt, fg=CC_black, relief='flat',
                                command=lambda: self.show_correction_ui(container, frm_actions, bscan))
        btn_correct.pack(side="right", expand=True, fill="x", padx=5)

    def show_correction_ui(self, container, frm_actions, bscan):
        # Nasconde i pulsanti originali
        frm_actions.pack_forget()

        # Crea un nuovo frame per il menù a tendina
        frm_correct = tk.Frame(container, bg=CC_frm_report_bg)
        frm_correct.pack(fill="x", pady=10, padx=10)

        # Menù a tendina (Combobox) con le malattie disponibili in OCTDL
        cb_disease = ttk.Combobox(frm_correct, values=disease_labels, state="readonly")
        cb_disease.set("Seleziona patologia...")
        cb_disease.pack(side="left", expand=True, fill="x", padx=5)

        # Pulsante per confermare la correzione
        btn_confirm = tk.Button(frm_correct, text="Conferma", bg=CC_blue_tech, fg=CC_white, relief='flat',
                                command=lambda: self.submit_validation(bscan['id'], 'Corretto', cb_disease.get(), frm_correct))
        btn_confirm.pack(side="right", padx=5)

    def submit_validation(self, bscan_id, esito, patologia_finale, current_frame):
        # Controllo di validità se il medico sta correggendo
        if esito == 'Corretto' and patologia_finale == "Seleziona patologia...":
            messagebox.showwarning("Attenzione", "Seleziona una patologia valida dal menù.")
            return

        # Per rifiuto, la patologia validata è None
        if esito == 'Rifiutato':
            patologia_finale = None

        # Salva la validazione nel database
        db_manager.save_validation(bscan_id, esito, patologia_finale)
        
        # Aggiorna la grafica (sostituisce i pulsanti con un'etichetta di successo)
        current_frame.pack_forget()
        if esito == 'Rifiutato':
            lbl_success = tk.Label(current_frame.master, text="Rifiutato dal medico", 
                                   bg=CC_red, fg=CC_white, font=("Arial", 10, "bold"), pady=5)
        else:
            lbl_success = tk.Label(current_frame.master, text=f"Validato: {patologia_finale}", 
                                   bg=CC_green, fg=CC_black, font=("Arial", 10, "bold"), pady=5)
        lbl_success.pack(fill="x", padx=10, pady=10)