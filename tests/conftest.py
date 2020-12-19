import json
import pytest
import os


@pytest.fixture
def har_data():
    """
    Given a HAR file name, returns a ``dict`` of this data from the
    corresponding file name in tests/data
    """
    data_path = os.path.abspath(__file__ + '/../data/')

    def load_doc(filename):
        full_path = os.path.join(data_path, filename)
        with open(full_path) as f:
            return json.loads(f.read())
    return load_doc


@pytest.fixture
def header_types():
    """
    Just returns all the headers we need to test
    """
    return ['content-length', 'content-encoding', 'accept-ranges', 'vary',
            'connection', 'via', 'cache-control', 'date', 'content-type', 'age']
