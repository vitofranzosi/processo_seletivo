"""A convocação de um recorte, lida pelas perguntas de quem conduz (143).

**Nada aqui decide; tudo aqui lê.** O estado do prazo é o da `019` (`selectors.estado_de`), o
estado documental é o da `115` (`documentos.leituras_por_chamada`), a ocupação é a da `016`, o aviso
de pendência e as tentativas de envio são da `066` e da `134`. Este módulo junta essas leituras na
forma das perguntas que a tela responde — quem convocar, quem foi, quem responde, quem tem documento
a conferir ou pendente, quem está pronto para o desfecho — e no passo de cada chamada.

**Ele não prioriza** (D-002 da `143`): a ordem do índice é fixa, e a prioridade continua sendo a do
andamento (`interface/andamento.py`), que aparece depois de um ato no bloco do próximo passo.

**O passo orienta, e não autoriza** (D-007): quem decide se o ato pode ser praticado é o comando.
O passo só escolhe qual ação rotineira aparece primeiro no cartão.

**"Pendência registrada" nunca é "candidato comunicado"** (FR-5018). A conferência pendente não
gera aviso — a `134` é por gesto, e nunca por evento —; o que o cartão diz do aviso vem do registro
do aviso e das tentativas de envio dele, e só disso.
"""

from dataclasses import dataclass

from django.utils import timezone

from processo_seletivo.classificacao.domain import faixa
from processo_seletivo.convocacao.domain import nomes

# --- O passo da chamada (data-model, FR-5011) ---------------------------------------------------

DESFECHADA = "DESFECHADA"
SEM_COMUNICACAO = "SEM_COMUNICACAO"
VENCIDA = "VENCIDA"
REENVIADO = "REENVIADO"
A_CONFERIR = "A_CONFERIR"
REFAZER_CONFERENCIA = "REFAZER_CONFERENCIA"
PENDENCIA = "PENDENCIA"
AGUARDANDO_DOCUMENTOS = "AGUARDANDO_DOCUMENTOS"
PRONTA = "PRONTA"
AGUARDANDO_RESPOSTA = "AGUARDANDO_RESPOSTA"

#: As ações rotineiras que um passo pode oferecer, e de quem cada uma é.
CONFERIR = "conferir"
DESFECHO = "desfecho"
EMITIR = "emitir"


@dataclass(frozen=True)
class Passo:
    codigo: str
    frase: str
    #: `acao` (há o que fazer), `espera` (é o candidato quem age), `alerta` (o prazo passou),
    #: `feito` (desfecho registrado). Vira classe na folha; a palavra da frase diz o mesmo, porque a
    #: cor sozinha não é informação (UX-371).
    tom: str
    acao: str = ""


def _n(quantos, singular, plural):
    return f"{quantos} {singular if quantos == 1 else plural}"


def _quando(instante):
    return timezone.localtime(instante).strftime("%d/%m/%Y %H:%M") if instante else ""


