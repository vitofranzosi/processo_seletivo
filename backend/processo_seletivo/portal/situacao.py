"""A situação da inscrição: o que o topo do acompanhamento diz, e de que ato o diz (063).

**Situação → Por quê → O que fazer**, nesta ordem e sempre as três (FR-1166). A pergunta com que a
pessoa chega é "em que pé eu estou?", e a tela respondia com documentos: o resultado de cada Etapa,
depois um bloco por publicação, e só no meio deles a convocação. Quem estava em duas listas lia
"8º lugar" e "2º lugar" sob o mesmo título e não sabia qual valia.

**Uma função pura, e o template só apresenta** (D-001). A precedência é a regra desta feature, e
regra em `{% if %}` não se testa caso a caso. Nada aqui consulta o banco nem lê o relógio: a view
passa o que já leu, e é por isso que a tela não ganhou consulta nenhuma (D-007).

**O que a função NÃO recebe é a outra metade da regra** (FR-1169, FR-1171). Não há argumento para o
corte da `014` nem para a apuração de ocupação da `016`:

- a apuração guarda contagens, e quem ocupa a vaga sai de cálculo — nenhum ato registra a pessoa
  (L-1). Só a convocação tira alguém de "Aguardando chamada";
- o corte é ato interno da gestão, que nenhuma publicação divulga (L-2).

Sem os dois na assinatura, nenhuma linha desta função consegue deduzir "dentro das vagas" da
posição, nem por descuido. É a prova estrutural; a varredura de vocabulário é a textual.

**As frases moram aqui, e só aqui** (D-005). Rótulos, frases de consequência, de canal e de cadastro
reserva são constantes deste módulo; o template não escreve nenhuma. A prova de que nenhuma outra
frase de consequência existe (SC-453) é ler estes dicionários.
"""

from dataclasses import dataclass, field

from django.urls import reverse
from django.utils import formats, timezone

from processo_seletivo.convocacao.domain import nomes as convocacao_nomes
from processo_seletivo.portal.leitura import _chave_da_lista
from processo_seletivo.publicacoes.domain.vocabulario_da_regra import (
    FORMA_DE_CONVOCACAO_POR_EXTENSO,
)

# --- O conjunto fechado, em ordem de precedência (D-002) ----------------------------------------
CONVOCADO = "CONVOCADO"
ELIMINADO = "ELIMINADO"
AGUARDANDO_CHAMADA = "AGUARDANDO_CHAMADA"
AGUARDANDO_DEFINITIVO = "AGUARDANDO_DEFINITIVO"
NAO_CLASSIFICADO = "NAO_CLASSIFICADO"
INSCRICAO_ENVIADA = "INSCRICAO_ENVIADA"

ROTULOS = {
    CONVOCADO: "Convocado",
    ELIMINADO: "Eliminado",
    # **Provisório, e dito como provisório** (FR-1170). "Classificado" a pessoa lê como aprovado; o
    # que o sistema sabe é que há classificação e que ninguém ainda a chamou.
    AGUARDANDO_CHAMADA: "Aguardando chamada",
    AGUARDANDO_DEFINITIVO: "Aguardando resultado definitivo",
    NAO_CLASSIFICADO: "Não classificado",
    INSCRICAO_ENVIADA: "Inscrição enviada",
}

# **O rótulo de cada desfecho em linguagem simples, e nenhum promovido a matrícula** (FR-1172). O
# *Aceite* é da convocação: inclui a pessoa na contagem de ocupantes, e nenhum ato depois dele
# confirma matrícula ou contratação (L-3). O sexto diz "matrícula" porque é o nome que a `019` dá ao
# desfecho, e não escolha desta tela por tipo de certame.
DESFECHOS = {
    convocacao_nomes.ACEITE: "Vaga aceita",
    convocacao_nomes.REGULARIZACAO: "Regularização registrada",
    convocacao_nomes.INDEFERIMENTO: "Indeferido na convocação",
    convocacao_nomes.DESISTENCIA_EXPRESSA: "Desistência registrada",
    convocacao_nomes.NAO_ATENDIMENTO: "Convocação não atendida",
    convocacao_nomes.INERCIA: "Matrícula cancelada por inércia",
    convocacao_nomes.RECLASSIFICACAO: "Reclassificado",
}

