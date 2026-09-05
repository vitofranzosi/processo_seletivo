"""O Resultado de quem não foi avaliado — o ato, e o que ele recusa (D-1).

A prova que importa aqui não é que o comando grava: é **o que ele não consulta**. Uma Etapa cuja
consolidação está impedida — decisória e não eliminatória, de leitura múltipla — continua podendo
registrar que alguém não compareceu, porque o impedimento é do mecanismo avaliação e a ocorrência
não passa por ele. É a invariante I-1 do briefing verificada pelo lado que ela nasceu para cobrir.
"""

from uuid import uuid4

import pytest

from processo_seletivo.auditoria.models import RegistroAuditoria
from processo_seletivo.processos.models import AtoAdministrativo
from processo_seletivo.publicacoes.models_retificacao import VersaoConsolidada
from processo_seletivo.resultados.application.ocorrencia import REGISTRAR, registrar_ocorrencia
from processo_seletivo.resultados.models import ResultadoEtapa
from processo_seletivo.shared.api.problems import DomainError
from tests.conftest import ator_institucional
from tests.fixtures.comissao import inscrever
from tests.fixtures.mesa import concluir_como, distribuir_para
from tests.fixtures.resultado import montar_etapa_de_leitura_unica

pytestmark = [pytest.mark.integration, pytest.mark.django_db(transaction=True)]

FALTOU = "não compareceu à Entrevista (item 6.3 do Edital)"


@pytest.fixture
def presidente():
    return ator_institucional("maria")


@pytest.fixture
def cenario(gestor, api_client, manager_headers):
    montado = montar_etapa_de_leitura_unica(
        gestor, api_client, manager_headers, seed=1600, codigo="1600"
    )
    montado["inscricoes"] = inscrever(montado["edital"], 3, primeiro=1)
    return montado


def registrar(cenario, ator, inscricoes, *, chave, motivo=FALTOU, etapa=None):
    return registrar_ocorrencia(
        actor=ator,
        processo_id=cenario["processo"].id,
        edital_id=cenario["edital"].id,
        etapa_id=etapa or cenario["etapa"],
        inscricao_ids=[i.id for i in inscricoes],
        motivo=motivo,
        idempotency_key=chave,
        correlation_id="teste",
    )


def test_a_ocorrencia_nasce_sem_avaliacao_sem_forma_e_sem_grandeza(cenario, presidente):
    """O ramo inteiro é feito de ausências, e é isso que ele afirma.

    Sem Avaliação porque ninguém avaliou; sem forma porque não houve conclusão sob forma nenhuma;
    sem pontuação e sem sentido porque o Edital não publicou grandeza para quem não compareceu.
    """
    desfecho = registrar(cenario, presidente, cenario["inscricoes"][:1], chave="o1")
    assert desfecho["feitas"] == 1

    resultado = ResultadoEtapa.objects.get(inscricao=cenario["inscricoes"][0])
    assert resultado.origem == ResultadoEtapa.Origem.OCORRENCIA
    assert resultado.avaliacao_id is None
    assert resultado.forma == ""
    assert resultado.pontuacao is None
    assert resultado.sentido == ""
    assert resultado.consequencia == ResultadoEtapa.Consequencia.ELIMINADA
    assert resultado.motivo == FALTOU
    assert resultado.consolidado_por == "maria"


def test_a_norma_que_fundamentou_a_constatacao_e_a_vigente(cenario, presidente):
    """I-2: o Resultado sem Avaliação também identifica a regra que o produziu.

    Sem a versão no próprio Resultado, este seria o ramo que ficaria sem norma nenhuma — não há
    `avaliacao__versao` a percorrer.
    """
    registrar(cenario, presidente, cenario["inscricoes"][:1], chave="o2")
    resultado = ResultadoEtapa.objects.get(inscricao=cenario["inscricoes"][0])
    vigente = VersaoConsolidada.objects.filter(edital=cenario["edital"]).latest("valid_from")
    assert resultado.versao_id == vigente.id