def passo_da_chamada(*, estado, desfecho, documentos, vencimento=None, canal=None):
    """O passo de uma convocação vigente, pela precedência do data-model (D-007).

    `documentos` é a `LeituraDocumental` da chamada, ou `None` quando ela não pede documento.
    **O vencimento vem antes dos documentos**: decorrido, nenhum desfecho nasce dele, e é o desfecho
    que a Administração deve registrar — a linha dos documentos continua dizendo o que há a
    conferir.
    """
    if desfecho is not None:
        return Passo(DESFECHADA, f"Desfecho registrado: {desfecho.get_especie_display()}.", "feito")
    if estado == nomes.CONVOCADO_PRAZO_NAO_INICIADO:
        # A palavra do canal (125, FR-4000): por publicação, quem age registra a publicação.
        emitir = canal.emitir if canal is not None else "Emitir a comunicação"
        return Passo(
            SEM_COMUNICACAO,
            f"{emitir}: o prazo desta convocação ainda não começou a correr.",
            "acao",
            EMITIR,
        )
    if estado == nomes.CONVOCADO_VENCIMENTO_DECORRIDO:
        if documentos is not None and not documentos.houve_apresentacao:
            # **Nada apresentado no prazo aponta o não atendimento** (152, FR-5809, UX-535, D-011).
            # Quem não respondeu à convocação não atendeu; o indeferimento pelas pendências é de
            # quem respondeu com falta. O código continua `VENCIDA`: a precedência dos passos da
            # `143` não muda, e o desfecho continua de quem registra — o geral oferece os outros.
            return Passo(
                VENCIDA,
                f"O prazo venceu em {_quando(vencimento)} sem nenhum documento apresentado. O "
                "desfecho que descreve isso é o não atendimento à convocação.",
                "alerta",
                DESFECHO,
            )
        return Passo(
            VENCIDA,
            "Registrar o desfecho: o vencimento decorreu, e nenhum desfecho nasce dele.",
            "alerta",
            DESFECHO,
        )
    if documentos is not None:
        contagens = documentos.contagens
        if documentos.estado == nomes.DOCUMENTOS_PARA_CONFERIR:
            if contagens["complementados"]:
                return Passo(
                    REENVIADO,
                    "Conferir de novo: o candidato reenviou "
                    + _n(
                        contagens["complementados"],
                        "documento que estava pendente",
                        "documentos que estavam pendentes",
                    )
                    + ".",
                    "acao",
                    CONFERIR,
                )
            return Passo(
                A_CONFERIR,
                "Conferir "
                + _n(contagens["recebidos"], "documento recebido", "documentos recebidos")
                + ".",
                "acao",
                CONFERIR,
            )
        if documentos.estado == nomes.DOCUMENTOS_COM_PENDENCIA:
            if not contagens["pendentes"]:
                # O "não se aplica" registrado sem condição publicada conta como pendência (131,
                # FR-4470), mas quem age é a conferência, e não o candidato.
                return Passo(
                    REFAZER_CONFERENCIA,
                    "Registrar outra conferência: um “não se aplica” foi registrado num "
                    "documento que o Edital exige de todos.",
                    "acao",
                    CONFERIR,
                )
            return Passo(
                PENDENCIA,
                "Aguardando o candidato corrigir "
                + _n(contagens["pendentes"], "documento pendente", "documentos pendentes")
                + ".",
                "espera",
            )
        if documentos.estado == nomes.DOCUMENTOS_AGUARDANDO:
            return Passo(
                AGUARDANDO_DOCUMENTOS,
                "Aguardando o candidato enviar "
                + _n(contagens["a_apresentar"], "documento", "documentos")
                + ".",
                "espera",
            )
        if documentos.estado == nomes.DOCUMENTOS_PRONTA:
            return Passo(
                PRONTA,
                "Pronta para o desfecho: os documentos obrigatórios estão conferidos.",
                "acao",
                DESFECHO,
            )
    if vencimento:
        frase = f"Aguardando a resposta do candidato, até {_quando(vencimento)}."
    else:
        frase = "Aguardando a resposta do candidato; o Edital não publica prazo."
    return Passo(AGUARDANDO_RESPOSTA, frase, "espera")


# --- O aviso da pendência (FR-5015 a FR-5018) ---------------------------------------------------


