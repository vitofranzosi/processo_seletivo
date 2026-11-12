"""A convocação como fluxo: os gestos que alcançam N pessoas, e a chamada que já comunica (050).

**Três laços por pessoa viraram gestos por recorte**, e nenhum deles decide nada sobre alguém:

- **convocar os titulares** é formalizar o que a faixa e a apuração já disseram (`FR-860`);
- **registrar o não atendimento dos vencidos** é o mesmo juízo que o relógio já mostrou, N vezes
  (`FR-877`, `DP-16`, opção B);
- **emitir as comunicações pendentes** é repetir, pessoa a pessoa, o envio que o Edital declarou
  (`FR-874`).

O que é decisão sobre uma pessoa — aceite, indeferimento, regularização, desistência,
reclassificação, inércia, e chamar o suplente — continua um ato por pessoa, e não passa por aqui
(`FR-881`).

**Cada gesto tem prévia, e a confirmação carrega a assinatura dela** (`D-007`). É o contrapeso da
`DP-17`: o que o sistema derivou fica visível antes do ato irreversível, e o ato recusa quando o
alcance de agora não é o que a pessoa viu.

**Nenhuma entidade de lote** (`D-011`). Cada registro é o de sempre, um por pessoa, com autor; o que
nasceu junto é reconstruído pela correlação da trilha, `convocacao-lote-<chave>`.

**A comunicação vem depois do `commit`, e pelo `comunicar` que já existe** (`D-006`). O envio nunca
acontece dentro da transação que trava o Processo, e cada pessoa tem a sua chave, derivada da chave
do gesto: repetir a confirmação completa os envios que não começaram e não reenvia nenhum.
"""

from zoneinfo import ZoneInfo

from django.conf import settings
from django.utils import timezone
from django.utils.dateparse import parse_datetime

from processo_seletivo.classificacao.application import marco_intermediario
from processo_seletivo.classificacao.domain.universo import por_identidade
from processo_seletivo.comissoes.application import comando_de_comissao, exigir_base_de_comissao
from processo_seletivo.comissoes.application.comissao import identificador
from processo_seletivo.convocacao.application import selectors
from processo_seletivo.convocacao.application.comunicar import (
    SEM_FORMA_DECLARADA,
    comunicar,
    previa_das_mensagens,
)
from processo_seletivo.convocacao.application.convocar import (
    _ESPECIE_POR_EXTENSO,
    _edital_do_processo,
    convocar,
    convocar_em_sequencia,
    declarado_da_convocacao,
    verificar_chamada,
)
from processo_seletivo.convocacao.application.convocar import ATO as ATO_DA_CHAMADA
from processo_seletivo.convocacao.application.desfechar import (
    apuracao_seguinte,
    auditar_desfecho,
    declarado_do_desfecho,
    registrar,
)
from processo_seletivo.convocacao.domain import (
    alcance,
    fila,
    fundamento,
    nomes,
    prazo,
    vocabulario_do_canal,
)
from processo_seletivo.convocacao.domain import especie as especie_da_posicao
from processo_seletivo.convocacao.domain.prazo_apresentado import apresentar
from processo_seletivo.convocacao.models import Convocacao
from processo_seletivo.editais.domain.recortes import rotulo_do_recorte
from processo_seletivo.ocupacao.domain.apuracao import chave_da_inscricao
from processo_seletivo.processos.domain.finalizacao import ensure_processo_accepts_changes
from processo_seletivo.publicacoes.application.selectors import effective_version
from processo_seletivo.publicacoes.domain.vocabulario_da_regra import (
    FORMA_POR_MENSAGEM_INDIVIDUAL,
    FORMA_POR_PUBLICACAO,
    FORMAS_DE_CONVOCACAO,
)
from processo_seletivo.publicacoes.models import VersaoConsolidada
from processo_seletivo.shared.api.problems import DomainError

GESTO_TITULARES = "convocacao:convocar_titulares"
#: A chamada individual e a para regularizar: a operação do próprio comando (152, FR-5818).
GESTO_CHAMADA = ATO_DA_CHAMADA
GESTO_VENCIDOS = "convocacao:nao_atendimento_dos_vencidos"

#: A frase que a trilha e a tela usam quando o vencimento foi digitado no ato.
ORIGEM_INFORMADA = "informado neste ato"


# --- O que é derivado --------------------------------------------------------------------------


def forma_vigente(versao, perfil_id):
    """A forma de comunicar que o Perfil declara **na versão vigente** — a que as convocações
    nascidas agora vão citar. `None` é *"não declarou"*, e nunca a publicação por omissão."""
    perfil = por_identidade((versao.content or {}).get("profiles"), perfil_id) or {}
    forma = perfil.get("callForm")
    return forma if forma in FORMAS_DE_CONVOCACAO else None


def rotulos(edital, versao, *, perfil_id, lista_id):
    """O Edital e o recorte por extenso, como o fundamento os cita."""
    perfil = por_identidade((versao.content or {}).get("profiles"), perfil_id) or {}
    recorte = rotulo_do_recorte(versao.content, perfil_id=perfil_id, lista_id=lista_id)
    return (
        f"Edital nº {edital.number}/{edital.year}",
        f"Perfil «{perfil.get('name') or ''}», recorte «{recorte}»",
    )


def eventos_do_cronograma(versao, *, agora=None):
    """Os Eventos do Cronograma publicado com data de fim — a origem que o vencimento pode ter.

    **Só com fim**, e só os futuros quando `agora` vem: o início de um Evento não é prazo para
    atender, e um Evento já encerrado daria vencimento anterior ao envio (`FR-269b`).
    """
    eventos = []
    for evento in (versao.content or {}).get("schedule") or []:
        fim = parse_datetime(evento.get("endAt") or "")
        if fim is None or (agora is not None and fim <= agora):
            continue
        eventos.append(
            {
                "id": str(evento.get("id")),
                "rotulo": evento.get("type") or evento.get("description") or "Evento",
                "fim": fim,
            }
        )
    return sorted(eventos, key=lambda item: item["fim"])


