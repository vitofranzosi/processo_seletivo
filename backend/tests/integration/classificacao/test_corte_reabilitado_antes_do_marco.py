"""A reabilitação de quem foi eliminado **antes da última** Etapa do marco, com o corte já emitido.

Registro em `doc/achado-reabilitado-antes-do-marco-nao-alcanca-o-corte.md`. **Este arquivo prende o
comportamento de hoje, e não a norma**: a pergunta de se o corte deveria acusar a reabilitação está
com o usuário. Escolhida uma saída que mude o comportamento, os testes marcados como *achado* são os
que viram — e o docstring de cada um diz qual.

O cenário de `tests/fixtures/corte.py` não serve: o marco dele enumera uma Etapa só, e nela quem é
eliminado continua no universo do ato. Aqui o marco enumera **duas** — a *Análise documental*,
pontuada e eliminatória, e a *Prova didática* —, e a última é a que delimita o universo
(`calcular_ordem`, `_ultima_etapa`, `restringir_a_participantes`).

```text
Análise documental   601: 90   602: 85   603: 80   604: 50 → ELIMINADA
Prova didática       601: 90   602: 80   603: 70   (604 não participa)
ordem                601, 602, 603          corte (alvo 2)   601, 602
recurso deferido     604 HABILITADA na Análise documental
```
"""

from decimal import Decimal

import pytest

from processo_seletivo.classificacao.application.calculo import calcular_ordem
from processo_seletivo.classificacao.application.corte import estado_do_corte
from processo_seletivo.classificacao.application.emissao import assinatura_da_proposta, emitir_ordem
from processo_seletivo.classificacao.application.selectors import ato_vigente, estado_do_marco
from processo_seletivo.classificacao.models import Corte
from processo_seletivo.comissoes.domain.funcoes import Funcao
from processo_seletivo.resultados.application.consolidacao import consolidar
from processo_seletivo.resultados.application.prontidao import impedimento_do_corte, participacao
from processo_seletivo.resultados.models import ResultadoEtapa
from tests.fixtures.comissao import alocar_em, constituir, inscrever
from tests.fixtures.corte import ENTREVISTA, MARCO, emitir, rascunho
from tests.fixtures.edital import PROFILE_ID
from tests.fixtures.mesa import concluir_como, distribuir_para
from tests.fixtures.publicacao import publish_original

pytestmark = [pytest.mark.integration, pytest.mark.django_db(transaction=True)]

PREFIXO = "reabilitado-antes"


def _rascunho(*, enumerar_documental):
    """O rascunho do corte, com a *Análise documental* enumerada pelo marco ou não."""
    base, pontuada = rascunho()
    documental = base["stages"][0]
    if enumerar_documental:
        documental["classificatory"] = True
        documental["weight"] = "1.0000"
        base["profiles"][0]["classificationMilestones"][0]["stages"] = [
            documental["id"],
            pontuada["id"],
        ]
    return base, documental, pontuada


def _avaliar_e_consolidar(gestor, contexto, etapa_id, notas, *, chave):
    contexto = {**contexto, "etapa": etapa_id}
    inscricoes = list(notas)
    distribuir_para(contexto, gestor, ["joao"], inscricoes, chave=f"{chave}-lote")
    for inscricao, nota in notas.items():
        concluir_como(contexto, "joao", inscricao, pontuacao=nota)
    consolidar(
        actor=gestor,
        processo_id=contexto["edital"].processo_id,
        edital_id=contexto["edital"].id,
        etapa_id=etapa_id,
        inscricao_ids=[item.id for item in inscricoes],
        idempotency_key=f"{chave}-consolidar",
        correlation_id="teste-reabilitado-antes",
    )


def _montar(gestor, api_client, manager_headers, process_payload, *, enumerar_documental):
    draft, documental, pontuada = _rascunho(enumerar_documental=enumerar_documental)
    edital = publish_original(api_client, manager_headers, process_payload, draft=draft)
    membros = constituir(
        gestor,
        edital.processo,
        [("maria", Funcao.PRESIDENTE), ("joao", Funcao.MEMBRO)],
        prefixo=PREFIXO,
    )
    for etapa in (documental, pontuada):
        alocar_em(gestor, edital.processo, membros["joao"], edital, etapa["id"])
    contexto = {"edital": edital, "processo": edital.processo, "membros": membros}
    inscricoes = inscrever(edital, 4, primeiro=601)

    _avaliar_e_consolidar(
        gestor,
        contexto,
        documental["id"],
        dict(zip(inscricoes, ("90.0000", "85.0000", "80.0000", "50.0000"), strict=True)),
        chave=f"{PREFIXO}-documental",
    )
    _avaliar_e_consolidar(
        gestor,
        contexto,
        pontuada["id"],
        dict(zip(inscricoes[:3], ("90.0000", "80.0000", "70.0000"), strict=True)),
        chave=f"{PREFIXO}-didatica",
    )
    emitir_ordem(
        actor=gestor,
        processo_id=edital.processo_id,
        edital_id=edital.id,
        perfil_id=PROFILE_ID,
        marco_id=MARCO,
        idempotency_key=f"{PREFIXO}-ordem",
        correlation_id="teste-reabilitado-antes",
        confirmacao_do_calculo=assinatura_da_proposta(
            calcular_ordem(edital=edital, perfil_id=PROFILE_ID, marco_id=MARCO)
        ),
    )
    emitir(edital, gestor, chave=f"{PREFIXO}-corte")
    return edital, documental, pontuada, inscricoes


