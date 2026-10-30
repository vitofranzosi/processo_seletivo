"""A passagem da Retificação entre pessoas — reprodução da auditoria de 29/10/2026.

**Por que existe.** Na reunião de validação de 29/10, quem homologa não encontrou a Retificação que
outra pessoa submetera, e só a alcançou colando o endereço copiado da sessão anterior. Estes casos
separam as três perguntas que a reunião misturou:

- **o servidor aceita a passagem?** — o fluxo inteiro, por três sessões distintas, por URL direta;
- **a navegação a oferece?** — partindo da Lista, sem conhecer o identificador;
- **a recusa é do servidor?** — o que a tela esconde também é recusado a quem envia direto.

Os casos marcados `xfail(strict=True)` descrevem o comportamento **esperado** que hoje não acontece.
O `strict` é o que os torna regressão: quando a correção chegar, eles passam, o pytest reprova o
`xfail` que sobrou, e quem corrigiu retira a marca — em vez de o achado ficar documentado por um
teste que nunca mais olha para ele.
"""

import re
from urllib.parse import urlsplit

import pytest
from django.test import Client
from django.urls import reverse

from processo_seletivo.auditoria.models import RegistroAuditoria
from processo_seletivo.interface.navegacao import SECOES
from processo_seletivo.publicacoes.models_retificacao import Retificacao, VersaoConsolidada
from tests.fixtures.autoridades import AUTORIDADE_DA_SUITE
from tests.fixtures.edital import caminho_linha_geral, caminho_perfil
from tests.fixtures.publicacao import publish_original
from tests.interface.conftest import identificar
from tests.interface.test_retificar import campos

pytestmark = [
    pytest.mark.django_db(transaction=True),
    pytest.mark.integration,
    pytest.mark.usefixtures("seletor_ligado"),
]

VAGAS = caminho_perfil("immediateVacancies")
LINHA_GERAL = caminho_linha_geral("immediateVacancies")
SIGNATARIO = {"signatario": str(AUTORIDADE_DA_SUITE)}

# A navegação por onde alguém procuraria: cada seção da barra — a Lista, Minhas Etapas, a Agenda e
# as que vierem — e tudo o que elas alcançam em dois cliques, desde que pertença ao Processo ou ao
# Edital em causa. As seções saem de `navegacao.SECOES`, para que uma porta nova entre na varredura
# sem ninguém lembrar dela; a que o papel não alcança responde fora de 200 e é ignorada. O
# documento e os PDFs ficam de fora — são arquivos, e não telas com caminho.
PROFUNDIDADE = 2
FORA_DA_NAVEGACAO = ("/documento", "/pdf", "/arquivo", "/sair", "/identificar")


@pytest.fixture
def edital(api_client, manager_headers, process_payload):
    return publish_original(api_client, manager_headers, process_payload)


@pytest.fixture
def vigente(edital):
    return VersaoConsolidada.objects.filter(edital=edital).latest("materialized_at")


def sessao(subject, papeis, escopo=None):
    """Uma sessão independente — outro navegador, outro cookie."""
    cliente = Client()
    identificar(cliente, subject, papeis, escopo=escopo)
    return cliente


def compor(cliente, edital, vigente, vagas="9"):
    url = reverse("interface:retificar", args=[edital.id])
    # A chave nasce no GET, como no navegador: sem ela, dois rascunhos colidiriam na chave vazia.
    chave = cliente.get(url).context["chave_idempotencia"]
    resposta = cliente.post(
        url,
        {
            **campos(vigente, **{VAGAS: vagas, LINHA_GERAL: vagas}),
            "justificativa": "Ampliação de vagas",
            "confirmar": "1",
            "chave_idempotencia": chave,
        },
    )
    assert resposta.status_code == 302, (resposta.context or {}).get("erros")
    return Retificacao.objects.latest("created_at")


def ato(cliente, retificacao, acao, **campos_extra):
    url = reverse("interface:retificacao-ato", args=[retificacao.id, acao])
    chave = cliente.get(url).context["chave_idempotencia"]
    return cliente.post(url, {"chave_idempotencia": chave, **campos_extra})


def submetida(edital, vigente):
    ana = sessao("ana.elaboradora", ["elaborador"])
    retificacao = compor(ana, edital, vigente)
    assert ato(ana, retificacao, "submeter").status_code == 302
    retificacao.refresh_from_db()
    assert retificacao.status == Retificacao.Status.EM_REVISAO
    return retificacao


