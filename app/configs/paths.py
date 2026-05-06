### Modulo per la configurazione dei path (PT = Path)
import os

PT_app_logo = 'assets/app_logo.png'
PT_query_dir = 'database/queries/'
PT_database = 'database/data/octanalysis.db'
PT_images_dir = 'database/data/images/'
PT_trainer_output_dir = 'deeplearning/data/trainer_output/'
PT_checkpoints_dir = 'deeplearning/data/checkpoints/'
PT_log_dir = 'logs/'

# -------------------------
# DATASET (KAGGLE + LOCAL)
# -------------------------
if os.path.exists("/kaggle/input"):
    PT_datasets_dir = "/kaggle/input/datasets/paultimothymooney/kermany2018/oct2017/OCT2017" 
else:
    PT_datasets_dir = 'deeplearning/data/datasets/'
