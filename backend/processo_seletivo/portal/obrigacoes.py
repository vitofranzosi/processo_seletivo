"""As obrigações da convocação: o que falta, o que está com a comissão e o conferido (118).

**Por que existe.** A `115` ensinou o portal a pedir documentos na convocação, e o resto do portal
não ficou sabendo: com o Requerimento de Matrícula enviado, o acompanhamento dizia *"Seu
Requerimento de Matrícula foi enviado."*, com o botão verde, enquanto quatro documentos
obrigatórios estavam em *"Falta enviar"* (F1 da revisão de 04/11/2026). A ação principal conhecia
três possibilidades, e nenhuma era documento. Esta projeção é o conjunto, e as duas telas leem a
mesma (FR-3721).

**Uma função pura, no molde de `portal/situacao.py`** (D-007). Ela recebe o que as views já leram —
a leitura documental da chamada, a política do Requerimento, o estado do prazo, a causa do
fechamento e o desfecho — e não lê relógio, não consulta o banco e não grava nada. A causa do
fechamento chega derivada da mesma condição que recusa o envio (FR-3578, FR-3582 da `115`): uma
segunda conta do mesmo prazo discordaria na fronteira.

**Ela não decide nada** (FR-3729). Não infere desfecho, perda de vaga, nova chamada nem prazo novo.
O fim do prazo e o estado final do Processo só fecham a escrita, e a categoria de cada item não
muda com o momento: muda o texto, e se há convite.

**As frases moram aqui** (FR-3746 a FR-3749), e o template não escreve nenhuma frase de estado. É
aqui que as varreduras de vocabulário as leem (FR-3751). Três termos não aparecem, de propósito: o
termo da gestão para o aceite, que para o candidato seria jargão e soaria como promessa (D-014);
"encaminhado", que nenhum registro de entrega sustenta; e o vínculo efetivado, que é fato do setor
competente, e não do GPS.
"""

from dataclasses import dataclass, field, replace
from types import SimpleNamespace

from django.utils import formats, timezone

from processo_seletivo.convocacao.application.documentos import NUCLEO_DO_PRAZO_DECORRIDO
from processo_seletivo.convocacao.application.documentos import (
    frase_do_prazo_decorrido as _frase_do_prazo_decorrido,
)
from processo_seletivo.convocacao.domain import documentos as dominio
from processo_seletivo.convocacao.domain import nomes as convocacao_nomes
from processo_seletivo.requerimentos.domain import nomes as requerimento_nomes

# --- O momento da chamada (FR-3722) -------------------------------------------------------------
ABERTA = "ABERTA"
ENCERRADA_PELO_PRAZO = "ENCERRADA_PELO_PRAZO"
ENCERRADA_PELO_PROCESSO = "ENCERRADA_PELO_PROCESSO"
DECIDIDA = "DECIDIDA"

# --- A causa do fechamento da escrita (FR-3721, D-015) ------------------------------------------
PRAZO = "PRAZO"
PROCESSO = "PROCESSO"

# --- A categoria de cada item, exatamente uma (FR-3722) -----------------------------------------
A_CORRIGIR = "A_CORRIGIR"
A_ENVIAR = "A_ENVIAR"
COM_A_COMISSAO = "COM_A_COMISSAO"
CONFERIDO = "CONFERIDO"
OPCIONAL = "OPCIONAL"
TAREFAS = (A_CORRIGIR, A_ENVIAR)

# --- O Requerimento de Matrícula na projeção (FR-3725) ------------------------------------------
REQ_NAO_PEDIDO = "NAO_PEDIDO"
REQ_ENVIADO = "ENVIADO"
REQ_NAO_ENVIADO = "NAO_ENVIADO"
REQ_NAO_ENVIADO_ENCERRADO = "NAO_ENVIADO_ENCERRADO"
REQ_NAO_ENVIADO_ATE_O_PRAZO = "NAO_ENVIADO_ATE_O_PRAZO"
REQ_A_PREENCHER = "A_PREENCHER"
REQ_SEM_CHAMADO = "SEM_CHAMADO"
REQ_NAO_ENVIADOS = (REQ_NAO_ENVIADO, REQ_NAO_ENVIADO_ENCERRADO, REQ_NAO_ENVIADO_ATE_O_PRAZO)

