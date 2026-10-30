"""A jornada operacional da Retificação, pela navegação comum (103).

**Por que existe.** A auditoria de 29/10 mostrou que o servidor aceitava a passagem entre pessoas e
que a navegação não a oferecia: a Retificação não publicada não tinha porta, e a devolvida não se
reabria pela tela. Estes casos percorrem a jornada inteira com **sessões `Client` independentes** —
outro navegador, outro cookie —, cada uma com o seu papel, e cada sessão só chega à Retificação pelo
que a navegação mostra a partir da barra (`navegacao.SECOES`). O endereço do detalhe nunca é
digitado: ele é lido da página que a pessoa teria aberto.

As jornadas seguem as letras do pedido da feature: A, o fluxo completo; B, devolução e correção do
mesmo registro; C, a sessão interrompida e retomada; D, a segregação; E, outra unidade; F, a
concorrência; G, a publicação e a consistência; H, a navegação sem URL conhecida.
"""

import threading

import pytest
from django.db import connection
from django.test.utils import CaptureQueriesContext
from django.urls import reverse

from processo_seletivo.auditoria.models import RegistroAuditoria
from processo_seletivo.interface import atos_retificacao
from processo_seletivo.interface import views as interface_views
from processo_seletivo.publicacoes.application.retificacoes import edit_retification
from processo_seletivo.publicacoes.application.selectors import effective_version
from processo_seletivo.publicacoes.domain.changes import resolve_path
from processo_seletivo.publicacoes.models_retificacao import Retificacao, VersaoConsolidada
from processo_seletivo.seguranca.domain import Actor
from processo_seletivo.shared.api.problems import DomainError
from tests.fixtures.publicacao import publish_original
from tests.interface.test_auditoria_passagem_da_retificacao import (
    LINHA_GERAL,
    SIGNATARIO,
    VAGAS,
    _links,
    alcancada,
    compor,
    navegar,
    sessao,
)


@pytest.fixture
def edital(api_client, manager_headers, process_payload):
    return publish_original(api_client, manager_headers, process_payload)


@pytest.fixture
def vigente(edital):
    return VersaoConsolidada.objects.filter(edital=edital).latest("materialized_at")


pytestmark = [
    pytest.mark.django_db(transaction=True),
    pytest.mark.integration,
    pytest.mark.usefixtures("seletor_ligado"),
]

ANA = ("ana.elaboradora", ["elaborador"])
ELISA = ("elisa.elaboradora", ["elaborador"])
BRUNO = ("bruno.homologador", ["homologador"])
CARLA = ("carla.publicadora", ["publicador"])
GABI = ("gabi.gestora", ["gestor"])
TODOS = ["elaborador", "homologador", "publicador"]


# ---------------------------------------------------------------------------------------------
# Auxiliares: o que a pessoa faz na tela, sem digitar endereço
# ---------------------------------------------------------------------------------------------


def encontrar(cliente, edital, rota, *args):
    """O endereço, lido de uma página que a navegação alcança — ou o teste falha.

    É o que separa este arquivo do teste da auditoria por URL direta: a pessoa só chega aonde um
    link a leva. Devolve o endereço e as páginas onde ele apareceu.
    """
    destino = reverse(rota, args=args)
    paginas = navegar(cliente, edital)
    onde = [caminho for caminho, html in paginas.items() if destino in _links(html)]
    assert onde, f"{destino} não é alcançável pela navegação"
    return destino, onde


def detalhe(cliente, retificacao):
    url, _ = encontrar(cliente, retificacao.edital, "interface:retificacao-detalhe", retificacao.id)
    resposta = cliente.get(url)
    assert resposta.status_code == 200
    return resposta.content.decode()


def campos_da_edicao(resposta, **trocas):
    """Todos os campos do formulário de edição como a tela os mostrou, com as trocas por caminho."""
    grupos = resposta.context["grupos"]
    campos = [campo for grupo in grupos for campo in grupo["campos"]]
    referencia = {campo["caminho"]: campo["referencia"] for campo in campos}
    enviados = {f"campo:{campo['referencia']}": campo["valor"] for campo in campos}
    enviados.update({f"campo:{referencia[caminho]}": valor for caminho, valor in trocas.items()})
    edicao = resposta.context["edicao"]
    enviados |= {
        "base": str(resposta.context["base"].id),
        "revisao": str(edicao["revisao"]),
        "justificativa": resposta.context["justificativa"],
        "vigencia": resposta.context["vigencia"],
    }
    return enviados


