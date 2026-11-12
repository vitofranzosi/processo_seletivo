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
from processo_seletivo.divulgacao.domain.publicabilidade import aferir, natureza_regride
from processo_seletivo.divulgacao.models import (
    DocumentoDoResultado,
    Natureza,
    PublicacaoResultado,
    SituacaoDivulgada,
)
from processo_seletivo.editais.domain.recortes import exigir_recorte_operacional
from processo_seletivo.processos.models import Edital, ProcessoSeletivo
from processo_seletivo.publicacoes.application.contexto_do_ato import (
    colunas_da_unidade,
    contexto_do_ato,
)
from processo_seletivo.publicacoes.application.selectors import effective_version
from processo_seletivo.seguranca.application.authorization import require_permission
from processo_seletivo.shared.api.problems import DomainError
from processo_seletivo.shared.application.commands import command_context
from processo_seletivo.shared.canonical import canonical_bytes, canonical_sha256
from processo_seletivo.shared.idempotency import finish, reserve

PERMISSAO = "resultado:publicar"
PUBLICAR = "RESULTADO_PUBLICAR"


def assinatura_da_previa(*, ato, publicacao_anterior, projecao, acompanhantes=()):
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

    **As listas sem concorrente que vão junto entram na assinatura** (155, FR-6330, R-006): cada
    uma com o seu ato e a publicação vigente dela. Uma ordem vazia emitida, ou publicada à parte,
    entre a prévia e a confirmação é leitura nova. **A chave só existe quando há o que
    acompanhar**: a publicação sem acompanhante assina o que sempre assinou, e quem compõe a
    assinatura sem a tela — o gesto do marco, as fixtures — continua conferindo.
    """
    conteudo = {
        "ato": str(ato.id),
        "publicacaoAnterior": (
            str(publicacao_anterior.id) if publicacao_anterior is not None else None
        ),
        "projecao": projecao["posicoes"],
    }
    if acompanhantes:
        conteudo["acompanhantes"] = sorted(
            [str(item["ato"].id), str(item["anterior"].id) if item["anterior"] else None]
            for item in acompanhantes
        )
    return canonical_sha256(conteudo)


def listas_sem_concorrente_do_marco(*, edital, marco_id, ato):
    """As ordens vigentes das **outras** listas do marco em que ninguém concorreu (155, R-006).

    `[{"ato", "anterior", "lista_id"}]`, na ordem da derivação dos recortes. Ninguém concorreu é a
    ordem vigente sem linha nenhuma — nem posição, nem sem posição —, que é o que a ordem vazia
    registra (FR-6329). Fica de fora a que já tem o definitivo publicado: depois dele não há
    natureza a acompanhar. **Independe da natureza**, e é por isso que a prévia pode assiná-la antes
    de a pessoa escolher uma: qual delas sai junto é `incluidas_na_publicacao`.
    """
    from processo_seletivo.classificacao.application.selectors import ato_vigente
    from processo_seletivo.classificacao.models import PosicaoNaOrdem
    from processo_seletivo.editais.domain.recortes import recortes_do_perfil

    conteudo = effective_version(edital_id=edital.id).content
    candidatas = []
    for lista_id, _ in recortes_do_perfil(conteudo, perfil_id=ato.perfil_id):
        if lista_id is None or str(lista_id) == str(ato.lista_id or ""):
            continue
        vigente = ato_vigente(edital=edital, marco_id=str(marco_id), lista_id=lista_id)
        if vigente is None or PosicaoNaOrdem.objects.filter(ato=vigente).exists():
            continue
        if PublicacaoResultado.objects.filter(ato=vigente, natureza=Natureza.DEFINITIVA).exists():
            continue
        candidatas.append(
            {
                "ato": vigente,
                "lista_id": lista_id,
                "anterior": vigente_do_marco(
                    edital=edital, marco_id=marco_id, lista_id=vigente.lista_id
                ),
            }
        )
    return candidatas


def incluidas_na_publicacao(*, edital, marco_id, candidatas, natureza, at=None, texto=""):
    """`(incluidas, de_fora)` das listas sem concorrente para **esta** natureza (FR-6330).

    Incluída é a que ainda não foi publicada nesta natureza, não regride, e que a aferição admite —
    a mesma pergunta que a publicação própria dela faria. A que a aferição recusa fica de fora com
    a mensagem, e continua tendo a publicação própria: incluí-la à força divulgaria o que a regra
    impede, e recusar o marco inteiro por ela prenderia as outras listas a um impedimento que não é
    delas.
    """
    incluidas, de_fora = [], []
    for item in candidatas:
        companheiro = item["ato"]
        if PublicacaoResultado.objects.filter(ato=companheiro, natureza=natureza).exists():
            continue
        if natureza_regride(item["anterior"], natureza):
            continue
        afericao = aferir(
            edital=edital,
            marco_id=marco_id,
            ato=companheiro,
            at=at,
            natureza=natureza,
            lista_id=companheiro.lista_id,
        )
        if not afericao.publicavel:
            de_fora.append({**item, "motivo": afericao.mensagem})
            continue
        try:
            declaracao = _declaracao_exigida(
                ato=companheiro, marco_id=marco_id, natureza=natureza, texto=texto
            )
        except DomainError as recusa:
            de_fora.append({**item, "motivo": recusa.detail})
            continue
        incluidas.append({**item, "declaracao": declaracao})
    return incluidas, de_fora


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
    com_as_listas_sem_concorrente=False,
):
    """Divulga um ato de ordenação vigente, congelando o que foi divulgado.

    Com `com_as_listas_sem_concorrente`, divulga também, **na mesma transação e na mesma
    confirmação**, as ordens vigentes das outras listas do marco em que ninguém concorreu, na mesma
    natureza e ainda não publicadas nela (155, FR-6330, R-006) — um registro por ato, como sempre.
    É a prévia da tela que o pede, porque é ela que as lista e as assina; o gesto do marco da `049`
    já publica cada lista na sua conferência, e não o pede.
    """
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

        # **O ato do recorte excedente não se divulga mais** (122, FR-3899). A pergunta é feita à
        # versão vigente: o que a operação de hoje usa. Publicações feitas antes não se tocam — a
        # recusa é só da divulgação nova, e vem depois da repetição, que devolve o que já foi.
        exigir_recorte_operacional(
            effective_version(edital_id=edital.id, at=agora).content,
            perfil_id=ato.perfil_id,
            lista_id=ato.lista_id,
        )

        # A autoridade habilitada na unidade do Edital e vigente hoje, conferida e travada — a mesma
        # regra da publicação do Edital e da Retificação (060, FR-1125, FR-1126).
        contexto = contexto_do_ato(edital, autoridade, agora)
        if natureza not in Natureza.values:
            raise DomainError(
                "publication_authority_required"
                if natureza is None
                else "publication_nature_regresses",
                "Escolha a natureza do resultado a divulgar.",
                422,
                campo="natureza",
            )

        # A lista vem **do ato**, e não do formulário: o ato é a autoridade sobre os eixos, e é
        # ele que a trigger de coerência confere. Recebê-la por parâmetro abriria a possibilidade
        # de publicar a ordem de uma lista declarando outra (021, D-015).
        lista_id = ato.lista_id
        publicabilidade = aferir(
            edital=edital,
            marco_id=marco_id,
            ato=ato,
            at=agora,
            natureza=natureza,
            lista_id=lista_id,
        )
        if not publicabilidade.publicavel:
            raise DomainError(
                publicabilidade.codigo,
                publicabilidade.mensagem,
                publicabilidade.status,
            )

        anterior = vigente_do_marco(edital=edital, marco_id=marco_id, lista_id=lista_id)
        if natureza_regride(anterior, natureza):
            raise DomainError(
                "publication_nature_regresses",
                "Um resultado preliminar não sucede um definitivo: a ordem entre as naturezas "
                "tem sentido único.",
                422,
                campo="natureza",
            )

        projecao = compor(ato)
        candidatas = (
            listas_sem_concorrente_do_marco(edital=edital, marco_id=marco_id, ato=ato)
            if com_as_listas_sem_concorrente
            else []
        )
        esperada = assinatura_da_previa(
            ato=ato, publicacao_anterior=anterior, projecao=projecao, acompanhantes=candidatas
        )
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
            ato=ato, marco_id=marco_id, natureza=natureza, texto=declaracao_de_encerramento
        )

        publicacao = _gravar_publicacao(
            edital=edital,
            ato=ato,
            natureza=natureza,
            anterior=anterior,
            projecao=projecao,
            agora=agora,
            actor=actor,
            contexto=contexto,
            declaracao=declaracao,
            correlation_id=correlation_id,
            idempotency_key=idempotency_key,
        )
        if candidatas:
            incluidas, _ = incluidas_na_publicacao(
                edital=edital,
                marco_id=marco_id,
                candidatas=candidatas,
                natureza=natureza,
                at=agora,
                texto=declaracao_de_encerramento,
            )
            for item in incluidas:
                # **Um registro por ato, na mesma transação** (R-006): a lista vazia tem a
                # publicação dela, com o conteúdo dela — "ninguém concorreu" —, e a trilha diz que
                # ela saiu junto desta.
                _gravar_publicacao(
                    edital=edital,
                    ato=item["ato"],
                    natureza=natureza,
                    anterior=item["anterior"],
                    projecao=compor(item["ato"]),
                    agora=agora,
                    actor=actor,
                    contexto=contexto,
                    declaracao=item["declaracao"],
                    correlation_id=correlation_id,
                    idempotency_key=idempotency_key,
                    junto_de=publicacao,
                )
        finish(reserva, publicacao, 201)
        return publicacao


def _gravar_publicacao(
    *,
    edital,
    ato,
    natureza,
    anterior,
    projecao,
    agora,
    actor,
    contexto,
    declaracao,
    correlation_id,
    idempotency_key,
    junto_de=None,
):
    """Grava a publicação de um ato, o que ela divulgou, o documento e a trilha.

    A mesma gravação para o ato pedido e para a lista sem concorrente que vai junto dele (155,
    R-006): duas cópias divergiriam na primeira coluna nova.
    """
    assinante = contexto.autoridade
    conteudo = conteudo_divulgado(
        projecao,
        natureza=natureza,
        publicado_em=agora,
        signatario=assinante,
        unidade=contexto.unidade,
        # **A causa é congelada no ato de publicar** (FR-088). Divulgação que sucede outra e
        # nasce de decisão de recurso é apresentada por ela — na página e no documento, que
        # leem os mesmos bytes. Derivá-la na leitura faria uma decisão posterior reescrever a
        # frase de um ato já praticado.
        retificacoes=_causas_da_retificacao(ato, anterior),
    )
    bytes_do_conteudo = canonical_bytes(conteudo)
    try:
        publicacao = PublicacaoResultado.objects.create(
            edital=edital,
            ato=ato,
            perfil_id=ato.perfil_id,
            marco_id=ato.marco_id,
            # Copiada do ato pela mesma razão que perfil e marco: ele é a autoridade sobre os
            # eixos, e a trigger de coerência recusa a publicação que declare outro (021).
            lista_id=ato.lista_id,
            natureza=natureza,
            publicacao_anterior=anterior,
            conteudo_publico=bytes_do_conteudo,
            conteudo_publico_hash=canonical_sha256(conteudo),
            publicado_por=actor.subject,
            publicado_em=agora,
            signatario_id=assinante.pk,
            signatario_nome=assinante.nome,
            signatario_cargo=assinante.cargo,
            signatario_ato_de_nomeacao=assinante.ato_de_nomeacao,
            **colunas_da_unidade(contexto.unidade),
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

    narrativa = _narrativa_do_ato(conteudo, ato, anterior)
    if junto_de is not None:
        narrativa = (
            f"{narrativa[:-1]}, junto da publicação {junto_de.id} do mesmo marco: ninguém "
            "concorreu nesta lista."
        )
    auditar(
        actor=actor,
        permissao=PERMISSAO,
        operation=PUBLICAR,
        aggregate=publicacao,
        now=agora,
        correlation_id=correlation_id,
        # Sem `com_ato_administrativo`: publicar não exige motivo — a sucessão já carrega o dela
        # no ato de origem (FR-067).
        reason=narrativa,
        idempotency_key=idempotency_key,
    )
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


def _declaracao_exigida(*, ato, marco_id, natureza, texto):
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
    from processo_seletivo.recursos.domain.janela import janela_do_ato

    texto = (texto or "").strip()
    if natureza != Natureza.DEFINITIVA:
        # Fora da definitiva a declaração não tem função: o preliminar não afirma que o prazo
        # acabou. Aceitá-la aqui gravaria uma afirmação sem objeto.
        return ""

    # A janela que vai valer para este ato depois de divulgado: a da versão que ele cita (RC-121).
    computavel = janela_do_ato(ato, marco_id) is not None
    if computavel and texto:
        raise DomainError(
            DECLARACAO_RECUSADA, MENSAGENS[DECLARACAO_RECUSADA], STATUS[DECLARACAO_RECUSADA]
        )
    if not computavel and not texto:
        raise DomainError(
            DECLARACAO_EXIGIDA, MENSAGENS[DECLARACAO_EXIGIDA], STATUS[DECLARACAO_EXIGIDA]
        )
    return "" if computavel else texto


def _causas_da_retificacao(ato, anterior):
    """As decisões que motivaram esta divulgação sucessora — serializáveis, ou lista vazia.

    Lista, e não a primeira: um ato pode citar mais de uma decisão (FR-112), e publicar uma e calar
    sobre a outra conta metade do que aconteceu.
    """
    if anterior is None:
        return []
    from processo_seletivo.recursos.application.selectors import causas_da_correcao

    return [
        {"recurso": causa["recurso"], "quando": causa["quando"].isoformat()}
        for causa in causas_da_correcao(ato)
    ]


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


__all__ = [
    "PERMISSAO",
    "PUBLICAR",
    "assinatura_da_previa",
    "incluidas_na_publicacao",
    "listas_sem_concorrente_do_marco",
    "publicar_resultado",
]