# --- As frases ----------------------------------------------------------------------------------
NADA_POR_ENQUANTO = "Nada por enquanto."
# **Não diz que a pessoa enviou tudo** (D-005). O documento aproveitado da inscrição não foi
# reenviado, e "você enviou tudo" apagaria a diferença; "está tudo certo" diria o que a comissão
# ainda não disse.
FRASE_DE_CONCLUSAO = (
    "Você não tem mais documentos para enviar agora. A comissão ainda vai concluir a análise."
)
PRAZO_NAO_INICIADO = (
    "O prazo ainda não começou a correr: ele conta a partir do envio da comunicação."
)
JA_PODE_ENVIAR = "Você já pode enviar."
SEM_PRAZO_REGISTRADO = "Esta convocação não tem prazo registrado."
CONVITE_AO_OPCIONAL = "Há documento opcional que você pode enviar, se quiser."
# **O núcleo mora com as recusas** (FR-3748): os comandos de envio o usam, e a tela não pode dizer
# outra coisa.
NUCLEO_DO_PRAZO = NUCLEO_DO_PRAZO_DECORRIDO
ACEITE = (
    "Este registro não é matrícula, bolsa nem contrato: ele registra o resultado desta convocação. "
    "Os próximos passos são os que o Edital indica."
)
REQUERIMENTO = "Requerimento de Matrícula"
REQUERIMENTO_ENVIADO = "✓ Requerimento de Matrícula enviado."
REQUERIMENTO_NAO_ENVIADO = "Requerimento de Matrícula: não enviado."
REQUERIMENTO_NAO_ENVIADO_ATE_O_PRAZO = (
    "Requerimento de Matrícula: não enviado até o prazo. Não é mais possível enviá-lo pelo portal."
)
REQUERIMENTO_NAO_ENVIADO_ENCERRADO = (
    "Requerimento de Matrícula: não enviado. O envio pelo portal está encerrado."
)
LINHA_DO_REQUERIMENTO = {
    REQ_NAO_ENVIADO: REQUERIMENTO_NAO_ENVIADO,
    REQ_NAO_ENVIADO_ATE_O_PRAZO: REQUERIMENTO_NAO_ENVIADO_ATE_O_PRAZO,
    REQ_NAO_ENVIADO_ENCERRADO: REQUERIMENTO_NAO_ENVIADO_ENCERRADO,
}


# Os selos dos cartões (FR-3744): o estado em texto, nunca só em cor ou símbolo. Fechada a chamada,
# o pendente se diz no passado e o que estava com a comissão não promete conferência.
class Selo(str):
    """O selo é a palavra; o `tipo` só escolhe a regra da folha, que acompanha a palavra."""

    def __new__(cls, texto, tipo):
        selo = super().__new__(cls, texto)
        selo.tipo = tipo
        return selo


SELO_PRECISA_DE_CORRECAO = Selo("Precisa de correção", "correcao")
SELO_PRECISAVA_DE_CORRECAO = Selo("Precisava de correção", "correcao")
SELO_AGUARDANDO = Selo("Aguardando conferência", "comissao")
SELO_NAO_CONFERIDO = Selo("Não conferido", "comissao")
SELO_CONFERIDO = Selo("Conferido", "conferido")
SELO_OPCIONAL = Selo("Opcional", "opcional")

ENCERRADO_OU_CANCELADO = {"ENCERRADO": "encerrado", "CANCELADO": "cancelado"}

HORA = "H\\hi"


def data(instante):
    return formats.date_format(timezone.localtime(instante), "d/m/Y")


def hora(instante):
    return formats.date_format(timezone.localtime(instante), HORA)


def data_e_hora(instante):
    """*"09/11/2026, às 13h27"* — o formato único do prazo e dos recebimentos (FR-3747)."""
    return f"{data(instante)}, às {hora(instante)}"


def ate(vencimento):
    """*"até 09/11/2026, às 13h27"* (FR-3747), ou vazio sem vencimento."""
    return f"até {data_e_hora(vencimento)}" if vencimento is not None else ""


def frase_do_prazo_decorrido(vencimento):
    """O núcleo único do vencido (FR-3748) — a mesma frase das recusas de envio por prazo."""
    return _frase_do_prazo_decorrido(SimpleNamespace(vencimento=vencimento))