def abrir_edicao(cliente, retificacao):
    """Do detalhe — alcançado pela navegação — ao formulário, pelo link "Editar a Retificação"."""
    corpo = detalhe(cliente, retificacao)
    url = reverse("interface:retificacao-editar", args=[retificacao.id])
    assert url in _links(corpo), "o detalhe não oferece a edição"
    resposta = cliente.get(url)
    assert resposta.status_code == 200
    return url, resposta


def editar(cliente, retificacao, vagas, **extras):
    url, tela = abrir_edicao(cliente, retificacao)
    dados = campos_da_edicao(tela, **{VAGAS: vagas, LINHA_GERAL: vagas})
    conferencia = cliente.post(url, dados | extras)
    assert conferencia.status_code == 200
    assert "O que muda em relação ao rascunho" in conferencia.content.decode()
    resposta = cliente.post(url, dados | extras | {"confirmar": "1"})
    assert resposta.status_code == 302, (resposta.context or {}).get("erros")
    return resposta


def vagas_propostas(retificacao):
    from processo_seletivo.publicacoes.application.retificacoes import (
        alteracoes_declaradas,
        conteudo_base,
    )
    from processo_seletivo.publicacoes.domain.fusao import aplicar

    retificacao.refresh_from_db()
    conteudo = aplicar(conteudo_base(retificacao.base_snapshot), alteracoes_declaradas(retificacao))
    return resolve_path(conteudo, VAGAS)


def praticar(cliente, retificacao, acao, **campos):
    """O ato pelo botão que o detalhe oferece — nunca pela URL montada."""
    corpo = detalhe(cliente, retificacao)
    url = reverse("interface:retificacao-ato", args=[retificacao.id, acao])
    assert f'href="{url}"' in corpo, f"o detalhe não oferece {acao}"
    confirmacao = cliente.get(url)
    resposta = cliente.post(
        url, {"chave_idempotencia": confirmacao.context["chave_idempotencia"], **campos}
    )
    assert resposta.status_code == 302, (resposta.context or {}).get("erro")
    retificacao.refresh_from_db()
    return confirmacao.content.decode()


def criar_pela_navegacao(cliente, edital, vigente, vagas="9"):
    url, _ = encontrar(cliente, edital, "interface:retificar", edital.id)
    assert url == reverse("interface:retificar", args=[edital.id])
    return compor(cliente, edital, vigente, vagas=vagas)


def operacoes(retificacao):
    return list(
        RegistroAuditoria.objects.filter(aggregate_id=retificacao.id)
        .order_by("occurred_at")
        .values_list("operation", "actor_subject")
    )


# ---------------------------------------------------------------------------------------------
# A — o fluxo completo, por quatro sessões, sem URL digitada
# ---------------------------------------------------------------------------------------------


def test_a_criar_retomar_editar_submeter_homologar_e_publicar(edital, vigente):
    ana = sessao(*ANA)
    retificacao = criar_pela_navegacao(ana, edital, vigente, vagas="9")

    # Ana sai e volta noutra sessão: a Lista diz o que a Retificação espera, e de quem.
    ana = sessao(*ANA)
    lista = ana.get(reverse("interface:lista")).content.decode()
    # Desde a 104 o ato vai para a faixa e para a coluna, e a marca diz só a situação.
    assert "Retificação em elaboração</a>" in lista
    assert "Concluir e submeter a Retificação" in lista
    editar(ana, retificacao, "7")
    assert vagas_propostas(retificacao) == 7

    confirmacao = praticar(ana, retificacao, "submeter")
    assert "a Retificação fica aguardando <strong>quem homologa</strong>" in confirmacao
    corpo = detalhe(ana, retificacao)
    assert "Aguardando quem homologa" in corpo

    bruno = sessao(*BRUNO)
    lista = bruno.get(reverse("interface:lista")).content.decode()
    assert "Retificação em revisão</a>" in lista
    assert "Analisar a Retificação" in lista
    assert "O próximo ato é seu" in detalhe(bruno, retificacao)
    praticar(bruno, retificacao, "homologar", motivo="Conferido")

    carla = sessao(*CARLA)
    assert "Publicar a Retificação" in carla.get(reverse("interface:lista")).content.decode()
    praticar(carla, retificacao, "publicar", **SIGNATARIO)

    assert retificacao.status == Retificacao.Status.PUBLICADA
    assert Retificacao.objects.filter(edital=edital).count() == 1
    assert [operacao for operacao, _ in operacoes(retificacao)] == [
        "CRIAR",
        "ALTERAR_RASCUNHO",
        "SUBMETER",
        "HOMOLOGAR",
        "PUBLICAR",
    ]


