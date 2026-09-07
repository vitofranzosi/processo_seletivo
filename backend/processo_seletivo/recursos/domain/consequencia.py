"""A consequência da correção é **derivada**, e nunca digitada.

O julgador fixa a **conclusão** — a pontuação na forma pontuada, o sentido na decisória. Quem diz
o que essa conclusão produz é a regra publicada da Etapa: a nota mínima e o caráter eliminatório na
forma pontuada, o sentido na decisória.

**Deixá-la livre permitiria uma decisão declarar `HABILITADA` com nota abaixo da mínima** — e
contradizer, no mesmo ato, a norma que ela própria cita. Não é hipótese remota: é o erro natural de
quem defere querendo ajudar e não confere a tabela (FR-059).

**A regra vem da versão que a decisão cita**, e não da vigente hoje. É a mesma escolha que a 015 fez
ao ler a norma pela versão que o ato cita: uma Retificação posterior não pode mudar retroativamente
o que uma decisão já produziu.

Nada aqui é regra nova. `resultados/domain/regra.py` é a mesma função que a consolidação usa desde a
013, e reusá-la é o que garante que a correção por recurso e a consolidação ordinária cheguem à
mesma consequência para a mesma nota — duas tabelas-verdade divergiriam no primeiro Edital atípico.
"""

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation

from processo_seletivo.avaliacoes.domain.formas import Forma
from processo_seletivo.avaliacoes.domain.previsao import forma_publicada
from processo_seletivo.resultados.domain.regra import consequencia as consequencia_da_regra
from processo_seletivo.resultados.domain.regra import impedimento_da_regra
from processo_seletivo.shared.api.problems import DomainError

INCOMPLETA = "appeal_correction_incomplete"


@dataclass(frozen=True)
class Conclusao:
    """O que o julgador fixou, na forma que a Etapa publica.

    O mesmo contrato que a consolidação já consome — três campos, e a forma escolhe qual vale.
    """

    forma: str
    pontuacao: Decimal | None
    sentido: str


def etapa_publicada(versao, etapa_id):
    """A Etapa como a **versão citada pela decisão** a descreve, ou `None`."""
    alvo = str(etapa_id)
    for etapa in versao.content.get("stages") or []:
        if str(etapa.get("id")) == alvo:
            return etapa
    return None


def derivar(*, versao, etapa_id, pontuacao=None, sentido=""):
    """`(consequencia, motivo, conclusao)` — ou recusa dizendo o que falta.

    A recusa é `422` e nomeia o campo ausente: uma correção fixada sem Etapa, ou sem a conclusão que
    a forma exige, não é decisão incompleta por descuido de quem implementa — é decisão que a tela
    deixou sair pela metade, e devolvê-la em silêncio faria nascer um sucessor sem grandeza onde a
    Etapa tem uma.
    """
    if etapa_id is None:
        raise DomainError(INCOMPLETA, "A correção precisa dizer a que Etapa se refere.", 422)
    etapa = etapa_publicada(versao, etapa_id)
    if etapa is None:
        raise DomainError(
            INCOMPLETA,
            "A Etapa indicada não existe na versão do Edital que esta decisão cita.",
            422,
        )
    impedimento = impedimento_da_regra(etapa)
    if impedimento is not None:
        # A mesma recusa que a consolidação daria, e pelo mesmo motivo: sem regra suficiente,
        # qualquer consequência que se declarasse afirmaria norma que ninguém escreveu.
        raise DomainError(INCOMPLETA, f"A Etapa não tem regra suficiente: {impedimento[1]}.", 422)

    forma = forma_publicada(etapa)
    conclusao = _conclusao(forma, pontuacao, sentido)
    efeito, motivo = consequencia_da_regra(etapa, conclusao)
    return efeito, motivo, conclusao


def _conclusao(forma, pontuacao, sentido):
    if forma == Forma.DECISORIA:
        if not sentido:
            raise DomainError(
                INCOMPLETA, "Esta Etapa é decisória: a correção precisa fixar o sentido.", 422
            )
        return Conclusao(forma=str(forma), pontuacao=None, sentido=str(sentido))
    if pontuacao is None:
        raise DomainError(
            INCOMPLETA, "Esta Etapa é pontuada: a correção precisa fixar a pontuação.", 422
        )
    try:
        valor = Decimal(str(pontuacao))
    except InvalidOperation as exc:
        # **Recusa, e não erro de servidor.** O que chega aqui é texto digitado por quem julga, e
        # texto que não é número é pedido malformado — não defeito do sistema. Deixar a exceção
        # subir devolvia 500 na tela de um julgamento, sem motivo escrito e apagando a motivação
        # que a pessoa já tinha redigido.
        raise DomainError(
            INCOMPLETA, f"'{pontuacao}' não é uma pontuação: informe um número.", 422
        ) from exc
    return Conclusao(forma=str(forma), pontuacao=valor, sentido="")


__all__ = ["INCOMPLETA", "Conclusao", "derivar", "etapa_publicada"]
