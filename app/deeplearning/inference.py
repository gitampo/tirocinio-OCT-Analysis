import torch
from .datasets import OCTDL
from .model_factory import (
    get_preprocessor, 
    load_model 
)
from deeplearning import CHECKPOINT_FOR_DISEASE_INFERENCE, DEFAULT_SEED
from deeplearning.utils import get_checkpoint_path, set_seed
from pathlib import Path

def infer_disease(images, seed=DEFAULT_SEED):

    # impostazione del seed per riproducibilità
    set_seed(seed)

    # checkpoint per l'inferenza
    checkpoint_to_load = CHECKPOINT_FOR_DISEASE_INFERENCE
    model_name, checkpoint_name = checkpoint_to_load.split('/')
    checkpoint_path = get_checkpoint_path(model_name, checkpoint_name)

    # guardia per il checkpoint
    if not Path(checkpoint_path).exists():
        raise FileNotFoundError(f"Checkpoint non trovato: '{checkpoint_path}'")

    # guardia per il numero di immagini
    if images is None or len(images) == 0: return ([],[])

    # caricamento del modello e del checkpoint
    model = load_model(model_name)
    model.load_state_dict(torch.load(checkpoint_path, weights_only=True))

    # impostazione del modello in modalità di valutazione
    model.eval()

    # mappa delle malattie
    disease_labels = OCTDL.labels

    # preprocessing delle immagini
    preprocessor = get_preprocessor(model_name)
    batch_to_infer = preprocessor({'image': images})

    # inferenza sulle immagini
    with torch.no_grad():

        # prepara gli input
        inputs = batch_to_infer['pixel_values']

        # esegue il forward pass
        outputs = model(inputs)
        logits = outputs['logits']
        probs = logits.softmax(dim=-1)
        preds = probs.argmax(dim=-1)

        return [disease_labels[pred] for pred in preds], list(probs.max(dim=-1).values*100)

    return infer_vitmae(checkpoint_to_load, images)