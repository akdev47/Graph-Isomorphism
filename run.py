import os
from collections import defaultdict

from graph_io import *
from graph import *


def is_discrete(color_classes):
    return len(set(color_classes.values())) == len(color_classes)


def get_coloring_classes_sizes(colors):
    size_of_color_classes = {}
    for color in colors:
        if color in size_of_color_classes:
            size_of_color_classes[color] += 1
        else:
            size_of_color_classes[color] = 1
    return size_of_color_classes


def branching_search(graph1: Graph, graph2: Graph, colors1: dict, colors2: dict):
    all_colors = list(colors1.values()) + list(colors2.values())

    chosen_vertex_g1 = None
    possible_mapping = []

    freq = {}
    for num in all_colors:
        if num in freq:
            freq[num] += 1
        else:
            freq[num] = 1

    # Step 2: Find the number with the maximum frequency
    most_frequent = None
    max_count = 0

    for num, count in freq.items():
        if count > max_count:
            max_count = count
            most_frequent = num
    # print(all_colors)

    biggest_color_class_g1 = most_frequent

    for v1 in graph1.vertices:
        if colors1[v1] == biggest_color_class_g1 and chosen_vertex_g1 is None:
            chosen_vertex_g1 = v1
            break
    for v2 in graph2.vertices:
        if colors2[v2] == biggest_color_class_g1:
            possible_mapping.append(v2)

    # print(possible_mapping)

    # we loop through all the vertices that are a possible match
    for vertex_g2 in possible_mapping:
        new_colors1, new_colors2 = colors1.copy(), colors2.copy()
        new_color = max(all_colors) + 1
        new_colors1[chosen_vertex_g1] = new_color
        new_colors2[vertex_g2] = new_color
        # new_colors1[chosen_vertex_g1], new_colors2[vertex_g2] = max(unique_colors) + 1

        all_vertices_colors = {}
        for vertex, color in new_colors1.items():
            all_vertices_colors[vertex] = color
        for vertex, color in new_colors2.items():
            all_vertices_colors[vertex] = color

        # we refine the coloring of both graphs
        coloring = get_final_coloring(graph1, graph2, all_vertices_colors)

        # print("Trying mapping: G1 vertex", chosen_vertex_g1, "→ G2 vertex", vertex_g2)
        # print("Before refinement:", new_colors1)

        # if the coloring after the refinement is the same: we do go deeper in this branch
        # else : we finish exploring this branch
        coloring_g1 = {v: color for v, color in coloring.items() if v in graph1.vertices}
        coloring_g2 = {v: color for v, color in coloring.items() if v in graph2.vertices}

        if coloring_g1[chosen_vertex_g1] != coloring_g2[vertex_g2]:
            continue

        # print("g1")
        # print(coloring_g1)
        # print("g2")
        # print(coloring_g2)
        sizes1 = sorted(get_coloring_classes_sizes(coloring_g1).values())
        sizes2 = sorted(get_coloring_classes_sizes(coloring_g2).values())

        if sizes1 == sizes2:
            if is_discrete(coloring_g1):
                # print("is discrete")
                return True
            else:
                # print("else")
                if branching_search(graph1, graph2, coloring_g1, coloring_g2):
                    # print("if branching search")
                    return True
    return False


def stable_coloring(graph):
    coloring = {v: 1 for v in graph.vertices}
    iterations = 0
    # print(f"\nGraph initial vertices: {len(graph.vertices)}")
    # print(f"Initial edges: {len(graph.edges)}")

    while True:
        new_coloring = {}
        color_info = {}

        if len(graph.edges) == 0 or all(len(v.neighbours) == len(graph.vertices[0].neighbours) for v in graph.vertices):
            if iterations == 0:
                neighborhood_signatures = {v: tuple(sorted([coloring[n] for n in v.neighbours])) for v in
                                           graph.vertices}
                return coloring, 0, neighborhood_signatures

        for v in graph.vertices:
            neighbor_colors = sorted([coloring[n] for n in v.neighbours])
            color_info[v] = (coloring[v], tuple(neighbor_colors))
            # print(f"Vertex {v}: color={coloring[v]}, neighbor_colors={neighbor_colors}")

        color_map = {}
        for i, color in enumerate(sorted(set(color_info.values()))):
            color_map[color] = i + 1

        for v in graph.vertices:
            new_coloring[v] = color_map[color_info[v]]

        if new_coloring == coloring:
            # print(f"Stabilized after {iterations} iterations: {coloring}")
            neighborhood_signatures = {v: tuple(sorted([coloring[n] for n in v.neighbours])) for v in graph.vertices}
            break

        coloring = new_coloring
        iterations += 1
        # print(f"Iteration {iterations}: {coloring}")

    return coloring, iterations, neighborhood_signatures


