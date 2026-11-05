"""As famílias da peça do kit de divulgação e o registro delas (119, FR-3802–FR-3808, D-003).

**Família é módulo Python declarativo, e não arquivo de dados** (`D-003`). Cada família constrói
objetos imutáveis — `Familia`, `Template`, `Caixa` —, e um erro de digitação quebra na importação,
e não na primeira geração. As famílias mudam por PR, nunca pela tela; a comunicação não edita
template pelo sistema.

**Template é família × formato** (FR-3803). Ele declara as caixas de texto — campo, fonte (pelo
papel), cor e fundo (pelo nome na paleta), corpos do maior ao menor, linhas, alinhamento e o que
fazer quando não cabe —, os ativos fixos que posiciona e o compositor que o desenha. A peça da `111`
é a família Institucional (`D-002`): o compositor de fluxo dela continua o mesmo, e lê da declaração
o que antes eram constantes no código.

**O resumo do template amarra a aprovação ao conteúdo** (FR-3833, `D-014`). É o SHA-256 da
declaração em JSON canônico, dos resumos dos ativos, imagens e fontes da família e do resumo das
referências SVG do template. A liberação nomeia versão **e** resumo curto (`D-010`): regravar o
resumo na mesma versão desencontra a configuração, e o template fica indisponível.
"""

import dataclasses
import hashlib
import json
from dataclasses import dataclass, field
from pathlib import Path

from processo_seletivo.interface import kit_fontes
from processo_seletivo.interface.kit_formatos import FORMATOS, Formato

PASTA_DOS_ATIVOS = Path(__file__).resolve().parent.parent / "kit_ativos"

#: Os papéis de fonte que uma família declara (data-model §Família). O `rotulo` é o da FIC: a Space
#: Mono do número e da faixa, uma terceira fonte além da do título e da do corpo.
PAPEIS = ("titulo", "corpo", "destaque", "rotulo")
#: O que uma caixa faz quando nenhum corpo cabe. Só `titulo` e `contato` podem omitir (FR-3803).
RECUSAR, OMITIR = "recusar", "omitir"
PODEM_OMITIR = frozenset({"titulo", "contato"})
#: Quantos caracteres do resumo a liberação nomeia (contracts/kit.md).
RESUMO_CURTO = 12


@dataclass(frozen=True)
class Ativo:
    """Um arquivo fixo da família — marca, padrão, balão, ilustração —, com o resumo (D-004)."""

    arquivo: str
    sha256: str
    descricao: str
    #: A parte do arquivo com tinta, em frações da largura e da altura, quando a transparência em
    #: volta é reserva de integridade (a marca da `111`).
    visivel: tuple | None = None


@dataclass(frozen=True)
class Imagem:
    """Uma imagem do banco curto da família (FR-3807), com o que o alternativo diz dela.

    Uma escolha vale para todos os formatos, e cada formato tem o seu arquivo, recortado e reduzido
    para ele: `arquivos` é `{formato: (arquivo, sha256)}`.
    """

    chave: str
    descricao: str
    licenca: str
    origem: str
    arquivos: dict

    def arquivo(self, formato):
        return self.arquivos[formato][0]

    def sha256(self, formato):
        return self.arquivos[formato][1]


@dataclass(frozen=True)
class Variante:
    chave: str
    nome: str
    #: Frase fixa, e por isso sujeita à FR-3814.
    chamada: str


@dataclass(frozen=True)
class Caixa:
    """Uma caixa de texto do template.

    `retangulo` nulo quer dizer que a posição é do compositor de fluxo, que empilha as caixas na
    ordem do conteúdo: é o caso da Institucional. `linhas_maximas` é um número para todos os corpos,
    ou um por corpo, na mesma ordem.
    """

    campo: str
    fonte: str
    cor: str
    fundo: str
    corpos: tuple
    linhas_maximas: int | tuple = 1
    alinhamento: str = "start"
    ao_nao_caber: str = RECUSAR
    retangulo: tuple | None = None

    def medidas(self):
        """`(corpo, linhas_maximas)` do maior corpo ao menor."""
        if isinstance(self.linhas_maximas, int):
            return tuple((corpo, self.linhas_maximas) for corpo in self.corpos)
        return tuple(zip(self.corpos, self.linhas_maximas, strict=True))


