"""A apresentação das mensagens de e-mail: os tokens, o estilo em linha e a composição das partes.

**Só apresentação.** Este módulo não envia, não decide destinatário nem texto: quem envia continua
sendo um dos remetentes declarados em `tests/test_situacoes_de_mensagem.py`, e o que cada mensagem
diz continua no modelo dela. Aqui mora o que todas têm em comum — a moldura institucional, a
paleta e a regra de que o HTML não diz nada que o texto puro não diga.

**Classe no modelo, `style` na mensagem.** Cliente de e-mail não lê folha de estilo com confiança: o
Gmail descarta o `<style>` em várias contas e o Outlook ignora metade do CSS. O que sobrevive é o
atributo `style` em cada elemento. Os modelos, porém, são varridos pela guarda da política de
conteúdo (`tests/interface/test_politica_de_conteudo.py`), que recusa `style=""` em todo `.html` do
repositório — e com razão, para as páginas. Em vez de abrir exceção na guarda, os modelos de
mensagem escrevem `class="..."`, e `estilizar` troca cada classe pela declaração dela **depois** de
renderizar. Os tokens moram num lugar só (`ESTILOS`), e uma classe sem regra é erro, não silêncio.

**Sem imagem e sem endereço externo.** A identificação é texto: imagem bloqueada por padrão vira um
retângulo vazio no topo da mensagem, e uma logomarca hospedada seria o único endereço da mensagem
que não é do GPS (FR-3886 da `121`). Nenhum recurso é carregado de fora.
"""

import re
from dataclasses import dataclass
from urllib.parse import urlparse

from django.template.loader import get_template
from django.urls import Resolver404, resolve

# --- Os tokens -----------------------------------------------------------------------------------
# Os da folha comum (`shared/static/shared/tokens.css`), copiados porque o e-mail não lê folha: o
# verde que preenche, o que escreve sobre fundo claro, e os fundos de estado. Os contrastes contra
# o branco são os do portal — todos acima de 4,5:1.

VERDE = "#15803d"
VERDE_TEXTO = "#146c37"
VERDE_ESCURO = "#0b5a2a"
VERDE_CLARO = "#e7f5ec"
AMBAR = "#8a5300"
AMBAR_FUNDO = "#fdf5e5"
ARDOSIA = "#4b5563"
ARDOSIA_FUNDO = "#f3f4f6"
TEXTO = "#1c1c1c"
TEXTO_FRACO = "#555555"
BORDA = "#d4d4d4"
FUNDO = "#f3f4f2"
BRANCO = "#ffffff"

FONTE = "'Segoe UI',Roboto,'Helvetica Neue',Arial,sans-serif"
MONO = "Consolas,'Courier New',monospace"

# **Seis estados, e a diferença é discreta**: a cor da borda e do fundo do quadro de destaque. Quem
# diz o estado é o título, e não a cor — ninguém precisa distinguir verde de âmbar para entender a
# mensagem. O desfavorável é ardósia, e não vermelho: um resultado ruim pede cuidado, não alarme.
ESTADOS = {
    "informacao": (VERDE_ESCURO, "#f1f5f2"),
    "acao": (VERDE, VERDE_CLARO),
    "prazo": (AMBAR, AMBAR_FUNDO),
    "confirmacao": (VERDE_TEXTO, VERDE_CLARO),
    "pendencia": (AMBAR, AMBAR_FUNDO),
    "desfavoravel": (ARDOSIA, ARDOSIA_FUNDO),
}

_TEXTO_BASE = f"font-family:{FONTE};color:{TEXTO};"