def frase_do_atendimento(canal):
    canal = (canal or "").strip()
    sufixo = f": {canal}" if canal else ""
    return f"Se você enviou algo que não aparece aqui, fale com o atendimento{sufixo}."


def juntar(nomes):
    """*"A, B e C"*."""
    nomes = list(nomes)
    if len(nomes) <= 1:
        return "".join(nomes)
    return ", ".join(nomes[:-1]) + " e " + nomes[-1]


def documentos(n):
    return f"{n} documento" if n == 1 else f"{n} documentos"


# --- O Requerimento -----------------------------------------------------------------------------


def estado_do_requerimento(disponibilidade, *, desfecho, causa=None):
    """O estado do Requerimento na projeção, pela primeira linha da FR-3725 que se aplicar.

    **A exigência e a situação vêm antes da disponibilidade** (D-016). A política da `029` responde
    se é possível escrever *agora*: depois do desfecho ela diz "ainda indisponível" a quem nunca
    enviou, e ler essa resposta como "não pedido" apagaria uma obrigação que existiu.

    **O Processo antes do prazo** (linha 3a, D-015, D-020): com os dois juntos, vale o Processo,
    como nos documentos. A linha 3a só alcança o Requerimento *na convocação*; o *na inscrição* não
    mudou.

    `disponibilidade` é a `Disponibilidade` que `preencher_requerimento.apurar` já devolve, ou
    `None` sem convocação.
    """
    d = disponibilidade
    if d is None or not d.exigido:
        return REQ_NAO_PEDIDO
    if d.enviado:
        return REQ_ENVIADO
    if desfecho is not None:
        return REQ_NAO_ENVIADO
    na_convocacao = d.momento == requerimento_nomes.NA_CONVOCACAO
    if na_convocacao and (d.fechado_pelo_processo or causa == PROCESSO):
        return REQ_NAO_ENVIADO_ENCERRADO
    if d.prazo_decorrido:
        return REQ_NAO_ENVIADO_ATE_O_PRAZO
    if d.estado_de_leitura in (requerimento_nomes.DISPONIVEL, requerimento_nomes.EM_PREENCHIMENTO):
        return REQ_A_PREENCHER
    # A proteção contra um chamado que o comando recusaria (FR-1098 da `059`).
    return REQ_SEM_CHAMADO


def linha_informativa_do_requerimento(disponibilidade, *, desfecho):
    """A exceção estritamente informativa da chamada sem documento (FR-3732, D-019).

    Só com o Requerimento declarado *na convocação* e não enviado, e só quando a política já não
    admite o preenchimento: com a chamada aberta, B e B2 ficam exatamente como hoje. Sem link e sem
    botão, e sem consulta nova — sai da mesma `Disponibilidade` que o chamado já lê.
    """
    d = disponibilidade
    if d is None or d.momento != requerimento_nomes.NA_CONVOCACAO:
        return ""
    return LINHA_DO_REQUERIMENTO.get(estado_do_requerimento(d, desfecho=desfecho), "")


# --- Os itens -----------------------------------------------------------------------------------


def categoria(obrigatorio, estado, *, apresentado):
    """A categoria de um item, primeiro pela situação e depois pelo estado (FR-3722, D-018)."""
    if estado in (convocacao_nomes.ITEM_CONFORME, convocacao_nomes.ITEM_NAO_SE_APLICA):
        return CONFERIDO
    if estado in (convocacao_nomes.ITEM_RECEBIDO, convocacao_nomes.ITEM_COMPLEMENTADO):
        return COM_A_COMISSAO
    if not obrigatorio:
        return OPCIONAL
    if estado == convocacao_nomes.ITEM_PENDENTE and apresentado:
        return A_CORRIGIR
    return A_ENVIAR


@dataclass(frozen=True)
class Item:
    """Um item pedido, com a categoria, o texto pronto e o que o cartão oferece."""

    lido: object
    categoria: str
    opcional: bool
    # A pendência registrada pela comissão: *a corrigir*, ou *a enviar* com motivo (cenário J).
    com_motivo: bool
    motivo: str
    texto: str
    selos: tuple
    destaque: bool
    pode_enviar: bool
    envio_recolhido: bool

    @property
    def id(self):
        return self.lido.item.id

    @property
    def ancora(self):
        return f"item-{self.lido.item.id}"

    @property
    def nome(self):
        return self.lido.nome

    @property
    def tarefa(self):
        return self.categoria in TAREFAS


