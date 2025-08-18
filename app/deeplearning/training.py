from pathlib import Path
import torch
import datasets
from transformers import Trainer

from .utils import get_checkpoint_from_name
from .models import ViTMAE
from configs.paths import *
from . import *

def train(model, checkpoint_name=None):
    checkpoint_to_load = None

    # trova i checkpoints a partire dal nome (se inseriti)
    if checkpoint_name:
        checkpoint_to_load = get_checkpoint_from_name(checkpoint_name)

    # controlla se il modello scelto è disponibile
    if model not in AVAILABLE_MODELS:
        raise ValueError(f"Modello '{model}' non disponibile")

    # controllo sul tipo di modello
    if model == 'vitmae-light':
        train_vitmae(checkpoint_to_load, type='light')
    elif model == 'vitmae-heavy':
        train_vitmae(checkpoint_to_load, type='heavy')
    else:
        raise NotImplementedError(f"Training non implementato per il modello '{model}'")

def load_train_eval_datasets():
    # caricamento e shuffle del dataset
    dataset = datasets.load_dataset("imagefolder", data_dir=PT_testing_dataset_dir)
    dataset = dataset.shuffle(seed=42)

    # split del dataset
    dataset = dataset['train'].train_test_split(test_size=0.2)
    train_dataset = dataset['train']
    eval_dataset = dataset['test'].train_test_split(test_size=0.5)['test']

    # preprocessing dei dati
    train_dataset_preprocessed = train_dataset.map(ViTMAE.augment, batched=True, batch_size=4, num_proc=5)
    train_dataset_preprocessed = train_dataset.map(ViTMAE.preprocess_batch, batched=True, batch_size=4, num_proc=5)
    eval_dataset_preprocessed = eval_dataset.map(ViTMAE.preprocess_batch, batched=True, batch_size=4, num_proc=5)

    return train_dataset_preprocessed, eval_dataset_preprocessed

def train_vitmae(checkpoint_to_load=None, type='heavy'):

    # richiesta del nome del modello
    print("Dai un nome al modello: ", end="")
    model_name = input().strip()

    # caricamento dei dataset preprocessati
    train_dataset, eval_dataset = load_train_eval_datasets()

    # possibili tipi di vitmae
    heavy_model = ViTMAE.ViTMAEForImageClassification_heavy()
    light_model = ViTMAE.ViTMAEForImageClassification_light()

    # caricamento del modello
    model = heavy_model if type == 'heavy' else light_model
    if checkpoint_to_load and Path(checkpoint_to_load).exists():
        model.load_state_dict(torch.load(checkpoint_to_load))

    # configurazione del training
    trainer = Trainer(
        model=model,
        args=vitmae_training_args,
        train_dataset=train_dataset,
        eval_dataset=eval_dataset,
        compute_metrics=vitmae_compute_metrics,
        callbacks=vitmae_callbacks
    )

    # training vero e proprio
    trainer.train()

    # salvataggio del modello addestrato
    torch.save(trainer.model.state_dict(), Path(PT_checkpoints_dir) / f'vitmae-{type}' / (model_name + '.pth'))