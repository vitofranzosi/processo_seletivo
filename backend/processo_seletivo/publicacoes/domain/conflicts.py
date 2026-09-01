"""Precondições de conteúdo por caminho alterado (FR-026, FR-036 da `001`).

`expectedPreviousHash` identifica o conteúdo que a pessoa responsável enxergava ao elaborar a
Alteração Normativa. Comparar esse hash com o conteúdo efetivamente vigente no `targetPath`
impede que uma Retificação sobrescreva silenciosamente outra publicada no intervalo entre a
elaboração e a Publicação.

O campo é opcional, mas `ADD` carrega uma precondição própria e não declarável: adicionar
pressupõe caminho ausente. Sem essa regra, um `ADD` sobre um caminho que outro ato criou seria
sobrescrita silenciosa que nem um cliente cuidadoso conseguiria evitar — não há como declarar
ausência num campo que guarda hash de conteúdo.

A regra vale apenas onde `ADD` de fato substitui, ou seja, em objeto. Em lista, `ADD` acrescenta
ao fim sem apagar nenhum elemento: incluir um Perfil é ato legítimo e não configura sobrescrita.

As precondições valem contra o conteúdo que cada alteração encontra, e não contra o conteúdo
inicial: um ato pode remover um caminho e recriá-lo em seguida.

Declarar o hash é opcional para o cliente, mas a verificação não é opcional para o sistema. Sem
declaração, `derive_preconditions` extrai a precondição da própria base declarada em
`baseSnapshotId` — que é, por construção, o conteúdo que a pessoa enxergava ao elaborar o ato.

**O que este módulo deixou de fazer.** A `003` guardava, além do hash, uma âncora de identidade
por índice atravessado, porque o hash responde "o valor ainda é este?" e não "ainda é esta
entidade?" — e com caminhos posicionais as duas perguntas eram distintas. Com o endereçamento
por chave, o próprio caminho nomeia a entidade, e não sobra índice para deslocar: a âncora
perdeu a pergunta que respondia e saiu inteira (FR-015). O hash ficou, porque a pergunta dele
continua de pé (FR-014).
"""

from copy import deepcopy

from processo_seletivo.publicacoes.domain import colecoes, elevacao
from processo_seletivo.publicacoes.domain.changes import (
    ABSENT,
    ChaveNaoEncontrada,
    add_overwrites,
    apply_change,
    resolve_path,
)
from processo_seletivo.shared.canonical import canonical_sha256

HASH_MISMATCH = "expected_hash_mismatch"
TARGET_PRESENT = "target_already_present"
KEY_NOT_FOUND = "target_key_not_found"
DUPLICATE_KEY = "duplicate_key_in_collection"


def previous_hash(content, target_path):
    """Hash canônico do conteúdo em `target_path`; vazio quando o caminho não existe."""
    value = resolve_path(content, target_path)
    return "" if value is ABSENT else canonical_sha256(value)


def _grafias_aceitas(content, target_path):
    """Os hashes que satisfazem a precondição neste caminho — em regra um, às vezes dois.

    Depois do incremento da `012`, a mesma Etapa tem duas grafias: a **literal**, que a consulta
    pública serve e que o `content_hash` da Publicação cobre, e a **elevada**, que a autoria compõe.
    Um cliente que leia o público e declare o hash de lá está fazendo exatamente o que o contrato
    manda — `expectedPreviousHash` é o hash do conteúdo que o autor encontrou — e recusá-lo
    transformaria o cuidadoso em caso de erro (012, T-017).

    **A condição, sem a qual isto vira buraco.** A grafia literal só é candidata enquanto as duas
    disserem a mesma coisa: os campos novos ainda exprimindo os valores que a ausência denota. Se
    uma Retificação publicada no intervalo declarou `maximumScore`, remover o campo devolveria a
    grafia antiga e o hash velho **passaria** — a precondição aprovando um ato escrito contra
    conteúdo que já não existe, que é o oposto de FR-036. Declarada máxima ou quantidade, vale só o
    hash da forma vigente.
    """
    valor = resolve_path(content, target_path)
    if valor is ABSENT:
        return {""}
    vigente = canonical_sha256(valor)
    if not isinstance(valor, dict):
        return {vigente}
    legado = {chave: valor.get(chave) for chave in elevacao.AUSENCIA if chave in valor}
    if not legado or any(
        valor.get(chave) != esperado for chave, esperado in elevacao.AUSENCIA.items()
    ):
        return {vigente}
    literal = {chave: item for chave, item in valor.items() if chave not in elevacao.AUSENCIA}
    return {vigente, canonical_sha256(literal)}


