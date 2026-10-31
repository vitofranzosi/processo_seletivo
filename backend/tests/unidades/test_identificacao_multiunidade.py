"""A identificação da unidade fora do documento oficial, com duas unidades (109, §6 do pedido).

O Cefor da fixture `autouse` e o `campus-a` fictício da convenção da `106` e da `107`, registrado
**só pelo registro** — nenhum caso muda código para que o campus exista (SC-1032). Os oito cenários
do pedido estão nomeados na docstring de cada caso; o oitavo, o Cefor inalterado, tem as frases
exatas que a `main` dizia em `ca1e53ed`, capturadas antes da mudança (SC-1031, `verificacao.md`).
"""

import ast
import re
from pathlib import Path
from types import SimpleNamespace

import pytest
from django.core import mail
from django.test import override_settings
from django.urls import reverse
from django.utils import timezone

from processo_seletivo.auditoria.models import RegistroAuditoria
from processo_seletivo.avisos.application import previa
from processo_seletivo.avisos.application.destinatarios import Universo
from processo_seletivo.avisos.domain import nomes as nomes_do_aviso
from processo_seletivo.convocacao.application.comunicar import _enviar
from processo_seletivo.identidade.application.mensagem import (
    avisar_mudanca_de_credencial,
    enviar_codigo,
)
from processo_seletivo.inscricoes.application.mensagem import enviar_comprovante
from processo_seletivo.interface.avisos import _rodape_visivel
from processo_seletivo.processos.models import Edital
from processo_seletivo.publicacoes.infrastructure import pdf
from processo_seletivo.publicacoes.models import Publicacao
from processo_seletivo.shared.api.problems import DomainError
from processo_seletivo.unidades.application import identificacao
from processo_seletivo.unidades.application.sincronizacao import sincronizar
from processo_seletivo.unidades.models import Unidade
from tests.fixtures.autoridades import CEFOR, registrar_autoridade, registrar_unidade
from tests.fixtures.edital import complete_draft
from tests.fixtures.publicacao import levar_a_publicacao, publish_original
from tests.interface.conftest import identificar
from tests.unit.publicacoes.test_pdf import texto_de

CANAL_DO_CAMPUS = "atendimento@campus-a.example"
CANAL_INSTITUCIONAL = "selecoes@ifes.example"


def _campus(**campos):
    return registrar_unidade(
        "campus-a",
        sigla="Campus A",
        nome="Campus A",
        cabecalho=["Campus A"],
        local="Serra (ES)",
        atendimento=CANAL_DO_CAMPUS,
        **campos,
    )


def _titulo(corpo):
    return re.search(r"<title>(.*?)</title>", corpo, re.S).group(1)


def _publicar_no_campus(api_client, process_payload):
    autoridade = registrar_autoridade(_campus(), cargo="Diretor-Geral do Campus A")
    criado = api_client.post(
        "/api/v1/admin/processos",
        process_payload,
        format="json",
        HTTP_AUTHORIZATION=("Bearer gestor-a|campus-a|processo:criar,processo:ativar,edital:criar"),
        HTTP_IDEMPOTENCY_KEY="campus-a-processo-0001",
        HTTP_X_CORRELATION_ID="campus-a",
    )
    assert criado.status_code == 201, criado.content
    edital = Edital.objects.get(processo_id=criado.json()["id"])
    # Outra semente: Perfil e Evento têm identificador global, e o mesmo rascunho nas duas unidades
    # seria recusado por identificador já vinculado (a mesma razão de `test_documento_da_unidade`).
    return levar_a_publicacao(
        api_client,
        edital,
        draft=complete_draft(seed=1),
        escopo="campus-a",
        signatory={"authorityId": str(autoridade.pk)},
    )


def _universo(edital):
    return Universo(
        origem=nomes_do_aviso.RESULTADO,
        edital=edital,
        perfil_id=None,
        marco_id=None,
        linhas=[],
        cabecalho={"edital": f"Edital {edital.number}/{edital.year}"},
    )


def _convocacao(edital):
    return SimpleNamespace(edital=edital, vencimento=timezone.now() + timezone.timedelta(days=3))


# --- O resolvedor ---------------------------------------------------------------------------------


