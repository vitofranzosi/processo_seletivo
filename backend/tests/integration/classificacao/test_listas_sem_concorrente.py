"""A lista em que ninguém concorre, perguntada uma vez por marco, é a da tela da ordenação (135,
FR-4670).

A tela diz "Ninguém concorreu por este recorte" quando o recorte é reservado e a proposta de
`calcular_ordem` não tem ninguém, com posição ou sem (`views.ordenacao`, `recorte_sem_ninguem`). A
pergunta do andamento não calcula a ordem: lê as Modalidades do mesmo universo, por marco. Aqui
as duas respostas são comparadas lista a lista — divergir é o defeito que esta função não pode ter.
"""

import pytest

from processo_seletivo.classificacao.application.calculo import (
    calcular_ordem,
    listas_sem_concorrente,
)
from processo_seletivo.publicacoes.application.selectors import effective_version
from tests.fixtures.corte import MARCO
from tests.fixtures.edital import PROFILE_ID
from tests.fixtures.recortes import MODALIDADE_PCD, MODALIDADE_PPI, montar_cenario_7_1_2

pytestmark = [pytest.mark.integration, pytest.mark.django_db(transaction=True)]


def _vazias(edital):
    return listas_sem_concorrente(
        edital=edital,
        conteudo=effective_version(edital_id=edital.id).content,
        perfil_id=PROFILE_ID,
        marco_id=MARCO,
    )


def _como_a_tela(edital, lista_id):
    """O critério de `recorte_sem_ninguem`, pela proposta que a tela calcula."""
    proposta = calcular_ordem(
        edital=edital, perfil_id=PROFILE_ID, marco_id=MARCO, lista_id=lista_id
    )
    return bool(lista_id) and not proposta["posicoes"] and not proposta["sem_posicao"]


def _confere_com_a_tela(edital, vazias):
    for lista_id in (None, MODALIDADE_PCD, MODALIDADE_PPI):
        assert (lista_id in vazias) == _como_a_tela(edital, lista_id), lista_id


def test_sem_autodeclarado_as_duas_reservadas_sao_vazias_e_a_ampla_nunca(
    gestor, api_client, manager_headers, process_payload
):
    edital, _, _ = montar_cenario_7_1_2(
        gestor,
        api_client,
        manager_headers,
        process_payload,
        prefixo="listas-135-vazias",
        autodeclarar=False,
        emitir_a_ordem=False,
    )
    vazias = _vazias(edital)
    assert vazias == {MODALIDADE_PCD, MODALIDADE_PPI}
    _confere_com_a_tela(edital, vazias)


def test_com_um_autodeclarado_a_lista_nao_e_vazia(
    gestor, api_client, manager_headers, process_payload
):
    edital, _, _ = montar_cenario_7_1_2(
        gestor,
        api_client,
        manager_headers,
        process_payload,
        prefixo="listas-135-uma",
        autodeclarar=False,
        modalidades={0: MODALIDADE_PPI},
        emitir_a_ordem=False,
    )
    vazias = _vazias(edital)
    assert vazias == {MODALIDADE_PCD}
    _confere_com_a_tela(edital, vazias)


def test_a_pergunta_custa_ate_duas_consultas_e_nao_cresce_com_as_inscricoes(
    gestor, api_client, manager_headers, process_payload
):
    """FR-4686: por marco, e nunca por inscrição. Até duas: o gate da progressão, quando a Etapa
    anterior exige habilitação, e as Modalidades. O conteúdo vigente não é relido — ele chega de
    quem chama (a revisão do PR #441)."""
    from django.db import connection
    from django.test.utils import CaptureQueriesContext

    from tests.fixtures.comissao import inscrever

    edital, _, _ = montar_cenario_7_1_2(
        gestor,
        api_client,
        manager_headers,
        process_payload,
        prefixo="listas-135-custo",
        emitir_a_ordem=False,
    )
    conteudo = effective_version(edital_id=edital.id).content

    def contar():
        with CaptureQueriesContext(connection) as capturadas:
            listas_sem_concorrente(
                edital=edital, conteudo=conteudo, perfil_id=PROFILE_ID, marco_id=MARCO
            )
        return len(capturadas)

    com_poucas = contar()
    assert com_poucas <= 2
    inscrever(edital, 12, primeiro=700)
    assert contar() == com_poucas
