"""O conflito de horário de quem avalia: duas entrevistas da mesma pessoa ao mesmo tempo (179).

**Puro, e por isso o mesmo para todos os que perguntam.** A Distribuição recusa a linha que cria
conflito, o rodízio trata o par como inelegível, a remarcação o anuncia antes de confirmar, e a
agenda publicada o mostra depois (FR-8205, FR-8207, FR-8208, FR-8209). Se cada um fizesse a conta,
cada um a faria um pouco diferente — e um "horários que só se tocam" contado como conflito num
lugar e não no outro faria a Distribuição recusar o que a agenda diz estar em ordem.

**A conta é a do intervalo semiaberto** (FR-8202): duas entrevistas conflitam quando cada uma começa
antes de a outra terminar. A que termina às 08:15 e a que começa às 08:15 não conflitam: é a mesma
pessoa saindo de uma sala e entrando na seguinte. O intervalo entre atendimentos é folga da agenda,
e não tempo de quem avalia — por isso não entra.

**Nada aqui é gravado** (FR-8203). O conflito é lido, a cada vez, da Atribuição e do horário; um
fato próprio seria a segunda fonte que diverge na primeira remarcação.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class Compromisso:
    """Uma entrevista de uma pessoa: o intervalo, a inscrição e onde ela acontece."""

    inicio: datetime
    fim: datetime
    inscricao_id: object
    etapa_id: object = None
    banca_nome: str = ""


@dataclass(frozen=True)
class Conflito:
    """Duas entrevistas da mesma pessoa que se sobrepõem, a de início mais cedo primeiro."""

    pessoa: str
    primeiro: Compromisso
    segundo: Compromisso
    passado: bool = False

    @property
    def inscricoes(self):
        return {self.primeiro.inscricao_id, self.segundo.inscricao_id}


def sobrepoem(a_inicio, a_fim, b_inicio, b_fim) -> bool:
    """Se dois intervalos semiabertos se sobrepõem. Os que só se tocam, não."""
    return a_inicio < b_fim and b_inicio < a_fim


def _ordem(compromisso: Compromisso):
    # `str` no desempate: a ordem não pode depender de como o banco devolveu as linhas, e os
    # identificadores são UUID ou texto conforme quem chama.
    return (compromisso.inicio, compromisso.fim, str(compromisso.inscricao_id))


def cabe(compromissos, inicio, fim, *, exceto=None) -> Compromisso | None:
    """O primeiro compromisso que impede `[inicio, fim)`, ou `None` quando o intervalo cabe.

    `exceto` é a inscrição que está sendo movida: na remarcação, o horário antigo da própria pessoa
    não é conflito com o novo.
    """
    for compromisso in sorted(compromissos, key=_ordem):
        if exceto is not None and compromisso.inscricao_id == exceto:
            continue
        if sobrepoem(compromisso.inicio, compromisso.fim, inicio, fim):
            return compromisso
    return None


def conflitos(compromissos_por_pessoa, *, agora=None) -> list[Conflito]:
    """Todos os pares que se sobrepõem, por pessoa, em ordem estável.

    A varredura ordena por início e compara cada compromisso só com os que começam antes de ele
    terminar: com dezenas por pessoa, é quase linear, e o resultado é o mesmo da comparação de todos
    com todos — que é o que os testes conferem.
    """
    achados = []
    for pessoa in sorted(compromissos_por_pessoa, key=str):
        lista = sorted(compromissos_por_pessoa[pessoa], key=_ordem)
        for i, atual in enumerate(lista):
            for seguinte in lista[i + 1 :]:
                if seguinte.inicio >= atual.fim:
                    break
                if seguinte.inscricao_id == atual.inscricao_id:
                    continue
                achados.append(
                    Conflito(
                        pessoa=pessoa,
                        primeiro=atual,
                        segundo=seguinte,
                        passado=agora is not None and max(atual.fim, seguinte.fim) <= agora,
                    )
                )
    return achados
