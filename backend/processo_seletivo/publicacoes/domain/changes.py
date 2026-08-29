"""Aplicação determinística de Alterações Normativas sobre o conteúdo canônico.

Caminhos seguem JSON Pointer (RFC 6901) com **uma extensão local declarada**: o segmento
`id=<uuid>`, que seleciona, dentro de uma lista, o elemento cujo `id` é esse. O RFC não tem
seleção por atributo, e alguma extensão era inevitável para endereçar um Perfil pela entidade e
não pela posição que ela ocupa. A escolha foi anunciá-la em vez de disfarçá-la: num campo que
fica gravado para sempre no ato publicado, dialeto que se esconde é pior que dialeto declarado.

**Qual forma de segmento vale depende do contêiner.** Em objeto, `id=algo` é nome de chave
literal, como sempre foi — a extensão não retira do RFC 6901 nada que ele permitia (FR-002). Em
lista valem o seletor, o índice e o token de acréscimo `-`.

Endereçar por índice uma coleção que tem chave é recusado (FR-007): é a causa do defeito que
esta feature elimina, e recusar na elaboração impede que o ato instável chegue a existir.
Coleção declarada atômica não é endereçada item a item (FR-011).

Em objeto, `ADD` grava a chave — criando ou substituindo. Em lista, `ADD` só acrescenta ao fim,
com `-`: nenhuma outra folha serve, nem índice nem seletor (FR-006). Essa distinção importa para
a precondição de sobrescrita em `conflicts.py`.

Acrescentar a uma coleção com chave exige objeto com `id` UUID. Sem isso nasceria, dentro do
conteúdo normativo, uma entidade que nenhuma Retificação futura conseguiria endereçar — e a
garantia desta feature vale para o que já está publicado tanto quanto para o que entra agora.
"""

import re
from copy import deepcopy

from processo_seletivo.publicacoes.domain import colecoes

ABSENT = object()

APPEND_TOKEN = "-"
SELETOR = "id="
OPERATIONS = frozenset({"ADD", "REPLACE", "REMOVE"})
_INDEX = re.compile(r"0|[1-9][0-9]*")
_UUID = re.compile(r"[0-9a-fA-F]{8}(?:-[0-9a-fA-F]{4}){3}-[0-9a-fA-F]{12}")


class CaminhoInexistente(ValueError):
    """O caminho não resolve no conteúdo. Continua sendo ValueError para quem já o tratava."""


class ChaveNaoEncontrada(CaminhoInexistente):
    """O seletor é válido, mas nenhum elemento da coleção tem essa chave (FR-008)."""


class EnderecamentoPosicional(ValueError):
    """Índice numérico sobre coleção que tem chave (FR-007)."""


class SeletorInvalido(ValueError):
    """`id=` em lista com valor que não é UUID (FR-003)."""


class ColecaoAtomica(ValueError):
    """Endereçamento item a item de coleção sem identificador (FR-011)."""


class AcrescimoPosicionado(ValueError):
    """`ADD` em lista com folha diferente de `-` (FR-006).

    Inserção em posição específica não existe nesta gramática. Um seletor resolveria a posição
    de uma entidade existente e inseriria antes dela — que é a operação que a feature retirou.
    """


class EntidadeSemChave(ValueError):
    """`ADD` em coleção com chave, de valor que não é objeto com `id` UUID (FR-001, FR-012)."""


def parse_path(path):
    if not path.startswith("/"):
        raise ValueError("targetPath deve ser absoluto")
    return [part.replace("~1", "/").replace("~0", "~") for part in path[1:].split("/")]


def selector_uuid(token):
    """UUID do seletor `id=<uuid>`, ou None quando o token não é seletor bem formado.

    Comparação por texto exato, sem normalização de caixa: dois textos diferentes são duas
    chaves diferentes, e normalizar aqui criaria uma equivalência que o snapshot não tem.
    """
    if not token.startswith(SELETOR):
        return None
    valor = token[len(SELETOR) :]
    return valor if _UUID.fullmatch(valor) else None


def _posicao(lista, token, path, forma, *, allow_append, estrito):
    """Posição que `token` designa em `lista`, ou None quando não designa nenhuma.

    `forma` é a forma da coleção — é ela que diz se há chave, e portanto se o índice é recusado.
    `estrito` separa quem aplica de quem só lê: aplicar sobre chave inexistente é recusa com
    código próprio; ler o conteúdo anterior de um caminho que não existe é apenas ausência.
    """
    if colecoes.e_atomica(forma):
        raise ColecaoAtomica(
            f"{forma} é coleção sem identificador e vale como valor único: "
            f"substitua a lista inteira em vez de endereçar {path}."
        )
    identificador = selector_uuid(token)
    if identificador is not None:
        for posicao, elemento in enumerate(lista):
            if isinstance(elemento, dict) and elemento.get(colecoes.CAMPO_CHAVE) == identificador:
                return posicao
        if estrito:
            raise ChaveNaoEncontrada(f"Não há item com esse identificador em {path}.")
        return None
    if token.startswith(SELETOR):
        raise SeletorInvalido(f"O seletor id= exige um UUID em {path}.")
    if token == APPEND_TOKEN:
        return len(lista) if allow_append else None
    if not _INDEX.fullmatch(token):
        return None
    if colecoes.tem_chave(forma):
        raise EnderecamentoPosicional(
            f"{path} endereça {forma} por posição. Endereçe pelo identificador do item, com "
            f"id=<uuid>, porque a posição muda quando outra Retificação é publicada."
        )
    posicao = int(token)
    return posicao if posicao <= (len(lista) if allow_append else len(lista) - 1) else None


