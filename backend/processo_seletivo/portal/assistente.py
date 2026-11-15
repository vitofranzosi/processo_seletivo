"""O assistente do Edital na página pública da seleção (074), aberto pela interface (170).

**O painel e os envios são os do protótipo da Fase C** (`interface/painel_do_assistente.py`), sem
outra arquitetura de conversa (`FR-1681`). Muda o acesso, que não é a identidade da gestão, porque é
a visão do candidato que se quer testar (`FR-1680`). Desde a `170`, a página abre por um de dois
caminhos, e só fora de produção (`duvidas/application/habilitacao.py`):

- **o ato do Administrador institucional**, Edital a Edital (FR-7520) — o percurso da interface,
  que não depende de chave nenhuma (FR-7508);
- **a chave `ASSISTENTE_NA_PAGINA_DO_EDITAL`**, que continua a demonstração local da `074` e que
  produção recusa (FR-7507).

**Em produção, nunca** (FR-7519): a abertura ao público espera os requisitos da abertura, e a regra
lê o ambiente a cada requisição — nem um banco de testes levado para lá abre o painel.

**A conversa é da sessão e do Edital** (`FR-1682`): chave própria, separada da do protótipo e da
tela técnica, e o registro continua sem identidade (a decisão 013 da `071`). Ela nasce no primeiro
envio: mostrar a página não grava nada na sessão. **Com o ato, a chave leva a marca dele** (R-5):
habilitar de novo começa conversa nova, e o histórico de antes não volta ao modelo (FR-7525).

**Os limites são os da `perguntar`, e um a mais** (`FR-1685`). O limite de turnos é por conversa,
e "Nova conversa" daria turnos novos sem fim; aqui a sessão abre no máximo
`ASSISTENTE_CONVERSAS_POR_SESSAO` conversas por Edital. Quem descarta o cookie escapa dele — o
limite por visitante é o `RA-8`, da abertura em produção —, e a barreira de gasto continua sendo o
limite da chave.

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

from processo_seletivo.duvidas.application import habilitacao
from processo_seletivo.duvidas.application.consultar import SemVersaoVigente, contexto
from processo_seletivo.duvidas.domain.habilitacao import PAGINA_PUBLICA
from processo_seletivo.interface import painel_do_assistente as painel_
from processo_seletivo.interface.assistente import chave_da_conversa
from processo_seletivo.publicacoes.application import selectors
from processo_seletivo.shared.api.problems import DomainError

CHAVE_DA_SESSAO = "assistente_do_edital"
#: Quantas conversas a sessão já abriu em cada Edital, para o teto de "Nova conversa".
CHAVE_DAS_CONTAGENS = "assistente_do_edital_conversas"
ROTA = "portal:assistente"
#: O parâmetro da página da seleção que mostra o aviso de assistente encerrado (UX-813, R-9).
ENCERRADO = "encerrado"


def _marca(edital_id):
    return habilitacao.marca(PAGINA_PUBLICA, edital_id)


def _abertas(request, edital_id):
    chave = chave_da_conversa(edital_id, _marca(edital_id))
    return int((request.session.get(CHAVE_DAS_CONTAGENS) or {}).get(chave, 0))


def _contar(request, edital_id, abertas):
    contagens = dict(request.session.get(CHAVE_DAS_CONTAGENS) or {})
    contagens[chave_da_conversa(edital_id, _marca(edital_id))] = abertas
    request.session[CHAVE_DAS_CONTAGENS] = contagens


def _conversa(request, edital_id, **opcoes):
    return painel_.conversa_da_sessao(
        request, edital_id, CHAVE_DA_SESSAO, marca=_marca(edital_id), **opcoes
    )


def _conversa_do_envio(request, edital_id):
    """A conversa em curso, ou a primeira — que já conta no teto da sessão."""
    conversa = _conversa(request, edital_id, criar=False)
    if conversa:
        return conversa
    _contar(request, edital_id, max(_abertas(request, edital_id), 1))
    return _conversa(request, edital_id)


def _destino(edital_id):
    return lambda **consulta: painel_.endereco("portal:selecao", edital_id, **consulta)


class _Encerrado(Exception):
    """O envio de quem conversava num Edital que deixou de atender (FR-7524)."""

    def __init__(self, edital_id):
        self.edital_id = edital_id


def _conversou_aqui(request, edital_id):
    prefixo = str(edital_id)
    return any(
        chave == prefixo or chave.startswith(f"{prefixo}:")
        for chave in (request.session.get(CHAVE_DA_SESSAO) or {})
    )


def _edital_com_pagina(request, edital_id):
    """O Edital da página pública que atende agora, ou a recusa.

    A recusa é 404, como na `074` com a chave desligada: quem nunca conversou não aprende que a rota
    existe. **A exceção é quem conversava aqui** (R-9): a desabilitação o encontra no meio da
    conversa, e ele recebe a página com o aviso de encerrado, em vez de um erro (UX-813). Em
    produção, sempre 404 (FR-7519). Nos dois casos, nada chega ao modelo.
    """
    if not habilitacao.pagina_publica_atende(edital_id):
        if not habilitacao.em_producao() and _conversou_aqui(request, edital_id):
            raise _Encerrado(edital_id)
        raise Http404
    try:
        return selectors.selecao_publica(edital_id=edital_id, at=timezone.now()).edital
    except DomainError as exc:
        raise Http404 from exc


def _envio(funcao):
    """Os três envios recusam igual: o aviso de encerrado, ou o 404 (FR-7524)."""

    def envio(request, edital_id):
        try:
            edital = _edital_com_pagina(request, edital_id)
        except _Encerrado as encerrado:
            return redirect(_destino(encerrado.edital_id)(assistente=ENCERRADO))
        return funcao(request, edital)

    envio.__name__ = funcao.__name__
    envio.__doc__ = funcao.__doc__
    return require_http_methods(["POST"])(envio)


def painel(request, edital, instante):
    """O fragmento do painel para a página da seleção, ou vazio quando não cabe."""
    if not habilitacao.pagina_publica_atende(edital.id):
        return ""
    try:
        lido = contexto(edital_id=edital.id, instante=instante)
    except SemVersaoVigente:
        return ""
    dados = painel_.contexto_do_painel(
        request,
        edital,
        lido,
        conversa=_conversa(request, edital.id, criar=False),
        rotas=painel_.rotas_do_painel(edital.id, ROTA),
        local=True,
    )
    dados["limite_de_conversas"] = request.GET.get("limite") == "1"
    return render_to_string(painel_.TEMPLATE, dados, request=request)


def encerrado(request, painel_mostrado):
    """Se a página mostra o aviso de assistente encerrado (UX-813): só pelo parâmetro do envio
    recusado, e só sem o painel — forjado com o painel aberto, não diz nada falso."""
    return request.GET.get("assistente") == ENCERRADO and not painel_mostrado


@_envio
def perguntar(request, edital):
    return painel_.enviar_pergunta(
        request, edital, _conversa_do_envio(request, edital.id), _destino(edital.id)
    )


@_envio
def sugestao(request, edital):
    return painel_.enviar_sugestao(
        request, edital, _conversa_do_envio(request, edital.id), _destino(edital.id)
    )


@_envio
def nova(request, edital):
    abertas = _abertas(request, edital.id)
    if abertas >= settings.ASSISTENTE_CONVERSAS_POR_SESSAO:
        return redirect(_destino(edital.id)(painel=1, limite=1))
    _conversa(request, edital.id, nova=True)
    _contar(request, edital.id, abertas + 1)
    return redirect(_destino(edital.id)(painel=1))
