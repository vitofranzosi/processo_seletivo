"""Constituir o sorteio: um comando, uma transação, um ato (021, FR-029, FR-031, FR-032).

**O que este comando não recebe.** Não recebe semente — não existe campo de semente em caminho
algum do sistema (FR-017). Não recebe método — ele consome o que a relação comprometeu ao congelar,
e resolvê-lo aqui seria escolhê-lo depois de conhecer a semente (FR-067, D-014). E não recebe
ordem: a ordem é derivada, e derivada de entradas que já estavam fixadas antes de este comando
existir.

**O que ele lê, na ordem em que lê.** A relação congelada; a ocorrência **já observada e
registrada**, sem ir à rede; o método, pela versão que a relação cita, conferido contra o resumo que
ela gravou. Só então normaliza o material bruto, calcula as chaves e grava — tudo numa transação.

**Não existe "refazer".** A anulação é a constituição de um sorteio **sucessor**, que nasce de
relação nova e ocorrência nova (FR-052, FR-054): um botão de refazer devolveria ao certame a
repetição até o resultado agradar, que é a fresta que a feature inteira existe para fechar.
"""

from processo_seletivo.avaliacoes.application.trilha import auditar
from processo_seletivo.classificacao.models import AtoDeOrdenacao, OrigemDaOrdem, PosicaoNaOrdem
from processo_seletivo.comissoes.application import comando_de_comissao, nao_encontrado
from processo_seletivo.comissoes.application.comissao import identificador
from processo_seletivo.processos.models import Edital
from processo_seletivo.shared.api.problems import DomainError
from processo_seletivo.sorteios.domain import chave as dominio_da_chave
from processo_seletivo.sorteios.domain import manifesto as dominio_do_manifesto
from processo_seletivo.sorteios.domain import metodo as dominio_do_metodo
from processo_seletivo.sorteios.domain import normalizacao, substituicao
from processo_seletivo.sorteios.models import OcorrenciaDaFonte, RelacaoDeHabilitados, Sorteio

CONSTITUIR = "SORTEIO_CONSTITUIR"
ATO = "sorteios:constituir"

# O que a `015` grava para quem recebe posição, e é o que o motor já entende (`calculo.py`).
# Reusar o valor mantém uma grafia só para o mesmo estado do motor; renomeá-lo seria mexer na `015`
# por causa da `021`. Ele **não** afirma habilitação no sentido do Edital — quem habilita é a
# análise documental, que nesta feature vem depois e é de outra capacidade (FR-064).
CONSEQUENCIA = "HABILITADA"


