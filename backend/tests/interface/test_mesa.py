"""A Mesa do avaliador: todas e somente as inscrições dela (US2).

A página é a mesma que a 011 deixou com um aviso; o que a `012` faz é substituir o aviso pela
lista. Quem chegou pela gestão continua sem Mesa — organizar o trabalho não é executá-lo.
"""

import pytest
from django.urls import reverse

from processo_seletivo.avaliacoes.application.selectors import POR_PAGINA
from tests.fixtures.comissao import alocar_em, inscrever
from tests.interface.conftest import identificar

pytestmark = [pytest.mark.django_db]


@pytest.fixture
def joao(gestor, processo_a, edital_a, comissao_de_a, etapa_a1):
    alocar_em(gestor, processo_a, comissao_de_a["joao"], edital_a, etapa_a1)
    return comissao_de_a["joao"]


@pytest.fixture
def mesa(edital_a, etapa_a1):
    return reverse("interface:minha-etapa", args=[edital_a.id, etapa_a1])


def distribuir_para(gestor, edital, etapa_id, membro, inscricoes, chave="mesa"):
    from processo_seletivo.avaliacoes.application.distribuicao import distribuir

    return distribuir(
        actor=gestor,
        processo_id=edital.processo_id,
        edital_id=edital.id,
        etapa_id=etapa_id,
        membro_ids=[membro.id],
        inscricao_ids=[i.id for i in inscricoes],
        idempotency_key=chave,
        correlation_id="teste",
    )


def test_a_mesa_lista_o_que_e_dele_e_conta(
    client, seletor_ligado, gestor, edital_a, etapa_a1, joao, mesa
):
    inscricoes = inscrever(edital_a, 3)
    distribuir_para(gestor, edital_a, etapa_a1, joao, inscricoes)
    identificar(client, "joao", [])

    corpo = client.get(mesa).content.decode()

    assert "no total" in corpo and ">3<" in corpo
    # As parcelas fecham com o total: três não iniciadas, nenhum rascunho, nenhuma concluída.
    assert "não iniciadas" in corpo
    for inscricao in inscricoes:
        assert inscricao.protocolo in corpo


def test_a_mesa_nao_mostra_inscricao_de_outro_avaliador(
    client, seletor_ligado, gestor, processo_a, edital_a, etapa_a1, joao, comissao_de_a, mesa
):
    """ "Todas **e somente**" é a metade que só se prova pela ausência (FR-020)."""
    from processo_seletivo.comissoes.domain.funcoes import Funcao
    from tests.fixtures.comissao import constituir

    ana = constituir(gestor, processo_a, [("ana", Funcao.MEMBRO)], prefixo="mesa")["ana"]
    alocar_em(gestor, processo_a, ana, edital_a, etapa_a1)
    minhas, dela = inscrever(edital_a, 1), inscrever(edital_a, 1, primeiro=80)
    distribuir_para(gestor, edital_a, etapa_a1, joao, minhas, chave="a")
    distribuir_para(gestor, edital_a, etapa_a1, ana, dela, chave="b")
    identificar(client, "joao", [])

    corpo = client.get(mesa).content.decode()

    assert minhas[0].protocolo in corpo
    assert dela[0].protocolo not in corpo


def avaliar(atribuicao, etapa_id, inscricao, edital, *, concluida):
    """Uma Avaliação em rascunho, ou realmente concluída.

    A conclusão exige pontuação, versão, instante e autor — é o que o check de completude do banco
    cobra, e é o que separa "rascunho gravado" de "ato encerrado".
    """
    from decimal import Decimal

    from django.utils import timezone

    from processo_seletivo.avaliacoes.domain.formas import Forma
    from processo_seletivo.avaliacoes.models import Avaliacao
    from processo_seletivo.publicacoes.models_retificacao import VersaoConsolidada

    encerrada = (
        {
            "estado": Avaliacao.Estado.CONCLUIDA,
            "forma": Forma.PONTUADA,
            "pontuacao": Decimal("80.0000"),
            "versao": VersaoConsolidada.objects.filter(edital=edital).latest("materialized_at"),
            "concluida_em": timezone.now(),
            "concluida_por": "joao",
        }
        if concluida
        else {}
    )
    return Avaliacao.objects.create(
        atribuicao=atribuicao,
        identity_subject="joao",
        etapa_id=etapa_id,
        inscricao_id=inscricao.id,
        **encerrada,
    )


def test_o_filtro_separa_pendentes_de_concluidas(
    client, seletor_ligado, gestor, edital_a, etapa_a1, joao, mesa
):
    """Os dois sentidos, e as contagens.

    Com apenas um rascunho, uma implementação em que "Concluídas" sempre voltasse vazio passaria:
    é preciso uma conclusão de verdade, e afirmar que ela **aparece** num filtro e **some** do
    outro (FR-021).
    """
    from processo_seletivo.avaliacoes.models import Atribuicao

    concluida, rascunho, intocada = inscrever(edital_a, 3)
    distribuir_para(gestor, edital_a, etapa_a1, joao, [concluida, rascunho, intocada])
    avaliar(
        Atribuicao.objects.get(inscricao=concluida), etapa_a1, concluida, edital_a, concluida=True
    )
    avaliar(
        Atribuicao.objects.get(inscricao=rascunho), etapa_a1, rascunho, edital_a, concluida=False
    )
    identificar(client, "joao", [])

    pendentes = client.get(f"{mesa}?filtro=pendentes").content.decode()
    concluidas = client.get(f"{mesa}?filtro=concluidas").content.decode()
    todas = client.get(mesa).content.decode()

    # A concluída aparece num filtro e some do outro.
    assert concluida.protocolo in concluidas
    assert concluida.protocolo not in pendentes
    # **Rascunho gravado continua pendente**: pendente é a ausência de conclusão, e não a de
    # avaliação — quem salvou sem concluir não terminou o trabalho.
    assert rascunho.protocolo in pendentes
    assert rascunho.protocolo not in concluidas
    assert intocada.protocolo in pendentes
    assert "no total" in todas and ">3<" in todas
    # Duas pendentes, e a Mesa agora diz **onde** elas estão: uma em rascunho, uma não iniciada.
    assert "em rascunho" in todas
    assert "não iniciada" in todas
    assert "concluída" in todas