def load_graphs_from_grl(file_path):
    with open(file_path) as f:
        read, _ = read_graph_list(Graph, f)
    return read


def group_equivalence_classes(colorings):
    equivalence_classes = {}

    for index_i, color_classes, iterations, discrete, neighborhood_signatures in colorings:

        key = (tuple(color_classes), iterations, discrete, tuple(sorted(neighborhood_signatures.values())))

        if key not in equivalence_classes:
            equivalence_classes[key] = []
        equivalence_classes[key].append(index_i)

    results = []
    for key, indices in equivalence_classes.items():
        sorted_indices = sorted(indices)
        results.append((sorted_indices, list(key[0]), key[1], key[2]))

    return results


def get_final_coloring(graph1, graph2, all_vertices_colors):

    # basic fast color refinement
    all_vs = list(graph1.vertices) + list(graph2.vertices)
    current_coloring = all_vertices_colors

    while True:
        new_coloring = {}
        sig_to_new_color = {}
        next_new_color = 0
        v_by_signature = defaultdict(list)

        for vertex in all_vs:
            original_color = current_coloring[vertex]
            neighbour_colors = []

            if vertex.neighbours:
                for n in vertex.neighbours:
                    if n in current_coloring:
                        neighbour_colors.append(current_coloring[n])
            neighbour_colors.sort()
            signature = (original_color, tuple(neighbour_colors))
            v_by_signature[signature].append(vertex)

        for signature in sorted(v_by_signature.keys()):
            if signature not in sig_to_new_color:
                sig_to_new_color[signature] = next_new_color
                next_new_color += 1
            assigned_color = sig_to_new_color[signature]
            for vertex in v_by_signature[signature]:
                new_coloring[vertex] = assigned_color
        if new_coloring == current_coloring:
            break
        current_coloring = new_coloring
    return current_coloring


def basic_colorref(all_graphs):
    graphs = load_graphs_from_grl(all_graphs)
    result = []

    # assigning initial color
    for graph in graphs:
        for vertex in graph.vertices:
            vertex.colornum = len(vertex.neighbours)

    # loop that will run till color refinement stabilizes
    stable = False
    while not stable:
        stable = True
        new_colors = {}

        # find neighbours and signature the vertices
        for graph in graphs:
            for vertex in graph.vertices:
                neighbour_colors = []
                for n in vertex.neighbours:
                    neighbour_colors.append(n.colornum)
                neighbour_colors.sort()
                signature = (vertex.colornum, tuple(neighbour_colors))
                new_colors[vertex] = signature

        colors = {}
        next_color = 0
        # assign new values to unique signatured ones
        for vertex in new_colors:
            signature = new_colors[vertex]
            if signature not in colors:
                colors[signature] = next_color
                next_color += 1

        # update each vertex baesd on colors
        for vertex in new_colors:
            new_color = colors[new_colors[vertex]]
            if new_color != vertex.colornum:
                stable = False
            vertex.colornum = new_color

    # signature for each graph
    signature_graph = {}
    for i, graph in enumerate(graphs):
        signature = []
        for v in graph.vertices:
            signature.append(v.colornum)
        signature.sort()
        signature = tuple(signature)

        # grroup identical signatured graphs
        if signature not in signature_graph:
            signature_graph[signature] = []
        signature_graph[signature].append(i)

    # size of each color and store in color class
    for signature, index in signature_graph.items():
        color_class = []
        for color in set(signature):
            color_class.append(signature.count(color))
        color_class.sort()

        # formatting
        is_discrete = len(set(signature)) == len(signature)
        iterations = ["I deleted the counting (we dont use that)"]
        result.append((sorted(index), color_class, iterations, is_discrete))

    return result


