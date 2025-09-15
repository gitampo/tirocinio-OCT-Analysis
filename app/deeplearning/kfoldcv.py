import numpy as np
from torch.utils.data import Dataset, Subset
from transformers import Trainer, TrainingArguments
from pathlib import Path
from PIL import Image
from sklearn.model_selection import GroupKFold
from contextlib import contextmanager

from utils.funs import get_available_filename
from utils.log import log_print
from configs.paths import PT_datasets_dir, PT_log_dir
from utils.print import formatted, humanized, print_info, print_separator, print_success_box, print_table
from .training import load_training_args
from .datasets import OCTDL
from .training import set_seed, load_training_args
from .testing import (
    compute_metrics_for_test, 
    print_results,
    metrics_names,
    metrics_formats
)
from .model_factory import (
    load_model, 
    get_preprocessor, 
    get_augmenter
)
from . import DEFAULT_KFOLDS, DEFAULT_SEED, TEST_BATCH_SIZE

class KFoldDataset(Dataset):
    def __init__(self, model_name):
        
        # otteniene il preprocessore delle immagini
        self.preprocessor = get_preprocessor(model_name)
        self.augmenter = get_augmenter(model_name)
        self.augmentation_enabled = True # per abilitare/disabilitare l'augmentation

        # path completo sino al dataset
        path_to_dataset = Path(PT_datasets_dir) / OCTDL.DATASET_NAME

        # lista di tutti i path delle immagini
        self.image_paths = (
            list(path_to_dataset.rglob("*.png")) +
            list(path_to_dataset.rglob("*.jpg")) +
            list(path_to_dataset.rglob("*.jpeg"))
        )

        # verifica che siano state trovate immagini
        if not self.image_paths:
            raise ValueError(f"Nessuna immagine trovata in {path_to_dataset}")

        # elementi del dataset (etichette e pazienti corrispondenti alle immagini)
        self.labels = [OCTDL.label2id(self.image_paths[idx].parent.name) for idx in range(len(self.image_paths))]
        self.patients = [OCTDL.get_patient_id(self.image_paths[idx].stem) for idx in range(len(self.image_paths))]

        # indici casuali per il rimescolamento del dataset
        self.num_examples = len(self.image_paths)
        indices = np.random.permutation(self.num_examples)
        
        # rimescolamento del dataset
        self.image_paths = np.array(self.image_paths)[indices]
        self.labels = np.array(self.labels)[indices]
        self.patients = np.array(self.patients)[indices]

    def __len__(self):
        return len(self.image_paths)

    def __getitem__(self, idx):
        # caricamento dell'immagine
        try:
            image = Image.open(self.image_paths[idx]).convert("RGB")
        except Exception as e:
            print(f"Errore nel caricamento dell'immagine {self.image_paths[idx]}: {e}")
            image = Image.new("RGB", (224, 224))  # crea una dummy image

        # applicazione dell'augmentation (se abilitata)
        if self.augmentation_enabled: 
            image = self.augmenter({"image": [image]})
        else: 
            image = {"image": [image]}

        # preprocessing dell'immagine
        image = self.preprocessor(image)["pixel_values"].squeeze()
        label = self.labels[idx]

        return {"pixel_values": image, "labels": label}
    
    @contextmanager
    def eval_mode(self):
        # Codice eseguito all'ingresso del blocco 'with'
        self.augmentation_enabled = False
        try:
            yield  # esecuzione del blocco 'with'
        finally:
            # Codice eseguito all'uscita dal blocco 'with', anche in caso di eccezioni
            self.augmentation_enabled = True

class KFoldModelWrapper():
    def __init__(self, model_name):
        self.model_name = model_name
        self.model = None

    def fit(self, train_dataset):

        # caricamento del modello e degli argomenti di training
        self.model = load_model(self.model_name)
        training_args = load_training_args()
        training_args.do_eval = False
        training_args.eval_strategy = "no"

        # creazione del trainer
        trainer = Trainer(
            model=self.model,
            args=training_args,
            train_dataset=train_dataset
        )

        # training vero e proprio
        print_info("Inizio del training...")
        trainer.train()

    def score(self, val_dataset):
        import tempfile

        # creazione del trainer
        trainer = Trainer(
            model=self.model,
            args=TrainingArguments(
                output_dir=tempfile.mkdtemp(),
                per_device_eval_batch_size=TEST_BATCH_SIZE,
                do_train=False,
                do_eval=True,
            ),
            compute_metrics=compute_metrics_for_test,
        )

        # valutazione sul validation set
        print_info("Inizio della valutazione...")
        output = trainer.evaluate(val_dataset)

        return output

def preprocess_final_results(outputs):

    # calcolo della media delle metriche sui vari fold
    averaged_metrics = []
    for key in outputs[0].keys():
        metric_name = key.replace('eval_','')
        if metric_name not in metrics_names: continue

        mean = np.mean([output[key] for output in outputs]).item()
        dev_std = np.std([output[key] for output in outputs]).item()

        averaged_metrics.append((
            humanized(metric_name),
            formatted(mean, metrics_formats[metric_name]),
            formatted(dev_std, metrics_formats[metric_name]), 
        ))

    return sorted(averaged_metrics)

def print_final_results(outputs):

    # preprocessing dei risultati (formattazione e cambio rappresentazione) e stampa
    metrics_rows = preprocess_final_results(outputs)
    print_table(headings=["METRICA", "VALORE MEDIO", "DEV.STD."], rows=metrics_rows)

def kfold_cv(model_name, num_folds=DEFAULT_KFOLDS, seed=DEFAULT_SEED):
    log_file = "kfoldcv.log"
    log_file =get_available_filename(PT_log_dir, log_file)

    # impostazione del seed per la ripoducibilità
    set_seed(seed)

    # istanziazione delle K-fold (GroupKFold per evitare data leakage tra pazienti)
    gkf = GroupKFold(n_splits=num_folds)

    # caricamento del dataset e gruppi (pazienti)
    dataset = KFoldDataset(model_name)

    # K-fold cross validation 
    fold_idx = 1
    outputs = []
    for train_idx, val_idx in gkf.split(X=dataset.image_paths, groups=dataset.patients):
        print_info(f"Fold {fold_idx}/{num_folds}")
        log_print(log_file, f"Fold {fold_idx}/{num_folds}")

        # creazione dei subset per il training e la validazione
        fold_dataset_train = Subset(dataset, train_idx)
        fold_dataset_val = Subset(dataset, val_idx)

        # addestramento (fit per il fold attuale)
        model = KFoldModelWrapper(model_name)
        model.fit(fold_dataset_train)

        # valutazione (disabilita l'augmentation durante la valutazione)
        with dataset.eval_mode():  
            output = model.score(fold_dataset_val)

        # risultati del fold
        print_results(output, labels=OCTDL.labels)
        log_print(log_file, f"Risultati del fold {fold_idx}: {output}")
        if 'eval_confusion_matrix' in output:
            del output['eval_confusion_matrix']  # non serve per il calcolo della media
        outputs.append(output)
        fold_idx += 1

    # stampa della media e della deviazione standard delle metriche
    print_separator(70)
    print_success_box(f"K-Fold Cross Validation ({num_folds} folds) completata!")
    log_print(log_file, f"Risultati finali: {outputs}")
    print_final_results(outputs)