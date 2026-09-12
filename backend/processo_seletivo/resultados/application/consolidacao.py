"""O ato que transforma avaliações concluídas em Resultado — em lote, e uma vez só.

**Nenhum mecanismo novo.** O invólucro transacional que bloqueia o Processo, reavalia a autorização
depois do bloqueio e reserva a chave é o da 011; o desfecho preservado no `result_payload` e as
recusas agrupadas por motivo são da 012; a trilha é a mesma chamada explícita. A 013 usa os quatro
e não escreve nenhum.

**O que a presidência confirma é um cálculo, e não uma nota.** Não há campo de pontuação, de
consequência nem de justificativa no corpo aceito: a pontuação é cópia exata da fonte e a
consequência sai da regra publicada. Deixar a presidência digitar qualquer um dos dois seria
transformar em decisão humana o que o Edital já decidiu (FR-016).

**Recusa de item e erro do pedido são coisas diferentes**, e a classificação é a mesma da 012: o
que a tela não deveria ter oferecido — seleção vazia, Etapa sem regra, inscrição fora do conjunto —
é erro sobre o pedido e impede qualquer criação; o que o caminho normal encontra — sem conclusão,
incompatibilidade, já consolidada — é recusa de linha, e o lote segue.
"""

from uuid import UUID

from processo_seletivo.avaliacoes.application.distribuicao import resultado_declarado
from processo_seletivo.avaliacoes.application.trilha import auditar
from processo_seletivo.comissoes.application import comando_de_comissao, nao_encontrado
from processo_seletivo.comissoes.application.comissao import identificador
from processo_seletivo.inscricoes.models import Inscricao
from processo_seletivo.processos.models import Edital
from processo_seletivo.resultados.application.prontidao import (
    E_TAMBEM_FORA,
    FORA_DA_FAIXA,
    FORA_DO_CORTE,
    NAO_PARTICIPA,
    PRONTA,
    REAVALIACAO,
    panorama_da_etapa,
)
from processo_seletivo.resultados.domain.regra import consequencia
from processo_seletivo.resultados.models import ResultadoEtapa
from processo_seletivo.shared.api.problems import DomainError

CONSOLIDAR = "RESULTADO_CONSOLIDAR"
ATO = "resultado:consolidar"


class Recusa:
    """Uma inscrição que não virou Resultado, e por quê."""

    def __init__(self, inscricao, motivo):
        self.inscricao = inscricao
        self.motivo = motivo

    def declarada(self):
        return {
            "inscricao": self.inscricao.protocolo or str(self.inscricao.id),
            "motivo": self.motivo,
        }

    def __repr__(self):
        return f"Recusa({self.inscricao}, {self.motivo!r})"


def _edital_do_processo(processo, edital_id):
    edital = Edital.objects.filter(pk=identificador(edital_id), processo=processo).first()
    if edital is None:
        raise nao_encontrado()
    return edital


def _etapa_vigente_ou_404(edital, etapa_id):
    """`(etapa, vigentes, conteudo)` — o conteúdo viaja porque a prontidão precisa dele.

    `effective_version` custa duas consultas, e a condição do corte da `014` precisa dos marcos que
    governam a Etapa: relê-lo lá dentro dobraria o custo de toda consolidação (014, R-005).
    """
    from processo_seletivo.comissoes.domain.etapas import conteudo_vigente

    conteudo = conteudo_vigente(edital)
    vigentes = {UUID(str(etapa["id"])): etapa for etapa in conteudo.get("stages") or []}
    etapa = vigentes.get(identificador(etapa_id))
    if etapa is None:
        raise nao_encontrado()
    return etapa, vigentes, conteudo


