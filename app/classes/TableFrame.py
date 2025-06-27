import tkinter as tk
from tkinter import ttk
from configs.colors import *
from configs.sizes import *
from configs.fonts import *
from util.funs import *
from functools import reduce

class TableFrame(tk.Frame):
    
    def __init__(self, parent, table_headings, table_rows, title, font_specs=(FT_family, FT_h1_size, 'bold'), row_anchors_dict=None):
        super(TableFrame,self).__init__(bg=CC_frm_default)
        
        # istanza dello stile
        style = ttk.Style()
        
        # stile della Treeview
        stylename = 'Treeview'
        style.theme_use('clam')
        style.layout(stylename, style.layout('Treeview'))
        style.configure(stylename, rowheight=SZ_tbl_pat_list_row_h, fieldbackground=CC_tbl_empty)
        style.map(stylename,
            background=[('active', CC_tbl_highlight), ('selected', CC_tbl_selected)],
            foreground=[('active', CC_tbl_text_highlight), ('selected', CC_tbl_text_selected)]
        )
        
        # stile dell'heading della Treeview
        style.configure("Treeview.Heading", 
                foreground=CC_tbl_heading_text,
                background=CC_tbl_heading_bg,
                relief='solid',
                font=(FT_family, FT_size, 'bold'))
        style.map("Treeview.Heading",
            background=[('active', CC_tbl_highlight), ('selected', CC_tbl_selected)],
            foreground=[('active', CC_tbl_text_highlight), ('selected', CC_tbl_text_selected), ('!active !selected', CC_tbl_text)]
        )
        
        # attributi di classe
        self.parent = parent
        self.title = title
        self.last_iid = None
        self.row_anchors_dict = row_anchors_dict
        
        # setup delle dei widget
        self.frm_container = self.setupContainer(self)
        self.lbl_title = self.setupTitle(self, title, font_specs)
        self.tbl = self.setupTreeview(self.frm_container, table_headings, table_rows, stylename)
        self.scroll_bar = self.setupScrollbar(self.frm_container)

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
        tbl.tag_configure("text", foreground=CC_tbl_text)
        
        # eventi della treeview
        tbl.bind("<Motion>", self.handle_highlight)
        tbl.bind("<MouseWheel>", self.handle_highlight)
        tbl.bind("<Leave>", self.on_leave)
        tbl.bind("<Configure>", self.resize_columns)
        tbl.bind("<<TreeviewSelect>>", self.stop_selection)
        
        # caricamento delle intestazioni
        for heading in table_headings:
            # se sono forniti degli allineamenti per le righe, li usa
            try: row_anchor = self.row_anchors_dict[heading]
            except: row_anchor='center'
            
            # crea intestazioni e colonne
            tbl.heading(heading, text=heading.upper(), anchor='center')            
            tbl.column(heading, stretch=True, anchor=row_anchor)
        
        # riempimento della tabella
        for i,row in enumerate(table_rows):
            # inserisce il valore alla fine della tabella
            tbl.insert(parent='', index=tk.END, iid=i, values=row)
            
            # assegna lo stile il tag in base alla posizione nella tabella
            if is_even(i): tbl.item(i, tags=('evenrow','text'))
            else: tbl.item(i, tags=('oddrow','text'))
            
        return tbl
    
    def setupTitle(self, parent, text, font_specs):
        # semplice label che funge da titolo
        lbl_title = tk.Label(parent, 
                             text=text, 
                             font=font_specs, 
                             fg = CC_title_fg,
                             bg=CC_title_bg, 
                             justify='left', 
                             anchor='w', 
                             padx=10, 
                             pady=10)
        lbl_title.grid(row=0, column=1, sticky='swe')
        return lbl_title

    def setupScrollbar(self, parent):
        scroll_bar = tk.Scrollbar(parent, orient='vertical', troughcolor=CC_tbl_scroll_trough, bg=CC_tbl_scroll, width=SZ_tbl_scroll_w, command=self.tbl.yview)
        scroll_bar.pack(side='left', fill='both')
        self.tbl.configure(yscrollcommand=scroll_bar.set)
        self.tbl.bind('<MouseWheel>', self.handle_scroll(type='both'))
        self.tbl.bind('<Button-4>', self.handle_scroll(type='up'))
        self.tbl.bind('<Button-5>', self.handle_scroll(type='down'))
        
        return scroll_bar

    def resize_columns(self, event):
        # ottiene la dimensione della tabella 
        tot_width = self.tbl.winfo_width()        
        
        # ottiene la lunghezza totale di tutti i nomi delle colonne
        tot_len = len( reduce(lambda concat, string: concat+string, self.tbl['columns']) )
                        
        # per ogni colonna calcola la dimensione 
        for col in self.tbl['columns']:
            # rapporto lunghezza nome colonna / lunghezza totale
            len_ratio = len(col)/tot_len
            # grandezza della colonna in percentuale
            col_width = int(len_ratio * tot_width)
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