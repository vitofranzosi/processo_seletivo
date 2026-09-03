"""As duas triggers do Resultado — o mesmo raciocínio em tempos diferentes.

`resultado_etapa_coerente` impede que a linha nasça errada; `resultado_etapa_append_only` impede
que ela mude depois. A ordem entre elas importa para o argumento: num registro append-only, uma
combinação errada gravada uma vez é **incorrigível**, de modo que a segunda trigger sozinha apenas
congelaria o erro.

Seis divergências, e a última é a que a primeira redação do plano não tinha. Elegibilidade, na 012,
é conclusão sob Atribuição **ativa** — sem conferi-la, a trigger provaria que o Resultado aponta
para a Avaliação certa sem provar que essa Avaliação podia fundamentar coisa alguma.
"""

from decimal import Decimal

import pytest
from django.db import IntegrityError, connection, transaction
from django.utils import timezone

from processo_seletivo.avaliacoes.models import Atribuicao
from processo_seletivo.resultados.models import ResultadoEtapa
from tests.fixtures.comissao import inscrever
from tests.fixtures.mesa import concluir_como, distribuir_para
from tests.fixtures.resultado import montar_etapa_de_leitura_unica

pytestmark = [pytest.mark.integration, pytest.mark.django_db(transaction=True)]

SOMENTE_POSTGRES = pytest.mark.skipif(
    connection.vendor != "postgresql",
    reason="As triggers são de PostgreSQL; em sqlite a garantia não existe.",
)


@pytest.fixture
def consolidavel(gestor, api_client, manager_headers):
    cenario = montar_etapa_de_leitura_unica(
        gestor, api_client, manager_headers, seed=1300, codigo="1300"
    )
    inscricao = inscrever(cenario["edital"], 1, primeiro=1)[0]
    distribuir_para(cenario, gestor, ["joao"], [inscricao], chave="lote-1300")
    avaliacao = concluir_como(cenario, "joao", inscricao, pontuacao="75")
    return cenario, inscricao, avaliacao


def gravar(cenario, inscricao, avaliacao, **sobrescrever):
    campos = {
        "inscricao": inscricao,
        "edital": cenario["edital"],
        "etapa_id": cenario["etapa"],
        "avaliacao": avaliacao,
        "pontuacao": avaliacao.pontuacao,
        "consequencia": ResultadoEtapa.Consequencia.HABILITADA,
        "motivo": "pontuação igual ou superior à nota mínima",
        "consolidado_em": timezone.now(),
        "consolidado_por": "maria",
    }
    campos.update(sobrescrever)
    return ResultadoEtapa.objects.create(**campos)


def test_o_caminho_correto_grava(consolidavel):
    cenario, inscricao, avaliacao = consolidavel
    assert gravar(cenario, inscricao, avaliacao).pk is not None


def test_o_modelo_recusa_atualizacao(consolidavel):
    resultado = gravar(*consolidavel)
    resultado.consequencia = ResultadoEtapa.Consequencia.ELIMINADA
    with pytest.raises(ValueError):
        resultado.save()


def test_o_modelo_recusa_exclusao(consolidavel):
    with pytest.raises(ValueError):
        gravar(*consolidavel).delete()


@SOMENTE_POSTGRES
def test_a_trigger_recusa_update_por_fora_do_orm(consolidavel):
    """A camada do modelo cobre o ORM; esta cobre quem chega por fora dele."""
    resultado = gravar(*consolidavel)
    with (
        pytest.raises(Exception, match="append-only"),
        transaction.atomic(),
        connection.cursor() as cursor,
    ):
        cursor.execute(
            "UPDATE resultados_resultadoetapa SET pontuacao = 0 WHERE id = %s", [str(resultado.id)]
        )


@SOMENTE_POSTGRES
def test_a_trigger_recusa_delete_por_fora_do_orm(consolidavel):
    resultado = gravar(*consolidavel)
    with (
        pytest.raises(Exception, match="append-only"),
        transaction.atomic(),
        connection.cursor() as cursor,
    ):
        cursor.execute("DELETE FROM resultados_resultadoetapa WHERE id = %s", [str(resultado.id)])


