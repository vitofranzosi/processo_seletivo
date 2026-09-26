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

from processo_seletivo.editais.domain import marcos
from processo_seletivo.editais.domain.calendario import (
    ano_do_evento,
    instante_vencido,
    vencido,
)
from processo_seletivo.editais.domain.documentos import (
    perfis_que_o_documento_publicado_alcanca,
    rotulo_da_modalidade,
)
from processo_seletivo.editais.domain.perfis import ProfileValidationError, validate_normative_rule
from processo_seletivo.editais.domain.secoes import CATALOGO, GERADA, TEXTUAL
from processo_seletivo.inscricoes.domain.periodo import (
    ENCERRADO,
    evento_designado,
    periodo_de_inscricoes,
)
from processo_seletivo.shared.tempo import ZONA


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
    # **Itens de texto**, transcrito do contrato (026). A declaração faltava, e a API aceitava
    # qualquer JSON dentro da lista: número, objeto, outra lista. A tela de Retificação a oferece
    # numa caixa de texto, uma exigência por linha, e item que não é texto não volta de lá igual —
    # o que se publicava não tinha como ser corrigido pelo canal do ator sem se corromper.
    Campo("requirements", list, tipo_do_item=str),
    Campo("immediateVacancies", int, minimo=0),
    Campo("reserveType", str, valores=RESERVA),
    Campo("reserveLimit", int, admite_nulo=True, minimo=0),
    # Qual das Modalidades declaradas é a ampla concorrência (014, D-014, FR-231). **Anulável**: há
    # Edital em que ela existe só como a linha geral do quadro, e nesse caso não há Modalidade a
    # apontar. Que a identidade aponte Modalidade **deste** Perfil é conferido à parte, porque
    # depende do conteúdo do Perfil inteiro e não da forma do campo.
    Campo("generalCompetitionModalityId", str, formato="uuid", admite_nulo=True),
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
    # A declaração de reversão da `016` (D-007). **`dict` anulável, e nulo é a declaração de que
    # este Edital não reverte** — não a ausência dela: sempre presente depois do degrau 14, como o
    # quadro depois do 12, porque duas grafias para a ausência é o que a versão canônica existe
    # para não admitir.
    #
    # **A forma de dentro não se declara aqui**, e é a mesma régua de `competitionModalities`: que
    # `kind` exista e seja um dos dois declaráveis é conferido por `_reversao_declarada`, que
    # precisa recusar a publicação com código próprio — `vacancy_reversion_kind_required` — em vez
    # de devolver "tipo inválido".
    #
    # **Ela estava faltando, e o defeito é o do `T110` da `014` repetido**: a publicação emitia o
    # campo, o degrau 14 o elevava, e a forma publicada não o conferia. Quem o encontrou foi
    # `tests/contract/test_forma_publicada.py`, ao acrescentar `vacancyReversion` ao contrato.
    Campo("vacancyReversion", dict, admite_nulo=True),
    # A forma de comunicar a convocação da `019` (D-009, R-007). **Texto anulável, e nulo é a
    # declaração de que este Edital não disse como convoca** — não a ausência do campo: sempre
    # presente depois do degrau 15, pela mesma razão do quadro depois do 12 e da reversão depois do
    # 14. Duas grafias para a ausência é o que a versão canônica existe para não admitir.
    #
    # **Campo solto, e não objeto como `vacancyReversion`**: ali o envelope existe porque a decisão
    # da `016` previa parâmetros do gatilho. Aqui há um valor entre dois, e um objeto com uma chave
    # só seria forma sem conteúdo — mais um caminho a endereçar na Retificação, sem nada dentro.
    Campo("callForm", str, admite_nulo=True),
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
    # Onde o Evento acontece (021, D-008). **Faltava**, e o defeito é o do `vacancyReversion`
    # repetido: `publish_edital` o emite em todo Evento publicado, e esta declaração não o conferia
    # — nenhum teste acusava, porque o guarda da forma confere coleções e não campos. Quem o
    # encontrou foi a `026`, ao enumerar os campos publicados para classificar a mutabilidade de
    # cada um: o campo governa onde a pessoa comparece e não tinha forma nem decisão.
    #
    # `str` sem `admite_nulo`, como `duties` e `workload` do Perfil: sempre presente, com `""`
    # quando não declarado. Uma segunda convenção para texto faria a versão canônica admitir mais
    # de uma forma.
    Campo("location", str),
    # Sempre presente, nunca nulo: a ausência de marca é `false`, e não "não informado". A regra
    # de quantos podem ser verdadeiros é de coerência entre itens e vive em
    # `_periodo_de_inscricoes`, porque a forma confere um campo por vez.
    Campo("isRegistrationPeriod", bool),
)