@dataclass(frozen=True)
class Template:
    familia: str
    formato: Formato
    versao: int
    #: O compositor que desenha este template; a chave em `kit_peca.COMPOSITORES`.
    composicao: str
    caixas: tuple
    #: Vazio: `<familia>/<formato> · <versao>`. A Institucional mantém o da `111` (`D-002`).
    identificador: str = ""
    forma_do_periodo: str = "de-a"
    tem_ofertas: bool = True
    tem_contato: bool = False
    #: `{nome do ativo: (x, y, largura, altura)}`; contam como obstáculo (D-011).
    ativos_posicionados: dict = field(default_factory=dict)
    area_da_imagem: tuple | None = None
    #: As medidas do layout que não são caixa — faixas, blocos, recuos — pelo nome.
    dimensoes: dict = field(default_factory=dict)
    #: O SHA-256 dos SVG de referência do template, fixado aqui e conferido pela suíte (D-014).
    resumo_das_referencias: str = ""
    #: A pasta das referências em `tests/fixtures/kit_referencias/`; só a suíte a lê.
    pasta_das_referencias: str = ""

    def __post_init__(self):
        if not self.identificador:
            nome = f"{self.familia}/{self.formato.chave} · {self.versao}"
            object.__setattr__(self, "identificador", nome)

    @property
    def chave(self):
        return f"{self.familia}/{self.formato.chave}"

    def caixa(self, campo):
        for caixa in self.caixas:
            if caixa.campo == campo:
                return caixa
        raise KeyError(f"O template {self.identificador} não declara a caixa {campo!r}.")


@dataclass(frozen=True)
class Familia:
    chave: str
    nome: str
    versao: int
    #: Códigos de unidade; vazio só na Institucional, que vale para todas (FR-3805).
    unidades: frozenset
    paleta: dict
    #: Papel → chave em `kit_fontes.FONTES`.
    fontes: dict
    ativos: dict
    frases: dict
    templates: dict
    imagens: tuple = ()
    variantes: tuple = ()
    #: Onde estão os arquivos da família, relativo a `kit_ativos/`.
    pasta: str = ""

    @property
    def pasta_dos_ativos(self):
        return PASTA_DOS_ATIVOS / self.pasta

    def cor(self, nome):
        return self.paleta[nome]

    def fonte(self, papel):
        return self.fontes[papel]

    def chaves_das_fontes(self):
        """As fontes da família, sem repetir, na ordem dos papéis declarados."""
        return tuple(dict.fromkeys(self.fontes.values()))


# ---- O registro ---------------------------------------------------------------------------------

REGISTRO: dict[str, Familia] = {}


def registrar(familia):
    if familia.chave in REGISTRO:
        raise ValueError(f"Família registrada duas vezes: {familia.chave}.")
    for chave, template in familia.templates.items():
        if template.familia != familia.chave or template.formato is not FORMATOS[chave]:
            raise ValueError(f"Template fora do lugar: {template.identificador}.")
    REGISTRO[familia.chave] = familia
    return familia


def familia(chave):
    return REGISTRO[chave]


def template(chave_da_familia, formato):
    """O template, ou `None` quando a família não desenha aquele formato."""
    registrada = REGISTRO.get(chave_da_familia)
    return registrada.templates.get(formato) if registrada else None


def templates():
    """Todos os templates registrados, por família e na ordem dos formatos."""
    return tuple(
        registrada.templates[formato]
        for registrada in REGISTRO.values()
        for formato in FORMATOS
        if formato in registrada.templates
    )


def familias_da_unidade(codigo):
    """A Institucional, que vale para todas, e as famílias desta unidade (FR-3805, EC-1)."""
    return tuple(
        registrada
        for registrada in REGISTRO.values()
        if not registrada.unidades or codigo in registrada.unidades
    )


# ---- O resumo do template (FR-3833, D-014) -----------------------------------------------------


