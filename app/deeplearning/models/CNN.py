import torch
import torch.nn as nn
from torchvision import transforms
import torchvision.models as models

# Configurazione per il preprocessing
class CNNImageProcessor:
    def __init__(self):
        self.transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.Grayscale(num_output_channels=3),  # OCT grayscale → RGB
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])
    
    def __call__(self, images, return_tensors=None):
        pixel_values = torch.stack([self.transform(img) for img in images])
        return {"pixel_values": pixel_values}

processor = CNNImageProcessor()

# ----------------------------------------------------------------------------
# ----------------------------------------------------------------------------

# ResNet18 per la classificazione delle immagini
class ResNet18ForImageClassification(torch.nn.Module):
    def __init__(self, num_labels=7):
        super().__init__()
        self.backbone = models.resnet18(weights='IMAGENET1K_V1')
        num_ftrs = self.backbone.fc.in_features
        self.backbone.fc = nn.Identity()
        self.classifier = torch.nn.Sequential(
            torch.nn.Linear(num_ftrs, 256),
            torch.nn.ReLU(),
            torch.nn.Dropout(0.2),
            torch.nn.Linear(256, 128),
            torch.nn.ReLU(),
            torch.nn.Dropout(0.2),
            torch.nn.Linear(128, num_labels)
        )

    def freeze_backbone(self):
        for param in self.backbone.parameters():
            param.requires_grad = False

    def forward(self, pixel_values, labels=None):
        features = self.backbone(pixel_values)
        logits = self.classifier(features)
        loss = None
        if labels is not None:
            loss = self.compute_loss(logits, labels)
        return {"loss": loss, "logits": logits}

    def compute_loss(self, logits, labels):
        return torch.nn.functional.cross_entropy(logits, labels)

# ResNet50 per la classificazione delle immagini
class ResNet50ForImageClassification(torch.nn.Module):
    def __init__(self, num_labels=7):
        super().__init__()
        self.backbone = models.resnet50(weights='IMAGENET1K_V1')
        num_ftrs = self.backbone.fc.in_features
        self.backbone.fc = nn.Identity()
        self.classifier = torch.nn.Sequential(
            torch.nn.Linear(num_ftrs, 512),
            torch.nn.ReLU(),
            torch.nn.Dropout(0.3),
            torch.nn.Linear(512, 256),
            torch.nn.ReLU(),
            torch.nn.Dropout(0.2),
            torch.nn.Linear(256, num_labels)
        )

    def freeze_backbone(self):
        for param in self.backbone.parameters():
            param.requires_grad = False

    def forward(self, pixel_values, labels=None):
        features = self.backbone(pixel_values)
        logits = self.classifier(features)
        loss = None
        if labels is not None:
            loss = self.compute_loss(logits, labels)
        return {"loss": loss, "logits": logits}

    def compute_loss(self, logits, labels):
        return torch.nn.functional.cross_entropy(logits, labels)

# DenseNet121 per la classificazione delle immagini
class DenseNet121ForImageClassification(torch.nn.Module):
    def __init__(self, num_labels=7):
        super().__init__()
        self.backbone = models.densenet121(weights='IMAGENET1K_V1')
        num_ftrs = self.backbone.classifier.in_features
        self.backbone.classifier = nn.Identity()
        self.classifier = torch.nn.Sequential(
            torch.nn.Linear(num_ftrs, 512),
            torch.nn.ReLU(),
            torch.nn.Dropout(0.3),
            torch.nn.Linear(512, 256),
            torch.nn.ReLU(),
            torch.nn.Dropout(0.2),
            torch.nn.Linear(256, num_labels)
        )

    def freeze_backbone(self):
        for param in self.backbone.parameters():
            param.requires_grad = False

    def forward(self, pixel_values, labels=None):
        features = self.backbone(pixel_values)
        logits = self.classifier(features)
        loss = None
        if labels is not None:
            loss = self.compute_loss(logits, labels)
        return {"loss": loss, "logits": logits}

    def compute_loss(self, logits, labels):
        return torch.nn.functional.cross_entropy(logits, labels)

# EfficientNet_b0 per la classificazione delle immagini
class EfficientNetB0ForImageClassification(torch.nn.Module):
    def __init__(self, num_labels=7):
        super().__init__()
        self.backbone = models.efficientnet_b0(weights='IMAGENET1K_V1')
        num_ftrs = self.backbone.classifier[1].in_features
        self.backbone.classifier = nn.Identity()
        self.classifier = torch.nn.Sequential(
            torch.nn.Linear(num_ftrs, 512),
            torch.nn.ReLU(),
            torch.nn.Dropout(0.3),
            torch.nn.Linear(512, 256),
            torch.nn.ReLU(),
            torch.nn.Dropout(0.2),
            torch.nn.Linear(256, num_labels)
        )

    def freeze_backbone(self):
        for param in self.backbone.parameters():
            param.requires_grad = False

    def forward(self, pixel_values, labels=None):
        features = self.backbone(pixel_values)
        logits = self.classifier(features)
        loss = None
        if labels is not None:
            loss = self.compute_loss(logits, labels)
        return {"loss": loss, "logits": logits}

    def compute_loss(self, logits, labels):
        return torch.nn.functional.cross_entropy(logits, labels)

# Factory function per compatibilità con il model_factory
def CNNForImageClassification(variant='resnet18', num_labels=7):
    """Factory function per creare modelli CNN in base alla variante richiesta"""
    if variant == 'resnet18':
        return ResNet18ForImageClassification(num_labels=num_labels)
    elif variant == 'resnet50':
        return ResNet50ForImageClassification(num_labels=num_labels)
    elif variant == 'densenet121':
        return DenseNet121ForImageClassification(num_labels=num_labels)
    elif variant == 'efficientnet_b0':
        return EfficientNetB0ForImageClassification(num_labels=num_labels)
    else:
        raise ValueError(f"Variant {variant} non supportata")

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