PROVISORIAS = {CONVOCADO, AGUARDANDO_CHAMADA, AGUARDANDO_DEFINITIVO, INSCRICAO_ENVIADA}

# --- As frases de consequência: estas duas, e nenhuma outra (FR-1177) --------------------------
# **Nenhuma promete perda.** A primeira não diz que haverá chamada; a segunda não diz que a pessoa
# perde a convocação, porque o não atendimento só existe quando alguém o registra (FR-274) — e por
# isso ela só aparece no estado em que é verdadeira: comunicação enviada, vencimento registrado,
# prazo correndo.
NOVAS_CHAMADAS = "Novas chamadas, se houver, serão publicadas conforme o Edital."
NAO_ATENDIMENTO_PODE_SER_REGISTRADO = (
    "Se você não atender no prazo, a comissão poderá registrar o não atendimento desta convocação."
)
CONSEQUENCIAS = (NOVAS_CHAMADAS, NAO_ATENDIMENTO_PODE_SER_REGISTRADO)

NADA_POR_ENQUANTO = "Nada por enquanto."
RESULTADO_CONFORME_O_EDITAL = "Nada por enquanto. O resultado será publicado conforme o Edital."
MAIS_DE_UMA_LISTA = "Você concorre em mais de uma lista, e cada lista tem a sua classificação."
PRELIMINAR_PODE_MUDAR = "Este resultado é preliminar e pode mudar no resultado definitivo."
SIGA_AS_INSTRUCOES = "Siga as instruções do Edital para esta convocação."
PREENCHER_REQUERIMENTO = "Preencher o Requerimento de Matrícula."
REQUERIMENTO_ENVIADO = "Seu Requerimento de Matrícula foi enviado."
PRAZO_NAO_INICIADO = (
    "A comunicação desta convocação ainda não foi enviada. O seu prazo ainda não começou a correr."
)


@dataclass(frozen=True)
class Linha:
    """Uma linha do porquê: o ato, dito pela lista e pela etapa a que pertence (FR-1173)."""

    texto: str
    link: str = ""
    link_rotulo: str = ""


@dataclass(frozen=True)
class Acao:
    """O que fazer. `principal` nunca falta: "Nada por enquanto." é resposta (FR-1178)."""

    principal: str
    link: str = ""
    link_rotulo: str = ""
    prazo: object = None
    aviso_de_prazo: str = ""
    consequencia: str = ""
    canal: str = ""
    reserva: str = ""
    recurso: tuple = ()


@dataclass(frozen=True)
class Situacao:
    codigo: str
    rotulo: str
    provisoria: bool
    porque: tuple = field(default_factory=tuple)
    o_que_fazer: Acao = None


def ordenar_cartoes(cartoes, perfil):
    """Os cartões na ordem do certame: o marco, e dentro dele a ordem das listas do Perfil (D-006).

    A ordem das listas é a da página pública do Edital (`062`): ampla concorrência primeiro, depois
    as Modalidades na ordem em que o Perfil as declara.
    """
    ordem_das_listas = {
        str(modalidade.get("id")): i
        for i, modalidade in enumerate((perfil or {}).get("competitionModalities") or [])
    }
    return sorted(
        cartoes,
        key=lambda cartao: (
            cartao["marco_codigo"],
            cartao["marco"],
            _chave_da_lista(cartao, ordem_das_listas),
        ),
    )