def resolver_vencimento(*, versao, vencimento=None, evento_id=""):
    """O vencimento do ato e a origem dele, dita por extenso para a trilha (`FR-866`, `D-010`).

    **Uma vez por ato.** O Evento escolhido tem precedência sobre a data digitada, porque é o que o
    Edital publicou; sem nenhum dos dois, o Edital não publica prazo, e vazio continua sendo isso.
    """
    if evento_id and vencimento is not None:
        # **Uma origem só.** Escolher o Evento e digitar uma data por cima deixava o Evento vencer
        # em silêncio, e o prazo que N pessoas recebiam não era o que a tela mostrava por último.
        raise DomainError(
            "vencimento_com_duas_origens",
            "Escolha o Evento do Cronograma ou digite a data — não os dois.",
            422,
            campo="vencimento",
        )
    if evento_id:
        for evento in eventos_do_cronograma(versao):
            if evento["id"] == str(evento_id):
                return evento["fim"], f"do fim do Evento «{evento['rotulo']}» do Cronograma"
        raise DomainError(
            "evento_do_vencimento_inexistente",
            "O Evento escolhido não está no Cronograma vigente, ou não tem data de fim.",
            422,
            campo="evento",
        )
    if vencimento is not None:
        return vencimento, ORIGEM_INFORMADA
    return None, ""


def _razao_do_vencimento(instante, origem):
    if instante is None:
        return "Sem vencimento: o Edital não publica prazo."
    quando = timezone.localtime(instante).strftime("%d/%m/%Y %H:%M")
    return f"Vencimento {quando}, {origem}."


def _recusar_vencimento_passado(instante, agora):
    if instante is not None and prazo.vencimento_precede_o_envio(
        vencimento=instante, enviado_em=agora
    ):
        raise DomainError(
            nomes.VENCIMENTO_ANTERIOR_AO_ENVIO,
            "O vencimento informado já passou, ou vence agora: prazo que vence antes de a pessoa "
            "poder saber não é prazo.",
            409,
            campo="vencimento",
        )


def _data(instante):
    return timezone.localtime(instante).strftime("%d/%m/%Y") if instante else ""


def _impedimento(leitura, forma):
    """Por que o gesto dos titulares não pode acontecer agora, com a recusa que a chamada daria."""
    if leitura["apuracao"] is None:
        return {
            "codigo": nomes.APURACAO_AUSENTE,
            "detalhe": "Este recorte não tem apuração de ocupação emitida: não há vaga conhecida "
            "para a qual convocar.",
        }
    if leitura["causasDeObsolescencia"]:
        return {
            "codigo": nomes.APURACAO_OBSOLETA,
            "detalhe": "A apuração vigente deste recorte está obsoleta: emita a seguinte na "
            "ocupação antes de convocar.",
        }
    if forma is None:
        # **`D-002`.** Cada convocação cita a versão do dia, e a forma é lida dela: convocar aqui
        # produziria N chamadas que nenhuma Retificação posterior torna comunicáveis.
        return {
            "codigo": nomes.FORMA_DE_COMUNICACAO_NAO_DECLARADA,
            "detalhe": "O Perfil publicado não declara como este Edital comunica a convocação. "
            "Convocar agora produziria chamadas que não podem ser comunicadas: declare a forma por "
            "Retificação antes.",
        }
    return None


def _conferir(previa, assinatura):
    if (assinatura or "") != previa["assinatura"]:
        raise DomainError(
            nomes.ALCANCE_MUDOU,
            "O que este gesto alcança mudou desde que a tela foi aberta: confira o alcance de "
            "agora antes de confirmar.",
            409,
        )


def correlacao_do_gesto(chave):
    """A identidade do gesto na trilha (`D-011`, `FR-880`)."""
    return f"convocacao-lote-{chave}"[:100]


# --- Convocar os titulares ---------------------------------------------------------------------


def previa_dos_titulares(*, edital, perfil_id, marco_id, lista_id=None, at=None, leitura=None):
    """O que o gesto dos titulares alcançaria agora — **sem praticar ato nenhum** (`FR-862`)."""
    agora = at or timezone.now()
    leitura = leitura or selectors.leitura_do_recorte(
        edital=edital, perfil_id=perfil_id, marco_id=marco_id, lista_id=lista_id, at=agora
    )
    versao = effective_version(edital_id=edital.id, at=agora)
    forma = forma_vigente(versao, perfil_id)
    titulares = alcance.titulares_do_comeco_da_fila(
        [pessoa["id"] for pessoa in leitura["fila"]],
        ocupando=leitura["ocupando"],
        reabilitados=leitura["reabilitados"],
    )
    identificadas = leitura["identificadas"]
    apuracao = leitura["apuracao"]
    texto_do_edital, texto_do_recorte = rotulos(
        edital, versao, perfil_id=perfil_id, lista_id=lista_id
    )
    return {
        "pessoas": [
            {**identificadas[inscricao], "posicao": posicao, "especie": nomes.VAGA_INICIAL}
            for posicao, inscricao in enumerate(titulares.pessoas, start=1)
        ],
        "parada": (
            {**identificadas[titulares.parada], "motivo": titulares.motivo_da_parada}
            if titulares.parada is not None
            else None
        ),
        "fundamento": (
            fundamento.da_convocacao(
                especie=nomes.VAGA_INICIAL,
                edital=texto_do_edital,
                recorte=texto_do_recorte,
                data_da_apuracao=_data(apuracao.emitida_em),
            )
            if apuracao is not None
            else ""
        ),
        "forma": forma,
        "impedimento": _impedimento(leitura, forma),
        "eventos": eventos_do_cronograma(versao, agora=agora),
        "versao": versao,
        "assinatura": alcance.assinatura(
            gesto="titulares",
            apuracao_id=apuracao.id if apuracao is not None else None,
            versao_id=versao.id,
            forma=forma,
            identidades=titulares.pessoas,
        ),
    }


