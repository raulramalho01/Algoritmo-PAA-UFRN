#!/usr/bin/env python3
"""
Algoritmo exato para o MLSteiner: branch-and-bound sobre conjuntos de rótulos
com ramificação por cortes (coluna "OPT" das tabelas do trabalho 02).

Ideia: o estado da busca é um conjunto C de rótulos já ESCOLHIDOS e um conjunto
de rótulos EXCLUÍDOS. Contraindo as componentes de G[C], toda solução que
estende C precisa ligar cada componente de Steiner às demais; logo, para cada
componente de Steiner A, ao menos um rótulo do CORTE de A (rótulos livres que
têm uma aresta saindo de A) entra na solução.

  1) Ramificação: escolhe-se a componente de Steiner A de menor corte, com
     rótulos c1, ..., cp. O ramo i escolhe ci e exclui c1, ..., c(i-1), de modo
     que os ramos são disjuntos e cobrem todas as soluções (busca completa).
  2) Poda por inviabilidade: se, mesmo com todos os rótulos não excluídos, os
     básicos não ficam conectados, o ramo é descartado.
  3) Poda por limite inferior: componentes de Steiner com cortes disjuntos
     exigem, cada uma, um rótulo próprio; então |C| + (nº de cortes disjuntos)
     é um limite inferior. Se ele não for menor que a melhor solução, poda.
  4) Limite superior inicial: a heurística MVCA-Steiner (heuristica.py).

Como só se descartam ramos sem solução melhor que a incumbente, o resultado é
ótimo. Com --limite, a busca para ao estourar o tempo e devolve a melhor
solução encontrada (nesse caso, sem garantia de otimalidade).

Uso:
    python3 exato.py instancia.txt
    python3 exato.py instancia.txt --limite 60     # no máximo 60 segundos
"""
import sys
import time

from guloso import (UnionFind, arestas_por_rotulo, eliminar_redundantes,
                    resolver_e_mostrar)
from heuristica import mvca_steiner

LIVRE, ESCOLHIDO, EXCLUIDO = 0, 1, 2


def exato_com_estatisticas(n, l, arestas, basicos, limite=None):
    """Devolve (C, info). info = {"nos": nós visitados, "otimo": prova de otimalidade,
    "inicial": tamanho da solução inicial (limite superior)}."""
    inicio = time.perf_counter()
    por_rotulo = arestas_por_rotulo(l, arestas)
    basicos = list(set(basicos))
    info = {"nos": 0, "otimo": True, "inicial": 0}
    if len(basicos) <= 1:
        return [], info

    melhor = mvca_steiner(n, l, arestas, basicos)       # limite superior
    info["inicial"] = len(melhor)
    estado = [LIVRE] * l

    def ramificar(C):
        nonlocal melhor
        if limite is not None and time.perf_counter() - inicio > limite:
            info["otimo"] = False
            return
        info["nos"] += 1

        # componentes de G[C]
        uf = UnionFind(n)
        for c in C:
            for (u, v) in por_rotulo[c]:
                uf.unir(u, v)
        raizes = {uf.achar(b) for b in basicos}
        if len(raizes) == 1:                            # C é viável
            if len(C) < len(melhor):
                melhor = list(C)
            return

        # poda por inviabilidade: C + todos os rótulos não excluídos
        uf2 = UnionFind(n)
        for (u, v, c) in arestas:
            if estado[c] != EXCLUIDO:
                uf2.unir(u, v)
        if len({uf2.achar(b) for b in basicos}) > 1:
            return

        # corte de cada componente de Steiner (só rótulos livres)
        corte = {r: set() for r in raizes}
        cruzam = [0] * l                  # nº de arestas do rótulo entre componentes
        for (u, v, c) in arestas:
            if estado[c] != LIVRE:
                continue
            a, b = uf.achar(u), uf.achar(v)
            if a == b:
                continue
            cruzam[c] += 1
            if a in corte:
                corte[a].add(c)
            if b in corte:
                corte[b].add(c)

        # poda por limite inferior: cortes disjuntos exigem rótulos distintos
        ordem = sorted(corte, key=lambda r: len(corte[r]))
        usados, minimo = set(), 0
        for r in ordem:
            if not corte[r]:
                return                    # componente isolada: ramo inviável
            if usados.isdisjoint(corte[r]):
                usados |= corte[r]
                minimo += 1
        if len(C) + minimo >= len(melhor):
            return

        # ramificação no menor corte; ramos disjuntos (inclui ci, exclui os anteriores)
        candidatos = sorted(corte[ordem[0]], key=lambda c: (-cruzam[c], c))
        excluidos = []
        for c in candidatos:
            estado[c] = ESCOLHIDO
            C.append(c)
            ramificar(C)
            C.pop()
            estado[c] = EXCLUIDO
            excluidos.append(c)
        for c in excluidos:
            estado[c] = LIVRE

    ramificar([])
    return eliminar_redundantes(n, por_rotulo, basicos, melhor), info


def exato(n, l, arestas, basicos, limite=None):
    """Conjunto ótimo de rótulos (lista), no mesmo formato dos outros métodos."""
    return exato_com_estatisticas(n, l, arestas, basicos, limite)[0]


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    limite = None
    if "--limite" in sys.argv:
        i = sys.argv.index("--limite")
        limite = float(sys.argv[i + 1])
        args = [a for a in args if a != sys.argv[i + 1]]
    if len(args) != 1:
        sys.exit("uso: python3 exato.py instancia.txt [--limite SEGUNDOS]")
    info = {}

    def resolver(*a):
        C, info_ = exato_com_estatisticas(*a, limite=limite)
        info.update(info_)
        return C

    resolver_e_mostrar("Exato (branch-and-bound)", resolver, args[0])
    print(f"nós visitados: {info['nos']}, solução inicial (MVCA-S): {info['inicial']}, "
          + ("ótimo provado" if info["otimo"] else "TEMPO ESGOTADO: sem prova de otimalidade"))
