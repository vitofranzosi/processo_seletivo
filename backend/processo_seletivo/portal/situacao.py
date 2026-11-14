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
from processo_seletivo.editais.domain import cadastro_de_reserva
from processo_seletivo.portal import desfecho as frases_do_desfecho
from processo_seletivo.portal import obrigacoes as obrigacoes_da_convocacao
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
# Os degraus da publicação das inscrições (148, FR-5434). **Em linguagem simples, e de propósito**:
# o topo não usa o vocabulário do deferimento (UX-058) nem o da homologação sem explicar (UX-156).
# O nome oficial do ato está na página do ato, a um link; aqui a pessoa lê o que ele significa
# para ela (UX-463).
INSCRICAO_RECEBIDA = "INSCRICAO_RECEBIDA"
INSCRICAO_ACEITA_PRELIMINAR = "INSCRICAO_ACEITA_PRELIMINAR"
INSCRICAO_NAO_ACEITA_PRELIMINAR = "INSCRICAO_NAO_ACEITA_PRELIMINAR"
INSCRICAO_ACEITA = "INSCRICAO_ACEITA"
INSCRICAO_NAO_ACEITA = "INSCRICAO_NAO_ACEITA"

ROTULOS = {
    CONVOCADO: "Convocado",
    ELIMINADO: "Eliminado",
    # **Provisório, e dito como provisório** (FR-1170). "Classificado" a pessoa lê como aprovado; o
    # que o sistema sabe é que há classificação e que ninguém ainda a chamou.
    AGUARDANDO_CHAMADA: "Aguardando chamada",
    AGUARDANDO_DEFINITIVO: "Aguardando resultado definitivo",
    NAO_CLASSIFICADO: "Não classificado",
    INSCRICAO_ENVIADA: "Inscrição enviada",
    INSCRICAO_RECEBIDA: "Inscrição recebida",
    INSCRICAO_ACEITA_PRELIMINAR: "Inscrição aceita (resultado preliminar)",
    INSCRICAO_NAO_ACEITA_PRELIMINAR: "Inscrição não aceita (resultado preliminar)",
    INSCRICAO_ACEITA: "Inscrição aceita",
    INSCRICAO_NAO_ACEITA: "Inscrição não aceita",
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

PROVISORIAS = {
    CONVOCADO,
    AGUARDANDO_CHAMADA,
    AGUARDANDO_DEFINITIVO,
    INSCRICAO_ENVIADA,
    INSCRICAO_RECEBIDA,
    INSCRICAO_ACEITA_PRELIMINAR,
    INSCRICAO_NAO_ACEITA_PRELIMINAR,
}

# O que o ato diz da inscrição, já traduzido pela view (148): a função pura não lê o vocabulário
# do ato, que é o do deferimento — e a varredura do requerimento (UX-058) lê este arquivo.
RECEBIDA_NO_ATO = "RECEBIDA"
ACEITA_NO_ATO = "ACEITA"
NAO_ACEITA_NO_ATO = "NAO_ACEITA"

# As frases dos degraus das inscrições (148). Uma vez, para a tela e para os testes.
RECEBIDA_NAO_E_ACEITA = (
    "Recebida quer dizer que a inscrição chegou dentro do prazo, e não que já foi aceita."
)
PRELIMINAR_DA_ANALISE_PODE_MUDAR = (
    "Este resultado é preliminar e pode mudar até a relação final das inscrições aceitas."
)
VER_O_ATO = "Ver a relação publicada"

# --- As frases de consequência: estas duas, e nenhuma outra (FR-1177) --------------------------
# **Nenhuma promete perda.** A primeira não diz que haverá chamada; a segunda não diz que a pessoa
# perde a convocação, porque o não atendimento só existe quando alguém o registra (FR-274) — e por
# isso ela só aparece no estado em que é verdadeira: comunicação enviada, vencimento registrado,
# prazo correndo **e providência pendente** (154, FR-6209): a quem já fez tudo, ela só assustava.
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
# **Uma frase só para o prazo que não começou** (118, FR-3749), a mesma nas duas telas.
PRAZO_NAO_INICIADO = obrigacoes_da_convocacao.PRAZO_NAO_INICIADO

# Os rótulos dos links que só navegam (118, FR-3730). **Nenhum começa por "Enviar"** (D-004): o
# clique leva à convocação, e não envia nada; o rótulo diz o que se vê ao chegar.
VER_O_QUE_ENVIOU = "Ver o que você enviou nesta convocação"
VER_COMO_FICOU = "Ver como ficou a convocação"
VER_E_CORRIGIR = "Ver e corrigir os documentos pendentes"
VER_O_QUE_FALTA = "Ver o que falta na convocação"
VER_A_CONVOCACAO = "Ver a convocação"
CONFERIR_O_ENVIADO = "Conferir o Requerimento de Matrícula enviado"


@dataclass(frozen=True)
class Linha:
    """Uma linha do porquê: o ato, dito pela lista e pela etapa a que pertence (FR-1173)."""

    texto: str
    link: str = ""
    link_rotulo: str = ""
    # O fundamento do ato, que o template recolhe sob a frase simples (156, FR-6400): só a linha
    # do desfecho o tem.
    fundamento: str = ""
    rotulo_do_fundamento: str = ""


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
    # **Abaixo da ação principal, e nunca no lugar dela** (118, FR-3731): o Requerimento enviado,
    # com documento na chamada.
    secundaria: str = ""
    secundaria_link: str = ""
    secundaria_rotulo: str = ""
    # A frase de conclusão e a do opcional, depois de "Nada por enquanto." (FR-3728).
    conclusao: str = ""
    opcional: str = ""
    # A linha estritamente informativa do Requerimento não enviado, sem link (FR-3732, D-019).
    informativo: str = ""
    # O que o registro do resultado não é (FR-3750).
    aceite: str = ""


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
    politica_do_requerimento=None,
    obrigacoes=None,
    inscricao_publicada=None,
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

    **As obrigações da convocação chegam prontas** (118): a projeção de `portal/obrigacoes.py`,
    quando a chamada pede documento, e a `Disponibilidade` do Requerimento, de onde sai a linha
    informativa da chamada sem documento. As duas são puras, e a view já as leu.
    """
    recurso = _recurso(recorriveis, cartoes)
    em_analise = _recursos_em_analise(recursos)

    if convocacao is not None and desfecho is not None:
        return _situacao(
            f"DESFECHO_{desfecho.especie}",
            DESFECHOS.get(desfecho.especie, desfecho.get_especie_display()),
            porque=(
                # **Duas camadas** (FR-1172, revista pela `156`): a frase simples da espécie, e o
                # fundamento gravado recolhido sob ela, palavra por palavra (FR-6400, FR-6401).
                Linha(
                    frases_do_desfecho.do_desfecho(desfecho, convocacao),
                    fundamento=frases_do_desfecho.fundamento_do_registro(desfecho),
                    rotulo_do_fundamento=frases_do_desfecho.FUNDAMENTO_DO_REGISTRO,
                ),
                _linha_da_convocacao(convocacao, perfil, cartoes),
                *em_analise,
            ),
            acao=_acao_do_desfecho(
                inscricao, requerimento, recurso, desfecho, politica_do_requerimento, obrigacoes
            ),
        )

    if convocacao is not None:
        return _situacao(
            CONVOCADO,
            porque=(_linha_da_convocacao(convocacao, perfil, cartoes), *em_analise),
            acao=(
                _acao_das_obrigacoes(inscricao, convocacao, obrigacoes, recurso)
                if obrigacoes is not None
                else _acao_da_convocacao(
                    inscricao, convocacao, estado, requerimento, recurso, politica_do_requerimento
                )
            ),
        )

    # **A retirada da reserva não é eliminação** (164, FR-7024, UX-742): quem a recebeu continua na
    # ampla, e o degrau dele é o da classificação. A linha que a explica entra no "porquê" de todo
    # degrau abaixo deste, junto dos recursos em análise.
    eliminacoes = [
        etapa
        for etapa in resultados_das_etapas
        if not etapa["habilitada"] and not etapa.get("retirada")
    ]
    em_analise = [
        *(_linha_da_retirada(etapa) for etapa in resultados_das_etapas if etapa.get("retirada")),
        *em_analise,
    ]
    nao_aceita = _nao_aceita_na_analise(eliminacoes, inscricao_publicada, em_analise, recurso)
    if nao_aceita is not None:
        return nao_aceita
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
    publicada = _publicada(inscricao_publicada, enviada, em_analise, recurso)
    if publicada is not None:
        return publicada
    return _situacao(
        INSCRICAO_ENVIADA,
        porque=(*enviada, *em_analise),
        acao=Acao(RESULTADO_CONFORME_O_EDITAL, recurso=recurso),
    )


def _nao_aceita_na_analise(eliminacoes, publicada, em_analise, recurso):
    """A inscrição que a análise das inscrições não aceitou — antes do degrau "Eliminado" (148).

    Só quando a eliminação é **da Etapa que o ato publicou**: eliminação numa Etapa posterior
    continua sendo "Eliminado", com a frase de sempre. O motivo detalhado é o parecer de quem
    analisou, que a seção da Etapa, logo abaixo, mostra enquanto o prazo corre (036); o topo não
    repete o motivo da consolidação, que só diria o rótulo da decisão.
    """
    if not publicada or not publicada.get("etapa_id"):
        return None
    da_analise = [e for e in eliminacoes if str(e.get("etapa_id")) == publicada["etapa_id"]]
    if not da_analise:
        return None
    preliminar = publicada["natureza"] == "PRELIMINAR"
    quando = _data(publicada["publicado_em"])
    if preliminar:
        texto = (
            f"Sua inscrição não foi aceita na análise das inscrições ({da_analise[0]['etapa']}), "
            f"no resultado preliminar publicado em {quando}."
        )
    else:
        texto = (
            f"Sua inscrição não está na relação final das inscrições aceitas, publicada em "
            f"{quando}. A análise das inscrições ({da_analise[0]['etapa']}) não a aceitou."
        )
    porque = [
        Linha(texto, publicada.get("link", ""), VER_O_ATO if publicada.get("link") else ""),
        Linha("O que faltou está na fundamentação da etapa, logo abaixo."),
    ]
    if preliminar:
        porque.append(Linha(PRELIMINAR_DA_ANALISE_PODE_MUDAR))
    return _situacao(
        INSCRICAO_NAO_ACEITA_PRELIMINAR if preliminar else INSCRICAO_NAO_ACEITA,
        porque=(*porque, *em_analise),
        acao=Acao(NADA_POR_ENQUANTO, recurso=recurso),
    )


def _publicada(publicada, enviada, em_analise, recurso):
    """Recebida, aceita no preliminar ou aceita em definitivo — quando nada depois disso existe."""
    if not publicada:
        return None
    quando = _data(publicada["publicado_em"])
    link = publicada.get("link", "")
    rotulo = VER_O_ATO if link else ""
    if publicada["situacao"] == RECEBIDA_NO_ATO:
        return _situacao(
            INSCRICAO_RECEBIDA,
            porque=(
                *enviada,
                Linha(
                    f"Sua inscrição consta na relação de inscrições recebidas, publicada em "
                    f"{quando}.",
                    link,
                    rotulo,
                ),
                Linha(RECEBIDA_NAO_E_ACEITA),
                *em_analise,
            ),
            acao=Acao(RESULTADO_CONFORME_O_EDITAL, recurso=recurso),
        )
    if publicada["situacao"] != ACEITA_NO_ATO:
        return None
    if publicada["natureza"] == "PRELIMINAR":
        return _situacao(
            INSCRICAO_ACEITA_PRELIMINAR,
            porque=(
                Linha(
                    f"Sua inscrição foi aceita na análise das inscrições, no resultado preliminar "
                    f"publicado em {quando}.",
                    link,
                    rotulo,
                ),
                Linha(PRELIMINAR_DA_ANALISE_PODE_MUDAR),
                *em_analise,
            ),
            acao=Acao(RESULTADO_CONFORME_O_EDITAL, recurso=recurso),
        )
    return _situacao(
        INSCRICAO_ACEITA,
        porque=(
            Linha(
                f"Sua inscrição está na relação final das inscrições aceitas, publicada em "
                f"{quando}. Isso ainda não é a classificação: a seleção continua conforme o "
                "Edital.",
                link,
                rotulo,
            ),
            *em_analise,
        ),
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
    # O número é o da regra única (162, FR-6945): o publicado no legado, o do corte nos demais.
    cadastro = cadastro_de_reserva.do_perfil(perfil or {})
    limite = cadastro.numero_mostrado()
    if tipo == "LIMITED" and limite:
        pessoas = "pessoa" if limite == 1 else "pessoas"
        if cadastro.com_modalidade and not cadastro.legado:
            return (
                f"O Edital prevê cadastro reserva de até {limite} {pessoas} em cada lista de "
                "concorrência deste Perfil."
            )
        return f"O Edital prevê cadastro reserva de até {limite} {pessoas} para este Perfil."
    if tipo == "LIMITED" and cadastro.por_lista and not cadastro.legado:
        listas = cadastro_de_reserva.frase_das_listas(
            cadastro.por_lista, unidade=lambda n: "pessoa" if n == 1 else "pessoas"
        )
        return f"O Edital prevê cadastro reserva de até {listas} deste Perfil."
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


def frase_do_aceite(desfecho):
    """O que vem depois da frase simples, no aceite e na regularização.

    **Os dois desfechos que incluem na ocupação, em toda convocação** (FR-3750, D-013 da `118`): o
    aceite sem documento é o mesmo ato. *"Este registro não é matrícula, bolsa nem contrato"* — a
    frase que a User Story 2 da `115` prometia — está desde a `156` na frase simples da espécie
    (FR-6406), no porquê; aqui fica só o que vem depois dela.
    """
    if desfecho is not None and desfecho.especie in convocacao_nomes.DESFECHOS_QUE_INCLUEM:
        return obrigacoes_da_convocacao.ACEITE
    return ""


def _acao_do_desfecho(inscricao, requerimento, recurso, desfecho, politica, obrigacoes):
    """Nada a fazer — e o que a pessoa mandou continua a um clique.

    **Enviado é estado terminal de leitura** (`FR-406` da `029`): desfechada a chamada, o
    Requerimento enviado continua consultável, como a `059` já mostrava. Os outros estados do
    requerimento não aparecem, porque a política já não oferece o preenchimento (`FR-1098`).

    **Com documento, o link leva à convocação** (118, FR-3730, linha 1), onde está o que a pessoa
    enviou; o Requerimento enviado desce para a linha secundária. Sem documento, como antes, mais a
    linha informativa do Requerimento pedido e não enviado (D-019).
    """
    conferir = reverse("portal:requerimento", args=[inscricao.id])
    aceite = frase_do_aceite(desfecho)
    if obrigacoes is not None:
        return Acao(
            NADA_POR_ENQUANTO,
            link=reverse("portal:convocacao", args=[inscricao.id]),
            link_rotulo=VER_O_QUE_ENVIOU,
            recurso=recurso,
            aceite=aceite,
            **_secundaria(obrigacoes, conferir),
        )
    if requerimento == "conferir":
        return Acao(
            NADA_POR_ENQUANTO,
            link=conferir,
            link_rotulo=CONFERIR_O_ENVIADO,
            recurso=recurso,
            aceite=aceite,
        )
    return Acao(
        NADA_POR_ENQUANTO,
        recurso=recurso,
        aceite=aceite,
        informativo=obrigacoes_da_convocacao.linha_informativa_do_requerimento(
            politica, desfecho=desfecho
        ),
    )


def _secundaria(obrigacoes, conferir):
    """O Requerimento enviado como linha secundária, com documento na chamada (FR-3731)."""
    if not obrigacoes.requerimento_enviado:
        return {}
    return {
        "secundaria": obrigacoes_da_convocacao.REQUERIMENTO_ENVIADO,
        "secundaria_link": conferir,
        "secundaria_rotulo": CONFERIR_O_ENVIADO,
    }


def _acao_das_obrigacoes(inscricao, convocacao, obrigacoes, recurso):
    """A ação da chamada que pede documento: a tabela da FR-3730 da `118`.

    **O link principal leva sempre à convocação**, mesmo com o Requerimento enviado ou a preencher
    (D-008): é lá que estão todas as obrigações, e o Requerimento enviado como ação principal era o
    que escondia os documentos sem envio (F1).

    O prazo e a consequência continuam os da `063` (FR-1176, FR-1177), mas só com a chamada aberta:
    encerrada, a frase do fechamento já diz o que houve, e prazo ou consequência ali convidariam a
    um ato que não existe mais.
    """
    destino = reverse("portal:convocacao", args=[inscricao.id])
    secundaria = _secundaria(obrigacoes, reverse("portal:requerimento", args=[inscricao.id]))
    if obrigacoes.encerrada:
        return Acao(
            obrigacoes.frase_de_estado,
            link=destino,
            link_rotulo=VER_COMO_FICOU,
            recurso=recurso,
            **secundaria,
        )
    prazo, aviso, consequencia = None, "", ""
    if obrigacoes.prazo_nao_iniciado:
        aviso = " ".join(obrigacoes.frase_do_prazo)
    elif convocacao.vencimento is not None:
        prazo = convocacao.vencimento
        # **Só com providência pendente** (154, FR-6209): quem já fez tudo o que a chamada pede não
        # tem o que deixar de atender, e a advertência assustava justamente essa pessoa (achado 20
        # do estudo da jornada final). O prazo fica (FR-6208).
        if obrigacoes.providencia_pendente:
            consequencia = NAO_ATENDIMENTO_PODE_SER_REGISTRADO
    if obrigacoes.tarefas:
        rotulo = VER_E_CORRIGIR if obrigacoes.totais["a_corrigir"] else VER_O_QUE_FALTA
    else:
        rotulo = VER_A_CONVOCACAO
    return Acao(
        obrigacoes.frase_de_estado,
        link=destino,
        link_rotulo=rotulo,
        prazo=prazo,
        aviso_de_prazo=aviso,
        consequencia=consequencia,
        recurso=recurso,
        conclusao=obrigacoes.frase_de_conclusao,
        opcional=obrigacoes.frase_do_opcional,
        **secundaria,
    )


def _acao_da_convocacao(inscricao, convocacao, estado, requerimento, recurso, politica=None):
    """Ação, prazo e consequência da convocação aberta sem documento (FR-1175 a FR-1177).

    A ação vem do Edital pela política da `029`: o Requerimento só é chamado quando ela diz que
    cabe. Sem ele, a instrução neutra — e a tela não diz matrícula nem contratação.

    **A consequência só existe com o prazo correndo.** Sem comunicação enviada com sucesso o prazo
    não começou (a `019` ignora o envio com falha), e dizer o que acontece "se você não atender no
    prazo" seria falar de um prazo que não existe. Com o vencimento decorrido, a tela diz a data e
    que o resultado ainda não foi registrado — e a situação continua "Convocado", porque nenhum
    relógio tem competência para desfechar (FR-274).

    **Exatamente a de hoje** (118, FR-3732, D-017): mudam só o formato do prazo e a frase do
    vencido, que são comuns a todas as telas, e entra a linha informativa do Requerimento pedido e
    não enviado, quando a política já não admite o preenchimento (D-019).
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
            CONFERIR_O_ENVIADO,
        )
    else:
        principal, link, link_rotulo = (
            SIGA_AS_INSTRUCOES,
            reverse("portal:convocacao", args=[inscricao.id]),
            "Ver convocação",
        )

    prazo, aviso, consequencia = None, "", ""
    if estado == convocacao_nomes.CONVOCADO_PRAZO_NAO_INICIADO:
        from processo_seletivo.convocacao.application.selectors import canal_de

        # A frase do canal da convocação (125, FR-3999).
        aviso = canal_de(convocacao).prazo_nao_iniciado
    elif estado == convocacao_nomes.CONVOCADO_VENCIMENTO_DECORRIDO:
        # O núcleo único do vencido (FR-3748), **e nunca com o Processo em estado final**, em que
        # ninguém registra resultado (D-015): ali a linha informativa já diz que o envio encerrou.
        if not (politica is not None and politica.fechado_pelo_processo):
            aviso = " ".join(
                (
                    obrigacoes_da_convocacao.frase_do_prazo_decorrido(convocacao.vencimento),
                    obrigacoes_da_convocacao.frase_do_atendimento(""),
                )
            )
    elif convocacao.vencimento is not None and not (
        politica is not None and politica.fechado_pelo_processo
    ):
        # Com o Processo em estado final, ninguém registra não atendimento (D-015, D-020): o prazo
        # e a consequência prometeriam um ato que não existe mais, e a linha informativa já diz que
        # o envio encerrou.
        prazo = convocacao.vencimento
        # **Só o Requerimento pedido nesta chamada, e já enviado, a tira** (154, FR-6201): sem nada
        # pedido pelo portal, o sistema não verifica o cumprimento, e a tela fica a de hoje.
        if obrigacoes_da_convocacao.providencia_pendente_sem_documento(politica):
            consequencia = NAO_ATENDIMENTO_PODE_SER_REGISTRADO

    return Acao(
        principal,
        link=link,
        link_rotulo=link_rotulo,
        prazo=prazo,
        aviso_de_prazo=aviso,
        consequencia=consequencia,
        recurso=recurso,
        informativo=obrigacoes_da_convocacao.linha_informativa_do_requerimento(
            politica, desfecho=None
        ),
    )


