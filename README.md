# Graph Isomorphism

A Python project for identifying graphs with the same structure and counting
their symmetries. Developed for Module 7: Discrete Structures & Algorithms at the
University of Twente, by Project Group 4 (2025).

Two graphs are **isomorphic** if their vertices can be relabelled so that their
edges match. An **automorphism** is an isomorphism from a graph to itself: a
rearrangement of its vertices that preserves its structure.

## What it does

- Groups graphs into isomorphism classes.
- Counts automorphisms of a single graph.
- Finds isomorphism classes and automorphism counts for collections of graphs.
- Uses colour refinement and recursive branching to reduce the search space.

## How it works

**Colour refinement** assigns vertices colours based on their degree and then
repeatedly refines those colours using the colours of neighbouring vertices.
The resulting stable colouring helps separate structurally different graphs
and narrow down possible vertex mappings.

When refinement leaves multiple possible matches, **branching** selects a vertex
and tries matching it with same-coloured vertices in the other graph. Each pair
receives a fresh colour before refinement is repeated recursively.

Isomorphism testing stops when a successful branch is found. Counting explores
the successful branches to count mappings. Automorphisms are counted by comparing
a graph with a copy of itself.

This is the original coursework implementation, using basic iterative colour
refinement. It does not implement the later fast colour refinement algorithm or
automorphism-group pruning. Large or highly symmetric graphs can be expensive
to process.

## Run the project

Requires Python 3. No third-party packages are needed.

From the repository directory:

```bash
python3 run.py
```

The program processes the files in `graphs/`. To use your own inputs, place graph
files in that directory:

| Input | Output |
| --- | --- |
| `.gr` | Automorphism count for a single graph |
| `.grl` | Groups of isomorphic graphs |
| `.grl` with `Aut` in its filename | Isomorphism groups and their automorphism counts |

`Aut` is case-sensitive in the original program. Keep `graphs/` limited to graph
files, since the program attempts to process every file in that directory.
Graph indices in the output start at zero.

## Included examples

The bundled coursework inputs cover graph grouping and automorphism counting.
For example, `basicGI1.grl` contains two isomorphism classes:

```text
[{0, 5}, {1, 2, 3, 4}]
```

The expected automorphism counts for `basicAut1.gr` and `basicAut2.gr` are
`13824` and `768`, respectively. Set and group ordering in printed output may vary.

## Graph file format

Files specify the number of vertices, followed by edges between vertices labelled
from `0` to `n - 1`. Lines starting with `#` are comments. In `.grl` files,
`--- Next graph:` separates successive graphs.

```text
# Number of vertices:
3
# Edge list:
0,1
1,2
--- Next graph:
3
0,2
2,1
```

## Repository structure

```text
.
├── run.py        # Original solver and program entry point
├── graph.py      # Course-provided graph data structures
├── graph_io.py   # Course-provided graph file utilities
├── graphs/       # Sample coursework inputs
└── README.md
```

## Credits

The solver was developed as a group coursework project by **Project Group 4**.
The supplied graph utilities retain their original author headers, crediting
Paul Bonsma, Pieter Bos, and Tariq Bontekoe. The graph inputs are supplied
coursework examples.

The Python source files are preserved unchanged from the saved Group 4 submission.
Repository preparation only organizes the files and adds this documentation.
