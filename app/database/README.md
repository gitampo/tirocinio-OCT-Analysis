# Database SQLite3
Il progetto utilizza un database SQLite3 e il modulo python `sqlite3` per connetersi al DB.

## Gestione delle query
Il progetto presenta le query separate dalla logica. Per questo sono presenti appositi file `.sql` nella cartella `queries/`.

Questi file vengono parsati perché oltre ai blocchi delle query da eseguire, contengono i nomi di ciascuna query.

I nomi delle query sono specificati tramite uno pseudo-decoratore della forma: 
```
@queryname:<nome_della_query>
...
```

```sql
-- e.g. creazione della tabella dei pazienti con queryname
@queryname:create_patients
CREATE TABLE IF NOT EXISTS patients (
    id INTEGER PRIMARY KEY,
    nome VARCHAR(50) NOT NULL,
    cognome VARCHAR(50) NOT NULL,
    sesso CHAR(1),
    età INTEGER check(età>=0)
);
```
Questo meccanismo è custom, inventato appositamento per il progetto e serve a richiamare le query nel codice attraverso un dizionario `queries` che è strutturato come di seguito:
```python
# struttura del dizionario `queries`
# N.B. ogni query_type corrisponde al nome (senza estensione) di un file di query
queries = {
    <query_type> : {
        <query_name> : <query_block>,
        <query_name> : <query_block>,
        ...
    },
    <query_type> : {
        <query_name> : <query_block>,
        <query_name> : <query_block>,
        ...
    },
    ...
}

# e.g. utilizzo del dizionario `queries`
queries['select']['select_all_patients']
```

## Struttura del package `database`
```bash
database/
│ 
├── README.md
│
├── __init__.py         ## init del package
│
├── db_manager.py       ## gestore connessioni
│
├── query_parser.py     ## parser dei file delle query
│
├── data/               ## cartella per memorizzazione dati
│   ├── images/...
│   └── octanalysis.db
│
└── queries/            ## cartella con i file di query
    ├── create.sql
    ├── insert.sql
    ├── select.sql
    └── ...
```