def _linha_da_convocacao(convocacao, perfil, cartoes):
    lista = nome_da_lista_da_convocacao(convocacao, perfil, cartoes)
    pela_lista = f" pela lista {lista}" if lista else ""
    return Linha(
        f"Convocação {convocacao.get_especie_display().lower()}{pela_lista}, "
        f"{convocacao.chamada}ª chamada, registrada em {_data(convocacao.criado_em)}."
    )


def natureza_do_cartao(cartao):
    """A natureza gravada no cabeçalho, ou a da coluna da publicação quando o cabeçalho não a traz.

    O cabeçalho congelado é a fonte, porque é o que a publicação disse; mas `situacoes_do_candidato`
    devolve vazio quando a chave falta, e a frase sairia "no  de Classificação final". A coluna
    `natureza` existe em toda publicação, e o rótulo dela é o mesmo que `compor` congela.
    """
    return cartao["natureza_rotulo"] or cartao["publicacao"].get_natureza_display()


def _linha_da_retirada(etapa):
    """A reserva perdida, dita pelo que acontece com a pessoa, e nunca como eliminação (UX-742).

    O motivo gravado já traz o rótulo do desfecho e o nome da reserva (FR-7008); a frase de cima diz
    o essencial antes dele, para quem não lê até o fim.
    """
    return Linha(
        f"Na etapa {etapa['etapa']}, você deixou de concorrer pela reserva de vagas e continua "
        "concorrendo pela ampla concorrência."
        + (f" {etapa['motivo'][:1].upper()}{etapa['motivo'][1:]}." if etapa.get("motivo") else "")
    )


