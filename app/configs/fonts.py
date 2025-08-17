### Modulo per la configurazione del font (FT = Font)
import tkinter as tk
import tkinter.font as tkFont

def get_fallback_font(fallback_list):
    w = tk.Tk(); w.withdraw()
    font_name = next((f for f in fallback_list if f in tkFont.families()), '')
    w.destroy()

    return font_name

FT_family = get_fallback_font(['Arial','courier'])
FT_size = 12
FT_appname_size = 30
FT_h1_size = 24
FT_h2_size = 20
FT_h3_size = 16
FT_alt_size = 15
FT_logout_size = 10