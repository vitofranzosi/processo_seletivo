"""Distribuir as inscrições entre quem já está alocado à Etapa — e desfazer a distribuição.

**O que o lote faz, e o que ele não faz.** Uma submissão atribui um conjunto de inscrições a um
conjunto de avaliadores, e a combinação é **uniforme**: cada inscrição selecionada vai para cada
avaliador selecionado. É assim que distribuir mil inscrições com dupla avaliação cabe em poucas
submissões, e é o mais longe que a `012` vai (FR-013, FR-047).

O que ela **não** faz é repartir: nada aqui divide o conjunto entre as pessoas, sorteia, olha carga
ou escolhe quem avalia quem. Repartir é decisão, e decisão sobre distribuição tem autoria.

**O sistema propõe; a presidência confirma** (`propor_rodizio` e `confirmar_rodizio`, e a regra em
`domain/rodizio.py`). É o "um dia" que esta docstring previa, e ele existe porque o caminho manual
não cabia na escala real: 600 inscrições com dupla avaliação custavam 24 telas e cerca de 700
marcações, e o equilíbrio da carga era aritmética de quem distribui. A proposta não grava nada, é
mostrada inteira antes de valer, e o ato registrado é o da confirmação — que é o que FR-017, FR-018
e FR-019 protegem: decisão sem autor é o que não pode existir (FR-107, P-002).

**As duas naturezas de recusa** (FR-085). Regra sobre a linha — impedimento, teto atingido,
atribuição que já existia, conclusão anterior daquela pessoa — é acumulada e relatada, e o restante
é distribuído: recusar quinhentas por causa de uma seria punir o caminho normal, como a alocação em
lote da 011 já decidiu. Erro sobre o pedido — Etapa inexistente, avaliador sem alocação, inscrição
de outro Edital ou não submetida — levanta e desfaz o lote inteiro, porque ali o pedido está errado
e distribuir a parte válida dele seria adivinhar a intenção.
"""

from django.utils import timezone

from processo_seletivo.avaliacoes.application.trilha import auditar
from processo_seletivo.avaliacoes.domain import rodizio
from processo_seletivo.avaliacoes.domain.conjunto import recusa_por_inscricoes_em_curso
from processo_seletivo.avaliacoes.domain.previsao import avaliacoes_previstas
from processo_seletivo.avaliacoes.models import Atribuicao, Avaliacao, Impedimento
from processo_seletivo.comissoes.application import comando_de_comissao, nao_encontrado
from processo_seletivo.comissoes.application.comissao import identificador
from processo_seletivo.comissoes.domain.etapas import conteudo_vigente, etapas_vigentes
from processo_seletivo.comissoes.models import AlocacaoEtapa, MembroComissao
from processo_seletivo.inscricoes.models import Inscricao
from processo_seletivo.processos.models import Edital
from processo_seletivo.shared.api.problems import DomainError

ATRIBUIR = "AVALIACAO_ATRIBUIR"
REMOVER = "AVALIACAO_ATRIBUICAO_REMOVER"

# **A recusa que impede a via comum de virar seletor de notas** (FR-092).
#
# Sem ela, esta sequência seria possível e indistinguível de trabalho normal: dois avaliadores
# concluem, a presidência não gosta de uma das notas, remove aquela Atribuição, a avaliação deixa
# de ser elegível, e a inscrição é distribuída a um terceiro. Isso é escolher qual avaliação conta
# no resultado, com a aparência de organizar o trabalho.
#
# A recusa nomeia os atos que **de fato** têm esse efeito, e o que cada um exige — porque
# invalidar uma avaliação concluída é legítimo quando há motivo, e o que não pode existir é o
# efeito sem o ato.
MOTIVO_DE_FR_092 = (
    "Esta avaliação já foi concluída, e a via comum de redistribuição não a alcança. "
    "Tirar uma avaliação concluída do conjunto elegível exige ato nomeado, com motivo e "
    "auditoria: registre o impedimento entre esta pessoa e esta inscrição, ou reabra a avaliação "
    "para que ela seja refeita."
)


