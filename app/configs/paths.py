### Modulo per la configurazione dei path (PT = Path)
import os
from pathlib import Path

# Get the app directory (where this file is located: app/configs/paths.py)
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
if os.path.exists("/kaggle/input"):
    # Cerca il dataset OCTDL in posizioni Kaggle note
    if os.path.exists("/kaggle/input/octdl"):
        PT_datasets_dir = "/kaggle/input/octdl"
    elif os.path.exists("/kaggle/input/octdl-optical-coherence-tomography-dataset"):
        PT_datasets_dir = "/kaggle/input/octdl-optical-coherence-tomography-dataset"
    elif os.path.exists("/kaggle/input/datasets/orvile/octdl-optical-coherence-tomography-dataset"):
        PT_datasets_dir = "/kaggle/input/datasets/orvile/octdl-optical-coherence-tomography-dataset"
    else:
        # Se niente è trovato, fallback a local
        PT_datasets_dir = str(app_dir / 'deeplearning/data/datasets/')
else:
    PT_datasets_dir = str(app_dir / 'deeplearning/data/datasets/')
