"""As duas perguntas de autorização da 011, e nada além delas.

São duas porque são duas coisas: **gerir** a comissão e **atuar** numa Etapa. Nenhuma view decide
por conta própria — ela chama daqui para saber o que desenhar, e o comando chama daqui de novo,
dentro da transação, para decidir se grava (D-006, D-016).
"""

from dataclasses import dataclass

from processo_seletivo.comissoes.domain.etapas import etapa_vigente
from processo_seletivo.comissoes.models import AlocacaoEtapa, Funcao, MembroComissao
from processo_seletivo.shared.api.problems import DomainError

# A permissão sistêmica vive em `PAPEIS`; a presidência **não** — ela é vínculo, e este nome
# existe só para a trilha dizer qual base autorizou o ato (FR-016, D-011, D-014).
PERMISSAO_SISTEMICA = "comissao:gerir"
BASE_PRESIDENCIA = "comissao:presidir"


@dataclass(frozen=True)
class Base:
    """Qual das duas bases autorizou. É o que a auditoria registra."""

    permissao: str

    @property
    def e_sistemica(self):
        return self.permissao == PERMISSAO_SISTEMICA


def membro_ativo(ator, processo):
    if ator is None or not getattr(ator, "subject", ""):
        return None
    return MembroComissao.objects.filter(
        processo=processo, identity_subject=ator.subject, ativo=True
    ).first()


def pode_gerir_comissao(ator, processo):
    """A base que autoriza gerir esta comissão, ou `None`.

    Duas bases, cada uma suficiente sozinha: a permissão sistêmica — que é como a comissão é
    constituída e como a administração superior intervém — ou a presidência **deste** Processo.
    Exigir as duas faria o presidente depender do papel de gestor, o que a seção 11 da spec
    recusa; aceitar qualquer papel global faria a presidência valer em todo Processo, o que o
    SC-011 recusa.
    """
    if ator is None or ator.institution_scope != processo.institution_scope:
        return None
    if ator.can(PERMISSAO_SISTEMICA):
        return Base(PERMISSAO_SISTEMICA)
    membro = membro_ativo(ator, processo)
    if membro is not None and membro.funcao == Funcao.PRESIDENTE:
        return Base(BASE_PRESIDENCIA)
    return None


def pode_atuar_na_etapa(ator, edital, etapa_id):
    """Se esta identidade pode abrir esta Etapa como atribuição sua.

    Não consulta função nem permissão, de propósito: presidir não é atuar, e privilégio
    administrativo não injeta Etapa em `Minhas Etapas` (FR-012, FR-044). Quem chega por gestão
    chega pela outra porta, e a página diz por qual delas foi.
    """
    processo = edital.processo
    if ator is None or ator.institution_scope != processo.institution_scope:
        return False
    membro = membro_ativo(ator, processo)
    if membro is None:
        return False
    alocada = AlocacaoEtapa.objects.filter(
        membro=membro, edital=edital, etapa_id=etapa_id, ativo=True
    ).exists()
    if not alocada:
        return False
    # A alocação órfã não concede acesso: a identidade precisa estar no conteúdo vigente
    # (FR-047, EC-011). Um guard nunca levanta — Edital sem versão vigente é ausência de
    # autorização, e não erro a exibir.
    try:
        return etapa_vigente(edital, etapa_id) is not None
    except DomainError:
        return False
