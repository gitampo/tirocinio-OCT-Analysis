"""Verifica che il mascheramento di ViTMAE sia esplicito e configurabile."""
import sys
from pathlib import Path

import pytest
import torch

sys.path.insert(0, str(Path(__file__).resolve().parent / "app"))

from deeplearning.model_factory import load_model

IMMAGINE = torch.linspace(-1, 1, 224).view(1, 1, 1, -1).expand(1, 3, 224, 224)
TOKEN_SENZA_MASCHERA = 197  # 196 patch + CLS
TOKEN_CON_MASCHERA_075 = 50  # 49 patch + CLS


def _numero_token(modello):
    with torch.no_grad():
        return modello.backbone(IMMAGINE).last_hidden_state.shape[1]


@pytest.mark.parametrize("nome", ["vitmae-light", "vitmae-heavy"])
def test_di_default_non_maschera_nulla(nome):
    modello = load_model(nome, pretrained=False).eval()
    assert _numero_token(modello) == TOKEN_SENZA_MASCHERA


@pytest.mark.parametrize("nome", ["vitmae-light", "vitmae-heavy"])
def test_si_puo_riprodurre_il_mascheramento_del_report(nome):
    modello = load_model(nome, pretrained=False, mask_ratio=0.75).eval()
    assert _numero_token(modello) == TOKEN_CON_MASCHERA_075


def test_senza_maschera_la_predizione_e_stabile():
    modello = load_model("vitmae-light", pretrained=False).eval()
    with torch.no_grad():
        prima = modello(IMMAGINE)["logits"]
        dopo = modello(IMMAGINE)["logits"]
    assert torch.allclose(prima, dopo, atol=1e-4)


def test_kfold_passa_mask_ratio_al_modello(monkeypatch):
    import deeplearning.kfoldcv as kfoldcv

    ricevuti = {}

    class Fermati(Exception):
        pass

    def finto_load_model(nome, **kwargs):
        ricevuti.update(kwargs)
        raise Fermati

    monkeypatch.setattr(kfoldcv, "load_model", finto_load_model)

    with pytest.raises(Fermati):
        kfoldcv.KFoldModelWrapper("vitmae-light", mask_ratio=0.75).fit(None)

    assert ricevuti["mask_ratio"] == 0.75


def test_la_cli_accetta_mask_ratio(monkeypatch):
    from utils.argparser import get_args

    monkeypatch.setattr(
        sys, "argv",
        ["main.py", "kfoldcv", "-m", "vitmae-light", "--mask-ratio", "0.75"],
    )
    assert get_args().mask_ratio == 0.75

    monkeypatch.setattr(sys, "argv", ["main.py", "kfoldcv", "-m", "vitmae-light"])
    assert get_args().mask_ratio == 0.0
