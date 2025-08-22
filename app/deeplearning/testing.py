import torch
from transformers import Trainer, TrainingArguments

from . import (
    DEFAULT_DATASET,
    DEFAULT_SPLIT,
    SEED,
    NUM_PROC,
    PREPROCESS_BATCH_SIZE,
    TEST_BATCH_SIZE
)
from .model_factory import load_model, get_preprocessor
from utils.print import (
    print_success_box, 
    print_separator,
    print_log
)
from .utils import ( 
    get_checkpoint_path,   
    load_dataset_from_name,      
    set_seed 
)            

# funzione di calcolo delle metriche di valutazione del modello
def test_compute_metrics(eval_pred):
    from sklearn.metrics import accuracy_score, balanced_accuracy_score
    logits, labels = eval_pred
    preds = logits.argmax(axis=-1)
    return {
        "accuracy": accuracy_score(labels, preds),
        "balanced_accuracy": balanced_accuracy_score(labels, preds)
    }

def test(model_name, checkpoint_name, dataset_name=DEFAULT_DATASET, dataset_split=DEFAULT_SPLIT):

    # impostazione del seed per riproducibilità
    set_seed(SEED)

    # caricamento del modello e del preprocess
    model = load_model(model_name)
    preprocessor = get_preprocessor(model_name)

    # caricamento del checkpoint
    print(f"Caricamento del checkpoint '{checkpoint_name}' per il modello '{model_name}'...")
    checkpoint = get_checkpoint_path(model_name, checkpoint_name)
    model.load_state_dict(torch.load(checkpoint, weights_only=True))

    # caricamento del dataset
    print_log(f"Caricamento del dataset '{dataset_name}'...")
    dataset = load_dataset_from_name(dataset_name, dataset_split)

    # preprocessing dei dati
    print_log("Preprocessing dei dati...")
    dataset = dataset.map(preprocessor, batched=True, batch_size=PREPROCESS_BATCH_SIZE, num_proc=NUM_PROC)
    
    # creazione del trainer
    trainer = Trainer(
        model=model,
        args=TrainingArguments(
            per_device_eval_batch_size=TEST_BATCH_SIZE, 
            do_train=False,
            do_eval=True),
        compute_metrics=test_compute_metrics,
    )

    # testing vero e proprio
    print_log("Inizio del testing...")
    metrics = trainer.evaluate(dataset['test'])
    print_success_box("Testing completato!")

    # stampa delle metriche
    print_separator(27)
    sorted_metrics = sorted(metrics.items())

    for metric, score in sorted_metrics:

        # rimuove il prefisso "eval " e sostituisce "_" con " "
        metric = metric.replace("_", " ").replace("eval ", "").capitalize()

        # se metric è "Accuracy" o "Balanced accuracy" stampa in percentuale
        if metric=="Accuracy" or metric=="Balanced accuracy": 
            print(f"{metric}: {score*100:.2f}%")
        else:
            print(f"{metric}: {score}")