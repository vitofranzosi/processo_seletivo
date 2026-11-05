"""A escolha da família na tela, a prévia e a exportação por formato, e o ZIP de família.

(119, FR-3805–FR-3808, FR-3818, FR-3828–FR-3830; EC-1, EC-7, EC-8, EC-9, EC-23.)

Os Editais são os do corpus pelo fluxo real, do Cefor, cuja família da comunicação é a Pós Lato
Sensu. A suíte libera todo o registro (`config/settings/test.py`); os casos de template não liberado
ou em versão divergente mudam a configuração por `settings`.
"""

import dataclasses
import io
import json
import zipfile

import pytest
from django.urls import reverse
from django.utils import timezone

from processo_seletivo.auditoria.models import RegistroAuditoria
from processo_seletivo.interface import kit_escolha, kit_familias, kit_pacote, kit_peca
from processo_seletivo.interface.kit_familias import fic, institucional, pos_lato_sensu
from processo_seletivo.portal import ficha as fichas
from tests.fixtures import kit
from tests.interface.conftest import identificar

pytestmark = pytest.mark.django_db

PUBLICO = "gps.exemplo.ifes.edu.br"
LATO = pos_lato_sensu.CHAVE
sem_rasterizador = pytest.mark.skipif(
    not kit_pacote.disponivel(), reason="o `resvg-py` não está instalado neste ambiente"
)


@pytest.fixture
def comunicacao(client, seletor_ligado, settings):
    settings.ALLOWED_HOSTS = [*settings.ALLOWED_HOSTS, PUBLICO]
    identificar(client, "cora.comunicacao", ["comunicacao"])
    return client


@pytest.fixture
def edital(api_client):
    return kit.publicar(api_client, chave="familias-na-tela", mudar=kit.lato_uma_oferta)


def _impressao(edital):
    return fichas.ler(edital, agora=timezone.now(), base_url=None).impressao


def _tela(client, edital, **consulta):
    return client.get(
        reverse("interface:kit-de-divulgacao", args=[edital.id]), consulta, HTTP_HOST=PUBLICO
    )


def _previa(client, edital, **consulta):
    consulta.setdefault("impressao", _impressao(edital))
    return client.get(
        reverse("interface:kit-de-divulgacao-previa", args=[edital.id]),
        consulta,
        HTTP_HOST=PUBLICO,
    )


def _exportar(client, edital, formato, **dados):
    dados.setdefault("impressao", _impressao(edital))
    return client.post(
        reverse("interface:kit-de-divulgacao-exportar", args=[edital.id, formato]),
        dados,
        HTTP_HOST=PUBLICO,
    )


def _eventos(edital):
    return RegistroAuditoria.objects.filter(
        aggregate_id=edital.id, operation="EXPORTAR_MATERIAL"
    ).order_by("occurred_at")


def _sem(settings, *formatos, familia=LATO):
    """A configuração da suíte sem os formatos dados da família (a Pós Lato Sensu, se não dita)."""
    settings.KIT_DE_DIVULGACAO_TEMPLATES = tuple(
        entrada
        for entrada in settings.KIT_DE_DIVULGACAO_TEMPLATES
        if not (entrada[0] == familia and entrada[1] in formatos)
    )


# ---- A lista (FR-3805, EC-1) ----------------------------------------------------------------


def test_sem_exportacao_a_tela_traz_a_institucional_e_oferece_a_familia_da_unidade(
    comunicacao, edital
):
    resposta = _tela(comunicacao, edital)
    assert resposta.status_code == 200
    escolha = resposta.context["escolha"]
    assert escolha.familia.chave == institucional.CHAVE
    assert [f.chave for f in resposta.context["familias"]] == [institucional.CHAVE, LATO, fic.CHAVE]
    assert resposta.context["secoes_da_familia"] is None


def test_unidade_sem_familia_so_tem_a_institucional():
    ficha = dataclasses.replace(_ficha_qualquer(), unidade_codigo="campus-serra")
    assert [f.chave for f in kit_escolha.familias_oferecidas(ficha)] == [institucional.CHAVE]


def test_familia_sem_template_liberado_nao_e_oferecida(settings):
    _sem(settings, "post", "story", "banner")
    oferecidas = [f.chave for f in kit_escolha.familias_oferecidas(_ficha_qualquer())]
    assert oferecidas == [institucional.CHAVE, fic.CHAVE]
    _sem(settings, "post", "story", "banner", familia=fic.CHAVE)
    assert [f.chave for f in kit_escolha.familias_oferecidas(_ficha_qualquer())] == [
        institucional.CHAVE
    ]