def _origem(lido):
    """De onde veio a apresentação vigente — `portal`, `inscricao` ou `chamada` — e quando."""
    aproveitada = lido.aproveitada
    if aproveitada is not None:
        return aproveitada["de"], aproveitada["em"]
    vigente = lido.vigente
    return "portal", (vigente.apresentado_em if vigente is not None else None)


def texto_do_item(lido, categoria_do_item, momento, prazo):
    """A célula da FR-3746 para o item, no momento da chamada.

    `prazo` é *"até ‹data›, às ‹hora›"*, ou vazio com o prazo não iniciado ou sem vencimento: nesses
    dois casos, *"até ‹prazo›"* sai de toda frase da coluna *aberta* (FR-3749).
    """
    estado = lido.estado
    motivo = (getattr(lido.conferencia, "motivo", "") or "").strip().rstrip(".")
    apresentado = lido.vigente is not None
    origem, em = _origem(lido)
    aberta = momento == ABERTA
    ate_o_prazo = f" {prazo}" if prazo else ""

    if estado == convocacao_nomes.ITEM_NAO_SE_APLICA:
        return f"Não se aplica: {motivo}." if motivo else "Não se aplica."
    if estado == convocacao_nomes.ITEM_CONFORME:
        if origem == "inscricao":
            return (
                "Conferido: de acordo com o Edital. É o arquivo enviado na inscrição, "
                f"em {data(em)}."
            )
        if origem == "chamada":
            return (
                "Conferido: de acordo com o Edital. É o arquivo enviado na chamada anterior, "
                f"em {data(em)}."
            )
        return "Conferido: de acordo com o Edital."

    if not lido.obrigatorio and estado in (
        convocacao_nomes.ITEM_A_APRESENTAR,
        convocacao_nomes.ITEM_PENDENTE,
    ):
        if estado == convocacao_nomes.ITEM_A_APRESENTAR:
            return "Opcional: envie se quiser." if aberta else "Opcional, não enviado."
        apontou = f"Opcional. A comissão apontou: {motivo}."
        if not aberta:
            return apontou
        arquivo = "um novo arquivo" if apresentado else "o arquivo"
        return f"{apontou} Se quiser, envie {arquivo}{ate_o_prazo}."

    if estado == convocacao_nomes.ITEM_A_APRESENTAR:
        return {
            ABERTA: "Falta enviar.",
            ENCERRADA_PELO_PRAZO: "Não enviado até o prazo.",
        }.get(momento, "Não enviado.")

    if estado == convocacao_nomes.ITEM_PENDENTE:
        if aberta:
            arquivo = "um novo arquivo" if apresentado else "o arquivo"
            return f"Precisa de correção: {motivo}. Envie {arquivo}{ate_o_prazo}."
        if momento == ENCERRADA_PELO_PRAZO:
            nenhum = "Nenhum novo arquivo" if apresentado else "Nenhum arquivo"
            return f"Precisava de correção: {motivo}. {nenhum} foi enviado até o prazo."
        return f"Precisava de correção: {motivo}."

    if estado == convocacao_nomes.ITEM_COMPLEMENTADO:
        if momento == ENCERRADA_PELO_PROCESSO:
            return (
                f"Novo arquivo recebido em {data(em)}; não foi conferido antes do encerramento "
                "do Processo."
            )
        if momento == DECIDIDA:
            return f"Novo arquivo enviado em {data(em)}; não foi conferido antes do resultado."
        return (
            f"Novo arquivo recebido em {data_e_hora(em)}, depois da correção pedida. "
            "A comissão vai conferir."
        )

    # Recebido: pelo portal, ou aproveitado da inscrição ou da chamada anterior.
    if origem == "inscricao":
        return {
            ABERTA: f"Você já enviou este documento na inscrição, em {data(em)}. Não precisa "
            "enviar de novo. A comissão vai conferir.",
            ENCERRADA_PELO_PRAZO: f"Enviado na inscrição, em {data(em)}. A comissão vai conferir.",
            ENCERRADA_PELO_PROCESSO: f"Enviado na inscrição, em {data(em)}; não foi conferido "
            "antes do encerramento do Processo.",
            DECIDIDA: f"Enviado na inscrição, em {data(em)}; não foi conferido antes do resultado.",
        }[momento]
    if origem == "chamada":
        anterior = f"Aproveitado da chamada anterior, enviado em {data(em)}"
        return {
            ABERTA: f"{anterior}. Não precisa enviar de novo. A comissão vai conferir de novo.",
            ENCERRADA_PELO_PRAZO: f"{anterior}. A comissão vai conferir de novo.",
            ENCERRADA_PELO_PROCESSO: f"{anterior}; não foi conferido antes do encerramento do "
            "Processo.",
            DECIDIDA: f"{anterior}; não foi conferido antes do resultado.",
        }[momento]
    return {
        ABERTA: f"Recebido em {data_e_hora(em)}. A comissão vai conferir; você não precisa fazer "
        "nada agora.",
        ENCERRADA_PELO_PRAZO: f"Recebido em {data_e_hora(em)}. A comissão vai conferir.",
        ENCERRADA_PELO_PROCESSO: f"Recebido em {data_e_hora(em)}; não foi conferido antes do "
        "encerramento do Processo.",
        DECIDIDA: f"Enviado em {data(em)}; não foi conferido antes do resultado.",
    }[momento]