@dataclass(frozen=True)
class SituacaoDoAviso:
    """O que se sabe do aviso de pendência de uma chamada, lido dos registros.

    `alcancavel` é `None` quando a tela não sabe — quem não pode conferir não recebe a prévia do
    gesto, e a frase sobre o gesto não aparece para essa pessoa.
    """

    pendencia_em: object = None
    reenviado_em: object = None
    aviso_em: object = None
    estado: str = ""
    aceito_em: object = None
    alcancavel: bool | None = None
    motivo: str = ""
    habilitado: bool = True

    @property
    def frase_da_pendencia(self):
        if self.pendencia_em is not None:
            return f"Pendência registrada em {_quando(self.pendencia_em)}."
        if self.reenviado_em is not None:
            return (
                f"O candidato reenviou o documento pendente em {_quando(self.reenviado_em)}; "
                "a nova conferência está por fazer."
            )
        return ""

    @property
    def frase_do_aviso(self):
        """A situação do aviso desde a pendência — com as palavras da `066` (UX-172 dela).

        **Três grupos** (157, FR-6543, UX-649): *solicitado, aguardando envio* — pendente, em
        envio, ou em falha temporária, que o despacho tenta de novo sozinho —; *enviado*, que é
        aceito pelo servidor de correio, e nunca "entregue" nem "lido" (FR-5016 da `143`); e *não
        enviado*, com o estado que o explica. O cartão da convocação e a página dos documentos leem
        esta mesma frase.
        """
        from processo_seletivo.avisos.domain import nomes as avisos

        if self.pendencia_em is None:
            return ""
        if self.aviso_em is not None:
            if self.estado in (avisos.PENDENTE, avisos.EM_ENVIO, avisos.ESTADO_FALHA_TEMPORARIA):
                return f"Aviso solicitado em {_quando(self.aviso_em)}; aguardando envio."
            if self.estado == avisos.ESTADO_ACEITA:
                return (
                    f"Aviso enviado em {_quando(self.aceito_em or self.aviso_em)}: aceito pelo "
                    "servidor de correio."
                )
            return f"Aviso não enviado: {avisos.ROTULO_DO_ESTADO.get(self.estado, self.estado)}."
        frase = (
            "Nenhum aviso desde esta pendência: o candidato a vê no portal, e nenhum e-mail "
            "sobre ela foi pedido."
        )
        if not self.habilitado:
            return f"{frase} O envio de avisos está desabilitado nesta instalação."
        if self.alcancavel:
            return f"{frase} O aviso pode ser pedido agora."
        if self.motivo:
            return f"{frase} O aviso não a alcança agora: {self.motivo}."
        return frase

    @property
    def oferece_o_aviso(self):
        """O link para o gesto: só se ele a alcançaria **e** o envio está habilitado — com
        `AVISOS_AOS_CANDIDATOS` desligado, o padrão de produção, a seção diz que está desabilitado
        e não tem botão, e o cartão não pode mandar a pessoa até lá (revisão do #453)."""
        return bool(
            self.pendencia_em and self.aviso_em is None and self.alcancavel and self.habilitado
        )


def _pendencia_e_reenvio(documentos):
    """O instante da pendência mais recente e o do reenvio mais recente, dos itens que os têm."""
    pendencia = reenvio = None
    for lido in documentos.pedidos:
        if lido.estado == nomes.ITEM_PENDENTE and lido.conferencia is not None:
            instante = lido.conferencia.conferido_em
            pendencia = instante if pendencia is None else max(pendencia, instante)
        elif lido.estado == nomes.ITEM_COMPLEMENTADO and lido.vigente is not None:
            instante = lido.vigente.apresentado_em
            reenvio = instante if reenvio is None else max(reenvio, instante)
    return pendencia, reenvio


