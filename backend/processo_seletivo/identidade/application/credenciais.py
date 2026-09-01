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

from processo_seletivo.identidade.models import CandidateIdentity
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
            recusado["cpf"] = "Este CPF não existe. Confira os números digitados."
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
