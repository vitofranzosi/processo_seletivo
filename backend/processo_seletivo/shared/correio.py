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

import json
import re
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse

from django.template.loader import get_template
from django.urls import Resolver404, resolve

# --- Os tokens -----------------------------------------------------------------------------------
# **Num arquivo versionado, e não em Python** (`templates/correio/estilos.json`): classe →
# declaração em linha. O mapa decide como o HTML sai, e o resumo gravado em cada convocação
# (FR-3889) precisa cobri-lo e ser recalculável pelo Git sem o código de produção (R-009 da `121`).
# Montado aqui, com f-strings, ele só se reconstituiria rodando o código daquele commit.
#
# Os valores são os da folha comum (`shared/static/shared/tokens.css`), copiados porque o e-mail não
# lê folha: o verde que preenche (#15803d), o que escreve sobre fundo claro (#146c37), o da faixa
# (#0b5a2a) e os fundos de estado. Os contrastes contra o fundo em que aparecem passam de 4,5:1.
#
# **Seis estados, e a diferença é discreta** (`destaque-‹estado›`): a cor da borda e do fundo do
# quadro. Quem diz o estado é o título, e não a cor. O desfavorável é ardósia, e não vermelho: um
# resultado ruim pede cuidado, não alarme.

CAMINHO_DOS_ESTILOS = Path(__file__).resolve().parent / "templates" / "correio" / "estilos.json"

#: O texto do arquivo como o processo o leu — **a fonte que estiliza e a que se resume**, a mesma
#: leitura, como a R-009 pede da fonte compilada dos modelos: um arquivo trocado depois do início do
#: processo não muda nem o HTML que sai nem o resumo que se grava.
FONTE_DOS_ESTILOS = CAMINHO_DOS_ESTILOS.read_text(encoding="utf-8")
ESTILOS = json.loads(FONTE_DOS_ESTILOS)
ESTADOS = tuple(
    classe.removeprefix("destaque-") for classe in ESTILOS if classe.startswith("destaque-")
)

#: Cabeçalhos de toda mensagem do GPS. `Auto-Submitted` (RFC 3834) diz que ninguém a escreveu à mão:
#: as respostas de férias e os avisos de ausência não voltam para uma caixa que ninguém lê.
#: Era só dos avisos (066); toda mensagem do sistema é automática, e o rodapé de todas já o diz.
CABECALHOS = {"Auto-Submitted": "auto-generated"}

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
    "CABECALHOS",
    "CAMINHO_DOS_ESTILOS",
    "ESTADOS",
    "ESTILOS",
    "FONTE_DOS_ESTILOS",
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
