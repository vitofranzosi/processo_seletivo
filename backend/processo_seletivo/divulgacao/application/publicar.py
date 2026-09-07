"""O comando de publicar um resultado — e a ordem exata em que ele faz as coisas.

```text
require_permission(actor, "resultado:publicar")          # fora da transação
  ↓
transação
  ↓
ProcessoSeletivo.objects.select_for_update()             # serializa com emitir_ordem
  ↓
reserve(operation="resultado:publicar:<ato_id>")         # repetido → desfecho anterior
  ↓
publicabilidade                                          # três recusas nomeadas
  ↓
compor projeção  →  confirmacao_da_previa confere?       # 409 se não
  ↓
gravar PublicacaoResultado + SituacaoDivulgada + documento
  ↓
auditar(...)  →  finish(...)
```

**O bloqueio do `ProcessoSeletivo` não é ornamento.** `emitir_ordem` roda dentro de
`comando_de_comissao`, que faz `select_for_update` na mesma linha e a mantém por toda a transação.
Sem tomar a **mesma** linha, publicar e emitir correm em paralelo: a publicação afere que o ato é
vigente, a emissão grava o sucessor, e a publicação grava a divulgação de um ato que deixou de ser
vigente entre a aferição e a gravação. Revalidar dentro da transação **não resolve** — a leitura é
consistente com o instante em que ocorreu, e o problema é o que acontece depois dela. Tomar a linha
antes de aferir serializa os dois comandos, e o perdedor encontra o mundo já mudado (T-005).

**`require_permission` corre fora da transação**, e por isso `reserve` pode vir antes de executar —
é o padrão de `processos/application/commands.py`, e não o de `comando_de_comissao`, que reserva
depois porque a base dele é contextual (T-006).

**Concorrência em quatro frentes**, cada uma para um caso que as outras não pegam: a idempotência
responde ao **mesmo** pedido repetido; `uq_publicacao_por_ato_natureza` responde a **dois pedidos
distintos** sobre o mesmo ato, que é o caso das duas abas com chaves diferentes; a assinatura da
prévia responde ao mundo que mudou entre ler e confirmar; e o bloqueio responde à emissão
concorrente.
"""

from django.db import IntegrityError

from processo_seletivo.avaliacoes.application.trilha import auditar
from processo_seletivo.classificacao.application.selectors import ato_por_id
from processo_seletivo.divulgacao.application.selectors import vigente_do_marco
from processo_seletivo.divulgacao.domain.conteudo import compor, conteudo_divulgado
from processo_seletivo.divulgacao.domain.publicabilidade import aferir
from processo_seletivo.divulgacao.models import (
    DocumentoDoResultado,
    Natureza,
    PublicacaoResultado,
    SituacaoDivulgada,
)
from processo_seletivo.processos.models import Edital, ProcessoSeletivo
from processo_seletivo.publicacoes.domain.autoridades import escolher
from processo_seletivo.seguranca.application.authorization import require_permission
from processo_seletivo.shared.api.problems import DomainError
from processo_seletivo.shared.application.commands import command_context
from processo_seletivo.shared.canonical import canonical_bytes, canonical_sha256
from processo_seletivo.shared.idempotency import finish, reserve

PERMISSAO = "resultado:publicar"
PUBLICAR = "RESULTADO_PUBLICAR"


