@queryname:insert_report
INSERT INTO reports(paziente,data,descrizione)
VALUES (?, ?, ?);

@queryname:insert_bscan
INSERT INTO bscans(report, immagine)
VALUES (?, ?);