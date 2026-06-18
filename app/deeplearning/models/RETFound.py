import torch
from torchvision import transforms
from transformers import ViTImageProcessor, ViTModel, ViTConfig

# Configurazione del modello
# RETFound è basato su ViT, quindi utilizzo la configurazione di ViT come base
try:
    config = ViTConfig.from_pretrained("google/vit-base-patch16-224")
    processor = ViTImageProcessor.from_pretrained('google/vit-base-patch16-224')
except Exception:
    # Fallback configuration if HuggingFace models are unavailable
    config = ViTConfig()
    processor = ViTImageProcessor()

# ============================================================================
# RETFound per la classificazione delle immagini OCT (wrapper con backbone ViT)
# ============================================================================

class RETFoundForImageClassification(torch.nn.Module):

    def __init__(self, num_labels=7, pretrained_checkpoint=None):
        super().__init__()

        # Load backbone (Vision Transformer as foundation model)
        self.backbone = ViTModel.from_pretrained("google/vit-base-patch16-224")
        
        # Load pretrained RETFound checkpoint if provided
        if pretrained_checkpoint is not None:
            try:
                checkpoint = torch.load(pretrained_checkpoint, map_location=torch.device('cpu'))
                self.backbone.load_state_dict(checkpoint, strict=False)
            except Exception as e:
                print(f"Warning: Could not load RETFound checkpoint: {e}")
        
        # Medical imaging classification head (lightweight for transfer learning)
        self.classifier = torch.nn.Sequential(
            torch.nn.Linear(self.backbone.config.hidden_size, 256),
            torch.nn.ReLU(),
            torch.nn.Dropout(0.3),
            torch.nn.Linear(256, 128),
            torch.nn.ReLU(),
            torch.nn.Dropout(0.2),
            torch.nn.Linear(128, num_labels)
        )

    def freeze_backbone(self):
        
        for param in self.backbone.parameters():
            param.requires_grad = False

    def unfreeze_backbone(self):
        
        for param in self.backbone.parameters():
            param.requires_grad = True

    def forward(self, pixel_values, labels=None):
        
        outputs = self.backbone(pixel_values)
        logits = self.classifier(outputs.last_hidden_state[:, 0])
        
        loss = None
        if labels is not None:
            loss = self.compute_loss(logits, labels)
        
        return {"loss": loss, "logits": logits}

    def compute_loss(self, logits, labels):
        """Compute cross-entropy loss."""
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
