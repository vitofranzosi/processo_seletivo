"""Para onde vai a mensagem dirigida a uma inscrição: a credencial principal, ou o endereço gravado.

**A credencial vem primeiro porque ela é provada.** O endereço gravado na Inscrição é indício
histórico — a `010` o diz com todas as letras —, e a pessoa pode ter trocado de caixa desde então.
Ele continua sendo a saída quando não há credencial, que é o caso de quem se inscreveu antes de o
portal existir.

**Num lugar só, e não em cada remetente** (066, data-model §3). A regra nasceu na comunicação da
convocação (`019`); o aviso precisa exatamente dela, e duas cópias divergiriam no primeiro ajuste —
uma pessoa receberia a convocação num endereço e o aviso da mesma chamada em outro.
"""

from processo_seletivo.identidade.models import CandidateEmail


def endereco_da_inscricao(inscricao):
    """O endereço de uma inscrição, ou `""` quando não há nenhum."""
    credencial = (
        CandidateEmail.objects.filter(
            identidade__subject=inscricao.identity_subject, principal=True
        )
        .values_list("email_canonico", flat=True)
        .first()
    )
    return credencial or inscricao.email or ""


def enderecos_das_inscricoes(inscricoes):
    """`{inscricao_id: endereço}` para muitas inscrições, em **uma** consulta às credenciais.

    É a mesma regra de `endereco_da_inscricao`, lida em lote: um aviso de quinhentas pessoas que
    perguntasse uma a uma pagaria quinhentas consultas na prévia e outras quinhentas na confirmação.
    """
    inscricoes = list(inscricoes)
    sujeitos = {inscricao.identity_subject for inscricao in inscricoes}
    credenciais = dict(
        CandidateEmail.objects.filter(identidade__subject__in=sujeitos, principal=True).values_list(
            "identidade__subject", "email_canonico"
        )
    )
    return {
        inscricao.id: credenciais.get(inscricao.identity_subject) or inscricao.email or ""
        for inscricao in inscricoes
    }


__all__ = ["endereco_da_inscricao", "enderecos_das_inscricoes"]
