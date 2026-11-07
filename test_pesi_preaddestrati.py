"""Verifica che i pesi pre-addestrati non vengano sostituiti in silenzio."""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent / "app"))

from deeplearning.model_factory import load_model
from deeplearning.models import RETFound, ViT, ViTMAE

CLASSI_BACKBONE = [
    ("vit", ViT.ViTModel),
    ("retfound", RETFound.ViTModel),
    ("vitmae-light", ViTMAE.ViTMAEModel),
    ("vitmae-heavy", ViTMAE.ViTMAEModel),
]


@pytest.mark.parametrize("nome, classe", CLASSI_BACKBONE)
def test_pesi_non_disponibili_causano_un_errore(nome, classe, monkeypatch):
    def pesi_non_disponibili(*args, **kwargs):
        raise OSError("pesi non disponibili")

    monkeypatch.setattr(classe, "from_pretrained", pesi_non_disponibili)

    with pytest.raises(OSError):
        load_model(nome)


@pytest.mark.parametrize("nome, classe", CLASSI_BACKBONE)
def test_pretrained_false_non_scarica_nulla(nome, classe, monkeypatch):
    def non_deve_essere_chiamata(*args, **kwargs):
        raise AssertionError("from_pretrained non deve essere chiamata")

    monkeypatch.setattr(classe, "from_pretrained", non_deve_essere_chiamata)

    modello = load_model(nome, num_labels=7, pretrained=False)
    assert modello.backbone.config.hidden_size == 768


def test_normalizzazione_uguale_ai_modelli_ufficiali():
    assert list(ViTMAE.processor.image_mean) == [0.485, 0.456, 0.406]
    assert list(ViTMAE.processor.image_std) == [0.229, 0.224, 0.225]
    assert int(ViTMAE.processor.resample) == 2
    assert list(ViT.processor.image_mean) == [0.5, 0.5, 0.5]
    assert list(ViT.processor.image_std) == [0.5, 0.5, 0.5]
    assert list(RETFound.processor.image_mean) == [0.5, 0.5, 0.5]
    assert list(RETFound.processor.image_std) == [0.5, 0.5, 0.5]
