import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from configs.colors import *
from configs.sizes import *
from configs.fonts import *
from configs.tables import *
from util.funs import *
from classes.ImageCanvas import *
from PIL import Image, ImageTk
import pathlib

class ReportFrame(tk.Frame):
    
    def __init__(self, parent, report_image):        
        
        # supercostruttore
        super(ReportFrame,self).__init__()
        
        # mostra l'immagine dell'OCT
        img_canvas = ImageCanvas(self, report_image, alt='Immagine OCT non trovata...')
        img_canvas.pack(fill='both', expand=True)