class Recusa:
    """Uma linha que não foi distribuída, e por quê."""

    def __init__(self, membro, inscricao, motivo):
        self.membro = membro
        self.inscricao = inscricao
        self.motivo = motivo

    def declarada(self):
        return {
            "avaliador": self.membro.identity_subject,
            "inscricao": self.inscricao.protocolo or str(self.inscricao.id),
            "motivo": self.motivo,
        }

    def __repr__(self):
        return f"Recusa({self.membro}, {self.inscricao}, {self.motivo!r})"


def resultado_declarado(feitas, recusas, verbo):
    """O desfecho do lote, na forma que a tela mostra e que a repetição devolve (FR-097).

    É **serializável** de propósito: ele é guardado na reserva de idempotência, porque recusa não
    é reconstruível depois — o estado que a produziu mudou no ato seguinte.
    """
    declaradas = [recusa.declarada() for recusa in recusas]
    return {
        "feitas": len(feitas),
        "verbo": verbo,
        "recusadas": len(recusas),
        "ids": [str(item.id) for item in feitas],
        "motivos": declaradas,
        "agrupados": _agrupar(declaradas),
    }


def _agrupar(declaradas):
    """As recusas por motivo, e não uma linha por par (FR-097).

    Vinte e cinco inscrições enviadas a três pessoas para duas vagas produziam setenta e cinco
    linhas repetindo a mesma frase. A informação — “o conjunto não cabe” — some no meio da
    repetição, que é o oposto de declarar o desfecho.
    """
    grupos = {}
    for item in declaradas:
        grupo = grupos.setdefault(item["motivo"], {"motivo": item["motivo"], "inscricoes": []})
        if item["inscricao"] not in grupo["inscricoes"]:
            grupo["inscricoes"].append(item["inscricao"])
    resumo = []
    for grupo in grupos.values():
        inscricoes = grupo["inscricoes"]
        amostra = ", ".join(inscricoes[:3])
        resto = len(inscricoes) - 3
        resumo.append(
            {
                "motivo": grupo["motivo"],
                "quantas": len(inscricoes),
                "exemplos": (
                    f"inscrições {amostra}" + (f" e mais {resto}" if resto > 0 else "")
                    if len(inscricoes) > 1
                    else f"inscrição {amostra}"
                ),
            }
        )
    return sorted(resumo, key=lambda item: -item["quantas"])


def _edital_do_processo(processo, edital_id):
    edital = Edital.objects.filter(
        pk=identificador(edital_id),
        processo=processo,
        institution_scope=processo.institution_scope,
    ).first()
    if edital is None:
        raise nao_encontrado()
    return edital


def _exigir_conjunto_fechado(edital):
    """E2E-017. Vale nos dois caminhos: proteger só o manual deixaria o automático como porta larga.

    A recusa acontece antes de qualquer leitura de membro ou inscrição, porque o que ela diz não
    depende de quem foi selecionado — depende só do prazo.
    """
    recusa = recusa_por_inscricoes_em_curso(conteudo_vigente(edital), timezone.now())
    if recusa is not None:
        raise recusa


def _etapa_vigente_ou_404(edital, etapa_id):
    vigentes = etapas_vigentes(edital)
    if etapa_id not in vigentes:
        raise nao_encontrado()
    return vigentes[etapa_id]


def _membros_alocados(processo, edital, etapa_id, ids):
    """Os membros pedidos, exigindo alocação ativa naquela Etapa (FR-011).

    Falta de alocação é **erro sobre o pedido**, e não recusa de linha: pedir para distribuir a
    quem não pode atuar na Etapa não é o caminho normal esbarrando numa regra — é uma seleção que
    a tela não deveria ter oferecido.
    """
    membros = list(MembroComissao.objects.filter(pk__in=ids, processo=processo, ativo=True))
    if len(membros) != len(set(ids)):
        raise DomainError(
            "pessoa_nao_e_membro_ativo",
            "Só membros ativos da comissão podem receber inscrições.",
            422,
            campo="membro_id",
        )
    alocados = set(
        AlocacaoEtapa.objects.filter(
            membro__in=membros, edital=edital, etapa_id=etapa_id, ativo=True
        ).values_list("membro_id", flat=True)
    )
    faltando = [m for m in membros if m.id not in alocados]
    if faltando:
        raise DomainError(
            "avaliador_sem_alocacao",
            "Só quem está alocado nesta Etapa pode receber inscrições dela.",
            422,
            campo="membro_id",
        )
    return membros


