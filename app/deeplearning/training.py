import torch
from transformers import Trainer
from pathlib import Path
import re

from . import (
    DEFAULT_DATASET,
    DEFAULT_SPLIT,
    NUM_PROC,
    PREPROCESS_BATCH_SIZE,
)
from .model_factory import load_training_args, load_model
from configs.paths import PT_checkpoints_dir
from utils.print import (
    print_separator, 
    print_warning, 
    print_success, 
    print_log,
    print_success_box
)
from .utils import (
    get_checkpoint_path,
    load_dataset_from_name
)


def ask_checkpoint_name(model_name):
    # dichiarazione variabili per il salvataggio del checkpoint
    new_checkpoint_name = ''
    new_checkpoint_path = ''
    continue_checking = True
    wants_to_overwrite = False

    # ciclo di controllo sulla scelta del nome del checkpoint
    while continue_checking:
        # chiede il nome del nuovo checkpoint
        print_separator()
        print("Come chiami il checkpoint in cui salvare l'allenamento?")
        print("Nome del nuovo checkpoint: "+ f" {model_name}/", end="")
        user_input = input().strip()

        # costruzione del nome e del percorso del checkpoint
        new_checkpoint_name = f"{model_name}/{user_input}"
        new_checkpoint_path = Path(PT_checkpoints_dir) / (new_checkpoint_name + '.pth')

        # controlla che il nome del checkpoint sia valido
        if not re.match(r'^[a-zA-Z0-9_-]+$', user_input):
            print_warning("Nome del checkpoint non valido. Caratteri ammessi: [a-zA-Z0-9_-]")
            print_warning("Riprova (INVIO)...", end="")
            input()
            continue

        # controlla se il checkpoint esiste già
        if new_checkpoint_path in (Path(PT_checkpoints_dir) / model_name).iterdir():
            print_warning("Esiste già un checkpoint con questo nome.")
            print_warning("Vuoi sovrascriverlo? (s/n): ", end="")
            overwrite_answer = input().strip().lower()

            # termina il controllo e sovrascrive il checkpoint
            if overwrite_answer == 's':
                wants_to_overwrite = True
                continue_checking = False
        else: 
            continue_checking = False
    print_separator()

    return new_checkpoint_name, new_checkpoint_path, wants_to_overwrite

def train(model_name, checkpoint_name=None, dataset_name=DEFAULT_DATASET, dataset_split=DEFAULT_SPLIT, from_scratch=True):
    
    # caricamento del modello e degli argomenti di training
    model = load_model(model_name)

    # caricamento degli argomenti di training
    training_args,   \
    compute_metrics, \
    callbacks,       \
    train_preprocess = load_training_args(model_name)

    # caricamento del checkpoint
    if (checkpoint_name) and (not from_scratch):
        print(f"Caricamento del checkpoint '{checkpoint_name}' per il modello '{model_name}'...")
        checkpoint_path = get_checkpoint_path(model_name, checkpoint_name)
        model.load_state_dict(torch.load(checkpoint_path, weights_only=True))
    elif (not checkpoint_name) and (not from_scratch):
        raise ValueError("Nessun checkpoint da caricare e non si sta addestrando da zero.")
    elif from_scratch:
        pass # TODO: inizializzare i pesi, ViTMAE non ne ha bisogno perché è pretrained

    # caricamento del dataset
    print_log(f"Caricamento del dataset '{dataset_name}'...")
    dataset = load_dataset_from_name(dataset_name, dataset_split)

    # preprocessing dei dati
    print_log("Preprocessing dei dati...")
    dataset = dataset.map(train_preprocess, batched=True, batch_size=PREPROCESS_BATCH_SIZE, num_proc=NUM_PROC)

    # creazione del trainer
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=dataset['train'],
        eval_dataset=dataset['eval'],
        compute_metrics=compute_metrics,
        callbacks=callbacks
    )

    # training vero e proprio
    print_log("Inizio del training...")
    trainer.train()
    print_success_box("Training completato!")

    # ottiene il nome da dare al checkpoint
    new_checkpoint_name, \
    new_checkpoint_path, \
    wants_to_overwrite = ask_checkpoint_name(model_name)

    # salvataggio del checkpoint
    message = "Sovrascrittura del checkpoint..." if wants_to_overwrite else "Salvataggio del nuovo checkpoint..."
    print_log(message)
    torch.save(trainer.model.state_dict(), new_checkpoint_path) # salvataggio del modello addestrato
    print_success(f"Checkpoint salvato come: {new_checkpoint_name}")