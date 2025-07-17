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
# sono esclusi dall'albero i file con i dati di mockup (es. *.csv e images/)
# è rappresentata principalmente la struttura del codice

OCT-Analysis
│
├── README.md
│
├── .gitignore
│
└── app
    │
    ├── main.py   # entry point
    │
    ├── assets
    │   └── app_logo.png
    │
    ├── classes
    │   ├── AddReportDialog.py
    │   ├── ImageCanvas.py
    │   ├── LoginFrame.py
    │   ├── OCTAnalysisApp.py
    │   ├── PatientHistoryFrame.py
    │   ├── PatientsListFrame.py
    │   ├── ReportFrame.py
    │   ├── TableFrame.py
    │   └── TopBar.py
    │
    ├── configs
    │   ├── colors.py
    │   ├── fonts.py
    │   ├── sizes.py
    │   └── tables.py
    │
    └── util
        ├── data.py
        └── funs.py
```