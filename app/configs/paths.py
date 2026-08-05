### Modulo per la configurazione dei path (PT = Path)
import os
from pathlib import Path

# Prende il percorso assoluto della cartella dell'applicazione
app_dir = Path(__file__).parent.parent.absolute()

PT_app_logo = str(app_dir / 'assets/app_logo.png')
PT_query_dir = str(app_dir / 'database/queries/')
PT_database = str(app_dir / 'database/data/octanalysis.db')
PT_images_dir = str(app_dir / 'database/data/images/')
PT_trainer_output_dir = str(app_dir / 'deeplearning/data/trainer_output/')
PT_checkpoints_dir = str(app_dir / 'deeplearning/data/checkpoints/')
PT_log_dir = str(app_dir / 'logs/')

# -------------------------
# DATASET (KAGGLE + LOCAL)
# -------------------------
def _resolve_default_dataset_root():
    known_candidates = [
        "/kaggle/input/octdl",
        "/kaggle/input/octdl-optical-coherence-tomography-dataset",
        "/kaggle/input/datasets/orvile/octdl-optical-coherence-tomography-dataset",
        "/kaggle/input/datasets/obulisainaren/retinal-oct-c8",
        "/kaggle/input/retinal-oct-c8",
        "/kaggle/input/datasets/obulisainaren/retinal-oct-c8/retinal-oct-c8",
        "/kaggle/input/OCTDL",
        "/kaggle/input/OCTDL/OCTDL",
        "/kaggle/input/octdl/OCTDL",
        "/kaggle/input/datasets/OCTDL",
        "/kaggle/working/OCTDL",
        str(app_dir / 'deeplearning/data/datasets/'),
        str(app_dir / 'deeplearning/data/datasets/OCTDL'),
    ]

    for candidate in known_candidates:
        if os.path.exists(candidate):
            return candidate

    return str(app_dir / 'deeplearning/data/datasets/')


PT_datasets_dir = _resolve_default_dataset_root()
