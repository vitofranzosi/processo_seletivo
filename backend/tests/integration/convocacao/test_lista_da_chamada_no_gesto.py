"""A lista de documentos da chamada, quando a convocação nasce do gesto dos titulares (115, 050).

**O defeito que estes casos prendem**: o gesto "convocar os titulares num ato só" criava a
convocação sem gravar a lista da chamada, e a `115` só a ligou ao caminho individual. A página dizia
"sem documento pedido", o e-mail não pedia documento, e o aceite era registrado sem documento
nenhum — porque a guarda do desfecho só olhava os itens gravados (FR-3572, FR-3592).

Duas metades, cada uma provada aqui:

- **todo caminho grava a mesma lista**: o gesto passa pela rotina que a chamada individual usa,
  com a versão lida sob a mesma trava, na mesma transação, para a mesma pessoa e condições;
- **a guarda do desfecho que inclui não confia na lista**: ela confere o que a versão da chamada
  pede à pessoa, e recusa quando a lista não o tem (FR-4401, D-020). Lista vazia sozinha não é
  falta (FR-3574).

O cenário é o do 77/2026 — duas vagas, dois titulares e uma suplente —, com os documentos de
matrícula do 72/2026 na convocação (`tests/fixtures/documentos_da_convocacao.py`).
"""

from contextlib import contextmanager
from datetime import timedelta
from unittest import mock

import pytest
from django.core import mail
from django.utils import timezone

from processo_seletivo.auditoria.models import RegistroAuditoria
from processo_seletivo.convocacao.application import documentos as servico
from processo_seletivo.convocacao.application import fluxo
from processo_seletivo.convocacao.application import selectors as leitura_do_recorte
from processo_seletivo.convocacao.domain import nomes
from processo_seletivo.convocacao.models import (
    ApresentacaoDeDocumento,
    Convocacao,
    DesfechoDaConvocacao,
    ItemDaListaDaConvocacao,
)
from processo_seletivo.shared.api.problems import DomainError
from tests.fixtures import documentos_da_convocacao as cenarios
from tests.fixtures.convocacao import convocar
from tests.fixtures.corte import MARCO, regra
from tests.fixtures.documentos_da_convocacao import (
    CERTIDAO,
    CERTIFICADO,
    CERTIFICADO_DO_MEDIO,
    CERTIFICADO_NA_CONVOCACAO,
    FICHA,
    HISTORICO,
    IDENTIDADE,
    RESIDENCIA,
    apresentar,
    conferir,
    convocar_primeira,
    desfechar,
    lido,
)
from tests.fixtures.edital import PROFILE_ID, identificador
from tests.fixtures.ocupacao import MODALIDADE_PPI

pytestmark = [pytest.mark.integration, pytest.mark.django_db(transaction=True)]

VENCIMENTO = timezone.now() + timedelta(days=3)
DO_ALUNO = {CERTIDAO, HISTORICO, CERTIFICADO_DO_MEDIO, RESIDENCIA}
AUTODECLARACAO_PPI = identificador(1311, 0)


def _montar(gestor, api_client, manager_headers, process_payload, *, prefixo, **kwargs):
    """O 77/2026 com os documentos do caso: dois titulares, que o gesto alcança juntos."""
    return cenarios.montar(
        gestor,
        api_client,
        manager_headers,
        process_payload,
        prefixo=prefixo,
        geral=2,
        cut=regra(surplusCount=1),
        **kwargs,
    )


@pytest.fixture
def aluno(db, gestor, api_client, manager_headers, process_payload, raiz_de_arquivos):
    return _montar(
        gestor,
        api_client,
        manager_headers,
        process_payload,
        documentos=cenarios.documentos_do_aluno(),
        prefixo="aluno-lote",
    )


def assinatura(edital):
    return fluxo.previa_dos_titulares(edital=edital, perfil_id=PROFILE_ID, marco_id=MARCO)[
        "assinatura"
    ]


def convocar_titulares(edital, gestor, chave="titulares-lote", *, alcance=None):
    """O gesto da `050`, pela prévia e pela confirmação — o caminho do botão."""
    return fluxo.convocar_titulares(
        actor=gestor,
        processo_id=edital.processo_id,
        edital_id=edital.id,
        perfil_id=PROFILE_ID,
        marco_id=MARCO,
        alcance_confirmado=alcance or assinatura(edital),
        idempotency_key=chave,
        vencimento=VENCIMENTO,
    )


def convocadas(resultado):
    return [Convocacao.objects.get(id=c["id"]) for c in resultado["convocadas"]]