def verificar_titulares(
    *,
    edital,
    perfil_id,
    marco_id,
    lista_id,
    alcance_confirmado,
    vencimento,
    evento_id,
    agora,
    leitura=None,
):
    """As recusas do gesto dos titulares pela leitura do recorte, na ordem do comando (140, D-004).

    **Uma verificação só, para o comando e para a conferência.** O comando a chama sob a trava, e é
    ali que ela decide; a conferência a chama sem trava, para não mostrar o botão de um ato que só
    pode ser recusado. Duas listas de recusas divergiriam, e a conferência passaria a prometer o que
    o comando nega.

    Devolve `(previa, instante, origem)`, ou levanta a `DomainError` que o comando levantaria.
    """
    # **Antes da prévia** (133, FR-4537): sem isto, o marco intermediário sem apuração recusava por
    # "apuração ausente" ou "nenhum titular", e a frase do motivo verdadeiro nunca chegava a quem
    # pediu (a revisão do PR #432 acusou).
    marco_intermediario.recusar(
        effective_version(edital_id=edital.id, at=agora).content, perfil_id, marco_id
    )
    previa = previa_dos_titulares(
        edital=edital,
        perfil_id=perfil_id,
        marco_id=marco_id,
        lista_id=lista_id,
        at=agora,
        leitura=leitura,
    )
    if previa["impedimento"]:
        raise DomainError(previa["impedimento"]["codigo"], previa["impedimento"]["detalhe"], 409)
    _conferir(previa, alcance_confirmado)
    if not previa["pessoas"]:
        raise DomainError(
            nomes.NENHUM_TITULAR_A_CONVOCAR,
            "Não há titular ainda não chamado neste recorte.",
            409,
        )
    instante, origem = resolver_vencimento(
        versao=previa["versao"], vencimento=vencimento, evento_id=evento_id
    )
    _recusar_vencimento_passado(instante, agora)
    return previa, instante, origem


def conferencia_dos_titulares(
    *,
    actor,
    edital,
    perfil_id,
    marco_id,
    lista_id,
    alcance_confirmado,
    vencimento=None,
    evento_id="",
    complemento="",
    agora=None,
):
    """O que a confirmação do gesto praticaria agora, **sem praticar nada** (140, FR-4800 a 4811).

    Nada aqui grava: nem convocação, nem comunicação, nem trilha, nem a reserva da chave — por isso
    esta função não abre o `comando_de_comissao`, que reserva a chave antes de qualquer coisa, e a
    chave consumida por uma prévia faria a confirmação repetir um ato que nunca aconteceu.

    **A recusa vem antes do conteúdo** (FR-4811): é a mesma verificação do comando, sem a trava, e
    mostrar o botão de um ato que só pode ser recusado seria um passo que não leva a lugar nenhum.
    Devolve `{"recusa": {codigo, detalhe}}` nesse caso.

    A base de quem pede não é conferida aqui: é a porta da tela, a mesma do gesto (FR-4813), e o
    comando a confere de novo sob a trava.
    """
    agora = agora or timezone.now()
    perfil, marco = identificador(perfil_id), identificador(marco_id)
    lista = identificador(lista_id) if lista_id else None
    leitura = selectors.leitura_do_recorte(
        edital=edital, perfil_id=perfil, marco_id=marco, lista_id=lista, at=agora
    )
    try:
        ensure_processo_accepts_changes(edital.processo)
        previa, instante, origem = verificar_titulares(
            edital=edital,
            perfil_id=perfil,
            marco_id=marco,
            lista_id=lista,
            alcance_confirmado=alcance_confirmado,
            vencimento=vencimento,
            evento_id=evento_id,
            agora=agora,
            leitura=leitura,
        )
    except DomainError as recusa:
        return {"recusa": {"codigo": recusa.code, "detalhe": recusa.detail}}
    forma = previa["forma"]
    canal = vocabulario_do_canal.canal(forma)
    pessoas = previa["pessoas"]
    nome_de = {str(pessoa["id"]): f"{pessoa['protocolo']} — {pessoa['nome']}" for pessoa in pessoas}
    mensagens = []
    if forma == FORMA_POR_MENSAGEM_INDIVIDUAL:
        mensagens = [
            {**grupo, "pessoas": [nome_de[inscricao] for inscricao in grupo["inscricoes"]]}
            for grupo in previa_das_mensagens(
                edital=edital,
                versao=previa["versao"],
                inscricoes=[pessoa["id"] for pessoa in pessoas],
                vencimento=instante,
                agora=agora,
            )
        ]
    return {
        "recusa": None,
        "pessoas": pessoas,
        "forma": forma,
        "publicacao": canal.publicacao,
        "canal": canal,
        "fundamento": fundamento.com_complemento(previa["fundamento"], complemento),
        "mensagens": mensagens,
        "prazo": _prazo_da_conferencia(instante, origem, canal, agora),
        "fora": _fora_do_gesto(previa, leitura),
        "versao": previa["versao"],
    }


def _prazo_da_conferencia(instante, origem, canal, agora):
    """O vencimento por extenso e a origem, ou a falta dele e o que a mensagem dirá (FR-4805)."""
    if instante is None:
        return {
            "informado": False,
            "frase": "Nenhum vencimento informado."
            + (
                ""
                if canal.publicacao
                else " A mensagem dirá que o prazo para atender é o que o Edital publica."
            ),
        }
    lido = apresentar(instante, agora, ZoneInfo(settings.TIME_ZONE))
    return {
        "informado": True,
        "frase": f"Até {lido.dia_da_semana}, {lido.data}, às {lido.hora} — {origem}. "
        f"O prazo corre {canal.a_partir_de}.",
    }


def _fora_do_gesto(previa, leitura):
    """Quem o gesto não alcança, e por quê, em grupos com a razão de cada um (FR-4806).

    Os textos repetem os da tela da convocação: a parada é a mesma frase da `050`, e o gesto que
    alcançaria cada grupo é o que a tela oferece abaixo do lote.
    """
    fora = []
    parada = previa["parada"]
    if parada is not None:
        if parada["motivo"] == alcance.PARADA_REABILITADO:
            razao = (
                "a decisão de recurso a pôs à frente, e ela não está entre as vagas da apuração; "
                "o gesto para nela, e chamá-la é a chamada individual."
            )
        else:
            razao = (
                "é suplente. O gesto convoca só titulares; chamar a vaga que vagou é a chamada "
                "individual, na tela da convocação."
            )
        fora.append({"rotulo": f"{parada['protocolo']} — {parada['nome']}", "razao": razao})
        alcancadas = {str(pessoa["id"]) for pessoa in previa["pessoas"]} | {str(parada["id"])}
        depois = [pessoa for pessoa in leitura["fila"] if str(pessoa["id"]) not in alcancadas]
        if depois:
            fora.append(
                {
                    "rotulo": f"Mais {len(depois)} "
                    + ("pessoa da fila" if len(depois) == 1 else "pessoas da fila"),
                    "razao": "vêm depois na fila, e o gesto para na primeira que não é titular.",
                }
            )
    for pessoa in leitura["regularizaveis"]:
        fora.append(
            {
                "rotulo": f"{pessoa['protocolo']} — {pessoa['nome']}",
                "razao": "Resultado indeferido: chamar para regularizar é outro gesto, na tela da "
                "convocação.",
            }
        )
    return fora


