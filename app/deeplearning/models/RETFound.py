import argparse

import torch
from huggingface_hub import hf_hub_download
from torchvision import transforms
from transformers import ViTImageProcessor

# Pesi ufficiali RETFound-MAE per OCT (licenza CC BY-NC 4.0, accesso su richiesta)
REPO_PESI = "YukunZhou/RETFound_mae_natureOCT"
FILE_PESI = "RETFound_mae_natureOCT.pth"
ARCHITETTURA = "vit_large_patch16_224"

# Chiavi del checkpoint MAE che l'encoder per la classificazione non usa
CHIAVI_MANCANTI_ATTESE = {"fc_norm.weight", "fc_norm.bias"}
CHIAVI_IGNORATE = {"mask_token", "norm.weight", "norm.bias"}

# Normalizzazione ImageNet e interpolazione bicubica, come nel repository ufficiale
processor = ViTImageProcessor(
    image_mean=[0.485, 0.456, 0.406],
    image_std=[0.229, 0.224, 0.225],
    resample=3,
)


def _crea_encoder():
    import timm  # import locale: serve solo quando si usa questo modello

    return timm.create_model(ARCHITETTURA, pretrained=False, num_classes=0, global_pool="avg")


def _scarica_pesi():
    # il token viene letto dalla variabile d'ambiente HF_TOKEN o dal login di Hugging Face
    percorso = hf_hub_download(REPO_PESI, FILE_PESI)

    # weights_only=True evita di eseguire codice arbitrario contenuto nel file
    torch.serialization.add_safe_globals([argparse.Namespace])
    return torch.load(percorso, map_location="cpu", weights_only=True)["model"]


def _carica_pesi(encoder, stato):
    esito = encoder.load_state_dict(stato, strict=False)

    mancanti = set(esito.missing_keys) - CHIAVI_MANCANTI_ATTESE
    inattese = [
        chiave for chiave in esito.unexpected_keys
        if not chiave.startswith("decoder") and chiave not in CHIAVI_IGNORATE
    ]
    if mancanti or inattese:
        raise RuntimeError(
            f"Pesi RETFound non compatibili. Mancanti: {sorted(mancanti)}. Inattese: {inattese}"
        )


class RETFoundForImageClassification(torch.nn.Module):
    def __init__(self, num_labels=7, pretrained=True):
        super().__init__()

        stato = _scarica_pesi() if pretrained else None

        self.backbone = _crea_encoder()
        if stato is not None:
            _carica_pesi(self.backbone, stato)

        # testa lineare, inizializzata come nel repository ufficiale
        self.classifier = torch.nn.Linear(self.backbone.num_features, num_labels)
        torch.nn.init.trunc_normal_(self.classifier.weight, std=2e-5)
        torch.nn.init.zeros_(self.classifier.bias)

    def freeze_backbone(self):
        for param in self.backbone.parameters():
            param.requires_grad = False

    def unfreeze_backbone(self):
        for param in self.backbone.parameters():
            param.requires_grad = True

    def forward(self, pixel_values, labels=None):
        logits = self.classifier(self.backbone(pixel_values))

        loss = None
        if labels is not None:
            loss = self.compute_loss(logits, labels)

        return {"loss": loss, "logits": logits}

    def compute_loss(self, logits, labels):
        return torch.nn.functional.cross_entropy(logits, labels)


# Funzioni per il preprocessing

def preprocess_batch(examples):
    global processor

    # Conversione in RGB
    examples['image'] = [image.convert('RGB') for image in examples['image']]

    # Processa il batch e trasforma le immagini in array NumPy
    processed_batch = processor(images=examples['image'], return_tensors="np")

    return processed_batch


def augment(examples):

    transform = transforms.Compose([
        transforms.RandomHorizontalFlip(p=0.5),
        transforms.RandomVerticalFlip(p=0.5),
        transforms.RandomRotation(degrees=10),
        transforms.ColorJitter(brightness=0.1, contrast=0.1, saturation=0.1),
        transforms.GaussianBlur(kernel_size=3, sigma=(0.1, 2.0)),
    ])

    # augmentation dei dati di addestramento
    examples['image'] = [transform(image.convert('RGB')) for image in examples['image']]

    return examples
