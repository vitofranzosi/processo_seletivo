"""O que **duas** telas do portal leem, e o saneamento da consulta pública.

Módulo nomeado, e não função solta em `views.py`, por uma razão que o repositório já pagou uma vez:
o Cronograma passou a ser mostrado em dois lugares — a área de quem já se inscreveu e a página
pública de quem ainda decide —, e duplicar o cálculo da situação do Evento criaria duas verdades
sobre "em curso". A `011` registrou o mesmo defeito com duas ordenações por nome no mesmo arquivo.

**A fase do Evento não é mais decidida aqui** (047, `FR-765`). Este módulo tinha régua própria, que
comparava o dia em UTC e não conhecia o Evento cancelado, enquanto a gestão lia outra, a da `045`.
Eram duas verdades sobre o mesmo cronograma, uma de cada lado. A régua agora mora no domínio
(`editais/domain/fase_do_evento.py`), e aqui ela só é traduzida para a marcação da tela.

Aqui não há regra de domínio nova. O que existe é leitura: conteúdo publicado entra, estrutura de
tela sai. Nada neste módulo grava, e nada aqui sabe quem está lendo.
"""

from urllib.parse import urlencode

from django.utils.dateparse import parse_datetime

from processo_seletivo.editais.domain import calendario
from processo_seletivo.editais.domain.fase_do_evento import (
    descricao_do_evento,
    esta_cancelado,
    fase_publica_do_evento,
    marcos_pendentes,
)
from processo_seletivo.inscricoes.domain.periodo import ABERTO, ENCERRADO, FUTURO, NAO_DESIGNADO
from processo_seletivo.shared.texto import dobrar

# ---------------------------------------------------------------------------
# O Cronograma (024, FR-125 a FR-128)
# ---------------------------------------------------------------------------


def cronograma(conteudo, agora):
    """Os Eventos do processo, na ordem publicada, com a situação **do evento**.

    Concluído, em curso ou por vir descrevem o Evento — nunca a pessoa. É a mesma distinção da
    `FR-076`, dita em dado: nada aqui sabe quem está lendo (FR-126).

    **O caso vazio não é decidido aqui.** A função devolve lista vazia, e cada tela resolve o que
    fazer com isso: a área do candidato escreve que o Edital não publicou cronograma, porque ali o
    assunto é a inscrição da pessoa e um buraco sem explicação seria pior; a página pública omite a
    seção inteira, porque ali o assunto é o Edital e dizer "não publicou" afirmaria uma omissão que
    o Edital pode nunca ter tido o que declarar (FR-128).
    """
    eventos = []
    for evento in sorted(conteudo.get("schedule") or [], key=lambda item: item.get("order") or 0):
        inicio = parse_datetime(evento.get("startAt") or "")
        fim = parse_datetime(evento.get("endAt") or "") if evento.get("endAt") else None
        situacao = situacao_do_evento(evento, conteudo, agora)
        eventos.append(
            {
                "nome": evento.get("description") or evento.get("type") or "",
                "inicio": inicio,
                "fim": fim,
                "situacao": situacao,
                # Onde o evento acontece, quando o Edital o declarou (021, D-008, FR-057;
                # 024, FR-127). Vazio significa não declarado, e a tela simplesmente não escreve
                # linha alguma — dizer "local não informado" afirmaria uma omissão onde o Edital
                # pode nunca ter tido o que declarar.
                "local": (evento.get("location") or "").strip(),
            }
        )
    return eventos


# A fase do domínio, dita com as classes que a marcação já usava (047, `R-1`). As três primeiras são
# as da `010` e da `024`, letra por letra: testes afirmam sobre `class="marco em_curso"`, e o CSS
# depende delas. A quarta nasce com a 047.
CLASSE_DA_FASE = {
    calendario.PLANEJADO: "futuro",
    calendario.EM_ANDAMENTO: "em_curso",
    calendario.CONCLUIDO: "concluido",
}
CANCELADO = "cancelado"


