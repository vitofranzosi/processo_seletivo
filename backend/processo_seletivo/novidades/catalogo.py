"""As notas das Novidades do GPS, lidas do arquivo versionado (168, FR-7420, FR-7421).

**A nota viaja com o código** (`D-001`). O arquivo mora neste app e entra na release como o resto do
`backend/`; um ambiente só mostra a nota que o commit dele contém. Nada aqui consulta o GitHub nem o
banco.

O que se confere **aqui** é o que basta para a página não quebrar: a forma de cada nota. O que pede
o resto do sistema — a rota do destino, a âncora da Documentação do Sistema, a configuração, a
capacidade, a spec citada e o vocabulário do texto visível — é conferido pela suíte
(`tests/novidades/test_catalogo.py`), antes do merge (FR-7422).
"""

import datetime
import re
import tomllib
from dataclasses import dataclass
from pathlib import Path

ARQUIVO = Path(__file__).with_name("novidades.toml")


@dataclass(frozen=True)
class Categoria:
    codigo: str
    rotulo: str
    plural: str


# A ordem é a do filtro. Três, e não mais (FR-7404): "novidade" é o que não existia, "melhoria" é o
# que existia e ficou melhor, "correção" é o comportamento errado que deixou de acontecer.
CATEGORIAS = (
    Categoria("novidade", "Novidade", "Novidades"),
    Categoria("melhoria", "Melhoria", "Melhorias"),
    Categoria("correcao", "Correção", "Correções"),
)
POR_CODIGO = {categoria.codigo: categoria for categoria in CATEGORIAS}

IDENTIFICADOR = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
OBRIGATORIOS = ("id", "data", "categoria", "titulo", "resumo", "prs", "specs")
OPCIONAIS = (
    "beneficio",
    "onde",
    "passos",
    "destino",
    "documentacao",
    "requer_configuracao",
    "para_capacidade",
)


class CatalogoInvalido(Exception):
    """O arquivo não se lê, ou uma nota não tem a forma. A mensagem diz qual nota e qual campo."""


@dataclass(frozen=True)
class Nota:
    id: str
    data: datetime.date
    categoria: Categoria
    titulo: str
    resumo: str
    # Fora do que se mostra (FR-7407): servem à rastreabilidade e ao roteiro de curadoria.
    prs: tuple
    specs: tuple
    beneficio: str = ""
    onde: str = ""
    passos: tuple = ()
    # O nome de uma rota da barra (`interface:agenda`); o link segue o predicado da seção (`D-004`).
    destino: str = ""
    # A âncora da seção da Documentação do Sistema, sem o `#`.
    documentacao: str = ""
    # O nome de uma configuração booleana; desligada, a nota não existe neste ambiente (`D-003`).
    requer_configuracao: str = ""
    # A capacidade de quem lê; sem ela, a nota não aparece para a pessoa (`D-004`).
    para_capacidade: str = ""


def _texto(numero, entrada, campo, *, obrigatorio):
    valor = entrada.get(campo, "")
    if not isinstance(valor, str):
        raise CatalogoInvalido(f"nota {numero} ({entrada.get('id')}): '{campo}' deve ser texto")
    valor = " ".join(valor.split())
    if obrigatorio and not valor:
        raise CatalogoInvalido(f"nota {numero} ({entrada.get('id')}): '{campo}' está vazio")
    return valor


