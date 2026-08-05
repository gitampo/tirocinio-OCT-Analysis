from pathlib import Path
import os
import sys

script_dir = Path(__file__).parent.absolute()
app_dir = script_dir / 'app'
os.chdir(app_dir)
sys.path.insert(0, str(app_dir))

from deeplearning.datasets import OCTDL


def test_interest_vs_rest_mapping():
    task_labels = OCTDL.get_task_labels(
        task_name='interest_vs_rest',
        interest_classes=['AMD', 'DME']
    )

    assert task_labels == ['AMD', 'DME', 'ALL_REST']
    assert OCTDL.label2id('AMD', task_name='interest_vs_rest', interest_classes=['AMD', 'DME']) == 0
    assert OCTDL.label2id('NO', task_name='interest_vs_rest', interest_classes=['AMD', 'DME']) == 2