def _inscricoes_da_selecao(edital, ids, panorama):
    """As inscrições pedidas, exigindo que sejam submetidas **e participantes** da Etapa.

    Fora do conjunto é **erro do pedido**, e não recusa de linha — a mesma classificação que
    `_inscricoes_atribuiveis` da 012 aplica a inscrição não submetida, e pelo mesmo motivo: pedir
    para consolidar quem foi eliminado numa Etapa anterior não é o caminho normal esbarrando numa
    regra, é uma seleção que a tela não deveria ter oferecido (FR-007).
    """
    inscricoes = list(
        Inscricao.objects.filter(pk__in=ids, edital=edital, status=Inscricao.Status.SUBMETIDA)
    )
    if len(inscricoes) != len(set(ids)):
        raise DomainError(
            "inscricao_nao_consolidavel",
            "Só inscrições submetidas deste Edital podem ser consolidadas.",
            422,
            campo="inscricao_id",
        )
    fora = [i for i in inscricoes if i.id not in panorama["participantes"]]
    if fora:
        # **A causa sai do panorama**, que já a classificou — e não de uma segunda consulta. Dizer
        # "foi eliminada ou aguarda a anterior" a quem a faixa do corte não alcançou afirmaria o
        # que não aconteceu: ele foi considerado, tem posição na ordem, e a norma publicada o
        # deixou de fora (014, FR-210, UX-025, E2E14-008).
        cortadas = [i for i in fora if panorama["estados"].get(i.id, (None,))[0] == FORA_DO_CORTE]
        raise DomainError(
            "inscricao_fora_da_etapa",
            (
                FORA_DA_FAIXA
                if len(cortadas) == len(fora)
                else NAO_PARTICIPA + (E_TAMBEM_FORA if cortadas else "")
            ),
            422,
            campo="inscricao_id",
        )
    return inscricoes


SEM_REAVALIACAO = "a reavaliação determinada por recurso ainda não foi concluída por um avaliador"
PIORARIA = (
    "a reavaliação produziu resultado pior que o protegido pela decisão, e o recurso não pode "
    "agravar a situação de quem recorreu; a avaliação fica registrada e o resultado não é superado"
)
MOTIVO_DA_REAVALIACAO = (
    "Resultado corrigido em cumprimento da decisão de reavaliação no recurso {protocolo}"
)


def _decisao_a_cumprir(panorama, inscricao, estado):
    """A decisão de reavaliação que esta consolidação cumpre, ou `None`.

    **É a única porta pela qual consolidar cria sucessor** (FR-068). Ela se abre apenas onde há,
    para aquele par, decisão dessa espécie ainda não cumprida — e é por isso que a pergunta é feita
    ao panorama, que já a respondeu para a Etapa inteira numa consulta só, e não ao banco por linha.
    """
    if estado != REAVALIACAO:
        return None
    return next(
        (
            decisao
            for (identidade, _etapa), decisao in panorama["reavaliacoes"].items()
            if identidade == inscricao.id
        ),
        None,
    )


def _conclusao_a_consolidar(panorama, inscricao, cumprindo):
    """A conclusão elegível — e, no cumprimento, a **nova** avaliação, que pode ainda não existir.

    Determinar reavaliação não a produz: alguém precisa avaliar. **A avaliação que fundamentou o
    Resultado protegido é excluída aqui**, e não deixada para a trigger: sem isso, consolidar em
    cumprimento reconsolidaria a mesma nota como se fosse a reavaliação, e o que chegaria ao
    operador seria um erro de banco em vez da frase que diz o que falta.

    Mais de uma nova é o mesmo caso ambíguo de sempre — escolher uma seria o sistema decidindo qual
    nota vale.
    """
    conclusoes = panorama["elegiveis"].get(inscricao.id, [])
    if cumprindo is not None:
        original = getattr(cumprindo.resultado_protegido, "avaliacao_id", None)
        conclusoes = [item for item in conclusoes if item.avaliacao_id != original]
    if len(conclusoes) != 1:
        return None
    return conclusoes[0]


def _pioraria(cumprindo, efeito, conclusao):
    from processo_seletivo.recursos.domain.pejus import piora

    protegido = cumprindo.resultado_protegido
    if protegido is None:
        return False
    return piora(protegido=protegido, consequencia=efeito, pontuacao=conclusao.pontuacao)


