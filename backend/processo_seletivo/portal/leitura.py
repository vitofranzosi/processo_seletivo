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

from dataclasses import dataclass
from urllib.parse import urlencode

from django.utils.dateparse import parse_datetime

from processo_seletivo.editais.domain import calendario, quadro
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
#
# **E uma quinta, que a vitrine fundia na terceira.** "Inscrições encerradas" reunia o Edital que
# fechou as inscrições e segue — resultado a publicar, recurso aberto, convocação — e o Edital que
# acabou. Para quem se inscreveu são opostos: um ainda pede atenção, o outro é registro. O que os
# separa não é fase inventada, é ato: o desfecho do próprio Edital. Sem ele, o Edital está em
# andamento; com ele, encerrado. A situação é **da vitrine**, e não do período: o domínio das
# inscrições continua com três estados e uma ausência.
EM_ANDAMENTO = "em-andamento"
GRUPOS = (
    (ABERTO, "Inscrições abertas"),
    (FUTURO, "Próximas seleções"),
    (EM_ANDAMENTO, "Em andamento"),
    (ENCERRADO, "Seleções encerradas"),
    (NAO_DESIGNADO, "Outras seleções publicadas"),
)

# As duas situações de quem já fechou as inscrições: juntas, são a parte da vitrine que cresce sem
# parar, e por isso a que se reparte em páginas (`views.vitrine`).
SITUACOES_FOLHEADAS = (EM_ANDAMENTO, ENCERRADO)

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


# A marca do Edital que fechou as inscrições e não acabou. Era "Encerrada" — a do período —, e
# num cartão com recurso aberto ela dizia o contrário do que o cartão mostrava logo abaixo. A frase
# do período continua dizendo quando as inscrições fecharam; a marca diz em que pé está o Edital.
MARCA_EM_ANDAMENTO = ("andamento", "Em andamento")


def marca_da_selecao(periodo, desfecho):
    """A marca que a vitrine e a página da seleção mostram: a de `situacao_publica`, salvo no
    Edital em andamento.

    Separada de `situacao_publica` porque esta também marca a ficha de divulgação, que descreve o
    período de inscrições e não o andamento do Edital. O período cancelado conserva a marca
    própria: "Período cancelado" informa mais que "Em andamento", e é o que a página diz.
    """
    if estado_na_vitrine(periodo, desfecho) == EM_ANDAMENTO and not periodo.cancelado:
        return MARCA_EM_ANDAMENTO
    return situacao_publica(periodo, desfecho)


def estado_na_vitrine(periodo, desfecho):
    """O estado que decide grupo, ordem e filtro da vitrine (`FR-763`, `R-3`).

    O Edital com desfecho **próprio** vai para *"Seleções encerradas"* qualquer que seja o
    período: o sistema não recebe mais inscrição dele (`recebe_inscricoes` exige publicado), e
    pelo período um Edital encerrado antes do prazo cairia em *"Inscrições abertas"* — um convite
    ao que acabou. O de Processo encerrado fica onde o período o põe, porque continua recebendo —
    caso que, desde a decisão de 28/09 sobre o RC-118, só existe no Processo encerrado antes dela.

    **O período que terminou, sem desfecho nenhum, é "Em andamento"** — e o período cancelado
    também: o Edital segue publicado, e uma Retificação pode lhe dar outro período. Até aqui os
    dois iam para o mesmo grupo do Edital encerrado, e o histórico escondia o que ainda corre.

    **Sem desfecho nenhum, e não só sem o do Edital.** O Edital de Processo encerrado ou cancelado
    não corre mais depois que as inscrições fecham: "Em andamento" sobre "Processo seletivo
    encerrado em…" seriam duas coisas ditas da mesma seleção. Ele vai para o histórico, com a
    marca do período.
    """
    if desfecho is not None and desfecho.do_edital:
        return ENCERRADO
    if periodo.estado == ENCERRADO:
        return EM_ANDAMENTO if desfecho is None else ENCERRADO
    return periodo.estado


# ---------------------------------------------------------------------------
# A consulta da vitrine (024, FR-138 a FR-146a)
# ---------------------------------------------------------------------------

