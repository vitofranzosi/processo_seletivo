"""A ordem por pontuação sem nenhum resultado é recusada no comando (128, US1).

O cenário é o do Edital 91 do estudo de orientação, reduzido: um marco por pontuação que enumera uma
Etapa, inscrições enviadas, ninguém avaliado. Todos os casos passam pelo comando, sob a trava — a
tela e o gesto da condução estão em `tests/interface/test_ordem_sem_resultado.py`.

**A ordem do acervo** — emitida sem nenhum resultado antes desta regra — é feita aqui desligando a
recusa por `monkeypatch`, e só para a emissão dela. Era o que o comando aceitava até a `128`, e é a
forma honesta de ter, no teste, um ato que hoje só existe no acervo.
"""

import pytest

from processo_seletivo.auditoria.models import RegistroAuditoria
from processo_seletivo.classificacao.application import ordem_sem_resultado
from processo_seletivo.classificacao.application.calculo import calcular_ordem
from processo_seletivo.classificacao.application.emissao import (
    EMITIR,
    assinatura_da_proposta,
    emitir_ordem,
)
from processo_seletivo.classificacao.application.selectors import ato_vigente
from processo_seletivo.classificacao.models import AtoDeOrdenacao
from processo_seletivo.resultados.application.consolidacao import consolidar
from processo_seletivo.resultados.application.ocorrencia import registrar_ocorrencia
from processo_seletivo.shared.api.problems import DomainError
from tests.fixtures.comissao import inscrever
from tests.fixtures.corte import (
    MARCO,
    entrevistar,
    montar_cenario_do_corte,
    rascunho_com_desempate,
    regra,
)
from tests.fixtures.edital import PROFILE_ID
from tests.fixtures.mesa import concluir_como, distribuir_para

pytestmark = [pytest.mark.integration, pytest.mark.django_db(transaction=True)]

CODIGO = "ordering_without_stage_results"


@pytest.fixture
def sem_avaliacao(gestor, api_client, manager_headers, process_payload):
    """Três inscrições enviadas, ninguém avaliado, ordem por emitir."""
    edital, pontuada, inscricoes = montar_cenario_do_corte(
        gestor,
        api_client,
        manager_headers,
        process_payload,
        prefixo="ordem-128",
        pontuacoes=(),
        emitir_a_ordem=False,
    )
    inscricoes += inscrever(edital, 2, primeiro=701)
    return edital, pontuada, inscricoes


def _emitir(edital, gestor, *, chave, motivo="", lista_id=None):
    vigente = ato_vigente(edital=edital, marco_id=MARCO, lista_id=lista_id)
    proposta = calcular_ordem(
        edital=edital, perfil_id=PROFILE_ID, marco_id=MARCO, lista_id=lista_id
    )
    return emitir_ordem(
        actor=gestor,
        processo_id=edital.processo_id,
        edital_id=edital.id,
        perfil_id=PROFILE_ID,
        marco_id=MARCO,
        lista_id=lista_id,
        idempotency_key=chave,
        correlation_id="teste-128",
        confirmacao_do_calculo=assinatura_da_proposta(proposta, ato_vigente=vigente),
        motivo=motivo,
    )


def _avaliar(edital, gestor, pontuada, inscricoes, notas, *, chave):
    contexto = {"edital": edital, "processo": edital.processo, "etapa": pontuada["id"]}
    from processo_seletivo.comissoes.models import MembroComissao

    contexto["membros"] = {
        "joao": MembroComissao.objects.get(processo=edital.processo, identity_subject="joao")
    }
    avaliados = inscricoes[: len(notas)]
    distribuir_para(contexto, gestor, ["joao"], avaliados, chave=f"{chave}-lote")
    for inscricao, nota in zip(avaliados, notas, strict=True):
        concluir_como(contexto, "joao", inscricao, pontuacao=nota)
    consolidar(
        actor=gestor,
        processo_id=edital.processo_id,
        edital_id=edital.id,
        etapa_id=pontuada["id"],
        inscricao_ids=[item.id for item in avaliados],
        idempotency_key=f"{chave}-consolidar",
        correlation_id="teste-128",
    )


def _emitir_como_no_acervo(monkeypatch, edital, gestor, *, chave):
    with monkeypatch.context() as desligada:
        desligada.setattr(ordem_sem_resultado, "recusar", lambda proposta: None)
        _emitir(edital, gestor, chave=chave)
    return ato_vigente(edital=edital, marco_id=MARCO)


