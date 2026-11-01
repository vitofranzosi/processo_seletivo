"""O teto e o Requerimento de Matrícula viajam no reaproveitamento (023, emenda do A-10).

**O defeito que estes testes prendem.** A cópia trazia as coleções e deixava para trás os dois
campos de raiz da etapa Inscrição. O 80/2026, reaproveitado do 51/2026 — que pedia o Requerimento
na convocação —, publicou `matriculationRequest = null`, foi publicável, e a convocada abriu
`/requerimento` para receber 404. O momento não se corrige por Retificação: o caminho de volta era
um Edital novo (auditoria de prontidão de 31/10/2026, A-10).

**A cópia roda como produção** (`como_producao`): ela escreve no Edital sob trava e grava trilha, e
o que só o privilégio recusa não se vê como superusuário (A-02).
"""

from unittest import mock

import pytest

from processo_seletivo.auditoria.models import RegistroAuditoria
from processo_seletivo.editais.application import reaproveitamento as servico
from processo_seletivo.editais.application.reaproveitamento import (
    o_que_sera_descartado,
    rascunho_vazio,
    reaproveitar_edital,
)
from processo_seletivo.editais.application.requerimento import (
    atualizar_requerimento_de_matricula,
)
from processo_seletivo.editais.application.teto import atualizar_teto_de_inscricoes
from processo_seletivo.processos.models import Edital
from processo_seletivo.publicacoes.application.selectors import effective_version
from processo_seletivo.requerimentos.domain import nomes
from processo_seletivo.shared.api.problems import DomainError
from tests.conftest import ator_institucional
from tests.fixtures.papel_de_producao import como_producao  # noqa: F401
from tests.fixtures.publicacao import publish_original

pytestmark = [pytest.mark.django_db, pytest.mark.integration]

DECLARACAO = "Declaro, sob as penas da Lei, que as informações prestadas são verdadeiras."


def declarar(*, teto=None, momento="", declaracao=""):
    """O gancho que fixa a etapa Inscrição da origem **antes** de o conteúdo congelar."""

    def antes_de_submeter(edital):
        Edital.objects.filter(pk=edital.pk).update(
            max_inscricoes_por_candidato=teto,
            requerimento_momento=momento,
            requerimento_declaracao=declaracao,
        )

    return antes_de_submeter


@pytest.fixture
def publicar_origem(db, api_client, manager_headers, process_payload):
    def publicar(**inscricao):
        return publish_original(
            api_client, manager_headers, process_payload, antes_de_submeter=declarar(**inscricao)
        )

    return publicar


@pytest.fixture
def destino(db, api_client, manager_headers):
    """Edital novo e vazio, em Processo próprio, **com descrição própria** — identificação dele."""
    criado = api_client.post(
        "/api/v1/admin/processos",
        {
            "institutionalCode": "PS-2027-010",
            "title": "Processo Seletivo 2027",
            "firstEdital": {"number": "80", "year": 2027, "title": "Edital da nova oferta"},
        },
        format="json",
        **{**manager_headers, "HTTP_IDEMPOTENCY_KEY": "destino-a10-0001"},
    )
    assert criado.status_code == 201, criado.content
    edital = Edital.objects.get(processo_id=criado.json()["id"])
    Edital.objects.filter(pk=edital.pk).update(description="Oferta de 2027, descrição própria")
    edital.refresh_from_db()
    return edital


@pytest.fixture
def elaborador():
    return ator_institucional("preparadora", "edital:elaborar")


def copiar(destino, origem, elaborador, *, chave="a10-0001", substituindo=False, revisao=None):
    return reaproveitar_edital(
        actor=elaborador,
        edital_id=destino.id,
        origem_id=origem.id,
        expected_revision=destino.revision if revisao is None else revisao,
        idempotency_key=chave,
        correlation_id="correlacao-a10",
        substituindo=substituindo,
    )


def configuracao(edital):
    edital.refresh_from_db()
    return (
        edital.max_inscricoes_por_candidato,
        edital.requerimento_momento,
        edital.requerimento_declaracao,
    )


# ---------------------------------------------------------------------------
# O que vem: o Requerimento como configuração coerente, e o teto
# ---------------------------------------------------------------------------


def test_requerimento_na_convocacao_vem_com_a_declaracao(
    publicar_origem,
    destino,
    elaborador,
    como_producao,  # noqa: F811
):
    origem = publicar_origem(momento=nomes.NA_CONVOCACAO, declaracao=DECLARACAO)

    with como_producao():
        copiado = copiar(destino, origem, elaborador)

    assert configuracao(copiado) == (None, nomes.NA_CONVOCACAO, DECLARACAO)


