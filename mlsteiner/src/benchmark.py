#!/usr/bin/env python3
"""
Bateria de testes longa (para deixar rodando a noite): executa TODOS os
algoritmos do projeto em 3 classes de instâncias e grava os resultados em CSV.

Algoritmos:
    cerulli    guloso de Cerulli et al. (2006)            (guloso.py)
    mvca       MVCA-Steiner                               (heuristica.py)
    mvca_se    MVCA-Steiner sem eliminação de redundantes (heuristica.py)
    pilot      Pilot Method                               (pilot.py)
    exato      branch-and-bound                           (exato.py)

Classes (d = 0.2 e q = 0.4 n em todas, como no artigo). Os tempos foram
calibrados para que nenhuma seja trivial e a noite toda seja suficiente:
    pequena   n=100  l=50    exato ~ segundos
    media     n=150  l=75    exato ~ dezenas de segundos a minutos
    grande    n=300  l=300   exato costuma esbarrar no limite; Pilot ~ 2-3 min

Cada algoritmo roda 1 vez por instância, num processo separado com tempo
máximo (se travar, é morto e registrado como "timeout"). Cada resultado é
gravado no CSV assim que sai: se o script for interrompido, basta rodar o
mesmo comando de novo que ele continua de onde parou.

Uso:
    python3 benchmark.py                               # padrão: 10 instâncias/classe, limite 1200 s
    python3 benchmark.py --instancias 5 --limite 600   # bateria menor
    python3 benchmark.py --classes pequena media       # só algumas classes
    mkdir -p resultados && nohup python3 benchmark.py > resultados/log.txt 2>&1 &   # a noite

Saídas (pasta resultados/):
    benchmark.csv    uma linha por (instância, algoritmo)
    resumo.txt       médias por classe e algoritmo (gerado ao final)
"""
import argparse
import csv
import multiprocessing as mp
import os
import platform
import time
from collections import defaultdict
from datetime import datetime, timedelta

from exato import exato_com_estatisticas
from gerador import gerar, ler, salvar, semente
from guloso import (arestas_por_rotulo, extrair_arvore, guloso_cerulli,
                    verificar_arvore)
from heuristica import mvca_steiner
from pilot import pilot

CLASSES = {
    #  nome      n    l   d    q
    "pequena": (100, 50, 0.2, 40),
    "media":   (150, 75, 0.2, 60),
    "grande":  (300, 300, 0.2, 120),
}
ALGORITMOS = ["cerulli", "mvca", "mvca_se", "pilot", "exato"]
PASTA_INST = "instancias_benchmark"
CAMPOS = ["classe", "instancia", "n", "l", "d", "q", "m", "algoritmo", "status",
          "rotulos", "tempo_s", "otimo_provado", "nos_bb", "inicial_bb",
          "arvore_ok", "arestas_arvore", "solucao", "data_hora"]


# ---------------------------------------------------------------------------
# Execução de um algoritmo (roda no processo filho)
# ---------------------------------------------------------------------------
def executar(alg, caminho, limite, fila):
    try:
        n, l, arestas, basicos = ler(caminho)
        extra = {}
        t = time.perf_counter()
        if alg == "cerulli":
            C = guloso_cerulli(n, l, arestas, basicos)
        elif alg == "mvca":
            C = mvca_steiner(n, l, arestas, basicos)
        elif alg == "mvca_se":
            C = mvca_steiner(n, l, arestas, basicos, eliminar=False)
        elif alg == "pilot":
            C = pilot(n, l, arestas, basicos)
        elif alg == "exato":
            C, info = exato_com_estatisticas(n, l, arestas, basicos, limite=limite)
            extra = {"otimo_provado": int(info["otimo"]), "nos_bb": info["nos"],
                     "inicial_bb": info["inicial"]}
        else:
            raise ValueError(alg)
        dt = time.perf_counter() - t
        # confere a solução: extrai a árvore e valida (fora da medição de tempo)
        T = extrair_arvore(n, arestas_por_rotulo(l, arestas), basicos, C)
        try:
            verificar_arvore(n, arestas, basicos, T)
            ok = 1
        except AssertionError:
            ok = 0
        fila.put({"status": "ok", "rotulos": len(C), "tempo_s": f"{dt:.4f}",
                  "arvore_ok": ok, "arestas_arvore": len(T),
                  "solucao": " ".join(map(str, sorted(C))), **extra})
    except Exception as e:  # noqa: BLE001 - qualquer falha vira linha no CSV
        fila.put({"status": f"erro: {type(e).__name__}: {e}"})