def avisos_por_raiz(convocacoes, *, agora):
    """`{id da raiz: (destinatário mais recente, estado, aceito_em)}` dos avisos de pendência.

    **Em consultas de número fixo, com as tentativas em `prefetch` e na ordem do número**
    (FR-5027): a tela não paga uma por linha, e o estado da `066` lê a última tentativa — sem
    `order_by`, a "última" seria a que o banco devolvesse por último. O destinatário pode ser de uma
    convocação que outra corrigiu depois: a raiz é a da regra da condução (`raizes_das`), a mesma
    que a prévia do gesto usa, e cai na chamada que o cartão mostra.
    """
    from django.conf import settings
    from django.db.models import Prefetch

    from processo_seletivo.avisos.application.selectors import tentativas_de
    from processo_seletivo.avisos.domain import estado as estado_do_aviso
    from processo_seletivo.avisos.domain import nomes as avisos
    from processo_seletivo.avisos.models import (
        DestinatarioDoAviso,
        InterrupcaoDoAviso,
        TentativaDeEnvio,
    )
    from processo_seletivo.convocacao.application import documentos as documentos_app

    por_id = {c.id: c for c in convocacoes}
    if not por_id:
        return {}
    destinatarios = (
        DestinatarioDoAviso.objects.filter(
            aviso__origem=avisos.PENDENCIA, convocacao_id__in=list(por_id)
        )
        .select_related("aviso", "aviso__interrupcao")
        .prefetch_related(
            Prefetch(
                "tentativas",
                queryset=TentativaDeEnvio.objects.select_related("resultado").order_by("numero"),
            )
        )
        .order_by("aviso__solicitado_em", "id")
    )
    if not destinatarios:
        return {}
    raizes = documentos_app.raizes_das(
        {d.convocacao_id: por_id[d.convocacao_id] for d in destinatarios}.values()
    )
    ultimos = {}
    for destinatario in destinatarios:
        ultimos[raizes[destinatario.convocacao_id].id] = destinatario
    resultado = {}
    for raiz, destinatario in ultimos.items():
        tentativas = tentativas_de(destinatario)
        try:
            interrompido = destinatario.aviso.interrupcao is not None
        except InterrupcaoDoAviso.DoesNotExist:
            interrompido = False
        estado = estado_do_aviso.estado_do_destinatario(
            elegibilidade=destinatario.elegibilidade,
            endereco=destinatario.endereco,
            tentativas=tentativas,
            interrompido=interrompido,
            solicitado_em=destinatario.aviso.solicitado_em,
            agora=agora,
            max_tentativas=settings.AVISOS_MAX_TENTATIVAS,
            janela_horas=settings.AVISOS_JANELA_DE_DESPACHO_HORAS,
        )
        aceito_em = tentativas[-1].registrado_em if estado == avisos.ESTADO_ACEITA else None
        resultado[raiz] = (destinatario, estado, aceito_em)
    return resultado


def situacao_do_aviso(documentos, *, aviso=None, motivo=None, habilitado=True):
    """A situação de uma chamada, ou `None` quando ela não tem pendência nem reenvio.

    `aviso` é o item de `avisos_por_raiz` desta chamada; `motivo` é o da prévia do gesto (`""`,
    alcançada; `None`, a tela não sabe). Aviso anterior à pendência mais recente não a cobre.
    """
    if documentos is None:
        return None
    pendencia, reenvio = _pendencia_e_reenvio(documentos)
    if pendencia is None and reenvio is None:
        return None
    aviso_em = estado = ""
    aceito_em = None
    if aviso is not None and pendencia is not None:
        destinatario, estado_lido, aceito = aviso
        if destinatario.aviso.solicitado_em >= pendencia:
            aviso_em, estado, aceito_em = destinatario.aviso.solicitado_em, estado_lido, aceito
    return SituacaoDoAviso(
        pendencia_em=pendencia,
        reenviado_em=reenvio,
        aviso_em=aviso_em or None,
        estado=estado,
        aceito_em=aceito_em,
        alcancavel=None if motivo is None else motivo == "",
        motivo=motivo or "",
        habilitado=habilitado,
    )


def anotar(linhas, *, convocacoes, raizes, previa_do_aviso, agora):
    """Acrescenta `passo` e `aviso` a cada linha que a view já montou (com `documentos`).

    `convocacoes` são todas as do recorte, sucedidas inclusive — as que a leitura do recorte já
    trouxe —: o aviso pedido para a convocação que outra corrigiu é da mesma chamada.
    `previa_do_aviso` é o que a prévia do gesto da `134` devolveu, ou `None` para quem não confere
    ou quando ninguém tem pendência.
    """
    from processo_seletivo.avisos.application.comando import envio_habilitado

    avisos = avisos_por_raiz(convocacoes, agora=agora)
    por_chamada = (previa_do_aviso or {}).get("por_chamada")
    habilitado = (
        previa_do_aviso.get("habilitado", True)
        if previa_do_aviso is not None
        else envio_habilitado()
    )
    for linha in linhas:
        raiz = raizes[linha["convocacao"].id]
        linha["passo"] = passo_da_chamada(
            estado=linha["estado"],
            desfecho=linha["desfecho"],
            documentos=linha.get("documentos"),
            vencimento=linha["convocacao"].vencimento,
            canal=linha.get("canal"),
        )
        linha["aviso"] = (
            situacao_do_aviso(
                linha.get("documentos"),
                aviso=avisos.get(raiz.id),
                motivo=None if por_chamada is None else por_chamada.get(str(raiz.id)),
                habilitado=habilitado,
            )
            if linha["desfecho"] is None
            else None
        )
    return linhas


