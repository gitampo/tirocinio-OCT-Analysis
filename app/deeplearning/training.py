from pathlib import Path
import torch
import datasets
from transformers import Trainer

from .utils import get_checkpoint_from_name
from .models import ViTMAE
from configs.paths import *
from . import AVAILABLE_MODELS, vitmae_training_args

def train(model, checkpoint_name=None):
    checkpoint_to_load = None

    # trova i checkpoints a partire dal nome (se inseriti)
    if checkpoint_name:
        checkpoint_to_load = get_checkpoint_from_name(checkpoint_name)

    # controlla se il modello scelto è disponibile
    if model not in AVAILABLE_MODELS:
        raise ValueError(f"Modello '{model}' non disponibile")

    # controllo sul tipo di modello
    if model == 'vitmae':
        train_vitmae(checkpoint_to_load)
    else:
        raise NotImplementedError(f"Training non implementato per il modello '{model}'")

def load_train_eval_datasets():
    # caricamento e shuffle del dataset
    dataset = datasets.load_dataset("imagefolder", data_dir=PT_testing_dataset_dir)
    dataset = dataset.shuffle(seed=42)

    # split del dataset
    dataset = dataset['train'].train_test_split(test_size=0.9)
    train_dataset = dataset['train']
    eval_dataset = dataset['test'].train_test_split(test_size=0.5)['test']

    # preprocessing dei dati
    train_dataset_preprocessed = train_dataset.map(ViTMAE.preprocess_batch, batched=True, batch_size=4, num_proc=5)
    eval_dataset_preprocessed = eval_dataset.map(ViTMAE.preprocess_batch, batched=True, batch_size=4, num_proc=5)

    return train_dataset_preprocessed, eval_dataset_preprocessed

def train_vitmae(checkpoint_to_load=None):

    # richiesta del nome del modello
    print("Dai un nome al modello: vitmae-", end="")
    model_name = 'vitmae-' + input().strip()

    # caricamento dei dataset preprocessati
    train_dataset, eval_dataset = load_train_eval_datasets()

    # caricamento del modello
    model = ViTMAE.ViTMAEForImageClassification()
    if checkpoint_to_load and Path(checkpoint_to_load).exists():
        model.load_state_dict(torch.load(checkpoint_to_load))

    # configurazione del training
    trainer = Trainer(
        model=model,
        args=vitmae_training_args,
        train_dataset=train_dataset,
        eval_dataset=eval_dataset
    )

    # training vero e proprio
    trainer.train()

    # salvataggio del modello addestrato
    torch.save(trainer.model.state_dict(), Path(PT_checkpoints_dir) / 'vitmae' / (model_name + '.pth'))