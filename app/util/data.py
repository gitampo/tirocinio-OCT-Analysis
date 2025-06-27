import pandas as pd

def retrieve_all_patients():
    # ottiene il data frame dal file csv
    df = pd.read_csv('./patients.csv', dtype={'id': str})
    
    # ottiene intestazioni e righe
    headings = tuple((heading for heading in df.columns))
    rows = list(tuple(r) for r in df.values)
    
    return headings, rows

def retrieve_one_patient_history(patient_id):
    # ottiene il data frame dal file csv
    df = pd.read_csv('./patients_history.csv')
    df = df[df['id_paziente']==patient_id]
    df.sort_values(by='data', ascending=True)
    
    # ottiene intestazioni e righe legate solo paziente cercato
    headings = tuple(heading for i, heading in enumerate(df.columns))
    rows = list(tuple(attr for i, attr in enumerate(tuple(row))) for row in df.values)
    
    return headings, rows