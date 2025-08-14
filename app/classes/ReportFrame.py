import tkinter as tk
from configs.colors import *
from configs.sizes import *
from configs.fonts import *
from configs.paths import *
from configs.tables import *
from utils.funs import *
from classes.ImageCanvas import *
from database.db_manager import get_bscans_of_report

class ReportFrame(tk.Frame):
    
    def __init__(self, parent, report_id):        
        
        # supercostruttore
        super(ReportFrame,self).__init__(parent, bg=CC_frm_report_bg)
        
        lbl_loading = tk.Label(self, text='Caricamento...', bg=CC_frm_report_bg, fg=CC_title_fg, pady=15)
        lbl_loading.pack(side="top")
        self.lbl_loading = lbl_loading
        self.has_loaded = False

        # ottiene le immagini delle bscans relative al report
        fetched_bscans = get_bscans_of_report(report_id)
        self.bscans_images = [bscan['immagine'] for bscan in fetched_bscans]

        # Canvas contenitore delle immagini
        self.canvas_container = tk.Canvas(self, bg=CC_frm_report_bg, highlightthickness=0)
        self.canvas_container.pack(side="left", fill="both", expand=True)

        # Frame contenitore per le anteprime delle bscan
        self.frm_container = tk.Frame(self.canvas_container, bg=CC_frm_report_bg)
        self.frm_container_id = self.canvas_container.create_window((0, 0), window=self.frm_container, anchor="nw")

        # Aggiunge le anteprime delle bscan al frame container
        for bscan_image in self.bscans_images:
            
            # ottiene il path completo a partire dal nome del file
            bscan_image_path = Path(PT_images_dir)/bscan_image
            
            # istanzia e posiziona l'immagine nel container
            bscan_preview = ImageCanvas(
                self.frm_container,
                bscan_image_path, 
                width=SZ_bscan_preview_w, 
                height=SZ_bscan_preview_h, 
                cursor='hand2',
                alt='Immagine bscan non trovata...')

        # Setup delle proprietà del canvas
        self.num_of_columns = 0
        self.setupScrollbar(self)

        # Bind degli eventi
        self.canvas_container.bind("<Configure>", self.load_bscan_previews)
        self.canvas_container.bind('<Enter>', self._activate_scroll)
        self.canvas_container.bind('<Leave>', self._deactivate_scroll)

    def update_scrollregion(self):
        # ottieni bounding box del contenuto
        bbox = self.canvas_container.bbox("all")
        if bbox is None:
            return

        # ottiene le coordinate della bounding box
        x0, y0, x1, y1 = bbox
        canvas_height = self.canvas_container.winfo_height()
        content_height = y1 - y0
        
        # la scrollregion sarà almeno grande quanto il canvas
        scroll_height = max(canvas_height, content_height)
        self.canvas_container.configure(scrollregion=(0, 0, x1, scroll_height))

    def load_bscan_previews(self, event=None):

        # calcola il numero di bscan-preview in una riga, in base alla larghezza di canvas e singola preview
        canvas_container_w = self.canvas_container.winfo_width()
        bscan_preview_tot_w = SZ_bscan_preview_w + SZ_bscan_preview_padx * 2
        previews_per_row = max(1, canvas_container_w // bscan_preview_tot_w)

        # ridimensiona il frame contenitore per adattarsi alla larghezza del canvas
        self.canvas_container.itemconfig(self.frm_container_id, width=canvas_container_w)

        # riposiziona le preview se necessario
        self.place_bscan_previews(previews_per_row)

        # forza l'aggiornamento del layout prima di aggiornare la scrollregion
        self.frm_container.update_idletasks()  

        # aggiorna la scroll region
        self.update_scrollregion()

        # rimuove il label di caricamento
        if not self.has_loaded:
            self.has_loaded = True
            self.lbl_loading.config(text='')

    def place_bscan_previews(self, num_of_columns):
        # controlla se il numero di colonne è cambiato
        if self.num_of_columns == num_of_columns: return

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
        self.num_of_columns = num_of_columns 

    def _activate_scroll(self, event=None):
        self.bind_all('<MouseWheel>', self.handle_scroll(type='both'))
        self.bind_all('<Button-4>', self.handle_scroll(type='up'))
        self.bind_all('<Button-5>', self.handle_scroll(type='down'))

    def _deactivate_scroll(self, event=None):
        self.unbind_all('<MouseWheel>')
        self.unbind_all('<Button-4>')
        self.unbind_all('<Button-5>')

    def setupScrollbar(self, parent):
        scroll_bar = tk.Scrollbar(parent, orient='vertical', troughcolor=CC_tbl_scroll_trough, bg=CC_tbl_scroll, width=SZ_tbl_scroll_w, command=self.canvas_container.yview)
        scroll_bar.pack(side='right', fill='y')
        self.canvas_container.configure(yscrollcommand=scroll_bar.set)

    def handle_scroll(self, type):
        # controlla il tipo di handler da restituire, in base al tipo richiesto
        # (N.B. in tutti i casi 'break' previene la propagazione dell'evento al Canvas)
        if   type=='both':
            # handle di entrambe le direzioni
            def scroll(event): 
                direction = -1 if event.delta > 0 else 1
                self.canvas_container.yview_scroll(direction, "units")
                return 'break'
            
        elif type=='up':
            # handle della direzione verso l'alto
            def scroll(event): 
                self.canvas_container.yview_scroll(-1, "units")
                return 'break'
        
        elif type=='down':
            # handle della direzione verso il basso
            def scroll(event): 
                self.canvas_container.yview_scroll(1, "units")
                return 'break'

        return scroll