"""Registrar que uma pessoa não pode avaliar determinada inscrição — e o efeito disso.

**O impedimento acompanha a pessoa**, pela identidade institucional estável, e não o vínculo de
comissão: preso ao vínculo, ele morreria quando ela saísse e readicioná-la seria o caminho para
contorná-lo. Ele nomeia razões que não mudam por reorganização administrativa (FR-099).

**Ele age antes da cadeia de autorização, e não dentro dela.** Registrar impedimento sobre uma
Atribuição ativa a inativa no mesmo ato; a autorização continua com duas condições, porque somar
uma terceira acrescentaria uma verificação por linha a toda listagem da feature (FR-080, FR-048).

**A 012 não infere impedimento** por CPF, sobrenome ou coincidência de dado. Declarar é ato de quem
sabe (FR-042).
"""

from processo_seletivo.avaliacoes.application.trilha import auditar
from processo_seletivo.avaliacoes.models import Atribuicao, Avaliacao, Impedimento
from processo_seletivo.comissoes.application import comando_de_comissao, nao_encontrado
from processo_seletivo.comissoes.application.comissao import identificador
from processo_seletivo.comissoes.models import MembroComissao
from processo_seletivo.inscricoes.models import Inscricao
from processo_seletivo.shared.api.problems import DomainError

IMPEDIR = "AVALIACAO_IMPEDIR"
# O ato que tira uma Avaliação do conjunto elegível tem nome próprio na trilha, e não se confunde
# com a remoção corriqueira de uma atribuição pendente (FR-092, FR-093).
TORNAR_INELEGIVEL = "AVALIACAO_TORNAR_INELEGIVEL"


def alcance_do_impedimento(*, processo, identity_subject, inscricao_id):
    """Quantas Atribuições ativas este impedimento inativará — **antes** de ele ser confirmado.

    Retirar trabalho de alguém não pode ser efeito colateral silencioso de registrar um motivo: a
    confirmação declara o alcance, e quem confirma sabe o que está fazendo (FR-041).
    """
    ativas = Atribuicao.objects.filter(
        membro__processo=processo,
        membro__identity_subject=identity_subject,
        inscricao_id=inscricao_id,
        ativo=True,
    )
    concluidas = Avaliacao.objects.filter(
        atribuicao__in=ativas, estado=Avaliacao.Estado.CONCLUIDA
    ).count()
    return {"atribuicoes": ativas.count(), "concluidas": concluidas}


def registrar_impedimento(
    *, actor, processo_id, identity_subject, inscricao_id, motivo, idempotency_key, correlation_id
):
    """Cria o impedimento e inativa as Atribuições ativas do par, na mesma transação.

    Devolve o **resultado declarado** do ato: quantas Atribuições foram inativadas e quantas delas
    tinham conclusão.

    As Avaliações já concluídas são **preservadas e tornadas inelegíveis** — nada nelas é apagado
    ou alterado, e elas deixam de integrar o conjunto que a 013 consome, o que libera a vaga que
    ocupavam (FR-041, FR-079, FR-090).
    """
    subject = (identity_subject or "").strip()
    texto = (motivo or "").strip()
    if not subject:
        raise DomainError(
            "identidade_obrigatoria", "Informe quem está impedido.", 422, campo="identity_subject"
        )
    if not texto:
        # O motivo é o que faz do impedimento um ato, e não uma preferência (FR-039).
        raise DomainError(
            "motivo_obrigatorio",
            "O impedimento exige motivo: é ele que sustenta o ato.",
            422,
            campo="motivo",
        )
    with comando_de_comissao(
        actor=actor,
        processo_id=processo_id,
        operation="avaliacao:impedir",
        # O motivo entra no conteúdo da chave: sem ele, reenviar a mesma chave com outro motivo
        # seria tratado como repetição, e o ato registrado não seria o que se pediu (FR-084).
        payload={"pessoa": subject, "inscricao": str(inscricao_id), "motivo": texto},
        idempotency_key=idempotency_key,
    ) as ctx:
        inscricao = Inscricao.objects.filter(
            pk=identificador(inscricao_id), edital__processo=ctx.processo
        ).first()
        if inscricao is None:
            raise nao_encontrado()
        if ctx.repetido:
            # **O desfecho original, e não um vazio.** A tela precisa dizer quantas atribuições o
            # ato inativou, e essa contagem não é reconstruível depois (FR-084, FR-097).
            return ctx.desfecho_anterior
        if not MembroComissao.objects.filter(
            processo=ctx.processo, identity_subject=subject
        ).exists():
            # Impedir quem nunca integrou esta comissão não é ato desta tela — e aceitar criaria
            # registro sobre alguém que o Processo não conhece.
            raise DomainError(
                "pessoa_fora_da_comissao",
                "Só quem integra ou integrou esta comissão pode ser declarado impedido.",
                422,
                campo="identity_subject",
            )
        impedimento, criado = Impedimento.objects.get_or_create(
            identity_subject=subject,
            inscricao=inscricao,
            defaults={"motivo": texto, "criado_em": ctx.now, "criado_por": actor.subject},
        )
        if not criado:
            raise DomainError(
                "impedimento_ja_registrado",
                "Já existe impedimento registrado entre esta pessoa e esta inscrição.",
                409,
                campo="identity_subject",
            )
        auditar(
            actor=actor,
            permissao=ctx.base.permissao,
            operation=IMPEDIR,
            # **O agregado é o próprio Impedimento**: impedir quem não tem Atribuição ativa é ato
            # legítimo — o caso preventivo — e ali não há Atribuição a que ancorar (T-016).
            aggregate=impedimento,
            now=ctx.now,
            correlation_id=correlation_id,
            reason=texto,
            idempotency_key=idempotency_key,
            com_ato_administrativo=True,
        )
        inativadas = []
        # `of=("self",)` porque a Avaliação é junção externa — o Postgres recusa `FOR UPDATE` do
        # lado anulável —, e o que precisa ser travado é a Atribuição, que é a linha que `concluir`
        # também bloqueia.
        ativas = list(
            Atribuicao.objects.select_for_update(of=("self",))
            .filter(
                membro__processo=ctx.processo,
                membro__identity_subject=subject,
                inscricao=inscricao,
                ativo=True,
            )
            .select_related("membro")
        )
        com_conclusao = set(
            Avaliacao.objects.filter(
                atribuicao__in=ativas, estado=Avaliacao.Estado.CONCLUIDA
            ).values_list("atribuicao_id", flat=True)
        )
        for atribuicao in ativas:
            Atribuicao.objects.filter(pk=atribuicao.pk).update(
                ativo=False, inativado_em=ctx.now, inativado_por=actor.subject
            )
            inativadas.append(atribuicao)
            auditar(
                actor=actor,
                permissao=ctx.base.permissao,
                operation=TORNAR_INELEGIVEL,
                aggregate=atribuicao,
                now=ctx.now,
                correlation_id=correlation_id,
                reason=texto,
                idempotency_key=idempotency_key,
                com_ato_administrativo=True,
            )
        resultado = {
            "impedimento": str(impedimento.id),
            "pessoa": subject,
            "inativadas": len(inativadas),
            "concluidas_inelegiveis": sum(
                1 for atribuicao in inativadas if atribuicao.id in com_conclusao
            ),
        }
        ctx.concluir_sem_resultado(201, resultado)
        return resultado
