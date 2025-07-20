# OCT-Analysis
L’OCT (tomografia ottica a radiazione coerente) è un esame non invasivo che fornisce delle immagini ad elevata risoluzione di scansioni a strati (tomografiche) della cornea, della parte centrale della retina (macula) e della testa del nervo ottico (papilla). Questo esame consente di ottenere informazioni fondamentali sullo stato di salute delle diverse parti anatomiche dell’occhio, indispensabili per la diagnosi e il monitoraggio di numerose patologie dell'apparato visivo. Tra le varie informazioni ottenibili dall’esame OCT figurano le alterazioni strutturali della retina e la misurazione dello spessore dei tessuti oculari. 

## Scopo dell'applicazione
Realizzare un’applicazione medica che fornisca, almeno, le seguenti possibilità: 
- al paziente, l’acquisizione e relativa visualizzazione delle sue OCT per una migliore conservazione della sua documentazione sanitaria; 
- al medico e al paziente, di estrarre e visualizzare informazioni sull’andamento di una patologia o, comunque, di uno status per cui è necessario un monitoraggio. 

## Eseguire il progetto (Unix/macOs)

````bash 
# entrare nella cartella del progetto
cd OCT-Analysis/

# (opzionale) spostarsi in un ambiente virtuale
python -m venv .venv
source .venv/bin/activate

# installare le dipendenze
pip install -r requirements.txt

# entrare nella cartella app/
cd app/

# eseguire lo script main.py
python main.py
````

## Struttura del progetto
``` bash
OCT-Analysis
│
├── README.md
│
├── requirements.txt
│
└── app
    │
    │   # entry point
    ├── main.py 
    │
    │   # assets
    ├── assets 
    │   └── app_logo.png
    │
    │   # classi per la GUI Tkinter
    ├── classes
    │   ├── AddReportDialog.py
    │   ├── ImageCanvas.py
    │   ├── LoginFrame.py
    │   ├── OCTAnalysisApp.py
    │   ├── PatientHistoryFrame.py
    │   ├── PatientsListFrame.py
    │   ├── ReportFrame.py
    │   ├── TableFrame.py
    │   └── TopBar.py
    │
    │   # moduli di configurazione del progetto
    ├── configs
    │   ├── colors.py
    │   ├── fonts.py
    │   ├── paths.py
    │   ├── sizes.py
    │   └── tables.py
    │
    │   # package per gestione del database
    ├── database
    │   ├── README.md
    │   ├── __init__.py
    │   ├── db_manager.py
    │   ├── query_parser.py
    │   │
    │   │   # dati memorizzati
    │   ├── data 
    │   │   ├── images/...
    │   │   └── octanalysis.db
    │   │
    │   │   # file di query
    │   └── queries
    │       ├── create.sql
    │       ├── drop.sql
    │       ├── insert.sql
    │       └── select.sql
    │
    │   # utility
    └── util
        └── funs.py
```

## Informazioni sui Package del progetto
Per ulteriori informazioni sui package, visitare gli appositi `README.md`:
- package `database`: [documentazione per package database](app/database/README.md)