# Os cinco parâmetros da consulta e o da página, e nenhum a mais. A lista é fechada porque ela é
# também o que atravessa para o caminho de volta na página da seleção: repassar texto arbitrário
# para dentro de um endereço é como se abre redirecionamento (T-007).
PARAMETROS = ("busca", "unidade", "situacao", "perfil", "ordem", "pagina")

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
        # A página **não** é filtro: não entra em `ativa`, e o formulário não a reenvia — quem
        # muda a busca ou um filtro recomeça da primeira página do novo conjunto.
        "pagina": pagina_pedida(parametros.get("pagina")),
    }
    # "Há consulta ativa" **não** inclui a ordenação: ordenar não reduz o catálogo, e tratá-la como
    # filtro faria a lista perder os grupos por um gesto que não filtrou nada (FR-146, FR-146a).
    consulta["ativa"] = any(consulta[chave] for chave in ("busca", "unidade", "situacao", "perfil"))
    # **O grupo recolhido abre sozinho quando há filtro dele aplicado** (072, FR-1601). Fechado, ele
    # esconderia a explicação da lista que a pessoa está vendo. A busca não conta: ela fica fora do
    # grupo. A ordem padrão também não, pela mesma razão de não contar em `ativa`.
    consulta["recolhidos_aplicados"] = any(
        consulta[chave] for chave in ("unidade", "situacao", "perfil")
    ) or (consulta["ordem"] != ORDEM_PADRAO)
    # A ordem padrão **não** entra no endereço. Sem esta linha, uma vitrine sem consulta nenhuma
    # punha `?ordem=prazo` no link de todo cartão: o endereço deixava de ser canônico, e quem
    # copiasse compartilharia um parâmetro que não escolheu.
    consulta["querystring"] = _querystring(consulta, consulta["pagina"])
    return consulta


def na_pagina(consulta, numero):
    """A mesma consulta, noutra página — para o endereço que os cartões levam dizer a página
    **mostrada**: a pedida pode ter passado da última, e a volta da seleção cairia noutro lugar."""
    return {**consulta, "pagina": numero, "querystring": _querystring(consulta, numero)}


def _querystring(consulta, pagina):
    """A consulta como endereço, com a página pedida — a primeira não se escreve, como a ordem
    padrão: o endereço sem consulta continua sendo o canônico."""
    pares = {
        chave: consulta[chave]
        for chave in PARAMETROS
        if chave != "pagina"
        and consulta[chave]
        and not (chave == "ordem" and consulta[chave] == ORDEM_PADRAO)
    }
    if pagina > 1:
        pares["pagina"] = pagina
    return urlencode(pares)


# ---------------------------------------------------------------------------
# As páginas do histórico
# ---------------------------------------------------------------------------

# Par, porque a grade tem duas colunas: página ímpar terminaria com um cartão sozinho na linha.
POR_PAGINA = 10

# Acima disso o número é ruído de endereço colado, e não página que alguém pediu; o corte evita
# converter um inteiro de milhares de dígitos só para descobrir que ele passa da última.
_DIGITOS_DA_PAGINA = 6


def pagina_pedida(valor):
    """Inteiro positivo, ou 1. Texto, zero e negativo levam à primeira — nunca a um erro, pela
    mesma régua de `consulta_da_vitrine`: endereço malformado não pode ser pior que endereço sem
    consulta."""
    texto = str(valor or "").strip()
    if not texto.isascii() or not texto.isdigit() or len(texto) > _DIGITOS_DA_PAGINA:
        return 1
    return max(int(texto), 1)


