"""A tela do piloto interno do assistente do Edital (071, contracts/tela.md).

**Duas condições, verificadas no servidor a cada requisição** (`FR-1460`): o alcance da página do
Edital, como na `070`, **e** a permissão própria do piloto. Faltando qualquer uma — ou com o piloto
desligado (`FR-1464`) —, a mesma negativa de recurso inexistente: quem não participa do piloto não
aprende, pela resposta, que ele existe neste Edital.

**POST, redirecionamento, GET** (`FR-1505`). O POST grava a troca e redireciona; o GET mostra a
conversa lida da tabela. Recarregar a página não refaz a chamada ao serviço.

**O navegador não carrega a conversa** (`FR-1494`). A sessão guarda só o identificador dela, por
Edital; o histórico é o que o servidor gravou, e um formulário forjado não acrescenta turno.
"""

import uuid

from django.conf import settings
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_http_methods

from processo_seletivo.duvidas.application.consultar import SemVersaoVigente, contexto
from processo_seletivo.duvidas.application.perguntar import PERMISSAO, perguntar
from processo_seletivo.duvidas.domain import canal as canais
from processo_seletivo.duvidas.domain import leitura, respostas
from processo_seletivo.duvidas.domain.estruturas_do_piloto import (
    RESPONDIDA_E_CONFERIDA,
    ROTULO_DA_FONTE,
    ROTULO_DO_TIPO_NO_PILOTO,
    ROTULO_DO_TRECHO,
    TELA,
)
from processo_seletivo.duvidas.infrastructure.inferencia import externo
from processo_seletivo.duvidas.models import TrocaDoPiloto
from processo_seletivo.interface import identidade
from processo_seletivo.processos.application.selectors import obter_edital
from processo_seletivo.shared.api.problems import DomainError

CHAVE_DA_SESSAO = "assistente"

#: Para onde a resposta leva quando a pergunta não é sobre este Edital, ou pede um ato (`FR-1486`).
CAMINHO_OFICIAL = {
    "OUTRA_SELECAO": ("As seleções abertas estão na vitrine pública", "portal:vitrine"),
    "FORA_DO_ESCOPO": (
        "Inscrição, envio de documentos e recurso são feitos na área do candidato",
        "portal:inscricoes",
    ),
    "DECISAO_NAO_TOMADA": (
        "A situação de cada inscrição está na área do candidato",
        "portal:inscricoes",
    ),
}

#: O que a tela diz no lugar da resposta, por estado (contracts/tela.md §3).
TEXTO_DO_ESTADO = {
    "NAO_PASSOU_NA_CONFERENCIA": (
        "A resposta não foi mostrada porque não se sustentou nas fontes do Edital."
    ),
    "INCOMPLETA": "O assistente não produziu uma resposta completa e conferível.",
    "POSSIVEL_CORTE": "O assistente não produziu uma resposta completa e conferível.",
    "RESPOSTA_MALFORMADA": "O assistente não produziu uma resposta completa e conferível.",
    "MODELO_DIFERENTE": "O assistente não produziu uma resposta completa e conferível.",
    "INDISPONIVEL": "O assistente não respondeu agora.",
    "TEMPO_ESGOTADO": "O assistente não respondeu agora.",
    "LIMITE_DE_USO": (
        "O limite de perguntas foi atingido. Tente de novo em alguns minutos, ou comece outra "
        "conversa."
    ),
    # O limite é do serviço do modelo, e não do piloto: com o mesmo texto do `LIMITE_DE_USO`, quem
    # lia achava que o piloto o tinha bloqueado (ensaio de 14/10). Recomeçar a conversa não ajuda.
    "LIMITE_DO_SERVICO": (
        "O serviço do modelo recusou a pergunta por excesso de pedidos. Tente de novo em alguns "
        "minutos."
    ),
    "ORCAMENTO_ESGOTADO": "O limite de gasto do serviço desta configuração acabou.",
    "EXCEDE_O_CONTEXTO": "Este Edital não cabe na configuração atual do piloto.",
    "PERGUNTA_RECUSADA": (
        "A pergunta não foi enviada: está vazia, passa do tamanho máximo ou, com o serviço "
        "externo, traz CPF, e-mail ou telefone."
    ),
    "SEM_TOKENIZER": "O piloto não está pronto: falta o tokenizer do modelo.",
}


def _edital_do_piloto(request, edital_id):
    """O Edital, ou a recusa — a mesma para as três ausências (`FR-1460`, `FR-1464`)."""
    ator = identidade.ator_da_sessao(request)
    if ator is None:
        return None, identidade.pedir_identificacao(request)
    edital = obter_edital(actor=ator, edital_id=edital_id)
    if edital is None or not settings.ASSISTENTE_PILOTO or not ator.can(PERMISSAO):
        raise DomainError("not_found", "Recurso não encontrado.", 404)
    return edital, None


def _conversa(request, edital_id, *, nova=False):
    conversas = dict(request.session.get(CHAVE_DA_SESSAO) or {})
    chave = str(edital_id)
    if nova or chave not in conversas:
        conversas[chave] = str(uuid.uuid4())
        request.session[CHAVE_DA_SESSAO] = conversas
    return conversas[chave]