def _descer(container, token, path, forma):
    """Um nível abaixo: o valor alcançado e a forma do contêiner que ele passa a ser."""
    if isinstance(container, dict):
        if token not in container:
            raise CaminhoInexistente(f"Caminho inexistente: {path}")
        return container[token], f"{forma}/{colecoes.escapar(token)}"
    if isinstance(container, list):
        posicao = _posicao(container, token, path, forma, allow_append=False, estrito=True)
        if posicao is None:
            raise CaminhoInexistente(f"Caminho inexistente: {path}")
        return container[posicao], f"{forma}/{colecoes.CURINGA}"
    raise CaminhoInexistente(f"Caminho inexistente: {path}")


def _recusar_controle_interno(tokens, path):
    if tokens and colecoes.e_controle_interno(tokens[0]):
        raise CaminhoInexistente(
            f"{path} endereça controle interno da Versão Consolidada, que não é conteúdo "
            "normativo e não pode ser alterado por Retificação."
        )


def _parent_of(content, path):
    """Contêiner que hospeda a folha do caminho, a folha, e a forma do contêiner."""
    tokens = parse_path(path)
    _recusar_controle_interno(tokens, path)
    parent, forma = content, ""
    for token in tokens[:-1]:
        parent, forma = _descer(parent, token, path, forma)
    return parent, tokens[-1], forma


def resolve_path(content, path):
    """Valor canônico atualmente em `path`, ou ABSENT quando o caminho não existe.

    A posição de acréscimo (`-`) nunca existe: nada há ali para ser sobrescrito. Chave que não
    está na coleção também não existe — aqui isso é ausência, não recusa: quem aplica é que
    precisa dizer `target_key_not_found`.
    """
    tokens = parse_path(path)
    _recusar_controle_interno(tokens, path)
    current, forma = content, ""
    for token in tokens:
        if isinstance(current, dict):
            if token not in current:
                return ABSENT
            current, forma = current[token], f"{forma}/{colecoes.escapar(token)}"
        elif isinstance(current, list):
            posicao = _posicao(current, token, path, forma, allow_append=False, estrito=False)
            if posicao is None:
                return ABSENT
            current, forma = current[posicao], f"{forma}/{colecoes.CURINGA}"
        else:
            return ABSENT
    return current


def add_overwrites(content, path):
    """`ADD` neste caminho substituiria conteúdo existente?

    Só em objeto: em lista, `ADD` acrescenta ao fim, sem apagar nada. É o que separa a
    sobrescrita silenciosa, que `conflicts.py` recusa, do acréscimo legítimo de um Perfil.
    """
    try:
        parent, leaf, _ = _parent_of(content, path)
    except ValueError:
        return False
    return isinstance(parent, dict) and leaf in parent


def _apply_to_dict(parent, leaf, operation, value, path):
    if operation in {"REPLACE", "REMOVE"} and leaf not in parent:
        raise CaminhoInexistente(f"Caminho inexistente: {path}")
    if operation == "REMOVE":
        del parent[leaf]
    else:
        parent[leaf] = value


def _validar_acrescimo(value, path, forma):
    """Quem entra numa coleção com chave precisa trazer a sua (FR-001).

    Sem esta verificação, `ADD /colecao/-` aceitava qualquer JSON: um Perfil sem `id` atravessava
    elaboração e Publicação e passava a integrar o conteúdo normativo como entidade que nenhuma
    Retificação futura poderia endereçar. Um `id` que não fosse texto era pior — quebrava a
    verificação de unicidade com `TypeError`, que a borda devolveria como erro interno.
    """
    if not colecoes.tem_chave(forma):
        return
    chave = value.get(colecoes.CAMPO_CHAVE) if isinstance(value, dict) else None
    if not isinstance(chave, str) or not _UUID.fullmatch(chave):
        raise EntidadeSemChave(
            f"O item acrescentado em {path} precisa ser um objeto com `id` no formato UUID. "
            "Sem identificador ele não poderia ser endereçado por nenhuma Retificação futura."
        )


def _apply_to_list(parent, leaf, operation, value, path, forma):
    if operation == "ADD":
        if leaf != APPEND_TOKEN:
            # `_posicao` primeiro, porque índice sobre coleção com chave é endereçamento
            # posicional e tem código próprio. O que sobra depois dele é o seletor.
            _posicao(parent, leaf, path, forma, allow_append=True, estrito=False)
            raise AcrescimoPosicionado(
                f"{path} pede acréscimo em posição específica, que não existe nesta gramática. "
                "Acréscimo é ao fim da coleção, com o token `-`."
            )
        _validar_acrescimo(value, path, forma)
        parent.append(value)
        return
    posicao = _posicao(parent, leaf, path, forma, allow_append=False, estrito=True)
    if posicao is None:
        raise CaminhoInexistente(f"Caminho inexistente: {path}")
    if operation == "REMOVE":
        del parent[posicao]
    else:
        parent[posicao] = value


def apply_change(content, change):
    """Aplica uma Alteração Normativa em `content`, no lugar. ValueError se o caminho não serve."""
    path = change["targetPath"]
    operation = change["operation"]
    if operation not in OPERATIONS:
        raise ValueError(f"Operação desconhecida: {operation}")
    parent, leaf, forma = _parent_of(content, path)
    value = deepcopy(change.get("newValue"))
    if isinstance(parent, dict):
        _apply_to_dict(parent, leaf, operation, value, path)
    elif isinstance(parent, list):
        _apply_to_list(parent, leaf, operation, value, path, forma)
    else:
        raise CaminhoInexistente(f"Caminho inexistente: {path}")


def apply_changes(base, changes, *, publication_id):
    result = deepcopy(base)
    provenance = {}
    for change in changes:
        apply_change(result, change)
        provenance[change["targetPath"]] = publication_id
    return result, provenance
