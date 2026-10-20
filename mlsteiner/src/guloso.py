#!/usr/bin/env python3
"""
Algoritmo guloso de Cerulli et al. (2006) para o MLSteiner (coluna "Cer." das
tabelas), mais as funções básicas usadas pelos outros scripts.

Ideia: começar sem nenhum rótulo e, a cada passo, adicionar o rótulo que deixa
o MENOR número de componentes de Steiner (componentes conexas que contêm ao
menos um vértice básico). Empates são decididos pelo menor índice do rótulo.
Para quando todos os básicos estão na mesma componente. No final, tenta
remover rótulos que ficaram desnecessários.

Uso:
    python3 guloso.py instancia.txt
"""
import sys
import time

from gerador import ler


# ---------------------------------------------------------------------------
# Union-Find (conjuntos disjuntos), para manter as componentes conexas
# ---------------------------------------------------------------------------
class UnionFind:
    def __init__(self, n):
        self.pai = list(range(n))

    def achar(self, x):
        pai = self.pai
        while pai[x] != x:
            pai[x] = pai[pai[x]]      # compressão de caminho
            x = pai[x]
        return x

    def unir(self, a, b):
        a, b = self.achar(a), self.achar(b)
        if a == b:
            return False
        self.pai[b] = a
        return True


# ---------------------------------------------------------------------------
# Estrutura auxiliar
# ---------------------------------------------------------------------------
def arestas_por_rotulo(l, arestas):
    """por_rotulo[c] = lista de arestas (u, v) com rótulo c."""
    por_rotulo = [[] for _ in range(l)]
    for (u, v, c) in arestas:
        por_rotulo[c].append((u, v))
    return por_rotulo


def componentes_steiner(n, por_rotulo, basicos, C):
    """Número de componentes conexas, usando só rótulos de C, que contêm básicos."""
    uf = UnionFind(n)
    for c in C:
        for (u, v) in por_rotulo[c]:
            uf.unir(u, v)
    return len({uf.achar(b) for b in basicos})


def viavel(n, por_rotulo, basicos, C):
    return componentes_steiner(n, por_rotulo, basicos, C) == 1


def eliminar_redundantes(n, por_rotulo, basicos, C):
    """Tenta remover cada rótulo, do menos para o mais frequente, mantendo a viabilidade."""
    C = list(C)
    for c in sorted(C, key=lambda c: len(por_rotulo[c])):
        sem_c = [x for x in C if x != c]
        if viavel(n, por_rotulo, basicos, sem_c):
            C = sem_c
    return C


def extrair_arvore(n, por_rotulo, basicos, C):
    """Árvore (lista de arestas (u, v, rótulo)) que conecta os básicos usando só rótulos de C.
    Faz uma busca em largura e depois poda folhas que não são básicas."""
    adj = [[] for _ in range(n)]
    for c in C:
        for (u, v) in por_rotulo[c]:
            adj[u].append((v, c))
            adj[v].append((u, c))
    raiz = basicos[0]
    pai = {raiz: None}
    fila = [raiz]
    for x in fila:
        for (y, c) in adj[x]:
            if y not in pai:
                pai[y] = (x, c)
                fila.append(y)
    eh_basico = set(basicos)
    grau = {x: 0 for x in pai}
    for y, pc in pai.items():
        if pc:
            grau[y] += 1
            grau[pc[0]] += 1
    vivos = set(pai)
    pilha = [x for x in pai if grau[x] == 1 and x not in eh_basico]
    while pilha:
        x = pilha.pop()
        if x not in vivos:
            continue
        vivos.discard(x)
        p = pai[x][0]
        grau[p] -= 1
        if grau[p] == 1 and p not in eh_basico:
            pilha.append(p)
    return [(x, pai[x][0], pai[x][1]) for x in vivos if pai[x] and pai[x][0] in vivos]