def constituir_sorteio(
    *,
    actor,
    processo_id,
    edital_id,
    relacao_id,
    ocorrencia_id,
    idempotency_key,
    correlation_id,
    sorteio_anterior_id=None,
    motivo_da_anulacao="",
):
    """Calcula a ordem e constitui o ato. Atômico e idempotente."""
    payload = {
        "edital": str(edital_id),
        "relacao": str(relacao_id),
        "ocorrencia": str(ocorrencia_id),
        "anterior": str(sorteio_anterior_id or ""),
        "motivo": (motivo_da_anulacao or "").strip(),
    }
    with comando_de_comissao(
        actor=actor,
        processo_id=processo_id,
        operation=ATO,
        payload=payload,
        idempotency_key=idempotency_key,
    ) as ctx:
        if ctx.repetido:
            return ctx.desfecho_anterior
        edital = _edital_do_processo(ctx.processo, edital_id)
        relacao = _relacao(edital, relacao_id)
        ocorrencia = _ocorrencia(ocorrencia_id)
        anterior = _anterior(edital, sorteio_anterior_id, motivo_da_anulacao, relacao, ocorrencia)

        # **O método vem antes de qualquer recusa sobre a ocorrência**, e a ordem é a correção de
        # um defeito: sem o método em mãos, não havia como perguntar se **esta** ocorrência é a
        # declarada — e a pergunta não era feita. O método vem da versão que a relação cita, e não
        # do conteúdo vigente: é o que faz a reprodução histórica valer, e o que impede uma
        # Retificação posterior de mudar, em silêncio, a regra sob a qual o certame se comprometeu
        # (FR-039, FR-067).
        metodo, _resumo = dominio_do_metodo.conferir_compromisso(
            relacao.versao.content,
            perfil_id=relacao.perfil_id,
            marco_id=relacao.marco_id,
            metodo_hash=relacao.metodo_hash,
        )
        _recusar_o_que_nao_pode_sortear(relacao, ocorrencia, metodo)
        _recusar_ato_ja_existente(edital, relacao, ocorrencia, anterior)
        semente = normalizacao.normalizar(
            material_bruto=ocorrencia.material_bruto,
            regra=(metodo.get("normalization") or {}).get("rule", ""),
        )
        participantes = list(
            relacao.participantes.select_related("inscricao").order_by("numero_publico")
        )
        recorte = dominio_da_chave.recorte(perfil_id=relacao.perfil_id, lista_id=relacao.lista_id)
        chaves = dominio_da_chave.chaves(
            relation_hash=relacao.resumo,
            draw_scope_id=recorte,
            seed=semente,
            public_numbers=[p.numero_publico for p in participantes],
        )
        ordem = dominio_da_chave.ordenar(chaves)
        _recusar_ordem_incompleta(relacao, ordem)

        sorteio, ato = _gravar(
            actor=actor,
            now=ctx.now,
            edital=edital,
            relacao=relacao,
            ocorrencia=ocorrencia,
            metodo=metodo,
            semente=semente,
            participantes=participantes,
            chaves=chaves,
            ordem=ordem,
            anterior=anterior,
            motivo=(motivo_da_anulacao or "").strip(),
        )
        auditar(
            actor=actor,
            permissao=ctx.base.permissao,
            operation=CONSTITUIR,
            aggregate=sorteio,
            now=ctx.now,
            correlation_id=correlation_id,
            reason=(
                (motivo_da_anulacao or "").strip()
                or f"Sorteio constituído com {len(ordem)} participantes."
            ),
            idempotency_key=idempotency_key,
        )
        declarado = {
            "sorteio": str(sorteio.id),
            "ato": str(ato.id),
            "relacao": str(relacao.id),
            "quantidade": len(ordem),
            "semente": semente,
            "manifestoHash": sorteio.manifesto_hash,
        }
        ctx.concluir_sem_resultado(201, declarado)
        return declarado


def anular_sorteio(
    *,
    actor,
    processo_id,
    edital_id,
    sorteio_anterior_id,
    relacao_id,
    ocorrencia_id,
    motivo,
    idempotency_key,
    correlation_id,
):
    """Anular **é** constituir o sucessor, e não desfazer (FR-052, FR-053, FR-054).

    Não há comando de "refazer" porque não há o que refazer: o ato anterior permanece íntegro,
    legível e verificável, e o novo nasce de relação nova e ocorrência nova. Um comando que
    apagasse ou reexecutasse devolveria ao certame a repetição até o resultado agradar.
    """
    if not (motivo or "").strip():
        raise DomainError(
            "draw_annulment_reason_required",
            "A anulação exige motivo escrito: um sorteio anulado sem razão registrada seria um "
            "ato desfeito sem que ninguém respondesse por isso.",
            422,
            campo="motivo",
        )
    return constituir_sorteio(
        actor=actor,
        processo_id=processo_id,
        edital_id=edital_id,
        relacao_id=relacao_id,
        ocorrencia_id=ocorrencia_id,
        idempotency_key=idempotency_key,
        correlation_id=correlation_id,
        sorteio_anterior_id=sorteio_anterior_id,
        motivo_da_anulacao=motivo,
    )


