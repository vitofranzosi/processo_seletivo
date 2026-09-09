"""O Pulso: a soma acima do Edital, e o tempo acima de todos.

A capacidade que hoje não existe em nível nenhum. Um Processo com três Editais não tem, em lugar
algum, quantas inscrições recebeu — e é isso que a `US1` entrega sozinha.
"""

import pytest

from processo_seletivo.interface import supervisao
from processo_seletivo.shared.tempo import ZONA
from tests.fixtures.supervisao import rascunhar, submeter

pytestmark = [pytest.mark.django_db, pytest.mark.integration]


def do_edital(pulso, edital):
    return next(item for item in pulso.por_edital if item.edital.id == edital.id)


def test_o_total_do_processo_e_a_soma_dos_editais(processo_a, edital_a, edital_c):
    """`FR-010` e `SC-002`: o número da supervisão é o que as duas telas de inscrição somam."""
    submeter(edital_a, 5)
    submeter(edital_c, 3, seed=2)

    lido = supervisao.pulso(processo_a)

    assert lido.submetidas_no_processo == 8
    assert do_edital(lido, edital_a).submetidas == 5
    assert do_edital(lido, edital_c).submetidas == 3


def test_cada_edital_aparece_nomeado_inclusive_o_de_zero_inscricoes(processo_a, edital_a, edital_c):
    """`FR-011` e `SC-007`: zero é resposta, e é apresentada como tal.

    O Edital sem inscrição alguma continua na leitura — some-lo da lista faria a soma parecer
    completa quando ela cobre menos Editais do que o Processo tem.
    """
    submeter(edital_a, 2)

    lido = supervisao.pulso(processo_a)

    nomeados = {(item.edital.number, item.edital.year) for item in lido.por_edital}
    assert nomeados == {
        (edital_a.number, edital_a.year),
        (edital_c.number, edital_c.year),
    }
    assert do_edital(lido, edital_c).submetidas == 0


def test_o_rascunho_nao_soma_ao_total_de_submetidas(processo_a, edital_a, edital_c):
    """`FR-012` e `SC-003`: duas grandezas, e nunca uma."""
    submeter(edital_a, 4)
    rascunhar(edital_a, 3)
    rascunhar(edital_c, 2, seed=2)

    lido = supervisao.pulso(processo_a)

    assert lido.submetidas_no_processo == 4
    assert lido.rascunhos_no_processo == 5
    assert do_edital(lido, edital_a).rascunhos == 3
    assert do_edital(lido, edital_c).rascunhos == 2


def test_o_instante_da_leitura_acompanha_os_indicadores(processo_a, edital_a, edital_c):
    """`FR-009`: o contrato é o instante lido, e não a tecnologia de atualização."""
    from django.utils import timezone

    antes = timezone.now()

    lido = supervisao.pulso(processo_a)

    assert antes <= lido.lido_em <= timezone.now()


# ---------------------------------------------------------------------------
# O tempo (`US2`) — período, tempo restante, marcos, últimas 24 horas e a série
# ---------------------------------------------------------------------------


def test_o_periodo_e_o_tempo_restante_saem_por_edital(processo_a, edital_a, edital_c):
    """`FR-019` e `SC-007`: a data é do Edital, e nunca do Processo (`D-005`)."""
    from processo_seletivo.inscricoes.domain.periodo import ABERTO, NAO_DESIGNADO

    lido = supervisao.pulso(processo_a)

    do_c = do_edital(lido, edital_c)
    assert do_c.periodo is not None
    assert do_c.periodo.situacao == ABERTO
    assert do_c.periodo.restante is not None and do_c.periodo.restante.days >= 4
    # O Edital A publica um Evento que **não** é o período de inscrições: a marca é do Evento, e
    # não do texto do tipo.
    assert do_edital(lido, edital_a).periodo is None
    assert do_edital(lido, edital_a).ausencia == supervisao.SEM_PERIODO
    assert NAO_DESIGNADO not in {do_c.periodo.situacao}


def test_evento_cancelado_nao_entra_nos_proximos_marcos(
    processo_a, edital_a, api_client, manager_headers
):
    """`FR-021`: cancelado saiu do cronograma efetivo, e cobrar prazo dele seria cobrar de quem já
    foi cancelado."""
    from datetime import timedelta

    from django.utils import timezone

    from tests.fixtures.supervisao import (
        evento_do_periodo,
        evento_simples,
        publicar_no_processo,
        rascunho_com_periodo,
    )

    agora = timezone.now()
    edital = publicar_no_processo(
        api_client,
        manager_headers,
        processo_a,
        number="04",
        title="Com marcos",
        chave="supervisao-marcos",
        draft=rascunho_com_periodo(
            4,
            eventos=[
                evento_do_periodo(
                    4, inicio=agora - timedelta(days=2), fim=agora + timedelta(days=2)
                ),
                evento_simples(
                    4,
                    base=403,
                    descricao="Resultado preliminar",
                    inicio=agora + timedelta(days=10),
                    fim=agora + timedelta(days=11),
                    ordem=2,
                ),
                evento_simples(
                    4,
                    base=404,
                    descricao="Sessão que não haverá",
                    inicio=agora + timedelta(days=12),
                    fim=agora + timedelta(days=13),
                    ordem=3,
                    status="CANCELADO",
                ),
            ],
        ),
    )

    marcos = do_edital(supervisao.pulso(processo_a), edital).proximos_marcos

    descricoes = [marco.descricao for marco in marcos]
    assert "Resultado preliminar" in descricoes
    assert "Sessão que não haverá" not in descricoes
    # `D-005`: todo marco carrega o Edital a que pertence.
    assert {marco.edital.id for marco in marcos} == {edital.id}