def _aviso_de_mudanca(edital_id, troca, versao_anterior):
    """O que separa a versão desta troca da anterior, nos atos (`FR-1468`, `FR-1415` da `070`).

    **A mudança da `070`, e não uma nova** (T028): `responder` devolve a `MudancaDeVersao` de
    qualquer pergunta, com os atos aplicados agora e não antes — inclusive quando nenhuma publicação
    nova aconteceu e só a fronteira de vigência passou. A `P-12` é a que todo Edital publicado
    oferece.
    """
    try:
        lido = contexto(
            edital_id=edital_id, instante=troca.instante, versao_anterior=str(versao_anterior)
        )
    except SemVersaoVigente:
        return ""
    mudanca = respostas.responder(lido, "P-12").mudanca
    if mudanca is None:
        return ""
    partes = [
        f"Retificação publicada em {leitura.instante_legivel(ato.publicado_em)}, vigente desde "
        f"{leitura.instante_legivel(ato.vigente_desde)}"
        for ato in mudanca.atos
    ]
    partes += [
        f"deixou de valer o ato publicado em {leitura.instante_legivel(ato.publicado_em)}"
        for ato in mudanca.sem_efeito
    ]
    return "; ".join(partes)


def _turnos(conversa, edital_id, versao_vigente):
    """Os turnos gravados, com o que a tela precisa dizer de cada um."""
    turnos, anterior = [], None
    conferidas = []  # `(versão, ordem)` das trocas conferidas, que poderiam entrar no histórico
    for troca in TrocaDoPiloto.objects.filter(conversa=conversa, edital_id=edital_id):
        elegiveis = [ordem for versao, ordem in conferidas if versao == troca.versao]
        todas = troca.fontes_citadas or []
        fontes = [fonte for fonte in todas if not fonte.get("aviso_da_aplicacao")]
        avisos = [fonte for fonte in todas if fonte.get("aviso_da_aplicacao")]
        turnos.append(
            {
                "troca": troca,
                "respondida": troca.estado == RESPONDIDA_E_CONFERIDA,
                "texto_do_estado": TEXTO_DO_ESTADO.get(troca.estado, ""),
                "rotulo_do_tipo": ROTULO_DO_TIPO_NO_PILOTO.get(troca.tipo, ""),
                "trechos": [
                    {**trecho, "rotulo": ROTULO_DO_TRECHO.get(trecho["natureza"], "")}
                    for trecho in troca.trechos or []
                ],
                "fontes": fontes,
                "avisos": avisos,
                "caminho_oficial": CAMINHO_OFICIAL.get(troca.tipo),
                "historico_reduzido": _historico_reduzido(troca, elegiveis),
                "versao_anterior": bool(troca.versao)
                and versao_vigente is not None
                and str(troca.versao) != str(versao_vigente),
                "mudou": bool(anterior and troca.versao and anterior != troca.versao),
                "atos_da_mudanca": _aviso_de_mudanca(edital_id, troca, anterior)
                if anterior and troca.versao and anterior != troca.versao
                else "",
            }
        )
        if troca.versao:
            anterior = troca.versao
        if troca.estado == RESPONDIDA_E_CONFERIDA:
            conferidas.append((troca.versao, troca.ordem))
    return turnos


def _historico_reduzido(troca, elegiveis):
    """A frase do `FR-1481`, quando turnos da mesma versão ficaram de fora para caber.

    `historico_desde` é o turno mais antigo enviado; qualquer turno elegível anterior a ele saiu.
    """
    if not troca.chamou_o_servico or not elegiveis:
        return ""
    if troca.historico_desde is None:
        return "Esta resposta não considerou as perguntas anteriores: elas não cabiam no contexto."
    if min(elegiveis) < troca.historico_desde:
        return f"Esta resposta considerou as perguntas a partir da nº {troca.historico_desde}."
    return ""


@require_http_methods(["GET", "POST"])
def conversar(request, edital_id):
    edital, recusa = _edital_do_piloto(request, edital_id)
    if recusa is not None:
        return recusa
    if request.method == "POST":
        try:
            troca = perguntar(
                edital_id=edital.id,
                conversa=_conversa(request, edital.id),
                pergunta=request.POST.get("pergunta", ""),
                instante=timezone.now(),
                origem=TELA,
            )
        except SemVersaoVigente:
            return redirect(reverse("interface:assistente", args=[edital.id]))
        destino = reverse("interface:assistente", args=[edital.id])
        return redirect(f"{destino}#troca-{troca.ordem}")

    pagina = {
        "edital": edital,
        "processo": edital.processo,
        "externo": externo(),
        "pergunta_maxima": settings.ASSISTENTE_PERGUNTA_MAXIMA,
        "rotulo_da_fonte": ROTULO_DA_FONTE,
    }
    try:
        lido = contexto(edital_id=edital.id, instante=timezone.now())
    except SemVersaoVigente:
        return render(request, "interface/assistente.html", {**pagina, "publicado": False})
    encontrado = canais.canal(lido.conteudo, lido.canal_institucional)
    conversa = _conversa(request, edital.id)
    pagina.update(
        {
            "publicado": True,
            "versao": lido.versao,
            "vigente_desde": leitura.instante_legivel(lido.versao.vigente_desde),
            "canal": canais.em_palavras(encontrado),
            "canal_paragrafos": encontrado.paragrafos,
            "turnos": _turnos(conversa, edital.id, lido.versao.id),
        }
    )
    return render(request, "interface/assistente.html", pagina)


@require_http_methods(["POST"])
def nova_conversa(request, edital_id):
    edital, recusa = _edital_do_piloto(request, edital_id)
    if recusa is not None:
        return recusa
    _conversa(request, edital.id, nova=True)
    return redirect(reverse("interface:assistente", args=[edital.id]))