# Os dois identificadores e o código são anuláveis por semântica: `null` é "não restringe". É a
# ausência deles que produz as cinco formas de aplicabilidade (044), e declará-los assim é o que
# impede uma sexta forma de existir no conteúdo publicado — nenhum valor especial, nenhum operador.
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
    # O recorte transversal (044): o **código** da Modalidade, em todos os Perfis que a têm. Texto,
    # e não identidade — é o código que as Modalidades de Perfis diferentes têm em comum.
    Campo("modalityCode", str, admite_nulo=True),
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
        findings.extend(_ampla_concorrencia_declarada(perfil, base=base))
        findings.extend(_reversao_declarada(perfil, base=base))
        findings.extend(_forma_de_convocacao_declarada(perfil, base))
        findings.extend(_corte_em_dois_marcos(perfil, base=base))
        for indice, marco in enumerate(perfil.get("classificationMilestones") or []):
            if not isinstance(marco, dict):
                continue
            chave = marco.get("id")
            dentro = f"id={chave}" if isinstance(chave, str) and chave else str(indice)
            caminho = f"{base}/classificationMilestones/{dentro}"
            findings.extend(_arredondamento_do_marco(marco, caminho))
            # **A exigência de Etapa é condicionada à forma da ordem** (030, FR-432), pela mesma
            # regra que a elaboração aplica em `editais/domain/perfis` — e a regra é a mesma
            # função, não uma cópia. O marco de sorteio que precede a análise documental não tem
            # Etapa a enumerar, e recusá-lo aqui contradizia a ajuda da própria tela.
            #
            # **Marco que não declara a forma continua exigindo Etapa**: é o que todo Edital
            # publicado antes desta feature afirma, e afrouxar sobre ele mudaria o já publicado.
            if not marco.get("stages") and marcos.exige_etapa(
                marco.get("orderProduction") or "",
                metodo_declarado=bool(marco.get("drawMethod")),
            ):
                findings.append(
                    ValidationFinding(
                        Severity.BLOCKING_ERROR,
                        "milestone_without_stage",
                        "O marco classificatório ordena pela pontuação e não enumera Etapa "
                        "alguma: sem Etapa não há pontuação a combinar, e a ordem não sai.",
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


def _marco_nomeado(marco) -> str:
    """Como a recusa chama o marco (014, FR-182, UX-025).

    O `code` é o que quem elabora digitou e o que o documento publica; o identificador só aparece
    quando não há código, porque uma recusa que diga um UUID não diz nada a quem vai corrigi-la. O
    percurso E2E encontrou as cinco recusas da regra de corte mudas quanto ao marco: num Perfil com
    três marcos, "a regra de corte não declara o desfecho" não dizia **qual** abrir (E2E14-002).
    """
    return str(marco.get("code") or marco.get("name") or marco.get("id") or "sem código")


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
    nomeado = _marco_nomeado(marco)
    findings = _forma_do_alvo(regra, caminho=caminho, nomeado=nomeado)
    if regra.get("tieOutcome") not in faixa.DESFECHOS_DE_EMPATE:
        findings.append(
            _impeditivo(
                "cut_rule_sem_desfecho_de_empate",
                f"A regra de corte do marco {nomeado} não declara o que acontece com o empate que "
                "atravessa a última posição da faixa. O sistema não escolhe por ela.",
                f"{caminho}/cutRule/tieOutcome",
            )
        )
    if regra.get("continuation") not in faixa.POLITICAS_DE_CONTINUACAO:
        findings.append(
            _impeditivo(
                "cut_rule_sem_politica_de_continuacao",
                f"A regra de corte do marco {nomeado} não declara se este Edital admite "
                "continuação além da faixa publicada.",
                f"{caminho}/cutRule/continuation",
            )
        )
    declarada = regra.get("governedStage")
    if not declarada:
        findings.append(
            _impeditivo(
                "cut_rule_sem_etapa_governada",
                f"A regra de corte do marco {nomeado} não declara qual Etapa o corte alimenta. Ela "
                "não é inferida de lugar nenhum: declare a Etapa, ou declare que este corte não "
                "governa nenhuma.",
                f"{caminho}/cutRule/governedStage",
            )
        )
    elif declarada != faixa.SEM_ETAPA_GOVERNADA:
        if str(declarada) not in etapas:
            findings.append(
                _impeditivo(
                    "cut_rule_com_etapa_inexistente",
                    f"A regra de corte do marco {nomeado} declara governar uma Etapa que este "
                    "Edital não publica.",
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
        # A pergunta "este marco ordena por sorteio?" passou a ter resposta declarada (030,
        # FR-413), e é `editais/domain/marcos` que a responde — aqui e nos demais leitores. Ler a
        # presença do método direto, como esta linha fazia, era a inferência que a FR-413 veio
        # substituir: ela não distingue *não sorteia* de *sorteia e ainda não declarei o método*.
        elif not marcos.ordena_por_sorteio(
            marco.get("orderProduction") or "", metodo_declarado=bool(marco.get("drawMethod"))
        ) and str(declarada) in {str(item) for item in (marco.get("stages") or [])}:
            findings.append(
                _impeditivo(
                    "cut_rule_com_etapa_circular",
                    f"A regra de corte do marco {nomeado} governa uma Etapa que alimenta a própria "
                    "ordem do marco: o universo da ordem passaria a depender do corte que ela "
                    "produz.",
                    f"{caminho}/cutRule/governedStage",
                )
            )
    findings.extend(_quadro_para_o_corte(regra, perfil=perfil, caminho=caminho, nomeado=nomeado))
    return findings


def _forma_do_alvo(regra, *, caminho, nomeado) -> list[ValidationFinding]:
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
                f"A regra de corte do marco {nomeado} não declara a espécie do alvo: uma "
                "quantidade fixa, ou a quantidade que o quadro de vagas do recorte publica.",
                f"{caminho}/cutRule/targetKind",
            )
        ]
    findings = []
    alvo = regra.get("targetCount")
    if especie == faixa.ALVO_FIXO and alvo is None:
        findings.append(
            _impeditivo(
                "cut_rule_sem_alvo",
                f"A regra de corte do marco {nomeado} declara alvo fixo e não diz quantos.",
                f"{caminho}/cutRule/targetCount",
            )
        )
    if especie == faixa.ALVO_DO_QUADRO and alvo is not None:
        findings.append(
            _impeditivo(
                "cut_rule_com_alvo_duplicado",
                f"A regra de corte do marco {nomeado} deriva o alvo do quadro de vagas e ainda "
                "assim declara uma quantidade fixa: o alvo tem uma fonte só.",
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
                    f"As quantidades da regra de corte do marco {nomeado} devem ser números "
                    "inteiros não negativos.",
                    f"{caminho}/cutRule/{campo}",
                )
            )
    return findings


def _quadro_para_o_corte(regra, *, perfil, caminho, nomeado) -> list[ValidationFinding]:
    """Alvo derivado exige linha de quadro para **todo recorte que o marco ordena** (014, FR-183).

    A `025` admite quadro parcial de propósito, e a regra de corte é do **marco**, que pode ordenar
    três listas. Sem esta conferência, um Edital com quadro parcial publicaria uma regra derivada
    inexequível na lista sem linha — e o defeito apareceria no dia da emissão, sob cronograma, com a
    correção dependendo de Retificação.

    **Os recortes são a linha geral e cada Modalidade que terá lista própria.** A Modalidade que o
    Perfil declara como **ampla concorrência** não é recorte próprio: a quantidade dela mora na
    linha geral, que é o recorte que o sorteio consulta, e dar-lhe linha seria declarar duas vezes o
    mesmo número (025, `FR-176`).

    Essa declaração é o que destrava a conferência no formato normal de Edital. A `R-006` da `025`
    registrou que identificar a ampla concorrência **casando o nome** seria decidir no plano uma
    questão que aquela spec deixou aberta — e continua certa. O que faltava era o Edital dizer qual
    é, e é o que `generalCompetitionModalityId` é: sem ele, exigir linha de toda Modalidade tornava
    impublicável o Edital que declara "Ampla concorrência" como Modalidade; com ele, a exigência
    vale inteira, sem heurística nenhuma.

    Linha **zerada** é declaração legítima e publica; o que impede é a ausência.
    """
    from processo_seletivo.classificacao.domain import faixa

    if regra.get("targetKind") != faixa.ALVO_DO_QUADRO:
        return []
    linhas = perfil.get("vacancyTable") or []
    declarados = {
        str(linha.get("modalityId")) if linha.get("modalityId") else None
        for linha in linhas
        if isinstance(linha, dict)
    }
    ampla = perfil.get("generalCompetitionModalityId")
    ampla = str(ampla) if ampla else None
    exigidos = [(None, "a ampla concorrência")]
    for modalidade in perfil.get("competitionModalities") or []:
        if not isinstance(modalidade, dict) or not modalidade.get("id"):
            continue
        identidade = str(modalidade["id"])
        if identidade == ampla:
            continue
        exigidos.append((identidade, modalidade.get("name") or identidade))
    return [
        _impeditivo(
            "cut_rule_sem_linha_de_quadro",
            f"A regra de corte do marco {nomeado} deriva o alvo do quadro de vagas, e não há linha "
            f"para {nome}.",
            f"{caminho}/cutRule/targetKind",
        )
        for chave, nome in exigidos
        if chave not in declarados
    ]


def _forma_de_convocacao_declarada(perfil, base) -> list[ValidationFinding]:
    """A forma declarada é uma das duas, ou nenhuma (019, `FR-287`).

    **Nulo é legítimo, e é o que todo Edital anterior ao degrau 15 afirma.** O que se recusa aqui é
    a forma **desconhecida**: publicada uma grafia que a `019` não interpreta, a convocação seria
    emitida por um canal que ninguém definiu — e convocação alcançada pela forma errada não tem
    conserto depois, porque publicação é ato imutável.
    """
    from processo_seletivo.publicacoes.domain.vocabulario_da_regra import FORMAS_DE_CONVOCACAO

    forma = perfil.get("callForm")
    if forma is None:
        return []
    caminho = f"{base}/callForm"
    if not isinstance(forma, str):
        return [_impeditivo(TIPO_INVALIDO, f"O item deveria ser texto em {caminho}.", caminho)]
    if forma not in FORMAS_DE_CONVOCACAO:
        return [
            _impeditivo(
                "call_form_unknown",
                f"A forma de convocação '{forma}' não é uma das declaráveis: o Edital comunica "
                "por publicação ou por mensagem individual.",
                caminho,
            )
        ]
    return []


def _reversao_declarada(perfil, *, base) -> list[ValidationFinding]:
    """A reversão declarada traz a espécie do gatilho, e pressupõe quadro (016, FR-249, FR-251).

    **Três recusas, e a ausência do objeto não é nenhuma delas.** `null` é declaração legítima —
    "este Edital não declara reversão" —, e o 57/2026 prova por que ela tem de ser respeitada: o
    item 4.5 dele proíbe por escrito o remanejamento entre cursos.

    **Objeto sem `kind` não vira espécie padrão.** Os dois Editais da amostra escrevem o gatilho de
    modo diferente — o 28/2026 reverte "havendo ausência de candidatos aprovados", o 57/2026 "na
    hipótese do não preenchimento total" —, e escolher por eles fixaria em ato publicado uma decisão
    de norma. Vaga revertida sob a leitura larga num Edital que manda a estreita é vaga que saiu do
    recorte reservado sem fundamento.

    **E reverter pressupõe quantidade por recorte**: declarar reversão num Perfil sem quadro é regra
    inexequível, e regra publicada inexequível é o que a `014` já recusou a publicar.
    """
    from processo_seletivo.ocupacao.domain.nomes import ESPECIES_DE_REVERSAO

    objeto = perfil.get("vacancyReversion")
    if objeto is None:
        return []
    caminho = f"{base}/vacancyReversion"
    if not isinstance(objeto, dict):
        return [_impeditivo(TIPO_INVALIDO, f"O item deveria ser objeto em {caminho}.", caminho)]
    especie = objeto.get("kind")
    if not especie:
        return [
            _impeditivo(
                "vacancy_reversion_kind_required",
                "O Perfil declara reversão de vaga sem dizer sob qual gatilho: declare por "
                "esgotamento da lista reservada ou por saldo não preenchido.",
                f"{caminho}/kind",
            )
        ]
    if especie not in ESPECIES_DE_REVERSAO:
        return [
            _impeditivo(
                "vacancy_reversion_kind_unknown",
                f"O gatilho de reversão '{especie}' não é um dos declaráveis.",
                f"{caminho}/kind",
            )
        ]
    if not (perfil.get("vacancyTable") or []):
        return [
            _impeditivo(
                "vacancy_reversion_sem_quadro",
                "O Perfil declara reversão de vaga e não publica quadro: não há quantidade por "
                "recorte a reverter.",
                caminho,
            )
        ]
    return []


def _ampla_concorrencia_declarada(perfil, *, base) -> list[ValidationFinding]:
    """A Modalidade declarada como ampla concorrência existe, e não tem linha própria (014, D-014).

    Duas recusas, e as duas são de coerência do que o próprio Perfil publica: apontar Modalidade que
    ele não declara deixaria a conferência do alvo derivado exigindo linha de um recorte que não
    existe, e dar linha à ampla concorrência declararia duas vezes o mesmo número — a quantidade
    dela já está na linha geral.
    """
    ampla = perfil.get("generalCompetitionModalityId")
    if not ampla:
        return _ampla_por_declarar(perfil, base=base)
    ampla = str(ampla)
    modalidades = {
        str(item.get("id"))
        for item in perfil.get("competitionModalities") or []
        if isinstance(item, dict) and item.get("id")
    }
    if ampla not in modalidades:
        return [
            _impeditivo(
                "general_competition_modality_unknown",
                "O Perfil declara como ampla concorrência uma Modalidade que ele não publica.",
                f"{base}/generalCompetitionModalityId",
            )
        ]
    tem_linha = any(
        isinstance(linha, dict) and str(linha.get("modalityId") or "") == ampla
        for linha in perfil.get("vacancyTable") or []
    )
    if not tem_linha:
        return []
    return [
        _impeditivo(
            "general_competition_modality_with_row",
            "A Modalidade declarada como ampla concorrência tem linha própria no quadro de vagas, "
            "e a quantidade dela já está na linha geral.",
            f"{base}/vacancyTable",
        )
    ]


def _ampla_por_declarar(perfil, *, base) -> list[ValidationFinding]:
    """O Perfil declara Modalidade e não diz qual delas é a da ampla concorrência (027, FR-325).

    **É advertência própria, e não a mesma da lista sem linha**, porque o ato que a resolve é outro:
    esta se resolve escolhendo num campo que já existe, aquela escrevendo uma quantidade. Somar os
    dois casos numa frase só mandaria metade das pessoas ao lugar errado.

    **E é o que a `025` prometeu e não teve como cumprir.** A FR-176 dela diz que o sistema deve
    advertir — e não recusar — sobre a Modalidade que o Edital *usa como* ampla concorrência, porque
    identificá-la exigiria casar o nome, e a `R-006` recusou isso por escrito: "Ampla concorrência",
    "AC", "Ampla Concorrência" e "ampla" são o mesmo recorte para quem lê e quatro cadeias
    diferentes para quem compara. O que faltava era o Edital **dizê-lo**, e o campo existe desde a
    `014`.

    O custo de não declarar é concreto: toda Modalidade não apontada conta como lista reservada, de
    modo que a que serve de ampla concorrência passa a exigir linha própria — e a quantidade dela
    mora na linha geral, onde a apuração a procura.
    """
    declaradas = [
        modalidade
        for modalidade in perfil.get("competitionModalities") or []
        if isinstance(modalidade, dict) and modalidade.get("id")
    ]
    if not declaradas:
        return []
    rotulo = perfil.get("code") or perfil.get("name") or ""
    return [
        ValidationFinding(
            Severity.WARNING,
            "general_competition_modality_undeclared",
            f"O Perfil '{rotulo}' declara {len(declaradas)} Modalidade(s) e não declara qual "
            "delas é a da ampla concorrência. Enquanto não declarar, todas contam como lista "
            "reservada e o quadro precisa de linha para cada uma — inclusive para a que serve de "
            "ampla concorrência, cuja quantidade mora na linha geral.",
            f"{base}/generalCompetitionModalityId",
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


# A Etapa que não referencia Evento nenhum (045, `FR-739`, `UX-086`). Código **próprio**, e não o
# `field_constraint_violated` da referência inexistente: `advertencias_do_ato` descarta aviso cujo
# código coincida com o de um impeditivo, e o invariante da declaração única prende que os dois
# conjuntos não se cruzem.
ETAPA_SEM_EVENTO = "stage_without_schedule_event"


def _etapa_sem_evento(snapshot: dict, *, ato: str) -> list[ValidationFinding]:
    """Etapa sem vínculo com o Cronograma — aviso de composição, e nunca recusa.

    **Aviso, porque a ausência é publicável e legítima** (`022`, `FR-026`): a validação recusa a
    referência a Evento **inexistente** e admite a ausência de referência. Torná-la impeditiva
    mudaria o que o sistema aceita publicar, e esta feature não decide isso.

    **Era sinal da Atenção, e saiu de lá** (045, `D-003`). Na condução ele apontava para uma
    Retificação que não alcança o vínculo — `scheduleEventId` é estrutural (`026`) —, e aparecia
    para sempre, sobre um fato que ninguém podia mudar. Seis dos quinze sinais do gestor, em 20/09.
    O momento em que a ausência se corrige sem custo é a composição, e é aqui que ela é dita.

    **Só no ato de publicação.** Na Retificação o aviso seria o mesmo beco com outra roupa: o
    vínculo não se retifica, e a tela da Retificação não o oferece.

    A ausência é dita nesses termos, e **nunca** como atraso, espera ou progresso zero: a Etapa não
    tem situação temporal a receber (`022`, `UX-001`, cuja regra de apresentação vem para cá).
    """
    if ato != ATO_DE_PUBLICACAO:
        return []
    itens = snapshot.get("stages")
    if not isinstance(itens, list):
        return []
    findings = []
    for posicao, item in enumerate(itens):
        if not isinstance(item, dict) or item.get("scheduleEventId"):
            continue
        caminho = _caminho_da_entidade("stages", item, posicao)
        findings.append(
            ValidationFinding(
                Severity.WARNING,
                ETAPA_SEM_EVENTO,
                "A Etapa não está vinculada a nenhum Evento do Cronograma, em "
                f"{caminho}/scheduleEventId.",
                f"{caminho}/scheduleEventId",
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


# Os dois atos que conferem conteúdo normativo, e a razão de eles serem distinguidos (027, D-004,
# FR-323, T-003). Publicar Edital novo sem linha geral **cria hoje** o defeito que a feature remove;
# retificar Edital publicado antes dela é o único caminho que o acervo tem. Uma exigência impeditiva
# escrita sem este recorte bloquearia toda Retificação de todo Edital do acervo — inclusive as que
# corrigem uma data e nada têm com vagas —, e coagir não é o mecanismo.
ATO_DE_PUBLICACAO = "publicacao"
ATO_DE_RETIFICACAO = "retificacao"


def validate_for_publication(
    snapshot: dict, *, ato: str = ATO_DE_PUBLICACAO, agora: datetime | None = None
) -> list[ValidationFinding]:
    """Os achados do conteúdo, classificados pelo ato que está sendo conferido.

    **Publicação é o padrão de propósito.** As chamadas de teste que não dizem o ato continuam
    valendo, e — o que importa mais — esquecer de passá-lo erra pelo lado que **recusa**, e não
    pelo que deixa passar. Quem precisa do comportamento estreito é uma só: `retificacoes.py`.

    **E o instante do ato é resolvido aqui, uma vez** (`028`, FR-341). Não a cada Evento: dois
    Eventos do mesmo cronograma seriam julgados contra instantes diferentes, e um cronograma cujo
    Evento vence no meio da passada produziria um relatório que não corresponde a estado nenhum.
    Quem grava passa o `now` da própria transação — é o que a Constituição pede no Princípio II,
    *"operações relacionadas DEVEM compartilhar referência temporal consistente na mesma
    transação"* —, e o padrão `None` lê o relógio, errando de novo pelo lado que acusa.
    """
    agora = agora or datetime.now(ZONA)
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
    findings.extend(_etapa_sem_evento(snapshot, ato=ato))
    findings.extend(_faixa_do_percentual(snapshot))
    findings.extend(_coerencia_dos_fatos(snapshot))
    findings.extend(_coerencia_dos_marcos(snapshot))
    findings.extend(_coerencia_da_janela_recursal(snapshot))
    findings.extend(_coerencia_do_metodo_de_sorteio(snapshot, ato=ato))
    findings.extend(_coerencia_da_forma_da_ordem(snapshot))
    findings.extend(_forma_da_ordem_declarada(snapshot, ato=ato))
    findings.extend(_perfil_sem_marco(snapshot, ato=ato))
    findings.extend(_marco_sem_regra_de_corte(snapshot, ato=ato))
    findings.extend(_metodo_do_sorteio_publicavel(snapshot, ato=ato))
    findings.extend(_coerencia_dos_requisitos(snapshot))
    findings.extend(_periodo_de_inscricoes(snapshot))
    findings.extend(_eventos_vencidos(snapshot, ato=ato, agora=agora))
    findings.extend(_ano_dos_eventos(snapshot, ato=ato))
    findings.extend(_declaracao_do_requerimento(snapshot, ato=ato))
    findings.extend(_periodo_de_inscricoes_encerrado(snapshot, ato=ato, agora=agora))
    findings.extend(_coerencia_dos_documentos_exigidos(snapshot))
    findings.extend(_coerencia_dos_anexos(snapshot))
    findings.extend(_coerencia_do_quadro_de_vagas(snapshot, ato=ato))
    return findings


def _perfis_bem_formados(snapshot: dict) -> list[dict]:
    """Os Perfis que são objetos — os demais já têm achado próprio.

    **A conferência de coerência não pode quebrar sobre conteúdo malformado**: o trabalho dela é
    acusá-lo, e uma exceção aqui apagaria todos os achados seguintes, inclusive os que dizem *por
    que* o conteúdo está malformado. Quem recusa `profiles` que não é lista, ou item que não é
    objeto, é `_violacoes_da_colecao`, e a mensagem dele é a que a pessoa precisa ler.
    """
    profiles = snapshot.get("profiles")
    if not isinstance(profiles, list):
        return []
    return [perfil for perfil in profiles if isinstance(perfil, dict)]


def _marcos_bem_formados(perfil: dict) -> list[dict]:
    """Idem, um nível abaixo."""
    marcos = perfil.get("classificationMilestones")
    if not isinstance(marcos, list):
        return []
    return [marco for marco in marcos if isinstance(marco, dict)]


def _coerencia_dos_requisitos(snapshot: dict) -> list[ValidationFinding]:
    """Uma exigência por item, com texto, e nenhuma quebra de linha dentro dele (026).

    O tipo do item é conferido pela forma publicada; o que não cabe lá é a **quebra**, porque ela é
    string válida. A restrição existe pelo canal do ator: a Retificação oferece a lista numa caixa
    de texto, uma linha por exigência, e um item com `\n` dentro se parte em dois ao voltar. Sem
    esta recusa, o Edital publicaria conteúdo que ninguém consegue corrigir sem corrompê-lo.

    É a mesma régua que a `026` aplicou ao `location` e à janela recursal: oferecer um campo cujo
    valor ninguém confere é publicar, pela via administrativa, o que a via de elaboração recusa.
    """
    findings = []
    for perfil in _perfis_bem_formados(snapshot):
        for posicao, requisito in enumerate(perfil.get("requirements") or []):
            if not isinstance(requisito, str):
                continue
            caminho = f"/profiles/id={perfil.get('id', '')}/requirements/{posicao}"
            if "\n" in requisito or "\r" in requisito:
                findings.append(
                    ValidationFinding(
                        severity=Severity.BLOCKING_ERROR,
                        code="requirement_multiline",
                        message=(
                            "Cada requisito de participação é uma exigência, e não um parágrafo: "
                            "quebra de linha dentro de um deles não tem como ser corrigida pela "
                            "tela de Retificação, que os oferece um por linha."
                        ),
                        path=caminho,
                    )
                )
            elif not requisito.strip():
                # **O item em branco pela mesma régua da quebra**, e a borda da API já o recusa:
                # a Retificação oferece a lista uma exigência por linha e descarta a linha vazia
                # ao converter, de modo que `""` publicado é exigência que ninguém lê e ninguém
                # corrige. Não exigir nada continua legítimo — é `requirements: []`, e não um
                # item sem texto.
                findings.append(
                    ValidationFinding(
                        severity=Severity.BLOCKING_ERROR,
                        code="requirement_blank",
                        message=(
                            "Requisito de participação em branco afirma que existe exigência sem "
                            "texto. Perfil que não exige nada publica a lista vazia."
                        ),
                        path=caminho,
                    )
                )
    return findings


def _coerencia_da_janela_recursal(snapshot: dict) -> list[ValidationFinding]:
    """A janela declarada precisa ser computável — **também depois de retificada** (026, US3).

    A regra existia e alcançava um caminho só. `validate_classification_milestones` a aplica na
    **elaboração** do Perfil, e a publicação nunca a conferiu: uma Retificação que gravasse
    `durationDays: 0` publicava sem recusa alguma, e o candidato leria um prazo de zero dias.

    Quem descobriu foi o canário 3 da `026`, ao levar o campo para a tela: oferecer um número que
    ninguém confere é publicar, pela via administrativa, o que a via de elaboração recusa.

    **A regra não é reescrita aqui** — `_validar_janela_recursal` continua sendo a única, e este
    achado a invoca. Duas cópias envelheceriam separadamente, e a que ficasse para trás seria
    justamente a do caminho menos percorrido.
    """
    from processo_seletivo.editais.domain.perfis import (
        ProfileValidationError,
        _validar_janela_recursal,
    )

    findings = []
    for perfil in _perfis_bem_formados(snapshot):
        for marco in _marcos_bem_formados(perfil):
            try:
                _validar_janela_recursal(marco.get("appealWindow"))
            except ProfileValidationError as recusa:
                findings.append(
                    ValidationFinding(
                        severity=Severity.BLOCKING_ERROR,
                        code="appeal_window_invalid",
                        message=f"Marco {marco.get('code', '')}: {recusa}",
                        path=(
                            f"/profiles/id={perfil.get('id', '')}"
                            f"/classificationMilestones/id={marco.get('id', '')}/appealWindow"
                        ),
                    )
                )
    return findings


def _coerencia_do_metodo_de_sorteio(snapshot: dict, *, ato: str) -> list[ValidationFinding]:
    """O método declarado vale inteiro — **também depois de retificado** (026, US4).

    Mesma lacuna da janela recursal, encontrada pelo mesmo caminho:
    `validate_classification_milestones` cobra o método completo na **elaboração** do Perfil, e a
    publicação nunca o conferia. Uma Retificação podia esvaziar a regra de substituição e publicar
    — e no dia da indisponibilidade a escolha da ocorrência voltaria para a mesa, que é exatamente
    o que a `021` proíbe.

    **A regra não é reescrita aqui**: `_validar_metodo_de_sorteio` continua sendo a única, e ela
    confere também o algoritmo, a fonte, as duas regras e a Etapa de habilitação contra o que este
    sistema executa.

    **A conferência da forma da ocorrência só entra na publicação** (035, FR-514). Ela é a sexta
    guarda do método, e a única que alcança conteúdo publicado que nunca passou por ela — as outras
    cinco existem desde que o método existe. Ligada no ato de Retificação, ela prenderia o Edital do
    acervo cuja ocorrência está em prosa: a Retificação é a **única** saída que ele tem, e é por
    onde a `FR-517` manda a pessoa ir. É o mesmo recorte, e pela mesma razão, que
    `_metodo_do_sorteio_publicavel` escreveu na `032`.

    **E não é afrouxamento.** O Edital que se publica hoje continua sendo impedido; o que muda é
    que corrigir o de ontem continua possível.
    """
    from processo_seletivo.editais.domain.perfis import (
        ProfileValidationError,
        _validar_metodo_de_sorteio,
        validate_common_draw_method,
    )

    conferir_forma = ato == ATO_DE_PUBLICACAO
    findings = []
    # **O método comum do Edital passa pela mesma conferência** (030, FR-429). A elaboração o
    # valida em `replace_draft`; a Retificação não passa por lá — ela opera sobre o snapshot, e o
    # que a governa é esta função. Sem esta passagem, remover `/drawMethod/substitutionRule` da
    # raiz, trocar a fonte por uma que este sistema não consulta ou invalidar o instante comum
    # publicava sem recusa.
    #
    # **E o dano é maior do que o do marco**, porque é um só ato: o método comum governa todo marco
    # que não declara o próprio, e uma Retificação que o esvazie devolve à mesa a escolha da
    # ocorrência de todos eles de uma vez.
    if snapshot.get("drawMethod") is not None:
        try:
            validate_common_draw_method(
                snapshot.get("drawMethod"), conferir_forma_da_ocorrencia=conferir_forma
            )
        except ProfileValidationError as recusa:
            findings.append(
                ValidationFinding(
                    severity=Severity.BLOCKING_ERROR,
                    code="common_draw_method_invalid",
                    message=f"Método do sorteio comum a este Edital: {recusa}",
                    path="/drawMethod",
                )
            )
    for perfil in _perfis_bem_formados(snapshot):
        for marco in _marcos_bem_formados(perfil):
            try:
                _validar_metodo_de_sorteio(
                    marco.get("drawMethod"),
                    etapas=marco.get("stages") or [],
                    conferir_forma_da_ocorrencia=conferir_forma,
                )
            except ProfileValidationError as recusa:
                findings.append(
                    ValidationFinding(
                        severity=Severity.BLOCKING_ERROR,
                        code="draw_method_invalid",
                        message=f"Marco {marco.get('code', '')}: {recusa}",
                        path=(
                            f"/profiles/id={perfil.get('id', '')}"
                            f"/classificationMilestones/id={marco.get('id', '')}/drawMethod"
                        ),
                    )
                )
    return findings


def _forma_da_ordem_declarada(snapshot: dict, *, ato: str) -> list[ValidationFinding]:
    """Marco que se publica pela primeira vez declara como a ordem dele é produzida (030, FR-413).

    **A tela obriga, e obrigar na tela não basta.** O `select` da composição é `required`, mas
    regra normativa não pode depender do navegador: a interface administrativa não é o único
    caminho até o conteúdo publicado — a API de rascunho é pública ao elaborador, e um envio que
    omita a chave gravava `""` sem que nada acusasse. O princípio IV pede a verificação no
    servidor, e é esta.

    **Na publicação, e não na gravação do rascunho.** O rascunho pode estar pela metade — é o que
    `cutRule`, `drawMethod` e `appealWindow` já praticam —, e recusar ali tornaria ilegal todo
    payload que os clientes de hoje produzem, sem que requisito nenhum peça essa quebra. O que não
    pode estar pela metade é o Edital publicado.

    **E não alcança a Retificação**, pela mesma razão que os achados do Cronograma não alcançam:
    `""` é o estado legítimo de todo marco do acervo, e cobrar dele uma declaração que a capacidade
    não oferecia quando ele foi composto seria pedir que a autoridade decidisse hoje o que o Edital
    de então não disse. A ausência continua sendo lida como sempre foi — sorteia quem declara
    método (FR-431, SC-142).
    """
    if ato != ATO_DE_PUBLICACAO:
        return []
    findings = []
    for perfil in _perfis_bem_formados(snapshot):
        for marco in _marcos_bem_formados(perfil):
            if marco.get("orderProduction"):
                continue
            findings.append(
                ValidationFinding(
                    severity=Severity.BLOCKING_ERROR,
                    code="order_production_nao_declarada",
                    message=(
                        f"O marco {marco.get('code', '')} não declara como a ordem dele é "
                        "produzida. Responda a primeira pergunta do cartão — pela pontuação "
                        "combinada das Etapas, ou por sorteio: sem ela o sistema volta a inferir a "
                        "forma da presença do método do sorteio, e a inferência não distingue quem "
                        "não sorteia de quem sorteia e ainda não declarou o método."
                    ),
                    path=(
                        f"/profiles/id={perfil.get('id', '')}"
                        f"/classificationMilestones/id={marco.get('id', '')}/orderProduction"
                    ),
                )
            )
    return findings


def _perfil_sem_marco(snapshot: dict, *, ato: str) -> list[ValidationFinding]:
    """Perfil que não declara marco algum não classifica ninguém (032, FR-457).

    **O achado de maior severidade da auditoria de 16/09/2026** (`ACH-49`), e o mais barato de
    evitar: a etapa de Classificação já dizia, em prosa, que *"um Perfil sem marco não
    classifica"*, e a Revisão respondia `IMPEDE: []` sobre um Edital em que isso era verdade. O
    Edital saiu publicado — ato imutável —, e a saída virou Retificação.

    **Na publicação, e não na gravação do rascunho**, pela razão que `_forma_da_ordem_declarada`
    escreve por extenso: o rascunho pode estar pela metade, e recusar ali tornaria ilegal todo
    payload que os clientes de hoje produzem. Um Perfil ganha marco na etapa de Classificação, que
    vem **depois** da de Perfis; cobrá-lo antes recusaria o assistente no meio do próprio caminho.

    **E não alcança a Retificação** (FR-460). O Edital sem marco existe: é o que a auditoria
    publicou. Tornar irretificável justamente o Edital que esta família existe para evitar trocaria
    um problema por outro pior — e é o que aconteceria sem o recorte, porque `retificacoes.py`
    afere o conteúdo produzido com `blocking_findings(validate_for_publication(...))`.

    **A truthiness é sobre o que o Perfil declara, e não sobre marcos bem formados.** Um
    `classificationMilestones` malformado já tem acusação própria em `_violacoes_da_colecao`, e
    empilhar duas sobre a mesma causa esconde a que resolve.
    """
    if ato != ATO_DE_PUBLICACAO:
        return []
    findings = []
    for perfil in _perfis_bem_formados(snapshot):
        if perfil.get("classificationMilestones"):
            continue
        # **`code` antes de `name`, como os três achados do quadro de vagas já fazem.** Não é
        # preferência: os quatro aparecem juntos na mesma lista da Revisão, e um Perfil chamado
        # `DOC-INFO` numa linha e `Professor de Informática` na seguinte pareceriam dois Perfis.
        rotulo = perfil.get("code") or perfil.get("name") or ""
        findings.append(
            ValidationFinding(
                severity=Severity.BLOCKING_ERROR,
                code="profile_without_milestone",
                message=(
                    f"O Perfil '{rotulo}' não declara marco classificatório algum: sem marco "
                    "ninguém é classificado por ele. Declare ao menos um na etapa Classificação."
                ),
                path=f"/profiles/id={perfil.get('id', '')}/classificationMilestones",
            )
        )
    return findings


def _marco_sem_regra_de_corte(snapshot: dict, *, ato: str) -> list[ValidationFinding]:
    """Marco sem regra de corte classifica e não convoca — e isso passa a ser dito (032, FR-461).

    **A distinção que esta função existe para fazer**: *ausência* de `cutRule` e `cutRule` que
    declara **não governar Etapa alguma** são estados diferentes, e só o primeiro dispara. A `014`
    criou o segundo de propósito (`FR-224`): a regra existe, a faixa nasce, e a convocação alcança
    — é o Edital 69/2026 da amostra, que sorteia, publica, convoca e manda comparecer, sem análise
    documental entre a ordem e a chamada. Cobrar dele uma regra que ele **tem** seria falso
    positivo no Edital mais simples e mais comum do acervo, e ruído treina a pessoa a ignorar a
    família inteira — que é o oposto do que o Princípio IV pede.

    **Aviso, e não impedimento.** Marco que não corta é legítimo, e a `014` fechou isso por
    escrito. O que a auditoria mediu (`ACH-46`) foi o silêncio: a tela dizia *"sem ele, a Etapa
    seguinte recebe todos os habilitados"* — verdade, e a metade menos importante. A consequência
    que importa é a outra ponta da cadeia, e a mensagem a nomeia inteira.

    **Recebe `ato` ainda sendo aviso**, e é deliberado: aviso não impede publicação nenhuma, mas
    sem o recorte a Retificação do Edital do acervo viria cheia de avisos sobre o que aquele Edital
    publicou e não tem como deixar de ter publicado.
    """
    if ato != ATO_DE_PUBLICACAO:
        return []
    findings = []
    for perfil in _perfis_bem_formados(snapshot):
        for marco in _marcos_bem_formados(perfil):
            if marco.get("cutRule"):
                continue
            findings.append(
                ValidationFinding(
                    severity=Severity.WARNING,
                    code="milestone_without_cut_rule",
                    message=(
                        f"O marco {_marco_nomeado(marco)} não declara regra de corte. Sem corte "
                        "não há geração, sem geração não há faixa, e sem faixa não há convocação: "
                        "este marco classifica e não convoca. Declare a regra na etapa "
                        "Classificação — ela pode declarar que não governa Etapa alguma."
                    ),
                    path=(
                        f"/profiles/id={perfil.get('id', '')}"
                        f"/classificationMilestones/id={marco.get('id', '')}/cutRule"
                    ),
                )
            )
    return findings


def _metodo_do_sorteio_publicavel(snapshot: dict, *, ato: str) -> list[ValidationFinding]:
    """Quem ordena por sorteio publica o método que o governa (032, FR-467).

    **O `ACH-50` da auditoria de 16/09/2026**: um Edital de sorteio foi publicado sem algoritmo,
    sem fonte, sem semente, sem normalização e sem regra de substituição. A tela já dizia que *"o
    método é conteúdo publicado do Edital"*; o que faltava era a verificação. Sem o método
    publicado, quem recebe o resultado não tem contra o que conferir o sorteio — e a verificação
    pública que a `021` construiu fica sem base normativa.

    **É a ausência, e não a declaração pela metade.** O método incompleto já tem achado próprio
    desde a `026` — `draw_method_invalid`, que reusa `_validar_metodo_de_sorteio` e confere os sete
    campos, a fonte que o sistema consulta e as duas regras com identificador e frase. Este trata
    do caso em que não há método nenhum: nem próprio no marco, nem comum na raiz do Edital.

    **A resolução é uma só** — `marcos.metodo_que_governa`, que é o ponto único desde a `030`. Uma
    segunda leitura aqui divergiria da do renderizador na primeira mudança, e a divergência
    apareceria como documento publicado dizendo uma coisa e sorteio fazendo outra.

    **Marco sem identidade não é endereçável**, e por isso a resolução não o alcança: ele recebe o
    achado, o que erra pelo lado que recusa. Quem tem a mensagem certa para ele é a conferência de
    forma, que já o acusa.

    **Só na publicação**, e não alcança a Retificação: `orderProduction` vazio é o estado legítimo
    de todo marco do acervo, e um Edital que declarou o sorteio antes desta feature não pode ficar
    irretificável por não ter dito o que a capacidade não pedia.
    """
    if ato != ATO_DE_PUBLICACAO:
        return []
    findings = []
    for perfil in _perfis_bem_formados(snapshot):
        for marco in _marcos_bem_formados(perfil):
            identidade = marco.get("id")
            metodo = (
                marcos.metodo_que_governa(snapshot, perfil_id=perfil.get("id"), marco_id=identidade)
                if identidade
                else None
            )
            if not marcos.ordena_por_sorteio(
                marco.get("orderProduction") or "", metodo_declarado=bool(metodo)
            ):
                continue
            if metodo:
                continue
            findings.append(
                ValidationFinding(
                    severity=Severity.BLOCKING_ERROR,
                    code="drawn_milestone_without_method",
                    message=(
                        f"O marco {_marco_nomeado(marco)} ordena por sorteio e não publica método "
                        "— nem próprio, nem comum a este Edital. Sem o método publicado ninguém "
                        "consegue conferir o sorteio contra a norma. Declare-o na etapa "
                        "Classificação."
                    ),
                    path=(
                        f"/profiles/id={perfil.get('id', '')}"
                        f"/classificationMilestones/id={identidade or ''}/drawMethod"
                    ),
                )
            )
    return findings


def _coerencia_da_forma_da_ordem(snapshot: dict) -> list[ValidationFinding]:
    """O marco não publica duas declarações incompatíveis sobre como a ordem nasce (030, FR-413).

    **A regra está escrita em `data-model.md`**: `POR_PONTUACAO` com método de sorteio preenchido é
    válido no rascunho — é o campo oculto que a FR-418 exige, e é ele que faz trocar a resposta não
    apagar o que já foi declarado — e **recusado na publicação**.

    **Por que a projeção de `edital_snapshot` não basta.** Ela descarta o método impertinente ao
    compor o snapshot, e com isso o ato de publicação nunca chega aqui com a contradição. A
    Retificação não passa por ela: ela opera sobre o conteúdo vigente, campo a campo, e uma
    Alteração que troque **só** `orderProduction` de `POR_SORTEIO` para `POR_PONTUACAO` deixa o
    `drawMethod` do marco onde estava. O resultado seria norma publicada dizendo, no mesmo objeto,
    que a ordem nasce da pontuação e que o sorteio tem fonte, ocorrência e regra de substituição.

    A recusa nomeia a saída, porque ela existe e é uma só: alterar os dois no mesmo ato. Um ato que
    muda a forma da ordem **é** um ato sobre o método, e separá-los publica a metade.
    """
    findings = []
    for perfil in _perfis_bem_formados(snapshot):
        for marco in _marcos_bem_formados(perfil):
            if marco.get("orderProduction") != "POR_PONTUACAO" or not marco.get("drawMethod"):
                continue
            findings.append(
                ValidationFinding(
                    severity=Severity.BLOCKING_ERROR,
                    code="order_production_contradiz_o_metodo",
                    message=(
                        f"O marco {marco.get('code', '')} declara que a ordem nasce da pontuação "
                        "e publica método de sorteio. As duas coisas não valem ao mesmo tempo: "
                        "retire o método no mesmo ato que muda a forma da ordem, ou mantenha a "
                        "forma por sorteio."
                    ),
                    path=(
                        f"/profiles/id={perfil.get('id', '')}"
                        f"/classificationMilestones/id={marco.get('id', '')}/orderProduction"
                    ),
                )
            )
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


# --- O cronograma conferido contra o instante do ato (028) --------------------------------------
#
# As três verificações abaixo existem porque o reaproveitamento copia o conteúdo normativo inteiro,
# datas inclusive, e nada acusava o Edital que nascia com o cronograma do ano anterior. Nenhuma
# delas move data: elas dizem, e quem declara prazo continua sendo quem assina o Edital.
#
# **As três valem só no ato de publicação.** No acervo, Evento vencido é a condição normal — o
# cronograma de todo Edital publicado vence com o tempo —, e produzi-las numa Retificação faria
# toda correção de vírgula carregar uma advertência por Evento. O que se repete a cada ato deixa de
# ser lido, e recusar prenderia o acervo inteiro. É a mesma forma que a `027` pratica em
# `_linha_geral_exigida` e `_acervo_sem_quadro`, pela mesma razão (FR-354).


def _instante(texto) -> datetime | None:
    """O instante declarado, ou nada quando o texto não descreve um.

    **Recuar em silêncio é deliberado.** Quem acusa texto que não é instante é a conferência de
    forma — `EVENTO_PUBLICADO` com o padrão `INSTANTE` —, e empilhar duas acusações sobre a mesma
    causa esconde a que resolve. É o mesmo recuo que `_perfis_bem_formados` pratica um nível acima.

    Instante sem deslocamento também não passa: comparar ingênuo com consciente levanta exceção, e
    a forma publicada exige o deslocamento. Quem o omitiu já tem achado próprio.
    """
    if not isinstance(texto, str):
        return None
    try:
        lido = datetime.fromisoformat(texto)
    except ValueError:
        return None
    return lido if lido.tzinfo is not None else None


def _eventos_bem_formados(snapshot: dict) -> list[tuple[int, dict]]:
    """Os Eventos que são objetos, com a posição em que foram declarados."""
    eventos = snapshot.get("schedule")
    if not isinstance(eventos, list):
        return []
    return [(posicao, evento) for posicao, evento in enumerate(eventos) if isinstance(evento, dict)]


def _nome_do_evento(evento: dict) -> str:
    """Como a mensagem chama o Evento — o que a pessoa digitou, e não o identificador."""
    for chave in ("description", "type"):
        valor = evento.get(chave)
        if isinstance(valor, str) and valor.strip():
            return valor.strip()
    return "sem descrição"


def _por_extenso(instante: datetime) -> str:
    """O instante como quem lê o Edital o escreve, na zona institucional (UX-047).

    Nunca texto ISO cru e nunca UTC: a auditoria de 13/09/2026 registrou como achado próprio a
    conferência que devolvia JSON Pointer e instante em UTC a quem só queria saber que data mudar.
    """
    return instante.astimezone(ZONA).strftime("%d/%m/%Y às %H:%M")


def _declaracao_do_requerimento(snapshot: dict, *, ato: str) -> list[ValidationFinding]:
    """Momento declarado sem texto de declaração — **erro impeditivo** (029, `FR-407`).

    **Impeditivo, e não advertência.** O texto é o que o candidato aceita, e é o que o cancelamento
    por informação falsa invoca. Sem ele, o aceite da `FR-393` guardaria o resumo de uma string
    vazia: um aceite de nada, gravado como se fosse aceite de alguma coisa. E publicação é ato
    imutável — o Edital nasceria com um requerimento inaceitável, e a correção não seria digitar de
    novo, e sim Retificar.

    **Condicionado ao ato de publicação**, como os achados que a `028` acrescentou. Uma exigência
    impeditiva sem esse recorte bloquearia toda Retificação de todo Edital do acervo, inclusive as
    que corrigem uma data e nada têm com requerimento — é a lição que a `027` deixou escrita.
    """
    if ato != ATO_DE_PUBLICACAO:
        return []
    declaracao = snapshot.get("matriculationRequest")
    if not isinstance(declaracao, dict) or not declaracao.get("moment"):
        return []
    if (declaracao.get("declarationText") or "").strip():
        return []
    return [
        ValidationFinding(
            Severity.BLOCKING_ERROR,
            "matriculation_request_without_declaration",
            "O Edital exige Requerimento de Matrícula e não tem o texto da declaração de "
            "veracidade. O candidato precisa aceitar um texto, e não um campo vazio.",
            "matriculationRequest/declarationText",
        )
    ]


def _eventos_vencidos(snapshot: dict, *, ato: str, agora: datetime) -> list[ValidationFinding]:
    """Evento cujo início ou término já passou — advertência, nunca recusa (FR-343).

    **Advertência porque existe Edital legítimo com Evento vencido**: o que registra o que já
    ocorreu, o que abre inscrições e é publicado no mesmo dia. Recusar transformaria "esta data já
    passou" em "este Edital não pode existir".

    **Um achado por Evento**, e ele nomeia o término quando os dois passaram (FR-343a): é o
    instante mais tardio, o que diz que o Evento inteiro acabou. O caminho acompanha o instante
    nomeado, para que a âncora leve ao campo de que a frase fala.
    """
    if ato != ATO_DE_PUBLICACAO:
        return []
    findings = []
    for posicao, evento in _eventos_bem_formados(snapshot):
        inicio = _instante(evento.get("startAt"))
        termino = _instante(evento.get("endAt"))
        if not vencido(inicio, termino, agora=agora):
            continue
        alvo = instante_vencido(inicio, termino, agora=agora)
        campo = "endAt" if alvo is termino else "startAt"
        quando = "terminou" if campo == "endAt" else "começou"
        findings.append(
            ValidationFinding(
                Severity.WARNING,
                "schedule_event_in_past",
                f"O Evento '{_nome_do_evento(evento)}' {quando} em {_por_extenso(alvo)}, "
                f"que já passou. O Edital será publicado com esta data como ela está.",
                f"{_caminho_da_entidade('schedule', evento, posicao)}/{campo}",
            )
        )
    return findings


def _ano_dos_eventos(snapshot: dict, *, ato: str) -> list[ValidationFinding]:
    """Evento cujo ano diverge do ano do Edital — advertência, nunca recusa (FR-344).

    **Nunca recusa, e são duas as razões.** Um Edital de 2027 publicado em dezembro de 2026 marca
    legitimamente eventos dos dois anos; e o `year` do Edital é **não retificável** pelo contrato da
    `026`, de modo que um impedimento apontaria para um campo que ninguém pode mexer.

    **O ano é o do início, e nunca o do término.** Um Evento que começa em dezembro e termina em
    janeiro é a definição de período que atravessa o ano; conferir os dois acusaria todo Edital de
    fim de ano, que é exatamente o caso que esta advertência não quer incomodar.
    """
    if ato != ATO_DE_PUBLICACAO:
        return []
    ano = snapshot.get("year")
    if isinstance(ano, bool) or not isinstance(ano, int):
        return []
    findings = []
    for posicao, evento in _eventos_bem_formados(snapshot):
        inicio = _instante(evento.get("startAt"))
        if inicio is None or ano_do_evento(inicio) == ano:
            continue
        findings.append(
            ValidationFinding(
                Severity.WARNING,
                "schedule_event_year_mismatch",
                f"O Evento '{_nome_do_evento(evento)}' começa em {_por_extenso(inicio)}, que é "
                f"de {ano_do_evento(inicio)}, e o Edital é de {ano}. Confira se a data é a desta "
                "oferta.",
                f"{_caminho_da_entidade('schedule', evento, posicao)}/startAt",
            )
        )
    return findings


def _periodo_de_inscricoes_encerrado(
    snapshot: dict, *, ato: str, agora: datetime
) -> list[ValidationFinding]:
    """Publicar um Edital cujas inscrições já fecharam é publicar um certame que ninguém pode
    disputar — e é o único achado desta feature que fecha porta (FR-346).

    **A leitura não é escrita aqui.** `periodo_de_inscricoes` é a função que o **portal** obedece
    para decidir se aceita uma inscrição; se a validação dissesse "encerrado" e o portal dissesse
    "aberto", o sistema recusaria publicar um Edital que em seguida receberia inscrição — dado
    independente e divergente, que é o que o Princípio II proíbe. O `>` estrito dela é também a
    FR-347: término exatamente igual ao instante do ato ainda é prazo.

    Sem término declarado não há encerramento, e a mesma função já responde assim: inventar um fim
    seria o sistema criando prazo que o Edital não fixou.
    """
    if ato != ATO_DE_PUBLICACAO:
        return []
    # **Com marca ambígua, este achado recua.** `periodo_de_inscricoes` escolhe o **primeiro**
    # Evento marcado, e com dois marcados essa escolha é arbitrária: se o primeiro estiver
    # encerrado, o conteúdo receberia `registration_period_ambiguous` **e**
    # `registration_period_closed` ao mesmo tempo, sobre uma causa só. Quem responde nesse caso é o
    # impeditivo que já existia — o Edital precisa de um período só antes de se poder dizer se ele
    # encerrou. Empilhar dois relatos esconde o que resolve.
    marcados = sum(
        1
        for _, evento in _eventos_bem_formados(snapshot)
        if evento.get("isRegistrationPeriod") is True
    )
    if marcados != 1:
        return []
    periodo = periodo_de_inscricoes(snapshot, agora)
    if periodo.estado != ENCERRADO or periodo.fim is None:
        return []
    designado = evento_designado(snapshot) or {}
    posicao = next(
        (posicao for posicao, evento in _eventos_bem_formados(snapshot) if evento is designado),
        0,
    )
    return [
        _impeditivo(
            "registration_period_closed",
            f"O período de inscrições encerrou em {_por_extenso(periodo.fim)}. Publicado assim, "
            "o Edital não receberá inscrição alguma — corrija a data do Evento na etapa "
            "Cronograma antes de publicar.",
            f"{_caminho_da_entidade('schedule', designado, posicao)}/endAt",
        )
    ]


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
        if documento.get("modalityCode"):
            achado = _recorte_por_codigo(documento, perfis, caminho)
            if achado is not None:
                findings.append(achado)
            continue
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
            continue
        if perfil_id is None:
            achado = _recorte_que_o_documento_publicado_alarga(documento, perfis, caminho)
            if achado is not None:
                findings.append(achado)
    findings.extend(_denominacoes_do_codigo(requisitos, perfis))
    return findings


def _recorte_por_codigo(documento: dict, perfis: dict, caminho: str) -> ValidationFinding | None:
    """As três recusas do recorte transversal sobre o conteúdo que passa a vigorar (044, R-007).

    A gravação do rascunho já as faz, e aqui elas valem de novo porque uma Retificação alcança o
    Perfil e a Modalidade sem passar pela gravação: remover o código do último Perfil, ou declarar
    ampla a Modalidade dele, deixaria o documento sem ninguém a quem ser pedido (FR-724, FR-704).
    """
    nome = documento.get("name", "")
    codigo = str(documento.get("modalityCode")).strip()
    if documento.get("profileId") is not None or documento.get("modalityId") is not None:
        return _impeditivo(
            "document_requirement_scope_conflict",
            f"O Documento Exigido '{nome}' recorta pela modalidade '{codigo}' em todos os Perfis, "
            "e declara também um Perfil ou a modalidade de um Perfil. Escolha um recorte só.",
            caminho,
        )
    com_o_codigo = [
        (perfil, modalidade)
        for perfil in perfis.values()
        for modalidade in perfil.get("competitionModalities") or []
        if str(modalidade.get("code") or "").strip() == codigo
    ]
    if not com_o_codigo:
        return _impeditivo(
            "document_requirement_modality_code_unknown",
            f"O Documento Exigido '{nome}' é pedido de quem concorre na modalidade '{codigo}', mas "
            "nenhum Perfil deste Edital tem modalidade com esse código. Ele não seria pedido a "
            "ninguém.",
            caminho,
        )
    for perfil, modalidade in com_o_codigo:
        ampla = perfil.get("generalCompetitionModalityId")
        if ampla and str(ampla) == str(modalidade.get("id")):
            return _impeditivo(
                "document_requirement_modality_code_general",
                f"O Documento Exigido '{nome}' é pedido de quem concorre na modalidade '{codigo}', "
                "mas ela é a ampla concorrência no Perfil "
                f"'{perfil.get('code') or perfil.get('name') or ''}'. A ampla concorrência não "
                "recorta documento.",
                caminho,
            )
    return None


def _denominacoes_do_codigo(requisitos: list, perfis: dict) -> list[ValidationFinding]:
    """O mesmo código, a mesma denominação — onde o Edital afirma que é a mesma modalidade (FR-706).

    **Só para código referido por documento transversal** (D-001): um Edital que não usa o recorte
    não afirma identidade nenhuma entre Perfis. **Só a denominação** (FR-707): percentual e
    fundamento são da cota, e a cota é por Perfil. **Um achado por código**, e não por Perfil
    divergente: com 16 Perfis num empate de 8 a 8, oito achados diriam oito problemas onde há um.

    A comparação apara as pontas e mais nada (D-005). O documento publicado imprime **uma**
    denominação no título do grupo, e não pode escolher entre duas que diferem por uma maiúscula.
    O caminho aponta os Perfis, porque é lá que se corrige.
    """
    referidos = []
    for documento in requisitos:
        if isinstance(documento, dict) and documento.get("modalityCode"):
            codigo = str(documento["modalityCode"]).strip()
            if codigo not in referidos:
                referidos.append(codigo)
    findings = []
    for codigo in referidos:
        por_denominacao = {}
        for perfil in perfis.values():
            for modalidade in perfil.get("competitionModalities") or []:
                if str(modalidade.get("code") or "").strip() != codigo:
                    continue
                denominacao = str(modalidade.get("name") or "").strip()
                rotulo = perfil.get("code") or perfil.get("name") or ""
                por_denominacao.setdefault(denominacao, []).append(rotulo)
        if len(por_denominacao) < 2:
            continue
        partes = "; ".join(
            f"'{denominacao}' em {', '.join(sorted(rotulos))}"
            for denominacao, rotulos in sorted(por_denominacao.items())
        )
        findings.append(
            _impeditivo(
                "modality_code_name_divergent",
                f"A modalidade '{codigo}' tem denominações diferentes entre os Perfis: {partes}. "
                "Um documento é pedido dela em todos os Perfis, e o Edital publicado precisa "
                "nomeá-la de um jeito só. Iguale a denominação nos Perfis.",
                "/profiles",
            )
        )
    return findings


def _recorte_que_o_documento_publicado_alarga(
    documento: dict, perfis: dict, caminho: str
) -> ValidationFinding | None:
    """Todos os Perfis, com a modalidade de um só: o Edital e a inscrição diriam coisas diferentes.

    Cada Perfil tem as suas Modalidades, e a inscrição aplica o recorte **pela identidade** — o
    documento restrito ao PcD do C1 nunca é pedido ao PcD do C2. O documento publicado, sem Perfil
    declarado, escreve o grupo **pelo nome**: *"Dos candidatos concorrentes na modalidade Pessoas
    com Deficiência"*. Com outro Perfil tendo modalidade de mesmo nome, o ato publicado exige o
    documento de todos eles e o portal o pede de um só. Foi o que a conferência do portal mostrou:
    um candidato PcD do C2 enviou a inscrição sem o laudo que o Edital dizia exigir dele
    (doc/achado-documento-condicional-no-portal.md). "Partir de um Edital anterior" produz esse
    recorte sozinho, ao acrescentar Perfis a uma origem que tinha um só.

    **Só quando o nome se repete.** Se nenhum outro Perfil tem modalidade com aquele nome, o grupo
    publicado alcança exatamente quem o portal alcança, e não há o que acusar. A pergunta mora em
    `documentos.py` porque a lista exigida da `044` a faz também (R-004).

    **A saída que a `044` acrescenta** vem em segundo lugar na mensagem, porque é a que o Edital da
    amostra quer dizer: "todo candidato PcD" — a modalidade daquele código em todos os Perfis.
    """
    dono, modalidade, outros = perfis_que_o_documento_publicado_alcanca(documento, perfis)
    if dono is None or not outros:
        return None
    rotulo = rotulo_da_modalidade(modalidade)
    codigo = str(modalidade.get("code") or "").strip()
    perfil_dono = dono.get("code") or dono.get("name") or ""
    return _impeditivo(
        "document_requirement_modality_scope_ambiguous",
        f"O Documento Exigido '{documento.get('name', '')}' vale para todos os Perfis, mas "
        f"está restrito à modalidade '{rotulo}' do Perfil '{perfil_dono}'. O Edital publicado o "
        f"exigiria de todo candidato em '{rotulo}', e a inscrição o pediria só no Perfil "
        f"'{perfil_dono}'. Declare o Perfil '{perfil_dono}' no documento, ou use a modalidade "
        f"'{rotulo}' ({codigo}) em todos os Perfis — ou, para exigi-lo em Perfis escolhidos, "
        "repita-o com a modalidade de cada um.",
        caminho,
    )


def _coerencia_do_quadro_de_vagas(
    snapshot: dict, *, ato: str = ATO_DE_PUBLICACAO
) -> list[ValidationFinding]:
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
        base = _caminho_da_entidade("profiles", perfil, posicao)
        linhas = perfil.get("vacancyTable")
        if not isinstance(linhas, list) or not linhas:
            # **Quadro ausente tem duas leituras, e é o ato que decide qual vale** (027, FR-323).
            # No acervo, ausência é o que **todo** Edital publicado antes do degrau 12 afirma, e
            # continua legítima: ausência não é zero (025, D-005, FR-160). Publicando Edital novo,
            # não: a linha geral é materializada na gravação, e chegar aqui sem ela significa que
            # alguém a contornou — publicar assim criaria hoje o Edital inerte que a feature existe
            # para deixar de produzir.
            findings.extend(_linha_geral_exigida(perfil, base=base, ato=ato))
            findings.extend(_acervo_sem_quadro(perfil, base=base, ato=ato))
            continue
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

        if not tem_linha_geral:
            findings.extend(_linha_geral_exigida(perfil, base=base, ato=ato))

        if not isinstance(total, int) or isinstance(total, bool):
            continue
        caminho_do_quadro = f"{base}/vacancyTable"
        # **A completude desconta a Modalidade declarada como ampla** (027, FR-317, T-002). Ela,
        # por norma, não tem linha — a quantidade dela mora na geral (025, D-004) —, e contá-la
        # aqui fazia a diferença nunca ser vazia: no formato mais comum do acervo, uma Modalidade
        # "Ampla concorrência" mais as reservadas, a igualdade **nunca rodava**. Era a lacuna que a
        # `025` registrou em R-006 e não tinha como fechar, porque não havia quem dissesse qual das
        # Modalidades era a ampla. Agora há, e a conferência alcança o Edital normal.
        ampla = perfil.get("generalCompetitionModalityId")
        reservadas = set(modalidades) - ({str(ampla)} if ampla else set())
        if soma > total:
            findings.append(
                _impeditivo(
                    "vacancy_sum_exceeds_total",
                    f"O quadro de vagas do Perfil '{rotulo}' soma {soma} e o Perfil declara "
                    f"{total} vagas imediatas — excesso de {soma - total}.",
                    caminho_do_quadro,
                )
            )
        elif tem_linha_geral and not (reservadas - com_linha) and soma != total:
            # **Sem lista reservada os dois números são o mesmo número** (027, FR-335), e a
            # mensagem diz isso em vez de deixar quem lê deduzir. Num Perfil que reparte, a
            # diferença pode ser de qualquer uma das linhas e a frase genérica é a certa; aqui há
            # uma linha só, e o conserto é mover as duas pontas no mesmo ato.
            findings.append(
                _impeditivo(
                    "vacancy_sum_mismatch",
                    (
                        f"O Perfil '{rotulo}' declara {total} vaga(s) imediata(s) e a linha da "
                        f"ampla concorrência diz {soma}. Este Perfil não declara lista reservada: "
                        "os dois são o mesmo número, e mudam no mesmo ato."
                        if not reservadas
                        else f"O quadro de vagas do Perfil '{rotulo}' soma {soma} e o Perfil "
                        f"declara {total} vagas imediatas — diferença de {total - soma}."
                    ),
                    caminho_do_quadro,
                )
            )

        findings.extend(
            _listas_reservadas_sem_linha(
                perfil, reservadas - com_linha, modalidades, base=base, rotulo=rotulo, soma=soma
            )
        )
    return findings


def _listas_reservadas_sem_linha(
    perfil, sem_linha, modalidades, *, base, rotulo, soma
) -> list[ValidationFinding]:
    """O que ficará sem quantidade a apurar, dito antes de a publicação torná-lo imutável (027).

    **Advertência, e não recusa.** Quadro parcial é legítimo: um Edital pode declarar a quantidade
    de uma lista e não a de outra, e a `025` decidiu isso com razão que continua de pé — ausência
    diz "o Edital não declarou", e recusar transformaria isso em "o Edital não pode existir".

    O que a `027` acrescenta é que o sistema **diga**. Era o quinto dos seis pontos em que a cadeia
    podia ter avisado e não avisava: o Perfil declarava a lista, não declarava a quantidade dela, a
    etapa 9 dizia "nada pendente", e a Ocupação respondia meses depois — quando a correção já não é
    digitar de novo, e sim Retificar.

    **Em números, e não só sinalizada** (UX-044): quem lê precisa saber o que o Perfil publica, o
    que o quadro reparte e qual recorte fica de fora, sem abrir outra tela para descobrir.
    """
    if not sem_linha:
        return []
    total = perfil.get("immediateVacancies")
    if isinstance(total, bool) or not isinstance(total, int):
        return []
    nomes = sorted(
        (modalidades[chave].get("name") or modalidades[chave].get("code") or "")
        for chave in sem_linha
        if chave in modalidades
    )
    if not nomes:
        return []
    return [
        ValidationFinding(
            Severity.WARNING,
            "vacancy_reserved_list_without_row",
            f"O Perfil '{rotulo}' publica {total} vaga(s) imediata(s) e reparte {soma} no quadro. "
            f"Sem linha no quadro: {', '.join(nomes)} — a ocupação e a convocação não terão "
            "quantidade a apurar nesse(s) recorte(s).",
            f"{base}/vacancyTable",
        )
    ]


def _acervo_sem_quadro(perfil, *, base, ato) -> list[ValidationFinding]:
    """O Edital do acervo publica vaga e não publica linha: o ato que resolve tem nome (027).

    **Só no ato de Retificação, e é deliberado.** Publicando Edital novo, a ausência de linha geral
    é impedimento — a FR-323 a recusa, e a derivação faz com que ela não aconteça. No acervo ela é
    a condição normal: todo Edital publicado antes desta feature declara vaga imediata e não
    declara quadro, porque a capacidade não existia.

    **E é advertência, nunca recusa.** Prender a Retificação de um Edital antigo até que alguém lhe
    dê quadro bloquearia até a correção de uma data, e coagir não é o mecanismo (FR-323). O que o
    sistema faz é dizer — aqui, que é onde quem pode agir já está: a tela de Retificação é
    exatamente o lugar onde a linha se acrescenta (FR-332).
    """
    if ato != ATO_DE_RETIFICACAO:
        return []
    # **Zero é uma declaração, e ausência não é zero** (025, D-005). Um Perfil legado que publica
    # `0` vaga imediata e nenhuma linha continua sem dizer quanto a ampla concorrência tem: a
    # Ocupação responde "não publicou quadro", e não "zero". Excluir o `0` daqui faria a FR-331
    # alcançar quase todo o acervo em vez de todo ele — e o `TEC-LAB` da demonstração é exatamente
    # essa forma. Negativo continua de fora porque a conferência de forma já o recusa, e empilhar
    # duas acusações sobre a mesma causa esconde a que resolve.
    total = perfil.get("immediateVacancies")
    if isinstance(total, bool) or not isinstance(total, int) or total < 0:
        return []
    rotulo = perfil.get("code") or perfil.get("name") or ""
    return [
        ValidationFinding(
            Severity.WARNING,
            "vacancy_table_absent_in_archive",
            f"O Perfil '{rotulo}' publica {total} vaga(s) imediata(s) e não publica quadro de "
            "vagas: a ocupação e a convocação não têm quantidade a apurar. Acrescentar a linha da "
            "ampla concorrência a este Perfil, nesta Retificação, é o ato que declara a "
            "quantidade.",
            f"{base}/vacancyTable",
        )
    ]


def _linha_geral_exigida(perfil, *, base, ato) -> list[ValidationFinding]:
    """Um Perfil publicado hoje declara quantas vagas a ampla concorrência tem (027, FR-323).

    **A exigência é do ato de publicação, e só dele.** No ato de Retificação ela não é produzida —
    não por brandura, mas porque o acervo inteiro foi publicado antes de a capacidade existir, e
    uma recusa aqui prenderia até a Retificação que corrige uma data. O caminho do acervo é a
    FR-331 e a FR-332: dizer quem precisa do ato, e qual ato é.

    **Total malformado ou negativo não chega a esta recusa**: quem tem a mensagem certa para ele é
    a conferência de forma do Perfil, e empilhar duas acusações sobre a mesma causa esconde a que
    resolve. Quem corrige o total resolve as duas de uma vez; quem lê duas não sabe por onde
    começar.
    """
    total = perfil.get("immediateVacancies")
    if ato != ATO_DE_PUBLICACAO or isinstance(total, bool) or not isinstance(total, int):
        return []
    if total < 0:
        return []
    rotulo = perfil.get("code") or perfil.get("name") or ""
    return [
        _impeditivo(
            "vacancy_general_row_missing",
            f"O Perfil '{rotulo}' publica {total} vaga(s) imediata(s) e não declara a linha da "
            "ampla concorrência no quadro de vagas — sem ela, a ocupação e a convocação não teriam "
            "quantidade a apurar.",
            f"{base}/vacancyTable",
        )
    ]


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