def duplicate_keys(content):
    """Coleções com chave em que algum identificador aparece mais de uma vez (FR-009).

    A unicidade é exigida **dentro** de cada coleção. Um identificador que apareça em duas
    coleções distintas do mesmo snapshot é irrelevante: a resolução é escopada à coleção que o
    caminho nomeia, e supor unicidade global seria uma invariante que ninguém garante.
    """
    repetidas = []
    for forma, lista in colecoes.colecoes_com_chave(content):
        vistos, repetidos = set(), set()
        for elemento in lista:
            chave = elemento.get(colecoes.CAMPO_CHAVE) if isinstance(elemento, dict) else None
            # Só texto é chave. `changes.py` já recusa acrescentar item sem `id` UUID; aqui a
            # exigência se repete porque esta função também lê conteúdo que ela não produziu, e
            # um `id` que fosse lista ou objeto quebraria o conjunto com `TypeError` — erro
            # interno onde deveria haver, no máximo, uma recusa.
            if not isinstance(chave, str):
                continue
            if chave in vistos:
                repetidos.add(chave)
            vistos.add(chave)
        repetidas.extend(f"{forma}/id={chave}" for chave in sorted(repetidos))
    return repetidas


def content_conflicts(content, changes):
    """Precondições que não se verificam em `content`, agrupadas por código de erro.

    Um `expectedPreviousHash` declarado prevalece sobre a regra do `ADD`: quem declara o
    conteúdo anterior sabe que o caminho está ocupado e assume a sobrescrita.

    A simulação também é onde a entidade endereçada é procurada: um caminho por chave que não
    resolve no conteúdo vigente é `target_key_not_found`, e não interrupção silenciosa (FR-008).
    Esse achado **substitui** a verificação de conteúdo, em vez de somar-se a ela: quando a
    entidade não está mais lá, dizer que o hash divergiu descreveria a consequência e esconderia
    a causa. Um caminho de objeto que deixou de existir é outro caso — ali o hash divergente é
    a resposta certa, e é o que continua sendo dito.

    A unicidade é verificada **depois de cada alteração**, e não só no estado final. Verificar só
    no fim deixava passar a substituição disfarçada: acrescentar um item com a chave de outro e
    remover o original em seguida termina com a coleção íntegra, mas no instante do acréscimo a
    chave já existia, e o que se publicou foi a troca de uma entidade por outra sob o mesmo
    identificador — que é o que FR-009 recusa.

    Repetição que já exista na base não é imputada ao ato: ele a encontrou, não a criou.
    """
    conflicts = {}
    current = deepcopy(content)
    preexistentes = set(duplicate_keys(current))
    for change in changes:
        path = change["targetPath"]
        seguinte = deepcopy(current)
        try:
            apply_change(seguinte, change)
            falha = None
        except ValueError as exc:
            falha = exc
        if isinstance(falha, ChaveNaoEncontrada):
            conflicts.setdefault(KEY_NOT_FOUND, []).append(path)
        else:
            declared = change.get("expectedPreviousHash")
            if declared:
                if declared not in _grafias_aceitas(current, path):
                    conflicts.setdefault(HASH_MISMATCH, []).append(path)
            elif change["operation"] == "ADD" and add_overwrites(current, path):
                conflicts.setdefault(TARGET_PRESENT, []).append(path)
        if falha is not None:
            # Alteração inaplicável ao conteúdo simulado: as seguintes partiriam de um
            # estado que não existe. A aplicabilidade é reportada por apply_changes.
            break
        novas = [
            repetida
            for repetida in duplicate_keys(seguinte)
            if repetida not in preexistentes and repetida not in conflicts.get(DUPLICATE_KEY, [])
        ]
        if novas:
            conflicts.setdefault(DUPLICATE_KEY, []).extend(novas)
        current = seguinte
    return conflicts


# `ADD` não tem "antes": acrescentar não sobrescreve, e a precondição própria do ADD é a ausência
# do caminho, verificada por `add_overwrites` e indeclarável como hash de conteúdo.
DERIVABLE_OPERATIONS = frozenset({"REPLACE", "REMOVE"})


def derive_preconditions(content, changes):
    """Hash do conteúdo que cada alteração encontra, na ordem em que serão aplicadas.

    O declarado pelo cliente prevalece. Cadeia vazia para `ADD` e para caminho inexistente, que
    é a ausência de precondição de conteúdo declarável.
    """
    derived = []
    current = deepcopy(content)
    for change in changes:
        declared = change.get("expectedPreviousHash")
        if declared:
            derived.append(declared)
        elif change["operation"] in DERIVABLE_OPERATIONS:
            derived.append(previous_hash(current, change["targetPath"]))
        else:
            derived.append("")
        try:
            apply_change(current, change)
        except ValueError:
            # Alteração inaplicável: as seguintes partiriam de um estado que não existe. A
            # aplicabilidade é reportada por apply_changes; aqui só se para de derivar.
            derived.extend([""] * (len(changes) - len(derived)))
            break
    return derived
