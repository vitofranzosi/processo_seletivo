"""O seletor único: quem está apto e o que sai de cada um (117, FR-3669 a FR-3674).

Lê o banco, e por isso pede o cenário; mas é a regra do seletor, sem tela nem arquivo, que se prova
aqui: os desfechos que incluem, as sucessões, a chamada mais recente, os momentos, a deduplicação,
as situações e a versão da definição.
"""

import pytest
from django.utils import timezone

from processo_seletivo.convocacao.application.desfechar import desfechar
from processo_seletivo.convocacao.domain import nomes as nomes_da_convocacao
from processo_seletivo.convocacao.models import ConferenciaDeDocumento, Convocacao
from processo_seletivo.formalizacao.application import conjunto, definir
from processo_seletivo.formalizacao.domain import nomes
from tests.fixtures import documentos_da_convocacao as cenarios
from tests.fixtures.documentos_da_convocacao import (
    CERTIDAO,
    CERTIFICADO_DO_MEDIO,
    HISTORICO,
    IDENTIDADE,
    RESIDENCIA,
    _documento,
)
from tests.fixtures.formalizacao import (
    CERTIFICADO_DO_CURSO,
    TITULOS,
    convocar_direto,
    definir_documentos,
    inscrever,
    montar_cenario_da_formalizacao,
    tornar_apta,
)

pytestmark = [pytest.mark.integration, pytest.mark.django_db]


def _aptos(cenario, **kwargs):
    return conjunto.aptos(
        cenario.edital, definicao=definir.vigente(cenario.edital), com_exportacoes=False, **kwargs
    )


def _situacoes(pessoa):
    return {documento.chave: documento.situacao for documento in pessoa.documentos}


def test_so_quem_tem_aceite_vigente_esta_apto(cenario, gestor):
    """US3, cenário 1: os aceites entram; o indeferimento e quem não respondeu, não."""
    definir_documentos(cenario.edital, gestor)
    pessoas = _aptos(cenario)

    assert {p.inscricao_id for p in pessoas} == {str(i.id) for i in cenario.inscricoes_aptas}
    fora = [i for i, _ in cenario.indeferidas + cenario.sem_resposta]
    assert not {str(i.id) for i in fora} & {p.inscricao_id for p in pessoas}


def test_os_desfechos_que_incluem_sao_os_da_convocacao():
    """FR-3669: aceite e regularização, pela constante da `019`, e nenhuma outra leitura."""
    assert nomes_da_convocacao.DESFECHOS_QUE_INCLUEM == (
        nomes_da_convocacao.ACEITE,
        nomes_da_convocacao.REGULARIZACAO,
    )


def test_o_aceite_sucedido_por_indeferimento_tira_a_pessoa(cenario, gestor):
    """SC-1103: corrigido o desfecho, a pessoa sai da próxima leitura sem ação de ninguém."""
    definir_documentos(cenario.edital, gestor)
    inscricao, convocacao = cenario.aptas[0]
    desfechar(
        actor=gestor,
        processo_id=cenario.edital.processo_id,
        convocacao_id=convocacao.id,
        especie=nomes_da_convocacao.INDEFERIMENTO,
        fundamento="Documento falso.",
        motivo="Correção do aceite",
        idempotency_key="corrige-117",
        correlation_id="teste-117",
    )

    assert str(inscricao.id) not in {p.inscricao_id for p in _aptos(cenario)}


def test_a_convocacao_corrigida_le_a_vigente(cenario, gestor):
    """A sucessora que corrige a convocação não tem o desfecho da anterior: não está apta."""
    definir_documentos(cenario.edital, gestor)
    inscricao, convocacao = cenario.aptas[0]
    Convocacao.objects.create(
        edital=convocacao.edital,
        perfil_id=convocacao.perfil_id,
        marco_id=convocacao.marco_id,
        inscricao=inscricao,
        especie=convocacao.especie,
        fundamento=convocacao.fundamento,
        apuracao=convocacao.apuracao,
        ato_de_ordenacao_id=convocacao.ato_de_ordenacao_id,
        corte_id=convocacao.corte_id,
        versao=convocacao.versao,
        criado_por="teste",
        criado_em=timezone.now(),
        convocacao_anterior=convocacao,
        motivo_da_sucessao="Vencimento corrigido",
    )

    assert str(inscricao.id) not in {p.inscricao_id for p in _aptos(cenario)}


