import tkinter as tk
from tkinter import ttk
from configs.colors import *
from configs.sizes import *



class PatientsFrame(tk.Frame):
    
    def __init__(self):
        super(PatientsFrame,self).__init__(height=SZ_topbar_h, bg=CC_white, padx=10, pady=10)
        
        # stile della Treeview
        style = ttk.Style()
        style.theme_use('clam')
        style.map('Treeview',
                  background=[('active', CC_highlight), ('selected', CC_selected)],)
        
        # tabella dei pazienti
        tbl_patients = ttk.Treeview(self, columns=('ID','Nome','Cognome'), show='headings')
        
        # table headings
        tbl_patients.heading('ID', text='ID', anchor='center')
        tbl_patients.heading('Nome', text='Nome', anchor='center')
        tbl_patients.heading('Cognome', text='Cognome', anchor='center')
        
        # table columns
        tbl_patients.column('ID', width=0, anchor='center')
        tbl_patients.column('Nome', width=200, anchor='center')
        tbl_patients.column('Cognome', width=200, anchor='center')
        
        tbl_patients.bind("<Motion>", self.on_enter)
        tbl_patients.bind("<Leave>", self.on_leave)
        
        tbl_patients.grid(row=1, column=1, sticky='nswe')
        tbl_patients.tag_configure("highlight", background=CC_highlight)
        
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=10)
        self.columnconfigure(2, weight=1)
        
        self.last_selected_iid = None
        
        # riempie la tabella
        for i in range(1,50+1):
            tbl_patients.insert(parent='', index=tk.END, iid=i, values=(i, 'John', 'Doe'))
            
        self.tbl_patients = tbl_patients
            
    def on_enter(self,event,*args):
        self.configure(cursor="hand2")
        
        last_selected_iid = self.last_selected_iid
        new_selected_iid = self.tbl_patients.identify_row(event.y)
            
        if last_selected_iid != new_selected_iid:
            self.tbl_patients.item(new_selected_iid, tags=("highlight",))
            if last_selected_iid is not None:
                self.tbl_patients.item(last_selected_iid, tags=())

        self.last_selected_iid = new_selected_iid

    def on_leave(self,event,*args):
        self.configure(cursor="arrow")
        self.tbl_patients.item(self.last_selected_iid, tags=())
        self.last_selected_iid = None

if __name__ == "__main__":
    root = tk.Tk()
    frame = PatientsFrame(root)
    root.mainloop()