def _selos(categoria_do_item, opcional, com_motivo, momento):
    aberta_ou_prazo = momento in (ABERTA, ENCERRADA_PELO_PRAZO)
    selos = []
    if com_motivo:
        selos.append(SELO_PRECISA_DE_CORRECAO if momento == ABERTA else SELO_PRECISAVA_DE_CORRECAO)
    elif categoria_do_item == COM_A_COMISSAO:
        # Encerrado o Processo ou registrado o resultado, ninguém mais confere: "aguardando"
        # prometeria uma conferência que o sistema recusa (FR-3724, FR-3742).
        selos.append(SELO_AGUARDANDO if aberta_ou_prazo else SELO_NAO_CONFERIDO)
    elif categoria_do_item == CONFERIDO:
        selos.append(SELO_CONFERIDO)
    if opcional:
        selos.append(SELO_OPCIONAL)
    return tuple(selos)


def _item(lido, momento, prazo):
    apresentado = lido.vigente is not None
    categoria_do_item = categoria(lido.obrigatorio, lido.estado, apresentado=apresentado)
    pendente = lido.estado == convocacao_nomes.ITEM_PENDENTE
    motivo = (getattr(lido.conferencia, "motivo", "") or "").strip() if pendente else ""
    aberta = momento == ABERTA
    # O envio é o da `115`: aberto para o que falta, o pendente e o que está com a comissão, e
    # recusado pelo comando no que já foi conferido (`ATENDIDOS`).
    pode_enviar = aberta and lido.estado not in dominio.ATENDIDOS
    return Item(
        lido=lido,
        categoria=categoria_do_item,
        opcional=not lido.obrigatorio,
        com_motivo=pendente,
        motivo=motivo,
        texto=texto_do_item(lido, categoria_do_item, momento, prazo),
        selos=_selos(categoria_do_item, not lido.obrigatorio, pendente, momento),
        destaque=pendente,
        pode_enviar=pode_enviar,
        # Com arquivo já recebido, o envio de outro fica recolhido — aberto quando a comissão pediu
        # a correção, que é justamente o que se espera da pessoa.
        envio_recolhido=pode_enviar and apresentado,
    )


# --- A projeção ---------------------------------------------------------------------------------


@dataclass(frozen=True)
class Tarefa:
    """Uma linha do bloco *O que fazer agora*: o documento e a âncora, ou o Requerimento."""

    texto: str
    ancora: str = ""
    motivo: str = ""
    requerimento: bool = False


