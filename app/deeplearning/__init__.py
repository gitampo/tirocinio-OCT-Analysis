from transformers import TrainingArguments
from configs.paths import PT_trainer_output_dir

AVAILABLE_MODELS = ['vitmae','other']
SEED = 42

# configurazione degli argomenti da passare al trainer di vitmae
vitmae_training_args = TrainingArguments(
    output_dir=PT_trainer_output_dir,
    per_device_train_batch_size=4,
    per_device_eval_batch_size=4,
    save_strategy="epoch",
    eval_strategy="epoch",
    logging_steps=100,
    num_train_epochs=10,
    load_best_model_at_end=False
)