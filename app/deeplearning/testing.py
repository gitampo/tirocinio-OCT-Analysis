import sys
import torch
import datasets
from pathlib import Path

from . import AVAILABLE_MODELS, SEED
from .models import ViTMAE
from .utils import get_checkpoint_from_name, set_seed

from utils.print import * 
from configs.paths import *

def test(model, checkpoint_name):

    # trova i checkpoints a partire dal nome (se inseriti)
    checkpoint_to_load = get_checkpoint_from_name(checkpoint_name)

    # controlla se il modello scelto è disponibile
    if model not in AVAILABLE_MODELS:
        raise ValueError(f"Modello '{model}' non disponibile")

    # controllo sul tipo di modello
    if model == 'vitmae':
        test_vitmae(checkpoint_to_load)
    else:
        raise NotImplementedError(f"Testing non implementato per il modello '{model}'")

def print_legend():
    print("-------------------------------------------------------------------------")
    print(f"Legenda: "+ 
            GRN +"verde=<corretto>"   + RST + ", " + 
            RED +"rosso=<incorretto>" + RST + ", " + 
            YLW +"giallo=<verità>"    + RST)
    print("Info: per ogni malattia sono stampate le probabilità di classificazione")
    print("-------------------------------------------------------------------------")

def load_test_dataset(seed=SEED):
    # caricamento e shuffle del dataset
    dataset = datasets.load_dataset("imagefolder", data_dir=PT_testing_dataset_dir)
    dataset = dataset.shuffle(seed=seed)

    # split del dataset
    dataset = dataset['train'].train_test_split(test_size=0.2)
    original_test_dataset = dataset['test'].train_test_split(test_size=0.5)['test']

    # preprocessing dei dati
    tot_examples = original_test_dataset.num_rows
    test_dataset_preprocessed = original_test_dataset.map(ViTMAE.preprocess_batch, batched=True, batch_size=4, num_proc=5)
    test_dataset_batched = test_dataset_preprocessed.batch(batch_size=8, num_proc=5)

    return test_dataset_batched, tot_examples

def test_vitmae(checkpoint_to_load):

    # impostazione del seed per la riproducibilità
    set_seed(SEED)

    # caricamento del dataset di test
    test_dataset_batched, tot_examples = load_test_dataset(seed=SEED)

    # caricamento del modello
    model = ViTMAE.ViTMAEForImageClassification()
    model.load_state_dict(torch.load(checkpoint_to_load))

    # impostazione del modello in modalità di valutazione
    model.eval()

    # mappa delle malattie
    disease_map = ['AMD','DME','ERM','NO','RAO','RVO','VID']

    # stampa della legenda
    print_legend()

    buffer = []
    # testing del modello
    with torch.no_grad():
        batch_count = 0
        tot_correct = 0
        for batch in test_dataset_batched:

            # prepara gli input
            inputs = torch.tensor(batch['pixel_values'])

            # esegui il forward pass
            outputs = model(inputs)
            logits = outputs['logits']
            probs = logits.softmax(dim=-1)

            # converte i tensori in liste per il confronto
            probs_indices = probs.argmax(dim=-1)
            truths = batch['label']

            buffer.append(f"batch #{batch_count}\n")
            buffer.append(f"batch size: {len(batch['pixel_values'])}\n")

            # confronta le previsioni con le verità e stampa i risultati
            for i, (pred, truth) in enumerate(zip(probs_indices, truths)):
                buffer.append(f"{i+1}) ")

                # conteggio delle previsioni corrette
                if pred == truth: tot_correct += 1

                # stampa le probabilità per ogni malattia
                for j, disease in enumerate(disease_map):

                    # colore verde se corretto, rosso se sbagliato, giallo se verità
                    if pred == truth and pred==j: 
                        buffer.append(GRN + f"{disease:<3s}:{probs[i][j]*100:6.2f}% " + RST)
                    elif pred != truth and pred==j: 
                        buffer.append(RED + f"{disease:<3s}:{probs[i][j]*100:6.2f}% " + RST)
                    elif pred != truth and truth==j: 
                        buffer.append(YLW + f"{disease:<3s}:{probs[i][j]*100:6.2f}% " + RST)
                    else:
                        buffer.append(f"{disease:<3s}:{probs[i][j]*100:6.2f}% ")

                    # separatore tra le malattie
                    if j < len(disease_map) - 1: buffer.append(" | ")
                buffer.append("\n")

            sys.stdout.write("\n" + ''.join(buffer) + "\n")
            buffer.clear()
            batch_count += 1

        # calcolo dell'accuratezza
        print_legend()
        print(BLD + f"Predizioni corrette: {tot_correct} / {tot_examples}" + RST)
        print(BLD + f"Accuratezza: {tot_correct / tot_examples * 100:.2f}%" + RST)