# ---------------------------------------------------------------------------------------------
# B — devolução das duas origens, correção e reenvio do mesmo registro
# ---------------------------------------------------------------------------------------------


def test_b_duas_devolucoes_e_o_mesmo_registro_chega_a_publicacao(edital, vigente):
    ana, bruno, carla = sessao(*ANA), sessao(*BRUNO), sessao(*CARLA)
    retificacao = criar_pela_navegacao(ana, edital, vigente, vagas="9")
    identidade = retificacao.id
    praticar(ana, retificacao, "submeter")

    # Primeira devolução: de EM_REVISAO.
    praticar(bruno, retificacao, "devolver", motivo="Faltou a linha da ampla concorrência")
    assert retificacao.status == Retificacao.Status.EM_ELABORACAO
    corpo = detalhe(ana, retificacao)
    assert "Devolvida para correção." in corpo
    assert "Faltou a linha da ampla concorrência" in corpo
    editar(ana, retificacao, "8")
    praticar(ana, retificacao, "submeter")
    praticar(bruno, retificacao, "homologar", motivo="Conferido")

    # Segunda devolução: de HOMOLOGADA.
    praticar(bruno, retificacao, "devolver", motivo="O número ainda não fecha")
    assert retificacao.status == Retificacao.Status.EM_ELABORACAO
    assert retificacao.homologated_by == ""
    assert "O número ainda não fecha" in detalhe(ana, retificacao)
    editar(ana, retificacao, "6")
    praticar(ana, retificacao, "submeter")
    praticar(bruno, retificacao, "homologar", motivo="Conferido")
    praticar(carla, retificacao, "publicar", **SIGNATARIO)

    assert retificacao.id == identidade
    assert retificacao.status == Retificacao.Status.PUBLICADA
    assert Retificacao.objects.filter(edital=edital).count() == 1
    assert resolve_path(effective_version(edital_id=edital.id).content, VAGAS) == 6
    contagem = [operacao for operacao, _ in operacoes(retificacao)]
    assert contagem.count("DEVOLVER") == 2
    assert contagem.count("ALTERAR_RASCUNHO") == 2
    assert contagem.count("SUBMETER") == 3


# ---------------------------------------------------------------------------------------------
# C — a sessão interrompida, retomada por outra pessoa do escopo
# ---------------------------------------------------------------------------------------------


def test_c_outra_elaboradora_retoma_o_rascunho_e_o_submete(edital, vigente):
    retificacao = criar_pela_navegacao(sessao(*ANA), edital, vigente, vagas="9")

    elisa = sessao(*ELISA)
    editar(elisa, retificacao, "5")
    praticar(elisa, retificacao, "submeter")

    retificacao.refresh_from_db()
    assert retificacao.created_by == "ana.elaboradora"
    assert retificacao.prepared_by == "elisa.elaboradora"
    assert vagas_propostas(retificacao) == 5
    assert ("ALTERAR_RASCUNHO", "elisa.elaboradora") in operacoes(retificacao)


def test_c_quem_elabora_ve_o_rascunho_ao_abrir_retificar_e_continua(edital, vigente):
    ana = sessao(*ANA)
    retificacao = criar_pela_navegacao(ana, edital, vigente)

    tela = sessao(*ANA).get(reverse("interface:retificar", args=[edital.id])).content.decode()

    assert "Este Edital já tem 1 Retificação em curso" in tela
    assert reverse("interface:retificacao-editar", args=[retificacao.id]) in tela
    assert "Continuar a elaboração" in tela


