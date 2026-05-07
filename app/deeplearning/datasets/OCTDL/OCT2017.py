from pathlib import Path
from configs.paths import PT_datasets_dir

DATASET_NAME = 'OCT2017 '

labels = ['CNV', 'DME', 'DRUSEN', 'NORMAL']

def id2label(id):
    return labels[id]

def label2id(label):
    return labels.index(label)

def get_patient_id(image_name):
    """
    Estrae un pseudo patient id dal filename.
    Esempio:
    CNV-1016042-1 -> 1016042
    """
    try:
        return image_name.split('-')[1]
    except:
        return image_name