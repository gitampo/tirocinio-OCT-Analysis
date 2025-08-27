from configs.paths import PT_database
from . import queries
import sqlite3

db_connection = None

def get_connection():
    global db_connection
    
    if not db_connection:
        raise ConnectionError('Connection to SQLite3 DB failed')
    
    return db_connection

# decorator per garantire la connessione al DB
def needs_connection(row_factory=None):
    def decorator(func):
        def wrapper(*args, **kwargs):
            # ottiene il parametro new_thread
            new_thread = kwargs.get('new_thread', False)

            # ottiene la connessione al DB
            conn = get_connection()
            if new_thread:
                conn = sqlite3.connect(PT_database)

            # imposta il row_factory e il cursore
            conn.row_factory = row_factory
            cursor = conn.cursor()

            # esegue la funzione con il cursore
            kwargs.pop('new_thread', None) # rimuove il parametro per non passarlo alla funzione
            result = func(cursor, *args, **kwargs)

            # gestisce la chiusura della connessione
            if new_thread:
                conn.commit()
                conn.close()

            return result
        return wrapper
    return decorator

######################################################################

@needs_connection()
def get_all_patients(cursor):
    # dati di tutti i pazienti
    res = cursor.execute(queries['select']['select_all_patients'])
    
    # ottiene intestazioni e righe
    headings = tuple(heading_desc[0] for heading_desc in cursor.description)
    rows = res.fetchall()
    
    return headings, rows

@needs_connection()
def get_patient_history(cursor, patient_id):
    # report del singolo paziente
    res = cursor.execute(queries['select']['select_report_by_patient_id'], [patient_id])
    
    # ottiene intestazioni e righe
    headings = tuple(heading_desc[0] for heading_desc in cursor.description)
    rows = res.fetchall()
    
    return headings, rows

@needs_connection(sqlite3.Row)
def get_patient(cursor, patient_id):
    # dati del singolo paziente
    res = cursor.execute(queries['select']['select_patient_by_id'], [patient_id])
    
    # ottiene un dizionario con i dati del paziente
    patient_dict = res.fetchone()
    
    return patient_dict

@needs_connection(sqlite3.Row)
def get_doctor(cursor, doctor_id):
    # dati del singolo medico
    res = cursor.execute(queries['select']['select_doctor_by_id'], [doctor_id])
    
    # ottiene un dizionario con i dati del paziente
    doctor_dict = res.fetchone()
    
    return doctor_dict

@needs_connection()
def add_report(cursor, report_dict, bscan_list):
    # dati del report da passare alla query
    args = [report_dict['paziente'],
            report_dict['data'],
            report_dict['descrizione']]

    # aggiunta del report
    cursor.execute(queries['insert']['insert_report'], args)
    report_id = cursor.lastrowid
    
    # aggiunta dei B-scan relativi al report
    for bscan in bscan_list:
        cursor.execute(queries['insert']['insert_bscan'], [report_id, bscan])

@needs_connection(sqlite3.Row)
def get_bscans_of_report(cursor, report_id):
    # B-scans per il report specificato
    res = cursor.execute(queries['select']['select_bscans_by_report_id'], [report_id])

    # ottiene un elenco di dizionari con i dati degli esami B-scan
    bscans = res.fetchall()

    return [dict(bscan) for bscan in bscans]

@needs_connection()
def set_prediction_for_bscan(cursor, bscan_id, malattia, probabilita):
    # aggiorna la previsione per il B-scan specificato
    cursor.execute(queries['update']['update_bscan_prediction'], [malattia, probabilita, bscan_id])
    cursor.connection.commit()