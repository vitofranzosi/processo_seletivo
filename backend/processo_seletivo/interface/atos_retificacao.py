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
    """Um ato e as situações de que ele parte.

    `situacoes_exigidas` é conjunto, e não situação única, porque `devolver` parte de duas — o
    domínio admite desfazer tanto a revisão quanto a homologação (`TRANSITIONS`). Enquanto era
    escalar, `cancelar` precisava de um ramo próprio em `disponiveis` e outro em `impedimento`
    para consultar o seu conjunto à parte; com o conjunto no próprio ato, os dois ramos somem e
    o terceiro caso nunca precisa nascer.
    """

    chave: str
    rotulo: str
    permissao: str
    situacoes_exigidas: frozenset[str]
    consequencias: list[str]
    irreversivel: bool = False
    interrupcao: bool = False
    exige_motivo: bool = False
    exige_signatario: bool = False
    rotulo_motivo: str = "Motivo"


CANCELAVEL = frozenset({"EM_ELABORACAO", "EM_REVISAO", "HOMOLOGADA"})
# Devolver desfaz a revisão ou a homologação, e por isso parte das duas — é o mesmo conjunto que
# `TRANSITIONS["devolver"]` declara no domínio.
DEVOLVIVEL = frozenset({"EM_REVISAO", "HOMOLOGADA"})

ATOS = {
    "submeter": AtoRetificacao(
        chave="submeter",
        rotulo="Submeter para revisão",
        permissao="retificacao:submeter",
        situacoes_exigidas=frozenset({"EM_ELABORACAO"}),
        consequencias=[
            "As alterações declaradas são congeladas para revisão.",
            "A Retificação deixa de poder ser editada até ser devolvida ou homologada.",
        ],
    ),
    "homologar": AtoRetificacao(
        chave="homologar",
        rotulo="Homologar",
        permissao="retificacao:homologar",
        situacoes_exigidas=frozenset({"EM_REVISAO"}),
        exige_motivo=True,
        rotulo_motivo="Fundamento da homologação",
        consequencias=[
            "As alterações passam a ser a versão candidata à Publicação.",
            "Nada muda no conteúdo vigente do Edital até a Publicação.",
        ],
    ),
    "devolver": AtoRetificacao(
        chave="devolver",
        rotulo="Devolver para elaboração",
        permissao="retificacao:homologar",
        situacoes_exigidas=DEVOLVIVEL,
        exige_motivo=True,
        rotulo_motivo="Motivo da devolução",
        consequencias=[
            "A Retificação volta para elaboração e pode ser editada novamente.",
            "Uma homologação anterior deixa de valer; sua autoria permanece na auditoria.",
            "O motivo fica registrado e é o que orienta quem for corrigir.",
        ],
    ),
    "publicar": AtoRetificacao(
        chave="publicar",
        rotulo="Publicar Retificação",
        permissao="retificacao:publicar",
        situacoes_exigidas=frozenset({"HOMOLOGADA"}),
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
        situacoes_exigidas=CANCELAVEL,
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


def disponiveis(retificacao, ator):
    for ato in ATOS.values():
        if ator.can(ato.permissao) and retificacao.status in ato.situacoes_exigidas:
            yield ato


def executar(ato, request, ator, retificacao, signatario=None):
    argumentos = {
        "actor": ator,
        "retificacao_id": retificacao.id,
        "expected_revision": retificacao.revision,
        # Confirmar duas vezes repete o mesmo ato, não pratica dois: a chave nasce na tela de
        # confirmação e volta no formulário, como nos atos do Edital e do Processo.
        "idempotency_key": request.POST.get("chave_idempotencia", ""),
        "correlation_id": request.correlation_id,
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
    return {
        "motivo": "situacao",
        "exigidas": sorted(ato.situacoes_exigidas),
        "atual": retificacao.status,
    }
