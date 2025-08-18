# Deeplearning
Questo package presenta tutto il necessario per eseguire training, testing e inferenza con i modelli messi a disposizione.

## Struttura del package `deeplearning`
```bash
deeplearning
│
├── README.md
│
├── __init__.py
│
├── inference.py
├── testing.py
├── training.py
├── utils.py        
│
├── checkpoints/... # checkpoints distinti per modello
│
├── datasets        # dataset per training e testing 
│   ├── OCTDL/...
│   └── ...
│
└── models          # classi e funzioni per i modelli
    ├── ViTMAE.py
    └── ...
```

## Moduli `inference`, `testing`, `training`, `utils`
La filosofia è che ciascun modulo contiene le funzioni distinte per i diversi modelli e c'è un unica funzione, in ciascun modulo, che si occupa di caricare training/testing/inferenza richiesto dall'utente.

`training.py` e `testing.py` si occupano anche del caricamento del dataset e del caricamento di checkpoint precedentemente salvati nella cartella `checkpoints/`.

`utils.py` contiene funzioni di utilità generica relative al deeplearning.

## Inizializzazione del package `__init__.py`
Lo script di inizializzaione presenta variabili importanti soprattutto per il training (es. TrainingArguments) ma anche la lista dei modelli disponibili, che va aggiornata manualmente qualora cambiassero i modelli disponibili nel sistema.
``` python
...

AVAILABLE_MODELS = ['vitmae-light', 'vitmae-heavy', ...]
SEED = 42
vitmae_training_args = ...

...
```

## Utilizzo del package attraverso Argparsing
Il package è pensato per essere utilizzato in unione con l'argparser del package `utils` ([vedi documentazione per package utils](../utils/README.md))