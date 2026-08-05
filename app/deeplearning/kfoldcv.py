import json
import numpy as np
import torch
from torch.utils.data import Dataset, Subset
from transformers import Trainer, TrainingArguments
from pathlib import Path
from PIL import Image
from sklearn.model_selection import StratifiedGroupKFold
from contextlib import contextmanager

from utils.funs import get_available_filename
from utils.log import log_print
from configs.paths import PT_datasets_dir, PT_log_dir
from utils.print import RST, formatted, humanized, print_info, print_separator, print_success_box, print_table
from .training import load_training_args, set_seed
from .datasets import OCTDL
from .testing import (
    compute_metrics_for_test, 
    print_results,
    metrics_names,
    metrics_formats,
)
from . import TRAIN_BATCH_SIZE, TEST_BATCH_SIZE
from .model_factory import (
    load_model, 
    get_preprocessor, 
    get_augmenter
)
from . import DEFAULT_KFOLDS, DEFAULT_SEED, TEST_BATCH_SIZE

class KFoldDataset(Dataset):
    def __init__(self, model_name, seed=DEFAULT_SEED, use_augmentation=True, task_name='full', interest_classes=None):
        dataset_root = Path(PT_datasets_dir.strip())
        candidate_dataset_path = dataset_root / OCTDL.DATASET_NAME

        if candidate_dataset_path.exists():
            path_to_dataset = candidate_dataset_path
        else:
            path_to_dataset = dataset_root

        # ottiene il preprocessore delle immagini
        self.preprocessor = get_preprocessor(model_name)
        self.augmenter = get_augmenter(model_name)
        self.augmentation_enabled = use_augmentation # per abilitare/disabilitare l'augmentation

        parent_path = dataset_root
        
        if parent_path.exists():
            try:
                contents = list(parent_path.iterdir())[:10]
            except Exception:
                pass

        # prova a trovare il dataset in vari percorsi possibili, inclusi quelli tipici di Kaggle
        candidate_roots = []
        for candidate in [
            path_to_dataset,
            dataset_root / OCTDL.DATASET_NAME,
            dataset_root / OCTDL.DATASET_NAME.lower(),
            Path('/kaggle/input/datasets/obulisainaren/retinal-oct-c8'),
            Path('/kaggle/input/retinal-oct-c8'),
            Path('/kaggle/input/datasets/obulisainaren/retinal-oct-c8/retinal-oct-c8'),
            Path('/kaggle/input'),
            Path('/kaggle/working'),
        ]:
            if candidate.exists():
                candidate_roots.append(candidate)

        self.image_paths = []
        for candidate_root in candidate_roots:
            self.image_paths.extend(list(candidate_root.rglob("*.png")))
            self.image_paths.extend(list(candidate_root.rglob("*.jpg")))
            self.image_paths.extend(list(candidate_root.rglob("*.jpeg")))
            if self.image_paths:
                break

        # verifica che siano state trovate immagini
        if not self.image_paths:
            searched_paths = ", ".join(str(path) for path in candidate_roots)
            raise ValueError(
                f"Nessuna immagine trovata nei percorsi: {searched_paths}\n"
                "Verifica che il dataset sia montato correttamente o che il path sia corretto."
            )

        self.task_labels = OCTDL.get_task_labels(task_name=task_name, interest_classes=interest_classes)

        # elementi del dataset (etichette e pazienti corrispondenti alle immagini)
        self.labels = [OCTDL.label2id(self.image_paths[idx].parent.name, task_name=task_name, interest_classes=interest_classes) for idx in range(len(self.image_paths))]
        self.patients = [OCTDL.get_patient_id(self.image_paths[idx].stem) for idx in range(len(self.image_paths))]

        # indici casuali per il rimescolamento del dataset
        self.num_examples = len(self.image_paths)
        rng = np.random.default_rng(seed)
        indices = rng.permutation(self.num_examples)

        # rimescolamento del dataset
        self.image_paths = np.array(self.image_paths)[indices]
        self.labels = np.array(self.labels)[indices]
        self.patients = np.array(self.patients)[indices]

    def __len__(self):
        return len(self.image_paths)

    def __getitem__(self, idx):
        # caricamento dell'immagine
        try:
            image = Image.open(self.image_paths[idx]).convert("RGB")
        except Exception as e:
            print(f"Errore nel caricamento dell'immagine {self.image_paths[idx]}: {e}")
            image = Image.new("RGB", (224, 224))  # crea una dummy image

        # applicazione dell'augmentation (se abilitata)
        if self.augmentation_enabled: 
            image = self.augmenter({"image": [image]})
        else: 
            image = {"image": [image]}

        # preprocessing dell'immagine
        image = self.preprocessor(image)["pixel_values"].squeeze()
        label = self.labels[idx]

        return {"pixel_values": image, "labels": label}
    
    @contextmanager
    def eval_mode(self):
        # Codice eseguito all'ingresso del blocco 'with'
        previous_mode = self.augmentation_enabled
        self.augmentation_enabled = False
        try:
            yield  # esecuzione del blocco 'with'
        finally:
            # Codice eseguito all'uscita dal blocco 'with', anche in caso di eccezioni
            self.augmentation_enabled = previous_mode