@dataclass(frozen=True)
class Pagina:
    """O recorte de uma lista que se mostra de cada vez, e os endereços das vizinhas.

    `ancora` é o `id` do que antecede a lista: sem ela, trocar de página devolveria a pessoa ao
    topo, acima do formulário e das seleções abertas, e ela teria de rolar tudo de novo para
    continuar de onde estava.
    """

    itens: list
    numero: int
    total_de_paginas: int
    total: int
    consulta: dict
    ancora: str

    @property
    def varias(self):
        return self.total_de_paginas > 1

    @property
    def primeiro(self):
        return (self.numero - 1) * POR_PAGINA + 1 if self.total else 0

    @property
    def ultimo(self):
        return min(self.numero * POR_PAGINA, self.total)

    @property
    def intervalo(self):
        """ "11–20", ou só "21" quando a página tem um cartão: "21–21" se lê como defeito."""
        return (
            str(self.primeiro) if self.primeiro == self.ultimo else f"{self.primeiro}–{self.ultimo}"
        )

    @property
    def anterior(self):
        return self._endereco(self.numero - 1) if self.numero > 1 else ""

    @property
    def seguinte(self):
        return self._endereco(self.numero + 1) if self.numero < self.total_de_paginas else ""

    def _endereco(self, numero):
        # Sem consulta, só a âncora — e por isso o template escreve o endereço da vitrine antes:
        # `href="#ancora"` sozinho conservaria a querystring da página atual, e a "Anterior" da
        # segunda página voltaria à segunda.
        consulta = _querystring(self.consulta, numero)
        return f"{'?' if consulta else ''}{consulta}#{self.ancora}"