# --- O índice "Neste recorte, agora" (FR-5001 a FR-5004) ----------------------------------------


@dataclass(frozen=True)
class Pergunta:
    chave: str
    quantas: object
    texto: str
    ancora: str = ""
    #: Se há o que fazer — e se é de quem está vendo, só para o estilo (D-002).
    trabalho: bool = False
    detalhe: str = ""
    detalhe_ancora: str = ""
    #: Se há ato a praticar **por alguém** no recorte, seja ou não de quem está vendo: é o que
    #: decide a frase "Nenhum ato a praticar" (FR-5004, revisão do #453).
    ato: bool = False


def _primeira(linhas, condicao):
    for linha in linhas:
        if condicao(linha):
            return f"convocacao-{linha['convocacao'].id}"
    return "chamadas"


def _estado_documental(linha):
    if linha["desfecho"] is not None or not linha.get("documentos"):
        return ""
    return linha["documentos"].estado


def indice(
    *,
    leitura,
    titulares,
    pode_convocar,
    pode_emitir,
    confere,
    sem_inscrito,
    marco_intermediario,
    secao_dos_pendentes,
    secao_dos_vencidos,
):
    """As perguntas do índice, na ordem fixa da FR-5001, com o número e o lugar do ato.

    `secao_dos_*` diz se a tela desenhou a seção — o link só vai para onde há o que ver. As
    linhas já vêm anotadas (`anotar`): a pendência e o aviso saem do cartão de cada uma.
    `titulares` é a prévia do gesto, lida para todos os que leem; `None` onde o marco não convoca.
    """
    linhas = leitura["linhas"]
    por_estado = leitura["porEstado"]
    perguntas = []
    if sem_inscrito:
        return perguntas
    if not marco_intermediario and titulares is not None:
        # **Para todos os que leem**, e não só para quem convoca: a auditoria e quem só confere
        # precisam saber que há titulares esperando, por outro papel (revisão do #453). **Com o
        # gesto impedido, não é trabalho nem tem âncora**: a prévia lista as pessoas mesmo com a
        # apuração obsoleta ou sem forma de comunicação, e a seção diz que não há gesto — o índice
        # diz o mesmo, com o impedimento.
        pessoas = len(titulares.get("pessoas") or [])
        impedimento = titulares.get("impedimento")
        if impedimento:
            perguntas.append(
                Pergunta(
                    "a_convocar",
                    0,
                    "titulares a convocar agora",
                    detalhe=f"o gesto está impedido: {impedimento['detalhe']}",
                )
            )
        else:
            perguntas.append(
                Pergunta(
                    "a_convocar",
                    pessoas,
                    ("titular a convocar" if pessoas == 1 else "titulares a convocar")
                    + ("" if pode_convocar or not pessoas else ", por quem conduz a convocação"),
                    "titulares" if pessoas and pode_convocar else "",
                    trabalho=bool(pessoas and pode_convocar),
                    ato=bool(pessoas),
                )
            )
        sem_chamada = vagas_sem_chamada(leitura)
        if not pessoas and not impedimento and sem_chamada:
            perguntas.append(_vaga_sem_chamada(leitura, sem_chamada, pode_convocar=pode_convocar))
    sem_comunicacao = por_estado.get(nomes.CONVOCADO_PRAZO_NAO_INICIADO, 0)
    if sem_comunicacao:
        perguntas.append(
            Pergunta(
                "sem_comunicacao",
                sem_comunicacao,
                leitura["canal"].pastilha_sem_comunicacao.lower() + " — o prazo não corre",
                "pendentes"
                if secao_dos_pendentes
                else _primeira(linhas, lambda x: x["estado"] == nomes.CONVOCADO_PRAZO_NAO_INICIADO),
                trabalho=pode_emitir,
                ato=True,
            )
        )
    perguntas.append(
        Pergunta(
            "convocadas",
            leitura["convocadas"],
            "pessoa convocada neste recorte"
            if leitura["convocadas"] == 1
            else "pessoas convocadas neste recorte",
            "chamadas" if leitura["convocadas"] else "",
        )
    )
    em_curso = [x for x in linhas if x["estado"] == nomes.CONVOCADO_PRAZO_EM_CURSO]
    vencimentos = [x["convocacao"].vencimento for x in em_curso if x["convocacao"].vencimento]
    perguntas.append(
        Pergunta(
            "aguardando",
            len(em_curso),
            "aguardando resposta, com o prazo em curso",
            "chamadas" if em_curso else "",
            detalhe=f"o primeiro vence em {_quando(min(vencimentos))}" if vencimentos else "",
        )
    )
    vencidas = por_estado.get(nomes.CONVOCADO_VENCIMENTO_DECORRIDO, 0)
    if vencidas:
        perguntas.append(
            Pergunta(
                "vencidas",
                vencidas,
                "com o vencimento decorrido e sem desfecho",
                "vencidos"
                if secao_dos_vencidos
                else _primeira(
                    linhas, lambda x: x["estado"] == nomes.CONVOCADO_VENCIMENTO_DECORRIDO
                ),
                trabalho=pode_emitir,
                ato=True,
            )
        )

    # **A pendência e o aviso falam do mesmo conjunto** (revisão do #453): a chamada com um
    # documento pendente, mesmo que outro esteja a conferir, é "com pendência" — é o conjunto que o
    # gesto da `134` seleciona —, e "pode ser avisada" é a parte dele que o cartão oferece ao gesto.
    def com_pendencia(linha):
        return linha["desfecho"] is None and bool(getattr(linha.get("aviso"), "pendencia_em", None))

    def avisavel(linha):
        return com_pendencia(linha) and linha["aviso"].oferece_o_aviso

    for chave, condicao, texto, de_quem in (
        (
            "a_conferir",
            lambda x: _estado_documental(x) == nomes.DOCUMENTOS_PARA_CONFERIR,
            "com documento a conferir",
            confere,
        ),
        ("pendencia", com_pendencia, "com pendência, aguardando o candidato", False),
        (
            "aguardando_documentos",
            lambda x: _estado_documental(x) == nomes.DOCUMENTOS_AGUARDANDO,
            "aguardando o envio dos documentos",
            False,
        ),
        (
            "prontas",
            lambda x: _estado_documental(x) == nomes.DOCUMENTOS_PRONTA,
            "prontas para o desfecho",
            pode_emitir,
        ),
    ):
        quantas = sum(1 for x in linhas if condicao(x))
        if chave in ("a_conferir", "pendencia", "prontas") or quantas:
            detalhe = detalhe_ancora = ""
            ato = bool(quantas) and chave != "pendencia"
            if chave == "pendencia":
                avisaveis = sum(1 for x in linhas if avisavel(x))
                if avisaveis:
                    detalhe = _n(avisaveis, "pode ser avisada agora", "podem ser avisadas agora")
                    detalhe_ancora = "avisar-pendencias"
                    de_quem = confere
                    ato = True
            perguntas.append(
                Pergunta(
                    chave,
                    quantas,
                    texto,
                    _primeira(linhas, condicao) if quantas else "",
                    trabalho=bool(ato and de_quem),
                    detalhe=detalhe,
                    detalhe_ancora=detalhe_ancora,
                    ato=ato,
                )
            )
    desfechadas = por_estado.get(nomes.DESFECHADO, 0)
    aptas = sum(1 for x in linhas if x.get("apto"))
    perguntas.append(
        Pergunta(
            "com_desfecho",
            desfechadas,
            "com desfecho registrado",
            "chamadas" if desfechadas else "",
            detalhe=_n(aptas, "apta para formalização", "aptas para formalização") if aptas else "",
        )
    )
    return perguntas