# ---------------------------------------------------------------------------------------------
# D — segregação de funções e vários papéis
# ---------------------------------------------------------------------------------------------


def test_d_quem_acumula_os_papeis_e_avisado_e_nao_recebe_o_botao_da_recusa(edital, vigente):
    dora = sessao("dora.acumula", TODOS)
    retificacao = compor(dora, edital, vigente)
    corpo = detalhe(dora, retificacao)
    assert "Editar a Retificação" in corpo
    assert "Submeter para revisão</a>" in corpo
    praticar(dora, retificacao, "submeter")

    confirmacao = praticar(dora, retificacao, "homologar", motivo="Conferido")
    assert "Se a\n  homologar, a publicação precisará ser feita por outra pessoa" in confirmacao

    corpo = detalhe(dora, retificacao)
    assert ">Publicar Retificação</a>" not in corpo
    assert 'aria-disabled="true"' in corpo
    assert atos_retificacao.SEGREGACAO in corpo
    url = reverse("interface:retificacao-ato", args=[retificacao.id, "publicar"])
    confirmacao = dora.get(url).content.decode()
    assert "Segregação de funções." in confirmacao
    assert "Confirmar: Publicar Retificação" not in confirmacao
    assert dora.post(url, {"chave_idempotencia": "ui-dora", **SIGNATARIO}).status_code == 403

    # Outra pessoa autorizada publica, pela mesma navegação.
    praticar(sessao(*CARLA), retificacao, "publicar", **SIGNATARIO)
    assert retificacao.status == Retificacao.Status.PUBLICADA


def test_d_as_recusas_dizem_qual_foi_a_causa(edital, vigente):
    retificacao = compor(sessao(*ANA), edital, vigente)

    sem_permissao = sessao(*BRUNO).get(
        reverse("interface:retificacao-ato", args=[retificacao.id, "submeter"])
    )
    fora_da_situacao = sessao(*CARLA).get(
        reverse("interface:retificacao-ato", args=[retificacao.id, "publicar"])
    )

    assert "Você não pode praticar este ato." in sem_permissao.content.decode()
    assert "Este ato não cabe na situação atual." in fora_da_situacao.content.decode()


# ---------------------------------------------------------------------------------------------
# E — outra unidade
# ---------------------------------------------------------------------------------------------


def test_e_outra_unidade_nao_ve_nem_edita(edital, vigente):
    retificacao = compor(sessao(*ANA), edital, vigente)
    alheia = sessao("zeca.elaborador", TODOS, escopo="outra-unidade")

    lista = alheia.get(reverse("interface:lista")).content.decode()
    edicao = alheia.get(reverse("interface:retificacao-editar", args=[retificacao.id]))
    envio = alheia.post(
        reverse("interface:retificacao-editar", args=[retificacao.id]), {"revisao": "1"}
    )

    assert str(retificacao.id) not in lista
    assert alheia.get(reverse("interface:detalhe", args=[edital.id])).status_code == 404
    assert (edicao.status_code, envio.status_code) == (404, 404)
    assert not alcancada(navegar(alheia, edital), retificacao)
    revisao = retificacao.revision
    retificacao.refresh_from_db()
    assert retificacao.revision == revisao


# ---------------------------------------------------------------------------------------------
# F — concorrência
# ---------------------------------------------------------------------------------------------


def test_f_duas_sessoes_editando_a_segunda_e_recusada_sem_gravar(edital, vigente):
    retificacao = compor(sessao(*ANA), edital, vigente, vagas="9")
    ana, elisa = sessao(*ANA), sessao(*ELISA)
    url, tela_ana = abrir_edicao(ana, retificacao)
    _, tela_elisa = abrir_edicao(elisa, retificacao)
    dados_ana = campos_da_edicao(tela_ana, **{VAGAS: "7", LINHA_GERAL: "7"})
    dados_elisa = campos_da_edicao(tela_elisa, **{VAGAS: "5", LINHA_GERAL: "5"})

    primeira = ana.post(url, dados_ana | {"confirmar": "1"})
    segunda = elisa.post(url, dados_elisa | {"confirmar": "1"})

    assert primeira.status_code == 302
    assert segunda.status_code == 412
    assert "foi alterada depois que você abriu a tela" in segunda.content.decode()
    assert vagas_propostas(retificacao) == 7
    assert operacoes(retificacao).count(("ALTERAR_RASCUNHO", "elisa.elaboradora")) == 0