def test_o_motivo_e_obrigatorio_e_a_recusa_e_do_pedido(cenario, presidente):
    """Nada é criado: sem a causa, o Resultado não teria o que responder a um recurso."""
    for vazio in ("", "   ", None):
        with pytest.raises(DomainError) as recusa:
            registrar(
                cenario, presidente, cenario["inscricoes"][:1], chave=uuid4().hex, motivo=vazio
            )
        assert recusa.value.code == "motivo_ausente"
    assert ResultadoEtapa.objects.count() == 0


def test_selecao_vazia_e_erro_do_pedido(cenario, presidente):
    with pytest.raises(DomainError) as recusa:
        registrar(cenario, presidente, [], chave="o3")
    assert recusa.value.code == "selecao_vazia"


def test_quem_ja_tem_resultado_e_recusa_de_linha_e_o_lote_segue(cenario, presidente):
    """I-6 pelo caminho do ato: no máximo um Resultado por Inscrição × Etapa.

    Recusa nomeada, e não sucesso silencioso nem exceção de integridade vazando para a tela.
    """
    registrar(cenario, presidente, cenario["inscricoes"][:1], chave="o4")
    desfecho = registrar(cenario, presidente, cenario["inscricoes"][:2], chave="o5")
    assert desfecho["feitas"] == 1
    assert desfecho["recusadas"] == 1
    assert "já possui Resultado" in desfecho["motivos"][0]["motivo"]
    assert ResultadoEtapa.objects.filter(inscricao=cenario["inscricoes"][0]).count() == 1


def test_a_ocorrencia_nao_reescreve_um_resultado_por_avaliacao(cenario, presidente, gestor):
    """A unicidade vale entre origens, e não dentro de cada uma.

    Consolidado por avaliação, o par está resolvido: constatar ausência depois seria contradizer o
    que já foi oficializado, e isso é anulação — ato que a V1 não tem.
    """
    from processo_seletivo.resultados.application.consolidacao import consolidar

    inscricao = cenario["inscricoes"][0]
    distribuir_para(cenario, gestor, ["joao"], [inscricao], chave="lote-1600")
    concluir_como(cenario, "joao", inscricao, pontuacao="75")
    consolidar(
        actor=presidente,
        processo_id=cenario["processo"].id,
        edital_id=cenario["edital"].id,
        etapa_id=cenario["etapa"],
        inscricao_ids=[inscricao.id],
        idempotency_key="c-1600",
        correlation_id="teste",
    )

    desfecho = registrar(cenario, presidente, [inscricao], chave="o6")
    assert desfecho["feitas"] == 0
    assert ResultadoEtapa.objects.get(inscricao=inscricao).origem == (
        ResultadoEtapa.Origem.AVALIACAO
    )


def test_a_etapa_impedida_de_consolidar_ainda_registra_ocorrencia(
    gestor, api_client, manager_headers, presidente
):
    """**A prova de I-1.** O impedimento é do mecanismo avaliação, e a ausência não passa por ele.

    Leitura múltipla é o caso mais claro: o Edital prevê duas avaliações e não declara como
    combiná-las, de modo que `consolidar` recusa a Etapa inteira. Quem faltou à Etapa continua
    precisando de desfecho, e ele não depende de combinação nenhuma.
    """
    from processo_seletivo.resultados.application.consolidacao import consolidar

    cenario = montar_etapa_de_leitura_unica(
        gestor, api_client, manager_headers, seed=1610, codigo="1610", avaliacoes=2
    )
    cenario["inscricoes"] = inscrever(cenario["edital"], 1, primeiro=1)

    with pytest.raises(DomainError) as recusa:
        consolidar(
            actor=presidente,
            processo_id=cenario["processo"].id,
            edital_id=cenario["edital"].id,
            etapa_id=cenario["etapa"],
            inscricao_ids=[cenario["inscricoes"][0].id],
            idempotency_key="c-1610",
            correlation_id="teste",
        )
    assert recusa.value.code == "regra_de_combinacao_ausente"

    desfecho = registrar(cenario, presidente, cenario["inscricoes"], chave="o7")
    assert desfecho["feitas"] == 1


