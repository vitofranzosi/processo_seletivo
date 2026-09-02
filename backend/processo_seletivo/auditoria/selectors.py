"""Consultas à trilha de auditoria.

A consulta nasceu dentro da view HTTP em T087. Ao ser também necessária pela interface, foi
trazida para a camada de aplicação: o escopo institucional precisa ser aplicado num lugar só,
e a trilha não pode virar a brecha por onde se enxerga o que não se alcança.
"""

import base64
import binascii

from processo_seletivo.auditoria.models import RegistroAuditoria
from processo_seletivo.shared.api.problems import DomainError

LIMITE_PADRAO = 20
LIMITE_MAXIMO = 100


def parse_limit(valor):
    if valor in (None, ""):
        return LIMITE_PADRAO
    try:
        limite = int(valor)
    except (TypeError, ValueError) as exc:
        raise DomainError("invalid_limit", "O limite deve ser um inteiro.", 400) from exc
    if not 1 <= limite <= LIMITE_MAXIMO:
        raise DomainError("invalid_limit", f"O limite deve estar entre 1 e {LIMITE_MAXIMO}.", 400)
    return limite


def encode_cursor(registro):
    raw = f"{registro.occurred_at.isoformat()}|{registro.event_id}"
    return base64.urlsafe_b64encode(raw.encode()).decode()


def decode_cursor(cursor):
    try:
        occurred_at, event_id = base64.urlsafe_b64decode(cursor.encode()).decode().split("|", 1)
        return occurred_at, event_id
    except (ValueError, UnicodeDecodeError, binascii.Error) as exc:
        raise DomainError("invalid_cursor", "O cursor informado é inválido.", 400) from exc


def consultar(
    *,
    actor,
    aggregate_type=None,
    aggregate_ids=None,
    cursor=None,
    limit=LIMITE_PADRAO,
    operation=None,
):
    """Registros do escopo do ator, do mais recente para o mais antigo, com cursor estável.

    `operation` existe para a trilha de uma comissão grande: constituir uma banca de cento e
    vinte e alocá-la produz centenas de eventos, e “quem perdeu acesso a esta Etapa, e quando”
    não se responde folheando dezenove páginas de vinte.
    """
    registros = RegistroAuditoria.objects.filter(institution_scope=actor.institution_scope)
    if aggregate_type:
        registros = registros.filter(aggregate_type=aggregate_type)
    if aggregate_ids is not None:
        registros = registros.filter(aggregate_id__in=list(aggregate_ids))
    if operation:
        registros = registros.filter(operation=operation)
    if cursor:
        occurred_at, event_id = decode_cursor(cursor)
        # O cursor aponta para o último item já entregue, na mesma ordem decrescente.
        registros = registros.filter(occurred_at__lte=occurred_at).exclude(
            occurred_at=occurred_at, event_id__gte=event_id
        )
    pagina = list(registros.order_by("-occurred_at", "-event_id")[: limit + 1])
    tem_mais = len(pagina) > limit
    pagina = pagina[:limit]
    return pagina, (encode_cursor(pagina[-1]) if pagina and tem_mais else None)


def trilha_do_edital(*, actor, edital, cursor=None, limit=LIMITE_PADRAO):
    """Tudo que aconteceu com um Edital, incluindo suas Retificações.

    Os atos de uma Retificação são auditados sob o identificador dela, não do Edital; quem
    responde questionamento sobre o certame precisa dos dois lados na mesma linha do tempo.
    """
    identificadores = [edital.id, *edital.retificacoes.values_list("id", flat=True)]
    return consultar(actor=actor, aggregate_ids=identificadores, cursor=cursor, limit=limit)


def trilha_da_comissao(
    *, actor, processo, cursor=None, limit=LIMITE_PADRAO, operation=None, pessoa=None
):
    """Tudo que aconteceu com a comissão deste Processo — membros e alocações na mesma linha.

    Os eventos da 011 têm por agregado o membro e a alocação, e não o Processo: é assim que a
    trilha responde "qual Etapa foi afetada". Reunir os dois pelo mesmo `consultar` que já busca
    por conjunto de identificadores é o que evita um subsistema paralelo de log (011, D-018).
    """
    from processo_seletivo.comissoes.models import AlocacaoEtapa, MembroComissao

    da_comissao = MembroComissao.objects.filter(processo=processo)
    if pessoa:
        # Por identificador exato, e não por pedaço do motivo: o motivo é texto livre, e filtrar
        # “ana” trazia os atos de “susana.lima” e as Etapas com “análise” no nome. Numa trilha,
        # mostrar atos de terceiros sob o rótulo de um filtro é pior que não filtrar.
        da_comissao = da_comissao.filter(identity_subject=pessoa)
    membros = list(da_comissao.values_list("id", flat=True))
    alocacoes = list(
        AlocacaoEtapa.objects.filter(membro_id__in=membros).values_list("id", flat=True)
    )
    if pessoa and not membros:
        return [], None
    return consultar(
        actor=actor,
        aggregate_ids=[*membros, *alocacoes],
        cursor=cursor,
        limit=limit,
        operation=operation,
    )