class KFoldModelWrapper():
    def __init__(self, model_name, task_name='full', interest_classes=None):
        self.model_name = model_name
        self.model = None
        self.task_name = task_name
        self.interest_classes = interest_classes

    def fit(self, train_dataset):

        task_labels = OCTDL.get_task_labels(task_name=self.task_name, interest_classes=self.interest_classes)

        # caricamento del modello
        self.model = load_model(self.model_name, num_labels=len(task_labels))

        # Adatto il modello CNN al numero di labels corretto
        is_cnn_model = self.model_name in ['resnet18', 'resnet50', 'densenet121', 'efficientnet_b0']
        if is_cnn_model:
            num_labels = len(task_labels)
            # Sostituisci l'ultimo layer con il numero di labels corretto
            if hasattr(self.model, 'classifier'):
                old_classifier = self.model.classifier
                # Assumendo che l'ultimo layer sia un Linear layer
                layers = []
                for layer in old_classifier:
                    if isinstance(layer, torch.nn.Linear) and layer.out_features == 7:
                        # Sostituisci il layer finale
                        layers.append(torch.nn.Linear(layer.in_features, num_labels))
                    else:
                        layers.append(layer)
                self.model.classifier = torch.nn.Sequential(*layers)

        # verifica se è un modello transformers o CNN
        is_transformers_model = self.model_name in ['vit', 'vitmae-light', 'vitmae-heavy']

        if is_transformers_model:
            # Training con Transformers Trainer
            training_args = load_training_args()
            training_args.do_eval = False
            training_args.eval_strategy = "no"

            trainer = Trainer(
                model=self.model,
                args=training_args,
                train_dataset=train_dataset
            )

            print_info("Inizio del training con Transformers...")
            trainer.train()
        else:
            # Training manuale per modelli CNN
            self._train_cnn_model(train_dataset)

    def _train_cnn_model(self, train_dataset):
        """Training loop manuale per modelli CNN"""
        import torch.optim as optim
        from torch.utils.data import DataLoader

        print_info("Inizio del training manuale per modello CNN...")

        # Parametri di training
        num_epochs = 20
        batch_size = TRAIN_BATCH_SIZE
        learning_rate = 1e-4
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        # Sposta il modello su device
        self.model.to(device)

        # Calcola pesi di classe per gestire il dataset sbilanciato
        train_labels = np.array(train_dataset.dataset.labels)[train_dataset.indices]
        class_counts = np.bincount(train_labels, minlength=len(OCTDL.get_task_labels(task_name=self.task_name, interest_classes=self.interest_classes)))
        class_weights = 1.0 / (class_counts + 1e-12)
        class_weights = torch.tensor(class_weights, dtype=torch.float32, device=device)

        # Ottimizzatore e loss function bilanciata
        optimizer = optim.Adam(self.model.parameters(), lr=learning_rate)
        criterion = torch.nn.CrossEntropyLoss(weight=class_weights)

        # DataLoader
        train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)

        # Training loop
        self.model.train()
        for epoch in range(num_epochs):
            epoch_loss = 0.0
            correct = 0
            total = 0

            for batch in train_loader:
                pixel_values = batch['pixel_values'].to(device)
                labels = batch['labels'].to(device)

                # Forward pass
                optimizer.zero_grad()
                outputs = self.model(pixel_values)
                
                # Gestisci output del modello (dict per transformers, tensor per CNN)
                if isinstance(outputs, dict):
                    logits = outputs["logits"]
                    loss = outputs.get("loss")
                    if loss is None:
                        loss = criterion(logits, labels)
                else:
                    logits = outputs
                    loss = criterion(logits, labels)

                # Backward pass
                loss.backward()
                optimizer.step()

                # Statistiche
                epoch_loss += loss.item()
                _, predicted = torch.max(logits.data, 1)
                total += labels.size(0)
                correct += (predicted == labels).sum().item()

            # Log per epoca
            avg_loss = epoch_loss / len(train_loader)
            accuracy = 100 * correct / total
            print_info(f"Epoch {epoch+1}/{num_epochs} - Loss: {avg_loss:.4f}, Accuracy: {accuracy:.2f}%")

    def score(self, val_dataset):
        # verifica se è un modello transformers o CNN
        is_transformers_model = self.model_name in ['vit', 'vitmae-light', 'vitmae-heavy']

        if is_transformers_model:
            # Valutazione con Transformers Trainer
            import tempfile
            trainer = Trainer(
                model=self.model,
                args=TrainingArguments(
                    output_dir=tempfile.mkdtemp(),
                    per_device_eval_batch_size=TEST_BATCH_SIZE,
                    do_train=False,
                    do_eval=True,
                ),
                compute_metrics=compute_metrics_for_test,
            )

            print_info("Inizio della valutazione con Transformers...")
            output = trainer.evaluate(val_dataset)
            return output
        else:
            # Valutazione manuale per modelli CNN
            return self._evaluate_cnn_model(val_dataset)

    def _evaluate_cnn_model(self, val_dataset):
        """Valutazione manuale per modelli CNN"""
        import torch
        from torch.utils.data import DataLoader

        print_info("Inizio della valutazione manuale per modello CNN...")

        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model.to(device)
        self.model.eval()

        # DataLoader per validation
        val_loader = DataLoader(val_dataset, batch_size=TEST_BATCH_SIZE, shuffle=False)

        all_predictions = []
        all_labels = []

        all_logits = []
        all_labels = []

        with torch.no_grad():
            for batch in val_loader:
                pixel_values = batch['pixel_values'].to(device)
                labels = batch['labels'].to(device)

                outputs = self.model(pixel_values)

                # Gestisci output del modello
                if isinstance(outputs, dict):
                    logits = outputs["logits"]
                else:
                    logits = outputs

                all_logits.append(logits.cpu())
                all_labels.extend(labels.cpu().numpy())

        logits = torch.cat(all_logits, dim=0).numpy()
        labels = np.array(all_labels)

        # Calcola le metriche usando la stessa funzione del testing
        metrics = compute_metrics_for_test((logits, labels))

        # Format the output to match Transformers format
        output = {}
        for key, value in metrics.items():
            if key == 'confusion_matrix':
                output['eval_confusion_matrix'] = value
            else:
                output[f'eval_{key}'] = value

        return output

