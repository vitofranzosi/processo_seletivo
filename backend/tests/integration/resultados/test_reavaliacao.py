"""A reavaliação determinada, do lado da operação: pendência, distribuição e a exceção única.

**A inscrição com reavaliação determinada tem Resultado** — e por isso a prontidão a chamava de
`consolidada`, escondendo exatamente a pendência que a decisão criou. Quem organiza a Etapa precisa
vê-la como trabalho a fazer, e não como trabalho feito (FR-067).

**Duas garantias vêm de graça, e o teste as registra como comportamento correto** (FR-068):

```text
uq_avaliacao_concluida_por_pessoa  quem concluiu a original não conclui a reavaliação
uq_atribuicao_ativa (por membro)   outro avaliador recebe Atribuição para o mesmo par
```

Nenhuma das duas é regra nova. Registrá-las em teste é o que impede que a próxima feature as
desfaça achando que eram acidente.
"""

from decimal import Decimal

import pytest

from processo_seletivo.recursos.application.julgar import julgar
from processo_seletivo.recursos.models import DecisaoRecurso
from processo_seletivo.resultados.application.consolidacao import consolidar
from processo_seletivo.resultados.application.prontidao import (
    CONSOLIDADA,
    REAVALIACAO,
    panorama_da_etapa,
)
from processo_seletivo.resultados.models import ResultadoEtapa
from tests.fixtures.mesa import concluir_como, distribuir_para
from tests.fixtures.recursos_us4 import cenario_julgavel, julgador

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.integration]


@pytest.fixture
def determinada(gestor, api_client, manager_headers, process_payload):
    """O cenário com a reavaliação já determinada, e ninguém tendo reavaliado ainda."""
    peca = cenario_julgavel(
        gestor, api_client, manager_headers, process_payload, seed=117, codigo="0817"
    )
    decisao, _ = julgar(
        actor=julgador(),
        recurso_id=peca["recurso"].id,
        especie=DecisaoRecurso.Especie.REAVALIACAO_DETERMINADA,
        motivacao="Reavalie-se a prova didática por avaliador diverso.",
        etapa_id=peca["cenario"]["etapa"],
        assinatura_do_resultado=str(peca["superado"].id),
        idempotency_key="reavaliar-us5b",
    )
    return {**peca, "decisao": decisao}


def panorama(determinada):
    from processo_seletivo.comissoes.application.comissao import identificador
    from processo_seletivo.comissoes.domain.etapas import etapas_vigentes

    edital = determinada["cenario"]["edital"]
    vigentes = etapas_vigentes(edital)
    etapa = vigentes[identificador(determinada["cenario"]["etapa"])]
    return panorama_da_etapa(edital=edital, etapa=etapa, etapas_vigentes=vigentes)


def consolidar_a_inscricao(determinada, *, chave):
    return consolidar(
        actor=_gestor(),
        processo_id=determinada["cenario"]["edital"].processo_id,
        edital_id=determinada["cenario"]["edital"].id,
        etapa_id=determinada["cenario"]["etapa"],
        inscricao_ids=[determinada["inscricao"].id],
        idempotency_key=chave,
        correlation_id="reavaliacao",
    )


def _gestor():
    from tests.conftest import ator_institucional

    return ator_institucional("carlos", "comissao:gerir")


def test_a_etapa_mostra_a_pendencia_nomeada_e_nao_consolidada(determinada):
    """O estado é o sexto, e não o de "já consolidada" — que é o que ela era antes (FR-067)."""
    estados = panorama(determinada)["estados"]

    estado, motivo = estados[determinada["inscricao"].id]
    assert estado == REAVALIACAO
    assert estado != CONSOLIDADA
    assert "reavaliação determinada" in motivo


def test_a_contagem_da_etapa_separa_a_pendencia(determinada):
    """A partição continua fechando: o sexto estado não pode sumir dentro de outro."""
    contagens = panorama(determinada)["contagens"]

    assert contagens["reavaliacoes"] == 1
    assert (
        contagens["consolidadas"]
        + contagens["prontas"]
        + contagens["impedidas"]
        + contagens["reavaliacoes"]
        == contagens["participantes"]
    )


def test_sem_nova_avaliacao_consolidar_recusa_dizendo_o_que_falta(determinada):
    """Determinar reavaliação não a produz: alguém precisa avaliar.

    A recusa nomeia o que falta em vez de consolidar de novo o que já estava lá — que é o que
    aconteceria se o cumprimento fosse presumido pela existência da decisão.
    """
    declarado = consolidar_a_inscricao(determinada, chave="sem-nova-avaliacao")

    assert declarado["feitas"] == 0
    assert declarado["recusadas"] == 1
    assert "ainda não foi concluída" in " ".join(
        motivo["motivo"] for motivo in declarado["motivos"]
    )
    assert not ResultadoEtapa.objects.filter(resultado_anterior__isnull=False).exists()


