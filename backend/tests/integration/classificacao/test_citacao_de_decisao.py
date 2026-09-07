"""A pertinência da citação é conferida **no banco**, e não apenas no comando.

Uma gravação direta que ligasse a decisão pertinente ao marco `M1` a um ato do marco `M2` do mesmo
Edital liberaria indevidamente a publicação definitiva de `M2` — sem que ninguém tivesse corrigido
o vício reconhecido. É o mesmo argumento de `check_ordering_act_provenance`: citação é proveniência,
e proveniência que só o comando confere é proveniência que qualquer outro caminho de escrita desfaz
(T-015, FR-112).

```text
espécie   só PROVIDENCIA_A_JUSANTE gera ato a jusante
Edital    a decisão e o ato pertencem ao mesmo Edital
Perfil    o Perfil da Inscrição que recorreu é o do ato
Marco     o marco do ato alcança a Etapa que o recurso alcança
```

Exige PostgreSQL: a conferência é uma trigger PL/pgSQL, e um teste que passasse em SQLite provaria
o contrário do que afirma.
"""

import pytest
from django.db.utils import ProgrammingError

from processo_seletivo.classificacao.models import CitacaoDeDecisao
from processo_seletivo.recursos.application.julgar import julgar
from processo_seletivo.recursos.models import DecisaoRecurso
from tests.conftest import ator_institucional
from tests.fixtures.divulgacao import emitir
from tests.fixtures.recursos_us4 import cenario_julgavel, julgador

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.integration]


@pytest.fixture
def cenario(gestor, api_client, manager_headers, process_payload):
    """Dois marcos no mesmo Edital, e uma providência determinada sobre a Etapa do intermediário."""
    peca = cenario_julgavel(
        gestor,
        api_client,
        manager_headers,
        process_payload,
        seed=126,
        codigo="0826",
        na_primeira_etapa=True,
    )
    decisao, _ = julgar(
        actor=julgador(),
        recurso_id=peca["recurso"].id,
        especie=DecisaoRecurso.Especie.PROVIDENCIA_A_JUSANTE,
        motivacao="Emita-se novo ato corrigindo o critério de desempate.",
        idempotency_key="providencia-citacao",
    )
    return {**peca, "decisao": decisao}


def test_a_citacao_pertinente_e_aceita(cenario):
    """A prova de que as recusas abaixo não são a trigger recusando tudo."""
    marco = cenario["cenario"]["marco_do_recurso"]
    ato = emitir(cenario["cenario"], _gestor(), marco=marco, chave="emitir-citacao-ok")

    citacao = CitacaoDeDecisao.objects.create(ato=ato, decisao=cenario["decisao"])

    assert citacao.pk is not None


def test_citacao_para_ato_de_outro_marco_e_recusada(cenario):
    """O caso que a trigger existe para impedir: liberar a definitiva de um marco alheio."""
    outro = cenario["cenario"]["marco"]
    ato = emitir(cenario["cenario"], _gestor(), marco=outro, chave="emitir-citacao-outro-marco")

    with pytest.raises(ProgrammingError, match="pertinent to another milestone"):
        CitacaoDeDecisao.objects.create(ato=ato, decisao=cenario["decisao"])


def test_citacao_de_especie_diferente_e_recusada(
    cenario, gestor, api_client, manager_headers, process_payload
):
    """Citar um indeferimento seria declarar cumprida uma providência que nunca foi determinada."""
    outra = cenario_julgavel(
        gestor, api_client, manager_headers, process_payload, seed=127, codigo="0827"
    )
    indeferimento, _ = julgar(
        actor=julgador(),
        recurso_id=outra["recurso"].id,
        especie=DecisaoRecurso.Especie.INDEFERIDO,
        motivacao="A nota corresponde ao que foi entregue.",
        idempotency_key="indeferir-citacao",
    )
    ato = emitir(outra["cenario"], _gestor(), chave="emitir-citacao-especie")

    with pytest.raises(ProgrammingError, match="determined no downstream remedy"):
        CitacaoDeDecisao.objects.create(ato=ato, decisao=indeferimento)


def test_citacao_de_decisao_de_outro_edital_e_recusada(
    cenario, gestor, api_client, manager_headers, process_payload
):
    """Edital e Perfil são conferidos juntos: a decisão de outro certame não alcança este ato."""
    alheio = cenario_julgavel(
        gestor, api_client, manager_headers, process_payload, seed=128, codigo="0828"
    )
    ato = emitir(alheio["cenario"], _gestor(), chave="emitir-citacao-alheia")

    with pytest.raises(ProgrammingError, match="another edital or profile"):
        CitacaoDeDecisao.objects.create(ato=ato, decisao=cenario["decisao"])


def test_a_citacao_e_append_only(cenario):
    """Apagá-la reabriria uma providência já cumprida, sem deixar rastro de quem a reabriu."""
    marco = cenario["cenario"]["marco_do_recurso"]
    ato = emitir(cenario["cenario"], _gestor(), marco=marco, chave="emitir-citacao-imutavel")
    citacao = CitacaoDeDecisao.objects.create(ato=ato, decisao=cenario["decisao"])

    with pytest.raises(TypeError):
        citacao.delete()
    with pytest.raises(TypeError):
        citacao.save()

    assert CitacaoDeDecisao.objects.filter(pk=citacao.pk).exists()


def test_a_mesma_decisao_nao_e_citada_duas_vezes_pelo_mesmo_ato(cenario):
    """`UNIQUE(ato, decisao)` — e **só** ele: um `UNIQUE(decisao)` criaria um beco permanente."""
    from django.db.utils import IntegrityError

    marco = cenario["cenario"]["marco_do_recurso"]
    ato = emitir(cenario["cenario"], _gestor(), marco=marco, chave="emitir-citacao-dupla")
    CitacaoDeDecisao.objects.create(ato=ato, decisao=cenario["decisao"])

    with pytest.raises(IntegrityError, match="uq_citacao_ato_decisao"):
        CitacaoDeDecisao.objects.create(ato=ato, decisao=cenario["decisao"])


def _gestor():
    return ator_institucional("carlos", "comissao:gerir")