def verificar_arvore(n, arestas, basicos, T):
    """Confere que T é uma árvore de G, sem ciclos, que conecta todos os básicos.
    Devolve o número de rótulos distintos usados."""
    existentes = {(min(u, v), max(u, v), c) for (u, v, c) in arestas}
    uf = UnionFind(n)
    for (u, v, c) in T:
        assert (min(u, v), max(u, v), c) in existentes, "aresta inexistente"
        assert uf.unir(u, v), "ciclo"
    assert len({uf.achar(b) for b in basicos}) == 1, "básicos desconectados"
    return len({c for (_, _, c) in T})


# ---------------------------------------------------------------------------
# Passo guloso genérico
# ---------------------------------------------------------------------------
def avaliar_rotulo(uf, por_rotulo_c, tem_basico, raizes_steiner):
    """Simula adicionar um rótulo sem alterar a estrutura principal.
    Devolve (componentes de Steiner resultantes, componentes sem básico absorvidas, uniões)."""
    pai = {}

    def achar(x):
        while pai.get(x, x) != x:
            x = pai[x]
        return x

    tb = {}
    unioes = absorvidas = 0
    for (u, v) in por_rotulo_c:
        a, b = achar(uf.achar(u)), achar(uf.achar(v))
        if a == b:
            continue
        ha, hb = tb.get(a, tem_basico[a]), tb.get(b, tem_basico[b])
        unioes += 1
        if ha != hb:              # uma tem básico e a outra não: absorção
            absorvidas += 1
        pai[b] = a
        tb[a] = ha or hb
    steiner = len({achar(r) for r in raizes_steiner})
    return steiner, absorvidas, unioes


def construir(n, l, por_rotulo, basicos, chave):
    """Laço guloso. 'chave' recebe (c, steiner, absorvidas, unioes) e devolve
    uma tupla: escolhe-se o rótulo com a MENOR chave."""
    uf = UnionFind(n)
    tem_basico = [False] * n
    for b in basicos:
        tem_basico[b] = True
    C, livres = [], set(range(l))
    raizes = {uf.achar(b) for b in basicos}
    while len(raizes) > 1:
        melhor, melhor_chave = None, None
        for c in livres:
            if not por_rotulo[c]:
                continue
            s, a, u = avaliar_rotulo(uf, por_rotulo[c], tem_basico, raizes)
            if u == 0:
                continue
            k = chave(c, s, a, u)
            if melhor_chave is None or k < melhor_chave:
                melhor, melhor_chave = c, k
        if melhor is None:
            raise ValueError("os vértices básicos não podem ser conectados")
        C.append(melhor)
        livres.discard(melhor)
        for (u, v) in por_rotulo[melhor]:
            a, b = uf.achar(u), uf.achar(v)
            if a != b:
                tb = tem_basico[a] or tem_basico[b]
                uf.unir(a, b)
                tem_basico[uf.achar(a)] = tb
        raizes = {uf.achar(b) for b in basicos}
    return C


def guloso_cerulli(n, l, arestas, basicos, eliminar=True):
    """Gulosa original: menor nº de componentes de Steiner; empate pelo menor índice."""
    por_rotulo = arestas_por_rotulo(l, arestas)
    C = construir(n, l, por_rotulo, basicos, chave=lambda c, s, a, u: (s, c))
    if eliminar:
        C = eliminar_redundantes(n, por_rotulo, basicos, C)
    return C


def resolver_e_mostrar(nome, funcao, caminho):
    n, l, arestas, basicos = ler(caminho)
    t = time.perf_counter()
    C = funcao(n, l, arestas, basicos)
    ms = 1000 * (time.perf_counter() - t)
    por_rotulo = arestas_por_rotulo(l, arestas)
    T = extrair_arvore(n, por_rotulo, basicos, C)
    k = verificar_arvore(n, arestas, basicos, T)
    print(f"{nome}: {len(C)} rótulos {sorted(C)}  ({ms:.1f} ms)")
    print(f"árvore verificada: {len(T)} arestas, {k} rótulos distintos")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("uso: python3 guloso.py instancia.txt")
    resolver_e_mostrar("Guloso (Cerulli et al., 2006)", guloso_cerulli, sys.argv[1])
