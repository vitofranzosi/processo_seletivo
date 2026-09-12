"""Os cinco sinais: cada um nasce da sua condição, e some quando ela se desfaz.

A contraprova é metade de cada teste. Um sinal que aparece e nunca some é indistinguível de uma
seção fixa, e é exatamente o que `D-001` recusa.
"""

from datetime import timedelta

import pytest
from django.utils import timezone

from processo_seletivo.interface import supervisao
from tests.conftest import ator_institucional
from tests.fixtures.supervisao import (
    SEGUNDO_SEED,
    etapa_ligada,
    evento_do_periodo,
    evento_simples,
    publicar_no_processo,
    rascunho_com_periodo,
    submeter,
)

pytestmark = [pytest.mark.django_db, pytest.mark.integration]


@pytest.fixture
def presidenta():
    """Quem preside — e, para os sinais, também quem alcança as telas donas."""
    return ator_institucional("maria", "recurso:julgar")


def das_especies(sinais, especie):
    return [sinal for sinal in sinais if sinal.especie == especie]


# ---------------------------------------------------------------------------
# `UX-001` — Etapa sem marco no cronograma
# ---------------------------------------------------------------------------


def test_etapa_sem_evento_vinculado_produz_o_sinal(
    processo_a, edital_a, edital_c, comissao_de_a, presidenta
):
    """`FR-026` e `SC-008`: dito **nesses termos**, e nunca como atraso ou progresso zero.

    A Etapa sem referência a Evento é publicável e legítima — a validação recusa referência a
    Evento inexistente, e **admite ausência de referência**. Transformá-la em impeditivo mudaria o
    que o sistema aceita publicar, o que é decisão normativa e não cabe a um painel.
    """
    achados = das_especies(supervisao.sinais(processo_a, presidenta), supervisao.UX_001)

    # A Etapa `Prova didática` do Edital A não declara `scheduleEventId`; a `Análise documental`
    # declara, e não produz sinal.
    assert [sinal.alvo for sinal in achados] == ["Prova didática"]
    unico = achados[0]
    assert unico.edital.id == edital_a.id
    assert "sem marco no cronograma" in unico.mensagem
    for proibido in ("atrasad", "aguardando", "progresso", "0 %", "0%"):
        assert proibido not in unico.mensagem.lower()
    assert unico.medida is None


def test_etapa_com_evento_vinculado_nao_produz_o_sinal(
    processo_a, edital_a, edital_c, comissao_de_a, presidenta
):
    """A contraprova: o Edital C tem uma Etapa só, e ela aponta o Evento do período."""
    achados = das_especies(supervisao.sinais(processo_a, presidenta), supervisao.UX_001)

    assert edital_c.id not in {sinal.edital.id for sinal in achados}


# ---------------------------------------------------------------------------
# `UX-002` — declarado × posição temporal (a tabela-verdade de `T-005`)
# ---------------------------------------------------------------------------

# As três posições, em ids distintos por combinação. Combinação omitida é a que ninguém testa.
COMBINACOES = [
    ("PLANEJADO", "antes", False, 411),
    ("PLANEJADO", "dentro", True, 412),
    ("PLANEJADO", "depois", True, 413),
    ("EM_ANDAMENTO", "antes", True, 414),
    ("EM_ANDAMENTO", "dentro", False, 415),
    ("EM_ANDAMENTO", "depois", True, 416),
    ("CONCLUIDO", "antes", True, 417),
    ("CONCLUIDO", "dentro", True, 418),
    ("CONCLUIDO", "depois", False, 419),
    ("CANCELADO", "depois", False, 420),
]
SEM_TERMINO = 421


def _janela(agora, posicao):
    if posicao == "antes":
        return agora + timedelta(days=10), agora + timedelta(days=11)
    if posicao == "dentro":
        return agora - timedelta(days=1), agora + timedelta(days=1)
    return agora - timedelta(days=11), agora - timedelta(days=10)