def assinatura_da_previa(*, ato, publicacao_anterior, projecao):
    """O resumo que detecta que o mundo mudou entre ler e confirmar (FR-031, T-005).

    **Cobre `{ato, publicacao_anterior, projecao}` e não contém o instante.** Ele é o outro resumo:
    `conteudo_publico_hash` cobre o conteúdo final, já com `publicado_em`, e existe para provar
    depois que o que se lê é o que foi divulgado. Calcular um só faria a confirmação nunca conferir
    — o instante definitivo da publicação só existe no POST.

    **`publicacao_anterior` está dentro da assinatura**, e é o que cobre o caso em que outra pessoa
    publica o mesmo marco entre a prévia e a confirmação: a cadeia mudou, a posição da nova
    publicação mudou, e a confirmação é recusada em vez de gravar uma sucessão de algo que já não é
    a ponta.

    Ficam de fora `natureza` e `autoridade`: são escolha do operador, submetidas no mesmo pedido, e
    não têm como ficar obsoletas — não existe leitura anterior delas a comparar. São **validadas**
    como entrada, não assinadas.
    """
    return canonical_sha256(
        {
            "ato": str(ato.id),
            "publicacaoAnterior": (
                str(publicacao_anterior.id) if publicacao_anterior is not None else None
            ),
            "projecao": projecao["posicoes"],
        }
    )