def projecao(convocacao):
    """O que a lista diz, sem o que é próprio da linha (id, chamada, instante)."""
    return sorted(
        (
            str(item.requisito_id),
            item.chave,
            item.situacao,
            item.forma_do_recorte,
            str(item.perfil_id or ""),
            str(item.modalidade_id or ""),
            item.modalidade_codigo,
            str(item.aproveita_requisito_id or ""),
            item.versao_id,
        )
        for item in convocacao.itens_da_lista.all()
    )


@contextmanager
def sem_lista():
    """Reproduz o defeito: a convocação nasce, e a lista não."""
    with mock.patch.object(servico, "gravar_lista_da_chamada", return_value=[]):
        yield


@contextmanager
def sem_o_ultimo_documento():
    """Uma lista que nasce sem o último documento que a versão pede — a lista incompleta."""
    real = servico.aplicabilidade

    def menos_um(*args, **kwargs):
        return real(*args, **kwargs)[:-1]

    with mock.patch.object(servico, "aplicabilidade", side_effect=menos_um):
        yield


# --- 1 e 2: cada caminho grava a lista ------------------------------------------------------------


def test_a_chamada_individual_grava_os_obrigatorios(aluno, gestor):
    """FR-3572: o caminho que já gravava, como referência dos demais."""
    _, convocacao = convocar_primeira(aluno, gestor, chave="individual")

    assert {str(i.requisito_id) for i in convocacao.itens_da_lista.all()} == DO_ALUNO
    assert {i.situacao for i in convocacao.itens_da_lista.all()} == {"OBRIGATORIO"}
    assert servico.faltas_na_lista(convocacao) == []


def test_o_gesto_dos_titulares_grava_a_lista_de_cada_convocada(aluno, gestor):
    """FR-3572: "individualmente ou no lote de titulares da `050`" — no lote também."""
    edital, _, _ = aluno

    praticadas = convocadas(convocar_titulares(edital, gestor))

    assert len(praticadas) == 2
    for convocacao in praticadas:
        itens = list(convocacao.itens_da_lista.all())
        assert {str(i.requisito_id) for i in itens} == DO_ALUNO
        assert {i.situacao for i in itens} == {"OBRIGATORIO"}
        assert {i.versao_id for i in itens} == {convocacao.versao_id}
        assert {i.gravada_em for i in itens} == {convocacao.criado_em}
        assert {i.inscricao_id for i in itens} == {convocacao.inscricao_id}
        leitura = servico.leitura_da_chamada(convocacao)
        assert leitura.estado == nomes.DOCUMENTOS_AGUARDANDO
        assert len(leitura.pendencias_para_incluir) == 4


def test_o_email_do_gesto_pede_os_documentos(aluno, gestor):
    """O sintoma que o estudo viu: o e-mail do lote não dizia que a convocação pede documentos."""
    edital, _, _ = aluno

    convocar_titulares(edital, gestor, chave="email")

    assert len(mail.outbox) == 2
    for mensagem in mail.outbox:
        assert "Esta convocação pede documentos" in mensagem.body


# --- 3: equivalência ------------------------------------------------------------------------------


def test_o_gesto_e_a_chamada_individual_gravam_listas_equivalentes(aluno, gestor):
    """SC-1341: mesma versão, Perfil e modalidade — a mesma lista, por qualquer caminho."""
    edital, _, _ = aluno
    _, individual = convocar_primeira(aluno, gestor, chave="primeiro-a-mao")

    (do_gesto,) = convocadas(convocar_titulares(edital, gestor, chave="resto-no-gesto"))

    assert individual.inscricao_id != do_gesto.inscricao_id
    assert individual.versao_id == do_gesto.versao_id
    assert projecao(do_gesto) == projecao(individual)


# --- 4: recorte por modalidade ----------------------------------------------------------------


