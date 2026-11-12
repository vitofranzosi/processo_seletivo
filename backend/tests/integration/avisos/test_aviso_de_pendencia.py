"""O aviso de pendência documental por e-mail (134): o gesto, as exclusões, o texto e o envio.

**A quinta situação da FR-084 da `010`.** Quem confere decide avisar, num gesto, as pessoas com
documento pendente na chamada; o gesto grava um aviso da `066` por pessoa, e o despacho da `066` o
envia. Os casos provam o que o usuário decidiu em 08/11/2026: nada depois do vencimento, do desfecho
ou do reenvio, um por pessoa por chamada por dia, o nome do documento sem o de modalidade, e nunca
o motivo nem dado da pessoa.

**Fictício.** O Edital, as pessoas e os documentos saem das fixtures; nenhuma mensagem sai do
processo: o backend de correio da suíte é o de memória.
"""

from datetime import timedelta

import pytest
from django.core import mail
from django.urls import reverse
from django.utils import timezone

from processo_seletivo.auditoria.models import RegistroAuditoria
from processo_seletivo.avisos.application import pendencias
from processo_seletivo.avisos.application.despacho import despachar
from processo_seletivo.avisos.domain import nomes
from processo_seletivo.avisos.domain.pendencia import DOCUMENTO_DE_MODALIDADE, NAO_E_A_CONVOCACAO
from processo_seletivo.avisos.models import (
    Aviso,
    DestinatarioDoAviso,
    InterrupcaoDoAviso,
    ResultadoDaTentativa,
    TentativaDeEnvio,
)
from processo_seletivo.convocacao.application import fluxo
from processo_seletivo.convocacao.domain import nomes as nomes_da_convocacao
from processo_seletivo.convocacao.models import ComunicacaoEmitida, Convocacao
from processo_seletivo.publicacoes.domain.vocabulario_da_regra import FORMA_POR_PUBLICACAO
from processo_seletivo.seguranca.domain import Actor
from processo_seletivo.shared.api.problems import DomainError
from tests.fixtures import documentos_da_convocacao as cenarios
from tests.fixtures.convocacao import convocar
from tests.fixtures.corte import MARCO, regra
from tests.fixtures.documentos_da_convocacao import (
    HISTORICO,
    RESIDENCIA,
    apresentar,
    conferir,
)
from tests.fixtures.edital import PROFILE_ID, identificador
from tests.fixtures.ocupacao import MODALIDADE_PPI

pytestmark = [pytest.mark.integration, pytest.mark.django_db(transaction=True)]

AUTODECLARACAO = identificador(1341, 1)
NOME_DA_AUTODECLARACAO = "Autodeclaração étnico-racial"
MOTIVO = "o arquivo está cortado na margem direita"
VENCIMENTO = timezone.now() + timedelta(days=3)
PORTAL = "http://testserver/selecoes/"


def _documentos():
    return [
        *cenarios.documentos_do_aluno()[:3],
        {
            "id": RESIDENCIA,
            "key": "residencia",
            "name": "Comprovante de residência",
            "instructions": "",
            "required": True,
            "order": 4,
            "moment": "AT_CALL",
        },
        {
            "id": AUTODECLARACAO,
            "key": "autodeclaracao-ppi",
            "name": NOME_DA_AUTODECLARACAO,
            "instructions": "",
            "required": True,
            "order": 5,
            "moment": "AT_CALL",
            "modalityId": MODALIDADE_PPI,
        },
    ]


