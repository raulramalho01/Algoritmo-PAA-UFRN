#!/usr/bin/env python3
"""
Roda os algoritmos em todas as instâncias de um tamanho n e imprime uma tabela
no formato das Tabelas 1 a 3 do artigo (médias de 10 instâncias por classe).

Colunas:  q  l  d  MVCA-S  Cer.  s/elim.  Pilot  ms
(A coluna OPT do artigo vem de um solver exato externo e não é recalculada aqui.)

Uso:
    python3 experimentos.py 50                # gera as instâncias, se preciso, e roda
    python3 experimentos.py 100 --sem-pilot   # pula o Pilot (mais lento)
    python3 experimentos.py 500 --sem-pilot   # n=500: o Pilot leva muito tempo
"""
import os
import sys
import time

from gerador import (DENSIDADES, FRACAO_L, FRACAO_Q, REPETICOES, gerar, ler,
                     nome_arquivo, salvar, semente)
from guloso import guloso_cerulli
from heuristica import mvca_steiner
from pilot import pilot

PASTA = "instancias"


def instancia(n, l, d, q, r):
    caminho = os.path.join(PASTA, nome_arquivo(n, l, d, q, r))
    if not os.path.exists(caminho):
        os.makedirs(PASTA, exist_ok=True)
        salvar(caminho, *gerar(n, l, d, q, semente(n, l, d, q, r)))
    return ler(caminho)


def main():
    if len(sys.argv) < 2:
        sys.exit("uso: python3 experimentos.py N [--sem-pilot]")
    n = int(sys.argv[1])
    usar_pilot = "--sem-pilot" not in sys.argv
    print(f"{'q':>4} {'l':>4} {'d':>4} | {'MVCA-S':>6} {'Cer.':>5} {'s/elim':>6} {'Pilot':>5} | {'ms':>6}")
    for fq in FRACAO_Q:
        q = int(fq * n)
        soma = [0.0, 0.0, 0.0, 0.0]
        for fl in FRACAO_L:
            l = int(fl * n)
            for d in DENSIDADES:
                v = [0, 0, 0, 0]
                tempo = 0.0
                for r in range(REPETICOES):
                    inst = instancia(n, l, d, q, r)
                    t = time.perf_counter()
                    v[0] += len(mvca_steiner(*inst))
                    tempo += time.perf_counter() - t
                    v[1] += len(guloso_cerulli(*inst))
                    v[2] += len(mvca_steiner(*inst, eliminar=False))
                    if usar_pilot:
                        v[3] += len(pilot(*inst))
                m = [x / REPETICOES for x in v]
                for i in range(4):
                    soma[i] += m[i]
                p = f"{m[3]:5.1f}" if usar_pilot else "    -"
                print(f"{q:>4} {l:>4} {d:>4} | {m[0]:6.1f} {m[1]:5.1f} {m[2]:6.1f} {p} | "
                      f"{1000 * tempo / REPETICOES:6.1f}", flush=True)
        p = f"{soma[3]:5.1f}" if usar_pilot else "    -"
        print(f"{'soma':>14} | {soma[0]:6.1f} {soma[1]:5.1f} {soma[2]:6.1f} {p} |")


if __name__ == "__main__":
    main()