def _linha_do_cartao(cartao):
    """Cada lista com a sua posição oficial, sem escolher a melhor nem reordenar (FR-1174)."""
    onde = (
        f"no {natureza_do_cartao(cartao).lower()} de {cartao['marco']}, "
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


def _recurso(recorriveis, cartoes):
    """O que se pode contestar agora, cada objeto nomeado de modo que não se confunda com o vizinho.

    **A publicação é nomeada pela lista e pelo marco.** `objetos_recorriveis` (`018`) a rotula só
    pelo marco, e quem está na ampla e numa reserva lia duas linhas idênticas — "Se você discordar
    de Classificação final" — sem saber qual era qual, o mesmo defeito dos cartões que esta
    feature corrige. A lista sai do cartão da mesma publicação; o Resultado de Etapa já é nomeado
    pela Etapa.
    """
    lista_da_publicacao = {
        str(cartao["publicacao"].id): cartao["lista"] for cartao in cartoes if cartao.get("lista")
    }
    return tuple(
        {
            "rotulo": (
                f"{lista_da_publicacao[str(alvo['id'])]} — {alvo['rotulo']}"
                if alvo.get("tipo") == "publicacao" and str(alvo["id"]) in lista_da_publicacao
                else alvo["rotulo"]
            ),
            "fecha_em": alvo["fecha_em"],
        }
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
    "natureza_do_cartao",
    "nome_da_lista_da_convocacao",
    "ordenar_cartoes",
    "situacao_da_inscricao",
]
