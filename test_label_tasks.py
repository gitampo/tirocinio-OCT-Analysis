import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "app"))

from deeplearning.utils import build_task_label_config


def test_full_task_keeps_original_labels():
    labels, mapping = build_task_label_config("OCTDL", task_name="full")

    assert labels == ["AMD", "DME", "ERM", "NO", "RAO", "RVO", "VID"]
    assert mapping == {
        "AMD": 0,
        "DME": 1,
        "ERM": 2,
        "NO": 3,
        "RAO": 4,
        "RVO": 5,
        "VID": 6,
    }


def test_interest_rest_task_collapses_non_interest_to_rest():
    labels, mapping = build_task_label_config(
        "OCTDL",
        task_name="interest-rest",
        interest_labels=["AMD", "DME", "ERM"],
    )

    assert labels == ["AMD", "DME", "ERM", "ALL_REST"]
    assert mapping["AMD"] == 0
    assert mapping["DME"] == 1
    assert mapping["ERM"] == 2
    assert mapping["NO"] == 3
    assert mapping["RAO"] == 3
    assert mapping["RVO"] == 3
    assert mapping["VID"] == 3
