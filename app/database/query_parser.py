import re
import os
from pathlib import Path

def parse_query_file(path_to_query_file):

    #  apertura del file di query da leggere
    with open(path_to_query_file, 'r') as query_file:
        # lettura di tutte le linee del file
        query_file_content = query_file.readlines()
        query_file_content = "".join(query_file_content)
        
        # separazione di nomi e blocchi delle query, per la composizione di un dizionario
        query_names = re.findall(r'@queryname:(.+)', query_file_content)
        query_blocks = re.split(r'@queryname:.+', query_file_content)[1:]
        
        # composizione del dizionario di query per il file richiesto 
        # N.B. dizionario della forma {nome-query:blocco-query}
        return dict(zip(query_names, query_blocks))
    
def load_all_queries(path_to_query_dir):
    all_queries_dict = {}
    
    # scansione di tutti i file nella cartella delle query
    for query_file in os.listdir(path_to_query_dir):
        
        # path sino al file di query dell'iterazione attuale
        query_file_path = Path(path_to_query_dir)/query_file
        
        # ottenimento del dizionario per il file scansionato
        query_file_dict = parse_query_file(query_file_path)
        
        # aggiunta del dizionario di query del file scansionato, 
        # al dizionario di tutte le query
        key = str(query_file_path.stem)
        all_queries_dict[key] = query_file_dict
    
    return all_queries_dict