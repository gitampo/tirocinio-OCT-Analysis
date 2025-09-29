import torch
from torchvision import transforms
from transformers import ViTImageProcessor, ViTModel, ViTConfig

# Configurazione del modello
config = ViTConfig.from_pretrained("google/vit-base-patch16-224")

# Processor per le immagini
processor = ViTImageProcessor.from_pretrained('google/vit-base-patch16-224')

# ----------------------------------------------------------------------------
# ----------------------------------------------------------------------------

# ViT per la classificazione delle immagini (head leggera)
class ViTForImageClassification(torch.nn.Module):
    def __init__(self, num_labels=7):
        super().__init__()

        self.backbone = ViTModel.from_pretrained("google/vit-base-patch16-224")
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