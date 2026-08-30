#!/usr/bin/env python3
"""Harness de carga para o SLO das consultas públicas (T092).

A suíte em `tests/performance/` garante que o custo por consulta não cresce com o histórico.
O SLO do plan.md — p95 até 2 s e pico de 500 consultas por segundo — é outra coisa: depende de
servidor de aplicação, pool de conexões, rede e banco dimensionado, nada disso presente numa
suíte de teste. Este script mede contra um serviço já implantado.

Não faz parte da suíte automatizada: os números dependem do ambiente e falhariam por motivo
errado em CI. Rode contra homologação, com dados representativos, e registre o resultado.

Uso:
    python scripts/carga_publica.py --base-url https://homologacao.exemplo/api/v1 \\
        --edital <uuid> --workers 50 --duracao 60

Saída: JSON com p50/p95/p99, throughput e distribuição de status.
"""

import argparse
import json
import statistics
import sys
import threading
import time
import urllib.error
import urllib.request
from collections import Counter

CAMINHOS = {
    "versao-vigente": "/public/editais/{edital}/versao-vigente",
    "historico": "/public/editais/{edital}/historico?limit=20",
}


def uma_consulta(url, timeout):
    inicio = time.monotonic()
    try:
        with urllib.request.urlopen(url, timeout=timeout) as resposta:
            resposta.read()
            return time.monotonic() - inicio, resposta.status
    except urllib.error.HTTPError as exc:
        return time.monotonic() - inicio, exc.code
    except Exception:  # noqa: BLE001 — indisponibilidade é resultado de medição, não erro do script
        return time.monotonic() - inicio, 0


def executar(url, workers, duracao, timeout):
    amostras, status = [], Counter()
    trava = threading.Lock()
    fim = time.monotonic() + duracao
    partida = threading.Barrier(workers, timeout=30)

    def trabalhador():
        locais, locais_status = [], Counter()
        partida.wait()
        while time.monotonic() < fim:
            latencia, codigo = uma_consulta(url, timeout)
            locais.append(latencia)
            locais_status[codigo] += 1
        with trava:
            amostras.extend(locais)
            status.update(locais_status)

    threads = [threading.Thread(target=trabalhador) for _ in range(workers)]
    inicio = time.monotonic()
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    return amostras, status, time.monotonic() - inicio


def percentil(valores, fracao):
    if not valores:
        return None
    ordenados = sorted(valores)
    indice = min(int(len(ordenados) * fracao), len(ordenados) - 1)
    return round(ordenados[indice] * 1000, 2)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", required=True, help="raiz da API, por exemplo /api/v1")
    parser.add_argument("--edital", required=True, help="uuid de um Edital publicado")
    parser.add_argument("--workers", type=int, default=50)
    parser.add_argument("--duracao", type=float, default=30.0, help="segundos por cenário")
    parser.add_argument("--timeout", type=float, default=10.0)
    parser.add_argument("--slo-p95-ms", type=float, default=2000.0)
    argumentos = parser.parse_args()

    relatorio = {"workers": argumentos.workers, "duracaoSegundos": argumentos.duracao}
    dentro_do_slo = True

    for nome, caminho in CAMINHOS.items():
        url = argumentos.base_url.rstrip("/") + caminho.format(edital=argumentos.edital)
        amostras, status, decorrido = executar(
            url, argumentos.workers, argumentos.duracao, argumentos.timeout
        )
        p95 = percentil(amostras, 0.95)
        sucesso = status.get(200, 0)
        relatorio[nome] = {
            "amostras": len(amostras),
            "throughputPorSegundo": round(len(amostras) / decorrido, 1) if decorrido else None,
            "p50Ms": percentil(amostras, 0.50),
            "p95Ms": p95,
            "p99Ms": percentil(amostras, 0.99),
            "mediaMs": round(statistics.fmean(amostras) * 1000, 2) if amostras else None,
            "status": dict(sorted(status.items())),
            "taxaSucesso": round(sucesso / len(amostras), 4) if amostras else 0.0,
        }
        if p95 is None or p95 > argumentos.slo_p95_ms or sucesso != len(amostras):
            dentro_do_slo = False

    relatorio["sloP95Ms"] = argumentos.slo_p95_ms
    relatorio["dentroDoSlo"] = dentro_do_slo
    print(json.dumps(relatorio, indent=2, ensure_ascii=False))
    return 0 if dentro_do_slo else 1


if __name__ == "__main__":
    sys.exit(main())
