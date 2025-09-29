import torch
from torchvision import transforms

# Processor per le immagini
def processor(images):
    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])

    pixels = torch.cat([transform(image) for image in images])

    return { "pixel_values": pixels }

# ----------------------------------------------------------------------------
# ----------------------------------------------------------------------------

# MLP per la classificazione delle immagini
class MLPImageClassification(torch.nn.Module):
    def __init__(self, num_labels=7):
        super().__init__()

        self.conv = torch.nn.Sequential(
            torch.nn.Conv2d(3, 32, kernel_size=3, stride=1, padding=1),
            torch.nn.ReLU(),
            torch.nn.MaxPool2d(2),  # 224 -> 112
            torch.nn.Conv2d(32, 64, kernel_size=3, stride=1, padding=1),
            torch.nn.ReLU(),
            torch.nn.MaxPool2d(2),  # 112 -> 56
            torch.nn.Conv2d(64, 128, kernel_size=3, stride=1, padding=1),
            torch.nn.ReLU(),
            torch.nn.MaxPool2d(2),  # 56 -> 28
        )
        self.flatten = torch.nn.Flatten()
        self.fc = torch.nn.Sequential(
            torch.nn.Linear(128*28*28, 128),
            torch.nn.ReLU(),
            torch.nn.Dropout(0.2),
            torch.nn.Linear(128, 128),
            torch.nn.ReLU(),
            torch.nn.Dropout(0.2),
            torch.nn.Linear(128, 128),
            torch.nn.ReLU(),
            torch.nn.Dropout(0.2),
            torch.nn.Linear(128, num_labels)
        )

    def forward(self, pixel_values, labels=None):
        logits = self.fc(self.flatten(self.conv(pixel_values)))
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
    processed_batch = processor(images=examples['image'])

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