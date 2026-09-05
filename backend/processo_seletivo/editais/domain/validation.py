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
from decimal import Decimal, InvalidOperation
from enum import StrEnum
from uuid import UUID

from processo_seletivo.editais.domain.perfis import ProfileValidationError, validate_normative_rule
from processo_seletivo.editais.domain.secoes import CATALOGO, GERADA, TEXTUAL


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
    # `str` sem `admite_nulo`: os três são **sempre presentes**, com `""` quando não informados
    # (FR-014). Declará-los assim é o que faz a versão canônica 3 identificar uma forma só.
    Campo("duties", str),
    Campo("workload", str),
    Campo("compensation", str),
    Campo("classificationInformation", dict),
    Campo("callInformation", dict),
    # A forma de **dentro** de cada Modalidade não é declarada. Que cada item seja objeto, é —
    # `items: { type: object }` está escrito no contrato, e conferi-lo é aplicar, não inventar.
    Campo("competitionModalities", list, tipo_do_item=dict),
    # As duas da versão 7, pela mesma régua: aqui se declara que a coleção existe e que cada item é
    # objeto; o que vai **dentro** do fato e do marco é verificado por `_coerencia_dos_marcos`, que
    # precisa do conteúdo inteiro e não caberia numa forma de campo (015, T-009).
    Campo("declaredFacts", list, tipo_do_item=dict),
    Campo("classificationMilestones", list, tipo_do_item=dict),
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
    # Sempre presente, nunca nulo: a ausência de marca é `false`, e não "não informado". A regra
    # de quantos podem ser verdadeiros é de coerência entre itens e vive em
    # `_um_periodo_de_inscricoes`, porque a forma confere um campo por vez.
    Campo("isRegistrationPeriod", bool),
)

# Os dois identificadores são anuláveis por semântica: `null` é "não restringe". É a ausência
# deles que produz as quatro combinações de aplicabilidade, e declará-los assim é o que impede
# uma quinta forma de existir no conteúdo publicado.
DOCUMENTO_EXIGIDO_PUBLICADO = (
    Campo("id", str, formato="uuid"),
    Campo("key", str),
    Campo("name", str),
    Campo("instructions", str),
    Campo("required", bool),
    Campo("order", int, minimo=0),
    Campo("profileId", str, admite_nulo=True, formato="uuid"),
    Campo("modalityId", str, admite_nulo=True, formato="uuid"),
)

# A forma canônica do decimal de `weight` e `minimumScore`, os dois `decimal(7,4)`: no máximo três
# dígitos inteiros, sempre quatro casas, e **sem zeros à esquerda**, porque é assim que a
# persistência os materializa. O sinal é admitido de propósito: o padrão descreve **forma**, e a
# faixa é regra de domínio — fazê-lo recusar o sinal misturaria as duas coisas, e foi assim que uma
# invariante não declarada entrou por uma expressão regular. A faixa vive em
# `_coerencia_das_etapas`, que já percorre a coleção.
DECIMAL = r"^-?(0|[1-9]\d{0,2})\.\d{4}$"

# As duas formas de conclusão, como o conteúdo publicado as grafa. A lista literal fica aqui, e não
# importada de `avaliacoes`: este módulo confere a **string publicada** contra o contrato, e não
# conhece o domínio da conclusão — importá-lo inverteria a direção de dependência entre os apps.
FORMAS = ("PONTUADA", "DECISORIA")

# As duas recusas de aplicabilidade, ditas uma vez.
ROTULO = "A Etapa pontuada não publica rótulos de resultado em "
NOTA = "A Etapa decisória não publica nota em "