def _ficha_qualquer():
    from tests.unit.kit.test_textos import _ficha

    return dataclasses.replace(_ficha(), unidade_codigo="cefor")


# ---- A tela da família (FR-3830, FR-3808) ---------------------------------------------------


def test_a_familia_escolhida_mostra_os_tres_formatos_com_previa_e_exportacao(comunicacao, edital):
    resposta = _tela(comunicacao, edital, familia=LATO, imagem="grupo")
    assert resposta.status_code == 200
    secoes = resposta.context["secoes_da_familia"]
    assert [item["formato"] for item in secoes["formatos"]] == ["post", "story", "banner"]
    assert all(item["peca"] is not None for item in secoes["formatos"])
    html = resposta.content.decode()
    assert "formato_da_peca=story" in html and "imagem=grupo" in html
    assert 'name="formato_da_peca" value="banner"' in html
    assert "foto de um grupo de estudantes" in html  # o alternativo traz a descrição (FR-3825)


def test_template_nao_liberado_aparece_indisponivel_e_os_outros_continuam(
    comunicacao, edital, settings
):
    _sem(settings, "banner")
    secoes = _tela(comunicacao, edital, familia=LATO).context["secoes_da_familia"]
    por_formato = {item["formato"]: item for item in secoes["formatos"]}
    assert por_formato["banner"]["peca"] is None
    assert por_formato["banner"]["motivo"] == kit_escolha.EM_APROVACAO
    assert por_formato["post"]["peca"] is not None


def test_versao_divergente_da_liberada_diz_versao_nova(comunicacao, edital, settings):
    settings.KIT_DE_DIVULGACAO_TEMPLATES = tuple(
        (f, formato, v, "0" * 12 if (f, formato) == (LATO, "story") else curto)
        for f, formato, v, curto in settings.KIT_DE_DIVULGACAO_TEMPLATES
    )
    secoes = _tela(comunicacao, edital, familia=LATO).context["secoes_da_familia"]
    story = next(item for item in secoes["formatos"] if item["formato"] == "story")
    assert story["motivo"] == kit_escolha.VERSAO_EM_APROVACAO


def test_escolha_fora_da_lista_na_tela_abre_com_a_pre_escolha_e_diz_por_que(comunicacao, edital):
    # Uma família que nenhum módulo registra: fora da lista fechada (EC-9).
    resposta = _tela(comunicacao, edital, familia="libras")
    assert resposta.status_code == 200
    assert resposta.context["escolha"].familia.chave == institucional.CHAVE
    assert kit_escolha.ESCOLHA_INDISPONIVEL in resposta.content.decode()


# ---- Prévia e exportação por formato (FR-3828, EC-9, EC-7) ----------------------------------


@sem_rasterizador
def test_previa_por_formato_e_404_fora_da_lista(comunicacao, edital, settings):
    resposta = _previa(comunicacao, edital, familia=LATO, imagem="fone", formato_da_peca="story")
    assert resposta.status_code == 200
    assert resposta["Content-Type"] == "image/png"
    for errado in (
        {"imagem": "praia", "formato_da_peca": "story"},
        {"imagem": "fone", "formato_da_peca": "reels"},
        {"familia": "fic", "imagem": "fone", "formato_da_peca": "post"},
    ):
        consulta = {"familia": LATO, **errado}
        assert _previa(comunicacao, edital, **consulta).status_code == 404
    _sem(settings, "post")
    assert (
        _previa(
            comunicacao, edital, familia=LATO, imagem="fone", formato_da_peca="post"
        ).status_code
        == 404
    )


def test_svg_da_familia_registra_a_escolha_e_o_template(comunicacao, edital):
    resposta = _exportar(comunicacao, edital, "svg", familia=LATO, imagem="biblioteca")
    assert resposta.status_code == 400  # sem formato da peça não há template: fora da lista
    resposta = _exportar(
        comunicacao, edital, "svg", familia=LATO, imagem="biblioteca", formato_da_peca="banner"
    )
    assert resposta.status_code == 200
    assert b'font-family="Poppins"' in resposta.content
    detalhe = _eventos(edital).get().detalhe
    template = pos_lato_sensu.BANNER
    assert detalhe["familia"] == LATO and detalhe["familia_versao"] == 1
    assert detalhe["imagem"] == "biblioteca"
    assert detalhe["imagem_sha256"] == pos_lato_sensu.IMAGENS[3].sha256("banner")
    assert detalhe["formato_da_peca"] == "banner"
    assert detalhe["template"] == "pos-lato-sensu/banner · 1"
    assert detalhe["template_versao"] == 1
    assert detalhe["template_resumo"] == kit_familias.resumo(template)