def chamadas_que_nao_ocupam(linhas):
    """Quantas chamadas sem desfecho ainda não ocupam vaga (133, FR-4547, CV-03).

    O titular conta como ocupado desde a apuração; a chamada para a vaga que vagou, ou para
    regularizar, ainda não ocupa — ela responde pela vaga, e chamar outra pessoa a dobraria. **É a
    mesma conta do Centro do Edital** (`andamento.py`), e mora aqui para que as duas telas não
    divirjam: divergiam, e a convocação dizia "Nenhum ato a praticar" com o Centro mandando chamar a
    próxima da fila (achado 03 do estudo de 11/11/2026).
    """
    return sum(
        1
        for linha in linhas
        if linha["desfecho"] is None
        and getattr(linha.get("convocacao"), "especie", None) != nomes.VAGA_INICIAL
    )


def vagas_sem_chamada(leitura):
    """As vagas que a apuração vigente dá como faltando e que nenhuma chamada em aberto cobre."""
    faltando = (leitura.get("ocupacao") or {}).get("faltando") or 0
    return max(faltando - chamadas_que_nao_ocupam(leitura["linhas"]), 0)


def _vaga_sem_chamada(leitura, quantas, *, pode_convocar):
    """A vaga reaberta — por desistência, não atendimento, indeferimento — e quem a ocupa a seguir.

    **Com alguém na fila, é ato**: a chamada individual, na seção da fila. **Sem ninguém, não é**:
    a tela já diz, na seção da fila, se ampliar a faixa é possível; o índice só conta a vaga, para
    que a frase "Nenhum ato a praticar" não a esconda.
    """
    texto = (
        "vaga a ocupar sem chamada em aberto"
        if quantas == 1
        else "vagas a ocupar sem chamada em aberto"
    )
    fila = leitura.get("fila") or []
    if not fila:
        return Pergunta(
            "vaga_sem_chamada",
            quantas,
            texto,
            detalhe="não há mais quem chamar na fila" + _situacao_da_vaga(leitura),
        )
    proxima = fila[0]
    detalhe = f"a próxima da fila é {proxima['protocolo']} — {proxima['nome']}"
    if not pode_convocar:
        detalhe += ", por quem conduz a convocação"
    return Pergunta(
        "vaga_sem_chamada",
        quantas,
        texto,
        "fila",
        trabalho=pode_convocar,
        detalhe=detalhe,
        ato=True,
    )


