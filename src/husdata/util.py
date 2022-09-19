import enum

def print_data(data: dict, ID: enum.Enum) -> None:
    """Prints translated data if exist

    Args:
        data: Raw data returned from request as a dictionary
        ID: Index registry for your controller as  a registry
    """
    for id in ID:
        print(id.name, ":", data.get(id, None))

def clamp_value(value: float, min_value: float, max_value: float):
    if value > max_value:
        return max_value
    elif value < min_value:
        return min_value
    else:
        return value