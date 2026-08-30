"""O que torna um Edital publicável.

Duas perguntas, e as duas moram aqui. A primeira é sobre a **raiz**: há título, ao menos um Perfil,
ao menos um Evento? A segunda é sobre a **forma de cada entidade**: o Perfil que passa a vigorar tem
os campos que o conteúdo publicado sempre carrega, com o tipo, a nulabilidade e as restrições que o
contrato declara?

A segunda pergunta existe porque o endereçamento da `004` garante **de quem** um ato fala, e não
que o que ele deixa seja um Edital bem formado. `REMOVE` de um campo obrigatório e `REPLACE` de um
Perfil inteiro omitindo campos passavam sem achado impeditivo, e o Perfil mutilado chegava à
consulta pública e ao PDF.

**A forma é transcrita do contrato, não inventada aqui.** `PerfilPublicado` e `EventoPublicado` no
`openapi.yaml` da `001` são a autoridade; um teste de contrato confere esta transcrição contra eles.
O domínio não pode ler o contrato em execução — ele vive em `specs/`, é artefato de processo e não é
distribuído com o pacote —, e a declaração conferida é o mesmo arranjo que a `004` usa para as
coleções com chave: o que é declarado e conferido falha alto quando diverge.

**A linha entre aplicar e inventar.** O que o contrato escreve, aplica-se — faixa de valor e
enumeração inclusive. O que ele não escreve, não se escreve aqui: coerência entre campos, como
`reserveLimit` condicionado ao tipo de reserva ou `endAt` posterior a `startAt`, é decisão normativa
que ninguém tomou.
"""

import re
from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from uuid import UUID


class Severity(StrEnum):
    INFO = "INFO"
    WARNING = "WARNING"
    BLOCKING_ERROR = "BLOCKING_ERROR"


@dataclass(frozen=True)
class ValidationFinding:
    severity: Severity
    code: str
    message: str
    path: str = ""


@dataclass(frozen=True)
class Campo:
    """Um campo da forma publicada, nas dimensões que se verificam.

    `minimo` e `valores` são as restrições que o contrato já escreve. Não há campo para coerência
    entre campos, e a ausência é deliberada: expressá-la aqui seria o primeiro passo para
    inventá-la.
    """

    nome: str
    tipo: type
    admite_nulo: bool = False
    formato: str = ""
    minimo: int | None = None
    valores: tuple[str, ...] = ()
    tipo_do_item: type | None = None
    padrao: str = ""


RESERVA = ("NONE", "LIMITED", "UNLIMITED")

PERFIL_PUBLICADO = (
    Campo("id", str, formato="uuid"),
    Campo("code", str),
    Campo("name", str),
    Campo("description", str),
    Campo("requirements", list),
    Campo("immediateVacancies", int, minimo=0),
    Campo("reserveType", str, valores=RESERVA),
    Campo("reserveLimit", int, admite_nulo=True, minimo=0),
    Campo("locality", str),
    Campo("classificationInformation", dict),
    Campo("callInformation", dict),
    # A forma de **dentro** de cada Modalidade não é declarada. Que cada item seja objeto, é —
    # `items: { type: object }` está escrito no contrato, e conferi-lo é aplicar, não inventar.
    Campo("competitionModalities", list, tipo_do_item=dict),
)

# A forma canônica do instante, transcrita de `EventoPublicado` no contrato: `T` maiúsculo,
# segundos obrigatórios, fração opcional, deslocamento `±HH:MM`. É o que `datetime.isoformat()`
# produz sobre um instante com fuso, que é o que o snapshot materializa.
INSTANTE = r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d{1,6})?[+-]\d{2}:\d{2}$"

