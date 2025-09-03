import torch
from torchvision import transforms
from transformers import AutoModel, ViTImageProcessor, ViTMAEModel, ViTMAEConfig
from transformers import TrainingArguments
from configs.paths import PT_checkpoints_dir, PT_trainer_output_dir

# Configurazione del modello
config = ViTMAEConfig.from_pretrained("facebook/vit-mae-base")

# Processor per le immagini
processor = ViTImageProcessor.from_pretrained('facebook/vit-mae-base')

# ----------------------------------------------------------------------------
# ----------------------------------------------------------------------------

# ViTMAE per la classificazione delle immagini (head pesante)
class ViTMAEForImageClassification_heavy(torch.nn.Module):
    def __init__(self, num_labels=7):
        super().__init__()

        self.backbone = ViTMAEModel.from_pretrained("facebook/vit-mae-base")
        self.classifier = torch.nn.Sequential(
            torch.nn.Linear(self.backbone.config.hidden_size, 256),
            torch.nn.ReLU(),
            torch.nn.Linear(256,256),
            torch.nn.ReLU(),
            torch.nn.Linear(256,256),
            torch.nn.ReLU(),
            torch.nn.Linear(256, num_labels)
        )

    def freeze_backbone(self):
        for param in self.backbone.parameters():
            param.requires_grad = False

    def forward(self, pixel_values, labels=None):
        outputs = self.backbone(pixel_values)
        logits = self.classifier(outputs.last_hidden_state[:, 0])
        loss = None
        if labels is not None:
            loss = self.compute_loss(logits, labels)
        return {"loss": loss, "logits": logits}

    def compute_loss(self, logits, labels):
        return torch.nn.functional.cross_entropy(logits, labels)

# ----------------------------------------------------------------------------

# ViTMAE per la classificazione delle immagini (head leggera)
class ViTMAEForImageClassification_light(torch.nn.Module):
    def __init__(self, num_labels=7):
        super().__init__()

        self.backbone = ViTMAEModel.from_pretrained("facebook/vit-mae-base")
        self.classifier = torch.nn.Sequential(
            torch.nn.Linear(self.backbone.config.hidden_size, 128),
            torch.nn.ReLU(),
            torch.nn.Dropout(0.2),
            torch.nn.Linear(128,128),
            torch.nn.ReLU(),
            torch.nn.Dropout(0.2),
            torch.nn.Linear(128, num_labels)
        )

    def freeze_backbone(self):
        for param in self.backbone.parameters():
            param.requires_grad = False

    def forward(self, pixel_values, labels=None):
        outputs = self.backbone(pixel_values)
        logits = self.classifier(outputs.last_hidden_state[:, 0])
        loss = None
        if labels is not None:
            loss = self.compute_loss(logits, labels)
        return {"loss": loss, "logits": logits}

    def compute_loss(self, logits, labels):
        return torch.nn.functional.cross_entropy(logits, labels)

# ----------------------------------------------------------------------------
# ----------------------------------------------------------------------------

# Funzione di preprocessing per le immagini
def preprocess_batch(examples):
    global processor

    # Conversione in RGB
    examples['image'] = [image.convert('RGB') for image in examples['image']]

    # Processa il batch e trasforma le immagini in tensori PyTorch
    processed_batch = processor(images=examples['image'], return_tensors="pt")

    return processed_batch

def augment(examples):

    transform = transforms.Compose([
        transforms.RandomHorizontalFlip(),
        transforms.RandomVerticalFlip(),
        transforms.RandomRotation(10)
    ])

    # augmentation dei dati di addestramento
    examples['image'] = [transform(image.convert('RGB')) for image in examples['image']]
    return examples   