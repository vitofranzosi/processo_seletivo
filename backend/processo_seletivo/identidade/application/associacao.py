"""A qual identidade um endereço provado pertence — e como essa decisão é tomada.

**O CPF não participa da decisão.** Ele confirma uma correspondência que o sistema já encontrou por
outro caminho, e nada além disso (P-003). Quem chega sem participação anterior nunca o informa: a
tela que existiria para proteger seria a tela que sequestra, porque bastaria conhecer o CPF alheio e
provar um endereço próprio para ocupá-lo antes do titular (FR-049).

**A decisão acontece antes de o vínculo existir** (FR-052). Recusar o convite, errar o CPF ou
esgotar as tentativas produz identidade própria e sessão utilizável — nenhum caminho termina em
beco sem saída.
"""

import uuid
from datetime import timedelta

from django.db import IntegrityError, transaction
from django.db.models import F
from django.db.models.functions import Lower
from django.utils import timezone

from processo_seletivo.identidade.models import (
    TETO_DE_TENTATIVAS,
    VALIDADE_EM_MINUTOS,
    CandidateEmail,
    CandidateIdentity,
    DesafioDeAcesso,
    novo_subject,
)
from processo_seletivo.inscricoes.domain.pessoais import digitos
from processo_seletivo.inscricoes.models import Inscricao


def identidade_da_credencial(email_canonico: str) -> CandidateIdentity | None:
    credencial = (
        CandidateEmail.objects.filter(email_canonico=email_canonico)
        .select_related("identidade")
        .first()
    )
    return credencial.identidade if credencial else None


def correspondencia_historica(email_canonico: str) -> list[CandidateIdentity]:
    """As identidades cujas inscrições anteriores trazem aquele endereço.

    É **indício**, e não autoridade: o endereço foi digitado num formulário, pode ter erro, pode
    pertencer a terceiro e pode ter sido reciclado pelo provedor anos depois (FR-040a). O que ele
    permite é oferecer o convite; quem confirma é o CPF.
    """
    subjects = (
        Inscricao.objects.filter(email__iexact=email_canonico)
        .values_list("identity_subject", flat=True)
        .distinct()
    )
    if not subjects:
        return []
    return list(CandidateIdentity.objects.filter(subject__in=list(subjects)))


def criar_identidade_com(email_canonico: str, email_como_informado: str) -> CandidateIdentity:
    """Identidade nova, com a credencial que acabou de ser provada como principal (FR-013).

    **Perder a corrida não é erro.** Duas abas validando o código quase juntas leem, as duas, que o
    endereço ainda não tem credencial; a segunda esbarra na restrição de unicidade. Deixar a
    exceção subir devolvia erro de servidor a quem tinha acabado de acertar o código — quando o
    desfecho que ela esperava já existe. Quem chega depois entra na identidade que passou a existir.
    """
    agora = timezone.now()
    try:
        with transaction.atomic():
            identidade = CandidateIdentity.objects.create(
                subject=novo_subject(), created_at=agora
            )
            CandidateEmail.objects.create(
                id=uuid.uuid4(),
                identidade=identidade,
                email_canonico=email_canonico,
                email_como_informado=email_como_informado,
                principal=True,
                verified_at=agora,
                created_at=agora,
            )
    except IntegrityError:
        vencedora = identidade_da_credencial(email_canonico)
        if vencedora is None:
            # A violação não foi a que se esperava: não há credencial para aquele endereço, então
            # esconder a exceção seria esconder outro defeito.
            raise
        return vencedora
    return identidade


def associar_credencial(
    identidade: CandidateIdentity, email_canonico: str, email_como_informado: str
) -> CandidateEmail:
    agora = timezone.now()
    primeira = not identidade.credenciais.exists()
    return CandidateEmail.objects.create(
        id=uuid.uuid4(),
        identidade=identidade,
        email_canonico=email_canonico,
        email_como_informado=email_como_informado,
        principal=primeira,
        verified_at=agora,
        created_at=agora,
    )


def abrir_reconciliacao(desafio: DesafioDeAcesso, alvos: list[CandidateIdentity]) -> None:
    """O desafio consumido passa a portar a decisão pendente (FR-052a, D-016).

    A contagem de tentativas de CPF fica aqui, e não na sessão — que uma aba nova zeraria — e nunca
    na identidade alvo, o que deixaria um terceiro esgotar as tentativas e impedir o titular
    legítimo de reconciliar.

    Quando há mais de um alvo, nenhum é anotado: o CPF é que desempata, e anotar um deles agora
    seria escolher antes de saber (FR-051).
    """
    DesafioDeAcesso.objects.filter(pk=desafio.pk).update(
        reconciliacao_ate=timezone.now() + timedelta(minutes=VALIDADE_EM_MINUTOS),
        reconciliacao_alvo=alvos[0] if len(alvos) == 1 else None,
    )
    desafio.refresh_from_db()


def reconciliacao_pendente(desafio: DesafioDeAcesso | None) -> bool:
    return bool(
        desafio
        and desafio.reconciliacao_ate
        and desafio.reconciliacao_ate > timezone.now()
        and desafio.tentativas_cpf < TETO_DE_TENTATIVAS
    )


