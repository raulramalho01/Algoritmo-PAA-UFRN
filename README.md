## Algoritmo-PAA-UFRN

Árvore de Steiner com Rotulação Mínima

## Integrantes

Victor Bastos Xavier

Raul Ramalho Lucena

## Descrição do Problema:

Árvore de Steiner com Rotulação Mínima (Minimum Labeling Steiner Tree Problem, MLSteiner) é um problema de otimização combinatória em grafos.

Entrada: um grafo não direcionado G = (V, E), em que cada aresta tem um rótulo (ou “cor”) de um conjunto L, e um subconjunto Q ⊆ V de vértices obrigatórios, chamados terminais ou vértices básicos.

Objetivo: encontrar uma árvore de Steiner, isto é, uma árvore que conecte todos os vértices de Q e que pode usar outros vértices de V como intermediários, usando o menor número possível de rótulos distintos. Aqui o custo é a quantidade de cores diferentes empregadas, e não o peso ou o número de arestas.

## Estrutura do Repositório

mlsteiner/
├── pyproject.toml
├── README.md
├── docs/
│   └── arvore-steiner-rotulacao-minima.gif
├── instances/
│   └── exemplo.json          # instâncias de exemplo para a CLI
├── src/
│   └── mlsteiner/
│       ├── __init__.py
│       ├── graph.py          # grafo rotulado + leitura de instâncias (JSON)
│       ├── solver.py         # heurística gulosa (MVCA) + extração da árvore
│       ├── exact.py          # força bruta para instâncias pequenas
│       ├── visualize.py      # matplotlib; só é importado com --plot
│       └── cli.py            # argparse, ponto de entrada da CLI
└── tests/
    ├── conftest.py           # fixtures: o grafo do GIF, casos-limite
    ├── test_graph.py
    ├── test_solver.py
    ├── test_cli.py
    └── test_visualize.py     # teste de fumaça com backend "Agg"