def test_requerimento_na_inscricao_preserva_o_momento_e_a_declaracao(
    publicar_origem,
    destino,
    elaborador,
    como_producao,  # noqa: F811
):
    origem = publicar_origem(momento=nomes.NA_INSCRICAO, declaracao=DECLARACAO)

    with como_producao():
        copiado = copiar(destino, origem, elaborador)

    assert configuracao(copiado) == (None, nomes.NA_INSCRICAO, DECLARACAO)


def test_origem_sem_requerimento_nao_inventa_exigencia(publicar_origem, destino, elaborador):
    """`null` na origem é *não exige*; o destino não pode passar a exigir por cópia."""
    origem = publicar_origem()
    assert effective_version(edital_id=origem.id).content["matriculationRequest"] is None

    copiado = copiar(destino, origem, elaborador)

    assert copiado.requerimento_momento == ""
    assert copiado.requerimento_declaracao == ""


def test_o_teto_da_origem_e_transferido(publicar_origem, destino, elaborador):
    origem = publicar_origem(teto=2)

    copiado = copiar(destino, origem, elaborador)

    assert copiado.max_inscricoes_por_candidato == 2


def test_sem_teto_na_origem_continua_sem_limite(publicar_origem, destino, elaborador):
    origem = publicar_origem()

    copiado = copiar(destino, origem, elaborador)

    assert copiado.max_inscricoes_por_candidato is None


def test_a_fonte_e_a_versao_vigente_e_nao_a_coluna_da_origem(publicar_origem, destino, elaborador):
    """A coluna da origem não é o que vigora nela: o que vigora é o conteúdo publicado (D-003)."""
    origem = publicar_origem(teto=2, momento=nomes.NA_CONVOCACAO, declaracao=DECLARACAO)
    Edital.objects.filter(pk=origem.pk).update(
        max_inscricoes_por_candidato=9, requerimento_momento="", requerimento_declaracao=""
    )

    copiado = copiar(destino, origem, elaborador)

    assert configuracao(copiado) == (2, nomes.NA_CONVOCACAO, DECLARACAO)


# ---------------------------------------------------------------------------
# O que fica: a identidade do destino
# ---------------------------------------------------------------------------


def test_numero_ano_titulo_descricao_e_processo_continuam_do_destino(
    publicar_origem, destino, elaborador
):
    origem = publicar_origem(teto=2, momento=nomes.NA_CONVOCACAO, declaracao=DECLARACAO)
    antes = (
        destino.number,
        destino.year,
        destino.title,
        destino.description,
        destino.processo_id,
    )

    copiado = copiar(destino, origem, elaborador)

    assert (
        copiado.number,
        copiado.year,
        copiado.title,
        copiado.description,
        copiado.processo_id,
    ) == antes
    assert copiado.description != origem.description


def test_a_configuracao_copiada_se_edita_antes_da_submissao(publicar_origem, destino, elaborador):
    """Copiar não é conferir: quem elabora revisa e muda pelos mesmos comandos de sempre."""
    origem = publicar_origem(teto=2, momento=nomes.NA_CONVOCACAO, declaracao=DECLARACAO)
    copiado = copiar(destino, origem, elaborador)

    copiado = atualizar_teto_de_inscricoes(
        actor=elaborador, edital_id=copiado.id, expected_revision=copiado.revision, teto=None
    )
    copiado = atualizar_requerimento_de_matricula(
        actor=elaborador,
        edital_id=copiado.id,
        expected_revision=copiado.revision,
        momento=nomes.NA_INSCRICAO,
        declaracao="Texto revisto para esta oferta.",
    )

    assert configuracao(copiado) == (None, nomes.NA_INSCRICAO, "Texto revisto para esta oferta.")
    assert copiado.status == Edital.Status.EM_ELABORACAO


def test_uma_revisao_e_um_evento_para_a_operacao_inteira(publicar_origem, destino, elaborador):
    """Pelas regras dos comandos de teto e Requerimento, e não pelos comandos — que seriam mais
    duas revisões e mais dois registros na trilha para um ato só."""
    origem = publicar_origem(teto=2, momento=nomes.NA_CONVOCACAO, declaracao=DECLARACAO)
    revisao = destino.revision

    copiado = copiar(destino, origem, elaborador)

    assert copiado.revision == revisao + 1
    operacoes = set(
        RegistroAuditoria.objects.filter(aggregate_id=destino.id).values_list(
            "operation", flat=True
        )
    )
    assert "ALTERAR_TETO_DE_INSCRICOES" not in operacoes
    assert "ALTERAR_REQUERIMENTO" not in operacoes


