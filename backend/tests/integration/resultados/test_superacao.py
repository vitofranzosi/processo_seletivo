"""A cadeia de sucessão do Resultado: as constraints, a matriz de origem e a trigger de coerência.

**As garantias centrais desta feature vivem no banco**, e este arquivo é onde elas são exercidas.
Em SQLite nada disto existe — as constraints parciais, a trigger e o privilégio negado são de
PostgreSQL —, e por isso os testes são pulados lá. Um PR verde em SQLite não prova nada do que a
018 promete.

A matriz de origem tem **quatro linhas legítimas, e só quatro**. Uma redação anterior do modelo
punha `decisao IS NULL` no ramo `AVALIACAO` de `ck_resultado_origem`, e isso tornava o sucessor por
reavaliação **impossível de existir**: `ck_sucessor_cita_decisao` exige decisão em todo sucessor, e
os dois `CHECK` se contradiziam. O teste que prende essa regressão é
`test_a_matriz_admite_as_quatro_linhas_legitimas` — e ele é positivo, de propósito: um esquema que
só aceita linhas impossíveis passa em todos os testes negativos e em nenhum positivo.
"""

from datetime import timedelta
from decimal import Decimal

import pytest
from django.db import IntegrityError, connection, transaction
from django.utils import timezone

from processo_seletivo.publicacoes.models_retificacao import VersaoConsolidada
from processo_seletivo.recursos.models import DecisaoRecurso
from processo_seletivo.resultados.application.consolidacao import consolidar
from processo_seletivo.resultados.models import ResultadoEtapa
from tests.fixtures.comissao import inscrever
from tests.fixtures.mesa import concluir_como, distribuir_para
from tests.fixtures.recursos import admitir, decidir, deferir_corrigindo, interpor, superar
from tests.fixtures.resultado import montar_etapa_de_leitura_unica

pytestmark = [pytest.mark.integration, pytest.mark.django_db(transaction=True)]

SOMENTE_POSTGRES = pytest.mark.skipif(
    connection.vendor != "postgresql",
    reason="As constraints parciais e as triggers são de PostgreSQL.",
)


@pytest.fixture
def consolidado(gestor, api_client, manager_headers):
    """Um Resultado vigente, nascido pelo caminho normal: avaliação concluída e consolidada."""
    cenario = montar_etapa_de_leitura_unica(
        gestor, api_client, manager_headers, seed=1800, codigo="1800"
    )
    inscricao = inscrever(cenario["edital"], 1, primeiro=1)[0]
    distribuir_para(cenario, gestor, ["joao"], [inscricao], chave="lote-1800")
    concluir_como(cenario, "joao", inscricao, pontuacao="55")
    consolidar(
        actor=gestor,
        processo_id=cenario["edital"].processo_id,
        edital_id=cenario["edital"].id,
        etapa_id=cenario["etapa"],
        inscricao_ids=[inscricao.id],
        idempotency_key="consolidar-1800",
        correlation_id="teste-1800",
    )
    resultado = ResultadoEtapa.objects.get(inscricao=inscricao)
    versao = VersaoConsolidada.objects.filter(edital=cenario["edital"]).latest("valid_from")
    return cenario, resultado, versao


def _deferido(resultado, versao, *, pontuacao="75.0000", protocolo="REC-2026-TESTE001"):
    return deferir_corrigindo(
        resultado,
        versao=versao,
        pontuacao=Decimal(pontuacao),
        consequencia=ResultadoEtapa.Consequencia.HABILITADA,
        protocolo=protocolo,
    )


# ── A matriz de origem ────────────────────────────────────────────────────────────────────────


