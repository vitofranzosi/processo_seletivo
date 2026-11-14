"""A deliberação aplica a regra publicada (165, US3).

O Edital de `tests/fixtures/deliberacao.py`: a Heteroidentificação colegiada, três pareceres, só
`PPI`, com o efeito "retira da reserva" da `164`.

```text
FR-7062  prontidão      faltam k de N; nenhuma antecipação; pronta com N
FR-7061  deliberação    a mesma combinação, três desfechos, um por regra
FR-7065  Resultado      origem DELIBERACAO, os N pareceres, a regra, a contagem, a versão vigente
FR-7066  motivo         regra e contagem, e a reserva perdida da 164
FR-7060  trilha         a consequência, sem regra nem contagem
SC-2351  reprodução     ler os pareceres e a versão chega à mesma consequência
```
"""

import pytest

from processo_seletivo.auditoria.models import RegistroAuditoria
from processo_seletivo.resultados.application.consolidacao import prever
from processo_seletivo.resultados.application.prontidao import (
    NAO_CONSOLIDAVEL,
    PRONTA,
    panorama_da_etapa,
)
from processo_seletivo.resultados.application.selectors import reproduzir_deliberacao
from processo_seletivo.resultados.domain import deliberacao
from processo_seletivo.resultados.models import ParecerDaDeliberacao, ResultadoEtapa
from tests.fixtures.deliberacao import (
    concluir_pareceres,
    consolidar_na,
    distribuir_na_hetero,
    montar_colegiada,
)

pytestmark = [pytest.mark.integration, pytest.mark.django_db]

F, D = "FAVORAVEL", "DESFAVORAVEL"


def _panorama(cenario):
    from processo_seletivo.comissoes.domain.etapas import conteudo_vigente

    conteudo = conteudo_vigente(cenario["edital"])
    vigentes = {str(etapa["id"]): etapa for etapa in conteudo["stages"]}
    etapa = vigentes[str(cenario["hetero"])]
    return panorama_da_etapa(
        edital=cenario["edital"], etapa=etapa, etapas_vigentes=vigentes, conteudo=conteudo
    )


def _resultado(cenario, inscricao):
    return ResultadoEtapa.vigentes.get(etapa_id=cenario["hetero"], inscricao=inscricao)


def test_espera_os_tres_pareceres_sem_antecipar(gestor, api_client, manager_headers):
    """FR-7062, D-005: dois Indeferido sob "confirma só por unanimidade" já decidiriam, e esperam."""
    cenario = montar_colegiada(
        gestor, api_client, manager_headers, seed=1651, regra="UNANIMOUS_FOR_FAVORABLE"
    )
    maria = cenario["inscricoes"][0]
    distribuir_na_hetero(cenario, gestor, [maria], chave="hetero-1651")
    concluir_pareceres(cenario, maria, {"ana": D, "bruno": D})

    panorama = _panorama(cenario)

    assert panorama["estados"][maria.id] == (NAO_CONSOLIDAVEL, "faltam 1 de 3 pareceres")
    # As outras duas inscrições esperam também, com nenhum dos três.
    assert panorama["contagens"]["aguardando_pareceres"] == 3
    concluir_pareceres(cenario, maria, {"carla": F})
    assert _panorama(cenario)["estados"][maria.id][0] == PRONTA


@pytest.mark.parametrize(
    "regra, sentido, consequencia, trecho",
    [
        ("MAJORITY", D, "RETIRADA_DA_RESERVA", "Indeferido por maioria: 2 de 3 pareceres"),
        (
            "UNANIMOUS_FOR_FAVORABLE",
            D,
            "RETIRADA_DA_RESERVA",
            "Indeferido por não haver unanimidade Deferido: 2 de 3 pareceres",
        ),
        (
            "UNANIMOUS_FOR_UNFAVORABLE",
            F,
            "HABILITADA",
            "Deferido por não haver unanimidade Indeferido: 1 de 3 pareceres Deferido",
        ),
    ],
)
def test_a_mesma_combinacao_sob_cada_regra(
    gestor, api_client, manager_headers, regra, sentido, consequencia, trecho
):
    """US3, FR-7061, FR-7064 a FR-7066: dois Indeferido e um Deferido, três desfechos."""
    seed = 1652 + ["MAJORITY", "UNANIMOUS_FOR_FAVORABLE", "UNANIMOUS_FOR_UNFAVORABLE"].index(regra)
    cenario = montar_colegiada(gestor, api_client, manager_headers, seed=seed, regra=regra)
    maria = cenario["inscricoes"][0]
    distribuir_na_hetero(cenario, gestor, [maria], chave=f"hetero-{seed}")
    pareceres = concluir_pareceres(cenario, maria, {"ana": D, "bruno": D, "carla": F})

    consolidar_na(cenario, cenario["hetero"], [maria], chave=f"consolidar-{seed}")

    resultado = _resultado(cenario, maria)
    assert resultado.origem == ResultadoEtapa.Origem.DELIBERACAO
    assert resultado.avaliacao_id is None
    assert resultado.sentido == sentido
    assert resultado.consequencia == consequencia
    assert resultado.regra_de_deliberacao == regra
    assert (resultado.favoraveis, resultado.desfavoraveis) == (1, 2)
    assert trecho in resultado.motivo
    assert {p.avaliacao_id for p in resultado.pareceres_da_deliberacao.all()} == {
        p.id for p in pareceres
    }
    if consequencia == "RETIRADA_DA_RESERVA":
        assert "deixa de concorrer pela reserva" in resultado.motivo
    for nome in ("ana", "bruno", "carla"):
        assert nome not in resultado.motivo


