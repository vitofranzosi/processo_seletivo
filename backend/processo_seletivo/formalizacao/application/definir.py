"""A definição dos documentos que vão ao setor que formaliza, e o histórico dela (117, US1).

**Quem define é a condução** (D-010): a presidência ou `comissao:gerir`, que sabem para que pediram
cada documento. O setor não escolhe o que recebe, e a gestão de acessos não decide conteúdo.

**Sobre todos os requisitos do Edital, de qualquer momento** (D-009): o certificado pedido só na
inscrição entra como o histórico pedido na convocação. A lista vem de **todas** as versões
publicadas, e não só da vigente: o requisito que uma Retificação retirou continua valendo para as
chamadas gravadas sob a versão anterior.

**Fora do conteúdo publicado** (FR-3657): gravar a definição não toca snapshot, hash, PDF nem
Documento Exigido, e não pede Retificação. A obrigação do candidato não muda; muda o que vai ao
setor, e cada exportação grava a versão que aplicou (FR-3655).

**Os avisos saem de dados que já existem** (FR-3658): o recorte por modalidade e o momento. Não há
taxonomia, catálogo nem classificador — a decisão do usuário os veda.
"""

from dataclasses import dataclass, field

from processo_seletivo.auditoria.application import record_event
from processo_seletivo.comissoes.domain.autorizacao import (
    BASES_DA_GESTAO_DA_COMISSAO,
    pode_gerir_comissao,
)
from processo_seletivo.editais.domain.documentos import (
    MODALIDADE_EM_TODOS_OS_PERFIS,
    NA_CONVOCACAO,
    PERFIL_E_MODALIDADE,
    TODOS_COM_MODALIDADE_DE_UM_PERFIL,
    momento_de,
    recorte_de,
)
from processo_seletivo.formalizacao.domain import nomes
from processo_seletivo.formalizacao.models import DefinicaoDosDocumentosDaFormalizacao
from processo_seletivo.processos.models import Edital
from processo_seletivo.seguranca.application.authorization import require_authorization_base
from processo_seletivo.shared.api.problems import DomainError
from processo_seletivo.shared.application.commands import command_context

#: As formas de recorte que dizem "só de uma modalidade de reserva" (FR-3658).
FORMAS_POR_MODALIDADE = frozenset(
    {PERFIL_E_MODALIDADE, MODALIDADE_EM_TODOS_OS_PERFIS, TODOS_COM_MODALIDADE_DE_UM_PERFIL}
)

AVISO_DE_MODALIDADE = (
    "Este documento é exigido só de candidatos de uma modalidade de reserva. Inclua-o só se o "
    "setor precisar dele para formalizar."
)
AVISO_DA_INSCRICAO = (
    "Este documento foi pedido na inscrição. Se ele serve só à classificação, não o inclua."
)


@dataclass(frozen=True)
class Requisito:
    """Um Documento Exigido do Edital, como a tela da definição o mostra."""

    id: str
    nome: str
    chave: str
    momento: str
    ordem: int
    por_modalidade: bool

    @property
    def da_inscricao(self):
        return self.momento == nomes.DA_INSCRICAO

    @property
    def avisos(self):
        avisos = []
        if self.por_modalidade:
            avisos.append(AVISO_DE_MODALIDADE)
        if self.da_inscricao:
            avisos.append(AVISO_DA_INSCRICAO)
        return avisos


@dataclass
class Versao:
    """Uma versão da definição, com o que entrou e saiu em relação à anterior (FR-3711)."""

    definicao: DefinicaoDosDocumentosDaFormalizacao
    numero: int
    acrescentados: list = field(default_factory=list)
    retirados: list = field(default_factory=list)


#: Onde a leitura das versões publicadas fica guardada, na própria instância do Edital.
_CONTEUDOS = "_formalizacao_conteudos_publicados"


def _conteudos(edital):
    """O conteúdo de todas as versões publicadas, lido **uma vez por instância do Edital**.

    É o maior campo do sistema, e a página, a verificação e o manifesto precisam dele para os
    requisitos e os Perfis: sem guardar, a mesma requisição o lia de quatro a seis vezes. A
    instância vive o tempo de uma requisição; as versões são append-only, e a que chegasse no meio
    dela entra na seguinte.
    """
    from processo_seletivo.publicacoes.models_retificacao import VersaoConsolidada

    guardado = getattr(edital, _CONTEUDOS, None)
    if guardado is None:
        guardado = list(
            VersaoConsolidada.objects.filter(edital=edital)
            .order_by("valid_from", "materialized_at")
            .values_list("content", flat=True)
        )
        setattr(edital, _CONTEUDOS, guardado)
    return guardado


def guardar_conteudos(editais):
    """As versões de vários Editais numa consulta só, guardadas em cada um: a lista do setor."""
    from processo_seletivo.publicacoes.models_retificacao import VersaoConsolidada

    editais = [edital for edital in editais if getattr(edital, _CONTEUDOS, None) is None]
    por_edital = {edital.id: [] for edital in editais}
    for edital_id, conteudo in (
        VersaoConsolidada.objects.filter(edital__in=editais)
        .order_by("valid_from", "materialized_at")
        .values_list("edital_id", "content")
    ):
        por_edital[edital_id].append(conteudo)
    for edital in editais:
        setattr(edital, _CONTEUDOS, por_edital[edital.id])


