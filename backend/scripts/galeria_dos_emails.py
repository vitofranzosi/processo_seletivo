"""A galeria das mensagens de e-mail do GPS: cada situação de envio, com dados fictícios.

Rode de `backend/`, sem banco nenhum — as composições são puras, e o script não envia nada:

    uv run python scripts/galeria_dos_emails.py --saida ../doc/galeria-dos-emails/depois

Grava, por mensagem, o HTML (`.html`), o texto puro com o assunto (`.txt`) e a mensagem inteira
(`.eml`), que abre num cliente de e-mail de verdade — Apple Mail, Outlook, Thunderbird — sem que
nada seja enviado. E um `index.html` com as prévias lado a lado, em 600 e em 375 px.

**Os casos-limite estão aqui de propósito**: título longo, campo opcional ausente, muitos
documentos, sem vencimento, implantação com várias unidades. Uma moldura que só funciona com o
caso feliz não é moldura.
"""

import argparse
import html as html_lib
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.test")

import django  # noqa: E402

django.setup()

from django.core.mail import EmailMultiAlternatives  # noqa: E402

from processo_seletivo.avisos.domain import mensagem as aviso  # noqa: E402
from processo_seletivo.avisos.domain import pendencia  # noqa: E402
from processo_seletivo.avisos.domain.modelos_iniciais import MODELOS_INICIAIS  # noqa: E402
from processo_seletivo.convocacao.application import comunicar  # noqa: E402
from processo_seletivo.convocacao.domain.mensagem import (  # noqa: E402
    CORRECAO,
    INICIAL,
    Citada,
    EscolhaDaMensagem,
)
from processo_seletivo.convocacao.domain.prazo_apresentado import apresentar  # noqa: E402
from processo_seletivo.identidade.application import mensagem as acesso  # noqa: E402
from processo_seletivo.identidade.models import DesafioDeAcesso  # noqa: E402
from processo_seletivo.inscricoes.application import mensagem as inscricao  # noqa: E402
from processo_seletivo.shared import correio  # noqa: E402
from processo_seletivo.unidades.application.identificacao import Identificacao  # noqa: E402

FUSO = ZoneInfo("America/Sao_Paulo")
AGORA = datetime(2026, 11, 13, 10, 0, tzinfo=FUSO)
VENCIMENTO = datetime(2026, 11, 19, 17, 0, tzinfo=FUSO)
PORTAL = "https://selecoes.ifes.edu.br/selecoes/"
LINK = PORTAL + "inscricoes/7f3c0e2a-1b2c-4d5e-8f90-123456789abc/convocacao"
CANAL = "selecao@cefor.ifes.edu.br"
CEFOR = Identificacao(sigla="Cefor", atendimento=CANAL)
SO_O_IFES = Identificacao()
PROCESSO = "Especialização em Docência para a Educação Profissional"
PROCESSO_LONGO = (
    "Curso de Pós-Graduação Lato Sensu em Práticas Pedagógicas Inclusivas na Educação "
    "Profissional, Científica e Tecnológica, na modalidade a distância, com polos em Vitória, "
    "Colatina e Cachoeiro de Itapemirim"
)


def _convocacao(
    variante,
    *,
    modelo=INICIAL,
    citada=None,
    vencimento=VENCIMENTO,
    processo=PROCESSO,
    requerimento=True,
    unidade="Cefor",
    assinatura="Cefor/Ifes",
    edital="72/2026",
):
    html, assunto, texto = comunicar._renderizar(
        *comunicar._modelos(modelo),
        {
            "edital": f"Edital {edital}",
            "processo": processo,
            "vencimento": vencimento,
            "enviado_em": AGORA,
            "link": LINK,
            "escolha": EscolhaDaMensagem(modelo=modelo, variante=variante, citada=citada),
            "requerimento_exigido": requerimento,
            "atendimento": CANAL,
            "assinatura": assinatura,
            "unidade": unidade,
        },
    )
    return correio.Mensagem(assunto=assunto, texto=texto, html=html)


