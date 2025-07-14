### Modulo per la configurazione delle giustificazioni (AC = Anchors)
### Le tabelle usano un dizionario per gli anchors delle colonne, in questo modo si configurano le giustificazioni.
### Di default le giustificazioni sono centrate.

AC_patients_list = {
    'nome':'w',
    'cognome':'w'    
}

AC_patient_history = {
    'descrizione':'w'  
}

# Larghezza percentuale di ciascuna colonna
# (se si inseriscono le dimensioni di tutte le colonne, 
#  allora la somma deve ammontare a 1, 
#  altrimenti le dimensioni vengono ignorate)
CS_patients_list = { 
    'id': 0.15,
    'sesso': 0.15,
    'età': 0.15
}

# Larghezza percentuale di ciascuna colonna
# (se si inseriscono le dimensioni di tutte le colonne, 
#  allora la somma deve ammontare a 1, 
#  altrimenti le dimensioni vengono ignorate)
CS_patient_history = { 
    'descrizione':0.5
}