def gesto_ja_concluido(*, actor, chave, operation=GESTO_TITULARES):
    """Se esta pessoa já concluiu o gesto com esta chave (140, D-005, FR-4812; 152, FR-5818).

    `operation` é a do comando: a do lote dos titulares, ou `GESTO_CHAMADA` para a chamada
    individual e a chamada para regularizar.

    **Só leitura.** A confirmação repetida — o duplo clique, a recarga — encontra o recorte já
    convocado, e recompor a conferência a recusaria como "alcance mudou" sobre um ato que aconteceu.
    Com a chave concluída, a confirmação vai ao comando, que devolve o desfecho do primeiro clique e
    não reenvia mensagem nenhuma. A reserva pendente não conta: é a do pedido ainda em curso, e o
    comando a trata.
    """
    from processo_seletivo.auditoria.models import IdempotencyRecord

    if actor is None or not chave:
        return False
    return IdempotencyRecord.objects.filter(
        institution_scope=actor.institution_scope,
        actor_subject=actor.subject,
        operation=operation,
        key=chave,
        response_status__isnull=False,
    ).exists()


# --- A conferência da chamada individual (152, US3) ---------------------------------------------

#: De onde vem a espécie, dito a quem confere (FR-5811).
_ORIGEM_DA_ESPECIE = {
    nomes.VAGA_INICIAL: "a pessoa está entre as vagas da apuração vigente",
    nomes.SUPLENCIA: "a pessoa está na fila depois das vagas da apuração: a vaga é a que vagou",
    nomes.PARA_REGULARIZAR: "a faixa alcançou a pessoa, e o Resultado dela está indeferido",
}


def conferencia_da_chamada(
    *,
    edital,
    perfil_id,
    marco_id,
    lista_id,
    inscricao_id,
    especie="",
    vencimento=None,
    evento_id="",
    complemento="",
    justifica_precedencia=False,
    agora=None,
):
    """O que a chamada individual praticaria agora, **sem praticar nada** (152, FR-5810 a FR-5817).

    O desenho é o de `conferencia_dos_titulares`, com uma pessoa (D-004): nada aqui grava, nem a
    reserva da chave — por isso não abre o `comando_de_comissao` —, e a recusa vem antes do
    conteúdo, pela mesma verificação do comando (`verificar_chamada`), sem a trava. A ordem das
    recusas é a de `convocar_e_comunicar`: o vencimento primeiro, e depois as do comando.

    Devolve `{"recusa": {codigo, detalhe}}` quando o comando recusaria.
    """
    agora = agora or timezone.now()
    perfil, marco = identificador(perfil_id), identificador(marco_id)
    lista = identificador(lista_id) if lista_id else None
    inscricao = identificador(inscricao_id)
    try:
        ensure_processo_accepts_changes(edital.processo)
        versao = effective_version(edital_id=edital.id, at=agora)
        instante, origem = resolver_vencimento(
            versao=versao, vencimento=vencimento, evento_id=evento_id
        )
        _recusar_vencimento_passado(instante, agora)
        verificada = verificar_chamada(
            edital=edital,
            perfil=perfil,
            marco=marco,
            lista=lista,
            inscricao=inscricao,
            especie=especie,
            agora=agora,
            justifica_precedencia=justifica_precedencia,
        )
    except DomainError as recusa:
        return {"recusa": {"codigo": recusa.code, "detalhe": recusa.detail}}
    especie = verificada.especie
    contexto = verificada.contexto
    forma = forma_vigente(verificada.versao, perfil)
    if forma is None:
        # **Antes do botão, e só aqui** (FR-5817). O comando de hoje grava a convocação e o envio
        # a recusa depois, com esta mesma frase: a chamada nasceria sem comunicação possível. A
        # conferência a recusa antes, e como a confirmação só pratica o que ela mostrou, a tela
        # não chega mais ao comando nesse caso. O comando não muda (FR-5846).
        return {
            "recusa": {
                "codigo": nomes.FORMA_DE_COMUNICACAO_NAO_DECLARADA,
                "detalhe": SEM_FORMA_DECLARADA,
            }
        }
    canal = vocabulario_do_canal.canal(forma)
    texto_do_edital, texto_do_recorte = rotulos(
        edital, verificada.versao, perfil_id=perfil, lista_id=lista
    )
    regularizar = especie == nomes.PARA_REGULARIZAR
    ordem = contexto["regularizaveis"] if regularizar else contexto["fila"]
    anteriores = fila.precedencia(ordem, inscricao)
    # Pela chave da inscrição: a fila e o formulário não grafam o identificador do mesmo jeito.
    identificadas = {
        chave_da_inscricao(chave): identidade
        for chave, identidade in selectors.identidades_de({inscricao, *anteriores}).items()
    }
    pessoa = identificadas[chave_da_inscricao(inscricao)]
    mensagens = []
    if forma == FORMA_POR_MENSAGEM_INDIVIDUAL:
        mensagens = [
            {**grupo, "pessoas": [f"{pessoa['protocolo']} — {pessoa['nome']}"]}
            for grupo in previa_das_mensagens(
                edital=edital,
                versao=verificada.versao,
                inscricoes=[inscricao],
                vencimento=instante,
                agora=agora,
            )
        ]
    return {
        "recusa": None,
        "pessoa": {**pessoa, "posicao": len(anteriores) + 1},
        "especie": especie,
        "especie_por_extenso": _ESPECIE_POR_EXTENSO[especie],
        "origem_da_especie": _ORIGEM_DA_ESPECIE[especie],
        # Quem ela passa à frente (FR-5812): só chega aqui com a marca, porque sem ela a
        # verificação recusou.
        "passa_a_frente_de": [identificadas[chave_da_inscricao(i)] for i in anteriores],
        "resultado": _resultado_a_regularizar(edital, contexto, inscricao) if regularizar else None,
        "forma": forma,
        "publicacao": canal.publicacao,
        "canal": canal,
        "fundamento": fundamento.com_complemento(
            fundamento.da_convocacao(
                especie=especie,
                edital=texto_do_edital,
                recorte=texto_do_recorte,
                data_da_apuracao=_data(verificada.apuracao.emitida_em),
            ),
            complemento,
        ),
        "mensagens": mensagens,
        "prazo": _prazo_da_conferencia(instante, origem, canal, agora),
        "versao": verificada.versao,
    }


