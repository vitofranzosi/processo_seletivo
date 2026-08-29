"""Atos do ciclo de vida do Processo Seletivo.

Ativação e desfecho são atos administrativos explícitos: não decorrem da situação dos Editais
(FR-005). O cancelamento é o único que depende deles, e por isso é o único cujo impedimento a
tela precisa mostrar antes da tentativa.
"""

from dataclasses import dataclass

from processo_seletivo.processos.application.commands import activate_process
from processo_seletivo.processos.application.finalizacao import cancel_process, close_process


@dataclass(frozen=True)
class AtoProcesso:
    chave: str
    rotulo: str
    permissao: str
    situacoes: frozenset[str]
    command: object
    consequencias: list[str]
    irreversivel: bool = False
    rotulo_motivo: str = "Motivo"
    depende_dos_editais: bool = False


ATOS = {
    "ativar": AtoProcesso(
        chave="ativar",
        rotulo="Ativar Processo",
        permissao="processo:ativar",
        situacoes=frozenset({"EM_ELABORACAO"}),
        command=activate_process,
        rotulo_motivo="Fundamento da ativação",
        consequencias=[
            "O Processo passa a Ativo, registrando a abertura formal do certame.",
            "A situação dos Editais não muda: cada um segue seu próprio fluxo.",
        ],
    ),
    "encerrar": AtoProcesso(
        chave="encerrar",
        rotulo="Encerrar Processo",
        permissao="processo:encerrar",
        situacoes=frozenset({"ATIVO"}),
        command=close_process,
        irreversivel=True,
        rotulo_motivo="Motivo do encerramento",
        consequencias=[
            "O Processo passa a Encerrado, registrando a conclusão regular do certame.",
            "Seus Editais deixam de aceitar qualquer alteração, inclusive Retificação.",
            "Publicações, documentos e histórico permanecem disponíveis na consulta pública.",
        ],
    ),
    "cancelar": AtoProcesso(
        chave="cancelar",
        rotulo="Cancelar Processo",
        permissao="processo:cancelar",
        situacoes=frozenset({"EM_ELABORACAO", "ATIVO"}),
        command=cancel_process,
        irreversivel=True,
        rotulo_motivo="Motivo do cancelamento",
        depende_dos_editais=True,
        consequencias=[
            "O Processo passa a Cancelado, registrando interrupção administrativa — que não é "
            "o mesmo que encerramento regular.",
            "Nenhum Edital é cancelado por consequência: cada um exige ato próprio.",
            "Nada é excluído: Publicações, documentos e histórico permanecem preservados.",
        ],
    ),
}


def disponiveis(processo, ator):
    for ato in ATOS.values():
        if ator.can(ato.permissao) and processo.status in ato.situacoes:
            yield ato