def test_envio_forjado_e_400_sem_registro(comunicacao, edital):
    for errado in (
        {"familia": "fic", "imagem": "fone", "formato_da_peca": "post"},
        {"familia": LATO, "imagem": "praia", "formato_da_peca": "post"},
        {"familia": LATO, "imagem": "fone", "formato_da_peca": "reels"},
        {"familia": LATO, "variante": "servidores", "imagem": "fone", "formato_da_peca": "post"},
    ):
        resposta = _exportar(comunicacao, edital, "svg", **errado)
        assert resposta.status_code == 400, errado
        assert kit_escolha.ESCOLHA_INDISPONIVEL in resposta.content.decode()
    assert not _eventos(edital).exists()


def test_template_desligado_depois_de_aberta_a_tela_e_409_sem_registro(
    comunicacao, edital, settings
):
    _sem(settings, "story")
    resposta = _exportar(
        comunicacao, edital, "svg", familia=LATO, imagem="fone", formato_da_peca="story"
    )
    assert resposta.status_code == 409
    assert kit_escolha.EM_APROVACAO in resposta.content.decode()
    assert not _eventos(edital).exists()


# ---- A pré-escolha (FR-3806, EC-8) e a desatualização (FR-3828) -----------------------------


def test_a_tela_reaberta_traz_a_escolha_da_ultima_exportacao(comunicacao, edital):
    _exportar(comunicacao, edital, "svg", familia=LATO, imagem="grupo", formato_da_peca="post")
    _exportar(comunicacao, edital, "md")  # texto não tem família, e não muda a pré-escolha
    resposta = _tela(comunicacao, edital)
    escolha = resposta.context["escolha"]
    assert (escolha.familia.chave, escolha.imagem) == (LATO, "grupo")
    assert not resposta.context["aviso_da_escolha"]
    # Trocar de família não é mudança do Edital: nenhuma faixa (FR-3828).
    assert resposta.context["desatualizadas"] == []


def test_imagem_retirada_do_banco_cai_na_primeira_e_diz_por_que(
    comunicacao, edital, monkeypatch, settings
):
    _exportar(comunicacao, edital, "svg", familia=LATO, imagem="fone", formato_da_peca="post")
    familia = kit_familias.familia(LATO)
    sem_a_primeira = dataclasses.replace(familia, imagens=familia.imagens[1:])
    monkeypatch.setitem(kit_familias.REGISTRO, LATO, sem_a_primeira)
    # O banco mudou, e com ele o resumo de cada template: a versão nova só vale liberada (FR-3835).
    settings.KIT_DE_DIVULGACAO_TEMPLATES = tuple(
        (LATO, t.formato.chave, t.versao, kit_familias.resumo(t)[:12])
        for t in sem_a_primeira.templates.values()
    )
    resposta = _tela(comunicacao, edital)
    escolha = resposta.context["escolha"]
    assert (escolha.familia.chave, escolha.imagem) == (LATO, "grupo")
    assert resposta.context["aviso_da_escolha"] == kit_escolha.IMAGEM_RETIRADA


# ---- O ZIP de família (FR-3829, D-015) ------------------------------------------------------


def _abrir(dados):
    with zipfile.ZipFile(io.BytesIO(dados)) as arquivo:
        return [info.filename for info in arquivo.infolist()], {
            info.filename: arquivo.read(info) for info in arquivo.infolist()
        }


@sem_rasterizador
def test_zip_da_familia_com_banner_nao_liberado(comunicacao, edital, settings):
    _sem(settings, "banner")
    resposta = _exportar(comunicacao, edital, "zip", familia=LATO, imagem="escrevendo")
    assert resposta.status_code == 200
    nomes, conteudo = _abrir(resposta.content)
    assert nomes == [
        "kit.md",
        "kit.txt",
        "peca-post.png",
        "peca-post.svg",
        "peca-post-alternativo.txt",
        "peca-story.png",
        "peca-story.svg",
        "peca-story-alternativo.txt",
        "ficha.json",
        "manifesto.json",
    ]
    manifesto = json.loads(conteudo["manifesto.json"])
    assert manifesto["versao_do_manifesto"] == 2
    assert manifesto["familia"] == {"chave": LATO, "versao": 1, "variante": None}
    assert manifesto["template"] is None and manifesto["peca"] is None
    pecas = manifesto["pecas"]
    assert [p["formato_da_peca"] for p in pecas] == ["post", "story", "banner"]
    assert [p["incluida"] for p in pecas] == [True, True, False]
    assert pecas[2]["motivo"] == "nao_liberado" and pecas[2]["arquivos"] == []
    assert [a["nome"] for a in pecas[0]["arquivos"]] == [
        "peca-post.png",
        "peca-post.svg",
        "peca-post-alternativo.txt",
    ]
    assert set(manifesto["fontes"]) == {"Poppins-Regular.ttf", "Poppins-Bold.ttf"}
    assert "escrevendo-post.jpg" in manifesto["ativos"]
    detalhe = _eventos(edital).get().detalhe
    assert detalhe["pecas"] == pecas
    assert detalhe["template"] is None and detalhe["manchete"] is None
    assert detalhe["sem_peca"] is None