def test_o_recorte_por_modalidade_vale_pessoa_a_pessoa_no_gesto(
    db, gestor, api_client, manager_headers, process_payload, raiz_de_arquivos
):
    """A autodeclaração só se pede a quem declarou a modalidade; ao outro, "não se aplica"."""
    documentos = [
        *cenarios.documentos_do_aluno()[:2],
        {
            "id": AUTODECLARACAO_PPI,
            "key": "autodeclaracao-ppi",
            "name": "Autodeclaração étnico-racial",
            "instructions": "",
            "required": True,
            "order": 3,
            "moment": "AT_CALL",
            "modalityId": MODALIDADE_PPI,
        },
    ]
    edital, _, inscricoes = _montar(
        gestor,
        api_client,
        manager_headers,
        process_payload,
        documentos=documentos,
        prefixo="recorte-lote",
        ppi=0,
        modalidades={0: MODALIDADE_PPI},
    )

    praticadas = {c.inscricao_id: c for c in convocadas(convocar_titulares(edital, gestor))}

    declarou = praticadas[inscricoes[0].id]
    nao_declarou = next(c for i, c in praticadas.items() if i != inscricoes[0].id)
    assert lido(declarou, AUTODECLARACAO_PPI).item.situacao == "OBRIGATORIO"
    assert lido(nao_declarou, AUTODECLARACAO_PPI).item.situacao == "NAO_SE_APLICA"
    assert lido(nao_declarou, CERTIDAO).item.situacao == "OBRIGATORIO"
    assert servico.faltas_na_lista(declarou) == []
    assert servico.faltas_na_lista(nao_declarou) == []


# --- 5: facultativo -----------------------------------------------------------------------------


def test_o_facultativo_entra_na_lista_do_gesto_e_nao_impede_o_aceite(
    db, gestor, api_client, manager_headers, process_payload, raiz_de_arquivos
):
    """FR-3592: o facultativo adverte e não impede — e, para advertir, precisa estar na lista."""
    edital, _, _ = _montar(
        gestor,
        api_client,
        manager_headers,
        process_payload,
        documentos=[
            cenarios.documentos_do_bolsista()[0],
            {**cenarios.documentos_do_bolsista()[1], "required": False},
        ],
        prefixo="facultativo-lote",
    )

    convocacao, _ = convocadas(convocar_titulares(edital, gestor))

    assert lido(convocacao, FICHA).item.situacao == "FACULTATIVO"
    assert servico.faltas_na_lista(convocacao) == []
    desfechar(edital, gestor, convocacao, nomes.ACEITE, "aceite-facultativo")
    assert DesfechoDaConvocacao.objects.get(convocacao=convocacao).especie == nomes.ACEITE


# --- 6: aproveitamento da inscrição ------------------------------------------------------------


def test_o_gesto_aproveita_o_documento_da_inscricao(
    db, gestor, api_client, manager_headers, process_payload, raiz_de_arquivos
):
    """FR-3576: o certificado enviado na inscrição atende a convocação do gesto, sem cópia."""
    edital, _, _ = _montar(
        gestor,
        api_client,
        manager_headers,
        process_payload,
        documentos=cenarios.documentos_do_certificado(),
        documentos_da_inscricao=(IDENTIDADE, CERTIFICADO),
        prefixo="aproveitamento-lote",
    )

    for convocacao in convocadas(convocar_titulares(edital, gestor)):
        alvo = lido(convocacao, CERTIFICADO_NA_CONVOCACAO)
        original = convocacao.inscricao.documentos.get(requirement_id=CERTIFICADO)
        assert alvo.estado == nomes.ITEM_RECEBIDO
        assert alvo.vigente.documento_da_inscricao_id == original.id
        assert alvo.vigente.content_hash == original.content_hash
        assert not alvo.vigente.arquivo
        assert alvo.vigente.apresentado_por == f"convocacao:{convocacao.id}"


# --- 7: convocação legitimamente sem documentos --------------------------------------------------


def test_o_edital_sem_documento_na_convocacao_aceita_sem_lista(
    db, gestor, api_client, manager_headers, process_payload, raiz_de_arquivos
):
    """FR-3574: lista vazia não é falta — o Edital que não pede nada continua como antes."""
    edital, _, _ = _montar(
        gestor,
        api_client,
        manager_headers,
        process_payload,
        documentos=[cenarios.documentos_do_aluno()[0]],
        prefixo="sem-documentos-lote",
    )

    convocacao, _ = convocadas(convocar_titulares(edital, gestor))

    assert not convocacao.itens_da_lista.exists()
    assert servico.faltas_na_lista(convocacao) == []
    assert servico.leitura_da_chamada(convocacao).estado == nomes.DOCUMENTOS_SEM_EXIGENCIA
    desfechar(edital, gestor, convocacao, nomes.ACEITE, "aceite-sem-documentos")
    assert DesfechoDaConvocacao.objects.get(convocacao=convocacao).especie == nomes.ACEITE


# --- 8: a guarda do desfecho que inclui ----------------------------------------------------------


