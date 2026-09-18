"""A forma da ordem no conteúdo publicado, e a fronteira do campo que o rascunho esconde (030).

Dois compromissos que se contradizem se forem lidos por metade, e que por isso vivem no mesmo
arquivo:

**SC-142** — um Edital composto antes desta feature publica, depois dela, **exatamente** o mesmo
conteúdo normativo. A chave `orderProduction` não nasce em snapshot já publicado, e não nasce
tampouco em marco que não declarou a forma: a ausência **é** a afirmação, e dela os leitores
derivam o comportamento de sempre — sorteia quem declara `drawMethod`.

**FR-418 e o contrato do rascunho** — o campo que a revelação progressiva torna impertinente
continua no rascunho, para que trocar a resposta não apague em silêncio o que já tinha sido
declarado. E **não alcança o conteúdo publicado**: um marco que era de sorteio e virou de pontuação
guarda o método e não o publica. Fechar só o primeiro caminho deixaria o defeito vivo — é a lição
que o assistente já aprendeu uma vez, quando a perda tinha duas portas e só uma foi fechada.
"""

import copy

import pytest

from processo_seletivo.editais.models.perfis import MarcoClassificatorio
from processo_seletivo.processos.models import Edital
from processo_seletivo.publicacoes.application.publish_edital import edital_snapshot
from tests.fixtures.publicacao import publish_original
from tests.fixtures.snapshot import PERFIL, rascunho_completo

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.integration]


#: As chaves que o marco publicava **antes** desta feature. Literal, e não derivado do emissor: um
#: conjunto lido do próprio código acompanharia qualquer chave nova em silêncio, que é exatamente
#: o que SC-142 existe para impedir.
CHAVES_DO_MARCO_ANTES_DA_FEATURE = {
    "id",
    "code",
    "name",
    "stages",
    "operation",
    "normalization",
    "rounding",
    "appealWindow",
    "drawMethod",
    "cutRule",
    "tiebreakers",
}


def rascunho(**alteracoes_do_marco):
    """O rascunho máximo, com o marco alterado — e `None` removendo a chave."""
    base = copy.deepcopy(rascunho_completo())
    perfil = next(item for item in base["profiles"] if item["id"] == PERFIL["A"])
    marco = perfil["classificationMilestones"][0]
    for chave, valor in alteracoes_do_marco.items():
        if valor is None:
            marco.pop(chave, None)
        else:
            marco[chave] = valor
    return base


def marco_publicado(edital):
    conteudo = edital_snapshot(Edital.objects.get(pk=edital.pk))
    perfil = next(item for item in conteudo["profiles"] if item["id"] == PERFIL["A"])
    return perfil["classificationMilestones"][0]


# --- SC-142: o que não pode ter mudado ------------------------------------------------------
#
# **O acervo é uma linha com `""`, e não um rascunho sem a chave.** A distinção passou a importar
# quando a publicação passou a exigir a declaração (FR-413, princípio IV): publicar conteúdo novo
# sem `orderProduction` é recusado, e simular o acervo por esse caminho testaria um estado que o
# sistema não produz mais.
#
# O estado do acervo é o que a migration deixou: coluna acrescentada, vazia, sem percorrer linha
# publicada. É ele que estes testes montam — publicando como se publica hoje e devolvendo o campo
# ao vazio depois, que é exatamente o que um Edital de antes da `030` tem no banco.


def _como_o_acervo(edital):
    """Devolve o marco ao estado que a migration deixou: forma vazia, método onde sempre esteve."""
    MarcoClassificatorio.objects.filter(perfil__edital=edital).update(forma_da_ordem="")
    return edital


def test_marco_que_nao_declara_a_forma_publica_o_conteudo_de_sempre(
    api_client, manager_headers, process_payload
):
    """O Edital anterior a esta feature, relido: nenhuma chave nova, nenhuma chave a menos."""
    edital = publish_original(
        api_client, manager_headers, process_payload, draft=rascunho(), anexos=1
    )

    marco = marco_publicado(_como_o_acervo(edital))

    assert set(marco) == CHAVES_DO_MARCO_ANTES_DA_FEATURE
    assert "orderProduction" not in marco


def test_a_forma_nao_declarada_nao_vira_padrao_no_modelo(
    api_client, manager_headers, process_payload
):
    """`""` no campo, e não `POR_SORTEIO` inferido do método que este marco declara."""
    edital = publish_original(
        api_client, manager_headers, process_payload, draft=rascunho(), anexos=1
    )

    marco = MarcoClassificatorio.objects.get(perfil_id=PERFIL["A"])
    _como_o_acervo(edital)
    marco.refresh_from_db()

    assert marco.forma_da_ordem == ""
    assert marco.metodo_de_sorteio, "o método continua declarado: a inferência de hoje o lê daqui"


