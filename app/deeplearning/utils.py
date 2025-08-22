import torch
import random
import numpy as np
from pathlib import Path
from configs.paths import PT_datasets_dir, PT_checkpoints_dir
import datasets
from . import *

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

def load_dataset_from_name(dataset_name, dataset_split):
    
    # controlla la validità del dataset e degli split
    check_valid_dataset(dataset_name)
    check_valid_split(dataset_split)

    # ottiene il percorso del dataset specificato e le dimensioni degli split del dataset
    dataset_path = Path(PT_datasets_dir) / dataset_name
    train_sz, eval_sz, test_sz = dataset_split

    # carica il dataset utilizzando la libreria datasets di Hugging Face
    dataset = datasets.load_dataset("imagefolder", data_dir=str(dataset_path))
    dataset_1 = dataset['train'].train_test_split(test_size=eval_sz+test_sz)
    dataset_2 = dataset_1['test'].train_test_split(test_size=test_sz/(eval_sz+test_sz)) # calcola la percentuale relativa

    # compone l'oggetto DatasetDict
    dataset = datasets.DatasetDict({
        'train': dataset_1['train'],
        'eval': dataset_2['train'],
        'test': dataset_2['test']
    })

    return dataset

def set_seed(seed=SEED):
    # imposta il seed di tutte le funzioni che usano
    # generazione pseudo-randomica
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False