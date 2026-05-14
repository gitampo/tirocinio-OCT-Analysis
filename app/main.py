from utils.argparser import get_args, handle_args

# quando lo script eseguito come main
if __name__ == '__main__':

    # ottiene gli arguments e li gestisce (CLI)
    args = get_args()
    handle_args(args)
    
    # lazy loading dei moduli per l'esecuzione dell'app
    from gui.OCTAnalysisApp import *
    from configs.paths import PT_database
    import sqlite3
    from database import db_manager

    # connessione al database e avvio applicazione
    # isolation_level=None abilita l'auto-commit per ogni operazione
    # NON usiamo 'with' per evitare il rollback automatico al termine
    db_connection = sqlite3.connect(PT_database, isolation_level=None)
    db_manager.db_connection = db_connection
    
    try:
        app = OCTAnalysisApp()
        app.mainloop()
    finally:
        # chiude la connessione quando l'app si termina
        db_connection.close()