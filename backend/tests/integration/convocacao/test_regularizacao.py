"""Convocar o indeferido para corrigir, e a regularização que sucede o Resultado (019, `US3`).

**É a via administrativa que o 77, o 58 e o 59 escrevem, e que hoje não existe no sistema.** O
candidato tem a matrícula indeferida por documentação incompleta; o Edital manda convocá-lo para
regularizar; ele corrige, e passa a ocupar a vaga. Sem esta história, a única saída seria o
recurso — e recurso é o remédio para quem discorda da decisão, não para quem apenas entregou um
papel a menos.

**A regularização sucede o Resultado pelo mecanismo da `018`** (`D-008`). A alternativa — um ato só
da `019` marcando a pessoa como apta — criaria um segundo caminho de habilitação, invisível para a
contagem da `016`. A `Q-3` o recusou por escrito.
"""

import pytest

from processo_seletivo.convocacao.application import selectors
from processo_seletivo.convocacao.application.desfechar import desfechar
from processo_seletivo.convocacao.domain import nomes
from processo_seletivo.ocupacao.application.selectors import ocupacao_do_recorte
from processo_seletivo.resultados.models import ResultadoEtapa
from processo_seletivo.shared.api.problems import DomainError
from tests.fixtures.convocacao import apurar, convocar, montar_cenario_da_convocacao
from tests.fixtures.corte import ENTREVISTA, MARCO
from tests.fixtures.edital import PROFILE_ID

pytestmark = pytest.mark.django_db(transaction=True)


@pytest.fixture
def com_indeferidos(db, gestor, api_client, manager_headers, process_payload, raiz_de_arquivos):
    """Os **dois** classificados dentro da faixa estão indeferidos, e há três vagas publicadas.

    É o recorte do item 8.2 do 77/2026: matrículas indeferidas, vagas sobrando, e a ordem de
    classificação decidindo quem é chamado primeiro para corrigir.
    """
    return montar_cenario_da_convocacao(
        gestor,
        api_client,
        manager_headers,
        process_payload,
        prefixo="regularizacao-019",
        indeferidas=(0, 1),
    )


def contexto(edital):
    return selectors.contexto_do_recorte(
        edital=edital, perfil_id=PROFILE_ID, marco_id=MARCO, lista_id=None
    )


def regularizar(edital, gestor, convocacao_id, chave):
    return desfechar(
        actor=gestor,
        processo_id=edital.processo_id,
        convocacao_id=convocacao_id,
        especie=nomes.REGULARIZACAO,
        fundamento="Documentação regularizada no prazo do item 8.2 do Edital 77/2026.",
        idempotency_key=chave,
        correlation_id="teste-convocacao-019",
    )


def test_o_cenario_tem_dois_indeferidos_na_faixa_e_nenhum_ocupante(com_indeferidos, gestor):
    """A premissa dos demais, medida e não suposta."""
    edital, _, _ = com_indeferidos
    leitura = contexto(edital)

    assert len(leitura["regularizaveis"]) == 2
    assert leitura["fila"] == [], "ninguém habilitado: não há quem chamar para vaga"
    assert leitura["apuracao"].ocupadas == 0
    assert leitura["apuracao"].faltando == 3


def test_a_convocacao_para_regularizar_respeita_a_ordem_de_classificacao(com_indeferidos, gestor):
    """`T061`: o item 8.2 do 77/2026 não abre exceção para quem corrige.

    Chamar o segundo indeferido antes do primeiro é a mesma quebra de ordem que chamar o segundo
    classificado antes do primeiro — e o prejuízo é o mesmo: quem estava na frente perde a vez sem
    que nada o registre.
    """
    edital, _, _ = com_indeferidos
    primeiro, segundo = contexto(edital)["regularizaveis"]

    with pytest.raises(DomainError) as erro:
        convocar(
            edital,
            gestor,
            segundo,
            especie=nomes.PARA_REGULARIZAR,
            idempotency_key="reg-fora-de-ordem",
        )

    assert erro.value.code == nomes.PRECEDENCIA_NA_ORDEM
    assert convocar(
        edital,
        gestor,
        primeiro,
        especie=nomes.PARA_REGULARIZAR,
        idempotency_key="reg-na-ordem",
    )


