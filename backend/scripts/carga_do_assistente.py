#!/usr/bin/env python3
"""As medições do piloto do assistente na L4 (071, `R-018`, `FR-1517`).

Monta pela aplicação as mensagens de uma pergunta fixa sobre o Edital — as fontes completas da
versão vigente, como a tela as manda — e chama o **serviço** diretamente, em 1, 2 e 4 perguntas
simultâneas. Imprime, por nível, o tempo até a resposta (p50 e p95), os tokens, os términos e as
falhas, com os instantes de início e fim: a memória e a ocupação da GPU são lidas na própria L4,
por quem a opera (`nvidia-smi`, `ollama ps`), e os instantes casam as duas leituras.

**Fora da suíte e só do serviço local**, como o `carga_publica.py`: os números dependem da L4, e no
serviço externo eles não diriam nada dela, e cada chamada custaria — o script recusa. Também passa
por fora do teto global da aplicação, de propósito: é ele que se mede aqui, para o
`ASSISTENTE_TETO_SIMULTANEO` (`SC-556`).

Com `--carga-publica`, roda o `carga_publica.py` contra a API pública antes de tudo, sem carga, e
de novo em paralelo com cada nível, e imprime os dois lado a lado (`SC-557`). A página pública não
entra: o harness do repositório mede a API.

Uso, em `backend/`, no shell preparado como no quickstart da `071`:

    uv run python scripts/carga_do_assistente.py --edital 92/2026 --simultaneas 1,2,4 \\
        --repeticoes 10 [--carga-publica http://localhost:8000/api/v1 --edital-publico <uuid>]
"""

import argparse
import json
import os
import subprocess
import sys
import threading
import time
from collections import Counter
from datetime import datetime
from pathlib import Path

from carga_publica import percentil

RAIZ = Path(__file__).resolve().parents[1]
PERGUNTA = "Até quando posso me inscrever, quantas vagas há e que documentos preciso enviar?"
# A carga pública de cada nível é curta, para caber inteira dentro dele: o que passasse do fim do
# nível seria medido sem a carga do piloto, e o script avisa quando isso acontece.
WORKERS_PUBLICOS = 10
DURACAO_PUBLICA = 15


def preparar_django():
    sys.path.insert(0, str(RAIZ))
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.development")
    import django

    django.setup()


def mensagens_do_edital(referencia):
    from django.utils import timezone

    from processo_seletivo.duvidas.application.consultar import contexto
    from processo_seletivo.duvidas.domain import fontes, mensagens
    from processo_seletivo.processos.models import Edital

    numero, ano = referencia.split("/")
    edital = Edital.objects.get(number=numero, year=int(ano))
    lido = contexto(edital_id=edital.id, instante=timezone.now())
    return mensagens.montar(lido, fontes.fontes_completas(lido), [], PERGUNTA).mensagens


def uma_chamada(mensagens):
    from processo_seletivo.duvidas.domain.mensagens import ESQUEMA_DA_SAIDA
    from processo_seletivo.duvidas.infrastructure import inferencia

    inicio = time.monotonic()
    try:
        devolucao = inferencia.conversar(
            mensagens, ESQUEMA_DA_SAIDA, inferencia.parametros_configurados()
        )
    except inferencia.FalhaDoServico as falha:
        return {"segundos": time.monotonic() - inicio, "falha": falha.codigo}
    return {
        "segundos": time.monotonic() - inicio,
        "entrada": devolucao.tokens_de_entrada,
        "saida": devolucao.tokens_de_saida,
        "termino": devolucao.termino or "—",
    }


