from sklearn.metrics import (
    accuracy_score, 
    balanced_accuracy_score,
    recall_score,
    f1_score,
    matthews_corrcoef,
    confusion_matrix,
    precision_score,
)
import torch
from transformers import Trainer, TrainingArguments

from . import (
    DEFAULT_DATASET,
    DEFAULT_SPLIT,
    DEFAULT_SEED,
    NUM_PROC,
    PREPROCESS_BATCH_SIZE,
    TEST_BATCH_SIZE
)
from .model_factory import (
    load_model, 
    get_preprocessor, 
)
from utils.print import (
    humanized,
    formatted,
    print_separator,
    print_success_box, 
    print_info,
    print_table,
    print_confusion_matrix
)
from .utils import ( 
    get_checkpoint_path,   
    load_splitted_dataset_from_name,      
    set_seed 
)

# dizionario globale e altre variabili per le metriche
metrics = {  
    "accuracy":           {"format":".2f%", "fun":accuracy_score,          "kwargs":{}                     },
    "balanced_accuracy":  {"format":".2f%", "fun":balanced_accuracy_score, "kwargs":{}                     },
    "f1_score_micro":     {"format":".2f%", "fun":f1_score,                "kwargs":{"average":"micro"}    },
    "recall_micro":       {"format":".2f%", "fun":recall_score,            "kwargs":{"average":"micro"}    },
    "precision_micro":    {"format":".2f%", "fun":precision_score,         "kwargs":{"average":"micro"}    },
    "f1_score_macro":     {"format":".2f%", "fun":f1_score,                "kwargs":{"average":"macro"}    },
    "recall_macro":       {"format":".2f%", "fun":recall_score,            "kwargs":{"average":"macro"}    },
    "precision_macro":    {"format":".2f%", "fun":precision_score,         "kwargs":{"average":"macro"}    },
    "f1_score_weighted":  {"format":".2f%", "fun":f1_score,                "kwargs":{"average":"weighted"} },
    "recall_weighted":    {"format":".2f%", "fun":recall_score,            "kwargs":{"average":"weighted"} },
    "precision_weighted": {"format":".2f%", "fun":precision_score,         "kwargs":{"average":"weighted"} },
    "MCC":                {"format":".3f" , "fun":matthews_corrcoef,       "kwargs":{}                     },
    "confusion_matrix":   {"format":None  , "fun":confusion_matrix,        "kwargs":{}                     },
}
metrics_names = metrics.keys()
metrics_formats = {metric: metrics[metric]['format'] for metric in metrics}

# funzione di calcolo delle metriche di valutazione del modello
def compute_metrics_for_test(eval_pred):
    global metrics

    # funzione di calcolo di una singola metrica
    def compute_metric(metric, labels, preds):
        global metrics
        return metrics[metric]["fun"](labels, preds, **metrics[metric]["kwargs"])

    # calcolo delle predizioni
    logits, labels = eval_pred
    preds = logits.argmax(axis=-1)

    # calcolo delle metriche
    computed_metrics = {metric: compute_metric(metric, labels, preds) for metric in metrics}
    return computed_metrics

def load_for_test(model_name, checkpoint_name, dataset_name, dataset_split):
    # caricamento del modello e del preprocess
    model = load_model(model_name)
    preprocessor = get_preprocessor(model_name)

    # caricamento del checkpoint
    print_info(f"Caricamento del checkpoint '{checkpoint_name}' per il modello '{model_name}'...")
    checkpoint = get_checkpoint_path(model_name, checkpoint_name)
    model.load_state_dict(torch.load(checkpoint, weights_only=True))

    # caricamento del dataset
    print_info(f"Caricamento del dataset '{dataset_name}'...")
    dataset = load_splitted_dataset_from_name(dataset_name, dataset_split)

    # preprocessing dei dati
    print_info("Preprocessing dei dati...")
    dataset = dataset.map(preprocessor, batched=True, batch_size=PREPROCESS_BATCH_SIZE, num_proc=NUM_PROC)

    # creazione delle etichette
    labels = dataset['train'].features['label'].names

    return model, dataset, labels

def preprocess_results(output):
    # rimuove il prefisso 'eval_' dai nomi delle metriche
    output = {k.replace('eval_',''):v for k,v in sorted(output.items())}

    # ottiene (pop) la matrice di confusione dai risultati
    confusion_matrix = output.pop('confusion_matrix', None)

    # ottiene coppie (metrica, valore) e (statistica, valore) per metriche e statistiche calcolate
    # N.B. distingue metriche e statistiche dipendentemente dal fatto che i nomi siano in metrics_names
    computed_metrics = [(k,v) for k,v in output.items() if k in metrics_names]
    computed_stats = [(k,v) for k,v in output.items() if k not in metrics_names]

    # lavora le metriche per ottenere valori ben formattati per la stampa
    metrics_rows = [(m,v,metrics_formats[m]) for m,v in computed_metrics]
    metrics_rows = [(humanized(m),formatted(v,f)) for m,v,f in metrics_rows]
    metrics_rows = sorted(metrics_rows)

    # lavora le statistiche per ottenere valori ben formattati per la stampa
    stats_rows = [(humanized(s),v) for s,v in sorted(computed_stats)]

    return confusion_matrix, metrics_rows, stats_rows

def print_results(output, model_name, labels):

    # preprocessing dei risultati (formattazione e cambio rappresentazione)
    confusion_matrix, \
    metrics_rows,     \
    stats_rows = preprocess_results(output)

    # stampa di matrice di confusione
    print("\n MATRICE DI CONFUSIONE \n (predizioni a lato; verità sopra):\n")
    print_confusion_matrix(confusion_matrix, labels=labels)
    print_separator(end="\n\n")

    # stampa della tabella delle metriche
    print_table(headings=["METRICA", "VALORE"], rows=metrics_rows)
    print_separator(end="\n\n")

    # stampa della tabella delle statistiche
    print_table(headings=["STATISTICA", "VALORE"], rows=stats_rows)

def test(model_name, checkpoint_name, dataset_name=DEFAULT_DATASET, dataset_split=DEFAULT_SPLIT, seed=DEFAULT_SEED):

    # impostazione del seed per riproducibilità
    set_seed(seed)

    # caricamento del modello e del dataset
    model, dataset, labels = load_for_test(model_name, checkpoint_name,
                                           dataset_name, dataset_split)

    # creazione del trainer
    trainer = Trainer(
        model=model,
        args=TrainingArguments(
            per_device_eval_batch_size=TEST_BATCH_SIZE, 
            do_train=False,
            do_eval=True),
        compute_metrics=compute_metrics_for_test,
    )

    # testing vero e proprio
    print_info("Inizio del testing...")
    output = trainer.evaluate(dataset['test'])
    print_success_box("Testing completato!")

    # stampa dei risultati
    print_results(output, model_name, labels)