def rodar_com_timeout(alg, caminho, limite_exato, limite_duro):
    fila = mp.Queue()
    p = mp.Process(target=executar, args=(alg, caminho, limite_exato, fila))
    inicio = time.perf_counter()
    p.start()
    try:
        res = fila.get(timeout=limite_duro)
    except Exception:  # queue.Empty: estourou o tempo máximo
        res = {"status": "timeout", "tempo_s": f"{time.perf_counter() - inicio:.4f}"}
    p.join(5)
    if p.is_alive():
        p.terminate()
        p.join()
    return res


# ---------------------------------------------------------------------------
# Instâncias, CSV e resumo
# ---------------------------------------------------------------------------
def preparar_instancia(classe, r):
    n, l, d, q = CLASSES[classe]
    os.makedirs(PASTA_INST, exist_ok=True)
    caminho = os.path.join(PASTA_INST, f"{classe}_n{n}_l{l}_d{int(d * 10)}_q{q}_{r}.txt")
    if not os.path.exists(caminho):
        salvar(caminho, *gerar(n, l, d, q, semente(n, l, d, q, r)))
    return caminho


def ja_feitos(csv_path):
    if not os.path.exists(csv_path):
        return set()
    with open(csv_path, newline="") as f:
        return {(row["classe"], row["instancia"], row["algoritmo"]) for row in csv.DictReader(f)}


def media(xs):
    return sum(xs) / len(xs) if xs else float("nan")


def resumo(csv_path, destino):
    with open(csv_path, newline="") as f:
        linhas = list(csv.DictReader(f))
    exato = {(r["classe"], r["instancia"]): int(r["rotulos"])
             for r in linhas if r["algoritmo"] == "exato" and r["status"] == "ok"}
    grupos = defaultdict(list)
    for r in linhas:
        grupos[(r["classe"], r["algoritmo"])].append(r)

    out = [f"Resumo gerado em {datetime.now():%Y-%m-%d %H:%M:%S} a partir de {csv_path}",
           "",
           "rótulos : média do nº de rótulos da solução",
           "=OPT    : instâncias em que atingiu o valor do exato (melhor conhecido)",
           "gap     : média de (rótulos - exato)",
           "prov.   : instâncias em que o exato provou otimalidade dentro do limite",
           "",
           f"{'classe':<8} {'algoritmo':<8} {'inst':>4} {'ok':>3} {'rótulos':>8} {'=OPT':>5} "
           f"{'gap':>6} {'t médio(s)':>11} {'t máx(s)':>10} {'prov.':>6}"]
    for classe in CLASSES:
        n, l, d, q = CLASSES[classe]
        if not any(k[0] == classe for k in grupos):
            continue
        out.append(f"--- {classe}: n={n} l={l} d={d} q={q}")
        for alg in ALGORITMOS:
            rs = grupos.get((classe, alg), [])
            if not rs:
                continue
            oks = [r for r in rs if r["status"] == "ok"]
            rot = [int(r["rotulos"]) for r in oks]
            ts = [float(r["tempo_s"]) for r in rs if r.get("tempo_s")]
            pares = [(int(r["rotulos"]), exato[(classe, r["instancia"])])
                     for r in oks if (classe, r["instancia"]) in exato]
            iguais = sum(a == b for a, b in pares)
            gap = media([a - b for a, b in pares])
            prov = (str(sum(int(r["otimo_provado"] or 0) for r in oks))
                    if alg == "exato" else "")
            out.append(f"{classe:<8} {alg:<8} {len(rs):>4} {len(oks):>3} {media(rot):>8.2f} "
                       f"{iguais:>5} {gap:>6.2f} {media(ts):>11.3f} "
                       f"{max(ts) if ts else float('nan'):>10.3f} {prov:>6}")
    texto = "\n".join(out) + "\n"
    with open(destino, "w") as f:
        f.write(texto)
    return texto


