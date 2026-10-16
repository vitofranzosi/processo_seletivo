"""O painel de dúvidas do Edital: o contexto do fragmento e os envios (Fase C).

Desenhado no protótipo da gestão (avaliação de 14/10) e servido, no desenvolvimento local, também
pela página pública da seleção (074, `FR-1681`). Quem decide o acesso, a chave da sessão e o
endereço de volta é a rota — `interface/prototipo_do_assistente.py`, na gestão, e
`portal/assistente.py`, no portal. Este módulo não importa nenhuma das duas, e é isso que deixa a
página da seleção importá-lo sem ciclo: o protótipo importa a página para mostrá-la de fundo.

**Dois modos.** O simulado (`?simulacao=<estado>`, só no protótipo) mostra cada estado sem chamada
nem gravação: as respostas do modelo são ilustrativas, e as fontes, as do Edital. O integrado usa as
funções que já existem — a sugestão pela `070` (`responder_sugestao`) e a pergunta livre pela mesma
`perguntar` da tela técnica —, sem outra arquitetura de conversa.
"""

from __future__ import annotations

import uuid

from django.conf import settings
from django.shortcuts import redirect
from django.urls import reverse
from django.utils import timezone

from processo_seletivo.duvidas.application.consultar import SemVersaoVigente, contexto
from processo_seletivo.duvidas.application.perguntar import (
    perguntar,
    preencher_com_a_resposta,
    responder_sugestao,
    resposta_da_sugestao,
)
from processo_seletivo.duvidas.domain import canal as canais
from processo_seletivo.duvidas.domain import catalogo, leitura, sugestoes
from processo_seletivo.duvidas.domain import fontes as derivacao
from processo_seletivo.duvidas.domain.estruturas import (
    DEPENDE_DA_LEITURA,
    DETALHE_EM_ANEXO,
    FONTES_DIVERGENTES,
    NAO_INFORMA,
    RESPONDIDA,
    ROTULO_DA_NATUREZA,
    TEXTO,
)
from processo_seletivo.duvidas.domain.estruturas_do_piloto import (
    CITACAO_LITERAL,
    DECISAO_NAO_TOMADA,
    INDISPONIVEL,
    NAO_PASSOU_NA_CONFERENCIA,
    RESPONDIDA_E_CONFERIDA,
    RESPOSTA_DA_SUGESTAO,
    ROTULO_DA_FONTE,
    TELA,
)
from processo_seletivo.duvidas.models import TrocaDoPiloto
from processo_seletivo.interface.assistente import CAMINHO_OFICIAL, _aviso_de_mudanca

TEMPLATE = "interface/prototipo_do_assistente.html"

#: As três sugestões à vista, nesta ordem, entre as que o Edital oferece; as outras ficam em "Mais
#: dúvidas" (avaliação de 14/10). A escolha é do protótipo: prazo, documentos e vagas.
SUGERIDAS = ("P-01", "P-05", "P-03")

#: O que o candidato lê no lugar da resposta. Três situações, e não catorze estados: "não deu para
#: confirmar no Edital" não pode parecer "o serviço está ocupado" (avaliação de 14/10). Texto do
#: protótipo; o definitivo é da spec da Fase C, com o `DA-01`.
NAO_CONFIRMADA = (
    "Não foi possível confirmar uma resposta nas fontes deste Edital. Consulte o texto do Edital "
    "ou o atendimento oficial."
)
INDISPONIVEL_AGORA = "O assistente não conseguiu responder agora. Tente de novo em alguns minutos."
TEXTO_PARA_O_CANDIDATO = {
    "NAO_PASSOU_NA_CONFERENCIA": NAO_CONFIRMADA,
    "INCOMPLETA": NAO_CONFIRMADA,
    "POSSIVEL_CORTE": NAO_CONFIRMADA,
    "RESPOSTA_MALFORMADA": NAO_CONFIRMADA,
    "MODELO_DIFERENTE": NAO_CONFIRMADA,
    "INDISPONIVEL": INDISPONIVEL_AGORA,
    "TEMPO_ESGOTADO": INDISPONIVEL_AGORA,
    "LIMITE_DO_SERVICO": INDISPONIVEL_AGORA,
    "LIMITE_DE_USO": "Esta conversa chegou ao limite de perguntas. Comece uma nova conversa.",
    "ORCAMENTO_ESGOTADO": "O assistente não está disponível agora.",
    "EXCEDE_O_CONTEXTO": "O assistente não está disponível para este Edital.",
    "SEM_TOKENIZER": "O assistente não está disponível agora.",
    "PERGUNTA_RECUSADA": (
        "A pergunta não foi enviada: está vazia, passa do tamanho máximo ou traz CPF, e-mail ou "
        "telefone."
    ),
}

