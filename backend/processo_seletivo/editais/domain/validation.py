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

import math
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
    # O quadro de vagas da `025`. Sempre presente depois do degrau 12 — vazio nos Editais
    # anteriores —, porque duas grafias para a ausência, chave ausente e lista vazia, é o que a
    # D-005 existe para não permitir.
    Campo("vacancyTable", list, tipo_do_item=dict),
)

# **A forma de dentro da linha É declarada**, ao contrário da de `competitionModalities`, que é a
# única coleção do snapshot cuja forma interna não é. A diferença é o argumento e não uma
# inconsistência: a linha carrega um número que a conferência da FR-161 vai **somar**, e somar
# campo não verificado é somar o que ninguém garantiu ser inteiro (025, R-013).
LINHA_DO_QUADRO_PUBLICADA = (
    Campo("id", str, formato="uuid"),
    Campo("modalityId", str, admite_nulo=True, formato="uuid"),
    Campo("immediateVacancies", int, minimo=0),
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
    # O Anexo que serve de modelo para este requisito, ou nulo (020, FR-020). Aponta a identidade
    # do **Anexo**, e nunca a do artefato: o artefato é o que aquela versão diz que o Anexo é, e
    # trocá-lo por Retificação não pode obrigar a reescrever o requisito que o cita.
    Campo("attachmentId", str, admite_nulo=True, formato="uuid"),
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

# O Anexo do Edital (020). Quatro campos e nenhum a mais, porque o sistema não conhece o que há
# dentro do artefato: o rótulo é texto único escrito pelo autor — designação e título juntos, sem
# campo separado que convidasse a derivar o numeral da posição (FR-005, FR-006) —, a ordem é campo
# próprio, e o par identidade-do-artefato mais resumo é o que liga a versão aos bytes. O resumo
# **verifica**; quem endereça é `artifactId`, porque dois artefatos de conteúdo idêntico são
# legítimos e o resumo não distingue os dois (FR-011).
ANEXO_PUBLICADO = (
    Campo("id", str, formato="uuid"),
    Campo("label", str),
    Campo("order", int, minimo=0),
    Campo("artifactId", str, formato="uuid"),
    # A grafia do SHA-256 é verificada como a do decimal e a do instante já são: sem ela, um resumo
    # truncado ou em maiúsculas atravessaria a publicação e só falharia na hora de comparar bytes.
    Campo("artifactHash", str, padrao="^[0-9a-f]{64}$"),
)

COLECOES_PUBLICADAS = (
    ("profiles", PERFIL_PUBLICADO),
    ("schedule", EVENTO_PUBLICADO),
    ("stages", ETAPA_PUBLICADA),
    ("sections", SECAO_PUBLICADA),
    ("attachments", ANEXO_PUBLICADO),
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
    parcelas = 0
    for etapa_id in marco.get("stages") or []:
        etapa = etapas.get(etapa_id) or {}
        if etapa.get("forma") == "DECISORIA":
            continue
        parcelas += 1
        peso = etapa.get("weight")
        if peso is not None:
            soma += Decimal(str(peso))
    # Marco sem parcela numérica não divide coisa alguma: a pontuação combinada é nula, e não há
    # divisor a exigir (FR-077). Recusá-lo aqui impediria uma ordenação legítima.
    if parcelas == 0 or soma != 0:
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
        findings.extend(_corte_em_dois_marcos(perfil, base=base))
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
            findings.extend(
                _regra_de_corte_do_marco(marco, perfil=perfil, etapas=etapas, caminho=caminho)
            )
            for etapa_id in marco.get("stages") or []:
                etapa = etapas.get(etapa_id)
                # Peso é cobrado de **parcela**, e não de porta: a Etapa decisória não soma, e
                # exigir peso dela seria exigir a declaração de um número que a regra não usa
                # (FR-067, FR-074).
                if (
                    etapa is not None
                    and etapa.get("forma") != "DECISORIA"
                    and etapa.get("weight") is None
                ):
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


def _regra_de_corte_do_marco(marco, *, perfil, etapas, caminho) -> list[ValidationFinding]:
    """As declarações que o sistema não pode concluir por ninguém (014, FR-182, FR-224, FR-226).

    Quatro dos seis campos da regra existem porque **não há padrão honesto** para eles. Resolver a
    ausência por conta própria afirmaria norma que ninguém escreveu — e as duas saídas fáceis do
    empate são o exemplo: admitir o excedente entrega à Etapa seguinte mais gente do que a comissão
    dimensionou, e parar no alvo corta alguém por desempate que a norma não previu.
    """
    from processo_seletivo.classificacao.domain import faixa

    regra = marco.get("cutRule")
    if not regra:
        return []
    findings = _forma_do_alvo(regra, caminho=caminho)
    if regra.get("tieOutcome") not in faixa.DESFECHOS_DE_EMPATE:
        findings.append(
            _impeditivo(
                "cut_rule_sem_desfecho_de_empate",
                "A regra de corte não declara o que acontece com o empate que atravessa a última "
                "posição da faixa. O sistema não escolhe por ela.",
                f"{caminho}/cutRule/tieOutcome",
            )
        )
    if regra.get("continuation") not in faixa.POLITICAS_DE_CONTINUACAO:
        findings.append(
            _impeditivo(
                "cut_rule_sem_politica_de_continuacao",
                "A regra de corte não declara se este Edital admite continuação além da faixa "
                "publicada.",
                f"{caminho}/cutRule/continuation",
            )
        )
    declarada = regra.get("governedStage")
    if not declarada:
        findings.append(
            _impeditivo(
                "cut_rule_sem_etapa_governada",
                "A regra de corte não declara qual Etapa o corte alimenta. Ela não é inferida de "
                "lugar nenhum: declare a Etapa, ou declare que este corte não governa nenhuma.",
                f"{caminho}/cutRule/governedStage",
            )
        )
    elif declarada != faixa.SEM_ETAPA_GOVERNADA:
        if str(declarada) not in etapas:
            findings.append(
                _impeditivo(
                    "cut_rule_com_etapa_inexistente",
                    "A regra de corte declara governar uma Etapa que este Edital não publica.",
                    f"{caminho}/cutRule/governedStage",
                )
            )
        # **A guarda é de circularidade, e não de ordem** (FR-229). Num marco cuja ordem é computada
        # a partir de Etapas, governar uma das Etapas que a alimentam fecharia laço: o universo da
        # ordem passaria a depender do corte que ela mesma produz. Num marco que ordena por sorteio
        # não há laço — a ordem vem da relação de habilitados —, e governar a Etapa que o marco
        # enumera é o **caso normal**: é a forma do 77/2026, em que não existe Etapa avaliada antes
        # do sorteio e a única que existe é a análise documental que o corte alimenta. Uma guarda
        # escrita como "a Etapa governada deve suceder a ordem do marco" tornaria aquele Edital
        # impublicável.
        elif not marco.get("drawMethod") and str(declarada) in {
            str(item) for item in (marco.get("stages") or [])
        }:
            findings.append(
                _impeditivo(
                    "cut_rule_com_etapa_circular",
                    "A regra de corte governa uma Etapa que alimenta a própria ordem do marco: o "
                    "universo da ordem passaria a depender do corte que ela produz.",
                    f"{caminho}/cutRule/governedStage",
                )
            )
    findings.extend(_quadro_para_o_corte(regra, perfil=perfil, caminho=caminho))
    return findings


def _forma_do_alvo(regra, *, caminho) -> list[ValidationFinding]:
    """A espécie e a aritmética do alvo, **também** na publicação (014, FR-179).

    Elas já são recusadas na elaboração, e repeti-las aqui não é redundância: a **Retificação não
    passa por `validate_profiles`**. `retificacoes.py` afere o conteúdo produzido apenas por
    `validate_for_publication`, e sem esta conferência uma Retificação poderia gravar
    `targetCount: -5` — ou nulo, com espécie fixa — e publicar. Na emissão, o alvo apurado viraria
    zero e o corte sairia com **ninguém** progredindo, em silêncio, sobre um Edital cuja norma
    publicada diz outra coisa. É a mesma razão pela qual a conferência da soma do quadro mora aqui.
    """
    from processo_seletivo.classificacao.domain import faixa

    especie = regra.get("targetKind")
    if especie not in faixa.ESPECIES_DE_ALVO:
        return [
            _impeditivo(
                "cut_rule_sem_especie_de_alvo",
                "A regra de corte não declara a espécie do alvo: uma quantidade fixa, ou a "
                "quantidade que o quadro de vagas do recorte publica.",
                f"{caminho}/cutRule/targetKind",
            )
        ]
    findings = []
    alvo = regra.get("targetCount")
    if especie == faixa.ALVO_FIXO and alvo is None:
        findings.append(
            _impeditivo(
                "cut_rule_sem_alvo",
                "A regra de corte declara alvo fixo e não diz quantos.",
                f"{caminho}/cutRule/targetCount",
            )
        )
    if especie == faixa.ALVO_DO_QUADRO and alvo is not None:
        findings.append(
            _impeditivo(
                "cut_rule_com_alvo_duplicado",
                "A regra de corte deriva o alvo do quadro de vagas e ainda assim declara uma "
                "quantidade fixa: o alvo tem uma fonte só.",
                f"{caminho}/cutRule/targetCount",
            )
        )
    for campo in ("targetCount", "surplusCount"):
        valor = regra.get(campo)
        if valor is None:
            continue
        if isinstance(valor, bool) or not isinstance(valor, int) or valor < 0:
            findings.append(
                _impeditivo(
                    "cut_rule_com_quantidade_invalida",
                    "As quantidades da regra de corte devem ser números inteiros não negativos.",
                    f"{caminho}/cutRule/{campo}",
                )
            )
    return findings


def _quadro_para_o_corte(regra, *, perfil, caminho) -> list[ValidationFinding]:
    """Alvo derivado exige linha de quadro para **todo recorte que o marco ordena** (014, FR-183).

    A `025` admite quadro parcial de propósito, e a regra de corte é do **marco**, que pode ordenar
    três listas. Sem esta conferência, um Edital com quadro parcial publicaria uma regra derivada
    inexequível na lista sem linha — e o defeito apareceria no dia da emissão, sob cronograma, com a
    correção dependendo de Retificação.

    **O que se exige aqui é a linha geral, e a restrição a ela é achado desta implementação.** A
    `D-014` da spec manda exigir linha para **todo recorte que o marco ordena**, e a leitura óbvia —
    a geral mais cada Modalidade declarada — torna impublicável o Edital no **formato normal**. A
    `025` documenta por quê: o Edital normal declara **também** uma Modalidade chamada "Ampla
    concorrência", e a `FR-176` daquela feature **proíbe** dar linha reservada a ela, porque a
    quantidade dela mora na linha geral. Essa Modalidade nunca terá linha, por norma — e exigi-la
    recusaria o 57/2026 e o 28/2026, que são justamente os Editais que usam alvo derivado.

    Identificá-la mecanicamente exigiria casar o nome, e a `025` recusou isso por escrito na sua
    `R-006`: seria decidir no plano uma questão que a spec declarou aberta, e erraria em Edital que
    chame a Modalidade de outra coisa. Copiar aqui aquela heurística seria copiar o que não se fez.

    **Sobra a metade que é sempre verdadeira**, e não é pouca: a linha geral é o recorte da ampla
    concorrência, todo marco a ordena, e sem ela o alvo derivado não tem de onde sair em recorte
    nenhum. O recorte por Modalidade é conferido **na emissão**, onde a lista é conhecida — é o que
    a `D-014` recusou por preferir a publicação, e a recusa foi tomada sem esta informação.

    Linha **zerada** é declaração legítima e publica; o que impede é a ausência.
    """
    from processo_seletivo.classificacao.domain import faixa

    if regra.get("targetKind") != faixa.ALVO_DO_QUADRO:
        return []
    linhas = perfil.get("vacancyTable") or []
    tem_linha_geral = any(
        isinstance(linha, dict) and not linha.get("modalityId") for linha in linhas
    )
    if tem_linha_geral:
        return []
    return [
        _impeditivo(
            "cut_rule_sem_linha_de_quadro",
            "A regra de corte deriva o alvo do quadro de vagas, e o Perfil não publica a linha "
            "geral — a da ampla concorrência, de onde o alvo sai em todo recorte sem lista.",
            f"{caminho}/cutRule/targetKind",
        )
    ]


def _corte_em_dois_marcos(perfil, *, base) -> list[ValidationFinding]:
    """Duas regras de corte do mesmo Perfil não governam a mesma Etapa (014, R-006).

    A Etapa governada decide quem participa dela, e duas declarações com alvos distintos não têm
    desempate possível. Não se escolhe uma: recusa-se o Edital que as publica. Unir as faixas
    aplicaria a soma de dois alvos que ninguém publicou, e "o marco de maior ordem vence" inventaria
    precedência normativa.

    **É dentro do Perfil**, e não do Edital: a Etapa é do Edital e alcança todos os Perfis, mas cada
    inscrição pertence a um Perfil só, e é a regra dele que a governa.
    """
    from processo_seletivo.classificacao.domain import faixa

    governadas = {}
    for marco in perfil.get("classificationMilestones") or []:
        if not isinstance(marco, dict):
            continue
        etapa = faixa.etapa_governada(marco.get("cutRule"))
        if etapa:
            governadas.setdefault(etapa, []).append(marco.get("code") or marco.get("id"))
    return [
        _impeditivo(
            "cut_rule_em_dois_marcos_da_mesma_etapa",
            f"Os marcos {' e '.join(str(item) for item in marcos)} declaram governar a mesma "
            "Etapa, com regras de corte que podem divergir.",
            f"{base}/classificationMilestones",
        )
        for etapa, marcos in governadas.items()
        if len(marcos) > 1
    ]


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
    findings.extend(_coerencia_dos_anexos(snapshot))
    findings.extend(_coerencia_do_quadro_de_vagas(snapshot))
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


def _coerencia_dos_anexos(snapshot: dict) -> list[ValidationFinding]:
    """O que impede publicar um Edital cujos anexos não estão de pé (020, FR-005, FR-023).

    Três regras, e a terceira é a que dá nome à feature. **Rótulo vazio** é impeditivo porque o
    documento publicado cita o anexo por ele: sem rótulo, o Edital manda o candidato a um anexo que
    não tem nome. **Referência pendurada** é impeditivo porque um requisito que aponta anexo
    inexistente é exatamente o defeito que a `020` veio corrigir, entrando pela porta de trás — a
    Retificação que remove o anexo e esquece o vínculo.

    **Rótulo repetido é aviso, e não impedimento**, porque rótulo não é identidade: dois anexos
    podem legitimamente se chamar igual — o Edital que publica dois modelos de declaração sob o
    mesmo título —, e recusar a publicação por isso seria o sistema decidindo redação por norma.
    """
    anexos = snapshot.get("attachments")
    if not isinstance(anexos, list):
        return []
    findings = []
    identidades = set()
    vistos = {}
    for indice, anexo in enumerate(anexos):
        if not isinstance(anexo, dict):
            continue
        caminho = _caminho_da_entidade("attachments", anexo, indice)
        identidades.add(str(anexo.get("id")))
        rotulo = anexo.get("label")
        if not isinstance(rotulo, str) or not rotulo.strip():
            findings.append(
                _impeditivo(
                    "attachment_label_required",
                    "O Anexo precisa de rótulo: é por ele que o Edital o cita.",
                    caminho,
                )
            )
        elif rotulo.strip() in vistos:
            findings.append(
                ValidationFinding(
                    Severity.WARNING,
                    "attachment_duplicate_label",
                    f"Dois Anexos têm o mesmo rótulo: '{rotulo.strip()}'.",
                    caminho,
                )
            )
        else:
            vistos[rotulo.strip()] = indice
    for indice, documento in enumerate(snapshot.get("documentRequirements") or []):
        if not isinstance(documento, dict):
            continue
        vinculo = documento.get("attachmentId")
        if vinculo is not None and str(vinculo) not in identidades:
            findings.append(
                _impeditivo(
                    "attachment_reference_dangling",
                    f"O Documento Exigido '{documento.get('name', '')}' aponta um Anexo que não "
                    "existe nesta versão do Edital.",
                    _caminho_da_entidade("documentRequirements", documento, indice),
                )
            )
    return findings


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


def _coerencia_do_quadro_de_vagas(snapshot: dict) -> list[ValidationFinding]:
    """O quadro de vagas depois da publicação: referência, soma e advertência (025).

    **A conferência vale sobre o conteúdo que uma Retificação produziria**, e é isso que a faz
    alcançar os dois pares de movimentos que a feature exige. Remover a Modalidade **e** a linha no
    mesmo ato passa; remover só a Modalidade é recusado (D-008). Reduzir a linha da PPI **e** o
    total do Perfil no mesmo ato passa; reduzir só a linha é recusado (FR-161). Verificar o
    resultado, e não a operação, é o que faz as duas coisas serem verdadeiras sem código de
    orquestração nenhum: `retificacoes.py` e `publish_edital.py` já chamam esta função.

    **A igualdade só roda em quadro completo; o limite superior roda sempre.** Somar menos que o
    total é legítimo num quadro parcial — o Edital declarou parte da repartição e não a toda
    (D-006). Somar **mais** não é legítimo em quadro algum: nenhum Edital reserva mais vagas do que
    oferece, e essa metade não precisa esperar pela completude (FR-177). É ela que alcança o Edital
    que declara uma Modalidade chamada "Ampla concorrência" e que, por seguir a FR-176, nunca fica
    completo — a lacuna que sobra está registrada em `research.md`, R-006.

    **A advertência do percentual nunca bloqueia e nunca escreve.** A FR-157 proíbe derivar,
    calcular ou recalcular quantidade a partir de percentual; a D-003 autoriza advertir e nada
    além. Ela compara e reporta — e aceita o arredondamento em qualquer direção, porque `Q 1` e
    `PCD 1` de um Edital real saem de arredondamento sobre censo.
    """
    findings = []
    for posicao, perfil in enumerate(snapshot.get("profiles") or []):
        if not isinstance(perfil, dict):
            continue
        linhas = perfil.get("vacancyTable")
        if not isinstance(linhas, list) or not linhas:
            # Quadro ausente é o que **todo** Edital publicado antes do degrau 12 afirma, e ele
            # continua publicável: ausência não é zero (D-005, FR-160).
            continue
        base = _caminho_da_entidade("profiles", perfil, posicao)
        modalidades = {
            str(modalidade.get("id")): modalidade
            for modalidade in perfil.get("competitionModalities") or []
            if isinstance(modalidade, dict) and modalidade.get("id")
        }
        total = perfil.get("immediateVacancies")
        rotulo = perfil.get("code") or perfil.get("name") or ""

        soma = 0
        com_linha = set()
        tem_linha_geral = False
        for indice, linha in enumerate(linhas):
            if not isinstance(linha, dict):
                findings.append(
                    _impeditivo(
                        TIPO_INVALIDO,
                        f"O item deveria ser objeto em {base}/vacancyTable/{indice}.",
                        f"{base}/vacancyTable/{indice}",
                    )
                )
                continue
            caminho = f"{base}/vacancyTable/{_dentro(linha, indice)}"
            # A forma de dentro da linha, campo a campo. `COLECOES_PUBLICADAS` só percorre coleções
            # de **raiz**, e o quadro é aninhado no Perfil — é o mesmo caminho que a coerência dos
            # marcos e a faixa do percentual já tomam.
            findings.extend(
                achado
                for campo in LINHA_DO_QUADRO_PUBLICADA
                if (achado := _violacao(campo, linha, f"{caminho}/{campo.nome}")) is not None
            )
            quantidade = linha.get("immediateVacancies")
            if isinstance(quantidade, int) and not isinstance(quantidade, bool):
                soma += quantidade
            modalidade_id = linha.get("modalityId")
            if modalidade_id is None:
                # A unicidade vale **também** depois da publicação: a elaboração a garante por
                # constraint parcial, e a constraint não alcança o conteúdo publicado. Duas
                # Retificações sucessivas, cada uma partindo de uma versão em que só uma linha
                # geral existia, produziriam duas — e o quadro afirmaria a ampla concorrência duas
                # vezes, com números diferentes (FR-154, invariante 2 da §5).
                if tem_linha_geral:
                    findings.append(
                        _impeditivo(
                            "vacancy_general_row_duplicated",
                            f"O quadro do Perfil '{rotulo}' declara mais de uma linha de ampla "
                            "concorrência, e ela tem uma linha só.",
                            caminho,
                        )
                    )
                tem_linha_geral = True
                continue
            modalidade_id = str(modalidade_id)
            if modalidade_id in com_linha:
                # Pela mesma razão da linha geral, um nível abaixo (FR-155).
                findings.append(
                    _impeditivo(
                        "vacancy_modality_row_duplicated",
                        f"O quadro do Perfil '{rotulo}' declara mais de uma linha para a mesma "
                        "modalidade, e cada uma tem no máximo uma.",
                        caminho,
                    )
                )
            if modalidade_id not in modalidades:
                findings.append(
                    _impeditivo(
                        "vacancy_row_modality_missing",
                        f"A linha de {quantidade} vaga(s) do quadro do Perfil '{rotulo}' aponta "
                        "uma modalidade que não existe neste Perfil.",
                        caminho,
                    )
                )
                continue
            com_linha.add(modalidade_id)
            findings.extend(
                _divergencia_do_percentual(modalidades[modalidade_id], quantidade, total, caminho)
            )

        if not isinstance(total, int) or isinstance(total, bool):
            continue
        caminho_do_quadro = f"{base}/vacancyTable"
        if soma > total:
            findings.append(
                _impeditivo(
                    "vacancy_sum_exceeds_total",
                    f"O quadro de vagas do Perfil '{rotulo}' soma {soma} e o Perfil declara "
                    f"{total} vagas imediatas — excesso de {soma - total}.",
                    caminho_do_quadro,
                )
            )
        elif tem_linha_geral and not (set(modalidades) - com_linha) and soma != total:
            findings.append(
                _impeditivo(
                    "vacancy_sum_mismatch",
                    f"O quadro de vagas do Perfil '{rotulo}' soma {soma} e o Perfil declara "
                    f"{total} vagas imediatas — diferença de {total - soma}.",
                    caminho_do_quadro,
                )
            )
    return findings


def _dentro(entidade, posicao):
    """O segmento que nomeia a entidade dentro da coleção: identidade, ou posição se não houver."""
    identificador = entidade.get("id")
    if isinstance(identificador, str) and identificador:
        return f"id={identificador}"
    return str(posicao)


def _divergencia_do_percentual(modalidade, quantidade, total, caminho) -> list[ValidationFinding]:
    """Dizer que `4` não é 20% de `80` é serviço legítimo; recalcular `4` não é (D-003, FR-163).

    O arredondamento é aceito nas duas direções porque a norma que fundamenta a cota manda
    arredondar, e Editais reais arredondam para cima e para baixo. O que se adverte é a quantidade
    que não cabe em arredondamento nenhum do percentual publicado.
    """
    regra = modalidade.get("normativeRule")
    if not isinstance(regra, dict):
        return []
    bruto = regra.get("percentage")
    if bruto is None or not isinstance(quantidade, int) or isinstance(quantidade, bool):
        return []
    if not isinstance(total, int) or isinstance(total, bool) or total <= 0:
        return []
    try:
        percentual = Decimal(str(bruto))
    except InvalidOperation:
        return []
    esperado = Decimal(total) * percentual / Decimal(100)
    piso, teto = math.floor(esperado), math.ceil(esperado)
    if piso <= quantidade <= teto:
        return []
    return [
        ValidationFinding(
            Severity.WARNING,
            "vacancy_row_percentage_divergence",
            f"A linha da modalidade '{modalidade.get('code', '')}' declara {quantidade} vaga(s), e "
            f"o percentual publicado na Regra Normativa ({_percentual_legivel(percentual)}%) sobre "
            f"{total} vagas daria {piso if piso == teto else f'{piso} ou {teto}'}. "
            "A quantidade declarada é a que vale.",
            caminho,
        )
    ]


def _percentual_legivel(percentual: Decimal) -> str:
    """O percentual sem zeros à direita, para que a advertência se leia como uma frase."""
    normalizado = percentual.normalize()
    return f"{normalizado:f}"


def blocking_findings(findings):
    return [item for item in findings if item.severity == Severity.BLOCKING_ERROR]
