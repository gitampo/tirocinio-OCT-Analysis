from operator import index
import tkinter as tk
from database import db_manager
from gui.BscanDialog import BscanDialog
from gui.ScrollableFrame import ScrollableFrame
from gui.ImageCanvas import ImageCanvas
from configs.colors import *
from configs.sizes import *
from configs.fonts import *
from configs.paths import *
from configs.tables import *
from utils.funs import *
from PIL import Image
from database.db_manager import get_bscans_of_report
from deeplearning.inference import infer_disease
from functools import partial

class ReportFrame(ScrollableFrame):

    def __init__(self, parent, report_id):

        # supercostruttore
        super(ReportFrame,self).__init__(parent, bg=CC_frm_report_bg)

        # crea la finestra di caricamento (sarà chiusa al termine del caricamento)
        tl = create_loading_dialog(self)
        tl.bind_all("<<LoadingCompleted>>", lambda e: tl.destroy())

        # flag per indicare se il caricamento è in corso
        self.is_loading = True

        # liste di input e label (da usare per l'inferenza)
        self.inputs = []
        self.lbl_list = []
        self.preview_refs = {}  # mappa bscan_id al suo preview frame

        # proprietà del canvas
        self.report_id = report_id
        self.bscans_per_row = None # calcolato successivamente
        self.opened_dialogs = {} # dialog delle bscans, aperti

        # gestione dell'evento di ridimensionamento
        self.canvas_container.bind("<Configure>", self.update_grid_layout)

    def setUpBscanPreview(self, parent, bscan):
            # immagine bscan (ora sappiamo che esiste)
            bscan_image_path = Path(PT_images_dir)/bscan['immagine']
            
            # container per la bscan
            bscan_container = tk.Frame(
                parent, 
                bg=CC_frm_report_bg,
                width=SZ_bscan_preview_w,
                height=SZ_bscan_preview_h
            )

            # label del filename
            lbl_filename = tk.Label(bscan_container, 
                text=bscan['immagine'], 
                bg=CC_lbl_bscan_label_bg, 
                fg=CC_lbl_bscan_label_fg,
                padx=10,
                pady=10)
            lbl_filename.pack(fill="x")

            # separatore
            tk.Frame(bscan_container, height=3, bg=CC_bscan_separator).pack(fill="x")

            bscan_preview = ImageCanvas(
                bscan_container,
                bscan_image_path,
                cursor='hand2',
                alt='Immagine bscan non trovata...')
            bscan_preview.pack(fill="both", expand=True)

            # separatore
            tk.Frame(bscan_container, height=3, bg=CC_bscan_separator).pack(fill="x")

            # label di previsione della malattia
            lbl_inference = tk.Label(bscan_container, 
                bg=CC_lbl_bscan_label_bg, 
                fg=CC_lbl_bscan_label_fg,
                padx=10,
                pady=10)
            lbl_inference.pack(fill="x")

            # carica le previsioni se presenti
            prob = bscan.get('probabilità_predizione') or bscan.get('probabilit�\xa0_predizione')
            if bscan['malattia_predetta'] is not None and prob is not None:
                pred = bscan['malattia_predetta']
                text = f"{pred} con {prob:.2f}% di probabilità"
                
                # aggiungi informazioni di validazione se presenti
                if bscan.get('validazione_medico'):
                    validazione = bscan['validazione_medico']
                    validata = bscan.get('malattia_validata')
                    if validazione == 'Approvato':
                        text += f"\n✓ Approvato dal medico"
                    elif validazione == 'Corretto':
                        text += f"\n✎ Corretto dal medico: {validata}"
                    elif validazione == 'Rifiutato':
                        text += f"\n✗ Rifiutato dal medico"
                
                lbl_inference.config(text=text)
            # altrimenti aggiungi all'elenco di input da usare per l'inferenza
            else:
                self.inputs += [Image.open(bscan_image_path)]
                self.lbl_list += [(bscan['id'], lbl_inference)]
                self.preview_refs[bscan['id']] = (bscan_preview, False)

            # associa il click dell'anteprima all'apertura del dialog
            bscan_preview.bind("<Button-1>", self.on_bscan_click)

    def load_bscans(self):
        # ottiene le immagini delle bscans relative al report
        bscans = get_bscans_of_report(self.report_id)

        # aggiunge le anteprime delle bscan al frame container solo per quelle con immagini esistenti
        for i, bscan in enumerate(bscans):
            bscan_image_path = Path(PT_images_dir)/bscan['immagine']
            if bscan_image_path.exists():
                self.setUpBscanPreview(self.frm_container, bscan)

        # esegue l'inferenza delle immagini che lo richiedono
        self.infer_diseases()

    def on_bscan_click(self, event):
        # ottiene il nome del file dell'immagine
        image_path = event.widget.image_path

        widget_id = event.widget.winfo_id()
        event.widget.master.configure(highlightthickness=1, highlightbackground=CC_dlg_bscan_highlight)

        # elimina eventuali dialog orfani
        if widget_id in self.opened_dialogs:
            dialog = self.opened_dialogs.get(widget_id)
            if not dialog.winfo_exists():
                self.opened_dialogs.pop(widget_id, None)

        # nuovo dialog con immagine bscan
        if widget_id not in self.opened_dialogs:
            dialog = BscanDialog(self, event.widget.master, image_path, lambda: self.opened_dialogs.pop(widget_id, None))
            self.opened_dialogs[widget_id] = dialog
        else:
            dialog = self.opened_dialogs.get(widget_id)
            if dialog: dialog.lift()

        return "break"

    def close_toplevels(self):
        for dialog in list(self.opened_dialogs.values()):
            try:
                if dialog.winfo_exists():
                    dialog.destroy()
            except tk.TclError:
                pass
        self.opened_dialogs.clear()

    def update_grid_layout(self, event=None):

        # carica le bscan se necessario
        if self.is_loading:
            self.load_bscans()

        # calcola il numero di bscan-preview in una riga, in base alla larghezza di canvas e singola preview
        canvas_container_w = self.canvas_container.winfo_width()
        bscan_preview_tot_w = SZ_bscan_preview_w + SZ_bscan_preview_padx * 2
        previews_per_row = max(1, canvas_container_w // bscan_preview_tot_w)
        
        # ridimensiona il frame contenitore per adattarsi alla larghezza del canvas
        self.canvas_container.itemconfig(self.frm_container_id, width=canvas_container_w)

        # riposiziona le preview se necessario
        self.place_bscan_previews(previews_per_row)
        self.update_scrollregion()

        # segnala il completamento del caricamento
        if self.is_loading:
            self.is_loading = False
            self.after(500, self.event_generate, "<<LoadingCompleted>>")

        return 'break'

    def infer_diseases(self):
        # verifica se ci sono immagini da elaborare
        if not self.inputs: return

        # esegue l'inferenza delle immagini senza predizione
        preds, probs = infer_disease(self.inputs)

        # se non ci sono risultati (checkpoint non disponibile), mostra messaggio
        if not preds or not probs:
            for bscan_id, lbl_inference in self.lbl_list:
                lbl_inference.config(text="Modello non disponibile - inferenza non possibile")
        else:
            # ciclo per aggiungere le previsioni al database e alla visualizzazione
            for (pred, prob, (bscan_id, lbl_inference)) in zip(preds, probs, self.lbl_list):
                prob = prob.item()

                # salva la previsione nel database e aggiorna la label corrispondente
                db_manager.set_prediction_for_bscan(bscan_id, pred, prob)
                lbl_inference.config(text=f"{pred} con {prob:.2f}% di probabilità")
                
                # nasconde il placeholder ora che esiste una predizione
                preview_ref = self.preview_refs.get(bscan_id)
                if preview_ref and preview_ref[1]:
                    preview_ref[0].pack_forget()

        # pulisce gli input
        self.inputs.clear()

    def place_bscan_previews(self, num_of_columns):
        # controlla se il numero di colonne è cambiato
        if self.bscans_per_row == num_of_columns: return

        # aggiorna il layout delle colonne
        self.frm_container.columnconfigure(tuple(i for i in range(num_of_columns)), weight=1)

        # scorre la lista di bscan per posizionarle tutte
        for i, bscan_preview in enumerate(self.frm_container.winfo_children()): 
            
            # rimuove la bscan-preview corrente dal layout grid
            bscan_preview.grid_forget()

            # calcola la posizione della preview
            row = i // num_of_columns
            column = i % num_of_columns

            # posiziona la bscan-preview nel layout grid nella nuova posizione
            bscan_preview.grid(row=row, column=column, sticky='nswe', padx=SZ_bscan_preview_padx, pady=SZ_bscan_preview_pady)

        # aggiorna il numero di colonne salvate nell'istanza
        self.bscans_per_row = num_of_columns 