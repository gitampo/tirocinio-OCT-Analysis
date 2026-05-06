from pathlib import Path
from configs.paths import PT_checkpoints_dir, PT_datasets_dir
from . import AVAILABLE_MODELS

def available_models():
    return AVAILABLE_MODELS

def available_checkpoints():
    checkpoints = []

    if not Path(PT_checkpoints_dir).exists():
        return []

    model_directories = [
        file for file in Path(PT_checkpoints_dir).iterdir()
        if file.is_dir()
    ]

    for model_dir in model_directories:
        checkpoints += [
            model_dir.stem + '/' + checkpoint_file.stem
            for checkpoint_file in model_dir.iterdir()
            if checkpoint_file.suffix in ('.pth', '.pt')
        ]

    return checkpoints

def available_datasets():
    return ["OCT2017"]