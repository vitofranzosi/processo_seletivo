"""A trilha da execução do trabalho, e os dois filtros que não saem de graça (FR-050, T-016).

O que este arquivo protege são duas suposições falsas que a primeira redação do plano fez:

- **`aggregate_id` não é a inscrição.** Os sete atos têm agregados diferentes, e filtrar por um só
  traria um sétimo dos eventos — pior que não filtrar, porque parece completo.
- **`actor_subject` não é o avaliador.** Nos atos da presidência o ator é ela, e o avaliador é o
  afetado. "O que aconteceu com o trabalho da Ana" não é "o que a Ana fez".
"""

import pytest
from django.urls import reverse

from processo_seletivo.avaliacoes.application.distribuicao import remover_atribuicao
from processo_seletivo.avaliacoes.application.impedimento import registrar_impedimento
from processo_seletivo.avaliacoes.models import Atribuicao
from tests.fixtures.comissao import DOCUMENTO_A, abrir_arquivo, inscrever
from tests.fixtures.edital import identificador
from tests.fixtures.mesa import concluir_como, distribuir_para
from tests.interface.conftest import identificar

pytestmark = [pytest.mark.django_db]

SEED = 15


@pytest.fixture
def cenario(gestor, api_client, manager_headers, raiz_de_arquivos):
    from tests.fixtures.comissao import (
        ETAPA_A1,
        alocar_em,
        constituir,
        publicar_processo_com_etapas,
    )

    edital = publicar_processo_com_etapas(
        api_client,
        {**manager_headers, "HTTP_IDEMPOTENCY_KEY": f"mvp-test-key-{SEED:04d}"},
        {
            "institutionalCode": "PS-2026-F1",
            "title": "Processo com trilha",
            "firstEdital": {"number": "F1", "year": 2026, "title": "Edital da trilha"},
        },
        seed=SEED,
        com_documentos=True,
        avaliacoes=2,
        maxima="100.0000",
    )
    etapa = identificador(ETAPA_A1, SEED)
    processo = edital.processo
    from processo_seletivo.comissoes.domain.funcoes import Funcao

    membros = constituir(
        gestor,
        processo,
        [("maria", Funcao.PRESIDENTE), ("joao", Funcao.MEMBRO), ("ana", Funcao.MEMBRO)],
        prefixo="trilha",
    )
    for nome in ("joao", "ana"):
        alocar_em(gestor, processo, membros[nome], edital, etapa, chave=f"tr-{nome}")
    return {"edital": edital, "etapa": etapa, "processo": processo, "membros": membros}


@pytest.fixture
def percurso(cenario, gestor, seletor_ligado):
    """Os sete atos, sobre a mesma inscrição — e as aberturas de dois avaliadores distintos."""
    inscricao = inscrever(
        cenario["edital"], 1, primeiro=1600, documentos=[identificador(DOCUMENTO_A, SEED)]
    )[0]
    outra = inscrever(cenario["edital"], 1, primeiro=1601)[0]
    distribuir_para(cenario, gestor, ["joao", "ana"], [inscricao], chave="tr")
    distribuir_para(cenario, gestor, ["joao"], [outra], chave="tr2")

    documento = reverse(
        "interface:mesa-documento",
        args=[
            cenario["edital"].id,
            cenario["etapa"],
            inscricao.id,
            identificador(DOCUMENTO_A, SEED),
        ],
    )
    # Cliente próprio por avaliador: reusar o do teste trocaria a sessão de quem audita.
    from django.test import Client

    for quem in ("joao", "ana"):
        cliente = Client()
        identificar(cliente, quem, [])
        abrir_arquivo(cliente, documento)

    from processo_seletivo.avaliacoes.application.avaliacao import gravar
    from tests.conftest import ator_institucional

    gravar(
        ator=ator_institucional("joao"),
        edital=cenario["edital"],
        etapa_id=cenario["etapa"],
        inscricao_id=inscricao.id,
        pontuacao="80",
        parecer="Em análise",
        expected_revision=1,
        correlation_id="teste",
    )
    avaliacao = concluir_como(cenario, "joao", inscricao, pontuacao="90", revisao=2)
    remover_atribuicao(
        actor=gestor,
        processo_id=cenario["processo"].id,
        atribuicao_ids=[Atribuicao.objects.get(inscricao=outra).id],
        idempotency_key="tr-rem",
        correlation_id="teste",
    )
    from processo_seletivo.avaliacoes.application.avaliacao import reabrir

    reabrir(
        actor=gestor,
        processo_id=cenario["processo"].id,
        avaliacao_id=avaliacao.id,
        motivo="Recurso deferido.",
        expected_revision=avaliacao.revision,
        idempotency_key="tr-reab",
        correlation_id="teste",
    )
    registrar_impedimento(
        actor=gestor,
        processo_id=cenario["processo"].id,
        identity_subject="ana",
        inscricao_id=inscricao.id,
        motivo="Parentesco.",
        idempotency_key="tr-imp",
        correlation_id="teste",
    )
    return {"inscricao": inscricao, "outra": outra}


