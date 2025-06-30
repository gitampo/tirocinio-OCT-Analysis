import tkinter as tk
from tkinter import ttk
from configs.colors import *
from configs.sizes import *
from configs.fonts import *
from configs.tables import *
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

        self.canvas = self.setupCanvas(photo)
        
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        
    def setupCanvas(self, image=None):
        # istanzia il Canvas dove risiederà l'immagine
        canvas = tk.Canvas(self, bg=CC_canvas_bg)
        canvas.grid(row=0, column=0, sticky='nswe')
        
        
        # aggiunge l'immagine al Canvas
        canvas.create_image(0, 0, image=image, anchor='nw')
        canvas.image = image # per evitare la perdita a causa del G.C.