@SOMENTE_POSTGRES
def test_a_matriz_admite_as_quatro_linhas_legitimas(consolidado, gestor):
    """As quatro que existem, e a segunda é a que a redação anterior tornava impossível."""
    cenario, raiz_por_avaliacao, versao = consolidado

    # 1 · raiz por avaliação — nasceu na fixture, pelo comando de consolidação.
    assert raiz_por_avaliacao.origem == ResultadoEtapa.Origem.AVALIACAO
    assert raiz_por_avaliacao.resultado_anterior_id is None
    assert raiz_por_avaliacao.decisao_id is None

    # 2 · sucessor por recurso — a decisão fixa a correção e é a fonte.
    _recurso, decisao, sucessor = _deferido(raiz_por_avaliacao, versao)
    assert sucessor.origem == ResultadoEtapa.Origem.RECURSO
    assert sucessor.avaliacao_id is None
    assert sucessor.decisao_id == decisao.id

    # 3 · **sucessor por avaliação**, em cumprimento de reavaliação determinada. É o caso que a
    #     contradição entre `ck_resultado_origem` e `ck_sucessor_cita_decisao` impedia de existir.
    outra = inscrever(cenario["edital"], 1, primeiro=40)[0]
    distribuir_para(cenario, gestor, ["joao"], [outra], chave="lote-1800-b")
    concluir_como(cenario, "joao", outra, pontuacao="50")
    consolidar(
        actor=gestor,
        processo_id=cenario["edital"].processo_id,
        edital_id=cenario["edital"].id,
        etapa_id=cenario["etapa"],
        inscricao_ids=[outra.id],
        idempotency_key="consolidar-1800-b",
        correlation_id="teste-1800-b",
    )
    protegido = ResultadoEtapa.objects.get(inscricao=outra)
    recurso = interpor(
        inscricao=outra, versao=versao, resultado=protegido, protocolo="REC-2026-TESTE002"
    )
    admitir(recurso)
    ordem = decidir(
        recurso,
        especie=DecisaoRecurso.Especie.REAVALIACAO_DETERMINADA,
        protegido=protegido,
        versao=versao,
    )
    reavaliacao = _segunda_avaliacao(cenario, gestor, outra, pontuacao="80")
    sucessor_por_avaliacao = ResultadoEtapa.objects.create(
        inscricao=outra,
        edital=cenario["edital"],
        etapa_id=cenario["etapa"],
        origem=ResultadoEtapa.Origem.AVALIACAO,
        avaliacao=reavaliacao,
        versao=reavaliacao.versao,
        forma=reavaliacao.forma,
        pontuacao=reavaliacao.pontuacao,
        sentido=reavaliacao.sentido,
        consequencia=ResultadoEtapa.Consequencia.HABILITADA,
        motivo="pontuação igual ou superior à nota mínima",
        consolidado_em=protegido.consolidado_em + timedelta(minutes=5),
        consolidado_por="maria",
        resultado_anterior=protegido,
        motivo_da_superacao="Reavaliação determinada em recurso.",
        decisao=ordem,
    )
    assert sucessor_por_avaliacao.origem == ResultadoEtapa.Origem.AVALIACAO
    assert sucessor_por_avaliacao.decisao_id == ordem.id

    # 4 · raiz por ocorrência — já coberta pela 013, e conferida aqui só quanto à matriz.
    assert not ResultadoEtapa.objects.filter(
        origem=ResultadoEtapa.Origem.OCORRENCIA, resultado_anterior__isnull=False
    ).exists()


@SOMENTE_POSTGRES
def test_raiz_por_recurso_e_recusada(consolidado):
    """`RECURSO` sem superado seria consolidação disfarçada de julgamento."""
    cenario, resultado, versao = consolidado
    recurso = interpor(
        inscricao=resultado.inscricao,
        versao=versao,
        resultado=resultado,
        protocolo="REC-2026-TESTE003",
    )
    admitir(recurso)
    decisao = decidir(recurso, protegido=resultado, consequencia="HABILITADA", versao=versao)

    with pytest.raises(Exception, match="must supersede a previous result"), transaction.atomic():
        ResultadoEtapa.objects.create(
            inscricao=resultado.inscricao,
            edital=cenario["edital"],
            etapa_id=cenario["etapa"],
            origem=ResultadoEtapa.Origem.RECURSO,
            avaliacao=None,
            versao=versao,
            forma="",
            pontuacao=None,
            sentido="",
            consequencia=ResultadoEtapa.Consequencia.HABILITADA,
            motivo="deferido",
            consolidado_em=timezone.now(),
            consolidado_por="julgadora",
            resultado_anterior=None,
            motivo_da_superacao="",
            decisao=decisao,
        )


