"""A edição de uma Retificação em elaboração, como ato inteiro contra a mesma base (103, R-006).

**Por que existe.** `edit_retification` substitui o conjunto de Alterações de uma vez, e a tela que
edita mostra o **conteúdo proposto** — a base com o que o rascunho já declara. O que volta dela é a
diferença sobre esse proposto, e não o ato. Concatenar as duas listas parecia bastar, e não basta:
duas substituições no mesmo caminho teriam a precondição de conteúdo derivada da base
(`derive_preconditions`), e a segunda seria recusada na publicação por hash — depois de passar por
revisão e homologação.

**A fusão é por caminho.** Cada Alteração já gravada passa a valer o que o conteúdo conferido tem
no caminho dela; some quando o caminho deixou de existir ou voltou ao valor da base; e a da
diferença que cai dentro de uma gravada já foi absorvida por ela. O resto da diferença entra depois.

**E ela se confere a si mesma** (FR-2718). O ato fundido, aplicado à base, precisa produzir
exatamente o conteúdo que a pessoa conferiu. Se não produzir, a edição é recusada e nada é gravado:
uma regra sobre caminhos pode ter um caso que ninguém previu, e o que não pode acontecer é ela
gravar em silêncio um ato que diz outra coisa.
"""

from copy import deepcopy

from processo_seletivo.publicacoes.domain.changes import (
    ABSENT,
    SELETOR,
    apply_changes,
    resolve_path,
)

# A conferência e a fusão nunca se publicam; o identificador só preenche a proveniência que
# `apply_changes` monta e que ninguém lê aqui.
_CONFERENCIA = "edicao-da-retificacao"


class FusaoInconsistente(ValueError):
    """O ato fundido não reproduz o conteúdo conferido; nada deve ser gravado."""


def caminho_da_entidade(alteracao):
    """O caminho em que a Alteração passa a morar depois de aplicada.

    Acrescentar ao fim de uma coleção com chave (`/profiles/-`) cria uma entidade que, dali em
    diante, se endereça pelo seletor da chave dela (`/profiles/id=<uuid>`) — é por esse caminho que
    a tela de edição a mostra, e é por ele que a diferença a alcança.
    """
    caminho = alteracao["targetPath"]
    valor = alteracao.get("newValue")
    if (
        alteracao["operation"] == "ADD"
        and caminho.endswith("/-")
        and isinstance(valor, dict)
        and valor.get("id")
    ):
        return f"{caminho[:-1]}{SELETOR}{valor['id']}"
    return caminho


def _dentro(caminho, de):
    return caminho == de or caminho.startswith(f"{de}/")


def aplicar(base, alteracoes):
    resultado, _ = apply_changes(base, alteracoes, publication_id=_CONFERENCIA)
    return resultado


def fundir(base, existentes, diferenca, *, desfeitas=()):
    """O ato inteiro que leva `base` ao conteúdo que a pessoa conferiu.

    - `base`: o conteúdo da versão em que a Retificação se apoia, na forma vigente;
    - `existentes`: as Alterações gravadas, na ordem;
    - `diferenca`: as Alterações que a tela derivou contra o conteúdo proposto;
    - `desfeitas`: os índices, em `existentes`, das remoções que a pessoa desfez (FR-2719).

    Devolve `(alteracoes, conferido)`. Levanta `FusaoInconsistente` se o ato fundido não reproduz o
    conferido, e `ValueError` se a diferença não se aplica ao proposto — as duas recusas que a tela
    devolve sem gravar.
    """
    desfeitas = set(desfeitas)
    mantidas = [
        alteracao
        for indice, alteracao in enumerate(existentes)
        if not (indice in desfeitas and alteracao["operation"] == "REMOVE")
    ]
    proposto = aplicar(base, mantidas)
    conferido = aplicar(proposto, diferenca)

    fundidas, absorvem = [], []
    for alteracao in mantidas:
        caminho = caminho_da_entidade(alteracao)
        absorvem.append(caminho)
        if alteracao["operation"] == "REMOVE":
            fundidas.append(alteracao)
            continue
        valor = resolve_path(conferido, caminho)
        if valor is ABSENT:
            # O acréscimo que a edição removeu sai do ato sem virar remoção — a entidade nunca
            # existiu no conteúdo vigente —, e a substituição dentro de algo removido não tem mais
            # onde valer.
            continue
        if alteracao["operation"] == "REPLACE" and valor == resolve_path(base, caminho):
            # Voltou ao vigente: a Alteração não muda mais nada.
            continue
        fundidas.append({**alteracao, "newValue": deepcopy(valor)})

    for alteracao in diferenca:
        if not any(_dentro(alteracao["targetPath"], caminho) for caminho in absorvem):
            fundidas.append(alteracao)

    if aplicar(base, fundidas) != conferido:
        raise FusaoInconsistente(
            "Não foi possível conciliar esta edição com as alterações já declaradas sem mudar o "
            "que você conferiu. Nada foi gravado. Abra a Retificação de novo e refaça a edição em "
            "partes menores."
        )
    return fundidas, conferido