#: A cobertura que a resposta declara, quando não é a resposta inteira (`070`, `FR-1421`).
NOTA_DO_TIPO = {
    NAO_INFORMA: "O Edital não traz esta informação.",
    DEPENDE_DA_LEITURA: "A resposta depende da leitura do texto do Edital, nas fontes abaixo.",
    FONTES_DIVERGENTES: "O Edital traz informações divergentes sobre isto. Confira as fontes.",
    DETALHE_EM_ANEXO: "O detalhe está num anexo do Edital.",
    DECISAO_NAO_TOMADA: "Esta consulta não toma decisões sobre inscrições.",
}

#: A espera, coerente com a etapa real (avaliação de 14/10). Não há "conferindo": a conferência leva
#: milissegundos depois que o modelo responde, e dizer que ela está acontecendo seria inventar uma
#: etapa. Também não há prazo prometido: os 5 a 35 segundos do ensaio foram observados, e não são
#: limite de nada.
ESPERA = "Consultando as informações deste Edital…"
ESPERA_LONGA = "A consulta está levando um pouco mais de tempo."
#: Quando a segunda frase aparece, no navegador. Só muda o texto; nada é cancelado.
SEGUNDOS_ATE_A_ESPERA_LONGA = 15

ESTADOS_SIMULADOS = (
    ("inicio", "Início"),
    ("escolha", "Escolha da opção"),
    ("resposta", "Resposta com fonte"),
    ("continuacao", "Continuação"),
    ("espera", "Espera"),
    ("espera-longa", "Espera longa"),
    ("falha", "Falha"),
    ("mudanca", "Mudança de versão"),
)


def conversa_da_sessao(request, edital_id, chave_da_sessao, *, nova=False, criar=True):
    """A conversa desta sessão neste Edital: uma por par, e outra a cada "Nova conversa".

    `criar=False` só lê: mostrar a página não grava nada na sessão, e a conversa nasce no primeiro
    envio (revisão da `074`). Sem conversa, devolve vazio.
    """
    conversas = dict(request.session.get(chave_da_sessao) or {})
    chave = str(edital_id)
    if nova or (criar and chave not in conversas):
        conversas[chave] = str(uuid.uuid4())
        request.session[chave_da_sessao] = conversas
    return conversas.get(chave, "")


def endereco(nome, edital_id, **consulta):
    """A rota nomeada do Edital, com a consulta — os valores são códigos do próprio painel."""
    destino = reverse(nome, args=[edital_id])
    if consulta:
        destino += "?" + "&".join(f"{chave}={valor}" for chave, valor in consulta.items())
    return destino


# ---- a troca, como o painel a mostra --------------------------------------------------------


def _documentos(origens):
    return [origem["documento"] for origem in origens or [] if origem.get("documento")]


def _segmentos(conteudo, excertos):
    """O conteúdo da fonte em pedaços, com o que o corpo da resposta já mostrou marcado.

    A citação aparece no balão, e a fonte a repete como contexto, e não como segunda cópia: o trecho
    citado vem destacado dentro da parte do Edital de onde saiu.
    """
    marcas = []
    for excerto in excertos:
        excerto = excerto.strip()
        inicio = conteudo.find(excerto) if len(excerto) >= 20 else -1
        if inicio >= 0:
            marcas.append((inicio, inicio + len(excerto)))
    segmentos, posicao = [], 0
    for inicio, fim in sorted(marcas):
        if inicio < posicao:
            continue
        if inicio > posicao:
            segmentos.append((conteudo[posicao:inicio], False))
        segmentos.append((conteudo[inicio:fim], True))
        posicao = fim
    if posicao < len(conteudo):
        segmentos.append((conteudo[posicao:], False))
    return segmentos


