"""As ações disponíveis na primeira tela, e a Lista que não se contradiz (104).

**Por que existe.** O diagnóstico de 30/10/2026 mostrou o homologador lendo "Nenhuma ação
disponível" ao lado da Retificação que esperava por ele, e a Lista oferecendo "Submeter" de um
Edital que o detalhe sabia impedido. Estes casos percorrem os cenários do pedido da 104 com sessões
`Client` independentes, e conferem que a faixa, a coluna e o detalhe dizem a mesma coisa:

- A, homologação: aparece para todo homologador, e some para todos depois do ato;
- B, publicação; C, devolução até a publicação; D, Edital com impedimento;
- E, vários papéis; F, sem ação; G, vários procedimentos; I, regressão das outras áreas.

O cenário H (teclado, 375 px) é conferido no navegador e registrado em `verificacao.md`; aqui se
prende o que é estrutura — a faixa vem antes do inventário e não é tabela.
"""

import pytest
from django.urls import reverse

from processo_seletivo.interface import trabalho
from processo_seletivo.processos.models import Edital
from processo_seletivo.publicacoes.models_retificacao import Retificacao, VersaoConsolidada
from tests.fixtures.edital import actor_headers, complete_draft
from tests.fixtures.publicacao import publish_original
from tests.interface.test_auditoria_passagem_da_retificacao import SIGNATARIO, compor, sessao
from tests.interface.test_jornada_da_retificacao import editar, praticar

pytestmark = [
    pytest.mark.django_db(transaction=True),
    pytest.mark.integration,
    pytest.mark.usefixtures("seletor_ligado"),
]

ANA = ("ana.elaboradora", ["elaborador"])
BRUNO = ("bruno.homologador", ["homologador"])
BEATRIZ = ("beatriz.homologadora", ["homologador"])
CARLA = ("carla.publicadora", ["publicador"])
GABI = ("gabi.gestora", ["gestor"])
TODOS = ["elaborador", "homologador", "publicador", "gestor"]
NADA = "Nenhum ato de Edital ou de Retificação, recurso ou avaliação aguarda você agora."


@pytest.fixture
def edital(api_client, manager_headers, process_payload):
    return publish_original(api_client, manager_headers, process_payload)


@pytest.fixture
def vigente(edital):
    return VersaoConsolidada.objects.filter(edital=edital).latest("materialized_at")


def lista(cliente):
    resposta = cliente.get(reverse("interface:lista"))
    assert resposta.status_code == 200
    return resposta


def faixa(cliente):
    return lista(cliente).context["faixa"]


def atos_da_faixa(cliente):
    return [(objeto.titulo, objeto.ato) for objeto in faixa(cliente).objetos]


def homologado_por(api_client, manager_headers, process_payload, quem_submete, quem_homologa):
    """Um Edital homologado, sem publicar, com quem submeteu e quem homologou à escolha."""
    criado = api_client.post(
        "/api/v1/admin/processos", process_payload, format="json", **manager_headers
    )
    edital = Edital.objects.get(processo_id=criado.json()["id"])
    elabora = actor_headers(quem_submete, ["edital:elaborar", "edital:submeter"])
    api_client.put(
        f"/api/v1/admin/editais/{edital.id}/rascunho",
        complete_draft(),
        format="json",
        **{**elabora, "HTTP_IF_MATCH": '"1"'},
    )
    api_client.post(
        f"/api/v1/admin/editais/{edital.id}/submissoes",
        format="json",
        **{**elabora, "HTTP_IF_MATCH": '"2"'},
    )
    api_client.post(
        f"/api/v1/admin/editais/{edital.id}/homologacoes",
        {"reason": "OK"},
        format="json",
        **{**actor_headers(quem_homologa, ["edital:homologar"]), "HTTP_IF_MATCH": '"3"'},
    )
    edital.refresh_from_db()
    assert edital.status == Edital.Status.HOMOLOGADO
    return edital


def submetida(edital, vigente, vagas="9"):
    ana = sessao(*ANA)
    retificacao = compor(ana, edital, vigente, vagas=vagas)
    praticar(ana, retificacao, "submeter")
    return retificacao


# ---------------------------------------------------------------------------------------------
# A — homologação: a primeira tela mostra, e o ato tira o item de todos
# ---------------------------------------------------------------------------------------------


