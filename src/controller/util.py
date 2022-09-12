"""
    Utilities
"""

from typing import MutableMapping

def print_dict(d: dict, indent=0):
    """Prints a dictionary with its keys and values in a nested indented manner. """
    if isinstance(d, dict):
        for key, value in d.items():
            print('\t'*indent, key, ': ')
            print_dict(value, indent+1)
    else:
        print('\t'*indent, d)


def flatten_dict(d: MutableMapping, parent_key: str = "", sep: str = "."):
    items = []
    for k, v in d.items():
        new_key = parent_key + sep + k if parent_key else k
        if isinstance(v, MutableMapping):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)