def trilha_da_avaliacao(
    *,
    actor,
    edital,
    etapa_id,
    inscricao=None,
    avaliador=None,
    cursor=None,
    limit=LIMITE_PADRAO,
    operation=None,
):
    """Tudo que aconteceu na execução do trabalho de uma Etapa — filtrável pelas três dimensões.

    FR-050 pede a trilha filtrável por inscrição, por avaliador e por operação, e as duas primeiras
    **não saem de graça**:

    - **`aggregate_id` não é a inscrição.** Os sete atos têm agregados diferentes: abrir documento
      registra sobre `Inscricao`, herdado da 009; atribuir e remover sobre `Atribuicao`; gravar,
      concluir e reabrir sobre `Avaliacao`; impedir sobre o `Impedimento`, e sobre cada Atribuição
      inativada. Filtrar por um só traria um sétimo dos eventos e esconderia o resto — pior que
      não filtrar, porque parece completo.
    - **`actor_subject` não é o avaliador.** Ele é quem praticou o ato, e nos atos da presidência o
      avaliador é o **afetado**. Perguntar "o que aconteceu com o trabalho da Ana" por ele
      devolveria só o que a Ana fez, e nada do que fizeram com ela.

    Daí os sete atos serem resolvidos **pelas relações**, e não por um campo do registro. Todos
    eles ancoram em objeto que nomeia a Etapa: atribuir, remover e abrir documento na Atribuição;
    gravar, concluir e reabrir na Avaliação; impedir no Impedimento (T-016).

    A abertura de documento **ancorou na Inscrição até 2026-09-02**, e ancorar ali era defeito: a
    Inscrição não distingue Etapa nem avaliador, de modo que a trilha de uma Etapa mostrava as
    aberturas de outra — e as consultas administrativas da 009, que registram a mesma operação
    sobre a mesma Inscrição, apareciam como se fossem trabalho da Mesa. Um histórico que mistura
    atos de origens diferentes é pior que um histórico incompleto, porque parece verdadeiro.

    O molde é `trilha_da_comissao`: resolver identificadores pelas relações e entregar o conjunto
    ao `consultar` que já existe, em vez de carimbar a inscrição em cada evento. Sendo **uma**
    consulta, e não duas reunidas em memória, o cursor da paginação continua valendo — duas
    páginas somadas fora do banco não têm cursor comum, e a segunda ficava inalcançável.
    """
    from processo_seletivo.avaliacoes.models import Atribuicao, Avaliacao, Impedimento

    atribuicoes = Atribuicao.objects.filter(edital=edital, etapa_id=etapa_id)
    impedimentos = Impedimento.objects.filter(inscricao__edital=edital)
    if inscricao:
        atribuicoes = atribuicoes.filter(inscricao_id=inscricao)
        impedimentos = impedimentos.filter(inscricao_id=inscricao)
    if avaliador:
        # Por Atribuição, e não pelo ator: nos atos da presidência quem pratica é ela, e filtrar
        # pelo ator devolveria só o que a pessoa fez — nunca o que fizeram com o trabalho dela.
        atribuicoes = atribuicoes.filter(membro__identity_subject=avaliador)
        impedimentos = impedimentos.filter(identity_subject=avaliador)
    ids_atribuicoes = list(atribuicoes.values_list("id", flat=True))
    ids_avaliacoes = list(
        Avaliacao.objects.filter(atribuicao_id__in=ids_atribuicoes).values_list("id", flat=True)
    )
    relacionados = [*ids_atribuicoes, *ids_avaliacoes, *impedimentos.values_list("id", flat=True)]
    return consultar(
        actor=actor,
        aggregate_ids=relacionados,
        cursor=cursor,
        limit=limit,
        operation=operation,
    )