def test_a_serie_agrupa_por_instante_de_submissao_e_preenche_o_dia_de_zero(
    processo_a, edital_a, edital_c
):
    """`FR-014` e `FR-015`: a série se constrói sobre `submitted_at`, e sobre mais nada.

    O dia sem submissão entra com zero: a ausência de um dia na série faria a leitura supor uma
    continuidade que não houve.
    """
    from datetime import timedelta

    from django.utils import timezone

    agora = timezone.now()
    submeter(edital_c, 2, quando=agora - timedelta(days=3), seed=2)
    submeter(edital_c, 1, primeiro=50, quando=agora - timedelta(days=1), seed=2)
    # Rascunho antigo: aberto e nunca enviado, ele não tem instante de submissão e não pertence à
    # série (`FR-015`).
    rascunhar(edital_c, 4, seed=2)

    serie = do_edital(supervisao.pulso(processo_a), edital_c).serie

    # O dia é o da zona institucional, e a asserção usa a mesma: um teste que lesse a zona do
    # sistema passaria aqui e reprovaria num CI em UTC, por uma diferença que não é do produto.
    por_dia = {ponto.dia: ponto.quantidade for ponto in serie}
    assert por_dia[(agora - timedelta(days=3)).astimezone(ZONA).date()] == 2
    assert por_dia[(agora - timedelta(days=1)).astimezone(ZONA).date()] == 1
    assert por_dia[(agora - timedelta(days=2)).astimezone(ZONA).date()] == 0
    assert sum(por_dia.values()) == 3


def test_as_ultimas_24_horas_somam_o_processo_e_excluem_a_borda(processo_a, edital_a, edital_c):
    """`FR-013`: a leitura recente é **uma contagem**, e contagem soma os Editais.

    A submissão de exatamente 24 horas fica de fora: a borda é onde o fora-por-um mora, e uma
    janela que a incluísse contaria um dia e um instante.
    """
    from datetime import timedelta

    from django.utils import timezone

    agora = timezone.now()
    submeter(edital_c, 3, quando=agora - timedelta(hours=2), seed=2)
    submeter(edital_a, 2, primeiro=60, quando=agora - timedelta(hours=20))
    submeter(edital_a, 1, primeiro=70, quando=agora - timedelta(hours=24))
    submeter(edital_a, 1, primeiro=80, quando=agora - timedelta(days=3))

    lido = supervisao.pulso(processo_a, agora=agora)

    assert lido.ultimas_24h == 5


def test_sem_periodo_em_curso_as_ultimas_24_horas_nao_sao_apresentadas(
    processo_a, edital_a, api_client, manager_headers
):
    """Fora da janela o número é sempre zero, e zero apresentado como notícia é ruído."""
    from datetime import timedelta

    from django.utils import timezone

    from tests.fixtures.supervisao import publicar_no_processo, rascunho_com_periodo

    agora = timezone.now()
    publicar_no_processo(
        api_client,
        manager_headers,
        processo_a,
        number="05",
        title="Período encerrado",
        chave="supervisao-encerrado",
        draft=rascunho_com_periodo(
            5, inicio=agora - timedelta(days=30), fim=agora - timedelta(days=10)
        ),
    )

    lido = supervisao.pulso(processo_a)

    assert lido.algum_periodo_em_curso is False
    assert lido.ultimas_24h is None


def test_edital_sem_cronograma_vigente_e_declarado_como_tal(
    processo_a, edital_a, edital_c, api_client, manager_headers
):
    """`FR-022`: dito explicitamente, em vez de prazo em branco."""
    criado = api_client.post(
        f"/api/v1/admin/processos/{processo_a.id}/editais",
        {"number": "06", "year": 2026, "title": "Em elaboração"},
        format="json",
        **{**manager_headers, "HTTP_IDEMPOTENCY_KEY": "supervisao-sem-cronograma"},
    )
    assert criado.status_code == 201, criado.content

    lido = supervisao.pulso(processo_a)

    em_elaboracao = next(
        item for item in lido.por_edital if str(item.edital.id) == criado.json()["id"]
    )
    assert em_elaboracao.ausencia == supervisao.SEM_CRONOGRAMA
    assert em_elaboracao.periodo is None
    assert em_elaboracao.proximos_marcos == ()
