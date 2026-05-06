from pathlib import Path
from configs.paths import PT_datasets_dir

DATASET_NAME = 'OCT2017 '

labels = ['CNV', 'DME', 'DRUSEN', 'NORMAL']

def id2label(id):
    return labels[id]

def label2id(label):
    return labels.index(label)

def get_patient_id(image_name):
    # nel dataset Kaggle non esistono patient_id
    # usiamo il nome immagine come identificativo univoco
    return image_name