@pytest.mark.django_db
def test_a_identificacao_sai_do_registro_e_sem_unidade_e_so_o_ifes():
    """FR-3201: a sigla do registro ao lado do Ifes; escopo sem unidade não recai em nenhuma."""
    _campus()
    assert identificacao.da_unidade("cefor").rotulo == "Cefor/Ifes"
    assert identificacao.da_unidade("campus-a").rotulo == "Campus A/Ifes"
    for sem_unidade in ("nao-registrada", "", None, "institucional"):
        assert identificacao.da_unidade(sem_unidade).rotulo == "Ifes"
        assert identificacao.da_unidade(sem_unidade).nome_curto == "Ifes"


@pytest.mark.django_db
def test_a_implantacao_e_a_unidade_ativa_so_quando_ha_uma():
    """FR-3202: uma ativa, ela; duas, só o Ifes; a desativada não conta."""
    assert identificacao.da_implantacao().rotulo == "Cefor/Ifes"
    campus = _campus()
    assert identificacao.da_implantacao().rotulo == "Ifes"
    campus.ativa = False
    campus.save(update_fields=["ativa"])
    assert identificacao.da_implantacao().rotulo == "Cefor/Ifes"
    # A desativada continua sendo a unidade dos Editais dela.
    assert identificacao.da_unidade("campus-a").rotulo == "Campus A/Ifes"


@pytest.mark.django_db
def test_o_canal_e_o_da_unidade_depois_o_institucional_depois_o_padrao(settings):
    """FR-3212: a recaída na ordem, e o Cefor, sem canal no registro, no institucional."""
    _campus()
    settings.PORTAL_ATENDIMENTO = CANAL_INSTITUCIONAL
    assert identificacao.da_unidade("campus-a").canal() == CANAL_DO_CAMPUS
    assert identificacao.da_unidade("cefor").canal() == CANAL_INSTITUCIONAL
    settings.PORTAL_ATENDIMENTO = ""
    assert identificacao.da_unidade("cefor").canal("a comissão do certame") == (
        "a comissão do certame"
    )


def test_a_sigla_do_ifes_e_a_mesma_do_compositor():
    """D-007: as duas constantes ficam separadas, e dizem o mesmo."""
    assert identificacao.SIGLA_DA_INSTITUICAO == pdf.SIGLA_DA_INSTITUICAO
    assert identificacao.NOME_DA_INSTITUICAO in pdf.INSTITUICAO


# --- 1. Cada unidade aparece com a sua identificação ----------------------------------------------


@pytest.mark.django_db
def test_1_cada_unidade_aparece_na_gestao_com_a_sua_identificacao(client, settings):
    """Cenário 1; FR-3204, FR-3205: título, marca e a quem pedir acesso, da unidade do ator."""
    settings.INTERFACE_SELETOR_IDENTIDADE = True
    _campus()

    identificar(client, "gestora-a", ["gestor"], escopo="campus-a")
    corpo = client.get(reverse("interface:lista")).content.decode()
    assert _titulo(corpo) == "Processos Seletivos — Campus A/Ifes"
    assert "Gestão de Processos Seletivos<span>Campus A/Ifes</span>" in corpo
    assert "Cefor" not in corpo

    identificar(client, "sem-papel-a", [], escopo="campus-a")
    corpo = client.get(reverse("interface:lista")).content.decode()
    assert "Peça acesso a quem administra o sistema no Campus A." in corpo

    identificar(client, "gestora-c", ["gestor"])
    corpo = client.get(reverse("interface:lista")).content.decode()
    assert _titulo(corpo) == "Processos Seletivos — Cefor/Ifes"
    assert "Campus A" not in corpo


@pytest.mark.django_db
def test_1_a_recusa_de_envio_grande_diz_a_unidade_de_quem_enviou(client, settings):
    """Cenário 1; FR-3205: a frase do limite de envio, que é texto do servidor, e não template."""
    settings.INTERFACE_SELETOR_IDENTIDADE = True
    _campus()
    identificar(client, "gestora-a", ["gestor"], escopo="campus-a")
    settings.DATA_UPLOAD_MAX_NUMBER_FIELDS = 2
    resposta = client.post(reverse("interface:unidade-ativa"), {f"c{n}": "x" for n in range(5)})
    corpo = resposta.content.decode()
    assert resposta.status_code == 413
    assert "administra o sistema no Campus A, dizendo o Edital" in corpo
    assert "Cefor" not in corpo