EVENTO_PUBLICADO = (
    Campo("id", str, formato="uuid"),
    Campo("type", str),
    Campo("description", str),
    Campo("startAt", str, formato="date-time", padrao=INSTANTE),
    Campo("endAt", str, admite_nulo=True, formato="date-time", padrao=INSTANTE),
    Campo("order", int, minimo=0),
    # `status` é produzido pelo sistema e nenhum esquema declara a enumeração dele. Entra como
    # presença e tipo; escrever os valores aqui seria inventar restrição, não transcrever uma.
    Campo("status", str),
)

COLECOES_PUBLICADAS = (("profiles", PERFIL_PUBLICADO), ("schedule", EVENTO_PUBLICADO))

CAMPO_AUSENTE = "field_required"
TIPO_INVALIDO = "field_type_invalid"
NULO_INVALIDO = "field_null_invalid"
FORMATO_INVALIDO = "field_format_invalid"
RESTRICAO_VIOLADA = "field_constraint_violated"

_NOME_DO_TIPO = {str: "texto", int: "número inteiro", list: "lista", dict: "objeto"}


def _e_do_tipo(valor, tipo):
    """`bool` é subclasse de `int` em Python, e `True` não é um número de vagas."""
    if tipo is int and isinstance(valor, bool):
        return False
    return isinstance(valor, tipo)


# Formato declarado que não estivesse aqui levantaria `KeyError` na primeira verificação, e é o
# comportamento desejado: erro de programação que falha alto vale mais que formato aceito em
# silêncio por não ter quem o verifique.
_LEITOR_DE_FORMATO = {"uuid": UUID, "date-time": datetime.fromisoformat}


def _formato_satisfeito(valor, campo):
    """A forma, pelo padrão declarado; a validade, pelo leitor.

    Os dois são necessários e nenhum basta. `datetime.fromisoformat` é parser de ISO 8601, não
    validador de instante: aceita data isolada, instante sem fuso, data de semana, formato básico e
    espaço no lugar do `T` — formas que o snapshot nunca materializa e que tornariam ambígua
    justamente a vigência. O padrão as recusa. E o padrão sozinho aceitaria `2026-02-30`, que tem a
    forma certa e não é um dia; o leitor a recusa.

    O padrão é o do contrato, e é mais estreito que RFC 3339 de propósito: descreve o que este
    sistema escreve, e não tudo o que a norma permitiria. Validar a norma inteira seria
    implementá-la informalmente para conferir um valor que nós mesmos produzimos.
    """
    if campo.padrao and not re.fullmatch(campo.padrao, valor):
        return False
    try:
        _LEITOR_DE_FORMATO[campo.formato](valor)
    except (ValueError, AttributeError, TypeError):
        return False
    return True


def _violacao(campo, entidade, caminho):
    """A primeira violação do campo, ou None. Uma por campo: a primeira já diz o que corrigir."""
    if campo.nome not in entidade:
        return ValidationFinding(
            Severity.BLOCKING_ERROR,
            CAMPO_AUSENTE,
            f"O campo obrigatório não está presente em {caminho}.",
            caminho,
        )
    valor = entidade[campo.nome]
    if valor is None:
        if campo.admite_nulo:
            return None
        return ValidationFinding(
            Severity.BLOCKING_ERROR,
            NULO_INVALIDO,
            f"O campo não admite valor nulo em {caminho}.",
            caminho,
        )
    if not _e_do_tipo(valor, campo.tipo):
        return ValidationFinding(
            Severity.BLOCKING_ERROR,
            TIPO_INVALIDO,
            f"O campo deveria ser {_NOME_DO_TIPO[campo.tipo]} em {caminho}.",
            caminho,
        )
    if campo.formato and not _formato_satisfeito(valor, campo):
        return ValidationFinding(
            Severity.BLOCKING_ERROR,
            FORMATO_INVALIDO,
            f"O campo não satisfaz o formato {campo.formato} em {caminho}.",
            caminho,
        )
    if campo.tipo_do_item is not None and not all(
        isinstance(item, campo.tipo_do_item) for item in valor
    ):
        return ValidationFinding(
            Severity.BLOCKING_ERROR,
            TIPO_INVALIDO,
            f"Todo item deveria ser {_NOME_DO_TIPO[campo.tipo_do_item]} em {caminho}.",
            caminho,
        )
    if campo.minimo is not None and valor < campo.minimo:
        return ValidationFinding(
            Severity.BLOCKING_ERROR,
            RESTRICAO_VIOLADA,
            f"O campo não admite valor menor que {campo.minimo} em {caminho}.",
            caminho,
        )
    if campo.valores and valor not in campo.valores:
        return ValidationFinding(
            Severity.BLOCKING_ERROR,
            RESTRICAO_VIOLADA,
            f"O campo admite apenas {', '.join(campo.valores)} em {caminho}.",
            caminho,
        )
    return None


