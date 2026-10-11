## Algoritmo-PAA-UFRN

Árvore de Steiner com Rotulação Mínima

## Integrantes

Victor Bastos Xavier

Raul Ramalho Lucena

## Descrição do Problema:

Árvore de Steiner com Rotulação Mínima (Minimum Labeling Steiner Tree Problem, MLSteiner) é um problema de otimização combinatória em grafos.

Entrada: um grafo não direcionado G = (V, E), em que cada aresta tem um rótulo (ou “cor”) de um conjunto L, e um subconjunto Q ⊆ V de vértices obrigatórios, chamados terminais ou vértices básicos.

Objetivo: encontrar uma árvore de Steiner, isto é, uma árvore que conecte todos os vértices de Q e que pode usar outros vértices de V como intermediários, usando o menor número possível de rótulos distintos. Aqui o custo é a quantidade de cores diferentes empregadas, e não o peso ou o número de arestas.

## Como rodar o Projeto

Placeholder


## TechStack

Python	3.10	Linguagem do projeto
uv	0.5	Gerenciamento do ambiente e das dependências (recomendado)
matplotlib	3.8	Visualização gráfica (opcional)
Pillow	10.0	Exportação de GIFs (opcional)
pytest	8.0	Suíte de testes
pytest-cov	5.0	Cobertura de testes

## Estrutura do Repositório

├── README.md
├── pyproject.toml
├── docs/
│   └── arvore-steiner-rotulacao-minima.gif
├── instances/
│   └── exemplo.json          # instâncias de exemplo para a CLI
├── src/
│   └── mlsteiner/
│       ├── __init__.py
│       ├── graph.py          # grafo rotulado e leitura de instâncias (JSON)
│       ├── solver.py         # heurística gulosa (MVCA) e extração da árvore
│       ├── exact.py          # força bruta para instâncias pequenas
│       ├── visualize.py      # visualização com matplotlib (opcional)
│       └── cli.py            # interface de linha de comando
└── tests/
    ├── conftest.py           # fixtures compartilhadas
    ├── test_graph.py
    ├── test_solver.py
    ├── test_cli.py
    └── test_visualize.py