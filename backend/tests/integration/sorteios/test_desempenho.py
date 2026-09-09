"""Trezentos participantes, do congelamento à ordem, dentro do tempo de uma tomada (SC-004).

**A grandeza que importa não é o SHA-256.** Trezentas chaves são trabalho desprezível; o custo real
é a chamada à fonte externa, e ela acontece **antes** da transação, num comando separado. Este teste
mede o que o operador vive ao vivo: publicar a relação e constituir o ato.

O limite é generoso de propósito — o que se quer detectar é a regressão de ordem de grandeza, como
uma consulta por participante nascendo dentro de um laço, e não a variação de uma máquina para
outra.
"""

import time

import pytest

from processo_seletivo.sorteios.application.ocorrencia import observar_ocorrencia
from processo_seletivo.sorteios.application.relacao import publicar_relacao
from processo_seletivo.sorteios.application.sorteio import constituir_sorteio
from processo_seletivo.sorteios.infrastructure.fontes.loteria_federal import FonteDeTeste
from tests.fixtures.sorteio import METODO, certame_de_sorteio, presidente

pytestmark = [pytest.mark.integration, pytest.mark.django_db(transaction=True)]

PARTICIPANTES = 300
LIMITE_SEGUNDOS = 60.0


def test_trezentos_participantes_do_congelamento_a_ordem(
    gestor, api_client, manager_headers, process_payload, capsys
):
    certame = certame_de_sorteio(
        gestor, api_client, manager_headers, process_payload, quantos=PARTICIPANTES
    )

    inicio = time.monotonic()
    relacao_id = publicar_relacao(
        actor=presidente(),
        processo_id=certame["processo"].id,
        edital_id=certame["edital"].id,
        perfil_id=certame["perfil"],
        marco_id=certame["marco"],
        idempotency_key="desempenho-relacao",
        correlation_id="teste-021",
    )["relacao"]
    congelamento = time.monotonic() - inicio

    observar_ocorrencia(
        actor=presidente(),
        processo_id=certame["processo"].id,
        fonte=METODO["source"],
        referencia=METODO["occurrence"],
        idempotency_key="desempenho-ocorrencia",
        correlation_id="teste-021",
        fonte_externa=FonteDeTeste(),
    )

    antes_do_ato = time.monotonic()
    declarado = constituir_sorteio(
        actor=presidente(),
        processo_id=certame["processo"].id,
        edital_id=certame["edital"].id,
        relacao_id=relacao_id,
        ocorrencia_id=observar_ocorrencia(
            actor=presidente(),
            processo_id=certame["processo"].id,
            fonte=METODO["source"],
            referencia=METODO["occurrence"],
            idempotency_key="desempenho-ocorrencia-2",
            correlation_id="teste-021",
            fonte_externa=FonteDeTeste(),
        )["ocorrencia"],
        idempotency_key="desempenho-sorteio",
        correlation_id="teste-021",
    )
    constituicao = time.monotonic() - antes_do_ato
    total = time.monotonic() - inicio

    with capsys.disabled():
        print(
            f"\n[SC-004] {PARTICIPANTES} participantes — congelamento {congelamento:.2f}s, "
            f"constituição {constituicao:.2f}s, total {total:.2f}s"
        )

    assert declarado["quantidade"] == PARTICIPANTES
    assert total < LIMITE_SEGUNDOS, f"{total:.2f}s para {PARTICIPANTES} participantes"
