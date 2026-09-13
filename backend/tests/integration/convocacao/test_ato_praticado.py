"""Convocação praticada não se desfaz — nem por Retificação, nem por apuração, nem por faixa (019).

**`FR-282`, e as três metades importam.** Uma pessoa chamada foi alcançada de verdade: ela leu a
mensagem, organizou a vida em torno do prazo, talvez pediu dispensa no trabalho. Desfazer isso
porque um ato administrativo posterior mudou o número seria a instituição voltando atrás sobre
alguém que fez tudo certo — e o sistema não tem como avisá-la de que a chamada evaporou.

**O que muda é o que vem depois, e nunca o que já foi praticado.** A Retificação muda o Edital
daqui para a frente; a apuração nova diz o número de hoje; a faixa seguinte alcança mais gente. Os
três são atos legítimos, e nenhum deles toca as convocações que já existem.
"""

import pytest

from processo_seletivo.convocacao.application import selectors
from processo_seletivo.convocacao.models import Convocacao
from tests.fixtures.convocacao import apurar, convocar
from tests.fixtures.corte import MARCO
from tests.fixtures.edital import PROFILE_ID, caminho_perfil
from tests.fixtures.ocupacao import LINHA_GERAL
from tests.fixtures.publicacao import create_retification, publish_retification

pytestmark = pytest.mark.django_db(transaction=True)


def contexto(edital):
    return selectors.contexto_do_recorte(
        edital=edital, perfil_id=PROFILE_ID, marco_id=MARCO, lista_id=None
    )


def praticar_uma(edital, gestor, chave):
    """Convoca a próxima da fila e devolve a linha gravada."""
    declarado = convocar(edital, gestor, contexto(edital)["fila"][0], idempotency_key=chave)
    return Convocacao.objects.get(id=declarado["id"])


def continua_de_pe(convocacao):
    """A convocação continua existindo, vigente, e com os mesmos valores que nasceu."""
    convocacao.refresh_from_db()
    assert not convocacao.sucessoras.exists(), "ninguém a sucedeu"
    return convocacao


def test_a_nova_apuracao_nao_desfaz_a_convocacao_praticada(cenario, gestor):
    """A apuração seguinte diz o número de hoje, e não revoga a chamada de ontem.

    **É o caso mais fácil de errar por omissão**: a apuração é a proveniência da convocação, e um
    desenho que a atualizasse por FK faria a sucessora reescrever o que a chamada citou.
    """
    edital, _, _ = cenario
    convocacao = praticar_uma(edital, gestor, "ap-convoca")
    apuracao_citada = convocacao.apuracao_id

    apurar(edital, gestor, chave="ap-nova", motivo="Reapuração do recorte")

    continua_de_pe(convocacao)
    assert convocacao.apuracao_id == apuracao_citada, (
        "a convocação continua citando a apuração que a fundamentou, e não a de hoje"
    )


def test_a_nova_faixa_nao_desfaz_a_convocacao_praticada(cenario_do_77, gestor):
    """Ampliar a faixa alcança mais gente; quem já foi chamado continua chamado.

    A faixa seguinte não revoga a anterior — a `014` fechou isso —, e a convocação continua citando
    o corte que a fundamentou.
    """
    from processo_seletivo.classificacao.application.corte import geracao_vigente
    from tests.fixtures.corte import emitir as emitir_corte

    edital, _, _ = cenario_do_77
    convocacao = praticar_uma(edital, gestor, "fx-convoca")
    corte_citado = convocacao.corte_id

    # A geração sucessora, e não uma faixa solta: emitir corte sobre um recorte que já tem geração
    # vigente **exige** declarar qual está sendo sucedida — é a guarda `corte_ja_emitido` da `014`.
    emitir_corte(
        edital,
        gestor,
        chave="fx-corte",
        motivo="Nova geração de corte para o recorte",
        geracao=geracao_vigente(edital=edital, perfil_id=PROFILE_ID, marco_id=MARCO, lista_id=None),
    )

    continua_de_pe(convocacao)
    assert convocacao.corte_id == corte_citado, (
        "a convocação continua citando o corte que a fundamentou"
    )


