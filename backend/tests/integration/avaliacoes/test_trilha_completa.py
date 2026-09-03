"""Os **sete** atos de FR-052, e o que cada registro precisa identificar (FR-053).

Atribuir, remover atribuição, abrir documento, gravar, concluir, reabrir e impedir. A lista existe
porque a trilha desta feature responde a perguntas que nenhuma outra responde: por que uma
avaliação não conta, quem abriu o documento de quem, e quando o acesso mudou.
"""

import pytest
from django.urls import reverse

from processo_seletivo.auditoria.models import RegistroAuditoria
from processo_seletivo.avaliacoes.application.avaliacao import gravar, reabrir
from processo_seletivo.avaliacoes.application.distribuicao import remover_atribuicao
from processo_seletivo.avaliacoes.application.impedimento import registrar_impedimento
from processo_seletivo.avaliacoes.models import Atribuicao
from tests.conftest import ator_institucional
from tests.fixtures.comissao import DOCUMENTO_A, abrir_arquivo, alocar_em, constituir, inscrever
from tests.fixtures.edital import identificador
from tests.fixtures.mesa import concluir_como, distribuir_para
from tests.interface.conftest import identificar

pytestmark = [pytest.mark.django_db, pytest.mark.integration]

SEED = 16
OS_SETE = (
    "AVALIACAO_ATRIBUIR",
    "AVALIACAO_ATRIBUICAO_REMOVER",
    "CONSULTAR_DOCUMENTO",
    "AVALIACAO_GRAVAR",
    "AVALIACAO_CONCLUIR",
    "AVALIACAO_REABRIR",
    "AVALIACAO_IMPEDIR",
)


@pytest.fixture
def cenario(gestor, api_client, manager_headers, raiz_de_arquivos):
    from processo_seletivo.comissoes.domain.funcoes import Funcao
    from tests.fixtures.comissao import ETAPA_A1, publicar_processo_com_etapas

    edital = publicar_processo_com_etapas(
        api_client,
        {**manager_headers, "HTTP_IDEMPOTENCY_KEY": f"mvp-test-key-{SEED:04d}"},
        {
            "institutionalCode": "PS-2026-G1",
            "title": "Processo dos sete atos",
            "firstEdital": {"number": "G1", "year": 2026, "title": "Edital dos sete atos"},
        },
        seed=SEED,
        com_documentos=True,
        avaliacoes=2,
        maxima="100.0000",
    )
    etapa = identificador(ETAPA_A1, SEED)
    membros = constituir(
        gestor,
        edital.processo,
        [("maria", Funcao.PRESIDENTE), ("joao", Funcao.MEMBRO)],
        prefixo="sete",
    )
    alocar_em(gestor, edital.processo, membros["joao"], edital, etapa, chave="sete")
    return {"edital": edital, "etapa": etapa, "processo": edital.processo, "membros": membros}


@pytest.fixture
def percorridos(cenario, gestor, client, seletor_ligado):
    alvo, descartada = inscrever(
        cenario["edital"], 2, primeiro=1700, documentos=[identificador(DOCUMENTO_A, SEED)]
    )
    distribuir_para(cenario, gestor, ["joao"], [alvo, descartada], chave="sete")
    identificar(client, "joao", [])
    abrir_arquivo(
        client,
        reverse(
            "interface:mesa-documento",
            args=[
                cenario["edital"].id,
                cenario["etapa"],
                alvo.id,
                identificador(DOCUMENTO_A, SEED),
            ],
        ),
    )
    gravar(
        ator=ator_institucional("joao"),
        edital=cenario["edital"],
        etapa_id=cenario["etapa"],
        inscricao_id=alvo.id,
        pontuacao="80",
        parecer="Em análise",
        expected_revision=1,
        correlation_id="teste",
    )
    avaliacao = concluir_como(cenario, "joao", alvo, pontuacao="90", revisao=2)
    remover_atribuicao(
        actor=gestor,
        processo_id=cenario["processo"].id,
        atribuicao_ids=[Atribuicao.objects.get(inscricao=descartada).id],
        idempotency_key="sete-rem",
        correlation_id="teste",
    )
    reabrir(
        actor=gestor,
        processo_id=cenario["processo"].id,
        avaliacao_id=avaliacao.id,
        motivo="Recurso deferido.",
        expected_revision=avaliacao.revision,
        idempotency_key="sete-reab",
        correlation_id="teste",
    )
    registrar_impedimento(
        actor=gestor,
        processo_id=cenario["processo"].id,
        identity_subject="joao",
        inscricao_id=alvo.id,
        motivo="Parentesco.",
        idempotency_key="sete-imp",
        correlation_id="teste",
    )
    return {"alvo": alvo, "descartada": descartada, "avaliacao": avaliacao}