def test_f_a_corrida_entre_conferir_e_gravar_e_recusada_pela_revisao(edital, vigente, monkeypatch):
    """A gravação concorrente cai entre a leitura da revisão e o comando: quem recusa é o CAS."""
    retificacao = compor(sessao(*ANA), edital, vigente, vagas="9")
    ana = sessao(*ANA)
    url, tela = abrir_edicao(ana, retificacao)
    dados = campos_da_edicao(tela, **{VAGAS: "7", LINHA_GERAL: "7"})
    fundir_original = interface_views.fundir

    def fundir_com_concorrente(*args, **kwargs):
        resultado = fundir_original(*args, **kwargs)

        # Outra sessão grava neste intervalo, por outra conexão.
        def concorrente():
            try:
                edit_retification(
                    actor=Actor("elisa.elaboradora", "cefor", frozenset({"retificacao:elaborar"})),
                    retificacao_id=retificacao.id,
                    expected_revision=retificacao.revision,
                    data={"justification": "Ampliação de vagas", "changes": resultado[0]},
                )
            finally:
                connection.close()

        linha = threading.Thread(target=concorrente)
        linha.start()
        linha.join()
        return resultado

    monkeypatch.setattr(interface_views, "fundir", fundir_com_concorrente)

    resposta = ana.post(url, dados | {"confirmar": "1"})

    # A corrida cai **dentro** da gravação, e a recusa volta no próprio formulário, como toda recusa
    # do comando nesta tela; a que chega antes de ler o formulário é a página 412.
    assert resposta.status_code == 200
    assert "foi alterada depois que você abriu a tela" in resposta.content.decode()
    assert [
        quem for operacao, quem in operacoes(retificacao) if operacao == "ALTERAR_RASCUNHO"
    ] == ["elisa.elaboradora"]


def test_f_ato_concorrente_sobre_a_edicao_aberta_recusa_a_gravacao(edital, vigente):
    """Abriu a edição, e outra pessoa submeteu: a gravação é recusada pela situação."""
    retificacao = compor(sessao(*ANA), edital, vigente)
    ana = sessao(*ANA)
    url, tela = abrir_edicao(ana, retificacao)
    praticar(sessao(*ELISA), retificacao, "submeter")

    resposta = ana.post(url, campos_da_edicao(tela, **{VAGAS: "4"}) | {"confirmar": "1"})

    assert resposta.status_code == 409
    assert "só a Retificação em elaboração se edita" in resposta.content.decode()


# ---------------------------------------------------------------------------------------------
# G — publicação e consistência
# ---------------------------------------------------------------------------------------------


def test_g_publicada_sai_das_pendencias_e_documentos_e_consolidacao_ficam_integros(edital, vigente):
    ana, bruno, carla = sessao(*ANA), sessao(*BRUNO), sessao(*CARLA)
    retificacao = criar_pela_navegacao(ana, edital, vigente, vagas="9")
    editar(ana, retificacao, "11")
    praticar(ana, retificacao, "submeter")
    praticar(bruno, retificacao, "homologar", motivo="Conferido")
    praticar(carla, retificacao, "publicar", **SIGNATARIO)

    lista = bruno.get(reverse("interface:lista")).content.decode()
    pagina_do_edital = bruno.get(reverse("interface:detalhe", args=[edital.id])).content.decode()

    assert "marca-da-retificacao" not in lista
    assert "Nenhuma Retificação em curso." in pagina_do_edital
    assert "Retificação nº 2" in pagina_do_edital
    assert reverse("interface:retificacao-detalhe", args=[retificacao.id]) in pagina_do_edital
    documento = retificacao.publication
    assert bruno.get(reverse("public-document", args=[documento.id])).status_code == 200
    vigente_agora = effective_version(edital_id=edital.id)
    assert resolve_path(vigente_agora.content, VAGAS) == 11
    assert vigente.id != vigente_agora.id
    assert resolve_path(vigente.content, VAGAS) != 11, "a versão anterior continua como estava"

    corpo = detalhe(bruno, retificacao)
    assert "Esta Retificação está encerrada (publicada)" in corpo
    assert "Editar a Retificação" not in corpo
    assert (
        ana.get(reverse("interface:retificacao-editar", args=[retificacao.id])).status_code == 409
    )


