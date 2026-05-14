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

def check_valid_dataset(dataset_name):
    dataset_path = Path(PT_datasets_dir) / dataset_name

    # controlla che il dataset esista
    if not dataset_path.exists():
        raise ValueError(f"Dataset '{dataset_name}' non disponibile")

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
    """
    from .datasets.OCTDL import get_patient_id

    # controlla la validità del dataset e degli split
    check_valid_dataset(dataset_name)
    check_valid_split(dataset_split)

    # ottiene il percorso del dataset specificato e le dimensioni degli split del dataset
    dataset_path = Path(PT_datasets_dir) / dataset_name
    train_sz, eval_sz, test_sz = dataset_split

    # carica il dataset utilizzando la libreria datasets di Hugging Face
    dataset = datasets.load_dataset("imagefolder", data_dir=str(dataset_path))
    dataset = dataset['train']  # estrae il split train

    # estrae i patient_id per ogni immagine
def extract_patient_id(example, idx):
    # HF imagefolder conserva il path qui
    file_path = example["image"].get("path", None)

    if file_path is None:
        raise ValueError("Path immagine non disponibile nel dataset")

    filename = Path(file_path).name
    example["patient_id"] = get_patient_id(filename)

    dataset = dataset.map(
    lambda ex, idx: extract_patient_id(ex, idx),
    with_indices=True,
    num_proc=NUM_PROC
    )
    
    return example

    

    
def set_seed(seed=DEFAULT_SEED):
    # imposta il seed di tutte le funzioni che usano
    # generazione pseudo-randomica
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False
