"""As decisões de produto da etapa 4, aprovadas pelo usuário em 18/10/2026 (088).

Três delas mudam alguma coisa: a trilha do cabeçalho sai no papel (D-001), o rótulo do aviso na
trilha ganha a hora (D-003) e "Classificação", no Ato, leva ao recorte do ato (D-004). A quarta — o
landmark de trilha sem link da lista e de Minhas Etapas — fica como está, e quem a prova continua
sendo `test_telas_de_uso_diario.py`. A impressão em si é conferida pelo Chrome (quickstart): aqui
fica o que a folha e a marcação garantem.
"""

import datetime as dt
import re
from pathlib import Path
from unittest import mock

import pytest
from django.urls import reverse
from django.utils import timezone

from tests.fixtures.corte import MARCO
from tests.fixtures.mesa import montar_cenario_da_presidencia
from tests.fixtures.recortes import MODALIDADE_PPI, emitir_recorte, montar_cenario_7_1_2
from tests.interface.conftest import identificar
from tests.interface.test_telas_de_inscricoes_e_recursos import (  # noqa: F401 — fixtures
    JULGADORA,
    cenario,
    peca,
)
from tests.interface.test_telas_de_uso_diario import cabecalho, trilha_unica_no_cabecalho
from tests.interface.test_telas_dos_avisos import publicado  # noqa: F401 — fixture

GESTAO = Path(__file__).resolve().parents[2] / "processo_seletivo/interface/templates/interface"
BASE = GESTAO / "base.html"
TROCAR_IDENTIDADE = f'<a href="{reverse("interface:identificar")}">Trocar identidade</a>'


def regras_de_impressao():
    """O corpo do `@media print` da folha comum, sem os comentários de Django."""
    folha = re.sub(r"\{% comment %\}.*?\{% endcomment %\}", "", BASE.read_text(), flags=re.S)
    inicio = folha.index("@media print{") + len("@media print{")
    profundidade, fim = 1, inicio
    while profundidade:
        profundidade += {"{": 1, "}": -1}.get(folha[fim], 0)
        fim += 1
    return folha[inicio : fim - 1]


def escondidos_no_papel():
    return {
        seletor.strip()
        for seletores, corpo in re.findall(r"([^{}]+)\{([^{}]*)\}", regras_de_impressao())
        if "display:none" in corpo.replace(" ", "")
        for seletor in seletores.split(",")
    }


def no_papel(corpo):
    """O que o cabeçalho de contexto imprime: tudo, menos o link direto dele, "Trocar identidade".

    A folha esconde `.cabecalho-de-contexto>a`, e só ele: se outro link entrar no cabeçalho fora da
    trilha, ele sumiria do papel sem ninguém decidir — e é isso que esta função não deixa passar.
    """
    cab = cabecalho(corpo)
    assert cab.count(TROCAR_IDENTIDADE) == 1
    impresso = cab.replace(TROCAR_IDENTIDADE, "")
    fora_da_trilha = re.sub(r"<nav .*?</nav>", "", impresso, flags=re.S)
    assert "<a " not in fora_da_trilha, "link no cabeçalho fora da trilha"
    return impresso


# ---- a trilha no papel (D-001, D-005) ----------------------------------------------------------


def test_no_papel_sai_o_cabecalho_sem_trocar_identidade_e_sem_a_barra():
    """`FR-2000`, `FR-2001`: a `076` escondia o cabeçalho inteiro; desde a `088`, só a ação dele."""
    escondidos = escondidos_no_papel()

    assert ".barra-lateral" in escondidos
    assert ".cabecalho-de-contexto>a" in escondidos
    assert ".cabecalho-de-contexto" not in escondidos
    assert ".caminho-da-secao" not in " ".join(escondidos)


def test_a_regra_de_impressao_e_uma_so():
    """`FR-2002`: nenhuma tela tem regra de impressão própria para o cabeçalho ou a trilha — a da
    folha comum vale para todas, inclusive para a recusa, que é a última com o caminho da `076`."""
    for template in GESTAO.glob("*.html"):
        if template == BASE:
            continue
        fonte = template.read_text()
        for bloco in re.findall(r"@media print\{(.*?)\n\}", fonte, re.S):
            assert "cabecalho-de-contexto" not in bloco, template.name
            assert "caminho-da-secao" not in bloco, template.name


def test_no_papel_a_trilha_quebra_a_linha():
    """`FR-2004`: a folha impressa é mais estreita que a tela, e nenhum nível pode ser cortado."""
    regras = regras_de_impressao().replace(" ", "")
    assert "white-space:nowrap" not in regras
    assert "overflow:hidden" not in regras


@pytest.fixture
def certame(gestor, api_client, manager_headers, process_payload):
    """Edital 7/1/2, com a ordem da ampla e a da lista PPI emitidas."""
    edital, _, _ = montar_cenario_7_1_2(
        gestor, api_client, manager_headers, process_payload, prefixo="decisoes-088"
    )
    emitir_recorte(edital, gestor, lista_id=MODALIDADE_PPI, chave="decisoes-088-ppi")
    return edital