def _recusar_o_que_nao_pode_sortear(relacao, ocorrencia, metodo):
    if relacao.sucessoras.exists():
        raise DomainError(
            "relation_superseded",
            "Esta relação foi sucedida: o universo comprometido já não é este. O sorteio nasce da "
            "relação vigente.",
            409,
        )
    if ocorrencia.indisponivel:
        raise DomainError(
            "occurrence_unavailable",
            "A ocorrência registrada é a de uma indisponibilidade. A regra publicada de "
            "substituição indica qual ocorrência a substitui; observe aquela.",
            409,
        )
    # **A ocorrência tem de ser a que o Edital declarou** (FR-013, FR-017). Ela chegava por
    # identidade, e fonte e referência nunca eram comparadas com o método congelado: bastava passar
    # outro UUID para sortear com uma extração que ninguém publicou. A regra de substituição é a
    # única coisa que desloca essa referência, e ela é mecânica.
    indisponiveis = set(
        OcorrenciaDaFonte.objects.filter(
            fonte=str((metodo or {}).get("source") or ""), indisponivel=True
        ).values_list("referencia", flat=True)
    )
    if not substituicao.admissivel(metodo, ocorrencia, indisponiveis):
        esperada = substituicao.proxima_a_observar(metodo, indisponiveis)
        raise DomainError(
            "occurrence_not_declared",
            f"O Edital declara a ocorrência {esperada!r} da fonte "
            f"{(metodo or {}).get('source')!r}, e esta é {ocorrencia.referencia!r} de "
            f"{ocorrencia.fonte!r}. A ocorrência que fixa a semente é a declarada — ou a que a "
            "regra publicada de substituição põe no lugar dela, e essa também não se escolhe.",
            409,
        )
    if ocorrencia.ocorrida_em is None:
        # Sem saber **quando o evento externo aconteceu**, não há como afirmar que ele é posterior
        # ao congelamento: o instante da leitura é escolhido por quem lê (FR-016).
        raise DomainError(
            "occurrence_without_instant",
            "A fonte não informou quando esta ocorrência aconteceu, e sem isso não é possível "
            "afirmar que ela é posterior ao congelamento da relação. Uma ocorrência que o sistema "
            "não sabe datar não semeia sorteio.",
            409,
        )
    if ocorrencia.ocorrida_em <= relacao.publicada_em:
        # A semente **posterior** ao congelamento é a inversão que organiza a feature inteira: uma
        # ocorrência anterior significaria que o universo foi fechado sabendo o resultado.
        #
        # **A comparação é com `ocorrida_em`, e não com `observada_em`.** Era com a segunda, e a
        # garantia era contornável: bastava congelar a relação depois de ver a extração na
        # televisão e registrá-la no sistema em seguida.
        raise DomainError(
            "occurrence_precedes_freeze",
            "A ocorrência aconteceu antes de a relação ser congelada. A semente é posterior ao "
            "compromisso do universo, e não o contrário.",
            409,
        )


def _recusar_ato_ja_existente(edital, relacao, ocorrencia, anterior):
    """A unicidade da FR-031, dita **antes** da escrita e em português.

    **A trava é que torna esta checagem suficiente.** `comando_de_comissao` toma `select_for_update`
    sobre o Processo antes de ceder o contexto, de modo que dois pedidos concorrentes não chegam
    aqui ao mesmo tempo: o segundo espera, entra depois do commit do primeiro, e enxerga o ato que
    ele criou. É por isso que a concorrência produz exatamente um ato **com uma recusa legível**, e
    não com uma violação de constraint no meio da transação.

    As constraints continuam sendo a garantia — elas valem para quem escreva por fora do comando —,
    e a ordem em que elas disparariam é justamente o problema que esta função resolve: o
    `AtoDeOrdenacao` é gravado primeiro, e `uq_ato_raiz_por_marco` falaria antes da
    `uq_sorteio_raiz`, devolvendo à tela o nome de uma constraint em vez do motivo.
    """
    if anterior is not None:
        # O sucessor nasce de relação nova e ocorrência nova, e a unicidade dele é a de sucessão —
        # `uq_sorteio_sucessor_unico` —, não a de raiz.
        return
    ja_sorteado = Sorteio.objects.filter(
        relacao=relacao, ocorrencia=ocorrencia, sorteio_anterior__isnull=True
    ).first()
    if ja_sorteado is not None:
        raise DomainError(
            "draw_already_constituted",
            "Já existe um sorteio para esta relação e esta ocorrência. Recalcular a ordem é livre "
            "e qualquer pessoa pode fazê-lo; emitir outro ato não.",
            409,
        )
    ato_vigente = AtoDeOrdenacao.objects.filter(
        edital=edital,
        perfil_id=relacao.perfil_id,
        marco_id=relacao.marco_id,
        lista_id=relacao.lista_id,
        ato_anterior__isnull=True,
    ).first()
    if ato_vigente is not None:
        raise DomainError(
            "ordering_act_already_exists",
            "Este recorte já tem ato de ordenação raiz. Um sorteio novo para ele nasce como "
            "sucessor, com o motivo da anulação do anterior.",
            409,
        )


