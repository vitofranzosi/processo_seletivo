"""A jornada de recorrer, do acompanhamento ao comprovante da peça.

Três telas encadeadas, e cada uma resolve uma pergunta diferente:

```text
acompanhamento  →  "posso recorrer disto?"   (e a ação só existe quando pode)
recorrer        →  "de quê, e por quê?"      (uma tela só, não um assistente)
recurso         →  "e agora, em que pé está?" (comprovante e situação juntos)
```

**A ação não é oferecida quando a interposição não é possível** (FR-013): antes da publicação não
há o que contestar, e um botão que sempre recusa ensina a pessoa a desconfiar da tela.
"""

import re

import pytest
from django.urls import reverse

from processo_seletivo.recursos.models import Recurso
from processo_seletivo.resultados.models import ResultadoEtapa
from tests.fixtures.divulgacao import (
    emitir,
    entrar_como_titular,
    montar_marco,
    pontuar,
    publicar_o_ato,
)

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.integration]


@pytest.fixture
def cenario(gestor, api_client, manager_headers, process_payload):
    """O ato emitido, e **ainda não publicado** — a publicação é escolha de cada teste.

    Quem publica é o teste porque a ausência de publicação é justamente o cenário que prova a
    FR-013: o Resultado existe no banco e a ação não é oferecida.
    """
    cenario = montar_marco(
        gestor, api_client, manager_headers, process_payload, seed=94, codigo="0794"
    )
    cenario["inscricoes"] = pontuar(
        cenario, gestor, ["90.0000", "70.0000"], primeiro=941, sufixo="94"
    )
    cenario["ato"] = emitir(cenario, gestor, chave="emitir-018-us2-portal")
    return cenario


def conteudo(resposta):
    corpo = resposta.content.decode()
    return re.search(r"<main[^>]*>(.*)</main>", corpo, re.DOTALL).group(1)


def acompanhar(client, inscricao):
    entrar_como_titular(client, inscricao)
    return conteudo(client.get(reverse("portal:acompanhamento", args=[inscricao.id])))


def test_sem_publicacao_a_acao_de_recorrer_nao_e_oferecida(client, cenario):
    """O Resultado existe e o ato está emitido — e não há o que contestar ainda (FR-013)."""
    corpo = acompanhar(client, cenario["inscricoes"][1])

    assert "Recorrer de um resultado" not in corpo


def test_publicado_o_marco_a_acao_aparece(client, cenario):
    publicar_o_ato(cenario, chave="publicar-018-us2-portal")

    corpo = acompanhar(client, cenario["inscricoes"][1])

    assert "Recorrer de um resultado" in corpo


def test_o_formulario_lista_o_que_se_pode_contestar(client, cenario):
    """A publicação do marco e o Resultado da Etapa, os dois alvos da mesma capacidade (D-001)."""
    publicar_o_ato(cenario, chave="publicar-018-us2-portal-b")
    inscricao = cenario["inscricoes"][1]
    entrar_como_titular(client, inscricao)

    corpo = conteudo(client.get(reverse("portal:recorrer", args=[inscricao.id])))

    assert corpo.count("<option") == 2
    assert 'value="resultado:' in corpo
    assert 'value="publicacao:' in corpo
    # O cabeçalho nomeia a seleção: quem tem inscrição em mais de um certame precisa saber de qual
    # resultado está recorrendo. Um subtítulo vazio é o defeito silencioso de ler o título do
    # lugar errado — o Edital não o guarda, quem o guarda é a versão consolidada.
    assert '<p class="sub"></p>' not in corpo


def test_interpor_leva_ao_comprovante_da_peca(client, cenario):
    """O protocolo é o que a pessoa leva, e ele aparece na primeira tela depois do envio."""
    publicar_o_ato(cenario, chave="publicar-018-us2-portal-c")
    inscricao = cenario["inscricoes"][1]
    alvo = ResultadoEtapa.vigentes.get(inscricao=inscricao, etapa_id=cenario["etapa"])
    entrar_como_titular(client, inscricao)

    resposta = client.post(
        reverse("portal:recorrer", args=[inscricao.id]),
        {"objeto": f"resultado:{alvo.id}", "fundamentacao": "A nota não reflete a prova entregue."},
        follow=True,
    )

    peca = Recurso.objects.get(inscricao=inscricao)
    corpo = conteudo(resposta)
    assert peca.protocolo in corpo
    assert "Aguardando análise de admissibilidade" in corpo
    assert "A nota não reflete a prova entregue." in corpo