def _comprovante(**trocas):
    dados = {
        "protocolo": "2026-0042-7731",
        "verificacao": "K7Q2-9XPA",
        "selecao": f"{PROCESSO}\nEdital 72/2026",
        "perfil": "Professores da rede pública",
        "modalidade": "Ampla concorrência",
        "quando": "13/11/2026 às 10:02",
        "documentos": [
            {"requisito": "Documento de identidade", "arquivo": "rg-maria.pdf"},
            {"requisito": "Diploma de graduação", "arquivo": "diploma.pdf"},
        ],
        "endereco": PORTAL,
        "assinatura": "Cefor/Ifes",
        **trocas,
    }
    return inscricao.compor_comprovante(dados)


def _aviso_066(indice, *, origem="RESULTADO", nome="Maria da Silva", destino=None):
    _, assunto, corpo = MODELOS_INICIAIS[indice]
    valores = {
        "data_da_publicacao": "13/11/2026",
        "natureza_do_resultado": "preliminar",
        "etapa": "Análise documental",
        "perfil": "Perfil Professores da rede pública",
        "edital": "Edital 72/2026",
        "area_do_candidato": PORTAL + "inscricoes/",
    }
    congelado = aviso.congelar(
        assunto=assunto,
        corpo=corpo,
        valores=valores,
        origem=origem,
        destino=destino or PORTAL + "editais/72-2026/",
        atendimento=CANAL,
        assinatura="Cefor/Ifes",
    )
    assunto, texto = aviso.para_a_pessoa(
        assunto=congelado[0], corpo=congelado[1], nome_do_candidato=nome
    )
    return correio.Mensagem(assunto, texto, correio.html_do_aviso(assunto=assunto, corpo=texto))


def _pendencia(pendentes, *, prazo=True):
    assunto, texto = pendencia.compor(
        instituicao="Ifes",
        edital="Edital 72/2026",
        pendentes=pendentes,
        prazo=apresentar(VENCIMENTO, AGORA, FUSO) if prazo else None,
        link=LINK,
        atendimento=CANAL,
        assinatura="Cefor/Ifes",
    )
    assunto, texto = aviso.para_a_pessoa(assunto=assunto, corpo=texto, nome_do_candidato="Maria")
    return correio.Mensagem(
        assunto, texto, correio.html_do_aviso(assunto=assunto, corpo=texto, estado="pendencia")
    )


P = pendencia.Pendente

