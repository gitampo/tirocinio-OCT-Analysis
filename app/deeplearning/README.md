# Deeplearning
Questo package presenta tutto il necessario per eseguire training, testing e inferenza con i modelli messi a disposizione. E' stata anche implementata k-fold cross validation sul dataset OCTDL.

La filosofia del package è generalizzare il training e il testing per consentirne l'esecuzione, in maniera indipendete dai modelli, dai checkpoint e dai database che si vogliono utilizzare.

## Utilizzo del package attraverso Argparsing
Il package è pensato per essere utilizzato in unione con l'argparser del package `utils` ([vedi documentazione per package utils](../utils/README.md))

## Struttura del package `deeplearning`
```bash
deeplearning
│
├── README.md
│
├── __init__.py
│
├── availables.py
├── inference.py
├── kfoldcv.py
├── model_factory.py
├── testing.py
├── training.py
├── utils.py        
│
├── data            # dati di input e di output dei modelli
│   ├── datasets   
│   └── checkpoints
│
└── models          # classi e funzioni per i modelli
    ├── ViTMAE.py
    └── ...
```

## Moduli del package
- **availables.py**: presenta funzioni che indicano modelli, checkpoint e dataset disponibili nel sistema.
- **kfoldcv.py**: k-fold cross validation di un modello sul dataset OCTDL. Dipende dagli altri moduli per implementare il training e le metriche di testing. Il kfoldcv viene eseguito senza information leakage tra split di train e split di test.
- **model_factory.py**: utilizzato per generalizzare il modello e altri training arguments, in modo da caricare correttamente il modello richiesto all'inizio di training e testing. Utilizza dizionari che associano al nome di ciascun modello le varie componenti del modello stesso.
- **training.py**: contiene una funzione `train()` che si occupa di caricare quanto serve per l'esecuzione del training e al termine chiede di fornire un nome al nuovo checkpoint. Utilizza `model_factory.py` per generalizzare.
- **testing.py**: contiene una funzione `test()` che si occupa di caricare quanto serve per l'esecuzione del testing e al termine mostra le metriche calcolate. Utilizza `model_factory.py` per generalizzare.
- **utils.py**: utility generali del package `deeplearning`.

## Inizializzazione del package `__init__.py`
Lo script di inizializzaione presenta variabili importanti che vanno eventualmente aggiornate, per esempio all'introduzione di nuovi modelli nel sistema.
``` python
# configurazione delle variabili del package
DEFAULT_DATASET = 'OCTDL'
DEFAULT_SPLIT = (0.8, 0.1, 0.1)  # train, eval, test split

PREPROCESS_BATCH_SIZE = 8
TRAIN_BATCH_SIZE = 8
TEST_BATCH_SIZE = 8

NUM_PROC = 5 # numero di processi per il data loading
SEED = 42 # fissare il seed per la riproducibilità

...
```

## Checkpoints
Il package ha una cartella `checkpoints` che contiene i salvataggi dei modelli allenati, in modo che possano essere caricati e utilizzati. La struttura della cartella è la seguente
```bash
data/checkpoints
│
├── model-1
│   ├── checkpoint-1.pth
│   ├── checkpoint-2.pth
│   ├── ...
│   └── checkpoint-n.pth
│
├── model-2
│   ├── checkpoint-1.pth
│   ├── checkpoint-2.pth
│   ├── ...
│   └── checkpoint-n.pth
│
├── ...
│
└── model-n
    ├── checkpoint-1.pth
    ├── checkpoint-2.pth
    ├── ...
    └── checkpoint-n.pth
```

## Datasets
Il package ha una cartella `datasets` che deve contenere tutti i dataset utilizzabili dalle architetture. Vista la natura del progetto i vari dataset devono essere nella forma di "imagefolder" senza split che distinga in train, test ed eval; come di seguito:
```bash
data/datasets
│
├── dataset-1
│   ├── class-1
│   ├── class-2
│   ├── ...
│   └── class-n
│
├── dataset-2
│   ├── class-1
│   ├── class-2
│   ├── ...
│   └── class-n
│
├── ...
│
└── dataset-n
    ├── class-1
    ├── class-2
    ├── ...
    └── class-n
```