def _situacao_da_vaga(leitura):
    """Com a fila vazia, a situação da vaga, na frase do Centro e da ocupação (155, R-008).

    **A mesma conta das três telas** (155, D-004): o índice só a cita, e o ato mora na ocupação.
    Vazia onde a situação não diz nada novo. Onde o Edital declara a reversão, a frase diz por que
    a vaga ainda não saiu, sem ato: a reversão é da apuração.
    """
    from processo_seletivo.interface import destinacao_da_vaga

    apuracao = (leitura.get("ocupacao") or {}).get("apuracao")
    if apuracao is None:
        return ""
    vaga = destinacao_da_vaga.situacao_do_recorte(
        edital=apuracao.edital,
        perfil_id=apuracao.perfil_id,
        marco_id=apuracao.marco_id,
        lista_id=apuracao.lista_id,
        rotulo=destinacao_da_vaga.rotulo_do_recorte(
            apuracao.versao.content, apuracao.perfil_id, apuracao.lista_id
        ),
    )
    if vaga is None:
        return ""
    if vaga["disponivel"]:
        return f"; {vaga['frase']} A declaração de vaga não preenchida é ato da ocupação"
    if vaga.get("reversao"):
        return f"; {vaga['frase']}"
    if vaga["impedimentos"]:
        motivos = "; ".join(i["frase"] for i in vaga["impedimentos"])
        return f"; a declaração de vaga não preenchida ainda não cabe: {motivos}"
    return ""


def sem_providencia(perguntas):
    """Se nenhuma pergunta tem ato a praticar **por ninguém** no recorte (FR-5004): só então a
    frase "Nenhum ato a praticar" aparece. O ato de outro papel conta — a auditoria lia a frase
    com três titulares esperando —, e o aviso alcançável com o envio habilitado também."""
    return not any(p.ato for p in perguntas)


# --- O contexto do recorte (FR-5000, FR-5019) ---------------------------------------------------


