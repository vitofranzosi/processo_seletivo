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

from django.utils import timezone
from django.utils.dateparse import parse_datetime

from processo_seletivo.classificacao.domain.universo import por_identidade
from processo_seletivo.comissoes.application import comando_de_comissao, exigir_base_de_comissao
from processo_seletivo.comissoes.application.comissao import identificador
from processo_seletivo.convocacao.application import selectors
from processo_seletivo.convocacao.application.comunicar import comunicar
from processo_seletivo.convocacao.application.convocar import (
    convocar,
    convocar_em_sequencia,
    declarado_da_convocacao,
)
from processo_seletivo.convocacao.application.desfechar import (
    apuracao_seguinte,
    auditar_desfecho,
    declarado_do_desfecho,
    registrar,
)
from processo_seletivo.convocacao.domain import alcance, fundamento, nomes, prazo
from processo_seletivo.editais.domain.recortes import rotulo_do_recorte
from processo_seletivo.processos.models import Edital
from processo_seletivo.publicacoes.application.selectors import effective_version
from processo_seletivo.publicacoes.domain.vocabulario_da_regra import (
    FORMA_POR_MENSAGEM_INDIVIDUAL,
    FORMA_POR_PUBLICACAO,
    FORMAS_DE_CONVOCACAO,
)
from processo_seletivo.publicacoes.models import VersaoConsolidada
from processo_seletivo.shared.api.problems import DomainError

GESTO_TITULARES = "convocacao:convocar_titulares"
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


def _edital_do_processo(processo_id, edital_id):
    edital = Edital.objects.filter(processo_id=processo_id, id=identificador(edital_id)).first()
    if edital is None:
        raise DomainError("edital_nao_encontrado", "Edital não encontrado.", 404)
    return edital


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
            edital = _edital_do_processo(ctx.processo.id, edital_id)
            perfil, marco = identificador(perfil_id), identificador(marco_id)
            lista = identificador(lista_id) if lista_id else None
            previa = previa_dos_titulares(
                edital=edital, perfil_id=perfil, marco_id=marco, lista_id=lista, at=ctx.now
            )
            if previa["impedimento"]:
                raise DomainError(
                    previa["impedimento"]["codigo"], previa["impedimento"]["detalhe"], 409
                )
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
            _recusar_vencimento_passado(instante, ctx.now)
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
    *, actor, processo_id, convocacoes, forma, chave, endereco_do_portal="", referencia=""
):
    """Uma emissão por convocação, pelo `comunicar` de sempre, com a chave derivada do gesto.

    **A falha de uma não impede as outras** (`FR-873`), e o resultado conta o que aconteceu. Uma
    recusa do `comunicar` — o estado indeterminado, sobretudo — é contada pelo código, e a pessoa
    fica com o prazo não iniciado, que é o que a tela mostra.

    **Por publicação, sem referência, nada é emitido**: o sistema não publica, e o prazo corre de
    onde a lista foi publicada. As convocações esperam o gesto das pendentes (`FR-876`).
    """
    if forma == FORMA_POR_PUBLICACAO and not (referencia or "").strip():
        return {"enviadas": 0, "falhas": 0, "aguardandoPublicacao": len(convocacoes), "recusas": {}}
    enviadas, falhas, recusas = 0, 0, {}
    for convocacao_id in convocacoes:
        try:
            emitida = comunicar(
                actor=actor,
                processo_id=processo_id,
                convocacao_id=convocacao_id,
                idempotency_key=f"{chave}:comunicar:{convocacao_id}",
                correlation_id=correlacao_do_gesto(chave),
                endereco_do_portal=endereco_do_portal,
                referencia_da_publicacao=referencia,
            )
        except DomainError as recusa:
            recusas[recusa.code] = recusas.get(recusa.code, 0) + 1
            continue
        if emitida.get("resultado") == "ENVIADA":
            enviadas += 1
        else:
            falhas += 1
    return {"enviadas": enviadas, "falhas": falhas, "aguardandoPublicacao": 0, "recusas": recusas}


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
):
    """A chamada individual da `050`: espécie e fundamento derivados, e a comunicação no mesmo ato.

    **O fundamento é derivado dentro do comando**, depois de a espécie ser conhecida e sob a trava:
    derivá-lo antes, fora dela, gravaria o texto de uma apuração que outra pessoa pode ter sucedido
    no meio do caminho.
    """
    edital = _edital_do_processo(processo_id, edital_id)
    versao = effective_version(edital_id=edital.id)
    instante, origem = resolver_vencimento(
        versao=versao, vencimento=vencimento, evento_id=evento_id
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
        edital = _edital_do_processo(ctx.processo.id, edital_id)
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
    linhas = list(alcance.pendentes(leitura["linhas"]).alcancadas)
    # **A forma é a da versão que cada convocação citou** — a mesma leitura de `forma_declarada` —,
    # mas as versões são lidas por conjunto: uma consulta por pessoa seria o crescimento que a
    # `FR-888` proíbe, e o recorte cita, quase sempre, uma versão só.
    versoes = VersaoConsolidada.objects.in_bulk({linha["convocacao"].versao_id for linha in linhas})
    formas = {forma_vigente(versoes[linha["convocacao"].versao_id], perfil_id) for linha in linhas}
    forma = next((f for f in sorted(formas, key=str) if f is not None), None)
    return {
        "linhas": linhas,
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
            "Não há convocação sem comunicação enviada neste recorte.",
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