def _inscricoes_atribuiveis(edital, ids, etapa_id=None):
    """Só inscrição **submetida** do Edital daquela Etapa (FR-002, FR-012).

    A `013` acrescenta a segunda condição: quem foi eliminado numa Etapa anterior, ou ainda aguarda
    o resultado da anterior, não é distribuível. É **erro do pedido**, e não recusa de linha — a
    mesma classificação que a submissão já tem aqui, e pelo mesmo motivo: uma seleção que a tela não
    deveria ter oferecido não é o caminho normal esbarrando numa regra (013, FR-007).
    """
    inscricoes = list(
        Inscricao.objects.filter(pk__in=ids, edital=edital, status=Inscricao.Status.SUBMETIDA)
    )
    if len(inscricoes) != len(set(ids)):
        raise DomainError(
            "inscricao_nao_atribuivel",
            "Só inscrições submetidas deste Edital podem ser distribuídas.",
            422,
            campo="inscricao_id",
        )
    if etapa_id is not None:
        from processo_seletivo.resultados.application.prontidao import restringir_a_participantes

        # A restrição é dobrada na consulta, e a comparação é de contagem: a seleção inteira ou
        # nada, sem uma pergunta por inscrição selecionada.
        participantes = restringir_a_participantes(
            Inscricao.objects.filter(pk__in=[i.id for i in inscricoes]),
            edital=edital,
            etapa_id=etapa_id,
            prefixo="",
        ).count()
        if participantes != len(inscricoes):
            raise DomainError(
                "inscricao_fora_da_etapa",
                "Uma ou mais inscrições selecionadas não participam desta Etapa: elas foram "
                "eliminadas numa Etapa anterior ou ainda aguardam o resultado da anterior.",
                422,
                campo="inscricao_id",
            )
    return inscricoes


def _contexto_de_recusa(edital, etapa_id, membros, inscricoes):
    """Tudo o que decide recusa de linha, em consultas por conjunto — nunca por linha (FR-048)."""
    identidades = {m.identity_subject for m in membros}
    ids_inscricoes = [i.id for i in inscricoes]
    impedidos = set(
        Impedimento.objects.filter(
            identity_subject__in=identidades, inscricao_id__in=ids_inscricoes
        ).values_list("identity_subject", "inscricao_id")
    )
    ja_atribuidas = set(
        Atribuicao.objects.filter(
            membro__in=membros,
            edital=edital,
            etapa_id=etapa_id,
            inscricao_id__in=ids_inscricoes,
            ativo=True,
        ).values_list("membro_id", "inscricao_id")
    )
    ja_concluidas = set(
        Avaliacao.objects.filter(
            identity_subject__in=identidades,
            etapa_id=etapa_id,
            inscricao_id__in=ids_inscricoes,
            estado=Avaliacao.Estado.CONCLUIDA,
        ).values_list("identity_subject", "inscricao_id")
    )
    ocupacao = {}
    for inscricao_id in Atribuicao.objects.filter(
        edital=edital, etapa_id=etapa_id, inscricao_id__in=ids_inscricoes, ativo=True
    ).values_list("inscricao_id", flat=True):
        ocupacao[inscricao_id] = ocupacao.get(inscricao_id, 0) + 1
    return impedidos, ja_atribuidas, ja_concluidas, ocupacao