def contexto_do_recorte(edital, marco_id, lista_id):
    """`{edital, perfil, marco, lista}` pela versão vigente — uma leitura dela."""
    from processo_seletivo.interface import conducao_do_marco

    conteudo, perfil, marco = conducao_do_marco.marco_publicado(edital, marco_id)
    lista = ""
    if perfil is not None:
        alvo = str(lista_id) if lista_id else None
        lista = next(
            (
                rotulo
                for identificador, rotulo in conducao_do_marco.recortes_do_marco(conteudo, perfil)
                if (str(identificador) if identificador else None) == alvo
            ),
            "",
        )
    return {
        "edital": f"Edital {edital.number}/{edital.year}",
        "perfil": (perfil or {}).get("name") or "",
        "marco": (marco or {}).get("name") or "",
        "lista": lista,
        # Se ampliar a faixa é possível (014, D-011): a tela só manda pedir a faixa seguinte onde o
        # Edital a publicou (achado 02 do estudo de 11/11/2026). Da mesma leitura, sem consulta.
        "continuacao_admitida": faixa.admite_continuacao((marco or {}).get("cutRule")),
    }


# --- As pessoas do recorte, na página dos documentos (FR-5024) ------------------------------------


def pessoas_do_recorte(*, edital, vigente):
    """A chamada entre as outras do recorte: a anterior, a seguinte e a próxima com documento a
    conferir, na ordem da tela da convocação (`leitura_do_recorte`: chamada, e o protocolo
    desempata).

    **Em consultas de número fixo**, para o recorte inteiro: as convocações com desfechos e
    sucessoras em `prefetch`, as identidades, e a leitura documental de todas as chamadas. Devolve
    também o que a prévia do aviso e a situação dele precisam, para não lerem o recorte de novo.
    """
    from processo_seletivo.convocacao.application import documentos as documentos_app
    from processo_seletivo.convocacao.application.selectors import (
        convocacoes_do_recorte,
        desfecho_de,
        identidades_de,
        vigentes,
    )

    todas = convocacoes_do_recorte(
        edital=edital,
        perfil_id=vigente.perfil_id,
        marco_id=vigente.marco_id,
        lista_id=vigente.lista_id,
    )
    em_vigor = vigentes(todas)
    identidades = identidades_de({c.inscricao_id for c in em_vigor})
    em_vigor.sort(key=lambda c: (c.criado_em, identidades[c.inscricao_id]["protocolo"]))
    raizes = documentos_app.raizes_das(em_vigor)
    decididas = {raizes[c.id].id for c in em_vigor if desfecho_de(c) is not None}
    leituras = documentos_app.leituras_por_chamada(set(raizes.values()), decididas=decididas)
    posicao = next((i for i, c in enumerate(em_vigor) if c.id == vigente.id), None)

    def pessoa(convocacao):
        if convocacao is None:
            return None
        return {"convocacao": convocacao, **identidades[convocacao.inscricao_id]}

    anterior = seguinte = proxima = None
    if posicao is not None:
        anterior = em_vigor[posicao - 1] if posicao > 0 else None
        seguinte = em_vigor[posicao + 1] if posicao + 1 < len(em_vigor) else None
        # A próxima a conferir **depois** desta, e depois as de antes: quem confere segue adiante.
        for convocacao in em_vigor[posicao + 1 :] + em_vigor[:posicao]:
            leitura = leituras.get(raizes[convocacao.id].id)
            if (
                leitura is not None
                and leitura.pedidos
                and leitura.estado == nomes.DOCUMENTOS_PARA_CONFERIR
            ):
                proxima = convocacao
                break
    from processo_seletivo.convocacao.application.selectors import (
        _forma_do_recorte,
        comunicacao_da_linha,
    )

    return {
        # As frases do canal desta chamada, como no cartão dela (125, FR-4000).
        "comunicacao": comunicacao_da_linha(vigente, _forma_do_recorte(em_vigor)),
        "anterior": pessoa(anterior),
        "seguinte": pessoa(seguinte),
        "proxima_a_conferir": pessoa(proxima),
        "posicao": None if posicao is None else posicao + 1,
        "total": len(em_vigor),
        "identidades": identidades,
        "convocacoes": todas,
        "raizes": raizes,
        "leituras": leituras,
    }
