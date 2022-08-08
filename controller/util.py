"""
    Utilities
"""

def print_dict(d: dict, indent=0):
    """Prints a dictionary with its keys and values in a nested indented manner. """
    if isinstance(d, dict):
        for key, value in d.items():
            print('\t'*indent, key, ': ')
            print_dict(value, indent+1)
    else:
        print('\t'*indent, d)


