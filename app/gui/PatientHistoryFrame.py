import tkinter as tk
from configs.colors import *
from configs.sizes import *
from configs.fonts import *
from configs.tables import *
from gui.TableFrame import *
from gui.AddReportDialog import *
from utils.funs import *

class PatientHistoryFrame(TableFrame):
    
    def __init__(self, parent, table_headings, table_rows, patient_dict, viewtype = 'doctor'):
        
        # supercostruttore
        super(PatientHistoryFrame,self).__init__(
            parent, 
            table_headings,
            table_rows,
            row=3, column=0,
            font_specs=(FT_family, FT_h2_size, 'bold'),
            columns_anchors_dict=AC_patient_history,
            columns_sizes_dict=CS_patient_history,
            unwanted_headings = ('id', 'paziente', 'oct', 'creato_il')
        )
        
        # dati del paziente
        nome = patient_dict['nome']
        cognome = patient_dict['cognome']
        
        self.patient_dict = patient_dict
        self.table_headings = table_headings
        self.table_rows = table_rows
        self.dlg_add_report = None
        
        # dati da condividere con il parent (inizialmente non ci sono dati)
        self.shared_data = None
                
        # imposta i widget
        self.setupFrameTitle(self, f'Storico di {nome} {cognome}', row=0, column=0)
        self.setupInfoFrame(self, patient_dict, row=1, column=0, )

        # associa l'apertura dello storico del paziente, all'evento del click sulla riga
        self.tbl.bind('<Button-1>', self.alert_parent_of_rowclick)
        
        # mostra il pulsante di aggiunta solo se la view è del dottore
        if viewtype == 'doctor':
            self.setupAddReportButton(self, row=2, column=0)
            self.bind('<<AddDialogSuccess>>', self.alert_parent_of_rowadd)
        
        # configurazione di righe e colonne
        self.columnconfigure(0, weight=1)
        self.rowconfigure(3, weight=1)
        
    def alert_parent_of_rowadd(self, event):# genera un evento visibile dal padre e gli passa i dati dello storico cliccato
        self.shared_data = self.patient_dict
        self.event_generate('<<ReportRowAdded>>')
        
    def alert_parent_of_rowclick(self, event):
        # se l'utente preme sull'heading, non deve fare niente
        region = self.tbl.identify_region(event.x, event.y)
        if region not in ('cell','tree'): return

        # ottiene l'iid della riga premuta
        clicked_iid = self.tbl.identify_row(event.y)
        if not clicked_iid: return

        # dizionario del report composto da chiavi e valori (chiavi=headings, valori=valori dell'item)
        index = self.tbl.index(clicked_iid)
        report_dict = dict(zip(self.table_headings, self.table_rows[index]))
    
        # dati condivisi con il parent
        self.shared_data = report_dict
    
        # genera un evento visibile dal padre e gli passa i dati dello storico cliccato
        self.event_generate('<<ReportRowClicked>>')
        
    def setupFrameTitle(self, parent, text, row=0, column=0, font_specs=(FT_family, FT_h1_size, 'bold')):
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
        lbl_title.grid(row=row, column=column, sticky='nwe')
        return lbl_title
    
    def setupInfoFrame(self, parent, patient_dict, row=0, column=0,):
        # frame di padding/di background
        frm_container = tk.Frame(parent, 
                             bg=CC_frm_default, 
                             padx=20, 
                             pady=10)
        frm_container.grid(row=row, column=column, sticky='nswe')
        
        # frame delle info del paziente
        frm_info = tk.Frame(frm_container, 
                             bg=CC_frm_info,
                             padx=20, 
                             pady=10)
        frm_info.pack(fill='both')
        
        font_specs = (FT_family, FT_size, 'bold')
        
        # etichette delle info del paziente
        lbl_tags = [
          tk.Label(frm_info,pady=2, fg=CC_frm_info_text, bg=CC_frm_info, font=font_specs, anchor='w',text='Id:')
         ,tk.Label(frm_info,pady=2, fg=CC_frm_info_text, bg=CC_frm_info, font=font_specs, anchor='w',text='Nome:')
         ,tk.Label(frm_info,pady=2, fg=CC_frm_info_text, bg=CC_frm_info, font=font_specs, anchor='w',text='Cognome:')
         ,tk.Label(frm_info,pady=2, fg=CC_frm_info_text, bg=CC_frm_info, font=font_specs, anchor='w',text='Sesso:')
         ,tk.Label(frm_info,pady=2, fg=CC_frm_info_text, bg=CC_frm_info, font=font_specs, anchor='w',text='Età:')
        ]
        
        # valori delle info del paziente
        lbl_values = [
          tk.Label(frm_info, pady=2, fg=CC_frm_info_text, bg=CC_frm_info, anchor='w',text=f'{patient_dict["id"]}'),
          tk.Label(frm_info, pady=2, fg=CC_frm_info_text, bg=CC_frm_info, anchor='w',text=f'{patient_dict["nome"]}'),
          tk.Label(frm_info, pady=2, fg=CC_frm_info_text, bg=CC_frm_info, anchor='w',text=f'{patient_dict["cognome"]}'),
          tk.Label(frm_info, pady=2, fg=CC_frm_info_text, bg=CC_frm_info, anchor='w',text=f'{patient_dict["sesso"]}'),
          tk.Label(frm_info, pady=2, fg=CC_frm_info_text, bg=CC_frm_info, anchor='w',text=f'{patient_dict.get("età", "N/A")}')
        ] 
        
        # posizionamento di etichette e valori
        pad_l = 0
        for lbl_tag, lbl_val in zip(lbl_tags,lbl_values):     
            lbl_tag.pack(padx=(pad_l,0), side='left')  
            lbl_val.pack(side='left')
            pad_l = 30 # padding sinistro di 30 (tranne che per il primo elemento)
            
        return frm_info
    
    def setupAddReportButton(self, parent, row=0, column=0):
        # frame di padding/di background
        frm_container = tk.Frame(parent, 
                             bg=CC_frm_default,
                             padx=20)
        frm_container.grid(row=row, column=column, sticky='nswe', pady=(0,10))
        
        # pulsante di aggiunta
        btn_add_report = tk.Button(frm_container, 
                                   text='Aggiungi Report +', 
                                   width=30, 
                                   fg=CC_btn_text_primary ,
                                   bg=CC_btn_primary,
                                   command=self.add_report)
        btn_add_report.pack(side='right')
        
    def add_report(self):
        self.close_toplevels() # chiude il dialog, se era già aperto
        
        # crea un nuovo dialog
        dlg_add_report = AddReportDialog(self, self.patient_dict)
              
        # salva il riferimento al dialog
        self.dlg_add_report = dlg_add_report
        
    def close_toplevels(self):
        # se era già aperto un dialog, lo chiude
        if self.dlg_add_report is not None:
            self.dlg_add_report.destroy()
            self.dlg_add_report = None