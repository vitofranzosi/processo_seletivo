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

from processo_seletivo.recursos.models import Recurso
from processo_seletivo.resultados.models import ResultadoEtapa
from tests.fixtures.divulgacao import entrar_como_titular
from tests.integration.recursos.test_janela import (
    JANELA_DE_CINCO,
    interpor_como_titular,
    montar,
)
from tests.integration.recursos.test_janela import (
    _envelhecer as envelhecer,
)

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.integration]

INSTANTE = re.compile(r"\d{2}/\d{2}/\d{4} às \d{2}h\d{2}")
INSTANTE_CURTO = re.compile(r"\d{2}/\d{2}/\d{4}")


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


def test_o_envio_depois_do_prazo_recebe_a_recusa_que_nomeia_a_norma(
    client, gestor, api_client, manager_headers, process_payload
):
    """FR-026 e SC-014: a recusa **chega** a quem envia, e não é engolida por um redirecionamento.

    A ação some da tela quando o prazo fecha (FR-013), e isso é certo — mas quem deixou o formulário
    aberto enquanto a janela corria envia depois dela, e esse envio precisa receber a norma, a
    abertura e o encerramento. A tela redirecionava para o acompanhamento antes de o pedido chegar
    ao domínio: a pessoa via a página de sempre, sem recusa nenhuma, e ficava sem saber que houve
    prazo e que ele passou.

    Recusar em silêncio é pior do que recusar: a interposição não aconteceu, e a única leitura
    disponível era a de que ela tinha acontecido.

    **O código continua 200**, como em toda recusa de formulário do portal — a página devolvida é a
    recusa, com o texto preservado. O defeito era o redirecionamento, e não o status: trocar só
    aqui deixaria o portal inconsistente consigo mesmo.
    """
    cenario = montar(
        gestor,
        api_client,
        manager_headers,
        process_payload,
        seed=174,
        codigo="0874",
        janela=JANELA_DE_CINCO,
    )
    inscricao = cenario["inscricoes"][0]
    alvo = ResultadoEtapa.vigentes.get(inscricao=inscricao, etapa_id=cenario["etapa"])
    entrar_como_titular(client, inscricao)
    # O formulário foi aberto enquanto o prazo corria; a publicação envelhece antes do envio.
    envelhecer(cenario["publicacao"], 10)

    resposta = client.post(
        reverse("portal:recorrer", args=[inscricao.id]),
        {"objeto": f"resultado:{alvo.id}", "fundamentacao": "A questão 12 foi anulada."},
    )

    assert resposta.status_code == 200, "recusa é resposta, e não redirecionamento"
    tela = corpo(resposta)
    assert "O prazo para recorrer deste resultado encerrou-se em" in tela
    assert "5 dias corridos" in tela, "a norma que fixou o prazo precisa ser citada"
    assert len(INSTANTE_CURTO.findall(tela)) >= 2, "a abertura e o encerramento, os dois"
    assert not Recurso.objects.filter(inscricao=inscricao).exists()


def test_depois_do_prazo_a_tela_nao_oferece_a_acao_de_novo(
    client, gestor, api_client, manager_headers, process_payload
):
    """A recusa não pode vir acompanhada de um formulário que produziria a mesma recusa."""
    cenario = montar(
        gestor,
        api_client,
        manager_headers,
        process_payload,
        seed=175,
        codigo="0875",
        janela=JANELA_DE_CINCO,
    )
    inscricao = cenario["inscricoes"][0]
    alvo = ResultadoEtapa.vigentes.get(inscricao=inscricao, etapa_id=cenario["etapa"])
    entrar_como_titular(client, inscricao)
    envelhecer(cenario["publicacao"], 10)

    tela = corpo(
        client.post(
            reverse("portal:recorrer", args=[inscricao.id]),
            {"objeto": f"resultado:{alvo.id}", "fundamentacao": "A questão 12 foi anulada."},
        )
    )

    assert "Interpor recurso" not in tela
    assert "Voltar ao acompanhamento" in tela

    # E o GET continua devolvendo quem chega pela navegação: sem objeto atacável, não há formulário.
    assert client.get(reverse("portal:recorrer", args=[inscricao.id])).status_code == 302
