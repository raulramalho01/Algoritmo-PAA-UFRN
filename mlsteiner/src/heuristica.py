#!/usr/bin/env python3
"""
Heurística MVCA-Steiner (proposta no trabalho; coluna "MVCA-S" das tabelas).

É o algoritmo guloso de Cerulli et al. (2006) com duas mudanças:
  1) Desempate: entre rótulos que deixam o mesmo número de componentes de
     Steiner, prefere o que absorve mais componentes SEM básicos para dentro
     das componentes de Steiner; persistindo o empate, o que faz mais uniões.
  2) Eliminação: no final, remove rótulos redundantes (do menos para o mais
     frequente).

Uso:
    python3 heuristica.py instancia.txt
    python3 heuristica.py instancia.txt --sem-eliminacao   # coluna "s/elim."
"""
import sys

from guloso import (arestas_por_rotulo, construir, eliminar_redundantes,
                    resolver_e_mostrar)


def mvca_steiner(n, l, arestas, basicos, eliminar=True):
    por_rotulo = arestas_por_rotulo(l, arestas)
    # menor nº de componentes de Steiner; depois mais absorções; depois mais uniões; depois menor índice
    C = construir(n, l, por_rotulo, basicos,
                  chave=lambda c, s, a, u: (s, -a, -u, c))
    if eliminar:
        C = eliminar_redundantes(n, por_rotulo, basicos, C)
    return C


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if len(args) != 1:
        sys.exit("uso: python3 heuristica.py instancia.txt [--sem-eliminacao]")
    if "--sem-eliminacao" in sys.argv:
        resolver_e_mostrar("MVCA-Steiner sem eliminação",
                           lambda *a: mvca_steiner(*a, eliminar=False), args[0])
    else:
        resolver_e_mostrar("MVCA-Steiner", mvca_steiner, args[0])
