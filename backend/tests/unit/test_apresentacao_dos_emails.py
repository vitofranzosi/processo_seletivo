"""A apresentação das mensagens de e-mail: a moldura comum, o estilo em linha e o que o HTML diz.

**A regra que importa é a última**: o HTML não diz nada que o texto puro não diga. Ele acrescenta só
a identificação institucional do cabeçalho e o rótulo do botão — e o endereço do botão vem, por
extenso, logo abaixo dele. É o que permite melhorar a apresentação sem mexer no que a mensagem
comunica, e é a regra que a convocação já cumpria frase a frase (SC-1159 da `121`).

Sem banco: as composições recebem a identificação pronta, e nenhum caso aqui envia mensagem.
"""

import html as html_lib
import re
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

import pytest

from processo_seletivo.avisos.domain import mensagem as aviso
from processo_seletivo.avisos.domain import pendencia
from processo_seletivo.avisos.domain.modelos_iniciais import MODELOS_INICIAIS
from processo_seletivo.convocacao.application import comunicar
from processo_seletivo.convocacao.domain.mensagem import (
    CORRECAO,
    INICIAL,
    Citada,
    EscolhaDaMensagem,
)
from processo_seletivo.convocacao.domain.prazo_apresentado import apresentar
from processo_seletivo.identidade.application import mensagem as acesso
from processo_seletivo.identidade.models import DesafioDeAcesso
from processo_seletivo.inscricoes.application import mensagem as inscricao
from processo_seletivo.shared import correio
from processo_seletivo.unidades.application.identificacao import Identificacao

RAIZ = Path(__file__).resolve().parents[2] / "processo_seletivo"
FUSO = ZoneInfo("America/Sao_Paulo")
AGORA = datetime(2026, 11, 13, 10, 0, tzinfo=FUSO)
VENCIMENTO = datetime(2026, 11, 19, 17, 0, tzinfo=FUSO)
PORTAL = "https://selecoes.exemplo.test/selecoes/"
LINK = PORTAL + "inscricoes/7f3c0e2a-1b2c-4d5e-8f90-123456789abc/convocacao"
CANAL = "selecao@exemplo.test"
CEFOR = Identificacao(sigla="Cefor", atendimento=CANAL)
TITULO_LONGO = "Curso de Pós-Graduação Lato Sensu em Práticas Pedagógicas Inclusivas " * 3


# --- As mensagens, com dados fictícios ------------------------------------------------------------


def _comprovante(**trocas):
    return inscricao.compor_comprovante(
        {
            "protocolo": "2026-0042-7731",
            "verificacao": "K7Q2-9XPA",
            "selecao": "Especialização em Docência\nEdital 72/2026",
            "perfil": "Professores da rede pública",
            "modalidade": "Ampla concorrência",
            "quando": "13/11/2026 às 10:02",
            "documentos": [
                {"requisito": "Documento de identidade", "arquivo": "rg.pdf"},
                {"requisito": "Diploma", "arquivo": "diploma.pdf"},
            ],
            "endereco": PORTAL,
            "assinatura": "Cefor/Ifes",
            **trocas,
        }
    )


def _convocacao(
    variante="documento_e_requerimento",
    *,
    modelo=INICIAL,
    vencimento=VENCIMENTO,
    processo="Especialização em Docência",
    unidade="Cefor",
    assinatura="Cefor/Ifes",
):
    citada = (
        Citada(enviado_em=AGORA - timedelta(days=2), vencimento=VENCIMENTO - timedelta(days=3))
        if modelo == CORRECAO
        else None
    )
    html, assunto, texto = comunicar._renderizar(
        *comunicar._modelos(modelo),
        {
            "edital": "Edital 72/2026",
            "processo": processo,
            "vencimento": vencimento,
            "enviado_em": AGORA,
            "link": LINK,
            "escolha": EscolhaDaMensagem(modelo=modelo, variante=variante, citada=citada),
            "requerimento_exigido": True,
            "atendimento": CANAL,
            "assinatura": assinatura,
            "unidade": unidade,
        },
    )
    return correio.Mensagem(assunto, texto, html)