@dataclass(frozen=True)
class Obrigacoes:
    momento: str
    causa: str
    itens: tuple
    tarefas: tuple
    requerimento: str
    totais: dict
    vencimento: object
    prazo_nao_iniciado: bool
    # *"até ‹data›, às ‹hora›"*, ou vazio sem prazo correndo (FR-3747, FR-3749).
    prazo: str
    frase_de_estado: str
    frase_de_conclusao: str = ""
    frase_do_opcional: str = ""
    frase_do_prazo: tuple = field(default_factory=tuple)
    titulo_do_fechamento: str = ""
    frase_do_fechamento: tuple = field(default_factory=tuple)
    titulo_do_resumo: str = ""
    resumo: tuple = field(default_factory=tuple)
    linha_do_requerimento: str = ""

    @property
    def aberta(self):
        return self.momento == ABERTA

    @property
    def encerrada(self):
        return self.momento in (ENCERRADA_PELO_PRAZO, ENCERRADA_PELO_PROCESSO)

    @property
    def decidida(self):
        return self.momento == DECIDIDA

    @property
    def tarefas_de_documento(self):
        return tuple(item for item in self._ordenados() if item.tarefa)

    @property
    def opcionais_a_enviar(self):
        return tuple(item for item in self.itens if item.categoria == OPCIONAL)

    @property
    def que_falta(self):
        """O bloco 3: as tarefas na ordem da FR-3726; os opcionais vêm à parte (FR-3738)."""
        return self.tarefas_de_documento

    @property
    def ja_apresentados(self):
        """O bloco 4: com a comissão, depois os conferidos, cada grupo na ordem do Edital."""
        return tuple(i for i in self.itens if i.categoria == COM_A_COMISSAO) + tuple(
            i for i in self.itens if i.categoria == CONFERIDO
        )

    @property
    def tem_bloco_que_falta(self):
        return bool(self.que_falta or self.opcionais_a_enviar)

    @property
    def primeira_ancora(self):
        tarefas = self.tarefas_de_documento
        return tarefas[0].ancora if tarefas else ""

    @property
    def rotulo_do_botao(self):
        """O botão ao primeiro cartão: diz o que se vê ao chegar, e não "Enviar" (D-004)."""
        if not self.tarefas_de_documento:
            return ""
        if self.totais["a_corrigir"]:
            return "Ver e corrigir os documentos pendentes"
        return "Ver os documentos que faltam"

    @property
    def linha_com_a_comissao(self):
        """*"Com a comissão: N documentos."*, sem verbo de tarefa (FR-3736)."""
        total = self.totais["com_a_comissao"]
        return f"Com a comissão: {documentos(total)}." if total else ""

    @property
    def convite_ao_opcional(self):
        """Sem tarefa e com opcional a enviar, a linha que leva ao bloco dos opcionais (FR-3736)."""
        return (
            CONVITE_AO_OPCIONAL
            if self.aberta and not self.tarefas and self.opcionais_a_enviar
            else ""
        )

    @property
    def requerimento_enviado(self):
        return self.requerimento == REQ_ENVIADO

    @property
    def requerimento_a_preencher(self):
        return self.requerimento == REQ_A_PREENCHER

    def _ordenados(self):
        """A ordem do candidato (FR-3726): a pendência registrada, depois o que falta enviar.

        A precedência da FR-3591 da `115`, que põe *para conferir* antes de *com pendência*, serve
        a quem confere, e não é usada aqui.
        """
        com_pendencia = [i for i in self.itens if i.tarefa and i.com_motivo]
        sem_pendencia = [i for i in self.itens if i.tarefa and not i.com_motivo]
        return com_pendencia + sem_pendencia