def _caminho_da_entidade(colecao, entidade, posicao):
    """A gramática da `004`, que nomeia a entidade sem consultar a versão vigente.

    Sem identificador utilizável o caminho recua para a posição: a `004` recusa entidade sem `id` no
    momento em que a alteração é aplicada, então isto não deve ocorrer — e é melhor que um achado
    que não nomeia nada.
    """
    identificador = entidade.get("id") if isinstance(entidade, dict) else None
    if isinstance(identificador, str) and identificador:
        return f"/{colecao}/id={identificador}"
    return f"/{colecao}/{posicao}"


def _violacoes_da_colecao(snapshot, colecao, forma):
    """As violações de forma dentro de uma coleção do snapshot.

    Coleção ausente ou vazia é assunto das condições de raiz, que já a reportam. Coleção que existe
    e **não é lista** era silêncio: um objeto é `truthy`, então a condição de raiz passava, e o laço
    daqui não tinha o que percorrer — zero achados para um snapshot que nenhuma consulta pública
    conseguiria projetar.
    """
    findings = []
    itens = snapshot.get(colecao)
    if itens is None:
        return findings
    if not isinstance(itens, list):
        return [
            ValidationFinding(
                Severity.BLOCKING_ERROR,
                TIPO_INVALIDO,
                f"A coleção deveria ser lista em /{colecao}.",
                f"/{colecao}",
            )
        ]
    for posicao, entidade in enumerate(itens):
        caminho = _caminho_da_entidade(colecao, entidade, posicao)
        if not isinstance(entidade, dict):
            findings.append(
                ValidationFinding(
                    Severity.BLOCKING_ERROR,
                    TIPO_INVALIDO,
                    f"O item deveria ser objeto em {caminho}.",
                    caminho,
                )
            )
            continue
        findings.extend(
            achado
            for campo in forma
            if (achado := _violacao(campo, entidade, f"{caminho}/{campo.nome}")) is not None
        )
    return findings


def validate_for_publication(snapshot: dict) -> list[ValidationFinding]:
    findings = []
    if not snapshot.get("title"):
        findings.append(
            ValidationFinding(
                Severity.BLOCKING_ERROR, "title_required", "Título obrigatório.", "title"
            )
        )
    if not snapshot.get("profiles"):
        findings.append(
            ValidationFinding(
                Severity.BLOCKING_ERROR,
                "profiles_required",
                "Ao menos um Perfil é obrigatório.",
                "profiles",
            )
        )
    if not snapshot.get("schedule"):
        findings.append(
            ValidationFinding(
                Severity.BLOCKING_ERROR,
                "schedule_required",
                "Ao menos um Evento é obrigatório.",
                "schedule",
            )
        )
    if not snapshot.get("description"):
        findings.append(
            ValidationFinding(
                Severity.WARNING,
                "description_missing",
                "O Edital não possui descrição.",
                "description",
            )
        )
    for colecao, forma in COLECOES_PUBLICADAS:
        findings.extend(_violacoes_da_colecao(snapshot, colecao, forma))
    return findings


def blocking_findings(findings):
    return [item for item in findings if item.severity == Severity.BLOCKING_ERROR]
