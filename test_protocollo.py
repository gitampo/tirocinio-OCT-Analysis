"""Verifica il protocollo comune di training della cross-validation."""
import json
import sys
from pathlib import Path

import numpy as np
import pytest
import torch
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent / "app"))

import deeplearning.kfoldcv as kfoldcv
from deeplearning.testing import compute_metrics_for_test

CLASSI = ["AMD", "DME", "ERM", "NO", "RAO", "RVO", "VID"]


class ModelloPiccolo(torch.nn.Module):
    def __init__(self, num_labels=7, **kwargs):
        super().__init__()
        self.lineare = torch.nn.Linear(3, num_labels)

    def forward(self, pixel_values, labels=None):
        return {"loss": None, "logits": self.lineare(pixel_values.mean(dim=(2, 3)))}


@pytest.fixture
def dataset_sintetico(tmp_path, monkeypatch):
    # 7 classi, 3 pazienti per classe, 2 immagini per paziente
    cartella = tmp_path / "OCTDL"
    righe = ["file_name,patient_id"]
    rng = np.random.default_rng(0)
    paziente = 0
    for classe in CLASSI:
        (cartella / classe).mkdir(parents=True)
        for _ in range(3):
            paziente += 1
            for k in range(2):
                nome = f"{classe}_{paziente}_{k}"
                pixel = rng.integers(0, 255, (32, 32, 3), dtype=np.uint8)
                Image.fromarray(pixel).save(cartella / classe / f"{nome}.png")
                righe.append(f"{nome},{paziente}")
    (cartella / "OCTDL_labels.csv").write_text("\n".join(righe))

    import configs.paths as paths
    import deeplearning.datasets.OCTDL as OCTDL
    import utils.log as log

    for modulo in (paths, OCTDL, kfoldcv):
        monkeypatch.setattr(modulo, "PT_datasets_dir", str(tmp_path))
    log_dir = tmp_path / "logs"
    log_dir.mkdir()
    monkeypatch.setattr(kfoldcv, "PT_log_dir", str(log_dir))
    monkeypatch.setattr(log, "PT_log_dir", str(log_dir))
    monkeypatch.setattr(kfoldcv, "PT_trainer_output_dir", str(tmp_path / "trainer"))
    monkeypatch.setattr(kfoldcv, "EPOCHE", 1)
    monkeypatch.setattr(kfoldcv, "load_model", lambda nome, num_labels=7, **k: ModelloPiccolo(num_labels))
    OCTDL._discover_available_labels.cache_clear()
    yield log_dir
    OCTDL._discover_available_labels.cache_clear()


def _esegui(log_dir, seed):
    kfoldcv.kfold_cv("mlp", num_folds=3, seed=seed)
    ultimo = max(log_dir.glob("*.json"), key=lambda p: p.stat().st_mtime)
    return json.loads(ultimo.read_text(encoding="utf-8"))


def test_i_fold_non_dipendono_dal_seed_di_training(dataset_sintetico):
    primo = _esegui(dataset_sintetico, seed=1)
    secondo = _esegui(dataset_sintetico, seed=2)

    assert [f["immagini"] for f in primo["fold"]] == [f["immagini"] for f in secondo["fold"]]
    assert primo["seed_split"] == secondo["seed_split"] == kfoldcv.SEED_SPLIT


def test_il_json_contiene_predizioni_e_pazienti_separati(dataset_sintetico):
    risultati = _esegui(dataset_sintetico, seed=42)

    assert len(risultati["fold"]) == 3
    tutte = [img for fold in risultati["fold"] for img in fold["immagini"]]
    assert len(tutte) == len(set(tutte)) == 42
    pazienti = [set(fold["pazienti"]) for fold in risultati["fold"]]
    assert all(a.isdisjoint(b) for i, a in enumerate(pazienti) for b in pazienti[i + 1:])
    for fold in risultati["fold"]:
        assert len(fold["predizioni"]) == len(fold["etichette"]) == len(fold["immagini"])


def test_pesi_classi_bilanciati():
    pesi = kfoldcv.pesi_classi(np.array([0, 0, 0, 1]), 2)
    assert torch.allclose(pesi, torch.tensor([4 / 6, 2.0]))


def test_la_loss_e_pesata(tmp_path):
    pesi = torch.tensor([1.0, 3.0])
    trainer = kfoldcv.WeightedTrainer(
        model=ModelloPiccolo(num_labels=2),
        args=kfoldcv.argomenti_training(0, str(tmp_path)),
        class_weights=pesi,
    )
    inputs = {"pixel_values": torch.rand(4, 3, 8, 8), "labels": torch.tensor([0, 1, 1, 0])}

    loss = trainer.compute_loss(trainer.model, inputs)

    logits = trainer.model(pixel_values=inputs["pixel_values"])["logits"]
    atteso = torch.nn.functional.cross_entropy(logits, inputs["labels"], weight=pesi)
    assert torch.allclose(loss, atteso)


def test_argomenti_di_training_comuni(tmp_path):
    args = kfoldcv.argomenti_training(42, str(tmp_path))
    assert args.learning_rate == 5e-5
    assert args.num_train_epochs == 20
    assert args.save_strategy == "no"


def test_augmentation_comune_senza_flip_verticale():
    nomi = [type(t).__name__ for t in kfoldcv._trasformazione_comune.transforms]
    assert nomi == ["RandomHorizontalFlip", "RandomRotation"]


def test_metriche_per_classe_allineate_anche_con_classe_assente():
    etichette = np.array([0, 1, 3, 4, 5, 6])  # manca la classe 2
    metriche = compute_metrics_for_test((np.eye(7)[etichette], etichette))

    assert len(metriche["classes_recall"]) == 7
    assert metriche["classes_recall"][3] == 1.0
    assert np.array(metriche["confusion_matrix"]).shape == (7, 7)


def test_deviazione_standard_campionaria():
    outputs = [{"eval_accuracy": 0.0}, {"eval_accuracy": 1.0}]
    righe, _ = kfoldcv.preprocess_final_results(outputs, [{}, {}], ["A"])
    assert righe[0][2] == "0.707"
