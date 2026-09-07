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
        reserva = reserve(
            actor=ator,
            operation=f"{OPERACAO}:{inscricao.pk}",
            key=idempotency_key,
            payload={"fundamentacao": fundamentacao},
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
        peca = Recurso.objects.create(
            protocolo=protocolo_do_recurso.gerar(agora.year),
            inscricao=inscricao,
            interposto_por=identidade.subject,
            interposto_em=agora,
            fundamentacao=fundamentacao.strip(),
            publicacao_atacada=publicacao,
            resultado_atacado=resultado,
            versao=versao,
            # A janela estruturada é do degrau 8, e ela ainda não existe. Enquanto não existir, a
            # ausência é a afirmação certa: o sistema **não inventa prazo**, e a tempestividade é
            # juízo de admissibilidade motivado — que é a degradação declarada pela D-004.
            janela_abriu_em=None,
            janela_fecha_em=None,
        )
        _auditar(ator, peca, agora, correlation_id, idempotency_key)
        finish(reserva, peca, 201)
        return peca


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
        idempotency_key=idempotency_key,
    )


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

    ja_recorridos = set(
        Recurso.objects.filter(inscricao=inscricao).values_list("publicacao_atacada_id", flat=True)
    ) | set(
        Recurso.objects.filter(inscricao=inscricao).values_list("resultado_atacado_id", flat=True)
    )

    publicacoes = [
        {
            "tipo": "publicacao",
            "id": item["publicacao"].id,
            "rotulo": item["marco"] or item["natureza_rotulo"],
        }
        for item in situacoes_do_candidato(inscricao)
        if item["publicacao"].id not in ja_recorridos
    ]
    resultados = [
        {"tipo": "resultado", "id": item["id"], "rotulo": item["etapa"]}
        for item in resultados_visiveis(inscricao)
        if item["id"] not in ja_recorridos
    ]
    return publicacoes + resultados
