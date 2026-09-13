"""Quem é titular, quem é suplente e quem é chamável — puro, e numa ordem só (019, `FR-266`).

**Esta feature não conta vagas** (`UX-035`). Quem responde *"quantas estão ocupadas"* é a `016`, e
é dela que vem `titulares_iniciais`: reimplementar a travessia aqui daria duas respostas à mesma
pergunta, e a primeira regra nova as faria divergir. O que este módulo acrescenta é a **cauda** —
quem vem depois do último titular, e em que ordem é chamado.

**Sem banco e sem norma.** O que entra é a sequência da faixa, os conjuntos de quem ocupa, de quem
já tem chamada em aberto e de quem já encerrou, e o que sai é uma lista na ordem de chamada. É o
que permite testar o 77/2026 inteiro sem migrar nada.

**A fila não é coluna de posição.** Ela é derivada da ordem vigente a cada leitura, como a faixa da
`014` e a vigência da `016`: guardar "posição na fila" exigiria `UPDATE` em tabela append-only e
faria a reclassificação reescrever o passado em vez de acrescentar um ato.
"""

from processo_seletivo.convocacao.domain import nomes
from processo_seletivo.ocupacao.domain.apuracao import chave_da_inscricao, elegiveis_em_ordem

#: Os desfechos que **encerram** a participação da pessoa naquele recorte: ela não volta a ser
#: chamável sem ato novo. A reclassificação não está aqui de propósito — ela move na fila, e a
#: `D-008` proíbe afirmar que o reclassificado perdeu habilitação.
DESFECHOS_QUE_ENCERRAM = (
    nomes.INDEFERIMENTO,
    nomes.DESISTENCIA_EXPRESSA,
    nomes.NAO_ATENDIMENTO,
    nomes.INERCIA,
)


def alcancados(*, progrediram_em_ordem, habilitadas, ocupantes_da_ampla=()):
    """A faixa que habilitou, na ordem: titulares primeiro, suplentes depois.

    **O teto é a faixa, e não o quadro.** Quem está fora dela não é suplente — é quem a `014` não
    selecionou, e chamá-lo seria selecionar. Ampliar a faixa é ato da `014`, pela `016`.
    """
    return elegiveis_em_ordem(
        progrediram_em_ordem=progrediram_em_ordem,
        habilitadas=habilitadas,
        ocupantes_da_ampla=ocupantes_da_ampla,
    )


def titulares(*, alcancados_em_ordem, efetivas):
    """Os primeiros `efetivas` alcançados — os que ocupam vaga desde o início."""
    return list(alcancados_em_ordem[: max(int(efetivas), 0)])


def suplentes(*, alcancados_em_ordem, efetivas):
    """A cauda: quem está na faixa, habilitou, e não ocupa vaga até que uma vague.

    **Suplente não ocupa nada**, e é a frase que o `min` da contagem antiga apagava: no 77/2026 são
    40 vagas com 30 suplentes na mesma faixa, e contá-los como ocupação daria 70 de 40.
    """
    return list(alcancados_em_ordem[max(int(efetivas), 0) :])