def situacao_do_evento(evento, conteudo, agora):
    """A classe da linha do Evento: a fase da régua única, ou `cancelado`, ou nada.

    **O cancelado é dito, e não tem fase** (`FR-766`): anunciar *"acontecendo agora"* ou uma data
    por vir de um Evento que saiu do cronograma é afirmar o que não vai acontecer. O período de
    inscrições é a exceção, e ela é da régua, não daqui (`fase_publica_do_evento`).

    **Sem início, nada**: a conferência de forma já acusa o Evento assim, e inventar-lhe uma fase
    seria a tela criando o que as datas não dão.
    """
    fase = fase_publica_do_evento(evento, conteudo, agora)
    if fase is not None:
        return CLASSE_DA_FASE[fase]
    return CANCELADO if esta_cancelado(evento) else ""


# ---------------------------------------------------------------------------
# Agora e próximo (047, `FR-767`, `FR-768`)
# ---------------------------------------------------------------------------


def agora_e_proximo(conteudo, agora):
    """O que está em andamento e o que vem depois, lidos da lista de marcos da gestão.

    **A lista é a do pulso** (`marcos_pendentes`), e não uma terceira leitura do cronograma: a
    gestão e a página pública respondem à mesma pergunta com a mesma resposta.

    **O período de inscrições não entra.** A marca e a frase do período já o dizem, com prazo e
    tudo; repeti-lo aqui seria a mesma informação duas vezes no mesmo cabeçalho. Quando o próximo
    Evento **é** o período, o bloco não diz próximo nenhum — o que viria depois dele não é o
    próximo, e anunciá-lo inverteria a ordem do que acontece.

    **Nada é inventado para preencher o vazio** (`FR-768`): sem Evento pendente, as duas listas
    vêm vazias e a tela omite o bloco. Nunca *"em análise"*: nenhum fato registra essa fase.
    """
    pendentes = marcos_pendentes(conteudo, agora)
    em_andamento = [
        {"nome": descricao_do_evento(evento), "inicio": inicio, "fim": fim}
        for evento, inicio, fim, fase in pendentes
        if fase == calendario.EM_ANDAMENTO and evento.get("isRegistrationPeriod") is not True
    ]
    planejados = [item for item in pendentes if item[3] == calendario.PLANEJADO]
    proximos = []
    if planejados:
        primeiro = planejados[0][1]
        # Os que empatam no início são ditos todos, na ordem publicada (caso-limite da 047): a
        # lista do pulso desempata pelo nome, e o Edital pode ter declarado outra ordem.
        empatados = sorted(
            (item for item in planejados if item[1] == primeiro),
            key=lambda item: item[0].get("order") or 0,
        )
        if not any(evento.get("isRegistrationPeriod") is True for evento, *_ in empatados):
            proximos = [
                {"nome": descricao_do_evento(evento), "inicio": inicio, "fim": fim}
                for evento, inicio, fim, _ in empatados
            ]
    return {"em_andamento": em_andamento, "proximos": proximos}


# ---------------------------------------------------------------------------
# O histórico normativo (024, FR-129 a FR-133)
# ---------------------------------------------------------------------------


def atos_publicados(edital_id):
    """Os atos publicados do Edital, prontos para a tela.

    O selector devolve o que aconteceu; aqui as alterações de cada Retificação viram português.
    A tradução acontece **neste** ponto, e não no selector, porque ela é decisão de apresentação:
    a API pública continua devolvendo `targetPath`, que é o que uma máquina precisa.

    O conteúdo-base de cada Retificação é o que dá nome às entidades alteradas — é o que o Edital
    dizia quando o ato foi escrito, e é o que quem lê o histórico reconhece.
    """
    from processo_seletivo.publicacoes.application import selectors
    from processo_seletivo.publicacoes.domain.alteracoes import alteracoes_legiveis

    atos = selectors.atos_publicados(edital_id=edital_id)
    for ato in atos:
        retificacao = ato.pop("retificacao", None)
        ato["justificativa"] = retificacao.justification if retificacao else ""
        ato["alteracoes"] = (
            alteracoes_legiveis(retificacao.base_snapshot.content, retificacao.alteracoes.all())
            if retificacao
            else []
        )
    return atos


