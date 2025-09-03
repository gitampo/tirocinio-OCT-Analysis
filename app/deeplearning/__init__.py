# configurazione delle variabili del package
AVAILABLE_MODELS = ['vitmae-light', 'vitmae-heavy']
CHECKPOINT_FOR_DISEASE_INFERENCE = 'vitmae-light/base'

DEFAULT_DATASET = 'OCTDL'
DEFAULT_SPLIT = (0.8, 0.1, 0.1)  # train, eval, test split
DEFAULT_SEED = 42 # seed per la riproducibilità
DEFAULT_KFOLDS = 2 # numero di fold per il K-Fold Cross Validation

PREPROCESS_BATCH_SIZE = 8
TRAIN_BATCH_SIZE = 8
TEST_BATCH_SIZE = 8

NUM_PROC = 3 # numero di processi per il data loading