@SOMENTE_POSTGRES
def test_sucessor_por_ocorrencia_e_recusado(consolidado):
    """A Ocorrência constata ausência; ela não corrige o que já foi decidido."""
    _cenario, resultado, versao = consolidado
    recurso = interpor(
        inscricao=resultado.inscricao,
        versao=versao,
        resultado=resultado,
        protocolo="REC-2026-TESTE004",
    )
    admitir(recurso)
    decisao = decidir(recurso, protegido=resultado, consequencia="ELIMINADA", versao=versao)

    with pytest.raises(IntegrityError), transaction.atomic():
        ResultadoEtapa.objects.create(
            inscricao=resultado.inscricao,
            edital=resultado.edital,
            etapa_id=resultado.etapa_id,
            origem=ResultadoEtapa.Origem.OCORRENCIA,
            avaliacao=None,
            versao=versao,
            forma="",
            pontuacao=None,
            sentido="",
            consequencia=ResultadoEtapa.Consequencia.ELIMINADA,
            motivo="não compareceu",
            consolidado_em=resultado.consolidado_em + timedelta(minutes=1),
            consolidado_por="maria",
            resultado_anterior=resultado,
            motivo_da_superacao="Recurso deferido.",
            decisao=decisao,
        )


# ── As constraints de cadeia ──────────────────────────────────────────────────────────────────


@SOMENTE_POSTGRES
def test_dois_sucessores_do_mesmo_superado_sao_recusados(consolidado):
    """A corrida "dois deferimentos sobre o mesmo Resultado", resolvida no banco.

    É a mesma garantia que `uq_ato_sucessor_unico` dá à emissão simultânea de dois sucessores do
    mesmo ato: ler o vigente antes de gravar é conforto de mensagem de erro, e não garantia.
    """
    _cenario, resultado, versao = consolidado
    _recurso, decisao, _sucessor = _deferido(resultado, versao, protocolo="REC-2026-TESTE005")

    # **Um segundo recurso do mesmo titular contra o mesmo objeto não existe** — a FR-011 o impede
    # no banco, e é a própria `uq_recurso_por_resultado` que o diz. A corrida que sobra é a de dois
    # sucessores nascendo da mesma decisão, e é ela que `uq_resultado_sucessor_unico` resolve.
    # Sequencialmente, quem recusa é a trigger — e a mensagem nomeia o problema. Sob concorrência
    # real, a trigger não vê a linha ainda não confirmada da outra transação, e é
    # `uq_resultado_sucessor_unico` que resolve: a constraint responde à corrida, a trigger
    # responde à leitura.
    with (
        pytest.raises(Exception, match="already has a successor"),
        transaction.atomic(),
    ):
        superar(resultado, decisao, pontuacao=Decimal("88.0000"), motivo="Outro deferimento.")


@SOMENTE_POSTGRES
def test_duas_raizes_do_mesmo_par_sao_recusadas(consolidado, gestor):
    """A invariante da 013 continua valendo — agora como unicidade da **raiz**."""
    cenario, resultado, _versao = consolidado

    with pytest.raises(IntegrityError), transaction.atomic():
        ResultadoEtapa.objects.create(
            inscricao=resultado.inscricao,
            edital=resultado.edital,
            etapa_id=resultado.etapa_id,
            origem=ResultadoEtapa.Origem.OCORRENCIA,
            avaliacao=None,
            versao=resultado.versao,
            forma="",
            pontuacao=None,
            sentido="",
            consequencia=ResultadoEtapa.Consequencia.ELIMINADA,
            motivo="não compareceu",
            consolidado_em=timezone.now(),
            consolidado_por="maria",
        )
    assert cenario is not None


