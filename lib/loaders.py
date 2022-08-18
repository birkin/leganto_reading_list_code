import csv


def load_csv( filepath: str ) -> list:
    """ Load courses CSV file into a list of dictionaries. """
    rows = []
    with open( filepath ) as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    return rows