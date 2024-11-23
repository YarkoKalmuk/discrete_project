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
        ("village", "A"): {("city", "B"), ("village", "C")},
        ("city", "B"): {("regional_center", "D")},
        ("village", "C"): ("village", "A")
    },
    {
        (("village", "A"), ("city", "B"), 10),
        (("village", "C"), ("regional_center", "D"), 15),
    }
]
    """
    with open(filename, 'r', encoding='utf-8') as file:
        blocked = set()
        all_road = {}
        status_road = True
        for i in file:
            line = i.strip("\n").split(",")
            if line == ['']:
                continue
            if "Заблоковані дороги:" in line:
                status_road = False
                continue
            elif "Зв'язки:" in line:
                continue
            key1 = (line[0], line[2])
            key2 = (line[1], line[2])
            if status_road:
                if key1 not in all_road:
                    all_road[key1] = {(key2)}
                else:
                    all_road[key1].add(key2)
                if key2 not in all_road:
                    all_road[key2] = {(key1)}
                else:
                    all_road[key2].add(key1)
            else:
                block = (key1, key2, int(line[4]))
                blocked.add(block)
        result = [all_road, blocked]
        return result
print(read_file('input_example.csv'))


def unconnected_places(
    all_roads: dict[tuple[str, str], set[tuple[str, str]]],
    blocked_roads: set[tuple[tuple[str, str], tuple[str, str]]]
) -> list[set[tuple[str, str]]]:
    """
    Function finds all unconnected places and returns them.

    :param all_roads: dict[tuple[str, str], set[tuple[str, str]]], A dictionary,
    where the key is the name and type of a place, and the value is a set of
    all places directly connected to it by one road.

    :param blocked_roads: set[tuple[tuple[str, str], tuple[str, str]]], A set
    of tuples representing roads that are blocked.

    :return: list[set[tuple[str, str]]], A list where each element is a set
    of connected components. The first element includes the regional center.

    Input:
    all_roads = {
                ("village", "A"): {("city", "B"), ("village", "C")},
                ("city", "B"): {("regional_center", "D")},
                ("village", "C"): {("village", "A")},
                ("regional_center", "D"): {("city", "B")}
                }

    blocked_roads = {(("village", "A"), ("city", "B"))}

    unconnected_places(all_roads, blocked_roads)

    Output:

    [
    {('regional_center', 'D'), ('city', 'B')}, 
    {('village', 'A'), ('village', 'C')}
    ]
    """
    # Remove blocked roads from the connections
    roads = {}
    for place, connections in all_roads.items():
        filtered_connections = {conn for conn in connections
            if (place, conn) not in blocked_roads and (conn, place) not in blocked_roads}
        roads[place] = filtered_connections

    components = []

    # Find all connected components
    for place in list(roads):
        if place in roads:
            component = set()
            stack = [place]
            while stack:
                node = stack.pop()
                if node in roads:
                    component.add(node)
                    stack.extend(roads[node])
                    del roads[node]
            components.append(component)

    # Sort components: put the one containing the regional center first
    components.sort(key=lambda comp:
            any((place[0] == "regional_center" for place in comp)), reverse=True)

    return components

def shortest_connection(paths: dict[tuple[str,str]: set[tuple[tuple[str, str], 15]]],
                        blocked: set[tuple[tuple[str, str], tuple[str, str], int]])\
                        -> set[tuple[tuple[str, str], tuple[str, str], int]]:
    """
    Finds a way to connect all points to the regional center as cheap
    (cost measured in km of roads restored) as possible.
    Input:
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
