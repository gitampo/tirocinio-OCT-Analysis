@queryname:update_bscan_prediction
UPDATE bscans
SET malattia_predetta = ?, probabilità_predizione = ?
WHERE id = ?;

@queryname:update_bscan_validation
UPDATE bscans
SET validazione_medico = ?, malattia_validata = ?, validato_il = CURRENT_TIMESTAMP
WHERE id = ?;