def _fonte(natureza, onde, rotulo, conteudo, literal, origens, links, excertos):
    if rotulo:
        onde = f"{onde} — {rotulo}"
    return {
        "natureza": natureza,
        "onde": onde,
        "segmentos": _segmentos(conteudo, excertos),
        "literal": literal,
        "documentos": _documentos(origens),
        "links": links or [],
    }


def _fonte_da_070(referencia, excertos):
    return _fonte(
        ROTULO_DA_NATUREZA.get(referencia["natureza"], ""),
        referencia["localizacao"],
        referencia.get("rotulo"),
        referencia["conteudo"],
        referencia["natureza"] == TEXTO,
        referencia.get("origens"),
        referencia.get("links"),
        excertos,
    )


def _fonte_do_piloto(fonte, excertos=()):
    return _fonte(
        fonte["natureza"],
        fonte["lugar"],
        fonte.get("rotulo"),
        fonte["conteudo"],
        fonte["natureza"] == ROTULO_DA_FONTE[TEXTO],
        fonte.get("origens"),
        fonte.get("links"),
        excertos,
    )


def _blocos(trechos, *, sugestao, por_id):
    """Os trechos em blocos de leitura: texto, lista, citação e aviso.

    Os itens seguidos viram uma lista. Na sugestão, o trecho `dado` é só do histórico: a explicação
    da `070` já o diz, e mostrá-lo de novo era a repetição que a avaliação apontou. O `contexto` é
    só do sistema: a opção escolhida, dita ao modelo.
    """
    blocos = []
    for trecho in trechos:
        natureza = trecho["natureza"]
        if natureza == "aviso":
            blocos.append({"tipo": "aviso", "texto": trecho["texto"]})
        elif natureza == "item":
            if not blocos or blocos[-1]["tipo"] != "lista":
                blocos.append({"tipo": "lista", "itens": []})
            blocos[-1]["itens"].append(trecho)
        elif natureza == CITACAO_LITERAL:
            citada = por_id.get((trecho.get("fontes") or [""])[0])
            onde = _fonte_do_piloto(citada)["onde"] if citada else ""
            blocos.append({"tipo": "citacao", "texto": trecho["texto"], "onde": onde})
        elif natureza == "contexto" or (natureza == "dado" and sugestao):
            continue
        else:
            blocos.append({"tipo": "texto", "texto": trecho["texto"]})
    return blocos


def _mensagem(troca, *, versao_vigente, mudanca=""):
    """A troca gravada — ou montada na simulação —, no formato do painel."""
    sugestao = troca.estado == RESPOSTA_DA_SUGESTAO
    mensagem = {
        "ordem": troca.ordem,
        "pergunta": troca.pergunta,
        "sugestao": sugestao,
        "respondida": troca.estado in (RESPONDIDA_E_CONFERIDA, RESPOSTA_DA_SUGESTAO),
        "anterior": bool(troca.versao and versao_vigente and str(troca.versao) != versao_vigente),
        "mudanca": mudanca,
        "falha": TEXTO_PARA_O_CANDIDATO.get(troca.estado, NAO_CONFIRMADA),
        "nota": NOTA_DO_TIPO.get(troca.tipo, "") if troca.tipo != RESPONDIDA else "",
        "caminho_oficial": None,
        "blocos": [],
        "fontes": [],
    }
    if not mensagem["respondida"]:
        return mensagem
    caminho = CAMINHO_OFICIAL.get(troca.tipo)
    if caminho:
        mensagem["caminho_oficial"] = (caminho[0], reverse(caminho[1]))
    trechos = troca.trechos or []
    todas = troca.fontes_citadas or []
    por_id = {} if sugestao else {fonte["id"]: fonte for fonte in todas}
    mensagem["blocos"] = _blocos(trechos, sugestao=sugestao, por_id=por_id)
    excertos = [t["texto"] for t in trechos if t["natureza"] == CITACAO_LITERAL]
    excertos += [t.get("detalhe", "") for t in trechos if t["natureza"] == "item"]
    if sugestao:
        mensagem["fontes"] = [_fonte_da_070(r, excertos) for r in todas]
        return mensagem
    avisos = [
        {"tipo": "aviso", "texto": f"{fonte['lugar']}: {fonte['conteudo']}"}
        for fonte in todas
        if fonte.get("aviso_da_aplicacao")
    ]
    mensagem["blocos"] = avisos + mensagem["blocos"]
    mensagem["fontes"] = [
        _fonte_do_piloto(fonte, excertos) for fonte in todas if not fonte.get("aviso_da_aplicacao")
    ]
    return mensagem


