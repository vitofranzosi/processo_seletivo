"""Gravar, concluir e reabrir pela ficha do barema (146, T017, T018).

O cenário é o do quickstart §2: o barema do 14/2026 publicado, uma inscrição com os dois documentos,
a avaliadora informando 1, 0, 3, 0, 52 — total 70. O que se prende é o caminho do serviço: o total
do servidor, o detalhamento na Avaliação e na Conclusão preservada, o rascunho com pendentes, a
conclusão que os nomeia, a recusa do total vindo do cliente, a trilha sem nota, e a reabertura
depois de uma Retificação do barema.
"""

from decimal import Decimal

import pytest
from django.db import DatabaseError, connection, transaction

from processo_seletivo.avaliacoes.application.avaliacao import (
    concluir,
    eventos_da_avaliacao,
    reabrir,
)
from processo_seletivo.avaliacoes.application.ficha import ficha_da_avaliacao
from processo_seletivo.avaliacoes.application.selectors import conclusoes_preservadas
from processo_seletivo.avaliacoes.models import Avaliacao, ConclusaoAvaliacao
from processo_seletivo.publicacoes.models_retificacao import VersaoConsolidada
from processo_seletivo.resultados.application.consolidacao import consolidar, prever
from processo_seletivo.resultados.models import ResultadoEtapa
from processo_seletivo.shared.api.problems import DomainError
from tests.conftest import ator_institucional
from tests.fixtures.barema import (
    concluir_com_ficha,
    criterio_de,
    ficha,
    gravar_ficha,
    montar_mesa_com_barema,
)
from tests.fixtures.comissao import ETAPA_A2, alocar_em, inscrever
from tests.fixtures.edital import identificador
from tests.fixtures.mesa import distribuir_para
from tests.fixtures.publicacao import retify

pytestmark = [
    pytest.mark.django_db,
    pytest.mark.integration,
    pytest.mark.usefixtures("raiz_de_arquivos"),
]

SEED = 146


@pytest.fixture
def cenario(gestor, api_client, manager_headers):
    return montar_mesa_com_barema(gestor, api_client, manager_headers, seed=SEED, codigo="B146")


@pytest.fixture
def inscricao(cenario, gestor):
    inscrita = inscrever(
        cenario["edital"],
        1,
        primeiro=4601,
        documentos=[cenario["titulos"], cenario["declaracao"]],
    )[0]
    distribuir_para(cenario, gestor, ["joao"], [inscrita], chave="barema-146")
    return inscrita


def vigente(edital):
    return VersaoConsolidada.objects.filter(edital=edital).latest("materialized_at")


def test_concluir_pela_ficha_grava_o_detalhamento_e_o_total(cenario, inscricao):
    """Quickstart §2.3: 1, 0, 3, 0, 52 dá 70 — com a Especialização e a docência no teto."""
    avaliacao = concluir_com_ficha(cenario, "joao", inscricao, ficha(SEED, 1, 0, 3, 0, 52))

    assert avaliacao.estado == Avaliacao.Estado.CONCLUIDA
    assert avaliacao.pontuacao == Decimal("70.0000")
    assert [linha["parcela"] for linha in avaliacao.criterios] == [
        "20.0000",
        "0.0000",
        "10.0000",
        "0.0000",
        "40.0000",
    ]
    assert [linha["limitada"] for linha in avaliacao.criterios] == [
        False,
        False,
        True,
        False,
        True,
    ]
    preservada = ConclusaoAvaliacao.objects.get(avaliacao=avaliacao)
    assert preservada.criterios == avaliacao.criterios
    assert preservada.pontuacao == Decimal("70.0000")
    assert preservada.versao_id == avaliacao.versao_id


def test_o_rascunho_aceita_criterio_em_branco(cenario, inscricao):
    avaliacao = gravar_ficha(cenario, "joao", inscricao, ficha(SEED, 1, None, 3))

    assert avaliacao.estado == Avaliacao.Estado.RASCUNHO
    # O total do rascunho é a soma do que já foi respondido.
    assert avaliacao.pontuacao == Decimal("30.0000")
    assert [linha["parcela"] for linha in avaliacao.criterios] == [
        "20.0000",
        None,
        "10.0000",
        None,
        None,
    ]


def test_a_conclusao_recusa_nomeando_os_pendentes(cenario, inscricao):
    """Quickstart §2.4: Mestrado em branco — a recusa o nomeia, e nada é gravado."""
    with pytest.raises(DomainError) as recusa:
        concluir_com_ficha(cenario, "joao", inscricao, ficha(SEED, 1, None, 3, 0, 52))

    assert recusa.value.code == "criterios_pendentes"
    assert "Diploma de Mestrado" in recusa.value.detail
    assert not Avaliacao.objects.filter(estado=Avaliacao.Estado.CONCLUIDA).exists()