def test_zip_da_familia_com_escolha_forjada_e_400(comunicacao, edital):
    resposta = _exportar(comunicacao, edital, "zip", familia=LATO, imagem="praia")
    assert resposta.status_code == 400
    assert not _eventos(edital).exists()


# ---- A revisão do incremento 2 --------------------------------------------------------------


def test_trocar_de_familia_no_formulario_nao_leva_a_imagem_da_anterior(comunicacao, edital):
    """FR-3806: sair da Pós para a Institucional pelo formulário, mesmo depois de exportar a Pós.

    O formulário leva a imagem marcada da família que está na tela; sem o `familia_da_tela`, a
    Institucional recebia uma imagem e a tela dizia "escolha indisponível", presa na Pós.
    """
    _exportar(comunicacao, edital, "svg", familia=LATO, imagem="grupo", formato_da_peca="post")
    resposta = _tela(
        comunicacao, edital, familia="institucional", familia_da_tela=LATO, imagem="grupo"
    )
    assert resposta.context["escolha"].familia.chave == "institucional"
    assert not resposta.context["aviso_da_escolha"]
    volta = _tela(comunicacao, edital, familia=LATO, familia_da_tela="institucional")
    assert (volta.context["escolha"].familia.chave, volta.context["escolha"].imagem) == (
        LATO,
        "fone",
    )
    # Na mesma família, a imagem fora da lista continua recusada (EC-9).
    forjada = _tela(comunicacao, edital, familia=LATO, familia_da_tela=LATO, imagem="praia")
    assert forjada.context["aviso_da_escolha"] == kit_escolha.ESCOLHA_INDISPONIVEL


def test_envio_forjado_com_a_institucional_e_recusado_sem_registro(comunicacao, edital):
    """EC-9: a Institucional não tem banco, variante nem outro formato."""
    for formato, errado in (
        ("svg", {"familia": "institucional", "formato_da_peca": "story"}),
        ("svg", {"imagem": "praia"}),
        ("png", {"familia": "institucional", "variante": "servidores"}),
        ("zip", {"familia": "institucional", "imagem": "fone"}),
    ):
        if formato == "png" and not kit_pacote.disponivel():
            continue
        resposta = _exportar(comunicacao, edital, formato, **errado)
        assert resposta.status_code == 400, (formato, errado)
    assert not _eventos(edital).exists()
    if kit_pacote.disponivel():
        assert _previa(comunicacao, edital, formato_da_peca="banner").status_code == 404


def test_institucional_fora_da_versao_congelada_so_sai_liberada(
    comunicacao, edital, monkeypatch, settings
):
    """FR-3835, EC-23: outro resumo da Institucional não sai pela chave da `111`."""
    monkeypatch.setattr(institucional, "RESUMO_CONGELADO_V1", "0" * 64)
    assert settings.KIT_DE_DIVULGACAO_PECA
    settings.KIT_DE_DIVULGACAO_TEMPLATES = tuple(
        e for e in settings.KIT_DE_DIVULGACAO_TEMPLATES if e[0] != "institucional"
    )
    resposta = _tela(comunicacao, edital, familia="institucional")
    assert resposta.context["secao_da_peca"]["motivo"] == kit_escolha.VERSAO_EM_APROVACAO
    assert _exportar(comunicacao, edital, "svg").status_code == 404
    zip_ = _exportar(comunicacao, edital, "zip")
    assert zip_.status_code == 200
    assert _eventos(edital).get().detalhe["sem_peca"] == kit_escolha.VERSAO_EM_APROVACAO
    curto = kit_familias.resumo(institucional.POST)[: kit_familias.RESUMO_CURTO]
    settings.KIT_DE_DIVULGACAO_TEMPLATES = (
        *settings.KIT_DE_DIVULGACAO_TEMPLATES,
        ("institucional", "post", 1, curto),
    )
    assert _exportar(comunicacao, edital, "svg").status_code == 200


