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
from django.db import DatabaseError, IntegrityError, connection, transaction
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
        "origem": ResultadoEtapa.Origem.AVALIACAO,
        "avaliacao": avaliacao,
        # A versão **da fonte**: a trigger recusa qualquer outra desde D-1.
        "versao_id": avaliacao.versao_id,
        "forma": avaliacao.forma,
        "pontuacao": avaliacao.pontuacao,
        "sentido": avaliacao.sentido,
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


# ------------------------- a coerência por forma, no banco (013, D-008, FR-049)


@pytest.fixture
def decisoria_consolidavel(gestor, api_client, manager_headers):
    cenario = montar_etapa_de_leitura_unica(
        gestor, api_client, manager_headers, seed=2500, codigo="2500", decisoria=True
    )
    inscricao = inscrever(cenario["edital"], 1, primeiro=1)[0]
    distribuir_para(cenario, gestor, ["joao"], [inscricao], chave="lote-2500")
    avaliacao = concluir_como(
        cenario, "joao", inscricao, sentido="DESFAVORAVEL", parecer="Faltou o diploma."
    )
    return cenario, inscricao, avaliacao


def test_o_resultado_decisorio_com_pontuacao_e_recusado(decisoria_consolidavel):
    """As **duas** camadas recusam, e a trigger chega primeiro.

    `ck_resultado_completo_por_forma` é defesa em profundidade: `BEFORE INSERT` roda antes de a
    constraint ser avaliada, de modo que um Resultado incoerente com a fonte nunca chega até ela. A
    constraint existe para o caso que a trigger não cobre — uma fonte que já estivesse errada —, e
    esse caso a constraint da própria Avaliação impede antes. Duas garantias, e nenhuma sozinha.
    """
    cenario, inscricao, avaliacao = decisoria_consolidavel

    with pytest.raises(DatabaseError):
        gravar(cenario, inscricao, avaliacao, pontuacao=Decimal("80.0000"))


def test_a_trigger_recusa_resultado_com_sentido_diferente_do_da_fonte(decisoria_consolidavel):
    """**O caso que motivou a decisão de comparar os três campos incondicionalmente.**

    Uma conferência que alternasse por forma nem olharia o sentido quando as pontuações fossem
    ambas nulas — e `IS DISTINCT FROM` resolve nulo contra nulo como igualdade. O Resultado sairia
    afirmando o contrário do que a Avaliação fonte afirmou, em silêncio.
    """
    cenario, inscricao, avaliacao = decisoria_consolidavel

    with pytest.raises(DatabaseError, match="does not match its source evaluation"):
        gravar(cenario, inscricao, avaliacao, sentido="FAVORAVEL")


def test_a_trigger_recusa_resultado_com_forma_diferente_da_fonte(decisoria_consolidavel):
    cenario, inscricao, avaliacao = decisoria_consolidavel

    with pytest.raises(DatabaseError, match="does not match its source evaluation"):
        gravar(cenario, inscricao, avaliacao, forma="PONTUADA", sentido="", pontuacao=None)


# ------------------------- as duas origens, por SQL cru (D-1)
#
# **Por fora do ORM de propósito.** Os testes acima chegam ao banco pelo modelo, e o modelo já
# recusa muita coisa antes — o que eles provam sobre a trigger é o que sobra. Aqui o `INSERT` é
# escrito à mão, com a lista de colunas explícita, porque é assim que chega quem tem o cliente do
# banco na mão: sem `save()`, sem `full_clean`, sem constraint de aplicação. É o único jeito de
# provar que o terceiro ramo e a nulabilidade nova não são promessa de código.


COLUNAS = (
    "id, inscricao_id, edital_id, etapa_id, origem, avaliacao_id, versao_id, forma, pontuacao, "
    "sentido, consequencia, motivo, consolidado_em, consolidado_por"
)


def inserir_cru(cenario, inscricao, **campos):
    """Um `INSERT` escrito à mão, com os valores que o chamador quiser — inclusive impossíveis."""
    import uuid

    from processo_seletivo.publicacoes.models_retificacao import VersaoConsolidada

    versao = VersaoConsolidada.objects.filter(edital=cenario["edital"]).latest("valid_from")
    linha = {
        "id": str(uuid.uuid4()),
        "inscricao_id": str(inscricao.id),
        "edital_id": str(cenario["edital"].id),
        "etapa_id": str(cenario["etapa"]),
        "origem": "OCORRENCIA",
        "avaliacao_id": None,
        "versao_id": str(versao.id),
        "forma": "",
        "pontuacao": None,
        "sentido": "",
        "consequencia": "ELIMINADA",
        "motivo": "não compareceu",
        "consolidado_em": timezone.now(),
        "consolidado_por": "maria",
    }
    linha.update(campos)
    with connection.cursor() as cursor:
        cursor.execute(
            f"INSERT INTO resultados_resultadoetapa ({COLUNAS}) VALUES "
            "(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
            [linha[nome.strip()] for nome in COLUNAS.split(",")],
        )
    return linha["id"]


@SOMENTE_POSTGRES
def test_o_ramo_por_ocorrencia_grava_por_sql_cru(consolidavel):
    """O caminho correto do terceiro ramo: sem Avaliação, sem forma, sem pontuação, sem sentido."""
    cenario, _, _ = consolidavel
    outra = inscrever(cenario["edital"], 1, primeiro=70)[0]
    assert inserir_cru(cenario, outra)
    assert ResultadoEtapa.objects.filter(inscricao=outra).exists()