#: (arquivo, nome, destinatário, gatilho, estado, antes, mensagem)
CATALOGO = [
    (
        "01-codigo",
        "Código de acesso",
        "Candidato",
        "Pede para entrar no portal",
        "Informação",
        "01-codigo",
        lambda: acesso.compor_codigo(codigo="482913", identificacao_da_implantacao=CEFOR),
    ),
    (
        "01b-codigo-varias-unidades",
        "Código de acesso — implantação com várias unidades",
        "Candidato",
        "Idem, com mais de uma unidade ativa",
        "Informação",
        None,
        lambda: acesso.compor_codigo(codigo="482913", identificacao_da_implantacao=SO_O_IFES),
    ),
    (
        "02-vinculo",
        "Código para acrescentar e-mail à conta",
        "Dono do e-mail informado",
        "Acrescenta outro e-mail à conta",
        "Ação",
        "02-vinculo",
        lambda: acesso.compor_codigo(
            codigo="482913",
            identificacao_da_implantacao=CEFOR,
            finalidade=DesafioDeAcesso.Finalidade.ADICIONAR_CREDENCIAL,
        ),
    ),
    (
        "03-mudanca",
        "Mudança no acesso à conta",
        "E-mail principal da conta",
        "E-mail acrescentado ou removido",
        "Informação",
        "03-mudanca",
        lambda: acesso.compor_mudanca(
            endereco="maria.trabalho@exemplo.test",
            acao="adicionado",
            atendimento=CANAL,
            identificacao_da_implantacao=CEFOR,
        ),
    ),
    (
        "04-inscricao",
        "Confirmação de inscrição",
        "Candidato",
        "Envia a inscrição",
        "Confirmação",
        "04-inscricao",
        _comprovante,
    ),
    (
        "04b-inscricao-sem-documentos-e-longa",
        "Confirmação — título longo, sem documento",
        "Candidato",
        "Idem",
        "Confirmação",
        None,
        lambda: _comprovante(selecao=f"{PROCESSO_LONGO}\nEdital 105/2026", documentos=[]),
    ),
    (
        "04c-inscricao-muitos-documentos",
        "Confirmação — muitos documentos",
        "Candidato",
        "Idem",
        "Confirmação",
        None,
        lambda: _comprovante(
            documentos=[
                {"requisito": r, "arquivo": a}
                for r, a in [
                    ("Documento de identidade", "rg.pdf"),
                    ("Diploma de graduação", "diploma-licenciatura-em-matematica-ufes-2019.pdf"),
                    ("Histórico escolar", "historico.pdf"),
                    ("Comprovante de residência", "conta-de-luz-outubro.pdf"),
                    ("Declaração de vínculo com a rede pública", "declaracao-sedu.pdf"),
                    ("Currículo Lattes", "lattes.pdf"),
                ]
            ]
        ),
    ),
    (
        "05-convocacao",
        "Convocação — documentos e Requerimento",
        "Candidato convocado",
        "Comissão comunica a convocação (Edital por mensagem)",
        "Ação + prazo",
        "05-convocacao",
        lambda: _convocacao("documento_e_requerimento"),
    ),
    (
        "05b-convocacao-sem-prazo-titulo-longo",
        "Convocação — sem vencimento, título longo",
        "Candidato convocado",
        "Idem",
        "Ação",
        None,
        lambda: _convocacao("nenhum", vencimento=None, processo=PROCESSO_LONGO, requerimento=False),
    ),
    (
        "05c-convocacao-so-requerimento-varias-unidades",
        "Convocação — só o Requerimento, sem unidade no cabeçalho",
        "Candidato convocado",
        "Idem",
        "Ação + prazo",
        None,
        lambda: _convocacao("so_requerimento", unidade="", assinatura="Ifes"),
    ),
    (
        "06-correcao",
        "Correção da convocação",
        "Candidato convocado",
        "Convocação corrigida e comunicada de novo",
        "Ação + prazo",
        "06-correcao",
        lambda: _convocacao(
            "so_documento",
            modelo=CORRECAO,
            citada=Citada(
                enviado_em=AGORA - timedelta(days=2),
                vencimento=datetime(2026, 11, 16, 17, 0, tzinfo=FUSO),
            ),
        ),
    ),
    (
        "07-aviso-resultado",
        "Aviso complementar — resultado",
        "Candidatos da publicação",
        "Operador confirma o aviso; o despacho envia",
        "Informação",
        "07-aviso-resultado",
        lambda: _aviso_066(0),
    ),
    (
        "07b-aviso-chamada",
        "Aviso complementar — nova chamada",
        "Convocados da publicação",
        "Idem, na chamada por publicação",
        "Informação",
        None,
        lambda: _aviso_066(2, origem="CHAMADA"),
    ),
    (
        "08-pendencia",
        "Aviso de pendência documental",
        "Convocado com documento a revisar",
        "Quem confere pede o aviso; o despacho envia",
        "Pendência",
        "08-pendencia",
        lambda: _pendencia([P("Comprovante de residência", False), P("Laudo", True)]),
    ),
    (
        "08b-pendencia-um-documento-sem-prazo",
        "Pendência — um documento, sem vencimento",
        "Idem",
        "Idem",
        "Pendência",
        None,
        lambda: _pendencia([P("Histórico escolar", False)], prazo=False),
    ),
]


