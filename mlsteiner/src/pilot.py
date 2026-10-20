#!/usr/bin/env python3
"""
Pilot Method de Cerulli et al. (2006) (coluna "Pilot" das tabelas).

Constrói a solução rótulo a rótulo. Em cada etapa, para CADA rótulo candidato,
completa a solução parcial com o algoritmo guloso ("solução-piloto") e mede o
tamanho do resultado. Fixa o candidato cuja solução-piloto foi a menor.
É muito mais lento que o guloso (executa o guloso O(l^2) vezes), mas costuma
achar soluções melhores.

Uso:
    python3 pilot.py instancia.txt
"""
import sys

from guloso import (UnionFind, arestas_por_rotulo, avaliar_rotulo,
                    eliminar_redundantes, resolver_e_mostrar, viavel)


def completar(n, l, por_rotulo, basicos, inicial):
    """Guloso de Cerulli (empate por índice) partindo da solução parcial 'inicial'."""
    uf = UnionFind(n)
    tem_basico = [False] * n
    for b in basicos:
        tem_basico[b] = True

    def adicionar(c):
        for (u, v) in por_rotulo[c]:
            a, b = uf.achar(u), uf.achar(v)
            if a != b:
                tb = tem_basico[a] or tem_basico[b]
                uf.unir(a, b)
                tem_basico[uf.achar(a)] = tb

    C = list(inicial)
    for c in C:
        adicionar(c)
    livres = set(range(l)) - set(C)
    raizes = {uf.achar(b) for b in basicos}
    while len(raizes) > 1:
        melhor, melhor_chave = None, None
        for c in livres:
            if not por_rotulo[c]:
                continue
            s, a, u = avaliar_rotulo(uf, por_rotulo[c], tem_basico, raizes)
            if u and (melhor_chave is None or (s, c) < melhor_chave):
                melhor, melhor_chave = c, (s, c)
        C.append(melhor)
        livres.discard(melhor)
        adicionar(melhor)
        raizes = {uf.achar(b) for b in basicos}
    return eliminar_redundantes(n, por_rotulo, basicos, C)


def pilot(n, l, arestas, basicos):
    por_rotulo = arestas_por_rotulo(l, arestas)
    melhor = completar(n, l, por_rotulo, basicos, [])
    mestre = []
    while not viavel(n, por_rotulo, basicos, mestre):
        escolhido, tam = None, None
        for i in range(l):
            if i in mestre or not por_rotulo[i]:
                continue
            piloto = completar(n, l, por_rotulo, basicos, mestre + [i])
            if tam is None or len(piloto) < tam:
                escolhido, tam, melhor_piloto = i, len(piloto), piloto
        if tam < len(melhor):
            melhor = melhor_piloto
        mestre.append(escolhido)
        if len(mestre) >= len(melhor):   # não há como melhorar mais
            break
    return melhor


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("uso: python3 pilot.py instancia.txt")
    resolver_e_mostrar("Pilot Method", pilot, sys.argv[1])
