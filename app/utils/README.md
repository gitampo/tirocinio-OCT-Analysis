# Argparser
Il progetto presenta una CLI, pensata principalmente per la gestione del package `deeplearning` ([vedi documentazione per package deeplearning](../deeplearning/README.md)).

Attraverso il parsing dei comandi è possibile gestire training e testing dei modelli. La CLI non è troppo avanzata e permette di effettuare solo operazioni semplici come: training from-scratch, training a partire da un checkpoint, testing di un modello addestrato.

Se si volesse modificare il dataset utilizzato o configurare più a fondo il training o il testing, si rimanda direttamente al package [deeplearning](../deeplearning/README.md).

## Comandi disponibili
Sono disponibili tre comandi: train, test, list
### Help principale 
```
usage: main.py [-h] {train,test,list} ...

CLI di OCT-Analysis, progetto di analisi delle immagini OCT per scopi
medici.

positional arguments:
  {train,test,list}
    train            Comando per l'esecuzione del training di un modello
    test             Comando per l'esecuzione del testing di un modello
    list             Comando per elencare i modelli e i checkpoints
                     disponibili

options:
  -h, --help         Mostra questo messaggio di help
```

### Help di `train` 
```
usage: main.py train [-h] -m MODEL (-s | -l CHCKPNT)

Comando per l'esecuzione del training di un modello

options:
  -h, --help                  Mostra questo messaggio di help
  -m MODEL, --model MODEL     Il modello di cui eseguire il training.
  -s, --from-scratch          Esegue il training da zero
  -l CHCKPNT, --load CHCKPNT  Carica i checkpoints prima del training.
```

### Help di `test`
```
usage: main.py test [-h] -m MODEL -l CHCKPNT

Comando per l'esecuzione del testing di un modello

options:
  -h, --help                  Mostra questo messaggio di help
  -m MODEL, --model MODEL     Il modello di cui eseguire il testing
  -l CHCKPNT, --load CHCKPNT  Carica i checkpoints prima del testing
```

### Help di `list`
```
usage: main.py list [-h] (-m | -c)

Comando per elencare i modelli e i checkpoints disponibili

options:
  -h, --help         Mostra questo messaggio di help
  -m, --models       Lista i checkpoints disponibili e caricabili
  -c, --checkpoints  Lista i checkpoints disponibili e caricabili
```
