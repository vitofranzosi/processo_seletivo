"""A vertical que a §24 da spec declara como primeira entrega significativa (MVP).

> presidente distribui → avaliador abre a Mesa → abre a inscrição → registra e conclui →
> quem não recebeu aquela inscrição não a alcança.

Três atores, um percurso, e a recusa como parte da entrega — não como nota de rodapé. Metade do
que esta feature promete só se prova pela negação: um caminho feliz que ninguém tentou furar não
demonstra que o avaliador vê **somente** o que lhe cabe.

Tudo pelo canal do ator, que é o que o princípio VI da Constituição exige.
"""

import pytest
from django.test import Client
from django.urls import reverse

from processo_seletivo.avaliacoes.models import Atribuicao, Avaliacao, ConclusaoAvaliacao
from processo_seletivo.comissoes.domain.funcoes import Funcao
from tests.fixtures.comissao import (
    DOCUMENTO_A,
    ETAPA_A1,
    abrir_arquivo,
    alocar_em,
    constituir,
    inscrever,
)
from tests.fixtures.edital import identificador
from tests.interface.conftest import identificar

pytestmark = [pytest.mark.django_db, pytest.mark.acceptance]

SEED = 6


@pytest.fixture
def edital(db, raiz_de_arquivos, api_client, manager_headers):
    """Etapa eliminatória, duas avaliações por inscrição, máxima 100 e mínima 70."""
    from tests.fixtures.comissao import publicar_processo_com_etapas

    return publicar_processo_com_etapas(
        api_client,
        {**manager_headers, "HTTP_IDEMPOTENCY_KEY": "mvp-test-key-0061"},
        {
            "institutionalCode": "PS-2026-061",
            "title": "Processo Seletivo Docente",
            "firstEdital": {"number": "07", "year": 2027, "title": "Edital 07/2027"},
        },
        seed=SEED,
        com_documentos=True,
        avaliacoes=2,
        maxima="100.0000",
        minima="70.0000",
    )


@pytest.fixture
def etapa(edital):
    return identificador(ETAPA_A1, SEED)


@pytest.fixture
def comissao(gestor, edital, etapa):
    """Maria preside; João e Ana avaliam. Bruno está alocado e não recebe nada."""
    processo = edital.processo
    membros = constituir(
        gestor,
        processo,
        [
            ("maria", Funcao.PRESIDENTE),
            ("joao", Funcao.MEMBRO),
            ("ana", Funcao.MEMBRO),
            ("bruno", Funcao.MEMBRO),
        ],
        prefixo="mvp",
    )
    for nome in ("joao", "ana", "bruno"):
        alocar_em(gestor, processo, membros[nome], edital, etapa)
    return membros


@pytest.fixture
def inscricoes(edital):
    return inscrever(edital, 2, primeiro=600, documentos=[identificador(DOCUMENTO_A, SEED)])


def como(subject):
    cliente = Client()
    identificar(cliente, subject, [])
    return cliente