def _aviso(indice=0, origem="RESULTADO"):
    _, assunto, corpo = MODELOS_INICIAIS[indice]
    congelado = aviso.congelar(
        assunto=assunto,
        corpo=corpo,
        valores={
            "data_da_publicacao": "13/11/2026",
            "natureza_do_resultado": "preliminar",
            "etapa": "Análise documental",
            "perfil": "Perfil Professores",
            "edital": "Edital 72/2026",
            "area_do_candidato": PORTAL + "inscricoes/",
        },
        origem=origem,
        destino=PORTAL + "editais/72-2026/",
        atendimento=CANAL,
        assinatura="Cefor/Ifes",
    )
    assunto, texto = aviso.para_a_pessoa(
        assunto=congelado[0], corpo=congelado[1], nome_do_candidato="Maria"
    )
    return correio.Mensagem(assunto, texto, correio.html_do_aviso(assunto=assunto, corpo=texto))


def _pendencia(prazo=True):
    assunto, texto = pendencia.compor(
        instituicao="Ifes",
        edital="Edital 72/2026",
        pendentes=[pendencia.Pendente("Comprovante", False), pendencia.Pendente("Laudo", True)],
        prazo=apresentar(VENCIMENTO, AGORA, FUSO) if prazo else None,
        link=LINK,
        atendimento=CANAL,
        assinatura="Cefor/Ifes",
    )
    assunto, texto = aviso.para_a_pessoa(assunto=assunto, corpo=texto, nome_do_candidato="Maria")
    return correio.Mensagem(
        assunto, texto, correio.html_do_aviso(assunto=assunto, corpo=texto, estado="pendencia")
    )


MENSAGENS = {
    "codigo": lambda: acesso.compor_codigo(codigo="482913", identificacao_da_implantacao=CEFOR),
    "codigo-so-o-ifes": lambda: acesso.compor_codigo(
        codigo="482913", identificacao_da_implantacao=Identificacao()
    ),
    "vinculo": lambda: acesso.compor_codigo(
        codigo="482913",
        identificacao_da_implantacao=CEFOR,
        finalidade=DesafioDeAcesso.Finalidade.ADICIONAR_CREDENCIAL,
    ),
    "mudanca": lambda: acesso.compor_mudanca(
        endereco="outra@exemplo.test",
        acao="adicionado",
        atendimento=CANAL,
        identificacao_da_implantacao=CEFOR,
    ),
    "comprovante": _comprovante,
    "comprovante-sem-documento-titulo-longo": lambda: _comprovante(
        documentos=[], selecao=f"{TITULO_LONGO}\nEdital 105/2026"
    ),
    "convocacao": _convocacao,
    "convocacao-sem-prazo-sem-unidade": lambda: _convocacao(
        "nenhum", vencimento=None, processo=TITULO_LONGO, unidade="", assinatura="Ifes"
    ),
    "correcao": lambda: _convocacao("so_documento", modelo=CORRECAO),
    "aviso-resultado": _aviso,
    "aviso-chamada": lambda: _aviso(2, origem="CHAMADA"),
    "pendencia": _pendencia,
    "pendencia-sem-prazo": lambda: _pendencia(prazo=False),
}

ROTULOS_DE_BOTAO = {
    "Rever minha inscrição",
    "Acessar minha convocação",
    *correio.ROTULOS_DAS_ROTAS.values(),
}


def normalizar(texto):
    return " ".join(html_lib.unescape(texto).split())


def trechos_visiveis(html):
    """Cada trecho de texto entre marcas do corpo, sem o preheader, o cabeçalho e os botões."""
    corpo = re.search(r"<body>(.*)</body>", html, re.S).group(1)
    corpo = re.sub(r"<!--.*?-->", " ", corpo, flags=re.S)
    for trecho in re.split(r"<[^>]+>", corpo):
        trecho = normalizar(trecho)
        if trecho:
            yield trecho


# --- O HTML não diz nada que o texto não diga -----------------------------------------------------


@pytest.mark.parametrize("nome", MENSAGENS)
def test_o_html_nao_diz_nada_que_o_texto_nao_diga(nome):
    mensagem = MENSAGENS[nome]()
    texto = normalizar(mensagem.assunto + " " + mensagem.texto)
    moldura = {"Instituto Federal do Espírito Santo", "Seleções", "Cefor · Seleções"}

    sobrando = [
        trecho
        for trecho in trechos_visiveis(mensagem.html)
        if trecho not in texto and trecho not in moldura and trecho not in ROTULOS_DE_BOTAO
    ]

    assert sobrando == [], f"{nome}: o HTML diz o que o texto não diz"


