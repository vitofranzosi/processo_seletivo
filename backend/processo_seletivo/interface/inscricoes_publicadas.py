"""A tela "Publicações das inscrições" — histórico, próximo ato, prévia e confirmação (148, UX-460).

**Uma tela, e não três.** A comissão precisa saber qual ato publicar, quando pode, quantas
inscrições ele contempla, o que o impede e o que acontece ao confirmar (FR-5432). As três naturezas
moram no mesmo lugar porque são a mesma cadeia: separá-las em telas obrigaria quem publica a
descobrir em qual delas está o próximo passo.

**A porta é a da divulgação de resultado** (`_edital_para_publicar`): publicar exige
`resultado:publicar`; a auditoria consulta e não publica (D-008, FR-5429). Fora do escopo, 404.

**A prévia é recomposta a cada GET, e não guardada.** Não há rascunho de publicação: sair da tela
não deixa nada para trás, e a assinatura da prévia é o que impede confirmar um mundo que mudou.
"""

from uuid import uuid4

from django.http import Http404
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_http_methods

from processo_seletivo.divulgacao.application import inscricoes as atos
from processo_seletivo.divulgacao.domain import inscricoes as dominio
from processo_seletivo.divulgacao.infrastructure.documento_das_inscricoes import (
    frase_da_natureza,
)
from processo_seletivo.interface import identidade
from processo_seletivo.shared.api.problems import DomainError
from processo_seletivo.shared.http import marcar_como_privada

CHAVE_DA_SESSAO = "inscricoes_publicadas_agora"

# O que cada natureza é, em uma frase para quem publica — a de quem consulta está no documento.
DESCRICOES = {
    dominio.RECEBIDAS: "Todas as inscrições enviadas no prazo, sem dizer se foram aceitas.",
    dominio.PRELIMINAR: "Deferidas e indeferidas pela análise das inscrições, com prazo de "
    "recurso. Pode mudar.",
    dominio.HOMOLOGACAO: "A relação final das inscrições aceitas, depois da análise e dos "
    "recursos. Não é classificação.",
}


@require_http_methods(["GET", "POST"])
def publicacoes_das_inscricoes(request, edital_id):
    from processo_seletivo.interface.views import _edital_para_publicar

    ator, edital, pode_publicar = _edital_para_publicar(request, edital_id, consulta=True)
    if ator is None:
        return identidade.pedir_identificacao(request)
    if request.method == "POST":
        return _publicar(request, ator, edital, pode_publicar)
    return _renderizar(
        request,
        ator,
        edital,
        pode_publicar,
        natureza=request.GET.get("natureza") or "",
        etapa_id=request.GET.get("etapa") or None,
    )


def _publicar(request, ator, edital, pode_publicar):
    natureza = request.POST.get("natureza", "")
    etapa_id = request.POST.get("etapa") or None
    try:
        ato = atos.publicar_inscricoes(
            actor=ator,
            edital_id=edital.id,
            natureza=natureza,
            etapa_id=etapa_id,
            prazo=request.POST.get("prazo", ""),
            motivo=request.POST.get("motivo", ""),
            autoridade=request.POST.get("autoridade", ""),
            confirmacao_da_previa=request.POST.get("confirmacao_da_previa", ""),
            idempotency_key=request.POST.get("chave_idempotencia") or uuid4().hex,
            correlation_id=getattr(request, "correlation_id", ""),
        )
    except DomainError as recusa:
        if recusa.status == 404:
            raise Http404 from recusa
        # A recusa volta à mesma tela, com o status que o contrato declara e a prévia recomposta —
        # é o que quem publica precisa para reconfirmar depois de uma prévia obsoleta.
        return _renderizar(
            request,
            ator,
            edital,
            pode_publicar,
            natureza=natureza,
            etapa_id=etapa_id,
            erro=recusa.detail,
            status=recusa.status,
        )
    request.session[CHAVE_DA_SESSAO] = str(ato.id)
    return redirect(reverse("interface:publicacoes-das-inscricoes", args=[edital.id]))


