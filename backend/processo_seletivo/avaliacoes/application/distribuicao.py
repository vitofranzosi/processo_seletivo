"""Distribuir as inscrições entre quem já está alocado à Etapa — e desfazer a distribuição.

**O que o lote faz, e o que ele não faz.** Uma submissão atribui um conjunto de inscrições a um
conjunto de avaliadores, e a combinação é **uniforme**: cada inscrição selecionada vai para cada
avaliador selecionado. É assim que distribuir mil inscrições com dupla avaliação cabe em poucas
submissões, e é o mais longe que a `012` vai (FR-013, FR-047).

O que ela **não** faz é repartir: nada aqui divide o conjunto entre as pessoas, sorteia, olha carga
ou escolhe quem avalia quem. Repartir é decisão, e decisão sobre distribuição tem autoria — o
sistema pode um dia **propor**, e a presidência confirmar, mas o ato registrado será o da
confirmação (FR-017, FR-018, FR-019, P-002). Quem quer dividir cem inscrições entre dois avaliadores
faz duas submissões de cinquenta, e as duas são atos dela.

**As duas naturezas de recusa** (FR-085). Regra sobre a linha — impedimento, teto atingido,
atribuição que já existia, conclusão anterior daquela pessoa — é acumulada e relatada, e o restante
é distribuído: recusar quinhentas por causa de uma seria punir o caminho normal, como a alocação em
lote da 011 já decidiu. Erro sobre o pedido — Etapa inexistente, avaliador sem alocação, inscrição
de outro Edital ou não submetida — levanta e desfaz o lote inteiro, porque ali o pedido está errado
e distribuir a parte válida dele seria adivinhar a intenção.
"""

from processo_seletivo.avaliacoes.application.trilha import auditar
from processo_seletivo.avaliacoes.domain.previsao import avaliacoes_previstas
from processo_seletivo.avaliacoes.models import Atribuicao, Avaliacao, Impedimento
from processo_seletivo.comissoes.application import comando_de_comissao, nao_encontrado
from processo_seletivo.comissoes.application.comissao import identificador
from processo_seletivo.comissoes.domain.etapas import etapas_vigentes
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
    return {
        "feitas": len(feitas),
        "verbo": verbo,
        "recusadas": len(recusas),
        "ids": [str(item.id) for item in feitas],
        "motivos": [recusa.declarada() for recusa in recusas],
    }


def _edital_do_processo(processo, edital_id):
    edital = Edital.objects.filter(
        pk=identificador(edital_id),
        processo=processo,
        institution_scope=processo.institution_scope,
    ).first()
    if edital is None:
        raise nao_encontrado()
    return edital


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


def _inscricoes_atribuiveis(edital, ids):
    """Só inscrição **submetida** do Edital daquela Etapa (FR-002, FR-012)."""
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
        etapa = _etapa_vigente_ou_404(edital, etapa_id)
        membros = _membros_alocados(ctx.processo, edital, etapa_id, ids_membros)
        inscricoes = _inscricoes_atribuiveis(edital, ids_inscricoes)
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