def _marco_de_versao(atos):
    """A transição no histórico: as respostas de cima não foram atualizadas (avaliação de 14/10)."""
    texto = "O Edital mudou desde as respostas acima"
    if atos:
        texto += f" ({atos})"
    return texto + ". Elas se referem à versão anterior; daqui em diante, à versão vigente."


def _mensagens_gravadas(conversa, edital_id, versao_vigente):
    mensagens, anterior = [], None
    for troca in TrocaDoPiloto.objects.filter(conversa=conversa, edital_id=edital_id):
        mudanca = ""
        if anterior and troca.versao and anterior != troca.versao:
            mudanca = _marco_de_versao(_aviso_de_mudanca(edital_id, troca, anterior))
        mensagens.append(_mensagem(troca, versao_vigente=versao_vigente, mudanca=mudanca))
        if troca.versao:
            anterior = troca.versao
    return mensagens


# ---- a simulação ----------------------------------------------------------------------------


def _troca_simulada(ordem, lido, **campos):
    return TrocaDoPiloto(
        ordem=ordem,
        versao=lido.versao.id,
        versao_curta=lido.versao.identificador_curto,
        **campos,
    )


def _sugestao_simulada(ordem, lido, codigo, perfil):
    """A resposta verdadeira da `070`, sem gravar: ela é de graça e não depende do modelo."""
    texto, resposta = resposta_da_sugestao(lido, codigo, perfil)
    troca = _troca_simulada(ordem, lido, pergunta=texto, estado=RESPOSTA_DA_SUGESTAO)
    if catalogo.PERFIL not in catalogo.POR_CODIGO[codigo].parametros:
        perfil = None
    preencher_com_a_resposta(troca, lido, codigo, resposta, perfil)
    return troca


def _resposta_simulada(ordem, lido, pergunta, explicacao):
    """Uma resposta do modelo, ilustrativa, que cita uma fonte de verdade deste Edital."""
    fontes = derivacao.fontes_completas(lido)
    # Um parágrafo inteiro de uma seção do Edital, para que a citação continue literal; os rótulos
    # curtos do cronograma não mostrariam como uma citação de verdade ocupa o painel.
    paragrafos = (
        (fonte, linha.strip())
        for fonte in fontes
        if fonte.natureza == TEXTO
        for linha in fonte.conteudo.split("\n")
        if len(linha.strip()) >= 120
    )
    escolhida = next(paragrafos, None)
    trechos = [{"natureza": "explicacao", "texto": explicacao, "fontes": []}]
    citadas = []
    if escolhida is not None:
        fonte, paragrafo = escolhida
        trechos.append({"natureza": CITACAO_LITERAL, "texto": paragrafo, "fontes": [fonte.id]})
        citadas.append(fonte.como_dict())
    return _troca_simulada(
        ordem,
        lido,
        pergunta=pergunta,
        estado=RESPONDIDA_E_CONFERIDA,
        tipo=RESPONDIDA,
        trechos=trechos,
        fontes_citadas=citadas,
    )