def _nota(numero, entrada):
    if not isinstance(entrada, dict):
        raise CatalogoInvalido(f"nota {numero}: não é uma tabela [[nota]]")
    nome = entrada.get("id")
    for campo in OBRIGATORIOS:
        if campo not in entrada:
            raise CatalogoInvalido(f"nota {numero} ({nome}): falta '{campo}'")
    desconhecidos = set(entrada) - set(OBRIGATORIOS) - set(OPCIONAIS)
    if desconhecidos:
        raise CatalogoInvalido(
            f"nota {numero} ({nome}): campo desconhecido {', '.join(sorted(desconhecidos))}"
        )
    if not isinstance(nome, str) or not IDENTIFICADOR.match(nome):
        raise CatalogoInvalido(f"nota {numero}: 'id' deve ser minúsculo, com hífens ({nome!r})")
    data = entrada["data"]
    # O TOML lê `2026-11-10` como data; data com hora ou texto é engano de quem escreveu.
    if not isinstance(data, datetime.date) or isinstance(data, datetime.datetime):
        raise CatalogoInvalido(f"nota {numero} ({nome}): 'data' deve ser AAAA-MM-DD, sem aspas")
    categoria = POR_CODIGO.get(entrada["categoria"])
    if categoria is None:
        raise CatalogoInvalido(
            f"nota {numero} ({nome}): categoria {entrada['categoria']!r} não é "
            f"{', '.join(POR_CODIGO)}"
        )
    prs = entrada["prs"]
    if (
        not prs
        or not isinstance(prs, list)
        or not all(isinstance(pr, int) and pr > 0 for pr in prs)
    ):
        raise CatalogoInvalido(f"nota {numero} ({nome}): 'prs' deve listar números de PR")
    specs = entrada["specs"]
    if not isinstance(specs, list) or not all(isinstance(s, str) for s in specs):
        raise CatalogoInvalido(f"nota {numero} ({nome}): 'specs' deve listar textos")
    passos = entrada.get("passos", [])
    if not isinstance(passos, list) or not all(isinstance(p, str) and p.strip() for p in passos):
        raise CatalogoInvalido(f"nota {numero} ({nome}): 'passos' deve listar textos")
    return Nota(
        id=nome,
        data=data,
        categoria=categoria,
        titulo=_texto(numero, entrada, "titulo", obrigatorio=True),
        resumo=_texto(numero, entrada, "resumo", obrigatorio=True),
        prs=tuple(prs),
        specs=tuple(specs),
        beneficio=_texto(numero, entrada, "beneficio", obrigatorio=False),
        onde=_texto(numero, entrada, "onde", obrigatorio=False),
        passos=tuple(" ".join(p.split()) for p in passos),
        destino=_texto(numero, entrada, "destino", obrigatorio=False),
        documentacao=_texto(numero, entrada, "documentacao", obrigatorio=False),
        requer_configuracao=_texto(numero, entrada, "requer_configuracao", obrigatorio=False),
        para_capacidade=_texto(numero, entrada, "para_capacidade", obrigatorio=False),
    )


def ler(conteudo):
    """As notas de um texto TOML, na ordem do arquivo, que é a da linha do tempo."""
    try:
        dados = tomllib.loads(conteudo)
    except tomllib.TOMLDecodeError as erro:
        raise CatalogoInvalido(f"o arquivo não é TOML válido: {erro}") from erro
    entradas = dados.get("nota", [])
    if not isinstance(entradas, list):
        raise CatalogoInvalido("as notas devem ser tabelas [[nota]]")
    notas = [_nota(numero, entrada) for numero, entrada in enumerate(entradas, start=1)]
    vistos = set()
    for nota in notas:
        if nota.id in vistos:
            raise CatalogoInvalido(f"o id {nota.id!r} se repete")
        vistos.add(nota.id)
    # A ordem do arquivo é a da página: a mais recente primeiro. Exigi-la, em vez de ordenar, mantém
    # o arquivo legível na revisão do PR, e duas notas do mesmo dia ficam na ordem que quem cura
    # escolheu.
    for anterior, seguinte in zip(notas, notas[1:], strict=False):
        if seguinte.data > anterior.data:
            raise CatalogoInvalido(
                f"a nota {seguinte.id!r} ({seguinte.data}) está depois de {anterior.id!r} "
                f"({anterior.data}): o arquivo vai da mais recente para a mais antiga"
            )
    return tuple(notas)


_LIDO = {}


def notas():
    """As notas do arquivo da release. Relidas só quando o arquivo muda — em produção, nunca."""
    try:
        marca = (ARQUIVO, ARQUIVO.stat().st_mtime_ns)
    except OSError as erro:
        raise CatalogoInvalido(f"o arquivo das notas não existe: {ARQUIVO}") from erro
    if marca not in _LIDO:
        _LIDO.clear()
        _LIDO[marca] = ler(ARQUIVO.read_text(encoding="utf-8"))
    return _LIDO[marca]