def test_a_o_homologador_ve_a_retificacao_na_primeira_tela_e_ela_some_para_todos(edital, vigente):
    retificacao = submetida(edital, vigente)
    bruno, beatriz = sessao(*BRUNO), sessao(*BEATRIZ)

    resposta = lista(bruno)
    corpo = resposta.content.decode()
    objetos = resposta.context["faixa"].objetos

    assert [(o.natureza, o.ato) for o in objetos] == [("retificacao", "Analisar a Retificação")]
    assert objetos[0].url == reverse("interface:retificacao-detalhe", args=[retificacao.id])
    assert objetos[0].desde == Retificacao.objects.get(pk=retificacao.pk).submitted_at
    assert "Ações disponíveis para você" in corpo
    assert corpo.index("acoes-disponiveis-titulo") < corpo.index('<article class="processo">')
    assert [o.ato for o in faixa(beatriz).objetos] == ["Analisar a Retificação"]

    # Quem homologa vê o que homologa, na tela da decisão.
    confirmacao = bruno.get(
        reverse("interface:retificacao-ato", args=[retificacao.id, "homologar"])
    ).content.decode()
    assert "O que esta Retificação altera (2)" in confirmacao

    praticar(bruno, retificacao, "homologar", motivo="Conferido")

    for cliente in (bruno, beatriz):
        resposta = lista(cliente)
        assert not resposta.context["faixa"]
        assert NADA in resposta.content.decode()


# ---------------------------------------------------------------------------------------------
# B — publicação
# ---------------------------------------------------------------------------------------------


def test_b_o_publicador_encontra_a_homologada_e_ela_some_depois_de_publicada(edital, vigente):
    retificacao = submetida(edital, vigente)
    praticar(sessao(*BRUNO), retificacao, "homologar", motivo="Conferido")
    carla = sessao(*CARLA)

    assert [o.ato for o in faixa(carla).objetos] == ["Publicar a Retificação"]
    praticar(carla, retificacao, "publicar", **SIGNATARIO)

    assert not faixa(carla)
    assert Retificacao.objects.get(pk=retificacao.pk).status == Retificacao.Status.PUBLICADA


# ---------------------------------------------------------------------------------------------
# C — devolução, correção e reenvio do mesmo registro, até a publicação
# ---------------------------------------------------------------------------------------------


def test_c_a_devolvida_se_reconhece_e_a_reenviada_tambem(edital, vigente):
    retificacao = submetida(edital, vigente)
    ana, bruno = sessao(*ANA), sessao(*BRUNO)
    praticar(bruno, retificacao, "devolver", motivo="Falta a linha da ampla")

    resposta = lista(ana)
    corpo = resposta.content.decode()
    [objeto] = resposta.context["faixa"].objetos
    assert objeto.ato == "Corrigir a Retificação devolvida"
    assert objeto.detalhe == "Motivo da devolução: Falta a linha da ampla"
    assert "Retificação devolvida</a>" in corpo
    pagina = ana.get(reverse("interface:detalhe", args=[edital.id])).content.decode()
    assert ">Devolvida</span>" in pagina
    # Um verbo só para a devolvida (D-013): o cartão diz "Corrigir", e a seção abaixo também.
    assert "Corrigir a Retificação devolvida" in pagina
    assert "corrigir a Retificação devolvida e submetê-la de novo" in pagina
    assert "submeter a Retificação para revisão" not in pagina

    editar(ana, retificacao, "8")
    praticar(ana, retificacao, "submeter")
    [objeto] = faixa(bruno).objetos
    assert objeto.situacao == "Retificação reenviada, em revisão"
    assert "Reenviada depois de devolvida." in bruno.get(objeto.url).content.decode()

    praticar(bruno, retificacao, "homologar", motivo="Conferido")
    praticar(sessao(*CARLA), retificacao, "publicar", **SIGNATARIO)
    assert Retificacao.objects.filter(edital=edital).count() == 1


def test_c_o_rascunho_novo_nao_e_dito_devolvido(edital, vigente):
    compor(sessao(*ANA), edital, vigente)

    [objeto] = faixa(sessao(*ANA)).objetos

    assert objeto.ato == "Concluir e submeter a Retificação"
    assert objeto.situacao == "Retificação em elaboração"


# ---------------------------------------------------------------------------------------------
# D — Edital com impedimento
# ---------------------------------------------------------------------------------------------


