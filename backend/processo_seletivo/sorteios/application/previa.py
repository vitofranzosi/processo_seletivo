"""A prévia **da relação**, e nunca da ordem (021, FR-030, D-010).

**O que esta leitura deliberadamente não faz.** Ela não calcula chave, não ordena e não devolve
posição nenhuma. Uma prévia da ordem depois de conhecida a semente seria o ensaio que a feature
existe para impedir; antes da semente ela nem existiria. O que a tela precisa mostrar é o
**universo** — quem entra, com que número — e o estado do compromisso de cada recorte.
"""

from processo_seletivo.inscricoes.models import Inscricao
from processo_seletivo.publicacoes.application.selectors import effective_version
from processo_seletivo.shared.api.problems import DomainError
from processo_seletivo.sorteios.application.selectors import relacao_vigente
from processo_seletivo.sorteios.domain import metodo as dominio_do_metodo
from processo_seletivo.sorteios.domain import projecao


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
    listas = [(None, "Ampla concorrência")] + [
        (str(modalidade.get("id")), modalidade.get("name") or "")
        for modalidade in perfil.get("competitionModalities") or []
    ]
    return {
        "perfil": perfil,
        "marco": marco,
        "metodo": metodo,
        "metodo_hash": dominio_do_metodo.resumo_do_metodo(metodo) if metodo else "",
        "recortes": [
            _recorte(edital, perfil_id, marco_id, lista_id, nome, submetidas)
            for lista_id, nome in listas
        ],
    }


def _recorte(edital, perfil_id, marco_id, lista_id, nome, submetidas):
    vigente = relacao_vigente(
        edital=edital, perfil_id=perfil_id, marco_id=marco_id, lista_id=lista_id
    )
    projetados = projecao.numerar(projecao.elegiveis(submetidas, lista_id=lista_id))
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
