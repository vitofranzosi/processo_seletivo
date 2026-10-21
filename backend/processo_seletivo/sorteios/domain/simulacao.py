"""O sorteio fictício da prévia: população, relação e ordem de cada recorte, sem banco (098).

**Nenhuma regra própria de ordem.** A ordem é `chave.ordem`, a mesma função que `constituir_sorteio`
usa por `chaves` + `ordenar`. O que este módulo acrescenta são as entradas fictícias que a
composição pode ter: candidatos inventados, a relação de cada recorte numerada como a oficial e um
resumo dela.

**A única entrada que difere do sorteio oficial é o resumo da relação** (R-002). Ele muda *qual*
ordem sai, e não a forma de calcular — e por isso `ordem_do_recorte` aceita o resumo de fora: é por
ali que o teste de equivalência injeta o da relação publicada e prova que a prévia ordena como o
certame.

**Nenhum gerador de aleatoriedade, nem aqui nem em lugar nenhum deste app** (021, FR-026; R-004). A
semente chega pronta. Quem a sorteia é a interface, e `test_sem_gerador_pseudoaleatorio.py` varre
este arquivo como varre os outros.

**Nada de `classificacao` nem de `ocupacao` entra aqui.** Os nomes chegam por parâmetro (`nomear`),
e o corte e a ocupação são da camada de aplicação, que importa o que a direção `sorteios →
classificacao` permite.
"""

from dataclasses import dataclass

from processo_seletivo.shared.canonical import canonical_sha256
from processo_seletivo.sorteios.domain import chave

#: O passo entre as vagas de nome de uma lista e as da seguinte: a ampla e até seis reservadas. Cada
#: lista tem a sua sequência de nomes, e é isso que mantém o nome de quem já existia quando outra
#: lista cresce (FR-2490). As sequências não se cruzam — a lista `k` usa as vagas `k`, `k + 7`,
#: `k + 14`… —, e vagas distintas dão nomes distintos no repertório da `094`.
LISTAS_DE_NOMES = 7

#: A sugestão para a linha que não publica quantidade (FR-2487).
SUGESTAO_SEM_LINHA = 10


@dataclass(frozen=True)
class CandidatoFicticio:
    id: str
    nome: str
    #: `None` para quem concorre só na ampla.
    lista_id: str | None


@dataclass(frozen=True)
class RelacaoFicticia:
    lista_id: str | None
    #: `((numero_publico, candidato), …)`, de 1 a N, na ordem da população.
    participantes: tuple
    resumo: str


def sugestao(vagas):
    """O dobro das vagas publicadas na linha, e dez quando a linha não publica quantidade."""
    return SUGESTAO_SEM_LINHA if vagas is None else 2 * int(vagas)


def populacao(so_ampla, por_reservada, *, nomear):
    """Os candidatos fictícios: primeiro os só da ampla, depois os autodeclarados de cada reservada.

    `por_reservada` é `[(lista_id, quantos)]`, na ordem da derivação dos recortes. **O nome é da
    vaga da pessoa na lista dela, e não da posição na população**: a i-ésima autodeclarada da PPI
    tem sempre o mesmo nome, ainda que a ampla ganhe vinte pessoas antes dela.

    **Até seis reservadas, e a recusa mora aqui**: a sétima usaria as vagas de nome da ampla, e duas
    pessoas teriam o mesmo nome em silêncio. O limite da aplicação (`acima_do_limite`) diz a frase
    ao elaborador; este garante que nenhum outro chamador produza nomes repetidos.
    """
    if len(por_reservada) >= LISTAS_DE_NOMES:
        raise ValueError(
            f"Até {LISTAS_DE_NOMES - 1} listas reservadas: a seguinte repetiria os nomes da ampla."
        )
    candidatos = [
        CandidatoFicticio(id=f"a{i}", nome=nomear(i * LISTAS_DE_NOMES), lista_id=None)
        for i in range(int(so_ampla))
    ]
    for ordinal, (lista_id, quantos) in enumerate(por_reservada, start=1):
        candidatos += [
            CandidatoFicticio(
                id=f"{lista_id}-{i}",
                nome=nomear(ordinal + i * LISTAS_DE_NOMES),
                lista_id=str(lista_id),
            )
            for i in range(int(quantos))
        ]
    return candidatos


def relacao_ficticia(candidatos, *, perfil_id, lista_id):
    """A relação de um recorte: a ampla com todos, a reservada só com os dela, numeradas de 1 a N.

    **O resumo tem forma diferente da relação oficial, de propósito** (R-005): a chave
    `previaDoSorteio` não existe em `projecao.conteudo_canonico`, e por isso o resumo fictício nunca
    coincide com o de uma relação publicada nem se confunde com um.
    """
    membros = [c for c in candidatos if lista_id is None or c.lista_id == str(lista_id)]
    participantes = tuple(enumerate(membros, start=1))
    resumo = canonical_sha256(
        {
            "previaDoSorteio": True,
            "perfilId": str(perfil_id),
            "listaId": str(lista_id) if lista_id is not None else None,
            "participantes": [[numero, c.nome] for numero, c in participantes],
        }
    )
    return RelacaoFicticia(
        lista_id=str(lista_id) if lista_id is not None else None,
        participantes=participantes,
        resumo=resumo,
    )


def ordem_do_recorte(relacao, *, perfil_id, semente, relation_hash=None):
    """A ordem sorteada do recorte, no formato que o corte e a rodada da `094`/`095` leem.

    `relation_hash=None` usa o resumo da relação fictícia; o teste de equivalência passa o da
    relação oficial (R-009). **Sem empate, sempre**: o desempate da chave é pelo número público
    (§ 4.2 do contrato do algoritmo), e duas posições iguais não existem.
    """
    por_numero = dict(relacao.participantes)
    sorteados = chave.ordem(
        relation_hash=relation_hash or relacao.resumo,
        draw_scope_id=chave.recorte(perfil_id=perfil_id, lista_id=relacao.lista_id),
        seed=semente,
        public_numbers=list(por_numero),
    )
    return [
        {
            "inscricao_id": por_numero[numero].id,
            "posicao": posicao,
            "empate_residual": False,
            "numero_publico": numero,
        }
        for posicao, numero in enumerate(sorteados, start=1)
    ]


def semente_da_rodada(semente, indice):
    """A semente da `indice`-ésima rodada do resumo, derivada da exibida (FR-2502, D-006)."""
    return f"{semente}:{indice}"


__all__ = [
    "CandidatoFicticio",
    "RelacaoFicticia",
    "ordem_do_recorte",
    "populacao",
    "relacao_ficticia",
    "semente_da_rodada",
    "sugestao",
]
