from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "app"))

from configs import paths


def test_find_octdl_dataset_root_from_nested_kaggle_like_structure(tmp_path):
    dataset_root = tmp_path / "retinal-oct-c8"
    (dataset_root / "AMD").mkdir(parents=True)
    (dataset_root / "DME").mkdir(parents=True)
    (dataset_root / "OCTDL_labels.csv").write_text(
        "file_name,patient_id\namd_1.png,1\n",
        encoding="utf-8",
    )
    (dataset_root / "AMD" / "amd_1.png").write_bytes(b"fake")

    result = paths.find_octdl_dataset_root(search_roots=[tmp_path])

    assert result == dataset_root
