@queryname:update_bscan_prediction
UPDATE bscans
SET malattia_predetta = ?, probabilità_predizione = ?
WHERE id = ?;