def paginar(itens, consulta, ancora):
    """A página pedida — ou a última, quando a pedida passa dela.

    A última, e não uma lista vazia: o endereço da página 5 continua existindo depois que o
    catálogo encolheu para quatro, e quem o guardou merece ver seleções, não um vazio.

    **A ordem vem pronta de quem chama.** Paginar antes de ordenar repartiria o histórico em
    páginas que não se sucedem.
    """
    total = len(itens)
    total_de_paginas = max(1, -(-total // POR_PAGINA))
    numero = min(consulta["pagina"], total_de_paginas)
    inicio = (numero - 1) * POR_PAGINA
    return Pagina(
        itens=itens[inicio : inicio + POR_PAGINA],
        numero=numero,
        total_de_paginas=total_de_paginas,
        total=total,
        consulta=consulta,
        ancora=ancora,
    )


# ---------------------------------------------------------------------------
# A ordem da vitrine
# ---------------------------------------------------------------------------


def _fechou_em(periodo, agora):
    """O fim das inscrições que já passou — `None` no período cancelado, que não "encerrou em"
    data nenhuma, e no que ainda não terminou."""
    if periodo.fim is not None and periodo.fim <= agora and not periodo.cancelado:
        return periodo.fim
    return None


def encerrou_em(selecao, agora):
    """Quando o Edital acabou — o instante que ordena o histórico.

    O do **ato de desfecho**, que é o fato que o pôs em "Seleções encerradas". Nunca a criação nem a
    publicação do Edital: um Edital publicado há um ano e encerrado ontem é o mais recente do
    histórico. Sob o desfecho **do Processo** o Edital continuou recebendo até o fim do período, e
    acabou no que veio por último. Sem a data do ato (`Desfecho.em` pode faltar), o fim das
    inscrições; sem ele, a vigência do conteúdo — é o que há, e mantém a ordem definida.
    """
    desfecho = selecao.get("desfecho")
    fechou = _fechou_em(selecao["periodo"], agora)
    ato = desfecho.em if desfecho is not None else None
    if ato is not None and (desfecho.do_edital or fechou is None):
        return ato
    if ato is not None:
        return max(ato, fechou)
    return fechou or selecao["vigente_desde"]


def _ordem_do_andamento(selecao, agora):
    """O que pede atenção primeiro, entre os Editais em andamento.

    Recurso aberto na frente, pelo prazo que termina antes: é o único item deste grupo que se pode
    **perder**. Depois, o que teve publicação mais recente; e o que ainda não publicou nada conta
    do fim das inscrições — de modo que o Edital recém-fechado não some atrás dos antigos.
    """
    resumo = selecao.get("acompanhamento") or {}
    prazo = resumo.get("prazo_unico") or resumo.get("primeiro_prazo")
    movimento = (
        resumo.get("mais_recente")
        or _fechou_em(selecao["periodo"], agora)
        or selecao["vigente_desde"]
    )
    return (
        (0, prazo.timestamp()) if prazo else (1, 0.0),
        -movimento.timestamp(),
    )


def ordenar_por_urgencia(selecoes, agora):
    """A ordem padrão: as situações, e dentro de cada uma o que importa primeiro a quem lê.

    Aberta e futura, pelo prazo **mais próximo** — é o que se pode perder. Em andamento, o recurso
    aberto e depois o movimento mais recente. Encerrada, a **mais recente**: quem volta ao
    histórico procura a seleção que acabou de fechar, e a ordem crescente punha na frente a mais
    antiga do catálogo, que é a que menos gente procura.

    **O desempate é total** — ano, número e identificador —, porque o histórico é repartido em
    páginas: com empate indefinido, a mesma seleção poderia aparecer em duas e outra em nenhuma.
    Vários Editais fechando no mesmo instante é o caso comum, e não o raro: um Processo costuma
    publicar os seus com um prazo só. Entre as encerradas o desempate também desce — o Edital de
    número maior é o mais novo dos que fecharam juntos.
    """

    def situacao(selecao):
        return ORDEM_DAS_SITUACOES.get(selecao["estado"], len(GRUPOS))

    def desempate(selecao):
        return (str(selecao["ano"]), str(selecao["numero"]), str(selecao["edital_id"]))

    def prazo(selecao):
        periodo = selecao["periodo"]
        return ((periodo.fim or periodo.inicio or agora), desempate(selecao))

    partes = {EM_ANDAMENTO: [], ENCERRADO: []}
    demais = []
    for selecao in selecoes:
        partes.get(selecao["estado"], demais).append(selecao)
    partes[ENCERRADO].sort(key=lambda s: (encerrou_em(s, agora), desempate(s)), reverse=True)
    partes[EM_ANDAMENTO].sort(key=lambda s: (_ordem_do_andamento(s, agora), desempate(s)))
    demais.sort(key=prazo)
    # A ordenação é estável: repartir por situação conserva a ordem que cada parte acabou de ganhar.
    return sorted(demais + partes[EM_ANDAMENTO] + partes[ENCERRADO], key=situacao)


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
        # O identificador desempata: sem ele, duas vigências iguais trocariam de lugar entre uma
        # página e a seguinte.
        resultado.sort(key=lambda s: (s["vigente_desde"], str(s["edital_id"])), reverse=True)
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
        # O lugar passou a ser visto no cartão, e o que se vê é o que se busca (072, FR-1610).
        *selecao.get("lugares_todos", []),
    ]
    return dobrar(" ".join(str(parte) for parte in partes))


def caminho_de_volta(parametros, destino):
    """O endereço da vitrine com a consulta que trouxe a pessoa até aqui (024, FR-144, T-007).

    **Só os parâmetros declarados atravessam, e só com valor de forma conhecida.** A página
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
    pares = {
        chave: valor
        for chave in PARAMETROS
        if chave != "pagina"
        and (valor := (parametros.get(chave) or "").strip()[:LIMITE_DA_BUSCA])
        and (chave not in aceitos or valor in aceitos[chave])
        and not (chave == "ordem" and valor == ORDEM_PADRAO)
    }
    # A página volta junto: quem abriu uma seleção da terceira página do histórico volta à
    # terceira. Só como inteiro — é o único valor que ela admite.
    if (pagina := pagina_pedida(parametros.get("pagina"))) > 1:
        pares["pagina"] = pagina
    consulta = urlencode(pares)
    return f"{destino}?{consulta}" if consulta else destino


# ---------------------------------------------------------------------------
# Os resultados divulgados, por Perfil, etapa e lista (062, FR-1148 a FR-1159)
# ---------------------------------------------------------------------------


def resultados_por_perfil(vigentes, conteudo):
    """As vigentes do Edital na forma da seção Vagas: Perfil, etapa, lista (062, D-005).

    **A página listava as vigentes em ordem de publicação**, e num Edital encerrado com dois Perfis
    e três listas eram seis linhas no mesmo nível, com o Perfil escondido no nome do marco e a
    ordem entre Perfis decidida pelo acaso do instante. Quem chega pergunta pela vaga, e a vaga já
    está organizada logo abaixo, na seção Vagas — a árvore repete essa organização.

    Recebe as vigentes de `historico_publico_do_edital`, já com `recurso_ate`, e o conteúdo vigente
    que a página já carregou. Não lê nada: tudo o que ela ordena está nas colunas da publicação, no
    cabeçalho congelado (já decodificado) e no conteúdo vigente (D-011).

    **As cadeias não se fundem.** Cada lista continua sendo a sua cadeia (a decisão do eixo da
    lista, da `021`): a natureza e a data ficam na linha da lista, e nunca sobem para a etapa
    (`FR-1155`); o histórico é um bloco por etapa, mas cada item diz a lista de onde veio.
    """
    perfis_vigentes = conteudo.get("profiles") or []
    posicao_do_perfil = {str(perfil.get("id")): i for i, perfil in enumerate(perfis_vigentes)}
    nome_vigente = {str(perfil.get("id")): perfil.get("name") or "" for perfil in perfis_vigentes}
    ordem_das_listas = {
        str(perfil.get("id")): {
            str(modalidade.get("id")): i
            for i, modalidade in enumerate(perfil.get("competitionModalities") or [])
        }
        for perfil in perfis_vigentes
    }

    grupos = {}
    for item in vigentes:
        publicacao = item["publicacao"]
        grupos.setdefault(str(publicacao.perfil_id), {}).setdefault(
            str(publicacao.marco_id), []
        ).append(item)

    perfis = []
    for perfil_id, por_marco in grupos.items():
        todas = [item for itens in por_marco.values() for item in itens]
        etapas = [
            _etapa(marco_id, itens, ordem_das_listas.get(perfil_id, {}))
            for marco_id, itens in por_marco.items()
        ]
        # **A ordem do certame, e não a de divulgação** (D-010): o mesmo `marco_codigo` congelado
        # que a Área do Candidato usa para ordenar as situações da pessoa.
        etapas.sort(key=lambda etapa: (etapa["codigo"], etapa["nome"]))
        perfis.append(
            {
                "perfil_id": perfil_id,
                # **O nome vigente, que é o da seção Vagas** (D-004 da spec). O congelado só entra
                # quando uma Retificação tirou o Perfil do Edital: um resultado publicado não deixa
                # de ser alcançável porque a vaga mudou, e não há outro nome a dar.
                "nome": nome_vigente.get(perfil_id) or _mais_recente(todas).get("perfil", ""),
                "etapas": etapas,
                "_ordem": (
                    (0, posicao_do_perfil[perfil_id], None)
                    if perfil_id in posicao_do_perfil
                    else (1, 0, _mais_recente(todas)["publicacao"].publicado_em)
                ),
            }
        )
    perfis.sort(key=lambda perfil: perfil.pop("_ordem"))
    return perfis


def _etapa(marco_id, itens, ordem_das_listas):
    itens = sorted(itens, key=lambda item: _chave_da_lista(item, ordem_das_listas))
    # As listas de uma etapa podem ter sido publicadas sob versões diferentes; o título é o da
    # vigente mais recente, sem corte nem reescrita (decisão recebida 4).
    recente = _mais_recente(itens)
    return {
        "marco_id": marco_id,
        "nome": recente.get("marco", ""),
        "codigo": recente.get("marco_codigo", ""),
        "listas": [
            {
                "lista_id": item["publicacao"].lista_id,
                "nome": item["lista"],
                "publicacao": item["publicacao"],
                "natureza_rotulo": item["natureza_rotulo"],
                "recurso_ate": item.get("recurso_ate"),
            }
            for item in itens
        ],
        # Na ordem das listas, e dentro de cada uma da mais recente para a mais antiga — que é a
        # ordem em que `historico_publico_do_edital` já entrega a cadeia.
        "anteriores": [anterior for item in itens for anterior in item["anteriores"]],
    }


def _chave_da_lista(item, ordem_das_listas):
    """Ampla concorrência primeiro; depois a ordem em que o Perfil declara as Modalidades (D-008).

    O recorte sem lista **é** a ampla concorrência — o mesmo do sorteio, e não a Modalidade que um
    Edital eventualmente declare com esse nome. Uma lista que o vigente já não conhece vai para o
    fim, pelo nome gravado, em vez de sumir.
    """
    return posicao_da_lista(item["publicacao"].lista_id, item["lista"], ordem_das_listas)


def posicao_da_lista(lista_id, nome, ordem_das_listas):
    """A chave de ordenação de uma lista — a mesma para resultados e para sorteios (145)."""
    if lista_id is None:
        return (0, 0, "")
    if str(lista_id) in ordem_das_listas:
        return (1, ordem_das_listas[str(lista_id)], "")
    return (2, 0, nome)


def nome_da_lista_citada(relacao):
    """O nome da lista na versão que a relação citou; "" quando ela não tem lista (021, FR-045).

    Da versão citada, e não do conteúdo vigente, que uma Retificação posterior pode ter mudado.
    """
    if not relacao.lista_id:
        return ""
    for perfil in relacao.versao.content.get("profiles") or []:
        if str(perfil.get("id")) != str(relacao.perfil_id):
            continue
        for modalidade in perfil.get("competitionModalities") or []:
            if str(modalidade.get("id")) == str(relacao.lista_id):
                return modalidade.get("name") or ""
    return ""


def _mais_recente(itens):
    return max(itens, key=lambda item: item["publicacao"].publicado_em)


# ---------------------------------------------------------------------------
# O sorteio de cada vaga, no cartão dela (145)
# ---------------------------------------------------------------------------

AMPLA_CONCORRENCIA = "Ampla concorrência"


def sorteios_por_vaga(sorteios, conteudo):
    """Os sorteios do Edital na forma do cartão: vaga, marco, lista (145, FR-5150 a FR-5153).

    **A lateral dizia cada lista num bloco próprio**, com o nome inteiro da vaga em cada um: num
    Edital de três vagas e três listas eram nove blocos, mais de quatro mil pontos de altura ao lado
    de cartões de duzentos e poucos, e do título de uma vaga até a relação dela eram duas telas e
    meia de celular. Quem chega pergunta pela vaga — é a mesma razão de `resultados_por_perfil`.

    Recebe o que `sorteios_do_edital` já leu e o conteúdo vigente que a página já carregou, e **não
    lê nada**: as duas consultas do sorteio continuam sendo duas (FR-5161).

    Devolve `(por_vaga, resumo)`. `por_vaga` é indexado pelo identificador do Perfil; `resumo` é o
    que o Edital inteiro tem a dizer, mais as relações de vaga que o conteúdo vigente já não conhece
    — elas continuam publicadas, e sumir da página seria esconder um ato (FR-5160).
    """
    perfis = {str(perfil.get("id")): perfil for perfil in conteudo.get("profiles") or []}
    grupos, sem_vaga = {}, []
    for item in sorteios:
        relacao = item["relacao"]
        if str(relacao.perfil_id) not in perfis:
            sem_vaga.append(item)
            continue
        grupos.setdefault(str(relacao.perfil_id), {}).setdefault(str(relacao.marco_id), []).append(
            item
        )

    por_vaga = {}
    for perfil_id, por_marco in grupos.items():
        perfil = perfis[perfil_id]
        ordem_dos_marcos = {
            str(marco.get("id")): i
            for i, marco in enumerate(perfil.get("classificationMilestones") or [])
        }
        ordem_das_listas = {
            str(modalidade.get("id")): i
            for i, modalidade in enumerate(perfil.get("competitionModalities") or [])
        }
        marcos = [
            _marco_do_sorteio(itens, ordem_das_listas)
            # Marco que o vigente já não declara vai para o fim, em vez de sumir.
            for _, itens in sorted(
                por_marco.items(),
                key=lambda par: ordem_dos_marcos.get(par[0], len(ordem_dos_marcos)),
            )
        ]
        por_vaga[perfil_id] = {
            "marcos": marcos,
            # O marco é nomeado só quando a vaga tem mais de um: com um só, o nome repetiria em
            # cada cartão o que o rótulo do bloco já diz (FR-5151).
            "varios_marcos": len(marcos) > 1,
        }

    return por_vaga, {
        "total": len(sorteios),
        "realizados": sum(1 for item in sorteios if item["sorteio"]),
        # A frase "está na vaga dele" só é verdade havendo cartão que o receba.
        "em_cartao": bool(por_vaga),
        # Com o nome da lista — também o da ampla, e o que o vigente já não diz (FR-5153): sem
        # ele, duas relações da mesma vaga retirada seriam dois acessos de texto igual.
        "sem_vaga": [{**item, "lista": _nome_da_lista_do_sorteio(item)} for item in sem_vaga],
    }


def _marco_do_sorteio(itens, ordem_das_listas):
    listas = sorted(
        (
            {
                "nome": _nome_da_lista_do_sorteio(item),
                "relacao": item["relacao"],
                "sorteio": item["sorteio"],
            }
            for item in itens
        ),
        key=lambda lista: posicao_da_lista(
            lista["relacao"].lista_id, lista["nome"], ordem_das_listas
        ),
    )
    realizados = [lista["sorteio"] for lista in listas if lista["sorteio"]]
    # **O estado é dito uma vez quando as listas estão no mesmo ponto** (FR-5154): três listas
    # aguardando são uma frase, e não três. Sorteadas em instantes diferentes, a frase única diria
    # a hora de uma só — então cada linha diz a sua.
    fechamentos = {_ate_o_minuto(lista["relacao"].publicada_em) for lista in listas}
    execucoes = {_ate_o_minuto(sorteio.executado_em) for sorteio in realizados}
    aguardando = not realizados and len(fechamentos) == 1
    realizado = len(realizados) == len(listas) and len(execucoes) == 1
    return {
        "nome": itens[0]["marco"],
        "listas": listas,
        "aguardando": aguardando,
        "realizado": realizado,
        "uniforme": aguardando or realizado,
        "realizados": len(realizados),
        "fechada_em": listas[0]["relacao"].publicada_em,
        "executado_em": realizados[0].executado_em if realizados else None,
    }


def _nome_da_lista_do_sorteio(item):
    """O recorte sem lista **é** a ampla concorrência (FR-5153) — o mesmo de `_chave_da_lista`.

    Lista que o conteúdo vigente já não nomeia é lida da versão que a relação citou, como faz a
    página da própria relação: inventar um rótulo seria afirmar uma denominação que o Edital não
    publica, e deixá-la sem nome a confundiria com a ampla.
    """
    relacao = item["relacao"]
    if not relacao.lista_id:
        return AMPLA_CONCORRENCIA
    return item["lista"] or nome_da_lista_citada(relacao)


def _ate_o_minuto(instante):
    return instante.replace(second=0, microsecond=0)


# ---------------------------------------------------------------------------
# O prazo de recurso de cada resultado vigente (047, FR-770; 072, research T-001)
# ---------------------------------------------------------------------------


def prazos_de_recurso(vigentes_por_edital, conteudo_vigente, agora):
    """Acrescenta `recurso_ate` a cada vigente: o fim da janela, só enquanto ela corre.

    **Saiu de `views.selecao` para que a vitrine e a página digam o mesmo prazo** (072, FR-1635). A
    conta é a da interposição (`janela_da_publicacao_divulgada`), sobre a versão que cada ato citou
    e a vigente do Edital (RC-121); o que esta função acrescenta é só o corte por `agora`, que a
    página fazia sozinha. Duas cópias do corte seriam duas réguas para o mesmo prazo.

    Recebe `{edital_id: vigentes}` e `{edital_id: conteúdo vigente}` — um Edital, para a página;
    todos os carregados, para a vitrine — e lê as versões citadas numa consulta só, para todos.
    """
    from processo_seletivo.recursos.application.selectors import (
        conteudos_citados,
        janela_da_publicacao_divulgada,
    )

    todas = [item for itens in vigentes_por_edital.values() for item in itens]
    citados = conteudos_citados([item["publicacao"] for item in todas])
    for edital_id, itens in vigentes_por_edital.items():
        for item in itens:
            janela = janela_da_publicacao_divulgada(
                item["publicacao"],
                conteudo=citados.get(item["publicacao"].ato_id) or {},
                vigente=conteudo_vigente[edital_id],
            )
            item["recurso_ate"] = janela[1] if janela is not None and agora <= janela[1] else None
    return vigentes_por_edital


# ---------------------------------------------------------------------------
# A oferta de cada Perfil, dita do mesmo jeito no cartão e na página (072, research T-005)
# ---------------------------------------------------------------------------

# Os mesmos que o documento lê para imprimir `CR` (096): uma lista só, no domínio.
TIPOS_COM_RESERVA = quadro.TIPOS_DE_CADASTRO


def quantidade_da_oferta(vagas, tipo_de_reserva):
    """A quantidade, separada do nome do Perfil (072, FR-1607; Q6).

    "Vaga" nomeia o Perfil e também a quantidade, e "2 vagas" num cartão de dois Perfis não diz qual
    das duas coisas. Por isso a quantidade vem sempre com o número, e o nome do Perfil nunca leva a
    palavra. Sem vaga imediata, o cadastro reserva **é** a oferta (024, FR-136); sem os dois, nada é
    escrito — "0 vagas" em destaque leria como ausência.
    """
    reserva = tipo_de_reserva in TIPOS_COM_RESERVA
    if vagas:
        quantas = f"{vagas} vaga{'s' if vagas != 1 else ''}"
        return f"{quantas} e cadastro reserva" if reserva else quantas
    return "cadastro reserva" if reserva else ""


def os_primeiros(itens, teto, termo="", texto=str):
    """`(mostrados, sobram)`: até `teto` itens, e quantos ficaram de fora (072, FR-1608 a FR-1610).

    **Com busca, o que casa com o termo vem primeiro.** O teto existe para que um Edital de trinta
    polos não vire trinta linhas; sem esta ordem, ele esconderia justamente o Perfil que fez o
    cartão ser encontrado — e o resultado pareceria erro (024, T-011: o que se busca é o que se vê).
    A ordem entre os que casam, e entre os que não casam, é a publicada.
    """
    itens = list(itens)
    if termo:
        procurado = dobrar(termo)
        itens.sort(key=lambda item: procurado not in dobrar(texto(item)))
    return itens[:teto], max(len(itens) - teto, 0)


# ---------------------------------------------------------------------------
# O resumo do que foi publicado, no cartão da vitrine (072, D-004, FR-1629 a FR-1633)
# ---------------------------------------------------------------------------

NATUREZA_NO_PLURAL = {
    "PRELIMINAR": "resultados preliminares",
    "DEFINITIVA": "resultados definitivos",
}


def resumo_do_acompanhamento(vigentes):
    """Resultado e prazo de recurso de um Edital, resumidos sem fazer um prazo valer para todos.

    Recebe os vigentes já com `recurso_ate` (`prazos_de_recurso`) — as mesmas linhas que a página da
    seleção mostra, de modo que cartão e página não têm como discordar (FR-1635). Devolve `None` sem
    vigente: nenhuma frase de ausência (FR-1633).

    **A regra é a da clarificação de 12/10** (D-004): com M vigentes e N deles de recurso aberto,

    - o prazo é dito **uma vez** só quando N = M e todos terminam no mesmo instante;
    - em qualquer outro caso com N > 0, "aberto para N de M" e o término **mais próximo entre os
      abertos** — nunca uma frase de prazo sem escopo;
    - a natureza só sai quando é a de todos: cada lista é a sua cadeia, e o preliminar de uma não
      faz o Edital "preliminar" (062, FR-1155).

    Perfil, etapa e lista ficam na página da seleção, onde a árvore da 062 já os organiza.
    """
    if not vigentes:
        return None
    naturezas = {item["publicacao"].natureza for item in vigentes}
    comum = naturezas.pop() if len(naturezas) == 1 else None
    terminos = [item["recurso_ate"] for item in vigentes if item.get("recurso_ate")]
    todos_juntos = len(terminos) == len(vigentes) and len(set(terminos)) == 1
    return {
        "total": len(vigentes),
        "mais_recente": max(item["publicacao"].publicado_em for item in vigentes),
        "natureza": vigentes[0]["natureza_rotulo"] if comum else "",
        "natureza_no_plural": NATUREZA_NO_PLURAL.get(comum, "") if comum else "",
        "abertos": len(terminos),
        "prazo_unico": terminos[0] if todos_juntos else None,
        "primeiro_prazo": min(terminos) if terminos and not todos_juntos else None,
    }