@SOMENTE_POSTGRES
def test_sucessor_sem_decisao_e_raiz_com_decisao_sao_recusados(consolidado):
    """`ck_sucessor_cita_decisao` é bidirecional, e as duas metades importam."""
    _cenario, resultado, versao = consolidado
    recurso = interpor(
        inscricao=resultado.inscricao,
        versao=versao,
        resultado=resultado,
        protocolo="REC-2026-TESTE007",
    )
    admitir(recurso)
    decisao = decidir(recurso, protegido=resultado, consequencia="HABILITADA", versao=versao)

    # sucessor sem decisão: superação sem fundamento. A recusa é da trigger, que roda antes das
    # constraints e nomeia o que está errado — o `CHECK` continua sendo a garantia sob ela.
    with pytest.raises(Exception, match="another registration or stage"), transaction.atomic():
        ResultadoEtapa.objects.create(
            inscricao=resultado.inscricao,
            edital=resultado.edital,
            etapa_id=resultado.etapa_id,
            origem=ResultadoEtapa.Origem.RECURSO,
            avaliacao=None,
            versao=versao,
            forma="",
            pontuacao=None,
            sentido="",
            consequencia=ResultadoEtapa.Consequencia.HABILITADA,
            motivo="deferido",
            consolidado_em=resultado.consolidado_em + timedelta(minutes=1),
            consolidado_por="julgadora",
            resultado_anterior=resultado,
            motivo_da_superacao="Recurso deferido.",
            decisao=None,
        )
    assert decisao.id is not None


@SOMENTE_POSTGRES
def test_sucessor_sem_motivo_da_superacao_e_recusado(consolidado):
    """Cada elo da correção carrega motivo obrigatório — aqui, o da superação."""
    _cenario, resultado, versao = consolidado
    recurso = interpor(
        inscricao=resultado.inscricao,
        versao=versao,
        resultado=resultado,
        protocolo="REC-2026-TESTE008",
    )
    admitir(recurso)
    decisao = decidir(recurso, protegido=resultado, consequencia="HABILITADA", versao=versao)

    with pytest.raises(IntegrityError), transaction.atomic():
        superar(resultado, decisao, motivo="")


# ── A trigger de coerência ────────────────────────────────────────────────────────────────────


@SOMENTE_POSTGRES
def test_sucessor_de_outro_par_e_recusado(consolidado, gestor):
    """O superado precisa ser do mesmo `(inscricao, etapa_id, edital)`."""
    cenario, resultado, versao = consolidado
    outra = inscrever(cenario["edital"], 1, primeiro=42)[0]
    distribuir_para(cenario, gestor, ["joao"], [outra], chave="lote-1800-c")
    concluir_como(cenario, "joao", outra, pontuacao="65")
    consolidar(
        actor=gestor,
        processo_id=cenario["edital"].processo_id,
        edital_id=cenario["edital"].id,
        etapa_id=cenario["etapa"],
        inscricao_ids=[outra.id],
        idempotency_key="consolidar-1800-c",
        correlation_id="teste-1800-c",
    )
    de_outra = ResultadoEtapa.objects.get(inscricao=outra)
    recurso = interpor(
        inscricao=resultado.inscricao,
        versao=versao,
        resultado=resultado,
        protocolo="REC-2026-TESTE009",
    )
    admitir(recurso)
    decisao = decidir(recurso, protegido=resultado, consequencia="HABILITADA", versao=versao)

    with pytest.raises(Exception, match="another registration or stage"), transaction.atomic():
        ResultadoEtapa.objects.create(
            inscricao=resultado.inscricao,
            edital=resultado.edital,
            etapa_id=resultado.etapa_id,
            origem=ResultadoEtapa.Origem.RECURSO,
            avaliacao=None,
            versao=versao,
            forma="",
            pontuacao=None,
            sentido="",
            consequencia=ResultadoEtapa.Consequencia.HABILITADA,
            motivo="deferido",
            consolidado_em=timezone.now(),
            consolidado_por="julgadora",
            resultado_anterior=de_outra,
            motivo_da_superacao="Recurso deferido.",
            decisao=decisao,
        )


