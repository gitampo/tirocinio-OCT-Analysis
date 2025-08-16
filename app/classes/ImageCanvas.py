import tkinter as tk
from configs.colors import *
from configs.sizes import *
from configs.fonts import *
from configs.tables import *
from utils.funs import *
from classes.TableFrame import *
from PIL import Image, ImageTk

class ImageCanvas(tk.Canvas):

    def __init__(self, parent, image_path, width=None, height=None, cursor='', alt='', **kwargs):
        super(ImageCanvas,self).__init__(parent, bg=kwargs.get('bg', CC_canvas_bg), highlightthickness=0)

        # dimensioni del canvas
        if width: self.configure(width=width)
        if height: self.configure(height=height)

        # imposta il tipo di cursore
        self.configure(cursor=cursor)

        # controllo sull'esistenza dell'immagine
        if Path(image_path).exists(): self.image = Image.open(image_path)
        else: self.image = None

        # attributi dell'immagine
        self.image_path = image_path 
        self.alt = alt # testo alternativo

        # gestione del resize
        self.bind('<Configure>', self.resize_image)

    def resize_image(self, event):
        # controllo sulla presenza dell'immagine
        if not self.image: 
            self.drawing_not_found_text()
            return

        # ottiene le dimensioni del canvas e dell'immagine
        canvas_w, canvas_h = (self.winfo_width(), self.winfo_height())
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
        self.delete('all')
        self.create_image(left, top, image=tkPhotoImage, anchor='nw')
        self.tk_image = tkPhotoImage # per evitare la perdita a causa del G.C.
        
    def drawing_not_found_text(self):
        # cancella scritte precedenti
        self.delete('all')
        
        # disegna la scritta al centro del canvas
        canvas_w, canvas_h = (self.winfo_width(), self.winfo_height())
        self.create_text(canvas_w//2, canvas_h//2, 
                                text=self.alt,
                                font=(FT_family, FT_alt_size),
                                fill=CC_canvas_fg)