def count_isomorphisms(graph1: 'Graph', graph2: 'Graph', colors1: dict, colors2: dict):
    sizes1_initial = sorted(get_coloring_classes_sizes(colors1).values())
    sizes2_initial = sorted(get_coloring_classes_sizes(colors2).values())
    if sizes1_initial != sizes2_initial:
        return 0

    if is_discrete(colors1):
        return 1

    total_isomorphism_count = 0
    all_colors = list(colors1.values()) + list(colors2.values())

    freq = {}
    for num in all_colors:
        if num in freq:
            freq[num] += 1
        else:
            freq[num] = 1

    # find the color class with the maximum frequency
    target_color = None
    max_count = 0

    for num, count in freq.items():
        if count > max_count:
            max_count = count
            target_color = num

    if target_color is None:
        print("Error , it should be caught by is_discrete()")
        return 0

    # Select a vertex from graph1 with the target color.
    chosen_vertex_g1 = None

    for v1 in graph1.vertices:
        if colors1[v1] == target_color and chosen_vertex_g1 is None:
            chosen_vertex_g1 = v1
            break

    if chosen_vertex_g1 is None:
        print(f"Error: Could not find vertex for target color {target_color}")
        return 0

    # Find matching vertices in graph2.
    possible_mapping = [v for v in graph2.vertices if colors2[v] == target_color]

    all_current_colors = list(colors1.values()) + list(colors2.values())
    next_new_color = max(all_current_colors) + 1

    for vertex_g2 in possible_mapping:
        branch_colors1, branch_colors2 = colors1.copy(), colors2.copy()
        branch_colors1[chosen_vertex_g1] = next_new_color
        branch_colors2[vertex_g2] = next_new_color

        all_vertices_colors = {}
        all_vertices_colors.update(branch_colors1)
        all_vertices_colors.update(branch_colors2)

        refined_coloring = get_final_coloring(graph1, graph2, all_vertices_colors)
        refined_colors1 = {v: color for v, color in refined_coloring.items() if v in graph1.vertices}
        refined_colors2 = {v: color for v, color in refined_coloring.items() if v in graph2.vertices}

        if refined_colors1.get(chosen_vertex_g1) != refined_colors2.get(vertex_g2):
            continue

        sizes1 = sorted(get_coloring_classes_sizes(refined_colors1).values())
        sizes2 = sorted(get_coloring_classes_sizes(refined_colors2).values())
        if sizes1 == sizes2:
            total_isomorphism_count += count_isomorphisms(graph1, graph2, refined_colors1, refined_colors2)

    return total_isomorphism_count


if __name__ == "__main__":
    path2 = "graphs"
    # result = basic_colorref(path)
    # print(result)


def get_equivalence_classes(path):
    list_of_equivalence_classes = []
    list_of_tuples = basic_colorref(path)
    for tuple in list_of_tuples:
        list_of_equivalence_classes.append(tuple[0])
    return list_of_equivalence_classes


def update_groups(pair, groups=[]):
    a, b = pair
    new_group = {a, b}
    merged = []

    for group in groups:
        if a in group or b in group:
            new_group |= group
            merged.append(group)

    for g in merged:
        groups.remove(g)

    groups.append(new_group)


