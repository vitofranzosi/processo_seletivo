"""A vaga que muda de recorte: reversão de cota e liberação por concomitância (016).

**O movimento nasce com a apuração da origem**, na mesma transação que o determina. A apuração do
**destino** o lê pelo `destino_lista_id` e nunca cria um segundo registro — a linha existe uma vez,
e é o que desfaz a circularidade entre "efetivas depende de movimentos" e "movimento aponta uma
apuração".

**Os dois sentidos são opostos, e trocá-los mantém a soma certa com o recorte errado.** A reversão
move quantidade da cota para a linha geral; a liberação devolve **ao recorte reservado** a vaga de
quem ocupou pela ampla. Só asserção de recorte pega a troca, e é por isso que ela tem teste próprio.
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


def _lista_reservada_de(inscricao):
    """A Modalidade que a inscrição escolheu, ou `None`.

    O candidato indica **uma** modalidade de reserva no ato da inscrição — item 4.2.3 do 28/2026 e
    do 57/2026 —, e é ela o destino da vaga liberada.
    """
    modalidade = getattr(inscricao, "modality_id", None)
    return modalidade or None


__all__ = [
    "gravar_reversao",
    "ha_quem_ocupar",
    "quantidade_que_a_cota_cede",
    "reverter_cota",
]