def _eml(mensagem):
    email = EmailMultiAlternatives(
        subject=mensagem.assunto,
        body=mensagem.texto,
        from_email="Seleções Ifes <nao-responda@exemplo.test>",
        to=["maria@exemplo.test"],
        headers=dict(correio.CABECALHOS),
    )
    email.attach_alternative(mensagem.html, "text/html")
    return email.message().as_bytes()


def _cartao(arquivo, nome, quem, gatilho, estado, antes, mensagem):
    e = html_lib.escape
    antes_html = ""
    if antes:
        antes_html = (
            f'<details><summary>Antes</summary><p><a href="../antes/{antes}.txt">texto</a>'
            + (
                f' · <a href="../antes/{antes}.html">HTML</a>'
                if antes.startswith("0") and antes[:2] in ("05", "06")
                else ""
            )
            + "</p></details>"
        )
    return f"""
<section id="{arquivo}">
  <h2>{e(nome)}</h2>
  <p class="meta"><b>Para:</b> {e(quem)} · <b>Quando:</b> {e(gatilho)} ·
     <b>Estado:</b> {e(estado)}</p>
  <p class="meta"><b>Assunto:</b> {e(mensagem.assunto)}</p>
  <p class="meta"><a href="{arquivo}.html">HTML</a> · <a href="{arquivo}.txt">texto puro</a> ·
     <a href="{arquivo}.eml">.eml</a> · <a href="{arquivo}-600.png">captura 600</a> ·
     <a href="{arquivo}-375.png">captura 375</a></p>
  {antes_html}
  <div class="previas">
    <figure><figcaption>Computador, 600 px</figcaption>
      <iframe src="{arquivo}.html" width="640" height="900"
        title="{e(nome)} em 600 px"></iframe></figure>
    <figure><figcaption>Celular, 375 px</figcaption>
      <iframe src="{arquivo}.html" width="375" height="900"
        title="{e(nome)} em 375 px"></iframe></figure>
  </div>
</section>"""


INDICE = """<!doctype html>
<html lang="pt-BR"><head><meta charset="utf-8"><title>Galeria dos e-mails do GPS</title>
<style>
body{{font-family:system-ui,sans-serif;margin:24px;color:#1c1c1c;background:#fafafa}}
section{{border-top:1px solid #ddd;padding:16px 0}} .meta{{margin:4px 0;font-size:14px;color:#444}}
.previas{{display:flex;gap:24px;flex-wrap:wrap;align-items:flex-start}}
iframe{{border:1px solid #ccc;background:#fff}} figcaption{{font-size:13px;color:#555}}
</style></head><body>
<h1>Galeria dos e-mails do GPS</h1>
<p>Dados fictícios. Gerada por <code>backend/scripts/galeria_dos_emails.py</code>; nada foi enviado.
Os <code>.eml</code> abrem num cliente de e-mail de verdade.</p>
{cartoes}
</body></html>"""


def main():
    argumentos = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    argumentos.add_argument("--saida", required=True, type=Path)
    saida = argumentos.parse_args().saida
    saida.mkdir(parents=True, exist_ok=True)
    cartoes = []
    for arquivo, nome, quem, gatilho, estado, antes, compor in CATALOGO:
        mensagem = compor()
        (saida / f"{arquivo}.html").write_text(mensagem.html, encoding="utf-8")
        (saida / f"{arquivo}.txt").write_text(
            f"Assunto: {mensagem.assunto}\n\n{mensagem.texto}", encoding="utf-8"
        )
        (saida / f"{arquivo}.eml").write_bytes(_eml(mensagem))
        cartoes.append(_cartao(arquivo, nome, quem, gatilho, estado, antes, mensagem))
    (saida / "index.html").write_text(INDICE.format(cartoes="".join(cartoes)), encoding="utf-8")
    print(f"{len(CATALOGO)} mensagens em {saida}")


if __name__ == "__main__":
    main()