def test_g_cancelar_so_ao_gestor_e_so_em_elaboracao(edital, vigente):
    retificacao = compor(sessao(*ANA), edital, vigente)
    url = reverse("interface:retificacao-ato", args=[retificacao.id, "cancelar"])

    assert f'href="{url}"' not in detalhe(sessao(*ANA), retificacao)
    praticar(sessao(*GABI), retificacao, "cancelar", motivo="Assunto tratado noutra Retificação")

    assert retificacao.status == Retificacao.Status.CANCELADA
    assert not atos_retificacao.em_curso(edital, Actor("x", "cefor"))
    assert (
        "Esta Retificação está encerrada (cancelada)"
        in sessao(*GABI)
        .get(reverse("interface:retificacao-detalhe", args=[retificacao.id]))
        .content.decode()
    )


def test_g_submetida_nao_oferece_cancelar_nem_editar(edital, vigente):
    retificacao = compor(sessao(*ANA), edital, vigente)
    praticar(sessao(*ANA), retificacao, "submeter")

    corpo = detalhe(sessao("gabi.e.ana", ["gestor", "elaborador"]), retificacao)

    assert "Cancelar Retificação" not in corpo
    assert "Editar a Retificação" not in corpo


# ---------------------------------------------------------------------------------------------
# H — navegação sem URL conhecida, para cada papel em cada situação
# ---------------------------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("situacao", "pessoa", "rota"),
    [
        ("EM_ELABORACAO", ANA, "interface:retificacao-detalhe"),
        ("EM_ELABORACAO", ELISA, "interface:retificacao-editar"),
        ("EM_ELABORACAO", GABI, "interface:retificacao-detalhe"),
        ("EM_REVISAO", BRUNO, "interface:retificacao-detalhe"),
        ("HOMOLOGADA", CARLA, "interface:retificacao-detalhe"),
    ],
)
def test_h_cada_papel_alcanca_a_retificacao_pela_barra(edital, vigente, situacao, pessoa, rota):
    retificacao = compor(sessao(*ANA), edital, vigente)
    if situacao != "EM_ELABORACAO":
        praticar(sessao(*ANA), retificacao, "submeter")
    if situacao == "HOMOLOGADA":
        praticar(sessao(*BRUNO), retificacao, "homologar", motivo="Conferido")

    cliente = sessao(*pessoa)
    destino = reverse(rota, args=[retificacao.id])
    paginas = navegar(cliente, edital)
    if rota == "interface:retificacao-editar":
        # A edição está a um clique do detalhe, que está a um clique da Lista.
        detalhe_url = reverse("interface:retificacao-detalhe", args=[retificacao.id])
        assert reverse("interface:lista") in alcancada(paginas, retificacao)
        assert destino in _links(cliente.get(detalhe_url).content.decode())
    else:
        assert reverse("interface:lista") in [
            caminho for caminho, html in paginas.items() if destino in _links(html)
        ]


def test_h_sem_retificacao_o_edital_publicado_diz_que_nao_ha(edital, vigente):
    corpo = sessao(*BRUNO).get(reverse("interface:detalhe", args=[edital.id])).content.decode()

    assert "Retificações em curso" in corpo
    assert "Nenhuma Retificação em curso." in corpo


# ---------------------------------------------------------------------------------------------
# Exceções da edição
# ---------------------------------------------------------------------------------------------


def test_editar_sem_permissao_e_403_com_a_permissao_nomeada(edital, vigente):
    retificacao = compor(sessao(*ANA), edital, vigente)

    resposta = sessao(*BRUNO).get(reverse("interface:retificacao-editar", args=[retificacao.id]))

    assert resposta.status_code == 403
    assert "retificacao:elaborar" in resposta.content.decode()


