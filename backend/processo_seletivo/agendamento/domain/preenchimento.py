"""A ordem do preenchimento automático, escrita uma vez (167, FR-7213, FR-7214, T-011).

**Pessoas pelo nome, e pelo protocolo no empate; horários do mais cedo ao mais tarde; as bancas lado
a lado em cada horário.** É uma ordem explicável, que a tela escreve como está, e que não expõe
posição na classificação (Assumptions, Q-6). O nome é comparado sem acento e sem caixa: "Álvaro"
não pode ir para o fim da fila por causa do acento.

É pura: a prévia e a aplicação chamam a mesma função sobre a mesma leitura, e é isso que faz a
assinatura da prévia ser comparável à da aplicação (T-010).
"""

from collections import Counter
from dataclasses import dataclass

from processo_seletivo.shared.texto import dobrar

ORDEM = (
    "Ordem: pessoas pelo nome, e pelo protocolo no empate; horários do mais cedo ao mais tarde; "
    "as bancas lado a lado em cada horário."
)


@dataclass(frozen=True)
class Pessoa:
    inscricao_id: str
    nome: str
    protocolo: str


@dataclass(frozen=True)
class Proposta:
    pares: tuple
    sem_horario: tuple
    livres: tuple
    por_dia_e_banca: dict
    ordem: str = ORDEM

    @property
    def recebem(self):
        return len(self.pares)

    @property
    def frase(self):
        """O veredito da prévia (contracts/recusas.md §3)."""
        if not self.pares:
            return (
                "Ninguém recebe horário: não há pessoa sem horário e horário livre ao mesmo tempo."
            )
        if not self.sem_horario:
            if len(self.pares) == 1:
                return "A pessoa sem horário recebe horário."
            return f"Todas as {len(self.pares)} pessoas recebem horário."
        recebem = (
            "1 pessoa recebe horário."
            if len(self.pares) == 1
            else f"{len(self.pares)} pessoas recebem horário."
        )
        continuam = (
            "1 continua sem horário."
            if len(self.sem_horario) == 1
            else f"{len(self.sem_horario)} continuam sem horário."
        )
        return f"{recebem} {continuam}"


def chave_da_pessoa(pessoa):
    return (dobrar(pessoa.nome), pessoa.protocolo or "", str(pessoa.inscricao_id))


def propor(sem_horario, livres):
    """Emparelha até acabar um dos dois. Quem já tem horário não está em `sem_horario`, e o horário
    dele não está em `livres`: o preenchimento não mexe em ninguém (FR-7213)."""
    pessoas = sorted(sem_horario, key=chave_da_pessoa)
    horarios = sorted(livres)
    quantos = min(len(pessoas), len(horarios))
    pares = tuple(zip(pessoas[:quantos], horarios[:quantos], strict=True))
    distribuicao = Counter((horario.dia, horario.banca_id) for _, horario in pares)
    return Proposta(
        pares=pares,
        sem_horario=tuple(pessoas[quantos:]),
        livres=tuple(horarios[quantos:]),
        por_dia_e_banca=dict(distribuicao),
    )