ETAPA_PUBLICADA = (
    Campo("id", str, formato="uuid"),
    Campo("name", str),
    Campo("order", int, minimo=0),
    Campo("weight", str, admite_nulo=True, formato="decimal", padrao=DECIMAL),
    Campo("eliminatory", bool),
    Campo("classificatory", bool),
    Campo("minimumScore", str, admite_nulo=True, formato="decimal", padrao=DECIMAL),
    # As duas do incremento da `012` (FR-007). Inteiro para a contagem de avaliações, que não tem
    # casas; decimal canônico para a máxima, que é `decimal(7,4)` como as outras duas. `null` é
    # "não declarado", e é assim que conteúdo publicado antes do incremento continua legível.
    Campo("evaluationsPerRegistration", int, admite_nulo=True, minimo=1),
    Campo("maximumScore", str, admite_nulo=True, formato="decimal", padrao=DECIMAL),
    # As três do incremento da revisão de `012` (FR-119). `forma` **não** admite nulo, e é o único
    # campo da Etapa publicada que não admite: nulo aqui criaria duas grafias canônicas para a mesma
    # versão — um snapshot com `null` e outro com `"PONTUADA"` descrevendo a mesma Etapa —, e a
    # versão existe para identificar uma forma só. A ausência é lida como pontuada apenas em
    # conteúdo anterior à 6, e quem a lê é `avaliacoes/domain/previsao.py` (FR-120).
    Campo("forma", str, valores=FORMAS),
    # Os rótulos são anuláveis porque neles o "não se aplica" é real: Etapa pontuada não nomeia
    # sentido nenhum. Que sejam obrigatórios na forma decisória é coerência **entre** campos, e
    # `Campo` não a expressa — ela vive em `_coerencia_das_etapas` (FR-121).
    Campo("rotuloFavoravel", str, admite_nulo=True),
    Campo("rotuloDesfavoravel", str, admite_nulo=True),
    Campo("scheduleEventId", str, admite_nulo=True, formato="uuid"),
)

# `content` e `source` **não entram**: dependem do tipo, e `Campo` não expressa coerência entre
# campos. A ausência é deliberada, e o que ela deixa de fora está em `_topologia_das_secoes`.
SECAO_PUBLICADA = (
    Campo("id", str, formato="uuid"),
    Campo("key", str),
    Campo("title", str),
    Campo("order", int, minimo=0),
    Campo("type", str, valores=(GERADA, TEXTUAL)),
)

COLECOES_PUBLICADAS = (
    ("profiles", PERFIL_PUBLICADO),
    ("schedule", EVENTO_PUBLICADO),
    ("stages", ETAPA_PUBLICADA),
    ("sections", SECAO_PUBLICADA),
    ("documentRequirements", DOCUMENTO_EXIGIDO_PUBLICADO),
)

CAMPO_AUSENTE = "field_required"
TIPO_INVALIDO = "field_type_invalid"
NULO_INVALIDO = "field_null_invalid"
FORMATO_INVALIDO = "field_format_invalid"
RESTRICAO_VIOLADA = "field_constraint_violated"

_NOME_DO_TIPO = {
    str: "texto",
    int: "número inteiro",
    bool: "booleano",
    list: "lista",
    dict: "objeto",
}


def _e_do_tipo(valor, tipo):
    """`bool` é subclasse de `int` em Python, e `True` não é um número de vagas."""
    if tipo is int and isinstance(valor, bool):
        return False
    return isinstance(valor, tipo)


# Formato declarado que não estivesse aqui levantaria `KeyError` na primeira verificação, e é o
# comportamento desejado: erro de programação que falha alto vale mais que formato aceito em
# silêncio por não ter quem o verifique.
_LEITOR_DE_FORMATO = {"uuid": UUID, "date-time": datetime.fromisoformat, "decimal": Decimal}


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
    except (ValueError, AttributeError, TypeError, InvalidOperation):
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


def _impeditivo(codigo, mensagem, caminho):
    return ValidationFinding(Severity.BLOCKING_ERROR, codigo, mensagem, caminho)