def _renderizar(request, ator, edital, pode_publicar, *, natureza, etapa_id, erro="", status=200):
    agora = timezone.now()
    cadeia = atos.cadeia(edital)
    vigente = cadeia[-1] if cadeia else None
    try:
        conteudo = atos.effective_version(edital_id=edital.id, at=agora).content
    except DomainError as recusa:
        # Edital não publicado: não há inscrição, e a tela não tem o que mostrar.
        raise Http404 from recusa
    etapas = dominio.etapas_de_analise(conteudo)
    escolhida = natureza if natureza in dominio.ROTULOS else _sugerida(vigente, etapas)
    opcoes = _opcoes(vigente, etapas, escolhida)
    disponivel = next(opcao for opcao in opcoes if opcao["valor"] == escolhida)["disponivel"]
    afericao = (
        atos.aferir(edital=edital, natureza=escolhida, etapa_id=etapa_id, at=agora)
        if disponivel
        else None
    )
    publicada_agora = request.session.pop(CHAVE_DA_SESSAO, None)
    from processo_seletivo.interface.views import _escolha_da_autoridade

    return marcar_como_privada(
        render(
            request,
            "interface/publicacoes_das_inscricoes.html",
            {
                "edital": edital,
                "processo": edital.processo,
                "cadeia": list(reversed(cadeia)),
                "vigente": vigente,
                "divergencia": atos.divergencia_do_vigente(edital, vigente, at=agora)
                if vigente is not None
                else None,
                "publicada_agora": publicada_agora,
                "opcoes": opcoes,
                "escolhida": escolhida,
                "rotulo_escolhida": dominio.ROTULOS[escolhida],
                "disponivel": disponivel,
                "afericao": afericao,
                "explicacao": frase_da_natureza(escolhida),
                "constam": dominio.CONSTAM[escolhida],
                "nao_constam": dominio.NAO_CONSTAM.get(escolhida, ""),
                # A prévia avisa por que a soma das listas passa do total (FR-5444, FR-5445).
                "tem_lista_reservada": afericao is not None
                and dominio.tem_lista_reservada(afericao.projecao.perfis),
                "frase_das_listas": dominio.FRASE_DAS_LISTAS,
                "escolher_etapa": _escolher_etapa(afericao, etapas),
                "pede_motivo": vigente is not None and vigente.natureza == escolhida,
                "pode_publicar": pode_publicar,
                "escolha_da_autoridade": _escolha_da_autoridade(edital) if pode_publicar else None,
                "sem_recurso": atos.SEM_RECURSO,
                "chave_idempotencia": uuid4().hex,
                "erro": erro,
            },
            status=status,
        )
    )


def _sugerida(vigente, etapas):
    """O próximo ato possível, dito pela cadeia — a comissão escolhe outro se quiser.

    Sem ato, a relação de recebidas, que todo Edital pode publicar. Depois dela, o preliminar quando
    há análise, e a homologação quando não há. Depois do preliminar, a homologação.
    """
    if vigente is None:
        return dominio.RECEBIDAS
    if vigente.natureza == dominio.RECEBIDAS:
        return dominio.PRELIMINAR if etapas else dominio.HOMOLOGACAO
    return dominio.HOMOLOGACAO


def _opcoes(vigente, etapas, escolhida):
    """As três naturezas, cada uma dizendo se está disponível e, se não, por quê (FR-5433)."""
    opcoes = []
    for valor, rotulo in dominio.ROTULOS.items():
        motivo = ""
        if vigente is not None and dominio.regride(vigente.natureza, valor):
            motivo = "Já foi publicado um ato posterior a este."
        elif valor == dominio.PRELIMINAR and not etapas:
            motivo = "O Edital não declara Etapa decisória de análise das inscrições."
        opcoes.append(
            {
                "valor": valor,
                "rotulo": rotulo,
                "descricao": DESCRICOES[valor],
                "disponivel": not motivo,
                "motivo": motivo,
                "atual": valor == escolhida,
                "correcao": vigente is not None and vigente.natureza == valor,
            }
        )
    return opcoes


def _escolher_etapa(afericao, etapas):
    """As Etapas a oferecer quando há mais de uma análise possível e nenhuma foi fixada."""
    if afericao is None or afericao.natureza == dominio.RECEBIDAS:
        return []
    codigos = {codigo for codigo, _ in afericao.impedimentos}
    if "inscricoes_etapa_a_escolher" not in codigos and "inscricoes_etapa_invalida" not in codigos:
        return []
    return [{"id": str(etapa.get("id")), "nome": etapa.get("name") or ""} for etapa in etapas]


__all__ = ["publicacoes_das_inscricoes"]
