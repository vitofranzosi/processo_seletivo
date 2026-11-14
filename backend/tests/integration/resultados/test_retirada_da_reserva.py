"""O desfecho desfavorável da Etapa restrita tira da reserva, e deixa seguir (164, US2, US6).

O Edital da `163` (`tests/fixtures/alcance.py`): Análise documental para todas, Heteroidentificação
só para `PPI`, Prova para todas. Seis inscrições: duas `PPI`, duas `PCD`, duas sem Modalidade.

```text
FR-7007  consolidação     o desfavorável sob "retira" produz RETIRADA_DA_RESERVA
FR-7008  motivo           cita o rótulo, a reserva perdida e a ampla mantida
FR-7011  progressão       a retirada segue para a Prova, como a habilitada; a eliminada não
FR-7009  Ocorrência       a ausência aplica o efeito da ausência, e o motivo diz "não compareceu"
FR-7003  um por Etapa     todo desfavorável por avaliação tem o mesmo efeito
SC-2332  "elimina"        o efeito declarado "elimina" produz o de antes
```
"""

import pytest

from processo_seletivo.resultados.application.consolidacao import consolidar
from processo_seletivo.resultados.application.ocorrencia import registrar_ocorrencia
from processo_seletivo.resultados.application.prontidao import participa_da_etapa, participacao
from processo_seletivo.resultados.models import ResultadoEtapa
from tests.conftest import ator_institucional
from tests.fixtures.alcance import MODALIDADE_PCD, MODALIDADE_PPI, montar_com_alcance
from tests.fixtures.comissao import inscrever
from tests.fixtures.mesa import concluir_como, distribuir_para

pytestmark = [pytest.mark.integration, pytest.mark.django_db]

MODALIDADES = {0: MODALIDADE_PPI, 1: MODALIDADE_PPI, 2: MODALIDADE_PCD, 3: MODALIDADE_PCD}
RETIRADA = ResultadoEtapa.Consequencia.RETIRADA_DA_RESERVA
ELIMINADA = ResultadoEtapa.Consequencia.ELIMINADA


def _montar(gestor, api_client, manager_headers, *, seed, **efeitos):
    cenario = montar_com_alcance(
        gestor, api_client, manager_headers, seed=seed, codigo=str(seed), **efeitos
    )
    cenario["inscricoes"] = inscrever(
        cenario["edital"], 6, primeiro=1, modalidades=MODALIDADES, perfil=cenario["perfil"]
    )
    inscricoes = cenario["inscricoes"]
    distribuir_para(cenario, gestor, ["joao"], inscricoes, chave=f"analise-{seed}")
    for inscricao in inscricoes:
        concluir_como(cenario, "joao", inscricao, pontuacao="80")
    _consolidar(cenario, cenario["analise"], inscricoes, chave=f"consolidar-analise-{seed}")
    return cenario


def _consolidar(cenario, etapa, inscricoes, *, chave):
    return consolidar(
        actor=ator_institucional("maria"),
        processo_id=cenario["processo"].id,
        edital_id=cenario["edital"].id,
        etapa_id=etapa,
        inscricao_ids=[i.id for i in inscricoes],
        idempotency_key=chave,
        correlation_id="teste",
    )


def _concluir_na_hetero(cenario, gestor, sentidos, *, seed):
    """`sentidos`: `{inscricao: "FAVORAVEL" | "DESFAVORAVEL"}` — e consolida as que concluiu."""
    na_hetero = {**cenario, "etapa": cenario["hetero"]}
    distribuir_para(na_hetero, gestor, ["joao"], list(sentidos), chave=f"hetero-{seed}")
    for inscricao, sentido in sentidos.items():
        concluir_como(na_hetero, "joao", inscricao, sentido=sentido)
    _consolidar(cenario, cenario["hetero"], list(sentidos), chave=f"consolidar-hetero-{seed}")


def _resultado(cenario, inscricao):
    return ResultadoEtapa.vigentes.get(etapa_id=cenario["hetero"], inscricao=inscricao)


def _ausencia(cenario, inscricoes, *, chave):
    return registrar_ocorrencia(
        actor=ator_institucional("maria"),
        processo_id=cenario["processo"].id,
        edital_id=cenario["edital"].id,
        etapa_id=cenario["hetero"],
        inscricao_ids=[i.id for i in inscricoes],
        motivo="Não compareceu à entrevista.",
        idempotency_key=chave,
        correlation_id="teste",
    )


def test_o_desfavoravel_retira_da_reserva_pelo_padrao(gestor, api_client, manager_headers):
    """FR-7001, FR-7007, FR-7008: sem declaração, a Etapa restrita retira, e o motivo diz o quê."""
    cenario = _montar(gestor, api_client, manager_headers, seed=1641)
    maria, outra = cenario["inscricoes"][:2]

    _concluir_na_hetero(cenario, gestor, {maria: "DESFAVORAVEL", outra: "FAVORAVEL"}, seed=1641)

    resultado = _resultado(cenario, maria)
    assert resultado.consequencia == RETIRADA
    assert "Não confirmada" in resultado.motivo
    assert "deixa de concorrer pela reserva Pretos e pardos" in resultado.motivo
    assert "continua na ampla concorrência" in resultado.motivo
    assert _resultado(cenario, outra).consequencia == ResultadoEtapa.Consequencia.HABILITADA