def situacao_da_inscricao(
    *,
    inscricao,
    perfil,
    cartoes,
    resultados_das_etapas,
    convocacao,
    desfecho,
    estado,
    requerimento,
    recorriveis,
    recursos,
):
    """A situação, pela primeira regra da precedência que se aplica (D-002).

    1. desfecho da convocação vigente;
    2. convocação vigente sem desfecho;
    3. Resultado de Etapa visível que eliminou;
    4. classificação em ao menos uma publicação definitiva;
    5. classificação só em publicações preliminares;
    6. sem posição em todas as listas;
    7. nada divulgado.

    Cada degrau é um ato mais recente no certame que o seguinte. A convocação vem antes da
    eliminação porque a convocação *para regularizar* existe justamente depois de um indeferimento.

    **Não recebe relógio.** O que depende do instante — o prazo da convocação ter começado ou
    terminado — chega já derivado em `estado`, pela mesma função que a tela da convocação usa
    (`estado_de`, da `019`): duas contas do mesmo prazo discordariam na fronteira.
    """
    recurso = _recurso(recorriveis)
    em_analise = _recursos_em_analise(recursos)

    if convocacao is not None and desfecho is not None:
        return _situacao(
            f"DESFECHO_{desfecho.especie}",
            DESFECHOS.get(desfecho.especie, desfecho.get_especie_display()),
            porque=(
                Linha(
                    f"Registrado em {_data(desfecho.registrado_em)}: {desfecho.fundamento.strip()}"
                ),
                _linha_da_convocacao(convocacao, perfil, cartoes),
                *em_analise,
            ),
            acao=_acao_do_desfecho(inscricao, requerimento, recurso),
        )

    if convocacao is not None:
        return _situacao(
            CONVOCADO,
            porque=(_linha_da_convocacao(convocacao, perfil, cartoes), *em_analise),
            acao=_acao_da_convocacao(inscricao, convocacao, estado, requerimento, recurso),
        )

    eliminacoes = [etapa for etapa in resultados_das_etapas if not etapa["habilitada"]]
    if eliminacoes:
        return _situacao(
            ELIMINADO,
            porque=(
                *(
                    Linha(
                        f"Você foi eliminado na etapa {etapa['etapa']}."
                        + (f" {etapa['motivo']}" if etapa.get("motivo") else "")
                    )
                    for etapa in eliminacoes
                ),
                *em_analise,
            ),
            acao=Acao(NADA_POR_ENQUANTO, recurso=recurso),
        )

    classificadas = [cartao for cartao in cartoes if cartao["classificada"]]
    if classificadas:
        definitiva = any(_definitiva(cartao) for cartao in classificadas)
        porque = [_linha_do_cartao(cartao) for cartao in cartoes]
        if len({str(cartao["lista_id"]) for cartao in cartoes}) > 1:
            porque.append(Linha(MAIS_DE_UMA_LISTA))
        if not definitiva:
            porque.append(Linha(PRELIMINAR_PODE_MUDAR))
            return _situacao(
                AGUARDANDO_DEFINITIVO,
                porque=(*porque, *em_analise),
                acao=Acao(NADA_POR_ENQUANTO, recurso=recurso),
            )
        return _situacao(
            AGUARDANDO_CHAMADA,
            porque=(*porque, *em_analise),
            acao=Acao(
                NADA_POR_ENQUANTO,
                consequencia=NOVAS_CHAMADAS,
                canal=frase_do_canal(perfil),
                reserva=frase_da_reserva(perfil),
                recurso=recurso,
            ),
        )

    if cartoes:
        return _situacao(
            NAO_CLASSIFICADO,
            porque=(*(_linha_do_cartao(cartao) for cartao in cartoes), *em_analise),
            acao=Acao(NADA_POR_ENQUANTO, recurso=recurso),
        )

    enviada = (
        (Linha(f"Inscrição enviada em {_data_e_hora(inscricao.submitted_at)}."),)
        if inscricao.submitted_at
        else ()
    )
    return _situacao(
        INSCRICAO_ENVIADA,
        porque=(*enviada, *em_analise),
        acao=Acao(RESULTADO_CONFORME_O_EDITAL, recurso=recurso),
    )


def frase_do_canal(perfil):
    """A forma de convocação que o Perfil declara, ou nada (FR-1179).

    **A mesma frase do PDF do Edital** (D-004), para que o Edital e a tela não digam a mesma coisa
    de dois jeitos. Sem declaração, a tela não nomeia canal — prometer e-mail a quem será convocado
    por publicação faria a pessoa esperar uma mensagem que não vem.
    """
    frase = FORMA_DE_CONVOCACAO_POR_EXTENSO.get((perfil or {}).get("callForm"))
    return f"As convocações deste Perfil são feitas {frase}." if frase else ""