def consolidar(
    *, actor, processo_id, edital_id, etapa_id, inscricao_ids, idempotency_key, correlation_id
):
    """Cria o Resultado das inscrições prontas, e declara por que as demais ficaram de fora."""
    ids = [identificador(i) for i in inscricao_ids]
    if not ids:
        raise DomainError(
            "selecao_vazia",
            "Selecione ao menos uma inscrição para consolidar.",
            422,
            campo="inscricao_id",
        )
    with comando_de_comissao(
        actor=actor,
        processo_id=processo_id,
        operation=ATO,
        payload={"etapa": str(etapa_id), "inscricoes": sorted(str(i) for i in ids)},
        idempotency_key=idempotency_key,
    ) as ctx:
        edital = _edital_do_processo(ctx.processo, edital_id)
        if ctx.repetido:
            # Antes de qualquer trabalho: a repetição devolve o desfecho original, e não um
            # recálculo que responderia "zero criados" sobre um estado que já mudou (FR-021).
            return ctx.desfecho_anterior
        etapa, vigentes, conteudo = _etapa_vigente_ou_404(edital, etapa_id)

        # **Uma leitura do panorama, antes do laço.** Elegíveis, Resultados existentes e conjuntos
        # da progressão saem daqui; dentro do laço não há consulta nenhuma.
        panorama = panorama_da_etapa(
            edital=edital, etapa=etapa, etapas_vigentes=vigentes, conteudo=conteudo
        )
        impedimento = panorama["impedimento_da_etapa"]
        if impedimento is not None:
            # Impedimento da **Etapa inteira** é erro do pedido: nenhuma inscrição dela pode ser
            # consolidada, e recusar linha a linha repetiria a mesma frase mil vezes (FR-015).
            raise DomainError(impedimento[0], impedimento[1].capitalize() + ".", 422)
        inscricoes = _inscricoes_da_selecao(edital, ids, panorama)

        criados, recusas = [], []
        for inscricao in inscricoes:
            estado, motivo = panorama["estados"][inscricao.id]
            cumprindo = _decisao_a_cumprir(panorama, inscricao, estado)
            if estado != PRONTA and cumprindo is None:
                recusas.append(Recusa(inscricao, motivo))
                continue
            conclusao = _conclusao_a_consolidar(panorama, inscricao, cumprindo)
            if conclusao is None:
                recusas.append(Recusa(inscricao, SEM_REAVALIACAO))
                continue
            efeito, causa = consequencia(etapa, conclusao)
            if cumprindo is not None and _pioraria(cumprindo, efeito, conclusao):
                # **A vedação de piora alcança este caminho** (FR-073). A nova Avaliação fica
                # registrada — ela é o juízo do avaliador, e apagá-la seria mentir sobre o que ele
                # concluiu —, mas o seu Resultado não vira sucessor. Sem isto, a reavaliação
                # ordenada seria a porta dos fundos da *non reformatio*.
                recusas.append(Recusa(inscricao, PIORARIA))
                continue
            resultado = ResultadoEtapa.objects.create(
                inscricao=inscricao,
                edital=edital,
                etapa_id=etapa["id"],
                origem=ResultadoEtapa.Origem.AVALIACAO,
                # A identidade basta: o Resultado guarda a chave estrangeira, e materializar o
                # modelo da fonte para gravá-la traria o Edital inteiro em JSON junto (T-011).
                avaliacao_id=conclusao.avaliacao_id,
                # A versão **da fonte**, copiada e não inventada: a trigger recusa qualquer outra.
                # Pela mesma razão que acima, a identidade basta — materializar a Versão
                # Consolidada traria o Edital inteiro em JSON por linha do lote (D-1).
                versao_id=conclusao.versao_id,
                # A conclusão é **copiada conforme a forma**, e não convertida: o indeferimento
                # não vira zero, e a nota não vira sentido (013, D-008, FR-016).
                forma=conclusao.forma,
                pontuacao=conclusao.pontuacao,
                sentido=conclusao.sentido,
                consequencia=efeito,
                motivo=causa,
                consolidado_em=ctx.now,
                consolidado_por=actor.subject,
                # A **exceção única**: fora do cumprimento de decisão, estes três campos são vazios
                # e a consolidação continua recusando o par que já tem Resultado vigente (FR-055).
                resultado_anterior=(
                    cumprindo.resultado_protegido if cumprindo is not None else None
                ),
                motivo_da_superacao=(
                    MOTIVO_DA_REAVALIACAO.format(protocolo=cumprindo.recurso.protocolo)
                    if cumprindo is not None
                    else ""
                ),
                decisao=cumprindo,
            )
            criados.append(resultado)
            # Um evento por Resultado, inclusive no lote: a trilha responde por agregado, e "qual
            # foi a consequência desta inscrição, e quem a produziu" é a pergunta que ela existe
            # para responder. **Sem pontuação e sem parecer** — a assinatura de `auditar` não tem
            # por onde eles caberem, e a omissão é de projeto (FR-040).
            auditar(
                actor=actor,
                permissao=ctx.base.permissao,
                operation=CONSOLIDAR,
                aggregate=resultado,
                now=ctx.now,
                correlation_id=correlation_id,
                reason=(
                    f"Resultado da Etapa {etapa.get('name') or etapa['id']} para a inscrição "
                    f"{inscricao.protocolo or inscricao.id}: {efeito.lower()}."
                ),
                idempotency_key=idempotency_key,
            )
        declarado = resultado_declarado(criados, recusas, "consolidada")
        ctx.concluir_sem_resultado(201, declarado)
        return declarado


__all__ = ["ATO", "CONSOLIDAR", "Recusa", "consolidar"]