ESTILOS = {
    # A moldura.
    "fundo": f"background-color:{FUNDO};",
    "moldura": "padding:24px 12px;",
    "cartao": (
        f"width:100%;max-width:600px;background-color:{BRANCO};border:1px solid {BORDA};"
        "border-radius:6px;border-collapse:separate;"
    ),
    "faixa": f"background-color:{VERDE_ESCURO};height:6px;line-height:6px;font-size:0;",
    "cabecalho": f"padding:20px 28px 16px 28px;border-bottom:1px solid {BORDA};",
    "marca": f"{_TEXTO_BASE}margin:0;font-size:15px;line-height:20px;font-weight:700;",
    "unidade": f"font-family:{FONTE};margin:2px 0 0 0;font-size:13px;color:{TEXTO_FRACO};",
    "conteudo": "padding:28px 28px 8px 28px;",
    "rodape": f"padding:20px 28px 24px 28px;border-top:1px solid {BORDA};",
    "preheader": (
        "display:none;max-height:0;overflow:hidden;mso-hide:all;font-size:1px;line-height:1px;"
        f"color:{FUNDO};opacity:0;"
    ),
    # O texto.
    "titulo": (f"{_TEXTO_BASE}margin:0 0 12px 0;font-size:22px;line-height:30px;font-weight:700;"),
    "subtitulo": f"{_TEXTO_BASE}margin:0 0 20px 0;font-size:15px;line-height:22px;",
    "texto": f"{_TEXTO_BASE}margin:0 0 16px 0;font-size:16px;line-height:24px;",
    "fraco": f"font-family:{FONTE};margin:0 0 12px 0;font-size:14px;line-height:21px;"
    f"color:{TEXTO_FRACO};",
    "rotulo": (
        f"font-family:{FONTE};margin:0 0 4px 0;font-size:13px;line-height:18px;"
        f"color:{TEXTO_FRACO};text-transform:uppercase;letter-spacing:.04em;font-weight:600;"
    ),
    "forte": "font-weight:700;",
    # Modificadores: vêm depois da classe principal e ganham dela — a declaração posterior vale.
    "espaco": "margin-top:14px;",
    "fim": "margin-bottom:0;",
    "lista": f"{_TEXTO_BASE}margin:0 0 16px 0;padding:0 0 0 22px;font-size:16px;line-height:24px;",
    "item": "margin:0 0 6px 0;",
    # O destaque: o código, o prazo, o protocolo, o quadro de segurança.
    "quadro": "width:100%;margin:0 0 20px 0;border-collapse:separate;",
    "codigo": (
        f"font-family:{MONO};margin:0;font-size:34px;line-height:44px;font-weight:700;"
        f"letter-spacing:8px;color:{TEXTO};"
    ),
    "prazo": f"{_TEXTO_BASE}margin:0;font-size:18px;line-height:26px;font-weight:700;",
    "dados": "width:100%;margin:0 0 20px 0;border-collapse:collapse;",
    "dado-rotulo": (
        f"font-family:{FONTE};padding:8px 12px 8px 0;font-size:14px;line-height:20px;"
        f"color:{TEXTO_FRACO};border-bottom:1px solid {BORDA};vertical-align:top;width:38%;"
    ),
    "dado-valor": (
        f"{_TEXTO_BASE}padding:8px 0;font-size:15px;line-height:21px;"
        f"border-bottom:1px solid {BORDA};vertical-align:top;"
    ),
    # A ação: um botão só, e o endereço por extenso abaixo dele.
    "acao": "margin:4px 0 8px 0;border-collapse:separate;",
    "botao-celula": f"background-color:{VERDE};border-radius:6px;",
    "botao": (
        f"display:inline-block;padding:14px 26px;font-family:{FONTE};font-size:16px;"
        f"line-height:20px;font-weight:700;color:{BRANCO};text-decoration:none;border-radius:6px;"
    ),
    "endereco": (
        f"font-family:{FONTE};margin:0 0 20px 0;font-size:13px;line-height:19px;"
        f"color:{TEXTO_FRACO};word-break:break-all;"
    ),
    "seguranca": (
        f"width:100%;margin:8px 0 20px 0;border:1px solid {BORDA};border-radius:6px;"
        "border-collapse:separate;"
    ),
    "seguranca-celula": "padding:14px 18px 4px 18px;",
    "seguranca-lista": (
        f"font-family:{FONTE};margin:0 0 12px 0;padding:0 0 0 20px;font-size:14px;"
        f"line-height:21px;color:{TEXTO_FRACO};"
    ),
    "assinatura": f"{_TEXTO_BASE}margin:0 0 4px 0;font-size:14px;line-height:20px;font-weight:700;",
    "nota": f"font-family:{FONTE};margin:0 0 4px 0;font-size:13px;line-height:19px;"
    f"color:{TEXTO_FRACO};",
}