# ---------------------------------------------------------------------------
# As quatro situações da vitrine (024, FR-145, FR-146)
# ---------------------------------------------------------------------------

# O domínio distingue quatro, e a tela passa a dizer as quatro. A quarta **não é** "encerrada":
# chamá-la assim afirmaria um fechamento que Edital nenhum declarou. É o Edital que não recebe
# inscrição por este sistema, e para ele nenhuma frase de prazo é escrita (FR-149).
GRUPOS = (
    (ABERTO, "Inscrições abertas"),
    (FUTURO, "Próximas seleções"),
    (ENCERRADO, "Inscrições encerradas"),
    (NAO_DESIGNADO, "Outras seleções publicadas"),
)

# A ordem de urgência de quem lê, e não a de criação de quem publicou.
ORDEM_DAS_SITUACOES = {estado: posicao for posicao, (estado, _) in enumerate(GRUPOS)}


def agrupar_por_situacao(selecoes):
    """As seleções em grupos nomeados, na ordem das quatro situações — grupo vazio não aparece.

    Substitui o par `abertas`/`outras`, em que "outras" era literalmente tudo o que não estava
    aberto: futuras, encerradas e sem período designado caíam no mesmo balde, embora o domínio já
    distinguisse as três. Quem procurava o que ainda vai abrir tinha de ler tudo para descobrir o
    que já fechou.
    """
    por_estado = {}
    for selecao in selecoes:
        por_estado.setdefault(selecao["estado"], []).append(selecao)
    return [
        {"estado": estado, "titulo": titulo, "selecoes": por_estado[estado]}
        for estado, titulo in GRUPOS
        if por_estado.get(estado)
    ]


# O rótulo da situação **de uma** seleção — no singular, porque ele vai no cartão. Os títulos de
# `GRUPOS` são de grupo e estão no plural; usar um pelo outro faria um cartão anunciar-se como
# categoria (FR-145).
# **Curtos, e diferentes do título do grupo.** A primeira versão repetia o título — "Inscrições
# abertas" na etiqueta, no cabeçalho do grupo e outra vez na frase do período: três vezes as mesmas
# palavras no mesmo cartão. Etiqueta é para varrer com o olho, não para ler.
SITUACAO_DO_CARTAO = {
    ABERTO: "Aberta",
    FUTURO: "Em breve",
    ENCERRADO: "Encerrada",
    # Não é "encerrada", e a diferença é normativa: nenhum Edital declarou fechamento aqui. O que
    # há é um Edital que não recebe inscrição por este sistema, e continua consultável (FR-149).
    NAO_DESIGNADO: "Consulta",
}
MARCA_DO_PERIODO_CANCELADO = "Período cancelado"


# ---------------------------------------------------------------------------
# O desfecho vence o período (047, `FR-760` a `FR-763`, `D-003`)
# ---------------------------------------------------------------------------

# A marca do Edital que acabou. **Diz de quem é o fim**, e por isso é mais longa que as quatro de
# cima: "Encerrada" já é a marca do período que terminou, e o cartão do Edital encerrado precisa
# se distinguir dele (`FR-763`).
#
# **Só o desfecho do Edital tem marca.** O do Processo não fecha o recebimento de inscrições
# (`Desfecho.do_edital`): um Edital publicado de Processo encerrado segue a marca do próprio
# período, e o encerramento do Processo é dito como fato, abaixo dela (`_periodo.html`).
MARCA_DO_DESFECHO = {
    "CANCELADO": ("cancelado", "Edital cancelado"),
    "ENCERRADO": ("encerrado_edital", "Edital encerrado"),
}


