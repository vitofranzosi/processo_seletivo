"""O assistente do Edital na página pública da seleção, no desenvolvimento local (074).

**O painel e os envios são os do protótipo da Fase C** (`interface/painel_do_assistente.py`), sem
outra arquitetura de conversa (`FR-1681`). Muda o acesso: a chave
`ASSISTENTE_NA_PAGINA_DO_EDITAL`, e não a identidade da gestão, porque é a visão do candidato que se
quer testar (`FR-1680`). Desligada, as rotas não existem — e produção recusa subir com ela ligada.

**A conversa é da sessão e do Edital** (`FR-1682`): chave própria, separada da do protótipo e da
tela técnica, e o registro continua sem identidade (a decisão 013 da `071`). Ela nasce no primeiro
envio: mostrar a página não grava nada na sessão.

**Os limites são os da `perguntar`, e um a mais** (`FR-1685`). O limite de turnos é por conversa,
e "Nova conversa" daria turnos novos sem fim; aqui a sessão abre no máximo
`ASSISTENTE_CONVERSAS_POR_SESSAO` conversas por Edital. Quem descarta o cookie escapa dele — o
limite por visitante é da implantação —, e a barreira de gasto continua sendo o limite da chave.

**Só a página pública abre o painel.** Os envios conferem o que a página confere: o Edital precisa
ter seleção pública agora. Um identificador qualquer não chega ao modelo.
"""

from __future__ import annotations

from django.conf import settings
from django.http import Http404
from django.shortcuts import redirect
from django.template.loader import render_to_string
from django.utils import timezone
from django.views.decorators.http import require_http_methods

from processo_seletivo.duvidas.application.consultar import SemVersaoVigente, contexto
from processo_seletivo.interface import painel_do_assistente as painel_
from processo_seletivo.publicacoes.application import selectors
from processo_seletivo.shared.api.problems import DomainError

CHAVE_DA_SESSAO = "assistente_do_edital"
#: Quantas conversas a sessão já abriu em cada Edital, para o teto de "Nova conversa".
CHAVE_DAS_CONTAGENS = "assistente_do_edital_conversas"
ROTA = "portal:assistente"


def _abertas(request, edital_id):
    return int((request.session.get(CHAVE_DAS_CONTAGENS) or {}).get(str(edital_id), 0))


def _contar(request, edital_id, abertas):
    contagens = dict(request.session.get(CHAVE_DAS_CONTAGENS) or {})
    contagens[str(edital_id)] = abertas
    request.session[CHAVE_DAS_CONTAGENS] = contagens


def _conversa_do_envio(request, edital_id):
    """A conversa em curso, ou a primeira — que já conta no teto da sessão."""
    conversa = painel_.conversa_da_sessao(request, edital_id, CHAVE_DA_SESSAO, criar=False)
    if conversa:
        return conversa
    _contar(request, edital_id, max(_abertas(request, edital_id), 1))
    return painel_.conversa_da_sessao(request, edital_id, CHAVE_DA_SESSAO)


def _destino(edital_id):
    return lambda **consulta: painel_.endereco("portal:selecao", edital_id, **consulta)


def _edital_com_pagina(edital_id):
    """O Edital da página pública, ou 404 — também com a chave desligada."""
    if not settings.ASSISTENTE_NA_PAGINA_DO_EDITAL:
        raise Http404
    try:
        return selectors.selecao_publica(edital_id=edital_id, at=timezone.now()).edital
    except DomainError as exc:
        raise Http404 from exc


def painel(request, edital, instante):
    """O fragmento do painel para a página da seleção, ou vazio quando não cabe."""
    if not settings.ASSISTENTE_NA_PAGINA_DO_EDITAL:
        return ""
    try:
        lido = contexto(edital_id=edital.id, instante=instante)
    except SemVersaoVigente:
        return ""
    dados = painel_.contexto_do_painel(
        request,
        edital,
        lido,
        conversa=painel_.conversa_da_sessao(request, edital.id, CHAVE_DA_SESSAO, criar=False),
        rotas=painel_.rotas_do_painel(edital.id, ROTA),
        local=True,
    )
    dados["limite_de_conversas"] = request.GET.get("limite") == "1"
    return render_to_string(painel_.TEMPLATE, dados, request=request)


@require_http_methods(["POST"])
def perguntar(request, edital_id):
    edital = _edital_com_pagina(edital_id)
    return painel_.enviar_pergunta(
        request, edital, _conversa_do_envio(request, edital.id), _destino(edital.id)
    )


@require_http_methods(["POST"])
def sugestao(request, edital_id):
    edital = _edital_com_pagina(edital_id)
    return painel_.enviar_sugestao(
        request, edital, _conversa_do_envio(request, edital.id), _destino(edital.id)
    )


@require_http_methods(["POST"])
def nova(request, edital_id):
    edital = _edital_com_pagina(edital_id)
    abertas = _abertas(request, edital.id)
    if abertas >= settings.ASSISTENTE_CONVERSAS_POR_SESSAO:
        return redirect(_destino(edital.id)(painel=1, limite=1))
    painel_.conversa_da_sessao(request, edital.id, CHAVE_DA_SESSAO, nova=True)
    _contar(request, edital.id, abertas + 1)
    return redirect(_destino(edital.id)(painel=1))
