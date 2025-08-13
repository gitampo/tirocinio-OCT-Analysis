import tkinter as tk
from configs.colors import *
from configs.sizes import *
from configs.fonts import *
from configs.tables import *
from utils.funs import *
from classes.ImageCanvas import *

class ReportFrame(tk.Frame):
    
    def __init__(self, parent, report_image):        
        
        # supercostruttore
        super(ReportFrame,self).__init__()
        
        # mostra l'immagine dell'OCT
        img_canvas = ImageCanvas(self, report_image, alt='Immagine OCT non trovata...')
        img_canvas.pack(fill='both', expand=True)