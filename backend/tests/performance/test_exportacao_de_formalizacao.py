"""O custo da página, da verificação e da montagem da formalização (117, SC-1111).

**Duas propriedades, medidas em separado.**

- **As consultas não crescem com as pessoas.** A página e a verificação de 5 e de 45 aptos custam o
  mesmo número de consultas, com a folga de `test_convocacao.py`. É o seletor em lote: uma consulta
  por pessoa não aparece com cinco, e aparece com o 72/2026.
- **O Cenário A cabe no tempo**: 40 aptos, 5 documentos de 1,5 MB cada — 200 arquivos, ~300 MB. A
  verificação e a montagem são **medidas e relatadas separadamente**, e cada uma termina em menos de
  30 s. **A transferência não é medida aqui**: não há rede real no CI, e ela é da VM (homologação,
  item 5). Este teste mede o código, e não a capacidade da VM.
"""

import time

import pytest
from django.db import connection
from django.test.utils import CaptureQueriesContext
from django.urls import reverse

from processo_seletivo.formalizacao.application import exportar
from processo_seletivo.formalizacao.domain import nomes
from processo_seletivo.seguranca.domain import Actor
from tests.fixtures.documentos_da_convocacao import (
    CERTIDAO,
    CERTIFICADO_DO_MEDIO,
    HISTORICO,
    IDENTIDADE,
    RESIDENCIA,
)
from tests.fixtures.formalizacao import (
    convocar_direto,
    definir_documentos,
    designar_direto,
    inscrever,
    montar_cenario_da_formalizacao,
    tornar_apta,
)
from tests.interface.conftest import identificar

pytestmark = [pytest.mark.django_db, pytest.mark.integration]

RUI = Actor("rui", "cefor", frozenset({nomes.CAPACIDADE}))
CINCO_DOCUMENTOS = (IDENTIDADE, CERTIDAO, HISTORICO, CERTIFICADO_DO_MEDIO, RESIDENCIA)
TETO_EM_SEGUNDOS = 30
UM_E_MEIO_MEGA = 1536 * 1024


def _mais_aptas(cenario, gestor, quantas, *, desde):
    for numero in range(desde, desde + quantas):
        inscricao = inscrever(cenario.edital, numero, documentos=(IDENTIDADE,))
        convocacao = convocar_direto(cenario.edital, inscricao)
        tornar_apta(cenario.edital, gestor, inscricao, convocacao, numero=numero)


def _consultas(funcao):
    with CaptureQueriesContext(connection) as capturadas:
        funcao()
    return len(capturadas)


def test_a_pagina_e_a_verificacao_nao_consultam_por_pessoa(
    gestor, api_client, manager_headers, process_payload, raiz_de_arquivos, client, settings
):
    """SC-1111: 5 e 45 aptos custam o mesmo, com folga de duas consultas."""
    settings.INTERFACE_SELETOR_IDENTIDADE = True
    cenario = montar_cenario_da_formalizacao(
        gestor,
        api_client,
        manager_headers,
        process_payload,
        aptas=5,
        da_inscricao=(IDENTIDADE,),
        prefixo="perf-117",
    )
    definir_documentos(cenario.edital, gestor, requisitos=CINCO_DOCUMENTOS)
    designar_direto(cenario.edital, "rui")
    identificar(client, "rui", ["formalizacao"])
    pagina = reverse("interface:formalizacao-edital", args=[cenario.edital.id])

    def ler_a_pagina():
        assert client.get(pagina).status_code == 200

    def verificar():
        exportar.verificar(RUI, edital_id=cenario.edital.id, alcance=nomes.RECORTE)

    ler_a_pagina()
    poucas = (_consultas(ler_a_pagina), _consultas(verificar))

    _mais_aptas(cenario, gestor, 40, desde=100)
    muitas = (_consultas(ler_a_pagina), _consultas(verificar))

    assert muitas[0] <= poucas[0] + 2, f"a página foi de {poucas[0]} a {muitas[0]} consultas"
    assert muitas[1] <= poucas[1] + 2, f"a verificação foi de {poucas[1]} a {muitas[1]} consultas"


def test_o_cenario_a_verifica_e_monta_em_menos_de_30_segundos_cada(
    gestor, api_client, manager_headers, process_payload, raiz_de_arquivos, capsys
):
    """SC-1111: 200 arquivos de 1,5 MB; verificação e montagem medidas e relatadas em separado."""
    cenario = montar_cenario_da_formalizacao(
        gestor,
        api_client,
        manager_headers,
        process_payload,
        aptas=40,
        tamanho=UM_E_MEIO_MEGA,
        da_inscricao=(IDENTIDADE,),
        prefixo="cenario-a-117",
    )
    definir_documentos(cenario.edital, gestor, requisitos=CINCO_DOCUMENTOS)
    designar_direto(cenario.edital, "rui")

    inicio = time.perf_counter()
    verificacao, comprovante = exportar.verificar(
        RUI, edital_id=cenario.edital.id, alcance=nomes.RECORTE
    )
    na_verificacao = time.perf_counter() - inicio
    assert verificacao.resultado == nomes.COMPLETO
    assert verificacao.documentos == 200

    inicio = time.perf_counter()
    gerado = exportar.baixar(RUI, edital_id=cenario.edital.id, token=comprovante)
    na_montagem = time.perf_counter() - inicio
    try:
        assert gerado.exportacao.quantidade_de_arquivos == 200
        tamanho = gerado.exportacao.tamanho
    finally:
        gerado.arquivo.close()

    with capsys.disabled():
        print(
            f"\n[117 · SC-1111] Cenário A: 40 aptos, 200 arquivos, {tamanho / 2**20:.0f} MB — "
            f"verificação {na_verificacao:.2f} s, montagem {na_montagem:.2f} s "
            "(transferência não medida no CI)"
        )
    assert na_verificacao < TETO_EM_SEGUNDOS
    assert na_montagem < TETO_EM_SEGUNDOS