def test_vale_a_chamada_mais_recente(cenario, gestor):
    """FR-3669, caso-limite: duas chamadas da mesma inscrição; a segunda, sem desfecho, decide."""
    definir_documentos(cenario.edital, gestor)
    inscricao, convocacao = cenario.aptas[0]
    Convocacao.objects.create(
        edital=convocacao.edital,
        perfil_id=convocacao.perfil_id,
        marco_id=convocacao.marco_id,
        inscricao=inscricao,
        especie=convocacao.especie,
        fundamento="Segunda chamada.",
        apuracao=convocacao.apuracao,
        ato_de_ordenacao_id=convocacao.ato_de_ordenacao_id,
        corte_id=convocacao.corte_id,
        versao=convocacao.versao,
        chamada=2,
        criado_por="teste",
        criado_em=timezone.now(),
    )

    assert str(inscricao.id) not in {p.inscricao_id for p in _aptos(cenario)}


def test_so_os_documentos_definidos_aparecem(cenario, gestor):
    """US3, cenário 2, FR-3673: fora da definição não aparece; renda e títulos ficam de fora."""
    definir_documentos(cenario.edital, gestor, requisitos=[IDENTIDADE, HISTORICO])
    pessoa = _aptos(cenario)[0]

    assert [d.chave for d in pessoa.documentos] == ["identidade", "historico"]
    assert all(d.incluivel for d in pessoa.documentos)


def test_o_da_inscricao_sai_sem_conferencia_e_diz_isso(cenario, gestor):
    """FR-3671, D-022: o hash do envio é o esperado, e a origem é o documento da inscrição."""
    definir_documentos(cenario.edital, gestor, requisitos=[CERTIFICADO_DO_CURSO, CERTIDAO])
    pessoa = _aptos(cenario)[0]
    certificado, certidao = pessoa.documentos

    assert certificado.origem == nomes.ORIGEM_DOCUMENTO
    assert certificado.sem_conferencia
    assert certificado.hash_esperado == certificado.fonte.content_hash
    assert certidao.origem == nomes.ORIGEM_APRESENTACAO
    assert not certidao.sem_conferencia
    assert certidao.conferido_em is not None


def test_nao_se_aplica_e_nao_apresentado_deixam_a_pessoa_completa(
    cenario, gestor, api_client, manager_headers, process_payload
):
    """FR-3672: as duas situações não tornam a pessoa incompleta, e não saem no pacote."""
    definir_documentos(cenario.edital, gestor, requisitos=[TITULOS, CERTIDAO, IDENTIDADE])
    # Quem não enviou os títulos, facultativos na inscrição.
    sem_titulos = inscrever(cenario.edital, 900, documentos=(IDENTIDADE, CERTIFICADO_DO_CURSO))
    convocacao = convocar_direto(cenario.edital, sem_titulos)
    tornar_apta(cenario.edital, gestor, sem_titulos, convocacao, numero=900)

    pessoa = next(p for p in _aptos(cenario) if p.inscricao_id == str(sem_titulos.id))
    assert _situacoes(pessoa)["titulos"] == nomes.NAO_APRESENTADO
    assert {d.chave for d in pessoa.incluiveis} == {"certidao", "identidade"}


def test_documento_da_convocacao_sem_conferencia_conforme_vigente_nao_sai(cenario, gestor):
    """FR-3671: uma conferência posterior que não é conforme tira o documento."""
    definir_documentos(cenario.edital, gestor, requisitos=[CERTIDAO])
    _, convocacao = cenario.aptas[0]
    item = cenarios.item(convocacao, CERTIDAO)
    vigente = item.apresentacoes.order_by("-numero").first()
    ConferenciaDeDocumento.objects.create(
        item=item,
        apresentacao=vigente,
        hash_conferido=vigente.content_hash,
        resultado=ConferenciaDeDocumento.Resultado.PENDENTE,
        motivo="Revista depois",
        conferencia_anterior=item.conferencias.order_by("-conferido_em").first(),
        motivo_da_substituicao="Revisão",
        conferido_por="carlos",
        unidade_de_atuacao="cefor",
        conferido_em=timezone.now(),
    )

    pessoa = next(p for p in _aptos(cenario) if p.convocacao_id == str(convocacao.id))
    assert _situacoes(pessoa) == {"certidao": nomes.NAO_CONFERIDO}
    assert pessoa.incluiveis == []