def _ato(edital, lista_id):
    from processo_seletivo.classificacao.application.selectors import ato_vigente

    return ato_vigente(edital=edital, marco_id=MARCO, lista_id=lista_id)


def _abrir(client, url):
    resposta = client.get(url)
    assert resposta.status_code == 200, url
    return resposta.content.decode()


def _url_do_ato(edital, ato):
    return reverse("interface:ato-de-ordenacao", args=[edital.id, MARCO, ato.id])


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_impresso_o_ato_diz_de_que_edital_e(client, seletor_ligado, certame):
    """`SC-780`: o Ato é a tela cuja folha a comissão leva à reunião."""
    identificar(client, "carlos", ["gestor"])
    papel = no_papel(_abrir(client, _url_do_ato(certame, _ato(certame, MODALIDADE_PPI))))
    assert f"Edital {certame.number}/{certame.year}</a>" in papel


@pytest.mark.django_db
@pytest.mark.integration
def test_impressa_a_inscricao_recebida_diz_de_que_edital_e(client, seletor_ligado, cenario):  # noqa: F811
    """`SC-780`."""
    identificar(client, "carlos", ["gestor"])
    edital, inscricao = cenario["edital"], cenario["inscricao"]
    papel = no_papel(_abrir(client, reverse("interface:inscricao-recebida", args=[inscricao.id])))
    assert f"Edital {edital.number}/{edital.year}</a>" in papel


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_impresso_o_recurso_diz_de_que_edital_e(client, seletor_ligado, peca):  # noqa: F811
    """`SC-780`."""
    edital, recurso = peca["cenario"]["edital"], peca["recurso"]
    identificar(client, JULGADORA, ["julgador"])
    papel = no_papel(_abrir(client, reverse("interface:recurso", args=[recurso.id])))
    assert f"Edital {edital.number}/{edital.year}</a>" in papel


@pytest.mark.django_db
@pytest.mark.integration
def test_impressa_a_inscricao_da_mesa_diz_de_que_mesa_e(
    client, seletor_ligado, gestor, api_client, manager_headers, raiz_de_arquivos
):
    """`SC-780`: a trilha da Mesa não passa pelo Edital — é a de quem avalia —, e é ela que sai."""
    mesa = montar_cenario_da_presidencia(gestor, api_client, manager_headers)
    edital, etapa, inscricao = mesa["edital"], mesa["etapa"], mesa["inscricao"]
    identificar(client, "joao", [])
    papel = no_papel(
        _abrir(client, reverse("interface:mesa-inscricao", args=[edital.id, etapa, inscricao.id]))
    )
    minha_mesa = reverse("interface:minha-etapa", args=[edital.id, etapa])
    assert f'<a href="{minha_mesa}">Minha Mesa</a>' in papel


@pytest.mark.django_db
@pytest.mark.integration
def test_impressa_a_recusa_sai_com_o_caminho_da_secao(client, seletor_ligado):
    """Caso-limite "Tela sem trilha, impressa": a recusa imprime o caminho até a seção, e nada
    mais (D-005)."""
    import uuid

    identificar(client, "carlos", ["gestor"])
    resposta = client.get(reverse("interface:inscricoes", args=[uuid.uuid4()]))
    assert resposta.status_code == 404
    papel = no_papel(resposta.content.decode())
    assert '<p class="caminho-da-secao">' in papel


# ---- a hora no rótulo do aviso (D-003, D-007) --------------------------------------------------


def _proximo(hora_utc, minuto=0):
    """O próximo instante, no futuro, com aquela hora em UTC — o aviso não pode preceder o ato."""
    agora = timezone.now().astimezone(dt.UTC)
    instante = agora.replace(hour=hora_utc, minute=minuto, second=0, microsecond=0)
    return instante if instante > agora else instante + dt.timedelta(days=1)


def _aviso_em(publicado_, instante, **kwargs):  # noqa: F811
    from processo_seletivo.avisos.models import Aviso
    from tests.fixtures.avisos import avisar_resultado

    with mock.patch("django.utils.timezone.now", return_value=instante):
        declarado = avisar_resultado(
            publicado_["edital"], publicado_["publicacao"].marco_id, **kwargs
        )
    aviso = Aviso.objects.get(pk=declarado["aviso"])
    assert aviso.solicitado_em == instante
    return aviso


def _rotulo(trilha, aviso_id):
    """O rótulo do aviso na trilha: a página atual, ou o link que leva a ele."""
    destino = reverse("interface:aviso", args=[aviso_id])
    link = re.search(rf'<a href="{re.escape(destino)}">([^<]+)</a>', trilha)
    return link.group(1) if link else re.search(r'aria-current="page">([^<]+)<', trilha).group(1)


def _tres_trilhas(client, aviso):
    from processo_seletivo.avisos.domain import nomes

    return {
        "histórico": reverse("interface:aviso", args=[aviso.id]),
        "interrupção": reverse("interface:aviso-interromper", args=[aviso.id]),
        "reenvio": reverse("interface:aviso-reenviar", args=[aviso.id])
        + f"?motivo={nomes.REENVIO_JUSTIFICADO}",
    }