def test_zero_sem_justificativa_conclui(cenario, inscricao):
    """Quickstart §2.5: o PDF comprova só o Doutorado, e o zero não pede justificativa."""
    avaliacao = concluir_com_ficha(cenario, "joao", inscricao, ficha(SEED, 1, 0, 0, 0, 0))

    assert avaliacao.pontuacao == Decimal("20.0000")
    assert all(linha["justificativa"] == "" for linha in avaliacao.criterios)


def test_a_justificativa_escrita_fica_com_a_parcela(cenario, inscricao):
    texto = "Certificado de especialização fora da área da Educação."
    avaliacao = concluir_com_ficha(
        cenario, "joao", inscricao, ficha(SEED, 1, 0, 1, 0, 52, justificativas={2: texto})
    )

    assert avaliacao.criterios[2]["justificativa"] == texto


def test_o_total_vindo_do_cliente_e_recusado(cenario, inscricao):
    """FR-5215: com barema o total é do servidor, e o enviado junto não é somado nem ignorado."""
    with pytest.raises(DomainError) as recusa:
        concluir(
            ator=ator_institucional("joao"),
            edital=cenario["edital"],
            etapa_id=cenario["etapa"],
            inscricao_id=inscricao.id,
            pontuacao="100",
            criterios=ficha(SEED, 1, 0, 3, 0, 52),
            parecer="",
            expected_revision=1,
            versao_reconhecida=vigente(cenario["edital"]).id,
            correlation_id="teste",
        )

    assert recusa.value.code == "pontuacao_calculada"


def test_sem_detalhamento_a_etapa_com_barema_nao_conclui_pelo_total(cenario, inscricao):
    with pytest.raises(DomainError) as recusa:
        concluir(
            ator=ator_institucional("joao"),
            edital=cenario["edital"],
            etapa_id=cenario["etapa"],
            inscricao_id=inscricao.id,
            pontuacao="70",
            parecer="",
            expected_revision=1,
            versao_reconhecida=vigente(cenario["edital"]).id,
            correlation_id="teste",
        )

    assert recusa.value.code == "pontuacao_calculada"


def test_a_etapa_sem_barema_recusa_o_detalhamento(cenario, inscricao, gestor):
    """A Prova didática do mesmo Edital não publicou barema: o detalhamento não cabe nela."""
    segunda = identificador(ETAPA_A2, SEED)
    alocar_em(gestor, cenario["processo"], cenario["membros"]["joao"], cenario["edital"], segunda)
    contexto = {**cenario, "etapa": segunda}
    distribuir_para(contexto, gestor, ["joao"], [inscricao], chave="barema-146-a2")

    with pytest.raises(DomainError) as recusa:
        gravar_ficha(contexto, "joao", inscricao, ficha(SEED, 1))

    assert recusa.value.code == "criterio_invalido"


def test_a_pontuacao_abaixo_da_minima_ainda_exige_parecer(cenario, inscricao):
    """O parecer obrigatório continua sobre o total (D-008): 20 < 60, Etapa eliminatória."""
    with pytest.raises(DomainError) as recusa:
        concluir_com_ficha(cenario, "joao", inscricao, ficha(SEED, 1, 0, 0, 0, 0), parecer="")

    assert recusa.value.code == "parecer_obrigatorio"


def test_a_trilha_registra_os_atos_sem_a_nota(cenario, inscricao):
    """FR-5230: os eventos de sempre, e nem total nem parcela no motivo."""
    gravar_ficha(cenario, "joao", inscricao, ficha(SEED, 1, 0, 3))
    avaliacao = concluir_com_ficha(
        cenario, "joao", inscricao, ficha(SEED, 1, 0, 3, 0, 52), revisao=2
    )

    motivos = list(eventos_da_avaliacao(avaliacao).values_list("operation", "reason"))
    assert [operacao for operacao, _ in motivos] == ["AVALIACAO_GRAVAR", "AVALIACAO_CONCLUIR"]
    assert not any("70" in motivo or "40" in motivo for _, motivo in motivos)


