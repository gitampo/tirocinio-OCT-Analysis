import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from configs.colors import *
from configs.sizes import *
from configs.fonts import *
from configs.tables import *
from util.funs import *
from classes.TableFrame import *
from PIL import Image, ImageTk
import pathlib

class ReportFrame(tk.Frame):
    
    def __init__(self, parent, report_image):        
        
        # supercostruttore
        super(ReportFrame,self).__init__()
        
        # dati da condividere con il parent (inizialmente non ci sono dati)
        self.shared_data = None

        # controllo sull'immagine dell'oct
        self.image = None        
        if Path(report_image).exists():
            # immagine dell'oct
            self.image = Image.open(report_image)

        self.canvas = self.setupCanvas()
        
        # gestione del resize
        self.canvas.bind('<Configure>', self.resize_image)
    
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        
    def setupCanvas(self, image=None):
       
        # istanzia il Canvas dove risiederà l'immagine
        canvas = tk.Canvas(self, bg=CC_canvas_bg)
        canvas.grid(row=0, column=0, sticky='nswe')
        
        return canvas
    
    def resize_image(self, event):
        # controllo sulla presenza dell'immagine
        if not self.image: 
            self.draw_not_found_text()
            return
        
        # ottiene le dimensioni del canvas e dell'immagine
        canvas_w, canvas_h = (self.canvas.winfo_width(), self.canvas.winfo_height())
        image_w, image_h = self.image.width, self.image.height

        # calcola le nuove dimensioni dell'immagine
        scale = min(canvas_w / image_w, canvas_h / image_h)
        new_image_size = (int(image_w * scale), int(image_h * scale))

        # resize dell'immagine
        resized_image = self.image.resize(new_image_size)
        tkPhotoImage = ImageTk.PhotoImage(resized_image)        
        
        # calcola la posizione centrata dell'immagine
        left, top = centered_position((canvas_w, canvas_h), new_image_size)
        
        # aggiunge l'immagine al Canvas, rimuovendo l'immagine precedente
        self.canvas.delete('all')
        self.canvas.create_image(left, top, image=tkPhotoImage, anchor='nw')
        self.canvas.image = tkPhotoImage # per evitare la perdita a causa del G.C.
        
    def draw_not_found_text(self):
        # cancella scritte precedenti
        self.canvas.delete('all')
        
        # disegna la scritta al centro del canvas
        canvas_w, canvas_h = (self.canvas.winfo_width(), self.canvas.winfo_height())
        self.canvas.create_text(canvas_w//2, canvas_h//2, 
                                text='Immagine OCT non trovata...',
                                font=(FT_family, FT_h3_size, ''),
                                fill=CC_canvas_fg)