def _topologia_das_secoes(snapshot: dict) -> list[ValidationFinding]:
    """O catálogo fixo tem de continuar valendo **depois** da publicação (FR-041).

    A forma declarada confere um campo por vez e não expressa coerência entre campos. Sem esta
    verificação, uma Retificação faria sobre o conteúdo publicado o que a interface impede:
    acrescentar seção com `ADD /sections/-`, remover uma do catálogo, trocar `type`, `order`,
    `title` ou origem, esvaziar uma textual ou dar conteúdo a uma gerada. O catálogo valeria na
    elaboração e deixaria de valer exatamente onde mais importa.

    Só o `content` das seções textuais pode variar.
    """
    itens = snapshot.get("sections")
    if not isinstance(itens, list):
        return []  # A forma declarada já reporta coleção que não é lista.

    esperado = {secao.key: secao for secao in CATALOGO}
    presentes = [item.get("key") for item in itens if isinstance(item, dict)]
    findings = []
    for chave in sorted(set(presentes) - set(esperado)):
        findings.append(
            _impeditivo(
                RESTRICAO_VIOLADA,
                f"A seção '{chave}' não pertence ao catálogo do Edital.",
                "/sections",
            )
        )
    for chave in sorted(set(esperado) - set(presentes)):
        findings.append(
            _impeditivo(
                CAMPO_AUSENTE,
                f"A seção obrigatória '{chave}' não está presente.",
                "/sections",
            )
        )

    for posicao, item in enumerate(itens):
        if not isinstance(item, dict):
            continue
        secao = esperado.get(item.get("key"))
        if secao is None:
            continue
        caminho = _caminho_da_entidade("sections", item, posicao)
        for atributo, declarado in (
            ("title", secao.title),
            ("order", secao.order),
            ("type", secao.type),
        ):
            if item.get(atributo) != declarado:
                findings.append(
                    _impeditivo(
                        RESTRICAO_VIOLADA,
                        f"O campo diverge do catálogo em {caminho}/{atributo}.",
                        f"{caminho}/{atributo}",
                    )
                )
        if secao.gerada:
            if item.get("source") != secao.source:
                findings.append(
                    _impeditivo(
                        RESTRICAO_VIOLADA,
                        f"A origem diverge do catálogo em {caminho}/source.",
                        f"{caminho}/source",
                    )
                )
            if "content" in item:
                findings.append(
                    _impeditivo(
                        RESTRICAO_VIOLADA,
                        "A seção gerada não carrega conteúdo próprio: ele viria a divergir do "
                        f"dado que a origina, em {caminho}/content.",
                        f"{caminho}/content",
                    )
                )
        elif not (isinstance(item.get("content"), str) and item["content"].strip()):
            findings.append(
                _impeditivo(
                    CAMPO_AUSENTE,
                    f"A seção textual precisa de conteúdo em {caminho}/content.",
                    f"{caminho}/content",
                )
            )
    return findings


def _coerencia_dos_fatos(snapshot: dict) -> list[ValidationFinding]:
    """O fato publicado precisa ser identificável e ter tipo executável (D-2).

    **Por que o tipo é verificado na publicação, e não só na elaboração.** A Retificação altera
    conteúdo já público sem passar pelo rascunho: sem esta verificação, publicar-se-ia por
    Retificação um fato de tipo que o congelamento não sabe gravar nem o desempate comparar — e o
    defeito só apareceria no dia da classificação, sobre valores já congelados.
    """
    findings = []
    for posicao, perfil in enumerate(snapshot.get("profiles") or []):
        if not isinstance(perfil, dict):
            continue
        base = _caminho_da_entidade("profiles", perfil, posicao)
        codigos = []
        for indice, fato in enumerate(perfil.get("declaredFacts") or []):
            if not isinstance(fato, dict):
                continue
            chave = fato.get("id")
            dentro = f"id={chave}" if isinstance(chave, str) and chave else str(indice)
            caminho = f"{base}/declaredFacts/{dentro}"
            codigos.append(fato.get("code"))
            if fato.get("type") not in {"DATA", "INTEIRO"}:
                findings.append(
                    ValidationFinding(
                        Severity.BLOCKING_ERROR,
                        "declared_fact_type_invalid",
                        "O tipo de um fato declarado deve ser data ou número inteiro.",
                        f"{caminho}/type",
                    )
                )
        if len(codigos) != len(set(codigos)):
            findings.append(
                ValidationFinding(
                    Severity.BLOCKING_ERROR,
                    "declared_fact_code_duplicated",
                    "Fatos declarados não podem repetir código no Perfil.",
                    f"{base}/declaredFacts",
                )
            )
    return findings


def _arredondamento_do_marco(marco, caminho) -> list[ValidationFinding]:
    """A regra precisa estar completa **na publicação**, e não no dia em que alguém a executa.

    Sem esta recusa, um marco sem arredondamento declarado publicaria uma regra que só fica
    completa quando o cálculo escolhe um padrão — e aí o padrão seria do código, não do Edital
    (FR-068).
    """
    from processo_seletivo.classificacao.domain.combinacao import (
        RegraIncompleta,
        arredondamento_publicado,
    )

    try:
        arredondamento_publicado(marco)
    except RegraIncompleta as falta:
        return [
            ValidationFinding(
                Severity.BLOCKING_ERROR,
                "milestone_rounding_invalid",
                str(falta),
                f"{caminho}/rounding",
            )
        ]
    return []


