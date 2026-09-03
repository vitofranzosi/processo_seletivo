"""A consulta administrativa em escala — paginada, filtrável, e contando (FR-066, FR-067).

**Por que existe.** A tela substituía a planilha para dezenas e a convocava de volta para
centenas: uma página só, com todas as linhas, sem busca, sem filtro e sem nenhum número além do
total. As perguntas de quem confere mil e quinhentas inscrições — "quantas por Perfil", "quantas
na modalidade reservada", "onde está fulano" — não se respondiam ali, e nenhuma delas exige
exportar coisa alguma: exigem que a tela saiba contar e filtrar.

O que estes testes prendem é isso, e mais uma coisa que não se vê: o custo da tela é o da
**página**, e não o do certame.
"""

import re

import pytest
from django.db import connection
from django.test.utils import CaptureQueriesContext
from django.urls import reverse
from django.utils import timezone

from processo_seletivo.inscricoes.application.consulta import POR_PAGINA
from processo_seletivo.inscricoes.models import Inscricao
from processo_seletivo.publicacoes.models_retificacao import VersaoConsolidada
from tests.fixtures.candidato import MODALIDADE_AC, MODALIDADE_PPP, PERFIL_DOCENTE, PERFIL_TECNICO
from tests.interface.conftest import identificar

pytestmark = [pytest.mark.django_db, pytest.mark.integration]


@pytest.fixture
def gestor(client, settings):
    settings.INTERFACE_SELETOR_IDENTIDADE = True
    identificar(client, "bruno.gestor", ["gestor"])
    return client


def inscrever(
    edital,
    quantas,
    *,
    primeiro=1,
    perfil=PERFIL_DOCENTE,
    modalidade=MODALIDADE_AC,
    enviada=True,
    nome="Candidato",
):
    """Inscrições direto no agregado — o percurso do candidato tem testes próprios."""
    versao = VersaoConsolidada.objects.filter(edital=edital).latest("materialized_at")
    agora = timezone.now()
    criadas = []
    for numero in range(primeiro, primeiro + quantas):
        inscricao = Inscricao.objects.create(
            created_at=agora,
            identity_subject=f"cand:escala-{numero:05d}",
            edital=edital,
            profile_id=perfil,
            modality_id=modalidade,
            nome=f"{nome} {numero:03d}",
            cpf="529.982.247-25",
            cpf_normalizado="52998224725",
            email=f"escala{numero}@exemplo.br",
        )
        if enviada:
            Inscricao.objects.filter(pk=inscricao.pk).update(
                status=Inscricao.Status.SUBMETIDA,
                protocolo=f"INS-2026-E{numero:05d}",
                submitted_at=agora,
                versao_aceita=versao,
                declaracoes_aceitas_em=agora,
            )
        inscricao.refresh_from_db()
        criadas.append(inscricao)
    return criadas


@pytest.fixture
def tela(selecao):
    return reverse("interface:inscricoes", args=[selecao.id])


def test_a_lista_pagina_em_vez_de_render_tudo(gestor, selecao, tela):
    inscrever(selecao, POR_PAGINA + 5)

    corpo = gestor.get(tela).content.decode()

    assert "Página 1 de 2" in corpo
    assert "Próxima" in corpo
    assert corpo.count("INS-2026-E") == POR_PAGINA


def test_o_total_continua_sendo_o_do_edital_e_nao_o_da_pagina(gestor, selecao, tela):
    """O `<h1>` é o mesmo número do rótulo que trouxe a pessoa até aqui (FR-066).

    Vê-lo virar 25 ao paginar diria que o certame encolheu — e é o contrato entre esta tela e a
    ação `Inscrições recebidas (N)` da lista de Editais.
    """
    inscrever(selecao, 30)

    corpo = gestor.get(tela).content.decode()

    assert "Inscrições — 30" in corpo


def test_procurar_por_nome_protocolo_ou_cpf_encontra_a_mesma_pessoa(gestor, selecao, tela):
    """Três formas, porque quem confere tem uma das três em mãos."""
    procurada, outra = inscrever(selecao, 2)

    por_nome = gestor.get(f"{tela}?busca=Candidato 001").content.decode()
    por_protocolo = gestor.get(f"{tela}?busca={procurada.protocolo}").content.decode()
    por_cpf = gestor.get(f"{tela}?busca=529.982.247-25").content.decode()

    assert procurada.protocolo in por_nome and outra.protocolo not in por_nome
    assert procurada.protocolo in por_protocolo and outra.protocolo not in por_protocolo
    assert procurada.protocolo in por_cpf and outra.protocolo in por_cpf, "o CPF é o mesmo dos dois"