@pytest.fixture
def cenario(gestor, api_client, manager_headers, process_payload):
    """O marco enumera as duas Etapas: é o caso do MAT do 72/2026."""
    return _montar(gestor, api_client, manager_headers, process_payload, enumerar_documental=True)


@pytest.fixture
def cenario_sem_enumerar(gestor, api_client, manager_headers, process_payload):
    """O marco enumera só a Prova didática; a Análise documental elimina, mas não pontua."""
    return _montar(gestor, api_client, manager_headers, process_payload, enumerar_documental=False)


def _reabilitar(edital, inscricao, etapa_id):
    """O recurso deferido que troca a eliminação por habilitação, pelo caminho da `018`."""
    from processo_seletivo.publicacoes.models_retificacao import VersaoConsolidada
    from tests.fixtures.recursos import admitir, decidir, interpor, superar

    superado = ResultadoEtapa.vigentes.get(edital=edital, inscricao=inscricao, etapa_id=etapa_id)
    assert superado.consequencia == ResultadoEtapa.Consequencia.ELIMINADA
    versao = VersaoConsolidada.objects.filter(edital=edital).latest("valid_from")
    recurso = interpor(
        inscricao=inscricao, versao=versao, resultado=superado, protocolo="REC-2026-REAB0001"
    )
    admitir(recurso)
    decisao = decidir(
        recurso,
        protegido=superado,
        consequencia=ResultadoEtapa.Consequencia.HABILITADA,
        forma=superado.forma,
        pontuacao=Decimal("75.0000"),
        sentido=superado.sentido,
        versao=versao,
    )
    return superar(
        superado,
        decisao,
        pontuacao=Decimal("75.0000"),
        consequencia=ResultadoEtapa.Consequencia.HABILITADA,
    )


def _causas_do_corte(edital):
    estado = estado_do_corte(edital=edital, perfil_id=PROFILE_ID, marco_id=MARCO)
    return estado["obsoleto"], [item["tipo"] for item in estado["causas"]]


# --- a premissa: o cenário é o que o achado descreve -------------------------------------------


def test_quem_foi_eliminado_na_primeira_etapa_do_marco_fica_fora_do_ato(cenario):
    edital, documental, pontuada, inscricoes = cenario
    ato = ato_vigente(edital=edital, marco_id=MARCO)
    corte = Corte.objects.get()

    assert set(ato.universo["participants"]) == {str(item.id) for item in inscricoes[:3]}
    assert {item["stageId"] for item in ato.universo["stageResults"]} == {
        str(documental["id"]),
        str(pontuada["id"]),
    }, "as duas Etapas produziram a ordem, e a Análise documental está entre elas"
    assert corte.ato_id == ato.id
    assert _causas_do_corte(edital) == (False, [])
    assert impedimento_do_corte(edital, ENTREVISTA) is None


# --- o achado, percorrido -----------------------------------------------------------------------


def test_achado_a_reabilitacao_antes_da_ultima_etapa_nao_obsoleta_o_corte(cenario):
    """**O achado.** Muda se a saída escolhida for alargar a pergunta ou delegar à ordem.

    A pessoa reabilitada nunca esteve em `participants`, e `_reingressou` só pergunta ali. Nenhuma
    das quatro causas aparece — e a decisão 008 da `014` diz que o corte *fica obsoleto*.
    """
    edital, documental, _pontuada, inscricoes = cenario

    _reabilitar(edital, inscricoes[3], documental["id"])

    assert _causas_do_corte(edital) == (False, [])


def test_achado_a_etapa_governada_segue_recebendo_trabalho(cenario):
    """**O achado, na consequência que a `FR-228` existe para impedir.**

    Muda se a saída escolhida for alargar a pergunta ou delegar à ordem; fica se for manter.
    """
    edital, documental, _pontuada, inscricoes = cenario

    _reabilitar(edital, inscricoes[3], documental["id"])

    assert impedimento_do_corte(edital, ENTREVISTA) is None
    participantes, _, _ = participacao(edital=edital, etapa_id=ENTREVISTA)
    assert participantes == {inscricoes[0].id, inscricoes[1].id}, (
        "a faixa antiga continua decidindo quem a Entrevista recebe"
    )


# --- o que já acusa, e por isso informa as saídas -----------------------------------------------