def _divisor_do_marco(marco, etapas, caminho) -> list[ValidationFinding]:
    """Operação que divide pela soma dos pesos precisa de soma diferente de zero (FR-073).

    Recusar aqui é o que separa **regra inválida do Edital** de **ausência de dado do
    participante**. Sem isto, o cálculo devolveria "não classificável" para todo mundo, e quem
    lesse a ordem concluiria que os participantes é que estavam incompletos.
    """
    from processo_seletivo.classificacao.domain.combinacao import divide_pela_soma_dos_pesos

    if not divide_pela_soma_dos_pesos(marco):
        return []
    soma = Decimal("0")
    for etapa_id in marco.get("stages") or []:
        etapa = etapas.get(etapa_id) or {}
        peso = etapa.get("weight")
        if peso is not None:
            soma += Decimal(str(peso))
    if soma != 0:
        return []
    return [
        ValidationFinding(
            Severity.BLOCKING_ERROR,
            "milestone_zero_divisor",
            "A operação do marco divide pela soma dos pesos, e as Etapas enumeradas somam zero: "
            "não há divisor.",
            f"{caminho}/operation",
        )
    ]


def _coerencia_dos_marcos(snapshot: dict) -> list[ValidationFinding]:
    """O marco só é executável se o que ele aponta existir e puder ser apontado (015, D-001).

    Três recusas, e as três dependem do **conteúdo inteiro** — por isso vivem aqui, e não na
    validação de elaboração do Perfil, que enxerga só o Perfil:

    - Etapa enumerada que não existe no mesmo conteúdo: o marco somaria o que ninguém publicou;
    - Etapa enumerada que não é classificatória: o Edital declarou que ela não classifica, e
      contá-la seria o sistema contradizendo o Edital (FR-010);
    - critério que aponta Etapa ou fato inexistente (FR-017). É **aqui** que o critério pendurado é
      impedido, e é por isso que ele não é estado que a tela precise tratar depois: uma Retificação
      que remova a Etapa enumerada sem ajustar o marco não publica (FR-043).

    Pelo mesmo caminho de `_faixa_do_percentual`: função dedicada, porque `COLECOES_PUBLICADAS` só
    percorre coleções de raiz e não desce para dentro do Perfil.
    """
    findings = []
    etapas = {
        etapa.get("id"): etapa
        for etapa in (snapshot.get("stages") or [])
        if isinstance(etapa, dict)
    }
    for posicao, perfil in enumerate(snapshot.get("profiles") or []):
        if not isinstance(perfil, dict):
            continue
        base = _caminho_da_entidade("profiles", perfil, posicao)
        fatos = {
            fato.get("id") for fato in (perfil.get("declaredFacts") or []) if isinstance(fato, dict)
        }
        for indice, marco in enumerate(perfil.get("classificationMilestones") or []):
            if not isinstance(marco, dict):
                continue
            chave = marco.get("id")
            dentro = f"id={chave}" if isinstance(chave, str) and chave else str(indice)
            caminho = f"{base}/classificationMilestones/{dentro}"
            findings.extend(_arredondamento_do_marco(marco, caminho))
            if not marco.get("stages"):
                findings.append(
                    ValidationFinding(
                        Severity.BLOCKING_ERROR,
                        "milestone_without_stage",
                        "O marco classificatório não enumera Etapa alguma: sem Etapa não há "
                        "pontuação a combinar, e a ordem não sai.",
                        f"{caminho}/stages",
                    )
                )
            findings.extend(_divisor_do_marco(marco, etapas, caminho))
            for etapa_id in marco.get("stages") or []:
                etapa = etapas.get(etapa_id)
                if etapa is not None and etapa.get("weight") is None:
                    findings.append(
                        ValidationFinding(
                            Severity.BLOCKING_ERROR,
                            "milestone_stage_without_weight",
                            "O marco enumera uma Etapa sem peso declarado. Quem enumera declara o "
                            "peso: ausência não é equivalência, e o cálculo não a interpreta.",
                            f"{caminho}/stages",
                        )
                    )
                if etapa is None:
                    findings.append(
                        ValidationFinding(
                            Severity.BLOCKING_ERROR,
                            "milestone_stage_missing",
                            "O marco classificatório enumera uma Etapa que não existe no Edital.",
                            f"{caminho}/stages",
                        )
                    )
                elif not etapa.get("classificatory"):
                    findings.append(
                        ValidationFinding(
                            Severity.BLOCKING_ERROR,
                            "milestone_stage_not_classificatory",
                            "O marco classificatório enumera uma Etapa que o Edital não publicou "
                            "como classificatória.",
                            f"{caminho}/stages",
                        )
                    )
            for criterio in marco.get("tiebreakers") or []:
                if not isinstance(criterio, dict):
                    continue
                parametros = criterio.get("parameters") or {}
                alvo_etapa = parametros.get("stageId")
                if alvo_etapa is not None and alvo_etapa not in etapas:
                    findings.append(
                        ValidationFinding(
                            Severity.BLOCKING_ERROR,
                            "tiebreaker_stage_missing",
                            "Um critério de desempate aponta Etapa que não existe no Edital.",
                            f"{caminho}/tiebreakers",
                        )
                    )
                alvo_fato = parametros.get("factId")
                if alvo_fato is not None and alvo_fato not in fatos:
                    findings.append(
                        ValidationFinding(
                            Severity.BLOCKING_ERROR,
                            "tiebreaker_fact_missing",
                            "Um critério de desempate aponta fato declarado que não existe "
                            "no Perfil.",
                            f"{caminho}/tiebreakers",
                        )
                    )
                if not (parametros.get("stageId") or parametros.get("factId")):
                    findings.append(
                        ValidationFinding(
                            Severity.BLOCKING_ERROR,
                            "tiebreaker_without_target",
                            "Um critério de desempate não declara o que compara: falta a Etapa ou "
                            "o fato declarado que ele consome.",
                            f"{caminho}/tiebreakers",
                        )
                    )
                if not criterio.get("whenMissing"):
                    findings.append(
                        ValidationFinding(
                            Severity.BLOCKING_ERROR,
                            "tiebreaker_missing_behaviour",
                            "Um critério de desempate não declara o que fazer quando o valor "
                            "que ele consome não existe.",
                            f"{caminho}/tiebreakers",
                        )
                    )
    return findings