# --- 2, 3, 5, 6. O Edital, o PDF, o portal e a troca de unidade -----------------------------------


@pytest.mark.django_db(transaction=True)
def test_2_3_5_6_o_edital_o_pdf_e_o_portal_dizem_a_unidade_do_ato(
    api_client, client, manager_headers, process_payload, settings
):
    """Cenários 2, 3, 5 e 6; FR-3206, FR-3207, FR-3216.

    O Edital do campus e o do Cefor, cada um na sua moldura; um operador do campus identificado no
    mesmo navegador não muda o que a página pública do Cefor diz; e renomear o campus no registro
    não reescreve nem o PDF nem a página do ato.
    """
    settings.INTERFACE_SELETOR_IDENTIDADE = True
    do_cefor = publish_original(api_client, manager_headers, process_payload)
    do_campus = _publicar_no_campus(api_client, process_payload)

    # 3: o PDF do campus diz o campus, e nada do Cefor.
    publicacao = Publicacao.objects.get(edital=do_campus, publication_order=1)
    texto = texto_de(bytes(publicacao.documento.bytes))
    assert publicacao.unidade_sigla == "Campus A"
    assert "Campus A" in texto.splitlines()[2]
    assert "Cefor" not in texto

    # 2 e 5: cada página pública com a sua unidade, com um operador do campus na mesma sessão.
    identificar(client, "gestora-a", ["gestor"], escopo="campus-a")
    pagina_do_cefor = client.get(reverse("portal:selecao", args=[do_cefor.id])).content.decode()
    pagina_do_campus = client.get(reverse("portal:selecao", args=[do_campus.id])).content.decode()
    assert _titulo(pagina_do_cefor).endswith("— Cefor/Ifes")
    assert 'Cefor<span>/Ifes</span> · <span class="nome-por-extenso">' in pagina_do_cefor
    assert _titulo(pagina_do_campus).endswith("— Campus A/Ifes")
    assert 'Campus A<span>/Ifes</span> · <span class="nome-por-extenso">' in pagina_do_campus

    # 5: a vitrine, com duas unidades ativas, não escolhe uma delas — nem a do operador.
    vitrine = client.get(reverse("portal:vitrine")).content.decode()
    assert _titulo(vitrine).endswith("— Ifes")
    assert '<a href="/selecoes/">Ifes · <span class="nome-por-extenso">' in vitrine

    # 6: o campus muda de sigla e de canal no registro; o ato não muda.
    documento_antes = bytes(publicacao.documento.bytes)
    Unidade.objects.filter(codigo="campus-a").update(sigla="Campus Alfa", atendimento="outro@x.br")
    publicacao.refresh_from_db()
    assert bytes(publicacao.documento.bytes) == documento_antes
    depois = client.get(reverse("portal:selecao", args=[do_campus.id])).content.decode()
    assert _titulo(depois).endswith("— Campus A/Ifes")
    assert "Campus Alfa" not in depois


# --- 4. As mensagens e o atendimento --------------------------------------------------------------


