from .query_parser import load_all_queries
from configs.paths import PT_query_dir, PT_database
import sqlite3

# caricamento del dizionario con tutte le queries
# N.B. dizionario della forma {query-type:{query-name:query-block}}
queries = load_all_queries(PT_query_dir)

# inizializzazione del database
with sqlite3.connect(PT_database) as connection:
    cursor = connection.cursor()
    
    # eliminazione delle tabelle già esistenti
    # todo: togliere questi 'drop' quando si toglieranno i dati di mockup
    cursor.execute(queries['drop']['drop_patients'])
    cursor.execute(queries['drop']['drop_doctors'])
    cursor.execute(queries['drop']['drop_reports'])
    
    # creazione delle tabelle
    cursor.execute(queries['create']['create_patients'])
    cursor.execute(queries['create']['create_doctors'])
    cursor.execute(queries['create']['create_reports'])
    
    # carica dati di mockup nel DB
    # todo: togliere questi 'insert' quando si toglieranno i dati di mockup
    cursor.execute(queries['insert']['insert_mockup_patients'])
    cursor.execute(queries['insert']['insert_mockup_doctors'])
    cursor.execute(queries['insert']['insert_mockup_reports'])