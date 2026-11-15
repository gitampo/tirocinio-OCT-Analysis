"""Validazione esterna: addestramento su tutto OCTDL e predizioni sul test set di C8.

Il training usa lo stesso identico protocollo della cross-validation (riusa kfoldcv.py).
Nel JSON ogni immagine di C8 conserva la sua classe originale (AMD, CNV, MH, ...):
la corrispondenza con le classi di OCTDL si decide dopo, in analisi, senza rifare il training.
"""
import json
from collections import Counter
from pathlib import Path

import numpy as np
import torch
from PIL import Image
from torch.utils.data import Dataset, Subset

from configs.paths import PT_log_dir
from utils.funs import get_available_filename
from utils.log import log_print
from utils.print import print_info, print_success_box
from . import kfoldcv
from .kfoldcv import KFoldDataset, KFoldModelWrapper, SEED_SPLIT, _commit_corrente, _in_json
from .model_factory import get_preprocessor
from .training import set_seed
from . import DEFAULT_SEED, TRAIN_BATCH_SIZE

ESTENSIONI = {".jpg", ".jpeg", ".png"}
IMMAGINI_OCTDL = 2064


def trova_test_c8():
    # cartella "test" del dataset Kaggle obulisainaren/retinal-oct-c8 (una sottocartella per classe)
    for cartella in sorted(Path("/kaggle/input").rglob("test")):
        if cartella.is_dir() and "c8" in str(cartella).lower():
            return cartella
    raise FileNotFoundError("Cartella 'test' di C8 non trovata: aggiungi al notebook il dataset obulisainaren/retinal-oct-c8")


class C8TestDataset(Dataset):
    # restituisce solo le immagini: il modello non conosce le classi di C8, quindi niente etichette
    def __init__(self, model_name, cartella_test, per_classe=None):
        self.preprocessor = get_preprocessor(model_name)
        percorsi = sorted(p for p in cartella_test.rglob("*") if p.suffix.lower() in ESTENSIONI)
        if per_classe:
            # modalita' prova: solo le prime immagini di ogni classe
            visti = Counter()
            scelti = []
            for p in percorsi:
                if visti[p.parent.name] < per_classe:
                    scelti.append(p)
                    visti[p.parent.name] += 1
            percorsi = scelti
        self.image_paths = percorsi
        self.classi_c8 = [p.parent.name for p in percorsi]

    def __len__(self):
        return len(self.image_paths)

    def __getitem__(self, idx):
        image = Image.open(self.image_paths[idx]).convert("RGB")
        return {"pixel_values": self.preprocessor({"image": [image]})["pixel_values"].squeeze()}


def stampa_riepilogo(classi_c8, predizioni, classi_octdl):
    # per ogni classe di C8: in quali classi di OCTDL finiscono le sue immagini
    righe = sorted(set(classi_c8))
    print(f"{'C8 -> OCTDL':12}" + "".join(f"{c:>6}" for c in classi_octdl) + f"{'totale':>8}")
    for classe in righe:
        conteggi = Counter(p for c, p in zip(classi_c8, predizioni) if c == classe)
        print(f"{classe:12}" + "".join(f"{conteggi[k]:>6}" for k in range(len(classi_octdl)))
              + f"{sum(conteggi.values()):>8}")


def validazione_esterna(model_name, seed=DEFAULT_SEED, mask_ratio=0.0, prova=False):
    set_seed(seed)

    # training set: tutto OCTDL, con l'augmentation comune (come nei fold della cross-validation)
    dataset = KFoldDataset(model_name, seed=SEED_SPLIT, use_augmentation=True)
    percorsi_train = [str(p).lower() for p in dataset.image_paths]
    if len(percorsi_train) != IMMAGINI_OCTDL or any("c8" in p for p in percorsi_train):
        raise RuntimeError(f"Il training set non e' OCTDL: {len(percorsi_train)} immagini, ad esempio {percorsi_train[:2]}")
    indici = np.arange(len(dataset))
    if prova:
        indici = indici[:64]
        kfoldcv.EPOCHE = 1   # prova veloce su CPU: 64 immagini e 1 epoca (argomenti_training legge EPOCHE)
    train = Subset(dataset, indici)

    # test set: test di C8, senza etichette per il modello
    cartella_test = trova_test_c8()
    test = C8TestDataset(model_name, cartella_test, per_classe=4 if prova else None)

    # file di log e JSON accanto, come in kfoldcv
    stem = Path(get_available_filename(PT_log_dir, "validazione_esterna.log")).stem
    log_print(stem,
              f"MODEL: {model_name} \n"
              f"SEED: {seed} \n"
              f"COMMIT: {_commit_corrente()} \n"
              f"PROTOCOLLO: AdamW lr={kfoldcv.LEARNING_RATE}, cosine+warmup 100, {kfoldcv.EPOCHE} epoche, "
              f"batch {TRAIN_BATCH_SIZE}, loss pesata, augmentation comune \n"
              f"TRAIN: OCTDL completo, {len(train)} immagini \n"
              f"TEST: {len(test)} immagini da {cartella_test} \n"
              f"MASK_RATIO: {mask_ratio} \n"
              f"PROVA: {prova} \n")

    # addestramento con lo stesso wrapper (e quindi lo stesso protocollo) della cross-validation
    modello = KFoldModelWrapper(model_name, mask_ratio=mask_ratio, seed=seed)
    modello.fit(train)

    # predizioni su C8 (il Trainer mette da solo il modello in modalita' valutazione).
    # Senza etichette il Trainer terrebbe anche la voce "loss" (None) dell'output e andrebbe in errore
    print_info(f"Predizioni su {len(test)} immagini di test di C8...")
    risultato = modello.trainer.predict(test, ignore_keys=["loss"])
    probabilita = torch.softmax(torch.as_tensor(risultato.predictions), dim=-1).numpy()
    predizioni = probabilita.argmax(axis=-1)

    classi_octdl = list(dataset.task_labels)
    risultati = {
        "modello": model_name, "seed": seed, "commit": _commit_corrente(), "mask_ratio": mask_ratio,
        "prova": prova, "epoche": kfoldcv.EPOCHE, "immagini_train": len(train),
        "classi": classi_octdl,
        "immagini": [p.name for p in test.image_paths],
        "classi_c8": test.classi_c8,
        "predizioni": predizioni.tolist(),
        "probabilita": probabilita.tolist(),
    }
    with open(Path(PT_log_dir) / f"{stem}.json", "w", encoding="utf-8") as file_json:
        json.dump(risultati, file_json, indent=1, default=_in_json)

    stampa_riepilogo(test.classi_c8, predizioni, classi_octdl)
    log_print(stem, f"Risultati salvati in {stem}.json")
    print_success_box(f"Validazione esterna completata: {Path(PT_log_dir) / (stem + '.json')}")
