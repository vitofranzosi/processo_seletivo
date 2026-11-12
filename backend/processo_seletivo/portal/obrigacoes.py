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
from zoneinfo import ZoneInfo

from django.conf import settings

from processo_seletivo.convocacao.application.documentos import NUCLEO_DO_PRAZO_DECORRIDO
from processo_seletivo.convocacao.application.documentos import (
    frase_do_prazo_decorrido as _frase_do_prazo_decorrido,
)
from processo_seletivo.convocacao.domain import documentos as dominio
from processo_seletivo.convocacao.domain import nomes as convocacao_nomes
from processo_seletivo.convocacao.domain import vocabulario_do_canal
from processo_seletivo.convocacao.domain.prazo_apresentado import apresentar
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
# A da mensagem, que é a de sempre; a da publicação mora com ela, na tabela do canal (125, FR-3999).
PRAZO_NAO_INICIADO = vocabulario_do_canal.MENSAGEM.prazo_nao_iniciado
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

# --- A chamada da `121` (FR-3858 a FR-3869) -----------------------------------------------------
# **O título diz o estado, e absorve o do bloco 1** (D-005): com *"O prazo desta convocação
# terminou"* no topo, o bloco não repete *"O prazo terminou"* abaixo. Nenhum promete vaga,
# matrícula nem contratação (FR-3751 da `118`).
TITULO_ABERTA = "Você foi convocado!"
TITULO_ENCERRADA_PELO_PRAZO = "O prazo desta convocação terminou"
TITULO_ENCERRADA_PELO_PROCESSO = "O envio pelo portal está encerrado"
TITULO_DECIDIDA = "Resultado da sua convocação"
TITULOS = {
    ABERTA: TITULO_ABERTA,
    ENCERRADA_PELO_PRAZO: TITULO_ENCERRADA_PELO_PRAZO,
    ENCERRADA_PELO_PROCESSO: TITULO_ENCERRADA_PELO_PROCESSO,
    DECIDIDA: TITULO_DECIDIDA,
}
# **A chamada aberta sem providência pendente** (154, FR-6202): a linha da chamada aberta da FR-3858
# se dividiu em duas. Com tudo enviado, *"Você foi convocado!"* repetia um convite que a pessoa já
# tinha atendido (achado 20 do estudo da jornada final). Não é momento novo — a etapa, o prazo, a
# ressalva e o andamento continuam os da chamada aberta —, e por isso não entra em `TITULOS`.
TITULO_SEM_PROVIDENCIA = "Acompanhe sua convocação"
# **A etapa descreve as obrigações da chamada, e não o estado** (FR-3860): sai da lista gravada no
# ato de convocar e da política do Requerimento, e vale igual antes e depois de qualquer envio. Sem
# imperativo — *"envie o Requerimento"* o pediria a quem já o enviou (cenário F).
ETAPAS = {
    (True, True): "Nesta etapa, você envia seus documentos e o Requerimento de Matrícula para a "
    "comissão conferir.",
    (True, False): "Nesta etapa, você envia seus documentos para a comissão conferir.",
    (False, True): "Nesta etapa, você envia o Requerimento de Matrícula e pode enviar documento "
    "opcional para a comissão conferir.",
    (False, False): "Nesta etapa, você pode enviar documento opcional para a comissão conferir.",
}
# **"Matrícula" só com o Requerimento de Matrícula** (D-003): num Edital de bolsista, que não o
# pede, "ainda não é a matrícula" seria falso.
RESSALVA_DA_MATRICULA = (
    "Esta convocação ainda não é a matrícula: a comissão confere o que você enviar e registra o "
    "resultado."
)
RESSALVA_DO_RESULTADO = (
    "Esta convocação ainda não é o resultado: a comissão confere o que você enviar e registra o "
    "resultado."
)
# O link só navega, e por isso não começa por "Enviar" (FR-3863; FR-3730 da `118`).
VER_O_QUE_PRECISO_FAZER = "Ver o que preciso fazer"
ROTULO_DO_PRAZO = "Prazo desta convocação"
CORRIGIDA = "Convocação corrigida: este é o prazo válido."
# A âncora do cartão do Requerimento a preencher, no bloco *O que falta* (FR-3738 da `118`).
ANCORA_DO_REQUERIMENTO = "requerimento-a-preencher"


