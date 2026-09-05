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

**A identidade das entidades é substrato de endereçamento, não conteúdo normativo.** Três regras
decorrem disso, e valem para qualquer operação e qualquer caminho, não só para o `ADD`:

- toda coleção declarada continua sendo uma coleção;
- todo elemento de coleção com chave carrega `id` UUID, depois de a alteração ser aplicada;
- o `id` de um elemento de coleção com chave não é endereçável;
- **a topologia das identidades só muda onde o ato a endereça**: `ADD /colecao/-` acrescenta uma,
  `REMOVE /colecao/id=X` retira aquela e o que estava dentro dela, e nenhuma outra operação
  cria ou destrói identidade nenhuma.

A última é a que generaliza as outras tentativas. Comparar o `id` do elemento substituído
alcançava um caso de vários: `REPLACE /profiles` trocava a lista inteira por outras entidades, e
`REPLACE` de um Perfil preservando o `id` dele apagava as Modalidades de dentro — em ambos, um
caminho já publicado deixava de nomear a entidade que nomeava sem que o ato a tivesse endereçado.
Vigiar a topologia antes e depois alcança os dois, e os que eu não pensei.
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


class CampoNaoRetificavel(ValueError):
    """Campo que existe no conteúdo publicado e que a Retificação não altera no lugar.

    Distinta de `IdentidadeNaoEnderecavel`: o identificador não é conteúdo normativo, e este é —
    o que ele tem de próprio é que alterá-lo reinterpretaria o que já foi gravado sob ele.
    """


class ColecaoAtomica(ValueError):
    """Endereçamento item a item de coleção sem identificador (FR-011)."""


class AcrescimoPosicionado(ValueError):
    """`ADD` em lista com folha diferente de `-` (FR-006).

    Inserção em posição específica não existe nesta gramática. Um seletor resolveria a posição
    de uma entidade existente e inseriria antes dela — que é a operação que a feature retirou.
    """


class EntidadeSemChave(ValueError):
    """A alteração deixaria elemento de coleção com chave sem `id` UUID (FR-001, FR-012)."""


class ColecaoDescaracterizada(ValueError):
    """A alteração deixaria uma coleção declarada sem ser lista, tornando a declaração falsa."""


class IdentidadeNaoEnderecavel(ValueError):
    """O caminho endereça o `id` de uma entidade, que é substrato e não conteúdo (FR-018)."""


class IdentidadeImplicita(ValueError):
    """A alteração criaria ou destruiria identidades sem endereçar a coleção delas (FR-018)."""


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


def _recusar_colecao_atomica(path, forma):
    if colecoes.e_atomica(forma):
        raise ColecaoAtomica(
            f"{forma} é coleção sem identificador e vale como valor único: "
            f"substitua a lista inteira em vez de endereçar {path}."
        )


