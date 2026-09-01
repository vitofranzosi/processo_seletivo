"""As leituras da 011: a organização do trabalho e a área pessoal de quem trabalha.

Toda Etapa vem de `etapas_vigentes()`, e a alocação órfã é **derivada na leitura** — comparação da
alocação com o conteúdo vigente, sem campo, sem sincronizador e sem cópia da Etapa (FR-047).
"""

from processo_seletivo.comissoes.domain.etapas import etapas_vigentes
from processo_seletivo.comissoes.models import AlocacaoEtapa, Funcao, MembroComissao
from processo_seletivo.processos.models import Edital
from processo_seletivo.shared.api.problems import DomainError


def _etapas_ou_nada(edital):
    """As Etapas vigentes, ou `None` quando o Edital ainda não foi publicado."""
    try:
        return etapas_vigentes(edital)
    except DomainError:
        return None


def membros(processo):
    return list(
        MembroComissao.objects.filter(processo=processo, ativo=True).order_by(
            "funcao", "identity_subject"
        )
    )


def tem_presidente(processo):
    return MembroComissao.objects.filter(
        processo=processo, ativo=True, funcao=Funcao.PRESIDENTE
    ).exists()


def editais_alocaveis(processo):
    """Os Editais do Processo que já têm conteúdo vigente, na ordem da tela."""
    return list(Edital.objects.filter(processo=processo).order_by("year", "number"))


def organizacao(processo):
    """Por Edital, e depois por Etapa — porque a Etapa pertence ao Edital (D-001).

    Dois Editais do mesmo Processo podem ter Etapas homônimas; sem o Edital antes, a tela
    apresentaria dois objetos distintos com o mesmo nome (EC-012).
    """
    alocacoes = list(
        AlocacaoEtapa.objects.filter(membro__processo=processo, ativo=True).select_related(
            "membro", "edital"
        )
    )
    por_etapa = {}
    for alocacao in alocacoes:
        por_etapa.setdefault((alocacao.edital_id, alocacao.etapa_id), []).append(alocacao)

    resultado = []
    for edital in editais_alocaveis(processo):
        vigentes = _etapas_ou_nada(edital)
        if vigentes is None:
            # Estado vazio de "não há Edital publicado" — distinto do de "o Edital publicado não
            # tem Etapas" (EC-008, EC-014).
            resultado.append({"edital": edital, "publicado": False, "etapas": []})
            continue
        etapas = []
        for etapa_id, dados in vigentes.items():
            do_grupo = por_etapa.get((edital.id, etapa_id), [])
            etapas.append(
                {
                    "id": etapa_id,
                    "nome": dados.get("name", ""),
                    "ordem": dados.get("order", 0),
                    "alocacoes": do_grupo,
                    "total": len(do_grupo),
                    "sem_membros": not do_grupo,
                }
            )
        etapas.sort(key=lambda e: (e["ordem"], e["nome"]))
        resultado.append({"edital": edital, "publicado": True, "etapas": etapas})
    return resultado


def orfas(processo):
    """Alocações ativas cuja Etapa não está mais no conteúdo vigente (EC-011).

    Derivadas aqui, e não persistidas: o que torna a alocação órfã é a identidade sair do
    conteúdo vigente, e não o conteúdo da Etapa mudar.
    """
    vigentes_por_edital = {}
    encontradas = []
    for alocacao in AlocacaoEtapa.objects.filter(
        membro__processo=processo, ativo=True
    ).select_related("membro", "edital"):
        if alocacao.edital_id not in vigentes_por_edital:
            vigentes_por_edital[alocacao.edital_id] = _etapas_ou_nada(alocacao.edital)
        vigentes = vigentes_por_edital[alocacao.edital_id]
        if vigentes is None or alocacao.etapa_id not in vigentes:
            encontradas.append(alocacao)
    return encontradas


def etapas_do_membro(membro):
    """As Etapas de uma pessoa, com o Edital de cada uma (FR-040)."""
    return _atribuicoes(
        AlocacaoEtapa.objects.filter(membro=membro, ativo=True).select_related("edital")
    )


def minhas_etapas(ator):
    """Todos e somente os objetos com alocação ativa desta identidade, no escopo dela (FR-043).

    Sem exceção por papel: privilégio administrativo não injeta Etapa aqui (FR-044, D-006).
    """
    if ator is None or not getattr(ator, "subject", ""):
        return []
    alocacoes = AlocacaoEtapa.objects.filter(
        ativo=True,
        membro__ativo=True,
        membro__identity_subject=ator.subject,
        membro__processo__institution_scope=ator.institution_scope,
    ).select_related("edital", "edital__processo", "membro")
    return _atribuicoes(alocacoes)


def _atribuicoes(alocacoes):
    vigentes_por_edital = {}
    itens = []
    for alocacao in alocacoes:
        if alocacao.edital_id not in vigentes_por_edital:
            vigentes_por_edital[alocacao.edital_id] = _etapas_ou_nada(alocacao.edital)
        vigentes = vigentes_por_edital[alocacao.edital_id] or {}
        dados = vigentes.get(alocacao.etapa_id)
        if dados is None:
            # A órfã não aparece para quem foi alocado: ela não concede acesso (FR-047).
            continue
        itens.append(
            {
                "alocacao": alocacao,
                "edital": alocacao.edital,
                "processo": alocacao.edital.processo,
                "etapa_id": alocacao.etapa_id,
                "nome": dados.get("name", ""),
                "ordem": dados.get("order", 0),
            }
        )
    itens.sort(key=lambda i: (i["edital"].year, _numero(i["edital"].number), i["ordem"]))
    return itens


def _numero(valor):
    """`number` é texto, então "11" viria antes de "2" numa ordenação lexicográfica."""
    bruto = (valor or "").strip()
    return (0, int(bruto), "") if bruto.isdigit() else (1, 0, bruto)
