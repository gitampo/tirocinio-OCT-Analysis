import tkinter as tk
from tkinter import ttk
from configs.colors import *
from configs.sizes import *
from configs.fonts import *
from util.funs import *
from functools import reduce

class TableFrame(tk.Frame):
    
    def __init__(self, parent, table_headings, table_rows, title, stylename):
        super(TableFrame,self).__init__(bg=CC_frm_default)
        
        # attributi di classe
        self.frm_container = self.setupContainer(self)
        self.lbl_title = self.setupTitle(self, title)
        self.tbl = self.setupTreeview(self.frm_container, table_headings, table_rows, stylename)
        self.scroll_bar = self.setupScrollbar(self.frm_container)
        self.parent = parent
        self.last_iid = None
        self.title = title

    def setupContainer(self, parent):
        # contenitore di tabella e scrollbar
        frm_container = tk.Frame(self)
        frm_container.grid(row=1, column=1, sticky='nswe')
        return frm_container

    def setupTreeview(self, parent, table_headings, table_rows, stylename):
        # tabella dei pazienti
        tbl = ttk.Treeview(parent, columns=table_headings, show='headings', style=stylename)
        tbl.pack(side='left', fill='both', expand=True)
        
        # stile righe pari e righe dispari
        tbl.tag_configure('evenrow', background=CC_tbl_evenrow) 
        tbl.tag_configure('oddrow', background=CC_tbl_oddrow)
        
        # configurazione del tag per l'highlight
        tbl.tag_configure("highlight", background=CC_tbl_highlight, foreground=CC_tbl_text_highlight)
        
        # eventi della treeview
        tbl.bind("<Motion>", self.handle_highlight)
        tbl.bind("<MouseWheel>", self.handle_highlight)
        tbl.bind("<Leave>", self.on_leave)
        tbl.bind("<Configure>", self.resize_columns)
        tbl.bind("<<TreeviewSelect>>", self.stop_selection)
        
        # caricamento delle intestazioni
        for heading in table_headings:
            tbl.heading(heading, text=heading.upper(), anchor='center')            
            tbl.column(heading, stretch=True, anchor='center')
        
        # riempimento della tabella
        for i,row in enumerate(table_rows):
            tbl.insert(parent='', index=tk.END, iid=i, values=row)
            
            # assegna lo stile il tag in base alla posizione nella tabella
            if is_even(i): tbl.item(i, tags=('evenrow'))
            else: tbl.item(i, tags=('oddrow'))
            
        return tbl
    
    def setupTitle(self, parent, text):
        # semplice label che funge da titolo
        lbl_title = tk.Label(parent, 
                             text=text, 
                             font=(FT_family, FT_h1_size), 
                             bg=CC_title_bg, 
                             justify='left', 
                             anchor='w', 
                             padx=10, 
                             pady=10)
        lbl_title.grid(row=0, column=1, sticky='swe')
        return lbl_title

    def setupScrollbar(self, parent):
        scroll_bar = tk.Scrollbar(parent, orient='vertical', command=self.tbl.yview)
        scroll_bar.pack(side='left', fill='y')
        self.tbl.configure(yscrollcommand=scroll_bar.set)
        self.tbl.bind('<MouseWheel>', self.handle_scroll(type='both'))
        self.tbl.bind('<Button-4>', self.handle_scroll(type='up'))
        self.tbl.bind('<Button-5>', self.handle_scroll(type='down'))
        
        return scroll_bar

    def resize_columns(self, event):
        tot_width = self.tbl.winfo_width()        
        tot_len = len( reduce(lambda concat, string: concat+string, self.tbl['columns']) )
                        
        print(self.title)
        for col in self.tbl['columns']:
            len_ratio = len(col)/tot_len
            col_width = int(len_ratio * tot_width)
            print(col, len_ratio)
            self.tbl.column(col, width=col_width)

    def handle_scroll(self, type):
        # controlla il tipo di handler da restituire, in base al tipo richiesto
        # (N.B. in tutti i casi 'break' previene la propagazione dell'evento alla Treeview)
        if   type=='both':
            # handle di entrambe le direzioni
            def scroll(event): 
                direction = -1 if event.delta > 0 else 1
                self.tbl.yview_scroll(direction, "units")
                return 'break'
            
        elif type=='up':
            # handle della direzione verso l'alto
            def scroll(event): 
                self.tbl.yview_scroll(-1, "units")
                return 'break'
        
        elif type=='down':
            # handle della direzione verso il basso
            def scroll(event): 
                self.tbl.yview_scroll(1, "units")
                return 'break'

        return scroll

    def handle_highlight(self,event,*args):
        # imposta il cursore
        self.configure(cursor="hand2")
        
        # ultimo e nuovo iid (treeview item-id)
        last_iid = self.last_iid
        new_iid = self.tbl.identify_row(event.y)
            
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
        tags = self.tbl.item(iid, 'tags')
        
        # termina se l'iid non è un numero
        if not is_number(iid): return
        
        # toglie lo stile della riga
        if is_even(int(iid)): tags = remove_tag('evenrow', tags)
        else: tags = remove_tag('oddrow', tags)
        
        # aggiunge l'highlight
        self.tbl.item(iid, tags=append_tag('highlight', tags))
        
    def clear_highlight(self, iid):
        tags = self.tbl.item(iid, 'tags')
        
        # termina se l'iid non è un numero
        if not is_number(iid): return
        
        # riassegna lo stile della riga
        if is_even(int(iid)): tags = append_tag('evenrow', tags)
        else: tags = append_tag('oddrow', tags)
        
        # toglie l'highlight
        self.tbl.item(iid, tags=remove_tag('highlight', tags))
        
    def stop_selection(self, event):
        for selection in self.tbl.selection():
            self.tbl.selection_remove(selection)