def _resultado_a_regularizar(edital, contexto, inscricao):
    """O Resultado indeferido que a regularização sucederá (FR-5811), pela leitura do desfecho.

    É a mesma escolha de `desfechar._suceder_o_resultado`: o vigente da Etapa governada pelo corte.
    Sem ele, `None` — e a regularização é recusada no desfecho, como hoje.
    """
    from processo_seletivo.resultados.models import ResultadoEtapa

    etapa = getattr(contexto["corte"], "etapa_governada_id", None)
    if etapa is None:
        return None
    indeferido = (
        ResultadoEtapa.vigentes.filter(inscricao_id=inscricao, edital=edital, etapa_id=etapa)
        .order_by("-consolidado_em")
        .first()
    )
    if indeferido is None or indeferido.consequencia != ResultadoEtapa.Consequencia.ELIMINADA:
        return None
    return {"motivo": indeferido.motivo, "em": indeferido.consolidado_em}


def convocar_titulares(
    *,
    actor,
    processo_id,
    edital_id,
    perfil_id,
    marco_id,
    alcance_confirmado,
    idempotency_key,
    lista_id=None,
    vencimento=None,
    evento_id="",
    complemento="",
    endereco_do_portal="",
):
    """Convoca os titulares da prévia confirmada, e depois comunica cada um (`FR-860`, `FR-871`)."""
    payload = {
        "edital": str(edital_id),
        "perfil": str(perfil_id),
        "marco": str(marco_id),
        "lista": str(lista_id) if lista_id else "",
        "alcance": alcance_confirmado or "",
        "vencimento": vencimento.isoformat() if vencimento else "",
        "evento": str(evento_id or ""),
        "complemento": (complemento or "").strip(),
    }
    correlacao = correlacao_do_gesto(idempotency_key)
    with comando_de_comissao(
        actor=actor,
        processo_id=processo_id,
        operation=GESTO_TITULARES,
        payload=payload,
        idempotency_key=idempotency_key,
    ) as ctx:
        if ctx.repetido:
            declarado = ctx.desfecho_anterior
        else:
            edital = _edital_do_processo(ctx.processo, edital_id)
            perfil, marco = identificador(perfil_id), identificador(marco_id)
            lista = identificador(lista_id) if lista_id else None
            previa, instante, origem = verificar_titulares(
                edital=edital,
                perfil_id=perfil,
                marco_id=marco,
                lista_id=lista,
                alcance_confirmado=alcance_confirmado,
                vencimento=vencimento,
                evento_id=evento_id,
                agora=ctx.now,
            )
            praticadas = convocar_em_sequencia(
                ctx,
                actor=actor,
                edital=edital,
                perfil_id=perfil,
                marco_id=marco,
                lista_id=lista,
                inscricoes=[pessoa["id"] for pessoa in previa["pessoas"]],
                fundamento=fundamento.com_complemento(previa["fundamento"], complemento),
                vencimento=instante,
                correlation_id=correlacao,
                razao_adicional=_razao_do_vencimento(instante, origem),
            )
            declarado = {
                "convocadas": [declarado_da_convocacao(c) for c in praticadas],
                "forma": previa["forma"],
            }
            ctx.concluir_sem_resultado(201, declarado)
    # **Depois do `commit`, e nunca dentro dele** (`D-006`): o SMTP lento não trava o certame, e um
    # `rollback` não desfaz o registro deixando a mensagem enviada.
    return {
        **declarado,
        **comunicar_cada(
            actor=actor,
            processo_id=processo_id,
            convocacoes=[c["id"] for c in declarado["convocadas"]],
            forma=declarado["forma"],
            chave=idempotency_key,
            endereco_do_portal=endereco_do_portal,
        ),
    }


def comunicar_cada(
    *,
    actor,
    processo_id,
    convocacoes,
    forma,
    chave,
    endereco_do_portal="",
    referencia="",
    correlacao=None,
):
    """Uma emissão por convocação, pelo `comunicar` de sempre, com a chave derivada do gesto.

    **A falha de uma não impede as outras** (`FR-873`), e o resultado conta o que aconteceu. Uma
    recusa do `comunicar` — o estado indeterminado, sobretudo — é contada pelo código, e a pessoa
    fica com o prazo não iniciado, que é o que a tela mostra.

    **Por publicação, sem referência, nada é emitido**: o sistema não publica, e o prazo corre de
    onde a lista foi publicada. As convocações esperam o gesto das pendentes (`FR-876`).
    """
    por_publicacao = forma == FORMA_POR_PUBLICACAO
    if por_publicacao and not (referencia or "").strip():
        return {
            "enviadas": 0,
            "falhas": 0,
            "aguardandoPublicacao": len(convocacoes),
            "recusas": {},
            "porPublicacao": True,
            "referencia": "",
        }
    enviadas, falhas, recusas = 0, 0, {}
    for convocacao_id in convocacoes:
        try:
            emitida = comunicar(
                actor=actor,
                processo_id=processo_id,
                convocacao_id=convocacao_id,
                idempotency_key=f"{chave}:comunicar:{convocacao_id}",
                correlation_id=correlacao or correlacao_do_gesto(chave),
                endereco_do_portal=endereco_do_portal,
                referencia_da_publicacao=referencia,
            )
        except DomainError as recusa:
            # **O motivo viaja junto da contagem**: "1 recusa" não diz a quem conduz o que fazer, e
            # a frase da recusa diz — a forma não declarada aponta a Retificação, o estado
            # indeterminado manda conferir o histórico.
            anterior = recusas.get(recusa.code) or {"quantas": 0, "detalhe": recusa.detail}
            recusas[recusa.code] = {**anterior, "quantas": anterior["quantas"] + 1}
            continue
        if emitida.get("resultado") == "ENVIADA":
            enviadas += 1
        else:
            falhas += 1
    # A forma e a referência viajam, para a confirmação dizer *"Publicação registrada"* e não
    # *"comunicações enviadas"* (125, FR-4000).
    return {
        "enviadas": enviadas,
        "falhas": falhas,
        "aguardandoPublicacao": 0,
        "recusas": recusas,
        "porPublicacao": por_publicacao,
        "referencia": (referencia or "").strip() if por_publicacao else "",
    }