def test_d_a_lista_nao_oferece_submeter_que_a_validacao_pode_recusar(
    api_client, manager_headers, process_payload
):
    """Edital novo, em elaboração e com pendência impeditiva: o detalhe desabilita "Submeter"."""
    api_client.post("/api/v1/admin/processos", process_payload, format="json", **manager_headers)
    edital = Edital.objects.get()
    ana = sessao(*ANA)

    resposta = lista(ana)
    linha = list(resposta.context["processos"][0].editais.all())[0]
    submeter = next(a for a in linha.acoes if a.chave == "submeter")
    detalhe = ana.get(reverse("interface:detalhe", args=[edital.id]))
    no_detalhe = next(a for a in detalhe.context["acoes"] if a.chave == "submeter")

    assert not no_detalhe.disponivel, "o detalhe vê a pendência"
    assert (submeter.rotulo, submeter.url) == (
        "Conferir e submeter",
        reverse("interface:detalhe", args=[edital.id]),
    )
    assert "Submeter para revisão" not in resposta.content.decode()
    # Na faixa, o Edital em elaboração conta como continuar a elaboração, que nunca é recusado.
    assert [o.ato for o in resposta.context["faixa"].objetos] == ["Continuar a elaboração"]


def test_d_quem_submeteu_e_homologou_nao_ve_publicar_como_acao(
    api_client, manager_headers, process_payload
):
    edital = homologado_por(api_client, manager_headers, process_payload, "dora", "dora")
    dora = sessao("dora", ["publicador"])

    resposta = lista(dora)
    linha = list(resposta.context["processos"][0].editais.all())[0]
    publicar = next(a for a in linha.acoes if a.chave == "publicar")

    assert not resposta.context["faixa"]
    assert not publicar.disponivel and "outra pessoa" in publicar.motivo
    assert "Conferir e publicar" not in resposta.content.decode()

    carla = sessao(*CARLA)
    [objeto] = faixa(carla).objetos
    assert (objeto.ato, objeto.url) == (
        "Conferir e publicar o Edital",
        reverse("interface:detalhe", args=[edital.id]),
    )
    assert objeto.desde is not None


# ---------------------------------------------------------------------------------------------
# E — vários papéis: um item por objeto, e a segregação respeitada
# ---------------------------------------------------------------------------------------------


def test_e_quem_acumula_papeis_ve_um_item_por_objeto(edital, vigente):
    submetida(edital, vigente)
    dora = sessao("dora.acumula", TODOS)

    objetos = faixa(dora).objetos

    assert [(o.natureza, o.ato) for o in objetos] == [("retificacao", "Analisar a Retificação")]


def test_e_a_publicacao_que_a_segregacao_recusa_nao_entra(edital, vigente):
    dora = sessao("dora.acumula", TODOS)
    retificacao = compor(dora, edital, vigente)
    praticar(dora, retificacao, "submeter")
    praticar(dora, retificacao, "homologar", motivo="Conferido")

    resposta = lista(dora)

    assert not resposta.context["faixa"]
    assert "Retificação homologada · aguarda quem publica</a>" in resposta.content.decode()
    assert [o.ato for o in faixa(sessao(*CARLA)).objetos] == ["Publicar a Retificação"]


# ---------------------------------------------------------------------------------------------
# F — sem ação: nada de faixa, e o inventário intacto
# ---------------------------------------------------------------------------------------------


def test_f_sem_acao_nao_ha_faixa_nem_zero(edital, vigente):
    submetida(edital, vigente)
    gabi = sessao(*GABI)

    resposta = lista(gabi)
    corpo = resposta.content.decode()

    assert not resposta.context["faixa"]
    assert NADA in corpo
    assert "acoes-disponiveis-titulo" not in corpo
    assert "0 procedimento" not in corpo
    assert reverse("interface:detalhe", args=[edital.id]) in corpo
    assert "Retificação em revisão · aguarda quem homologa</a>" in corpo


# ---------------------------------------------------------------------------------------------
# G — vários procedimentos: contagem, ordem, links, sem duplicidade
# ---------------------------------------------------------------------------------------------


def test_g_varios_procedimentos_ordenados_e_sem_duplicidade(
    edital, vigente, api_client, manager_headers, process_payload, monkeypatch
):
    primeira = submetida(edital, vigente, vagas="9")
    segunda = submetida(edital, vigente, vagas="8")
    dora = sessao("dora.acumula", TODOS)

    resposta = lista(dora)
    objetos = resposta.context["faixa"].objetos

    assert [o.chave for o in objetos] == [
        ("retificacao", primeira.id),
        ("retificacao", segunda.id),
    ], "a que espera há mais tempo vem primeiro"
    assert len({o.chave for o in objetos}) == len(objetos)
    assert "2 procedimentos" in resposta.content.decode()
    for objeto in objetos:
        assert dora.get(objeto.url).status_code == 200

    # Acima de cinco, os demais ficam no "Mostrar os outros", sem página nova.
    monkeypatch.setattr(trabalho, "MOSTRADOS", 1)
    corpo = lista(dora).content.decode()
    assert "Mostrar os outros 1" in corpo


