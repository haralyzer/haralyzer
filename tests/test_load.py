import os

from haralyzer import load_file, load_json, HarParser

data_path = os.path.abspath(__file__ + '/../data/')


def test_load_file():
    parser = load_file(f"{data_path}/firefox.har")
    assert isinstance(parser, HarParser)


def test_load_json():
    with open(f"{data_path}/firefox.har", "r") as infile:
        data = infile.read()
    parser = load_json(data)
    assert isinstance(parser, HarParser)
