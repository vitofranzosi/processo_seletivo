"""A prévia **da relação**, e nunca da ordem (021, FR-030, D-010).

**O que esta leitura deliberadamente não faz.** Ela não calcula chave, não ordena e não devolve
posição nenhuma. Uma prévia da ordem depois de conhecida a semente seria o ensaio que a feature
existe para impedir; antes da semente ela nem existiria. O que a tela precisa mostrar é o
**universo** — quem entra, com que número — e o estado do compromisso de cada recorte.
"""

from processo_seletivo.inscricoes.models import Inscricao
from processo_seletivo.publicacoes.application.selectors import effective_version
from processo_seletivo.shared.api.problems import DomainError
from processo_seletivo.sorteios.application.habilitacao import habilitadas_na_etapa
from processo_seletivo.sorteios.application.selectors import relacao_vigente
from processo_seletivo.sorteios.domain import metodo as dominio_do_metodo
from processo_seletivo.sorteios.domain import projecao, substituicao


def recortes_do_marco(*, edital, perfil_id, marco_id, at=None):
    """O marco, o método publicado e o estado de cada recorte — ampla concorrência e reservas."""
    versao = effective_version(edital_id=edital.id, at=at)
    perfil, marco = _perfil_e_marco(versao.content, perfil_id, marco_id)
    metodo = dominio_do_metodo.metodo_declarado(
        versao.content, perfil_id=perfil_id, marco_id=marco_id
    )
    submetidas = list(
        Inscricao.objects.filter(
            edital=edital, profile_id=perfil_id, status=Inscricao.Status.SUBMETIDA
        )
    )
    # **A mesma regra de quem entra que a publicação aplica** (FR-002, R-012). A prévia projetava
    # sem o filtro da Etapa de habilitação: onde o Edital declara uma, a comissão via um número e
    # congelava outro, sem que nada explicasse a diferença.
    habilitadas = habilitadas_na_etapa(edital, metodo)
    ocorrencia_da_vez, proxima_referencia, descartadas = _ocorrencia_declarada(metodo)
    listas = [(None, "Ampla concorrência")] + [
        (str(modalidade.get("id")), modalidade.get("name") or "")
        for modalidade in perfil.get("competitionModalities") or []
    ]
    return {
        "perfil": perfil,
        "marco": marco,
        "metodo": metodo,
        # A ocorrência da vez — a declarada, ou a que a regra de substituição pôs no lugar dela —,
        # a referência que ainda falta observar, e as que a indisponibilidade descartou. A tela as
        # exibe para que a semente esteja **à vista antes do ato**, e para que o descarte fique
        # visível: é o controle da R-006.
        "ocorrencia": ocorrencia_da_vez,
        "proxima_referencia": proxima_referencia,
        "ocorrencias_descartadas": descartadas,
        "metodo_hash": dominio_do_metodo.resumo_do_metodo(metodo) if metodo else "",
        "recortes": [
            _recorte(edital, perfil_id, marco_id, lista_id, nome, submetidas, habilitadas)
            for lista_id, nome in listas
        ],
    }


def _ocorrencia_declarada(metodo):
    """A ocorrência que a regra publicada manda usar **agora**, se já foi observada.

    **Não é mais "a declarada", e a diferença é a regra de substituição funcionando** (FR-015). A
    tela lia sempre a referência declarada no Edital: registrada uma indisponibilidade, ela
    continuava mostrando aquela linha, o botão de observar sumia — porque a ocorrência "existia" —
    e o sorteio ficava travado para sempre. Agora ela pergunta à regra qual é a vez, e a resposta é
    derivada, não escolhida.
    """
    from processo_seletivo.sorteios.models import OcorrenciaDaFonte

    if not metodo:
        return None, "", []
    fonte = metodo.get("source", "")
    registradas = list(OcorrenciaDaFonte.objects.filter(fonte=fonte))
    indisponiveis = {o.referencia for o in registradas if o.indisponivel}
    try:
        proxima = substituicao.proxima_a_observar(metodo, indisponiveis)
    except DomainError as esgotada:
        return (
            None,
            "",
            [
                {"referencia": o.referencia, "evidencia": o.evidencia, "motivo": esgotada.detail}
                for o in registradas
                if o.indisponivel
            ],
        )
    atual = next((o for o in registradas if o.referencia == proxima), None)
    descartadas = [
        {"referencia": o.referencia, "evidencia": o.evidencia}
        for o in registradas
        if o.indisponivel and o.referencia != proxima
    ]
    return atual, proxima, descartadas


def _recorte(edital, perfil_id, marco_id, lista_id, nome, submetidas, habilitadas):
    vigente = relacao_vigente(
        edital=edital, perfil_id=perfil_id, marco_id=marco_id, lista_id=lista_id
    )
    projetados = projecao.numerar(
        projecao.elegiveis(submetidas, lista_id=lista_id, habilitadas=habilitadas)
    )
    return {
        "lista_id": lista_id or "",
        "nome": nome,
        # Quantos entrariam **agora**, se a relação fosse publicada neste instante. Depois do
        # congelamento é a relação que manda, e a divergência entre os dois números é informação:
        # ela diz que um fato de origem mudou desde o compromisso.
        "projetados": len(projetados),
        "participantes": [
            {
                "numero": numero,
                "nome": inscricao.nome or "",
                "protocolo": inscricao.protocolo or "",
            }
            for numero, inscricao in projetados
        ],
        "relacao": vigente,
        "congelada": vigente is not None,
        "sorteio": getattr(vigente, "sorteios", None) and vigente.sorteios.first(),
    }


def _perfil_e_marco(conteudo, perfil_id, marco_id):
    for perfil in conteudo.get("profiles") or []:
        if str(perfil.get("id")) != str(perfil_id):
            continue
        for marco in perfil.get("classificationMilestones") or []:
            if str(marco.get("id")) == str(marco_id):
                return perfil, marco
    raise DomainError("not_found", "Recurso não encontrado.", 404)


__all__ = ["recortes_do_marco"]
