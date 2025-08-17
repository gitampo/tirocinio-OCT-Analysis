import torch
from deeplearning.models import ViTMAE
from pathlib import Path
from configs.paths import PT_checkpoints_dir

def infer_disease(images):
    # caricamento del checkpoint
    checkpoint_to_load = Path(PT_checkpoints_dir)/"vitmae"/"vitmae-augmented.pth"

    return infer_vitmae(checkpoint_to_load, images)

def infer_vitmae(checkpoint_to_load, images):

    # guardia per il checkpoint
    if not Path(checkpoint_to_load).exists():
        raise FileNotFoundError(f"Checkpoint non trovato: '{checkpoint_to_load}'")

    # guardia per il numero di immagini
    if images is None or len(images) == 0: return

    # caricamento del modello
    model = ViTMAE.ViTMAEForImageClassification()
    model.load_state_dict(torch.load(checkpoint_to_load))

    # impostazione del modello in modalità di valutazione
    model.eval()

    # mappa delle malattie
    disease_map = ['AMD','DME','ERM','NO','RAO','RVO','VID']

    # preprocessing delle immagini
    batch_to_infer = ViTMAE.preprocess_batch({'image':images})

    # inferenza sulle immagini
    with torch.no_grad():

        # prepara gli input
        inputs = batch_to_infer['pixel_values']

        # esegue il forward pass
        outputs = model(inputs)
        logits = outputs['logits']
        probs = logits.softmax(dim=-1)
        preds = probs.argmax(dim=-1)

        return [disease_map[pred] for pred in preds], list(probs.max(dim=-1).values*100)
