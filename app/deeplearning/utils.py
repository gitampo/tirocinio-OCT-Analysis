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
    root_path = Path(PT_datasets_dir)
    candidate_paths = [
        root_path / dataset_name,
        root_path / dataset_name.lower(),
    ]

    for candidate in candidate_paths:
        if candidate.exists():
            return candidate

    # Special case: OCTDL può essere fornito come directory radice del dataset Kaggle
    if dataset_name == 'OCTDL':
        # Se nella root esiste il CSV delle etichette, consideriamo la root come dataset root
        if (root_path / 'OCTDL_labels.csv').exists():
            return root_path

        # Se la root contiene le cartelle di classe del dataset OCTDL
        if root_path.exists() and any(child.is_dir() for child in root_path.iterdir()):
            return root_path

    raise ValueError(f"Dataset '{dataset_name}' non disponibile")


def check_valid_dataset(dataset_name):
    dataset_path = resolve_dataset_path(dataset_name)

    # controlla che il dataset-imagefolder contenga solo classi e non split (train/, test/, eval/) o che comunque non contenga file che non siano immagini
    dataset_classes = [file.stem for file in dataset_path.iterdir() if file.is_dir()]
    for dataset_class in dataset_classes:
        if not all(file.is_file() for file in (dataset_path/dataset_class).iterdir()):
            raise ValueError(f"La classe '{dataset_class}' del dataset '{dataset_name}' contiene elementi che non sono immagini."
                              "Ricorda: i dataset devono essere imagefolder contenenti cartelle per ogni classe.")

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
    dataset_path = Path(PT_datasets_dir) / dataset_name

    # carica il dataset utilizzando la libreria datasets di Hugging Face
    dataset = datasets.load_dataset("imagefolder", data_dir=str(dataset_path))

    return dataset

def load_splitted_dataset_from_name(dataset_name, dataset_split):
    """
    Carica il dataset con split a livello di paziente (anti-leakage).
    
    Raggruppa le immagini per patient_id e divide i gruppi di pazienti
    (non le singole immagini) in train/eval/test. Questo garantisce che
    nessun paziente appare in più split.
    
    Supporta sia OCTDL che OCT2017.
    """
    
    # Importa dinamicamente il modulo di dataset corretto per estrarre patient_id
    if dataset_name == 'OCTDL':
        from .datasets.OCTDL import get_patient_id, DATASET_NAME, LABELS_CSV
    elif dataset_name == 'OCT2017':
        from .datasets.OCT2017 import get_patient_id
    else:
        raise ValueError(f"Dataset '{dataset_name}' non supportato per lo split anti-leakage")

    # controlla la validità del dataset e degli split
    check_valid_dataset(dataset_name)
    check_valid_split(dataset_split)

    # ottiene il percorso del dataset specificato e le dimensioni degli split del dataset
    dataset_path = Path(PT_datasets_dir) / dataset_name
    train_sz, eval_sz, test_sz = dataset_split

    # carica il dataset utilizzando la libreria datasets di Hugging Face
    dataset = datasets.load_dataset("imagefolder", data_dir=str(dataset_path))
    dataset = dataset['train']  # estrae il split train

    # Per OCTDL, carica il CSV per una mappatura diretta file_name → patient_id
    if dataset_name == 'OCTDL':
        df_labels = pd.read_csv(dataset_path / LABELS_CSV)[["file_name", "patient_id"]]
        # Crea un dizionario per lookup veloce
        filename_to_patient = dict(zip(df_labels['file_name'], df_labels['patient_id'].astype(str)))
        
        # Estrai patient_id da ogni immagine basandosi sul CSV
        patient_ids_list = []
        for idx in range(len(dataset)):
            # Il CSV è ordinato come il dataset, quindi usa l'indice direttamente
            if idx < len(df_labels):
                patient_id = str(df_labels.iloc[idx]['patient_id'])
            else:
                patient_id = str(idx)  # Fallback
            patient_ids_list.append(patient_id)
    else:
        # Per OCT2017, estrai from class label (pseudo patient_id)
        # Usa il nome della classe come patient_id
        label_names = dataset.features['label'].names
        patient_ids_list = [label_names[example['label']] for example in dataset]
    
    # Aggiungi patient_id al dataset
    dataset = dataset.add_column('patient_id', patient_ids_list)

    # raggruppa per patient_id
    patient_indices = {}
    for idx in range(len(dataset)):
        pid = dataset[idx]['patient_id']
        if pid not in patient_indices:
            patient_indices[pid] = []
        patient_indices[pid].append(idx)

    # ottiene la lista unica di patient_id e la shuffla per riproducibilità
    patient_ids = list(patient_indices.keys())
    random.shuffle(patient_ids)

    # calcola i punti di split basati su patient_id
    num_patients = len(patient_ids)
    train_patient_count = int(num_patients * train_sz)
    eval_patient_count = int(num_patients * eval_sz)

    train_patient_ids = patient_ids[:train_patient_count]
    eval_patient_ids = patient_ids[train_patient_count:train_patient_count + eval_patient_count]
    test_patient_ids = patient_ids[train_patient_count + eval_patient_count:]

    # raccoglie gli indici delle immagini per ogni split
    train_indices = []
    eval_indices = []
    test_indices = []

    for pid in train_patient_ids:
        train_indices.extend(patient_indices[pid])
    for pid in eval_patient_ids:
        eval_indices.extend(patient_indices[pid])
    for pid in test_patient_ids:
        test_indices.extend(patient_indices[pid])

    # crea i dataset splits usando select
    train_dataset = dataset.select(train_indices)
    eval_dataset = dataset.select(eval_indices)
    test_dataset = dataset.select(test_indices)

    # rimuove la colonna patient_id (non serve più per il training)
    train_dataset = train_dataset.remove_columns(['patient_id'])
    eval_dataset = eval_dataset.remove_columns(['patient_id'])
    test_dataset = test_dataset.remove_columns(['patient_id'])

    # compone l'oggetto DatasetDict
    dataset = datasets.DatasetDict({
        'train': train_dataset,
        'eval': eval_dataset,
        'test': test_dataset
    })

    return dataset

def set_seed(seed=DEFAULT_SEED):
    # imposta il seed di tutte le funzioni che usano
    # generazione pseudo-randomica
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False
