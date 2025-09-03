from PIL import Image
from sklearn.model_selection import GroupKFold
import torch
import datasets
from transformers import Trainer
from sklearn.metrics import make_scorer
import numpy as np

from configs.paths import PT_datasets_dir
from utils.print import print_info
from pathlib import Path

from .datasets import OCTDL
from .utils import set_seed, load_training_args
from . import (
    DEFAULT_DATASET,
    DEFAULT_KFOLDS,
    DEFAULT_SEED,
    NUM_PROC,
    PREPROCESS_BATCH_SIZE,
    TEST_BATCH_SIZE,
    TRAIN_BATCH_SIZE,
)
from .testing import metrics, metrics_names
from .model_factory import (
    get_preprocessor, 
    load_model 
)

class ModelWrapperForKFoldCV():

    def __init__(self, model_name):
        self.model_name = model_name
        self.model = load_model(self.model_name)
        self.fold_idx = 1

    def fit(self, image_paths, labels):

        # caricamento degli argomenti di training
        print_info(f"Caricamento degli argomenti di training per '{self.model_name}'...")
        training_args = load_training_args()
        training_args.do_eval = False
        training_args.eval_strategy = "no"

        # caricamento del modello
        print_info(f"Caricamento del modello '{self.model_name}'...")

        # composizione del dataset di training
        print_info(f"Caricamento del dataset di training per '{self.model_name}'...")
        data_dict = {"image_paths": list(map(str, image_paths)), "labels": labels}
        dataset = datasets.Dataset.from_dict(data_dict)
        training_dataset = dataset.map(self.preprocess_batch, batched=True, batch_size=PREPROCESS_BATCH_SIZE, num_proc=NUM_PROC)

        # creazione del trainer
        print_info(f"Caricamento degli argomenti di training per '{self.model_name}'...")
        trainer = Trainer(
            model=self.model,
            args=training_args,
            train_dataset=training_dataset,
            eval_dataset=None,
        )
        
        # esecuzione del training
        print_info(f"Inizio training n.{self.fold_idx}...")
        trainer.train()
        print_info(f"Fine training n.{self.fold_idx}...")

        del training_dataset

    def score(self, image_paths, labels):

        # argomenti di training ma in modalità eval
        training_args = load_training_args()
        training_args.do_train = False
        training_args.do_eval = False
        training_args.eval_strategy = "no"

        # dataset
        print_info(f"Caricamento del dataset di testing per '{self.model_name}'...")
        data_dict = {"image_paths": list(map(str, image_paths)), "labels": labels}
        dataset = datasets.Dataset.from_dict(data_dict)
        testing_dataset = dataset.map(
            self.preprocess_batch, 
            batched=True, 
            batch_size=PREPROCESS_BATCH_SIZE, 
            num_proc=NUM_PROC
        )

        # creazione del trainer
        trainer = Trainer(
            model=self.model,
            args=training_args,
        )
        
        # predizioni del modello
        print_info(f"Inizio predizioni n.{self.fold_idx}...")
        predictions = trainer.predict(testing_dataset)
        y_preds = predictions.predictions.argmax(axis=-1)
        y_true = predictions.label_ids
        print_info(f"Fine predizioni n.{self.fold_idx}...")

        # calcolo delle metriche
        print_info(f"Calcolo metriche del fold n.{self.fold_idx}...")
        fold_scores = {}
        for metric in metrics_names:
            score = metrics[metric]["fun"](y_preds, y_true, **metrics[metric]["kwargs"])
            fold_scores[metric] = score

        del testing_dataset

        return fold_scores

    def preprocess_batch(self, examples):

        # ottienimento del preprocessore
        preprocessor = get_preprocessor(self.model_name)

        # preprocessing delle immagini
        examples["image"] = [Image.open(image_path).convert("RGB") for image_path in examples["image_paths"]]
        processed = preprocessor(examples)

        return processed

def get_kfoldcv_dataset():

    # path completo sino al dataset
    path_to_dataset = Path(PT_datasets_dir) / OCTDL.DATASET_NAME

    # elenco delle immagini, etichette e pazienti
    image_paths = (
        list(path_to_dataset.rglob("*.png")) +
        list(path_to_dataset.rglob("*.jpg")) +
        list(path_to_dataset.rglob("*.jpeg"))
    )

    # elementi del dataset (etichette e pazienti corrispondenti alle immagini)
    labels = [OCTDL.label2id(image_paths[idx].parent.name) for idx in range(len(image_paths))]
    patients = [OCTDL.get_patient_id(image_paths[idx].stem) for idx in range(len(image_paths))]

    # conversione in array numpy
    image_paths, labels, patients = np.array(image_paths), np.array(labels), np.array(patients)

    return image_paths, labels, patients

def kfold_cv(model_name, dataset_name=DEFAULT_DATASET, seed=DEFAULT_SEED, num_folds=DEFAULT_KFOLDS):

    # impostazione del seed per riproducibilità
    set_seed(seed)

    # caricamento del dataset
    print_info("Caricamento del dataset...")
    image_paths, labels, patients = get_kfoldcv_dataset()
    
    # esecuzione della cross validation
    print_info(f"Esecuzione della {num_folds}-fold cross validation...")

    # cross validation
    scores = []
    gkf = GroupKFold(n_splits=num_folds)
    for train_idx, test_idx in gkf.split(image_paths, labels, groups=patients):

        # istanziazione del modello per la cross validation
        model = ModelWrapperForKFoldCV(model_name)

        # suddivisione del dataset in training e test
        X_train, X_test = image_paths[train_idx], image_paths[test_idx]
        y_train, y_test = labels[train_idx], labels[test_idx]

        # addestramento del modello e valutazione per la fold attuale
        model.fit(X_train, y_train)
        scores.append(model.score(X_test, y_test))

    print(scores)