def test_o_fundamento_do_edital_fica_no_ato(com_indeferidos, gestor):
    """A chamada para regularizar é ato motivado, e o motivo é o item que a autoriza."""
    from processo_seletivo.convocacao.models import Convocacao

    edital, _, _ = com_indeferidos
    primeiro = contexto(edital)["regularizaveis"][0]

    declarado = convocar(
        edital,
        gestor,
        primeiro,
        especie=nomes.PARA_REGULARIZAR,
        fundamento="Item 8.2 do Edital 77/2026: convocação para regularização documental.",
        idempotency_key="reg-fundamento",
    )

    convocacao = Convocacao.objects.get(id=declarado["id"])
    assert "8.2" in convocacao.fundamento
    assert convocacao.especie == nomes.PARA_REGULARIZAR


def test_quem_esta_habilitado_nao_e_convocavel_para_regularizar(cenario, gestor):
    """Não há o que regularizar em quem não foi indeferido.

    A recusa é `fora_da_faixa` porque a fila da regularização é outra — e a mensagem dela nomeia as
    três razões possíveis, em vez de mandar quem lê procurar a Inscrição no corte.
    """
    edital, _, _ = cenario
    habilitado = contexto(edital)["fila"][0]

    with pytest.raises(DomainError) as erro:
        convocar(
            edital,
            gestor,
            habilitado,
            especie=nomes.PARA_REGULARIZAR,
            idempotency_key="reg-habilitado",
        )

    assert erro.value.code == nomes.FORA_DA_FAIXA


def test_o_ciclo_da_regularizacao_ocupa_a_vaga_sem_reabrir_a_ordem(com_indeferidos, gestor):
    """`T065`: o indeferido continua existindo sucedido, a apuração seguinte o conta, e a ordem
    não é reaberta.

    **Nenhum ato de ordenação novo é emitido**, e é o que distingue esta via do recurso: a `018`
    manda o deferimento reabrir a ordem porque a decisão pode mudar pontuação e posição. Aqui não
    muda nada disso — a pessoa sempre esteve onde está, e o que faltava era um documento.
    """
    from processo_seletivo.classificacao.models import AtoDeOrdenacao

    edital, _, _ = com_indeferidos
    atos_antes = AtoDeOrdenacao.objects.filter(edital=edital).count()
    primeiro = contexto(edital)["regularizaveis"][0]
    convocada = convocar(
        edital,
        gestor,
        primeiro,
        especie=nomes.PARA_REGULARIZAR,
        idempotency_key="ciclo-reg-convoca",
    )

    declarado = regularizar(edital, gestor, convocada["id"], "ciclo-reg-desfecho")
    apurar(edital, gestor, chave="ciclo-reg-apura", motivo="Regularização registrada")

    assert declarado["efeito"] == "INCLUSAO"
    numeros = ocupacao_do_recorte(
        edital=edital, perfil_id=PROFILE_ID, marco_id=MARCO, lista_id=None
    )
    assert numeros["ocupadas"] == 1, "a apuração seguinte conta quem regularizou"
    assert numeros["faltando"] == 2
    assert AtoDeOrdenacao.objects.filter(edital=edital).count() == atos_antes, (
        "a regularização não reabre a ordem"
    )

    vigente = ResultadoEtapa.vigentes.get(inscricao_id=primeiro, edital=edital, etapa_id=ENTREVISTA)
    assert vigente.origem == ResultadoEtapa.Origem.REGULARIZACAO
    assert vigente.consequencia == ResultadoEtapa.Consequencia.HABILITADA
    anterior = vigente.resultado_anterior
    assert anterior.consequencia == ResultadoEtapa.Consequencia.ELIMINADA, (
        "o indeferido continua existindo, sucedido"
    )


def test_regularizado_passa_a_contar_na_ocupacao_e_sai_da_fila_de_regularizacao(
    com_indeferidos, gestor
):
    """Depois de regularizar, a pessoa é ocupante — e não é mais chamável para corrigir nada."""
    edital, _, _ = com_indeferidos
    primeiro = contexto(edital)["regularizaveis"][0]
    convocada = convocar(
        edital,
        gestor,
        primeiro,
        especie=nomes.PARA_REGULARIZAR,
        idempotency_key="conta-reg-convoca",
    )

    regularizar(edital, gestor, convocada["id"], "conta-reg-desfecho")
    apurar(edital, gestor, chave="conta-reg-apura", motivo="Regularização registrada")

    depois = contexto(edital)
    assert primeiro not in depois["regularizaveis"]
    assert str(primeiro) in depois["ocupando"]