def _faixa_do_percentual(snapshot: dict) -> list[ValidationFinding]:
    """FR-030 vale também **depois** da publicação.

    A forma declarada confere que cada item de `competitionModalities` é objeto e nada dentro dele
    — decisão registrada em `PERFIL_PUBLICADO`, e mantida. O efeito é que a faixa do percentual
    valia na gravação do rascunho e deixava de valer na Retificação, que é justamente onde o
    conteúdo muda depois de público: publicava-se por Retificação uma cota de zero por cento, ou de
    cento e cinquenta, que a interface e a API de rascunho recusam.

    A regra é a mesma de `validate_normative_rule`, invocada aqui e não reescrita: duas cópias da
    faixa divergiriam, e é exatamente por não repetir a regra que esta verificação não vira um
    segundo domínio.
    """
    findings = []
    for posicao, perfil in enumerate(snapshot.get("profiles") or []):
        if not isinstance(perfil, dict):
            continue
        base = _caminho_da_entidade("profiles", perfil, posicao)
        modalidades = perfil.get("competitionModalities")
        if not isinstance(modalidades, list):
            continue
        for indice, modalidade in enumerate(modalidades):
            if not isinstance(modalidade, dict):
                continue
            regra = modalidade.get("normativeRule")
            if not isinstance(regra, dict):
                continue
            chave = modalidade.get("id")
            dentro = f"id={chave}" if isinstance(chave, str) and chave else str(indice)
            caminho = f"{base}/competitionModalities/{dentro}"
            try:
                validate_normative_rule(regra)
            except ProfileValidationError as exc:
                findings.append(
                    _impeditivo(
                        RESTRICAO_VIOLADA,
                        f"{exc} Em {caminho}/normativeRule/percentage.",
                        f"{caminho}/normativeRule/percentage",
                    )
                )
    return findings


