import tkinter as tk
from classes.BscanDialog import BscanDialog
from classes.ScrollableFrame import ScrollableFrame
from classes.ImageCanvas import ImageCanvas
from configs.colors import *
from configs.sizes import *
from configs.fonts import *
from configs.paths import *
from configs.tables import *
from utils.funs import *
from PIL import Image
from database.db_manager import get_bscans_of_report
from deeplearning.inference import infer_disease
from tqdm import tqdm

class ReportFrame(ScrollableFrame):

    def __init__(self, parent, report_id):

        # supercostruttore
        super(ReportFrame,self).__init__(parent, bg=CC_frm_report_bg)
        
        # label di caricamento
        lbl_loading = tk.Label(self, text='Caricamento...', bg=CC_frm_report_bg, fg=CC_title_fg, pady=15)
        lbl_loading.pack(side="top", fill="x")
        self.lbl_loading = lbl_loading
        self.has_loaded = False

        # riposiziona canvas e scrollbar (sotto la label di caricamento)
        self.canvas_container.pack_forget()
        self.scrollbar.pack_forget()
        self.canvas_container.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        # ottiene le immagini delle bscans relative al report
        fetched_bscans = get_bscans_of_report(report_id)
        bscans_images = [bscan['immagine'] for bscan in fetched_bscans]

        # lista delle bscan caricate
        self.loaded_bscans = []

        # aggiunge le anteprime delle bscan al frame container
        for bscan_image in tqdm(bscans_images):

            bscan_container = tk.Frame(self.frm_container, bg=CC_frm_report_bg)

            # ottiene il path completo a partire dal nome del file
            bscan_image_path = Path(PT_images_dir)/bscan_image
            
            # istanzia e posiziona l'immagine nel container
            bscan_preview = ImageCanvas(
                bscan_container,
                bscan_image_path, 
                width=SZ_bscan_preview_w, 
                height=SZ_bscan_preview_h, 
                cursor='hand2',
                alt='Immagine bscan non trovata...')

            # label del filename
            lbl_filename = tk.Label(bscan_container, 
                                    text=bscan_image, 
                                    bg=CC_lbl_bscan_label_bg, 
                                    fg=CC_lbl_bscan_label_fg,
                                    padx=10,
                                    pady=10)
            lbl_filename.pack(fill="x")

            # aggiunge l'anteprima al container
            bscan_preview.pack(fill="both", expand=True)

            # label dell'inferenza
            bscan_image = [Image.open(bscan_image_path)]
            inferred_disease, probability = infer_disease(bscan_image)
            lbl_inference = tk.Label(bscan_container, 
                                     text=f"{inferred_disease} con {probability:.2f}% di probabilità", 
                                     bg=CC_lbl_bscan_label_bg, 
                                     fg=CC_lbl_bscan_label_fg,
                                     padx=10,
                                     pady=10)
            lbl_inference.pack(fill="x")

            # associa il click dell'anteprima all'apertura del dialog
            bscan_preview.bind("<Button-1>", self.on_bscan_click)
            self.loaded_bscans.append(bscan_preview)

        # proprietà del canvas
        self.bscans_per_row = None
        self.opened_dialogs = {}

        # evento di ricaricamento
        self.canvas_container.bind("<Configure>", self.update_grid_layout)

    def on_bscan_click(self, event):
        # ottiene il nome del file dell'immagine
        image_path = event.widget.image_path

        # nuovo dialog con immagine bscan
        if image_path not in self.opened_dialogs.keys():
            dialog = BscanDialog(self, event.widget, image_path, lambda: self.opened_dialogs.pop(image_path, None))

            # aggiunge il path dell'immagine alla lista delle bscans aperte
            self.opened_dialogs.update({image_path: dialog})
        else:
            dialog = self.opened_dialogs[image_path]
            dialog.lift()

        return "break"

    def update_grid_layout(self, event=None):

        # calcola il numero di bscan-preview in una riga, in base alla larghezza di canvas e singola preview
        canvas_container_w = self.canvas_container.winfo_width()
        bscan_preview_tot_w = SZ_bscan_preview_w + SZ_bscan_preview_padx * 2
        previews_per_row = max(1, canvas_container_w // bscan_preview_tot_w)

        # ridimensiona il frame contenitore per adattarsi alla larghezza del canvas
        self.canvas_container.itemconfig(self.frm_container_id, width=canvas_container_w)

        # riposiziona le preview se necessario
        self.place_bscan_previews(previews_per_row)

        # aggiorna la scroll region
        self.update_scrollregion()

        # rimuove la label di caricamento
        if not self.has_loaded:
            self.has_loaded = True
            self.lbl_loading.pack_forget()

        return 'break'

    def place_bscan_previews(self, num_of_columns):
        # controlla se il numero di colonne è cambiato
        if self.bscans_per_row == num_of_columns: return

        # aggiorna il layout delle colonne
        self.frm_container.columnconfigure(tuple(i for i in range(num_of_columns)), weight=1)

        # scorre la lista di bscan per posizionarle tutte
        for index, bscan_preview in enumerate(self.frm_container.winfo_children()): 

            # rimuove l'bscan-preview corrente dal layout grid
            bscan_preview.grid_forget()

            # calcola la posizione della preview
            row = index // num_of_columns
            column = index % num_of_columns

            # posiziona l'bscan-preview nel layout grid nella nuova posizione
            bscan_preview.grid(row=row, column=column, padx=SZ_bscan_preview_padx, pady=SZ_bscan_preview_pady)
        
        # aggiorna il numero di colonne salvate nell'istanza
        self.bscans_per_row = num_of_columns 