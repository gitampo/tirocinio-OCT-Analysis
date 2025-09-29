from .models import MLP
from .models import ViTMAE
from .models import ViT

AVAILABLE_MODELS = ['vitmae-light', 'vitmae-heavy', 'vit', 'mlp']

# configurazione dei dizionari per il training di vitmae
_model_classes    = {
    "vitmae-light": ViTMAE.ViTMAEForImageClassification_light,
    "vitmae-heavy": ViTMAE.ViTMAEForImageClassification_heavy,
    "vit": ViT.ViTForImageClassification,
    "mlp": MLP.MLPImageClassification
}
_train_preprocessor = {
    "vitmae-light": lambda examples: ViTMAE.preprocess_batch(ViTMAE.augment(examples)),
    "vitmae-heavy": lambda examples: ViTMAE.preprocess_batch(ViTMAE.augment(examples)),
    "vit": lambda examples: ViT.preprocess_batch(ViT.augment(examples)),
    "mlp": lambda examples: MLP.preprocess_batch(MLP.augment(examples))
}
_preprocessor  = {
    "vitmae-light": ViTMAE.preprocess_batch,
    "vitmae-heavy": ViTMAE.preprocess_batch,
    "vit": ViT.preprocess_batch,
    "mlp": MLP.preprocess_batch
}
_augmenter    = {
    "vitmae-light": ViTMAE.augment,
    "vitmae-heavy": ViTMAE.augment,
    "vit": ViT.augment,
    "mlp": MLP.augment
}

# lista dei mapping
maps = [
    _model_classes,
    _train_preprocessor,
    _preprocessor,
    _augmenter
]

# verifica che le chiavi dei dizionari corrispondano ai modelli disponibili
for map in maps:
    if list(map.keys()) != AVAILABLE_MODELS:
        raise ValueError(
        "Errore nell'inizializzazione del package 'deeplearning': " \
        "Le chiavi dei dizionari non corrispondono ai modelli disponibili.")

# decoratore per il controllo del modello
def check_model_available(wrapped):
    def wrapper(model_name, *args, **kwargs):

        # verifica se il modello è supportato
        if model_name not in AVAILABLE_MODELS:
            raise NotImplementedError(f"Modello '{model_name}' non supportato")

        # chiamata alla funzione wrapped
        result = wrapped(model_name, *args, **kwargs)

        return result
    return wrapper

@check_model_available
def load_model(model_name):
    # caricamento del modello
    model = _model_classes[model_name]()
    return model

@check_model_available
def get_train_preprocessor(model_name):
    return _train_preprocessor[model_name]

@check_model_available
def get_test_preprocessor(model_name):
    return _preprocessor[model_name]

@check_model_available
def get_preprocessor(model_name):
    return _preprocessor[model_name]

@check_model_available
def get_augmenter(model_name):
    return _augmenter[model_name]