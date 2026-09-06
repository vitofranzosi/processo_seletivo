"""As três tabelas da divulgação nascem e não mudam mais — por nenhum caminho (FR-040, FR-071).

Três camadas, e elas não se substituem: o modelo recusa, a trigger recusa **mesmo de quem tem
privilégio**, e o papel de runtime não tem `UPDATE` nem `DELETE` para tentar. A do meio é a que
vale contra quem chega por fora da aplicação; a de baixo continua valendo se a trigger for
removida.
"""

import uuid

import pytest
from django.db import DatabaseError, IntegrityError, connection, transaction
from django.utils import timezone

from processo_seletivo.divulgacao.models import (
    DocumentoDoResultado,
    PublicacaoResultado,
    SituacaoDivulgada,
)
from processo_seletivo.seguranca.papeis import TABELAS_APPEND_ONLY
from tests.fixtures.divulgacao import montar_ato_publicavel

pytestmark = [pytest.mark.integration, pytest.mark.django_db(transaction=True)]

SOMENTE_POSTGRES = pytest.mark.skipif(
    connection.vendor != "postgresql",
    reason="As triggers e os privilégios são de PostgreSQL; em sqlite a garantia não existe.",
)

TABELAS_DA_DIVULGACAO = (
    "divulgacao_publicacaoresultado",
    "divulgacao_situacaodivulgada",
    "divulgacao_documentodoresultado",
)


@pytest.fixture
def publicada(gestor, api_client, manager_headers, process_payload):
    """Uma publicação com uma situação divulgada e um documento — as três tabelas povoadas."""
    cenario = montar_ato_publicavel(
        gestor, api_client, manager_headers, process_payload, seed=30, codigo="0730"
    )
    ato = cenario["ato"]
    publicacao = PublicacaoResultado.objects.create(
        edital=cenario["edital"],
        ato=ato,
        perfil_id=ato.perfil_id,
        marco_id=ato.marco_id,
        natureza="PRELIMINAR",
        conteudo_publico=b'{"cabecalho":{},"posicoes":[]}',
        conteudo_publico_hash="0" * 64,
        publicado_por="paula.publicadora",
        publicado_em=timezone.now(),
        signatario_id=uuid.uuid4(),
        signatario_nome="Diretora do Cefor",
        signatario_cargo="Diretora-Geral",
    )
    situacao = SituacaoDivulgada.objects.create(
        publicacao=publicacao,
        inscricao=cenario["inscricoes"][0],
        situacao=SituacaoDivulgada.Situacao.CLASSIFICADA,
        posicao=1,
        pontuacao="90,00",
    )
    documento = DocumentoDoResultado.objects.create(
        publicacao=publicacao, bytes=b"%PDF-1.4", documento_hash="1" * 64
    )
    return cenario, publicacao, situacao, documento


def test_as_tres_tabelas_estao_na_politica_de_privilegios():
    """Registrar é o que faz a política enxergá-las: o que não está na tupla não é revogado."""
    assert set(TABELAS_DA_DIVULGACAO) <= set(TABELAS_APPEND_ONLY)


@pytest.mark.parametrize("tabela", TABELAS_DA_DIVULGACAO)
def test_o_modelo_recusa_alteracao_e_exclusao(publicada, tabela):
    _, publicacao, situacao, documento = publicada
    linha = {
        "divulgacao_publicacaoresultado": publicacao,
        "divulgacao_situacaodivulgada": situacao,
        "divulgacao_documentodoresultado": documento,
    }[tabela]

    with pytest.raises(TypeError, match="append-only"):
        linha.save()
    with pytest.raises(TypeError, match="append-only"):
        linha.delete()


@SOMENTE_POSTGRES
def test_o_papel_de_runtime_nao_consegue_escrever_sobre_as_tres(publicada):
    """A segunda camada, e a única que vale contra quem chega por fora da aplicação (FR-071).

    A consulta é a mesma de `conferencia`: se `provisionar_papeis` deixasse de revogar, o papel
    teria `UPDATE` sobre o que a instituição já divulgou, e nada avisaria.
    """
    from processo_seletivo.seguranca.papeis import comandos_de_privilegios

    with connection.cursor() as cursor:
        cursor.execute("SELECT 1 FROM pg_roles WHERE rolname = 'ps_runtime_teste'")
        if cursor.fetchone() is None:
            cursor.execute("CREATE ROLE ps_runtime_teste NOLOGIN")
        for comando in comandos_de_privilegios(
            migration_role=connection.settings_dict["USER"] or "postgres",
            runtime_role="ps_runtime_teste",
            tabelas=TABELAS_DA_DIVULGACAO,
        ):
            cursor.execute(comando)
        excessivos = []
        for tabela in TABELAS_DA_DIVULGACAO:
            cursor.execute(
                "SELECT has_table_privilege(%s, %s, 'UPDATE') "
                "OR has_table_privilege(%s, %s, 'DELETE')",
                ["ps_runtime_teste", f"public.{tabela}", "ps_runtime_teste", f"public.{tabela}"],
            )
            if cursor.fetchone()[0]:
                excessivos.append(tabela)

    assert excessivos == [], f"o runtime ainda escreve sobre: {excessivos}"


@SOMENTE_POSTGRES
@pytest.mark.parametrize("tabela", TABELAS_DA_DIVULGACAO)
@pytest.mark.parametrize("verbo", ["UPDATE", "DELETE"])
def test_a_trigger_recusa_mutacao_por_sql_cru(publicada, tabela, verbo):
    """Absoluta: a recusa vale mesmo para quem tem privilégio de sobra (FR-040)."""
    _, publicacao, situacao, documento = publicada
    alvo = {
        "divulgacao_publicacaoresultado": publicacao.id,
        "divulgacao_situacaodivulgada": situacao.id,
        "divulgacao_documentodoresultado": documento.id,
    }[tabela]
    sql = (
        f"DELETE FROM {tabela} WHERE id = %s"
        if verbo == "DELETE"
        else f"UPDATE {tabela} SET id = id WHERE id = %s"
    )

    with (
        pytest.raises(DatabaseError, match="append-only"),
        transaction.atomic(),
        connection.cursor() as cursor,
    ):
        cursor.execute(sql, [str(alvo)])


def test_duas_situacoes_da_mesma_inscricao_na_mesma_publicacao_sao_recusadas(publicada):
    """`uq_situacao_por_publicacao_inscricao`: uma pessoa tem **uma** situação por divulgação.

    Sem ela, a Área do Candidato poderia mostrar duas situações contraditórias para o mesmo marco
    e não teria como escolher entre elas — e nenhuma das duas seria errada de mais.
    """
    cenario, publicacao, *_ = publicada

    with pytest.raises(IntegrityError), transaction.atomic():
        SituacaoDivulgada.objects.create(
            publicacao=publicacao,
            inscricao=cenario["inscricoes"][0],
            situacao=SituacaoDivulgada.Situacao.SEM_POSICAO,
            motivo="Outra afirmação sobre a mesma pessoa.",
        )