@pytest.mark.django_db
def test_4_o_aviso_assina_e_aponta_o_atendimento_da_unidade_do_edital(settings):
    """Cenário 4; FR-3209, FR-3212, FR-3216: e o texto congelado não muda com o registro."""
    settings.PORTAL_ATENDIMENTO = CANAL_INSTITUCIONAL
    _campus()
    do_campus = SimpleNamespace(institution_scope="campus-a", number="7", year=2026)
    do_cefor = SimpleNamespace(institution_scope="cefor", number="8", year=2026)

    _, corpo_do_campus = previa.congelar(
        _universo(do_campus), assunto="Assunto", corpo="Corpo", enderecos={}
    )
    _, corpo_do_cefor = previa.congelar(
        _universo(do_cefor), assunto="Assunto", corpo="Corpo", enderecos={}
    )
    assert f"fale com {CANAL_DO_CAMPUS}." in corpo_do_campus
    assert "Campus A/Ifes — Seleções" in corpo_do_campus
    assert "Cefor" not in corpo_do_campus
    assert f"fale com {CANAL_INSTITUCIONAL}." in corpo_do_cefor
    assert "Cefor/Ifes — Seleções" in corpo_do_cefor
    assert CANAL_DO_CAMPUS not in corpo_do_cefor

    # O editor mostra o mesmo rodapé que vai sair.
    visivel = _rodape_visivel(nomes_do_aviso.RESULTADO, "campus-a")
    assert "Campus A/Ifes — Seleções" in visivel and CANAL_DO_CAMPUS in visivel

    # Congelado: a mudança do registro depois não o alcança.
    congelado = corpo_do_campus
    Unidade.objects.filter(codigo="campus-a").update(sigla="Campus Alfa")
    assert congelado == corpo_do_campus
    _, de_agora = previa.congelar(
        _universo(do_campus), assunto="Assunto", corpo="Corpo", enderecos={}
    )
    assert "Campus Alfa/Ifes — Seleções" in de_agora


@pytest.mark.django_db
def test_4_a_convocacao_e_o_comprovante_assinam_pela_unidade(settings):
    """Cenário 4; FR-3209, FR-3212."""
    settings.PORTAL_ATENDIMENTO = CANAL_INSTITUCIONAL
    _campus()
    mail.outbox = []
    _enviar(
        _convocacao(SimpleNamespace(institution_scope="campus-a", number="7", year=2026)),
        destinatario="pessoa@ex.br",
        endereco_do_portal="http://x/",
    )
    _enviar(
        _convocacao(SimpleNamespace(institution_scope="cefor", number="8", year=2026)),
        destinatario="pessoa@ex.br",
        endereco_do_portal="http://x/",
    )
    do_campus, do_cefor = (mensagem.body for mensagem in mail.outbox)
    assert f"fale com {CANAL_DO_CAMPUS}." in do_campus and "Campus A/Ifes — Seleções" in do_campus
    assert "Cefor" not in do_campus
    assert f"fale com {CANAL_INSTITUCIONAL}." in do_cefor and "Cefor/Ifes — Seleções" in do_cefor

    mail.outbox = []
    enviar_comprovante(
        para="pessoa@ex.br", dados={**_DADOS_DO_COMPROVANTE, "assinatura": "Campus A/Ifes"}
    )
    assert "Campus A/Ifes — Seleções" in mail.outbox[0].body


@pytest.mark.django_db
def test_4_a_conta_do_candidato_fala_pela_implantacao_e_pelo_canal_institucional(settings):
    """Cenário 4; FR-3210, FR-3214: o código de acesso não é de unidade nenhuma."""
    settings.PORTAL_ATENDIMENTO = CANAL_INSTITUCIONAL
    _campus()
    mail.outbox = []
    enviar_codigo(para="pessoa@ex.br", codigo="123456")
    avisar_mudanca_de_credencial(
        para="pessoa@ex.br",
        endereco="outra@ex.br",
        acao="adicionado",
        atendimento=identificacao.canal_institucional(),
    )
    codigo, mudanca = mail.outbox
    assert codigo.subject == "Seu código de acesso — Seleções Ifes"
    assert "\nIfes — Seleções\n" in codigo.body
    assert mudanca.subject == "Mudança no acesso à sua conta — Seleções Ifes"
    assert f"fale com {CANAL_INSTITUCIONAL}" in mudanca.body
    for mensagem in (codigo, mudanca):
        assert "Campus A" not in mensagem.body and "Cefor" not in mensagem.body


# --- 7. Nada vaza entre unidades ------------------------------------------------------------------


