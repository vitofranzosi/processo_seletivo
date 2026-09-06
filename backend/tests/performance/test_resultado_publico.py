"""O custo da página pública do resultado, medido em **consultas** (T-013).

A asserção é sobre consultas, e não sobre tempo — pelo mesmo motivo que em `test_public_queries.py`:
contagem de consultas é determinística e detecta a degradação que importa, enquanto tempo de parede
em suíte de teste depende da máquina.

**E não se promete tempo invariável.** Desserializar, montar o HTML e transmiti-lo crescem com o
número de posições, como em qualquer lista. O que a página promete é derivada zero em consultas: ela
lê a publicação e a cadeia que diz se ela ainda é a vigente, e mais nada. A composição do conteúdo,
essa proporcional ao universo, acontece **uma vez**, dentro do comando de publicar.
"""

import pytest
from django.db import connection
from django.test.utils import CaptureQueriesContext
from django.urls import reverse

from processo_seletivo.divulgacao.models import PublicacaoResultado
from tests.fixtures.divulgacao import montar_ato_publicavel, publicar_o_ato

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.performance]


def _publicar_com(gestor, api_client, manager_headers, process_payload, *, quantas, seed, codigo):
    cenario = montar_ato_publicavel(
        gestor,
        api_client,
        manager_headers,
        process_payload,
        seed=seed,
        codigo=codigo,
        pontuacoes=tuple(f"{50 + n % 50}.0000" for n in range(quantas)),
        primeiro=2000 + seed * 100,
    )
    return publicar_o_ato(cenario, chave=f"publicar-carga-{seed}")


def _consultas_da_pagina(client, publicacao):
    with CaptureQueriesContext(connection) as capturadas:
        resposta = client.get(reverse("portal:resultado", args=[publicacao.id]))
    assert resposta.status_code == 200
    return len(capturadas.captured_queries)


def test_o_custo_em_consultas_nao_cresce_com_o_numero_de_posicoes(
    client, gestor, api_client, manager_headers, process_payload
):
    """Derivada zero entre uma lista curta e uma longa — a promessa de T-013.

    Se a página compusesse o conteúdo na leitura em vez de lê-lo gravado, o custo cresceria com o
    universo, e é exatamente essa regressão que este teste denuncia.
    """
    curta = _publicar_com(
        gestor, api_client, manager_headers, process_payload, quantas=3, seed=70, codigo="0770"
    )
    barata = _consultas_da_pagina(client, curta)

    longa = _publicar_com(
        gestor,
        api_client,
        {**manager_headers, "HTTP_IDEMPOTENCY_KEY": "carga-017-0771"},
        process_payload,
        quantas=40,
        seed=71,
        codigo="0771",
    )
    cara = _consultas_da_pagina(client, longa)

    assert barata == cara, (
        f"o custo cresceu com a lista: {barata} consultas com 3 posições, {cara} com 40 — "
        "a página lê o conteúdo gravado, e não o recompõe"
    )


def test_a_pagina_custa_um_numero_pequeno_e_declarado_de_consultas(
    client, gestor, api_client, manager_headers, process_payload
):
    """A publicação e a cadeia: duas leituras, e o teto existe para que uma terceira apareça."""
    publicacao = _publicar_com(
        gestor, api_client, manager_headers, process_payload, quantas=3, seed=72, codigo="0772"
    )

    quantidade = _consultas_da_pagina(client, publicacao)

    assert quantidade <= 3, (
        f"a página custou {quantidade} consultas: são a publicação e a cadeia das sucessoras, "
        "e uma terceira leitura precisa ser justificada"
    )


def test_o_documento_custa_uma_consulta(
    client, gestor, api_client, manager_headers, process_payload
):
    """Ele entrega bytes gravados; recompor qualquer coisa apareceria aqui."""
    publicacao = _publicar_com(
        gestor, api_client, manager_headers, process_payload, quantas=3, seed=73, codigo="0773"
    )

    with CaptureQueriesContext(connection) as capturadas:
        resposta = client.get(reverse("portal:resultado-documento", args=[publicacao.id]))
    assert resposta.status_code == 200

    assert len(capturadas.captured_queries) <= 1


def test_a_composicao_acontece_uma_vez_dentro_do_comando(
    gestor, api_client, manager_headers, process_payload
):
    """O custo proporcional ao universo existe — e mora onde deve, no ato de publicar.

    Este teste não afirma que publicar é barato: afirma que ele é o **único** lugar que paga o
    preço, e que a leitura pública não o paga de novo a cada acesso.
    """
    publicacao = _publicar_com(
        gestor, api_client, manager_headers, process_payload, quantas=5, seed=74, codigo="0774"
    )

    assert PublicacaoResultado.objects.get(pk=publicacao.pk).conteudo_publico
    assert publicacao.situacoes.count() == 5