def publicar_resultado(
    *,
    actor,
    processo_id,
    edital_id,
    marco_id,
    ato_id,
    natureza,
    autoridade,
    confirmacao_da_previa,
    idempotency_key,
    correlation_id,
    declaracao_de_encerramento="",
):
    """Divulga um ato de ordenação vigente, congelando o que foi divulgado."""
    require_permission(actor, PERMISSAO)
    with command_context() as agora:
        processo = (
            ProcessoSeletivo.objects.select_for_update()
            .filter(pk=processo_id, institution_scope=actor.institution_scope)
            .first()
        )
        if processo is None:
            raise _nao_encontrado()
        edital = Edital.objects.filter(
            pk=edital_id, processo=processo, institution_scope=processo.institution_scope
        ).first()
        if edital is None:
            raise _nao_encontrado()
        ato = ato_por_id(edital=edital, marco_id=marco_id, ato_id=ato_id)
        if ato is None:
            raise _nao_encontrado()

        reserva = reserve(
            actor=actor,
            operation=f"{PERMISSAO}:{ato_id}",
            key=idempotency_key,
            payload={
                "ato": str(ato_id),
                "natureza": str(natureza or ""),
                "autoridade": str(autoridade or ""),
                "confirmacao": confirmacao_da_previa or "",
                # **A declaração faz parte do pedido** (FR-098). Sem ela na reserva, a mesma chave
                # reenviada com outro fundamento devolveria a primeira publicação em silêncio — e a
                # afirmação que ficou gravada não seria a que a pessoa acabou de escrever.
                "declaracao": (declaracao_de_encerramento or "").strip(),
            },
        )
        if reserva.result_id:
            # A repetição devolve o desfecho que o primeiro pedido declarou, e não uma leitura do
            # mundo depois dele — inclusive quando esse mundo já mudou (FR-030).
            return PublicacaoResultado.objects.get(pk=reserva.result_id)

        assinante = escolher(autoridade)
        if assinante is None:
            raise DomainError(
                "publication_authority_required",
                "Escolha a autoridade signatária entre as do catálogo.",
                422,
                campo="autoridade",
            )
        if natureza not in Natureza.values:
            raise DomainError(
                "publication_authority_required"
                if natureza is None
                else "publication_nature_regresses",
                "Escolha a natureza do resultado a divulgar.",
                422,
                campo="natureza",
            )

        publicabilidade = aferir(
            edital=edital, marco_id=marco_id, ato=ato, at=agora, natureza=natureza
        )
        if not publicabilidade.publicavel:
            raise DomainError(
                publicabilidade.codigo,
                publicabilidade.mensagem,
                publicabilidade.status,
            )

        anterior = vigente_do_marco(edital=edital, marco_id=marco_id)
        if anterior is not None and anterior.natureza == Natureza.DEFINITIVA:
            if natureza == Natureza.PRELIMINAR:
                raise DomainError(
                    "publication_nature_regresses",
                    "Um resultado preliminar não sucede um definitivo: a ordem entre as naturezas "
                    "tem sentido único.",
                    422,
                    campo="natureza",
                )

        projecao = compor(ato)
        esperada = assinatura_da_previa(ato=ato, publicacao_anterior=anterior, projecao=projecao)
        if (confirmacao_da_previa or "") != esperada:
            # A conferência **recalcula** com a projeção composta agora e com o predecessor vigente
            # **agora**. Não se usa o predecessor que veio no formulário: ele é justamente o que
            # pode ter envelhecido, e aceitá-lo faria a recusa vir da constraint de raiz, com outra
            # mensagem, para o mesmo fato.
            raise DomainError(
                "publication_preview_stale",
                "A projeção ou a cadeia mudaram entre a prévia e a confirmação; confira o que "
                "será divulgado antes de tentar de novo.",
                409,
                campo="confirmacao_da_previa",
            )

        declaracao = _declaracao_exigida(
            edital=edital, marco_id=marco_id, natureza=natureza, texto=declaracao_de_encerramento
        )

        conteudo = conteudo_divulgado(
            projecao,
            natureza=natureza,
            publicado_em=agora,
            signatario=assinante,
            # **A causa é congelada no ato de publicar** (FR-088). Divulgação que sucede outra e
            # nasce de decisão de recurso é apresentada por ela — na página e no documento, que
            # leem os mesmos bytes. Derivá-la na leitura faria uma decisão posterior reescrever a
            # frase de um ato já praticado.
            retificacao=_causa_da_retificacao(ato, anterior),
        )
        bytes_do_conteudo = canonical_bytes(conteudo)
        try:
            publicacao = PublicacaoResultado.objects.create(
                edital=edital,
                ato=ato,
                perfil_id=ato.perfil_id,
                marco_id=ato.marco_id,
                natureza=natureza,
                publicacao_anterior=anterior,
                conteudo_publico=bytes_do_conteudo,
                conteudo_publico_hash=canonical_sha256(conteudo),
                publicado_por=actor.subject,
                publicado_em=agora,
                signatario_id=assinante.identificador,
                signatario_nome=assinante.nome,
                signatario_cargo=assinante.cargo,
                prazo_encerrado_declarado_em=agora if declaracao else None,
                prazo_encerrado_declarado_por=actor.subject if declaracao else "",
                prazo_encerrado_fundamento=declaracao,
            )
        except IntegrityError as exc:
            # A cobertura dupla e deliberada: a idempotência responde ao **mesmo** pedido
            # repetido; a constraint responde a **dois pedidos distintos** sobre o mesmo ato e a
            # mesma natureza, que é o caso das duas abas com chaves diferentes (FR-039).
            raise DomainError(
                "publication_already_exists",
                "Este ato já foi divulgado nesta natureza.",
                409,
            ) from exc

        SituacaoDivulgada.objects.bulk_create(
            SituacaoDivulgada(
                publicacao=publicacao,
                inscricao_id=item["inscricao_id"],
                situacao=item["situacao"],
                posicao=item["posicao"],
                compartilhada=item["compartilhada"],
                pontuacao=item["pontuacao"],
                motivo=item["motivo"],
            )
            for item in projecao["situacoes"]
        )
        _gravar_documento(publicacao, conteudo)

        auditar(
            actor=actor,
            permissao=PERMISSAO,
            operation=PUBLICAR,
            aggregate=publicacao,
            now=agora,
            correlation_id=correlation_id,
            # Sem `com_ato_administrativo`: publicar não exige motivo — a sucessão já carrega o dela
            # no ato de origem (FR-067).
            reason=_narrativa_do_ato(conteudo, ato, anterior),
            idempotency_key=idempotency_key,
        )
        finish(reserva, publicacao, 201)
        return publicacao


