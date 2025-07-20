@queryname:create_patients
CREATE TABLE IF NOT EXISTS patients (
    id INTEGER PRIMARY KEY,
    nome VARCHAR(50) NOT NULL,
    cognome VARCHAR(50) NOT NULL,
    sesso CHAR(1),
    età INTEGER check(età>=0)
);

@queryname:create_reports
CREATE TABLE IF NOT EXISTS reports (
    id INTEGER PRIMARY KEY,
    paziente INTEGER REFERENCES patients(id),
    data DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    descrizione VARCHAR(300) NOT NULL,
    oct VARCHAR(255) NOT NULL
);

@queryname:create_doctors
CREATE TABLE IF NOT EXISTS doctors (
    id INTEGER PRIMARY KEY,
    username VARCHAR(55) NOT NULL,
    nome VARCHAR(50) NOT NULL,
    cognome VARCHAR(50) NOT NULL,
    sesso CHAR(1) DEFAULT 'M'
);