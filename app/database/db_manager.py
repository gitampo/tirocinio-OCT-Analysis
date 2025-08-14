from . import queries
import sqlite3

db_connection = None

def get_connection():
    global db_connection
    
    if not db_connection:
        raise ConnectionError('Connection to SQLite3 DB failed')
    
    return db_connection

######################################################################

def get_all_patients():
    # prende la connessione e imposta row-factory e cursore
    conn = get_connection()
    conn.row_factory = None
    cursor = conn.cursor()
    
    # dati di tutti i pazienti
    res = cursor.execute(queries['select']['select_all_patients'])
    
    # ottiene intestazioni e righe
    headings = tuple(heading_desc[0] for heading_desc in cursor.description)
    rows = res.fetchall()
    
    return headings, rows

def get_patient_history(patient_id):
    # prende la connessione e imposta row-factory e cursore
    conn = get_connection()
    conn.row_factory = None
    cursor = conn.cursor()
    
    # report del singolo paziente
    res = cursor.execute(queries['select']['select_report_by_patient_id'], [patient_id])
    
    # ottiene intestazioni e righe
    headings = tuple(heading_desc[0] for heading_desc in cursor.description)
    rows = res.fetchall()
    
    return headings, rows

def get_patient(patient_id):
    # prende la connessione e imposta row-factory e cursore
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # dati del singolo paziente
    res = cursor.execute(queries['select']['select_patient_by_id'], [patient_id])
    
    # ottiene un dizionario con i dati del paziente
    patient_dict = res.fetchone()
    
    return patient_dict

def get_doctor(doctor_id):
    # prende la connessione e imposta row-factory e cursore
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # dati del singolo medico
    res = cursor.execute(queries['select']['select_doctor_by_id'], [doctor_id])
    
    # ottiene un dizionario con i dati del paziente
    doctor_dict = res.fetchone()
    
    return doctor_dict

def add_report(report_dict):
    # prende la connessione e imposta row-factory e cursore
    conn = get_connection()
    conn.row_factory = None
    cursor = conn.cursor()

    # dati del report da passare alla query
    args = [report_dict['paziente'],
            report_dict['data'],
            report_dict['descrizione'],
            report_dict['oct']]
    
    # aggiunta del report
    cursor.execute(queries['insert']['insert_report'], args)

def get_bscans_of_report(report_id):
    # prende la connessione e imposta row-factory e cursore
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # B-scans per il report specificato
    res = cursor.execute(queries['select']['select_bscans_by_report_id'], [report_id])

    # ottiene un elenco di dizionari con i dati degli esami B-scan
    bscans = res.fetchall()

    return [dict(bscan) for bscan in bscans]