def requerimento_na_chamada(disponibilidade):
    """O Requerimento é pedido **nesta chamada**: exigido, e declarado *na convocação*."""
    d = disponibilidade
    return bool(d is not None and d.exigido and d.momento == requerimento_nomes.NA_CONVOCACAO)


def requerimento_exigido(disponibilidade):
    """O Edital exige o Requerimento de Matrícula, em qualquer momento (D-003)."""
    return bool(disponibilidade is not None and disponibilidade.exigido)


def ressalva(disponibilidade):
    """A ressalva da FR-3864: *"ainda não é a matrícula"* só com o Requerimento (D-003)."""
    return RESSALVA_DA_MATRICULA if requerimento_exigido(disponibilidade) else RESSALVA_DO_RESULTADO


@dataclass(frozen=True)
class CartaoDoPrazo:
    """O cartão do prazo da chamada (FR-3861): o rótulo e o formato da `118`, a data como o maior
    texto, e a linha do dia da semana e da contagem abaixo dela (FR-3874).

    Sem data, ele diz só a frase do caso: o prazo não iniciado (FR-3749 da `118`) ou a convocação
    sem vencimento (FR-3737 da `118`). A correção vem acima da data, no próprio cartão (FR-3869).
    """

    #: Só com data: com o prazo não iniciado ou sem vencimento, o cartão diz **só** a frase do caso.
    rotulo: str = ""
    corrigida: str = ""
    data: str = ""
    linha: str = ""
    frases: tuple = ()


def cartao_do_prazo(
    *,
    prazo_nao_iniciado,
    vencimento,
    agora,
    corrigida,
    ja_pode_enviar=False,
    frase_do_nao_iniciado=PRAZO_NAO_INICIADO,
):
    """O cartão do prazo de uma chamada **aberta**; com ela fechada, não há cartão (FR-3867).

    `frase_do_nao_iniciado` é a do canal da convocação (125, FR-3999); sem ela, a da mensagem.
    """
    frase_da_correcao = CORRIGIDA if corrigida else ""
    if prazo_nao_iniciado:
        frases = (frase_do_nao_iniciado,) + ((JA_PODE_ENVIAR,) if ja_pode_enviar else ())
        return CartaoDoPrazo(corrigida=frase_da_correcao, frases=frases)
    if vencimento is None:
        return CartaoDoPrazo(corrigida=frase_da_correcao, frases=(SEM_PRAZO_REGISTRADO,))
    prazo = apresentado(vencimento, agora)
    return CartaoDoPrazo(
        rotulo=ROTULO_DO_PRAZO,
        corrigida=frase_da_correcao,
        data=prazo.ate,
        # Sem o instante da requisição, a contagem não se diz: inventá-la do relógio aqui faria a
        # função depender de quando é chamada (FR-3873).
        linha=prazo.linha if agora is not None else "",
    )


@dataclass(frozen=True)
class AcaoDaChamada:
    rotulo: str
    ancora: str


# --- A volta do envio (121, FR-3870) -------------------------------------------------------------
# **"O arquivo aguarda"**, e não "ela aguarda" (D-010): concorda com todo nome de documento. Nunca
# "aceito", "aprovado", "conferido" nem "atendido" — a comissão ainda não disse nada (FR-3751).
RECEBEMOS = (
    "Recebemos: {documento}, em {data}, às {hora}. O arquivo aguarda a conferência da comissão."
)
JA_RECEBIDO = "Este arquivo já tinha sido recebido."
PROXIMA_TAREFA = "Próxima tarefa:"