def test_a_vertical_completa(seletor_ligado, edital, etapa, comissao, inscricoes, gestor):
    da_maria, do_joao, do_bruno = como("maria"), como("joao"), como("bruno")
    primeira, segunda = inscricoes

    # 1. A presidente distribui — em lote, e pela tela.
    distribuicao = reverse("interface:distribuicao", args=[edital.id, etapa])
    da_maria.post(
        distribuicao,
        {
            "acao": "distribuir",
            "chave_idempotencia": "mvp-lote",
            "membro_id": [str(comissao["joao"].id)],
            "inscricao_id": [str(primeira.id), str(segunda.id)],
        },
    )
    painel = da_maria.get(distribuicao).content.decode()
    assert "2</strong> atribuídas" in painel
    assert Atribuicao.objects.filter(ativo=True).count() == 2

    # 2. João abre a Mesa e vê as duas.
    mesa = reverse("interface:minha-etapa", args=[edital.id, etapa])
    corpo_da_mesa = do_joao.get(mesa).content.decode()
    # As contagens da Mesa são um controle de filtro: o número e o estado, lado a lado.
    assert "no total" in corpo_da_mesa and ">2<" in corpo_da_mesa
    assert "não iniciadas" in corpo_da_mesa
    assert primeira.protocolo in corpo_da_mesa

    # 3. Abre a inscrição e o documento — que é conferido antes de sair um byte.
    pagina = reverse("interface:mesa-inscricao", args=[edital.id, etapa, primeira.id])
    detalhe = do_joao.get(pagina).content.decode()
    assert "Documento de identificação" in detalhe
    documento = reverse(
        "interface:mesa-documento",
        args=[edital.id, etapa, primeira.id, identificador(DOCUMENTO_A, SEED)],
    )
    assert abrir_arquivo(do_joao, documento).status_code == 200

    # 4. Registra e conclui — dois atos distintos.
    do_joao.post(
        reverse("interface:mesa-avaliacao-gravar", args=[edital.id, etapa, primeira.id]),
        {"pontuacao": "88", "parecer": "Em análise", "expected_revision": "1"},
    )
    avaliacao = Avaliacao.objects.get(inscricao_id=primeira.id, identity_subject="joao")
    assert avaliacao.estado == Avaliacao.Estado.RASCUNHO

    versao = edital.versoes_consolidadas.latest("materialized_at")
    do_joao.post(
        reverse("interface:mesa-avaliacao-concluir", args=[edital.id, etapa, primeira.id]),
        {
            "pontuacao": "88",
            "parecer": "Atende ao exigido no item 4.2.",
            "expected_revision": str(avaliacao.revision),
            "versao_reconhecida": str(versao.id),
        },
    )
    avaliacao.refresh_from_db()
    assert avaliacao.estado == Avaliacao.Estado.CONCLUIDA
    assert avaliacao.versao_id == versao.id
    assert ConclusaoAvaliacao.objects.filter(avaliacao=avaliacao).count() == 1

    # A Mesa passa a contar a conclusão.
    depois = do_joao.get(mesa).content.decode()
    # As parcelas fecham com o total: uma não iniciada, uma concluída, duas ao todo.
    assert ">1</strong> <span>não iniciada" in depois
    assert ">1</strong> <span>concluída" in depois

    # 5. **A recusa faz parte da entrega.** Bruno está alocado, e não recebeu nada.
    assert do_bruno.get(mesa).status_code == 200
    assert "Nenhuma inscrição foi distribuída a você" in do_bruno.get(mesa).content.decode()
    assert do_bruno.get(pagina).status_code == 404
    assert abrir_arquivo(do_bruno, documento).status_code == 404

    # E quem não está alocado não alcança nem a Etapa.
    assert como("estranho").get(mesa).status_code == 404


def test_a_vertical_nao_produz_resultado(
    seletor_ligado, edital, etapa, comissao, inscricoes, gestor
):
    """SC-013: a 012 executa o trabalho e para ali.

    Nada nesta jornada diz média, quórum, divergência, situação, apto ou aprovado — e a ausência
    é o critério de aceite, porque antecipá-los faria a nota de uma pessoa parecer decisão da
    instituição (P-006, FR-037).
    """
    da_maria, do_joao = como("maria"), como("joao")
    primeira = inscricoes[0]
    da_maria.post(
        reverse("interface:distribuicao", args=[edital.id, etapa]),
        {
            "acao": "distribuir",
            "chave_idempotencia": "mvp-sem-resultado",
            "membro_id": [str(comissao["joao"].id)],
            "inscricao_id": [str(primeira.id)],
        },
    )
    avaliacao_da_tela = reverse("interface:mesa-inscricao", args=[edital.id, etapa, primeira.id])
    do_joao.post(
        reverse("interface:mesa-avaliacao-concluir", args=[edital.id, etapa, primeira.id]),
        {
            "pontuacao": "88",
            "parecer": "Atende.",
            "expected_revision": "1",
            "versao_reconhecida": str(edital.versoes_consolidadas.latest("materialized_at").id),
        },
    )

    telas = [
        do_joao.get(avaliacao_da_tela).content.decode(),
        do_joao.get(reverse("interface:minha-etapa", args=[edital.id, etapa])).content.decode(),
        da_maria.get(reverse("interface:distribuicao", args=[edital.id, etapa])).content.decode(),
    ]

    primeira.refresh_from_db()
    assert primeira.status == "SUBMETIDA"
    for corpo in telas:
        for proibido in ("média", "Média", "quórum", "apto", "Apto", "aprovad", "classificaç"):
            assert proibido not in corpo