@pytest.mark.django_db(transaction=True)
def test_7_a_404_e_a_moldura_nao_dizem_a_unidade_do_objeto_alheio(
    api_client, client, process_payload, settings
):
    """Cenário 7; FR-3208, FR-3219: o Edital do campus não abre ao Cefor, e a recusa não o diz."""
    settings.INTERFACE_SELETOR_IDENTIDADE = True
    do_campus = _publicar_no_campus(api_client, process_payload)
    identificar(client, "gestora-c", ["gestor"])
    settings.DEBUG = False
    resposta = client.get(reverse("interface:detalhe", args=[do_campus.id]))
    corpo = resposta.content.decode()
    assert resposta.status_code == 404
    assert "Campus A" not in corpo
    # Duas unidades ativas: a 404 é da implantação, e a implantação é o Ifes.
    assert _titulo(corpo) == "Página não encontrada — Ifes"
    lista = client.get(reverse("interface:lista")).content.decode()
    assert "Campus A" not in lista and CANAL_DO_CAMPUS not in lista


# --- 8. O Cefor como era --------------------------------------------------------------------------


@pytest.mark.django_db
def test_8_o_cefor_sozinho_diz_exatamente_o_que_dizia(client, settings):
    """Cenário 8; FR-3217, SC-1031: as frases da `main` em `ca1e53ed`, literais."""
    settings.INTERFACE_SELETOR_IDENTIDADE = True
    settings.PORTAL_ATENDIMENTO = CANAL_INSTITUCIONAL

    identificar(client, "gestora", ["gestor"])
    lista = client.get(reverse("interface:lista")).content.decode()
    assert _titulo(lista) == "Processos Seletivos — Cefor/Ifes"
    assert (
        '<span class="nome-do-produto">Gestão de Processos Seletivos<span>Cefor/Ifes</span></span>'
        in lista
    )
    identificar(client, "sem-papel", [])
    assert "Peça acesso a quem administra o sistema no Cefor.</p>" in (
        client.get(reverse("interface:lista")).content.decode()
    )
    with override_settings(DATA_UPLOAD_MAX_NUMBER_FIELDS=2):
        grande = client.post(reverse("interface:unidade-ativa"), {f"c{n}": "x" for n in range(5)})
    assert (
        "Peça a ampliação do limite de envio a quem administra o sistema no Cefor, dizendo o "
        "Edital e a tela: até lá, esta tela não consegue gravar."
    ) in grande.content.decode()
    client.logout()
    vitrine = client.get(reverse("portal:vitrine")).content.decode()
    assert _titulo(vitrine) == "Processos seletivos — Cefor/Ifes"
    assert (
        '<a href="/selecoes/">Cefor<span>/Ifes</span> · <span class="nome-por-extenso">' in vitrine
    )
    settings.DEBUG = False
    nao_encontrada = client.get("/nao-existe-109/").content.decode()
    assert _titulo(nao_encontrada) == "Página não encontrada — Cefor/Ifes"
    assert '<span class="marca">Cefor<span>/Ifes</span> · Processos Seletivos</span>' in (
        nao_encontrada
    )

    mail.outbox = []
    enviar_codigo(para="pessoa@ex.br", codigo="123456")
    enviar_comprovante(para="pessoa@ex.br", dados=_DADOS_DO_COMPROVANTE)
    codigo, comprovante = mail.outbox
    assert codigo.subject == "Seu código de acesso — Seleções Cefor/Ifes"
    assert codigo.body.endswith(
        "\nCefor/Ifes — Seleções\nEsta mensagem é automática; não responda.\n"
    )
    assert comprovante.body.endswith(
        "\nCefor/Ifes — Seleções\nEsta mensagem é automática; não responda.\n"
    )


_DADOS_DO_COMPROVANTE = {
    "protocolo": "P1",
    "verificacao": "V1",
    "selecao": "Seleção\nEdital 1/2026",
    "perfil": "Perfil",
    "modalidade": "AC",
    "quando": "01/10/2026",
    "documentos": [],
    "endereco": "http://x/",
}


# --- O registro -----------------------------------------------------------------------------------


def _declarado(**extra):
    cefor = {chave: valor for chave, valor in CEFOR.items() if chave != "codigo"}
    return {"cefor": cefor, **extra}


CAMPUS_DECLARADO = {
    "sigla": "Campus A",
    "nome": "Campus A",
    "cabecalho": ["Campus A"],
    "local": "Serra (ES)",
    "ativa": True,
}


