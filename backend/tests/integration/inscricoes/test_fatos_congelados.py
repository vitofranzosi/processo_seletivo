"""O que a inscrição congela na submissão, e o que nada mais muda (015, D-2).

Congelar é o ponto inteiro: o valor que entra na classificação tem de ser o do momento da
inscrição. Sem isso, editar o perfil depois mudaria classificação histórica — e a Constituição
exige que o estado vigente em qualquer instante relevante seja reproduzível.
"""

import pytest

from processo_seletivo.inscricoes.application.rascunho import (
    abrir_inscricao,
    anexar_documento,
    gravar_dados,
)
from processo_seletivo.inscricoes.application.submissao import enviar_inscricao
from processo_seletivo.inscricoes.models import Inscricao, ValorDeFato
from processo_seletivo.publicacoes.models_retificacao import VersaoConsolidada
from processo_seletivo.shared.api.problems import DomainError
from tests.fixtures.candidato import MARIA, MODALIDADE_AC, PERFIL_DOCENTE, PERFIL_TECNICO, pdf
from tests.fixtures.publicacao import retify
from tests.fixtures.selecao import DOCUMENTO_DE_TODOS, DOCUMENTO_DO_PERFIL

pytestmark = [pytest.mark.integration, pytest.mark.django_db(transaction=True)]

DECLARACOES = {"veracidade": True, "ciencia": True}
NASCIMENTO = "00000000-0000-0000-0000-0000000005a1"
OUTRO = "00000000-0000-0000-0000-0000000005a2"


def perfil_publicado(edital):
    from tests.fixtures.candidato import PERFIL_DOCENTE as identificador

    return identificador


def declarar_fato(api_client, edital, identificador, sigla, tipo, *, sufixo="fato"):
    retify(
        api_client,
        edital,
        [
            {
                "targetPath": f"/profiles/id={PERFIL_DOCENTE}/declaredFacts/-",
                "operation": "ADD",
                "newValue": {
                    "id": identificador,
                    "code": sigla,
                    "label": f"Dado {sigla}",
                    "type": tipo,
                },
            }
        ],
        suffix=sufixo,
    )


def pronta(edital, perfil=PERFIL_DOCENTE):
    inscricao = abrir_inscricao(identidade=MARIA, edital_id=edital.id, profile_id=perfil)
    inscricao = gravar_dados(
        identidade=MARIA, inscricao=inscricao, dados={"modality_id": MODALIDADE_AC}
    )
    exigidos = [(DOCUMENTO_DE_TODOS, "rg.pdf")]
    if perfil == PERFIL_DOCENTE:
        exigidos.append((DOCUMENTO_DO_PERFIL, "dip.pdf"))
    for requisito, nome in exigidos:
        anexar_documento(
            identidade=MARIA, inscricao=inscricao, requirement_id=requisito, arquivo=pdf(nome)
        )
    inscricao.refresh_from_db()
    return inscricao


def enviar(inscricao, fatos=None, chave="envio"):
    return enviar_inscricao(
        identidade=MARIA,
        inscricao=inscricao,
        declaracoes=DECLARACOES,
        idempotency_key=f"{chave}-{inscricao.pk}",
        fatos=fatos or {},
    )


def test_o_valor_congela_na_submissao_sob_a_versao_do_ato(
    api_client, selecao, candidatos_registrados
):
    declarar_fato(api_client, selecao, NASCIMENTO, "NASCIMENTO", "DATA")
    vigente = VersaoConsolidada.objects.filter(edital=selecao).latest("materialized_at")

    enviada = enviar(pronta(selecao), {NASCIMENTO: "1990-05-20"})

    valor = ValorDeFato.objects.get(inscricao=enviada, fato_id=NASCIMENTO)
    assert valor.valor_data.isoformat() == "1990-05-20"
    assert valor.versao_id == vigente.pk == enviada.versao_aceita_id
    assert valor.congelado_em == enviada.submitted_at


def test_editar_o_perfil_depois_nao_muda_valor_congelado(
    api_client, selecao, candidatos_registrados
):
    """A razão de congelar: sem isto, editar o perfil mudaria classificação histórica."""
    declarar_fato(api_client, selecao, NASCIMENTO, "NASCIMENTO", "DATA")
    enviada = enviar(pronta(selecao), {NASCIMENTO: "1990-05-20"})
    antes = ValorDeFato.objects.get(inscricao=enviada).valor_data

    Inscricao.objects.filter(pk=enviada.pk).update(nome="Maria Editada")

    assert ValorDeFato.objects.get(inscricao=enviada).valor_data == antes