def test_o_aceite_da_convocacao_sem_lista_e_recusado(aluno, gestor):
    """FR-4401: o caso do estudo de 07/11 — gesto, zero itens, aceite. Agora recusado."""
    edital, _, _ = aluno
    with sem_lista():
        convocacao, _ = convocadas(convocar_titulares(edital, gestor))
    assert not convocacao.itens_da_lista.exists(), "o defeito reproduzido"
    assert servico.leitura_da_chamada(convocacao).pendencias_para_incluir == []

    with pytest.raises(DomainError) as recusa:
        desfechar(edital, gestor, convocacao, nomes.ACEITE, "aceite-sem-lista")

    assert recusa.value.code == nomes.LISTA_DA_CONVOCACAO_INCOMPLETA
    assert recusa.value.status == 409
    for nome in (
        "Certidão de nascimento ou casamento",
        "Histórico escolar do ensino médio",
        "Certificado de conclusão do ensino médio",
        "Comprovante de residência",
    ):
        assert nome in recusa.value.detail
    assert not DesfechoDaConvocacao.objects.filter(convocacao=convocacao).exists()


def test_o_aceite_da_lista_incompleta_e_recusado_nomeando_so_o_que_falta(aluno, gestor):
    """Os três itens gravados não bastam: falta o quarto, e só ele é nomeado."""
    edital, _, _ = aluno
    with sem_o_ultimo_documento():
        pessoa, convocacao = convocar_primeira(aluno, gestor, chave="incompleta")
    assert convocacao.itens_da_lista.count() == 3
    for indice, requisito in enumerate((CERTIDAO, HISTORICO, CERTIFICADO_DO_MEDIO)):
        apresentar(pessoa, convocacao, requisito, corpo=f"documento {indice}".encode())
        conferir(gestor, convocacao, requisito, "CONFORME", chave=f"incompleta-{indice}")
    assert servico.leitura_da_chamada(convocacao).pendencias_para_incluir == []

    with pytest.raises(DomainError) as recusa:
        desfechar(edital, gestor, convocacao, nomes.ACEITE, "aceite-incompleta")

    assert recusa.value.code == nomes.LISTA_DA_CONVOCACAO_INCOMPLETA
    assert "Comprovante de residência" in recusa.value.detail
    assert "Certidão de nascimento" not in recusa.value.detail
    assert not DesfechoDaConvocacao.objects.filter(convocacao=convocacao).exists()


def test_a_regularizacao_da_convocacao_sem_lista_e_recusada(
    db, gestor, api_client, manager_headers, process_payload, raiz_de_arquivos
):
    """A regularização também inclui na ocupação, e passa pela mesma guarda (FR-3592)."""
    edital, _, _ = cenarios.montar(
        gestor,
        api_client,
        manager_headers,
        process_payload,
        documentos=cenarios.documentos_do_aluno(),
        prefixo="regularizar-sem-lista",
        indeferidas=(0, 1),
    )
    primeiro = leitura_do_recorte.contexto_do_recorte(
        edital=edital, perfil_id=PROFILE_ID, marco_id=MARCO, lista_id=None
    )["regularizaveis"][0]
    with sem_lista():
        declarado = convocar(
            edital,
            gestor,
            primeiro,
            especie=nomes.PARA_REGULARIZAR,
            idempotency_key="para-regularizar",
        )
    convocacao = Convocacao.objects.get(id=declarado["id"])

    with pytest.raises(DomainError) as recusa:
        desfechar(edital, gestor, convocacao, nomes.REGULARIZACAO, "regularizar")

    assert recusa.value.code == nomes.LISTA_DA_CONVOCACAO_INCOMPLETA
    assert not DesfechoDaConvocacao.objects.filter(convocacao=convocacao).exists()


def test_os_desfechos_que_nao_incluem_nao_leem_a_lista(aluno, gestor):
    """FR-3593: a guarda é de quem inclui; a desistência da convocação defeituosa se registra."""
    edital, _, _ = aluno
    with sem_lista():
        convocacao, _ = convocadas(convocar_titulares(edital, gestor))

    desfechar(edital, gestor, convocacao, nomes.DESISTENCIA_EXPRESSA, "desistiu", "Desistiu.")

    desfecho = DesfechoDaConvocacao.objects.get(convocacao=convocacao)
    assert desfecho.especie == nomes.DESISTENCIA_EXPRESSA


# --- 9: falha durante a gravação ----------------------------------------------------------------


