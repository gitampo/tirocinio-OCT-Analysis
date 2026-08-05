import pandas as pd 
from pathlib import Path 
from configs.paths import PT_datasets_dir, find_octdl_dataset_root 

DATASET_NAME = 'OCTDL' 
LABELS_CSV = "OCTDL_labels.csv" 
labels = ['AMD','DME','ERM','NO','RAO','RVO','VID'] # l'ordine è importante 
IMAGE_EXTENSIONS = ('.png', '.jpg', '.jpeg')


def _discover_available_labels(dataset_root=None):
    if dataset_root is None:
        try:
            dataset_root = get_dataset_root()
        except FileNotFoundError:
            return list(labels)

    dataset_root = Path(dataset_root)
    if not dataset_root.exists():
        return list(labels)

    discovered = []
    for image_path in dataset_root.rglob('*'):
        if not image_path.is_file():
            continue
        if image_path.suffix.lower() not in IMAGE_EXTENSIONS:
            continue
        parent_name = image_path.parent.name
        if parent_name not in discovered:
            discovered.append(parent_name)

    if not discovered:
        return list(labels)

    ordered = [label for label in labels if label in discovered]
    ordered.extend([label for label in discovered if label not in ordered])
    return ordered


def get_task_labels(task_name='full', interest_classes=None, dataset_root=None):
    available_labels = _discover_available_labels(dataset_root=dataset_root)

    if task_name == 'full':
        return list(available_labels)

    if task_name == 'interest_vs_rest':
        if not interest_classes:
            raise ValueError("Per il task 'interest_vs_rest' servono le classi d'interesse")

        interest_classes = [str(class_name) for class_name in interest_classes]
        invalid_classes = [class_name for class_name in interest_classes if class_name not in available_labels]
        if invalid_classes:
            raise ValueError(f"Classi d'interesse non valide: {invalid_classes}")

        return interest_classes + ['ALL_REST']

    raise ValueError(f"Task '{task_name}' non supportato")


def id2label(id, task_name='full', interest_classes=None, dataset_root=None):
    return get_task_labels(task_name=task_name, interest_classes=interest_classes, dataset_root=dataset_root)[id]
 
def label2id(label, task_name='full', interest_classes=None, dataset_root=None):
    task_labels = get_task_labels(task_name=task_name, interest_classes=interest_classes, dataset_root=dataset_root)
    if task_name == 'interest_vs_rest':
        if interest_classes is not None and label in interest_classes:
            return interest_classes.index(label)
        return len(interest_classes or [])

    if label in task_labels:
        return task_labels.index(label)

    if dataset_root is not None:
        discovered_labels = _discover_available_labels(dataset_root=dataset_root)
        if label in discovered_labels:
            task_labels = discovered_labels
            return task_labels.index(label)

    # fallback conservativo: accetta etichette sconosciute come nuove classi
    task_labels = list(task_labels) + [label]
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