@dataclass(frozen=True)
class ConfirmacaoDoEnvio:
    frase: str
    #: A primeira tarefa da FR-3726 **depois** do envio, ou `None`.
    proxima: object = None
    proxima_ancora: str = ""
    #: Sem tarefa restante, a frase de conclusão da FR-3728 no lugar da próxima tarefa.
    conclusao: str = ""
    rotulo: str = PROXIMA_TAREFA
    #: No envio de vários (150, FR-5608): uma linha por documento recebido, na ordem de chegada.
    recebidos: tuple = ()
    #: E os recusados do mesmo envio, como `(nome, âncora do cartão)`, com o rótulo que os conta.
    nao_recebidos: tuple = ()
    rotulo_dos_nao_recebidos: str = ""


# --- A volta do envio de vários (150, FR-5608) ---------------------------------------------------
# **"Recebemos R de N"**, com N o que a pessoa mandou: a frase diz, antes da lista, que pode faltar
# algum. O mesmo cuidado da D-010 da `121` com o verbo: o arquivo **aguarda**, nunca foi "aceito".
RECEBEMOS_DE = "Recebemos {recebidos} de {total} documentos. {aguarda}"
AGUARDA_UM = "O arquivo aguarda a conferência da comissão."
AGUARDAM = "Os arquivos aguardam a conferência da comissão."
LINHA_DO_RECEBIDO = "{documento}, em {data}, às {hora}."
LINHA_DO_JA_RECEBIDO = "{documento}: este arquivo já tinha sido recebido."
UM_NAO_RECEBIDO = "1 documento não foi recebido:"
NAO_RECEBIDOS = "{quantos} documentos não foram recebidos:"


def confirmacao_do_lote(projecao, *, envios, total, recusas=()):
    """A confirmação do envio de vários documentos, montada da projeção depois do último (FR-5608).

    **Com um só, é a de hoje** (`confirmacao_do_envio`), sem "1 de 1". Com mais, a frase conta os
    recebidos sobre os enviados, lista cada recebido com data e hora, e liga cada recusado ao cartão
    dele, onde a recusa está (FR-3871 da `121`).

    **A próxima tarefa e a conclusão não são recalculadas aqui**: vêm de `confirmacao_do_envio`
    sobre o último recebido, e só a frase é trocada. Assim o que a `154` mudar ali vale igual para
    o envio de um e para o de vários, sem duas regras para manter.
    """
    if total <= 1 and len(envios) == 1 and not recusas:
        return confirmacao_do_envio(projecao, **envios[0])
    linhas = []
    base = None
    for envio in envios:
        item = next((i for i in projecao.itens if str(i.id) == str(envio["item_id"])), None)
        if item is None:
            continue
        if envio["ja_recebido"]:
            linhas.append(LINHA_DO_JA_RECEBIDO.format(documento=item.nome))
        else:
            apresentacao = next(
                (a for a in item.lido.apresentacoes if str(a.id) == str(envio["apresentacao_id"])),
                None,
            )
            instante = apresentacao.apresentado_em if apresentacao is not None else None
            linhas.append(
                LINHA_DO_RECEBIDO.format(
                    documento=item.nome,
                    data=data(instante) if instante else "",
                    hora=hora(instante) if instante else "",
                )
            )
        # O `ja_recebido=False` só pede a cauda inteira — próxima tarefa ou conclusão —, que o
        # caminho do mesmo arquivo de novo omite; a frase dele é descartada logo abaixo.
        base = confirmacao_do_envio(projecao, **{**envio, "ja_recebido": False})
    if base is None:
        return None
    por_ancora = {i.ancora: i.nome for i in projecao.itens}
    nao_recebidos = tuple(
        (por_ancora[r["ancora"]], r["ancora"]) for r in recusas if r["ancora"] in por_ancora
    )
    rotulo = ""
    if nao_recebidos:
        rotulo = (
            UM_NAO_RECEBIDO
            if len(nao_recebidos) == 1
            else NAO_RECEBIDOS.format(quantos=len(nao_recebidos))
        )
    return replace(
        base,
        frase=RECEBEMOS_DE.format(
            recebidos=len(linhas),
            total=max(total, len(linhas)),
            aguarda=AGUARDA_UM if len(linhas) == 1 else AGUARDAM,
        ),
        recebidos=tuple(linhas),
        nao_recebidos=nao_recebidos,
        rotulo_dos_nao_recebidos=rotulo,
    )