# ---------------------------------------------------------------------------------------------
# A coluna e o detalhe não se contradizem
# ---------------------------------------------------------------------------------------------


def test_a_coluna_tem_o_ato_e_nao_diz_nenhuma_acao(edital, vigente):
    retificacao = submetida(edital, vigente)

    corpo = lista(sessao(*BRUNO)).content.decode()
    url = reverse("interface:retificacao-detalhe", args=[retificacao.id])

    assert f'<a class="acao principal-da-linha" href="{url}">Analisar a Retificação</a>' in corpo
    assert "Nenhuma ação disponível para seus papéis" not in corpo


def test_o_detalhe_do_edital_nomeia_a_retificacao_que_espera_a_pessoa(edital, vigente):
    submetida(edital, vigente)
    url = reverse("interface:detalhe", args=[edital.id])

    para_bruno = sessao(*BRUNO).get(url).content.decode()
    para_carla = sessao(*CARLA).get(url).content.decode()

    assert "Uma Retificação deste Edital aguarda você:" in para_bruno
    assert "Nenhum ato disponível para seus papéis nesta situação." not in para_bruno
    assert "aguarda quem homologa." in para_carla
    assert "Uma Retificação deste Edital aguarda você" not in para_carla


def test_a_confirmacao_separa_os_avisos_que_ja_valiam(edital, vigente, monkeypatch):
    """O aviso que o vigente já tinha vai para o `details`; o que o ato introduz fica em cima."""
    from types import SimpleNamespace

    from processo_seletivo.interface import views

    retificacao = submetida(edital, vigente)
    antigo = SimpleNamespace(code="ANTIGO", path="/a", message="Aviso de antes")
    novo = SimpleNamespace(code="NOVO", path="/b", message="Aviso do ato")
    monkeypatch.setattr(views, "advertencias_do_ato", lambda item: [antigo, novo])
    monkeypatch.setattr(views, "advertencias_do_vigente", lambda item: {("ANTIGO", "/a")})

    corpo = (
        sessao(*BRUNO)
        .get(reverse("interface:retificacao-ato", args=[retificacao.id, "homologar"]))
        .content.decode()
    )

    assert corpo.index("Aviso do ato") < corpo.index("Avisos que já valiam no Edital vigente (1)")
    assert corpo.index("Avisos que já valiam") < corpo.index("Aviso de antes")


# ---------------------------------------------------------------------------------------------
# I — regressão das outras áreas e do escopo
# ---------------------------------------------------------------------------------------------


def test_i_outra_unidade_nao_ve_item_nem_marca(edital, vigente):
    retificacao = submetida(edital, vigente)
    alheia = sessao("zeca", TODOS, escopo="outra-unidade")

    resposta = lista(alheia)

    assert not resposta.context["faixa"]
    assert str(retificacao.id) not in resposta.content.decode()


def test_i_minhas_etapas_diz_o_que_cobre_e_a_agenda_e_a_visao_seguem_de_pe(edital, vigente):
    submetida(edital, vigente)
    bruno = sessao(*BRUNO)

    etapas = bruno.get(reverse("interface:minhas-etapas")).content.decode()

    assert "Você não possui Etapas atribuídas no momento." in etapas
    assert "Esta área é da avaliação" in etapas
    assert reverse("interface:lista") in etapas
    assert bruno.get(reverse("interface:agenda")).status_code == 200
    gestor = sessao("gabi.visao", ["gestor"])
    assert gestor.get(reverse("interface:visao-geral")).status_code == 200


# ---------------------------------------------------------------------------------------------
# A cobertura: recursos e avaliação de comissão também são ações disponíveis (FR-2804)
# ---------------------------------------------------------------------------------------------