def _narrativa_do_ato(conteudo, ato, anterior):
    """O que a trilha guarda por extenso — incluindo **a versão normativa que o ato citava**.

    A FR-066 pede a versão na trilha, e a SC-017 a cobra pelo nome. O `RegistroAuditoria` não tem
    coluna para ela, e criar uma seria acrescentar campo a uma tabela append-only compartilhada por
    todas as features por necessidade de uma só. `reason` é o texto livre que descreve o ato — é
    onde a 013 e a 015 já escrevem a narrativa deles —, e é por ele que a versão chega à trilha
    sem log paralelo (FR-067).

    A sucessão também é dita aqui: ela é o que distingue divulgar pela primeira vez de substituir o
    que já estava divulgado, e quem lê a trilha precisa dos dois.
    """
    partes = [
        f"{conteudo['cabecalho']['titulo']} divulgado",
        f"sob a versão normativa {ato.versao_id}",
    ]
    if anterior is not None:
        partes.append(f"sucedendo a publicação {anterior.id}")
    return ", ".join(partes) + "."


def _declaracao_exigida(*, edital, marco_id, natureza, texto):
    """A declaração expressa, exigida **somente** onde não há janela computável (FR-085, FR-086).

    Onde o Edital declara a janela, o sistema verifica: pedir a declaração ali seria pedir à pessoa
    que respondesse pelo que a máquina sabe — e reintroduziria, com mais passos, a afirmação sem
    lastro que o E2E17-005 registrou. Por isso ela é **recusada** quando há janela, e não apenas
    ignorada: aceitar em silêncio ensinaria a preenchê-la sempre.

    Enquanto o degrau 8 não existir, nenhum marco tem janela computável — e a declaração é sempre
    exigida na definitiva. É a degradação declarada, e não um estado transitório escondido.
    """
    from processo_seletivo.divulgacao.domain.publicabilidade import (
        DECLARACAO_EXIGIDA,
        DECLARACAO_RECUSADA,
        MENSAGENS,
        STATUS,
    )
    from processo_seletivo.recursos.domain.janela import janela_declarada

    texto = (texto or "").strip()
    if natureza != Natureza.DEFINITIVA:
        # Fora da definitiva a declaração não tem função: o preliminar não afirma que o prazo
        # acabou. Aceitá-la aqui gravaria uma afirmação sem objeto.
        return ""

    computavel = janela_declarada(edital=edital, marco_id=marco_id) is not None
    if computavel and texto:
        raise DomainError(
            DECLARACAO_RECUSADA, MENSAGENS[DECLARACAO_RECUSADA], STATUS[DECLARACAO_RECUSADA]
        )
    if not computavel and not texto:
        raise DomainError(
            DECLARACAO_EXIGIDA, MENSAGENS[DECLARACAO_EXIGIDA], STATUS[DECLARACAO_EXIGIDA]
        )
    return "" if computavel else texto


def _causa_da_retificacao(ato, anterior):
    """A decisão de recurso que motivou esta divulgação sucessora — serializável, ou `None`."""
    if anterior is None:
        return None
    from processo_seletivo.recursos.application.selectors import causa_da_correcao

    causa = causa_da_correcao(ato)
    if causa is None:
        return None
    return {"recurso": causa["recurso"], "quando": causa["quando"].isoformat()}


def _gravar_documento(publicacao, conteudo):
    """O documento oficial, derivado **do conteúdo já composto** e gravado uma vez (FR-062).

    Deriva dos mesmos bytes que a página, e é por isso que os rótulos dos dois conferem (FR-064).
    Gerá-lo de novo na leitura faria uma Retificação posterior alcançar um ato já praticado.
    """
    import hashlib

    from processo_seletivo.divulgacao.infrastructure.documento import render_resultado_pdf

    arquivo = render_resultado_pdf(conteudo)
    DocumentoDoResultado.objects.create(
        publicacao=publicacao,
        bytes=arquivo,
        documento_hash=hashlib.sha256(arquivo).hexdigest(),
    )


def _nao_encontrado():
    """A mesma resposta para tudo que o ator não alcança: quem não alcança não descobre o quê."""
    return DomainError("not_found", "Recurso não encontrado.", 404)


__all__ = ["PERMISSAO", "PUBLICAR", "assinatura_da_previa", "publicar_resultado"]