def _compute_subset_class_counts(dataset, subset):
    labels = np.array(dataset.labels)[subset.indices]
    return np.bincount(labels, minlength=len(OCTDL.labels))

def _build_oversampled_subset(dataset, subset, seed=DEFAULT_SEED):
    """
    Esegue random oversampling del subset fino a portare ogni classe
    alla numerosità della classe più frequente del fold.
    """
    rng = np.random.default_rng(seed)

    indices = np.array(subset.indices)
    labels = np.array(dataset.labels)[indices]
    class_to_indices = {
        class_id: indices[labels == class_id]
        for class_id in range(len(dataset.task_labels))
    }

    class_counts = {class_id: len(class_indices) for class_id, class_indices in class_to_indices.items()}
    max_count = max(class_counts.values()) if class_counts else 0

    oversampled_indices = []
    for class_id, class_indices in class_to_indices.items():
        if len(class_indices) == 0:
            continue

        oversampled_indices.extend(class_indices.tolist())
        missing = max_count - len(class_indices)
        if missing > 0:
            sampled = rng.choice(class_indices, size=missing, replace=True)
            oversampled_indices.extend(sampled.tolist())

    rng.shuffle(oversampled_indices)
    return Subset(dataset, oversampled_indices)

def preprocess_final_results(outputs, classes_outputs, task_labels):

    # calcolo della media delle metriche sui vari fold
    averaged_metrics = []
    for key in outputs[0].keys():
        metric_name = key.replace('eval_','')
        if metric_name not in metrics_names: continue # ignora le statistiche che non sono metriche

        # calcolo di media e deviazione standard per la metrica corrente
        mean = np.mean([output[key] for output in outputs]).item()
        dev_std = np.std([output[key] for output in outputs]).item()

        # memorizzazione della metrica formattata (per la stampa)
        averaged_metrics.append((
            humanized(metric_name),
            formatted(mean, metrics_formats[metric_name]),
            formatted(dev_std, metrics_formats[metric_name]), 
        ))

    # calcolo della media delle metriche per classe sui vari fold
    averaged_classes_metrics = []
    for key in classes_outputs[0].keys():
        metric_name = key.replace('eval_','')
        if metric_name not in metrics_names: continue # ignora le statistiche che non sono metriche

        means = []
        dev_stds = []
        for label in OCTDL.labels:
            # calcolo di media e deviazione standard per la metrica e per la classe corrente
            mean = np.mean([class_output[key][task_labels.index(label)] for class_output in classes_outputs]).item()
            dev_std = np.std([class_output[key][task_labels.index(label)] for class_output in classes_outputs]).item()

            # medie e deviazioni standard per ogni classe
            means.append(formatted(mean, metrics_formats[metric_name]))
            dev_stds.append(formatted(dev_std, metrics_formats[metric_name]))
        
        # memorizzazione della metrica formattata (per la stampa)
        averaged_classes_metrics.append(
            (humanized(metric_name.replace('classes_','')), 
             *[ f"{mean} (±{dev_std})" for mean, dev_std in zip(means, dev_stds)]
             ))

    return sorted(averaged_metrics), sorted(averaged_classes_metrics)

