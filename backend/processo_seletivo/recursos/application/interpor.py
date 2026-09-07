"""Interpor recurso: o ato do candidato, e as quatro recusas que o antecedem.

**Uma capacidade, dois objetos atacáveis** (D-001). Publicação de marco e `ResultadoEtapa` do par
percorrem o **mesmo** fluxo e produzem a mesma espécie de peça: o que muda é qual identidade a peça
nomeia. Construir dois fluxos duplicaria a máquina inteira para variar um campo.

**A titularidade é a porta, e a recusa é 404** — nunca 403. Dizer "existe, mas não é seu" já
entrega que existe, e é o contrato que `exigir_titularidade` já sustenta em todo o portal.

**A janela é gravada, e não recalculada depois.** A peça registra se havia prazo computável e qual
era: recalcular na leitura responderia com a norma de hoje sobre um ato de ontem (FR-024).

A idempotência é a do projeto — a mesma `reserve`/`finish` que a submissão da inscrição usa, com o
`Actor` sem permissão alguma que `ator_do_candidato` monta. O duplo clique reserva a mesma chave e
devolve a mesma peça; a unicidade persistente por titular × objeto é a segunda barreira, e é ela
que responde se duas requisições escaparem por caminhos diferentes (FR-010, FR-011).
"""

import uuid

from django.db import IntegrityError, transaction
from django.utils import timezone

from processo_seletivo.inscricoes.application.rascunho import ator_do_candidato
from processo_seletivo.inscricoes.domain.titularidade import exigir_titularidade
from processo_seletivo.publicacoes.application.selectors import selecao_publica
from processo_seletivo.recursos.domain import protocolo as protocolo_do_recurso
from processo_seletivo.recursos.models import Recurso
from processo_seletivo.resultados.application.selectors import resultados_visiveis
from processo_seletivo.shared.api.problems import DomainError
from processo_seletivo.shared.application.commands import command_context
from processo_seletivo.shared.idempotency import finish, reserve

OPERACAO = "recurso:interpor"

PECA_SEM_FUNDAMENTO = "Recurso sem fundamentação não é peça: escreva a razão da sua contestação."
OBJETO_SUPERADO = (
    "O que você está contestando deixou de ser o vigente enquanto esta página estava aberta. "
    "Abra o resultado atual e, se ainda quiser recorrer, interponha sobre ele."
)
JA_INTERPOSTO = "Você já recorreu deste mesmo resultado, pelo recurso {protocolo}."


