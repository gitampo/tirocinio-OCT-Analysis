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

IMAGE_EXTENSIONS = ('.png', '.jpg', '.jpeg')
DATASET_NAME_HINTS = ('octdl', 'retinal', 'retinal-oct', 'retinal-oct-c8', 'c8')


def _path_has_dataset_signals(path: Path) -> bool:
    if not path.exists() or not path.is_dir():
        return False

    if any(path.glob(f'*{ext}') for ext in IMAGE_EXTENSIONS):
        return True

    if (path / 'OCTDL_labels.csv').exists():
        return True

    return any((path / child).exists() for child in ['AMD', 'DME', 'ERM', 'NO', 'RAO', 'RVO', 'VID'])


def find_octdl_dataset_root(search_roots=None):
    roots = []
    if search_roots:
        roots.extend([Path(root) for root in search_roots if root])
    else:
        roots.extend([
            Path('/kaggle/input'),
            Path('/kaggle/working'),
            Path.cwd(),
            app_dir,
        ])

    for root in roots:
        if not root.exists():
            continue

        if _path_has_dataset_signals(root):
            return root

        for child in sorted(root.iterdir()):
            if not child.is_dir():
                continue
            name = child.name.lower()
            if any(hint in name for hint in DATASET_NAME_HINTS) and _path_has_dataset_signals(child):
                return child

    for root in roots:
        if not root.exists():
            continue

        for candidate in sorted(root.rglob('*')):
            if not candidate.is_dir():
                continue
            name = candidate.name.lower()
            if any(hint in name for hint in DATASET_NAME_HINTS) and _path_has_dataset_signals(candidate):
                return candidate

    return None


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
        candidate_path = Path(candidate)
        if candidate_path.exists() and _path_has_dataset_signals(candidate_path):
            return str(candidate_path)

    discovered = find_octdl_dataset_root()
    if discovered is not None:
        return str(discovered)

    return str(app_dir / 'deeplearning/data/datasets/')


PT_datasets_dir = _resolve_default_dataset_root()