@pytest.mark.parametrize("nome", MENSAGENS)
def test_a_mensagem_e_de_e_mail_e_nao_de_pagina(nome):
    """Estilo em linha, sem classe sobrando, sem script, imagem, folha ou fonte de fora."""
    html = MENSAGENS[nome]().html

    assert "class=" not in html, "classe que o cliente de e-mail ignoraria"
    assert 'style="' in html
    for proibido in ("<script", "<style", "<link", "<img", "src=", "@import", "javascript:"):
        assert proibido not in html.lower(), proibido
    assert '<meta name="viewport"' in html and 'lang="pt-BR"' in html
    assert "max-width:600px" in html, "o cartão é fluido até 600 px"
    assert '<!--[if mso]><table role="presentation" width="600"' in html


@pytest.mark.parametrize("nome", MENSAGENS)
def test_todo_endereco_e_do_portal_ou_o_canal(nome):
    """Nenhum rastreio, nenhum serviço de terceiro: só o portal, e o canal da comissão."""
    mensagem = MENSAGENS[nome]()
    for endereco in re.findall(r'href="([^"]+)"', mensagem.html):
        assert endereco.startswith(PORTAL) or endereco == f"mailto:{CANAL}", endereco
        assert endereco.replace("&amp;", "&") in mensagem.texto or endereco.startswith("mailto:")


@pytest.mark.parametrize("nome", MENSAGENS)
def test_o_texto_puro_termina_na_assinatura(nome):
    texto = MENSAGENS[nome]().texto
    assert texto.rstrip().endswith(
        "Esta mensagem é automática; não responda."
    ) or texto.rstrip().endswith(
        "Você a recebe porque foi convocado num processo seletivo em que se inscreveu."
    )


@pytest.mark.parametrize("nome", ["codigo", "codigo-so-o-ifes", "vinculo"])
def test_o_codigo_nao_leva_link_nem_vai_ao_preheader(nome):
    """P-001 da `010`: nenhum link autentica; e o código não aparece na notificação do celular."""
    mensagem = MENSAGENS[nome]()
    assert "href=" not in mensagem.html
    assert "http" not in mensagem.html + mensagem.texto
    preheader = re.search(r'<div style="display:none[^"]*">(.*?)</div>', mensagem.html, re.S)
    assert preheader and "482913" not in preheader.group(1)
    assert re.search(r"\b(\d{6})\b", mensagem.texto).group(1) == "482913"


def test_a_implantacao_com_varias_unidades_nao_escolhe_uma():
    mensagem = MENSAGENS["codigo-so-o-ifes"]()
    assert mensagem.assunto == "Seu código de acesso — Seleções Ifes"
    assert "Cefor" not in mensagem.html + mensagem.texto
    assert "\nIfes — Seleções\n" in mensagem.texto


def test_o_comprovante_escapa_o_que_a_pessoa_escreveu():
    """O nome do arquivo é da pessoa: no HTML ele é texto, e nunca marcação."""
    mensagem = _comprovante(
        documentos=[{"requisito": "RG", "arquivo": '<img src=x onerror=alert(1)> "a".pdf'}]
    )
    assert "<img" not in mensagem.html
    assert "&lt;img src=x onerror=alert(1)&gt;" in mensagem.html
    assert '<img src=x onerror=alert(1)> "a".pdf' in mensagem.texto


def test_o_comprovante_nao_leva_cpf_nem_telefone_e_guarda_o_que_os_testes_guardam():
    texto = _comprovante().texto
    for frase in (
        "Código de verificação:",
        "Perfil de vaga:",
        "não implica deferimento",
        "código de acesso a cada entrada",
    ):
        assert frase in texto
    assert "CPF" not in texto


def test_a_convocacao_tem_um_endereco_so_e_o_prazo_no_preheader():
    mensagem = _convocacao()
    assert re.findall(r'href="([^"]+)"', mensagem.html) == [LINK]
    preheader = re.search(r'<div style="display:none[^"]*">(.*?)</div>', mensagem.html, re.S)
    assert normalizar(preheader.group(1)) in normalizar(mensagem.texto)
    assert "19/11/2026" in preheader.group(1)


# --- O aviso: o texto congelado em blocos ---------------------------------------------------------