def confirmacao_do_envio(projecao, *, item_id, apresentacao_id, ja_recebido):
    """A confirmação do envio aceito, montada da projeção depois dele (FR-3870, R-006).

    Cada volta mostra só o seu envio (D-010); o andamento mostra o acumulado. O mesmo arquivo de
    novo diz só que já tinha sido recebido, sem próxima tarefa nova.
    """
    item = next((i for i in projecao.itens if str(i.id) == str(item_id)), None)
    if item is None:
        return None
    if ja_recebido:
        return ConfirmacaoDoEnvio(frase=JA_RECEBIDO)
    apresentacao = next(
        (a for a in item.lido.apresentacoes if str(a.id) == str(apresentacao_id)), None
    )
    instante = apresentacao.apresentado_em if apresentacao is not None else None
    frase = RECEBEMOS.format(
        documento=item.nome,
        data=data(instante) if instante else "",
        hora=hora(instante) if instante else "",
    )
    if not projecao.aberta:
        # **Fechada entre o envio e a volta** — o prazo venceu, o Processo encerrou ou o resultado
        # saiu: nem próxima tarefa nem conclusão. A conclusão diria "não tem mais documentos para
        # enviar" logo acima de "ficaram sem envio", e a chamada já conta o que houve.
        return ConfirmacaoDoEnvio(frase=frase)
    if projecao.tarefas:
        return ConfirmacaoDoEnvio(
            frase=frase, proxima=projecao.tarefas[0], proxima_ancora=projecao.primeira_ancora
        )
    return ConfirmacaoDoEnvio(frase=frase, conclusao=FRASE_DE_CONCLUSAO)


SUBSTITUIDA = "Convocação substituída"
_POR_PUBLICACAO = "PUBLICATION"


def linha_da_substituida(anterior):
    """A linha *"Convocação substituída"* dos dados do ato, da **imediatamente anterior** (FR-3869).

    **A anterior, e não a última comunicada da cadeia** (R-008, D-008): a mensagem da correção cita
    a última enviada com sucesso, e os dados do ato dizem qual convocação esta substituiu. As duas
    leituras são diferentes por decisão do usuário, e não se unificam.

    Lê só o que `vigentes_por_inscricao` já trouxe no *prefetch* — a anterior e as comunicações dela
    —, sem consulta por item. **Sem o motivo** (a proteção de dados da `120`), e sem *"novo prazo"*
    nem *"prorrogação"*: a sucessora pode antecipar (FR-3856 da `120`).
    """
    if anterior is None:
        return ""
    prazo = f"até {data_e_hora(anterior.vencimento)}" if anterior.vencimento else ""
    enviadas = [c for c in anterior.comunicacoes.all() if c.resultado == "ENVIADA" and c.enviado_em]
    if not enviadas:
        if not prazo:
            return "Não comunicada, sem prazo registrado."
        return f"Não comunicada. O prazo registrado era {prazo}, e não vale mais."
    ultima = max(enviadas, key=lambda comunicacao: comunicacao.enviado_em)
    if ultima.forma == _POR_PUBLICACAO:
        quando = f"Publicada em {ultima.referencia_da_publicacao.strip()}"
    else:
        # *"Enviada"*, e não *"Comunicada"*: a palavra da mensagem (125, D-008, FR-3869 revista).
        quando = f"Enviada em {data_e_hora(ultima.enviado_em)}"
    if not prazo:
        return f"{quando}, sem prazo registrado."
    return f"{quando}, com prazo {prazo}. Esse prazo não vale mais."


