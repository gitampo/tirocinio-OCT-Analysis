# configurazione delle variabili del package
AVAILABLE_MODELS = ['vitmae-light', 'vitmae-heavy']
CHECKPOINT_FOR_DISEASE_INFERENCE = 'vitmae-light/base'

DEFAULT_DATASET = 'OCTDL'
DEFAULT_SPLIT = (0.8, 0.1, 0.1)  # train, eval, test split

PREPROCESS_BATCH_SIZE = 8
TRAIN_BATCH_SIZE = 8
TEST_BATCH_SIZE = 8

NUM_PROC = 5 # numero di processi per il data loading
SEED = 42 # fissare il seed per la riproducibilità