def test_a_ordem_ja_acusa_a_reabilitacao_antes_mesmo_da_prova_didatica(cenario):
    """A ordem fica obsoleta **no deferimento**, e não só depois do Resultado na Etapa seguinte.

    É o que a saída "delegar à ordem" leria: a reabilitada volta ao conjunto de participantes da
    última Etapa (Regra 1 deixa de excluí-la; o gate da Regra 2 passa a admiti-la), e a proposta
    de agora já a conta — sem posição, porque ainda não tem nota ali.
    """
    edital, documental, _pontuada, inscricoes = cenario

    _reabilitar(edital, inscricoes[3], documental["id"])

    estado = estado_do_marco(edital=edital, marco_id=MARCO)
    assert estado["obsoleto"] is True, estado["divergencias"]
    reingresso = next(
        item for item in estado["divergencias"] if item["tipo"] == "participantes_alterados"
    )
    assert reingresso["reingressaram"] == [str(inscricoes[3].id)]


def test_a_publicacao_da_ordem_ja_e_impedida(cenario):
    """A `FR-219` não depende do corte aqui: a ordem é recusada antes, por *reingresso pendente*.

    O que o achado deixa sem guarda é o trabalho da Etapa governada (`FR-228`), e não a publicação.
    """
    from processo_seletivo.divulgacao.domain.publicabilidade import REINGRESSO_PENDENTE, aferir

    edital, documental, _pontuada, inscricoes = cenario
    _reabilitar(edital, inscricoes[3], documental["id"])

    afericao = aferir(
        edital=edital,
        marco_id=MARCO,
        ato=ato_vigente(edital=edital, marco_id=MARCO),
        natureza="PRELIMINAR",
    )

    assert afericao.codigo == REINGRESSO_PENDENTE


def test_achado_o_mesmo_quando_a_etapa_anterior_nao_e_enumerada(cenario_sem_enumerar):
    """**O achado é mais largo do que o título dele.** Muda junto com o caso enumerado.

    A Regra 1 exclui quem foi eliminado em **qualquer** Etapa anterior à última do marco, enumerada
    ou não. Aqui a Análise documental nem produz a ordem — e a reabilitação nela muda o universo do
    ato do mesmo jeito.
    """
    edital, documental, _pontuada, inscricoes = cenario_sem_enumerar
    ato = ato_vigente(edital=edital, marco_id=MARCO)
    assert str(inscricoes[3].id) not in ato.universo["participants"]

    _reabilitar(edital, inscricoes[3], documental["id"])

    assert estado_do_marco(edital=edital, marco_id=MARCO)["obsoleto"] is True
    assert _causas_do_corte(edital) == (False, [])
    assert impedimento_do_corte(edital, ENTREVISTA) is None


def test_o_contraste_quem_estava_no_ato_e_acusado(cenario):
    """O mesmo deferimento, na mesma Etapa, de quem **estava** em `participants`: aí a causa sai.

    Prova que a diferença do achado é o universo em que a pergunta é feita, e não a Etapa: a
    Análise documental está entre as que produziram a ordem.
    """
    from tests.integration.classificacao.test_corte_obsoleto import _superar_resultado

    edital, documental, _pontuada, inscricoes = cenario

    _superar_resultado(edital, inscricoes[2].id, documental["id"])

    assert _causas_do_corte(edital) == (True, ["participante_reingressou"])
    assert impedimento_do_corte(edital, ENTREVISTA) is not None


def test_o_corte_so_acusa_depois_da_ordem_sucessora(cenario, gestor):
    """A cronologia do achado até o fim: a causa que chega é *ordem sucedida*, e só aqui."""
    edital, documental, pontuada, inscricoes = cenario
    _reabilitar(edital, inscricoes[3], documental["id"])
    _avaliar_e_consolidar(
        gestor,
        {"edital": edital, "processo": edital.processo, "membros": _membros(edital)},
        pontuada["id"],
        {inscricoes[3]: "95.0000"},
        chave=f"{PREFIXO}-didatica-reabilitada",
    )
    assert _causas_do_corte(edital) == (False, []), "nem com o Resultado na Prova didática"

    emitir_ordem(
        actor=gestor,
        processo_id=edital.processo_id,
        edital_id=edital.id,
        perfil_id=PROFILE_ID,
        marco_id=MARCO,
        idempotency_key=f"{PREFIXO}-ordem-sucessora",
        correlation_id="teste-reabilitado-antes",
        confirmacao_do_calculo=assinatura_da_proposta(
            calcular_ordem(edital=edital, perfil_id=PROFILE_ID, marco_id=MARCO),
            ato_vigente=ato_vigente(edital=edital, marco_id=MARCO),
        ),
        motivo="recurso deferido na Análise documental",
    )

    assert _causas_do_corte(edital) == (True, ["ordem_sucedida"])
    assert impedimento_do_corte(edital, ENTREVISTA) is not None
    # O que estava em jogo na janela: com 75 + 95, a reabilitada passa a 602, que a faixa antiga
    # mandava à Entrevista — e que a geração sucessora, com alvo 2, deixaria de fora.
    sucessora = ato_vigente(edital=edital, marco_id=MARCO)
    ordem = [
        str(item)
        for item in sucessora.posicoes.order_by("posicao").values_list("inscricao_id", flat=True)
    ]
    assert ordem == [str(inscricoes[indice].id) for indice in (0, 3, 1, 2)]


def _membros(edital):
    from processo_seletivo.comissoes.models import MembroComissao

    return {
        membro.identity_subject: membro
        for membro in MembroComissao.objects.filter(processo=edital.processo)
    }