def test_os_recursos_que_aguardam_decisao_sao_um_item_por_edital(
    gestor, api_client, manager_headers, process_payload
):
    from processo_seletivo.recursos.models import DecisaoRecurso
    from tests.fixtures.recursos import decidir
    from tests.fixtures.recursos_us4 import cenario_julgavel

    peca = cenario_julgavel(
        gestor, api_client, manager_headers, process_payload, seed=152, codigo="0512"
    )
    edital = peca["cenario"]["edital"]
    marta = sessao("marta.julgadora", ["julgador"])

    [objeto] = faixa(marta).objetos
    assert (objeto.natureza, objeto.ato) == ("recursos", "Decidir recursos (1)")
    assert objeto.url == reverse("interface:recursos", args=[edital.id])
    assert "Recursos aguardando decisão (1)" in lista(marta).content.decode()

    # O cenário traz a peça já admitida, aguardando julgamento; decidida, ela sai.
    decidir(peca["recurso"], especie=DecisaoRecurso.Especie.INDEFERIDO)
    assert not faixa(marta)


def test_a_etapa_com_inscricoes_a_avaliar_e_um_item_e_conta_o_que_falta(
    gestor, api_client, manager_headers
):
    from tests.fixtures.mesa import concluir_como, distribuir_para, inscricoes_de, montar_banca

    cenario = montar_banca(gestor, api_client, manager_headers, seed=104, codigo="AD")
    inscricoes = inscricoes_de(cenario, 3, primeiro=1040)
    distribuir_para(cenario, gestor, ["joao"], inscricoes, chave="ad")
    joao = sessao("joao", [])

    [objeto] = faixa(joao).objetos
    assert (objeto.natureza, objeto.ato) == ("avaliacao", "Avaliar (3 pendentes)")
    assert objeto.url == reverse(
        "interface:minha-etapa", args=[cenario["edital"].id, cenario["etapa"]]
    )

    for inscricao in inscricoes:
        concluir_como(cenario, "joao", inscricao)
    assert not faixa(joao)


def test_o_edital_em_revisao_e_homologar_o_edital_e_some_depois(
    api_client, manager_headers, process_payload
):
    """O ramo do Edital submetido (FR-2804), que a convergência achou sem teste próprio."""
    criado = api_client.post(
        "/api/v1/admin/processos", process_payload, format="json", **manager_headers
    )
    edital = Edital.objects.get(processo_id=criado.json()["id"])
    elabora = actor_headers("ana.elaboradora", ["edital:elaborar", "edital:submeter"])
    api_client.put(
        f"/api/v1/admin/editais/{edital.id}/rascunho",
        complete_draft(),
        format="json",
        **{**elabora, "HTTP_IF_MATCH": '"1"'},
    )
    api_client.post(
        f"/api/v1/admin/editais/{edital.id}/submissoes",
        format="json",
        **{**elabora, "HTTP_IF_MATCH": '"2"'},
    )
    bruno = sessao(*BRUNO)

    [objeto] = faixa(bruno).objetos
    assert (objeto.natureza, objeto.ato, objeto.situacao) == (
        "edital",
        "Homologar o Edital",
        "Edital em revisão",
    )
    assert objeto.url == reverse("interface:detalhe", args=[edital.id])
    assert objeto.desde is not None
    assert not faixa(sessao(*CARLA)), "publicar ainda não cabe"

    api_client.post(
        f"/api/v1/admin/editais/{edital.id}/homologacoes",
        {"reason": "OK"},
        format="json",
        **{
            **actor_headers("bruno.homologador", ["edital:homologar"]),
            "HTTP_IF_MATCH": '"3"',
        },
    )
    assert not faixa(bruno)
    assert [o.ato for o in faixa(sessao(*CARLA)).objetos] == ["Conferir e publicar o Edital"]


def test_cada_item_da_faixa_e_um_link_so_com_o_ato_no_nome(edital, vigente):
    """D-011: o ato parecia botão e não respondia; agora o item inteiro é um link, e um só."""
    import re

    retificacao = submetida(edital, vigente)
    corpo = lista(sessao(*BRUNO)).content.decode()
    faixa_html = corpo[corpo.index('class="acoes-disponiveis"') : corpo.index("cobertura-da-faixa")]
    url = reverse("interface:retificacao-detalhe", args=[retificacao.id])

    assert faixa_html.count(f'href="{url}"') == 1
    assert re.search(
        rf'<a class="item-de-trabalho" href="{re.escape(url)}"\s+'
        r'aria-label="Analisar a Retificação: Retificação do Edital \d+/\d+"\s+'
        r'aria-describedby="contexto-mostrado-1">',
        faixa_html,
    )
    assert 'id="contexto-mostrado-1"' in faixa_html
