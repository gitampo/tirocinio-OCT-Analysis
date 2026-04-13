from .query_parser import load_all_queries
from configs.paths import PT_query_dir, PT_database
import sqlite3
from pathlib import Path

# caricamento del dizionario con tutte le queries
# N.B. dizionario della forma {query-type:{query-name:query-block}}
queries = load_all_queries(PT_query_dir)

DB_PATH = Path(PT_database)


def _create_database(connection):
    cursor = connection.cursor()

    # eliminazione delle tabelle già esistenti
    # todo: togliere questi 'drop' quando si toglieranno i dati di mockup
    cursor.execute(queries['drop']['drop_patients'])
    cursor.execute(queries['drop']['drop_doctors'])
    cursor.execute(queries['drop']['drop_reports'])
    cursor.execute(queries['drop']['drop_bscans'])

    # creazione delle tabelle
    cursor.execute(queries['create']['create_patients'])
    cursor.execute(queries['create']['create_doctors'])
    cursor.execute(queries['create']['create_reports'])
    cursor.execute(queries['create']['create_bscans'])

    # carica dati di mockup nel DB
    # todo: togliere questi 'insert' quando si toglieranno i dati di mockup
    cursor.execute(queries['mockup']['insert_mockup_patients'])
    cursor.execute(queries['mockup']['insert_mockup_doctors'])
    cursor.execute(queries['mockup']['insert_mockup_reports'])
    cursor.execute(queries['mockup']['insert_mockup_bscans'])

    connection.commit()


def _initialize_database():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(PT_database)
    try:
        cursor = connection.cursor()
        cursor.execute('PRAGMA integrity_check;')
        integrity = cursor.fetchone()
        if integrity is None or integrity[0] != 'ok':
            raise sqlite3.DatabaseError('Database integrity check failed')

        _create_database(connection)
    except sqlite3.DatabaseError:
        connection.close()
        if DB_PATH.exists():
            DB_PATH.unlink()

        with sqlite3.connect(PT_database) as connection:
            _create_database(connection)
    else:
        connection.close()


# inizializzazione del database
_initialize_database()
