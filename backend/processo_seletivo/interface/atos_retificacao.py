"""Atos do fluxo da Retificação, no mesmo formato dos atos do Edital.

Separado porque os commands recebem `retificacao_id`, e porque as consequências são outras:
o que uma Retificação provoca depende de vigência, não só de estado.
"""

from dataclasses import dataclass

from processo_seletivo.publicacoes.application.retificacoes import (
    publish_retification,
    transition_retification,
)


@dataclass(frozen=True)
class AtoRetificacao:
    chave: str
    rotulo: str
    permissao: str
    situacao_exigida: str
    consequencias: list[str]
    irreversivel: bool = False
    interrupcao: bool = False
    exige_motivo: bool = False
    exige_signatario: bool = False
    rotulo_motivo: str = "Motivo"


ATOS = {
    "submeter": AtoRetificacao(
        chave="submeter",
        rotulo="Submeter para revisão",
        permissao="retificacao:submeter",
        situacao_exigida="EM_ELABORACAO",
        consequencias=[
            "As alterações declaradas são congeladas para revisão.",
            "A Retificação deixa de poder ser editada até ser devolvida ou homologada.",
        ],
    ),
    "homologar": AtoRetificacao(
        chave="homologar",
        rotulo="Homologar",
        permissao="retificacao:homologar",
        situacao_exigida="EM_REVISAO",
        exige_motivo=True,
        rotulo_motivo="Fundamento da homologação",
        consequencias=[
            "As alterações passam a ser a versão candidata à Publicação.",
            "Nada muda no conteúdo vigente do Edital até a Publicação.",
        ],
    ),
    "publicar": AtoRetificacao(
        chave="publicar",
        rotulo="Publicar Retificação",
        permissao="retificacao:publicar",
        situacao_exigida="HOMOLOGADA",
        irreversivel=True,
        exige_signatario=True,
        consequencias=[
            "A Retificação torna-se pública e imutável.",
            "O conteúdo vigente do Edital passa a incluir estas alterações a partir da vigência "
            "declarada — imediatamente, se nenhuma data futura foi informada.",
            "A Publicação original e as versões anteriores continuam preservadas e consultáveis.",
            "Correções posteriores exigem nova Retificação.",
        ],
    ),
    "cancelar": AtoRetificacao(
        chave="cancelar",
        rotulo="Cancelar Retificação",
        permissao="retificacao:cancelar",
        situacao_exigida=None,
        irreversivel=True,
        interrupcao=True,
        exige_motivo=True,
        rotulo_motivo="Motivo do cancelamento",
        consequencias=[
            "A Retificação é encerrada sem produzir efeito no conteúdo vigente.",
            "O registro é preservado no histórico, marcado como cancelado.",
        ],
    ),
}
CANCELAVEL = {"EM_ELABORACAO", "EM_REVISAO", "HOMOLOGADA"}


def disponiveis(retificacao, ator):
    for ato in ATOS.values():
        if not ator.can(ato.permissao):
            continue
        if ato.chave == "cancelar":
            if retificacao.status in CANCELAVEL:
                yield ato
        elif retificacao.status == ato.situacao_exigida:
            yield ato


def executar(ato, request, ator, retificacao, signatario=None):
    argumentos = {
        "actor": ator,
        "retificacao_id": retificacao.id,
        "expected_revision": retificacao.revision,
    }
    if ato.chave == "publicar":
        return publish_retification(**argumentos, signatory=signatario)
    return transition_retification(
        **argumentos, action=ato.chave, reason=(request.POST.get("motivo") or "").strip()
    )


def impedimento(retificacao, ator, ato):
    """O que impede este ato agora — para dizer antes da confirmação, não depois dela.

    `disponiveis` já responde isto para montar a lista de ações; a tela de confirmação,
    alcançável por URL direta, oferecia "Confirmar" sem consultá-lo. Quem recusa continua
    sendo o command: aqui só se explica o que ele responderia.
    """
    if not ator.can(ato.permissao):
        return {"motivo": "permissao", "permissao": ato.permissao}
    if any(cabivel.chave == ato.chave for cabivel in disponiveis(retificacao, ator)):
        return None
    exigidas = sorted(CANCELAVEL) if ato.chave == "cancelar" else [ato.situacao_exigida]
    return {"motivo": "situacao", "exigidas": exigidas, "atual": retificacao.status}
