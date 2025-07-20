from classes.OCTAnalysisApp import *
from configs.paths import PT_database
import sqlite3
from database import db_manager

# quando lo script eseguito come main
if __name__ == '__main__':
    # connessione al database e avvio applicazione
    with sqlite3.connect(PT_database) as db_connection:
        db_manager.db_connection = db_connection    # imposta la connessione del db_manager 
        app = OCTAnalysisApp()                      # istanzia l'applicazione
        app.mainloop()                              # avvia il mainloop di Tkinter