@pytest.mark.skipif(connection.vendor != "postgresql", reason="o gatilho é do PostgreSQL")
def test_o_detalhamento_da_concluida_nao_muda_por_sql_direto(cenario, inscricao):
    """SC-1630: o gatilho recriado pela `avaliacoes/0005` cobre a coluna nova."""
    avaliacao = concluir_com_ficha(cenario, "joao", inscricao, ficha(SEED, 1, 0, 3, 0, 52))

    with pytest.raises(DatabaseError, match="concluded evaluations are immutable"):
        with transaction.atomic(), connection.cursor() as cursor:
            cursor.execute(
                "UPDATE avaliacoes_avaliacao SET criterios = '[]'::jsonb WHERE id = %s",
                [str(avaliacao.id)],
            )
    with pytest.raises(DatabaseError, match="concluded evaluations are immutable"):
        with transaction.atomic(), connection.cursor() as cursor:
            # A forma exata da reabertura, com o detalhamento trocado no mesmo ato.
            cursor.execute(
                "UPDATE avaliacoes_avaliacao SET estado = 'RASCUNHO', concluida_em = NULL, "
                "concluida_por = '', versao_id = NULL, revision = revision + 1, "
                "criterios = '[]'::jsonb WHERE id = %s",
                [str(avaliacao.id)],
            )

    avaliacao.refresh_from_db()
    assert len(avaliacao.criterios) == 5


def _retificar_o_barema(api_client, edital, etapa_id, mudar, *, sufixo):
    """Uma Retificação que troca o barema da Etapa inteira — com a máxima que a soma der."""
    atual = next(e for e in vigente(edital).content["stages"] if e["id"] == str(etapa_id))
    criterios = mudar([dict(c) for c in atual["criteria"]])
    maxima = sum((Decimal(c["maximumScore"]) for c in criterios), Decimal("0"))
    retify(
        api_client,
        edital,
        [
            {
                "targetPath": f"/stages/id={etapa_id}",
                "operation": "REPLACE",
                "newValue": {**atual, "criteria": criterios, "maximumScore": f"{maxima:.4f}"},
            }
        ],
        suffix=sufixo,
    )


def _consolidar(cenario, gestor, inscricao, *, chave):
    return consolidar(
        actor=gestor,
        processo_id=cenario["processo"].id,
        edital_id=cenario["edital"].id,
        etapa_id=cenario["etapa"],
        inscricao_ids=[inscricao.id],
        idempotency_key=chave,
        correlation_id="teste",
    )


def _reabrir(gestor, cenario, avaliacao, chave):
    return reabrir(
        actor=gestor,
        processo_id=cenario["processo"].id,
        avaliacao_id=avaliacao.id,
        motivo="O barema foi retificado depois da conclusão.",
        expected_revision=avaliacao.revision,
        idempotency_key=chave,
        correlation_id="teste",
    )


def test_retificacao_da_descricao_bloqueia_ate_reabrir_e_concluir_de_novo(
    api_client, cenario, inscricao, gestor
):
    """Quickstart §2.6: a descrição da docência retificada; a conclusão anterior não consolida.

    Reaberta, a ficha volta preenchida pelo barema vigente, e a conclusão nova, sob ele, consolida.
    """
    concluida = concluir_com_ficha(cenario, "joao", inscricao, ficha(SEED, 1, 0, 3, 0, 52))

    def so_em_ead(criterios):
        criterios[4]["description"] = "Só em cursos EaD."
        return criterios

    _retificar_o_barema(api_client, cenario["edital"], cenario["etapa"], so_em_ead, sufixo="d")

    _etapa, consolidaveis, recusas = prever(
        edital=cenario["edital"], etapa_id=cenario["etapa"], inscricao_ids=[inscricao.id]
    )
    assert consolidaveis == []
    assert "barema" in str(recusas)
    _consolidar(cenario, gestor, inscricao, chave="cons-146-antes")
    assert not ResultadoEtapa.objects.filter(inscricao=inscricao).exists()

    reaberta = _reabrir(gestor, cenario, concluida, "reabrir-146-d")
    assert reaberta.criterios == concluida.criterios

    nova = vigente(cenario["edital"])
    tela = ficha_da_avaliacao(
        reaberta, nova.content["stages"][0], cenario["etapa"], [], nova.content
    )
    assert [linha["quantidade"] for linha in tela["linhas"]] == ["1", "0", "3", "0", "52"]
    assert tela["linhas"][4]["descricao"] == "Só em cursos EaD."
    assert tela["total"] == Decimal("70")

    concluir_com_ficha(
        cenario, "joao", inscricao, ficha(SEED, 1, 0, 3, 0, 52), revisao=reaberta.revision
    )
    _consolidar(cenario, gestor, inscricao, chave="cons-146-depois")
    resultado = ResultadoEtapa.vigentes.get(inscricao=inscricao, etapa_id=cenario["etapa"])
    assert resultado.pontuacao == Decimal("70.0000")


def test_reordenar_o_barema_nao_bloqueia_a_consolidacao(api_client, cenario, inscricao, gestor):
    concluir_com_ficha(cenario, "joao", inscricao, ficha(SEED, 1, 0, 3, 0, 52))

    _retificar_o_barema(
        api_client, cenario["edital"], cenario["etapa"], lambda c: list(reversed(c)), sufixo="o"
    )
    _consolidar(cenario, gestor, inscricao, chave="cons-146-ordem")

    assert ResultadoEtapa.vigentes.get(inscricao=inscricao).pontuacao == Decimal("70.0000")