def test_o_aviso_da_pendencia_vira_lista_botao_e_nota():
    mensagem = _pendencia()
    assert "<ul" in mensagem.html and mensagem.html.count("<li") == 2
    assert ">Abrir minha convocação</a>" in mensagem.html
    assert re.findall(r'href="([^"]+)"', mensagem.html)[0] == LINK
    nota = "Este aviso não é a convocação e não altera o seu prazo."
    assert nota in mensagem.html
    assert "Cefor/Ifes — Seleções" in mensagem.html
    assert correio.ESTADOS["pendencia"][1] in mensagem.html


def test_o_endereco_fora_do_portal_nao_vira_botao():
    blocos = correio.blocos_do_aviso("Veja o Edital em https://www.ifes.edu.br/editais")["blocos"]
    assert [bloco.tipo for bloco in blocos] == ["texto"]


def test_o_endereco_no_meio_da_frase_nao_vira_botao():
    blocos = correio.blocos_do_aviso(f"Acesse {PORTAL}inscricoes/ e confira a situação.")
    assert [bloco.tipo for bloco in blocos["blocos"]] == ["texto"]


def test_o_texto_sem_rodape_nao_ganha_rodape():
    partes = correio.blocos_do_aviso("Olá.\n\nUm aviso sem a linha do rodapé.")
    assert partes["nota"] == [] and partes["assinatura"] == []
    assert len(partes["blocos"]) == 2


def test_o_rodape_do_aviso_de_resultado_fica_num_quadro():
    mensagem = _aviso()
    assert "Este aviso não substitui a publicação." in mensagem.html
    assert correio.ESTADOS["informacao"][1] in mensagem.html
    assert ">Entrar na área do candidato</a>" in mensagem.html


def test_o_preheader_pula_a_saudacao():
    blocos = correio.blocos_do_aviso(_aviso().texto)["blocos"]
    assert correio.resumo_para_o_preheader(blocos).startswith("Foi publicado em 13/11/2026")


@pytest.mark.parametrize(
    ("assinatura", "unidade"),
    [("Cefor/Ifes — Seleções", "Cefor"), ("Ifes — Seleções", ""), ("", "")],
)
def test_a_unidade_do_cabecalho_vem_da_assinatura(assinatura, unidade):
    assert correio.unidade_da_assinatura(assinatura) == unidade


# --- O estilo em linha ----------------------------------------------------------------------------


def test_classe_sem_estilo_e_erro_e_nao_silencio():
    with pytest.raises(ValueError, match="classe sem estilo"):
        correio.estilizar('<p class="texto inventada">x</p>')


def test_a_classe_vira_estilo_na_ordem_e_o_texto_escapado_fica_como_esta():
    saida = correio.estilizar('<p class="texto fim">a class=&quot;texto&quot; b</p>')
    assert saida.startswith('<p style="' + correio.ESTILOS["texto"] + correio.ESTILOS["fim"])
    assert "a class=&quot;texto&quot; b" in saida


def test_todo_estado_tem_destaque_com_contraste_de_borda():
    for estado in correio.ESTADOS:
        assert f"destaque-{estado}" in correio.ESTILOS


MODELOS_DE_MENSAGEM = sorted(
    [
        *RAIZ.glob("*/templates/*/mensagem/*.html"),
        *RAIZ.glob("shared/templates/correio/*.html"),
    ]
)


@pytest.mark.parametrize("modelo", MODELOS_DE_MENSAGEM, ids=lambda p: p.name)
def test_toda_classe_dos_modelos_tem_estilo(modelo):
    """O par da regra da gestão — classe citada exige regra na folha —, para o e-mail."""
    fonte = re.sub(r"\{% comment %\}.*?\{% endcomment %\}", "", modelo.read_text(), flags=re.S)
    for atributo in re.findall(r'\sclass="([^"]*)"', fonte):
        for classe in re.sub(r"\{\{.*?\}\}|\{%.*?%\}", " ", atributo).split():
            if classe.endswith("-"):
                continue  # "destaque-{{ estado }}": o estado é conferido acima
            assert classe in correio.ESTILOS, f"{modelo.name}: {classe}"


def test_os_modelos_cobrem_as_cinco_situacoes():
    nomes = {modelo.name for modelo in MODELOS_DE_MENSAGEM}
    assert {"codigo.html", "vinculo.html", "mudanca.html", "comprovante.html"} <= nomes
    assert {"inicial.html", "correcao.html", "aviso.html", "base.html"} <= nomes
