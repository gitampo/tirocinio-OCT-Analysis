import tkinter as tk
from pathlib import Path
from configs.colors import *
from configs.sizes import *
from classes.ImageCanvas import ImageCanvas

class BscanDialog(tk.Toplevel):

    def __init__(self, parent, caller, image_path, destroy_callback=None):
        super().__init__(parent, bg=CC_dlg_bscan_bg)

        # impostazioni della finestra
        self.geometry(f"{SZ_bscan_dialog_w}x{SZ_bscan_dialog_h}")
        self.minsize(width=SZ_bscan_dialog_min_w, height=SZ_bscan_dialog_min_h)
        self.title(f"Bscan {Path(image_path).name}")
        self.transient(parent)

        # imposta il chiamante
        caller.configure(highlightthickness=1)
        self.caller = caller

        # funzione di callback per la chiusura del dialog
        self.destroy_callback = destroy_callback

        # aggiunge l'immagine del dialog
        bscan_image = ImageCanvas(self, image_path, bg=CC_dlg_bscan_bg)
        bscan_image.pack(fill="both", expand=True)

        # chiusura del dialog
        self.protocol("WM_DELETE_WINDOW", self.destroy_dialog)

    def destroy_dialog(self):
        # chiama la funzione di callback se presente
        if self.destroy_callback: self.destroy_callback()

        # ripristina l'highlight del chiamante e chiude il dialog
        self.caller.configure(highlightthickness=0)
        self.destroy()