def test_o_fato_declarado_e_exigido_no_envio(api_client, selecao, candidatos_registrados):
    """Declarar um fato é dizer que uma regra o consome.

    Enviar sem ele seria classificar no vazio.
    """
    declarar_fato(api_client, selecao, NASCIMENTO, "NASCIMENTO", "DATA")

    with pytest.raises(DomainError) as recusa:
        enviar(pronta(selecao), {})

    assert recusa.value.code == "declared_fact_required"


def test_rascunho_abandonado_nao_consome_direito(api_client, selecao, candidatos_registrados):
    """O teto conta só submetidas: abandonar um rascunho não pode custar um direito (FR-064)."""
    retify(
        api_client,
        selecao,
        [{"targetPath": "/maxInscricoesPorCandidato", "operation": "REPLACE", "newValue": 1}],
        suffix="teto",
    )
    abandonado = pronta(selecao, PERFIL_TECNICO)
    assert abandonado.status == Inscricao.Status.RASCUNHO

    enviada = enviar(pronta(selecao, PERFIL_DOCENTE))

    assert enviada.status == Inscricao.Status.SUBMETIDA


def test_reduzir_o_teto_por_retificacao_nao_invalida_o_ja_submetido(
    api_client, selecao, candidatos_registrados
):
    """Publicação anterior não se reescreve: quem entrou sob a norma que a admitia permanece."""
    enviada = enviar(pronta(selecao, PERFIL_DOCENTE))

    retify(
        api_client,
        selecao,
        [{"targetPath": "/maxInscricoesPorCandidato", "operation": "REPLACE", "newValue": 1}],
        suffix="teto",
    )

    enviada.refresh_from_db()
    assert enviada.status == Inscricao.Status.SUBMETIDA
    assert Inscricao.objects.filter(pk=enviada.pk).exists()


def test_remover_o_fato_e_acrescentar_outro_nao_toca_o_valor_congelado(
    api_client, selecao, candidatos_registrados
):
    """O ciclo completo (T061): congelar, retificar removendo e acrescentando, e conferir a âncora.

    O valor antigo continua apontando para a **identidade** do fato que o governou e para a
    **versão** sob a qual foi congelado — nem uma nem outra mudam porque o Edital passou a exigir
    outra coisa. É isso que faz "o congelado sob o primeiro permanece legível sob a norma que o
    governou" ser verificável, e não retórica (FR-058).
    """
    declarar_fato(api_client, selecao, NASCIMENTO, "NASCIMENTO", "DATA")
    enviada = enviar(pronta(selecao), {NASCIMENTO: "1990-05-20"})
    congelado = ValorDeFato.objects.get(inscricao=enviada, fato_id=NASCIMENTO)
    versao_do_ato = congelado.versao_id

    retify(
        api_client,
        selecao,
        [
            {
                "targetPath": f"/profiles/id={PERFIL_DOCENTE}/declaredFacts/id={NASCIMENTO}",
                "operation": "REMOVE",
            },
            {
                "targetPath": f"/profiles/id={PERFIL_DOCENTE}/declaredFacts/-",
                "operation": "ADD",
                "newValue": {
                    "id": OUTRO,
                    "code": "ANO",
                    "label": "Ano de nascimento",
                    "type": "INTEIRO",
                },
            },
        ],
        suffix="troca",
    )

    congelado.refresh_from_db()
    assert str(congelado.fato_id) == NASCIMENTO, "o valor continua ligado ao fato que o governou"
    assert congelado.versao_id == versao_do_ato, "e à versão sob a qual foi congelado"
    assert congelado.valor_data.isoformat() == "1990-05-20"
    vigente = VersaoConsolidada.objects.filter(edital=selecao).latest("materialized_at")
    declarados = next(item for item in vigente.content["profiles"] if item["id"] == PERFIL_DOCENTE)[
        "declaredFacts"
    ]
    assert [item["id"] for item in declarados] == [OUTRO], "o vigente exige outro fato"
