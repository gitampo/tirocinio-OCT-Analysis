labels = ['CNV', 'DME', 'DRUSEN', 'NORMAL']

DATASET_NAME = 'OCT2017'


def id2label(id):
    return labels[id]


def label2id(label):
    return labels.index(label)


def get_patient_id(image_name):
    """Estrae un pseudo patient id dal nome del file."""
    parts = image_name.split('-')
    if len(parts) >= 2:
        return parts[1]
    return image_name