def obrigacoes_da_convocacao(
    *,
    leitura,
    requerimento,
    estado_do_prazo,
    causa_do_fechamento,
    desfecho,
    vencimento,
    estado_final_do_processo="",
    canal="",
):
    """As obrigações da chamada vigente, ou `None` quando ela não pede documento (FR-3743).

    `causa_do_fechamento` é `None`, `PRAZO` ou `PROCESSO`, derivada pela view da mesma condição que
    recusa o envio; com as duas, vale o Processo (D-015). `estado_final_do_processo` é o status do
    Processo encerrado ou cancelado, para dizer qual dos dois; `canal`, o atendimento da unidade.
    """
    pedidos = list(getattr(leitura, "pedidos", None) or [])
    if not pedidos:
        return None

    if desfecho is not None:
        momento = DECIDIDA
    elif causa_do_fechamento == PROCESSO:
        momento = ENCERRADA_PELO_PROCESSO
    elif causa_do_fechamento == PRAZO:
        momento = ENCERRADA_PELO_PRAZO
    else:
        momento = ABERTA

    prazo_nao_iniciado = estado_do_prazo == convocacao_nomes.CONVOCADO_PRAZO_NAO_INICIADO
    prazo = "" if prazo_nao_iniciado else ate(vencimento)

    itens = tuple(_item(lido, momento, prazo if momento == ABERTA else "") for lido in pedidos)
    estado_req = estado_do_requerimento(requerimento, desfecho=desfecho, causa=causa_do_fechamento)
    obrigatorios = [i for i in itens if not i.opcional]
    totais = {
        "a_corrigir": sum(1 for i in obrigatorios if i.categoria == A_CORRIGIR),
        "a_enviar": sum(1 for i in obrigatorios if i.categoria == A_ENVIAR),
        "com_a_comissao": sum(1 for i in obrigatorios if i.categoria == COM_A_COMISSAO),
        "conferidos": sum(1 for i in obrigatorios if i.categoria == CONFERIDO),
        "requerimento": momento == ABERTA and estado_req == REQ_A_PREENCHER,
    }

    base = Obrigacoes(
        momento=momento,
        causa=causa_do_fechamento or "",
        itens=itens,
        tarefas=(),
        requerimento=estado_req,
        totais=totais,
        vencimento=vencimento,
        prazo_nao_iniciado=prazo_nao_iniciado,
        prazo=prazo,
        frase_de_estado="",
        linha_do_requerimento=LINHA_DO_REQUERIMENTO.get(estado_req, ""),
    )
    tarefas = ()
    if momento == ABERTA:
        tarefas = tuple(
            Tarefa(texto=item.nome, ancora=item.ancora, motivo=item.motivo)
            for item in base.tarefas_de_documento
        )
        if totais["requerimento"]:
            tarefas += (Tarefa(texto=REQUERIMENTO, requerimento=True),)

    extras = {}
    if momento == ABERTA:
        extras.update(_aberta(base, tarefas, totais, prazo, prazo_nao_iniciado))
    elif momento == ENCERRADA_PELO_PRAZO:
        extras.update(_encerrada_pelo_prazo(base, vencimento, estado_req, canal))
    elif momento == ENCERRADA_PELO_PROCESSO:
        extras.update(_encerrada_pelo_processo(base, estado_req, estado_final_do_processo, canal))
    else:
        extras["frase_de_estado"] = NADA_POR_ENQUANTO

    return replace(base, tarefas=tarefas, **extras)


def frase_das_tarefas(totais):
    """*"Você ainda precisa corrigir 1 documento, enviar 2 documentos e preencher…"*"""
    partes = []
    if totais["a_corrigir"]:
        partes.append(f"corrigir {documentos(totais['a_corrigir'])}")
    if totais["a_enviar"]:
        partes.append(f"enviar {documentos(totais['a_enviar'])}")
    if totais["requerimento"]:
        partes.append("preencher o Requerimento de Matrícula")
    return f"Você ainda precisa {juntar(partes)}." if partes else ""


def _aberta(base, tarefas, totais, prazo, prazo_nao_iniciado):
    opcionais = base.opcionais_a_enviar
    extras = {"frase_de_estado": frase_das_tarefas(totais) or NADA_POR_ENQUANTO}
    if not tarefas:
        extras["frase_de_conclusao"] = FRASE_DE_CONCLUSAO
        if opcionais:
            qual = "o documento opcional" if len(opcionais) == 1 else "os documentos opcionais"
            ate_o_prazo = f" {prazo}" if prazo else ""
            extras["frase_do_opcional"] = f"Se quiser, você ainda pode enviar {qual}{ate_o_prazo}."
    if prazo_nao_iniciado:
        frases = (PRAZO_NAO_INICIADO,)
        if tarefas or opcionais:
            frases += (JA_PODE_ENVIAR,)
        extras["frase_do_prazo"] = frases
    elif prazo:
        extras["frase_do_prazo"] = (f"Prazo desta convocação: {prazo}.",)
    else:
        extras["frase_do_prazo"] = (SEM_PRAZO_REGISTRADO,)
    return extras