def frase_da_reserva(perfil):
    """O cadastro reserva **do Edital**, nunca a pertença da pessoa a ele (FR-1180, L-5).

    Que o Perfil prevê cadastro reserva de até nove pessoas é fato publicado. Que a pessoa está nele
    seria conta sobre a posição — 3 vagas, 9 de reserva, você é o 8º —, e a conta é exatamente o que
    esta tela não faz.
    """
    tipo = (perfil or {}).get("reserveType")
    limite = (perfil or {}).get("reserveLimit")
    if tipo == "LIMITED" and limite:
        pessoas = "pessoa" if limite == 1 else "pessoas"
        return f"O Edital prevê cadastro reserva de até {limite} {pessoas} para este Perfil."
    if tipo == "UNLIMITED":
        return "O Edital prevê cadastro reserva para este Perfil, sem limite de pessoas."
    if tipo == "LIMITED":
        return "O Edital prevê cadastro reserva para este Perfil."
    return ""


def nome_da_lista_da_convocacao(convocacao, perfil, cartoes):
    """O nome da lista pela qual a pessoa foi chamada (D-003).

    A convocação não guarda nome: sem lista é a ampla concorrência; com lista, a Modalidade do
    Perfil no conteúdo vigente; e, se uma Retificação a tirou, o nome que o cartão da mesma lista
    congelou.
    """
    if convocacao.lista_id is None:
        return "Ampla concorrência"
    for modalidade in (perfil or {}).get("competitionModalities") or []:
        if str(modalidade.get("id")) == str(convocacao.lista_id):
            return modalidade.get("name") or ""
    for cartao in cartoes:
        if str(cartao["lista_id"]) == str(convocacao.lista_id):
            return cartao["lista"]
    return ""


def _situacao(codigo, rotulo=None, *, porque, acao):
    return Situacao(
        codigo=codigo,
        rotulo=rotulo or ROTULOS[codigo],
        provisoria=codigo in PROVISORIAS,
        porque=tuple(porque),
        o_que_fazer=acao,
    )


def _acao_do_desfecho(inscricao, requerimento, recurso):
    """Nada a fazer — e o que a pessoa mandou continua a um clique.

    **Enviado é estado terminal de leitura** (`FR-406` da `029`): desfechada a chamada, o
    Requerimento enviado continua consultável, como a `059` já mostrava. Os outros estados do
    requerimento não aparecem, porque a política já não oferece o preenchimento (`FR-1098`).
    """
    if requerimento == "conferir":
        return Acao(
            NADA_POR_ENQUANTO,
            link=reverse("portal:requerimento", args=[inscricao.id]),
            link_rotulo="Conferir o Requerimento de Matrícula enviado",
            recurso=recurso,
        )
    return Acao(NADA_POR_ENQUANTO, recurso=recurso)


def _acao_da_convocacao(inscricao, convocacao, estado, requerimento, recurso):
    """Ação, prazo e consequência da convocação aberta (FR-1175 a FR-1177).

    A ação vem do Edital pela política da `029`: o Requerimento só é chamado quando ela diz que
    cabe. Sem ele, a instrução neutra — e a tela não diz matrícula nem contratação.

    **A consequência só existe com o prazo correndo.** Sem comunicação enviada com sucesso o prazo
    não começou (a `019` ignora o envio com falha), e dizer o que acontece "se você não atender no
    prazo" seria falar de um prazo que não existe. Com o vencimento decorrido, a tela diz a data e
    que o resultado ainda não foi registrado — e a situação continua "Convocado", porque nenhum
    relógio tem competência para desfechar (FR-274).
    """
    if requerimento == "preencher":
        principal, link, link_rotulo = (
            PREENCHER_REQUERIMENTO,
            reverse("portal:requerimento", args=[inscricao.id]),
            "Preencher Requerimento de Matrícula",
        )
    elif requerimento == "conferir":
        principal, link, link_rotulo = (
            REQUERIMENTO_ENVIADO,
            reverse("portal:requerimento", args=[inscricao.id]),
            "Conferir o Requerimento de Matrícula enviado",
        )
    else:
        principal, link, link_rotulo = (
            SIGA_AS_INSTRUCOES,
            reverse("portal:convocacao", args=[inscricao.id]),
            "Ver convocação",
        )

    prazo, aviso, consequencia = None, "", ""
    if estado == convocacao_nomes.CONVOCADO_PRAZO_NAO_INICIADO:
        aviso = PRAZO_NAO_INICIADO
    elif estado == convocacao_nomes.CONVOCADO_VENCIMENTO_DECORRIDO:
        aviso = (
            f"O prazo desta convocação terminou em {_data_e_hora(convocacao.vencimento)}. "
            "O resultado da convocação ainda não foi registrado. "
            "Se você atendeu e não consta, fale com o atendimento."
        )
    elif convocacao.vencimento is not None:
        prazo = convocacao.vencimento
        consequencia = NAO_ATENDIMENTO_PODE_SER_REGISTRADO

    return Acao(
        principal,
        link=link,
        link_rotulo=link_rotulo,
        prazo=prazo,
        aviso_de_prazo=aviso,
        consequencia=consequencia,
        recurso=recurso,
    )


