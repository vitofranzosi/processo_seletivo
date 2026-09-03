"""Atos do fluxo do Edital: o que cada um faz, exige e provoca.

Uma tabela em vez de uma cadeia de condicionais, porque a tela precisa das mesmas três
respostas para todos: quem pode praticar, o que o ato exige de quem confirma, e — o que FR-010
e FR-011 pedem — o que ele provoca, dito antes da confirmação.

Nada aqui autoriza nem valida: quem recusa é o command. Isto é a explicação, não a regra.
"""

from dataclasses import dataclass, field

from processo_seletivo.processos.application.finalizacao import cancel_edital, close_edital
from processo_seletivo.publicacoes.application.publish_edital import (
    homologate_edital,
    publish_edital,
    return_edital_to_drafting,
    revoke_homologation,
    submit_edital,
)


@dataclass(frozen=True)
class Ato:
    chave: str
    rotulo: str
    permissao: str
    situacao_exigida: str
    command: object
    consequencias: list[str]
    irreversivel: bool = False
    interrupcao: bool = False
    exige_motivo: bool = False
    exige_signatario: bool = False
    rotulo_motivo: str = "Motivo"
    campos: list[str] = field(default_factory=list)


ATOS = {
    "submeter": Ato(
        chave="submeter",
        rotulo="Submeter para revisão",
        permissao="edital:submeter",
        situacao_exigida="EM_ELABORACAO",
        command=submit_edital,
        consequencias=[
            "O conteúdo atual é congelado como a revisão que será homologada.",
            "O Edital sai de elaboração e não pode mais ser editado por este formulário.",
            "A revisão fica registrada em seu nome na auditoria.",
        ],
    ),
    "homologar": Ato(
        chave="homologar",
        rotulo="Homologar",
        permissao="edital:homologar",
        situacao_exigida="EM_REVISAO",
        command=homologate_edital,
        exige_motivo=True,
        rotulo_motivo="Fundamento da homologação",
        consequencias=[
            "A revisão submetida passa a ser a versão candidata à Publicação.",
            "A homologação fica registrada em seu nome e pode ser revogada antes de publicar.",
        ],
    ),
    "devolver": Ato(
        chave="devolver",
        rotulo="Devolver para elaboração",
        permissao="edital:homologar",
        situacao_exigida="EM_REVISAO",
        command=return_edital_to_drafting,
        exige_motivo=True,
        rotulo_motivo="Motivo da devolução",
        consequencias=[
            "O Edital volta para elaboração e pode ser editado novamente pelo formulário.",
            "A revisão submetida é preservada no histórico; a próxima submissão cria outra.",
            "O motivo fica registrado e é o que orienta quem for corrigir.",
        ],
    ),
    "revogar-homologacao": Ato(
        chave="revogar-homologacao",
        rotulo="Revogar homologação",
        permissao="edital:homologar",
        situacao_exigida="HOMOLOGADO",
        command=revoke_homologation,
        exige_motivo=True,
        rotulo_motivo="Motivo da revogação",
        consequencias=[
            "O Edital volta para revisão e deixa de poder ser publicado.",
            "A homologação anterior é preservada no histórico, marcada como revogada.",
        ],
    ),
    "publicar": Ato(
        chave="publicar",
        rotulo="Publicar",
        permissao="edital:publicar",
        situacao_exigida="HOMOLOGADO",
        command=publish_edital,
        irreversivel=True,
        exige_signatario=True,
        consequencias=[
            "O Edital torna-se público e imutável — nada mais pode ser editado.",
            "Correções posteriores só são possíveis por Retificação, com novo fluxo de aprovação.",
            "O documento publicado é gerado e preservado com o hash do conteúdo homologado.",
            "A Publicação passa a constar da consulta pública, acessível a qualquer pessoa.",
        ],
    ),
    "encerrar": Ato(
        chave="encerrar",
        rotulo="Encerrar",
        permissao="edital:encerrar",
        situacao_exigida="PUBLICADO",
        command=close_edital,
        irreversivel=True,
        exige_motivo=True,
        rotulo_motivo="Motivo do encerramento",
        consequencias=[
            "O Edital passa a Encerrado, registrando a conclusão regular de suas etapas.",
            "Nenhuma Retificação poderá ser publicada depois disso.",
            "Publicações, documentos e histórico permanecem disponíveis na consulta pública.",
        ],
    ),
    "cancelar": Ato(
        chave="cancelar",
        rotulo="Cancelar",
        permissao="edital:cancelar",
        situacao_exigida=None,
        command=cancel_edital,
        irreversivel=True,
        interrupcao=True,
        exige_motivo=True,
        rotulo_motivo="Motivo do cancelamento",
        consequencias=[
            "O Edital passa a Cancelado, registrando interrupção administrativa — que não é "
            "o mesmo que encerramento regular.",
            "Nada é excluído: Publicações, documentos e histórico permanecem preservados.",
            "Nenhuma transição posterior será admitida.",
        ],
    ),
}

# Situações a partir das quais cancelar é admitido; o domínio confirma.
CANCELAVEL = {"EM_ELABORACAO", "EM_REVISAO", "HOMOLOGADO", "PUBLICADO"}


def disponiveis(edital, ator):
    """Atos que fazem sentido nesta situação e que este ator pode praticar."""
    for ato in ATOS.values():
        if not ator.can(ato.permissao):
            continue
        if ato.chave == "cancelar":
            if edital.status in CANCELAVEL:
                yield ato
        elif edital.status == ato.situacao_exigida:
            yield ato


def impedimento(edital, ator, ato):
    """O que impede este ato agora — para dizer antes da confirmação, não depois dela.

    `disponiveis` já responde isto para montar a lista de ações; a tela de confirmação,
    alcançável por URL direta, oferecia "Confirmar" sem consultá-lo. Quem recusa continua
    sendo o command: aqui só se explica o que ele responderia.
    """
    if not ator.can(ato.permissao):
        return {"motivo": "permissao", "permissao": ato.permissao}
    if any(cabivel.chave == ato.chave for cabivel in disponiveis(edital, ator)):
        return None
    exigidas = sorted(CANCELAVEL) if ato.chave == "cancelar" else [ato.situacao_exigida]
    return {"motivo": "situacao", "exigidas": exigidas, "atual": edital.status}