@pytest.fixture
def edital_da_tabela_verdade(api_client, manager_headers, processo_a):
    """Um Edital cujo cronograma percorre a tabela-verdade inteira de `T-005`."""
    agora = timezone.now()
    eventos = [
        evento_do_periodo(
            7,
            inicio=agora - timedelta(days=2),
            fim=agora + timedelta(days=2),
            status="EM_ANDAMENTO",
        )
    ]
    for ordem, (declarado, posicao, _, base) in enumerate(COMBINACOES, start=2):
        inicio, fim = _janela(agora, posicao)
        eventos.append(
            evento_simples(
                7,
                base=base,
                descricao=f"{declarado} {posicao}",
                inicio=inicio,
                fim=fim,
                ordem=ordem,
                status=declarado,
            )
        )
    # Sem término declarado: marco instantâneo, forma normal do dado, e por isso nunca divergente.
    eventos.append(
        evento_simples(
            7,
            base=SEM_TERMINO,
            descricao="EM_ANDAMENTO sem término",
            inicio=agora - timedelta(days=3),
            ordem=len(COMBINACOES) + 2,
            status="EM_ANDAMENTO",
        )
    )
    return publicar_no_processo(
        api_client,
        manager_headers,
        processo_a,
        number="07",
        title="Tabela-verdade",
        chave="supervisao-tabela-verdade",
        draft=rascunho_com_periodo(7, eventos=eventos, etapas=[etapa_ligada(7)]),
    )


def test_a_tabela_verdade_inteira_de_ux_002(
    processo_a, edital_a, comissao_de_a, presidenta, edital_da_tabela_verdade
):
    """`FR-027` e `SC-009`: as seis que produzem sinal, as três coerentes e as duas exclusões.

    Nem o `status` nem a posição é corrigido: os dois são apresentados, e a tela não afirma qual
    deles vale.
    """
    achados = das_especies(supervisao.sinais(processo_a, presidenta), supervisao.UX_002)

    divergentes = {
        sinal.alvo for sinal in achados if sinal.edital.id == edital_da_tabela_verdade.id
    }
    esperados = {f"{d} {p}" for d, p, produz, _ in COMBINACOES if produz}
    assert divergentes == esperados
    assert "EM_ANDAMENTO sem término" not in divergentes


def test_ux_002_apresenta_as_duas_informacoes_sem_arbitrar(
    processo_a, edital_a, comissao_de_a, presidenta, edital_da_tabela_verdade
):
    """`UX-002`: na forma *declarado X · prazo encerrado em D*."""
    achados = das_especies(supervisao.sinais(processo_a, presidenta), supervisao.UX_002)

    encerrado = next(sinal for sinal in achados if sinal.alvo == "PLANEJADO depois")
    assert "declarado planejado" in encerrado.mensagem
    assert "prazo encerrado em" in encerrado.mensagem


# ---------------------------------------------------------------------------
# `UX-003` — cobertura de avaliação insuficiente
# ---------------------------------------------------------------------------


def test_inscricao_sem_avaliador_e_carente_e_permanece_no_denominador(
    processo_a, edital_a, edital_c, comissao_de_a, presidenta
):
    """`FR-028`, `FR-032` e `FR-033`: numerador e denominador, e a unidade sem ninguém nos dois.

    Retirar do denominador quem não recebeu avaliador nenhum faria a cobertura parecer completa
    justamente onde ela não começou (`SC-006`).
    """
    submeter(edital_c, 4, seed=SEGUNDO_SEED)

    achados = das_especies(supervisao.sinais(processo_a, presidenta), supervisao.UX_003)

    do_c = next(sinal for sinal in achados if sinal.edital.id == edital_c.id)
    assert do_c.medida == supervisao.Medida(numerador=4, denominador=4)
    assert do_c.alvo == "Análise documental"
    assert f"{edital_c.number}/{edital_c.year}" in do_c.mensagem


def test_sem_inscricao_submetida_nao_ha_cobertura_a_cobrar(
    processo_a, edital_a, edital_c, comissao_de_a, presidenta
):
    """A contraprova: zero carentes sobre zero inscrições não é pendência, é ausência."""
    achados = das_especies(supervisao.sinais(processo_a, presidenta), supervisao.UX_003)

    assert achados == []


