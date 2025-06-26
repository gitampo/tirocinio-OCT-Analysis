import tkinter as tk
from tkinter import ttk
from configs.colors import *
from configs.sizes import *
from configs.fonts import *
from util.funs import *

class PatientsListFrame(tk.Frame):
    
    def __init__(self, parent, table_headings, table_rows):
        super(PatientsListFrame,self).__init__(bg=CC_frm_default)
        
        # stile della Treeview
        style = ttk.Style()
        style.theme_use('clam')
        style.layout('PLTreeview', style.layout('Treeview'))
        style.configure('PLTreeview', rowwidth=0, rowheight=SZ_tbl_pat_list_row_h, relief='solid', borderwidth=1)
        style.map('PLTreeview',
            background=[('active', CC_tbl_highlight), ('selected', CC_tbl_selected)],
            foreground=[('active', CC_tbl_text_highlight), ('selected', CC_tbl_text_selected), ('!selected', CC_tbl_text)]
        )
        
        # attributi di classe
        self.setupTitle(f'Lista dei pazienti')
        self.tbl_patients = self.setupTreeview(table_headings, table_rows, 'PLTreeview')
        self.scroll_bar = self.setupScrollbar()
        self.parent = parent
        self.last_iid = None
        
        # configurazione delle colonne
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=10)
        self.columnconfigure(2, weight=1)
        
        # configurazione delle righe
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=10)
        self.rowconfigure(2, weight=1)

    def setupTreeview(self, table_headings, table_rows, style):
        # tabella dei pazienti
        tbl_patients = ttk.Treeview(self, columns=table_headings, show='headings', style=style)
        
        # stile righe pari e righe dispari
        tbl_patients.tag_configure('evenrow', background=CC_tbl_evenrow) 
        tbl_patients.tag_configure('oddrow', background=CC_tbl_oddrow)
        
        for heading in table_headings:
            tbl_patients.heading(heading, text=heading.upper(), anchor='center')            
            tbl_patients.column(heading, anchor='center')
        
        # configurazione e posizionamento della treeview
        tbl_patients.tag_configure("highlight", background=CC_tbl_highlight)
        tbl_patients.grid(row=1, column=1, sticky='nswe')
        
        # eventi della treeview
        tbl_patients.bind("<Motion>", self.handle_highlight)
        tbl_patients.bind("<MouseWheel>", self.handle_highlight)
        tbl_patients.bind("<Leave>", self.on_leave)
        tbl_patients.bind("<Button-1>", self.open_patient_frame)
        tbl_patients.bind("<<TreeviewSelect>>", self.stop_selection)
        
        # riempimento della tabella
        for i,row in enumerate(table_rows):
            tbl_patients.insert(parent='', index=tk.END, iid=i, values=row)
            
            # assegna lo stile il tag in base alla posizione nella tabella
            if is_even(i): tbl_patients.item(i, tags=('evenrow'))
            else: tbl_patients.item(i, tags=('oddrow'))
            
        return tbl_patients
    
    def setupTitle(self, text):
        lbl_title = tk.Label(self, text=text, font=(FT_family, FT_h1_size), bg=CC_frm_default)
        lbl_title.grid(row=0, column=1)
        return lbl_title

    def setupScrollbar(self):
        scroll_bar = tk.Scrollbar(self, orient='vertical', command=self.tbl_patients.yview)
        scroll_bar.grid(row=1, column=2, sticky='ns')
        self.tbl_patients.configure(yscrollcommand=scroll_bar.set)
        self.tbl_patients.bind('<MouseWheel>', self.handle_scroll(type='both'))
        self.tbl_patients.bind('<Button-4>', self.handle_scroll(type='up'))
        self.tbl_patients.bind('<Button-5>', self.handle_scroll(type='down'))
        
        return scroll_bar

    def open_patient_frame(self, event):
        
        # ottiene l'id del paziente 
        item_iid = self.tbl_patients.identify_row(event.y)
        item = self.tbl_patients.item(item_iid)

        # dizionario del paziente composto da chiavi e valori (chiavi=headings, valori=valori dell'item)
        patient_dict = dict(zip(self.tbl_patients['columns'], item['values']))
    
        # passa l'esecuzione al parent, che gestirà l'apertura del frame del paziente
        self.parent.open_patient_history(patient_dict)

    def handle_scroll(self, type):
        # controlla il tipo di handler da restituire, in base al tipo richiesto
        # (N.B. in tutti i casi 'break' previene la propagazione dell'evento alla Treeview)
        if   type=='both':
            # handle di entrambe le direzioni
            def scroll(event): 
                direction = -1 if event.delta > 0 else 1
                self.tbl_patients.yview_scroll(direction, "units")
                return 'break'
            
        elif type=='up':
            # handle della direzione verso l'alto
            def scroll(event): 
                self.tbl_patients.yview_scroll(-1, "units")
                return 'break'
        
        elif type=='down':
            # handle della direzione verso il basso
            def scroll(event): 
                self.tbl_patients.yview_scroll(1, "units")
                return 'break'

        return scroll

    def handle_highlight(self,event,*args):
        # imposta il cursore
        self.configure(cursor="hand2")
        
        # ultimo e nuovo iid (treeview item-id)
        last_iid = self.last_iid
        new_iid = self.tbl_patients.identify_row(event.y)
            
        # gestisce l'highlight dell'item
        if last_iid != new_iid:
            self.set_highlight(new_iid)
                
            # rimuove l'highlight al precedente item se non è None
            if last_iid is not None:
                self.clear_highlight(last_iid)

        # aggiorna l'ultimo iid al valore del nuovo
        self.last_iid = new_iid

    def on_leave(self,event,*args):
        # reset del cursore
        self.configure(cursor="arrow")
        
        # rimuove l'highlight all'item che lo aveva
        if self.last_iid is not None:
            self.clear_highlight(self.last_iid)
            self.last_iid = None
            
    def set_highlight(self, iid):
        tags = self.tbl_patients.item(iid, 'tags')
        
        # termina se l'iid non è un numero
        if not is_number(iid): return
        
        # toglie lo stile della riga
        if is_even(int(iid)): tags = remove_tag('evenrow', tags)
        else: tags = remove_tag('oddrow', tags)
        
        # aggiunge l'highlight
        self.tbl_patients.item(iid, tags=append_tag('highlight', tags))
        
    def clear_highlight(self, iid):
        tags = self.tbl_patients.item(iid, 'tags')
        
        # termina se l'iid non è un numero
        if not is_number(iid): return
        
        # riassegna lo stile della riga
        if is_even(int(iid)): tags = append_tag('evenrow', tags)
        else: tags = append_tag('oddrow', tags)
        
        # toglie l'highlight
        self.tbl_patients.item(iid, tags=remove_tag('highlight', tags))
        
    def stop_selection(self, event):
        for selection in self.tbl_patients.selection():
            self.tbl_patients.selection_remove(selection)