def _recusar_ordem_incompleta(relacao, ordem):
    """A ordem cobre **todos**, e não é truncada pelo número de vagas (FR-025)."""
    if len(ordem) != relacao.quantidade:
        raise DomainError(
            "draw_order_incomplete",
            f"A ordem cobriria {len(ordem)} de {relacao.quantidade} participantes. A ordem do "
            "sorteio alcança todos os participantes da relação, e nunca só os que caberiam nas "
            "vagas.",
            422,
        )


def _gravar(
    *,
    actor,
    now,
    edital,
    relacao,
    ocorrencia,
    metodo,
    semente,
    participantes,
    chaves,
    ordem,
    anterior,
    motivo,
):
    por_numero = {p.numero_publico: p for p in participantes}
    ato = AtoDeOrdenacao.objects.create(
        edital=edital,
        perfil_id=relacao.perfil_id,
        marco_id=relacao.marco_id,
        lista_id=relacao.lista_id,
        origem=OrigemDaOrdem.SORTEIO,
        versao=relacao.versao,
        ato_anterior=anterior.ato if anterior is not None else None,
        motivo_da_sucessao=motivo,
        # As quatro identidades e `stageResults` são exigência da trigger de proveniência; a
        # proveniência do sorteio vem junto, e é a chave `origem` que a leitura usa para despachar.
        universo={
            "editalId": str(edital.id),
            "profileId": str(relacao.perfil_id),
            "milestoneId": str(relacao.marco_id),
            "versionId": str(relacao.versao_id),
            "stageResults": [],
            "origem": OrigemDaOrdem.SORTEIO.value,
            "relacaoId": str(relacao.id),
            "relationHash": relacao.resumo,
            "quantidade": relacao.quantidade,
        },
        emitido_por=actor.subject,
        emitido_em=now,
    )
    PosicaoNaOrdem.objects.bulk_create(
        [
            PosicaoNaOrdem(
                ato=ato,
                inscricao=por_numero[numero].inscricao,
                posicao=posicao,
                # Sorteio não pontua: não há grandeza a afirmar, e escrever zero afirmaria uma.
                pontuacao_combinada=None,
                modalidade_id=por_numero[numero].inscricao.modality_id,
                consequencia=CONSEQUENCIA,
                motivo="",
                # A ordem é total: o desempate por número público não deixa empate residual.
                empate_residual=False,
                desempate=[],
            )
            for posicao, numero in enumerate(ordem, start=1)
        ]
    )
    # **O resumo do manifesto nasce com o sorteio, e não depois dele.** O agregado é append-only
    # nas três camadas — `save` recusa, a trigger recusa, o privilégio não existe —, então não há
    # segunda gravação a fazer. Derivar antes de salvar é o que torna a proveniência completa desde
    # o primeiro instante, em vez de existir uma janela em que o sorteio existe sem o seu pacote.
    sorteio = Sorteio(
        edital=edital,
        perfil_id=relacao.perfil_id,
        marco_id=relacao.marco_id,
        lista_id=relacao.lista_id,
        relacao=relacao,
        ocorrencia=ocorrencia,
        metodo_hash=relacao.metodo_hash,
        semente_normalizada=semente,
        ato=ato,
        executado_em=now,
        executado_por=actor.subject,
        sorteio_anterior=anterior,
        motivo_da_anulacao=motivo,
    )
    sorteio.manifesto_hash = dominio_do_manifesto.resumo_do_manifesto(
        dominio_do_manifesto.derivar(
            sorteio=sorteio, relacao=relacao, metodo=metodo, chaves=chaves, ordem=ordem
        )
    )
    # Sem `try`: a recusa legível já aconteceu em `_recusar_ato_ja_existente`, sob a trava do
    # comando. Uma violação de constraint **aqui** significaria que alguém escreveu por fora, e
    # abafá-la numa mensagem amigável esconderia exatamente o que precisa aparecer.
    sorteio.save()
    return sorteio, ato