for _estado, (_cor, _fundo) in ESTADOS.items():
    ESTILOS[f"destaque-{_estado}"] = (
        f"background-color:{_fundo};border-left:4px solid {_cor};border-radius:4px;"
        "padding:16px 18px;"
    )

_CLASSE = re.compile(r'\sclass="([^"]*)"')


def estilizar(html):
    """Troca cada `class="..."` pelo `style` das classes, na ordem em que aparecem.

    Classe desconhecida é erro: um quadro sem regra sairia sem cor, e ninguém veria até abrir a
    mensagem num cliente de e-mail.
    """

    def trocar(casamento):
        declaracoes = []
        for classe in casamento.group(1).split():
            if classe not in ESTILOS:
                raise ValueError(f"classe sem estilo na mensagem: {classe!r}")
            declaracoes.append(ESTILOS[classe])
        return f' style="{"".join(declaracoes)}"'

    return _CLASSE.sub(trocar, html)


def assunto_e_corpo(texto):
    """A primeira linha do texto puro é o assunto; o resto, sem as linhas vazias das tags.

    A convenção da convocação (121), estendida às demais: o assunto mora no mesmo modelo que o
    corpo, e não numa constante à parte que pode dizer outra coisa.
    """
    linhas = [linha.rstrip() for linha in texto.strip("\n").split("\n")]
    corpo = re.sub(r"\n{3,}", "\n\n", "\n".join(linhas[1:]).strip("\n"))
    return linhas[0].strip(), corpo + "\n"


@dataclass(frozen=True)
class Mensagem:
    assunto: str
    texto: str
    html: str


def compor(nome, contexto):
    """Renderiza `<nome>.txt` e `<nome>.html` com o mesmo contexto: o assunto, o texto e o HTML."""
    assunto, texto = assunto_e_corpo(get_template(f"{nome}.txt").render(contexto))
    html = estilizar(get_template(f"{nome}.html").render(contexto))
    return Mensagem(assunto=assunto, texto=texto, html=html)


def moldura(identificacao):
    """O que o cabeçalho e o rodapé leem de uma `Identificacao` da `unidades` (109).

    `unidade` vazia é a mensagem só da instituição: a conta do candidato, ou a implantação com mais
    de uma unidade ativa. O cabeçalho diz então "Seleções", sem escolher unidade por quem lê.
    """
    return {
        "instituicao": identificacao.instituicao,
        "instituicao_por_extenso": identificacao.nome_da_instituicao,
        "unidade": identificacao.sigla,
        "assinatura": identificacao.rotulo,
    }


# --- O texto congelado dos avisos (066, 134) ------------------------------------------------------
# O aviso guarda o texto que saiu, e o HTML é só outra forma de mostrá-lo: nenhuma frase a mais.
# Os únicos acréscimos são o cabeçalho institucional e o rótulo do botão, que nomeia a página para
# onde o endereço leva — lido da rota, e não do texto que a unidade escreveu.

#: O rótulo do botão para cada página do portal que um aviso pode citar.
ROTULOS_DAS_ROTAS = {
    "portal:convocacao": "Abrir minha convocação",
    "portal:inscricoes": "Entrar na área do candidato",
    "portal:inscricao": "Abrir minha inscrição",
}

SEPARADOR_DO_RODAPE = "—"
_ENDERECO = re.compile(r"https?://\S+")
_ENDERECO_NO_FIM = re.compile(r"^(?P<frase>.*?)\s*(?P<endereco>https?://\S+?)[.)]?$", re.S)


def rotulo_da_rota(endereco):
    """O rótulo do botão do endereço, ou `""` quando ele não é uma página conhecida do portal."""
    try:
        rota = resolve(urlparse(endereco).path)
    except Resolver404:
        return ""
    return ROTULOS_DAS_ROTAS.get(rota.view_name, "")


@dataclass(frozen=True)
class Bloco:
    """Um parágrafo do texto, como o HTML o mostra."""

    tipo: str  # "texto", "lista" ou "acao"
    linhas: tuple = ()
    endereco: str = ""
    rotulo: str = ""