def _coerencia_das_etapas(snapshot: dict) -> list[ValidationFinding]:
    """Uma passagem, três conferências (FR-020 e FR-022).

    A forma declarada confere que `scheduleEventId` é um UUID, não que ele **exista**; e o padrão
    decimal descreve a forma de `weight` e `minimumScore`, não a faixa. As três coisas ficam aqui,
    onde a coleção já é percorrida.
    """
    itens = snapshot.get("stages")
    if not isinstance(itens, list):
        return []

    eventos = {
        evento.get("id") for evento in (snapshot.get("schedule") or []) if isinstance(evento, dict)
    }
    findings = []
    for posicao, item in enumerate(itens):
        if not isinstance(item, dict):
            continue
        caminho = _caminho_da_entidade("stages", item, posicao)
        referencia = item.get("scheduleEventId")
        if referencia is not None and referencia not in eventos:
            findings.append(
                _impeditivo(
                    RESTRICAO_VIOLADA,
                    "A Etapa referencia um Evento que não existe no Cronograma, em "
                    f"{caminho}/scheduleEventId.",
                    f"{caminho}/scheduleEventId",
                )
            )
        for atributo, minimo, mensagem in (
            ("weight", None, "O peso da Etapa deve ser maior que zero em"),
            ("minimumScore", 0, "A nota mínima da Etapa não pode ser negativa em"),
            ("maximumScore", None, "A pontuação máxima da Etapa deve ser maior que zero em"),
        ):
            valor = _decimal_ou_none(item.get(atributo))
            fora = valor is not None and (valor <= 0 if minimo is None else valor < minimo)
            if fora:
                findings.append(
                    _impeditivo(
                        RESTRICAO_VIOLADA,
                        f"{mensagem} {caminho}/{atributo}.",
                        f"{caminho}/{atributo}",
                    )
                )
        # A aplicabilidade por forma (FR-119, FR-121). `Campo` valida um campo por vez e não
        # expressa isto: publicar `maximumScore = 100` numa Etapa que não pontua seria a regra
        # normativa fictícia que P-007 existe para impedir, e uma Etapa decisória sem rótulo
        # publicaria um juízo que ninguém sabe ler.
        #
        # **São três estados, e não dois.** O rótulo é exigido numa forma e proibido na outra; a
        # nota é proibida na decisória e apenas **admitida** na pontuada — Etapa pontuada sem nota
        # mínima nem máxima é legítima, e é o que FR-066 chama de limite não declarado. Tratar
        # "admitido" como "exigido" recusaria Edital que o sistema publica desde a 012.
        #
        # "Proibido" significa **nulo**, e nunca ausente: no conteúdo publicado toda chave da Etapa
        # está sempre lá, e o que se recusa é o valor.
        decisoria = item.get("forma") == "DECISORIA"
        for atributo, exigido, proibido, recusa in (
            ("rotuloFavoravel", decisoria, not decisoria, ROTULO),
            ("rotuloDesfavoravel", decisoria, not decisoria, ROTULO),
            ("minimumScore", False, decisoria, NOTA),
            ("maximumScore", False, decisoria, NOTA),
        ):
            valor = item.get(atributo)
            # Rótulo em branco não é rótulo: um documento com `""` no lugar do indeferimento não
            # diz nada a quem lê o Edital. Para os decimais, `strip` não se aplica.
            presente = valor.strip() != "" if isinstance(valor, str) else valor is not None
            if exigido and not presente:
                findings.append(
                    _impeditivo(
                        RESTRICAO_VIOLADA,
                        f"A Etapa decisória deve publicar os rótulos do resultado em "
                        f"{caminho}/{atributo}.",
                        f"{caminho}/{atributo}",
                    )
                )
            elif proibido and presente:
                findings.append(
                    _impeditivo(
                        RESTRICAO_VIOLADA, f"{recusa}{caminho}/{atributo}.", f"{caminho}/{atributo}"
                    )
                )

        # Coerência entre os dois, e não faixa de um só: nota mínima acima da máxima descreveria
        # uma Etapa em que ninguém pode ser aprovado. Vale só na forma pontuada, porque é a única
        # em que os dois existem (012, FR-033, FR-121).
        minima = _decimal_ou_none(item.get("minimumScore"))
        maxima = _decimal_ou_none(item.get("maximumScore"))
        if minima is not None and maxima is not None and minima > maxima:
            findings.append(
                _impeditivo(
                    RESTRICAO_VIOLADA,
                    "A nota mínima da Etapa não pode superar a pontuação máxima em "
                    f"{caminho}/minimumScore.",
                    f"{caminho}/minimumScore",
                )
            )
    return findings