def confirmar_cpf(desafio: DesafioDeAcesso, cpf: str) -> CandidateIdentity | None:
    """Confere o CPF contra as identidades correspondentes — e conta a tentativa de qualquer jeito.

    Contar antes de decidir é o que impede a diferença de comportamento entre acerto e erro virar
    informação. E a contagem incide sobre **quem tenta**, através do desafio, nunca sobre o alvo
    (FR-052c).
    """
    # Reserva condicional, e não `valor lido + 1`: o segundo perde a corrida do mesmo jeito que o
    # contador de tentativas do código perdia — duas requisições que leem `tentativas_cpf = 4`
    # gravam as duas `5`, e a quinta e a sexta tentativas custam uma só. Quem não reserva não
    # confere CPF nenhum.
    reservada = DesafioDeAcesso.objects.filter(
        pk=desafio.pk,
        tentativas_cpf__lt=TETO_DE_TENTATIVAS,
        reconciliacao_ate__gt=timezone.now(),
    ).update(tentativas_cpf=F("tentativas_cpf") + 1)
    if reservada != 1:
        return None
    desafio.refresh_from_db()

    informado = digitos(cpf)
    if len(informado) != 11:
        return None

    # O alvo anotado quando o convite abriu **decide**, e não apenas informa. Refazer a busca
    # deixava o conjunto de candidatas mudar sob um desafio já aberto — uma inscrição nova com
    # aquele endereço, criada noutra sessão, e a identidade reconciliada podia não ser a que o
    # convite anunciou. Quando havia mais de uma candidata, nenhum alvo foi anotado, porque
    # escolher ali seria escolher antes de saber: aí o CPF desempata entre as candidatas de agora,
    # que é o que a FR-051 pede.
    if desafio.reconciliacao_alvo_id is not None:
        alvo = desafio.reconciliacao_alvo
        return alvo if alvo.cpf_normalizado == informado else None

    candidatas = correspondencia_historica(desafio.email_canonico)
    conferem = [
        identidade for identidade in candidatas if identidade.cpf_normalizado == informado
    ]
    if len(conferem) != 1:
        return None
    return conferem[0]


def encerrar_reconciliacao(desafio: DesafioDeAcesso) -> None:
    DesafioDeAcesso.objects.filter(pk=desafio.pk).update(reconciliacao_ate=None)


def esta_vazia(identidade: CandidateIdentity) -> bool:
    return not Inscricao.objects.filter(identity_subject=identidade.subject).exists()


def credencial_com_correspondencia(identidade: CandidateIdentity) -> CandidateEmail | None:
    """A credencial desta identidade que aparece em inscrição de **outra** — se houver.

    É o que torna a retomada oferecível: sem endereço com correspondência, não há o que retomar.
    """
    credenciais = list(identidade.credenciais.all())
    if not credenciais:
        return None
    # Uma consulta para todos os endereços, e não uma por credencial: `Lower` sobre a coluna é o
    # que permite comparar em conjunto, já que `iexact` não aceita lista.
    enderecos = {credencial.email_canonico for credencial in credenciais}
    subjects = set(
        Inscricao.objects.annotate(canonico=Lower("email"))
        .filter(canonico__in=enderecos)
        .exclude(identity_subject=identidade.subject)
        .values_list("identity_subject", flat=True)
        .distinct()
    )
    if not subjects:
        return None
    com_correspondencia = set(
        Inscricao.objects.annotate(canonico=Lower("email"))
        .filter(canonico__in=enderecos, identity_subject__in=subjects)
        .values_list("canonico", flat=True)
        .distinct()
    )
    for credencial in credenciais:
        if credencial.email_canonico in com_correspondencia:
            return credencial
    return None


def retomar(*, vazia: CandidateIdentity, destino: CandidateIdentity) -> bool:
    """Move todas as credenciais e descarta a identidade vazia — numa operação só (FR-054, FR-055).

    **Por que atômica, e por que sob bloqueio.** Verificar "está vazia" e descartar depois deixaria
    um rascunho nascer no intervalo, e ele ficaria órfão de uma identidade que deixou de existir —
    `Inscricao` não referencia a identidade por chave estrangeira, então nada além deste bloqueio
    impede isso. A abertura de rascunho toma a mesma linha (`rascunho._travar_a_identidade`).

    **Por que todas as credenciais.** Cada uma já foi provada por desafio, e a identidade não tem
    inscrição alguma: mover só a que carregava a correspondência perderia o que a pessoa comprovou,
    sem ganho nenhum de segurança.

    Devolve `False` quando a premissa deixou de valer dentro do bloqueio — que é exatamente o caso
    que o bloqueio existe para pegar.
    """
    with transaction.atomic():
        travada = (
            CandidateIdentity.objects.select_for_update().filter(pk=vazia.pk).first()
        )
        if travada is None or not esta_vazia(travada):
            return False
        principal_do_destino = destino.credenciais.filter(principal=True).exists()
        travada.credenciais.update(identidade=destino, principal=False)
        if not principal_do_destino:
            primeira = destino.credenciais.order_by("created_at").first()
            if primeira is not None:
                destino.credenciais.filter(pk=primeira.pk).update(principal=True)
        travada.delete()
    return True
