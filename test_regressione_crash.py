"""Test di regressione per i crash di train/test e kfoldcv."""
import subprocess
import sys
from contextlib import nullcontext
from pathlib import Path

import numpy as np

APP_DIR = Path(__file__).resolve().parent / "app"
sys.path.insert(0, str(APP_DIR))


def test_utils_usa_la_libreria_datasets_di_huggingface():
    # Processo separato: il bug dipende dall'ordine degli import
    codice = (
        "import deeplearning.training, deeplearning.utils as u; "
        "assert u.datasets.__name__ == 'datasets', u.datasets.__name__"
    )
    esito = subprocess.run(
        [sys.executable, "-c", codice],
        cwd=APP_DIR,
        capture_output=True,
        text=True,
    )
    assert esito.returncode == 0, esito.stderr[-1000:]


def test_kfold_cv_arriva_alla_tabella_finale(monkeypatch, tmp_path, capsys):
    import deeplearning.kfoldcv as kfoldcv
    import utils.log as log
    from deeplearning.testing import compute_metrics_for_test

    class FakeDataset:
        task_labels = ["A", "B", "C"]
        labels = np.array([0, 1, 2] * 4)
        image_paths = np.arange(12)
        patients = np.arange(12)  # un paziente per immagine

        def __len__(self):
            return 12

        def eval_mode(self):
            return nullcontext()

    dataset = FakeDataset()

    class FakeModel:
        def __init__(self, *args, **kwargs):
            pass

        def fit(self, train_dataset):
            pass

        def score(self, val_dataset):
            # predizioni perfette: qui interessa il flusso, non le metriche
            y = dataset.labels[val_dataset.indices]
            metriche = compute_metrics_for_test((np.eye(3)[y], y))
            return {f"eval_{nome}": valore for nome, valore in metriche.items()}

    monkeypatch.setattr(kfoldcv, "KFoldDataset", lambda *a, **k: dataset)
    monkeypatch.setattr(kfoldcv, "KFoldModelWrapper", FakeModel)
    monkeypatch.setattr(kfoldcv, "PT_log_dir", str(tmp_path))
    monkeypatch.setattr(log, "PT_log_dir", str(tmp_path))

    kfoldcv.kfold_cv("mlp", num_folds=2)

    assert "VALORE MEDIO" in capsys.readouterr().out
