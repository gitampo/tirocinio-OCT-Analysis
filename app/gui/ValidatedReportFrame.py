import tkinter as tk
from tkinter import ttk, messagebox
from gui.ReportFrame import ReportFrame
from deeplearning.datasets.OCTDL import labels as disease_labels
from configs.colors import *
from database import db_manager

class ValidatedReportFrame(ReportFrame):
    
    def __init__(self, parent, report_id, who_is_logged='doctor'):
        self.who_is_logged = who_is_logged
        super().__init__(parent, report_id)

    def setUpBscanPreview(self, parent, bscan):
        super().setUpBscanPreview(parent, bscan)
        bscan_container = parent.winfo_children()[-1]
        
        # CASO A: Il referto viene riaperto (la predizione è GIA' nel DB)
        if self.who_is_logged == 'doctor' and bscan.get('malattia_predetta') and not bscan.get('validazione_medico'):
            self.add_validation_widgets(bscan_container, bscan)
        elif self.who_is_logged == 'doctor' and bscan.get('malattia_predetta') and bscan.get('validazione_medico'):
            self.add_revalidation_button(bscan_container, bscan)

    def infer_diseases(self):
        # Memorizziamo i contenitori grafici PRIMA che l'inferenza originale svuoti la lista
        pending_scans = [(bscan_id, lbl.master) for bscan_id, lbl in self.lbl_list]
        
        # Facciamo lavorare l'IA originale
        super().infer_diseases()
        
        # CASO B: Prima apertura (le predizioni sono appena state calcolate)
        if self.who_is_logged == 'doctor':
            # Scarichiamo dal DB i dati appena aggiornati dall'IA
            updated_bscans = {b['id']: b for b in db_manager.get_bscans_of_report(self.report_id)}
            
            for bscan_id, container in pending_scans:
                bscan = updated_bscans.get(bscan_id)
                # Se l'IA ha fatto una predizione, mostriamo i bottoni
                if bscan and bscan.get('malattia_predetta') and not bscan.get('validazione_medico'):
                    self.add_validation_widgets(container, bscan)

    def add_validation_widgets(self, container, bscan):
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

    def add_revalidation_button(self, container, bscan):
        frm_revalidate = tk.Frame(container, bg=CC_frm_report_bg)
        frm_revalidate.pack(fill="x", pady=10, padx=10)

        def on_revalidate():
            frm_revalidate.destroy()
            self.add_validation_widgets(container, bscan)

        btn_revalidate = tk.Button(frm_revalidate, text="Modifica validazione", bg=CC_blue_tech, fg=CC_white, relief='flat',
                                   command=on_revalidate)
        btn_revalidate.pack(fill="x")

    def show_correction_ui(self, container, frm_actions, bscan):
        frm_actions.pack_forget()

        frm_correct = tk.Frame(container, bg=CC_frm_report_bg)
        frm_correct.pack(fill="x", pady=10, padx=10)

        lbl_select = tk.Label(frm_correct, text="Seleziona patologia:", bg=CC_frm_report_bg, fg=CC_white)
        lbl_select.pack(anchor="w", padx=5, pady=(5, 0))

        # Crea bottoni per ogni malattia
        frm_diseases = tk.Frame(frm_correct, bg=CC_frm_report_bg)
        frm_diseases.pack(fill="x", padx=5, pady=5)

        for disease in disease_labels:
            btn_disease = tk.Button(frm_diseases, text=disease, bg=CC_blue_tech, fg=CC_white, relief='flat',
                                    command=lambda d=disease: self.submit_validation(bscan['id'], 'Corretto', d, frm_correct))
            btn_disease.pack(side="left", expand=True, fill="x", padx=2, pady=2)

    def submit_validation(self, bscan_id, esito, patologia_finale, current_frame):
        if esito == 'Rifiutato':
            patologia_finale = None

        db_manager.save_validation(bscan_id, esito, patologia_finale)
        
        # Disabilita tutti i widget nel frame di azione per evitare double-click
        for widget in current_frame.winfo_children():
            if isinstance(widget, tk.Button):
                widget.config(state="disabled")
        
        # Aggiungi il messaggio di conferma
        frm_success = tk.Frame(current_frame.master, bg=CC_frm_report_bg)
        frm_success.pack(fill="x", padx=10, pady=5)
        
        if esito == 'Rifiutato':
            lbl_success = tk.Label(frm_success, text="✗ Rifiutato dal medico", 
                                   bg=CC_red, fg=CC_white, font=("Arial", 10, "bold"), pady=5)
        else:
            lbl_success = tk.Label(frm_success, text=f"✓ Validato: {patologia_finale}", 
                                   bg=CC_green, fg=CC_black, font=("Arial", 10, "bold"), pady=5)
        lbl_success.pack(fill="x")