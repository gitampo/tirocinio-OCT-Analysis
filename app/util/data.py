import pandas as pd

def retrieve_all_patients():
    # ottiene il data frame dal file csv
    df = pd.read_csv('./patients.csv', dtype={'id': str})
    
    # ottiene intestazioni e righe
    headings = tuple((h for h in df.columns))
    rows = list(tuple(r) for r in df.values)
    
    return headings, rows

def retrieve_one_patient_history(patient_id):
    # ottiene il data frame dal file csv
    df = pd.read_csv('./patients_history.csv')
    df = df[df['id_paziente']==patient_id]
    df.sort_values(by='data', ascending=True)
    
    # ottiene intestazioni e righe legate solo paziente cercato
    headings = tuple(h for h in df.columns)
    rows = list(tuple(r) for r in df.values)
    
    return headings, rows

def find_patient(patient_id):
    # ottiene il data frame con il paziente cercato
    df = pd.read_csv('./patients.csv')
    df = df[df['id']==patient_id]    
    
    # prende solo la riga cercata (in forma di dizionario)
    row = df.iloc[0].to_dict()
       
    return row

def find_doctor(doctor_id):
    # ottiene il data frame con il medico cercato 
    df = pd.read_csv('./doctors.csv')
    df = df[df['id']==doctor_id]    
    
    # prende solo la riga cercata (in forma di dizionario)
    row = df.iloc[0].to_dict()
       
    return row