def interpor(
    *,
    identidade,
    inscricao,
    publicacao=None,
    resultado=None,
    fundamentacao,
    assinatura_do_objeto,
    idempotency_key,
    correlation_id="",
):
    """Grava a peça, ou recusa antes de gravar coisa alguma.

    `assinatura_do_objeto` é a identidade do que a tela apresentou. Divergência entre o lido e o
    vigente recusa em vez de interpor: quem clicou "recorrer" numa página aberta há dez minutos
    pode estar contestando um ato que já foi sucedido, e a peça nasceria contra o objeto errado
    (FR-009).
    """
    exigir_titularidade(inscricao, identidade)
    if (publicacao is None) == (resultado is None):
        raise DomainError("not_found", "Recurso não encontrado.", 404)
    if not (fundamentacao or "").strip():
        raise DomainError("appeal_reason_required", PECA_SEM_FUNDAMENTO, 422)

    ator = ator_do_candidato(identidade, inscricao.edital)
    with command_context() as agora:
        # **A interposição serializa com a publicação definitiva** (spec §concorrência).
        # Sem este bloqueio, a aferição de definitividade lê "zero recursos pendentes" enquanto uma
        # interposição é gravada na transação vizinha, e as duas confirmam: nasce um resultado
        # definitivo com recurso pendente dentro dele — que é exatamente o defeito que o E2E17-005
        # registrou, agora por corrida em vez de por seletor livre.
        #
        # O ponto de bloqueio é o `ProcessoSeletivo`, o mesmo que emitir, publicar e consolidar já
        # travam. Travar em outro lugar criaria uma segunda ordem de bloqueio, que é como nascem os
        # *deadlocks* entre comandos que hoje convivem.
        _travar_o_processo(inscricao, ator)
        reserva = reserve(
            actor=ator,
            operation=f"{OPERACAO}:{inscricao.pk}",
            key=idempotency_key,
            payload={
                "fundamentacao": fundamentacao,
                # **O pedido inteiro, e não só a razão** (FR-098). Sem o objeto na reserva, a mesma
                # chave usada contra outro Resultado devolveria a primeira peça em vez de conflitar
                # — e quem recorreu de duas coisas receberia o protocolo de uma só, sem saber.
                "objeto": str(getattr(publicacao or resultado, "pk", "")),
                "tipo": "publicacao" if publicacao is not None else "resultado",
            },
        )
        if reserva.result_id:
            return Recurso.objects.get(pk=reserva.result_id)

        alvo = publicacao or resultado
        if str(alvo.pk) != str(assinatura_do_objeto):
            raise DomainError("appeal_target_superseded", OBJETO_SUPERADO, 409)
        _recusar_se_superado(publicacao, resultado)
        _recusar_se_invisivel(inscricao, resultado)
        _recusar_se_repetido(inscricao, publicacao, resultado)

        versao = selecao_publica(edital_id=inscricao.edital_id)
        abriu, fecha = _janela(inscricao, publicacao, resultado, agora)
        peca = _gravar(
            protocolo=protocolo_do_recurso.gerar(agora.year),
            inscricao=inscricao,
            interposto_por=identidade.subject,
            interposto_em=agora,
            fundamentacao=fundamentacao.strip(),
            publicacao_atacada=publicacao,
            resultado_atacado=resultado,
            versao=versao,
            # **Gravada, e não recalculada depois** (FR-024). Recalcular na leitura responderia
            # com a norma de hoje sobre um ato de ontem. `None` nos dois quando o Edital não
            # declarou janela: a ausência é a afirmação certa — o sistema não inventa prazo, e a
            # tempestividade volta a ser juízo de admissibilidade motivado (D-004, FR-028).
            janela_abriu_em=abriu,
            janela_fecha_em=fecha,
        )
        _auditar(ator, peca, agora, correlation_id, idempotency_key)
        finish(reserva, peca, 201)
        return peca


def _gravar(**campos):
    """A gravação e a **segunda** barreira da unicidade — a que responde sob concorrência.

    Cobertura dupla, e deliberada, como em `publicar_resultado`: a idempotência responde ao
    **mesmo** pedido repetido, e `_recusar_se_repetido` escreve a mensagem que nomeia o protocolo.
    A constraint parcial responde a **dois pedidos distintos** que atravessaram a leitura prévia
    ao mesmo tempo —
    duas abas, duas chaves —, e sem esta tradução essa corrida viraria erro 500 numa tela de
    candidato (FR-011, FR-098).
    """
    try:
        with transaction.atomic():
            return Recurso.objects.create(**campos)
    except IntegrityError as exc:
        anterior = Recurso.objects.filter(
            inscricao=campos["inscricao"],
            publicacao_atacada=campos["publicacao_atacada"],
            resultado_atacado=campos["resultado_atacado"],
        ).first()
        protocolo = anterior.protocolo if anterior is not None else ""
        raise DomainError(
            "appeal_already_filed", JA_INTERPOSTO.format(protocolo=protocolo), 409
        ) from exc


NAO_PREVISTO = "appeal_not_provided"

NAO_ADMITE = (
    "O Edital declara que este resultado não admite recurso por esta via. Se você discorda do que "
    "foi decidido, procure a comissão do certame."
)

FORA_DO_PRAZO = (
    "O prazo para recorrer deste resultado encerrou-se em {fecha}. Ele foi de {dias} dias "
    "corridos, contados da divulgação de {abre}, conforme o Edital."
)


