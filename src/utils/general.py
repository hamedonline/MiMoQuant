from uuid import uuid4
from collections import OrderedDict


def pick_color(c_name: str) -> tuple[int, int, int]:
    """
    Returns the RGB values associated with a color name.

    Args:
        c_name (str): The color name.

    Returns:
        tuple[int, int, int]: The RGB values as a tuple with each component
        in the range 0 to 255. Unknown color names default to white.
    """
    color_dict: dict[str, tuple[int, int, int]] = {
        'red': (255, 0, 0),
        'green': (0, 255, 0),
        'blue': (0, 0, 255),
        'yellow': (255, 255, 0),
        'purple': (255, 0, 255),
        'turquoise': (0, 255, 255),
        'black': (0, 0, 0),
        'white': (255, 255, 255)
    }
    return color_dict.get(c_name, (255, 255, 255))


def generate_random_unique_string(length, lowercase=False):
    """
    Generates a random unique identifier of the requested length.

    Args:
        length (int): The number of characters to return.
        lowercase (bool, optional): Whether to return lowercase characters.
            Defaults to ``False``.

    Returns:
        str: A hexadecimal unique identifier.
    """
    if lowercase:
        return uuid4().hex[:length].lower()
    return uuid4().hex[:length].upper()


def is_empty(obj):
    """
    Checks whether an object is empty.

    Args:
        obj (object): An object supporting Python's truth-value testing,
            such as a list, dictionary, tuple, set, or string.

    Returns:
        bool: ``True`` if the object is empty; otherwise, ``False``.
    """
    return not obj


def is_divisible(num_value, divisor):
    """
    Checks whether a number is divisible by a divisor.

    Args:
        num_value (int | float): The number to test.
        divisor (int | float): The divisor to use.

    Returns:
        bool: ``True`` if ``num_value`` is evenly divisible by ``divisor``;
        otherwise, ``False``.
    """
    return not bool(num_value % divisor)


def is_odd(int_value):
    """
    Checks whether an integer is odd.

    Args:
        int_value (int): The integer to test.

    Returns:
        bool: ``True`` if ``int_value`` is odd; otherwise, ``False``.
    """
    return not is_divisible(int_value, 2)


def is_even(int_value):
    """
    Checks whether an integer is even.

    Args:
        int_value (int): The integer to test.

    Returns:
        bool: ``True`` if ``int_value`` is even; otherwise, ``False``.
    """
    return is_divisible(int_value, 2)


def count_decimal_digits(num: float | int) -> int:
    """
    Returns the count of digits after the decimal point for a given number.
    """
    if not isinstance(num, (int, float)):
        raise TypeError('The input must be either an integer or a float number.')
    return 0 if isinstance(num, int) else len(str(num).split('.')[-1])


def sort_dict(dict_obj, sort_by='values', order='asc', slicer=None) -> dict:
    """
    Sorts a dictionary by its keys or values.

    Args:
        dict_obj (dict): The dictionary to sort.
        sort_by (str, optional): Whether to sort by ``'keys'`` or
            ``'values'``. Defaults to ``'values'``.
        order (str, optional): The sort order, either ``'asc'`` or ``'desc'``.
            Defaults to ``'asc'``.
        slicer (slice, optional): A slice selecting items from the sorted
            dictionary. If ``None``, all items are included. Defaults to
            ``None``.

    Returns:
        dict: A dictionary containing the sorted items.
    """
    reverse_order = False if order == 'asc' else True
    if slicer is None:
        slicer = slice(len(dict_obj))
    if sort_by == 'values':
        return {k:v for k, v in sorted(dict_obj.items(), key=lambda item: item[1], reverse=reverse_order)[slicer]}
    return {k:dict_obj[k] for k in sorted(dict_obj.keys(), reverse=reverse_order)[slicer]}


def merge_dicts(*dict_args):
    """
    Given any number of dictionaries, shallow copy and merge into a new dict,
    precedence goes to key-value pairs in latter dictionaries.
    """
    result = {}
    for dictionary in dict_args:
        result.update(dictionary)
    return result


def has_duplicates(list_obj):
    """
    Checks whether a list contains duplicate items.

    Args:
        list_obj (list): The list to check.

    Returns:
        bool: ``True`` if the list contains duplicate items; otherwise,
        ``False``.
    """
    return len(list_obj) != len(set(list_obj))


def remove_duplicates(list_obj, maintain_order=True):
    """
    Removes duplicate values from a list.

    The items in ``list_obj`` should be of the same type.

    Args:
        list_obj (list): The list from which to remove duplicates.
        maintain_order (bool, optional): Whether to preserve the original
            order of items. Defaults to ``True``.

    Returns:
        list: A list containing only unique items.
    """
    if not is_empty(list_obj):
        if isinstance(list_obj[0], dict): # if list items are of dictionary type
            return remove_duplicates_from_dict_list(list_obj, maintain_order=maintain_order)
        else:
            if maintain_order:
                #return list(dict.fromkeys(list_obj)) # Python 3.7+
                return list(OrderedDict.fromkeys(list_obj))
            else:
                return list(set(list_obj))
    return []


def remove_duplicates_from_dict_list(dict_list, maintain_order=True):
    """
    Removes duplicate dictionaries from a list.

    Args:
        dict_list (list[dict]): The list of dictionaries from which to remove
            duplicates.
        maintain_order (bool, optional): Whether to preserve the original
            order of dictionaries. Defaults to ``True``.

    Returns:
        list[dict]: A list containing only unique dictionaries.
    """
    if maintain_order:
        seen = set()
        output_list = []
        for d in dict_list:
            t = tuple(sorted(d.items()))
            if t not in seen:
                seen.add(t)
                output_list.append(d)
        return output_list
    else:
        return [dict(t) for t in {tuple(d.items()) for d in dict_list}]


def compact_list(list_obj):
    """
    Removes falsey values from a list.

    This includes values such as ``False``, ``None``, ``0``, and empty
    strings.

    Args:
        list_obj (list): The list to compact.

    Returns:
        list: A list containing only truthy values from ``list_obj``.
    """
    return list(filter(bool, list_obj))