# ---------------------------------------------------------------------------
# `UX-004` — ato de ordenação vigente obsoleto
# ---------------------------------------------------------------------------


@pytest.fixture
def peca(gestor, api_client, manager_headers, process_payload):
    """O cenário da `018`: marco emitido e divulgado, com um recurso admitido e sem decisão."""
    from tests.fixtures.recursos_us4 import cenario_julgavel

    return cenario_julgavel(
        gestor, api_client, manager_headers, process_payload, seed=122, codigo="0221"
    )


def deferir(peca):
    """O deferimento que reabilita quem estava fora — a divergência mais consequente das três."""
    from decimal import Decimal

    from processo_seletivo.recursos.application.julgar import julgar
    from processo_seletivo.recursos.models import DecisaoRecurso
    from tests.fixtures.recursos_us4 import julgador

    return julgar(
        actor=julgador(),
        recurso_id=peca["recurso"].id,
        especie=DecisaoRecurso.Especie.CORRECAO_FIXADA,
        motivacao="A prova didática entregue não foi considerada.",
        etapa_id=peca["cenario"]["etapa"],
        pontuacao=Decimal("82.0000"),
        assinatura_do_resultado=str(peca["superado"].id),
        idempotency_key="deferir-na-supervisao",
    )


@pytest.mark.django_db(transaction=True)
def test_o_ato_obsoleto_aparece_sem_que_seja_preciso_abrir_o_marco(peca, presidenta):
    """`FR-029`: a obsolescência só se descobria abrindo o marco, um a um.

    O sinal nasce da **confirmação**, e não do filtro: o filtro barato apenas escolhe quem vale a
    pena confirmar.
    """
    processo = peca["cenario"]["processo"]
    antes = das_especies(supervisao.sinais(processo, presidenta), supervisao.UX_004)
    assert antes == [], "o cenário não pode nascer obsoleto — senão o teste abaixo não prova nada"

    deferir(peca)

    achados = das_especies(supervisao.sinais(processo, presidenta), supervisao.UX_004)
    assert len(achados) == 1
    assert achados[0].alvo == "Classificação final"
    assert achados[0].edital.id == peca["cenario"]["edital"].id


@pytest.mark.django_db(transaction=True)
def test_fato_posterior_que_nao_altera_o_universo_do_marco_nao_produz_sinal(
    peca, presidenta, api_client
):
    """`T-003`: o filtro é conservador, e é a confirmação que decide.

    Uma Retificação alheia ao recorte do marco faz o ato citar uma versão que já não vige — o
    filtro barato o admite como candidato —, e a comparação exata não encontra divergência
    nenhuma. Exibir o candidato como sinal produziria alarme falso, e um painel que erra uma vez
    deixa de ser lido.
    """
    from processo_seletivo.publicacoes.models_retificacao import VersaoConsolidada
    from tests.fixtures.edital import identificador
    from tests.fixtures.publicacao import retify

    cenario = peca["cenario"]
    retify(
        api_client,
        cenario["edital"],
        [
            {
                "targetPath": f"/schedule/id={identificador(402, 122)}/description",
                "operation": "REPLACE",
                "newValue": "Período de inscrições (redação ajustada)",
            }
        ],
        suffix="supervisao",
    )

    vigente = VersaoConsolidada.objects.filter(edital=cenario["edital"]).latest("materialized_at")
    assert cenario["ato"].versao_id != vigente.id, (
        "sem versão nova o filtro barato não admitiria candidato, e o teste não provaria o descarte"
    )
    assert das_especies(supervisao.sinais(cenario["processo"], presidenta), supervisao.UX_004) == []


# ---------------------------------------------------------------------------
# `UX-005` — recurso sem membro desimpedido
# ---------------------------------------------------------------------------


def impedir(inscricao, subject):
    """O `Impedimento` declarado da `012` — a quinta das cinco origens de `T-004`."""
    from processo_seletivo.avaliacoes.models import Impedimento

    return Impedimento.objects.create(
        identity_subject=subject,
        inscricao=inscricao,
        motivo="Parentesco declarado.",
        criado_em=timezone.now(),
        criado_por="carlos",
    )