def test_a_versao_e_a_vigente_e_a_reproducao_confere(gestor, api_client, manager_headers):
    """FR-7065, SC-2351: a versão cuja regra foi aplicada, e a reprodução chega ao mesmo lugar."""
    cenario = montar_colegiada(gestor, api_client, manager_headers, seed=1656)
    maria = cenario["inscricoes"][0]
    distribuir_na_hetero(cenario, gestor, [maria], chave="hetero-1656")
    concluir_pareceres(cenario, maria, {"ana": F, "bruno": D, "carla": F})
    consolidar_na(cenario, cenario["hetero"], [maria], chave="consolidar-1656")

    resultado = _resultado(cenario, maria)
    vigente = cenario["edital"].versoes_consolidadas.latest("materialized_at")
    assert resultado.versao_id == vigente.id
    reproduzida = reproduzir_deliberacao(resultado)
    assert reproduzida.sentido == resultado.sentido == F
    assert reproduzida.favoraveis == 2


def test_a_trilha_diz_a_consequencia_sem_contagem(gestor, api_client, manager_headers):
    """FR-7060: a trilha não traz a regra nem a contagem."""
    cenario = montar_colegiada(gestor, api_client, manager_headers, seed=1657)
    maria = cenario["inscricoes"][0]
    distribuir_na_hetero(cenario, gestor, [maria], chave="hetero-1657")
    concluir_pareceres(cenario, maria, {"ana": D, "bruno": D, "carla": D})
    consolidar_na(cenario, cenario["hetero"], [maria], chave="consolidar-1657")

    resultado = _resultado(cenario, maria)
    evento = RegistroAuditoria.objects.get(aggregate_id=str(resultado.id))
    assert "retirada_da_reserva" in evento.reason
    assert "3 de 3" not in evento.reason
    assert "unanimidade" not in evento.reason and "maioria" not in evento.reason


def test_a_conferencia_e_o_ato_leem_o_mesmo_plano(gestor, api_client, manager_headers):
    """FR-7067, UX-752: a previsão mostra a deliberação, e o ato faz o que ela mostrou."""
    cenario = montar_colegiada(gestor, api_client, manager_headers, seed=1658)
    maria, joana, _ = cenario["inscricoes"]
    distribuir_na_hetero(cenario, gestor, [maria, joana], chave="hetero-1658")
    concluir_pareceres(cenario, maria, {"ana": D, "bruno": D, "carla": F})
    concluir_pareceres(cenario, joana, {"ana": F, "bruno": D})

    _etapa, consolidaveis, recusas = prever(
        edital=cenario["edital"], etapa_id=cenario["hetero"], inscricao_ids=[maria.id, joana.id]
    )

    assert [item.inscricao for item in consolidaveis] == [maria]
    linha = deliberacao.linha_da_conferencia(_etapa, consolidaveis[0].conclusao)
    assert linha == "Indeferido — 2 de 3 pareceres Indeferido, por maioria"
    assert [(r.inscricao, r.motivo) for r in recusas] == [(joana, "faltam 1 de 3 pareceres")]


@pytest.mark.django_db(transaction=True)
def test_o_banco_recusa_deliberacao_sem_pareceres(gestor, api_client, manager_headers):
    """T-006: um Resultado deliberado sem os pareceres não sobrevive ao COMMIT."""
    from django.db import DatabaseError, transaction

    cenario = montar_colegiada(gestor, api_client, manager_headers, seed=1659)
    maria = cenario["inscricoes"][0]
    vigente = cenario["edital"].versoes_consolidadas.latest("materialized_at")
    with pytest.raises(DatabaseError):
        with transaction.atomic():
            ResultadoEtapa.objects.create(
                inscricao=maria,
                edital=cenario["edital"],
                etapa_id=cenario["hetero"],
                origem=ResultadoEtapa.Origem.DELIBERACAO,
                versao_id=vigente.id,
                forma="DECISORIA",
                sentido=F,
                consequencia="HABILITADA",
                motivo="forjado",
                consolidado_em=vigente.materialized_at,
                consolidado_por="intruso",
                regra_de_deliberacao="MAJORITY",
                favoraveis=2,
                desfavoraveis=1,
            )
    assert not ResultadoEtapa.objects.filter(inscricao=maria, etapa_id=cenario["hetero"]).exists()
    assert not ParecerDaDeliberacao.objects.exists()