def _janelas_pertinentes(inscricao, publicacao, resultado, agora):
    """As janelas abertas ou fechadas que alcançam este objeto, na norma vigente.

    **Vários marcos podem enumerar a mesma Etapa** (FR-027), e a interposição contra o
    `ResultadoEtapa` é possível enquanto **qualquer** uma delas estiver aberta: prazo que restringe
    direito interpreta-se a favor de quem recorre. Contra a publicação, a janela é a daquele marco,
    e só.
    """
    from processo_seletivo.comissoes.domain.etapas import conteudo_vigente
    from processo_seletivo.divulgacao.application.selectors import vigente_do_marco
    from processo_seletivo.recursos.domain.janela import (
        admite_recurso,
        declaracao_do_marco,
        janela_da_publicacao,
    )

    edital = inscricao.edital
    conteudo = conteudo_vigente(edital)
    if publicacao is not None:
        marcos = [str(publicacao.marco_id)]
    else:
        marcos = [
            str(marco.get("id"))
            for perfil in conteudo.get("profiles") or []
            if str(perfil.get("id")) == str(inscricao.profile_id)
            for marco in perfil.get("classificationMilestones") or []
            if str(resultado.etapa_id) in {str(item) for item in marco.get("stages") or []}
        ]

    janelas, negados = [], []
    for marco_id in marcos:
        declaracao = declaracao_do_marco(conteudo, marco_id)
        negados.append(admite_recurso(declaracao) is False)
        vigente = (
            publicacao
            if publicacao is not None
            else vigente_do_marco(edital=edital, marco_id=marco_id)
        )
        computada = janela_da_publicacao(vigente, declaracao)
        if computada is not None:
            janelas.append(computada)
    return janelas, bool(negados) and all(negados)


def _janela(inscricao, publicacao, resultado, agora):
    """A janela que se grava na peça — e a recusa quando **todas** as pertinentes fecharam.

    Nenhuma janela declarada devolve `(None, None)`, e a interposição segue: sem norma não há prazo,
    e inventá-lo seria o sistema legislando (FR-028).
    """
    janelas, so_negativas = _janelas_pertinentes(inscricao, publicacao, resultado, agora)
    if so_negativas:
        # **`admits: false` é norma, e não silêncio** (FR-113). Tratá-lo como ausência
        # transformaria "este marco não admite recurso" em "cabe recurso para sempre" — o oposto do
        # que o Edital publicou.
        #
        # **Código próprio, e não o da janela encerrada**: um só obrigaria quem recebe a ler a
        # mensagem para distinguir "chegue mais cedo" de "não é por aqui", e as duas orientações são
        # opostas. A recusa nomeia a norma, porque é ela que a pessoa tem direito de conferir.
        raise DomainError(NAO_PREVISTO, NAO_ADMITE, 422)
    if not janelas:
        return None, None

    abertas = [(abre, fecha) for abre, fecha in janelas if agora <= fecha]
    if abertas:
        # A mais generosa entre as abertas: prazo que restringe direito interpreta-se a favor de
        # quem recorre, e é o que a FR-027 manda fazer quando dois marcos alcançam a mesma Etapa.
        return max(abertas, key=lambda par: par[1])

    abre, fecha = max(janelas, key=lambda par: par[1])
    dias = (fecha.date() - abre.astimezone(fecha.tzinfo).date()).days
    raise DomainError(
        "appeal_window_closed",
        FORA_DO_PRAZO.format(fecha=_data(fecha), dias=dias, abre=_data(abre)),
        422,
    )


def _data(momento):
    from processo_seletivo.shared.tempo import ZONA

    return momento.astimezone(ZONA).strftime("%d/%m/%Y")


def _travar_o_processo(inscricao, ator):
    """Bloqueia o Processo do Edital da Inscrição, e devolve-o.

    O escopo institucional entra no filtro porque o `Actor` do candidato o carrega — e porque
    encontrar o Processo de outra unidade aqui seria alcançar o que a autorização não alcança.
    """
    from processo_seletivo.processos.models import ProcessoSeletivo

    processo = (
        ProcessoSeletivo.objects.select_for_update()
        .filter(pk=inscricao.edital.processo_id, institution_scope=ator.institution_scope)
        .first()
    )
    if processo is None:
        raise DomainError("not_found", "Recurso não encontrado.", 404)
    return processo


def _recusar_se_superado(publicacao, resultado):
    """O objeto atacado precisa ser o **vigente** — a peça não nasce contra história.

    Recorrer de um ato já sucedido não é contestação: é contestar o que a instituição já corrigiu.
    O caminho é o objeto vigente, e a mensagem o diz.

    `sucessor` é o reverso de uma **chave estrangeira**, e não de um um-para-um: a unicidade do
    sucessor mora em `uq_resultado_sucessor_unico`, no banco. Perguntar por `hasattr` devolveria
    `True` sempre — o gerenciador reverso existe com ou sem linha —, e o primeiro teste de
    interposição encontrou exatamente isso: nenhum recurso contra Resultado nascia.
    """
    if publicacao is not None and publicacao.sucessoras.exists():
        raise DomainError("appeal_target_superseded", OBJETO_SUPERADO, 409)
    if resultado is not None and resultado.sucessor.exists():
        raise DomainError("appeal_target_superseded", OBJETO_SUPERADO, 409)