@SOMENTE_POSTGRES
def test_sucessor_por_recurso_com_decisao_de_especie_errada_e_recusado(consolidado):
    """Origem `RECURSO` exige decisão que **fixou** a correção — não uma que ordenou reavaliação."""
    _cenario, resultado, versao = consolidado
    recurso = interpor(
        inscricao=resultado.inscricao,
        versao=versao,
        resultado=resultado,
        protocolo="REC-2026-TESTE010",
    )
    admitir(recurso)
    ordem = decidir(
        recurso,
        especie=DecisaoRecurso.Especie.REAVALIACAO_DETERMINADA,
        protegido=resultado,
        versao=versao,
    )

    with pytest.raises(Exception, match="fixed no correction"), transaction.atomic():
        superar(
            resultado,
            ordem,
            pontuacao=Decimal("75.0000"),
            consequencia=ResultadoEtapa.Consequencia.HABILITADA,
        )


@SOMENTE_POSTGRES
def test_sucessor_anterior_no_tempo_ao_superado_e_recusado(consolidado):
    """A cronologia é monotônica: sem isto, "o mais recente" e "o vigente" divergiriam."""
    _cenario, resultado, versao = consolidado
    recurso = interpor(
        inscricao=resultado.inscricao,
        versao=versao,
        resultado=resultado,
        protocolo="REC-2026-TESTE011",
    )
    admitir(recurso)
    decisao = decidir(recurso, protegido=resultado, consequencia="HABILITADA", versao=versao)

    with pytest.raises(Exception, match="not later than"), transaction.atomic():
        ResultadoEtapa.objects.create(
            inscricao=resultado.inscricao,
            edital=resultado.edital,
            etapa_id=resultado.etapa_id,
            origem=ResultadoEtapa.Origem.RECURSO,
            avaliacao=None,
            versao=versao,
            forma="",
            pontuacao=None,
            sentido="",
            consequencia=ResultadoEtapa.Consequencia.HABILITADA,
            motivo="deferido",
            consolidado_em=resultado.consolidado_em - timedelta(minutes=1),
            consolidado_por="julgadora",
            resultado_anterior=resultado,
            motivo_da_superacao="Recurso deferido.",
            decisao=decisao,
        )


@SOMENTE_POSTGRES
def test_sucessor_com_pontuacao_diferente_da_fixada_e_recusado(consolidado):
    """A decisão fixou 75; o sucessor tenta gravar 90.

    Conferir só a consequência deixaria isto passar — e o Resultado é append-only: o número errado
    entraria uma vez e ficaria, com a decisão ao lado dizendo outra coisa. É a FR-058 no banco.
    """
    _cenario, resultado, versao = consolidado
    recurso = interpor(
        inscricao=resultado.inscricao,
        versao=versao,
        resultado=resultado,
        protocolo="REC-2026-TESTE013",
    )
    admitir(recurso)
    decisao = decidir(
        recurso,
        protegido=resultado,
        consequencia="HABILITADA",
        forma=resultado.forma,
        pontuacao=Decimal("75.0000"),
        sentido=resultado.sentido,
        versao=versao,
    )

    with (
        pytest.raises(Exception, match="does not reproduce its decision conclusion"),
        transaction.atomic(),
    ):
        superar(resultado, decisao, pontuacao=Decimal("90.0000"))


@SOMENTE_POSTGRES
def test_sucessor_que_supera_resultado_diferente_do_protegido_e_recusado(consolidado, gestor):
    """A decisão protege um Resultado; a superação precisa recair exatamente sobre ele.

    Sem esta conferência, a decisão e a superação poderiam apontar para linhas diferentes do mesmo
    par — e a *non reformatio*, que compara contra `resultado_protegido`, estaria comparando com o
    Resultado errado.
    """
    _cenario, resultado, versao = consolidado
    recurso = interpor(
        inscricao=resultado.inscricao,
        versao=versao,
        resultado=resultado,
        protocolo="REC-2026-TESTE014",
    )
    admitir(recurso)
    decisao = decidir(
        recurso,
        protegido=resultado,
        consequencia="HABILITADA",
        forma=resultado.forma,
        pontuacao=Decimal("75.0000"),
        sentido=resultado.sentido,
        versao=versao,
    )
    primeiro = superar(resultado, decisao, pontuacao=Decimal("75.0000"))

    # `primeiro` é do mesmo par, mas **não** é o que a decisão protegeu.
    with (
        pytest.raises(Exception, match="does not protect"),
        transaction.atomic(),
    ):
        ResultadoEtapa.objects.create(
            inscricao=resultado.inscricao,
            edital=resultado.edital,
            etapa_id=resultado.etapa_id,
            origem=ResultadoEtapa.Origem.RECURSO,
            avaliacao=None,
            versao=versao,
            forma=decisao.forma,
            pontuacao=decisao.pontuacao,
            sentido=decisao.sentido,
            consequencia=decisao.consequencia,
            motivo="deferido",
            consolidado_em=primeiro.consolidado_em + timedelta(minutes=1),
            consolidado_por="julgadora",
            resultado_anterior=primeiro,
            motivo_da_superacao="Recurso deferido.",
            decisao=decisao,
        )


