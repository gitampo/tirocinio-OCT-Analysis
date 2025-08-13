import torch
import random
import numpy as np
from pathlib import Path
from configs.paths import PT_checkpoints_dir
from . import AVAILABLE_MODELS, SEED

def available_models():
    return AVAILABLE_MODELS

def available_checkpoints():
    checkpoints = []
    
    # ottiene le cartelle relative ai modelli 
    model_directories = [file for file in Path(PT_checkpoints_dir).iterdir() if file.is_dir()]

    # per ogni modello, ottiene la lista di checkpoints e la salva nel formato "model/checkpoint"
    for model_dir in model_directories:
        checkpoints += [model_dir.stem+'/'+checkpoint_file.stem 
                        for checkpoint_file in model_dir.iterdir() 
                        if checkpoint_file.suffix in ('.pth','.pt')]

    return checkpoints

def get_checkpoint_from_name(checkpoint_name):

    # ottiene il nome del modello e il checkpoint
    model, checkpoint = checkpoint_name.split('/')

    # guardia per il modello
    if model not in [dir.stem for dir in Path(PT_checkpoints_dir).iterdir()]:
        raise ValueError(f"Modello '{model}' non disponibile")
    
    # cerca il file del checkpoint specificato
    checkpoint_file = None
    for file in (Path(PT_checkpoints_dir)/model).iterdir():
        if file.stem==checkpoint:
            checkpoint_file = file

    # guardia per il checkpoint
    if checkpoint_file is None:
        raise ValueError(f"Checkpoint '{checkpoint_name}' non disponibile")

    return checkpoint_file


def set_seed(seed=SEED):
    # imposta il seed di tutte le funzioni che usano
    # generazione pseudo-randomica
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False