def test_zip_da_institucional_registra_a_familia_e_vira_a_pre_escolha(comunicacao, edital):
    """FR-3828: o ZIP da Institucional também registra a família, e a tela reabre nela."""
    _exportar(comunicacao, edital, "svg", familia=LATO, imagem="grupo", formato_da_peca="post")
    assert _exportar(comunicacao, edital, "zip").status_code == 200
    detalhe = _eventos(edital).last().detalhe
    assert {k: detalhe[k] for k in ("familia", "familia_versao", "variante", "imagem")} == {
        "familia": "institucional",
        "familia_versao": institucional.FAMILIA.versao,
        "variante": None,
        "imagem": None,
    }
    assert _tela(comunicacao, edital).context["escolha"].familia.chave == "institucional"


def test_familia_que_saiu_da_lista_volta_a_institucional_e_diz_por_que(
    comunicacao, edital, settings
):
    """FR-3806, EC-8: a família anterior trocada tem o motivo dito, como a imagem."""
    _exportar(comunicacao, edital, "svg", familia=LATO, imagem="grupo", formato_da_peca="post")
    _sem(settings, "post", "story", "banner")
    resposta = _tela(comunicacao, edital)
    assert resposta.context["escolha"].familia.chave == "institucional"
    assert resposta.context["aviso_da_escolha"] == kit_escolha.FAMILIA_RETIRADA


@sem_rasterizador
def test_zip_da_familia_com_recusa_e_versao_divergente(comunicacao, edital, settings, monkeypatch):
    """FR-3829: cada motivo de não inclusão no manifesto, e os outros formatos seguem."""
    settings.KIT_DE_DIVULGACAO_TEMPLATES = tuple(
        (f, formato, versao, "0" * 12 if (f, formato) == (LATO, "banner") else curto)
        for f, formato, versao, curto in settings.KIT_DE_DIVULGACAO_TEMPLATES
    )
    original = kit_escolha.compor

    def recusa_o_story(ficha, escolhida, formato, *args):
        if formato == "story":
            raise kit_peca.PecaRecusada("O título não cabe no story.")
        return original(ficha, escolhida, formato, *args)

    monkeypatch.setattr(kit_escolha, "compor", recusa_o_story)
    resposta = _exportar(comunicacao, edital, "zip", familia=LATO, imagem="fone")
    assert resposta.status_code == 200
    pecas = json.loads(_abrir(resposta.content)[1]["manifesto.json"])["pecas"]
    assert [(p["formato_da_peca"], p["incluida"], p["motivo"]) for p in pecas] == [
        ("post", True, None),
        ("story", False, "recusa"),
        ("banner", False, "versao_divergente"),
    ]
    assert pecas[1]["recusa"] == "O título não cabe no story."


def test_zip_da_familia_sem_rasterizador_leva_o_svg(comunicacao, edital, monkeypatch):
    """FR-3829: sem o rasterizador, o formato entra com o SVG e o motivo `sem_rasterizador`."""
    monkeypatch.setattr(kit_pacote, "disponivel", lambda: False)
    resposta = _exportar(comunicacao, edital, "zip", familia=LATO, imagem="fone")
    assert resposta.status_code == 200
    nomes, conteudo = _abrir(resposta.content)
    assert "peca-post.svg" in nomes and "peca-post.png" not in nomes
    pecas = json.loads(conteudo["manifesto.json"])["pecas"]
    assert {p["motivo"] for p in pecas} == {"sem_rasterizador"}
    assert all(p["incluida"] for p in pecas)


def test_a_tela_diz_em_que_formatos_as_opcoes_sairam_resumidas(comunicacao, api_client):
    """FR-3836: os quatro polos do 91 saem resumidos no post e no story, e a tela o diz uma vez."""
    quatro = kit.publicar(api_client, chave="familias-quatro-polos")
    resposta = _tela(comunicacao, quatro, familia=LATO, familia_da_tela=LATO)
    secao = resposta.context["secoes_da_familia"]
    assert kit_peca.RESUMO_EM.format(formatos="post, story") in secao["avisos"]
    textos = dict((chave, texto) for chave, _, texto in resposta.context["textos"])
    assert textos["legenda"].count("480 horas") == 4  # as opções completas nos textos