# --- A correção da convocação pela tela (120) ---------------------------------------------------

#: O formato do `datetime-local`, que é o que o script da prévia compara (`R-009` da `120`).
FORMATO_DO_CAMPO = "%Y-%m-%dT%H:%M"

_ESPECIES_POR_EXTENSO = dict(Convocacao._meta.get_field("especie").choices)

# **A mensagem individual sai como a da correção** (121, FR-3890, revendo a FR-3844 da `120`): ela
# diz que substitui a anterior, com a data do envio substituído e o prazo que ele informava, e sem
# o motivo. Sem nenhuma mensagem enviada com sucesso na cadeia, não há o que substituir, e sai a
# inicial (D-008 da `121`) — a prévia o diz, para a comissão não esperar o quadro que não virá.
_FRASE_DA_COMUNICACAO = {
    FORMA_POR_MENSAGEM_INDIVIDUAL: "A mensagem da convocação sai de novo, com o prazo válido, "
    "dizendo que corrige a anterior, e sem o motivo. Se nenhuma mensagem desta convocação foi "
    "enviada com sucesso, ela sai como a primeira.",
    FORMA_POR_PUBLICACAO: "A comunicação aguarda a publicação da chamada, como nas demais "
    "convocações deste Perfil.",
    None: "O Perfil publicado não declara como este Edital comunica a convocação: a comunicação "
    "não sai, e o prazo não começa a correr até que a forma seja declarada por Retificação.",
}


def impedimento_da_correcao(leitura):
    """Por que nenhuma convocação do recorte se corrige agora, ou `None` (120, `FR-3839`).

    **As mesmas causas que o comando recusaria**, lidas da leitura que a tela já fez: com elas, a
    tela não oferece formulário que a confirmação recusaria. A ordem sucedida chega aqui como causa
    de obsolescência da apuração, e por isso não precisa de leitura própria.
    """
    if leitura["apuracao"] is None:
        return {"codigo": nomes.APURACAO_AUSENTE, "causas": []}
    if leitura["causasDeObsolescencia"]:
        return {"codigo": nomes.APURACAO_OBSOLETA, "causas": list(leitura["causasDeObsolescencia"])}
    return None


def previa_das_correcoes(leitura, *, versao, perfil_id, fundamentos):
    """O que cada cartão em aberto mostra antes de corrigir, sem consulta (120, `FR-3844`).

    **Em memória, da leitura que a tela já fez** (`FR-3855`): a espécie pela mesma função que o
    comando usa (`R-004`), o fundamento do dicionário que a chamada individual já calculou, e a
    assinatura do que é mostrado (`FR-3857`). Só a chamada em aberto e com vencimento se corrige
    pela tela (`D-004`).
    """
    apuracao = leitura["apuracao"]
    forma = forma_vigente(versao, perfil_id)
    previas = {}
    if apuracao is None:
        return previas
    regularizaveis = [pessoa["id"] for pessoa in leitura["regularizaveis"]]
    for linha in leitura["linhas"]:
        convocacao = linha["convocacao"]
        if linha["desfecho"] is not None or convocacao.vencimento is None:
            continue
        especie = especie_da_posicao.especie_da_sucessora(
            convocacao.inscricao_id,
            ocupando=leitura["ocupando"],
            alcancados=leitura["alcancados"],
            regularizaveis=regularizaveis,
            anterior=convocacao,
        )
        previas[str(convocacao.id)] = {
            "especie": especie,
            "especiePorExtenso": _ESPECIES_POR_EXTENSO.get(especie, especie),
            "especieDifere": especie != convocacao.especie,
            "fundamento": fundamentos.get(especie, ""),
            # **O fundamento muda quando a corrigida cita outra apuração ou outra versão**
            # (`D-006`): comparar os textos esbarraria no complemento, que a corrigida guarda junto.
            "fundamentoDifere": convocacao.apuracao_id != apuracao.id
            or convocacao.versao_id != getattr(versao, "id", None),
            "forma": forma,
            "fraseDaComunicacao": _FRASE_DA_COMUNICACAO.get(forma, _FRASE_DA_COMUNICACAO[None]),
            "venceu": linha["estado"] == nomes.CONVOCADO_VENCIMENTO_DECORRIDO,
            "vencimentoAtual": timezone.localtime(convocacao.vencimento).strftime(FORMATO_DO_CAMPO),
            "assinatura": alcance.assinatura_da_correcao(
                convocacao_id=convocacao.id,
                apuracao_id=apuracao.id,
                versao_id=getattr(versao, "id", None),
                forma=forma,
                especie=especie,
            ),
        }
    return previas


def efeito_do_vencimento(anterior, novo):
    """Estendido, antecipado ou mantido — o que a correção fez com o prazo (120, `FR-3849`)."""
    if anterior is None or novo is None:
        return ""
    antes = timezone.localtime(anterior).strftime(FORMATO_DO_CAMPO)
    depois = timezone.localtime(novo).strftime(FORMATO_DO_CAMPO)
    if depois > antes:
        return "estendido"
    if depois < antes:
        return "antecipado"
    return "mantido"


# --- A chamada individual, que continua para o suplente e para a exceção -----------------------


def fundamentos_por_especie(*, edital, perfil_id, lista_id, apuracao, at=None):
    """O fundamento derivado de cada espécie, para a tela mostrar antes da chamada (`FR-870`)."""
    if apuracao is None:
        return {}
    versao = effective_version(edital_id=edital.id, at=at)
    texto_do_edital, texto_do_recorte = rotulos(
        edital, versao, perfil_id=perfil_id, lista_id=lista_id
    )
    return {
        especie: fundamento.da_convocacao(
            especie=especie,
            edital=texto_do_edital,
            recorte=texto_do_recorte,
            data_da_apuracao=_data(apuracao.emitida_em),
        )
        for especie in nomes.ESPECIES_DE_CONVOCACAO
    }