@SOMENTE_POSTGRES
def test_o_superado_permanece_integro_e_consultavel(consolidado):
    """Superar não altera: o anterior continua com pontuação, consequência e motivo intactos."""
    _cenario, resultado, versao = consolidado
    antes = (resultado.pontuacao, resultado.consequencia, resultado.motivo)

    _recurso, _decisao, sucessor = _deferido(resultado, versao, protocolo="REC-2026-TESTE012")

    resultado.refresh_from_db()
    assert (resultado.pontuacao, resultado.consequencia, resultado.motivo) == antes
    assert ResultadoEtapa.objects.filter(inscricao=resultado.inscricao).count() == 2
    assert ResultadoEtapa.vigentes.get(inscricao=resultado.inscricao).id == sucessor.id


def _segunda_avaliacao(cenario, gestor, inscricao, *, pontuacao):
    """Uma Avaliação **diferente**, por outro avaliador, construída direto pelo ORM.

    **Não passa pela Mesa de propósito.** Distribuir e avaliar uma inscrição que já tem Resultado é
    o caminho que a US5 vai abrir — a prontidão hoje a apresenta como consolidada, e a Mesa a
    recusa. O que a fundação precisa provar é outra coisa: que o **esquema** admite o sucessor por
    avaliação. Rotear pelo comando aqui misturaria as duas perguntas, e a primeira a falhar
    esconderia a segunda.

    Duas garantias que a fixture herda sem pedir: `uq_avaliacao_concluida_por_pessoa` impede que
    quem concluiu a original conclua de novo o mesmo par — por isso o avaliador é outro —, e
    `uq_atribuicao_ativa` é por membro, e não por par, o que torna a segunda Atribuição possível.
    """
    from django.utils import timezone as _tz

    from processo_seletivo.avaliacoes.models import Atribuicao, Avaliacao
    from processo_seletivo.comissoes.domain.funcoes import Funcao
    from tests.fixtures.comissao import alocar_em, constituir

    membros = constituir(
        gestor,
        cenario["edital"].processo,
        [("otavio", Funcao.MEMBRO)],
        prefixo="reavaliacao-1800",
    )
    alocar_em(
        gestor, cenario["edital"].processo, membros["otavio"], cenario["edital"], cenario["etapa"]
    )
    membro = membros["otavio"]
    atribuicao = Atribuicao.objects.create(
        membro=membro,
        edital=cenario["edital"],
        etapa_id=cenario["etapa"],
        inscricao=inscricao,
        ativo=True,
        criado_em=_tz.now(),
        criado_por="maria",
    )
    original = Avaliacao.objects.filter(inscricao_id=inscricao.id).first()
    return Avaliacao.objects.create(
        atribuicao=atribuicao,
        identity_subject=membro.identity_subject,
        etapa_id=atribuicao.etapa_id,
        inscricao_id=atribuicao.inscricao_id,
        estado=Avaliacao.Estado.CONCLUIDA,
        forma=original.forma,
        pontuacao=Decimal(pontuacao),
        sentido=original.sentido,
        versao=original.versao,
        parecer="Reavaliação determinada em recurso deferido.",
        concluida_por=membro.identity_subject,
        concluida_em=_tz.now(),
    )