@pytest.fixture
def auditor_na_tela(client, seletor_ligado):
    identificar(client, "carlos", ["gestor", "auditor"])
    return client


def registros(cliente, url):
    """Só a lista de atos.

    O corpo inteiro não serve para asserção de **ausência**: o seletor de filtros lista os sete
    rótulos de operação, e "não contém X" seria sempre falso.
    """
    corpo = cliente.get(url).content.decode()
    inicio = corpo.find('<ol class="auditoria"')
    if inicio == -1:
        return ""
    return corpo[inicio : corpo.find("</ol>", inicio)]


def trilha(cenario, **filtros):
    base = reverse("interface:trilha-da-avaliacao", args=[cenario["edital"].id, cenario["etapa"]])
    if not filtros:
        return base
    return base + "?" + "&".join(f"{chave}={valor}" for chave, valor in filtros.items())


def test_os_sete_atos_aparecem_na_trilha(auditor_na_tela, cenario, percurso):
    corpo = registros(auditor_na_tela, trilha(cenario))

    for rotulo in (
        "Atribuição de inscrição a avaliador",
        "Remoção de atribuição",
        "Consulta a documento do candidato",
        "Gravação de avaliação",
        "Conclusão de avaliação",
        "Reabertura de avaliação",
        "Registro de impedimento",
    ):
        assert rotulo in corpo, rotulo


def test_o_filtro_por_inscricao_reune_os_agregados_relacionados(auditor_na_tela, cenario, percurso):
    """A prova de que `aggregate_id` sozinho não bastaria: são quatro agregados diferentes."""
    corpo = registros(auditor_na_tela, trilha(cenario, inscricao=str(percurso["inscricao"].id)))

    for rotulo in (
        "Atribuição de inscrição a avaliador",
        "Consulta a documento do candidato",
        "Conclusão de avaliação",
        "Registro de impedimento",
    ):
        assert rotulo in corpo, rotulo
    # A remoção foi sobre **outra** inscrição, e não entra.
    assert "Remoção de atribuição" not in corpo


def test_o_filtro_por_avaliador_traz_o_que_fizeram_com_ele(auditor_na_tela, cenario, percurso):
    """Um ato da presidência sobre a atribuição da Ana aparece no filtro **dela**.

    Se o filtro saísse de `actor_subject`, este impedimento apareceria sob "carlos" — quem o
    praticou — e não sob quem ele afetou.
    """
    dela = registros(auditor_na_tela, trilha(cenario, avaliador="ana"))

    assert "Registro de impedimento" in dela
    assert "Avaliação tornada inelegível" in dela


def test_dois_avaliadores_abrindo_a_mesma_inscricao_nao_se_misturam(
    auditor_na_tela, cenario, percurso
):
    """O único ato cujo agregado não distingue avaliadores — e por isso entra pelo ator."""
    do_joao = registros(auditor_na_tela, trilha(cenario, avaliador="joao"))
    da_ana = registros(auditor_na_tela, trilha(cenario, avaliador="ana"))

    assert do_joao.count("Consulta a documento do candidato") == 1
    assert da_ana.count("Consulta a documento do candidato") == 1
    # Cada um sob o seu, e nenhum sob o do outro: a conclusão é do João e não aparece na dela.
    assert "Conclusão de avaliação" in do_joao
    assert "Conclusão de avaliação" not in da_ana


def test_o_impedimento_preventivo_aparece_nos_dois_filtros(auditor_na_tela, cenario, gestor):
    """Sem Atribuição ativa, o agregado é o próprio Impedimento — e ele não pode sumir da trilha."""
    inscricao = inscrever(cenario["edital"], 1, primeiro=1610)[0]
    registrar_impedimento(
        actor=gestor,
        processo_id=cenario["processo"].id,
        identity_subject="joao",
        inscricao_id=inscricao.id,
        motivo="Preventivo.",
        idempotency_key="prev",
        correlation_id="teste",
    )

    por_inscricao = registros(auditor_na_tela, trilha(cenario, inscricao=str(inscricao.id)))
    por_avaliador = registros(auditor_na_tela, trilha(cenario, avaliador="joao"))

    assert "Registro de impedimento" in por_inscricao
    assert "Registro de impedimento" in por_avaliador


def test_os_filtros_combinam(auditor_na_tela, cenario, percurso):
    corpo = registros(
        auditor_na_tela,
        trilha(
            cenario,
            avaliador="joao",
            inscricao=str(percurso["inscricao"].id),
            operacao="AVALIACAO_CONCLUIR",
        ),
    )

    assert "Conclusão de avaliação" in corpo
    assert "Registro de impedimento" not in corpo


def test_a_trilha_exige_permissao_de_auditoria(client, seletor_ligado, cenario, percurso):
    identificar(client, "carlos", ["gestor"])

    assert client.get(trilha(cenario)).status_code == 403