def momento_sem_documento(*, estado_do_prazo, desfecho, fechado_pelo_processo):
    """O momento da chamada que não pede documento, para o título da FR-3858 (FR-3868).

    A causa vem do que a tela sem documento já sabe: o estado do prazo e, pela política do
    Requerimento, se o Processo está em estado final. Com os dois, vale o Processo (D-015 da `118`).
    """
    if desfecho is not None:
        return DECIDIDA
    if fechado_pelo_processo:
        return ENCERRADA_PELO_PROCESSO
    if estado_do_prazo == convocacao_nomes.CONVOCADO_VENCIMENTO_DECORRIDO:
        return ENCERRADA_PELO_PRAZO
    return ABERTA


def providencia_pendente_sem_documento(disponibilidade):
    """A providência pendente da chamada que não pede documento (154, FR-6201, D-006).

    **Só o Requerimento pedido nesta chamada, e já enviado, a desfaz.** O chamado `"conferir"` da
    tela não serve para isto: ele vale para todo Requerimento enviado, inclusive o pedido na
    inscrição — e aí a chamada não pede nada pelo portal, e a D-006 manda manter a tela de hoje,
    porque o sistema não verifica o cumprimento externo. Lê a mesma `Disponibilidade` que a tela já
    leu, sem consulta.
    """
    return not (requerimento_na_chamada(disponibilidade) and disponibilidade.enviado)


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


def fuso():
    """O fuso da instalação, das settings, e nunca o do servidor (121, FR-3873)."""
    return ZoneInfo(settings.TIME_ZONE)


def apresentado(vencimento, agora=None):
    """O prazo apresentado da `121`: a mesma função do e-mail, no fuso da instalação (FR-3873).

    Sem `agora`, a data e a hora valem e a contagem é a do próprio instante — é o caso de quem só
    quer escrever uma data, como os recebimentos.
    """
    return apresentar(vencimento, agora or vencimento, fuso())


def data(instante):
    return apresentado(instante).data


def hora(instante):
    return apresentado(instante).hora


def data_e_hora(instante):
    """*"09/11/2026, às 13h27"* — o formato único do prazo e dos recebimentos (FR-3747)."""
    return apresentado(instante).data_e_hora