def _resumo_de_arquivo(caminho):
    return hashlib.sha256(Path(caminho).read_bytes()).hexdigest()


def declaracao(template_):
    """A declaração do template e da família dele, em JSON canônico.

    Entra o que muda o desenho — caixas, frases, paleta, fontes, ativos, imagens, posições — com o
    resumo de cada arquivo, lido do arquivo, e não do que a declaração diz: um ativo trocado sem
    atualizar o registro muda o resumo do template mesmo assim.
    """
    registrada = REGISTRO[template_.familia]
    dados = {
        "template": dataclasses.asdict(template_),
        "familia": {
            "chave": registrada.chave,
            "versao": registrada.versao,
            "paleta": registrada.paleta,
            "fontes": registrada.fontes,
            "frases": registrada.frases,
            "variantes": [dataclasses.asdict(v) for v in registrada.variantes],
        },
        "insumos": {
            "fontes": {
                kit_fontes.FONTES[chave].arquivo: _resumo_de_arquivo(
                    kit_fontes.FONTES[chave].caminho
                )
                for chave in registrada.chaves_das_fontes()
            },
            "ativos": {
                nome: {
                    **dataclasses.asdict(ativo),
                    "sha256": _resumo_de_arquivo(registrada.pasta_dos_ativos / ativo.arquivo),
                }
                for nome, ativo in registrada.ativos.items()
            },
            "imagens": [
                {
                    **dataclasses.asdict(imagem),
                    "lidos": {
                        formato: _resumo_de_arquivo(registrada.pasta_dos_ativos / arquivo)
                        for formato, (arquivo, _) in imagem.arquivos.items()
                    },
                }
                for imagem in registrada.imagens
            ],
        },
    }
    return json.dumps(dados, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def resumo(template_):
    return hashlib.sha256(declaracao(template_).encode()).hexdigest()


# ---- A liberação (FR-3808, FR-3835, D-010) -----------------------------------------------------


#: O motivo do template cuja versão ou resumo no código não são os liberados (EC-23, FR-3835).
VERSAO_EM_APROVACAO = "Versão nova em aprovação pela comunicação."


def institucional_v1(template_):
    """A Institucional na versão 1 com o resumo congelado: a única que a chave da `111` rege."""
    from processo_seletivo.interface.kit_familias import institucional

    return (
        template_.familia == institucional.CHAVE
        and template_.versao == 1
        and resumo(template_) == institucional.RESUMO_CONGELADO_V1
    )


def liberados():
    """Os templates que este ambiente pode gerar.

    A Institucional na versão 1, com o resumo congelado, é da chave da `111`
    (`KIT_DE_DIVULGACAO_PECA`), que continua regendo a peça de produção; listá-la na chave nova não
    a libera nem a retém. Todo o resto é da `KIT_DE_DIVULGACAO_TEMPLATES`, que nomeia versão e
    resumo curto: template cuja versão ou resumo no código não são os nomeados fica indisponível.
    """
    from django.conf import settings

    nomeados = {
        (familia_, formato): (versao, curto)
        for familia_, formato, versao, curto in settings.KIT_DE_DIVULGACAO_TEMPLATES
    }
    saida = []
    for candidato in templates():
        if institucional_v1(candidato):
            if settings.KIT_DE_DIVULGACAO_PECA:
                saida.append(candidato)
            continue
        nomeado = nomeados.get((candidato.familia, candidato.formato.chave))
        if nomeado == (candidato.versao, resumo(candidato)[:RESUMO_CURTO]):
            saida.append(candidato)
    return tuple(saida)


def _registrar_as_familias():
    # Importadas aqui, e não no topo: cada família importa as classes deste módulo.
    from processo_seletivo.interface.kit_familias import (
        aperfeicoamento,
        fic,
        institucional,
        libras,
        pos_lato_sensu,
        uab,
    )

    registrar(institucional.FAMILIA)
    registrar(pos_lato_sensu.FAMILIA)
    registrar(fic.FAMILIA)
    registrar(aperfeicoamento.FAMILIA)
    registrar(libras.FAMILIA)
    registrar(uab.FAMILIA)


_registrar_as_familias()
