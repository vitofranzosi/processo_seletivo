"""Habilitar e desabilitar o assistente pela interface (170).

**A configuração técnica fica no ambiente, e a decisão fica aqui** (`D-001`). O ambiente diz o
serviço, o modelo, o tokenizer e a credencial; este módulo diz se o assistente é oferecido, e grava
quem decidiu, quando e por quê.

**Uma regra só, para os cinco leitores** (FR-7515, FR-7520). A tela do piloto, a entrada nela, o
protótipo, o painel da página pública e as rotas dele perguntam `piloto_atende` ou
`pagina_publica_atende`, e a resposta é lida do banco a cada requisição (FR-7523). Nenhuma decisão
fica guardada na sessão ou na memória do processo.

**Produção é do backend, e não de configuração editável** (`D-005`, R-4). `AMBIENTE_DE_PRODUCAO` é o
literal do `production.py`. Em produção, a página pública não abre, nem com ato gravado num banco
copiado de outro ambiente (FR-7519), e o ato que a habilitaria é recusado, nomeando os requisitos da
abertura (FR-7518).

**A configuração é exigida no ato, e não a cada conversa** (FR-7504). Sem ela, as frentes se
comportam como a `071` e a `074` já se comportam: as sugestões respondem sem o modelo, e a pergunta
livre termina no estado explícito, sem chamada. Exigi-la a cada conversa mudaria esse comportamento,
de que a suíte e a demonstração local dependem.

**Duas etapas, como em Unidades** (`110`). `conferir` só lê, e mostra a consequência; o ato
reconfere tudo sob a trava (FR-7531). A trava é consultiva, e não `FOR UPDATE`, porque o runtime
não tem `UPDATE` na tabela append-only (R-3).
"""

import hashlib
from dataclasses import dataclass

from django.conf import settings
from django.db import connection
from django.utils import timezone

from processo_seletivo.auditoria.application import record_event
from processo_seletivo.duvidas.domain import habilitacao as nomes
from processo_seletivo.duvidas.infrastructure.inferencia import configuracao_do_servico
from processo_seletivo.duvidas.models import HabilitacaoDoAssistente
from processo_seletivo.seguranca.acessos import ESCOPO_INSTITUCIONAL
from processo_seletivo.seguranca.application.authorization import (
    base_de_permissao,
    require_authorization_base,
)
from processo_seletivo.seguranca.domain import Actor
from processo_seletivo.shared.api.problems import DomainError
from processo_seletivo.shared.application.commands import command_context

BASE = base_de_permissao("habilitar o assistente do Edital")


# --- O ambiente ---------------------------------------------------------------------------------


def em_producao():
    return bool(getattr(settings, "AMBIENTE_DE_PRODUCAO", False))


def _atalho_do_piloto():
    # O atalho de demonstração (FR-7506). Produção recusa subir com ele, e a conferência repete a
    # recusa aqui, para que nenhum caminho de configuração o deixe valer lá.
    return bool(settings.ASSISTENTE_PILOTO) and not em_producao()


def _atalho_da_pagina():
    return bool(settings.ASSISTENTE_NA_PAGINA_DO_EDITAL) and not em_producao()


# --- O estado de uma frente -------------------------------------------------------------------


def _atos(frente, edital_id=None):
    atos = HabilitacaoDoAssistente.objects.filter(frente=frente)
    if frente == nomes.PAGINA_PUBLICA:
        atos = atos.filter(edital_id=edital_id)
    return atos


def ultimo_ato(frente, edital_id=None):
    """O ato vigente da frente, ou `None` — que é desabilitada (negar por padrão)."""
    return _atos(frente, edital_id).order_by("-ordem").first()


def _habilitado(frente, edital_id=None):
    ato = ultimo_ato(frente, edital_id)
    return ato if ato is not None and ato.habilitada else None


def piloto_atende():
    """Se o piloto é oferecido agora (FR-7515). O alcance e a permissão são de quem pergunta."""
    return _atalho_do_piloto() or _habilitado(nomes.PILOTO) is not None


def pagina_publica_atende(edital_id):
    """Se a página pública deste Edital oferece o painel agora (FR-7519, FR-7520).

    Quem pergunta confere, ele mesmo, se o Edital tem seleção pública: é a página que a mostra.
    """
    if em_producao():
        return False
    return _atalho_da_pagina() or _habilitado(nomes.PAGINA_PUBLICA, edital_id) is not None


def marca(frente, edital_id=None):
    """A marca da conversa (R-5): o ato vigente, e ato novo é conversa nova. Sem ato — com o atalho
    de demonstração —, nenhuma marca, e a conversa fica na chave de sempre, só do Edital."""
    ato = _habilitado(frente, edital_id)
    return str(ato.id) if ato is not None else ""


