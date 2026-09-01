"""A fonte única de Etapas da 011.

Toda leitura de Etapa desta feature passa por aqui — criar alocação, listar a organização,
montar `Minhas Etapas` e autorizar o acesso. É isso que torna verdadeiro por construção o critério
de que uma Etapa alocável é exatamente uma Etapa que aparecerá para quem foi alocado (SC-021): as
duas perguntas passam pelo mesmo código.

**Nunca consultar `edital.etapas`.** Aquela é a coleção de elaboração, e ela diverge do conteúdo
vigente depois de uma Retificação — que pode remover Etapa e pode acrescentar Etapa sem linha
correspondente (D-002, D-012).
"""

from uuid import UUID

from processo_seletivo.publicacoes.application.selectors import effective_version
from processo_seletivo.shared.api.problems import DomainError


def sem_versao_vigente():
    """O Edital nunca foi publicado, então não há Etapa a alocar (FR-032, EC-014).

    Erro do domínio, e não subclasse: `DomainError` é dataclass, e o projeto inteiro a levanta
    com código e mensagem em vez de derivá-la.
    """
    return DomainError(
        "edital_sem_versao_vigente",
        "Este Edital ainda não foi publicado: suas Etapas não são alocáveis.",
        409,
    )


def conteudo_vigente(edital, *, at=None):
    """A Versão Consolidada vigente, ou a recusa de Edital não publicado."""
    try:
        return effective_version(edital_id=edital.id, at=at).content
    except DomainError as exc:
        if exc.code == "no_effective_version":
            raise sem_versao_vigente() from exc
        raise


def etapas_vigentes(edital, *, at=None):
    """As Etapas do conteúdo vigente, por identidade. Devolve `{UUID: dados}`."""
    return {
        UUID(etapa["id"]): etapa
        for etapa in (conteudo_vigente(edital, at=at).get("stages") or [])
    }


def evento_vigente(edital, evento_id, *, at=None):
    """O Evento de Cronograma do conteúdo vigente, ou `None`.

    Pela mesma razão que a Etapa: `EventoCronograma` é a linha de elaboração, e uma Retificação
    que mude as datas grava na Versão Consolidada sem escrever de volta nela. Ler a linha faria
    a tela mostrar o período superado — e Evento acrescentado por Retificação não tem linha
    nenhuma (D-012).
    """
    if not evento_id:
        return None
    alvo = str(evento_id)
    for evento in conteudo_vigente(edital, at=at).get("schedule") or []:
        if str(evento.get("id")) == alvo:
            return evento
    return None


def etapa_vigente(edital, etapa_id, *, at=None):
    """Uma Etapa, ou `None` quando a identidade não está no conteúdo vigente."""
    return etapas_vigentes(edital, at=at).get(_uuid(etapa_id))


def _uuid(valor):
    return valor if isinstance(valor, UUID) else UUID(str(valor))
