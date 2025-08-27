import re
from pathlib import Path
import tkinter as tk
from configs.colors import CC_loading_bg, CC_loading_fg 

def remove_tag(tag, tag_tuple):
    new_tag_tuple = tag_tuple
    
    # se il secondo parametro è una stringa, lo tratta come una tupla
    if isinstance(tag_tuple, str) and tag==tag_tuple:
        return ()
    elif isinstance(tag_tuple, str):
        return (tag_tuple,)
    
    # controlla che il secondo parametro sia una tupla
    if not isinstance(tag_tuple,tuple):
        raise TypeError(f'expected a tuple as second parameter, but "{type(tag_tuple)}" was found')
    
    # se la tupla ha il tag, lo rimuove
    if tag in tag_tuple: 
        tag_list = list(tag_tuple)
        tag_list.remove(tag)
        new_tag_tuple = tuple(tag_list)
        
    return new_tag_tuple

def append_tag(tag, tag_tuple):
    # se il secondo parametro è una stringa, lo tratta come una tupla
    if isinstance(tag_tuple, str):
        return (tag_tuple, tag)
    
    # controlla che il secondo parametro sia una tupla
    if not isinstance(tag_tuple,tuple):
        raise TypeError(f'expected a tuple as second parameter, but "{type(tag_tuple)}" was found')
    
    # aggiunge il tag alla tupla
    tag_list = list(tag_tuple)
    tag_list.append(tag)
    new_tag_tuple = tuple(tag_list)
    
    return new_tag_tuple

def push_tag(tag, tag_tuple):
    # se il secondo parametro è una stringa, lo tratta come una tupla
    if isinstance(tag_tuple, str):
        return (tag_tuple, tag)
    
    # controlla che il secondo parametro sia una tupla
    if not isinstance(tag_tuple,tuple):
        raise TypeError(f'expected a tuple as second parameter, but "{type(tag_tuple)}" was found')
    
    # aggiunge il tag alla tupla
    tag_list = list(tag_tuple)
    tag_list.insert(0,tag)
    new_tag_tuple = tuple(tag_list)
    
    return new_tag_tuple

def has_tag(tag_tuple, tag):   
    # controlla se il primo parametro è una stringa
    if isinstance(tag_tuple, str):
        return tag==tag_tuple
    
    # controlla che il primo parametro sia una tupla
    if not isinstance(tag_tuple,tuple):
        raise TypeError(f'expected a tuple as first parameter, but "{type(tag_tuple)}" was found')
        
    # controlla se è presente il tag
    return tag in tag_tuple

def is_even(n):
    return int(n)%2==0

def is_number(n):
    try:
        float(n)
        int(n)    
    except ValueError:
        return False
    
    return True

def centered_position(container_size, contained_size):
    container_w, container_h = container_size
    contained_w, contained_h = contained_size
    
    # calcolo della posizione del contenuto
    left = (container_w-contained_w)//2
    top  = (container_h-contained_h)//2
    
    return left, top

def remove_headings(unwanted_headings, headings, rows):
        unwanted_idexes = [headings.index(h) for h in headings if h in unwanted_headings]
        
        new_headings = tuple(h for h in headings if h not in unwanted_headings)
        new_rows = [tuple(value for i, value in enumerate(row) if i not in unwanted_idexes) for row in rows]
        
        return new_headings, new_rows
    
def hasfunc(item, func):
    return hasattr(item, func) and callable(eval(f'item.{func}'))

def get_available_filename(directory, filename):
    
    # inizializzazione
    available_filename = filename
    counter = 1
    path = Path(directory)/filename
    
    # ciclo per ricerca di un nome disponibile
    while path.exists():
        # ottiene il nome del file pulito, senza contatore
        cleaned_stem = re.sub(r'\(\d+\)$', '', path.stem)
        
        # se il nome è già preso, aggiunge il counter e cambia il nome
        available_filename = f'{cleaned_stem}({counter}){path.suffix}'
        path = path.with_name(available_filename) # rinomina il file
        counter += 1 # se serve un'altra iterazione
        
    return available_filename

def centered_toplevel(parent, size=(250, 150)):
    # istanzia una finestra di dialogo
    tl = tk.Toplevel(parent)

    # ottiene la finestra master
    master = parent.winfo_toplevel()
    master_x, master_y = master.winfo_x(), master.winfo_y()

    # calcola la posizione centrata
    x, y = centered_position((master.winfo_width(), master.winfo_height()), size)

    # posizione della finestra di dialogo come figlia della finestra master
    tl.geometry(f"{size[0]}x{size[1]}+{x+master_x}+{y+master_y}")
    tl.transient(master)

    return tl

def create_loading_dialog(parent, size=(350, 150)):

    # crea una finestra di dialogo per il caricamento
    tl = centered_toplevel(parent, size)
    tl.title("Caricamento...")
    tl.resizable(False, False)
    tl.protocol("WM_DELETE_WINDOW", lambda: None)

    # inserisce una label nella finestra di caricamento
    lbl_loading = tk.Label(tl, text="Attendere...", bg=CC_loading_bg, fg=CC_loading_fg)
    lbl_loading.pack(fill="both", expand=True)

    tl.update_idletasks()

    return tl