def situacao_publica(periodo, desfecho):
    """`(chave, rótulo)` da marca da seleção: o desfecho, quando há, e senão a do período.

    **O desfecho vence** porque o período descreve a norma e o desfecho descreve o que aconteceu
    com ela. Até a 047, um Edital cancelado dentro do período anunciava *"Aberta — faltam 19
    dias"*: a marca lia só o período, e o cancelamento não chegava à página (`FR-761`).
    """
    if desfecho is not None and desfecho.do_edital:
        return MARCA_DO_DESFECHO[desfecho.operacao]
    # **O período cancelado é encerrado para o grupo, e não para a etiqueta** (RC-119, revisão do
    # PR 221). A régua o lê como `ENCERRADO` — ele não recebe, e vai para as encerradas —, mas
    # "Encerrada" no cartão e "cancelado" na página seriam duas coisas ditas da mesma seleção.
    if getattr(periodo, "cancelado", False):
        return periodo.estado, MARCA_DO_PERIODO_CANCELADO
    return periodo.estado, SITUACAO_DO_CARTAO.get(periodo.estado, "")


def estado_na_vitrine(periodo, desfecho):
    """O estado que decide grupo, ordem e filtro da vitrine (`FR-763`, `R-3`).

    O Edital com desfecho **próprio** vai para *"Inscrições encerradas"* qualquer que seja o
    período: o sistema não recebe mais inscrição dele (`recebe_inscricoes` exige publicado). O de
    Processo encerrado fica onde o período o põe, porque continua recebendo — caso que, desde a
    decisão de 28/09 sobre o RC-118, só existe no Processo encerrado antes dela. Pelo período, um
    Edital encerrado antes do prazo cairia em *"Inscrições abertas"* — um convite ao que acabou.
    Não é um quinto grupo: a `024` fixou quatro pelo que o candidato procura, e a marca do cartão
    já diz de quem é o fim.
    """
    return ENCERRADO if desfecho is not None and desfecho.do_edital else periodo.estado


# ---------------------------------------------------------------------------
# A consulta da vitrine (024, FR-138 a FR-146a)
# ---------------------------------------------------------------------------

# Os cinco parâmetros, e nenhum a mais. A lista é fechada porque ela é também o que atravessa para
# o caminho de volta na página da seleção: repassar texto arbitrário para dentro de um endereço é
# como se abre redirecionamento (T-007).
PARAMETROS = ("busca", "unidade", "situacao", "perfil", "ordem")

ORDEM_PADRAO = "prazo"
ORDENS = (ORDEM_PADRAO, "recentes")

LIMITE_DA_BUSCA = 200


def opcoes_da_consulta(selecoes):
    """As unidades e os Perfis que **existem** no catálogo publicado.

    Os filtros são montados a partir do catálogo, e não de uma lista fixa: oferecer um campus que
    não tem seleção nenhuma é prometer resultado onde não há, e uma lista fixa envelhece calada.
    """
    unidades = sorted({selecao["unidade"] for selecao in selecoes if selecao["unidade"]})
    perfis = sorted(
        {nome for selecao in selecoes for nome in selecao["perfis"] if nome},
        key=dobrar,
    )
    return {"unidades": unidades, "perfis": perfis}


def consulta_da_vitrine(parametros, opcoes):
    """O que a pessoa pediu, saneado (024, T-004).

    **Valor irreconhecível é lido como ausência do filtro, nunca como erro.** Recusar com 4xx daria
    a um endereço colado um comportamento pior do que o de não filtrar, e abriria superfície de
    mensagem de erro numa página anônima. É a mesma régua da `FR-142`: consulta sem resultado não
    é erro, e consulta malformada também não.
    """
    busca = (parametros.get("busca") or "").strip()[:LIMITE_DA_BUSCA]
    unidade = parametros.get("unidade") or ""
    situacao = parametros.get("situacao") or ""
    perfil = parametros.get("perfil") or ""
    ordem = parametros.get("ordem") or ""
    consulta = {
        "busca": busca,
        "unidade": unidade if unidade in opcoes["unidades"] else "",
        "situacao": situacao if situacao in ORDEM_DAS_SITUACOES else "",
        "perfil": perfil if perfil in opcoes["perfis"] else "",
        "ordem": ordem if ordem in ORDENS else ORDEM_PADRAO,
    }
    # "Há consulta ativa" **não** inclui a ordenação: ordenar não reduz o catálogo, e tratá-la como
    # filtro faria a lista perder os grupos por um gesto que não filtrou nada (FR-146, FR-146a).
    consulta["ativa"] = any(consulta[chave] for chave in ("busca", "unidade", "situacao", "perfil"))
    # A ordem padrão **não** entra no endereço. Sem esta linha, uma vitrine sem consulta nenhuma
    # punha `?ordem=prazo` no link de todo cartão: o endereço deixava de ser canônico, e quem
    # copiasse compartilharia um parâmetro que não escolheu.
    consulta["querystring"] = urlencode(
        {
            chave: consulta[chave]
            for chave in PARAMETROS
            if consulta[chave] and not (chave == "ordem" and consulta[chave] == ORDEM_PADRAO)
        }
    )
    return consulta


