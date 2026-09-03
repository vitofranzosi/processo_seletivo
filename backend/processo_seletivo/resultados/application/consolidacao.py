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

from processo_seletivo.avaliacoes.application.distribuicao import resultado_declarado
from processo_seletivo.avaliacoes.application.trilha import auditar
from processo_seletivo.comissoes.application import comando_de_comissao, nao_encontrado
from processo_seletivo.comissoes.application.comissao import identificador
from processo_seletivo.comissoes.domain.etapas import etapas_vigentes
from processo_seletivo.inscricoes.models import Inscricao
from processo_seletivo.processos.models import Edital
from processo_seletivo.resultados.application.prontidao import PRONTA, panorama_da_etapa
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
    vigentes = etapas_vigentes(edital)
    etapa = vigentes.get(identificador(etapa_id))
    if etapa is None:
        raise nao_encontrado()
    return etapa, vigentes


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
        raise DomainError(
            "inscricao_fora_da_etapa",
            "Uma ou mais inscrições selecionadas não participam desta Etapa: elas foram "
            "eliminadas numa Etapa anterior ou ainda aguardam o resultado da anterior.",
            422,
            campo="inscricao_id",
        )
    return inscricoes


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
        etapa, vigentes = _etapa_vigente_ou_404(edital, etapa_id)

        # **Uma leitura do panorama, antes do laço.** Elegíveis, Resultados existentes e conjuntos
        # da progressão saem daqui; dentro do laço não há consulta nenhuma.
        panorama = panorama_da_etapa(edital=edital, etapa=etapa, etapas_vigentes=vigentes)
        impedimento = panorama["impedimento_da_etapa"]
        if impedimento is not None:
            # Impedimento da **Etapa inteira** é erro do pedido: nenhuma inscrição dela pode ser
            # consolidada, e recusar linha a linha repetiria a mesma frase mil vezes (FR-015).
            raise DomainError(impedimento[0], impedimento[1].capitalize() + ".", 422)
        inscricoes = _inscricoes_da_selecao(edital, ids, panorama)

        criados, recusas = [], []
        for inscricao in inscricoes:
            estado, motivo = panorama["estados"][inscricao.id]
            if estado != PRONTA:
                recusas.append(Recusa(inscricao, motivo))
                continue
            avaliacao = panorama["elegiveis"][inscricao.id][0]
            efeito, causa = consequencia(etapa, avaliacao.pontuacao)
            resultado = ResultadoEtapa.objects.create(
                inscricao=inscricao,
                edital=edital,
                etapa_id=etapa["id"],
                avaliacao=avaliacao,
                pontuacao=avaliacao.pontuacao,
                consequencia=efeito,
                motivo=causa,
                consolidado_em=ctx.now,
                consolidado_por=actor.subject,
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
