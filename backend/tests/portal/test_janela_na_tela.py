"""O prazo recursal **exibido** ao candidato — não só gravado na peça (FR-024).

A caminhada da T125 encontrou o buraco: a janela era computada na aplicação, gravada no `Recurso` e
aplicada na recusa, mas nenhuma tela do candidato dizia **até quando**. Quem abria "Recorrer" via a
lista do que podia contestar sem uma data em lugar nenhum — e, encerrado o prazo, a ação
simplesmente desaparecia, sem que a pessoa soubesse que existiu.

```text
janela declarada e aberta   a tela diz o instante em que ela fecha, e a peça diz de quando a quando
janela não declarada        nenhuma data aparece — não há prazo a exibir nem a aplicar (FR-028)
```

A distinção importa: data ausente porque o prazo passou e data ausente porque prazo nenhum existe
são coisas diferentes, e a segunda é norma, não silêncio.
"""

import re

import pytest
from django.urls import reverse

from tests.fixtures.divulgacao import entrar_como_titular
from tests.integration.recursos.test_janela import (
    JANELA_DE_CINCO,
    interpor_como_titular,
    montar,
)

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.integration]

INSTANTE = re.compile(r"\d{2}/\d{2}/\d{4} às \d{2}h\d{2}")


def corpo(resposta):
    return re.search(r"<main[^>]*>(.*)</main>", resposta.content.decode(), re.DOTALL).group(1)


def test_o_formulario_diz_ate_quando_cabe_recorrer(
    client, gestor, api_client, manager_headers, process_payload
):
    """FR-024: o instante do encerramento aparece onde a escolha é feita."""
    cenario = montar(
        gestor,
        api_client,
        manager_headers,
        process_payload,
        seed=171,
        codigo="0871",
        janela=JANELA_DE_CINCO,
    )
    inscricao = cenario["inscricoes"][0]
    entrar_como_titular(client, inscricao)

    tela = corpo(client.get(reverse("portal:recorrer", args=[inscricao.id])))

    assert INSTANTE.search(tela), (
        "quem escolhe o que contestar precisa ler o instante em que o prazo fecha"
    )
    assert "23h59" in tela, "a janela fecha ao fim do dia, e é isso que a tela precisa dizer"


def test_a_peca_mostra_de_quando_a_quando_o_prazo_ia(
    client, gestor, api_client, manager_headers, process_payload
):
    """FR-024: a janela gravada é a que a pessoa lê depois — abertura, encerramento e situação."""
    cenario = montar(
        gestor,
        api_client,
        manager_headers,
        process_payload,
        seed=172,
        codigo="0872",
        janela=JANELA_DE_CINCO,
    )
    inscricao = cenario["inscricoes"][0]
    peca = interpor_como_titular(cenario, inscricao, chave="interpor-janela-na-tela")
    entrar_como_titular(client, inscricao)

    tela = corpo(client.get(reverse("portal:recurso", args=[peca.id])))

    assert len(INSTANTE.findall(tela)) >= 2, "os dois instantes da janela precisam aparecer"
    assert "Dentro do prazo" in tela


def test_sem_janela_declarada_nenhuma_data_de_prazo_aparece(
    client, gestor, api_client, manager_headers, process_payload
):
    """FR-028 e SC-015: ausência de declaração não vira prazo inventado na tela."""
    cenario = montar(gestor, api_client, manager_headers, process_payload, seed=173, codigo="0873")
    inscricao = cenario["inscricoes"][0]
    peca = interpor_como_titular(cenario, inscricao, chave="interpor-sem-janela-na-tela")
    entrar_como_titular(client, inscricao)

    formulario = corpo(client.get(reverse("portal:recorrer", args=[inscricao.id])))
    comprovante = corpo(client.get(reverse("portal:recurso", args=[peca.id])))

    assert "prazo" not in formulario.lower()
    assert "Prazo recursal" not in comprovante
