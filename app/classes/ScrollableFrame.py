import tkinter as tk
from configs.colors import *
from configs.sizes import *

class ScrollableFrame(tk.Frame):

    def __init__(self, parent, bg):
        super(ScrollableFrame, self).__init__(parent, bg=bg)

        # crea un canvas e una scrollbar
        self.canvas_container = tk.Canvas(self, bg=bg, highlightthickness=0)
        self.scrollbar = tk.Scrollbar(self, orient="vertical", troughcolor=CC_tbl_scroll_trough, bg=CC_tbl_scroll, width=SZ_tbl_scroll_w, command=self.canvas_container.yview)
        self.frm_container = tk.Frame(self.canvas_container, bg=bg)

        # posiziona il frame interno, dentro al canvas
        self.frm_container_id = self.canvas_container.create_window((0, 0), window=self.frm_container, anchor="nw")

        # configura la scrollbar
        self.canvas_container.configure(yscrollcommand=self.scrollbar.set)

        # posiziona il canvas e la scrollbar
        self.canvas_container.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        # configura il canvas
        self.canvas_container.bind("<Configure>", self.on_configure)
        self.canvas_container.bind("<Enter>", self._activate_scroll)
        self.canvas_container.bind("<Leave>", self._deactivate_scroll)

    def on_configure(self, event):

        # aggiorna le dimensioni del frame contenitore
        self.frm_container.update_idletasks()
        self.canvas_container.itemconfig(self.frm_container_id, width=self.canvas_container.winfo_width())

        # aggiorna la regione di scorrimento del canvas
        self.update_scrollregion()

    def _activate_scroll(self, event=None):
        self.canvas_container.bind_all('<MouseWheel>', self.handle_scroll(type='both'))
        self.canvas_container.bind_all('<Button-4>', self.handle_scroll(type='up'))
        self.canvas_container.bind_all('<Button-5>', self.handle_scroll(type='down'))

    def _deactivate_scroll(self, event=None):
        self.canvas_container.unbind_all('<MouseWheel>')
        self.canvas_container.unbind_all('<Button-4>')
        self.canvas_container.unbind_all('<Button-5>')

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
    
    def update_scrollregion(self):

        # aggiorna le dimensioni del frame contenitore
        self.frm_container.update_idletasks()

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