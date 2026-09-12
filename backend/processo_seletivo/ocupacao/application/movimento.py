"""A quantidade que sai de um recorte e entra em outro: a reversão de cota (016, `FR-246`).

**Há um sentido só, e a ausência do segundo é o achado da US4.** A concorrência concomitante do item
8.9 do 28/2026 parecia ser o sentido oposto — e não é: ela não transfere quantidade nenhuma. O
autodeclarado que ocupa pela ampla apenas **não é computado** no preenchimento da reservada, que
continua com as vagas que publicou. Aquilo é exclusão no cálculo de `ocupadas`, e mora em
`apuracao.apurar`.

**O movimento nasce com a apuração da origem**, na mesma transação que o determina, e com o id
gerado **antes** dela — para que ela o inclua nos próprios `movimentosLidos` e já nasça com a
`efetivas` líquida da cessão. A apuração do **destino** o lê pelo `destino_lista_id` e nunca cria um
segundo registro.
"""

from processo_seletivo.classificacao.application.selectors import ato_vigente
from processo_seletivo.ocupacao.domain import nomes, reversao
from processo_seletivo.ocupacao.models import MovimentoDeVaga
from processo_seletivo.shared.api.problems import DomainError


def quantidade_que_a_cota_cede(*, especie, efetivas, ocupadas, ha_quem_ocupar):
    """Quanto a cota cede, **antes** de a apuração existir.

    A ordem importa: o id do movimento é gerado antes da apuração, para que ela o inclua nos
    próprios `movimentosLidos` e nasça com a `efetivas` líquida. Por isso o cálculo tem de ser
    possível sem a apuração em mão.
    """
    return reversao.quantidade_a_reverter(
        especie=especie, efetivas=efetivas, ocupadas=ocupadas, ha_quem_ocupar=ha_quem_ocupar
    )


def gravar_reversao(
    *,
    identidade,
    apuracao,
    quantidade,
    origem_lista_id,
    publicadas,
    especie,
    registrado_por,
    registrado_em,
):
    """Grava o movimento com o id que a apuração já citou."""
    causa = (
        "Lista reservada esgotada com saldo"
        if especie == nomes.REVERSAO_POR_ESGOTAMENTO
        else "Vagas reservadas não preenchidas"
    )
    return MovimentoDeVaga.objects.create(
        id=identidade,
        apuracao=apuracao,
        especie=nomes.MOVIMENTO_REVERSAO,
        origem_lista_id=origem_lista_id,
        # **O destino é a linha geral — `None`** —, e não a Modalidade declarada como ampla
        # concorrência: a quantidade da ampla mora na linha geral, e apontar a Modalidade faria o
        # movimento chegar a um recorte que não tem linha.
        destino_lista_id=None,
        quantidade=quantidade,
        causa=f"{causa}: {quantidade} de {publicadas}.",
        registrado_por=registrado_por,
        registrado_em=registrado_em,
    )


def reverter_cota(*, apuracao, especie, ha_quem_ocupar, registrado_por, registrado_em):
    """Cria o movimento de reversão da cota para a linha geral, se houver o que reverter.

    Devolve o `MovimentoDeVaga` criado, ou `None` quando não há reversão — e `None` não é falha: é
    o desfecho normal de um Edital que não declara reversão, ou de uma cota sem saldo, ou de uma
    lista que ainda tem quem ocupar sob o gatilho de esgotamento.

    **A origem é sempre uma cota, nunca a linha geral.** Reverter da ampla para a ampla não existe,
    e a constraint de recortes distintos o recusaria — mas recusar aqui diz por quê.
    """
    if apuracao.lista_id is None:
        raise DomainError(
            "reversao_da_linha_geral",
            "A linha geral é o destino da reversão, e não a origem: a ampla concorrência não "
            "reverte para si mesma.",
            409,
        )
    import uuid

    quantidade = quantidade_que_a_cota_cede(
        especie=especie,
        efetivas=apuracao.efetivas,
        ocupadas=apuracao.ocupadas,
        ha_quem_ocupar=ha_quem_ocupar,
    )
    if not quantidade:
        return None
    return gravar_reversao(
        identidade=uuid.uuid4(),
        apuracao=apuracao,
        quantidade=quantidade,
        origem_lista_id=apuracao.lista_id,
        publicadas=apuracao.publicadas,
        especie=especie,
        registrado_por=registrado_por,
        registrado_em=registrado_em,
    )


def ha_quem_ocupar(*, edital, marco_id, lista_id, ja_ocupadas):
    """Se a ordem daquela lista ainda tem alguém por ocupar além dos já ocupados.

    **É a condição que separa as duas espécies de gatilho**, e não a contagem de ocupadas: sob
    esgotamento, havendo quem ocupar não se reverte nada — a vaga continua sendo da cota, esperando
    análise.
    """
    ato = ato_vigente(edital=edital, marco_id=marco_id, lista_id=lista_id)
    if ato is None:
        return False
    com_posicao = sum(1 for posicao in ato.posicoes.all() if posicao.posicao is not None)
    return com_posicao > ja_ocupadas


__all__ = [
    "gravar_reversao",
    "ha_quem_ocupar",
    "quantidade_que_a_cota_cede",
    "reverter_cota",
]