# --- A permissão --------------------------------------------------------------------------------


def exigir_permissao(ator):
    """FR-7511: a permissão com o escopo institucional, conferidos aqui; a tela é a segunda."""
    require_authorization_base(
        ator is not None
        and ator.can(nomes.HABILITAR)
        and ator.institution_scope == ESCOPO_INSTITUCIONAL,
        bases=[BASE],
    )


def _motivo(motivo):
    motivo = (motivo or "").strip()
    if not motivo:
        raise DomainError(
            nomes.MOTIVO_OBRIGATORIO,
            "Informe o motivo — por exemplo, o teste ou o pedido que determinou a mudança.",
            422,
            campo="motivo",
        )
    return motivo


# --- As leituras da página ------------------------------------------------------------------


@dataclass(frozen=True)
class EditalDaPagina:
    edital: object
    ato: object
    tem_pagina_publica: bool

    @property
    def habilitado(self):
        return self.ato is not None and self.ato.habilitada


def _editais_com_pagina(instante):
    from processo_seletivo.publicacoes.application.selectors import selecoes_publicas

    return {versao.edital_id for versao in selecoes_publicas(at=instante)}


def _tem_pagina_publica(edital_id, instante):
    from processo_seletivo.publicacoes.application.selectors import selecao_publica

    try:
        selecao_publica(edital_id=edital_id, at=instante)
    except DomainError:
        return False
    return True


def ler(ator):
    """Tudo o que a página mostra (contracts/tela.md). Não chama o modelo (FR-7502)."""
    from processo_seletivo.processos.models import Edital

    exigir_permissao(ator)
    agora = timezone.now()
    com_pagina = _editais_com_pagina(agora)
    habilitados = set(
        HabilitacaoDoAssistente.objects.filter(frente=nomes.PAGINA_PUBLICA).values_list(
            "edital_id", flat=True
        )
    )
    editais = Edital.objects.filter(id__in=com_pagina | habilitados).order_by(
        "institution_scope", "-year", "number", "id"
    )
    ultimos = {}
    for ato in HabilitacaoDoAssistente.objects.filter(
        frente=nomes.PAGINA_PUBLICA, edital_id__in=[e.id for e in editais]
    ).order_by("edital_id", "ordem"):
        ultimos[ato.edital_id] = ato
    return {
        "configuracao": configuracao_do_servico(),
        "em_producao": em_producao(),
        "atalho_do_piloto": _atalho_do_piloto(),
        "atalho_da_pagina": _atalho_da_pagina(),
        "piloto": ultimo_ato(nomes.PILOTO),
        "editais": [
            EditalDaPagina(edital, ultimos.get(edital.id), edital.id in com_pagina)
            for edital in editais
        ],
        "requisitos": nomes.REQUISITOS_DA_ABERTURA,
        "historico": list(
            HabilitacaoDoAssistente.objects.select_related("edital").order_by(
                "-criado_em", "-ordem"
            )
        ),
    }


def estado_do_edital(edital_id):
    """A linha da página do Edital na gestão (FR-7522): quem alcança o Edital a lê sem permissão
    própria, porque ela diz o que a página pública, aberta a todos, já mostra."""
    if em_producao():
        return None
    return _habilitado(nomes.PAGINA_PUBLICA, edital_id)


# --- Os atos --------------------------------------------------------------------------------------


def _edital(edital_id):
    from processo_seletivo.processos.models import Edital

    edital = Edital.objects.filter(id=edital_id).first()
    if edital is None:
        raise DomainError("not_found", "Recurso não encontrado.", 404)
    return edital


def _faltas_da_configuracao():
    configuracao = configuracao_do_servico()
    if configuracao["completa"]:
        return
    faltas = "; ".join(nomes.FALTAS[falta] for falta in configuracao["faltas"])
    raise DomainError(
        nomes.CONFIGURACAO_INCOMPLETA,
        f"O assistente não pode ser habilitado: {faltas}.",
        409,
    )


def _recusa_de_producao():
    requisitos = "; ".join(
        f"{codigo} — {rotulo}" for codigo, rotulo, _ in nomes.REQUISITOS_DA_ABERTURA
    )
    return DomainError(
        nomes.ABERTURA_PUBLICA_EM_PRODUCAO,
        "Em produção, a página pública não abre enquanto os requisitos da abertura estiverem "
        f"pendentes: {requisitos}.",
        409,
    )