def distribuir(
    *,
    actor,
    processo_id,
    edital_id,
    etapa_id,
    membro_ids,
    inscricao_ids,
    idempotency_key,
    correlation_id,
):
    """O **resultado declarado** do lote.

    Cada Atribuição criada gera seu evento, inclusive no lote (FR-016).
    """
    etapa_id = identificador(etapa_id)
    ids_membros = [identificador(m) for m in membro_ids]
    ids_inscricoes = [identificador(i) for i in inscricao_ids]
    if not ids_membros or not ids_inscricoes:
        raise DomainError(
            "selecao_vazia",
            "Selecione ao menos um avaliador e ao menos uma inscrição.",
            422,
            campo="inscricao_id",
        )
    with comando_de_comissao(
        actor=actor,
        processo_id=processo_id,
        operation="avaliacao:distribuir",
        payload={
            "etapa": str(etapa_id),
            "membros": sorted(str(i) for i in ids_membros),
            "inscricoes": sorted(str(i) for i in ids_inscricoes),
        },
        idempotency_key=idempotency_key,
    ) as ctx:
        edital = _edital_do_processo(ctx.processo, edital_id)
        if ctx.repetido:
            return ctx.desfecho_anterior
        _exigir_conjunto_fechado(edital)
        etapa = _etapa_vigente_ou_404(edital, etapa_id)
        membros = _membros_alocados(ctx.processo, edital, etapa_id, ids_membros)
        inscricoes = _inscricoes_atribuiveis(edital, ids_inscricoes, etapa_id=etapa_id)
        previstas = avaliacoes_previstas(etapa)
        impedidos, ja_atribuidas, ja_concluidas, ocupacao = _contexto_de_recusa(
            edital, etapa_id, membros, inscricoes
        )
        nome_da_etapa = etapa.get("name") or str(etapa_id)

        criadas, recusas = [], []
        for inscricao in inscricoes:
            candidatos = []
            for membro in membros:
                motivo = _motivo_da_recusa(
                    membro, inscricao, impedidos, ja_atribuidas, ja_concluidas
                )
                if motivo is not None:
                    recusas.append(Recusa(membro, inscricao, motivo))
                    continue
                candidatos.append(membro)
            vagas = previstas - ocupacao.get(inscricao.id, 0)
            if len(candidatos) > vagas:
                # **O conjunto não cabe, e o sistema não escolhe quem fica.** Conceder as vagas na
                # ordem em que os membros vieram faria a ordenação do banco decidir quem avalia
                # quem — decisão de distribuição, tomada por ninguém, que é exatamente o que
                # FR-017 e P-002 recusam. Recusa-se a inscrição inteira, e a presidência escolhe.
                recusas.extend(
                    Recusa(membro, inscricao, _motivo_do_excesso(vagas, len(candidatos), previstas))
                    for membro in candidatos
                )
                continue
            for membro in candidatos:
                atribuicao = Atribuicao.objects.create(
                    membro=membro,
                    edital=edital,
                    etapa_id=etapa_id,
                    inscricao=inscricao,
                    criado_em=ctx.now,
                    criado_por=actor.subject,
                )
                ocupacao[inscricao.id] = ocupacao.get(inscricao.id, 0) + 1
                criadas.append(atribuicao)
                # Um evento por Atribuição, inclusive no lote: a trilha responde por agregado, e
                # "quem passou a avaliar esta inscrição, e quando" é a pergunta que ela existe
                # para responder (FR-016, FR-052).
                auditar(
                    actor=actor,
                    permissao=ctx.base.permissao,
                    operation=ATRIBUIR,
                    aggregate=atribuicao,
                    now=ctx.now,
                    correlation_id=correlation_id,
                    reason=_motivo_do_ato(membro, inscricao, nome_da_etapa),
                    idempotency_key=idempotency_key,
                )
        resultado = resultado_declarado(criadas, recusas, "atribuída")
        ctx.concluir_sem_resultado(201, resultado)
        return resultado


def _carga_atual(edital, etapa_id, membros):
    """Quantas atribuições ativas cada pessoa já tem nesta Etapa — por agregação (FR-048)."""
    from django.db.models import Count

    contagem = dict(
        Atribuicao.objects.filter(edital=edital, etapa_id=etapa_id, ativo=True, membro__in=membros)
        .values_list("membro_id")
        .annotate(total=Count("id"))
    )
    return {membro.id: contagem.get(membro.id, 0) for membro in membros}


