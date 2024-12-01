"""main.py module"""
import argparse
import networkx as nx
import matplotlib.pyplot as plt

print("Script started...")
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

Connections:
city A, village B, 1
village B, regional_center C, 1
regional_center C, village F, 5
village F, city E, 1
city E, village D, 1
village D, city G, 2
city G, village H, 1
village H, city I, 1
city I, city A, 2

Blocked roads:
city I, city A, 2
village D, city G, 2
regional_center C, village F, 5


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
            line = i.strip("\n").split()
            if line == []:
                continue
            if "Blocked" in line:
                status_road = False
                continue
            elif "Connections:" in line:
                continue
            key1 = (line[0], line[1][:-1])
            key2 = (line[2], line[3][:-1])
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
    roads = {}
    for place, connections in all_roads.items():
        filtered_connections = {conn for conn in connections
            if (place, conn) not in blocked_roads and (conn, place) not in blocked_roads}
        roads[place] = filtered_connections

    components = []

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

    components.sort(key=lambda comp:
            any((place[0] == "regional_center" for place in comp)), reverse=True)

    return components


def shortest_connection(paths: dict[tuple[str,str]: set[tuple[tuple[str, str]]]],
                        blocked: set[tuple[tuple[str, str], tuple[str, str], int]])\
                        -> set[tuple[tuple[str, str], tuple[str, str], int]]:
    """
    Finds a way to connect all points to the regional center as cheap
    (cost measured in km of roads restored) as possible.
    >>> shortest_connection({\
        ("village", "A"): {("city", "B"), ("village", "C")},\
        ("city", "B"): {("regional_center"), ("city", "A")},\
        ("village", "C"): {("village", "A"), ("regional_center", "D")},\
        ("regional_center", "D"): {("city", "B"), ("village", "C")}\
    },{(("village", "A"), ("city", "B"), 10),\
        (("regional_center", "D"), ("village", "C"), 8)})
    {(('regional_center', 'D'), ('village', 'C'), 8)}
    >>> shortest_connection({\
        ("city", "A"): {("city", "B"), ("regional_center", "C"), ("city", "I")},\
        ("city", "B"): {("city", "A"), ("regional_center", "C")},\
        ("regional_center", "C"): {("city", "B"), ("city", "A"), ("city", "F")},\
        ("city", "H"): {("city", "G"), ("city", "I")},\
        ("city", "G"): {("city", "H"), ("city", "I"), ("city", "D")},\
        ("city", "I"): {("city", "G"), ("city", "H"), ("city", "A")},\
        ("city", "E"): {("city", "D"), ("city", "F")},\
        ("city", "F"): {("city", "D"), ("city", "E"), ("regional_center", "C")},\
        ("city", "D"): {("city", "F"), ("city", "E"), ("city", "G")},\
    },{(("city", "I"), ("city", "A"), 3),\
    (("city", "G"), ("city", "D"), 5),\
    (("city", "E"), ("city", "F"), 1),\
    (("city", "A"), ("city", "C"), 2),\
    (("regional_center", "C"), ("city", "F"), 3)}) == {\
    (("regional_center", "C"), ("city", "F"), 3), (("city", "I"), ("city", "A"), 3)}
    True
    """
    blocked = blocked.copy()
    restored = set()
    while True:
        reblocked = {(a, b) for a, b, c in blocked}
        groups = unconnected_places(paths, reblocked)
        if len(groups) > 1:
            disconnected = set.union(*groups[1:])
        else:
            break
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


def write_to_file(filename: str, unconnected: list[set[tuple[str, str]]],
                  restored: set[tuple[tuple[str, str], tuple[str, str], int]]) -> None:
    """
    Function writes result to a file

    :param filename: str, A file to write to
    :param unconnected: A result of unconnected_places function
    :param restored: A result of shortest_connection function
    :return: None
    """
    with open(filename, 'w', encoding='utf-8') as file:
        file.write("Unconnected places:\n")
        for bobik in unconnected:
            file.write(f"{', '.join([f'{place[0]} {place[1]}' for place in bobik])}\n")
        file.write("\nRestored roads:\n")
        for road in restored:
            punkt1, punkt2, length = road
            file.write(f"{punkt1[0]} {punkt1[1]}, {punkt2[0]} {punkt2[1]}, {length}\n")

def visual(all_roads, blocked_roads):
    """
    Creates a visualization of a graph representing connections between places,
    with the ability to highlight blocked roads.
    
    The function draws a graph where nodes represent locations and edges
    represent connections between them. Blocked roads are highlighted in red.

    :param all_roads: A dictionary where keys are tuples (type, name) of places
                      and values are sets of connected places as tuples.
    :param blocked_roads: A set of tuples representing blocked roads between places.

    >>> all_roads = {
    ...     ("місто", "A"): {("село", "B")},
    ...     ("село", "B"): {("місто", "A"), ("обласний центр", "C")},
    ...     ("обласний центр", "C"): {("село", "B"), ("село", "F")},
    ...     ("село", "F"): {("обласний центр", "C"), ("місто", "E")}
    ... }
    >>> blocked_roads = {(("місто", "A"), ("село", "B"))}
    >>> visual(all_roads, blocked_roads)
    """
    G = nx.Graph()
    for place, connections in all_roads.items():
        for connection in connections:
            G.add_edge(place, connection)
    edge_colors = ['red' if ((place, connection) in blocked_roads or (connection, place) in blocked_roads) 
                   else 'black' for place, connections in all_roads.items() for connection in connections]
    pos = nx.spring_layout(G)
    plt.figure(figsize=(13, 9))
    nx.draw(G, pos, with_labels=True,
             node_color='green',
                  node_size = 200,
                      font_size=15,
                          font_weight=None,
                              edge_color=edge_colors)
    plt.title("Візуалізація графа зв'язків між місцями")
    plt.show()

def main(input_filename:str, output_filename:str) -> None:
    """
    A main function

    :param input_f:str, A file to read from
    :param output_f:str, A file to write to
    :return: None
    """
    parser=argparse.ArgumentParser(description="Process an input file and write to an output file.")
    parser.add_argument("--input", type=str, required=False, help="Path to the input file")
    parser.add_argument('--output', type=str, required=False, help="Path to the output file")
    args = parser.parse_args()
    if not args.input:
        args.input = input_filename
    if not args.output:
        args.output = output_filename

    all_roads, blocked_roads = read_file(args.input)
    blocked_no_weight = {(road[0], road[1]) for road in blocked_roads}
    unconnected = unconnected_places(all_roads, blocked_no_weight)
    restored = shortest_connection(all_roads, blocked_roads)
    write_to_file(args.output, unconnected, restored)
    print("Processing complete!")

res = read_file("discrete_project\input_example.csv")
all_roads, blocked_roads = res
visual(all_roads, blocked_roads)


if __name__ == '__main__':
    main("input_example.csv", "output_example.csv")
    import doctest
    doctest.testmod()