def _simulacao(estado, lido, oferecidas, perfil):
    """`(mensagens, pendente, espera)` de cada estado simulado."""
    vigente = str(lido.versao.id)
    primeira = "P-05" if "P-05" in oferecidas else next(iter(oferecidas), None)
    sugerida = [_sugestao_simulada(1, lido, primeira, perfil)] if primeira else []
    continuacao = _resposta_simulada(
        len(sugerida) + 1,
        lido,
        "Preciso enviar todos?",
        "Resposta ilustrativa do protótipo: aqui o modelo responderia à continuação, sabendo da "
        "pergunta sugerida e da resposta anterior, e citaria o trecho do Edital em que se apoia.",
    )

    def mostrar(trocas, **por_ordem):
        return [
            _mensagem(troca, versao_vigente=vigente, mudanca=por_ordem.get(str(troca.ordem), ""))
            for troca in trocas
        ]

    if estado == "resposta":
        unica = _resposta_simulada(
            1,
            lido,
            "Como faço a inscrição?",
            "Resposta ilustrativa do protótipo: a explicação vem primeiro, em poucas linhas, e a "
            "citação literal aparece só quando faz parte da resposta, identificada como texto do "
            "Edital.",
        )
        return mostrar([unica]), "", ""
    if estado == "continuacao":
        return mostrar([*sugerida, continuacao]), "", ""
    if estado in ("espera", "espera-longa"):
        espera = ESPERA if estado == "espera" else ESPERA_LONGA
        return mostrar(sugerida), "Preciso enviar todos?", espera
    if estado == "falha":
        nao_confirmada = _troca_simulada(
            len(sugerida) + 1,
            lido,
            pergunta="E se eu perder o prazo?",
            estado=NAO_PASSOU_NA_CONFERENCIA,
        )
        indisponivel = _troca_simulada(
            len(sugerida) + 2, lido, pergunta="E se eu perder o prazo?", estado=INDISPONIVEL
        )
        return mostrar([*sugerida, nao_confirmada, indisponivel]), "", ""
    if estado == "mudanca":
        for troca in sugerida:
            troca.versao = uuid.uuid4()  # a versão anterior, que não é mais a vigente
        # A Retificação da versão vigente, de verdade: o marco e a linha da versão no topo do
        # painel precisam contar a mesma história (avaliação de 14/10).
        if lido.versao.retificacoes:
            publicada, vigente_desde = lido.versao.retificacoes[-1]
            atos = (
                f"Retificação publicada em {leitura.instante_legivel(publicada)}, vigente desde "
                f"{leitura.instante_legivel(vigente_desde)}"
            )
        else:
            atos = f"vigente desde {leitura.instante_legivel(lido.versao.vigente_desde)}"
        marco = _marco_de_versao(atos)
        return mostrar([*sugerida, continuacao], **{str(continuacao.ordem): marco}), "", ""
    return [], "", ""


# ---- as telas -------------------------------------------------------------------------------


def _sugestoes(conteudo):
    """`(principais, mais)`: três à vista, e as outras que o Edital oferece em "Mais dúvidas"."""
    oferecidas = {pergunta.codigo: pergunta for pergunta in catalogo.oferecidas(conteudo)}

    def linha(codigo):
        pergunta = oferecidas[codigo]
        return (codigo, sugestoes.texto_no_painel(codigo), catalogo.PERFIL in pergunta.parametros)

    principais = [linha(codigo) for codigo in SUGERIDAS if codigo in oferecidas]
    mais = [linha(codigo) for codigo in oferecidas if codigo not in SUGERIDAS]
    return principais, mais


def _opcoes(conteudo):
    perfis = conteudo.get("profiles") or []
    return [(perfil.get("code"), sugestoes.nome_da_opcao(perfil, perfis)) for perfil in perfis]


def _atendimento(contato):
    """O contato como link, quando ele é um endereço; texto, quando não é."""
    if "@" in contato and " " not in contato:
        return contato, f"mailto:{contato}"
    if contato.startswith(("https://", "http://")):
        return contato, contato
    return contato, ""