def _recusar_se_invisivel(inscricao, resultado):
    """Não se recorre do que ainda não foi divulgado — nem do que é só do próprio titular.

    O Resultado existe no banco desde a consolidação, e existir não o torna contestável: o fato que
    abre o recurso é o mesmo que abre a leitura, a publicação vigente de um marco do Perfil que
    enumera aquela Etapa (D-003, FR-014). Sem ele não há ato administrativo a atacar, e a peça
    nasceria contra um número que a instituição ainda não afirmou.

    A recusa é `404`, e não 422: o objeto **não é visível**, e dizer "existe, mas você ainda não
    pode vê-lo" antecipa o resultado — que é exatamente o que a não divulgação protege.
    """
    if resultado is None:
        return
    visiveis = {item["id"] for item in resultados_visiveis(inscricao)}
    if resultado.pk not in visiveis:
        raise DomainError("appeal_not_visible", "Recurso não encontrado.", 404)


def _recusar_se_repetido(inscricao, publicacao, resultado):
    """Um recurso por titular e objeto, pendente **ou já decidido** (FR-011, FR-012).

    A leitura prévia existe para a mensagem nomear o protocolo da primeira peça; a garantia é da
    constraint parcial, que é quem responde sob concorrência.
    """
    anterior = Recurso.objects.filter(
        inscricao=inscricao,
        publicacao_atacada=publicacao,
        resultado_atacado=resultado,
    ).first()
    if anterior is not None:
        raise DomainError(
            "appeal_already_filed", JA_INTERPOSTO.format(protocolo=anterior.protocolo), 409
        )


def _auditar(ator, peca, agora, correlation_id, idempotency_key):
    """A trilha existente, e **sem a fundamentação**.

    Fundamentação é conteúdo do juízo, e não registro de que houve juízo — a mesma linha que a 012
    traçou ao manter parecer e pontuação fora da trilha (FR-094).

    Sem `permissao`: interpor não atravessa `require_permission`. O candidato prova o controle de
    um e-mail e a titularidade da própria Inscrição, e é só isso que a autorização dele é — a 010
    removeu de propósito o provedor que deixava alguém declarar quem era.
    """
    from processo_seletivo.avaliacoes.application.trilha import auditar

    auditar(
        actor=ator,
        permissao="",
        operation=OPERACAO,
        aggregate=peca,
        now=agora,
        correlation_id=correlation_id,
        # **O ato, e não o conteúdo dele** (FR-094, FR-095). A trilha responde "houve interposição,
        # por quem, quando e contra o quê"; a fundamentação continua fora, porque ela é conteúdo do
        # juízo e copiá-la criaria uma segunda cópia do dado sensível, sob outro regime de acesso.
        reason=f"Recurso {peca.protocolo} interposto contra {_objeto_auditavel(peca)}.",
        idempotency_key=idempotency_key,
    )


def _objeto_auditavel(peca):
    if peca.publicacao_atacada_id is not None:
        return f"a publicação {peca.publicacao_atacada_id}"
    return f"o resultado de etapa {peca.resultado_atacado_id}"


def objeto_atacado(inscricao, tipo, identificador):
    """O objeto que a tela apresentou — **inclusive quando ele já foi superado**.

    A busca nasce restrita ao universo do titular: o Resultado é da Inscrição dele, e a publicação
    é do par Edital × Perfil dela. É a mesma fronteira que o gatilho `recurso_coerente` sustenta no
    banco, e aqui ela recusa com 404 em vez de erro de integridade.

    **Sem filtro de vigência, e é deliberado.** Quem deixou a página aberta enquanto o resultado era
    corrigido precisa achar o objeto que clicou para receber a recusa que explica o que aconteceu e
    aponta o vigente (FR-009). Filtrar aqui devolveria "não encontrado", e quem lê isso conclui que
    o sistema perdeu o resultado dela. Quem decide sobre a vigência é `_recusar_se_superado`.
    """
    from processo_seletivo.divulgacao.models import PublicacaoResultado
    from processo_seletivo.resultados.models import ResultadoEtapa

    try:
        alvo = uuid.UUID(str(identificador))
    except ValueError:
        raise DomainError("not_found", "Recurso não encontrado.", 404) from None

    if tipo == "publicacao":
        achado = PublicacaoResultado.objects.filter(
            pk=alvo, edital_id=inscricao.edital_id, perfil_id=inscricao.profile_id
        ).first()
    elif tipo == "resultado":
        achado = ResultadoEtapa.objects.filter(pk=alvo, inscricao=inscricao).first()
    else:
        achado = None

    if achado is None:
        raise DomainError("not_found", "Recurso não encontrado.", 404)
    return achado