@pytest.mark.django_db(transaction=True)
def test_com_a_comissao_inteira_impedida_o_sinal_aparece(peca, presidenta):
    """`FR-030` e `SC-010`: a condição verificável, e não a quantidade pendente isolada.

    João concluiu a Avaliação que fundamentou o Resultado atacado; Maria recebe impedimento
    declarado quanto àquela inscrição. Com os dois membros ativos impedidos, o conjunto de
    desimpedidos é vazio.
    """
    impedir(peca["inscricao"], "maria")

    achados = das_especies(
        supervisao.sinais(peca["cenario"]["processo"], presidenta), supervisao.UX_005
    )

    assert len(achados) == 1
    assert achados[0].edital.id == peca["cenario"]["edital"].id
    assert achados[0].medida is None


@pytest.mark.django_db(transaction=True)
def test_bastando_um_membro_desimpedido_o_sinal_some(peca, presidenta):
    """A contraprova de `SC-010`: Maria não tem impedimento, e a condição não se verifica."""
    achados = das_especies(
        supervisao.sinais(peca["cenario"]["processo"], presidenta), supervisao.UX_005
    )

    assert achados == []


@pytest.mark.django_db(transaction=True)
def test_dobrar_os_recursos_pendentes_nao_dobra_as_consultas(
    peca, presidenta, django_assert_num_queries
):
    """`FR-031` e `D-008`: a pergunta é agregada, e não `recurso × membro`.

    Iterar o guardião individual custaria cinco leituras por par, que é exatamente o custo por
    linha que a `018` já recusou uma vez.
    """
    from django.db import connection
    from django.test.utils import CaptureQueriesContext

    from tests.fixtures.recursos import admitir, interpor

    processo = peca["cenario"]["processo"]
    impedir(peca["inscricao"], "maria")
    with CaptureQueriesContext(connection) as com_um:
        supervisao.sinais(processo, presidenta)
    orcamento = len(com_um.captured_queries)

    # Inscrições distintas: `uq_recurso_por_publicacao` admite uma peça por par inscrição ×
    # publicação, e é a constraint que impede o cenário de existir de outro jeito.
    from tests.fixtures.supervisao import submeter

    outras = submeter(peca["cenario"]["edital"], 3, primeiro=9000, seed=122)
    for numero, inscricao in enumerate(outras):
        admitir(
            interpor(
                inscricao=inscricao,
                versao=peca["recurso"].versao,
                resultado=None,
                publicacao=peca["publicacao"],
                protocolo=f"REC-2026-EXTRA{numero:03d}",
            )
        )

    with django_assert_num_queries(orcamento):
        supervisao.sinais(processo, presidenta)


# ---------------------------------------------------------------------------
# `UX-004` — o ato **sorteado**, e os recortes que não são a ampla concorrência
# ---------------------------------------------------------------------------


@pytest.fixture
def certame_sorteado(gestor, api_client, manager_headers, process_payload):
    """Um marco de sorteio com cotas: ampla concorrência, PPI e PcD sobre o mesmo marco."""
    from tests.fixtures.sorteio import certame_com_cotas

    return certame_com_cotas(gestor, api_client, manager_headers, process_payload)


def ato_sorteado(cenario, relacao_publicada, *, lista_id=None):
    """O ato que um sorteio grava, com a relação que o originou citada no universo."""
    from processo_seletivo.classificacao.models import AtoDeOrdenacao, OrigemDaOrdem
    from processo_seletivo.publicacoes.models_retificacao import VersaoConsolidada
    from tests.fixtures.sorteio import MARCO, universo_de_sorteio

    versao = VersaoConsolidada.objects.filter(edital=cenario["edital"]).latest("materialized_at")
    return AtoDeOrdenacao.objects.create(
        edital=cenario["edital"],
        perfil_id=cenario["perfil"],
        marco_id=MARCO,
        lista_id=lista_id,
        origem=OrigemDaOrdem.SORTEIO,
        versao=versao,
        universo=universo_de_sorteio(
            cenario["edital"],
            versao=versao,
            perfil_id=cenario["perfil"],
            relacao=relacao_publicada,
        ),
        emitido_por="maria",
        emitido_em=timezone.now(),
    )