def convocar_e_comunicar(
    *,
    actor,
    processo_id,
    edital_id,
    perfil_id,
    marco_id,
    inscricao_id,
    idempotency_key,
    correlation_id,
    lista_id=None,
    especie="",
    vencimento=None,
    evento_id="",
    complemento="",
    motivo="",
    justifica_precedencia=False,
    endereco_do_portal="",
    correcao=None,
):
    """A chamada individual da `050`: espécie e fundamento derivados, e a comunicação no mesmo ato.

    **O fundamento é derivado dentro do comando**, depois de a espécie ser conhecida e sob a trava:
    derivá-lo antes, fora dela, gravaria o texto de uma apuração que outra pessoa pode ter sucedido
    no meio do caminho.
    """
    # **Autorizar antes de trabalhar** (Princípio III), como o `comunicar` faz: sem isto, quem não
    # tem base saberia, pela recusa, se o Edital e o Evento existem.
    exigir_base_de_comissao(actor=actor, processo_id=processo_id)
    edital = _edital_do_processo(processo_id, edital_id)
    versao = effective_version(edital_id=edital.id)
    instante, origem = resolver_vencimento(
        versao=versao, vencimento=vencimento, evento_id=evento_id
    )
    if correcao is not None and instante is None:
        # **Na correção, vazio não quer dizer "o Edital não publica prazo"** (120, `D-004`): a tela
        # só oferece a correção em chamada com vencimento, e é o prazo que ela existe para corrigir.
        raise DomainError(
            nomes.VENCIMENTO_DA_CORRECAO_OBRIGATORIO,
            "Informe o vencimento novo — a data e a hora, ou o fim de um Evento do Cronograma.",
            422,
            campo="vencimento",
        )
    _recusar_vencimento_passado(instante, timezone.now())
    texto_do_edital, texto_do_recorte = rotulos(
        edital, versao, perfil_id=identificador(perfil_id), lista_id=lista_id
    )

    def derivar(especie_derivada, apuracao):
        return fundamento.com_complemento(
            fundamento.da_convocacao(
                especie=especie_derivada,
                edital=texto_do_edital,
                recorte=texto_do_recorte,
                data_da_apuracao=_data(apuracao.emitida_em),
            ),
            complemento,
        )

    declarado = convocar(
        actor=actor,
        processo_id=processo_id,
        edital_id=edital_id,
        perfil_id=perfil_id,
        marco_id=marco_id,
        lista_id=lista_id,
        inscricao_id=inscricao_id,
        especie=especie,
        fundamento="",
        fundamento_por_especie=derivar,
        vencimento=instante,
        motivo=motivo,
        justifica_precedencia=justifica_precedencia,
        idempotency_key=idempotency_key,
        correlation_id=correlation_id,
        razao_adicional=_razao_do_vencimento(instante, origem),
        correcao=correcao,
    )
    forma = forma_vigente(versao, identificador(perfil_id))
    return {
        "convocacao": declarado,
        **comunicar_cada(
            actor=actor,
            processo_id=processo_id,
            convocacoes=[declarado["id"]],
            forma=forma,
            chave=idempotency_key,
            endereco_do_portal=endereco_do_portal,
            correlacao=correlation_id,
        ),
    }


# --- O não atendimento dos vencidos (`DP-16`, opção B) -------------------------------------------


def previa_dos_vencidos(*, edital, perfil_id, marco_id, lista_id=None, at=None, leitura=None):
    """As convocações vencidas sem desfecho, as que ficam de fora e por quê (`FR-878`)."""
    agora = at or timezone.now()
    leitura = leitura or selectors.leitura_do_recorte(
        edital=edital, perfil_id=perfil_id, marco_id=marco_id, lista_id=lista_id, at=agora
    )
    particao = alcance.vencidas(leitura["linhas"])
    versao = effective_version(edital_id=edital.id, at=agora)
    texto_do_edital, texto_do_recorte = rotulos(
        edital, versao, perfil_id=perfil_id, lista_id=lista_id
    )
    return {
        "linhas": list(particao.alcancadas),
        "fora": particao.fora,
        "fundamento": fundamento.do_nao_atendimento(
            edital=texto_do_edital, recorte=texto_do_recorte
        ),
        "assinatura": alcance.assinatura(
            gesto="vencidos",
            apuracao_id=None,
            versao_id=None,
            forma=None,
            identidades=[linha["convocacao"].id for linha in particao.alcancadas],
        ),
    }


def registrar_nao_atendimento_dos_vencidos(
    *,
    actor,
    processo_id,
    edital_id,
    perfil_id,
    marco_id,
    alcance_confirmado,
    idempotency_key,
    lista_id=None,
    complemento="",
):
    """Um desfecho de não atendimento por convocação vencida, num ato só (`FR-877`, `FR-880`).

    **Pelo mesmo `registrar` do desfecho individual** (`D-013`): mesmas recusas, mesmo efeito,
    mesma linha. E, no fim, **uma** tentativa de apuração seguinte, que conta todos os efeitos que
    o gesto escreveu (`D-005`).
    """
    payload = {
        "edital": str(edital_id),
        "perfil": str(perfil_id),
        "marco": str(marco_id),
        "lista": str(lista_id) if lista_id else "",
        "alcance": alcance_confirmado or "",
        "complemento": (complemento or "").strip(),
    }
    correlacao = correlacao_do_gesto(idempotency_key)
    with comando_de_comissao(
        actor=actor,
        processo_id=processo_id,
        operation=GESTO_VENCIDOS,
        payload=payload,
        idempotency_key=idempotency_key,
    ) as ctx:
        if ctx.repetido:
            return ctx.desfecho_anterior
        edital = _edital_do_processo(ctx.processo, edital_id)
        previa = previa_dos_vencidos(
            edital=edital,
            perfil_id=identificador(perfil_id),
            marco_id=identificador(marco_id),
            lista_id=identificador(lista_id) if lista_id else None,
            at=ctx.now,
        )
        _conferir(previa, alcance_confirmado)
        if not previa["linhas"]:
            raise DomainError(
                nomes.NENHUMA_CONVOCACAO_VENCIDA,
                "Não há convocação com o vencimento decorrido e sem desfecho neste recorte.",
                409,
            )
        texto = fundamento.com_complemento(previa["fundamento"], complemento)
        desfechos = []
        for linha in previa["linhas"]:
            desfecho = registrar(
                ctx,
                linha["convocacao"],
                actor=actor,
                especie=nomes.NAO_ATENDIMENTO,
                fundamento=texto,
            )
            auditar_desfecho(ctx, desfecho, actor, correlacao)
            desfechos.append(desfecho)
        seguinte = apuracao_seguinte(
            ctx,
            previa["linhas"][0]["convocacao"],
            actor=actor,
            quantos=len(desfechos),
            correlation_id=correlacao,
        )
        declarado = {"desfechos": [declarado_do_desfecho(d) for d in desfechos], **seguinte}
        ctx.concluir_sem_resultado(201, declarado)
        return declarado