@pytest.mark.django_db
@pytest.mark.integration
def test_o_rotulo_do_aviso_tem_a_hora_de_brasilia(client, seletor_ligado, publicado):  # noqa: F811
    """`FR-2010`, `FR-2011`; caso-limite "Aviso perto da meia-noite em UTC": às 01:30 UTC são
    22:30 do dia anterior em America/Sao_Paulo, e é esse o dia e a hora da trilha — os do título."""
    instante = _proximo(1, 30)
    aviso = _aviso_em(publicado, instante)
    local = timezone.localtime(instante)
    assert local.date() != instante.date()
    esperado = f"Aviso de {local:%d/%m/%Y} às 22:30"

    identificar(client, "publicadora", ["publicador"])
    for tela, url in _tres_trilhas(client, aviso).items():
        corpo = _abrir(client, url)
        assert _rotulo(trilha_unica_no_cabecalho(corpo), aviso.id) == esperado, tela
    assert f"<h1>{esperado}</h1>" in _abrir(client, reverse("interface:aviso", args=[aviso.id]))


@pytest.mark.django_db
@pytest.mark.integration
def test_dois_avisos_do_mesmo_dia_tem_rotulos_diferentes(client, seletor_ligado, publicado):  # noqa: F811
    """`SC-782`: às 10:00 e às 16:00 de Brasília, no mesmo dia, nas três telas que o nomeiam."""
    manha = _proximo(13)
    tarde = manha + dt.timedelta(hours=6)
    primeiro = _aviso_em(publicado, manha)
    segundo = _aviso_em(
        publicado, tarde, chave="avisar-088-tarde", justificativa="O texto da manhã saiu errado."
    )
    assert timezone.localtime(manha).date() == timezone.localtime(tarde).date()

    identificar(client, "publicadora", ["publicador"])
    for tela in ("histórico", "interrupção", "reenvio"):
        rotulos = {
            _rotulo(trilha_unica_no_cabecalho(_abrir(client, _tres_trilhas(client, a)[tela])), a.id)
            for a in (primeiro, segundo)
        }
        assert len(rotulos) == 2, (tela, rotulos)


# ---- "Classificação" no recorte do ato (D-004, D-006) ------------------------------------------


def _link_da_classificacao(corpo):
    return re.search(
        r'<a href="([^"]+)">Classificação</a> ›', trilha_unica_no_cabecalho(corpo)
    ).group(1)


def _recorte_atual(corpo):
    return re.search(
        r'<nav aria-label="Recortes deste marco".*?<span aria-current="true">([^<]+)</span>',
        corpo,
        re.S,
    ).group(1)


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_do_ato_de_uma_lista_a_classificacao_e_a_dessa_lista(client, seletor_ligado, certame):
    """`FR-2020`, `FR-2021`, `SC-783`: o desvio que a decisão 006 da `084` registrou. O endereço é o
    mesmo que "Cancelar e voltar" usa na conferência da emissão do mesmo recorte."""
    identificar(client, "carlos", ["gestor"])
    ordenacao = reverse("interface:ordenacao", args=[certame.id, MARCO])
    ato = _abrir(client, _url_do_ato(certame, _ato(certame, MODALIDADE_PPI)))
    destino = _link_da_classificacao(ato)

    assert destino == f"{ordenacao}?lista={MODALIDADE_PPI}"
    conferencia = client.post(
        reverse("interface:emitir-ordenacao", args=[certame.id, MARCO]),
        {"chave_idempotencia": "decisoes-088-conferir", "lista": MODALIDADE_PPI},
    ).content.decode()
    assert f'href="{destino}"' in conferencia

    da_lista = _abrir(client, destino)
    assert _recorte_atual(da_lista) == _recorte_atual(
        _abrir(client, f"{ordenacao}?lista={MODALIDADE_PPI}")
    )
    assert _recorte_atual(da_lista) != _recorte_atual(_abrir(client, ordenacao))


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_do_ato_da_ampla_a_classificacao_e_a_de_antes(client, seletor_ligado, certame):
    """`FR-2020`, `FR-2022`: sem recorte pedido, como antes; o rótulo e o fim da trilha ficam."""
    identificar(client, "carlos", ["gestor"])
    ato = _ato(certame, None)
    corpo = _abrir(client, _url_do_ato(certame, ato))

    assert _link_da_classificacao(corpo) == reverse("interface:ordenacao", args=[certame.id, MARCO])
    assert (
        trilha_unica_no_cabecalho(corpo)
        .rstrip()
        .endswith(f'<span aria-current="page">Ato {ato.id}</span>')
    )


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_quem_audita_segue_o_mesmo_link(client, seletor_ligado, certame):
    """Caso-limite "Quem audita": o link e o destino não dependem de quem lê; a porta da
    Classificação continua a dela."""
    url = _url_do_ato(certame, _ato(certame, MODALIDADE_PPI))
    destinos = set()
    for nome, papeis in (("carlos", ["gestor"]), ("auditora", ["auditor"])):
        identificar(client, nome, papeis)
        destinos.add(_link_da_classificacao(_abrir(client, url)))
    assert len(destinos) == 1