def test_os_sete_atos_produzem_evento(cenario, percorridos):
    registrados = set(RegistroAuditoria.objects.values_list("operation", flat=True))

    for operacao in OS_SETE:
        assert operacao in registrados, operacao


def test_cada_evento_identifica_ator_operacao_e_instante(cenario, percorridos):
    """FR-053. Um evento sem ator ou sem instante não responde a pergunta nenhuma."""
    for evento in RegistroAuditoria.objects.filter(operation__in=OS_SETE):
        assert evento.actor_subject
        assert evento.operation
        assert evento.occurred_at is not None
        assert evento.institution_scope
        assert evento.permission


def test_a_inscricao_e_alcancavel_a_partir_de_todo_evento(cenario, percorridos):
    """A trilha responde "o que aconteceu com esta inscrição" — pelas relações, e não por coluna.

    Cada agregado dos sete atos leva à inscrição: `Inscricao` diretamente, `Atribuicao` e
    `Impedimento` por chave estrangeira, `Avaliacao` pela Atribuição. É isso que torna o filtro de
    FR-050 possível sem carimbar a inscrição em cada evento (FR-070, T-016).
    """
    from processo_seletivo.avaliacoes.models import Avaliacao, Impedimento
    from processo_seletivo.inscricoes.models import Inscricao

    resolve = {
        "Inscricao": lambda pk: Inscricao.objects.filter(pk=pk).values_list("id", flat=True),
        "Atribuicao": lambda pk: Atribuicao.objects.filter(pk=pk).values_list(
            "inscricao_id", flat=True
        ),
        "Avaliacao": lambda pk: Avaliacao.objects.filter(pk=pk).values_list(
            "inscricao_id", flat=True
        ),
        "Impedimento": lambda pk: Impedimento.objects.filter(pk=pk).values_list(
            "inscricao_id", flat=True
        ),
    }
    for evento in RegistroAuditoria.objects.filter(operation__in=OS_SETE):
        alcance = resolve[evento.aggregate_type](evento.aggregate_id)
        assert list(alcance), (evento.operation, evento.aggregate_type)


def test_a_etapa_e_alcancavel_nos_atos_da_avaliacao(cenario, percorridos):
    """FR-053 pede a Etapa, e ela vem da Atribuição — que é quem a conhece."""
    from processo_seletivo.avaliacoes.models import Avaliacao

    for evento in RegistroAuditoria.objects.filter(
        operation__in=("AVALIACAO_ATRIBUIR", "AVALIACAO_CONCLUIR")
    ):
        if evento.aggregate_type == "Atribuicao":
            etapa = Atribuicao.objects.get(pk=evento.aggregate_id).etapa_id
        else:
            etapa = Avaliacao.objects.get(pk=evento.aggregate_id).etapa_id
        assert str(etapa) == str(cenario["etapa"])


def test_os_atos_com_motivo_tambem_gravam_ato_administrativo(cenario, percorridos):
    """Impedir, tornar inelegível e reabrir: o motivo obrigatório vive no ato, não na trilha."""
    from processo_seletivo.processos.models import AtoAdministrativo

    operacoes = set(AtoAdministrativo.objects.values_list("operation", flat=True))

    assert {"AVALIACAO_IMPEDIR", "AVALIACAO_REABRIR", "AVALIACAO_TORNAR_INELEGIVEL"} <= operacoes
    for ato in AtoAdministrativo.objects.filter(operation__startswith="AVALIACAO_"):
        assert ato.reason.strip()