def ate(vencimento):
    """*"até 09/11/2026, às 13h27"* (FR-3747), ou vazio sem vencimento."""
    return apresentado(vencimento).ate if vencimento is not None else ""


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

    condicao = getattr(lido, "condicao", None)
    if estado == convocacao_nomes.ITEM_A_APRESENTAR and condicao and aberta:
        # **O condicional orienta e não manda enviar** (131, FR-4475, UX-304): a quem a condição
        # não alcança, *"Falta enviar."* pedia o que o Edital não pede. Continua tarefa, porque a
        # comissão pode precisar do arquivo para saber se a condição se aplica.
        return (
            f"Obrigatório {condicao}. Se for o seu caso, envie{ate_o_prazo}. Se não for, você não "
            "precisa enviar: a comissão registra."
        )
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
    # A chamada da `121`: o instante da requisição, para a contagem do prazo; se a vigente sucede
    # outra; e o que a política do Requerimento diz da etapa e da ressalva.
    agora: object = None
    corrigida: bool = False
    pede_requerimento: bool = False
    requerimento_exigido: bool = False
    # A frase do prazo não iniciado, no canal da convocação (125, FR-3999).
    frase_do_nao_iniciado: str = PRAZO_NAO_INICIADO

    @property
    def aberta(self):
        return self.momento == ABERTA

    # --- A chamada (121, FR-3858 a FR-3865) ----------------------------------------------------

    @property
    def titulo(self):
        """O título de primeiro nível, pelo estado (FR-3858) e, aberta, pela providência (154,
        FR-6202, FR-6203). É lido a cada projeção: o envio que tira a última tarefa e a pendência
        nova mudam o título sem que nada o guarde."""
        if self.aberta and not self.providencia_pendente:
            return TITULO_SEM_PROVIDENCIA
        return TITULOS[self.momento]

    # --- A providência pendente (154, FR-6200, FR-6205, FR-6209) --------------------------------

    @property
    def providencia_pendente(self):
        """Há tarefa da FR-3726 com a chamada aberta (D-001 da `154`).

        **As mesmas `tarefas` do resumo e da ação**: obrigatório a corrigir, obrigatório a enviar e
        o Requerimento a preencher. O opcional, o facultativo pendente, o que está com a comissão e
        o conferido ficam fora. Ler daqui, e não de uma segunda regra, é o que impede a página de
        dizer *"Acompanhe sua convocação"* e, logo abaixo, uma tarefa.
        """
        return self.aberta and bool(self.tarefas)

    @property
    def conferencia_terminada(self):
        """Todo obrigatório conferido — conforme ou *não se aplica* —, sem tarefa (D-002 da `154`).

        **Ao menos um obrigatório**: a chamada só com facultativo não tem conferência que termine.
        O estado dos opcionais não entra, e é por isso que a frase da US2 fala só dos obrigatórios.
        """
        obrigatorios = [item for item in self.itens if not item.opcional]
        return (
            self.aberta
            and not self.tarefas
            and bool(obrigatorios)
            and all(item.categoria == CONFERIDO for item in obrigatorios)
        )

    @property
    def cabe_a_consequencia(self):
        """A advertência da FR-1177 da `063`, revista pela FR-6209 da `154`.

        `prazo` já é vazio com o prazo não iniciado (comunicação não enviada) e sem vencimento
        registrado; `aberta` já exclui o vencido, o Processo encerrado e o desfecho. A condição nova
        é a última: **só com providência pendente** — quem já fez tudo não tem o que deixar de
        atender (achado 20 do estudo). O cartão do prazo não depende disto (FR-6208).
        """
        return self.aberta and bool(self.prazo) and self.providencia_pendente

    @property
    def pede_documento_obrigatorio(self):
        return any(not item.opcional for item in self.itens)

    @property
    def etapa(self):
        """O que a chamada pede, só com ela aberta (FR-3860, FR-3867)."""
        if not self.aberta:
            return ""
        return ETAPAS[(self.pede_documento_obrigatorio, self.pede_requerimento)]

    @property
    def cartao(self):
        """O cartão do prazo, só com a chamada aberta (FR-3861, FR-3867)."""
        if not self.aberta:
            return None
        return cartao_do_prazo(
            prazo_nao_iniciado=self.prazo_nao_iniciado,
            frase_do_nao_iniciado=self.frase_do_nao_iniciado,
            vencimento=self.vencimento,
            agora=self.agora,
            corrigida=self.corrigida,
            ja_pode_enviar=bool(self.tarefas or self.opcionais_a_enviar),
        )

    @property
    def resumo_do_que_falta(self):
        """*"Você ainda precisa ‹tarefas›."*, ou a frase de conclusão sem tarefa (FR-3862)."""
        if not self.aberta:
            return ""
        return frase_das_tarefas(self.totais) or FRASE_DE_CONCLUSAO

    @property
    def acao(self):
        """**Um** link à primeira tarefa da FR-3726, ou nada sem tarefa (FR-3863)."""
        if not self.aberta or not self.tarefas:
            return None
        return AcaoDaChamada(rotulo=VER_O_QUE_PRECISO_FAZER, ancora=self.primeira_ancora)

    @property
    def ressalva(self):
        """A ressalva da FR-3864, depois da ação, só com a chamada aberta (D-003)."""
        if not self.aberta:
            return ""
        return RESSALVA_DA_MATRICULA if self.requerimento_exigido else RESSALVA_DO_RESULTADO

    @property
    def andamento(self):
        """As contagens da FR-3727, só obrigatórios e sem o Requerimento (FR-3865, D-004).

        *A corrigir* só quando houver. Sem barra, sem percentual e sem frase de conclusão: "100 %
        enviado" leria como aprovado (FR-3728 da `118`).
        """
        if not self.aberta:
            return ()
        t = self.totais
        linhas = [("A corrigir", t["a_corrigir"])] if t["a_corrigir"] else []
        return (
            *linhas,
            ("A enviar", t["a_enviar"]),
            ("Aguardando conferência", t["com_a_comissao"]),
            ("Conferidos", t["conferidos"]),
        )

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
        """*O que falta*: documentos e o Requerimento a preencher; sem tarefa, os opcionais (FR-3735
        da `118`, revista pela `121`)."""
        return bool(
            self.que_falta or self.opcionais_a_enviar or self.requerimento_a_preencher_na_chamada
        )

    # --- O envio dos arquivos escolhidos (150, D-001 revista em 12/11/2026) ----------------------
    # Um botão só para a página, e não um por cartão: ele mora no fim do primeiro bloco que tem
    # cartão com envio. *O que falta* quando há o que mandar ali; senão, *O que você já
    # apresentou*, onde só há substituição. Os cartões de substituição que ficam abaixo do botão
    # apontam para ele.

    @property
    def envio_no_que_falta(self):
        return any(i.pode_enviar for i in self.que_falta + self.opcionais_a_enviar)

    @property
    def envio_no_que_ja_apresentou(self):
        return not self.envio_no_que_falta and any(i.pode_enviar for i in self.ja_apresentados)

    @property
    def um_so_com_envio(self):
        """Um cartão só com envio: a frase de como se envia não fala em "cada documento"."""
        return sum(1 for i in self.itens if i.pode_enviar) == 1

    @property
    def primeira_ancora(self):
        """A âncora da primeira tarefa da FR-3726 — e a do Requerimento quando ele é a única (121,
        FR-3863, SC-1151). Antes da `121` ela só olhava documentos, e o botão sumia justamente
        quando a única coisa a fazer era o Requerimento."""
        tarefas = self.tarefas_de_documento
        if tarefas:
            return tarefas[0].ancora
        return ANCORA_DO_REQUERIMENTO if self.totais["requerimento"] else ""

    @property
    def requerimento_a_preencher_na_chamada(self):
        """O cartão do Requerimento no bloco *O que falta* (FR-3738). O total já só vale com a
        chamada aberta: é a mesma condição que faz dele tarefa."""
        return bool(self.totais["requerimento"])

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
    agora=None,
    corrigida=False,
    prazo_nao_iniciado=PRAZO_NAO_INICIADO,
):
    """As obrigações da chamada vigente, ou `None` quando ela não pede documento (FR-3743).

    `causa_do_fechamento` é `None`, `PRAZO` ou `PROCESSO`, derivada pela view da mesma condição que
    recusa o envio; com as duas, vale o Processo (D-015). `estado_final_do_processo` é o status do
    Processo encerrado ou cancelado, para dizer qual dos dois; `canal`, o atendimento da unidade.

    `agora` é o instante da requisição, para a contagem do cartão do prazo, e `corrigida` diz que a
    vigente sucede outra (121, FR-3861, FR-3869). A projeção continua sem ler relógio.

    `prazo_nao_iniciado` é a frase do canal da convocação (125, FR-3999): a projeção não lê a forma.
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

    frase_do_nao_iniciado = prazo_nao_iniciado
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
        agora=agora,
        corrigida=corrigida,
        pede_requerimento=requerimento_na_chamada(requerimento),
        requerimento_exigido=requerimento_exigido(requerimento),
        frase_do_nao_iniciado=frase_do_nao_iniciado,
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
        frases = (base.frase_do_nao_iniciado,)
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
    "CORRIGIDA",
    "DECIDIDA",
    "ENCERRADA_PELO_PRAZO",
    "ENCERRADA_PELO_PROCESSO",
    "FRASE_DE_CONCLUSAO",
    "NUCLEO_DO_PRAZO",
    "PRAZO",
    "PROCESSO",
    "TITULOS",
    "TITULO_SEM_PROVIDENCIA",
    "CartaoDoPrazo",
    "Obrigacoes",
    "apresentado",
    "ate",
    "cartao_do_prazo",
    "categoria",
    "estado_do_requerimento",
    "frase_do_prazo_decorrido",
    "linha_da_substituida",
    "linha_informativa_do_requerimento",
    "momento_sem_documento",
    "obrigacoes_da_convocacao",
    "providencia_pendente_sem_documento",
    "ressalva",
    "texto_do_item",
]