def test_a_busca_sem_correspondencia_diz_que_e_o_filtro(gestor, selecao, tela):
    """A tela vazia por filtro não pode se parecer com a tela vazia por não ter chegado ninguém."""
    inscrever(selecao, 2)

    corpo = gestor.get(f"{tela}?busca=Fulano").content.decode()

    assert "Nenhuma inscrição recebida corresponde a este filtro." in corpo
    assert "Nenhuma inscrição recebida até agora." not in corpo


def test_os_contadores_por_perfil_sao_o_filtro(gestor, selecao, tela):
    """FR-067 pela via da `012`: o número que responde a pergunta é o que leva ao recorte."""
    docentes = inscrever(selecao, 3)
    tecnicos = inscrever(selecao, 2, primeiro=90, perfil=PERFIL_TECNICO, nome="Técnico")

    corpo = gestor.get(tela).content.decode()
    filtrada = gestor.get(f"{tela}?perfil={PERFIL_TECNICO}").content.decode()

    assert f'href="?perfil={PERFIL_TECNICO}"' in corpo
    assert "<strong>3</strong>" in corpo and "<strong>2</strong>" in corpo
    for tecnico in tecnicos:
        assert tecnico.protocolo in filtrada
    for docente in docentes:
        assert docente.protocolo not in filtrada


def test_o_filtro_por_modalidade_responde_a_pergunta_da_cota(gestor, selecao, tela):
    ampla = inscrever(selecao, 2)
    reservada = inscrever(selecao, 1, primeiro=80, modalidade=MODALIDADE_PPP)

    corpo = gestor.get(f"{tela}?modalidade={MODALIDADE_PPP}").content.decode()

    assert reservada[0].protocolo in corpo
    for inscricao in ampla:
        assert inscricao.protocolo not in corpo


def test_os_contadores_nao_mudam_com_o_filtro(gestor, selecao, tela):
    """O filtro muda o que se lista, e nunca o que se conta.

    Contadores que seguem o recorte descrevem a pergunta, e não o certame — e quem lê "2 de 2"
    depois de filtrar não tem como saber que havia trinta.
    """
    inscrever(selecao, 3)
    inscrever(selecao, 2, primeiro=90, perfil=PERFIL_TECNICO, nome="Técnico")

    corpo = gestor.get(f"{tela}?perfil={PERFIL_TECNICO}").content.decode()

    assert "Inscrições — 5" in corpo
    assert "<strong>3</strong>" in corpo, "o Perfil não filtrado continua contando o que tem"


def test_a_paginacao_carrega_o_filtro_consigo(gestor, selecao, tela):
    """Avançar de página não pode desfazer a pergunta que trouxe a pessoa até aqui."""
    inscrever(selecao, POR_PAGINA + 3, perfil=PERFIL_TECNICO, nome="Técnico")

    corpo = gestor.get(f"{tela}?perfil={PERFIL_TECNICO}&busca=Técnico").content.decode()

    proxima = re.search(r'<a href="([^"]+)">Próxima</a>', corpo)
    assert proxima, "há segunda página"
    assert f"perfil={PERFIL_TECNICO}" in proxima.group(1)
    assert "busca=" in proxima.group(1)


def test_os_rascunhos_paginam_por_conta_propria(gestor, selecao, tela):
    """Dois conjuntos com prazos distintos: avançar num não arrasta quem conferia o outro."""
    inscrever(selecao, 3)
    inscrever(selecao, POR_PAGINA + 2, primeiro=200, enviada=False, nome="Rascunho")

    corpo = gestor.get(tela).content.decode()
    segunda = gestor.get(f"{tela}?rascunhos=2").content.decode()

    assert "Em preenchimento — 27" in corpo
    assert "Páginas de rascunhos em preenchimento" in corpo
    assert corpo.index("Inscrições recebidas neste Edital") < corpo.index(
        "Rascunhos em preenchimento"
    ), "o que chegou continua vindo primeiro"
    assert "Página 2 de 2" in segunda


@pytest.mark.performance
def test_o_custo_da_tela_e_o_da_pagina_e_nao_o_do_certame(gestor, selecao, tela):
    """A prova que um limite absoluto não dá: o mesmo custo para 5 e para 300.

    Antes, a tela carregava todas as inscrições e **todos** os documentos do Edital para desenhar
    o que coubesse — o custo crescia com o certame, que é exatamente o que uma seleção grande faz.
    """
    inscrever(selecao, 5)
    with CaptureQueriesContext(connection) as poucas:
        gestor.get(tela)

    inscrever(selecao, 295, primeiro=1000)
    with CaptureQueriesContext(connection) as muitas:
        resposta = gestor.get(tela)

    assert resposta.status_code == 200
    assert len(muitas.captured_queries) == len(poucas.captured_queries), (
        f"{len(poucas.captured_queries)} → {len(muitas.captured_queries)}"
    )