def test_desfazer_tudo_e_recusado_sem_gravar(edital, vigente):
    retificacao = compor(sessao(*ANA), edital, vigente, vagas="9")
    ana = sessao(*ANA)
    url, tela = abrir_edicao(ana, retificacao)
    original = resolve_path(vigente.content, VAGAS)
    dados = campos_da_edicao(tela, **{VAGAS: str(original), LINHA_GERAL: str(original)})
    revisao = retificacao.revision

    resposta = ana.post(url, dados | {"confirmar": "1"})

    assert resposta.status_code == 200
    assert "não mudaria conteúdo nenhum do Edital" in resposta.content.decode()
    retificacao.refresh_from_db()
    assert retificacao.revision == revisao


def test_so_a_justificativa_muda_e_grava(edital, vigente):
    retificacao = compor(sessao(*ANA), edital, vigente, vagas="9")
    ana = sessao(*ANA)
    url, tela = abrir_edicao(ana, retificacao)

    resposta = ana.post(
        url, campos_da_edicao(tela) | {"justificativa": "Outra razão", "confirmar": "1"}
    )

    assert resposta.status_code == 302
    retificacao.refresh_from_db()
    assert retificacao.justification == "Outra razão"
    assert vagas_propostas(retificacao) == 9


def test_a_edicao_parte_do_que_o_rascunho_ja_declara(edital, vigente):
    retificacao = compor(sessao(*ANA), edital, vigente, vagas="9")

    _, tela = abrir_edicao(sessao(*ANA), retificacao)

    valores = {
        campo["caminho"]: campo["valor"]
        for grupo in tela.context["grupos"]
        for campo in grupo["campos"]
    }
    assert str(valores[VAGAS]) == "9"
    assert tela.context["justificativa"] == "Ampliação de vagas"
    assert "Aplicar a todos" not in tela.content.decode()


# ---------------------------------------------------------------------------------------------
# O custo das telas que listam (FR-2705, FR-2707, SC-974)
# ---------------------------------------------------------------------------------------------


def _consultas(cliente, url):
    with CaptureQueriesContext(connection) as capturadas:
        assert cliente.get(url).status_code == 200
    return len(capturadas)


def test_a_lista_e_o_edital_nao_crescem_com_as_retificacoes(edital, vigente):
    ana = sessao(*ANA)
    bruno = sessao(*BRUNO)
    compor(ana, edital, vigente, vagas="9")
    lista, pagina = reverse("interface:lista"), reverse("interface:detalhe", args=[edital.id])
    com_uma = (_consultas(bruno, lista), _consultas(bruno, pagina))
    for vagas in ("8", "7", "6", "5"):
        compor(ana, edital, vigente, vagas=vagas)

    com_cinco = (_consultas(bruno, lista), _consultas(bruno, pagina))

    assert com_cinco == com_uma
    assert bruno.get(lista).content.decode().count("marca-da-retificacao") == 5


def test_a_api_que_edita_o_rascunho_tambem_entra_na_trilha(edital, vigente, api_client):
    retificacao = compor(sessao(*ANA), edital, vigente, vagas="9")

    resposta = api_client.put(
        f"/api/v1/admin/retificacoes/{retificacao.id}/rascunho",
        {
            "justification": "Pela API",
            "changes": [
                {"targetPath": VAGAS, "operation": "REPLACE", "newValue": 3},
                {"targetPath": LINHA_GERAL, "operation": "REPLACE", "newValue": 3},
            ],
        },
        format="json",
        HTTP_AUTHORIZATION="Bearer api.elaboradora|cefor|retificacao:elaborar",
        HTTP_IF_MATCH=f'"{retificacao.revision}"',
        HTTP_X_CORRELATION_ID="corr-103",
    )

    assert resposta.status_code == 200, resposta.content
    registro = RegistroAuditoria.objects.get(
        aggregate_id=retificacao.id, operation="ALTERAR_RASCUNHO"
    )
    assert (registro.actor_subject, registro.permission) == (
        "api.elaboradora",
        "retificacao:elaborar",
    )
    assert (registro.previous_revision, registro.new_revision) == (
        retificacao.revision,
        retificacao.revision + 1,
    )
    assert registro.correlation_id == "corr-103"
    with pytest.raises(DomainError):
        edit_retification(
            actor=Actor("x", "cefor", frozenset({"retificacao:elaborar"})),
            retificacao_id=retificacao.id,
            expected_revision=retificacao.revision,
            data={"justification": "x", "changes": []},
        )
