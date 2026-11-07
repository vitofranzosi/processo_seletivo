"""A inaplicabilidade documental com fundamento publicado, pelos serviços (131).

O cenário é o 72/2026 em miniatura, com dois titulares convocados num gesto só. Uma das inscrições
declara PPI, e a convocação pede:

- a certidão e o histórico, incondicionais (figura B);
- o certificado de alistamento militar, com a condição publicada (figura C);
- a autodeclaração étnico-racial, por recorte à modalidade PPI e sem condição — obrigatória para
  quem a declarou e excluída pelo recorte para a outra (figuras B e A).

O que se prova, na numeração dos cenários de `contracts/cenarios.md`:

- 1, 10: o incondicional não se afasta, por ninguém;
- 2, 8: o condicional se afasta, pelo alocado, com o fato;
- 5, 6: o motivo ausente ou sem palavra é recusado;
- 7: com arquivo, o "não se aplica" pede a abertura, e depois tranca o envio;
- 11: o item fora do recorte não existe para a conferência;
- 12: a correção da convocação herda condição e conferência;
- a substituição que envolve o "não se aplica" pede motivo, haja ou não arquivo.
"""

from datetime import timedelta

import pytest
from django.utils import timezone

from processo_seletivo.convocacao.application import documentos as servico
from processo_seletivo.convocacao.application import fluxo
from processo_seletivo.convocacao.domain import nomes
from processo_seletivo.convocacao.models import ConferenciaDeDocumento, Convocacao
from processo_seletivo.seguranca.domain import Actor
from processo_seletivo.shared.api.problems import DomainError
from tests.fixtures import documentos_da_convocacao as cenarios
from tests.fixtures.corte import MARCO, regra
from tests.fixtures.documentos_da_convocacao import (
    CERTIDAO,
    HISTORICO,
    abrir,
    apresentar,
    conferir,
    item,
    lido,
)
from tests.fixtures.edital import PROFILE_ID, identificador
from tests.fixtures.ocupacao import MODALIDADE_PPI

pytestmark = [pytest.mark.integration, pytest.mark.django_db(transaction=True)]

ALISTAMENTO = identificador(1311, 1)
AUTODECLARACAO = identificador(1311, 2)
CONDICAO = "no caso de candidatos do sexo masculino, maiores de 18 anos"
FATO = "Candidata do sexo feminino, conforme o documento de identidade."
VENCIMENTO = timezone.now() + timedelta(days=3)


def _documentos():
    return [
        *cenarios.documentos_do_aluno()[:3],
        {
            "id": ALISTAMENTO,
            "key": "alistamento",
            "name": "Certificado de alistamento militar ou de reservista",
            "instructions": "",
            "required": True,
            "order": 4,
            "moment": "AT_CALL",
            "requiredWhen": CONDICAO,
        },
        {
            "id": AUTODECLARACAO,
            "key": "autodeclaracao-ppi",
            "name": "Autodeclaração étnico-racial",
            "instructions": "",
            "required": True,
            "order": 5,
            "moment": "AT_CALL",
            "modalityId": MODALIDADE_PPI,
        },
    ]


@pytest.fixture
def cenario(db, gestor, api_client, manager_headers, process_payload, raiz_de_arquivos):
    edital, _, inscricoes = cenarios.montar(
        gestor,
        api_client,
        manager_headers,
        process_payload,
        documentos=_documentos(),
        prefixo="inaplicabilidade-131",
        geral=2,
        cut=regra(surplusCount=1),
        ppi=0,
        modalidades={0: MODALIDADE_PPI},
    )
    assinatura = fluxo.previa_dos_titulares(edital=edital, perfil_id=PROFILE_ID, marco_id=MARCO)[
        "assinatura"
    ]
    praticadas = fluxo.convocar_titulares(
        actor=gestor,
        processo_id=edital.processo_id,
        edital_id=edital.id,
        perfil_id=PROFILE_ID,
        marco_id=MARCO,
        alcance_confirmado=assinatura,
        idempotency_key="titulares-131",
        vencimento=VENCIMENTO,
    )
    por_inscricao = {
        c.inscricao_id: c
        for c in Convocacao.objects.filter(
            id__in=[linha["id"] for linha in praticadas["convocadas"]]
        )
    }
    ppi = por_inscricao[inscricoes[0].id]
    ampla = next(c for i, c in por_inscricao.items() if i != inscricoes[0].id)
    return {
        "edital": edital,
        "ppi": ppi,
        "ampla": ampla,
        "pessoa_ppi": inscricoes[0],
        "pessoa_ampla": next(i for i in inscricoes if i.id == ampla.inscricao_id),
    }


