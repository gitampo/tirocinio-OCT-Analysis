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

# se si inseriscono le dimensioni di tutte le colonne, la somma deve ammontare a 1
CS_patients_list = { 
    'id': 0.15,
    'sesso': 0.15,
    'età': 0.15
}

# se si inseriscono le dimensioni di tutte le colonne, la somma deve ammontare a 1
CS_patient_history = { 
    'descrizione':0.5 
}