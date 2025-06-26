import tkinter as tk
from tkinter import ttk
from configs.colors import *
from configs.sizes import *
from util.funs import *


class PatientsFrame(tk.Frame):
    
    def __init__(self):
        super(PatientsFrame,self).__init__(height=SZ_topbar_h, bg=CC_white, padx=10, pady=10)
        
        # tabella dei pazienti
        tbl_patients = ttk.Treeview(self, columns=('ID','Nome','Cognome'), show='headings')
        
        # stile della Treeview
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('Treeview', rowheight=50, relief='solid', borderwidth=1)
        style.map('Treeview',
                  background=[('active', CC_highlight), ('selected', CC_selected)],)
        
        # stile righe pari e righe dispari
        tbl_patients.tag_configure('evenrow', background=CC_evenrow) 
        tbl_patients.tag_configure('oddrow', background=CC_oddrow)
        
        # table headings
        tbl_patients.heading('ID', text='ID', anchor='center')
        tbl_patients.heading('Nome', text='Nome', anchor='center')
        tbl_patients.heading('Cognome', text='Cognome', anchor='center')
        
        # table columns
        tbl_patients.column('ID', width=0, anchor='center')
        tbl_patients.column('Nome', width=200, anchor='center')
        tbl_patients.column('Cognome', width=200, anchor='center')
        
        # configurazione e posizionamento della treeview
        tbl_patients.tag_configure("highlight", background=CC_highlight)
        tbl_patients.grid(row=1, column=1, sticky='nswe')
        
        # eventi della treeview
        tbl_patients.bind("<Motion>", self.on_motion)
        tbl_patients.bind("<Leave>", self.on_leave)
        
        # configurazione delle colonne
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=10)
        self.columnconfigure(2, weight=1)
        
        # riempimento della tabella
        for i in range(1,50+1):
            tbl_patients.insert(parent='', index=tk.END, iid=i, values=(i, 'John', 'Doe'))
            
            # assegna lo stile il tag in base alla posizione nella tabella
            if is_even(i): tbl_patients.item(i, tags=('evenrow'))
            else: tbl_patients.item(i, tags=('oddrow'))
            
        self.last_iid = None
        self.tbl_patients = tbl_patients
            
    def on_motion(self,event,*args):
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