def _relacao(edital, relacao_id):
    relacao = (
        RelacaoDeHabilitados.objects.filter(pk=identificador(relacao_id), edital=edital)
        .select_related("versao")
        .first()
    )
    if relacao is None:
        raise nao_encontrado()
    return relacao


def _ocorrencia(ocorrencia_id):
    ocorrencia = OcorrenciaDaFonte.objects.filter(pk=identificador(ocorrencia_id)).first()
    if ocorrencia is None:
        raise nao_encontrado()
    return ocorrencia


def _anterior(edital, sorteio_anterior_id, motivo, relacao, ocorrencia):
    """O sorteio que este sucede — e as cinco coerências que a sucessão exige (FR-053, FR-054).

    **A verificação era só "pertence ao mesmo Edital"**, e isso deixava passar exatamente o que a
    FR-052 proíbe: encadear um "sucessor" com a mesma relação e a mesma ocorrência é refazer o
    sorteio com os mesmos insumos, com outro nome. Também deixava encadear atos de recortes
    diferentes, o que produziria uma cadeia que não é cadeia de nada.
    """
    if not sorteio_anterior_id:
        return None
    anterior = Sorteio.objects.filter(pk=identificador(sorteio_anterior_id), edital=edital).first()
    if anterior is None:
        raise nao_encontrado()
    if not (motivo or "").strip():
        raise DomainError(
            "draw_annulment_reason_required",
            "O sorteio sucessor exige o motivo da anulação do anterior.",
            422,
            campo="motivo",
        )
    if anterior.sucessores.exists():
        raise DomainError(
            "draw_already_superseded",
            "Este sorteio já foi anulado por um sucessor. A cadeia é linear: anula-se o vigente.",
            409,
        )
    if (
        str(anterior.perfil_id) != str(relacao.perfil_id)
        or str(anterior.marco_id) != str(relacao.marco_id)
        or str(anterior.lista_id or "") != str(relacao.lista_id or "")
    ):
        raise DomainError(
            "draw_succession_across_scopes",
            "O sorteio sucessor é do mesmo recorte que o anulado. Encadear recortes diferentes "
            "produziria uma cadeia que não descreve certame nenhum.",
            409,
        )
    if str(anterior.relacao_id) == str(relacao.id):
        raise DomainError(
            "draw_succession_reuses_relation",
            "O sorteio sucessor nasce de relação **nova**: reusar a relação anulada seria refazer "
            "o sorteio sobre o mesmo universo, que é o 'executar de novo' que não existe.",
            409,
        )
    if str(anterior.ocorrencia_id) == str(ocorrencia.id):
        raise DomainError(
            "draw_succession_reuses_occurrence",
            "O sorteio sucessor nasce de ocorrência **nova**: reusar a semente do ato anulado "
            "produziria a mesma ordem, com outro número de ato.",
            409,
        )
    if str(getattr(relacao.relacao_anterior, "id", "")) != str(anterior.relacao_id):
        raise DomainError(
            "draw_succession_relation_not_linked",
            "A relação do sucessor precisa suceder diretamente a do sorteio anulado. Uma relação "
            "de outra cadeia deixaria o universo do sucessor sem ligação com o que se anulou.",
            409,
        )
    return anterior


def _edital_do_processo(processo, edital_id):
    edital = Edital.objects.filter(
        pk=identificador(edital_id),
        processo=processo,
        institution_scope=processo.institution_scope,
    ).first()
    if edital is None:
        raise nao_encontrado()
    return edital


__all__ = ["ATO", "CONSTITUIR", "anular_sorteio", "constituir_sorteio"]
