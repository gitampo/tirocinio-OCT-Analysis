from pathlib import Path
from collections import Counter
import pandas as pd
import numpy as np
import datasets
import random
import torch
from sklearn.model_selection import StratifiedShuffleSplit

from . import *
from configs.paths import (
    PT_datasets_dir, 
    PT_checkpoints_dir, 
    PT_trainer_output_dir,
    find_octdl_dataset_root,
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
        dataset_root,
        Path('/kaggle/input') / dataset_name,
        Path('/kaggle/input') / dataset_name.lower(),
        Path('/kaggle/input') / 'octdl',
        Path('/kaggle/input') / 'octdl-optical-coherence-tomography-dataset',
        Path('/kaggle/input') / 'datasets' / 'orvile' / 'octdl-optical-coherence-tomography-dataset',
        Path('/kaggle/input') / 'datasets' / 'obulisainaren' / 'retinal-oct-c8',
        Path('/kaggle/input') / 'retinal-oct-c8',
        Path('/kaggle/input') / 'datasets' / 'obulisainaren' / 'retinal-oct-c8' / 'retinal-oct-c8',
        Path('/kaggle/working') / 'retinal-oct-c8',
    ]

    for candidate in candidate_paths:
        if candidate.exists():
            return candidate

    discovered = find_octdl_dataset_root([dataset_root, Path('/kaggle/input'), Path('/kaggle/working'), Path.cwd()])
    if discovered is not None:
        return discovered

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


def _build_splitted_dataset_from_files(dataset_path, dataset_name, task_name='full', interest_classes=None):
    image_extensions = [".png", ".jpg", ".jpeg"]
    image_paths = []
    for ext in image_extensions:
        image_paths.extend(sorted(dataset_path.rglob(f"*{ext}")))

    if len(image_paths) == 0:
        raise ValueError(f"Dataset '{dataset_name}' non contiene immagini valide")

    if dataset_name == 'OCTDL':
        from .datasets.OCTDL import get_patient_id, LABELS_CSV, get_task_labels
        df_labels = pd.read_csv(dataset_path / LABELS_CSV)[["file_name", "patient_id"]]
        filename_to_patient = dict(zip(df_labels['file_name'], df_labels['patient_id'].astype(str)))
        label_names = get_task_labels(task_name=task_name, interest_classes=interest_classes)
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
        if dataset_name == 'OCTDL' and task_name == 'interest_vs_rest':
            if label_name not in ['AMD','DME','ERM','NO','RAO','RVO','VID']:
                raise ValueError(f"Etichetta '{label_name}' non valida per il dataset '{dataset_name}'")
        elif label_name not in label_names:
            raise ValueError(f"Etichetta '{label_name}' non valida per il dataset '{dataset_name}'")

        if dataset_name == 'OCTDL':
            patient_id = filename_to_patient.get(image_path.stem)
            if patient_id is None:
                raise ValueError(f"Patient ID non trovato per il file '{image_path.name}' (stem={image_path.stem})")
        else:
            patient_id = str(get_patient_id(image_path.stem))

        examples['image'].append(str(image_path))
        if dataset_name == 'OCTDL':
            from .datasets.OCTDL import label2id
            examples['label'].append(label2id(label_name, task_name=task_name, interest_classes=interest_classes))
        else:
            examples['label'].append(label_names.index(label_name))
        examples['patient_id'].append(str(patient_id))

    features = datasets.Features({
        'image': datasets.Image(),
        'label': datasets.ClassLabel(names=label_names),
        'patient_id': datasets.Value('string')
    })

    dataset = datasets.Dataset.from_dict(examples, features=features)
    return dataset


def _get_patient_majority_labels(dataset):
    patient_labels = {}
    for example in dataset:
        pid = example['patient_id']
        patient_labels.setdefault(pid, []).append(example['label'])

    return {
        pid: Counter(labels).most_common(1)[0][0]
        for pid, labels in patient_labels.items()
    }


def _stratified_patient_split(patient_ids, patient_labels, test_size, seed):
    if test_size <= 0 or len(patient_ids) == 0:
        return np.arange(len(patient_ids)), np.array([], dtype=patient_ids.dtype)

    try:
        splitter = StratifiedShuffleSplit(n_splits=1, test_size=test_size, random_state=seed)
        train_idx, test_idx = next(splitter.split(patient_ids, patient_labels))
        return train_idx, test_idx
    except ValueError:
        rng = np.random.default_rng(seed)
        perm = rng.permutation(len(patient_ids))
        split = int(np.round(len(patient_ids) * test_size))
        return perm[split:], perm[:split]


def load_splitted_dataset_from_name(dataset_name, dataset_split, seed=DEFAULT_SEED, task_name='full', interest_classes=None):
    """
    Carica il dataset con split a livello di paziente (anti-leakage).
    
    Raggruppa le immagini per patient_id e divide i gruppi di pazienti
    (non le singole immagini) in train/eval/test. Questo garantisce che
    nessun paziente appare in più split e mantiene la distribuzione delle
    classi con una stratificazione basata sul label di paziente.
    """
    if dataset_name not in ['OCTDL', 'OCT2017']:
        raise ValueError(f"Dataset '{dataset_name}' non supportato per lo split anti-leakage")

    check_valid_dataset(dataset_name)
    check_valid_split(dataset_split)

    dataset_path = resolve_dataset_path(dataset_name)
    train_sz, eval_sz, test_sz = dataset_split

    dataset = _build_splitted_dataset_from_files(dataset_path, dataset_name, task_name=task_name, interest_classes=interest_classes)

    # raggruppa per patient_id
    patient_indices = {}
    for idx, example in enumerate(dataset):
        pid = example['patient_id']
        patient_indices.setdefault(pid, []).append(idx)

    patient_majority_labels = _get_patient_majority_labels(dataset)
    patient_ids = np.array(list(patient_majority_labels.keys()))
    patient_labels = np.array(list(patient_majority_labels.values()))

    # Stratified split per paziente per mantenere la distribuzione delle classi
    trainval_idx, test_idx = _stratified_patient_split(patient_ids, patient_labels, test_sz, seed)
    trainval_patient_ids = patient_ids[trainval_idx]
    trainval_patient_labels = patient_labels[trainval_idx]
    test_patient_ids = patient_ids[test_idx]

    if eval_sz > 0:
        relative_eval_size = eval_sz / (train_sz + eval_sz)
        train_idx, eval_idx = _stratified_patient_split(trainval_patient_ids, trainval_patient_labels, relative_eval_size, seed)
        train_patient_ids = trainval_patient_ids[train_idx]
        eval_patient_ids = trainval_patient_ids[eval_idx]
    else:
        train_patient_ids = trainval_patient_ids
        eval_patient_ids = np.array([], dtype=trainval_patient_ids.dtype)

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


    

    
def attach_image_transform(dataset, preprocessor):
    """Attach an on-the-fly image preprocessing transform to a dataset."""
    def transform(batch):
        images = batch['image']
        if len(images) > 0 and isinstance(images[0], list):
            images = images[0]
        processed = preprocessor({'image': images})
        return {
            'pixel_values': processed['pixel_values'],
            'label': batch['label']
        }

    return dataset.with_transform(transform)


def set_seed(seed=DEFAULT_SEED):
    # imposta il seed di tutte le funzioni che usano
    # generazione pseudo-randomica
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False