def contexto_do_painel(request, edital, lido, *, conversa, rotas, simulacao="", local=False):
    """O contexto do fragmento. `rotas` são os três envios; `local`, a página pública da `074`."""
    opcoes = _opcoes(lido.conteudo)
    perfil = opcoes[0][0] if opcoes else ""
    principais, mais = _sugestoes(lido.conteudo)
    oferecidas = [codigo for codigo, *_ in principais + mais]
    vigente = str(lido.versao.id)
    if simulacao:
        mensagens, pendente, espera = _simulacao(simulacao, lido, oferecidas, perfil)
    else:
        gravadas = _mensagens_gravadas(conversa, edital.id, vigente) if conversa else []
        mensagens, pendente, espera = gravadas, "", ""
    # A pergunta que depende da opção, num Edital com mais de uma: o painel pergunta qual, como uma
    # conversa faria, em vez de pôr um seletor na entrada.
    escolher = "P-05" if simulacao == "escolha" else request.GET.get("escolher", "")
    escolha = None
    if escolher in oferecidas and len(opcoes) > 1:
        escolha = {"codigo": escolher, "pergunta": sugestoes.texto_no_painel(escolher)}
    encontrado = canais.canal(lido.conteudo, lido.canal_institucional)
    return {
        "edital": edital,
        "versao": lido.versao,
        "vigente_desde": leitura.instante_legivel(lido.versao.vigente_desde),
        "atendimento": [_atendimento(contato) for contato in encontrado.contatos],
        "principais": principais,
        "mais": mais,
        "opcoes": opcoes,
        "escolha": escolha,
        "mensagens": mensagens,
        "pendente": (request.GET.get("pergunta") or pendente) if pendente else "",
        "espera": espera,
        "espera_curta": ESPERA,
        "espera_longa": ESPERA_LONGA,
        "segundos_ate_a_espera_longa": SEGUNDOS_ATE_A_ESPERA_LONGA,
        "recusa": request.GET.get("recusa") == "1",
        "simulacao": simulacao,
        "estados_simulados": ESTADOS_SIMULADOS,
        "pergunta_maxima": settings.ASSISTENTE_PERGUNTA_MAXIMA,
        "rotas": rotas,
        "local": local,
        "aberto": request.GET.get("painel") == "1",
    }


def rotas_do_painel(edital_id, prefixo):
    return {
        envio: reverse(f"{prefixo}-{envio}", args=[edital_id])
        for envio in ("perguntar", "sugestao", "nova")
    }


# ---- os envios, comuns às duas rotas --------------------------------------------------------


def enviar_pergunta(request, edital, conversa, destino):
    """A pergunta livre, pela mesma `perguntar` da tela técnica, com os limites dela."""
    try:
        troca = perguntar(
            edital_id=edital.id,
            conversa=conversa,
            pergunta=request.POST.get("pergunta", ""),
            instante=timezone.now(),
            origem=TELA,
        )
    except SemVersaoVigente:
        return redirect(destino())
    return redirect(destino(painel=1) + f"#troca-{troca.ordem}")


def enviar_sugestao(request, edital, conversa, destino):
    codigo = request.POST.get("sugestao", "")
    perfil = request.POST.get("perfil") or None
    pergunta = catalogo.POR_CODIGO.get(codigo)
    try:
        if pergunta and catalogo.PERFIL in pergunta.parametros and not perfil:
            opcoes = _opcoes(contexto(edital_id=edital.id, instante=timezone.now()).conteudo)
            if len(opcoes) != 1:
                return redirect(destino(painel=1, escolher=codigo))
            perfil = opcoes[0][0]
        troca = responder_sugestao(
            edital_id=edital.id,
            conversa=conversa,
            codigo=codigo,
            perfil=perfil,
            instante=timezone.now(),
            origem=TELA,
        )
    except SemVersaoVigente:
        return redirect(destino())
    except catalogo.ParametroRecusado:
        return redirect(destino(painel=1, recusa=1))
    return redirect(destino(painel=1) + f"#troca-{troca.ordem}")