@SOMENTE_POSTGRES
def test_inscricao_divergente_da_fonte_e_recusada(consolidavel, gestor):
    cenario, _, avaliacao = consolidavel
    outra = inscrever(cenario["edital"], 1, primeiro=90)[0]
    with pytest.raises(Exception, match="source evaluation"), transaction.atomic():
        gravar(cenario, outra, avaliacao)


@SOMENTE_POSTGRES
def test_etapa_divergente_da_fonte_e_recusada(consolidavel):
    cenario, inscricao, avaliacao = consolidavel
    with pytest.raises(Exception, match="source evaluation"), transaction.atomic():
        gravar(cenario, inscricao, avaliacao, etapa_id=cenario["segunda"])


@SOMENTE_POSTGRES
def test_pontuacao_divergente_da_fonte_e_recusada(consolidavel):
    """O Resultado afirma um número; a trigger exige que seja o número da fonte."""
    cenario, inscricao, avaliacao = consolidavel
    with pytest.raises(Exception, match="source evaluation"), transaction.atomic():
        gravar(cenario, inscricao, avaliacao, pontuacao=Decimal("99.0000"))


@SOMENTE_POSTGRES
def test_avaliacao_em_rascunho_e_recusada(gestor, api_client, manager_headers):
    cenario = montar_etapa_de_leitura_unica(
        gestor, api_client, manager_headers, seed=1301, codigo="1301"
    )
    inscricao = inscrever(cenario["edital"], 1, primeiro=1)[0]
    distribuir_para(cenario, gestor, ["joao"], [inscricao], chave="lote-1301")
    from processo_seletivo.avaliacoes.models import Avaliacao

    atribuicao = Atribuicao.objects.get(inscricao=inscricao, etapa_id=cenario["etapa"], ativo=True)
    rascunho = Avaliacao.objects.create(
        atribuicao=atribuicao,
        identity_subject=atribuicao.membro.identity_subject,
        etapa_id=atribuicao.etapa_id,
        inscricao_id=atribuicao.inscricao_id,
        pontuacao=Decimal("70.0000"),
    )
    with pytest.raises(Exception, match="source evaluation"), transaction.atomic():
        gravar(cenario, inscricao, rascunho, pontuacao=rascunho.pontuacao)


@SOMENTE_POSTGRES
def test_avaliacao_sob_atribuicao_inativa_e_recusada(consolidavel):
    """A sexta divergência, e a que o plano quase deixou passar.

    Elegibilidade é conclusão sob Atribuição ativa. Sem esta linha, a trigger conferiria coerência
    e não elegibilidade — e um Resultado nascido de conclusão já retirada do conjunto ficaria
    consolidado para sempre, porque append-only não corrige, congela.
    """
    cenario, inscricao, avaliacao = consolidavel
    Atribuicao.objects.filter(pk=avaliacao.atribuicao_id).update(
        ativo=False, inativado_em=timezone.now(), inativado_por="maria"
    )
    with pytest.raises(Exception, match="source evaluation"), transaction.atomic():
        gravar(cenario, inscricao, avaliacao)


@SOMENTE_POSTGRES
def test_dois_resultados_para_o_mesmo_par_sao_recusados(consolidavel):
    """A invariante central, dita no banco e não no botão da tela."""
    gravar(*consolidavel)
    cenario, inscricao, avaliacao = consolidavel
    with pytest.raises(IntegrityError), transaction.atomic():
        gravar(cenario, inscricao, avaliacao)


@SOMENTE_POSTGRES
def test_consequencia_invalida_e_recusada_pelo_banco(consolidavel):
    """`TextChoices` valida no formulário; o banco valida sempre.

    `bulk_create`, SQL direto e código futuro não passam pelo `full_clean`, e num registro
    append-only uma consequência inventada entraria uma vez e ficaria — não há caminho que a
    corrija depois. É por isso que a lista fechada precisa ser constraint, e não apenas `choices`.
    """
    cenario, inscricao, avaliacao = consolidavel
    with pytest.raises(IntegrityError), transaction.atomic():
        gravar(cenario, inscricao, avaliacao, consequencia="APROVADA")


@SOMENTE_POSTGRES
def test_consequencia_vazia_e_recusada_pelo_banco(consolidavel):
    cenario, inscricao, avaliacao = consolidavel
    with pytest.raises(IntegrityError), transaction.atomic():
        gravar(cenario, inscricao, avaliacao, consequencia="")
