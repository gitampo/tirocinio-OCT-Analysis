import tkinter as tk
from tkinter import ttk
from configs.colors import *
from configs.sizes import *
from configs.fonts import *
from configs.anchors import *
from util.funs import *
from classes.TableFrame import *
from PIL import Image, ImageTk

class ReportFrame(tk.Frame):
    
    def __init__(self, parent, report_image):        
        
        # supercostruttore
        super(ReportFrame,self).__init__()
        
        # dati da condividere con il parent (inizialmente non ci sono dati)
        self.shared_data = None
        
        # immagine dell'oct
        image = Image.open(report_image) 
        image = image.resize((SZ_window_w, SZ_window_h-SZ_topbar_h))
        photo = ImageTk.PhotoImage(image)

        # istanzia il Canvas dove risiederà l'immagine
        canvas = tk.Canvas(self, width=image.width, height=image.height)
        canvas.grid(row=0, column=0, sticky='nswe')
        
        
        # aggiunge l'immagine al Canvas
        canvas.create_image(0, 0, image=photo, anchor='nw')
        canvas.image = photo # per evitare la perdita a causa del G.C.
        
        # configurazione delle colonne
        self.columnconfigure(1, weight=1)
        
        # configurazione delle righe
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=10)

    def alert_parent(self, event):
        # se l'utente preme sull'heading, non deve fare niente
        region = self.tbl.identify_region(event.x, event.y)
        if region == "heading": return "break"

        # ottiene l'item della riga premuta
        item_iid = self.tbl.identify_row(event.y)
        item = self.tbl.item(item_iid)

        # dizionario del paziente composto da chiavi e valori (chiavi=headings, valori=valori dell'item)
        patient_dict = dict(zip(self.tbl['columns'], item['values']))
    
        # dati condivisi con il parent
        self.shared_data = patient_dict
    
        # genera un evento visibile dal padre e gli passa i dati del paziente cliccato
        self.event_generate('<<PatientRowClicked>>')