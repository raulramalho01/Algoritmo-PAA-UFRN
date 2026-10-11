# Árvore de Steiner com Rotulação Mínima

Implementação em Python de uma heurística para o problema da **Árvore de Steiner com Rotulação Mínima** (*Minimum Labeling Steiner Tree*, MLSteiner): dado um grafo cujas arestas têm rótulos e um conjunto de vértices terminais, encontrar uma árvore que conecte todos os terminais usando o menor número possível de rótulos distintos.

<p align="center">
  <img src="docs/arvore-steiner-rotulacao-minima.gif" width="600" alt="Animação da Árvore de Steiner com Rotulação Mínima">
</p>

## Estrutura do repositório

```
.
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
```

## Tecnologias utilizadas

| Tecnologia | Versão mínima | Uso |
| --- | --- | --- |
| [Python](https://www.python.org/) | 3.10 | Linguagem do projeto |
| [uv](https://docs.astral.sh/uv/) | 0.5 | Gerenciamento do ambiente e das dependências (recomendado) |
| [matplotlib](https://matplotlib.org/) | 3.8 | Visualização gráfica (opcional) |
| [Pillow](https://python-pillow.org/) | 10.0 | Exportação de GIFs (opcional) |
| [pytest](https://docs.pytest.org/) | 8.0 | Suíte de testes |
| [pytest-cov](https://pytest-cov.readthedocs.io/) | 5.0 | Cobertura de testes |

O núcleo do algoritmo usa apenas a biblioteca padrão do Python. As bibliotecas de visualização só são necessárias para as opções `--plot` e `--gif`.

## Como rodar o projeto

### 1. Clonar o repositório

```bash
git clone https://github.com/<seu-usuario>/<seu-repositorio>.git
cd <seu-repositorio>
```

### 2. Sem a interface gráfica

Instala apenas o algoritmo, sem matplotlib. Ideal para servidores, CI ou para usar o pacote como biblioteca.

Com **uv**:

```bash
uv sync
uv run mlsteiner instances/exemplo.json
```

Com **pip** e ambiente virtual:

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -e .
mlsteiner instances/exemplo.json
```

A saída mostra os rótulos escolhidos e as arestas da árvore no terminal.

### 3. Com a interface gráfica

Instala também as dependências de visualização.

Com **uv**:

```bash
uv sync --extra viz
uv run mlsteiner instances/exemplo.json --plot                  # abre uma janela com o passo a passo
uv run mlsteiner instances/exemplo.json --gif docs/saida.gif    # salva a animação em GIF
```

Com **pip** e ambiente virtual:

```bash
pip install -e ".[viz]"
mlsteiner instances/exemplo.json --plot
mlsteiner instances/exemplo.json --gif docs/saida.gif
```

> **Sem monitor (SSH, WSL, CI):** a opção `--plot` precisa de uma tela. Nesses ambientes, use `--gif`, que funciona sem janela.

### 4. Rodar os testes

Com **uv**:

```bash
uv run pytest
uv run pytest --cov=mlsteiner     # com relatório de cobertura
```

Com **pip**:

```bash
pip install -e ".[viz,dev]"
pytest
```

## Formato das instâncias

```json
{
  "terminals": [1, 3, 4, 8],
  "edges": [[1, 2, "a"], [2, 3, "a"], [3, 4, "b"], [8, 7, "b"]]
}
```

Cada aresta é `[u, v, rótulo]`. Os vértices são inferidos a partir das arestas.