def test_o_metodo_do_marco_sem_forma_declarada_continua_publicado(
    api_client, manager_headers, process_payload
):
    """A ausência de declaração **não** aciona a fronteira de FR-418.

    Ela vale para quem declarou pontuação, e não para quem não declarou nada — senão a feature
    apagaria o método de todo Edital anterior a ela, que é o oposto de SC-142.
    """
    edital = publish_original(
        api_client, manager_headers, process_payload, draft=rascunho(), anexos=1
    )

    assert marco_publicado(_como_o_acervo(edital))["drawMethod"]


def test_publicar_marco_sem_declarar_a_forma_e_recusado(
    api_client, manager_headers, process_payload
):
    """FR-413 no servidor, e não só no `required` da tela (princípio IV).

    A interface obriga — o `select` é `required` —, e obrigar na tela não basta: a API de rascunho
    é o outro caminho até o conteúdo publicado, e um envio que omitisse a chave gravava `""` sem
    que nada acusasse. Publicado assim, o marco voltaria a ser lido por inferência, que é
    exatamente o que a FR-413 veio eliminar.

    **Na publicação, e não na gravação**: o rascunho pode estar pela metade, como o corte e a
    janela recursal já podem.
    """
    from processo_seletivo.editais.domain.validation import (
        ATO_DE_RETIFICACAO,
        blocking_findings,
        validate_for_publication,
    )
    from processo_seletivo.publicacoes.application.publish_edital import edital_snapshot

    edital = publish_original(
        api_client, manager_headers, process_payload, draft=rascunho(), anexos=1
    )
    conteudo = edital_snapshot(Edital.objects.get(pk=_como_o_acervo(edital).pk))

    impeditivos = {achado.code for achado in blocking_findings(validate_for_publication(conteudo))}
    na_retificacao = {
        achado.code
        for achado in blocking_findings(validate_for_publication(conteudo, ato=ATO_DE_RETIFICACAO))
    }

    assert "order_production_nao_declarada" in impeditivos
    assert "order_production_nao_declarada" not in na_retificacao, (
        "o acervo se retifica como está: cobrar dele uma declaração que a capacidade não oferecia "
        "seria pedir que a autoridade decidisse hoje o que o Edital de então não disse"
    )


# --- A chave nova, quando declarada ---------------------------------------------------------


def test_a_forma_declarada_viaja_ate_o_conteudo_publicado(
    api_client, manager_headers, process_payload
):
    edital = publish_original(
        api_client, manager_headers, process_payload, draft=rascunho(), anexos=1
    )

    assert marco_publicado(edital)["orderProduction"] == "POR_SORTEIO"


# --- A fronteira do campo oculto (FR-418) ---------------------------------------------------


def test_o_metodo_escondido_pela_troca_de_forma_nao_alcanca_o_publicado(
    api_client, manager_headers, process_payload
):
    """O marco que era de sorteio e virou de pontuação: guarda o método, e não o publica."""
    edital = publish_original(
        api_client,
        manager_headers,
        process_payload,
        draft=rascunho(orderProduction="POR_PONTUACAO"),
        anexos=1,
    )

    guardado = MarcoClassificatorio.objects.get(perfil_id=PERFIL["A"])

    assert guardado.metodo_de_sorteio, "o rascunho guarda o que a tela escondeu (FR-418)"
    assert marco_publicado(edital)["drawMethod"] is None, (
        "o Edital não pode afirmar um sorteio que ele não faz"
    )


# --- As duas contradições que só a Retificação alcança ---------------------------------------
#
# **A projeção de `edital_snapshot` não é a fronteira, e tratá-la como tal foi o defeito.** Ela
# descarta o método impertinente ao compor o snapshot, e com isso o ato de **publicação** nunca
# chega à conferência com a contradição. A Retificação não passa por ela: opera sobre o conteúdo
# vigente, campo a campo, e uma Alteração que mude só um lado deixa o outro onde estava.
#
# Os dois casos abaixo são conferidos sobre o conteúdo, e não pelo percurso da Retificação, porque
# é o conteúdo que `validate_for_publication` governa — e porque assim eles falham no lugar em que
# a regra mora, e não três camadas acima.

from processo_seletivo.editais.domain.validation import (  # noqa: E402
    blocking_findings,
    validate_for_publication,
)
from tests.fixtures.snapshot import conteudo_normativo  # noqa: E402
from tests.unit.editais.test_marco_classificatorio import (  # noqa: E402
    conteudo_com_marco as _conteudo_publicavel_com_marco,
)