def test_a_retificacao_nao_desfaz_a_convocacao_praticada(cenario, gestor, api_client):
    """**O caso mais duro**: a Retificação muda o Edital, e a chamada foi feita sob o anterior.

    A convocação guarda a versão que valia quando foi praticada. Retificar o quadro muda quantas
    vagas o Edital publica **daqui para a frente**, e o que já foi praticado continua de pé, citando
    a norma sob a qual foi praticado.
    """
    edital, _, _ = cenario
    convocacao = praticar_uma(edital, gestor, "rt-convoca")
    versao_citada = convocacao.versao_id

    publish_retification(
        api_client,
        create_retification(
            api_client,
            edital,
            [
                {
                    "targetPath": (
                        f"{caminho_perfil('vacancyTable')}/id={LINHA_GERAL}/immediateVacancies"
                    ),
                    "operation": "REPLACE",
                    "newValue": 5,
                },
                {
                    "targetPath": caminho_perfil("immediateVacancies"),
                    "operation": "REPLACE",
                    "newValue": 5,
                },
            ],
            suffix="convocacao",
        ),
        suffix="convocacao",
    )

    continua_de_pe(convocacao)
    assert convocacao.versao_id == versao_citada, (
        "a convocação continua citando a versão sob a qual foi praticada"
    )


def test_as_tres_juntas_nao_desfazem_nada(cenario, gestor, api_client):
    """**As três, e não uma delas** — que é o que a `T047a` cobra por escrito.

    O modo de errar aqui é provar uma e presumir as outras duas: cada uma chega por um caminho
    diferente, e um desenho que sobrevivesse a duas poderia cair na terceira.
    """
    edital, _, _ = cenario
    convocacao = praticar_uma(edital, gestor, "tres-convoca")

    apurar(edital, gestor, chave="tres-apura", motivo="Reapuração")
    publish_retification(
        api_client,
        create_retification(
            api_client,
            edital,
            [{"targetPath": caminho_perfil("name"), "operation": "REPLACE", "newValue": "Outro"}],
            suffix="tres",
        ),
        suffix="tres",
    )
    apurar(edital, gestor, chave="tres-apura-2", motivo="Reapuração depois da Retificação")

    continua_de_pe(convocacao)
    assert Convocacao.objects.filter(edital=edital).count() == 1


def test_o_deferimento_nao_desfaz_convocacao_praticada_nem_cancela_matricula(cenario_do_77, gestor):
    """`FR-292a`, e é a metade da `D-007` que nenhuma outra tarefa cobre (`T050a`).

    **O deferimento devolve a vez a quem recorreu, e não tira a de quem já a teve.** A outra metade
    da decisão — a que a `FR-292b` trata — põe o reabilitado na frente da fila; esta diz o que ele
    **não** faz: nenhuma convocação praticada se desfaz, e nenhuma matrícula efetivada é cancelada.

    A alternativa seria a instituição tirar a vaga de quem cumpriu tudo o que lhe foi pedido, meses
    depois, por causa de um erro que não foi dela. Quem responde por esse erro é a Administração, e
    a `D-007` fechou que ela não o cobra de terceiro.
    """
    from processo_seletivo.convocacao.application.desfechar import desfechar
    from processo_seletivo.convocacao.domain import nomes
    from processo_seletivo.convocacao.models import DesfechoDaConvocacao
    from processo_seletivo.resultados.models import ResultadoEtapa
    from tests.fixtures.corte import ENTREVISTA
    from tests.fixtures.recursos import admitir, decidir, interpor, superar

    edital, _, inscricoes = cenario_do_77
    # Uma titular é chamada e **aceita**: a matrícula está efetivada.
    convocacao = praticar_uma(edital, gestor, "df-convoca")
    desfechar(
        actor=gestor,
        processo_id=edital.processo_id,
        convocacao_id=convocacao.id,
        especie=nomes.ACEITE,
        fundamento="Matrícula efetivada.",
        idempotency_key="df-aceite",
        correlation_id="teste-convocacao-019",
    )

    # E alguém de fora da faixa tem o recurso deferido, voltando a ser habilitado.
    de_fora = inscricoes[3]
    superado = ResultadoEtapa.objects.create(
        inscricao=de_fora,
        edital=edital,
        versao=convocacao.versao,
        etapa_id=ENTREVISTA,
        origem=ResultadoEtapa.Origem.OCORRENCIA,
        consequencia=ResultadoEtapa.Consequencia.ELIMINADA,
        motivo="Documentação indeferida",
        consolidado_em=convocacao.criado_em,
        consolidado_por="teste",
    )
    recurso = interpor(inscricao=de_fora, versao=convocacao.versao, resultado=superado)
    admitir(recurso)
    decisao = decidir(
        recurso,
        protegido=superado,
        consequencia=ResultadoEtapa.Consequencia.HABILITADA,
        versao=convocacao.versao,
    )
    superar(superado, decisao, consequencia=ResultadoEtapa.Consequencia.HABILITADA)

    continua_de_pe(convocacao)
    desfecho = DesfechoDaConvocacao.objects.get(convocacao=convocacao)
    assert desfecho.especie == nomes.ACEITE, "a matrícula efetivada continua efetivada"