# ---------------------------------------------------------------------------
# A proteção contra sobrescrita
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "declarado",
    [
        {"max_inscricoes_por_candidato": 3},
        {"requerimento_momento": nomes.NA_INSCRICAO, "requerimento_declaracao": "Do destino."},
    ],
    ids=["teto", "requerimento"],
)
def test_destino_ja_configurado_nao_e_sobrescrito_em_silencio(
    publicar_origem, destino, elaborador, declarado
):
    """Nenhuma coleção preenchida, e ainda assim há o que perder."""
    origem = publicar_origem(teto=2, momento=nomes.NA_CONVOCACAO, declaracao=DECLARACAO)
    Edital.objects.filter(pk=destino.pk).update(**declarado)
    destino.refresh_from_db()
    antes = configuracao(destino)
    assert rascunho_vazio(destino) is False

    with pytest.raises(DomainError) as recusa:
        copiar(destino, origem, elaborador)

    assert recusa.value.code == "draft_not_empty"
    assert configuracao(destino) == antes
    assert not destino.perfis.exists()


def test_a_confirmacao_enumera_o_teto_e_o_requerimento_e_so_entao_substitui(
    publicar_origem, destino, elaborador
):
    origem = publicar_origem(teto=2, momento=nomes.NA_CONVOCACAO, declaracao=DECLARACAO)
    Edital.objects.filter(pk=destino.pk).update(
        max_inscricoes_por_candidato=3,
        requerimento_momento=nomes.NA_INSCRICAO,
        requerimento_declaracao="Do destino.",
    )
    destino.refresh_from_db()

    descarte = o_que_sera_descartado(destino)
    assert descarte["teto"] == 3
    assert descarte["requerimento"] == nomes.NA_INSCRICAO

    trocado = copiar(destino, origem, elaborador, substituindo=True)

    assert configuracao(trocado) == (2, nomes.NA_CONVOCACAO, DECLARACAO)


def test_a_mesma_chave_nao_executa_uma_segunda_copia(publicar_origem, destino, elaborador):
    """A repetição devolve o que a primeira devolveu, e não copia de novo por cima da revisão."""
    origem = publicar_origem(teto=2, momento=nomes.NA_CONVOCACAO, declaracao=DECLARACAO)
    revisao = destino.revision
    copiado = copiar(destino, origem, elaborador)
    copiado = atualizar_teto_de_inscricoes(
        actor=elaborador, edital_id=copiado.id, expected_revision=copiado.revision, teto=5
    )

    repetido = copiar(destino, origem, elaborador, revisao=revisao)

    assert repetido.pk == copiado.pk
    assert configuracao(repetido)[0] == 5
    assert (
        RegistroAuditoria.objects.filter(
            aggregate_id=destino.id, operation=servico.OPERACAO
        ).count()
        == 1
    )


def test_falha_no_meio_nao_deixa_copia_parcial(publicar_origem, destino, elaborador):
    """O teto e o Requerimento entram antes de `replace_draft`; se ele recusar, nada fica."""
    origem = publicar_origem(teto=2, momento=nomes.NA_CONVOCACAO, declaracao=DECLARACAO)
    revisao = destino.revision

    with (
        mock.patch.object(
            servico,
            "replace_draft",
            side_effect=DomainError("invalid_profiles", "Recusa simulada.", 422),
        ),
        pytest.raises(DomainError),
    ):
        copiar(destino, origem, elaborador)

    destino.refresh_from_db()
    assert configuracao(destino) == (None, "", "")
    assert destino.revision == revisao
    assert not destino.anexos.exists()
    assert rascunho_vazio(destino) is True


def test_origem_que_publicou_teto_invalido_recusa_a_copia_inteira(
    publicar_origem, destino, elaborador
):
    """A regra do comando vale na cópia: um valor que a origem publicou fora dela não chega ao
    rascunho, e o destino fica como estava."""
    origem = publicar_origem()
    versao = effective_version(edital_id=origem.id)

    conteudo = {**versao.content, "maxInscricoesPorCandidato": 0}
    with (
        mock.patch.object(servico, "elevar", return_value=conteudo),
        pytest.raises(DomainError) as recusa,
    ):
        copiar(destino, origem, elaborador)

    assert recusa.value.code == "field_constraint_violated"
    assert configuracao(destino) == (None, "", "")
    assert rascunho_vazio(destino) is True