def test_a_mesa_pagina(client, seletor_ligado, gestor, edital_a, etapa_a1, joao, mesa):
    """Quarenta e oito é comum; quinhentas não pode quebrar a tela (FR-022)."""
    inscricoes = inscrever(edital_a, POR_PAGINA + 3)
    distribuir_para(gestor, edital_a, etapa_a1, joao, inscricoes)
    identificar(client, "joao", [])

    corpo = client.get(mesa).content.decode()

    assert "Página 1 de 2" in corpo
    assert "Próxima" in corpo


def test_alocado_sem_atribuicao_encontra_a_mesa_vazia(client, seletor_ligado, joao, mesa):
    """FR-023: alocação abre a porta da Etapa; a Atribuição abre a inscrição.

    O estado vazio explica que não há trabalho distribuído — e **não** fala em permissão, que
    diria a coisa errada.
    """
    identificar(client, "joao", [])

    resposta = client.get(mesa)
    corpo = resposta.content.decode()

    assert resposta.status_code == 200
    assert "Nenhuma inscrição foi distribuída a você" in corpo
    assert "permiss" not in corpo.lower()


def test_quem_chega_pela_gestao_nao_tem_mesa(
    client, seletor_ligado, gestor, edital_a, etapa_a1, joao, mesa
):
    """Organizar o trabalho não é executá-lo, e a página diz por qual porta o ator chegou."""
    inscricoes = inscrever(edital_a, 2)
    distribuir_para(gestor, edital_a, etapa_a1, joao, inscricoes)
    identificar(client, "carlos", ["gestor"])

    corpo = client.get(mesa).content.decode()

    assert "chegou aqui pela gestão" in corpo
    assert "Minha Mesa" not in corpo
    assert inscricoes[0].protocolo not in corpo


def test_a_mesa_nao_e_armazenavel_pelo_navegador(
    client, seletor_ligado, gestor, edital_a, etapa_a1, joao, mesa
):
    distribuir_para(gestor, edital_a, etapa_a1, joao, inscrever(edital_a, 1))
    identificar(client, "joao", [])

    resposta = client.get(mesa)

    assert "no-store" in resposta["Cache-Control"]


# --------------------------- a forma decisória pelo canal real (012, FR-122; E2E-015)


@pytest.fixture
def mesa_decisoria(gestor, api_client, manager_headers):
    from tests.fixtures.comissao import inscrever
    from tests.fixtures.mesa import distribuir_para
    from tests.fixtures.resultado import montar_etapa_de_leitura_unica

    cenario = montar_etapa_de_leitura_unica(
        gestor, api_client, manager_headers, seed=2400, codigo="2400", decisoria=True
    )
    inscricao = inscrever(cenario["edital"], 1, primeiro=1)[0]
    distribuir_para(cenario, gestor, ["joao"], [inscricao], chave="lote-2400")
    return cenario, inscricao


@pytest.mark.django_db
@pytest.mark.integration
def test_a_mesa_decisoria_mostra_os_rotulos_e_nao_o_campo_de_nota(
    client, seletor_ligado, mesa_decisoria
):
    """Jornada 2: o instrumento é o da forma publicada, e o vocabulário é o do Edital."""
    cenario, inscricao = mesa_decisoria
    identificar(client, "joao", [])

    corpo = client.get(
        reverse(
            "interface:mesa-inscricao",
            args=[cenario["edital"].id, cenario["etapa"], inscricao.id],
        )
    ).content.decode()

    assert 'name="sentido"' in corpo and ">Deferido<" in corpo and ">Indeferido<" in corpo
    assert 'id="pontuacao"' not in corpo


@pytest.mark.django_db
@pytest.mark.integration
def test_o_post_com_o_campo_da_outra_forma_e_recusado_no_canal_real(
    client, seletor_ligado, mesa_decisoria
):
    """A recusa é do domínio, e por isso ela existe também para quem não passa pela tela."""
    from processo_seletivo.avaliacoes.models import Avaliacao

    cenario, inscricao = mesa_decisoria
    identificar(client, "joao", [])

    client.post(
        reverse(
            "interface:mesa-avaliacao-concluir",
            args=[cenario["edital"].id, cenario["etapa"], inscricao.id],
        ),
        {
            "pontuacao": "80",
            "sentido": "FAVORAVEL",
            "parecer": "Atende",
            "expected_revision": "1",
            "versao_reconhecida": str(
                cenario["edital"].versoes_consolidadas.latest("materialized_at").id
            ),
        },
    )

    assert not Avaliacao.objects.filter(estado=Avaliacao.Estado.CONCLUIDA).exists()
