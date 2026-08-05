import pandas as pd 
from pathlib import Path 
from configs.paths import PT_datasets_dir, find_octdl_dataset_root 

DATASET_NAME = 'OCTDL' 
LABELS_CSV = "OCTDL_labels.csv" 
labels = ['AMD','DME','ERM','NO','RAO','RVO','VID'] # l'ordine è importante 


def get_task_labels(task_name='full', interest_classes=None):
    if task_name == 'full':
        return list(labels)

    if task_name == 'interest_vs_rest':
        if not interest_classes:
            raise ValueError("Per il task 'interest_vs_rest' servono le classi d'interesse")

        interest_classes = [str(class_name) for class_name in interest_classes]
        invalid_classes = [class_name for class_name in interest_classes if class_name not in labels]
        if invalid_classes:
            raise ValueError(f"Classi d'interesse non valide: {invalid_classes}")

        return interest_classes + ['ALL_REST']

    raise ValueError(f"Task '{task_name}' non supportato")


def id2label(id, task_name='full', interest_classes=None):
    return get_task_labels(task_name=task_name, interest_classes=interest_classes)[id]
 
def label2id(label, task_name='full', interest_classes=None):
    task_labels = get_task_labels(task_name=task_name, interest_classes=interest_classes)
    if task_name == 'interest_vs_rest':
        if label in interest_classes:
            return interest_classes.index(label)
        if label in labels:
            return len(interest_classes)
        raise ValueError(f"Etichetta '{label}' non supportata per il task '{task_name}'")
    return task_labels.index(label) 

def get_dataset_root():
    dataset_root = Path(PT_datasets_dir)
    candidate_paths = [
        dataset_root / DATASET_NAME,
        dataset_root / DATASET_NAME.lower(),
        dataset_root,
        Path('/kaggle/input') / DATASET_NAME,
        Path('/kaggle/input') / DATASET_NAME.lower(),
        Path('/kaggle/input') / 'datasets' / 'obulisainaren' / 'retinal-oct-c8',
        Path('/kaggle/input') / 'retinal-oct-c8',
        Path('/kaggle/working') / 'retinal-oct-c8',
    ]

    for candidate in candidate_paths:
        if candidate.exists():
            return candidate

    discovered = find_octdl_dataset_root([dataset_root, Path('/kaggle/input'), Path('/kaggle/working'), Path.cwd()])
    if discovered is not None:
        return discovered

    raise FileNotFoundError(f"Dataset root for '{DATASET_NAME}' non trovato in {PT_datasets_dir}")


def get_patient_id(image_name): 
    dataset_root = get_dataset_root()
    df = pd.read_csv(dataset_root / LABELS_CSV)[["file_name", "patient_id"]]
    
    patient_id = int(
        df[df["file_name"] == image_name]["patient_id"].values[0]
    )

    return patient_id