def _conferir(frente, edital_id, habilitar):
    """O que recusa o ato, sem gravar. Volta o Edital da página pública, ou `None`."""
    if frente not in nomes.FRENTES:
        raise DomainError("not_found", "Recurso não encontrado.", 404)
    edital = _edital(edital_id) if frente == nomes.PAGINA_PUBLICA else None
    if habilitar:
        if frente == nomes.PAGINA_PUBLICA and em_producao():
            raise _recusa_de_producao()
        _faltas_da_configuracao()
        if edital is not None and not _tem_pagina_publica(edital.id, timezone.now()):
            raise DomainError(
                nomes.SEM_PAGINA_PUBLICA,
                "Este Edital não tem seleção pública agora: não há página onde abrir o assistente.",
                409,
            )
    vigente = _habilitado(frente, edital_id) is not None
    if vigente == habilitar:
        raise _nada_muda(habilitar)
    return edital


def _nada_muda(habilitar):
    if habilitar:
        return DomainError(nomes.JA_HABILITADO, "O assistente já está habilitado aqui.", 409)
    return DomainError(nomes.JA_DESABILITADO, "O assistente já está desabilitado aqui.", 409)


def conferir(ator, *, frente, edital_id=None, habilitar):
    """A primeira etapa: recusa o que o ato recusaria, e devolve o Edital, sem gravar."""
    exigir_permissao(ator)
    return _conferir(frente, edital_id, habilitar)


def _travar(frente, edital_id):
    # Uma trava por frente — o piloto, ou a página de um Edital —, derivada do nome, e não do
    # banco: dois atos sobre a mesma frente se enfileiram, e sobre frentes diferentes não se
    # esperam (R-3). Fora do PostgreSQL é no-op, como a da administração institucional.
    if connection.vendor != "postgresql":
        return
    chave = hashlib.blake2b(f"assistente:{frente}:{edital_id or ''}".encode(), digest_size=8)
    numero = int.from_bytes(chave.digest(), "big", signed=True)
    with connection.cursor() as cursor:
        cursor.execute("SELECT pg_advisory_xact_lock(%s)", [numero])


def _situacao(habilitada):
    # No gênero de "o assistente", e não no feminino: o feminino em maiúsculas é a grafia da
    # consequência do Resultado, e o guardião dos leitores dela (164) a procura em todo o código.
    return "HABILITADO" if habilitada else "DESABILITADO"


def _praticar(ator, *, frente, edital_id, habilitar, motivo, correlation_id):
    exigir_permissao(ator)
    motivo = _motivo(motivo)
    with command_context() as agora:
        _travar(frente, edital_id)
        # Sob a trava, tudo de novo: entre a confirmação mostrada e o envio, outra pessoa pode ter
        # praticado o ato, e o segundo recebe "nada muda" em vez de gravar outro igual (FR-7531).
        edital = _conferir(frente, edital_id, habilitar)
        anterior = ultimo_ato(frente, edital_id)
        ato = HabilitacaoDoAssistente.objects.create(
            frente=frente,
            edital=edital,
            ordem=(anterior.ordem + 1) if anterior else 1,
            habilitada=habilitar,
            motivo=motivo,
            autor=ator.subject,
            criado_em=agora,
        )
        # O ato sobre um Edital vai para a trilha da unidade dele, pelo mesmo artifício da 110: o
        # mesmo `subject` e as mesmas permissões, no escopo da unidade (R-8, FR-7529).
        escopo = edital.institution_scope if edital is not None else ESCOPO_INSTITUCIONAL
        record_event(
            actor=Actor(ator.subject, escopo, ator.permissions),
            permission=nomes.HABILITAR,
            operation=nomes.OPERACAO_HABILITAR if habilitar else nomes.OPERACAO_DESABILITAR,
            aggregate=ato,
            now=agora,
            correlation_id=correlation_id,
            reason=motivo,
            previous_state=_situacao(anterior.habilitada) if anterior else "",
            new_state=_situacao(habilitar),
            new_revision=None,
            detalhe={
                "frente": frente,
                "edital": str(edital.id) if edital is not None else None,
                "rotulo": f"Edital {edital.number}/{edital.year}" if edital is not None else "",
            },
        )
    return ato


def habilitar(ator, *, frente, edital_id=None, motivo, correlation_id=""):
    return _praticar(
        ator,
        frente=frente,
        edital_id=edital_id,
        habilitar=True,
        motivo=motivo,
        correlation_id=correlation_id,
    )


def desabilitar(ator, *, frente, edital_id=None, motivo, correlation_id=""):
    return _praticar(
        ator,
        frente=frente,
        edital_id=edital_id,
        habilitar=False,
        motivo=motivo,
        correlation_id=correlation_id,
    )
