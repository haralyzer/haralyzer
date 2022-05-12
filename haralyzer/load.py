"""Utility functions to easily load files"""
import json

from .assets import HarParser


def load_file(file: [str, bytes]) -> HarParser:
    """
    Function to read a har file
    :param file: Path to har file or bytes of har file
    :type file: [str, bytes]
    :return: HarParser Object
    :rtype HarParser
    """
    with open(file=file, mode="r", encoding="utf-8") as infile:
        return HarParser(json.load(infile))


def load_json(data: [str, bytes]) -> HarParser:
    """
    Function to load json as a HarParser
    :param data: Input json string or bytes
    :type  data: [str, bytes]
    :return: HarParser Object
    :rtype HarParser
    """
    return HarParser(json.loads(s=data))
