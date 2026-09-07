"""A administração reconstrói o recurso inteiro **numa jornada só** — sem banco e sem shell.

A FR-092 é uma lista, e a pergunta que ela responde é a da auditoria e a de quem julga: *como este
recurso chegou aqui, e o que ele alcançou?* Hoje, responder isso exigiria abrir cinco telas e
cruzar identificadores à mão — e é exatamente o que a SC-020 recusa.

```text
quem interpôs · qual Inscrição · qual objeto · qual era o ato vigente naquele instante
sob qual versão · quando · se dentro da janela
quem admitiu e por quê · quem decidiu e por quê
qual efeito · qual ato superado · qual sucessor nasceu
```

**É a FR-092, e não a FR-093.** Aqui aparecem identificadores técnicos e autoria de ato, porque
quem lê é a administração. O que chega ao candidato é outra coisa, e está em `tests/portal/`.
"""

import re
from decimal import Decimal

import pytest
from django.urls import reverse

from processo_seletivo.publicacoes.application.selectors import selecao_publica
from processo_seletivo.recursos.application.admitir import admitir
from processo_seletivo.resultados.models import ResultadoEtapa
from tests.conftest import ator_institucional
from tests.fixtures.divulgacao import emitir, montar_marco, pontuar, publicar_o_ato
from tests.fixtures.recursos import decidir, superar
from tests.interface.conftest import identificar

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.integration]

JULGADORA = "helena.julgadora"


@pytest.fixture
def julgado(gestor, api_client, manager_headers, process_payload):
    """O ciclo inteiro percorrido: interpor, admitir, decidir, superar.

    A peça é interposta pelo **comando** do candidato, e não pela fixture curta: a proveniência
    afirma o que a interposição gravou, e montá-la por atalho provaria a tela contra um dado que
    o produto não produz.
    """
    from processo_seletivo.portal.identidade import IdentidadeDoCandidato
    from processo_seletivo.recursos.application.interpor import interpor

    cenario = montar_marco(
        gestor, api_client, manager_headers, process_payload, seed=100, codigo="0800"
    )
    cenario["inscricoes"] = pontuar(cenario, gestor, ["55.0000"], primeiro=1001, sufixo="100")
    cenario["ato"] = emitir(cenario, gestor, chave="emitir-018-us3c")
    publicar_o_ato(cenario, chave="publicar-018-us3c")

    inscricao = cenario["inscricoes"][0]
    superado = ResultadoEtapa.vigentes.get(inscricao=inscricao, etapa_id=cenario["etapa"])
    peca = interpor(
        identidade=IdentidadeDoCandidato(
            inscricao.identity_subject, inscricao.nome, inscricao.cpf_normalizado, "c@ex.br"
        ),
        inscricao=inscricao,
        resultado=superado,
        fundamentacao="A prova didática entregue não foi considerada no parecer.",
        assinatura_do_objeto=str(superado.pk),
        idempotency_key="proveniencia-us3",
    )
    admitir(
        actor=ator_institucional(JULGADORA, "recurso:julgar"),
        recurso_id=peca.id,
        admitido=True,
        motivo="Tempestivo e regularmente instruído.",
        assinatura_do_estado="",
        idempotency_key="admitir-proveniencia-us3",
    )
    peca.refresh_from_db()
    decisao = decidir(
        peca,
        protegido=superado,
        consequencia=ResultadoEtapa.Consequencia.HABILITADA,
        forma="PONTUADA",
        pontuacao=Decimal("82.0000"),
        versao=selecao_publica(edital_id=inscricao.edital_id),
    )
    sucessor = superar(superado, decisao, pontuacao=Decimal("82.0000"))
    return {
        "cenario": cenario,
        "peca": peca,
        "superado": superado,
        "sucessor": sucessor,
        "decisao": decisao,
        "inscricao": inscricao,
    }


