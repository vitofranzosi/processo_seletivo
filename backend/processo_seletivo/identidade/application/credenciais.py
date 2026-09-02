"""O núcleo mínimo da identidade: o nome e o CPF que a Inscrição exige.

**Por que a identidade os carrega.** A abertura de rascunho os copia (`inscricoes/application/
rascunho.py`), e o nome vai no comprovante — é por ele que a conferência documental acontece. Um
provedor que entregue só e-mail quebraria a jornada da `009` na primeira inscrição de todo candidato
novo (FR-004).

**Pedidos uma vez.** Quem veio da `009` nunca os informa: a reconciliação já os trouxe. Quem chega
novo informa na primeira inscrição, e não antes — pedir dado pessoal a quem só quer olhar a vitrine
é cobrar antes de entregar (FR-005).

**E uma vez não é para sempre.** Erro de digitação e alteração de nome são eventos normais, e a
`009` permitia redigitar os dois a cada identificação: uma identidade persistente não pode ser mais
rígida do que o estado que ela substitui (FR-008).
"""

from django.db import transaction
from django.utils import timezone

from processo_seletivo.auditoria.models import RegistroAuditoria
from processo_seletivo.identidade.application.associacao import (
    associar_credencial,
    identidade_da_credencial,
)
from processo_seletivo.identidade.models import CandidateEmail, CandidateIdentity
from processo_seletivo.inscricoes.domain.pessoais import cpf_valido, digitos
from processo_seletivo.inscricoes.models import Inscricao

LIMITE_DO_NOME = 255


def falta_o_nucleo(identidade: CandidateIdentity) -> bool:
    return not identidade.nome or not identidade.cpf_normalizado


def cpf_congelado(identidade: CandidateIdentity) -> bool:
    """A partir da primeira inscrição enviada, o CPF é peça de ato administrativo (FR-008).

    Corrigi-lo passa a ser ato institucional, fora desta feature — e não porque o dado virou
    sagrado, mas porque ele já constou de um comprovante que alguém tem em mãos.
    """
    return Inscricao.objects.filter(
        identity_subject=identidade.subject, status=Inscricao.Status.SUBMETIDA
    ).exists()


def recusas(dados: dict, *, cpf_editavel: bool) -> dict:
    """As recusas que a pessoa lê — as mesmas da `009`, e pelos mesmos motivos.

    O comprimento entra aqui porque sem ele o campo grande demais atravessa a aplicação inteira e
    estoura na gravação. E o nome completo é exigido porque ele vai no comprovante: um primeiro nome
    sozinho obriga a conferência manual que esta jornada existe para tirar.
    """
    recusado = {}
    nome = dados.get("nome", "").strip()
    if not nome:
        recusado["nome"] = "Informe seu nome completo."
    elif len(nome) > LIMITE_DO_NOME:
        recusado["nome"] = f"O nome pode ter no máximo {LIMITE_DO_NOME} caracteres."
    elif len([parte for parte in nome.split() if len(parte) > 1]) < 2:
        recusado["nome"] = "Informe o nome completo, com sobrenome."

    if cpf_editavel:
        cpf = dados.get("cpf", "")
        if len(digitos(cpf)) != 11:
            recusado["cpf"] = "Informe um CPF com 11 dígitos."
        elif not cpf_valido(cpf):
            # Contar onze dígitos aceitava qualquer número inventado — e um CPF digitado errado
            # produz uma inscrição que a equipe não consegue conferir contra documento nenhum.
            #
            # A frase diz o que o sistema **confere**, e não mais do que isso: o cálculo é o dos
            # dígitos verificadores, e nenhuma consulta à Receita acontece aqui. "Este CPF não
            # existe" soava como afirmação sobre a pessoa, e era a resposta que ela lia depois de
            # digitar um número que existe e que ela errou por um dígito.
            recusado["cpf"] = "Estes números não formam um CPF válido. Confira o que digitou."
    return recusado


def gravar_nucleo(identidade: CandidateIdentity, *, nome: str, cpf: str = "") -> CandidateIdentity:
    """Grava nome e — quando ainda editável — CPF.

    Não toca em inscrição alguma: os rascunhos abertos leem da identidade a cada requisição, e as
    enviadas congelaram o que constava no ato (FR-014).
    """
    campos = {"nome": nome.strip()}
    if cpf and not cpf_congelado(identidade):
        campos["cpf_normalizado"] = digitos(cpf)
    CandidateIdentity.objects.filter(pk=identidade.pk).update(**campos)
    identidade.refresh_from_db()
    return identidade


# ---------------------------------------------------------------------------
# As credenciais da identidade: acrescentar, escolher a principal, remover.
# ---------------------------------------------------------------------------


