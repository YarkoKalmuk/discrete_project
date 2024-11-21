"""main.py module"""
import argparse

def read_file(filename: str) -> list[ dict[tuple[str, str]: set[tuple[str, str, int]]],
                                     set[tuple[tuple[str, str], tuple[str, str], int]]]:
    """
    Reads a csv file and returns a list with first el as dictionary with keys as tuples
    containing type of place and its name and values as set of connected
    places as tuples of type of place and its name and int as a road lenght, 
    and second element in list is set of blocked roads.

    :param filename: str, A file name to read from

    :return:list[ dict[tuple[str, str], set[ tuple[tuple[str, str], tuple[str, str]]]], where
        - first el of list is a dictionary with type and name of place as keys and
    type, name of connected places and distance between them as values,
        - second el is a set of blocked roads, as tuples of tuple of first
    place and its type and another tuple as second place, its name and lenght of the road.

    Example:

    Зв'язки:
село A, місто B, 10
місто B, обласний центр D, 15
село A, село C, 5

Заблоковані дороги:
село A, місто B, 10
село C, обласний центр D, 15

    Output:
[
    {
        ("village", "A"): {("city", "B", 10), ("village", "C", 5)},
        ("city", "B"): {("regional_center", "D", 15)},
        ("village", "C"): ("village", "A", 5)
    },
    {
        (("village", "A"), ("city", "B"), 10),
        (("village", "C"), ("regional_center", "D"), 15),
    }
]
    """
    pass


def unconnected_places(info: list[ dict[tuple[str, str], set[tuple[str, str, int]]],
                                     set[tuple[tuple[str, str], tuple[str, str], int]]])\
-> dict[ str: set[tuple[str, str]], str: list[set[ tuple[tuple[str, str], tuple[str, str], int]]] ]:
    """
    Function finds places that are disconnected from regional centers and returns them

    :param info: list[ dict[tuple[str, str], set[ tuple[tuple[str, str], tuple[str, str]]]], where
        - first el of list is a dictionary with type and name of place as keys and
    type, name of connected places and distance between them as values,
        - second el is a set of blocked roads, as tuples of tuple of first
    place and its type and another tuple as second place, its name and lenght of the road.

    :return: dict with keys:
        - "disconnected_places": set of places (type, name) disconnected from regional centers.
        - "connected_components": list of sets of roads, where each road is represented as:
          ((type1, name1), (type2, name2), distance).

    Example:

info = [
    {
        ("village", "A"): {("city", "B", 10), ("village", "C", 5)},
        ("city", "B"): {("regional_center", "D", 15)},
        ("village", "C"): {("village", "A", 5)},
        ("regional_center", "D"): {("city", "B", 15)},
    },
    {
        (("village", "A"), ("city", "B"), 10)
    }
]

    Output:

{
    "disconnected_places": {
        ("village", "A"),
        ("village", "C"),
    },
    "connected_components": [
        {
            (("regional_center", "D"), ("city", "B"), 15)
        },
        {
            (("village", "A"), ("village", "C"), 5)
        }
    ]
}
    """
    pass


def shortest_connection(paths: dict[tuple[str,str]: set[tuple[tuple[str, str], 15]]],
                        blocked: set[tuple[tuple[str, str], tuple[str, str], int]])\
    -> set[tuple[tuple[str, str], tuple[str, str], int]]:
    """
    Input:
    # {
    #     ("village", "A"): {(("city", "B"), 10), (("village", "C"), 5)},
    #     ("city", "B"): {(("regional_center", "D"), 15), (("city", "A"), 10)},
    #     ("village", "C"): {(("village", "A"), 5), (("regional_center", "D"), 8)},
    #     ("regional_center", "D"): {(("city", "B"), 15), (("village", "C"), 8)}
    # },
    {
        ("village", "A"): {("city", "B"), ("village", "C")},
        ("city", "B"): {("regional_center"), ("city", "A")},
        ("village", "C"): {("village", "A"), ("regional_center", "D")},
        ("regional_center", "D"): {("city", "B"), ("village", "C")}
    },
    {
        (("village", "A"), ("city", "B"), 10)
        (("regional_center", "D"), ("village", "C"), 8)
    }

    Output:
    {
        (("regional_center", "D"), ("village", "C"), 8)
    }
    """
    blocked = blocked.copy()
    restored = set()
    while len(blocked) > 0:
        disconnected, groups = unconnected_places(paths, blocked)
        accessible = groups[0]
        options = []
        for node in accessible:
            for vertice in disconnected:
                if vertice in paths[node]:
                    for block in blocked:
                        if node in block and vertice in block:
                            options.append(block)
        options = sorted(options, key=lambda x: x[2])
        choice = options[0]
        blocked.remove(choice)
        restored.add(choice)
    return restored


def write_to_file(filename : str ) -> None: # plus two arguments as a result of func unconnected_places and shortest_places
    """
    Function writes output to a file

    :param filename: str, A name of the file you want to write to
    :param:
    :param:

    :return : None
    """
    pass

# allows user to run module in terminal