def test_a_retirada_segue_para_a_etapa_seguinte(gestor, api_client, manager_headers):
    """FR-7011: a Prova exige a habilitação da Heteroidentificação, e a retirada a satisfaz."""
    cenario = _montar(gestor, api_client, manager_headers, seed=1642)
    maria, outra = cenario["inscricoes"][:2]
    _concluir_na_hetero(cenario, gestor, {maria: "DESFAVORAVEL", outra: "FAVORAVEL"}, seed=1642)

    participantes, eliminadas, aguardando = participacao(
        edital=cenario["edital"], etapa_id=cenario["prova"]
    )

    assert maria.id in participantes
    assert maria.id not in eliminadas | aguardando
    assert participa_da_etapa(
        edital=cenario["edital"], etapa_id=cenario["prova"], inscricao_id=maria.id
    )


def test_o_efeito_declarado_elimina_como_antes(gestor, api_client, manager_headers):
    """SC-2332, D-009: "elimina" é a eliminação de hoje, inteira — fora da Prova também."""
    cenario = _montar(gestor, api_client, manager_headers, seed=1643, efeito="ELIMINATION")
    maria, outra = cenario["inscricoes"][:2]
    _concluir_na_hetero(cenario, gestor, {maria: "DESFAVORAVEL", outra: "FAVORAVEL"}, seed=1643)

    participantes, eliminadas, _ = participacao(edital=cenario["edital"], etapa_id=cenario["prova"])

    assert _resultado(cenario, maria).consequencia == ELIMINADA
    assert "reserva" not in _resultado(cenario, maria).motivo
    assert maria.id in eliminadas
    assert maria.id not in participantes


def test_a_ausencia_tem_o_mesmo_efeito_pelo_padrao(gestor, api_client, manager_headers):
    """FR-7004, FR-7009: sem declaração da ausência, ela retira, e o motivo diz a ausência."""
    cenario = _montar(gestor, api_client, manager_headers, seed=1644)
    joao = cenario["inscricoes"][1]

    _ausencia(cenario, [joao], chave="ausencia-1644")

    resultado = _resultado(cenario, joao)
    assert resultado.consequencia == RETIRADA
    assert resultado.origem == ResultadoEtapa.Origem.OCORRENCIA
    assert resultado.motivo.startswith("Não compareceu à entrevista.")
    assert "continua na ampla concorrência" in resultado.motivo


def test_a_ausencia_elimina_quando_o_edital_o_declara(gestor, api_client, manager_headers):
    """US6: o 57/2026, 8.11 — o ausente é eliminado; o indeferido só deixa a reserva."""
    cenario = _montar(
        gestor, api_client, manager_headers, seed=1645, efeito_da_ausencia="ELIMINATION"
    )
    maria, joao = cenario["inscricoes"][:2]

    _ausencia(cenario, [joao], chave="ausencia-1645")
    _concluir_na_hetero(cenario, gestor, {maria: "DESFAVORAVEL"}, seed=1645)

    assert _resultado(cenario, joao).consequencia == ELIMINADA
    # FR-7009: o desfavorável por avaliação nunca aplica o efeito da ausência.
    assert _resultado(cenario, maria).consequencia == RETIRADA
    participantes, eliminadas, _ = participacao(edital=cenario["edital"], etapa_id=cenario["prova"])
    assert joao.id in eliminadas
    assert maria.id in participantes


def test_a_ausencia_retira_mesmo_quando_o_desfavoravel_elimina(gestor, api_client, manager_headers):
    """FR-7009, o caso inverso: cada efeito vale para o seu fundamento."""
    cenario = _montar(
        gestor,
        api_client,
        manager_headers,
        seed=1646,
        efeito="ELIMINATION",
        efeito_da_ausencia="RESERVE_REMOVAL",
    )
    maria, joao = cenario["inscricoes"][:2]

    _ausencia(cenario, [joao], chave="ausencia-1646")
    _concluir_na_hetero(cenario, gestor, {maria: "DESFAVORAVEL"}, seed=1646)

    assert _resultado(cenario, joao).consequencia == RETIRADA
    assert _resultado(cenario, maria).consequencia == ELIMINADA


def test_a_etapa_para_todas_continua_eliminando(gestor, api_client, manager_headers):
    """FR-7002, FR-7009: sem reserva de onde retirar, a ausência e o desfavorável eliminam."""
    cenario = _montar(gestor, api_client, manager_headers, seed=1647, alcance=None)
    ampla = cenario["inscricoes"][4]

    _ausencia(cenario, [ampla], chave="ausencia-1647")

    assert _resultado(cenario, ampla).consequencia == ELIMINADA