@SOMENTE_POSTGRES
def test_a_ocorrencia_que_cita_avaliacao_e_recusada_pela_trigger(consolidavel):
    """Constatação e conclusão são coisas diferentes, e a linha não pode afirmar as duas."""
    cenario, inscricao, avaliacao = consolidavel
    with (
        pytest.raises(DatabaseError, match="must not cite a source evaluation"),
        transaction.atomic(),
    ):
        inserir_cru(cenario, inscricao, avaliacao_id=str(avaliacao.id))


@SOMENTE_POSTGRES
def test_a_ocorrencia_que_cita_versao_de_outro_edital_e_recusada(
    consolidavel, gestor, api_client, manager_headers
):
    """A única conferência que sobra no ramo sem fonte — e sem ela a proveniência seria promessa.

    A versão citada pelo Resultado por Ocorrência não vem copiada de lugar nenhum: quem escreve a
    linha a escolhe. Se ela pudesse ser de outro Edital, o Resultado afirmaria ter sido fundamentado
    por norma que nunca governou este certame, e I-2 seria letra morta neste ramo.
    """
    from processo_seletivo.publicacoes.models_retificacao import VersaoConsolidada

    cenario, inscricao, _ = consolidavel
    alheio = montar_etapa_de_leitura_unica(
        gestor, api_client, manager_headers, seed=1302, codigo="1302"
    )
    de_fora = VersaoConsolidada.objects.filter(edital=alheio["edital"]).latest("valid_from")
    with (
        pytest.raises(DatabaseError, match="version of another edital"),
        transaction.atomic(),
    ):
        inserir_cru(cenario, inscricao, versao_id=str(de_fora.id))


@SOMENTE_POSTGRES
def test_a_ocorrencia_com_pontuacao_e_recusada_pela_constraint(consolidavel):
    """O terceiro ramo é feito de ausências, e a constraint cobra as três.

    A trigger aprovaria esta linha — ela não cita Avaliação e a versão é deste Edital —, e é
    exatamente por isso que as duas camadas precisam existir: a trigger confere contra a fonte, e
    a constraint confere que a linha é internamente coerente.
    """
    cenario, inscricao, _ = consolidavel
    with pytest.raises(IntegrityError), transaction.atomic():
        inserir_cru(cenario, inscricao, pontuacao=Decimal("80.0000"))


@SOMENTE_POSTGRES
def test_a_ocorrencia_com_sentido_e_recusada_pela_constraint(consolidavel):
    cenario, inscricao, _ = consolidavel
    with pytest.raises(IntegrityError), transaction.atomic():
        inserir_cru(cenario, inscricao, sentido="DESFAVORAVEL")


@SOMENTE_POSTGRES
def test_a_ocorrencia_com_forma_e_recusada_pela_constraint(consolidavel):
    """Carimbar `DECISORIA` numa ausência diria que alguém avaliou quem não compareceu."""
    cenario, inscricao, _ = consolidavel
    with pytest.raises(IntegrityError), transaction.atomic():
        inserir_cru(cenario, inscricao, forma="DECISORIA", sentido="DESFAVORAVEL")


@SOMENTE_POSTGRES
def test_o_resultado_por_avaliacao_sem_fonte_e_recusado(consolidavel):
    """A metade que `null=True` sozinho abriria: uma linha sem fonte **e** sem constatação.

    Quem recusa é a **trigger**, e não a constraint: `BEFORE INSERT` roda antes de o `CHECK` ser
    avaliado, e a linha nem chega até `ck_resultado_origem`. As duas cobrem o caso, e é bom que
    cubram — a constraint sobrevive a uma trigger derrubada por engano numa manutenção, e é ela
    que fecha o caso oposto, que a trigger aprovaria (o teste da forma na Ocorrência, acima).
    """
    cenario, inscricao, _ = consolidavel
    with (
        pytest.raises(DatabaseError, match="does not match its source evaluation"),
        transaction.atomic(),
    ):
        inserir_cru(cenario, inscricao, origem="AVALIACAO", forma="PONTUADA", pontuacao=None)


@SOMENTE_POSTGRES
def test_o_ramo_por_avaliacao_confere_a_versao_da_fonte(
    consolidavel, gestor, api_client, manager_headers
):
    """A versão do Resultado é a **da Avaliação**, e a trigger não aceita outra.

    Sem esta conferência, materializar a norma no Resultado abriria justamente a contradição que o
    argumento original contra materializá-la previa: duas respostas para "sob qual regra isto foi
    decidido".
    """
    from processo_seletivo.publicacoes.models_retificacao import VersaoConsolidada

    cenario, inscricao, avaliacao = consolidavel
    alheio = montar_etapa_de_leitura_unica(
        gestor, api_client, manager_headers, seed=1303, codigo="1303"
    )
    outra = VersaoConsolidada.objects.filter(edital=alheio["edital"]).latest("valid_from")
    with (
        pytest.raises(DatabaseError, match="does not match its source evaluation"),
        transaction.atomic(),
    ):
        gravar(cenario, inscricao, avaliacao, versao_id=str(outra.id))