def homologada(edital, vigente):
    retificacao = submetida(edital, vigente)
    bruno = sessao("bruno.homologador", ["homologador"])
    assert ato(bruno, retificacao, "homologar", motivo="Conferido").status_code == 302
    retificacao.refresh_from_db()
    assert retificacao.status == Retificacao.Status.HOMOLOGADA
    return retificacao


def _links(html):
    return {
        urlsplit(href.replace("&amp;", "&")).path for href in re.findall(r'href="([^"]+)"', html)
    }


def navegar(cliente, edital):
    """Tudo o que a pessoa alcança a partir da barra, sem digitar endereço nenhum."""
    relevantes = (str(edital.id), str(edital.processo_id))
    visitadas, fronteira, paginas = set(), [reverse(secao.rota) for secao in SECOES], {}
    for _ in range(PROFUNDIDADE + 1):
        proxima = []
        for caminho in fronteira:
            if caminho in visitadas:
                continue
            visitadas.add(caminho)
            resposta = cliente.get(caminho)
            if resposta.status_code != 200 or "html" not in resposta.get("Content-Type", ""):
                continue
            html = resposta.content.decode()
            paginas[caminho] = html
            proxima += [
                link
                for link in _links(html)
                if link.startswith("/gestao/")
                and any(chave in link for chave in relevantes)
                and not any(trecho in link for trecho in FORA_DA_NAVEGACAO)
            ]
        fronteira = proxima
    return paginas


def alcancada(paginas, retificacao):
    destino = reverse("interface:retificacao-detalhe", args=[retificacao.id])
    return [caminho for caminho, html in paginas.items() if destino in _links(html)]


# ---------------------------------------------------------------------------------------------
# 1. O servidor aceita a passagem entre três pessoas
# ---------------------------------------------------------------------------------------------


def test_tres_sessoes_concluem_o_fluxo_pela_url_direta(edital, vigente):
    """O caminho que a reunião percorreu, com o endereço copiado: ele funciona de ponta a ponta."""
    retificacao = homologada(edital, vigente)
    carla = sessao("carla.publicadora", ["publicador"])

    detalhe = carla.get(reverse("interface:retificacao-detalhe", args=[retificacao.id]))
    assert "Publicar Retificação" in detalhe.content.decode()
    assert ato(carla, retificacao, "publicar", **SIGNATARIO).status_code == 302

    retificacao.refresh_from_db()
    assert retificacao.status == Retificacao.Status.PUBLICADA
    assert retificacao.prepared_by == "ana.elaboradora"
    assert retificacao.homologated_by == "bruno.homologador"
    assert retificacao.publication.published_by == "carla.publicadora"


def test_a_trilha_registra_ator_operacao_e_os_dois_estados(edital, vigente):
    retificacao = homologada(edital, vigente)
    ato(sessao("carla.publicadora", ["publicador"]), retificacao, "publicar", **SIGNATARIO)

    registros = RegistroAuditoria.objects.filter(
        aggregate_id=retificacao.id,
        operation__in=["CRIAR", "SUBMETER", "HOMOLOGAR", "PUBLICAR"],
    ).order_by("occurred_at")

    assert [
        (r.operation, r.actor_subject, r.permission, r.previous_state, r.new_state)
        for r in registros
    ] == [
        ("CRIAR", "ana.elaboradora", "retificacao:elaborar", "", "EM_ELABORACAO"),
        ("SUBMETER", "ana.elaboradora", "retificacao:submeter", "EM_ELABORACAO", "EM_REVISAO"),
        ("HOMOLOGAR", "bruno.homologador", "retificacao:homologar", "EM_REVISAO", "HOMOLOGADA"),
        ("PUBLICAR", "carla.publicadora", "retificacao:publicar", "HOMOLOGADA", "PUBLICADA"),
    ]
    assert all(r.occurred_at for r in registros)


# ---------------------------------------------------------------------------------------------
# 2. A navegação oferece a passagem? — o ponto em que a continuidade se rompe
# ---------------------------------------------------------------------------------------------


@pytest.mark.xfail(
    strict=True,
    reason="AUD-RET-01: nenhuma tela lista Retificação não publicada; o único link para o "
    "detalhe sai de 'Documentos publicados'",
)
def test_quem_homologa_encontra_a_retificacao_em_revisao_sem_conhecer_a_url(edital, vigente):
    retificacao = submetida(edital, vigente)
    bruno = sessao("bruno.homologador", ["homologador"])

    assert alcancada(navegar(bruno, edital), retificacao)


@pytest.mark.xfail(strict=True, reason="AUD-RET-01: idem, para a homologada")
def test_quem_publica_encontra_a_retificacao_homologada_sem_conhecer_a_url(edital, vigente):
    retificacao = homologada(edital, vigente)
    carla = sessao("carla.publicadora", ["publicador"])

    assert alcancada(navegar(carla, edital), retificacao)


