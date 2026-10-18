"""O protótipo interno do painel de dúvidas do Edital (Fase C, avaliação de 14/10).

Serve para validar a experiência — o painel lateral no desktop, a tela cheia no celular, as
sugestões respondidas pela `070`, a espera, a falha e a mudança de versão — **antes** de qualquer
spec da Fase C. Não é a tela final, e não é vista por candidatos.

**O acesso é o do piloto** (`_edital_do_piloto`): o alcance do Edital, a permissão do piloto e a
chave ligada, com a mesma negativa para as três ausências. Nenhuma rota pública.

**O fundo é a página pública de verdade.** A resposta da `selecao` do portal, com o painel
acrescentado antes do `</body>`: a pessoa que avalia vê o painel sobre a página que o candidato vê,
e nada no portal muda para isso. É a costura de um protótipo, e não o desenho da Fase C.

**Dois modos.** O simulado (`?simulacao=<estado>`) mostra cada estado sem chamada nem gravação: as
respostas do modelo são ilustrativas, e as fontes, as do Edital. O integrado usa as funções que já
existem — a sugestão pela `070` (`responder_sugestao`) e a pergunta livre pela mesma `perguntar` da
tela técnica —, sem outra arquitetura de conversa. A conversa do protótipo tem chave própria na
sessão: as sugestões não aparecem na tela técnica, que continua como está.

**O painel mora em `painel_do_assistente.py`** (074): o contexto, a simulação e os envios, que a
página pública da seleção também usa no desenvolvimento local. Aqui ficam o acesso da gestão e a
chave da sessão do protótipo.
"""

from __future__ import annotations

from django.http import Http404, HttpResponse
from django.shortcuts import redirect
from django.template.loader import render_to_string
from django.utils import timezone
from django.views.decorators.http import require_http_methods

from processo_seletivo.duvidas.application.consultar import SemVersaoVigente, contexto
from processo_seletivo.interface import painel_do_assistente as painel_
from processo_seletivo.interface.assistente import _edital_do_piloto
from processo_seletivo.portal import views as portal
from processo_seletivo.shared.politica_de_conteudo import em_observacao

CHAVE_DA_SESSAO = "assistente_prototipo"
ROTA = "interface:assistente-prototipo"


def _conversa(request, edital_id, **opcoes):
    return painel_.conversa_da_sessao(request, edital_id, CHAVE_DA_SESSAO, **opcoes)


def _destino(edital):
    return lambda **consulta: painel_.endereco(ROTA, edital.id, **consulta)


@require_http_methods(["GET"])
def prototipo(request, edital_id):
    edital, recusa = _edital_do_piloto(request, edital_id)
    if recusa is not None:
        return recusa
    try:
        lido = contexto(edital_id=edital.id, instante=timezone.now())
        # Sem o painel da página pública: com a chave da `074` ligada, seriam dois.
        pagina = portal.selecao(request, edital.id, assistente=False)
    except (SemVersaoVigente, Http404):
        return HttpResponse(
            "<p>Só Edital publicado tem página pública, e este não tem versão vigente agora.</p>"
        )
    simulacao = request.GET.get("simulacao", "")
    if simulacao not in dict(painel_.ESTADOS_SIMULADOS):
        simulacao = ""
    dados = painel_.contexto_do_painel(
        request,
        edital,
        lido,
        conversa="" if simulacao else _conversa(request, edital.id, criar=False),
        rotas=painel_.rotas_do_painel(edital.id, ROTA),
        simulacao=simulacao,
    )
    painel = render_to_string(painel_.TEMPLATE, dados, request=request)
    html = pagina.content.decode("utf-8").replace("</body>", painel + "</body>", 1)
    # A página é a do portal, com a folha dele no documento: a política do portal (091).
    return em_observacao(HttpResponse(html))


@require_http_methods(["POST"])
def prototipo_perguntar(request, edital_id):
    edital, recusa = _edital_do_piloto(request, edital_id)
    if recusa is not None:
        return recusa
    return painel_.enviar_pergunta(request, edital, _conversa(request, edital.id), _destino(edital))


@require_http_methods(["POST"])
def prototipo_sugestao(request, edital_id):
    edital, recusa = _edital_do_piloto(request, edital_id)
    if recusa is not None:
        return recusa
    return painel_.enviar_sugestao(request, edital, _conversa(request, edital.id), _destino(edital))


@require_http_methods(["POST"])
def prototipo_nova(request, edital_id):
    edital, recusa = _edital_do_piloto(request, edital_id)
    if recusa is not None:
        return recusa
    _conversa(request, edital.id, nova=True)
    return redirect(_destino(edital)(painel=1))
