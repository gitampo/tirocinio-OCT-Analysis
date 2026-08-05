from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent / 'app'))

from deeplearning.datasets import OCTDL


def test_unknown_label_is_mapped_without_crashing(tmp_path):
    dataset_root = tmp_path / 'retinal-oct-c8'
    (dataset_root / 'DR').mkdir(parents=True)
    (dataset_root / 'DR' / 'img.png').write_bytes(b'fake')

    labels = OCTDL.get_task_labels(task_name='full', dataset_root=dataset_root)
    assert 'DR' in labels
    assert OCTDL.label2id('DR', task_name='full', dataset_root=dataset_root) == labels.index('DR')