def test_a_inscricao_e_distribuivel_e_avaliavel_pelas_operacoes_existentes(determinada):
    """Nenhuma operação nova — mas **não era verdade de graça** (FR-067).

    O contrato afirmava que a reavaliação seria distribuível porque `uq_atribuicao_ativa` é por
    membro. A constraint de fato permite; o que recusava era o **teto do Edital**: a distribuição
    contava a avaliação original contra as `n` que a Etapa prevê e respondia "esta inscrição já tem
    as avaliações que o Edital declara". A determinação ficava inexequível pelo caminho normal.

    A correção é uma vaga a mais **enquanto a decisão está pendente**, e não uma exceção de
    conveniência: a reavaliação é avaliação ordenada por decisão, e contá-la contra o teto do curso
    normal confundiria duas coisas diferentes. A vaga some quando a decisão é cumprida.
    """
    cenario = determinada["cenario"]
    outra = _segundo_avaliador(cenario)

    declarado = distribuir_para(
        cenario, _gestor(), [outra], [determinada["inscricao"]], chave="lote-reav"
    )
    assert declarado["recusadas"] == 0, declarado["motivos"]
    avaliacao = concluir_como(cenario, outra, determinada["inscricao"], pontuacao="88.0000")

    assert avaliacao.concluida_por == outra
    assert avaliacao.pontuacao == Decimal("88.0000")


def test_a_consolidacao_em_cumprimento_cria_o_sucessor_citando_a_decisao(determinada):
    """**A exceção única** (FR-068).

    Fora dela, consolidar continua recusando o par que já tem Resultado vigente.
    """
    cenario = determinada["cenario"]
    outra = _segundo_avaliador(cenario)
    distribuir_para(cenario, _gestor(), [outra], [determinada["inscricao"]], chave="lote-reav-b")
    concluir_como(cenario, outra, determinada["inscricao"], pontuacao="88.0000")

    declarado = consolidar_a_inscricao(determinada, chave="cumprir-reavaliacao")

    assert declarado["recusadas"] == 0
    assert declarado["feitas"] == 1
    sucessor = ResultadoEtapa.objects.get(pk=declarado["ids"][0])
    assert sucessor.resultado_anterior_id == determinada["superado"].id
    assert sucessor.decisao_id == determinada["decisao"].id
    assert sucessor.origem == ResultadoEtapa.Origem.AVALIACAO
    assert sucessor.avaliacao_id is not None
    assert sucessor.pontuacao == Decimal("88.0000")
    assert (
        ResultadoEtapa.vigentes.get(
            inscricao=determinada["inscricao"], etapa_id=cenario["etapa"]
        ).pk
        == sucessor.pk
    )


def test_fora_do_cumprimento_consolidar_continua_recusando_o_par_com_resultado(determinada):
    """A exceção não pode virar a regra: sem decisão pendente, o par consolidado é `CONSOLIDADA`."""
    cenario = determinada["cenario"]
    outra_inscricao = cenario["inscricoes"][1]

    estado, motivo = panorama(determinada)["estados"][outra_inscricao.id]

    assert estado == CONSOLIDADA
    assert "já possui Resultado" in motivo


def test_quem_concluiu_a_original_nao_conclui_a_reavaliacao(determinada):
    """`uq_avaliacao_concluida_por_pessoa` — garantia que **já existe**, e o teste a registra.

    Ela não foi escrita para a 018, e é justamente por isso que vale registrá-la: a próxima feature
    que mexer na Mesa precisa saber que a imparcialidade da reavaliação depende dela.
    """
    from django.db.utils import IntegrityError

    from processo_seletivo.shared.api.problems import DomainError

    cenario = determinada["cenario"]
    original = cenario["membros"]["joao"].identity_subject
    distribuir_para(cenario, _gestor(), ["joao"], [determinada["inscricao"]], chave="lote-reav-c")

    with pytest.raises((IntegrityError, DomainError)):
        concluir_como(cenario, original, determinada["inscricao"], pontuacao="99.0000", revisao=1)


def _segundo_avaliador(cenario):
    """Um avaliador diverso do que concluiu a original, alocado na Etapa."""
    from processo_seletivo.comissoes.models import Funcao
    from tests.fixtures.comissao import alocar_em, constituir

    membros = constituir(
        _gestor(), cenario["processo"], [("ana", Funcao.MEMBRO)], prefixo="reav-us5"
    )
    cenario["membros"]["ana"] = membros["ana"]
    alocar_em(
        _gestor(),
        cenario["processo"],
        membros["ana"],
        cenario["edital"],
        cenario["etapa"],
        chave="aloc-reav-us5",
    )
    return "ana"
