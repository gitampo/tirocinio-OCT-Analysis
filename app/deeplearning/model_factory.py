from .models import ViTMAE
from . import AVAILABLE_MODELS

# configurazione dei dizionari per il training di vitmae
_model_classes    = {
    "vitmae-light": ViTMAE.ViTMAEForImageClassification_light,
    "vitmae-heavy": ViTMAE.ViTMAEForImageClassification_heavy
}
_training_args    = {
    "vitmae-light": ViTMAE.vitmae_training_args,
    "vitmae-heavy": ViTMAE.vitmae_training_args
}
_compute_metrics  = {
    "vitmae-light": ViTMAE.vitmae_compute_metrics,
    "vitmae-heavy": ViTMAE.vitmae_compute_metrics
}
_callbacks        = {
    "vitmae-light": ViTMAE.vitmae_callbacks,
    "vitmae-heavy": ViTMAE.vitmae_callbacks
}
_train_preprocessor = {
    "vitmae-light": lambda examples: ViTMAE.preprocess_batch(ViTMAE.augment(examples)),
    "vitmae-heavy": lambda examples: ViTMAE.preprocess_batch(ViTMAE.augment(examples))
}
_preprocessor  = {
    "vitmae-light": ViTMAE.preprocess_batch,
    "vitmae-heavy": ViTMAE.preprocess_batch
}

# lista dei mapping
maps = [
    _model_classes,
    _training_args,
    _compute_metrics,
    _callbacks,
    _train_preprocessor,
    _preprocessor
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
def load_training_args(model_name):

    # caricamento degli argomenti di training, metriche, callbacks e preprocess
    training_args       = _training_args[model_name]
    compute_metrics     = _compute_metrics[model_name]
    callbacks           = _callbacks[model_name]
    train_preprocessor  = _train_preprocessor[model_name]

    return training_args, compute_metrics, callbacks, train_preprocessor

@check_model_available
def get_training_args(model_name):
    return _training_args[model_name]

@check_model_available
def get_compute_metrics(model_name):
    return _compute_metrics[model_name]

@check_model_available
def get_callbacks(model_name):
    return _callbacks[model_name]

@check_model_available
def get_train_preprocessor(model_name):
    return _train_preprocessor[model_name]

@check_model_available
def get_test_preprocessor(model_name):
    return _preprocessor[model_name]

@check_model_available
def get_preprocessor(model_name):
    return _preprocessor[model_name]