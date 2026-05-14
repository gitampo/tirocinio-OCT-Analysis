from pathlib import Path
import pandas as pd
import numpy as np
import datasets
import random
import torch

from . import *
from configs.paths import (
    PT_datasets_dir, 
    PT_checkpoints_dir, 
    PT_trainer_output_dir
)

def check_valid_split(dataset_split):
    train_sz, eval_sz, test_sz = dataset_split

    # controlla che gli split ammontino a 1
    if train_sz + eval_sz + test_sz != 1:
        raise ValueError(f"Dataset split '{dataset_split}' non valido: gli split devono sommare a 1")
    
    # controlla che gli split siano non negativi
    if train_sz < 0 or eval_sz < 0 or test_sz < 0:
        raise ValueError(f"Dataset split '{dataset_split}' non valido: gli split devono essere non negativi")

def resolve_dataset_path(dataset_name):
    dataset_root = Path(PT_datasets_dir)
    candidate_paths = [
        dataset_root / dataset_name,
        dataset_root / dataset_name.lower(),
        dataset_root
    ]

    for candidate in candidate_paths:
        if candidate.exists():
            return candidate

    raise ValueError(f"Dataset '{dataset_name}' non disponibile")


def check_valid_dataset(dataset_name):
    dataset_path = resolve_dataset_path(dataset_name)

    # cerca tutte le immagini ricorsivamente
    image_extensions = [".png", ".jpg", ".jpeg"]

    images = []
    for ext in image_extensions:
        images.extend(dataset_path.rglob(f"*{ext}"))

    # se non trova immagini -> errore
    if len(images) == 0:
        raise ValueError(
            f"Dataset '{dataset_name}' non contiene immagini valide"
        )

    print(f"[DEBUG] Trovate {len(images)} immagini nel dataset '{dataset_name}'")

def get_checkpoint_path(model_name, checkpoint_name):

    # guardia per il modello (deve esistere una cartella)
    if model_name not in [dir.stem for dir in Path(PT_checkpoints_dir).iterdir()]:
        raise ValueError(f"Checkpoint '{model_name}/{checkpoint_name}' non disponibile")

    # cerca il file del checkpoint specificato
    checkpoint_path = None
    for file in (Path(PT_checkpoints_dir)/model_name).iterdir():
        checkpoint_path = file if (file.stem==checkpoint_name) else checkpoint_path

    # guardia per il checkpoint
    if checkpoint_path is None:
        raise ValueError(f"Checkpoint '{model_name}/{checkpoint_name}' non disponibile")

    return checkpoint_path

def load_dataset_from_name(dataset_name):

    # controlla la validità del dataset
    check_valid_dataset(dataset_name)

    # ottiene il percorso del dataset specificato
    dataset_path = resolve_dataset_path(dataset_name)

    # carica il dataset utilizzando la libreria datasets di Hugging Face
    dataset = datasets.load_dataset("imagefolder", data_dir=str(dataset_path))

    return dataset


def _build_splitted_dataset_from_files(dataset_path, dataset_name):
    image_extensions = [".png", ".jpg", ".jpeg"]
    image_paths = []
    for ext in image_extensions:
        image_paths.extend(sorted(dataset_path.rglob(f"*{ext}")))

    if len(image_paths) == 0:
        raise ValueError(f"Dataset '{dataset_name}' non contiene immagini valide")

    if dataset_name == 'OCTDL':
        from .datasets.OCTDL import get_patient_id, LABELS_CSV, labels as label_names
        df_labels = pd.read_csv(dataset_path / LABELS_CSV)[["file_name", "patient_id"]]
        filename_to_patient = dict(zip(df_labels['file_name'], df_labels['patient_id'].astype(str)))
    elif dataset_name == 'OCT2017':
        from .datasets.OCT2017 import get_patient_id, labels as label_names
    else:
        raise ValueError(f"Dataset '{dataset_name}' non supportato per lo split anti-leakage")

    examples = {
        'image': [],
        'label': [],
        'patient_id': [],
    }

    for image_path in image_paths:
        label_name = image_path.parent.name
        if label_name not in label_names:
            raise ValueError(f"Etichetta '{label_name}' non valida per il dataset '{dataset_name}'")

        if dataset_name == 'OCTDL':
            patient_id = filename_to_patient.get(image_path.name)
            if patient_id is None:
                raise ValueError(f"Patient ID non trovato per il file '{image_path.name}'")
        else:
            patient_id = str(get_patient_id(image_path.stem))

        examples['image'].append(str(image_path))
        examples['label'].append(label_names.index(label_name))
        examples['patient_id'].append(str(patient_id))

    features = datasets.Features({
        'image': datasets.Image(),
        'label': datasets.ClassLabel(names=label_names),
        'patient_id': datasets.Value('string')
    })

    dataset = datasets.Dataset.from_dict(examples, features=features)
    return dataset


def load_splitted_dataset_from_name(dataset_name, dataset_split):
    """
    Carica il dataset con split a livello di paziente (anti-leakage).
    
    Raggruppa le immagini per patient_id e divide i gruppi di pazienti
    (non le singole immagini) in train/eval/test. Questo garantisce che
    nessun paziente appare in più split.
    """
    if dataset_name not in ['OCTDL', 'OCT2017']:
        raise ValueError(f"Dataset '{dataset_name}' non supportato per lo split anti-leakage")

    check_valid_dataset(dataset_name)
    check_valid_split(dataset_split)

    dataset_path = resolve_dataset_path(dataset_name)
    train_sz, eval_sz, test_sz = dataset_split

    dataset = _build_splitted_dataset_from_files(dataset_path, dataset_name)

    # raggruppa per patient_id
    patient_indices = {}
    for idx, example in enumerate(dataset):
        pid = example['patient_id']
        patient_indices.setdefault(pid, []).append(idx)

    patient_ids = list(patient_indices.keys())
    random.shuffle(patient_ids)

    num_patients = len(patient_ids)
    train_patient_count = int(num_patients * train_sz)
    eval_patient_count = int(num_patients * eval_sz)

    train_patient_ids = patient_ids[:train_patient_count]
    eval_patient_ids = patient_ids[train_patient_count:train_patient_count + eval_patient_count]
    test_patient_ids = patient_ids[train_patient_count + eval_patient_count:]

    train_indices = []
    eval_indices = []
    test_indices = []

    for pid in train_patient_ids:
        train_indices.extend(patient_indices[pid])
    for pid in eval_patient_ids:
        eval_indices.extend(patient_indices[pid])
    for pid in test_patient_ids:
        test_indices.extend(patient_indices[pid])

    train_dataset = dataset.select(train_indices).remove_columns(['patient_id'])
    eval_dataset = dataset.select(eval_indices).remove_columns(['patient_id'])
    test_dataset = dataset.select(test_indices).remove_columns(['patient_id'])

    return datasets.DatasetDict({
        'train': train_dataset,
        'eval': eval_dataset,
        'test': test_dataset
    })


    

    
def set_seed(seed=DEFAULT_SEED):
    # imposta il seed di tutte le funzioni che usano
    # generazione pseudo-randomica
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False
