from transformers import TrainingArguments, EarlyStoppingCallback
from configs.paths import PT_trainer_output_dir

AVAILABLE_MODELS = ['vitmae-light', 'vitmae-heavy']
SEED = 42

# configurazione degli argomenti da passare al trainer di vitmae
vitmae_training_args = TrainingArguments(
    output_dir=PT_trainer_output_dir,
    per_device_train_batch_size=8,
    per_device_eval_batch_size=8,
    save_strategy="epoch",
    eval_strategy="epoch",
    logging_steps=100,
    num_train_epochs=20,
    load_best_model_at_end=False,
    metric_for_best_model="accuracy"
)

# lista delle callbacks da passare al trainer di vitmae
vitmae_callbacks = [
    # EarlyStoppingCallback(early_stopping_patience=3)
]

# metriche da passare al trainer di vitmae
def vitmae_compute_metrics(eval_pred):
    predictions, labels = eval_pred
    predictions = predictions.argmax(axis=-1)
    acc = (predictions == labels).mean()
    return {"accuracy": acc}