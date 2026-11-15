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
    # "Nova funcionalidade", e não "Novidade": a página inteira se chama Novidades, e o filtro
    # "Novidades" dentro dela não dizia o que separava (revisão editorial de 14/11, `D-012`).
    Categoria("novidade", "Nova funcionalidade", "Funcionalidades"),
    Categoria("melhoria", "Melhoria", "Melhorias"),
    Categoria("correcao", "Correção", "Correções"),
)
POR_CODIGO = {categoria.codigo: categoria for categoria in CATEGORIAS}

# O peso da nota para quem opera, independente do tipo (FR-7428, `D-012`). A categoria diz o que
# a mudança é; a relevância diz quanto ela muda o trabalho — e decide o tamanho do cartão e o que
# abre o "Desde sua última visita". Medida pelo benefício, nunca pelo número de PRs.
RELEVANCIAS = ("transformadora", "relevante", "incremental")

IDENTIFICADOR = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
OBRIGATORIOS = ("id", "data", "categoria", "relevancia", "titulo", "resumo", "prs", "specs")
OPCIONAIS = (
    "exemplo",
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
    relevancia: str
    titulo: str
    resumo: str
    # Fora do que se mostra (FR-7407): servem à rastreabilidade e ao roteiro de curadoria.
    prs: tuple
    specs: tuple
    # A cena concreta que a página mostra como "Na prática" (FR-7427): é o que faz a nota se
    # entender de primeira (diretriz de 14/11, `doc/curadoria-das-novidades.md`).
    exemplo: str = ""
    beneficio: str = ""
    onde: str = ""
    passos: tuple = ()
    # O nome de uma rota da barra (`interface:agenda`); o link segue o predicado da seção (`D-004`).
    destino: str = ""
    # A âncora da seção da Documentação do Sistema, sem o `#`.
    documentacao: str = ""
    # O nome de uma configuração booleana; desligada, a nota não existe neste ambiente (`D-003`).
    requer_configuracao: str = ""
    # As capacidades de quem lê, e basta uma; sem nenhuma, a nota não aparece para a pessoa
    # (`D-004`). No arquivo, um texto ou uma lista de textos.
    para_capacidade: tuple = ()


def _texto(numero, entrada, campo, *, obrigatorio):
    valor = entrada.get(campo, "")
    if not isinstance(valor, str):
        raise CatalogoInvalido(f"nota {numero} ({entrada.get('id')}): '{campo}' deve ser texto")
    valor = " ".join(valor.split())
    if obrigatorio and not valor:
        raise CatalogoInvalido(f"nota {numero} ({entrada.get('id')}): '{campo}' está vazio")
    return valor


def _capacidades(numero, entrada):
    valor = entrada.get("para_capacidade", [])
    valores = [valor] if isinstance(valor, str) else valor
    if not isinstance(valores, list) or not all(isinstance(v, str) and v.strip() for v in valores):
        raise CatalogoInvalido(
            f"nota {numero} ({entrada.get('id')}): "
            "'para_capacidade' deve ser texto ou lista de textos"
        )
    return tuple(v.strip() for v in valores)


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
    if entrada["relevancia"] not in RELEVANCIAS:
        raise CatalogoInvalido(
            f"nota {numero} ({nome}): relevância {entrada['relevancia']!r} não é "
            f"{', '.join(RELEVANCIAS)}"
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
        relevancia=entrada["relevancia"],
        titulo=_texto(numero, entrada, "titulo", obrigatorio=True),
        resumo=_texto(numero, entrada, "resumo", obrigatorio=True),
        prs=tuple(prs),
        specs=tuple(specs),
        exemplo=_texto(numero, entrada, "exemplo", obrigatorio=False),
        beneficio=_texto(numero, entrada, "beneficio", obrigatorio=False),
        onde=_texto(numero, entrada, "onde", obrigatorio=False),
        passos=tuple(" ".join(p.split()) for p in passos),
        destino=_texto(numero, entrada, "destino", obrigatorio=False),
        documentacao=_texto(numero, entrada, "documentacao", obrigatorio=False),
        requer_configuracao=_texto(numero, entrada, "requer_configuracao", obrigatorio=False),
        para_capacidade=_capacidades(numero, entrada),
    )


@dataclass(frozen=True)
class Capacidade:
    """Uma entrega de produto, e não uma mudança: o que o GPS passou a fazer (FR-7429, `D-012`).

    Reúne as notas que a construíram — dez, vinte PRs que, juntos, são uma coisa só para quem
    opera — e é o que a página mostra em "Descubra o que o GPS já faz". Não tem data própria: a
    página diz quantas atualizações a construíram, e não inventa um dia de lançamento.
    """

    id: str
    ordem: int
    icone: str
    titulo: str
    resumo: str
    notas: tuple
    como_comecar: str = ""
    passos: tuple = ()
    destino: str = ""
    documentacao: str = ""
    requer_configuracao: str = ""
    para_capacidade: tuple = ()


CAPACIDADE_OBRIGATORIOS = ("id", "ordem", "icone", "titulo", "resumo", "notas")
CAPACIDADE_OPCIONAIS = (
    "como_comecar",
    "passos",
    "destino",
    "documentacao",
    "requer_configuracao",
    "para_capacidade",
)
ICONE = re.compile(r"^i-[a-z]+(?:-[a-z]+)*$")


def _capacidade(numero, entrada, ids_das_notas):
    if not isinstance(entrada, dict):
        raise CatalogoInvalido(f"capacidade {numero}: não é uma tabela [[capacidade]]")
    nome = entrada.get("id")
    rotulo = f"capacidade {numero} ({nome})"
    for campo in CAPACIDADE_OBRIGATORIOS:
        if campo not in entrada:
            raise CatalogoInvalido(f"{rotulo}: falta '{campo}'")
    desconhecidos = set(entrada) - set(CAPACIDADE_OBRIGATORIOS) - set(CAPACIDADE_OPCIONAIS)
    if desconhecidos:
        raise CatalogoInvalido(f"{rotulo}: campo desconhecido {', '.join(sorted(desconhecidos))}")
    if not isinstance(nome, str) or not IDENTIFICADOR.match(nome):
        raise CatalogoInvalido(f"capacidade {numero}: 'id' deve ser minúsculo, com hífens")
    if not isinstance(entrada["ordem"], int):
        raise CatalogoInvalido(f"{rotulo}: 'ordem' deve ser um número inteiro")
    if not isinstance(entrada["icone"], str) or not ICONE.match(entrada["icone"]):
        raise CatalogoInvalido(f"{rotulo}: 'icone' deve ser um símbolo como 'i-pasta'")
    notas = entrada["notas"]
    if not notas or not isinstance(notas, list) or not all(isinstance(n, str) for n in notas):
        raise CatalogoInvalido(f"{rotulo}: 'notas' deve listar os ids das notas que a construíram")
    for nota in notas:
        if nota not in ids_das_notas:
            raise CatalogoInvalido(f"{rotulo}: a nota {nota!r} não existe")
    passos = entrada.get("passos", [])
    if not isinstance(passos, list) or not all(isinstance(p, str) and p.strip() for p in passos):
        raise CatalogoInvalido(f"{rotulo}: 'passos' deve listar textos")
    texto = {
        campo: _texto(numero, entrada, campo, obrigatorio=False)
        for campo in CAPACIDADE_OPCIONAIS
        if campo not in ("passos", "para_capacidade")
    }
    return Capacidade(
        id=nome,
        ordem=entrada["ordem"],
        icone=entrada["icone"],
        titulo=_texto(numero, entrada, "titulo", obrigatorio=True),
        resumo=_texto(numero, entrada, "resumo", obrigatorio=True),
        notas=tuple(notas),
        passos=tuple(" ".join(p.split()) for p in passos),
        para_capacidade=_capacidades(numero, entrada),
        **texto,
    )


@dataclass(frozen=True)
class Catalogo:
    notas: tuple
    capacidades: tuple

    def capacidade_da_nota(self):
        """O id de cada nota → a capacidade a que ela pertence."""
        return {nota: capacidade for capacidade in self.capacidades for nota in capacidade.notas}


def ler(conteudo):
    """As notas de um texto TOML, na ordem do arquivo, que é a da linha do tempo."""
    return ler_catalogo(conteudo).notas


def ler_catalogo(conteudo):
    """As notas e as capacidades de um texto TOML."""
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
    ids = {nota.id for nota in notas}
    capacidades = [
        _capacidade(numero, entrada, ids)
        for numero, entrada in enumerate(dados.get("capacidade", []), start=1)
    ]
    dono = {}
    for capacidade in capacidades:
        for nota in capacidade.notas:
            if nota in dono:
                raise CatalogoInvalido(
                    f"a nota {nota!r} está em {dono[nota]!r} e em {capacidade.id!r}: "
                    "uma nota pertence a uma capacidade só"
                )
            dono[nota] = capacidade.id
    if len({c.id for c in capacidades}) != len(capacidades):
        raise CatalogoInvalido("o id de uma capacidade se repete")
    if len({c.ordem for c in capacidades}) != len(capacidades):
        raise CatalogoInvalido("duas capacidades têm a mesma ordem")
    return Catalogo(tuple(notas), tuple(sorted(capacidades, key=lambda c: c.ordem)))


_LIDO = {}


def notas():
    """As notas do arquivo da release."""
    return catalogo().notas


def capacidades():
    """As capacidades do arquivo da release, na ordem dos destaques."""
    return catalogo().capacidades


def catalogo():
    """O arquivo da release, lido. Relido só quando o arquivo muda — em produção, nunca.

    **A falha também se guarda**, pela mesma marca: com o arquivo inválido, a barra e a página o
    releriam e reinterpretariam a cada tela, e o erro é o mesmo até o arquivo mudar.
    """
    try:
        marca = (ARQUIVO, ARQUIVO.stat().st_mtime_ns)
    except OSError as erro:
        raise CatalogoInvalido(f"o arquivo das notas não existe: {ARQUIVO}") from erro
    if marca not in _LIDO:
        try:
            lido = ler_catalogo(ARQUIVO.read_text(encoding="utf-8"))
        except CatalogoInvalido as erro:
            lido = erro
        _LIDO.clear()
        _LIDO[marca] = lido
    resultado = _LIDO[marca]
    if isinstance(resultado, CatalogoInvalido):
        raise resultado
    return resultado