@pytest.fixture
def cenario(db, gestor, api_client, manager_headers, process_payload, raiz_de_arquivos):
    """Duas pessoas convocadas e comunicadas por mensagem individual; uma declarou a PPI."""
    edital, _, inscricoes = cenarios.montar(
        gestor,
        api_client,
        manager_headers,
        process_payload,
        documentos=_documentos(),
        prefixo="pendencia-134",
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
        idempotency_key="titulares-134",
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
    mail.outbox.clear()
    return {
        "edital": edital,
        "ppi": ppi,
        "ampla": ampla,
        "pessoa_ppi": inscricoes[0],
        "pessoa_ampla": next(i for i in inscricoes if i.id == ampla.inscricao_id),
    }


@pytest.fixture
def alocado(cenario, gestor):
    """O membro `joao`, só alocado à conferência deste Edital."""
    from processo_seletivo.comissoes.application.alocacao import alocar_a_conferencia
    from processo_seletivo.comissoes.models import MembroComissao

    edital = cenario["edital"]
    membro = MembroComissao.objects.get(processo=edital.processo, identity_subject="joao")
    alocar_a_conferencia(
        actor=gestor,
        processo_id=edital.processo_id,
        membro_id=membro.id,
        edital_id=edital.id,
        idempotency_key="alocar-134",
        correlation_id="teste-134",
    )
    return Actor("joao", gestor.institution_scope, frozenset())


def _pendente(ator, convocacao, requisito, chave):
    return conferir(ator, convocacao, requisito, "PENDENTE", chave=chave, motivo=MOTIVO)


def _avisar(ator, edital, *, chave="avisar-134", lista_id=None):
    return pendencias.avisar_pendencias(
        actor=ator,
        edital_id=edital.id,
        perfil_id=PROFILE_ID,
        marco_id=MARCO,
        lista_id=lista_id,
        endereco_do_portal=PORTAL,
        idempotency_key=chave,
        correlation_id="teste-134",
    )


def _selecao(edital, *, agora=None):
    return pendencias.selecionar(
        edital=edital,
        perfil_id=PROFILE_ID,
        marco_id=MARCO,
        lista_id=None,
        agora=agora or timezone.now(),
    )


def _exclusoes(selecao):
    return {pessoa.convocacao.id: pessoa.exclusao for pessoa in selecao.pessoas}


def _recusa(funcao):
    with pytest.raises(DomainError) as erro:
        funcao()
    return erro.value


def _avisos_de_pendencia():
    return Aviso.objects.filter(origem=nomes.PENDENCIA)


# --- O gesto e a seleção (US1, FR-4603 a FR-4608, SC-1441) ----------------------------------------


def test_o_gesto_grava_um_aviso_por_pessoa_com_pendencia_e_nada_sai_no_clique(cenario, alocado):
    _pendente(alocado, cenario["ampla"], RESIDENCIA, "pend-1")
    comunicacoes = ComunicacaoEmitida.objects.count()

    declarado = _avisar(alocado, cenario["edital"])

    assert declarado["alcancadas"] == 1
    aviso = _avisos_de_pendencia().get()
    assert (aviso.motivo, aviso.natureza, aviso.referencia_da_publicacao) == (
        nomes.PRIMEIRO_AVISO,
        "",
        "",
    )
    destinatario = DestinatarioDoAviso.objects.get(aviso=aviso)
    assert destinatario.convocacao_id == cenario["ampla"].id
    assert destinatario.elegibilidade == nomes.ELEGIVEL
    assert destinatario.endereco
    # **Nada sai no clique** (FR-4619, FR-1265 da `066`), e o aviso não é comunicação (FR-4618).
    assert mail.outbox == []
    assert ComunicacaoEmitida.objects.count() == comunicacoes


def test_quem_nunca_teve_pendencia_nao_entra_nem_na_contagem(cenario, alocado):
    _pendente(alocado, cenario["ampla"], RESIDENCIA, "pend-1")

    selecao = _selecao(cenario["edital"])

    assert [p.convocacao.id for p in selecao.pessoas] == [cenario["ampla"].id]


def test_o_despacho_envia_e_a_trilha_registra_o_gesto_e_o_envio(cenario, alocado):
    _pendente(alocado, cenario["ampla"], RESIDENCIA, "pend-1")
    vencimento = Convocacao.objects.get(id=cenario["ampla"].id).vencimento

    declarado = _avisar(alocado, cenario["edital"])
    resumo = despachar()

    assert resumo.tentadas == 1
    assert len(mail.outbox) == 1
    gesto = RegistroAuditoria.objects.get(operation=nomes.OPERACAO_AVISAR_PENDENCIAS)
    assert gesto.actor_subject == "joao"
    assert gesto.detalhe["avisos"] == declarado["avisos"]
    envio = RegistroAuditoria.objects.get(operation=nomes.OPERACAO_ENVIO_DA_PENDENCIA)
    assert envio.actor_subject == nomes.SUJEITO_DO_DESPACHO
    assert str(envio.aggregate_id) == declarado["avisos"][0]
    assert envio.detalhe == {"tentativa": 1, "resultado": nomes.ACEITA}
    # **A trilha não leva endereço nem nome** (FR-4620, FR-4621).
    endereco = DestinatarioDoAviso.objects.get().endereco
    for registro in (gesto, envio):
        assert endereco not in f"{registro.reason}{registro.detalhe}"
        assert cenario["pessoa_ampla"].nome not in f"{registro.reason}{registro.detalhe}"
    # **Não reinicia prazo** (FR-4618, SC-1447).
    assert Convocacao.objects.get(id=cenario["ampla"].id).vencimento == vencimento


def test_quem_so_le_a_conducao_nao_avisa(cenario, alocado, sem_nada):
    _pendente(alocado, cenario["ampla"], RESIDENCIA, "pend-1")

    erro = _recusa(lambda: _avisar(sem_nada, cenario["edital"]))

    assert erro.status == 404
    assert not _avisos_de_pendencia().exists()


def test_quem_gere_a_comissao_tambem_avisa(cenario, alocado, gestor):
    _pendente(alocado, cenario["ampla"], RESIDENCIA, "pend-1")

    assert _avisar(gestor, cenario["edital"])["alcancadas"] == 1


def test_o_duplo_clique_devolve_o_primeiro(cenario, alocado):
    _pendente(alocado, cenario["ampla"], RESIDENCIA, "pend-1")

    primeiro = _avisar(alocado, cenario["edital"], chave="mesma")
    segundo = _avisar(alocado, cenario["edital"], chave="mesma")

    assert primeiro == segundo
    assert _avisos_de_pendencia().count() == 1


# --- As exclusões (US2, FR-4606, FR-4607, FR-4609) ------------------------------------------------


def test_com_desfecho_nao_ha_aviso(cenario, alocado, gestor):
    _pendente(alocado, cenario["ampla"], RESIDENCIA, "pend-1")
    cenarios.desfechar(
        cenario["edital"],
        gestor,
        cenario["ampla"],
        nomes_da_convocacao.DESISTENCIA_EXPRESSA,
        "desiste-134",
    )

    erro = _recusa(lambda: _avisar(alocado, cenario["edital"]))

    assert erro.code == nomes.AVISO_SEM_PENDENCIA_A_AVISAR
    assert pendencias.COM_DESFECHO in erro.detail
    assert not _avisos_de_pendencia().exists()


def test_vencimento_decorrido_nao_ha_aviso(cenario, alocado):
    _pendente(alocado, cenario["ampla"], RESIDENCIA, "pend-1")

    depois = _selecao(cenario["edital"], agora=VENCIMENTO + timedelta(minutes=1))
    antes = _selecao(cenario["edital"], agora=VENCIMENTO - timedelta(minutes=1))

    assert _exclusoes(depois) == {cenario["ampla"].id: pendencias.VENCIDA}
    assert _exclusoes(antes) == {cenario["ampla"].id: ""}


def test_item_reenviado_depois_da_pendencia_nao_entra(cenario, alocado):
    ampla, pessoa = cenario["ampla"], cenario["pessoa_ampla"]
    _pendente(alocado, ampla, RESIDENCIA, "pend-1")
    apresentar(pessoa, ampla, RESIDENCIA, corpo=b"comprovante legivel")

    erro = _recusa(lambda: _avisar(alocado, cenario["edital"]))

    assert erro.code == nomes.AVISO_SEM_PENDENCIA_A_AVISAR
    assert pendencias.COMPLEMENTADA in erro.detail
    # O nome da página de documentos (154, FR-6212, cenário 4 da US3).
    assert "documento reenviado — aguardando nova conferência" in erro.detail


def test_so_o_item_ainda_pendente_entra_no_texto(cenario, alocado):
    ampla, pessoa = cenario["ampla"], cenario["pessoa_ampla"]
    _pendente(alocado, ampla, RESIDENCIA, "pend-1")
    _pendente(alocado, ampla, HISTORICO, "pend-2")
    apresentar(pessoa, ampla, HISTORICO, corpo=b"historico completo")

    _avisar(alocado, cenario["edital"])

    corpo = _avisos_de_pendencia().get().corpo
    assert "- Comprovante de residência" in corpo
    assert "Histórico escolar" not in corpo


def test_um_aviso_por_pessoa_por_chamada_por_dia(cenario, alocado):
    _pendente(alocado, cenario["ampla"], RESIDENCIA, "pend-1")
    _avisar(alocado, cenario["edital"], chave="hoje-1")

    erro = _recusa(lambda: _avisar(alocado, cenario["edital"], chave="hoje-2"))
    amanha = _selecao(cenario["edital"], agora=timezone.now() + timedelta(days=1))

    assert erro.code == nomes.AVISO_SEM_PENDENCIA_A_AVISAR
    assert pendencias.JA_AVISADA_HOJE in erro.detail
    assert _avisos_de_pendencia().count() == 1
    # **Amanhã, se a pendência continuar, pode** (SC-1442).
    assert _exclusoes(amanha) == {cenario["ampla"].id: ""}


def test_o_limite_e_da_chamada_e_nao_de_quem_foi_avisado(cenario, alocado):
    """O aviso de uma pessoa não tira a outra do gesto seguinte, no mesmo dia (D-003)."""
    _pendente(alocado, cenario["ampla"], RESIDENCIA, "pend-1")
    _avisar(alocado, cenario["edital"], chave="primeiro")
    _pendente(alocado, cenario["ppi"], RESIDENCIA, "pend-2")

    declarado = _avisar(alocado, cenario["edital"], chave="segundo")

    assert declarado["alcancadas"] == 1
    assert {"motivo": pendencias.JA_AVISADA_HOJE, "quantas": 1} in declarado["exclusoes"]
    assert (
        DestinatarioDoAviso.objects.filter(aviso__origem=nomes.PENDENCIA)
        .values_list("convocacao_id", flat=True)
        .distinct()
        .count()
        == 2
    )


def test_sem_endereco_fica_de_fora_contado_a_parte(cenario, alocado, monkeypatch):
    """FR-4608: sem endereço não há aviso, e a resposta o conta à parte (D-006)."""
    from processo_seletivo.identidade.application import endereco

    _pendente(alocado, cenario["ampla"], RESIDENCIA, "pend-1")
    _pendente(alocado, cenario["ppi"], RESIDENCIA, "pend-2")
    sem = cenario["pessoa_ampla"].id
    original = endereco.enderecos_das_inscricoes

    def sem_o_da_ampla(inscricoes):
        return {i: e for i, e in original(inscricoes).items() if i != sem}

    monkeypatch.setattr(endereco, "enderecos_das_inscricoes", sem_o_da_ampla)

    declarado = _avisar(alocado, cenario["edital"])

    assert declarado["alcancadas"] == 1
    assert {"motivo": pendencias.SEM_ENDERECO, "quantas": 1} in declarado["exclusoes"]
    assert DestinatarioDoAviso.objects.get().convocacao_id == cenario["ppi"].id


def test_registrar_a_pendencia_nao_grava_aviso(cenario, alocado):
    """Por gesto, e nunca por evento (FR-4604)."""
    _pendente(alocado, cenario["ampla"], RESIDENCIA, "pend-1")

    assert not _avisos_de_pendencia().exists()
    assert mail.outbox == []


# --- O texto (US3, FR-4613 a FR-4617, SC-1443) ----------------------------------------------------


def test_o_texto_nomeia_o_documento_e_oculta_o_de_modalidade(cenario, alocado):
    ppi, pessoa = cenario["ppi"], cenario["pessoa_ppi"]
    _pendente(alocado, ppi, RESIDENCIA, "pend-1")
    _pendente(alocado, ppi, AUTODECLARACAO, "pend-2")

    _avisar(alocado, cenario["edital"])
    despachar()

    [mensagem] = mail.outbox
    edital = cenario["edital"]
    texto = f"{mensagem.subject}\n{mensagem.body}"
    assert mensagem.subject == (
        f"Ifes · Edital {edital.number}/{edital.year}: há documento da sua convocação para revisar"
    )
    assert not mensagem.subject.startswith("Convocação")
    assert "- Comprovante de residência" in mensagem.body
    assert f"- {DOCUMENTO_DE_MODALIDADE}" in mensagem.body
    assert NOME_DA_AUTODECLARACAO not in texto
    assert MOTIVO not in texto
    assert pessoa.nome not in texto
    assert pessoa.protocolo not in texto
    assert "PPI" not in texto and "étnico" not in texto
    assert NAO_E_A_CONVOCACAO in mensagem.body
    assert reverse("portal:convocacao", args=[pessoa.id]) in mensagem.body
    assert mensagem.attachments == []
    assert mensagem.to == [DestinatarioDoAviso.objects.get().endereco]


def test_o_texto_diz_o_vencimento_sem_contagem(cenario, alocado):
    from zoneinfo import ZoneInfo

    from django.conf import settings

    from processo_seletivo.avisos.domain.pendencia import frase_do_prazo
    from processo_seletivo.convocacao.domain.prazo_apresentado import apresentar as apresentado

    _pendente(alocado, cenario["ampla"], RESIDENCIA, "pend-1")

    _avisar(alocado, cenario["edital"])

    corpo = _avisos_de_pendencia().get().corpo
    vencimento = Convocacao.objects.get(id=cenario["ampla"].id).vencimento
    prazo = apresentado(vencimento, timezone.now(), ZoneInfo(settings.TIME_ZONE))
    assert frase_do_prazo(prazo) in corpo
    assert prazo.data in corpo and prazo.dia_da_semana in corpo
    assert "faltam" not in corpo and "termina" not in corpo


def test_o_cpf_nao_vai_ao_texto(cenario, alocado):
    pessoa = cenario["pessoa_ampla"]
    _pendente(alocado, cenario["ampla"], RESIDENCIA, "pend-1")

    _avisar(alocado, cenario["edital"])

    aviso = _avisos_de_pendencia().get()
    cpf = getattr(pessoa, "cpf", "") or ""
    digitos = "".join(c for c in cpf if c.isdigit())
    if digitos:
        assert digitos not in aviso.corpo.replace(".", "").replace("-", "")
    assert "CPF" not in aviso.corpo


# --- A convocação por publicação (US4, FR-4612, SC-1444) ------------------------------------------


@pytest.fixture
def por_publicacao(db, gestor, api_client, manager_headers, process_payload, raiz_de_arquivos):
    """Duas pessoas convocadas num Perfil que comunica por publicação; só uma foi publicada."""
    from processo_seletivo.convocacao.application import selectors
    from processo_seletivo.convocacao.application.comunicar import comunicar

    edital, _, _ = cenarios.montar(
        gestor,
        api_client,
        manager_headers,
        process_payload,
        documentos=_documentos()[:4],
        prefixo="pendencia-134-publicacao",
        forma=FORMA_POR_PUBLICACAO,
        geral=2,
        cut=regra(surplusCount=1),
    )
    fila = selectors.contexto_do_recorte(
        edital=edital, perfil_id=PROFILE_ID, marco_id=MARCO, lista_id=None
    )["fila"]
    publicada = convocar(
        edital, gestor, fila[0], vencimento=VENCIMENTO, idempotency_key="pub-conv-1"
    )
    comunicar(
        actor=gestor,
        processo_id=edital.processo_id,
        convocacao_id=publicada["id"],
        idempotency_key="pub-com-1",
        correlation_id="teste-134",
        referencia_da_publicacao="Site do Cefor, 08/11/2026, 1ª chamada.",
    )
    sem_publicacao = convocar(
        edital, gestor, fila[1], vencimento=VENCIMENTO, idempotency_key="pub-conv-2"
    )
    mail.outbox.clear()
    return (
        edital,
        Convocacao.objects.get(id=publicada["id"]),
        Convocacao.objects.get(id=sem_publicacao["id"]),
    )


def test_vale_na_convocacao_por_publicacao(por_publicacao, gestor):
    edital, publicada, sem_publicacao = por_publicacao
    _pendente(gestor, publicada, RESIDENCIA, "pend-pub-1")
    _pendente(gestor, sem_publicacao, RESIDENCIA, "pend-pub-2")

    declarado = _avisar(gestor, edital)
    despachar()

    assert declarado["alcancadas"] == 1
    assert {"motivo": pendencias.NAO_COMUNICADA, "quantas": 1} in declarado["exclusoes"]
    assert DestinatarioDoAviso.objects.get(aviso__origem=nomes.PENDENCIA).convocacao_id == (
        publicada.id
    )
    [mensagem] = mail.outbox
    assert "- Comprovante de residência" in mensagem.body
    # O aviso não é a publicação nem a substitui: nenhuma comunicação nova (FR-4618).
    assert ComunicacaoEmitida.objects.filter(convocacao=sem_publicacao).count() == 0


# --- A chave (US5, FR-4610, SC-1445) --------------------------------------------------------------


def test_com_a_chave_desligada_nada_se_grava_nem_sai(cenario, alocado, settings):
    _pendente(alocado, cenario["ampla"], RESIDENCIA, "pend-1")
    settings.AVISOS_AOS_CANDIDATOS = False

    erro = _recusa(lambda: _avisar(alocado, cenario["edital"]))
    previa = pendencias.previa(
        actor=alocado,
        edital=cenario["edital"],
        perfil_id=PROFILE_ID,
        marco_id=MARCO,
        lista_id=None,
    )

    assert erro.code == nomes.AVISO_ENVIO_DESABILITADO
    assert not _avisos_de_pendencia().exists()
    assert despachar().desabilitado
    assert mail.outbox == []
    assert previa["habilitado"] is False


def test_com_a_chave_desligada_o_despacho_nao_envia_o_que_ja_foi_gravado(
    cenario, alocado, settings
):
    _pendente(alocado, cenario["ampla"], RESIDENCIA, "pend-1")
    _avisar(alocado, cenario["edital"])
    settings.AVISOS_AOS_CANDIDATOS = False

    assert despachar().desabilitado
    assert mail.outbox == []


# --- As telas da `066` (FR-4622, D-008) -----------------------------------------------------------


def test_o_reenvio_da_066_recusa_o_aviso_de_pendencia(cenario, alocado, gestor):
    from processo_seletivo.avisos.application.confirmar import confirmar_reenvio

    _pendente(alocado, cenario["ampla"], RESIDENCIA, "pend-1")
    aviso_id = _avisar(alocado, cenario["edital"])["avisos"][0]

    erro = _recusa(
        lambda: confirmar_reenvio(
            actor=gestor,
            aviso_id=aviso_id,
            motivo=nomes.REENVIO_JUSTIFICADO,
            assinatura="",
            enderecos={},
            idempotency_key="reenvio-134",
            correlation_id="teste-134",
            justificativa="Tentar de novo.",
        )
    )

    assert erro.code == nomes.AVISO_DE_PENDENCIA_SEM_REENVIO


# --- A tela de condução (UX-311 a UX-313) ---------------------------------------------------------


@pytest.fixture
def na_gestao(client, settings):
    settings.INTERFACE_SELETOR_IDENTIDADE = True
    resposta = client.post(
        reverse("interface:identificar"), {"subject": "carlos", "papeis": ["gestor"]}
    )
    assert resposta.status_code == 302
    return client


def test_a_conducao_oferece_o_gesto_e_o_post_responde_o_ato(cenario, alocado, na_gestao):
    _pendente(alocado, cenario["ampla"], RESIDENCIA, "pend-1")
    edital = cenario["edital"]
    conducao = reverse("interface:convocacao", args=[edital.id, MARCO])

    antes = na_gestao.get(conducao).content.decode()
    resposta = na_gestao.post(
        reverse("interface:avisar-pendencias", args=[edital.id, MARCO]),
        {"lista": "", "chave": "tela-134"},
    )
    depois = na_gestao.get(conducao).content.decode()

    assert "Avisar as pessoas com pendência nesta chamada" in antes
    assert "1 pessoa pode ser avisada agora." in antes
    assert resposta.status_code == 302
    assert "1 aviso de pendência registrado para envio" in depois
    assert _avisos_de_pendencia().count() == 1
    assert mail.outbox == []


def test_a_conducao_com_a_chave_desligada_nao_oferece_o_botao(
    cenario, alocado, na_gestao, settings
):
    _pendente(alocado, cenario["ampla"], RESIDENCIA, "pend-1")
    settings.AVISOS_AOS_CANDIDATOS = False
    edital = cenario["edital"]

    corpo = na_gestao.get(reverse("interface:convocacao", args=[edital.id, MARCO])).content
    corpo = corpo.decode()

    assert "envio de avisos desabilitado nesta instalação" in corpo
    assert "Avisar as pessoas com pendência nesta chamada" not in corpo


def test_o_historico_do_edital_nomeia_a_pendencia(cenario, alocado, na_gestao):
    _pendente(alocado, cenario["ampla"], RESIDENCIA, "pend-1")
    aviso_id = _avisar(alocado, cenario["edital"])["avisos"][0]

    lista = na_gestao.get(reverse("interface:avisos-do-edital", args=[cenario["edital"].id]))
    detalhe = na_gestao.get(reverse("interface:aviso", args=[aviso_id]))

    assert "Pendência documental" in lista.content.decode()
    corpo = detalhe.content.decode()
    assert "Pendência documental da convocação" in corpo
    assert "aviso-reenviar" not in corpo and "/reenviar" not in corpo


# --- O despacho relê a pendência antes de enviar (FR-4623, SC-1449, D-011) ------------------------


def _interrupcao_pelo_despacho():
    interrupcao = InterrupcaoDoAviso.objects.get(aviso__origem=nomes.PENDENCIA)
    assert interrupcao.interrompido_por == nomes.SUJEITO_DO_DESPACHO
    return interrupcao


def test_o_despacho_interrompe_o_aviso_cuja_pendencia_foi_resolvida(cenario, alocado):
    ampla, pessoa = cenario["ampla"], cenario["pessoa_ampla"]
    _pendente(alocado, ampla, RESIDENCIA, "pend-1")
    _avisar(alocado, cenario["edital"])
    # A pessoa reenvia entre o gesto e o despacho: o aviso já não tem o que pedir.
    apresentar(pessoa, ampla, RESIDENCIA, corpo=b"comprovante legivel")

    resumo = despachar()

    assert (resumo.tentadas, resumo.interrompidos) == (0, 1)
    assert mail.outbox == []
    assert not TentativaDeEnvio.objects.exists()
    assert pendencias.SEM_PENDENCIA in _interrupcao_pelo_despacho().motivo
    trilha = RegistroAuditoria.objects.get(operation=nomes.OPERACAO_INTERROMPER)
    assert trilha.actor_subject == nomes.SUJEITO_DO_DESPACHO
    assert pessoa.nome not in trilha.reason
    # **Interrompido, não sai mais**: a execução seguinte não o encontra.
    assert despachar().tentadas == 0


def test_o_despacho_interrompe_o_aviso_vencido_antes_do_envio(
    cenario, alocado, monkeypatch, settings
):
    _pendente(alocado, cenario["ampla"], RESIDENCIA, "pend-1")
    _avisar(alocado, cenario["edital"])
    # A janela larga só para que o aviso ainda seja do despacho depois do vencimento.
    settings.AVISOS_JANELA_DE_DESPACHO_HORAS = 24 * 5
    depois = VENCIMENTO + timedelta(minutes=1)
    monkeypatch.setattr(timezone, "now", lambda: depois)

    resumo = despachar()

    assert (resumo.tentadas, resumo.interrompidos) == (0, 1)
    assert mail.outbox == []
    assert pendencias.VENCIDA in _interrupcao_pelo_despacho().motivo


def test_o_despacho_interrompe_o_aviso_cuja_lista_mudou(cenario, alocado):
    _pendente(alocado, cenario["ampla"], RESIDENCIA, "pend-1")
    _avisar(alocado, cenario["edital"])
    # Outro documento passou a pendente depois do gesto: o texto congelado não o nomeia.
    _pendente(alocado, cenario["ampla"], HISTORICO, "pend-2")

    resumo = despachar()

    assert (resumo.tentadas, resumo.interrompidos) == (0, 1)
    assert pendencias.LISTA_MUDOU in _interrupcao_pelo_despacho().motivo


def test_o_aviso_interrompido_pelo_despacho_nao_conta_no_dia(cenario, alocado):
    _pendente(alocado, cenario["ampla"], RESIDENCIA, "pend-1")
    _avisar(alocado, cenario["edital"], chave="primeiro")
    _pendente(alocado, cenario["ampla"], HISTORICO, "pend-2")
    despachar()

    # **Nada saiu**, e o gesto do mesmo dia avisa de novo, com a lista de agora (D-011).
    declarado = _avisar(alocado, cenario["edital"], chave="segundo")
    resumo = despachar()

    assert declarado["alcancadas"] == 1
    assert (resumo.tentadas, resumo.interrompidos) == (1, 0)
    assert len(mail.outbox) == 1
    assert "- Comprovante de residência" in mail.outbox[0].body
    assert "Histórico escolar" in mail.outbox[0].body


def test_quem_ainda_tem_a_mesma_pendencia_recebe(cenario, alocado):
    """A releitura não muda nada para quem continua como o gesto o encontrou."""
    _pendente(alocado, cenario["ampla"], RESIDENCIA, "pend-1")
    _avisar(alocado, cenario["edital"])

    resumo = despachar()

    assert (resumo.tentadas, resumo.interrompidos) == (1, 0)
    assert not InterrupcaoDoAviso.objects.exists()


# --- A trilha do envio (FR-4621) e o Processo em estado final (FR-4610) ---------------------------


def test_a_tentativa_orfa_tambem_vai_a_trilha(cenario, alocado):
    _pendente(alocado, cenario["ampla"], RESIDENCIA, "pend-1")
    declarado = _avisar(alocado, cenario["edital"])
    # Uma execução que morreu entre gravar o início e o resultado.
    TentativaDeEnvio.objects.create(
        destinatario=DestinatarioDoAviso.objects.get(), numero=1, iniciada_em=timezone.now()
    )

    resumo = despachar()

    assert resumo.orfas == 1
    # A indeterminada nunca se repete sozinha (FR-1267 da `066`).
    assert (resumo.tentadas, mail.outbox) == (0, [])
    envio = RegistroAuditoria.objects.get(operation=nomes.OPERACAO_ENVIO_DA_PENDENCIA)
    assert str(envio.aggregate_id) == declarado["avisos"][0]
    assert envio.detalhe == {"tentativa": 1, "resultado": nomes.INDETERMINADA}


def test_a_trilha_que_falha_nao_desfaz_o_resultado(cenario, alocado, monkeypatch):
    """A mensagem saiu: a falha da trilha vai ao log, e o resultado aceito fica registrado."""
    from processo_seletivo.auditoria import application as auditoria

    _pendente(alocado, cenario["ampla"], RESIDENCIA, "pend-1")
    _avisar(alocado, cenario["edital"])

    def falha(**_):
        raise RuntimeError("trilha indisponível")

    monkeypatch.setattr(auditoria, "record_event", falha)
    resumo = despachar()

    assert resumo.resultados == {nomes.ACEITA: 1}
    assert len(mail.outbox) == 1
    assert ResultadoDaTentativa.objects.get().resultado == nomes.ACEITA
    assert not RegistroAuditoria.objects.filter(
        operation=nomes.OPERACAO_ENVIO_DA_PENDENCIA
    ).exists()


def test_processo_em_estado_final_recusa_o_gesto(cenario, alocado):
    from processo_seletivo.processos.models import ProcessoSeletivo

    _pendente(alocado, cenario["ampla"], RESIDENCIA, "pend-1")
    ProcessoSeletivo.objects.filter(pk=cenario["edital"].processo_id).update(
        status=ProcessoSeletivo.Status.CANCELADO
    )

    erro = _recusa(lambda: _avisar(alocado, cenario["edital"]))

    assert erro.code == nomes.AVISO_PROCESSO_EM_ESTADO_FINAL
    assert not _avisos_de_pendencia().exists()
