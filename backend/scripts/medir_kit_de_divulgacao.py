#!/usr/bin/env python3
"""Mede, no servidor de homologação, o que o SC-1137 e o SC-1134 pedem do kit (119, T044).

Roteiro de verificação, e não do produto: lê um Edital publicado, **não grava nada** — nenhum
evento de exportação, nenhuma linha — e imprime, num lote de N gerações:

- **a tela**: a ficha lida e as peças dos formatos liberados da família compostas e rasterizadas,
  que é o trabalho do servidor para abrir o kit com as três prévias;
- **o ZIP**: o pacote da família inteiro, como a exportação o monta;
- **a repetibilidade**: o SHA-256 do PNG de cada formato em duas gerações seguidas, que precisa ser
  o mesmo.

Rode de `backend/`, no servidor, com as settings do ambiente e o endereço público dele:

    DJANGO_SETTINGS_MODULE=config.settings.production \\
        uv run python scripts/medir_kit_de_divulgacao.py \\
        --edital <id do Edital> --base-url https://<endereço público> --familia pos-lato-sensu

**O tempo daqui é o do servidor**, sem rede nem navegador. O SC-1137 é medido no navegador; este
número diz quanto dele é do servidor, e é o que muda quando o código muda. Os dois vão para o
`verificacao.md`.

**Por que em `scripts/`, e não um comando de gestão**: é ferramenta de verificação de uma feature,
como a galeria; não tem lugar no produto.
"""

import argparse
import hashlib
import os
import statistics
import sys
import time
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
if "DJANGO_SETTINGS_MODULE" not in os.environ:
    sys.exit("Defina DJANGO_SETTINGS_MODULE com as settings do ambiente medido.")

import django  # noqa: E402

django.setup()

from django.utils import timezone  # noqa: E402

from processo_seletivo.interface import (  # noqa: E402
    kit_de_divulgacao,
    kit_escolha,
    kit_familias,
    kit_pacote,
    kit_peca,
)
from processo_seletivo.portal import ficha as fichas  # noqa: E402
from processo_seletivo.processos.models import Edital  # noqa: E402

#: Os tetos do SC-1137, em segundos.
TETO_DA_TELA = 2.0
TETO_DO_ZIP = 3.0


def _pecas(edital, base_url, dados):
    """As peças dos formatos liberados, com o PNG de cada uma: o trabalho da tela com as prévias."""
    ficha = fichas.ler(edital, agora=timezone.now(), base_url=base_url)
    escolhida = kit_escolha.ler(dados, ficha, edital)
    liberados = kit_familias.liberados()
    lista = kit_escolha.manchetes(ficha, escolhida, liberados)
    saida = {}
    for template in kit_escolha.templates_da_familia(escolhida.familia):
        formato = template.formato.chave
        try:
            peca = kit_escolha.compor(ficha, escolhida, formato, liberados, lista)
        except kit_peca.PecaRecusada as recusa:
            saida[formato] = f"sem peça: {recusa.motivo}"
            continue
        png = kit_pacote.rasterizar(kit_peca.svg(peca, ficha), kit_peca.fontes_da_peca(peca))
        saida[formato] = hashlib.sha256(png).hexdigest()
    return ficha, saida


def _zip(edital, base_url, dados):
    ficha = fichas.ler(edital, agora=timezone.now(), base_url=base_url)
    conteudo, _ = kit_de_divulgacao.pacote_da_familia(ficha, edital, dados, None)
    return conteudo


def _cronometrar(funcao, vezes):
    tempos = []
    for _ in range(vezes):
        inicio = time.perf_counter()
        funcao()
        tempos.append(time.perf_counter() - inicio)
    return tempos


def _resumo(nome, tempos, teto):
    mediana, maximo = statistics.median(tempos), max(tempos)
    situacao = "dentro" if maximo < teto else "ACIMA"
    return (
        f"{nome}: mediana {mediana:.3f} s, máximo {maximo:.3f} s em {len(tempos)} gerações "
        f"— {situacao} do teto de {teto:.0f} s (só servidor)"
    )


def main():
    argumentos = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    argumentos.add_argument("--edital", required=True, help="o id do Edital publicado")
    argumentos.add_argument("--base-url", required=True, help="o endereço público do ambiente")
    argumentos.add_argument("--familia", default="pos-lato-sensu")
    argumentos.add_argument("--imagem", default="", help="vazio: a primeira do banco")
    argumentos.add_argument("--lote", type=int, default=20)
    opcoes = argumentos.parse_args()

    if not kit_pacote.disponivel():
        sys.exit("O rasterizador (resvg-py) não está instalado neste ambiente: não há PNG.")
    edital = Edital.objects.get(pk=opcoes.edital)
    dados = {"familia": opcoes.familia}
    if opcoes.imagem:
        dados["imagem"] = opcoes.imagem
    base_url = opcoes.base_url.rstrip("/")

    ficha, primeira = _pecas(edital, base_url, dados)
    if not ficha.tem_material:
        sys.exit(f"O Edital não tem material: {ficha.motivo}")
    _, segunda = _pecas(edital, base_url, dados)
    print(
        f"Edital {ficha.numero}/{ficha.ano}, família {opcoes.familia}, impressão {ficha.impressao}"
    )
    print("Liberados:", ", ".join(t.identificador for t in kit_familias.liberados()))
    for formato, valor in primeira.items():
        igual = "idêntico" if valor == segunda.get(formato) else "DIFERENTE"
        print(f"  {formato}: {valor} — {igual} na segunda geração (SC-1134)")

    print(
        _resumo(
            "Tela com as prévias",
            _cronometrar(lambda: _pecas(edital, base_url, dados), opcoes.lote),
            TETO_DA_TELA,
        )
    )
    print(
        _resumo(
            "ZIP da família",
            _cronometrar(lambda: _zip(edital, base_url, dados), opcoes.lote),
            TETO_DO_ZIP,
        )
    )


if __name__ == "__main__":
    main()