def _o_que_nao_se_envia(estado_req):
    if estado_req in (REQ_NAO_ENVIADO_ATE_O_PRAZO, REQ_NAO_ENVIADO_ENCERRADO):
        return "documentos nem o Requerimento de Matrícula"
    return "documentos"


def _nomes_sem_envio(base):
    return [
        f"{item.nome} (correção pedida)" if item.categoria == A_CORRIGIR else item.nome
        for item in base.tarefas_de_documento
    ]


def _resumo(base, *, com_a_comissao):
    """As linhas do *"ficou assim"*: o sem envio, o que está com a comissão e o Requerimento."""
    linhas = []
    sem_envio = _nomes_sem_envio(base)
    if sem_envio:
        linhas.append(f"Sem envio: {juntar(sem_envio)}.")
    total = base.totais
    if total["com_a_comissao"]:
        linhas.append(f"{com_a_comissao}: {documentos(total['com_a_comissao'])}.")
    if total["conferidos"]:
        linhas.append(f"Conferidos: {documentos(total['conferidos'])}.")
    if base.requerimento == REQ_ENVIADO:
        linhas.append(REQUERIMENTO_ENVIADO)
    elif base.linha_do_requerimento:
        linhas.append(base.linha_do_requerimento)
    return tuple(linhas)


def _sem_envio(base, estado_req, quando):
    nomes = _nomes_sem_envio(base)
    if estado_req in (REQ_NAO_ENVIADO_ATE_O_PRAZO, REQ_NAO_ENVIADO_ENCERRADO):
        nomes.append(REQUERIMENTO)
    return f"{quando}, ficaram sem envio: {juntar(nomes)}." if nomes else ""


def _encerrada_pelo_prazo(base, vencimento, estado_req, canal):
    """O vencido: o núcleo único e os complementos (FR-3741, FR-3748)."""
    fechamento = (
        frase_do_prazo_decorrido(vencimento),
        f"Não é mais possível enviar {_o_que_nao_se_envia(estado_req)} pelo portal.",
        frase_do_atendimento(canal),
    )
    sem_envio = _sem_envio(base, estado_req, "Até o prazo")
    return {
        "frase_de_estado": " ".join(fechamento + ((sem_envio,) if sem_envio else ())),
        "titulo_do_fechamento": "O prazo terminou",
        "frase_do_fechamento": fechamento,
        "titulo_do_resumo": "Até o prazo, ficou assim",
        "resumo": _resumo(base, com_a_comissao="Com a comissão"),
        "frase_do_prazo": (f"O prazo desta convocação terminou em {data_e_hora(vencimento)}.",)
        if vencimento is not None
        else (),
    }


def _encerrada_pelo_processo(base, estado_req, estado_final_do_processo, canal):
    """O Processo em estado final: sem prazo vencido nem conferência prometida (FR-3741)."""
    participio = ENCERRADO_OU_CANCELADO.get(estado_final_do_processo, "encerrado")
    fechamento = (
        f"Este Processo Seletivo foi {participio}, e não é mais possível enviar "
        f"{_o_que_nao_se_envia(estado_req)} pelo portal.",
        frase_do_atendimento(canal),
    )
    sem_envio = _sem_envio(base, estado_req, "Até o encerramento do Processo")
    return {
        "frase_de_estado": " ".join(fechamento + ((sem_envio,) if sem_envio else ())),
        "titulo_do_fechamento": "O envio pelo portal está encerrado",
        "frase_do_fechamento": fechamento,
        "titulo_do_resumo": "Até o encerramento do Processo, ficou assim",
        # Sem "aguardando": com o Processo em estado final ninguém confere (FR-3724).
        "resumo": _resumo(base, com_a_comissao="Não conferidos antes do encerramento"),
    }


__all__ = [
    "ABERTA",
    "ACEITE",
    "DECIDIDA",
    "ENCERRADA_PELO_PRAZO",
    "ENCERRADA_PELO_PROCESSO",
    "FRASE_DE_CONCLUSAO",
    "NUCLEO_DO_PRAZO",
    "PRAZO",
    "PROCESSO",
    "Obrigacoes",
    "ate",
    "categoria",
    "estado_do_requerimento",
    "frase_do_prazo_decorrido",
    "linha_informativa_do_requerimento",
    "obrigacoes_da_convocacao",
    "texto_do_item",
]