def test_sem_nenhum_resultado_a_emissao_e_recusada_e_nada_e_gravado(sem_avaliacao, gestor):
    """FR-4200, FR-4206, FR-4210, FR-4211, SC-1300."""
    edital, pontuada, _ = sem_avaliacao

    with pytest.raises(DomainError) as recusa:
        _emitir(edital, gestor, chave="128-recusa")

    assert recusa.value.code == CODIGO
    assert recusa.value.detail == (
        f"Nenhuma das 3 inscrições deste recorte tem resultado na Etapa {pontuada['name']}. Para "
        "emitir a ordem, distribua as inscrições, avalie e consolide os resultados dessa Etapa."
    )
    assert AtoDeOrdenacao.objects.filter(edital=edital).count() == 0
    assert RegistroAuditoria.objects.filter(operation=EMITIR).count() == 0


def test_a_recusa_vem_antes_da_assinatura(sem_avaliacao, gestor):
    """D-005: a confirmação velha recebe a razão da regra, e não "a ordem mudou"."""
    edital, _, _ = sem_avaliacao

    with pytest.raises(DomainError) as recusa:
        emitir_ordem(
            actor=gestor,
            processo_id=edital.processo_id,
            edital_id=edital.id,
            perfil_id=PROFILE_ID,
            marco_id=MARCO,
            idempotency_key="128-assinatura-velha",
            correlation_id="teste-128",
            confirmacao_do_calculo="assinatura-de-outra-leitura",
        )

    assert recusa.value.code == CODIGO


def test_com_um_resultado_a_ordem_parcial_e_emitida(sem_avaliacao, gestor):
    """FR-4204, SC-1301."""
    edital, pontuada, inscricoes = sem_avaliacao
    _avaliar(edital, gestor, pontuada, inscricoes, ["80.0000"], chave="128-parcial")

    _emitir(edital, gestor, chave="128-parcial-ordem")

    ato = ato_vigente(edital=edital, marco_id=MARCO)
    assert ato is not None
    assert ato.posicoes.filter(posicao__isnull=False).count() == 1
    assert ato.posicoes.filter(posicao__isnull=True).count() == 2


def test_depois_que_o_resultado_chega_a_mesma_emissao_e_aceita_com_a_mesma_chave(
    sem_avaliacao, gestor
):
    """US1, cenário 5; FR-4210: a recusa não deixou desfecho preso à chave."""
    edital, pontuada, inscricoes = sem_avaliacao
    with pytest.raises(DomainError):
        _emitir(edital, gestor, chave="128-depois")

    _avaliar(edital, gestor, pontuada, inscricoes, ["90.0000", "70.0000"], chave="128-depois")
    _emitir(edital, gestor, chave="128-depois")

    assert ato_vigente(edital=edital, marco_id=MARCO) is not None


def test_universo_vazio_continua_emitindo_a_ordem_vazia(
    gestor, api_client, manager_headers, process_payload
):
    """FR-4205: o recorte em que ninguém concorreu, num Edital em que ninguém foi avaliado."""
    from tests.fixtures.recortes import MODALIDADE_PCD, montar_cenario_7_1_2

    edital, _, _ = montar_cenario_7_1_2(
        gestor,
        api_client,
        manager_headers,
        process_payload,
        prefixo="ordem-128-vazia",
        pontuacoes=(),
        autodeclarar=False,
        emitir_a_ordem=False,
    )

    _emitir(edital, gestor, chave="128-vazia", lista_id=MODALIDADE_PCD)

    ato = ato_vigente(edital=edital, marco_id=MARCO, lista_id=MODALIDADE_PCD)
    assert ato is not None and ato.universo["participants"] == []
    with pytest.raises(DomainError) as recusa:
        _emitir(edital, gestor, chave="128-vazia-ampla")
    assert recusa.value.code == CODIGO, "a ampla do mesmo Edital tem inscrição, e é recusada"


def test_o_recorte_reservado_com_autodeclarados_e_sem_resultado_e_recusado(
    gestor, api_client, manager_headers, process_payload
):
    """FR-4203: o universo é o do recorte, e quem se autodeclarou nele não tem Resultado."""
    from tests.fixtures.recortes import MODALIDADE_PPI, montar_cenario_7_1_2

    edital, _, _ = montar_cenario_7_1_2(
        gestor,
        api_client,
        manager_headers,
        process_payload,
        prefixo="ordem-128-reservado",
        pontuacoes=(),
        modalidades={0: MODALIDADE_PPI},
        autodeclarar=False,
        emitir_a_ordem=False,
    )

    with pytest.raises(DomainError) as recusa:
        _emitir(edital, gestor, chave="128-reservado", lista_id=MODALIDADE_PPI)

    assert recusa.value.code == CODIGO
    assert recusa.value.detail.startswith("A inscrição deste recorte não tem resultado")