@pytest.fixture
def alocado(cenario, gestor):
    """O membro `joao`, só alocado à conferência deste Edital: sem papel nenhum de gestão."""
    from processo_seletivo.comissoes.application.alocacao import alocar_a_conferencia
    from processo_seletivo.comissoes.models import MembroComissao

    edital = cenario["edital"]
    membro = MembroComissao.objects.get(processo=edital.processo, identity_subject="joao")
    alocar_a_conferencia(
        actor=gestor,
        processo_id=edital.processo_id,
        membro_id=membro.id,
        edital_id=edital.id,
        idempotency_key="alocar-131",
        correlation_id="teste-131",
    )
    return Actor("joao", gestor.institution_scope, frozenset())


def _recusa(funcao):
    with pytest.raises(DomainError) as recusa:
        funcao()
    return recusa.value


def _conferencias(convocacao, requisito):
    return ConferenciaDeDocumento.objects.filter(item=item(convocacao, requisito)).count()


# --- 1 e 10: o incondicional não se afasta ----------------------------------------------------


@pytest.mark.parametrize("requisito", [CERTIDAO, HISTORICO, AUTODECLARACAO])
def test_incondicional_nao_se_afasta(cenario, alocado, gestor, requisito):
    """Nem pelo alocado nem por quem gere a comissão: não há quem dispense (2ª decisão)."""
    convocacao = cenario["ppi"]
    for ator, chave in ((alocado, "a"), (gestor, "g")):
        recusa = _recusa(
            lambda ator=ator, chave=chave: conferir(
                ator,
                convocacao,
                requisito,
                "NAO_SE_APLICA",
                chave=f"{chave}-{requisito}",
                motivo=FATO,
            )
        )
        assert recusa.code == nomes.NAO_SE_APLICA_SEM_CONDICAO
    assert _conferencias(convocacao, requisito) == 0


def test_tres_incondicionais_afastados_nao_chegam_ao_aceite(cenario, alocado):
    """O cenário do estudo de 07/11, que o aceite deixava passar: agora nem se registra."""
    convocacao = cenario["ppi"]
    for requisito in (CERTIDAO, HISTORICO, AUTODECLARACAO):
        _recusa(
            lambda requisito=requisito: conferir(
                alocado,
                convocacao,
                requisito,
                "NAO_SE_APLICA",
                chave=f"t-{requisito}",
                motivo="Dispensado.",
            )
        )

    pendentes = {
        lido.nome for lido in servico.leitura_da_chamada(convocacao).pendencias_para_incluir
    }
    assert {"Autodeclaração étnico-racial", "Histórico escolar do ensino médio"} <= pendentes


# --- 2 e 8: o condicional, pelo alocado -------------------------------------------------------


def test_o_alocado_registra_o_nao_se_aplica_no_condicional(cenario, alocado):
    convocacao = cenario["ppi"]

    conferencia = conferir(
        alocado, convocacao, ALISTAMENTO, "NAO_SE_APLICA", chave="ok", motivo=FATO
    )

    assert conferencia.conferido_por == "joao"
    assert conferencia.motivo == FATO
    assert conferencia.apresentacao_id is None
    item_lido = lido(convocacao, ALISTAMENTO)
    assert item_lido.estado == nomes.ITEM_NAO_SE_APLICA
    assert item_lido.condicao == CONDICAO
    assert item_lido not in servico.leitura_da_chamada(convocacao).pendencias_para_incluir


# --- 5 e 6: o motivo ----------------------------------------------------------------------------


def test_nao_se_aplica_sem_motivo_e_recusado(cenario, alocado):
    recusa = _recusa(
        lambda: conferir(alocado, cenario["ppi"], ALISTAMENTO, "NAO_SE_APLICA", chave="sem")
    )
    assert recusa.code == nomes.MOTIVO_DA_CONFERENCIA_OBRIGATORIO


@pytest.mark.parametrize("motivo", [".", "-", "...", " . ", "—", "?!"])
@pytest.mark.parametrize("resultado", ["NAO_SE_APLICA", "PENDENTE"])
def test_motivo_sem_palavra_e_recusado(cenario, alocado, motivo, resultado):
    convocacao = cenario["ppi"]

    recusa = _recusa(
        lambda: conferir(
            alocado, convocacao, ALISTAMENTO, resultado, chave=f"{resultado}{motivo}", motivo=motivo
        )
    )

    assert recusa.code == nomes.MOTIVO_SEM_CONTEUDO
    assert _conferencias(convocacao, ALISTAMENTO) == 0


# --- 7: com arquivo -------------------------------------------------------------------------------