def test_a_ocorrencia_exclui_da_etapa_seguinte(gestor, api_client, manager_headers, presidente):
    """A progressão não distingue origem: `ELIMINADA` é `ELIMINADA` (D-003).

    É o que a 015 vai consumir — quem foi eliminado por ausência não entra na ordem, pelo mesmo
    caminho de quem foi eliminado por nota.
    """
    from processo_seletivo.resultados.application.prontidao import participacao

    cenario = montar_etapa_de_leitura_unica(
        gestor, api_client, manager_headers, seed=1620, codigo="1620"
    )
    cenario["inscricoes"] = inscrever(cenario["edital"], 2, primeiro=1)
    faltante = cenario["inscricoes"][0]

    registrar(cenario, presidente, [faltante], chave="o8")

    participantes, eliminadas, _ = participacao(
        edital=cenario["edital"], etapa_id=cenario["segunda"]
    )
    assert faltante.id in eliminadas
    assert faltante.id not in participantes


def test_quem_nao_participa_da_etapa_e_erro_do_pedido(
    gestor, api_client, manager_headers, presidente
):
    """Eliminado na primeira, não se constata ausência na segunda: ele já não participa dela."""
    cenario = montar_etapa_de_leitura_unica(
        gestor, api_client, manager_headers, seed=1630, codigo="1630"
    )
    cenario["inscricoes"] = inscrever(cenario["edital"], 2, primeiro=1)
    faltante = cenario["inscricoes"][0]
    registrar(cenario, presidente, [faltante], chave="o9")

    with pytest.raises(DomainError) as recusa:
        registrar(cenario, presidente, [faltante], chave="o10", etapa=cenario["segunda"])
    assert recusa.value.code == "inscricao_fora_da_etapa"


def test_a_mesma_chave_com_o_mesmo_conteudo_devolve_o_desfecho_original(cenario, presidente):
    primeiro = registrar(cenario, presidente, cenario["inscricoes"][:1], chave="o11")
    eventos = RegistroAuditoria.objects.filter(operation=REGISTRAR).count()

    repetido = registrar(cenario, presidente, cenario["inscricoes"][:1], chave="o11")
    assert repetido == primeiro
    assert ResultadoEtapa.objects.count() == 1
    assert RegistroAuditoria.objects.filter(operation=REGISTRAR).count() == eventos


def test_a_mesma_chave_com_motivo_diferente_e_conflito(cenario, presidente):
    """Dois motivos são dois atos: a repetição não pode devolver o desfecho de um para o outro."""
    registrar(cenario, presidente, cenario["inscricoes"][:1], chave="o12")
    with pytest.raises(DomainError) as recusa:
        registrar(
            cenario,
            presidente,
            cenario["inscricoes"][:1],
            chave="o12",
            motivo="eliminada por descumprimento de pré-requisito (item 5.3)",
        )
    assert recusa.value.status == 409


def test_dois_atos_concorrentes_produzem_no_maximo_um_resultado(cenario, presidente):
    """O invólucro serializa por Processo; a unicidade é o cinto que sobra."""
    registrar(cenario, presidente, cenario["inscricoes"][:1], chave=uuid4().hex)
    segundo = registrar(cenario, presidente, cenario["inscricoes"][:1], chave=uuid4().hex)
    assert segundo["feitas"] == 0
    assert ResultadoEtapa.objects.filter(inscricao=cenario["inscricoes"][0]).count() == 1


def test_o_ato_deixa_trilha_e_motivo_no_ato_administrativo(cenario, presidente):
    """I-5: oficializar resultado é operação explícita, autorizada e **auditável**.

    O motivo vai ao `AtoAdministrativo` porque é dele que quem responde a um recurso lê a causa —
    como já lê a do impedimento e a da reabertura.
    """
    registrar(cenario, presidente, cenario["inscricoes"][:1], chave="o13")

    evento = RegistroAuditoria.objects.get(operation=REGISTRAR)
    assert evento.aggregate_type == "ResultadoEtapa"
    ato = AtoAdministrativo.objects.get(operation=REGISTRAR)
    assert ato.reason.endswith(FALTOU)
    assert ato.actor_subject == "maria"


def test_quem_nao_preside_nem_gere_recebe_a_resposta_uniforme(cenario):
    """404, e não 403: o mesmo que a 011 responde a tudo que o ator não alcança."""
    with pytest.raises(DomainError) as recusa:
        registrar(cenario, ator_institucional("joao"), cenario["inscricoes"][:1], chave="o14")
    assert recusa.value.status == 404
    assert ResultadoEtapa.objects.count() == 0