def test_a_ocorrencia_que_elimina_e_resultado(sem_avaliacao, gestor):
    """FR-4201, D-002: uma eliminação por Ocorrência basta; a ordem sai parcial."""
    edital, pontuada, inscricoes = sem_avaliacao
    registrar_ocorrencia(
        actor=gestor,
        processo_id=edital.processo_id,
        edital_id=edital.id,
        etapa_id=pontuada["id"],
        inscricao_ids=[inscricoes[0].id],
        motivo="Não compareceu à Etapa.",
        idempotency_key="128-ocorrencia",
        correlation_id="teste-128",
    )

    _emitir(edital, gestor, chave="128-ocorrencia-ordem")

    ato = ato_vigente(edital=edital, marco_id=MARCO)
    assert ato.posicoes.filter(consequencia="ELIMINADA").count() == 1


def test_resultado_so_na_etapa_do_desempate_nao_basta(
    gestor, api_client, manager_headers, process_payload
):
    """FR-4202, D-003: a Entrevista desempata, não é enumerada, e não decide quem tem posição."""
    edital, _, inscricoes = montar_cenario_do_corte(
        gestor,
        api_client,
        manager_headers,
        process_payload,
        cut=regra(governedStage="NONE"),
        prefixo="ordem-128-desempate",
        pontuacoes=(),
        draft_factory=rascunho_com_desempate,
        emitir_a_ordem=False,
    )
    entrevistar(edital, gestor, [(inscricoes[0], "80.0000")], chave="128-entrevista")

    with pytest.raises(DomainError) as recusa:
        _emitir(edital, gestor, chave="128-desempate-ordem")

    assert recusa.value.code == CODIGO


def test_a_sucessao_de_uma_ordem_do_acervo_sem_resultado_e_recusada(
    sem_avaliacao, gestor, monkeypatch
):
    """FR-4207, FR-4219, SC-1304: o ato do acervo continua vigente; sucedê-lo sem resultado, não."""
    edital, pontuada, inscricoes = sem_avaliacao
    do_acervo = _emitir_como_no_acervo(monkeypatch, edital, gestor, chave="128-acervo")
    assert do_acervo is not None

    with pytest.raises(DomainError) as recusa:
        _emitir(edital, gestor, chave="128-acervo-sucessao", motivo="Conferência.")

    assert recusa.value.code == CODIGO
    assert ato_vigente(edital=edital, marco_id=MARCO) == do_acervo

    # Quando o resultado chega, o ato do acervo fica obsoleto, e a sucessão é aceita.
    _avaliar(edital, gestor, pontuada, inscricoes, ["90.0000"], chave="128-acervo-avaliar")
    _emitir(edital, gestor, chave="128-acervo-sucessao-2", motivo="Resultados consolidados.")
    sucessor = ato_vigente(edital=edital, marco_id=MARCO)
    assert sucessor != do_acervo and sucessor.ato_anterior_id == do_acervo.id


def test_a_repeticao_de_um_pedido_atendido_devolve_o_desfecho(sem_avaliacao, gestor, monkeypatch):
    """FR-4209: a repetição não passa pela regra; devolve o que o primeiro pedido declarou."""
    edital, _, _ = sem_avaliacao
    with monkeypatch.context() as desligada:
        desligada.setattr(ordem_sem_resultado, "recusar", lambda proposta: None)
        proposta = calcular_ordem(edital=edital, perfil_id=PROFILE_ID, marco_id=MARCO)
        argumentos = {
            "actor": gestor,
            "processo_id": edital.processo_id,
            "edital_id": edital.id,
            "perfil_id": PROFILE_ID,
            "marco_id": MARCO,
            "idempotency_key": "128-repeticao",
            "correlation_id": "teste-128",
            "confirmacao_do_calculo": assinatura_da_proposta(proposta),
        }
        primeiro = emitir_ordem(**argumentos)

    assert emitir_ordem(**argumentos) == primeiro
    assert AtoDeOrdenacao.objects.filter(edital=edital).count() == 1