def _bloco(paragrafo):
    linhas = [linha.strip() for linha in paragrafo.split("\n") if linha.strip()]
    if all(linha.startswith("- ") for linha in linhas):
        return Bloco("lista", tuple(linha[2:] for linha in linhas))
    casou = _ENDERECO_NO_FIM.match(" ".join(linhas))
    # Só vira botão o endereço que termina o parágrafo **e** leva a uma página conhecida: no meio da
    # frase, ou para fora do portal, ele continua texto, e o cliente de e-mail o torna clicável.
    if casou and len(_ENDERECO.findall(paragrafo)) == 1:
        rotulo = rotulo_da_rota(casou["endereco"])
        if rotulo:
            frase = casou["frase"].strip()
            return Bloco("acao", (frase,) if frase else (), casou["endereco"], rotulo)
    return Bloco("texto", tuple(linhas))


def blocos_do_aviso(corpo):
    """O texto congelado do aviso, em blocos: o corpo, a nota do rodapé e a assinatura.

    O rodapé do sistema começa na linha `—` (066, 134). O primeiro parágrafo depois dela é a nota
    — o que o aviso não é, e a quem perguntar —, e o último, a assinatura. Texto sem a linha é
    corpo inteiro: o HTML não inventa rodapé.
    """
    partes = re.split(rf"\n{SEPARADOR_DO_RODAPE}\n", corpo.strip(), maxsplit=1)
    corpo_proprio = partes[0]
    rodape = partes[1] if len(partes) > 1 else ""
    blocos = [_bloco(p) for p in re.split(r"\n\s*\n", corpo_proprio) if p.strip()]
    paragrafos_do_rodape = [p for p in re.split(r"\n\s*\n", rodape) if p.strip()]
    nota = paragrafos_do_rodape[:-1] if len(paragrafos_do_rodape) > 1 else paragrafos_do_rodape
    assinatura = paragrafos_do_rodape[-1] if len(paragrafos_do_rodape) > 1 else ""
    return {
        "blocos": blocos,
        "nota": [linha for p in nota for linha in p.split("\n") if linha.strip()],
        "assinatura": [linha for linha in assinatura.split("\n") if linha.strip()],
    }


def resumo_para_o_preheader(blocos, limite=140):
    """A primeira frase de conteúdo, sem a saudação: o que aparece ao lado do assunto na caixa."""
    for bloco in blocos:
        if bloco.tipo != "texto":
            continue
        texto = " ".join(bloco.linhas)
        if re.match(r"^(Olá|Prezad[oa])\b", texto) and len(texto) < 60:
            continue
        return texto if len(texto) <= limite else texto[: limite - 1].rsplit(" ", 1)[0] + "…"
    return ""


def unidade_da_assinatura(assinatura):
    """ "Cefor/Ifes — Seleções" → "Cefor"; "Ifes — Seleções" → `""` (só a instituição)."""
    rotulo = assinatura.split(" — ")[0].strip()
    sigla, _, instituicao = rotulo.partition("/")
    return sigla if instituicao else ""


def html_do_aviso(*, assunto, corpo, estado="informacao"):
    """O HTML de um aviso a partir do texto que ele congelou — e só dele.

    **A unidade do cabeçalho sai da assinatura do texto**, e não de uma consulta: o despacho envia
    dezenas por minuto, e o texto já diz quem assina (109, FR-3209).
    """
    from processo_seletivo.unidades.application import identificacao

    partes = blocos_do_aviso(corpo)
    return estilizar(
        get_template("correio/aviso.html").render(
            {
                "instituicao_por_extenso": identificacao.NOME_DA_INSTITUICAO,
                "unidade": unidade_da_assinatura(" ".join(partes["assinatura"][:1])),
                "assunto": assunto,
                "preheader": resumo_para_o_preheader(partes["blocos"]),
                "estado": estado if estado in ESTADOS else "informacao",
                **partes,
            }
        )
    )


__all__ = [
    "ESTADOS",
    "ESTILOS",
    "Mensagem",
    "ROTULOS_DAS_ROTAS",
    "assunto_e_corpo",
    "blocos_do_aviso",
    "compor",
    "estilizar",
    "html_do_aviso",
    "moldura",
    "resumo_para_o_preheader",
    "rotulo_da_rota",
    "unidade_da_assinatura",
]
