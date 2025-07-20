@queryname:select_all_patients
SELECT * FROM patients;

@queryname:select_report_by_patient_id
SELECT * FROM reports
WHERE paziente == ?
ORDER BY data DESC;

@queryname:select_patient_by_id
SELECT * FROM patients 
WHERE id == ?;

@queryname:select_doctor_by_id
SELECT * FROM doctors
WHERE id == ?;


