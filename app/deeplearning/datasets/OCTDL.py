import pandas as pd
from pathlib import Path
from configs.paths import PT_datasets_dir

DATASET_NAME = 'OCTDL'
LABELS_CSV = "OCTDL_labels.csv"

labels = ['AMD','DME','ERM','NO','RAO','RVO','VID'] # l'ordine è importante

def id2label(id):
    return labels[id]

def label2id(label):
    return labels.index(label)

def get_patient_id(image_name):

    # 1) dato il path completo al dataset OCTDL, 2) ottiene il dataframe con filename e patient-id
    # e 3) ottiene il patient-id corrispondente all'immagine
    path_to_dataset = Path(PT_datasets_dir) / DATASET_NAME
    df = pd.read_csv(path_to_dataset / LABELS_CSV)[["file_name", "patient_id"]]
    patient_id = int(df[df["file_name"] == image_name]["patient_id"].values[0])

    return patient_id