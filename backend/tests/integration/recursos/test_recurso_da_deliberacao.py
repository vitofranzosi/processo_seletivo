"""O recurso contra o Resultado deliberado corrige o desfecho, e não refaz a votação (165).

```text
FR-7069  impedimento   os autores dos pareceres e quem tem parecer pendente não julgam
FR-7070  correção      o julgador fixa o sentido; o sucessor é RECURSO, e os pareceres ficam
FR-7071  reavaliação   recusada antes de gravar; nenhuma decisão, nenhuma reserva
FR-7072  piora         a correção mais grave que o recorrido é indeferimento
FR-7077  titular       lê os pareceres desfavoráveis, sem autoria e à parte do motivo
FR-7081  julgador      lê todos os pareceres, com autoria
```
"""

import pytest

from processo_seletivo.auditoria.models import IdempotencyRecord
from processo_seletivo.recursos.application.julgar import julgar
from processo_seletivo.recursos.application.selectors import (
    pareceres_do_titular,
    textos_da_deliberacao,
)
from processo_seletivo.recursos.domain.elegibilidade import (
    DELIBEROU,
    PENDENTE,
    impedimento,
)
from processo_seletivo.recursos.models import DecisaoRecurso
from processo_seletivo.resultados.models import ParecerDaDeliberacao, ResultadoEtapa
from processo_seletivo.shared.api.problems import DomainError
from tests.conftest import ator_institucional
from tests.fixtures.deliberacao import (
    concluir_pareceres,
    consolidar_na,
    distribuir_na_hetero,
    montar_colegiada,
)
from tests.fixtures.recursos import admitir, interpor
from tests.fixtures.recursos_us4 import julgador

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.integration]

F, D = "FAVORAVEL", "DESFAVORAVEL"


@pytest.fixture
def deliberado(gestor, api_client, manager_headers):
    cenario = montar_colegiada(gestor, api_client, manager_headers, seed=1701)
    maria = cenario["inscricoes"][0]
    distribuir_na_hetero(cenario, gestor, [maria], chave="hetero-1701")
    concluir_pareceres(cenario, maria, {"ana": D, "bruno": D, "carla": F})
    consolidar_na(cenario, cenario["hetero"], [maria], chave="consolidar-1701")
    resultado = ResultadoEtapa.vigentes.get(etapa_id=cenario["hetero"], inscricao=maria)
    recurso = interpor(inscricao=maria, versao=resultado.versao, resultado=resultado)
    admitir(recurso)
    return {"cenario": cenario, "resultado": resultado, "recurso": recurso, "maria": maria}


def _julgar(deliberado, especie, *, chave, sentido="", ator=None):
    return julgar(
        actor=ator or julgador(),
        recurso_id=deliberado["recurso"].id,
        especie=especie,
        motivacao="O fenótipo está bem descrito na gravação.",
        etapa_id=deliberado["cenario"]["hetero"],
        sentido=sentido,
        assinatura_do_resultado=str(deliberado["resultado"].id),
        idempotency_key=chave,
    )


def test_os_autores_dos_pareceres_nao_julgam(deliberado):
    """FR-7069: cada um dos três, e não só um."""
    for nome in ("ana", "bruno", "carla"):
        ator = ator_institucional(nome, "recurso:julgar")
        assert impedimento(ator, deliberado["recurso"]) == DELIBEROU


def test_quem_tem_parecer_pendente_nao_julga(deliberado, gestor):
    """FR-7069: com Atribuição ativa e sem conclusão sobre o par, julgaria sem ver o que julga."""
    from django.utils import timezone

    from processo_seletivo.avaliacoes.models import Atribuicao
    from processo_seletivo.comissoes.domain.funcoes import Funcao
    from tests.fixtures.comissao import constituir

    cenario = deliberado["cenario"]
    davi = constituir(gestor, cenario["processo"], [("davi", Funcao.MEMBRO)], prefixo="davi")[
        "davi"
    ]
    Atribuicao.objects.create(
        membro=davi,
        edital=cenario["edital"],
        etapa_id=cenario["hetero"],
        inscricao=deliberado["maria"],
        criado_em=timezone.now(),
        criado_por="teste",
    )

    ator = ator_institucional("davi", "recurso:julgar")
    assert impedimento(ator, deliberado["recurso"]) == PENDENTE


def test_a_correcao_fixada_cria_o_sucessor_sem_tocar_os_pareceres(deliberado):
    """FR-7070, cenário 1 da US5."""
    decisao, sucessor = _julgar(
        deliberado, DecisaoRecurso.Especie.CORRECAO_FIXADA, sentido=F, chave="corrigir"
    )

    assert sucessor.origem == ResultadoEtapa.Origem.RECURSO
    assert sucessor.consequencia == ResultadoEtapa.Consequencia.HABILITADA
    assert sucessor.regra_de_deliberacao == "" and sucessor.favoraveis is None
    assert ParecerDaDeliberacao.objects.filter(resultado=deliberado["resultado"]).count() == 3
    assert not ParecerDaDeliberacao.objects.filter(resultado=sucessor).exists()
    assert decisao.sentido == F


def test_a_reavaliacao_e_recusada_antes_de_gravar(deliberado):
    """FR-7071, D-007: nenhuma decisão, nenhuma reserva de idempotência."""
    with pytest.raises(DomainError) as recusa:
        _julgar(deliberado, DecisaoRecurso.Especie.REAVALIACAO_DETERMINADA, chave="reavaliar")

    assert recusa.value.code == "reavaliacao_colegiada_indisponivel"
    assert "correção fixada" in recusa.value.detail
    assert not DecisaoRecurso.objects.filter(recurso=deliberado["recurso"]).exists()
    assert not IdempotencyRecord.objects.filter(key="reavaliar").exists()


def test_o_indeferimento_segue_como_hoje(deliberado):
    decisao, sucessor = _julgar(deliberado, DecisaoRecurso.Especie.INDEFERIDO, chave="indeferir")

    assert sucessor is None
    assert decisao.especie == DecisaoRecurso.Especie.INDEFERIDO
    assert ResultadoEtapa.vigentes.get(pk=deliberado["resultado"].pk)


def test_o_titular_le_os_desfavoraveis_sem_autoria(deliberado):
    """FR-7077, D-009: o recurso pendente mantém os textos visíveis; os favoráveis não aparecem."""
    resultado = deliberado["resultado"]
    lido = pareceres_do_titular(deliberado["maria"], [{"id": resultado.id, "habilitada": False}])[
        resultado.id
    ]

    assert lido["estado"] == "visivel"
    assert lido["textos"] == ["Parecer de ana: desfavoravel.", "Parecer de bruno: desfavoravel."]
    assert "carla" not in lido["texto"]
    assert "ana" not in resultado.motivo and "bruno" not in resultado.motivo


def test_o_julgador_le_todos_com_autoria(deliberado):
    """FR-7081."""
    textos = textos_da_deliberacao(deliberado["resultado"])

    assert {(avaliacao.identity_subject, avaliacao.sentido) for avaliacao, _ in textos} == {
        ("ana", D),
        ("bruno", D),
        ("carla", F),
    }
    assert all(texto for _, texto in textos)