def _linha_da_convocacao(convocacao, perfil, cartoes):
    lista = nome_da_lista_da_convocacao(convocacao, perfil, cartoes)
    pela_lista = f" pela lista {lista}" if lista else ""
    return Linha(
        f"Convocação {convocacao.get_especie_display().lower()}{pela_lista}, "
        f"{convocacao.chamada}ª chamada, registrada em {_data(convocacao.criado_em)}."
    )


def _linha_do_cartao(cartao):
    """Cada lista com a sua posição oficial, sem escolher a melhor nem reordenar (FR-1174)."""
    onde = (
        f"no {cartao['natureza_rotulo'].lower()} de {cartao['marco']}, "
        f"publicado em {_data(cartao['publicacao'].publicado_em)}"
    )
    if cartao["classificada"]:
        compartilhada = " (posição compartilhada)" if cartao["compartilhada"] else ""
        return Linha(f"{cartao['lista']}: {cartao['posicao']}º lugar{compartilhada} {onde}.")
    motivo = f" {cartao['motivo']}" if cartao.get("motivo") else ""
    return Linha(f"{cartao['lista']}: sem posição {onde}.{motivo}")


def _definitiva(cartao):
    from processo_seletivo.divulgacao.models import Natureza

    return cartao["publicacao"].natureza == Natureza.DEFINITIVA


def _recurso(recorriveis):
    return tuple(
        {"rotulo": alvo["rotulo"], "fecha_em": alvo["fecha_em"]}
        for alvo in recorriveis
        if alvo.get("fecha_em")
    )


def _recursos_em_analise(recursos):
    """Recurso pendente não muda a situação — só ato muda —, e o porquê diz que ele existe."""
    from processo_seletivo.recursos.application.selectors import (
        AGUARDANDO_ADMISSIBILIDADE,
        AGUARDANDO_JULGAMENTO,
    )

    return [
        Linha(
            f"Seu recurso {peca['protocolo']} está em análise: "
            f"{peca['situacao_rotulo'][0].lower()}{peca['situacao_rotulo'][1:]}.",
            link=reverse("portal:recurso", args=[peca["recurso"].id]),
            link_rotulo=f"Ver o recurso {peca['protocolo']}",
        )
        for peca in recursos
        if peca["situacao"] in (AGUARDANDO_ADMISSIBILIDADE, AGUARDANDO_JULGAMENTO)
    ]


def _data(instante):
    return formats.date_format(timezone.localtime(instante), "d/m/Y")


HORA = "H\\hi"


def _data_e_hora(instante):
    local = timezone.localtime(instante)
    return f"{formats.date_format(local, 'd/m/Y')} às {formats.date_format(local, HORA)}"


__all__ = [
    "CONSEQUENCIAS",
    "DESFECHOS",
    "NOVAS_CHAMADAS",
    "ROTULOS",
    "Acao",
    "Linha",
    "Situacao",
    "frase_da_reserva",
    "frase_do_canal",
    "nome_da_lista_da_convocacao",
    "ordenar_cartoes",
    "situacao_da_inscricao",
]
