"""
A library for finding disconnected vertices in a graph and
the cheapest way to restore connection.
"""
import argparse


def read_file(filename: str) -> tuple[dict[tuple[str, str]: set[tuple[str, str, int]]],
                                      set[tuple[tuple[str, str], tuple[str, str], int]]]:
    """
    Reads a graph-containing file, which is split into 2 parts:
    Connections and Blocked roads, the first one containing edges between nodes in a
    non-directional graph, and the second one being blocked edges - a subset of the first part,
    additionally having the third parameter - length of the blocked road, which we will need in
    other functions. Returns 
    1. A dictionary with node being the key and a set with adjacent nodes being the value.
    2. A set of blocked roads, a single blocked road being a tuple of node1, node2 and the weight
    of the edge.

    :param filename: str, A file name to read from

    :return:list[ dict[tuple[str, str], set[ tuple[tuple[str, str], tuple[str, str]]]], where
        - first el of list is a dictionary with type and name of place as keys and
    type, name of connected places and distance between them as values,
        - second el is a set of blocked roads, as tuples of tuple of first
    place and its type and another tuple as second place, its name and length of the road.

    Example:

Connections:
city A, village B
village B, regional_center C
regional_center C, village F
village F, city E
city E, village D
village D, city G
city G, village H
village H, city I
city I, city A

Blocked roads:
city I, city A, 2
village D, city G, 2
regional_center C, village F, 5


    Output:
(
{   ('city', 'A'): {('city', 'I'), ('village', 'B')},
    ('village', 'B'): {('regional_center', 'C'), ('city', 'A')},
    ('regional_center', 'C'): {('village', 'F'), ('village', 'B')},
    ('village', 'F'): {('regional_center', 'C'), ('city', 'E')},
    ('city', 'E'): {('village', 'F'), ('village', 'D')},
    ('village', 'D'): {('city', 'G'), ('city', 'E')},
    ('city', 'G'): {('village', 'H'), ('village', 'D')},
    ('village', 'H'): {('city', 'G'), ('city', 'I')},
    ('city', 'I'): {('village', 'H'), ('city', 'A')}
},
{   (('regional_center', 'C'), ('village', 'F'), 5),
    (('city', 'I'), ('city', 'A'), 2),
    (('village', 'D'), ('city', 'G'), 2)
})

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
            if status_road:
                key2 = (line[2], line[3])
                if key1 not in all_road:
                    all_road[key1] = {(key2)}
                else:
                    all_road[key1].add(key2)
                if key2 not in all_road:
                    all_road[key2] = {(key1)}
                else:
                    all_road[key2].add(key1)
            else:
                key2 = (line[2], line[3][:-1])
                block = (key1, key2, int(line[4]))
                blocked.add(block)
        return all_road, blocked


def disconnected_places(
    all_roads: dict[tuple[str, str], set[tuple[str, str]]],
    blocked_roads: set[tuple[tuple[str, str], tuple[str, str]]]
) -> tuple[set[tuple[str, str]], set[frozenset[tuple[str, str]]]]:
    """
    Function finds all disconnected places and returns them.

    :param all_roads: dict[tuple[str, str], set[tuple[str, str]]], A dictionary,
    where the key is the name and type of a place, and the value is a set of
    all places directly connected to it by one road.

    :param blocked_roads: set[tuple[tuple[str, str], tuple[str, str]]], A set
    of tuples representing roads that are blocked.

    :return: tuple[set[tuple[str, str]], set[frozenset[tuple[str, str]]]],
    A tuple with connected and disconnected places. The first
    set includes the regional center and elements connected to it, the second
    set includes frozen sets of groups of disconnected places.

    Input:
    all_roads = {
                ("village", "A"): {("city", "B"), ("village", "C")},
                ("city", "B"): {("regional_center", "D")},
                ("village", "C"): {("village", "A")},
                ("regional_center", "D"): {("city", "B")}
                }

    blocked_roads = {(("village", "A"), ("city", "B"))}

    disconnected_places(all_roads, blocked_roads)

    Output:

    (
    {('regional_center', 'D'), ('city', 'B')},
    {{('village', 'A'), ('village', 'C')}}
    )
    """
    roads = {}
    for place, connections in all_roads.items():
        filtered_connections = {conn for conn in connections
            if (place, conn) not in blocked_roads and (conn, place) not in blocked_roads}
        roads[place] = filtered_connections

    central = set()
    components = set()
    for place in list(roads):
        flag = False
        if place in roads:
            component = set()
            stack = [place]
            while stack:
                node = stack.pop()
                if node in roads:
                    if node[0] == "regional_center":
                        flag = True
                    component.add(node)
                    stack.extend(roads[node])
                    del roads[node]
            if flag:
                central = component
            else:
                components.add(frozenset(component))

    return central, components


def shortest_connection(paths: dict[tuple[str,str]: set[tuple[tuple[str, str]]]],
                        blocked: set[tuple[tuple[str, str], tuple[str, str], int]])\
                        -> set[tuple[tuple[str, str], tuple[str, str], int]]:
    """
    Finds a way to connect all points to the regional center as cheap
    (cost measured in km of roads restored) as possible.
    :param paths: dict[tuple[str,str]: set[tuple[tuple[str, str]]]], a graph represented
    as a dictionary.
    :param blocked: set[tuple[tuple[str, str], tuple[str, str], int]], a set of blocked edges
    :return: set[tuple[tuple[str, str], tuple[str, str], int]], a set of roads (edges), that 
    represent the cheapest way to restore connections to all nodes.
    >>> shortest_connection({\
        ("village", "A"): {("city", "B"), ("village", "C")},\
        ("city", "B"): {("regional_center", "D"), ("city", "A")},\
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
        accessible, groups = disconnected_places(paths, reblocked)
        disconnected = set()
        if len(groups) == 0:
            break
        for group in groups:
            disconnected.update(set(group))
        options = []
        for node in accessible:
            for vertice in disconnected:
                if vertice in paths[node]:
                    for block in blocked:
                        if node in block and vertice in block:
                            options.append(block)
        options = sorted(options, key=lambda x: x[2])
        if not options:
            raise ValueError("Impossible to restore connection to all localities")
        choice = options[0]
        blocked.remove(choice)
        restored.add(choice)
    return restored


def write_to_file(filename: str, disconnected: set[frozenset[tuple[str, str]]],
                  restored: set[tuple[tuple[str, str], tuple[str, str], int]]) -> None:
    """
    Function writes result to a file

    :param filename: str, A file to write to
    :param disconnected: A result of disconnected_places function
    :param restored: A result of shortest_connection function
    :return: None
    """
    with open(filename, 'w', encoding='utf-8') as file:
        file.write("Disconnected places:\n")
        for group in disconnected:
            file.write(f"{', '.join([f'{place[0]} {place[1]}' for place in group])}\n")
        file.write("\nRestored roads:\n")
        for road in restored:
            punkt1, punkt2, length = road
            file.write(f"{punkt1[0]} {punkt1[1]}, {punkt2[0]} {punkt2[1]}, {length}\n")


def visual(all_roads, blocked_roads, restored_roads=None):
    """
    Creates a visualization of a graph representing connections between places,
    with the ability to highlight blocked roads.
    
    The function draws a graph where nodes represent locations and edges
    represent connections between them. Blocked roads are highlighted in red.
    Restored roads are highlighted in green. Normal roads are green.

    :param all_roads: A dictionary where keys are tuples (type, name) of places
                      and values are sets of connected places as tuples.
    :param blocked_roads: A set of tuples representing blocked roads between places.
    :param restored_roads: optional argument, display edges as blue if restored
    """
    G = nx.Graph()
    reblocked = {tuple(sorted([a,b])): c for a,b,c in blocked_roads}
    restored = {}
    if restored_roads:
        restored = {tuple(sorted([a,b])): c for a,b,c in restored_roads}
    for place, connections in all_roads.items():
        for connection in connections:
            G.add_edge(place, connection)
    edge_colors = []
    for edge in G.edges():
        srt = tuple(sorted(list(edge)))
        if srt in reblocked:
            if restored_roads and srt in restored:
                edge_colors.append("blue")
            else:
                edge_colors.append("red")
        else:
            edge_colors.append("green")

    regional = ()
    labels = {}
    for edge in G.nodes():
        if edge[0] == "regional_center":
            regional = edge
            labels[edge] = "R.C. "+edge[1]
        else:
            labels[edge] = edge[1]

    pos = nx.bfs_layout(G,regional)
    plt.figure(figsize=(15, 8))
    nx.draw(G, pos, with_labels=False,
            node_color='green',
                node_size = 800,
                    font_size=15,
                        font_weight=None,
                            edge_color=edge_colors,
                                style="dashed",
                                    width = 3.5)
    nx.draw_networkx_edge_labels(G, pos, reblocked, font_size=15)
    nx.draw_networkx_labels(G, pos, labels, font_size=17, font_color="black")
    plt.gca().margins(0.08)
    plt.show()


def ui():
    """
    If the paths to input or output files weren't specified, this
    function is called and walks user through the process of solving the problem.
    """
    print("Hello! Specify the path to the graph file, please")
    path = input(">>> ")
    all_r, blocked_r = read_file(path)
    reblocked = {(a,b) for a,b,c in blocked_r}
    while True:
        print("What do you want to do now?")
        print("0. Visualize the graph")
        print("1. Find disconnected places")
        print("2. Find the best way to restore roads")
        print("3. Visualize the best way to restore roads")
        print("4. Exit")
        choice = input(">>> ")
        if choice not in ("0", "1", "2", "3", "4"):
            print("Sorry, no such option :(")
            return None
        if choice == "0":
            print("Here's your graph")
            visual(all_r, blocked_r)
        elif choice == "1":
            print("Here are the places, disconnected from the regional center:\n")
            _, groups = disconnected_places(all_r, reblocked)
            for group in groups:
                for locality in group:
                    print(" ".join(locality))
            print()
        elif choice == "2":
            print("Here is the best way to restore roads:\n")
            restored = shortest_connection(all_r, blocked_r)
            total_restored = 0
            for road in restored:
                total_restored += road[2]
                print(f"Restore {road[2]} km between {road[0][0]} \
{road[0][1]} and {road[1][0]} {road[1][1]}")
            print(f"In total, {total_restored} km of roads need to be restored\n")
        elif choice == "3":
            print("Cool! The blue roads are the ones restored")
            restored = shortest_connection(all_r, blocked_r)
            visual(all_r, blocked_r, restored)
        else:
            print("See you!")
            return None


def main(argprs):
    """
    A function that implements argparse functionality.
    While calling the function in terminal, specify the path to input and output files, e.g.:
    python3 main.py --input input_example --output output_example
    :return: None
    """
    print("Script started...")
    all_roads, blocked_roads = read_file(argprs.input)
    blocked_no_weight = {(road[0], road[1]) for road in blocked_roads}
    _, disconnected = disconnected_places(all_roads, blocked_no_weight)
    restored = shortest_connection(all_roads, blocked_roads)
    write_to_file(argprs.output, disconnected, restored)
    print("Processed data has been written to a file!")


if __name__ == '__main__':
    parser=argparse.ArgumentParser(description="Process an input file and write to an output file")
    parser.add_argument("--input", type=str, required=False, help="Path to the input file")
    parser.add_argument('--output', type=str, required=False, help="Path to the output file")
    args = parser.parse_args()
    if not args.input or not args.output:
        import networkx as nx
        import matplotlib.pyplot as plt
        ui()
    else:
        main(args)
    import doctest
    doctest.testmod()