def test_a_conferencia_nao_se_aplica_e_situacao_nao_se_aplica(cenario, gestor):
    definir_documentos(cenario.edital, gestor, requisitos=[RESIDENCIA])
    _, convocacao = cenario.aptas[0]
    item = cenarios.item(convocacao, RESIDENCIA)
    ConferenciaDeDocumento.objects.create(
        item=item,
        resultado=ConferenciaDeDocumento.Resultado.NAO_SE_APLICA,
        motivo="Mora com os pais",
        conferencia_anterior=item.conferencias.order_by("-conferido_em").first(),
        motivo_da_substituicao="Revisão",
        conferido_por="carlos",
        unidade_de_atuacao="cefor",
        conferido_em=timezone.now(),
    )

    pessoa = next(p for p in _aptos(cenario) if p.convocacao_id == str(convocacao.id))
    assert _situacoes(pessoa) == {"residencia": nomes.NAO_SE_APLICA}


def test_o_arquivo_aproveitado_por_referencia_sai_uma_vez(
    db, gestor, api_client, manager_headers, process_payload, raiz_de_arquivos
):
    """US3, cenário 3, FR-3659: o certificado da inscrição, aproveitado na convocação, sai uma vez,
    pelo item da convocação."""
    aproveitado = "00000000-0000-0000-0000-000000001173"
    documentos = [
        _documento(IDENTIDADE, "identidade", "Documento de identificação", 1),
        _documento(CERTIFICADO_DO_CURSO, "certificado", "Certificado do curso", 2),
        _documento(
            aproveitado,
            "certificado-na-convocacao",
            "Certificado do curso",
            3,
            momento="AT_CALL",
            reusesRequirementId=CERTIFICADO_DO_CURSO,
        ),
    ]
    cenario = montar_cenario_da_formalizacao(
        gestor,
        api_client,
        manager_headers,
        process_payload,
        aptas=0,
        documentos=documentos,
        prefixo="aproveita-117",
    )
    inscricao = inscrever(cenario.edital, 1, documentos=(IDENTIDADE, CERTIFICADO_DO_CURSO))
    convocacao = convocar_direto(cenario.edital, inscricao)
    cenarios.conferir(gestor, convocacao, aproveitado, "CONFORME", chave="aproveita-conforme")
    cenarios.desfechar(
        cenario.edital, gestor, convocacao, nomes_da_convocacao.ACEITE, "aproveita-aceite"
    )
    definir_documentos(cenario.edital, gestor, requisitos=[CERTIFICADO_DO_CURSO, aproveitado])

    (pessoa,) = _aptos(cenario)
    assert [(d.chave, d.origem) for d in pessoa.documentos] == [
        ("certificado-na-convocacao", nomes.ORIGEM_APRESENTACAO)
    ]
    assert str(pessoa.documentos[0].fonte.requirement_id) == str(CERTIFICADO_DO_CURSO)


def test_a_versao_da_definicao_e_a_que_se_passa(cenario, gestor):
    primeira = definir_documentos(cenario.edital, gestor, requisitos=[IDENTIDADE])
    definir_documentos(cenario.edital, gestor, requisitos=[CERTIFICADO_DO_MEDIO])

    pela_primeira = conjunto.aptos(cenario.edital, definicao=primeira, com_exportacoes=False)
    assert [d.chave for d in pela_primeira[0].documentos] == ["identidade"]
    assert [d.chave for d in _aptos(cenario)[0].documentos] == ["certificado-medio"]


def test_a_ordem_e_perfil_nome_e_protocolo(
    db, gestor, api_client, manager_headers, process_payload, raiz_de_arquivos
):
    cenario = montar_cenario_da_formalizacao(
        gestor,
        api_client,
        manager_headers,
        process_payload,
        aptas=3,
        nomes=["Zuleica", "ana", "Bruno"],
        prefixo="ordem-117",
    )
    definir_documentos(cenario.edital, gestor)
    assert [p.nome for p in _aptos(cenario)] == ["ana", "Bruno", "Zuleica"]