def relacao_do_recorte(cenario, *, lista_id=None, anterior=None, inscricoes=()):
    from processo_seletivo.publicacoes.models_retificacao import VersaoConsolidada
    from tests.fixtures.sorteio import MARCO, relacao

    versao = VersaoConsolidada.objects.filter(edital=cenario["edital"]).latest("materialized_at")
    return relacao(
        cenario["edital"],
        versao=versao,
        perfil_id=cenario["perfil"],
        marco_id=MARCO,
        lista_id=lista_id,
        inscricoes=inscricoes,
        anterior=anterior,
        motivo="Habilitação revista." if anterior is not None else "",
    )


@pytest.mark.django_db(transaction=True)
def test_o_ato_sorteado_fica_obsoleto_pela_relacao_e_o_sinal_o_alcanca(
    certame_sorteado, presidenta
):
    """`FR-029` com a `021`: a obsolescência de um sorteio não passa por versão nem por Resultado.

    Um ato sorteado envelhece quando a **relação de habilitados** que o originou ganha sucessora —
    e uma relação nova não altera a versão do Edital nem produz `ResultadoEtapa`. As duas condições
    do filtro barato passavam ao largo disso, e a confirmação exata nunca era chamada: o sinal
    ficava cego, em silêncio, que é o modo de falha que `T-003` diz custar caro.
    """
    inscricoes = certame_sorteado["inscricoes"]
    original = relacao_do_recorte(certame_sorteado, inscricoes=inscricoes)
    ato_sorteado(certame_sorteado, original)

    antes = das_especies(
        supervisao.sinais(certame_sorteado["processo"], presidenta), supervisao.UX_004
    )
    assert antes == [], "sem relação sucessora o ato reflete o fato que o originou"

    relacao_do_recorte(certame_sorteado, anterior=original, inscricoes=inscricoes[:2])

    achados = das_especies(
        supervisao.sinais(certame_sorteado["processo"], presidenta), supervisao.UX_004
    )
    assert len(achados) == 1
    assert achados[0].destino is not None
    # A dona é o sorteio, e não a ordenação: uma ordem sorteada não se refaz recalculando, e a tela
    # da 015 ofereceria justamente o recálculo que só uma semente nova produz.
    assert achados[0].destino.url.endswith("/sorteio")


@pytest.mark.django_db(transaction=True)
def test_o_ato_de_uma_lista_de_reserva_tambem_e_alcancado(certame_sorteado, presidenta):
    """`021`, `D-006`: um marco de cotas tem três atos raiz, e "o ato do marco" não é pergunta.

    Consultar o vigente sem dizer de qual lista devolve o da ampla concorrência, e os de PPI e PcD
    ficam invisíveis — a supervisão diria que está tudo em ordem enquanto duas das três ordens
    publicadas já não correspondem ao universo comprometido.
    """
    from tests.fixtures.sorteio import LISTA_PPI

    cotista = certame_sorteado["cotista_ppi"]
    original = relacao_do_recorte(certame_sorteado, lista_id=LISTA_PPI, inscricoes=[cotista])
    ato_sorteado(certame_sorteado, original, lista_id=LISTA_PPI)
    relacao_do_recorte(
        certame_sorteado, lista_id=LISTA_PPI, anterior=original, inscricoes=[cotista]
    )

    achados = das_especies(
        supervisao.sinais(certame_sorteado["processo"], presidenta), supervisao.UX_004
    )

    assert len(achados) == 1
    # O recorte é nomeado: sem ele os três sinais do mesmo marco sairiam com a mesma frase.
    assert "Pretos, pardos e indígenas" in achados[0].alvo
    assert "Pretos, pardos e indígenas" in achados[0].mensagem