def test_a_recusa_preserva_o_que_a_pessoa_escreveu(client, cenario):
    """Recusar apagando o texto seria pedir que ela escrevesse tudo de novo por um erro nosso."""
    publicar_o_ato(cenario, chave="publicar-018-us2-portal-d")
    inscricao = cenario["inscricoes"][1]
    alvo = ResultadoEtapa.vigentes.get(inscricao=inscricao, etapa_id=cenario["etapa"])
    entrar_como_titular(client, inscricao)
    client.post(
        reverse("portal:recorrer", args=[inscricao.id]),
        {"objeto": f"resultado:{alvo.id}", "fundamentacao": "A primeira razão."},
    )

    segunda = client.post(
        reverse("portal:recorrer", args=[inscricao.id]),
        {"objeto": f"resultado:{alvo.id}", "fundamentacao": "Uma segunda razão, diferente."},
    )

    corpo = conteudo(segunda)
    assert segunda.status_code == 200
    assert "Você já recorreu" in corpo
    assert "Uma segunda razão, diferente." in corpo
    assert Recurso.objects.filter(inscricao=inscricao).count() == 1


def test_o_duplo_clique_produz_uma_peca_so(client, cenario):
    """A chave de idempotência é determinística: o segundo envio idêntico devolve a mesma peça."""
    publicar_o_ato(cenario, chave="publicar-018-us2-portal-e")
    inscricao = cenario["inscricoes"][1]
    alvo = ResultadoEtapa.vigentes.get(inscricao=inscricao, etapa_id=cenario["etapa"])
    entrar_como_titular(client, inscricao)
    envio = {"objeto": f"resultado:{alvo.id}", "fundamentacao": "A nota não reflete a prova."}

    primeira = client.post(reverse("portal:recorrer", args=[inscricao.id]), envio)
    segunda = client.post(reverse("portal:recorrer", args=[inscricao.id]), envio)

    assert primeira.status_code == segunda.status_code == 302
    assert primeira["Location"] == segunda["Location"]
    assert Recurso.objects.filter(inscricao=inscricao).count() == 1


def test_sem_fundamentacao_a_peca_nao_nasce(client, cenario):
    publicar_o_ato(cenario, chave="publicar-018-us2-portal-f")
    inscricao = cenario["inscricoes"][1]
    alvo = ResultadoEtapa.vigentes.get(inscricao=inscricao, etapa_id=cenario["etapa"])
    entrar_como_titular(client, inscricao)

    resposta = client.post(
        reverse("portal:recorrer", args=[inscricao.id]),
        {"objeto": f"resultado:{alvo.id}", "fundamentacao": "   "},
    )

    assert resposta.status_code == 200
    assert "escreva a razão" in conteudo(resposta)
    assert not Recurso.objects.filter(inscricao=inscricao).exists()


def test_o_recurso_aparece_no_acompanhamento(client, cenario):
    publicar_o_ato(cenario, chave="publicar-018-us2-portal-g")
    inscricao = cenario["inscricoes"][1]
    alvo = ResultadoEtapa.vigentes.get(inscricao=inscricao, etapa_id=cenario["etapa"])
    entrar_como_titular(client, inscricao)
    client.post(
        reverse("portal:recorrer", args=[inscricao.id]),
        {"objeto": f"resultado:{alvo.id}", "fundamentacao": "A nota não reflete a prova."},
    )

    corpo = acompanhar(client, inscricao)

    peca = Recurso.objects.get(inscricao=inscricao)
    assert "Seus recursos" in corpo
    assert peca.protocolo in corpo


def test_a_tela_da_peca_nao_expoe_enum_nem_identificador(client, cenario):
    """A espécie e a situação chegam em português institucional (FR-048, SC-021).

    `AGUARDANDO_ADMISSIBILIDADE` na tela não é economia de tradução: é a fronteira entre o que o
    domínio nomeia para si e o que a instituição diz a alguém.
    """
    publicar_o_ato(cenario, chave="publicar-018-us2-portal-h")
    inscricao = cenario["inscricoes"][1]
    alvo = ResultadoEtapa.vigentes.get(inscricao=inscricao, etapa_id=cenario["etapa"])
    entrar_como_titular(client, inscricao)
    client.post(
        reverse("portal:recorrer", args=[inscricao.id]),
        {"objeto": f"resultado:{alvo.id}", "fundamentacao": "A nota não reflete a prova."},
    )
    peca = Recurso.objects.get(inscricao=inscricao)

    corpo = conteudo(client.get(reverse("portal:recurso", args=[peca.id])))

    assert '<p class="sub"></p>' not in corpo
    assert "aguardando_admissibilidade" not in corpo.lower()
    assert str(peca.id) not in corpo
    assert str(alvo.id) not in corpo