def print_final_results(outputs, classes_outputs, task_labels):

    # preprocessing dei risultati (formattazione e cambio rappresentazione) e stampa
    metrics_rows, classes_rows = preprocess_final_results(outputs, classes_outputs, task_labels)
    print_table(headings=["METRICA", "VALORE MEDIO", "DEV.STD."], rows=metrics_rows)
    print_table(headings=["", *task_labels], rows=classes_rows)

def print_class_distribution_per_fold(gkf, dataset):
    from functools import reduce

    folds_distributions = []
    tot = len(dataset.labels)
    for fold_idx, (train_idx, val_idx) in enumerate(gkf.split(X=dataset.image_paths, y=dataset.labels, groups=dataset.patients), start=1):

        # subset di training e di validazione
        fold_dataset_train = Subset(dataset, train_idx)
        fold_dataset_val = Subset(dataset, val_idx)

        # funzione per contare le occorrenze delle classi nel dataset
        def count_occurrences(label, fold_dataset):
            labels = [dataset.labels[i] for i in fold_dataset.indices]
            value = reduce(lambda acc, x: acc + (1 if x == dataset.task_labels.index(label) else 0), labels, 0)
            return  value

        # calcolo della distribuzione delle classi per il fold attuale
        train_counts = []
        val_counts = []
        for label in OCTDL.labels:
            # memorizzazione dei conteggi di ciascuna classe per il fold attuale
            train_counts.append(count_occurrences(label, fold_dataset_train))
            val_counts.append(count_occurrences(label, fold_dataset_val))

        # memorizzazione della distribuzione di tutte le classi classi per il fold attuale
        format_str = lambda count: "%-4d %7s" %  (count, f"({count/tot*100:.2f}%)")
        total = lambda l : reduce(lambda acc, x: acc + x, l, 0)
        folds_distributions.append((f"fold {fold_idx} - train", *[format_str(count) for count in train_counts], "="+format_str(total(train_counts))))
        folds_distributions.append((f"fold {fold_idx} - val", *[format_str(count) for count in val_counts], "="+format_str(total(val_counts))))
        folds_distributions.append((*['' for _ in range(len(dataset.task_labels)+2)],)) # riga vuota

    # stampa della distribuzione delle classi per ogni fold
    print_table(headings=["", *dataset.task_labels, ""], rows=folds_distributions)