def _carentes(edital, etapa_id, previstas):
    """As inscrições submetidas que ainda têm vaga, na ordem do protocolo.

    A ordem é a do protocolo porque a proposta precisa ser reproduzível: a mesma pergunta, sobre o
    mesmo estado, tem de devolver a mesma resposta — senão não há o que conferir sob trava.
    """
    from processo_seletivo.resultados.application.prontidao import restringir_a_participantes

    # **A progressão vale aqui também.** Proteger só o caminho manual deixaria o automático como a
    # porta larga: o rodízio parte de todas as submetidas, e sem esta restrição proporia — e a
    # confirmação criaria — Atribuição para inscrição eliminada na Etapa anterior. A regra é da
    # Etapa, e não da forma de distribuir (013, FR-005).
    inscricoes = list(
        restringir_a_participantes(
            Inscricao.objects.filter(edital=edital, status=Inscricao.Status.SUBMETIDA),
            edital=edital,
            etapa_id=etapa_id,
            prefixo="",
        ).order_by("protocolo", "id")
    )
    ocupacao = {}
    for inscricao_id in Atribuicao.objects.filter(
        edital=edital, etapa_id=etapa_id, ativo=True
    ).values_list("inscricao_id", flat=True):
        ocupacao[inscricao_id] = ocupacao.get(inscricao_id, 0) + 1
    return [i for i in inscricoes if ocupacao.get(i.id, 0) < previstas], ocupacao


def _plano_do_rodizio(processo, edital, etapa_id, ids_membros):
    """O estado lido e a proposta calculada — sem escrever nada."""
    etapa = _etapa_vigente_ou_404(edital, etapa_id)
    membros = _membros_alocados(processo, edital, etapa_id, ids_membros)
    previstas = avaliacoes_previstas(etapa)
    inscricoes, ocupacao = _carentes(edital, etapa_id, previstas)
    impedidos, ja_atribuidas, ja_concluidas, _ = _contexto_de_recusa(
        edital, etapa_id, membros, inscricoes
    )
    carga = _carga_atual(edital, etapa_id, membros)
    pares, projecao, fora = rodizio.propor(
        previstas=previstas,
        inscricoes=inscricoes,
        membros=membros,
        ocupacao=ocupacao,
        carga=carga,
        impedidos=impedidos,
        ja_atribuidas=ja_atribuidas,
        ja_concluidas=ja_concluidas,
    )
    return etapa, membros, pares, projecao, fora, carga


def propor_rodizio(*, actor, processo, edital_id, etapa_id, membro_ids):
    """A proposta, para a presidência ler antes de decidir. **Não grava nada** (FR-107).

    Devolve o que a tela precisa dizer: quantas atribuições no total, quantas para cada pessoa —
    antes e depois —, o que fica de fora e por quê, e a assinatura que a confirmação vai carregar.
    """
    ids_membros = [identificador(m) for m in membro_ids]
    if not ids_membros:
        raise DomainError(
            "selecao_vazia",
            "Selecione as pessoas entre quem distribuir.",
            422,
            campo="membro_id",
        )
    edital = _edital_do_processo(processo, edital_id)
    # Recusar aqui, e não só na confirmação: propor um plano que a confirmação vai recusar seria
    # convidar a presidência a montar o que não pode ser executado.
    _exigir_conjunto_fechado(edital)
    etapa_id = identificador(etapa_id)
    _, membros, pares, projecao, fora, carga = _plano_do_rodizio(
        processo, edital, etapa_id, ids_membros
    )
    return {
        "total": len(pares),
        "inscricoes": len({inscricao.id for inscricao, _ in pares}),
        "por_pessoa": [
            {
                "membro": membro,
                "antes": carga[membro.id],
                "depois": projecao[membro.id],
                "recebe": projecao[membro.id] - carga[membro.id],
            }
            for membro in membros
        ],
        "fora": [item.declarada() for item in fora],
        "assinatura": rodizio.assinar(pares),
        "membro_ids": [str(i) for i in ids_membros],
    }