def ordem_de_chamada(
    *,
    alcancados_em_ordem,
    servidos=(),
    com_chamada_em_aberto=(),
    encerrados=(),
    reclassificados=(),
    reabilitados=(),
):
    """Quem pode ser chamado, na ordem em que deve ser (`FR-266`, `FR-292b`).

    Sai de fora quem **já foi servido** — respondeu com aceite ou regularização —, quem tem
    **chamada em aberto** — a pessoa ainda está dentro do prazo dela — e quem **encerrou** por um
    dos quatro desfechos que põem fim à participação no recorte.

    **Servido, e não ocupante.** Pela contagem da `016` os titulares ocupam vaga desde a emissão da
    apuração, antes de qualquer chamada; tirar os ocupantes daqui faria a primeira convocação do
    certame ser recusada por não haver quem chamar. O que dispensa uma segunda chamada é a pessoa
    **ter respondido**, e não a aritmética já a ter contado.

    **O reabilitado por deferimento vem primeiro, e não onde a ordem o colocaria** (`FR-292b`). A
    `018` devolveu a ele uma habilitação que ele deveria ter tido desde o começo, e chamá-lo depois
    de quem passou à frente enquanto o recurso corria seria executar a decisão pela metade.

    **O reclassificado vem por último, depois do último suplente** (`FR-291`). Ele não perdeu
    habilitação — a `D-008` proíbe afirmá-lo —, mas abriu mão da vez; e só volta a ser chamável
    quando não há mais ninguém antes dele.
    """
    fora = {chave_da_inscricao(i) for i in servidos}
    fora |= {chave_da_inscricao(i) for i in com_chamada_em_aberto}
    fora |= {chave_da_inscricao(i) for i in encerrados}
    adiados = {chave_da_inscricao(i) for i in reclassificados}
    a_frente = {chave_da_inscricao(i) for i in reabilitados}

    topo, corpo, cauda = [], [], []
    for identificador in alcancados_em_ordem:
        chave = chave_da_inscricao(identificador)
        if chave in fora:
            continue
        if chave in a_frente:
            topo.append(identificador)
        elif chave in adiados:
            cauda.append(identificador)
        else:
            corpo.append(identificador)
    return topo + corpo + cauda


def regularizaveis(*, progrediram_em_ordem, habilitadas, ja_chamados=()):
    """Quem a faixa alcançou e **não** habilitou, na ordem — os indeferidos (019, `US3`).

    **É o complemento de `alcancados`, e não um subconjunto dele.** Quem tem o Resultado indeferido
    não ocupa vaga e não é chamável para uma; o que a convocação para regularizar lhe oferece é
    corrigir o que faltou, e a ordem entre eles é a mesma ordem de classificação — o item 8.2 do
    77/2026 não abre exceção para quem corrige.

    **Quem está fora da faixa não entra.** O indeferimento não apaga a fronteira do corte: chamar
    para regularizar quem a `014` não selecionou seria selecioná-lo por outra porta.
    """
    habilitadas_de = {chave_da_inscricao(i) for i in habilitadas}
    chamados = {chave_da_inscricao(i) for i in ja_chamados}
    fora, vistas = [], set()
    for identificador in progrediram_em_ordem:
        chave = chave_da_inscricao(identificador)
        if chave in vistas:
            continue
        vistas.add(chave)
        if chave not in habilitadas_de and chave not in chamados:
            fora.append(identificador)
    return fora


def proximo(fila):
    """O próximo a chamar, ou `None` quando a lista alcançada esgotou.

    `None` **não** é "não há mais candidatos": é "não há mais quem chamar dentro do teto que o
    Edital publicou". A faixa seguinte é ato da `014`, e esta feature não a pede — oferecer um botão
    que ela não pode cumprir é o defeito que a `UX-037` proíbe.
    """
    return fila[0] if fila else None


def esgotou(fila):
    """Não há mais ninguém chamável dentro da faixa alcançada (`lista_alcancada_esgotada`)."""
    return not fila


def precedencia(fila, inscricao):
    """Quem está antes desta Inscrição na ordem de chamada, e ainda não foi chamado.

    **É a lista, e não um booleano**, porque a recusa precisa nomear quem foi pulado: *"há alguém
    antes dela"* não diz a quem conduz o certame o que fazer. Vazia significa que ela é a próxima.
    """
    alvo = chave_da_inscricao(inscricao)
    anteriores = []
    for identificador in fila:
        if chave_da_inscricao(identificador) == alvo:
            return anteriores
        anteriores.append(identificador)
    return anteriores


def esta_na_faixa(alcancados_em_ordem, inscricao):
    """A Inscrição está na faixa vigente e habilitou (`fora_da_faixa`)."""
    alvo = chave_da_inscricao(inscricao)
    return any(chave_da_inscricao(i) == alvo for i in alcancados_em_ordem)


__all__ = [
    "DESFECHOS_QUE_ENCERRAM",
    "alcancados",
    "esgotou",
    "esta_na_faixa",
    "ordem_de_chamada",
    "precedencia",
    "regularizaveis",
    "proximo",
    "suplentes",
    "titulares",
]
