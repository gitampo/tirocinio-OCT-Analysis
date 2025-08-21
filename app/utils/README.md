# Argparser
Il progetto presenta una CLI, pensata principalmente per la gestione del package `deeplearning` ([vedi documentazione per package deeplearning](../deeplearning/README.md)).

Attraverso il parsing dei comandi è possibile gestire training e testing dei modelli. La CLI non è troppo avanzata e permette di effettuare solo operazioni semplici come: training from-scratch, training a partire da un checkpoint, testing di un modello addestrato.

Se si volesse configurare più a fondo il training o il testing, si rimanda direttamente al package [deeplearning](../deeplearning/README.md).

## Comandi disponibili
Sono disponibili i seguenti comandi: `train`, `test`, `list`
### Help principale 
```
usage: main.py [-h] COMMAND ...

CLI di OCT-Analysis, progetto di analisi delle immagini OCT per scopi medici.

positional arguments:
   COMMAND
      train
          Comando per l'esecuzione del training di un
          modello
      test
          Comando per l'esecuzione del testing di un
          modello
      list
          Comando per elencare i modelli e i
          checkpoints disponibili

options:
   -h, --help
          Mostra questo messaggio di help.
```

### Help di `train` 
```
usage: main.py train [-h] (-s MODEL | -c CHECKPOINT) [-d DATASET]

Comando per l'esecuzione del training di un modello

options:
   -h, --help
          Mostra questo messaggio di help.
   -s MODEL, --from-scratch MODEL
          Avvia il training da zero, del modello
          specificato.
          (vedi anche "list --models")
   -c CHECKPOINT, --from-checkpoint CHECKPOINT
          Avvia il training a partire dal checkpoint
          specificato.
          (vedi anche "list --checkpoints").
   -d DATASET, --dataset DATASET
          Specifica il dataset da utilizzare per il
          training.

examples:
   # Training da zero
   python main.py train --from-scratch vitmae-light

   # Training da checkpoint
   python main.py train --from-checkpoint vitmae-light/base

   # Training da zero con dataset specifico
   python main.py train -s vitmae-light --dataset OCTDL
```

### Help di `test`
```
usage: main.py test [-h] -c CHECKPOINT [-d DATASET]

Comando per l'esecuzione del testing di un modello

options:
   -h, --help
          Mostra questo messaggio di help.
   -c CHECKPOINT, --checkpoint CHECKPOINT
          Carica i checkpoints prima del testing
   -d DATASET, --dataset DATASET
          Specifica il dataset da utilizzare per il
          testing.

examples:
   # Testing del checkpoint selezionato
   python main.py test --checkpoint vitmae-light/base

   # Testing del checkpoint su un dataset specifico
   python main.py test -c vitmae-light/base --dataset OCTDL
```

### Help di `list`
```
usage: main.py list [-h] (-m | -c | -d)

Comando per elencare i modelli e i checkpoints disponibili

options:
   -h, --help
          Mostra questo messaggio di help.
   -m, --models
          Lista dei modelli disponibili.
   -c, --checkpoints
          Lista dei checkpoints disponibili.
   -d, --datasets
          Lista dei dataset disponibili.

examples:
   # Listing dei modelli disponibili
   python main.py list --models

   # Listing dei checkpoint disponibili
   python main.py list --checkpoints

   # Listing dei dataset disponibili
   python main.py list --datasets
```