def um_nivel(mensagens, simultaneas, repeticoes):
    """`simultaneas` perguntas ao mesmo tempo, cada uma repetida `repeticoes` vezes."""
    amostras, trava = [], threading.Lock()
    partida = threading.Barrier(simultaneas)

    def trabalhador():
        partida.wait()
        for _ in range(repeticoes):
            resultado = uma_chamada(mensagens)
            with trava:
                amostras.append(resultado)

    threads = [threading.Thread(target=trabalhador) for _ in range(simultaneas)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    return amostras


def iniciar_carga_publica(base, edital):
    return subprocess.Popen(
        [
            sys.executable,
            str(Path(__file__).with_name("carga_publica.py")),
            "--base-url",
            base,
            "--edital",
            edital,
            "--workers",
            str(WORKERS_PUBLICOS),
            "--duracao",
            str(DURACAO_PUBLICA),
        ],
        stdout=subprocess.PIPE,
        text=True,
    )


def resultado_publico(processo):
    saida, _ = processo.communicate()
    try:
        return json.loads(saida)
    except ValueError:
        return None


def p95_publico(relatorio):
    if not relatorio:
        return "sem resultado"
    partes = []
    for caminho in ("versao-vigente", "historico"):
        item = relatorio.get(caminho) or {}
        falhas = item.get("amostras", 0) - item.get("status", {}).get("200", 0)
        partes.append(f"{caminho} {item.get('p95Ms')} ms, {falhas} falhas")
    return "; ".join(partes)


def agora():
    return datetime.now().astimezone().isoformat(timespec="seconds")


def segundos(valor):
    return "—" if valor is None else f"{valor / 1000:.1f} s".replace(".", ",")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--edital", required=True, help="número/ano de um Edital publicado")
    parser.add_argument("--simultaneas", default="1,2,4")
    parser.add_argument("--repeticoes", type=int, default=10)
    parser.add_argument("--carga-publica", default=None, help="raiz da API pública")
    parser.add_argument("--edital-publico", default=None, help="uuid do Edital na API pública")
    argumentos = parser.parse_args()
    if bool(argumentos.carga_publica) != bool(argumentos.edital_publico):
        parser.error("--carga-publica e --edital-publico vão juntos")

    preparar_django()
    from django.conf import settings

    from processo_seletivo.duvidas.infrastructure import inferencia, tokens

    if settings.ASSISTENTE_SERVICO != inferencia.OLLAMA:
        sys.exit("As medições são do serviço local: ASSISTENTE_SERVICO precisa ser ollama.")
    mensagens = mensagens_do_edital(argumentos.edital)
    try:
        medidos = tokens.contar(mensagens)
    except tokens.SemTokenizer:
        medidos = None
    print(
        f"Edital {argumentos.edital}; modelo {settings.ASSISTENTE_MODELO}; contexto "
        f"{settings.ASSISTENTE_CONTEXTO_TOKENS}; entrada medida: {medidos or '—'} tokens"
    )

    sem_carga = None
    if argumentos.carga_publica:
        print(f"API pública sem a carga do piloto — de {agora()}")
        sem_carga = resultado_publico(
            iniciar_carga_publica(argumentos.carga_publica, argumentos.edital_publico)
        )
        print(f"  até {agora()}: {p95_publico(sem_carga)}")

    for simultaneas in (int(item) for item in argumentos.simultaneas.split(",")):
        publico = None
        if argumentos.carga_publica:
            publico = iniciar_carga_publica(argumentos.carga_publica, argumentos.edital_publico)
        inicio = agora()
        amostras = um_nivel(mensagens, simultaneas, argumentos.repeticoes)
        fim = agora()
        tempos = [amostra["segundos"] for amostra in amostras if "falha" not in amostra]
        falhas = Counter(amostra["falha"] for amostra in amostras if "falha" in amostra)
        terminos = Counter(amostra["termino"] for amostra in amostras if "termino" in amostra)
        entradas = sorted({amostra["entrada"] for amostra in amostras if amostra.get("entrada")})
        saidas = [amostra["saida"] for amostra in amostras if amostra.get("saida")]
        print(f"{simultaneas} simultâneas — de {inicio} a {fim}")
        print(
            f"  amostras {len(amostras)}; falhas: "
            + (", ".join(f"{codigo} {n}" for codigo, n in sorted(falhas.items())) or "nenhuma")
        )
        print(
            f"  tempo p50 {segundos(percentil(tempos, 0.50))}  p95 "
            f"{segundos(percentil(tempos, 0.95))}"
        )
        print(
            f"  tokens de entrada {', '.join(map(str, entradas)) or '—'}  saída p50 "
            f"{sorted(saidas)[len(saidas) // 2] if saidas else '—'}  términos: "
            + (", ".join(f"{termino} {n}" for termino, n in sorted(terminos.items())) or "—")
        )
        if publico is not None:
            if publico.poll() is None:
                print(
                    "  aviso: a carga pública passou do fim do nível; parte dela foi medida sem a "
                    "carga do piloto"
                )
            com_carga = resultado_publico(publico)
            print(f"  API pública com a carga: {p95_publico(com_carga)}")
            print(f"  API pública sem a carga: {p95_publico(sem_carga)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