def _conteudo_com_marco(**alteracoes):
    """Conteúdo publicável cujo marco recebe as alterações pedidas.

    O construtor vem do irmão `test_marco_classificatorio`, que já monta Edital com Etapa
    classificatória e marco que a enumera — `conteudo_normativo` sozinho não declara marco nenhum,
    e um conteúdo sem marco não exercita regra de marco.
    """
    conteudo = _conteudo_publicavel_com_marco()
    perfil = next(item for item in conteudo["profiles"] if item.get("classificationMilestones"))
    perfil["classificationMilestones"][0].update(alteracoes)
    return conteudo


def _codigos(conteudo):
    return {achado.code for achado in blocking_findings(validate_for_publication(conteudo))}


@pytest.mark.django_db(transaction=False)
def test_o_metodo_comum_pela_metade_impede_a_publicacao():
    """FR-429 — o método comum vale inteiro, e a Retificação é o caminho que o alcança.

    Uma Alteração que remova `/drawMethod/substitutionRule` da raiz devolve à mesa, no dia da
    indisponibilidade, a escolha da ocorrência de **todos** os marcos que referenciam o comum — de
    uma vez, por um ato só. Era o buraco simétrico ao que a `026` fechou no método do marco.
    """
    conteudo = conteudo_normativo()
    conteudo["drawMethod"] = {
        "algorithm": "IFES-SORTEIO-SHA256-v1",
        "source": "Fonte de demonstração",
        "occurrence": "5901",
        "occurrenceAt": "2020-01-01T20:00:00-03:00",
        "derivation": "A extração de sábado imediatamente anterior.",
        "normalization": {"rule": "DIGITOS_EM_SEQUENCIA", "text": "Os cinco números."},
    }

    assert "common_draw_method_invalid" in _codigos(conteudo)


@pytest.mark.django_db(transaction=False)
def test_o_metodo_comum_inteiro_publica():
    """A contraprova: declarado por completo, ele atravessa sem achado nenhum."""
    conteudo = conteudo_normativo()
    conteudo["drawMethod"] = {
        "algorithm": "IFES-SORTEIO-SHA256-v1",
        "source": "Fonte de demonstração",
        "occurrence": "5901",
        "occurrenceAt": "2020-01-01T20:00:00-03:00",
        "derivation": "A extração de sábado imediatamente anterior.",
        "normalization": {"rule": "DIGITOS_EM_SEQUENCIA", "text": "Os cinco números."},
        "substitutionRule": {
            "rule": "OCORRENCIA_SEGUINTE_DA_MESMA_FONTE",
            "text": "Vale a extração seguinte da mesma fonte.",
        },
    }

    assert "common_draw_method_invalid" not in _codigos(conteudo)


@pytest.mark.django_db(transaction=False)
def test_pontuacao_com_metodo_declarado_impede_a_publicacao():
    """A regra que `data-model.md` já escrevia, e que faltava no código.

    Trocar **só** `orderProduction` de `POR_SORTEIO` para `POR_PONTUACAO` por Retificação deixaria
    o `drawMethod` do marco onde estava: norma publicada dizendo, no mesmo objeto, que a ordem
    nasce da pontuação e que o sorteio tem fonte, ocorrência e regra de substituição.
    """
    metodo = {
        "algorithm": "IFES-SORTEIO-SHA256-v1",
        "source": "Fonte de demonstração",
        "occurrence": "5901",
        "occurrenceAt": "2020-01-01T20:00:00-03:00",
        "derivation": "A extração de sábado imediatamente anterior.",
        "normalization": {"rule": "DIGITOS_EM_SEQUENCIA", "text": "Os cinco números."},
        "substitutionRule": {
            "rule": "OCORRENCIA_SEGUINTE_DA_MESMA_FONTE",
            "text": "Vale a seguinte.",
        },
        "qualifyingStageId": None,
    }

    contraditorio = _conteudo_com_marco(orderProduction="POR_PONTUACAO", drawMethod=metodo)
    coerente = _conteudo_com_marco(orderProduction="POR_PONTUACAO", drawMethod=None)
    sorteio = _conteudo_com_marco(orderProduction="POR_SORTEIO", drawMethod=metodo)

    assert "order_production_contradiz_o_metodo" in _codigos(contraditorio)
    assert "order_production_contradiz_o_metodo" not in _codigos(coerente)
    assert "order_production_contradiz_o_metodo" not in _codigos(sorteio), (
        "quem declara sorteio e método não se contradiz — é o caso normal"
    )


@pytest.mark.django_db(transaction=False)
def test_o_marco_do_acervo_com_metodo_e_sem_forma_declarada_continua_publicando():
    """A ausência de declaração não é contradição: é o estado de todo Edital anterior à `030`."""
    conteudo = _conteudo_com_marco()
    marco = next(item for item in conteudo["profiles"] if item.get("classificationMilestones"))[
        "classificationMilestones"
    ][0]
    marco.pop("orderProduction", None)

    assert "order_production_contradiz_o_metodo" not in _codigos(conteudo)
