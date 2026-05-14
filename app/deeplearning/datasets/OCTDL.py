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

def get_dataset_root():
    dataset_root = Path(PT_datasets_dir)
    candidate_paths = [
        dataset_root / DATASET_NAME,
        dataset_root / DATASET_NAME.lower(),
        dataset_root,
    ]

    for candidate in candidate_paths:
        if candidate.exists():
            return candidate

    raise FileNotFoundError(f"Dataset root for '{DATASET_NAME}' non trovato in {PT_datasets_dir}")


def get_patient_id(image_name): 
    dataset_root = get_dataset_root()
    df = pd.read_csv(dataset_root / LABELS_CSV)[["file_name", "patient_id"]]
    
    patient_id = int(
        df[df["file_name"] == image_name]["patient_id"].values[0]
    )

    return patient_id