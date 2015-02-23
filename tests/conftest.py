import json
import pytest
import os


@pytest.fixture
def har_data(request):
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
