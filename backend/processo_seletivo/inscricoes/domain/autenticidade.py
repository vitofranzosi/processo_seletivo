"""O código que prova que um comprovante impresso não foi alterado.

O resumo de cada arquivo (D9) responde "este anexo é o que foi entregue?". Falta a outra metade:
"este **papel** é o que o sistema emitiu?". Um comprovante é um HTML impresso — qualquer pessoa
edita a página antes de imprimir e troca o nome, o protocolo ou a lista de documentos.

O código aqui é um HMAC-SHA256 sobre o que o comprovante afirma: protocolo, titular, instante do
envio, Edital, Perfil, modalidade e o resumo de cada documento. Quem confere abre a inscrição no
sistema e compara o código com o do papel — batem, o papel é fiel; não batem, alguma coisa foi
alterada.

**Por que HMAC e não um resumo simples.** Um SHA-256 do texto qualquer pessoa recalcula, e então
qualquer pessoa forja: altera o comprovante e recalcula o número. O HMAC depende de uma chave que
só o servidor tem, e por isso não pode ser reproduzido de fora.

**O que ele não é.** Não é assinatura digital com valor jurídico próprio — não há certificado, não
há ICP-Brasil, e trocar a `SECRET_KEY` invalida os códigos já emitidos. É verificação interna: dá
a quem confere um jeito de recusar um papel adulterado sem depender de olhar linha por linha.
"""

import hashlib
import hmac

from django.conf import settings

GRUPO = 4
DIGITOS = 16


def codigo_de_verificacao(inscricao, documentos) -> str:
    """`A1B2-C3D4-E5F6-7890` — dezesseis dígitos hexadecimais, em grupos de quatro.

    Dezesseis e não sessenta e quatro porque este número é **transcrito por pessoas**: alguém lê no
    papel e digita ou compara na tela. Sessenta e quatro caracteres nessa situação produzem erro de
    leitura, não segurança — e o que se defende aqui é a alteração de um comprovante por quem o
    apresenta, não um ataque de colisão com poder computacional.
    """
    return _formatar(_digest(_material(inscricao, documentos)))


def _material(inscricao, documentos) -> str:
    """O que o comprovante afirma, em ordem fixa.

    Ordem fixa porque o código precisa ser o mesmo a cada emissão: dois cálculos sobre os mesmos
    fatos em ordens diferentes dariam números diferentes, e o candidato veria o comprovante
    "mudar" ao reimprimi-lo.
    """
    partes = [
        inscricao.protocolo,
        inscricao.identity_subject,
        inscricao.submitted_at.isoformat() if inscricao.submitted_at else "",
        str(inscricao.edital_id),
        str(inscricao.profile_id),
        str(inscricao.modality_id or ""),
    ]
    partes.extend(sorted(f"{d.requirement_id}:{d.content_hash}" for d in documentos))
    return "|".join(partes)


def _digest(material: str) -> str:
    return hmac.new(settings.SECRET_KEY.encode(), material.encode(), hashlib.sha256).hexdigest()


def _formatar(digest: str) -> str:
    curto = digest[:DIGITOS].upper()
    return "-".join(curto[i : i + GRUPO] for i in range(0, DIGITOS, GRUPO))