def test_a_falha_na_lista_de_uma_pessoa_desfaz_o_gesto_inteiro(aluno, gestor):
    """Nenhuma convocação sem lista, nenhuma lista sem convocação, nenhuma trilha, nenhum e-mail."""
    edital, _, _ = aluno
    real = servico.gravar_lista_da_chamada
    chamadas = []

    def falha_na_segunda(convocacao, *, versao):
        chamadas.append(convocacao.id)
        if len(chamadas) == 2:
            raise RuntimeError("falha simulada ao gravar a lista")
        return real(convocacao, versao=versao)

    vista = assinatura(edital)
    with mock.patch.object(servico, "gravar_lista_da_chamada", side_effect=falha_na_segunda):
        with pytest.raises(RuntimeError):
            convocar_titulares(edital, gestor, chave="falha", alcance=vista)

    assert len(chamadas) == 2, "a primeira lista chegou a ser gravada antes da falha"
    assert Convocacao.objects.count() == 0
    assert ItemDaListaDaConvocacao.objects.count() == 0
    assert ApresentacaoDeDocumento.objects.count() == 0
    assert not RegistroAuditoria.objects.filter(operation="CONVOCACAO_CONVOCAR").exists()
    assert mail.outbox == []

    # A reserva da chave se desfez com o resto: a mesma confirmação, de novo, pratica o gesto.
    praticadas = convocadas(convocar_titulares(edital, gestor, chave="falha", alcance=vista))
    assert len(praticadas) == 2
    assert all(servico.faltas_na_lista(c) == [] for c in praticadas)


# --- 10: reexecução ---------------------------------------------------------------------------


def test_repetir_o_gesto_nao_duplica_a_lista(aluno, gestor):
    """A mesma chave devolve o ato; outra chave não acha titular a chamar. A lista é a mesma."""
    edital, _, _ = aluno
    vista = assinatura(edital)
    primeira = convocar_titulares(edital, gestor, chave="repetir", alcance=vista)
    itens = set(ItemDaListaDaConvocacao.objects.values_list("id", flat=True))

    segunda = convocar_titulares(edital, gestor, chave="repetir", alcance=vista)
    with pytest.raises(DomainError) as recusa:
        convocar_titulares(edital, gestor, chave="outra-chave")

    assert segunda["convocadas"] == primeira["convocadas"]
    assert recusa.value.code == nomes.NENHUM_TITULAR_A_CONVOCAR
    assert set(ItemDaListaDaConvocacao.objects.values_list("id", flat=True)) == itens
    assert len(itens) == 8


# --- 11: herança na correção --------------------------------------------------------------------


def test_a_correcao_da_convocacao_do_gesto_herda_a_lista(aluno, gestor):
    """D-009: a sucessora não grava lista, lê a da raiz, e o aceite dela espera os documentos."""
    edital, _, _ = aluno
    raiz, _ = convocadas(convocar_titulares(edital, gestor))

    declarado = convocar(
        edital,
        gestor,
        raiz.inscricao_id,
        idempotency_key="corrigir-gesto",
        motivo="Vencimento informado errado.",
        vencimento=VENCIMENTO + timedelta(days=2),
    )
    sucessora = Convocacao.objects.get(id=declarado["id"])

    assert sucessora.convocacao_anterior_id == raiz.id
    assert not sucessora.itens_da_lista.exists()
    assert len(servico.leitura_da_chamada(sucessora).itens) == 4
    assert servico.faltas_na_lista(sucessora) == []
    with pytest.raises(DomainError) as recusa:
        desfechar(edital, gestor, sucessora, nomes.ACEITE, "aceite-sucessora")
    assert recusa.value.code == nomes.DOCUMENTOS_NAO_CONFERIDOS


def test_corrigir_a_convocacao_sem_lista_nao_a_conserta(aluno, gestor):
    """A sucessora herda a lista da raiz — e, se a raiz não tem, herda a falta, e a recusa."""
    edital, _, _ = aluno
    with sem_lista():
        raiz, _ = convocadas(convocar_titulares(edital, gestor))

    declarado = convocar(
        edital,
        gestor,
        raiz.inscricao_id,
        idempotency_key="corrigir-sem-lista",
        motivo="Vencimento informado errado.",
        vencimento=VENCIMENTO + timedelta(days=2),
    )
    sucessora = Convocacao.objects.get(id=declarado["id"])

    assert not ItemDaListaDaConvocacao.objects.exists()
    with pytest.raises(DomainError) as recusa:
        desfechar(edital, gestor, sucessora, nomes.ACEITE, "aceite-sucessora-sem-lista")
    assert recusa.value.code == nomes.LISTA_DA_CONVOCACAO_INCOMPLETA