# --- As comunicações pendentes -----------------------------------------------------------------


def previa_das_pendentes(*, edital, perfil_id, marco_id, lista_id=None, at=None, leitura=None):
    """As convocações sem desfecho e sem envio com sucesso, e a forma que elas citam (`FR-874`)."""
    leitura = leitura or selectors.leitura_do_recorte(
        edital=edital, perfil_id=perfil_id, marco_id=marco_id, lista_id=lista_id, at=at
    )
    candidatas = list(alcance.pendentes(leitura["linhas"]).alcancadas)
    # **Emissão em estado indeterminado não é pendente** (spec, *Edge Cases*). A guarda do
    # `comunicar` vale para a mesma chave, e este gesto usa uma chave nova por pessoa: sem este
    # filtro, a reserva que ficou aberta depois de a mensagem sair — ou a que está saindo agora,
    # noutra requisição — seria atropelada, e a pessoa receberia a mesma convocação duas vezes.
    indeterminadas = _com_emissao_indeterminada(linha["convocacao"].id for linha in candidatas)
    linhas = [linha for linha in candidatas if linha["convocacao"].id not in indeterminadas]
    # **A forma é a da versão que cada convocação citou** — a mesma leitura de `forma_declarada` —,
    # mas as versões são lidas por conjunto: uma consulta por pessoa seria o crescimento que a
    # `FR-888` proíbe, e o recorte cita, quase sempre, uma versão só.
    versoes = VersaoConsolidada.objects.in_bulk({linha["convocacao"].versao_id for linha in linhas})
    formas = {forma_vigente(versoes[linha["convocacao"].versao_id], perfil_id) for linha in linhas}
    # **Publicação vence**, e não a ordem alfabética: com uma Retificação no meio, o recorte pode
    # ter pendentes das duas formas, e a referência de onde se publicou precisa ser pedida sempre
    # que houver uma por publicação. A individual ignora a referência, de modo que pedi-la não a
    # atrapalha.
    forma = next(
        (f for f in (FORMA_POR_PUBLICACAO, FORMA_POR_MENSAGEM_INDIVIDUAL) if f in formas), None
    )
    return {
        "linhas": linhas,
        "indeterminadas": len(indeterminadas),
        "forma": forma,
        "porPublicacao": forma == FORMA_POR_PUBLICACAO,
        "assinatura": alcance.assinatura(
            gesto="pendentes",
            apuracao_id=None,
            versao_id=None,
            forma=forma,
            identidades=[linha["convocacao"].id for linha in linhas],
        ),
    }


def _com_emissao_indeterminada(convocacoes):
    """As convocações cuja emissão reservou a chave e nunca registrou o que aconteceu.

    **Por conteúdo, e não por chave**: a reserva guarda o resumo da carga que o `comunicar` usa, e a
    carga é a identidade da convocação. Qualquer reserva aberta sobre ela — de quem quer que seja —
    significa que uma mensagem pode ter saído sem registro.
    """
    from processo_seletivo.auditoria.models import IdempotencyRecord
    from processo_seletivo.convocacao.application.comunicar import ATO as ATO_DE_COMUNICAR
    from processo_seletivo.shared.canonical import canonical_sha256

    por_resumo = {canonical_sha256({"convocacao": str(c)}): c for c in convocacoes}
    if not por_resumo:
        return set()
    abertas = IdempotencyRecord.objects.filter(
        operation=ATO_DE_COMUNICAR,
        response_status__isnull=True,
        request_hash__in=list(por_resumo),
    ).values_list("request_hash", flat=True)
    return {por_resumo[resumo] for resumo in abertas}


def emitir_pendentes(
    *,
    actor,
    processo_id,
    edital_id,
    perfil_id,
    marco_id,
    alcance_confirmado,
    idempotency_key,
    lista_id=None,
    referencia_da_publicacao="",
    endereco_do_portal="",
):
    """Emite, pessoa a pessoa, as comunicações pendentes do recorte (`FR-874`, `FR-876`, `D-012`).

    **Autorizar antes de trabalhar** (Princípio III), como o `comunicar` faz. O gesto não abre
    transação própria: cada emissão tem a sua, com a chave reservada antes do envio — é isso que
    impede duas mensagens na caixa da mesma pessoa.
    """
    exigir_base_de_comissao(actor=actor, processo_id=processo_id)
    edital = _edital_do_processo(processo_id, edital_id)
    previa = previa_das_pendentes(
        edital=edital,
        perfil_id=identificador(perfil_id),
        marco_id=identificador(marco_id),
        lista_id=identificador(lista_id) if lista_id else None,
    )
    _conferir(previa, alcance_confirmado)
    if not previa["linhas"]:
        raise DomainError(
            nomes.NENHUMA_COMUNICACAO_PENDENTE,
            # A frase do canal (125, FR-4001).
            vocabulario_do_canal.canal(
                FORMA_POR_PUBLICACAO if previa["porPublicacao"] else None
            ).recusa_sem_pendente,
            409,
        )
    referencia = (referencia_da_publicacao or "").strip()
    if previa["porPublicacao"] and not referencia:
        raise DomainError(
            nomes.REFERENCIA_DA_PUBLICACAO_OBRIGATORIA,
            "Este Edital comunica a convocação por publicação: declare onde e quando a lista foi "
            "publicada, porque o prazo corre a partir disso.",
            422,
            campo="referencia_da_publicacao",
        )
    return comunicar_cada(
        actor=actor,
        processo_id=processo_id,
        convocacoes=[str(linha["convocacao"].id) for linha in previa["linhas"]],
        forma=previa["forma"] or FORMA_POR_MENSAGEM_INDIVIDUAL,
        chave=idempotency_key,
        endereco_do_portal=endereco_do_portal,
        referencia=referencia,
    )


__all__ = [
    "comunicar_cada",
    "convocar_e_comunicar",
    "convocar_titulares",
    "emitir_pendentes",
    "eventos_do_cronograma",
    "forma_vigente",
    "fundamentos_por_especie",
    "previa_das_pendentes",
    "previa_dos_titulares",
    "previa_dos_vencidos",
    "registrar_nao_atendimento_dos_vencidos",
    "resolver_vencimento",
]
