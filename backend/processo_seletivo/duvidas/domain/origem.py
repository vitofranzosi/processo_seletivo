"""De qual ato publicado vem cada valor da versão vigente (070, `R-004`, `FR-1437`).

A versão consolidada guarda, por caminho alterado, a publicação que o produziu
(`ProvenienciaConteudo`). Duas coisas impedem ler essa tabela pelo caminho mais longo.

- **Ela só acrescenta.** `consolidate` faz `provenance.update(...)` ato a ato, e a substituição
  posterior de um Perfil inteiro não apaga o registro antigo de um campo dele
  (`publicacoes/domain/consolidation.py`). O caminho mais longo daria a Retificação de antes, cujo
  valor já não vigora.
- **Valor composto tem mais de uma origem.** O quadro de vagas com uma linha retificada e as outras
  originais não vem de um ato só.

Por isso a regra é a da aplicação: vence o **último ato aplicado** entre os que escreveram o próprio
caminho ou um ancestral dele; os descendentes alterados **depois** desse ato acrescentam a origem
deles. Sem registro nenhum, vale a publicação original, que é a primeira dos atos aplicados.

**Por que isso torna o link correto.** O documento de um ato é composto da base dele mais as
alterações dele: contém sempre os valores que ele fixou. O documento que a página pública chama de
"Edital completo" pode não conter (achado de 12/10, `D-004`).
"""

from __future__ import annotations

from processo_seletivo.publicacoes.domain.changes import ABSENT, resolve_path

#: A folha do acréscimo ao fim de uma coleção (`ADD /colecao/-`, gramática da `004`).
ACRESCIMO = "/-"


def _ancestral_ou_proprio(alvo: str, caminho: str) -> bool:
    return caminho == alvo or caminho.startswith(alvo + "/")


def _descendente(alvo: str, caminho: str) -> bool:
    return alvo.startswith(caminho + "/")


def origens(caminho, proveniencias, atos):
    """Os atos de que vem o valor em `caminho`, na ordem de aplicação.

    `proveniencias` são pares `(target_path, publicacao_id)`; `atos` são os `AtoPublicado` da
    versão, **na ordem de aplicação** — `(effective_at, publication_order)` —, a original primeiro.
    """
    if not atos:
        return ()
    posicao = {ato.publicacao_id: indice for indice, ato in enumerate(atos)}
    por_id = {ato.publicacao_id: ato for ato in atos}

    escritores = [
        posicao[publicacao]
        for alvo, publicacao in proveniencias
        if publicacao in posicao and _ancestral_ou_proprio(alvo, caminho)
    ]
    vencedor = max(escritores) if escritores else 0

    depois = sorted(
        {
            posicao[publicacao]
            for alvo, publicacao in proveniencias
            if publicacao in posicao
            and _descendente(alvo, caminho)
            and posicao[publicacao] > vencedor
        }
    )
    indices = [vencedor, *depois]
    return tuple(por_id[atos[indice].publicacao_id] for indice in indices)


def colecoes_acrescidas(proveniencias):
    """As coleções a que algum ato acrescentou entidade: `/profiles`, e não `/profiles/-`."""
    return tuple(
        sorted({alvo[: -len(ACRESCIMO)] for alvo, _ in proveniencias if alvo.endswith(ACRESCIMO)})
    )


def _no_documento(conteudo, caminho):
    try:
        return resolve_path(conteudo, caminho) is not ABSENT
    except ValueError:
        return False


def acrescimos(proveniencias, conteudo, atos, conteudos_dos_atos):
    """Os registros que a proveniência não tem: a entidade acrescentada por Retificação.

    **O acréscimo é gravado pelo caminho literal** — `/profiles/-`, e não `/profiles/id=<novo>` —, e
    `consolidate` guarda um registro por caminho: o segundo ato que acrescenta um Perfil apaga o
    registro do primeiro. Sem isto, o cartão do Perfil acrescentado caía na regra "sem registro,
    vale a original" e levava a um documento que não o contém.

    A regra: a entidade vem do **primeiro ato, na ordem de aplicação, cujo documento a contém**. O
    documento de cada ato é a base dele mais ele (`R-005`), e por isso o link resultante contém o
    valor (`SC-535`). A tabela das alterações não é lida: é fronteira da consulta (`FR-1412`).
    """
    if not atos or not conteudos_dos_atos:
        return ()
    novos = []
    for colecao in colecoes_acrescidas(proveniencias):
        try:
            itens = resolve_path(conteudo, colecao)
        except ValueError:
            continue
        if not isinstance(itens, list):
            continue
        for item in itens:
            if not isinstance(item, dict) or item.get("id") is None:
                continue
            caminho = f"{colecao}/id={item['id']}"
            primeiro = next(
                (
                    ato
                    for ato in atos
                    if ato.publicacao_id in conteudos_dos_atos
                    and _no_documento(conteudos_dos_atos[ato.publicacao_id], caminho)
                ),
                None,
            )
            if primeiro is not None and primeiro is not atos[0]:
                novos.append((caminho, primeiro.publicacao_id))
    return tuple(novos)