def _decimal_ou_none(valor):
    """Valor fora da forma decimal não é assunto daqui: a forma declarada já o reporta."""
    try:
        return None if valor is None else Decimal(valor)
    except (ValueError, TypeError, InvalidOperation):
        return None


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
    findings.extend(_topologia_das_secoes(snapshot))
    findings.extend(_coerencia_das_etapas(snapshot))
    findings.extend(_faixa_do_percentual(snapshot))
    findings.extend(_coerencia_dos_fatos(snapshot))
    findings.extend(_coerencia_dos_marcos(snapshot))
    findings.extend(_periodo_de_inscricoes(snapshot))
    findings.extend(_coerencia_dos_documentos_exigidos(snapshot))
    return findings


def _periodo_de_inscricoes(snapshot: dict) -> list[ValidationFinding]:
    """Um período, no máximo — e nenhum é aviso, não impedimento (FR-004 da 009).

    A constraint do banco garante um por Cronograma na elaboração. Ela não alcança o conteúdo
    publicado: duas Retificações sucessivas marcam dois Eventos, cada uma partindo de uma versão
    em que só o outro estava marcado, e o resultado passaria sem que nada acusasse. A publicação é
    onde esse estado para.

    A ausência de marca é caso legítimo: nem todo Edital abre inscrição por este sistema nesta
    versão. Ele continua publicável, e simplesmente não recebe inscrições.
    """
    eventos = snapshot.get("schedule")
    if not isinstance(eventos, list):
        return []
    # Item malformado é assunto da forma declarada, que já o reporta. Aqui ele é ignorado para
    # que a coerência não vire um segundo relato do mesmo defeito — nem uma exceção.
    marcados = [
        evento
        for evento in eventos
        if isinstance(evento, dict) and evento.get("isRegistrationPeriod") is True
    ]
    if len(marcados) > 1:
        return [
            _impeditivo(
                "registration_period_ambiguous",
                "Mais de um Evento do Cronograma está marcado como período de inscrições. "
                f"São {len(marcados)}, e o Edital precisa de um só.",
                "/schedule",
            )
        ]
    if not marcados:
        return [
            ValidationFinding(
                Severity.WARNING,
                "registration_period_missing",
                "Nenhum Evento do Cronograma está marcado como período de inscrições. "
                "O Edital será publicado, mas não receberá inscrições pelo sistema.",
                "/schedule",
            )
        ]
    return []


def _coerencia_dos_documentos_exigidos(snapshot: dict) -> list[ValidationFinding]:
    """Requisito inaplicável nunca seria pedido a ninguém — e ninguém perceberia (FR-006 da 009).

    A elaboração já recusa Perfil e modalidade alheios. Aqui a mesma regra vale sobre o conteúdo
    que passa a vigorar, porque uma Retificação alcança tanto o requisito quanto o Perfil que ele
    aponta: remover o Perfil deixaria para trás um documento restrito a nada.
    """
    requisitos = snapshot.get("documentRequirements")
    if not isinstance(requisitos, list):
        return []
    perfis = {
        str(perfil.get("id")): perfil
        for perfil in snapshot.get("profiles") or []
        if isinstance(perfil, dict) and perfil.get("id")
    }
    findings = []
    for indice, documento in enumerate(requisitos):
        if not isinstance(documento, dict):
            continue
        caminho = f"/documentRequirements/{indice}"
        perfil_id = documento.get("profileId")
        modalidade_id = documento.get("modalityId")
        if perfil_id is not None and str(perfil_id) not in perfis:
            findings.append(
                _impeditivo(
                    "document_requirement_profile_unknown",
                    f"O Documento Exigido '{documento.get('name', '')}' restringe-se a um Perfil "
                    "que não existe neste Edital.",
                    caminho,
                )
            )
            continue
        if modalidade_id is None:
            continue
        alcance = [perfis[str(perfil_id)]] if perfil_id is not None else perfis.values()
        modalidades = {
            str(modalidade.get("id"))
            for perfil in alcance
            for modalidade in perfil.get("competitionModalities") or []
        }
        if str(modalidade_id) not in modalidades:
            findings.append(
                _impeditivo(
                    "document_requirement_modality_unknown",
                    f"O Documento Exigido '{documento.get('name', '')}' restringe-se a uma "
                    "modalidade que não existe no alcance declarado.",
                    caminho,
                )
            )
    return findings


def blocking_findings(findings):
    return [item for item in findings if item.severity == Severity.BLOCKING_ERROR]