def counting_automorphisms(graph_list, equivalence_classes_list, counting, single_graph_flag):
    isomorphic_groups = []

    # if we just have a single graph we simply count the automorphims.
    if single_graph_flag:
        graph1 = graph_list[0]
        graph2 = copy_graph(graph1)
        coloring1 = stable_coloring(graph1)[0]
        coloring2 = stable_coloring(graph2)[0]
        return count_isomorphisms(graph1, graph2, coloring1, coloring2)

    # Here we create the groups of isomorphic graphs
    for i in range(len(equivalence_classes_list)):
        for j in range(len(equivalence_classes_list[i])):
            for k in range(j + 1, len(equivalence_classes_list[i])):
                coloring1 = stable_coloring(graph_list[equivalence_classes_list[i][j]])[0]
                coloring2 = stable_coloring(graph_list[equivalence_classes_list[i][k]])[0]
                graph1 = graph_list[equivalence_classes_list[i][j]]
                graph2 = graph_list[equivalence_classes_list[i][k]]
                if branching_search(graph1, graph2, coloring1, coloring2):
                    update_groups((equivalence_classes_list[i][j], equivalence_classes_list[i][k]), isomorphic_groups)

    # if we dont need to count we just return the isomorphic classes (including the classes with only one graph in it)
    # otherwise we skip this part
    if counting is False:
        all_indices_in_equivlence_classes = []
        for group in isomorphic_groups:
            for index in group:
                all_indices_in_equivlence_classes.append(index)
        for eqclass in equivalence_classes_list:
            for graph_index in eqclass:
                if graph_index not in all_indices_in_equivlence_classes:
                    isomorphic_groups.append({graph_index})
        return isomorphic_groups
    all_indices_in_equivlence_classes = []
    for group in isomorphic_groups:
        for index in group:
            all_indices_in_equivlence_classes.append(index)
    for eqclass in equivalence_classes_list:
        for graph_index in eqclass:
            if graph_index not in all_indices_in_equivlence_classes:
                isomorphic_groups.append({graph_index})

    # Now we go through the isomorphic groups, and we take 2 graphs out of it
    # to calculate the automorphisms for the whole group and put it in the dictionary.
    final_group_to_counts = {}
    for group in isomorphic_groups:
        group_frozenset = frozenset(group)
        if group_frozenset not in final_group_to_counts:
            # Use any pair in the group to get the count(since all are isomorphic to each other)
            if len(group_frozenset) == 1:
                fs = group_frozenset
                index = list(fs)[0]
                graph1 = graph_list[index]
                coloring1 = stable_coloring(graph_list[index])[0]
                graph2 = copy_graph(graph1)
                coloring2 = stable_coloring(graph2)[0]
                # print(count_isomorphisms(graph_list[0],graph2,coloring1,coloring2))
                # print(graph_list[group_frozenset[0]])
                final_group_to_counts[group_frozenset] = count_isomorphisms(graph1, graph2, coloring1, coloring2)
            else:
                for i in group:
                    for k in group:
                        if i < k:
                            coloring1 = stable_coloring(graph_list[i])[0]
                            coloring2 = stable_coloring(graph_list[k])[0]
                            if branching_search(graph_list[i], graph_list[k], coloring1, coloring2):
                                final_group_to_counts[group_frozenset] = count_isomorphisms(graph_list[i],
                                                                                            graph_list[k],
                                                                                            coloring1, coloring2)
                                break
                    if group_frozenset in final_group_to_counts:
                        break

    return final_group_to_counts


def copy_graph(graph):
    new_graph = Graph(graph.directed, graph.simple)

    # Create new vertices and map old vertices to new ones
    vertex_map = {}  # Maps old Vertex object -> new Vertex object
    for old_v in graph.vertices:
        new_v = Vertex(new_graph, old_v.label)
        new_graph.add_vertex(new_v)
        vertex_map[old_v] = new_v

    # Create new edges connecting the new vertices
    for old_edge in graph.edges:
        new_tail = vertex_map[old_edge.tail]
        new_head = vertex_map[old_edge.head]
        new_edge = Edge(new_tail, new_head, old_edge.weight)
        new_graph.add_edge(new_edge)

    return new_graph


def printing_isomorphic_graphs(path, counting_flag, single_graph_flag):
    list_of_equivalence_classes = get_equivalence_classes(path)
    list_of_graphs = load_graphs_from_grl(path)
    if counting_flag and single_graph_flag:
        return counting_automorphisms(list_of_graphs, list_of_equivalence_classes, True, True)
    elif counting_flag:
        return counting_automorphisms(list_of_graphs, list_of_equivalence_classes, True, False)
    else:
        return counting_automorphisms(list_of_graphs, list_of_equivalence_classes, False, False)


# function just for making the output look nice (getting rid of the "frozenset" prefix)
def print_dict_nice(dictionary):
    result = "{"
    items = []
    for key, value in dictionary.items():
        key_str = str(set(key))
        items.append(f"{key_str}: {value}")
    result += ", ".join(items) + "}"
    print(result)


def final_answer():
    for file_path in os.listdir(path2):
        print(file_path + ":")
        if "Aut" in file_path and file_path.endswith("grl"):
            print_dict_nice(printing_isomorphic_graphs(os.path.join(path2, file_path), True, False))
        elif file_path.endswith("gr"):
            print(printing_isomorphic_graphs(os.path.join(path2, file_path), True, True))
        else:
            print(printing_isomorphic_graphs(os.path.join(path2, file_path), False, False))


print(final_answer())
