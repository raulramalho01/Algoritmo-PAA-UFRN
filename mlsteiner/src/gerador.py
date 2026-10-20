#!/usr/bin/env python3
"""
Gerador de instâncias para o problema da Árvore de Steiner com Rotulação
Mínima (MLSteiner), no esquema de Cerulli et al. (2006) e Consoli et al. (2009).

Parâmetros de uma instância:
    n  número de vértices
    l  número de rótulos (cores)
    d  densidade do grafo: m = d * n(n-1)/2 arestas
    q  número de vértices básicos (terminais)

Formato do arquivo gerado:
    linha 1:  n m l q
    linha 2:  os q vértices básicos (numerados de 0 a n-1)
    demais:   uma aresta por linha: u v rótulo

Uso:
    python3 gerador.py 100 125 0.2 40 --seed 7 -o inst.txt   # uma instância
    python3 gerador.py --banco instancias/                   # banco completo (720)
"""
import argparse
import os
import random


def gerar(n, l, d, q, seed):
    """Gera uma instância e devolve (n, l, arestas, basicos).
    arestas é uma lista de tuplas (u, v, rotulo)."""
    rng = random.Random(seed)
    m = max(n - 1, round(d * n * (n - 1) / 2))

    # 1) árvore geradora aleatória: garante que o grafo é conexo.
    #    Cada vértice (numa ordem aleatória) liga-se a um vértice anterior.
    ordem = list(range(n))
    rng.shuffle(ordem)
    arestas = set()
    for i in range(1, n):
        u, v = ordem[i], ordem[rng.randrange(i)]
        arestas.add((min(u, v), max(u, v)))

    # 2) completa até m arestas, sorteando pares distintos uniformemente.
    faltam = m - len(arestas)
    if d > 0.5:
        # grafo denso: embaralhar a lista de pares livres é mais rápido
        livres = [(i, j) for i in range(n) for j in range(i + 1, n)
                  if (i, j) not in arestas]
        rng.shuffle(livres)
        arestas.update(livres[:faltam])
    else:
        while len(arestas) < m:
            u, v = rng.randrange(n), rng.randrange(n)
            if u != v:
                arestas.add((min(u, v), max(u, v)))

    # 3) um rótulo uniforme para cada aresta
    rotuladas = [(u, v, rng.randrange(l)) for (u, v) in sorted(arestas)]

    # 4) q vértices básicos sorteados sem reposição
    basicos = rng.sample(range(n), q)
    return n, l, rotuladas, basicos


def salvar(caminho, n, l, arestas, basicos):
    with open(caminho, "w") as f:
        f.write(f"{n} {len(arestas)} {l} {len(basicos)}\n")
        f.write(" ".join(map(str, basicos)) + "\n")
        for (u, v, c) in arestas:
            f.write(f"{u} {v} {c}\n")


def ler(caminho):
    """Lê um arquivo de instância e devolve (n, l, arestas, basicos)."""
    with open(caminho) as f:
        n, m, l, q = map(int, f.readline().split())
        basicos = list(map(int, f.readline().split()))
        arestas = [tuple(map(int, f.readline().split())) for _ in range(m)]
    return n, l, arestas, basicos


# Classes usadas no artigo: 3 x 2 x 4 x 3 = 72 classes, 10 instâncias cada.
NS = [50, 100, 500]
FRACAO_Q = [0.2, 0.4]
FRACAO_L = [0.25, 0.5, 1.0, 1.25]
DENSIDADES = [0.8, 0.5, 0.2]
REPETICOES = 10


def classes():
    for n in NS:
        for fq in FRACAO_Q:
            for fl in FRACAO_L:
                for d in DENSIDADES:
                    yield n, int(fl * n), d, int(fq * n)


def semente(n, l, d, q, r):
    """Semente determinística: a mesma classe e repetição geram sempre a mesma instância."""
    return n * 1_000_000 + l * 10_000 + int(d * 10) * 1000 + q * 10 + r


def nome_arquivo(n, l, d, q, r):
    return f"mls_n{n}_l{l}_d{int(d * 10)}_q{q}_{r}.txt"


def gerar_banco(pasta):
    os.makedirs(pasta, exist_ok=True)
    total = 0
    for (n, l, d, q) in classes():
        for r in range(REPETICOES):
            inst = gerar(n, l, d, q, semente(n, l, d, q, r))
            salvar(os.path.join(pasta, nome_arquivo(n, l, d, q, r)), *inst)
            total += 1
    print(f"{total} instâncias gravadas em {pasta}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Gerador de instâncias MLSteiner")
    ap.add_argument("n", type=int, nargs="?")
    ap.add_argument("l", type=int, nargs="?")
    ap.add_argument("d", type=float, nargs="?")
    ap.add_argument("q", type=int, nargs="?")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("-o", "--saida", default="instancia.txt")
    ap.add_argument("--banco", metavar="PASTA", help="gera o banco completo de 720 instâncias")
    a = ap.parse_args()
    if a.banco:
        gerar_banco(a.banco)
    elif None in (a.n, a.l, a.d, a.q):
        ap.error("informe n l d q, ou use --banco PASTA")
    else:
        inst = gerar(a.n, a.l, a.d, a.q, a.seed)
        salvar(a.saida, *inst)
        print(f"instância gravada em {a.saida} ({len(inst[2])} arestas)")
