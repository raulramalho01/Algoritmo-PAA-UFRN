#!/usr/bin/env python3
"""
Compara o algoritmo exato (OPT) com o MVCA-Steiner, o guloso de Cerulli e o
Pilot Method, nas mesmas instâncias do trabalho 01 (médias de 10 instâncias
por classe). Imprime uma tabela no formato das Tabelas 1 a 3 do artigo.

Colunas:  q  l  d  OPT  MVCA-S  Cer.  Pilot  #ót.  #prov  ms(exato)
  #ót.   instâncias em que o MVCA-S atingiu OPT
  #prov  instâncias em que o exato provou a otimalidade dentro do limite
  † depois do OPT: a classe tem instância sem prova (OPT é a melhor solução achada)

Uso:
    python3 experimentos_exato.py 50                  # limite padrão: 60 s por instância
    python3 experimentos_exato.py 100 --limite 30
    python3 experimentos_exato.py 50 --sem-pilot
"""
import sys
import time

from experimentos import instancia
from gerador import DENSIDADES, FRACAO_L, FRACAO_Q, REPETICOES
from guloso import guloso_cerulli
from heuristica import mvca_steiner
from exato import exato_com_estatisticas
from pilot import pilot


def main():
    if len(sys.argv) < 2:
        sys.exit("uso: python3 experimentos_exato.py N [--limite SEGUNDOS] [--sem-pilot]")
    n = int(sys.argv[1])
    usar_pilot = "--sem-pilot" not in sys.argv
    limite = 60.0
    if "--limite" in sys.argv:
        limite = float(sys.argv[sys.argv.index("--limite") + 1])
    print(f"{'q':>4} {'l':>4} {'d':>4} | {'OPT':>5} {'MVCA-S':>6} {'Cer.':>5} {'Pilot':>5} | "
          f"{'#ót.':>4} {'#prov':>5} | {'ms exato':>9}")
    for fq in FRACAO_Q:
        q = int(fq * n)
        soma = [0.0, 0.0, 0.0, 0.0]
        for fl in FRACAO_L:
            l = int(fl * n)
            for d in DENSIDADES:
                v = [0, 0, 0, 0]
                otimos = provados = 0
                tempo = 0.0
                for r in range(REPETICOES):
                    inst = instancia(n, l, d, q, r)
                    t = time.perf_counter()
                    C, info = exato_com_estatisticas(*inst, limite=limite)
                    tempo += time.perf_counter() - t
                    h = len(mvca_steiner(*inst))
                    v[0] += len(C)
                    v[1] += h
                    v[2] += len(guloso_cerulli(*inst))
                    if usar_pilot:
                        v[3] += len(pilot(*inst))
                    otimos += h == len(C)
                    provados += info["otimo"]
                m = [x / REPETICOES for x in v]
                for i in range(4):
                    soma[i] += m[i]
                marca = "" if provados == REPETICOES else "†"
                p = f"{m[3]:5.1f}" if usar_pilot else "    -"
                print(f"{q:>4} {l:>4} {d:>4} | {m[0]:5.1f}{marca or ' '} {m[1]:5.1f} {m[2]:5.1f} {p} | "
                      f"{otimos:>4} {provados:>5} | {1000 * tempo / REPETICOES:9.1f}", flush=True)
        p = f"{soma[3]:5.1f}" if usar_pilot else "    -"
        print(f"{'soma':>14} | {soma[0]:5.1f}  {soma[1]:5.1f} {soma[2]:5.1f} {p} |")


if __name__ == "__main__":
    main()
