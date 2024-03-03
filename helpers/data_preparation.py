import os
import csv

ABS_DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'Data')


def get_data(dataset="100_animals_plants"):
    """
    Wrapper for getting correct data for given dataset.

    :param dataset: The dataset to be used
                    Default: 100_animals_plants
                    Options: 100_animals_plants
    :return: Depending on dataset (e.g. tuple of sent, label)
    """
    for filename in os.listdir(ABS_DATA_DIR):
        if filename.split(".")[0] == dataset:
            if filename.split(".")[1] == "csv":
                return get_binary_from_csv(os.path.join(ABS_DATA_DIR, filename))
            elif filename.split(".")[1] == "txt":
                raise NotImplemented

    raise AssertionError(f"Dataset {dataset} cannot found.")




def get_binary_from_csv(path):
    """
    For CSV-files containing sentences and the corresponding labels.
    :param path: The path for the dataset
    :return: List of tuples containing the sentence and its label
    """
    data = []
    with open(os.path.join(path), "r") as f:
        csvreader = csv.reader(f)
        for row in csvreader:
            if not row[0].startswith('#'):
                data.append(row)

    return [tuple(x) for x in data]


if __name__ == "__main__":
    print(get_data())