def confirmar_rodizio(
    *,
    actor,
    processo_id,
    edital_id,
    etapa_id,
    membro_ids,
    assinatura,
    idempotency_key,
    correlation_id,
):
    """O ato: grava a proposta **que foi confirmada**, e nenhuma outra (FR-107).

    A proposta é recalculada **depois da trava** e conferida contra a assinatura que a presidência
    viu. Entre ver e confirmar, uma conclusão nova ou um impedimento mudam quem recebe o quê sem
    mudar quantos são — e confirmar um plano executando outro é a mesma falha que FR-041 e FR-106
    existem para impedir, só que distribuída por seiscentas linhas.
    """
    ids_membros = [identificador(m) for m in membro_ids]
    etapa_id = identificador(etapa_id)
    if not ids_membros:
        raise DomainError(
            "selecao_vazia",
            "Selecione as pessoas entre quem distribuir.",
            422,
            campo="membro_id",
        )
    if not (assinatura or "").strip():
        # **Sem a assinatura não há proposta confirmada**, e sem proposta confirmada não há ato:
        # gravar aqui seria o sistema distribuindo por conta própria, que é exatamente o que
        # FR-017 recusa. A conferência não pode ser desligável por quem monta o formulário.
        raise DomainError(
            "proposta_nao_confirmada",
            "Nenhuma distribuição foi confirmada. Peça a proposta, confira o que ela faz e então "
            "confirme.",
            422,
            campo="assinatura",
        )
    with comando_de_comissao(
        actor=actor,
        processo_id=processo_id,
        operation="avaliacao:distribuir-rodizio",
        payload={
            "etapa": str(etapa_id),
            "membros": sorted(str(i) for i in ids_membros),
            "proposta": assinatura or "",
        },
        idempotency_key=idempotency_key,
    ) as ctx:
        edital = _edital_do_processo(ctx.processo, edital_id)
        if ctx.repetido:
            return ctx.desfecho_anterior
        etapa, _, pares, _, fora, _ = _plano_do_rodizio(ctx.processo, edital, etapa_id, ids_membros)
        if rodizio.assinar(pares) != assinatura:
            raise DomainError(
                "proposta_mudou",
                "A distribuição proposta mudou desde que você a viu — alguém concluiu, foi "
                "impedido ou recebeu inscrição nesse intervalo. Confira a nova proposta antes de "
                "confirmar.",
                409,
            )
        if not pares:
            raise DomainError(
                "nada_a_distribuir",
                "Não há inscrição com vaga para estas pessoas nesta Etapa.",
                422,
                campo="membro_id",
            )
        nome_da_etapa = etapa.get("name") or str(etapa_id)
        criadas = []
        for inscricao, membro in pares:
            atribuicao = Atribuicao.objects.create(
                membro=membro,
                edital=edital,
                etapa_id=etapa_id,
                inscricao=inscricao,
                criado_em=ctx.now,
                criado_por=actor.subject,
            )
            criadas.append(atribuicao)
            # Um evento por Atribuição, como no lote manual: o que muda é como a presidência
            # chegou à decisão, não o que a trilha guarda dela (FR-016, FR-052).
            auditar(
                actor=actor,
                permissao=ctx.base.permissao,
                operation=ATRIBUIR,
                aggregate=atribuicao,
                now=ctx.now,
                correlation_id=correlation_id,
                reason=_motivo_do_ato(membro, inscricao, nome_da_etapa),
                idempotency_key=idempotency_key,
            )
        motivos = [
            {
                "avaliador": "—",
                "inscricao": item.inscricao.protocolo or str(item.inscricao.id),
                "motivo": item.motivo,
            }
            for item in fora
        ]
        resultado = {
            "feitas": len(criadas),
            "verbo": "atribuída",
            "recusadas": len(fora),
            "ids": [str(a.id) for a in criadas],
            "motivos": motivos,
            "agrupados": _agrupar(motivos),
        }
        ctx.concluir_sem_resultado(201, resultado)
        return resultado


def _motivo_do_ato(membro, inscricao, nome_da_etapa):
    """O que a trilha guarda do ato: quem, qual inscrição e que Etapa era **então**.

    O protocolo antes do identificador porque é ele que a pessoa reconhece; e o nome da Etapa
    porque o UUID sozinho não informa quem audita, como a 011 já registrou.
    """
    protocolo = inscricao.protocolo or inscricao.id
    return f"{membro.identity_subject} — inscrição {protocolo}, Etapa “{nome_da_etapa}”"


