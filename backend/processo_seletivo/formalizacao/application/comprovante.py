"""O comprovante da verificação: assinado pelo servidor, vale 15 minutos (117, D-024).

**Prova que a verificação aconteceu, e não autoriza nada.** O download revalida o papel, a
designação e cada pessoa pelo predicado único, relê todos os arquivos e recompõe o resumo: o
comprovante só diz *qual* verificação o operador viu, para que o servidor confira que o pacote é
exatamente aquele.

**Assinado, e não resumido** (D-024): um SHA-256 dos dados prova consistência, e não origem — quem
reconstruísse os valores fabricaria o resumo e pularia a verificação. `django.core.signing` assina
com HMAC sobre a chave do sistema, com sal próprio da feature, e tem validade por `max_age`. Não há
tabela, e por isso o comprovante pode ser usado mais de uma vez pelo mesmo ator dentro da validade:
cada uso é uma exportação registrada, como clicar de novo.

**Assinado, e não cifrado**: quem o tem lê os campos. Por isso só há identificadores opacos, códigos
e o resumo — nenhum nome, CPF ou nome de arquivo —, e ele vai no corpo do POST, nunca na URL.
"""

import hashlib
import json

from django.core import signing
from django.utils import timezone

from processo_seletivo.formalizacao.domain import nomes
from processo_seletivo.shared.api.problems import DomainError


def resumo_canonico(conteudo):
    """O SHA-256 da forma canônica do conteúdo verificado: chaves ordenadas, sem espaço."""
    texto = json.dumps(conteudo, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(texto.encode()).hexdigest()


def emitir(actor, verificacao):
    """O comprovante de uma verificação concluída (FR-3689a)."""
    payload = {
        "v": nomes.VERSAO_DO_COMPROVANTE,
        "sujeito": actor.subject,
        "unidade": actor.institution_scope,
        "edital": str(verificacao.edital.id),
        "designacao": str(verificacao.designacao.id),
        "alcance": verificacao.alcance,
        "perfil": verificacao.perfil_id or "",
        "pessoas": sorted(verificacao.pedidas),
        "definicao": str(verificacao.definicao.id),
        "resultado": verificacao.resultado,
        "incluidas": len(verificacao.incluidas),
        "total": len(verificacao.pessoas),
        "resumo": verificacao.resumo,
        "emitido_em": timezone.now().isoformat(),
    }
    return signing.dumps(payload, salt=nomes.SAL_DO_COMPROVANTE, compress=True)


def invalida():
    return DomainError(nomes.VERIFICACAO_INVALIDA, nomes.INVALIDA, 409)


def conferir(actor, token):
    """O conteúdo do comprovante, ou a recusa — **antes** de qualquer arquivo ser lido.

    Assinatura inválida (adulterado ou fabricado sem a chave, ou com outro sal) e comprovante de
    outro ator ou de outra unidade são *verificação inválida*; passado da validade, *verificação
    expirada*. O expirado é conferido primeiro porque `SignatureExpired` é um caso de assinatura
    inválida no framework, e a frase dele é outra.
    """
    try:
        payload = signing.loads(
            token or "",
            salt=nomes.SAL_DO_COMPROVANTE,
            max_age=nomes.VALIDADE_DO_COMPROVANTE,
        )
    except signing.SignatureExpired as erro:
        raise DomainError(nomes.VERIFICACAO_EXPIRADA, nomes.EXPIRADA, 409) from erro
    except (signing.BadSignature, ValueError, TypeError) as erro:
        raise invalida() from erro
    if not isinstance(payload, dict) or payload.get("v") != nomes.VERSAO_DO_COMPROVANTE:
        raise invalida()
    if payload.get("sujeito") != actor.subject or payload.get("unidade") != actor.institution_scope:
        raise invalida()
    if payload.get("alcance") not in (nomes.SELECAO, nomes.RECORTE):
        raise invalida()
    return payload