@pytest.mark.xfail(
    strict=True,
    reason="AUD-RET-01: nem quem criou reencontra o próprio rascunho depois de sair da tela — "
    "não é filtro por autoria, é ausência de listagem",
)
def test_quem_elabora_reencontra_o_proprio_rascunho(edital, vigente):
    ana = sessao("ana.elaboradora", ["elaborador"])
    retificacao = compor(ana, edital, vigente)

    assert alcancada(navegar(ana, edital), retificacao)


def test_hoje_nenhuma_tela_alcancavel_cita_a_retificacao_pendente(edital, vigente):
    """A forma positiva do achado: o que a navegação mostra, e o que ela não mostra.

    O homologador alcança a Lista, a Agenda, o Processo e o Edital — e o Edital, publicado, diz o
    que se faz com ele sem dizer que há uma Retificação esperando por esta pessoa. A Agenda anuncia
    só a Retificação já publicada com vigência futura (101), que é outra coisa. Nem o identificador
    nem o endereço aparecem em página alguma.
    """
    retificacao = submetida(edital, vigente)
    paginas = navegar(sessao("bruno.homologador", ["homologador"]), edital)

    assert reverse("interface:detalhe", args=[edital.id]) in paginas
    assert reverse("interface:agenda") in paginas
    assert not [caminho for caminho, html in paginas.items() if str(retificacao.id) in html]


def test_a_unica_porta_e_a_da_retificacao_ja_publicada(edital, vigente):
    """Depois de publicada, o detalhe do Edital passa a ligar a ela — antes, não."""
    retificacao = homologada(edital, vigente)
    ato(sessao("carla.publicadora", ["publicador"]), retificacao, "publicar", **SIGNATARIO)

    paginas = navegar(sessao("bruno.homologador", ["homologador"]), edital)

    assert alcancada(paginas, retificacao) == [reverse("interface:detalhe", args=[edital.id])]


def test_um_segundo_rascunho_nasce_sem_aviso_do_primeiro(edital, vigente):
    """Quem não encontra o rascunho começa outro: a tela de Retificar não diz que já existe um."""
    ana = sessao("ana.elaboradora", ["elaborador"])
    primeira = compor(ana, edital, vigente, vagas="9")

    tela = ana.get(reverse("interface:retificar", args=[edital.id])).content.decode()
    segunda = compor(ana, edital, vigente, vagas="8")

    assert str(primeira.id) not in tela
    assert primeira.id != segunda.id
    assert (
        Retificacao.objects.filter(edital=edital, status=Retificacao.Status.EM_ELABORACAO).count()
        == 2
    )


# ---------------------------------------------------------------------------------------------
# 3. A tela e o servidor concordam sobre o ato?
# ---------------------------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("papeis", "situacao", "acao", "oferece"),
    [
        (["homologador"], "EM_REVISAO", "homologar", True),
        (["publicador"], "EM_REVISAO", "homologar", False),
        (["elaborador"], "EM_REVISAO", "homologar", False),
        (["publicador"], "HOMOLOGADA", "publicar", True),
        (["homologador"], "HOMOLOGADA", "publicar", False),
    ],
)
def test_o_detalhe_oferece_exatamente_o_que_o_servidor_aceita(
    edital, vigente, papeis, situacao, acao, oferece
):
    retificacao = (homologada if situacao == "HOMOLOGADA" else submetida)(edital, vigente)
    cliente = sessao("pessoa.de.teste", papeis)
    rotulo = {"homologar": "Homologar", "publicar": "Publicar Retificação"}[acao]

    corpo = cliente.get(
        reverse("interface:retificacao-detalhe", args=[retificacao.id])
    ).content.decode()
    resposta = ato(cliente, retificacao, acao, motivo="Conferido", **SIGNATARIO)

    assert (f">{rotulo}</a>" in corpo) is oferece
    assert (resposta.status_code == 302) is oferece
    if not oferece:
        assert resposta.status_code == 403


def test_ato_em_situacao_incompativel_e_recusado_pelo_servidor(edital, vigente):
    retificacao = submetida(edital, vigente)
    carla = sessao("carla.publicadora", ["publicador"])

    resposta = ato(carla, retificacao, "publicar", **SIGNATARIO)

    assert resposta.status_code == 409
    retificacao.refresh_from_db()
    assert retificacao.status == Retificacao.Status.EM_REVISAO