def objetos_recorriveis(inscricao):
    """O que o titular pode contestar agora — e é daqui que a tela decide oferecer a ação.

    **A ação não aparece quando a interposição não é possível** (FR-013). A recusa existe para quem
    chega por outro caminho, e não como comportamento normal da tela: oferecer um botão que sempre
    recusa é pior do que não oferecê-lo.
    """
    from processo_seletivo.divulgacao.application.selectors import situacoes_do_candidato

    # Uma consulta, e não duas: os dois campos vêm da mesma varredura das peças do titular. Duas
    # leituras idênticas variando a coluna é o tipo de custo que passa despercebido com uma peça e
    # aparece com dez.
    ja_recorridos = {
        identificador
        for par in Recurso.objects.filter(inscricao=inscricao).values_list(
            "publicacao_atacada_id", "resultado_atacado_id"
        )
        for identificador in par
        if identificador is not None
    }

    agora = timezone.now()
    publicacoes = [
        {
            "tipo": "publicacao",
            "id": item["publicacao"].id,
            "rotulo": item["marco"] or item["natureza_rotulo"],
            "fecha_em": _fecha_em(inscricao, item["publicacao"], None, agora),
        }
        for item in situacoes_do_candidato(inscricao)
        if item["publicacao"].id not in ja_recorridos
        and _no_prazo(inscricao, item["publicacao"], None, agora)
    ]
    resultados = [
        {
            "tipo": "resultado",
            "id": item["id"],
            "rotulo": item["etapa"],
            "fecha_em": _fecha_em(inscricao, None, _resultado(inscricao, item["id"]), agora),
        }
        for item in resultados_visiveis(inscricao)
        if item["id"] not in ja_recorridos
        and _no_prazo(inscricao, None, _resultado(inscricao, item["id"]), agora)
    ]
    return publicacoes + resultados


def _fecha_em(inscricao, publicacao, resultado, agora):
    """Quando o prazo daquele objeto fecha — `None` quando não há janela declarada.

    **É a mesma escolha da interposição**, e tem de ser: mostrar uma data e aceitar até outra faria
    a tela mentir. Entre janelas abertas vale a mais generosa, porque é ela que a FR-027 aplica.

    Sem declaração não há data a exibir, e `None` aqui não é "não sei": é a FR-028 dizendo que
    prazo nenhum existe para exibir ou aplicar.
    """
    janelas, so_negativas = _janelas_pertinentes(inscricao, publicacao, resultado, agora)
    if so_negativas or not janelas:
        return None
    abertas = [fecha for _abre, fecha in janelas if agora <= fecha]
    return max(abertas) if abertas else None


def _resultado(inscricao, identificador):
    from processo_seletivo.resultados.models import ResultadoEtapa

    return ResultadoEtapa.objects.filter(pk=identificador, inscricao=inscricao).first()


def _no_prazo(inscricao, publicacao, resultado, agora):
    """Se ainda cabe recorrer deste objeto **hoje**, pela janela declarada.

    **A ação não é oferecida quando a interposição não é possível** (FR-013): um botão que sempre
    recusa ensina a pessoa a desconfiar da tela. Sem janela declarada não há prazo a aplicar, e a
    resposta é sim — que é o comportamento de todo Edital anterior ao degrau 8.
    """
    if resultado is None and publicacao is None:
        return False
    janelas, so_negativas = _janelas_pertinentes(inscricao, publicacao, resultado, agora)
    if so_negativas:
        return False
    return not janelas or any(agora <= fecha for _abre, fecha in janelas)
