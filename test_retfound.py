"""Verifica che il modello retfound carichi davvero i pesi RETFound e non altri."""
import sys
from pathlib import Path

import pytest
import torch

sys.path.insert(0, str(Path(__file__).resolve().parent / "app"))

from deeplearning.model_factory import load_model
from deeplearning.models import RETFound


@pytest.fixture
def encoder_piccolo(monkeypatch):
    # stessa famiglia di modelli, ma leggero: nessun download e poca memoria
    monkeypatch.setattr(RETFound, "ARCHITETTURA", "vit_tiny_patch16_224")
    return RETFound._crea_encoder()


def _checkpoint_mae(encoder):
    stato = {k: v.clone() for k, v in encoder.state_dict().items() if not k.startswith("fc_norm")}
    stato["mask_token"] = torch.zeros(1, 1, 8)
    stato["decoder_embed.weight"] = torch.zeros(8, 8)
    stato["norm.weight"] = torch.zeros(1)
    stato["norm.bias"] = torch.zeros(1)
    return stato


def test_architettura_e_vit_large():
    modello = load_model("retfound", num_labels=7, pretrained=False).eval()

    assert modello.backbone.num_features == 1024
    assert len(modello.backbone.blocks) == 24
    assert modello.backbone.pos_embed.shape == (1, 197, 1024)

    with torch.no_grad():
        logits = modello(torch.zeros(1, 3, 224, 224))["logits"]
    assert logits.shape == (1, 7)


def test_i_pesi_del_checkpoint_vengono_copiati(encoder_piccolo):
    stato = _checkpoint_mae(encoder_piccolo)
    stato["cls_token"] = torch.full_like(stato["cls_token"], 3.0)

    RETFound._carica_pesi(encoder_piccolo, stato)

    assert torch.equal(encoder_piccolo.cls_token, stato["cls_token"])


def test_un_peso_mancante_causa_un_errore(encoder_piccolo):
    stato = _checkpoint_mae(encoder_piccolo)
    del stato["blocks.0.attn.proj.weight"]

    with pytest.raises(RuntimeError, match="non compatibili"):
        RETFound._carica_pesi(encoder_piccolo, stato)


def test_un_peso_sconosciuto_causa_un_errore(encoder_piccolo):
    stato = _checkpoint_mae(encoder_piccolo)
    stato["peso_sconosciuto"] = torch.zeros(1)

    with pytest.raises(RuntimeError, match="non compatibili"):
        RETFound._carica_pesi(encoder_piccolo, stato)


def test_senza_accesso_ai_pesi_il_programma_si_ferma(monkeypatch):
    def nessun_accesso():
        raise OSError("accesso negato")

    monkeypatch.setattr(RETFound, "_scarica_pesi", nessun_accesso)

    with pytest.raises(OSError):
        load_model("retfound")


def test_pretrained_false_non_scarica_nulla(monkeypatch, encoder_piccolo):
    def non_deve_essere_chiamata():
        raise AssertionError("_scarica_pesi non deve essere chiamata")

    monkeypatch.setattr(RETFound, "_scarica_pesi", non_deve_essere_chiamata)

    load_model("retfound", pretrained=False)


def test_normalizzazione_ufficiale():
    assert list(RETFound.processor.image_mean) == [0.485, 0.456, 0.406]
    assert list(RETFound.processor.image_std) == [0.229, 0.224, 0.225]
    assert int(RETFound.processor.resample) == 3