def filtrar(selecoes, consulta):
    """Os filtros se somam — `E` entre eles, nunca `OU` (FR-139).

    `OU` devolveria mais resultados a cada filtro acrescentado, que é o contrário do que quem
    filtra está pedindo.
    """
    resultado = list(selecoes)
    if consulta["unidade"]:
        resultado = [s for s in resultado if s["unidade"] == consulta["unidade"]]
    if consulta["situacao"]:
        resultado = [s for s in resultado if s["estado"] == consulta["situacao"]]
    if consulta["perfil"]:
        resultado = [s for s in resultado if consulta["perfil"] in s["perfis"]]
    if consulta["busca"]:
        termo = dobrar(consulta["busca"])
        resultado = [s for s in resultado if termo in _texto_do_cartao(s)]
    if consulta["ordem"] == "recentes":
        # Pela vigência **do conteúdo exibido**, e não pelo instante do ato que o produziu: uma
        # Retificação publicada hoje e vigente semana que vem não muda a posição hoje, porque o
        # cartão ainda mostra o conteúdo anterior (FR-140, T-006).
        resultado.sort(key=lambda s: s["vigente_desde"], reverse=True)
    return resultado


def _texto_do_cartao(selecao):
    """O que se busca é **o que se vê** (FR-138, T-011).

    Varrer descrição, requisitos ou o texto das seções devolveria cartões em que o termo procurado
    não aparece em lugar nenhum — e o resultado pareceria erro. E percorrer o conteúdo inteiro de
    cada versão publicada a cada busca é a porta para o índice que a `D-003` adiou.
    """
    partes = [
        selecao["processo_titulo"],
        selecao["titulo"],
        f"{selecao['numero']}/{selecao['ano']}",
        selecao["unidade"],
        *selecao["perfis"],
    ]
    return dobrar(" ".join(str(parte) for parte in partes))


def caminho_de_volta(parametros, destino):
    """O endereço da vitrine com a consulta que trouxe a pessoa até aqui (024, FR-144, T-007).

    **Só os cinco parâmetros declarados atravessam, e só com valor de forma conhecida.** A página
    da seleção não interpreta a consulta — ela só a devolve —, e por isso o que ela repassa precisa
    ser conferido: valor arbitrário ecoado para dentro de um endereço é como se abre
    redirecionamento. O portal já trata disso em `_destino_seguro`, e o critério aqui é mais
    estreito.

    O que se confere, e por quê:

    - **nome do parâmetro**, contra `PARAMETROS` — nada mais atravessa;
    - **`situacao` e `ordem`**, contra as enumerações — são os dois que a tela lê como estado;
    - **comprimento**, sempre. `unidade` e `perfil` seguem como texto livre porque a vitrine os
      confere na chegada, contra o catálogo; o que ela não faz é limitar o tamanho, e um valor de
      cem mil caracteres viraria um `href` de cem mil caracteres em cada cartão.

    O destino é caminho relativo desta aplicação e os valores vão percent-encoded, de modo que o
    resultado nunca sai deste host.
    """
    aceitos = {"situacao": ORDEM_DAS_SITUACOES, "ordem": ORDENS}
    consulta = urlencode(
        {
            chave: valor
            for chave in PARAMETROS
            if (valor := (parametros.get(chave) or "").strip()[:LIMITE_DA_BUSCA])
            and (chave not in aceitos or valor in aceitos[chave])
            and not (chave == "ordem" and valor == ORDEM_PADRAO)
        }
    )
    return f"{destino}?{consulta}" if consulta else destino