def test_com_arquivo_o_nao_se_aplica_pede_a_abertura_e_depois_tranca(cenario, alocado):
    convocacao, pessoa = cenario["ppi"], cenario["pessoa_ppi"]
    enviada = apresentar(pessoa, convocacao, ALISTAMENTO, corpo=b"reservista").apresentacao

    recusa = _recusa(
        lambda: conferir(alocado, convocacao, ALISTAMENTO, "NAO_SE_APLICA", chave="x", motivo=FATO)
    )
    assert recusa.code == nomes.NAO_SE_APLICA_SEM_ABERTURA

    abrir(alocado, enviada)
    conferencia = conferir(
        alocado, convocacao, ALISTAMENTO, "NAO_SE_APLICA", chave="y", motivo=FATO
    )
    assert conferencia.apresentacao_id == enviada.id
    assert conferencia.hash_conferido == enviada.content_hash

    trancado = _recusa(lambda: apresentar(pessoa, convocacao, ALISTAMENTO, corpo=b"outro"))
    assert trancado.code == nomes.DOCUMENTO_JA_CONFERIDO


# --- a substituição -------------------------------------------------------------------------------


def test_trocar_para_nao_se_aplica_sem_arquivo_pede_motivo(cenario, alocado):
    convocacao = cenario["ppi"]
    conferir(alocado, convocacao, ALISTAMENTO, "PENDENTE", chave="p", motivo="Falta o arquivo.")

    recusa = _recusa(
        lambda: conferir(alocado, convocacao, ALISTAMENTO, "NAO_SE_APLICA", chave="n", motivo=FATO)
    )
    assert recusa.code == nomes.MOTIVO_DA_SUBSTITUICAO_OBRIGATORIO

    conferir(
        alocado,
        convocacao,
        ALISTAMENTO,
        "NAO_SE_APLICA",
        chave="n2",
        motivo=FATO,
        motivo_da_substituicao="A candidata apresentou a identidade na conferência.",
    )
    assert lido(convocacao, ALISTAMENTO).estado == nomes.ITEM_NAO_SE_APLICA


def test_sair_do_nao_se_aplica_tambem_pede_motivo(cenario, alocado):
    convocacao = cenario["ppi"]
    conferir(alocado, convocacao, ALISTAMENTO, "NAO_SE_APLICA", chave="n", motivo=FATO)

    recusa = _recusa(
        lambda: conferir(alocado, convocacao, ALISTAMENTO, "PENDENTE", chave="p", motivo="Envie.")
    )
    assert recusa.code == nomes.MOTIVO_DA_SUBSTITUICAO_OBRIGATORIO


def test_a_pendencia_sem_arquivo_continua_sem_motivo_de_revisao(cenario, alocado):
    """A liberdade que a `115` prende para a pendência não muda: só o "não se aplica" pede."""
    convocacao = cenario["ppi"]
    conferir(alocado, convocacao, CERTIDAO, "PENDENTE", chave="p1", motivo="Falta a certidão.")

    conferir(alocado, convocacao, CERTIDAO, "PENDENTE", chave="p2", motivo="Ainda falta.")

    assert lido(convocacao, CERTIDAO).estado == nomes.ITEM_PENDENTE


# --- 11: fora do recorte --------------------------------------------------------------------------


@pytest.mark.parametrize("resultado", ["CONFORME", "PENDENTE", "NAO_SE_APLICA"])
def test_item_fora_do_recorte_nao_se_confere(cenario, gestor, resultado):
    convocacao = cenario["ampla"]
    assert item(convocacao, AUTODECLARACAO).situacao == "NAO_SE_APLICA"

    recusa = _recusa(
        lambda: conferir(
            gestor, convocacao, AUTODECLARACAO, resultado, chave=f"fora-{resultado}", motivo=FATO
        )
    )

    assert recusa.status == 404
    assert _conferencias(convocacao, AUTODECLARACAO) == 0


# --- 12: a correção da convocação ----------------------------------------------------------------


def test_a_correcao_herda_condicao_e_conferencia(cenario, gestor, alocado):
    """A sucessora usa a lista e as conferências da chamada (FR-3573 da `115`)."""
    from tests.fixtures.convocacao import convocar

    convocacao = cenario["ppi"]
    conferir(alocado, convocacao, ALISTAMENTO, "NAO_SE_APLICA", chave="n", motivo=FATO)

    declarado = convocar(
        cenario["edital"],
        gestor,
        convocacao.inscricao_id,
        idempotency_key="corrigir-131",
        motivo="Vencimento corrigido.",
        vencimento=VENCIMENTO + timedelta(days=2),
    )
    sucessora = Convocacao.objects.get(id=declarado["id"])

    herdado = lido(sucessora, ALISTAMENTO)
    assert herdado.estado == nomes.ITEM_NAO_SE_APLICA
    assert herdado.condicao == CONDICAO


def test_a_condicao_se_le_da_versao_da_lista(cenario):
    """FR-4456: o requisito é o da versão que o item cita, e não o da vigente."""
    alvo = item(cenario["ppi"], ALISTAMENTO)

    assert servico.requisito_do_item(alvo)["requiredWhen"] == CONDICAO
    assert alvo.versao_id == cenario["ppi"].versao_id