def test_outra_unidade_nao_ve_nem_pratica(edital, vigente):
    retificacao = submetida(edital, vigente)
    alheio = sessao("zeca.homologador", ["homologador"], escopo="outra-unidade")

    detalhe = alheio.get(reverse("interface:retificacao-detalhe", args=[retificacao.id]))
    envio = alheio.post(
        reverse("interface:retificacao-ato", args=[retificacao.id, "homologar"]),
        {"chave_idempotencia": "ui-alheio", "motivo": "x"},
    )

    assert detalhe.status_code == 404
    assert envio.status_code == 404
    retificacao.refresh_from_db()
    assert retificacao.status == Retificacao.Status.EM_REVISAO


def test_a_segunda_homologacao_e_recusada_e_nao_duplica(edital, vigente):
    """Duas sessões com a mesma tela aberta: a segunda chega a uma situação que já mudou."""
    retificacao = submetida(edital, vigente)
    url = reverse("interface:retificacao-ato", args=[retificacao.id, "homologar"])
    bruno, beatriz = (
        sessao("bruno.homologador", ["homologador"]),
        sessao("beatriz.homologadora", ["homologador"]),
    )
    chaves = [cliente.get(url).context["chave_idempotencia"] for cliente in (bruno, beatriz)]

    primeira = bruno.post(url, {"chave_idempotencia": chaves[0], "motivo": "ok"})
    segunda = beatriz.post(url, {"chave_idempotencia": chaves[1], "motivo": "ok"})

    assert (primeira.status_code, segunda.status_code) == (302, 409)
    retificacao.refresh_from_db()
    assert retificacao.homologated_by == "bruno.homologador"
    assert (
        RegistroAuditoria.objects.filter(aggregate_id=retificacao.id, operation="HOMOLOGAR").count()
        == 1
    )


# ---------------------------------------------------------------------------------------------
# 4. Segregação por identidade
# ---------------------------------------------------------------------------------------------

TODOS = ["elaborador", "homologador", "publicador"]


def _uma_pessoa_ate_homologar(edital, vigente):
    dora = sessao("dora.acumula", TODOS)
    retificacao = compor(dora, edital, vigente)
    ato(dora, retificacao, "submeter")
    ato(dora, retificacao, "homologar", motivo="Conferido")
    retificacao.refresh_from_db()
    assert retificacao.status == Retificacao.Status.HOMOLOGADA
    return dora, retificacao


def test_uma_pessoa_sozinha_nao_publica_o_que_elaborou_e_homologou(edital, vigente):
    dora, retificacao = _uma_pessoa_ate_homologar(edital, vigente)

    resposta = ato(dora, retificacao, "publicar", **SIGNATARIO)

    assert resposta.status_code == 403
    assert "elaborar, homologar e publicar" in resposta.content.decode()
    retificacao.refresh_from_db()
    assert retificacao.status == Retificacao.Status.HOMOLOGADA


@pytest.mark.xfail(
    strict=True,
    reason="AUD-RET-03: o detalhe oferece 'Publicar Retificação' a quem o servidor vai recusar "
    "por segregação; o Edital avisa antes, a Retificação não",
)
def test_o_detalhe_nao_oferece_publicar_a_quem_a_segregacao_impede(edital, vigente):
    dora, retificacao = _uma_pessoa_ate_homologar(edital, vigente)

    corpo = dora.get(
        reverse("interface:retificacao-detalhe", args=[retificacao.id])
    ).content.decode()

    assert ">Publicar Retificação</a>" not in corpo


def test_caracterizacao_quem_so_compos_conclui_se_outra_pessoa_submeter(edital, vigente):
    """**Caracterização, e não regra confirmada.** A segregação lê `prepared_by`, que é quem
    **submeteu**; `created_by` — quem compôs as alterações — não entra na conta. Quem compõe,
    homologa e publica fica de fora da recusa se outra pessoa apenas clicar em "Submeter".

    Se o "elaborou" da regra for "compôs", este caso deve passar a ser recusado. A decisão é de
    governança, e este teste existe para que a resposta, qualquer que seja, fique escrita.
    """
    dora = sessao("dora.acumula", TODOS)
    retificacao = compor(dora, edital, vigente)
    ato(sessao("ana.elaboradora", ["elaborador"]), retificacao, "submeter")
    ato(dora, retificacao, "homologar", motivo="Conferido")

    resposta = ato(dora, retificacao, "publicar", **SIGNATARIO)

    retificacao.refresh_from_db()
    assert resposta.status_code == 302
    assert retificacao.created_by == "dora.acumula"
    assert retificacao.prepared_by == "ana.elaboradora"
    assert retificacao.homologated_by == retificacao.publication.published_by == "dora.acumula"
