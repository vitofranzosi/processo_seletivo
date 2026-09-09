"""A chave de cada participante e a ordem que ela produz — `IFES-SORTEIO-SHA256-v1`.

Função pura, sem Django e sem banco: é este módulo que o `contracts/algoritmo-sorteio.md`
descreve, e é dele que uma pessoa fora da instituição precisa de uma reimplementação. Nada aqui
consulta o mundo; tudo entra por parâmetro.

**As cinco entradas são cinco, e a assinatura é a garantia disso** (FR-024). A chave recebe
domínio, resumo da relação, identidade do recorte, semente e número público — e mais nada. Um
valor escolhido por qualquer ator depois do congelamento não tem por onde entrar: não há
`**kwargs`, não há dicionário de extras, e acrescentar campo aqui é mudar a versão do algoritmo,
que é ato normativo (FR-027).

**Por que a ordenação é função separada da chave.** O § 4 do contrato — ordem crescente, desempate
por número público — é regra própria, e o desempate precisa de prova executável que a chave não
pode dar: não existe entrada válida do sistema que produza dois resumos iguais, porque números
públicos iguais em relações distintas têm `relationHash` distintos e na mesma relação a numeração é
única. Separar `ordenar` de `chave` é o que torna o desempate testável sem prometer colisão de
SHA-256, que ninguém constrói (R-004, FR-028).
"""

import hashlib

from processo_seletivo.shared.canonical import canonical_bytes

# Literal e invariante nesta versão. Separador de domínio: impede que um resumo calculado para
# outro fim do sistema colida de propósito com uma chave de sorteio.
DOMINIO = "processo-seletivo/sorteio/v1"

# O que o Edital publica quando declara o algoritmo. Trocar qualquer regra deste módulo é publicar
# `…-v2`, e é ato da classe da Retificação.
ALGORITMO = "IFES-SORTEIO-SHA256-v1"


def bytes_canonicos(*, relation_hash, draw_scope_id, seed, public_number) -> bytes:
    """Os bytes que entram no resumo, exatamente como o § 2 do contrato os descreve.

    Exposta separadamente porque os vetores normativos os publicam: quem reimplementa confere
    primeiro os bytes e só depois o resumo, e um erro de serialização deixa de parecer erro de
    SHA-256.
    """
    return canonical_bytes(
        {
            "domain": DOMINIO,
            "drawScopeId": str(draw_scope_id),
            "publicNumber": int(public_number),
            "relationHash": str(relation_hash),
            "seed": str(seed),
        }
    )


def chave(*, relation_hash, draw_scope_id, seed, public_number) -> str:
    """A chave de um participante: SHA-256 dos bytes canônicos, em hexadecimal minúsculo."""
    return hashlib.sha256(
        bytes_canonicos(
            relation_hash=relation_hash,
            draw_scope_id=draw_scope_id,
            seed=seed,
            public_number=public_number,
        )
    ).hexdigest()


def chaves(*, relation_hash, draw_scope_id, seed, public_numbers) -> dict[int, str]:
    """A chave de cada número público, sem ordenar."""
    return {
        int(numero): chave(
            relation_hash=relation_hash,
            draw_scope_id=draw_scope_id,
            seed=seed,
            public_number=numero,
        )
        for numero in public_numbers
    }


def ordenar(chaves_por_numero) -> list[int]:
    """Os números públicos na ordem do sorteio: chave crescente, desempate por número crescente.

    Comparar a representação hexadecimal minúscula dá o mesmo resultado que comparar os 32 bytes,
    porque o comprimento é fixo — e é o que permite ao verificador de terceiro usar qualquer das
    duas. O desempate é o § 4.2, e é a única regra deste módulo que a chave sozinha não exercita.
    """
    return [
        numero
        for numero, _ in sorted(
            ((int(numero), str(valor)) for numero, valor in chaves_por_numero.items()),
            key=lambda par: (par[1], par[0]),
        )
    ]


def ordem(*, relation_hash, draw_scope_id, seed, public_numbers) -> list[int]:
    """Do universo à ordem, numa chamada: calcula as chaves e as ordena.

    **Todos os participantes recebem posição** (FR-025). Não há corte por número de vagas aqui, e
    não haverá em lugar nenhum: quem ocupa vaga é pergunta de outra capacidade (FR-064).
    """
    return ordenar(
        chaves(
            relation_hash=relation_hash,
            draw_scope_id=draw_scope_id,
            seed=seed,
            public_numbers=public_numbers,
        )
    )


def recorte(*, perfil_id, lista_id=None) -> str:
    """`drawScopeId`: `<perfilId>` sem lista, `<perfilId>:<listaId>` com ela.

    O marco não entra: ele já está dentro do `relationHash`, que cobre `milestoneId`, e é o
    `relationHash` que separa as chaves de relações distintas (021, N1).
    """
    return f"{perfil_id}:{lista_id}" if lista_id else str(perfil_id)


__all__ = [
    "ALGORITMO",
    "DOMINIO",
    "bytes_canonicos",
    "chave",
    "chaves",
    "ordem",
    "ordenar",
    "recorte",
]