def test_concluir_sob_a_versao_anterior_e_recusado(api_client, cenario, inscricao):
    """SC-1628: a avaliadora pontuou sob um barema, e ele mudou antes de ela concluir."""
    vista = vigente(cenario["edital"]).id
    gravar_ficha(cenario, "joao", inscricao, ficha(SEED, 1, 0, 3, 0, 52))

    def baixar(criterios):
        criterios[3]["maximumScore"] = "10.0000"
        criterios[3]["pointsPerUnit"] = "10.0000"
        return criterios

    _retificar_o_barema(api_client, cenario["edital"], cenario["etapa"], baixar, sufixo="m")

    with pytest.raises(DomainError) as recusa:
        concluir(
            ator=ator_institucional("joao"),
            edital=cenario["edital"],
            etapa_id=cenario["etapa"],
            inscricao_id=inscricao.id,
            pontuacao=None,
            criterios=ficha(SEED, 1, 0, 3, 0, 52),
            parecer="",
            expected_revision=2,
            versao_reconhecida=vista,
            correlation_id="teste",
        )
    assert recusa.value.code == "versao_mudou"


def test_reaberta_depois_de_retificacao_a_ficha_reconcilia(api_client, cenario, inscricao, gestor):
    """FR-5222 e SC-1633: renomeado um critério, removido outro e acrescentado um novo.

    A conclusão preservada continua lendo os nomes da versão que cita; a reaberta mostra os da
    vigente, com o valor do critério que continuou, e o novo pendente.
    """
    concluida = concluir_com_ficha(cenario, "joao", inscricao, ficha(SEED, 1, 0, 3, 0, 52))
    novo = identificador(1475, SEED)

    # O curso de formação (15) sai, e o livro (15) entra: a soma continua 100 (D-003).
    livro = {
        "id": novo,
        "name": "Livro publicado",
        "description": "",
        "maximumScore": "15.0000",
        "pointsPerUnit": "5.0000",
        "unitLabel": "livro",
        "documentRequirementId": None,
    }

    etapa = cenario["etapa"]
    caminho = f"/stages/id={etapa}"
    retify(
        api_client,
        cenario["edital"],
        [
            {
                "targetPath": f"{caminho}/criteria/id={criterio_de(0, SEED)}/name",
                "operation": "REPLACE",
                "newValue": "Título de Doutor",
            },
            {"targetPath": f"{caminho}/criteria/id={criterio_de(3, SEED)}", "operation": "REMOVE"},
            {"targetPath": f"{caminho}/criteria/-", "operation": "ADD", "newValue": livro},
            {
                "targetPath": f"{caminho}/maximumScore",
                "operation": "REPLACE",
                "newValue": "100.0000",
            },
        ],
        suffix="r",
    )
    reaberta = _reabrir(gestor, cenario, concluida, "reabrir-146-r")
    nova = vigente(cenario["edital"])

    tela = ficha_da_avaliacao(
        reaberta, nova.content["stages"][0], cenario["etapa"], [], nova.content
    )
    assert [linha["nome"] for linha in tela["linhas"]] == [
        "Título de Doutor",
        "Diploma de Mestrado",
        "Especialização",
        "Exercício de docência em EaD",
        "Livro publicado",
    ]
    assert [linha["quantidade"] for linha in tela["linhas"]] == ["1", "0", "3", "52", ""]
    assert tela["pendentes"] == ["Livro publicado"]

    criterios = [*ficha(SEED, 1, 0, 3), ficha(SEED, *([None] * 5))[4]]
    criterios[3] = {**criterios[3], "quantidade": "52"}
    criterios.append({"criterionId": novo, "quantidade": "2", "justificativa": ""})
    de_novo = concluir_com_ficha(cenario, "joao", inscricao, criterios, revisao=reaberta.revision)
    assert de_novo.pontuacao == Decimal("80.0000")

    linhas, _ = conclusoes_preservadas(
        edital=cenario["edital"], etapa_id=cenario["etapa"], inscricao_id=inscricao.id
    )
    nomes = [[parcela["nome"] for parcela in linha["ficha"]["linhas"]] for linha in linhas]
    # A primeira conclusão, sob o barema original; a segunda, sob o retificado.
    assert nomes[0][0] == "Diploma de Doutorado"
    assert "Curso de formação de orientadores" in nomes[0]
    assert nomes[1][0] == "Título de Doutor"
    assert "Livro publicado" in nomes[1]