# ---------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser(description="Bateria noturna de testes MLSteiner")
    ap.add_argument("--instancias", type=int, default=10, help="instâncias por classe (padrão 10)")
    ap.add_argument("--limite", type=float, default=1200.0,
                    help="limite de tempo do exato por instância, em s (padrão 1200)")
    ap.add_argument("--limite-duro", type=float, default=3600.0,
                    help="tempo máximo de QUALQUER algoritmo antes de ser morto (padrão 3600)")
    ap.add_argument("--classes", nargs="+", choices=list(CLASSES), default=list(CLASSES))
    ap.add_argument("--algoritmos", nargs="+", choices=ALGORITMOS, default=ALGORITMOS)
    ap.add_argument("--saida", default="resultados", help="pasta de saída (padrão resultados/)")
    a = ap.parse_args()

    os.makedirs(a.saida, exist_ok=True)
    csv_path = os.path.join(a.saida, "benchmark.csv")
    feitos = ja_feitos(csv_path)
    novo = not os.path.exists(csv_path)
    tarefas = [(c, r, alg) for c in a.classes for r in range(a.instancias) for alg in a.algoritmos]
    pendentes = [t for t in tarefas if (t[0], str(t[1]), t[2]) not in feitos]

    print(f"Início: {datetime.now():%Y-%m-%d %H:%M:%S}  |  {platform.node()}  |  "
          f"Python {platform.python_version()}")
    print(f"Classes: {a.classes}  |  {a.instancias} instâncias/classe  |  algoritmos: {a.algoritmos}")
    print(f"Limite do exato: {a.limite:.0f} s  |  limite duro: {a.limite_duro:.0f} s")
    print(f"Tarefas: {len(tarefas)} no total, {len(tarefas) - len(pendentes)} já feitas, "
          f"{len(pendentes)} pendentes  ->  {csv_path}", flush=True)

    inicio = time.time()
    with open(csv_path, "a", newline="") as f:
        w = csv.DictWriter(f, fieldnames=CAMPOS)
        if novo:
            w.writeheader()
        for i, (classe, r, alg) in enumerate(pendentes, 1):
            n, l, d, q = CLASSES[classe]
            caminho = preparar_instancia(classe, r)
            with open(caminho) as fi:
                m = int(fi.readline().split()[1])
            res = rodar_com_timeout(alg, caminho, a.limite, a.limite_duro)
            linha = {"classe": classe, "instancia": r, "n": n, "l": l, "d": d, "q": q, "m": m,
                     "algoritmo": alg, "data_hora": f"{datetime.now():%Y-%m-%d %H:%M:%S}", **res}
            w.writerow(linha)
            f.flush()
            decorrido = time.time() - inicio
            extra = ""
            if alg == "exato" and res.get("status") == "ok":
                extra = " ótimo" if res.get("otimo_provado") else " SEM PROVA (limite)"
            print(f"[{i:>3}/{len(pendentes)}] {classe:<7} #{r} {alg:<8} "
                  f"{res.get('status', ''):<8} rótulos={res.get('rotulos', '-'):>3} "
                  f"t={float(res.get('tempo_s', 0)):9.2f}s{extra}  "
                  f"(decorrido {timedelta(seconds=int(decorrido))})", flush=True)

    print()
    print(resumo(csv_path, os.path.join(a.saida, "resumo.txt")))
    print(f"Fim: {datetime.now():%Y-%m-%d %H:%M:%S}  |  duração {timedelta(seconds=int(time.time() - inicio))}")


if __name__ == "__main__":
    main()