def requisitos_do_edital(edital):
    """Os requisitos de todas as versões publicadas, pelo id; a versão mais recente os nomeia.

    Na ordem da tela: os da inscrição primeiro, depois os da convocação, cada grupo na ordem que o
    Edital declarou.
    """
    por_id = {}
    for conteudo in _conteudos(edital):
        for requisito in conteudo.get("documentRequirements") or []:
            identidade = str(requisito.get("id") or "")
            if not identidade:
                continue
            por_id[identidade] = Requisito(
                id=identidade,
                nome=requisito.get("name") or requisito.get("key") or "Documento",
                chave=requisito.get("key") or "documento",
                momento=(
                    nomes.DA_CONVOCACAO
                    if momento_de(requisito) == NA_CONVOCACAO
                    else nomes.DA_INSCRICAO
                ),
                ordem=int(requisito.get("order") or 0),
                por_modalidade=recorte_de(requisito).forma in FORMAS_POR_MODALIDADE,
            )
    return sorted(por_id.values(), key=lambda r: (not r.da_inscricao, r.ordem, r.nome))


@dataclass(frozen=True)
class Perfil:
    id: str
    nome: str
    ordem: int


def perfis_do_edital(edital, conteudos=None):
    """Os Perfis de todas as versões publicadas, pelo id, na ordem da versão mais recente."""
    por_id = {}
    for conteudo in conteudos if conteudos is not None else _conteudos(edital):
        for ordem, perfil in enumerate(conteudo.get("profiles") or []):
            if isinstance(perfil, dict) and perfil.get("id"):
                nome = str(perfil.get("name") or perfil.get("code") or "Perfil").strip()
                por_id[str(perfil["id"])] = Perfil(str(perfil["id"]), nome, ordem)
    return sorted(por_id.values(), key=lambda perfil: (perfil.ordem, perfil.nome))


def vigente(edital):
    """A versão mais recente da definição, ou `None`: e `None` é que nada vai (FR-3660)."""
    return (
        DefinicaoDosDocumentosDaFormalizacao.objects.filter(edital=edital)
        .order_by("-definido_em", "-id")
        .first()
    )


def historico(edital, requisitos=None):
    """As versões, da mais recente para a primeira, com a diferença calculada na leitura."""
    nomes_por_id = {r.id: r.nome for r in (requisitos or requisitos_do_edital(edital))}
    linhas = list(
        DefinicaoDosDocumentosDaFormalizacao.objects.filter(edital=edital).order_by(
            "definido_em", "id"
        )
    )
    versoes = []
    anterior = set()
    for numero, definicao in enumerate(linhas, start=1):
        atual = {str(r) for r in definicao.requisitos}
        versoes.append(
            Versao(
                definicao=definicao,
                numero=numero,
                acrescentados=sorted(nomes_por_id.get(r, r) for r in atual - anterior),
                retirados=sorted(nomes_por_id.get(r, r) for r in anterior - atual),
            )
        )
        anterior = atual
    return list(reversed(versoes))


def edital_da_conducao(actor, edital_id):
    """O Edital e a base de quem o conduz, ou a recusa da matriz (FR-3654).

    Outra unidade ou inexistente é 404; no escopo, sem gerir a comissão, a recusa que diz o que
    falta. O auditor lê a tela e o histórico, e é a view que decide isso — aqui só se grava.
    """
    edital = (
        Edital.objects.filter(pk=edital_id, institution_scope=actor.institution_scope)
        .select_related("processo")
        .first()
    )
    if edital is None:
        raise DomainError("not_found", "Recurso não encontrado.", 404)
    base = pode_gerir_comissao(actor, edital.processo)
    require_authorization_base(base is not None, bases=BASES_DA_GESTAO_DA_COMISSAO)
    return edital, base


def definir(*, actor, edital_id, requisitos, motivo, correlation_id=""):
    """Grava uma versão nova da definição, com motivo e trilha (FR-3653 a FR-3656)."""
    edital, base = edital_da_conducao(actor, edital_id)
    motivo = (motivo or "").strip()
    if not motivo:
        raise DomainError(
            nomes.MOTIVO_OBRIGATORIO,
            "Diga por que estes documentos vão ao setor. O motivo fica no histórico, que o "
            "auditor lê.",
            422,
            campo="motivo",
        )
    conhecidos = {r.id for r in requisitos_do_edital(edital)}
    if not conhecidos:
        raise DomainError(
            nomes.EDITAL_SEM_PUBLICACAO,
            "Este Edital ainda não tem versão publicada, e por isso não tem documentos a definir.",
            409,
        )
    pedidos = sorted({str(r).strip() for r in requisitos if str(r).strip()})
    if any(r not in conhecidos for r in pedidos):
        raise DomainError(
            nomes.REQUISITO_FORA_DO_EDITAL,
            "Um dos documentos marcados não é deste Edital. Abra a tela de novo.",
            422,
        )
    with command_context() as agora:
        definicao = DefinicaoDosDocumentosDaFormalizacao.objects.create(
            edital=edital,
            requisitos=pedidos,
            motivo=motivo,
            definido_por=actor.subject,
            unidade_de_atuacao=actor.institution_scope,
            definido_em=agora,
        )
        record_event(
            actor=actor,
            permission=base.permissao,
            operation=nomes.DEFINIR,
            aggregate=edital,
            now=agora,
            correlation_id=correlation_id,
            # O id da versão, e não a lista: ela está na linha, e o motivo também.
            reason=f"Versão {definicao.id} da definição dos documentos para a formalização.",
            new_state="",
            new_revision=None,
            detalhe={"definicao": str(definicao.id), "requisitos": len(pedidos)},
        )
    return definicao