def _motivo_do_excesso(vagas, candidatos, previstas):
    """O conjunto não cabe — e é a presidência que escolhe, não a ordenação do banco.

    Conceder as vagas na ordem em que os membros vieram faria o sistema decidir quem avalia quem,
    e a ordem seria a de `MembroComissao.Meta.ordering`: função e identificador. Ninguém teria
    tomado a decisão, e ela pareceria distribuição (FR-017, FR-019, P-002).
    """
    if vagas <= 0:
        return (
            f"Esta inscrição já tem as {previstas} avaliações que o Edital declara para esta Etapa."
        )
    plural = "s" if vagas > 1 else ""
    return (
        f"Restam {vagas} vaga{plural} nesta inscrição e {candidatos} pessoas foram selecionadas. "
        "Escolha quem avalia esta inscrição — o sistema não escolhe por você."
    )


def _motivo_da_recusa(membro, inscricao, impedidos, ja_atribuidas, ja_concluidas):
    """As três regras que dependem **só** da linha; o teto é da inscrição, e vem depois."""
    if (membro.identity_subject, inscricao.id) in impedidos:
        return "Há impedimento registrado entre esta pessoa e esta inscrição."
    if (membro.id, inscricao.id) in ja_atribuidas:
        return "Esta inscrição já estava atribuída a esta pessoa."
    if (membro.identity_subject, inscricao.id) in ja_concluidas:
        return (
            "Esta pessoa já concluiu a avaliação desta inscrição nesta Etapa. "
            "O caminho de volta é a reabertura."
        )
    return None


def remover_atribuicao(*, actor, processo_id, atribuicao_ids, idempotency_key, correlation_id):
    """Retira Atribuições — e alcança **apenas** as que não têm Avaliação concluída.

    A recusa nomeada de FR-092, que diz quais atos teriam esse efeito, entra com o impedimento e a
    anulação declarada. Aqui a via comum simplesmente não alcança: retirar trabalho de quem já
    concluiu mudaria o conjunto que a `013` consome, e isso não pode ser efeito colateral de
    reorganizar a distribuição.
    """
    ids = [identificador(i) for i in atribuicao_ids]
    if not ids:
        raise DomainError(
            "selecao_vazia",
            "Selecione ao menos uma atribuição para remover.",
            422,
            campo="atribuicao_id",
        )
    with comando_de_comissao(
        actor=actor,
        processo_id=processo_id,
        operation="avaliacao:remover-atribuicao",
        payload={"atribuicoes": sorted(str(i) for i in ids)},
        idempotency_key=idempotency_key,
    ) as ctx:
        if ctx.repetido:
            return ctx.desfecho_anterior
        # **A trava vem antes da leitura das conclusões**, e é a mesma linha que `concluir`
        # bloqueia. Sem ela, esta consulta poderia ler "pendente", inativar, e uma conclusão
        # concorrente gravar depois — produzindo avaliação concluída e inelegível pela via comum,
        # que é o efeito sem ato que FR-092 impede.
        atribuicoes = list(
            Atribuicao.objects.select_for_update(of=("self",))
            .filter(pk__in=ids, edital__processo=ctx.processo, ativo=True)
            .select_related("membro", "inscricao")
        )
        concluidas = set(
            Avaliacao.objects.filter(
                atribuicao__in=atribuicoes, estado=Avaliacao.Estado.CONCLUIDA
            ).values_list("atribuicao_id", flat=True)
        )
        removidas, recusas = [], []
        for atribuicao in atribuicoes:
            if atribuicao.id in concluidas:
                recusas.append(Recusa(atribuicao.membro, atribuicao.inscricao, MOTIVO_DE_FR_092))
                continue
            Atribuicao.objects.filter(pk=atribuicao.pk).update(
                ativo=False, inativado_em=ctx.now, inativado_por=actor.subject
            )
            removidas.append(atribuicao)
            auditar(
                actor=actor,
                permissao=ctx.base.permissao,
                operation=REMOVER,
                aggregate=atribuicao,
                now=ctx.now,
                correlation_id=correlation_id,
                reason=(
                    f"{atribuicao.membro.identity_subject} — inscrição "
                    f"{atribuicao.inscricao.protocolo or atribuicao.inscricao_id}"
                ),
                idempotency_key=idempotency_key,
            )
        resultado = resultado_declarado(removidas, recusas, "removida")
        ctx.concluir_sem_resultado(200, resultado)
        return resultado