def kfold_cv(model_name, num_folds=DEFAULT_KFOLDS, seed=DEFAULT_SEED, use_augmentation=True, oversample_rare=False, task_name='full', interest_classes=None):
    # impostazione del seed per la ripoducibilità
    set_seed(seed)

    # caricamento del dataset per la K-fold cross validation (Dataset custom)
    dataset = KFoldDataset(model_name, seed=seed, use_augmentation=use_augmentation, task_name=task_name, interest_classes=interest_classes)

    # istanziazione delle K-fold (StratifiedGroupKFold per mantenere le classi bilanciate
    # tra i fold e evitare data leakage tra pazienti)
    gkf = StratifiedGroupKFold(n_splits=num_folds)

    # funzione per stampare la distribuzione delle classi in ogni fold
    print_class_distribution_per_fold(gkf, dataset)

    # preparazione del file di log
    log_file = "kfoldcv.log"
    log_file = get_available_filename(PT_log_dir, log_file)
    log_filestem = Path(log_file).stem
    log_print(log_filestem, 
              f"MODEL: {model_name}           \n"
              f"KFOLDS: {num_folds}           \n"
              f"SEED: {seed}                  \n"
              f"DATASET: {OCTDL.DATASET_NAME} \n"
              f"TASK: {task_name} \n"
              f"INTEREST_CLASSES: {interest_classes or []} \n"
              f"AUGMENTATION: {use_augmentation} \n"
              f"OVERSAMPLE_RARE: {oversample_rare} \n")

    # K-fold cross validation 
    fold_idx = 1
    outputs = []
    classes_outputs = []
    for train_idx, val_idx in gkf.split(X=dataset.image_paths, y=dataset.labels, groups=dataset.patients):
        print_info(f"Fold {fold_idx}/{num_folds}")
        log_print(log_filestem, f"Fold {fold_idx}/{num_folds}")

        # creazione dei subset per il training e la validazione
        fold_dataset_train = Subset(dataset, train_idx)
        fold_dataset_val = Subset(dataset, val_idx)

        # opzionale: oversampling delle classi rare nel train fold
        if oversample_rare:
            before_counts = _compute_subset_class_counts(dataset, fold_dataset_train)
            fold_dataset_train = _build_oversampled_subset(dataset, fold_dataset_train, seed=seed + fold_idx)
            after_counts = _compute_subset_class_counts(dataset, fold_dataset_train)

            rows = []
            for class_id, class_name in enumerate(OCTDL.labels):
                rows.append((class_name, int(before_counts[class_id]), int(after_counts[class_id])))

            print_table(headings=["CLASSE", "TRAIN PRIMA", "TRAIN DOPO"], rows=rows)

        # addestramento (fit per il fold attuale)
        model = KFoldModelWrapper(model_name, task_name=task_name, interest_classes=interest_classes)
        model.fit(fold_dataset_train)

        # valutazione (disabilita l'augmentation durante la valutazione)
        with dataset.eval_mode():  
            output = model.score(fold_dataset_val)

        # risultati del fold
        print_results(output, labels=dataset.task_labels)
        log_print(log_filestem, f"Risultati del fold {fold_idx}: {output}")
        print_separator(70)

        # rimozione della matrice di confusione dai risultati
        if 'eval_confusion_matrix' in output:
            del output['eval_confusion_matrix']  # non serve per il calcolo della media

        # separa i risultati delle metriche per classe (se presenti)
        keys = list(output.keys())
        class_output = {k:output.pop(k) for k in keys if k.startswith('eval_classes_')}
        
        # memorizza i risultati del fold
        classes_outputs.append(class_output)
        outputs.append(output)
        fold_idx += 1

    # stampa della media e della deviazione standard delle metriche
    print_success_box(f"K-Fold Cross Validation ({num_folds} folds) completata!")
    log_print(log_filestem, f"Risultati finali: {outputs}")
    print_final_results(outputs, classes_outputs)