def abrir(client, julgado):
    identificar(client, JULGADORA, ["julgador"])
    resposta = client.get(reverse("interface:recurso", args=[julgado["peca"].id]))
    assert resposta.status_code == 200
    return re.search(r"<main[^>]*>(.*)</main>", resposta.content.decode(), re.DOTALL).group(1)


def test_a_tela_do_recurso_responde_a_lista_inteira_da_fr_092(client, seletor_ligado, julgado):
    """Uma jornada, e não cinco. Cada asserção é um item da lista, e nenhuma é decorativa."""
    corpo = abrir(client, julgado)
    peca = julgado["peca"]

    # quem interpôs, qual Inscrição, quando
    assert peca.interposto_por in corpo
    assert julgado["inscricao"].nome in corpo
    assert julgado["inscricao"].protocolo in corpo
    # qual objeto, e sob qual versão
    assert str(julgado["superado"].id) in corpo
    assert str(peca.versao_id) in corpo
    # se dentro da janela — e aqui a resposta honesta é que não há prazo computável
    assert "Sem prazo computável" in corpo
    # quem admitiu e por quê
    assert JULGADORA in corpo
    assert "Tempestivo e regularmente instruído." in corpo
    # quem decidiu e por quê
    assert "Recurso deferido — o resultado foi corrigido" in corpo
    assert "O parecer não enfrentou o documento juntado na inscrição." in corpo
    # qual efeito: o ato superado e o sucessor que nasceu
    assert "55" in corpo
    assert "82" in corpo


def test_a_fundamentacao_aparece_como_escrita(client, seletor_ligado, julgado):
    """Resumir a razão de quem recorre é decidir por ele o que importa."""
    corpo = abrir(client, julgado)

    assert "A prova didática entregue não foi considerada no parecer." in corpo


def test_a_tela_nomeia_o_ato_vigente_no_ramo_da_publicacao(
    client, seletor_ligado, gestor, api_client, manager_headers, process_payload
):
    """No ramo do Resultado não há ato de ordenação a nomear, e afirmar um seria inventá-lo.

    Este teste prende a metade que existe: contra a publicação, o ato que ela divulgou **é** parte
    da proveniência, e é por ele que se reconstrói o que estava vigente naquele instante.
    """
    from tests.fixtures.recursos import interpor as interpor_curto

    cenario = montar_marco(
        gestor, api_client, manager_headers, process_payload, seed=101, codigo="0801"
    )
    cenario["inscricoes"] = pontuar(cenario, gestor, ["70.0000"], primeiro=1011, sufixo="101")
    cenario["ato"] = emitir(cenario, gestor, chave="emitir-018-us3d")
    publicacao = publicar_o_ato(cenario, chave="publicar-018-us3d")
    inscricao = cenario["inscricoes"][0]
    peca = interpor_curto(
        inscricao=inscricao,
        versao=selecao_publica(edital_id=inscricao.edital_id),
        publicacao=publicacao,
        protocolo="REC-2026-US30020",
    )

    identificar(client, JULGADORA, ["julgador"])
    corpo = client.get(reverse("interface:recurso", args=[peca.id])).content.decode()

    assert "Ato vigente naquele instante" in corpo
    assert str(publicacao.ato_id) in corpo


def test_a_tela_do_recurso_nao_faz_uma_consulta_por_ato(
    client, seletor_ligado, julgado, django_assert_num_queries
):
    """A proveniência é uma tela, e não um laço de leituras.

    O `select_related` da view e o `prefetch_related` dos dois atos existem para isto: uma tela que
    fizesse uma leitura por item da lista pareceria rápida com um recurso e sumiria com cem.
    """
    identificar(client, JULGADORA, ["julgador"])
    caminho = reverse("interface:recurso", args=[julgado["peca"].id])
    client.get(caminho)

    # Sete: sessão, a peça com os dois atos prefetchados, o impedimento, o Edital e o Resultado
    # vigente do par que o formulário de julgamento assina. O número é **constante** — não cresce
    # com a proveniência, e é isso que este orçamento protege.
    with django_assert_num_queries(7):
        client.get(caminho)