@pytest.mark.django_db
def test_o_canal_entra_pelo_registro_com_trilha_e_o_cefor_nao_muda():
    """FR-3211, FR-3217, FR-3218: o canal pelo arquivo e pelo comando de sempre."""
    criadas, alteradas, mantidas = sincronizar(
        _declarado(**{"campus-a": {**CAMPUS_DECLARADO, "atendimento": f" {CANAL_DO_CAMPUS} "}})
    )
    assert (criadas, alteradas, mantidas) == (1, 0, 1)
    campus = Unidade.objects.get(codigo="campus-a")
    assert campus.atendimento == CANAL_DO_CAMPUS
    evento = RegistroAuditoria.objects.get(operation="REGISTRAR_UNIDADE", aggregate_id=campus.pk)
    assert evento.detalhe["depois"]["atendimento"] == CANAL_DO_CAMPUS
    assert Unidade.objects.get(codigo="cefor").atendimento == ""


@pytest.mark.django_db
@pytest.mark.parametrize("canal", ["", "   ", "linha\noutra", 42, "x" * 256], ids=repr)
def test_canal_declarado_malformado_e_recusado_antes_de_gravar(canal):
    """FR-3211: para não ter canal, omite-se; o que entra cabe numa linha."""
    with pytest.raises(DomainError) as recusa:
        sincronizar(_declarado(**{"campus-a": {**CAMPUS_DECLARADO, "atendimento": canal}}))
    assert recusa.value.code == "unidade_malformada"
    assert not Unidade.objects.filter(codigo="campus-a").exists()


# --- O guardião -----------------------------------------------------------------------------------

RAIZ = Path(__file__).resolve().parents[2] / "processo_seletivo"

# As superfícies que o inventário classificou como identidade da unidade (U). Os explicativos,
# históricos e de demonstração ficam de fora de propósito (D-008), e por isso a lista é literal:
# uma tela nova que escrever "Cefor" não é pega aqui, e é o inventário que a revisão confere.
TEMPLATES_DA_UNIDADE = (
    "interface/templates/interface/base.html",
    "interface/templates/interface/base_de_acesso.html",
    "interface/templates/interface/lista.html",
    "interface/templates/interface/minhas_etapas.html",
    "interface/templates/interface/recusa.html",
    "portal/templates/portal/base.html",
    "shared/templates/404.html",
    "shared/templates/_marca_da_unidade.html",
)
MODULOS_DA_UNIDADE = (
    "avisos/domain/mensagem.py",
    "convocacao/application/comunicar.py",
    "inscricoes/application/mensagem.py",
    "identidade/application/mensagem.py",
    "interface/erros.py",
)
_COMENTARIO = re.compile(r"{% comment %}.*?{% endcomment %}|{#.*?#}", re.S)


def _textos_que_saem(caminho):
    """As constantes de texto do módulo que não são docstring: o que pode chegar a quem lê."""
    arvore = ast.parse(caminho.read_text(encoding="utf-8"))
    docstrings = {
        id(no.body[0].value)
        for no in ast.walk(arvore)
        if isinstance(no, ast.Module | ast.FunctionDef | ast.ClassDef)
        and no.body
        and isinstance(no.body[0], ast.Expr)
        and isinstance(no.body[0].value, ast.Constant)
    }
    return [
        no.value
        for no in ast.walk(arvore)
        if isinstance(no, ast.Constant) and isinstance(no.value, str) and id(no) not in docstrings
    ]


@pytest.mark.parametrize("relativo", TEMPLATES_DA_UNIDADE)
def test_nenhum_template_da_moldura_escreve_a_sigla_de_uma_unidade(relativo):
    """SC-1035: a sigla vem do registro; o "Ifes" do template é a instituição, não uma unidade."""
    visivel = _COMENTARIO.sub("", (RAIZ / relativo).read_text(encoding="utf-8"))
    assert "Cefor" not in visivel


@pytest.mark.parametrize("relativo", MODULOS_DA_UNIDADE)
def test_nenhuma_mensagem_escreve_a_sigla_de_uma_unidade(relativo):
    """SC-1035: assinatura e canal chegam resolvidos; nenhum texto que sai diz "Cefor"."""
    assert not [texto for texto in _textos_que_saem(RAIZ / relativo) if "Cefor" in texto]