def adicionar(
    identidade, *, email_canonico: str, email_como_informado: str, correlation_id: str = ""
) -> CandidateEmail:
    """Liga um endereço já provado à identidade, **e registra o ato junto** (FR-016, FR-089).

    Não pede CPF: quem já está dentro não precisa provar de novo quem é — precisa provar que
    controla **aquela** caixa, e isso o desafio já fez.

    O registro fica **dentro** da mesma transação, e não depois dela. A primeira versão gravava a
    credencial, comitava, e só então escrevia na trilha: uma falha entre as duas deixaria a
    credencial existindo sem evento nenhum que a explicasse. É o padrão que a `009` já segue —
    `command_context()` abre a transação e `record_event` é chamado lá dentro — e sair do auxiliar
    fez perder, sem anunciar, a garantia que vinha com ele (Princípio IV).
    """
    with transaction.atomic():
        credencial = associar_credencial(identidade, email_canonico, email_como_informado)
        registrar_ato(identidade, operacao="ASSOCIAR_CREDENCIAL", correlation_id=correlation_id)
    return credencial


def pertence_a_outra(identidade, email_canonico: str) -> bool:
    dona = identidade_da_credencial(email_canonico)
    return dona is not None and dona.pk != identidade.pk


def tornar_principal(identidade, credencial_id) -> bool:
    """Troca qual credencial alimenta a Inscrição (FR-013).

    Numa transação só: entre baixar a antiga e levantar a nova existe um instante em que a
    identidade não teria principal — e é justamente o estado que a restrição parcial de banco
    recusa. Fazer as duas coisas juntas é o que impede a troca de falhar pela metade.
    """
    with transaction.atomic():
        nova = identidade.credenciais.select_for_update().filter(pk=credencial_id).first()
        if nova is None:
            return False
        identidade.credenciais.filter(principal=True).update(principal=False)
        identidade.credenciais.filter(pk=nova.pk).update(principal=True)
    return True


# Os três desfechos de uma remoção, e eles não se confundem. A primeira versão devolvia um
# booleano, e a view traduzia qualquer recusa em "você não pode remover seu último e-mail" — quem
# pedisse a remoção de credencial alheia lia isso, sobre algo que não é dela. Nada era apagado, mas
# a resposta descrevia errado o que aconteceu, e numa investigação apontaria para o lado errado.
REMOVIDA = "removida"
E_A_ULTIMA = "e_a_ultima"
NAO_E_SUA = "nao_e_sua"


def remover(identidade, credencial_id, *, correlation_id: str = "") -> str:
    """Remove uma credencial — nunca a última, e nunca deixando a identidade sem principal.

    Remover a última é apagar o próprio acesso (FR-018), e nenhuma tela deveria oferecer isso. A
    conferência é do servidor porque esconder o botão não é fronteira de segurança.

    E **não toca inscrição alguma** (FR-019): o que foi submetido registrou o endereço que constava
    no ato, e credencial é como se entra, não o que se enviou.

    O registro do ato fica dentro da mesma transação, pela razão de `adicionar`.
    """
    with transaction.atomic():
        credenciais = list(identidade.credenciais.select_for_update())
        alvo = next((item for item in credenciais if str(item.pk) == str(credencial_id)), None)
        if alvo is None:
            # Perguntado **antes** da contagem: não ser sua é uma recusa, ser a última é outra.
            return NAO_E_SUA
        if len(credenciais) <= 1:
            return E_A_ULTIMA
        era_principal = alvo.principal
        alvo.delete()
        if era_principal:
            # A identidade não fica sem principal: a mais antiga das que restam assume.
            herdeira = identidade.credenciais.order_by("created_at").first()
            identidade.credenciais.filter(pk=herdeira.pk).update(principal=True)
        registrar_ato(identidade, operacao="REMOVER_CREDENCIAL", correlation_id=correlation_id)
    return REMOVIDA


def registrar_ato(identidade, *, operacao: str, correlation_id: str = "") -> None:
    """Associação e remoção de credencial entram na trilha existente (FR-089).

    **Sem `record_event`, e o motivo é honesto**: aquele auxiliar lê `status` e `revision` do
    agregado, e a identidade do candidato não tem nem um nem outro — ela não é máquina de estados.
    Acrescentar os dois campos só para caber no auxiliar seria modelar para a ferramenta.

    **`institution_scope` fica vazio**, e a consequência está declarada em D-012: este evento não
    aparece na consulta administrativa de auditoria, que filtra por escopo. Ele não pertence a
    Edital nenhum. É investigável por inspeção direta da trilha, que é append-only e preserva ator,
    ato, momento e correlação — e essa é a decisão, tomada de frente, e não um campo em branco
    descoberto depois.
    """
    RegistroAuditoria.objects.create(
        occurred_at=timezone.now(),
        actor_subject=identidade.subject,
        permission="",
        institution_scope="",
        operation=operacao,
        aggregate_type=CandidateIdentity.__name__,
        aggregate_id=identidade.pk,
        correlation_id=correlation_id,
    )
