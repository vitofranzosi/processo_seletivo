"""As duas perguntas de autorização da 011, e nada além delas.

São duas porque são duas coisas: **gerir** a comissão e **atuar** numa Etapa. Nenhuma view decide
por conta própria — ela chama daqui para saber o que desenhar, e o comando chama daqui de novo,
dentro da transação, para decidir se grava (D-006, D-016).
"""

from dataclasses import dataclass

from django.db.models import Q

from processo_seletivo.comissoes.domain.etapas import etapa_vigente, etapas_vigentes
from processo_seletivo.comissoes.models import (
    AlocacaoAConferencia,
    AlocacaoEtapa,
    Funcao,
    MembroComissao,
)
from processo_seletivo.seguranca.application.authorization import (
    Base as BaseDaRecusa,
)
from processo_seletivo.seguranca.application.authorization import (
    base_de_permissao,
)
from processo_seletivo.shared.api.problems import DomainError

# A permissão sistêmica vive em `PAPEIS`; a presidência **não** — ela é vínculo, e este nome
# existe só para a trilha dizer qual base autorizou o ato (FR-016, D-011, D-014).
PERMISSAO_SISTEMICA = "comissao:gerir"
BASE_PRESIDENCIA = "comissao:presidir"
# **O nome da base que a alocação à conferência dá, e só isso** (115, D-010): não é capacidade do
# catálogo, nenhum papel a concede, e ela existe para a trilha dizer por que o ato foi admitido.
BASE_CONFERENCIA = "comissao:conferir_documentos"

# --- As mesmas duas bases, ditas como recusa (033, `FR-486`) ------------------------------------
#
# **São o predicado de `pode_gerir_comissao` escrito para quem recebe a negativa**, e moram aqui —
# junto dele — porque a interface deixou de ser a única a perguntá-lo: o ato de instrução do recurso
# recusa **dentro da transação**, e importar a constante da camada de views seria ciclo. Definir o
# par nos dois lugares criaria a segunda formulação que a `FR-486` existe para não haver, e a cópia
# divergiria na primeira palavra que alguém melhorasse (036).
#
# **O conjunto aceito continua sendo de quem chama**, que é o que a `FR-489` prende: este módulo
# oferece o par; nenhuma porta é obrigada a usá-lo, e as que têm modo compõem o seu.
#
# A presidência é a única que não nasce de `base_de_permissao`, e a diferença é o ponto da `FR-485`:
# ela **não é papel**, vem da composição da comissão, e nenhum papel a concede. Mandar pedir "o
# papel de presidente" mandaria pedir o que não existe.
BASE_DE_GESTAO_DA_COMISSAO = base_de_permissao("gerir a comissão")
BASE_DA_PRESIDENCIA_DO_PROCESSO = BaseDaRecusa(
    "a presidência deste Processo", "a quem preside este Processo"
)
BASES_DA_GESTAO_DA_COMISSAO = (BASE_DE_GESTAO_DA_COMISSAO, BASE_DA_PRESIDENCIA_DO_PROCESSO)
# A terceira base, só da conferência dos documentos da convocação (115, FR-3595).
BASE_DA_ALOCACAO_A_CONFERENCIA = BaseDaRecusa(
    "a conferência dos documentos da convocação deste Edital",
    "a quem a presidência alocou à conferência",
)
BASES_DA_CONFERENCIA = (*BASES_DA_GESTAO_DA_COMISSAO, BASE_DA_ALOCACAO_A_CONFERENCIA)


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


def pode_conferir_documentos(ator, edital, perfil_id):
    """**O predicado único** da conferência dos documentos da convocação (115, FR-3595, D-010).

    Toda leitura de documento da convocação, toda entrega de arquivo e todo registro de conferência
    na gestão passam por aqui. Três bases, cada uma suficiente sozinha: as duas que já desfecham —
    a permissão sistêmica e a presidência —, e a alocação à conferência, que alcança o Perfil da
    convocação quando não é restrita ou quando é restrita a ele.

    **Muda a regra, e não o dado**, quando o multiunidade chegar (§7 do complemento): é aqui que
    "designado no Perfil, com a unidade ofertante dele" entrará, e nenhuma tela precisará saber.
    """
    if ator is None or edital is None:
        return None
    processo = edital.processo
    base = pode_gerir_comissao(ator, processo)
    if base is not None:
        return base
    membro = membro_ativo(ator, processo)
    if membro is None:
        return None
    alocada = (
        AlocacaoAConferencia.objects.filter(membro=membro, edital=edital, ativo=True)
        .filter(Q(perfil_id__isnull=True) | Q(perfil_id=perfil_id))
        .exists()
    )
    return Base(BASE_CONFERENCIA) if alocada else None


def perfis_da_conferencia(ator, edital):
    """Os Perfis que este ator confere neste Edital: `None` é todos, conjunto vazio é nenhum.

    A mesma regra do predicado, respondida para a lista inteira da condução numa leitura só — chamar
    o predicado por linha faria dele o gargalo da tela.
    """
    if ator is None or edital is None:
        return set()
    processo = edital.processo
    if pode_gerir_comissao(ator, processo) is not None:
        return None
    membro = membro_ativo(ator, processo)
    if membro is None:
        return set()
    perfis = set(
        AlocacaoAConferencia.objects.filter(membro=membro, edital=edital, ativo=True).values_list(
            "perfil_id", flat=True
        )
    )
    if None in perfis:
        return None
    return {str(perfil) for perfil in perfis}


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


def etapas_autorizadas(ator, edital):
    """Todas as Etapas deste Edital em que esta identidade pode atuar, numa leitura só.

    `pode_atuar_na_etapa` responde por uma Etapa e custa duas a três consultas. A 012 vai
    desenhar listas — candidatos às dezenas, cada linha precisando saber se o ator alcança a
    Etapa dela — e chamar o guard por linha faria dele o gargalo da feature seguinte. Esta é a
    mesma regra, respondida para o conjunto: quem constrói uma lista chama isto uma vez e
    filtra em memória.

    Devolve um `set` de identificadores. Conjunto vazio significa "nenhuma", e nunca "todas".
    """
    processo = edital.processo
    if ator is None or ator.institution_scope != processo.institution_scope:
        return set()
    membro = membro_ativo(ator, processo)
    if membro is None:
        return set()
    alocadas = set(
        AlocacaoEtapa.objects.filter(membro=membro, edital=edital, ativo=True).values_list(
            "etapa_id", flat=True
        )
    )
    if not alocadas:
        return set()
    try:
        vigentes = set(etapas_vigentes(edital))
    except DomainError:
        return set()
    # A alocação órfã não concede acesso, aqui pela mesma razão que lá (FR-047).
    return alocadas & vigentes
