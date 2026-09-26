"""A lista exigida: gravar no envio, ler depois, reconstruir o que não foi gravado (044).

**Nenhum leitor de inscrição enviada recalcula o recorte fora daqui.** A Mesa, a consulta
administrativa e a inscrição enviada no portal leem por `lista_exigida`, e é isso que faz os três
mostrarem o mesmo — o que foi pedido no envio, e não o que a regra de hoje pediria.

**A inscrição em rascunho não passa por aqui.** Ela continua lendo a versão vigente, porque ainda
não pediu nada a ninguém: a lista nasce no ato do envio, e só nele.
"""

from dataclasses import dataclass

from processo_seletivo.editais.domain.documentos import (
    NAO_SE_APLICA,
    Recorte,
    Veredito,
    aplicabilidade,
)
from processo_seletivo.inscricoes.models import ItemDaListaExigida


@dataclass(frozen=True)
class ListaExigida:
    """Os vereditos de uma inscrição enviada, e se eles foram gravados ou reconstruídos."""

    itens: list[Veredito]
    reconstruida: bool

    @property
    def pedidos(self) -> list[Veredito]:
        return [item for item in self.itens if item.situacao != NAO_SE_APLICA]

    @property
    def nao_se_aplicam(self) -> list[Veredito]:
        return [item for item in self.itens if item.situacao == NAO_SE_APLICA]


def gravar_lista_exigida(inscricao, *, versao, agora):
    """Um item por Documento Exigido da versão aceita, na transação do envio (FR-714).

    Recebe a **mesma** `versao` e o **mesmo** `agora` que o ato gravou na inscrição: o gatilho de
    coerência recusa outra versão e outro instante, e é isso que prende a lista ao envio mesmo com
    uma Retificação publicada no meio dele.

    Só o envio e a semente chamam esta função (D-004, R-005). Um teste varre o código e confere.
    """
    vereditos = aplicabilidade(
        versao.content,
        profile_id=str(inscricao.profile_id),
        modality_id=None if inscricao.modality_id is None else str(inscricao.modality_id),
    )
    ItemDaListaExigida.objects.bulk_create(
        [
            ItemDaListaExigida(
                inscricao=inscricao,
                versao=versao,
                requisito_id=veredito.requisito["id"],
                chave=veredito.requisito.get("key", ""),
                situacao=veredito.situacao,
                forma_do_recorte=veredito.recorte.forma,
                perfil_id=veredito.recorte.perfil_id,
                modalidade_id=veredito.recorte.modalidade_id,
                modalidade_codigo=veredito.recorte.modalidade_codigo or "",
                divergente_do_publicado=veredito.divergente_do_publicado,
                gravada_em=agora,
            )
            for veredito in vereditos
        ]
    )


def lista_exigida(inscricao, conteudo, *, itens=None) -> ListaExigida:
    """A lista de uma inscrição enviada, sobre o conteúdo da versão que ela aceitou.

    Com itens gravados, lê os itens. Sem eles — inscrição enviada antes da `044` —, reconstrói pela
    regra única e diz que reconstruiu (FR-726). `itens` permite a quem lê muitas inscrições
    carregá-los de uma vez (`listas_exigidas`).
    """
    gravados = list(inscricao.lista_exigida.all()) if itens is None else itens
    if not gravados:
        return ListaExigida(
            aplicabilidade(
                conteudo,
                profile_id=str(inscricao.profile_id),
                modality_id=None if inscricao.modality_id is None else str(inscricao.modality_id),
            ),
            reconstruida=True,
        )
    requisitos = {
        str(requisito.get("id")): requisito
        for requisito in conteudo.get("documentRequirements") or []
    }
    vereditos = [
        Veredito(
            # O documento como está na versão aceita — é dali que vêm nome e instrução. A versão é
            # imutável e está na linha, e ler o nome dela não é recalcular recorte.
            requisitos.get(str(item.requisito_id))
            or {"id": str(item.requisito_id), "key": item.chave, "name": item.chave},
            item.situacao,
            Recorte(
                item.forma_do_recorte,
                perfil_id=None if item.perfil_id is None else str(item.perfil_id),
                modalidade_id=None if item.modalidade_id is None else str(item.modalidade_id),
                modalidade_codigo=item.modalidade_codigo or None,
            ),
            item.divergente_do_publicado,
        )
        for item in gravados
    ]
    vereditos.sort(key=lambda veredito: veredito.requisito.get("order", 0))
    return ListaExigida(vereditos, reconstruida=False)


def listas_exigidas(inscricoes, conteudo_de) -> dict:
    """As listas de várias inscrições com **uma** consulta, e não uma por linha (R-006).

    `conteudo_de` recebe a inscrição e devolve o conteúdo da versão que ela aceitou. É o que mantém
    a lista "Inscrições recebidas" com o mesmo número de consultas para 5 e para 300 inscrições.
    """
    por_inscricao = {}
    for item in ItemDaListaExigida.objects.filter(
        inscricao_id__in=[inscricao.pk for inscricao in inscricoes]
    ):
        por_inscricao.setdefault(item.inscricao_id, []).append(item)
    return {
        inscricao.pk: lista_exigida(
            inscricao, conteudo_de(inscricao), itens=por_inscricao.get(inscricao.pk, [])
        )
        for inscricao in inscricoes
    }
