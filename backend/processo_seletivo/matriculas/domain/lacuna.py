"""O que saiu vazio, e por quê — o conceito que esta feature acrescenta ao domínio (`FR-439`).

**Uma coluna vazia gerada por regra é uma afirmação verificável de ausência; uma coluna preenchida
por dedução humana é indistinguível de dado declarado.** É essa diferença que justifica a feature, e
é por isso que a lacuna é objeto de domínio e não mensagem de tela: ela tem espécie, razão e
quantidade, e o relatório deriva dela em vez de descrevê-la por fora.

**Sem o relatório, a lacuna vira preenchimento manual às pressas** — e o erro volta pela porta que a
feature existe para fechar. Por isso a `US2` é P1 junto com a que gera o arquivo, e por isso o
resumo aparece **antes** do download (`UX-060`): depois dele, ninguém lê.
"""

from dataclasses import dataclass

from processo_seletivo.matriculas.domain import nomes


@dataclass(frozen=True)
class Lacuna:
    """A razão pela qual **esta** célula não traz o valor que o destino esperaria.

    `valor_declarado` só existe na lacuna **nominal**: ela é o caso em que o sistema tem um valor e
    o destino não o comporta, e dizer qual valor era é o que impede a declaração de sumir em
    silêncio.
    """

    especie: str
    razao: str
    valor_declarado: str = ""


@dataclass(frozen=True)
class ItemDoRelatorio:
    """Uma coluna, a razão de ela ter saído vazia, e quantas linhas isso alcançou.

    `pessoas` traz nome e protocolo de quem foi alcançado, e **só na lacuna nominal**: listar quem
    não declarou o nome do pai seria expor uma ausência legítima sem nenhum ganho para quem lê.
    """

    coluna: str
    especie: str
    razao: str
    quantidade: int
    pessoas: tuple = ()


# **O aviso que vai em toda geração** (`FR-452`, `D-002`). Ele não é lacuna de valor — a coluna 31
# sai **preenchida** —, é lacuna de significado: o que este sistema mede e o que o destino define
# são coisas diferentes com os mesmos limites.
#
# **Por isso ele aparece mesmo quando não há nenhuma outra lacuna** (`SC-153`): o desvio é
# sistemático, cresce com o tamanho da família e é sempre no mesmo sentido. Quem recebe o arquivo
# fica em condição de decidir o que fazer com isso; quem o gera não decide por ele.
AVISO_DA_RENDA = ItemDoRelatorio(
    coluna="RENDA_PER_CAPITA_PNP",
    especie=nomes.DIVERGENCIA,
    razao=(
        "A coluna traz a faixa da renda somada da família, que é o que este sistema coleta, num "
        "campo que o destino define como renda por pessoa. Os limites das duas listas coincidem e "
        "os denominadores não: uma família de quatro pessoas com 2 salários mínimos declara "
        "«de 1,5 a 2,5» aqui e está em 0,5 por pessoa. O desvio é sempre para cima e cresce com o "
        "tamanho da família."
    ),
    quantidade=0,
)


def consolidar(lacunas_por_pessoa) -> tuple:
    """As lacunas de todas as linhas, agrupadas por coluna — mais o aviso obrigatório.

    Recebe uma sequência de `(pessoa, coluna, lacuna)`, onde `pessoa` é o texto que identifica quem
    foi alcançado. Devolve os itens na ordem em que as colunas saem no arquivo, que é a ordem em que
    quem lê vai procurá-las.

    **O aviso da renda entra sempre, e entra primeiro.** Ele é o único item que não depende de
    nenhuma linha ter faltado, e pô-lo no fim o faria ser lido depois de quem já decidiu que
    entendeu o relatório.
    """
    agrupadas = {}
    for pessoa, coluna, lacuna in lacunas_por_pessoa:
        chave = (coluna, lacuna.especie, lacuna.razao)
        atingidas = agrupadas.setdefault(chave, [])
        if lacuna.especie == nomes.NOMINAL:
            declarado = f" — declarou «{lacuna.valor_declarado}»" if lacuna.valor_declarado else ""
            atingidas.append(f"{pessoa}{declarado}")
        else:
            atingidas.append("")
    itens = [
        ItemDoRelatorio(
            coluna=coluna,
            especie=especie,
            razao=razao,
            quantidade=len(atingidas),
            pessoas=tuple(nome for nome in atingidas if nome),
        )
        for (coluna, especie, razao), atingidas in agrupadas.items()
    ]
    return (AVISO_DA_RENDA, *itens)