def _posicao(lista, token, path, forma, *, allow_append, estrito):
    """Posição que `token` designa em `lista`, ou None quando não designa nenhuma.

    `forma` é a forma da coleção — é ela que diz se há chave, e portanto se o índice é recusado.
    `estrito` separa quem aplica de quem só lê: aplicar sobre chave inexistente é recusa com
    código próprio; ler o conteúdo anterior de um caminho que não existe é apenas ausência.
    """
    _recusar_colecao_atomica(path, forma)
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
    if tokens and colecoes.e_campo_de_identidade(tokens[0]):
        raise CaminhoInexistente(
            f"{path} endereça {tokens[0]}, que identifica o conteúdo publicado e não pode ser "
            "alterado por Retificação. Corrigir a identificação do Edital ou do Processo é outro "
            "ato, e não uma alteração do conteúdo normativo."
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


def _chave_de(elemento):
    chave = elemento.get(colecoes.CAMPO_CHAVE) if isinstance(elemento, dict) else None
    return chave if isinstance(chave, str) and _UUID.fullmatch(chave) else None


def _identidade_permitida(change, path, forma):
    """Prefixo sob o qual esta alteração pode criar ou destruir identidades. `None` se nenhum.

    `ADD /colecao/-` pode acrescentar a entidade nova e tudo o que vier dentro dela.
    `REMOVE /colecao/id=X` pode retirar X e tudo o que estava dentro de X. Qualquer outra
    operação precisa deixar a topologia intacta.

    `forma` é a do contêiner, e a permissão depende dela: sem essa condição, um caminho que
    apenas *pareça* endereçar uma coleção — `-` como nome literal de chave num objeto, ou um
    seletor sobre um objeto — receberia uma permissão que não corresponde a coleção nenhuma.
    Nada é explorável por aí hoje, mas permissão concedida sobre premissa errada é o que fica
    esperando a próxima coleção declarada.
    """
    if not colecoes.tem_chave(forma):
        return None
    operacao = change["operation"]
    if operacao == "ADD" and path.endswith(f"/{APPEND_TOKEN}"):
        nova = _chave_de(change.get("newValue"))
        colecao = path[: -len(APPEND_TOKEN) - 1]
        # `nova` vazia não chega aqui: `_recusar_entidades_sem_chave` já recusou o acréscimo sem
        # `id` utilizável. O ramo fica porque falha para o lado seguro — sem permissão, e portanto
        # com recusa — se a ordem dessas verificações mudar um dia.
        return f"{colecao}/{colecoes.CAMPO_CHAVE}={nova}" if nova else None
    if operacao == "REMOVE" and selector_uuid(parse_path(path)[-1]) is not None:
        return path
    return None


def _recusar_identidades_implicitas(antes, depois, change, path, forma):
    permitido = _identidade_permitida(change, path, forma)

    def fora(identidades):
        return sorted(
            identidade
            for identidade in identidades
            if permitido is None or not identidade.startswith(permitido)
        )

    criadas, destruidas = fora(depois - antes), fora(antes - depois)
    if criadas or destruidas:
        raise IdentidadeImplicita(
            f"{path} criaria ou destruiria identidades que não endereça: "
            f"{', '.join(criadas + destruidas)}. Entidade se acrescenta com `/colecao/-` e se "
            "retira com `/colecao/id=<uuid>`; nenhuma outra alteração pode fazer uma aparecer ou "
            "desaparecer, senão um caminho já publicado deixaria de nomear a entidade que nomeava."
        )


def _recusar_entidades_sem_chave(content, path):
    """Nenhuma alteração pode deixar entidade que ninguém consiga endereçar depois.

    Verificado sobre o **resultado**, e não sobre o valor de uma operação em particular: a mesma
    entidade sem chave entrava por `ADD`, por `REPLACE` do Perfil inteiro, por `REPLACE` ou
    `REMOVE` do campo `id`, e por `REPLACE` de `/profiles` de uma vez. Vigiar o estado alcança as
    quatro portas; vigiar a operação alcançava uma.
    """
    descaracterizadas = colecoes.declaradas_que_nao_sao_lista(content)
    if descaracterizadas:
        raise ColecaoDescaracterizada(
            f"{path} deixaria {', '.join(descaracterizadas)} sem ser uma coleção. A declaração de "
            "quais coleções têm chave é a premissa da gramática, e alterá-la por dentro de uma "
            "Retificação a tornaria falsa sem que nada acusasse."
        )
    for forma, lista in colecoes.colecoes_com_chave(content):
        for posicao, elemento in enumerate(lista):
            if _chave_de(elemento) is None:
                raise EntidadeSemChave(
                    f"{path} deixaria o item {posicao} de {forma} sem `id` no formato UUID. "
                    "Sem identificador ele não poderia ser endereçado por nenhuma Retificação "
                    "futura."
                )


def _apply_to_list(parent, leaf, operation, value, path, forma):
    # Antes de qualquer atalho: `ADD` com a folha `-` não passa por `_posicao`, e sem esta linha
    # acrescentava item a `requirements` — a única operação que ainda alterava uma coleção
    # atômica item a item (FR-011).
    _recusar_colecao_atomica(path, forma)
    if operation == "ADD":
        if leaf != APPEND_TOKEN:
            # `_posicao` primeiro, porque índice sobre coleção com chave é endereçamento
            # posicional e tem código próprio. O que sobra depois dele é o seletor.
            _posicao(parent, leaf, path, forma, allow_append=True, estrito=False)
            raise AcrescimoPosicionado(
                f"{path} pede acréscimo em posição específica, que não existe nesta gramática. "
                "Acréscimo é ao fim da coleção, com o token `-`."
            )
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
    # **Depois** de `_parent_of`, e não antes: caminho inexistente e seletor inválido têm
    # precedência, porque um caminho que não existe não endereça campo algum — retificável ou não.
    if colecoes.e_campo_nao_retificavel(f"{forma}/{colecoes.escapar(leaf)}"):
        raise CampoNaoRetificavel(
            f"{path} endereça um campo que a Retificação não altera no lugar. Mudar o tipo de um "
            "fato declarado cria fato novo: remova este e acrescente outro, com identidade "
            "própria, para que o valor congelado sob o primeiro continue legível sob a norma "
            "que o governou."
        )
    if leaf == colecoes.CAMPO_CHAVE and colecoes.e_elemento_de_colecao_com_chave(forma):
        raise IdentidadeNaoEnderecavel(
            f"{path} endereça o identificador da entidade, que é o substrato do endereçamento e "
            "não conteúdo normativo. Alterá-lo faria um caminho já publicado deixar de nomear a "
            "entidade que ele nomeava."
        )
    antes = colecoes.identidades(content)
    value = deepcopy(change.get("newValue"))
    if isinstance(parent, dict):
        _apply_to_dict(parent, leaf, operation, value, path)
    elif isinstance(parent, list):
        _apply_to_list(parent, leaf, operation, value, path, forma)
    else:
        raise CaminhoInexistente(f"Caminho inexistente: {path}")
    _recusar_entidades_sem_chave(content, path)
    _recusar_identidades_implicitas(antes, colecoes.identidades(content), change, path, forma)


def apply_changes(base, changes, *, publication_id):
    result = deepcopy(base)
    provenance = {}
    for change in changes:
        apply_change(result, change)
        provenance[change["targetPath"]] = publication_id
    return result, provenance
