"""O andamento da seleção depois da publicação — o que está feito, o que falta e de quem é (127).

**Por que este módulo existe.** Até a publicação o GPS orienta bem: o bastão diz quem age e por que
não dá ainda. Depois dela o cartão "O que fazer agora" era o mesmo num Edital que espera a semente e
num em convocação (`J-01` do estudo de 06/11), e o que falta estava espalhado por marco e por
recorte em sete telas. O domínio já sabia quase tudo; faltava um lugar que lesse junto.

**Leitura, e não motor** (FR-4050). Nada aqui autoriza, pratica ou guarda coisa alguma. Cada fato é
a resposta de uma função que **já** decide uma tela de ato — `previa.recortes_do_marco` no sorteio,
`conducao_do_marco.indicador_do_marco` na ordem, no corte, na apuração e na publicação, o panorama e
o resumo da distribuição nas Etapas, a `leitura_do_recorte` e as três prévias na convocação, a
aferição da publicabilidade no definitivo, e os objetos de trabalho da `104` para recurso,
Retificação e avaliação. Uma segunda regra aqui divergiria da tela na primeira mudança: é a lição da
`103` e da `104`. Quando a `126` mudar uma célula da condução do marco, a mudança chega aqui.

**Duas camadas** (R-001). As funções `situacao_*` são puras: recebem os fatos já lidos e devolvem a
`Celula`. É o que deixa as sete situações serem provadas em todas as famílias de classificação —
inclusive as duas que o banco de demonstração não tem (S3, habilitação antes do sorteio; P3, vários
marcos no Perfil) — sem montar um certame por caso. A leitura (`do_edital`) é a única que toca o
banco.

**Sem próximo passo único** (FR-4051). O que sai é um conjunto: cada ponto da jornada em cada lista
tem a sua situação, e as providências são as células em aberto. Quem escolhe o que mostrar primeiro
é a apresentação, por regra fixa (`providencias.py`).

**As sete situações são de apresentação** (D-007). Nenhuma é coluna nem estado do domínio, e a
ausência de ato nunca é pendência: sem ato vigente, a célula é *Depois*, *Aguarda*, *Impedido*, *Não
se aplica* ou *Pendente*, pela regra do ato.
"""

import logging
from dataclasses import dataclass, field, replace
from datetime import datetime

from django.urls import reverse
from django.utils import timezone

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------------------------
# As situações, a expectativa e os responsáveis (data-model)
# ---------------------------------------------------------------------------------------------

FEITO, OBSOLETO, PENDENTE = "feito", "obsoleto", "pendente"
AGUARDA, IMPEDIDO, DEPOIS, NAO_SE_APLICA = "aguarda", "impedido", "depois", "nao_se_aplica"
SITUACOES = (FEITO, OBSOLETO, PENDENTE, AGUARDA, IMPEDIDO, DEPOIS, NAO_SE_APLICA)

#: Palavra e sinal (UX-230). A cor acompanha na folha; nunca é a única pista (WCAG 1.4.1).
ROTULOS = {
    FEITO: "Feito",
    OBSOLETO: "Obsoleto",
    PENDENTE: "Pendente",
    AGUARDA: "Aguarda",
    IMPEDIDO: "Impedido",
    DEPOIS: "Depois",
    NAO_SE_APLICA: "Não se aplica",
}
SINAIS = {
    FEITO: "✓",
    OBSOLETO: "↺",
    PENDENTE: "●",
    AGUARDA: "◷",
    IMPEDIDO: "⊘",
    DEPOIS: "·",
    NAO_SE_APLICA: "—",
}
#: O que entra no nível 1: o que alguém precisa fazer, ou o que espera o mundo (FR-4080).
EM_ABERTO = frozenset({OBSOLETO, PENDENTE, AGUARDA, IMPEDIDO})
#: O que alguém pode praticar agora — é o que a coerência com a tela prende (SC-1230).
A_PRATICAR = frozenset({OBSOLETO, PENDENTE})

ESPERADA, CONDICIONAL, SEM_EFEITO = "esperada", "condicional", "sem_efeito"

#: Os papéis que respondem pelos atos depois da publicação (contrato de derivação, §3.2). O texto é
#: o que a tela escreve antes do ato da providência de outro papel ("Quem publica resultado: …").
CONDUZ, PUBLICA, AVALIA = "conduz", "publica", "avalia"
JULGA, RETIFICA, CONFERE, RETIFICACAO = "julga", "retifica", "confere", "retificacao"
PAPEIS = {
    CONDUZ: "Quem conduz a seleção",
    PUBLICA: "Quem publica resultado",
    AVALIA: "Os avaliadores alocados",
    JULGA: "Quem julga recursos",
    CONFERE: "Quem conduz ou confere documentos",
    RETIFICA: "Quem elabora Retificações",
    RETIFICACAO: "Quem age na Retificação",
}
#: A ordem dos grupos de outros papéis no nível 1 (FR-4082).
ORDEM_DOS_PAPEIS = (CONDUZ, AVALIA, CONFERE, PUBLICA, JULGA, RETIFICACAO, RETIFICA)

#: As naturezas, para o agrupamento (D-016) e para o teste de coerência (SC-1230).
RELACAO, SEMENTE, SORTEIO, ORDEM = "relacao", "semente", "sorteio", "ordem"
CORTE, APURACAO, RESULTADO, CONVOCACAO = "corte", "apuracao", "resultado", "convocacao"
DISTRIBUIR, AVALIAR, CONSOLIDAR, REAVALIAR = "distribuir", "avaliar", "consolidar", "reavaliar"
CONFERIR, RECURSO = "conferir", "recurso"
ETAPA = "etapa"

#: O que a Etapa "sem efeito" diz no nível 1 (D-010). Não manda fazer nada.
SEM_EFEITO_NO_GPS = "está declarada no Edital, e nenhum ato do GPS depende do resultado dela"


@dataclass(frozen=True)
class Celula:
    """A situação de um ponto da jornada numa lista — e, em aberto, uma providência."""

    situacao: str
    natureza: str = ""
    ato: str = ""
    responsavel: str = ""
    nota: str = ""
    razao: str = ""
    url: str = ""
    condicional: bool = False
    ate: datetime | None = None
    contagem: int | None = None
    #: Quem resolve o impedimento, quando não é quem pratica o ato (quase sempre a Retificação).
    quem_resolve: str = ""

    @property
    def rotulo(self):
        return ROTULOS[self.situacao]

    @property
    def sinal(self):
        return SINAIS[self.situacao]

    @property
    def em_aberto(self):
        return self.situacao in EM_ABERTO


def _c(situacao, **campos):
    return Celula(situacao, **campos)


# ---------------------------------------------------------------------------------------------
# A expectativa das Etapas (FR-4060, D-012) — pura
# ---------------------------------------------------------------------------------------------


def expectativa_das_etapas(conteudo, perfis=None):
    """`{etapa_id: ESPERADA | SEM_EFEITO}` para as Etapas do conteúdo, pelos marcos de `perfis`.

    **Pergunta a quem já sabe** (D-012): `quem_exige_o_resultado` é o que impede publicar Edital
    com Etapa que nunca consolidaria, pelas três ligações de um marco — enumerada (e não porta),
    governada pelo corte, de habilitação do sorteio. A ela se somam:

    - a Etapa que o **desempate** lê sem o marco a enumerar (114): a ordem a lê, e dizer "nada
      depende dela" seria falso — o complemento de generalidade deixava o ponto "a verificar";
    - a enumerada por marco **de pontuação** que consolida, porta inclusive: a eliminatória
      desfavorável tira a pessoa da ordem, e emitir antes dela é emitir o que envelhece;
    - a **progressão**: a Etapa que consolida e vem antes, pela ordem, de uma esperada filtra quem
      segue nela (`prontidao`, regras 1 e 2) — calculada por ponto fixo, porque a cadeia anda para
      trás.

    `perfis` restringe aos marcos de alguns Perfis (a célula do nível 2 é por Perfil); sem ele, vale
    o Edital inteiro, que é o que o nível 1 cobra.
    """
    from processo_seletivo.classificacao.domain.desempate import etapas_do_desempate
    from processo_seletivo.editais.domain.validation import quem_exige_o_resultado
    from processo_seletivo.resultados.domain.regra import impedimento_da_regra

    perfis = list((conteudo or {}).get("profiles") or []) if perfis is None else list(perfis)
    etapas = {str(e.get("id")): e for e in (conteudo or {}).get("stages") or [] if e.get("id")}
    consolidavel = {eid: impedimento_da_regra(e) is None for eid, e in etapas.items()}
    esperadas = set(quem_exige_o_resultado({**(conteudo or {}), "profiles": perfis}))
    # **Só as que um ato consome puxam a progressão** (D-019). A enumerada por marco de sorteio é
    # esperada — dá visibilidade e recurso —, mas nada a jusante a lê; as que vêm antes dela só a
    # filtrariam, e cobrá-las mandaria avaliar o que não muda nenhum ato.
    for perfil in perfis:
        for marco in perfil.get("classificationMilestones") or []:
            if marco.get("orderProduction") == "POR_SORTEIO" or marco.get("drawMethod"):
                continue
            esperadas.update(etapas_do_desempate(marco))
            esperadas.update(
                str(e) for e in marco.get("stages") or [] if consolidavel.get(str(e), False)
            )
    esperadas &= set(etapas)
    consumidas = _consumidas_por_ato(conteudo, perfis) & esperadas
    mudou = True
    while mudou:
        mudou = False
        limite = max((etapas[e].get("order") or 0 for e in consumidas), default=None)
        if limite is None:
            break
        for eid, etapa in etapas.items():
            if eid in esperadas or not consolidavel[eid]:
                continue
            if (etapa.get("order") or 0) < limite:
                esperadas.add(eid)
                consumidas.add(eid)
                mudou = True
    return {eid: (ESPERADA if eid in esperadas else SEM_EFEITO) for eid in etapas}


def _consumidas_por_ato(conteudo, perfis):
    """As Etapas cujo resultado um ato do GPS lê: a ordem por pontuação (enumerada ou desempate), o
    corte que a governa, e a relação do sorteio que a declara de habilitação."""
    from processo_seletivo.classificacao.domain import faixa
    from processo_seletivo.classificacao.domain.desempate import etapas_que_a_ordem_le

    saida = set()
    for perfil in perfis:
        for marco in perfil.get("classificationMilestones") or []:
            governada = faixa.etapa_governada(marco.get("cutRule"))
            if governada:
                saida.add(str(governada))
            habilitacao = (marco.get("drawMethod") or {}).get("qualifyingStageId")
            if habilitacao:
                saida.add(str(habilitacao))
            if not (marco.get("orderProduction") == "POR_SORTEIO" or marco.get("drawMethod")):
                saida.update(etapas_que_a_ordem_le(marco))
    return saida


# ---------------------------------------------------------------------------------------------
# As regras puras, ponto a ponto (FR-4062, FR-4065 a FR-4076; data-model, "as regras")
# ---------------------------------------------------------------------------------------------


def situacoes_da_etapa(f):
    """`(resumo, providencias)` da Etapa no Edital inteiro, a partir dos fatos da distribuição.

    `f` traz o que a tela da distribuição lê: `expectativa`, `bloqueio` (`(codigo, frase)` ou
    `None`), `inscricoes_em_curso` (a frase da recusa, ou ""), `governada`, `com_faixa`, o resumo
    (`participantes`, `carentes`, `sem_conclusao`, `prontas`, `consolidadas`, `reavaliacoes`), `url`
    (a distribuição, para quem a abre), `minhas` (as pendentes da própria pessoa, pela carga de
    Minhas Etapas) e `url_da_mesa`.

    **Uma Etapa pode pedir três coisas ao mesmo tempo** (FR-4062): distribuir quem está sem
    avaliador, avaliar o que já foi distribuído e consolidar o que ficou pronto. São três
    providências, de responsáveis diferentes; o resumo é a primeira delas, para a célula.
    """
    nome = f.get("nome") or "a Etapa"
    if f.get("expectativa") == SEM_EFEITO:
        return _c(NAO_SE_APLICA, natureza=ETAPA, nota="sem efeito no GPS"), []
    url = f.get("url") or ""
    bloqueio = f.get("bloqueio")
    if bloqueio and bloqueio[0] != "corte-obsoleto":
        celula = _c(
            IMPEDIDO,
            natureza=ETAPA,
            ato=f"Consolidar {nome}",
            responsavel=CONDUZ,
            razao=_frase(bloqueio[1]),
            url=url,
            quem_resolve=RETIFICA,
        )
        # A Mesa continua aberta a quem tem inscrição atribuída (a carga da `104`): a regra impede
        # consolidar, e não avaliar. Calar o trabalho dele aqui seria a faixa da Lista dizendo uma
        # coisa e o Edital outra.
        return celula, [celula, *_avaliar_minhas(f)]
    if f.get("inscricoes_em_curso"):
        celula = _c(
            AGUARDA,
            natureza=DISTRIBUIR,
            ato=f"Distribuir {nome}",
            razao=f["inscricoes_em_curso"],
            url=url,
            ate=f.get("fim_das_inscricoes"),
        )
        return celula, [celula]
    if f.get("governada") and not f.get("com_faixa"):
        return (
            _c(
                DEPOIS,
                natureza=ETAPA,
                razao="só participa a faixa do corte, e o corte que a alimenta não foi emitido",
            ),
            [],
        )
    if bloqueio:
        celula = _c(
            IMPEDIDO,
            natureza=CORTE,
            ato="Emitir a geração sucessora do corte",
            responsavel=CONDUZ,
            razao=_frase(bloqueio[1]),
            url=url,
        )
        return celula, [celula]
    participantes = f.get("participantes") or 0
    if not participantes:
        return _c(NAO_SE_APLICA, natureza=ETAPA, nota="nenhuma inscrição participa"), []
    consolidadas = f.get("consolidadas") or 0
    nota = f"{consolidadas} de {participantes} consolidadas"
    providencias = []
    reavaliacoes = f.get("reavaliacoes") or 0
    if reavaliacoes:
        providencias.append(
            _c(
                OBSOLETO,
                natureza=REAVALIAR,
                ato="Cumprir "
                + _n(reavaliacoes, "reavaliação determinada", "reavaliações determinadas"),
                responsavel=CONDUZ,
                razao="um recurso determinou reavaliar, e outro avaliador precisa concluir",
                url=url,
                contagem=reavaliacoes,
                nota=nota,
            )
        )
    # **Quem já tem Resultado não espera avaliador** (D-013). O resumo da distribuição conta como
    # carente toda participante sem avaliador suficiente, inclusive a consolidada por Ocorrência ou
    # por regularização; cobrar distribuí-la mandaria trabalhar no que já está decidido.
    abertas = max(participantes - consolidadas, 0)
    carentes = min(f.get("carentes") or 0, abertas)
    if carentes:
        providencias.append(
            _c(
                PENDENTE,
                natureza=DISTRIBUIR,
                ato="Distribuir "
                + _n(
                    carentes,
                    "inscrição sem avaliador suficiente",
                    "inscrições sem avaliador suficiente",
                ),
                responsavel=CONDUZ,
                url=url,
                contagem=carentes,
                nota=nota,
            )
        )
    a_avaliar = min(
        max((f.get("sem_conclusao") or 0) - (f.get("carentes") or 0), 0), abertas - carentes
    )
    minhas = min(f.get("minhas") or 0, a_avaliar) if a_avaliar else 0
    if minhas:
        providencias.append(
            _c(
                PENDENTE,
                natureza=AVALIAR,
                ato=f"Avaliar {_n(minhas, 'inscrição', 'inscrições')}",
                responsavel=AVALIA,
                url=f.get("url_da_mesa") or "",
                contagem=minhas,
                nota=nota,
            )
        )
    if a_avaliar - minhas > 0:
        providencias.append(
            _c(
                PENDENTE,
                natureza=AVALIAR,
                ato="Avaliar "
                + _n(a_avaliar - minhas, "inscrição distribuída", "inscrições distribuídas"),
                responsavel=AVALIA,
                contagem=a_avaliar - minhas,
                nota=nota,
            )
        )
    prontas = f.get("prontas") or 0
    if prontas:
        providencias.append(
            _c(
                PENDENTE,
                natureza=CONSOLIDAR,
                ato=f"Consolidar {_n(prontas, 'inscrição pronta', 'inscrições prontas')}",
                responsavel=CONDUZ,
                url=url,
                contagem=prontas,
                nota=nota,
            )
        )
    if providencias:
        resumo = providencias[0]
        return replace(resumo, natureza=ETAPA, url=resumo.url or url), providencias
    if consolidadas >= participantes:
        return _c(FEITO, natureza=ETAPA, nota=nota, url=url), []
    # Participantes sem conclusão elegível e sem avaliação a fazer: a partição diz "não
    # consolidável" (conclusões demais, norma incompatível). É a tela da distribuição que diz por
    # quê, linha a linha; aqui fica a indicação de que há algo a olhar lá.
    celula = _c(
        PENDENTE,
        natureza=CONSOLIDAR,
        ato="Conferir as inscrições não consolidáveis",
        responsavel=CONDUZ,
        url=url,
        nota=nota,
    )
    return celula, [celula]


def _avaliar_minhas(f):
    minhas = f.get("minhas") or 0
    if not minhas or not f.get("url_da_mesa"):
        return []
    return [
        _c(
            PENDENTE,
            natureza=AVALIAR,
            ato=f"Avaliar {_n(minhas, 'inscrição', 'inscrições')}",
            responsavel=AVALIA,
            url=f["url_da_mesa"],
            contagem=minhas,
        )
    ]


def situacao_da_etapa_no_perfil(edital, *, participantes, consolidadas, reavaliacoes=0):
    """A célula da Etapa num Perfil, a partir da do Edital e da partição do Perfil (D-013).

    A Etapa vale para o Edital inteiro, e a distribuição também. O Perfil só muda duas leituras: se
    ninguém dele participa, não se aplica; se todos os dele estão consolidados, está feita para
    ele — ainda que outro Perfil tenha trabalho em aberto na mesma Etapa.
    """
    if edital.situacao in (NAO_SE_APLICA, DEPOIS, IMPEDIDO, AGUARDA):
        return edital
    if not participantes:
        return _c(NAO_SE_APLICA, natureza=ETAPA, nota="nenhuma inscrição deste Perfil participa")
    nota = f"{consolidadas} de {participantes} consolidadas"
    if consolidadas >= participantes and not reavaliacoes:
        return _c(FEITO, natureza=ETAPA, nota=nota, url=edital.url)
    return replace(edital, nota=nota)


def feita(celula):
    """O ponto anterior está resolvido para quem vem depois: feito, ou não se aplica."""
    return celula is not None and celula.situacao in (FEITO, NAO_SE_APLICA)


def situacao_da_relacao(f):
    """A relação de habilitados de uma lista, num marco por sorteio (FR-4065).

    `f`: `congelada`, `projetados`, `diagnostico` (da relação congelada que nunca sorteará),
    `habilitacao` (a célula da Etapa de habilitação, ou `None`), `inscricoes_em_curso` (frase),
    `congelar_inviavel` (o aviso da `102`, ou `None`), `url`.
    """
    url = f.get("url") or ""
    if f.get("congelada"):
        if f.get("diagnostico"):
            return _c(
                OBSOLETO,
                natureza=RELACAO,
                ato="Congelar a relação sucessora",
                responsavel=CONDUZ,
                razao=(
                    "a relação congelada não sorteará com a extração declarada: a extração é "
                    "anterior ao congelamento, e o caminho começa por uma Retificação"
                ),
                url=url,
                quem_resolve=RETIFICA,
            )
        return _c(FEITO, natureza=RELACAO, nota=_n(f.get("participantes"), "participante"), url=url)
    habilitacao = f.get("habilitacao")
    if habilitacao is not None and not feita(habilitacao):
        return _c(
            DEPOIS,
            natureza=RELACAO,
            razao="a relação só admite quem habilitou na Etapa de habilitação, ainda não feita",
        )
    if not f.get("projetados"):
        return _c(
            NAO_SE_APLICA,
            natureza=RELACAO,
            nota="nenhuma inscrição nesta lista",
            razao="não há universo a comprometer aqui",
        )
    if f.get("inscricoes_em_curso"):
        return _c(
            AGUARDA,
            natureza=RELACAO,
            ato="Congelar a relação",
            razao=f["inscricoes_em_curso"],
            url=url,
            ate=f.get("fim_das_inscricoes"),
        )
    inviavel = f.get("congelar_inviavel")
    if inviavel:
        return _c(
            IMPEDIDO,
            natureza=RELACAO,
            ato="Congelar a relação",
            responsavel=CONDUZ,
            razao=(
                f"congelar hoje condenaria o sorteio: a extração declarada é de "
                f"{_data(inviavel.get('dia'))}, e o caminho é retificá-la"
            ),
            url=url,
            quem_resolve=RETIFICA,
        )
    return _c(
        PENDENTE,
        natureza=RELACAO,
        ato="Congelar a relação",
        responsavel=CONDUZ,
        url=url,
        contagem=f.get("projetados"),
    )


def situacao_da_semente(f):
    """A semente do marco — comum às listas dele (FR-4066).

    `f`: `alguma_congelada`, `observada`, `recusa` (`{"causa", "detalhe"}` da cadeia consumida ou da
    declaração), `ocorre_em`, `agora`, `referencia`, `url`.

    **A falha de acesso à fonte não muda nada** (contrato §5): nada é gravado, e quem tentou
    continua diante da mesma providência, que se tenta de novo.
    """
    url = f.get("url") or ""
    if f.get("observada"):
        return _c(FEITO, natureza=SEMENTE, nota=f.get("referencia") or "", url=url)
    if f.get("sem_instante"):
        return _c(
            IMPEDIDO,
            natureza=SEMENTE,
            ato="Realizar o sorteio",
            responsavel=CONDUZ,
            razao=(
                "a ocorrência observada não diz desde quando a extração vale, ou está "
                "indisponível, e o sorteio seria recusado"
            ),
            url=url,
        )
    if not f.get("alguma_congelada"):
        return _c(DEPOIS, natureza=SEMENTE, razao="nenhuma relação deste marco está congelada")
    recusa = f.get("recusa")
    if recusa:
        return _c(
            IMPEDIDO,
            natureza=SEMENTE,
            ato="Observar a extração",
            responsavel=CONDUZ,
            razao=_frase(recusa.get("detalhe") or ""),
            url=url,
            quem_resolve=RETIFICA,
        )
    ocorre_em, agora = f.get("ocorre_em"), f.get("agora")
    if ocorre_em is not None and agora is not None and ocorre_em > agora:
        return _c(
            AGUARDA,
            natureza=SEMENTE,
            ato="Observar a extração",
            razao=f"a extração {f.get('referencia') or ''} está prevista para {_data(ocorre_em)}",
            url=url,
            ate=ocorre_em,
        )
    return _c(
        PENDENTE,
        natureza=SEMENTE,
        ato="Observar a extração",
        responsavel=CONDUZ,
        nota=f.get("referencia") or "",
        url=url,
    )


def situacao_do_sorteio(f):
    """O sorteio de uma lista (FR-4067). `f`: `relacao`, `semente` (células), `ordem` (a célula da
    ordem do indicador da condução), `url`."""
    relacao, semente, ordem = f["relacao"], f["semente"], f.get("ordem") or {}
    url = f.get("url") or ""
    estado = ordem.get("estado")
    if estado == "feito":
        return _c(FEITO, natureza=SORTEIO, nota=ordem.get("nota") or "", url=url)
    if estado == "obsoleto":
        if not f.get("anulavel"):
            # A tela só oferece a anulação com a relação sucessora e uma ocorrência nova (021):
            # o passo 1 dela é retificar, e dizer "anule" mandaria a uma tela sem o botão.
            return _c(
                IMPEDIDO,
                natureza=SORTEIO,
                ato="Anular e sortear de novo",
                responsavel=CONDUZ,
                razao=(
                    "a relação que originou o sorteio foi sucedida, e anular exige a relação nova "
                    "e uma ocorrência nova"
                ),
                url=url,
                quem_resolve=RETIFICA,
            )
        return _c(
            OBSOLETO,
            natureza=SORTEIO,
            ato="Anular e sortear de novo",
            responsavel=CONDUZ,
            razao="a relação que originou o sorteio foi sucedida",
            url=url,
        )
    if relacao.situacao == NAO_SE_APLICA:
        return _c(NAO_SE_APLICA, natureza=SORTEIO, nota="nenhuma inscrição nesta lista")
    if relacao.situacao == OBSOLETO:
        return _c(
            IMPEDIDO,
            natureza=SORTEIO,
            ato="Realizar o sorteio",
            responsavel=CONDUZ,
            razao="a extração é anterior ao congelamento da relação, e o sorteio seria recusado",
            url=url,
            quem_resolve=RETIFICA,
        )
    if relacao.situacao != FEITO or semente.situacao != FEITO:
        return _c(
            DEPOIS,
            natureza=SORTEIO,
            razao=("falta congelar a relação" if relacao.situacao != FEITO else "falta a semente"),
        )
    return _c(PENDENTE, natureza=SORTEIO, ato="Realizar o sorteio", responsavel=CONDUZ, url=url)


def situacao_da_ordem(f):
    """A ordem de uma lista num marco por pontuação (FR-4068).

    `f`: `celula` (a da ordem no indicador da condução), `faltam` (nomes das Etapas que a ordem lê e
    que ainda não estão feitas no Perfil).

    **A ordem não é recusada sem avaliação, e mesmo assim é *Depois*** (o `G-01` do estudo, que é da
    `126`): emiti-la antes das Etapas grava uma ordem que envelhece quando os resultados chegam, e a
    sucessão exige motivo. Dizer *Pendente* mandaria emitir.
    """
    celula = f.get("celula") or {}
    estado, url = celula.get("estado"), celula.get("url") or ""
    if estado == "feito":
        return _c(FEITO, natureza=ORDEM, nota=celula.get("nota") or "", url=url)
    if estado == "obsoleto":
        return _c(
            OBSOLETO,
            natureza=ORDEM,
            ato="Emitir a ordem sucessora",
            responsavel=CONDUZ,
            razao="a regra ou o universo mudaram depois da emissão",
            url=url,
        )
    if estado == "nao_se_aplica":
        return _c(NAO_SE_APLICA, natureza=ORDEM, nota=celula.get("nota") or "")
    faltam = f.get("faltam") or []
    if faltam:
        return _c(
            DEPOIS,
            natureza=ORDEM,
            razao=f"a ordem lê {_lista_de_nomes(faltam)}, que ainda não está feita"
            if len(faltam) == 1
            else f"a ordem lê {_lista_de_nomes(faltam)}, que ainda não estão feitas",
        )
    return _c(PENDENTE, natureza=ORDEM, ato="Emitir a ordem", responsavel=CONDUZ, url=url)


def situacao_do_corte(f):
    """O corte de uma lista (FR-4069). `f`: `celula` (do indicador), `ordem` (a célula da ordem ou
    do     sorteio, já derivada)."""
    celula = f.get("celula") or {}
    estado, url = celula.get("estado"), celula.get("url") or ""
    if estado == "nao_se_aplica":
        return _c(NAO_SE_APLICA, natureza=CORTE, nota=celula.get("nota") or "")
    if estado == "feito":
        return _c(FEITO, natureza=CORTE, url=url)
    if estado == "obsoleto":
        return _c(
            OBSOLETO,
            natureza=CORTE,
            ato="Emitir a geração sucessora do corte",
            responsavel=CONDUZ,
            razao="o corte vigente está para trás",
            url=url,
        )
    ordem = f.get("ordem")
    if ordem is not None and ordem.situacao == NAO_SE_APLICA:
        return _c(NAO_SE_APLICA, natureza=CORTE, nota="nenhuma inscrição nesta lista")
    if ordem is None or ordem.situacao != FEITO:
        return _c(DEPOIS, natureza=CORTE, razao="o corte lê a ordem, que ainda não está vigente")
    return _c(PENDENTE, natureza=CORTE, ato="Emitir o corte", responsavel=CONDUZ, url=url)


def situacao_da_apuracao(f):
    """A apuração da ocupação de uma lista (FR-4069, FR-4070, D-014).

    `f`: `celula` (do indicador), `ordem`, `corte` (a célula do corte, no marco que corta),
    `governada` (a célula da Etapa governada no Perfil, ou `None`), `nome_da_governada`.

    **No marco que corta, a apuração espera o corte** (D-018). O domínio a aceita antes, mas os
    titulares saem de quem a faixa alcançou: sem corte não há faixa, a apuração conta todas as vagas
    como faltando, e a convocação manda pedir a faixa seguinte de um corte que não existe — o beco
    `J-06` do estudo.
    """
    celula = f.get("celula") or {}
    estado, url = celula.get("estado"), celula.get("url") or ""
    if estado == "nao_se_aplica":
        return _c(NAO_SE_APLICA, natureza=APURACAO, nota=celula.get("nota") or "")
    if estado == "feito":
        return _c(FEITO, natureza=APURACAO, url=url)
    governada = f.get("governada")
    if estado == "obsoleto" and governada is not None and not feita(governada):
        return _c(
            DEPOIS,
            natureza=APURACAO,
            razao="a apuração está para trás, e a sucessora espera a Etapa governada pela faixa",
        )
    if estado == "obsoleto":
        return _c(
            OBSOLETO,
            natureza=APURACAO,
            ato="Emitir a apuração sucessora",
            responsavel=CONDUZ,
            razao="a apuração vigente está para trás",
            url=url,
        )
    ordem = f.get("ordem")
    if ordem is not None and ordem.situacao == NAO_SE_APLICA:
        return _c(NAO_SE_APLICA, natureza=APURACAO, nota="nenhuma inscrição nesta lista")
    if ordem is None or ordem.situacao != FEITO:
        return _c(
            DEPOIS, natureza=APURACAO, razao="a apuração lê a ordem, que ainda não está vigente"
        )
    corte = f.get("corte")
    if corte is not None and not feita(corte):
        return _c(
            DEPOIS,
            natureza=APURACAO,
            razao=(
                "a apuração conta quem a faixa do corte alcançou, e o corte desta lista ainda não "
                "está vigente"
            ),
        )
    if governada is not None and not feita(governada):
        nome = f.get("nome_da_governada") or "a Etapa governada pela faixa"
        return _c(
            DEPOIS,
            natureza=APURACAO,
            razao=(
                f"quem ocupa é quem habilitou em {nome}, governada pela faixa, que ainda não está "
                "feita: apurar agora apuraria ninguém"
            ),
        )
    return _c(PENDENTE, natureza=APURACAO, ato="Apurar a ocupação", responsavel=CONDUZ, url=url)


def situacao_do_resultado(f):
    """A divulgação do resultado de uma lista (FR-4071, FR-4072, D-008, D-009).

    `f`: `celula` (a da publicação no indicador), `ordem`, `definitiva` (a aferição da definitiva,
    quando a vigente é preliminar: `{"nivel", "codigo", "mensagem"}`), `url_da_previa`.
    """
    from processo_seletivo.divulgacao.domain import publicabilidade as p

    celula = f.get("celula") or {}
    estado, nota = celula.get("estado"), (celula.get("nota") or "")
    url = celula.get("url") or ""
    previa = f.get("url_da_previa") or url
    ordem = f.get("ordem")
    if estado != "feito" and ordem is not None and ordem.situacao == OBSOLETO:
        return _c(
            DEPOIS,
            natureza=RESULTADO,
            razao="a ordem vigente está para trás: o ato sucessor vem antes de divulgar",
        )
    afericao = f.get("afericao")
    if estado != "feito" and afericao and afericao.get("nivel") == p.IMPEDIMENTO:
        return _c(
            IMPEDIDO,
            natureza=RESULTADO,
            ato="Publicar o resultado",
            responsavel=PUBLICA,
            razao=_frase(afericao.get("mensagem") or ""),
            url=previa,
            quem_resolve=CONDUZ,
        )
    if estado == "obsoleto":
        return _c(
            OBSOLETO,
            natureza=RESULTADO,
            ato="Publicar o resultado vigente",
            responsavel=PUBLICA,
            razao="o público lê um ato anterior",
            url=previa,
        )
    if estado == "feito":
        if "preliminar" not in nota:
            return _c(FEITO, natureza=RESULTADO, nota=nota, url=url)
        definitiva = f.get("definitiva")
        if not definitiva or definitiva.get("nivel") != p.IMPEDIMENTO:
            return _c(
                PENDENTE,
                natureza=RESULTADO,
                ato="Publicar o resultado definitivo",
                responsavel=PUBLICA,
                nota=nota,
                url=previa,
            )
        espera = definitiva.get("codigo") in (
            p.JANELA_ABERTA,
            p.RECURSO_PENDENTE,
            p.REAVALIACAO_PENDENTE,
            p.PROVIDENCIA_PENDENTE,
        )
        return _c(
            AGUARDA if espera else IMPEDIDO,
            natureza=RESULTADO,
            ato="Publicar o resultado definitivo",
            responsavel="" if espera else PUBLICA,
            nota=nota,
            razao=_frase(_sem_marcacao(definitiva.get("mensagem") or "")),
            url=previa,
            ate=definitiva.get("ate"),
        )
    if ordem is not None and ordem.situacao == NAO_SE_APLICA:
        return _c(NAO_SE_APLICA, natureza=RESULTADO, nota="nenhuma inscrição nesta lista")
    if ordem is None or ordem.situacao not in (FEITO, OBSOLETO):
        return _c(DEPOIS, natureza=RESULTADO, razao="não há ordem vigente a divulgar")
    return _c(
        PENDENTE,
        natureza=RESULTADO,
        ato="Publicar o resultado",
        responsavel=PUBLICA,
        url=previa,
    )


def situacoes_da_convocacao(f):
    """`(resumo, providencias)` da convocação de uma lista (FR-4073 a FR-4076).

    `f` traz o que a tela da convocação lê: `apuracao` (a célula da apuração), `impedimento` (da
    prévia dos titulares: `{"codigo", "detalhe"}` ou `None`), `titulares`, `pendentes`,
    `por_publicacao`, `vencidos`, `em_curso` (quantas com prazo correndo) e `ate` (o vencimento mais
    próximo delas), `faltando` (a ocupar), `fila` (quantos chamáveis), `esgotou`, `corte_vigente`,
    `com_quadro`, `conferir` e `decidir` (chamadas com documento a conferir, e prontas para o
    desfecho), `aguardando_documentos`, `convocadas`, `desfechadas`, `url`, `url_da_ocupacao`.
    """
    from processo_seletivo.convocacao.domain import nomes

    url = f.get("url") or ""
    apuracao = f.get("apuracao")
    if apuracao is not None and apuracao.situacao == NAO_SE_APLICA:
        return _c(NAO_SE_APLICA, natureza=CONVOCACAO, nota=apuracao.nota or ""), []
    if apuracao is None or apuracao.situacao != FEITO:
        return _c(DEPOIS, natureza=CONVOCACAO, razao="não há apuração vigente desta lista"), []
    governada = f.get("governada")
    if governada is not None and not feita(governada):
        # **A convocação chama quem habilitou na Etapa governada** (item 2 da revisão): com ela em
        # aberto, a fila não tem ninguém, e "esgotou" mandaria pedir a faixa seguinte — o `J-06`.
        nome = f.get("nome_da_governada") or "a Etapa governada pela faixa"
        return (
            _c(
                DEPOIS,
                natureza=CONVOCACAO,
                razao=f"quem é chamado é quem habilitou em {nome}, que ainda não está feita",
            ),
            [],
        )
    impedimento = f.get("impedimento") or {}
    if impedimento.get("codigo") == nomes.FORMA_DE_COMUNICACAO_NAO_DECLARADA:
        celula = _c(
            IMPEDIDO,
            natureza=CONVOCACAO,
            ato="Convocar",
            responsavel=CONDUZ,
            razao=_frase(impedimento.get("detalhe") or ""),
            url=url,
            quem_resolve=RETIFICA,
        )
        return celula, [celula]
    providencias = []
    pendentes = f.get("pendentes") or 0
    if pendentes:
        texto = (
            f"Registrar a publicação de {_n(pendentes, 'convocação', 'convocações')}"
            if f.get("por_publicacao")
            else f"Emitir {_n(pendentes, 'comunicação', 'comunicações')}"
        )
        providencias.append(
            _c(
                PENDENTE,
                natureza=CONVOCACAO,
                ato=texto,
                responsavel=CONDUZ,
                razao="o prazo não começou a correr",
                url=url,
                contagem=pendentes,
            )
        )
    vencidos = f.get("vencidos") or 0
    if vencidos:
        providencias.append(
            _c(
                PENDENTE,
                natureza=CONVOCACAO,
                ato="Registrar o não atendimento de "
                + _n(vencidos, "convocação vencida", "convocações vencidas"),
                responsavel=CONDUZ,
                url=url,
                contagem=vencidos,
            )
        )
    decidir = f.get("decidir") or 0
    if decidir:
        providencias.append(
            _c(
                PENDENTE,
                natureza=CONVOCACAO,
                ato="Registrar o desfecho de "
                + _n(decidir, "convocação pronta", "convocações prontas"),
                responsavel=CONDUZ,
                razao="os documentos obrigatórios estão conferidos",
                url=url,
                contagem=decidir,
            )
        )
    conferir = f.get("conferir") or 0
    if conferir:
        providencias.append(
            _c(
                PENDENTE,
                natureza=CONFERIR,
                ato=f"Conferir os documentos de {_n(conferir, 'convocação', 'convocações')}",
                responsavel=CONFERE,
                url=f.get("url_da_conferencia") or url,
                contagem=conferir,
            )
        )
    titulares = f.get("titulares") or 0
    if titulares:
        providencias.append(
            _c(
                PENDENTE,
                natureza=CONVOCACAO,
                ato=f"Convocar {_n(titulares, 'titular', 'titulares')}",
                responsavel=CONDUZ,
                url=url,
                contagem=titulares,
            )
        )
    faltando = f.get("faltando") or 0
    sem_chamada = max(faltando - (f.get("em_aberto") or 0), 0)
    if not titulares and sem_chamada:
        if f.get("fila"):
            providencias.append(
                _c(
                    PENDENTE,
                    natureza=CONVOCACAO,
                    ato="Chamar a próxima da fila",
                    responsavel=CONDUZ,
                    razao=_n(sem_chamada, "vaga a ocupar", "vagas a ocupar")
                    + " sem chamada em aberto",
                    url=url,
                    condicional=True,
                    contagem=sem_chamada,
                )
            )
        elif f.get("esgotou") and f.get("corte_vigente") and f.get("com_quadro"):
            providencias.append(
                _c(
                    PENDENTE,
                    natureza=APURACAO,
                    ato="Pedir a faixa seguinte",
                    responsavel=CONDUZ,
                    razao="não há mais quem chamar dentro da faixa, e há vaga a ocupar",
                    url=f.get("url_da_ocupacao") or "",
                    condicional=True,
                    contagem=sem_chamada,
                )
            )
    em_curso = f.get("em_curso") or 0
    aguardando = f.get("aguardando_documentos") or 0
    if em_curso:
        providencias.append(
            _c(
                AGUARDA,
                natureza=CONVOCACAO,
                ato=f"Resposta de {_n(em_curso, 'convocação', 'convocações')}",
                razao=(
                    f"o prazo corre até {_data(f.get('ate'))}"
                    + (f"; {aguardando} aguardam documentos" if aguardando else "")
                    if f.get("ate")
                    else "o prazo está correndo"
                ),
                url=url,
                ate=f.get("ate"),
                contagem=em_curso,
            )
        )
    if not providencias and sem_chamada and not titulares:
        # Vaga a ocupar e ninguém a chamar, sem faixa a ampliar (item 12 da revisão): não é
        # "feito", e nenhum ato desta tela resolve.
        providencias.append(
            _c(
                IMPEDIDO,
                natureza=CONVOCACAO,
                ato="Ocupar a vaga",
                responsavel=CONDUZ,
                razao=(
                    _n(sem_chamada, "vaga a ocupar", "vagas a ocupar")
                    + ", e não há mais quem chamar nesta lista"
                ),
                url=url,
            )
        )
    if providencias:
        primeira = next((c for c in providencias if c.situacao in A_PRATICAR), providencias[0])
        return replace(primeira, natureza=CONVOCACAO), providencias
    convocadas = f.get("convocadas") or 0
    if not faltando and not convocadas:
        return _c(NAO_SE_APLICA, natureza=CONVOCACAO, nota="nenhuma vaga a ocupar"), []
    desfechadas = f.get("desfechadas") or 0
    nota = f"{desfechadas} de {convocadas} com desfecho" if convocadas else ""
    return (
        _c(
            FEITO,
            natureza=CONVOCACAO,
            nota=nota,
            url=url,
            contagem=max(convocadas - desfechadas, 0),
        ),
        [],
    )


# ---------------------------------------------------------------------------------------------
# A composição da sequência do Perfil (FR-4103, FR-4104, D-011) — pura
# ---------------------------------------------------------------------------------------------

GRUPO_DAS_ETAPAS = "Etapas · valem para o Perfil"
GRUPO_DO_SORTEIO = "Marco · por sorteio"
GRUPO_DA_PONTUACAO = "Marco · por pontuação"
GRUPO_DA_GOVERNADA = "Etapa governada pela faixa"
GRUPO_SEM_EFEITO = "Sem efeito no GPS"


@dataclass
class Ponto:
    tipo: str
    titulo: str
    grupo: str
    marco: dict | None = None
    etapa: dict | None = None
    #: `{lista_id: Celula}`. A Etapa e a semente têm a mesma célula em todas as listas.
    celulas: dict = field(default_factory=dict)

    def celula(self, lista_id):
        return self.celulas.get(_chave(lista_id))


def por_sorteio(marco):
    return marco.get("orderProduction") == "POR_SORTEIO" or bool(marco.get("drawMethod"))


def sequencia_do_perfil(etapas, marcos, expectativa):
    """Os pontos do Perfil, na ordem da `jornada()` da `094`, sem colunas fixas (FR-4103).

    `etapas` são as do conteúdo; `marcos`, os do Perfil; `expectativa`, a do Perfil
    (`expectativa_das_etapas`). Cada ponto ainda sem células.

    **A `jornada()` precisa de um selecionado**, e aqui ele não tem papel: os estados de simulação
    que ela devolve são ignorados, e só a sequência e os tipos são lidos (R-002).

    **O marco por sorteio com Etapa de habilitação vem depois dela** (D-011). A `jornada()` o põe
    no começo, que é o certo para o sorteio que precede a análise documental; com
    `qualifyingStageId`, a relação lê o resultado da Etapa, e a ordem se inverte.
    """
    from processo_seletivo.avaliacoes.domain.previsao import forma_publicada
    from processo_seletivo.classificacao.domain import faixa
    from processo_seletivo.classificacao.domain.jornada import jornada

    if not marcos:
        return []
    publicadas = [
        {
            "id": str(e.get("id")),
            "name": e.get("name") or "",
            "order": e.get("order") or 0,
            "forma": forma_publicada(e),
        }
        for e in etapas
        if e.get("id")
    ]
    por_id = {e["id"]: e for e in etapas if e.get("id")}
    com_sub = [
        {**m, "sub": indice, "stages": [str(s) for s in m.get("stages") or []]}
        for indice, m in enumerate(marcos)
    ]
    brutos = jornada(publicadas, com_sub, 0)
    brutos = _habilitacao_antes_do_sorteio(brutos)
    governadas = {
        faixa.etapa_governada(m.get("cutRule"))
        for m in marcos
        if faixa.etapa_governada(m.get("cutRule"))
    }
    pontos = []
    for bruto in brutos:
        if bruto["tipo"] == "marco":
            # O marco do conteúdo, e não a cópia com `sub` que a `jornada()` recebeu: a leitura
            # encontra os pontos do marco por identidade.
            pontos.extend(_pontos_do_marco(marcos[bruto["marco"]["sub"]]))
            continue
        etapas_do_ponto = bruto.get("etapas") or [bruto["etapa"]]
        for etapa in etapas_do_ponto:
            eid = str(etapa["id"])
            if expectativa.get(eid) == SEM_EFEITO:
                grupo = GRUPO_SEM_EFEITO
            elif bruto["tipo"] == "etapa_alimentada" or eid in governadas:
                grupo = GRUPO_DA_GOVERNADA
            else:
                grupo = GRUPO_DAS_ETAPAS
            pontos.append(Ponto(ETAPA, etapa["name"], grupo, etapa=por_id.get(eid, etapa)))
    return _governadas_antes_da_apuracao(pontos)


def _habilitacao_antes_do_sorteio(brutos):
    """D-011: tira o marco por sorteio com `qualifyingStageId` do começo e o põe depois da Etapa."""
    saida = list(brutos)
    for bruto in list(saida):
        if bruto["tipo"] != "marco":
            continue
        metodo = bruto["marco"].get("drawMethod") or {}
        alvo = str(metodo.get("qualifyingStageId") or "")
        if not alvo:
            continue
        indice_da_etapa = next(
            (
                i
                for i, outro in enumerate(saida)
                if outro["tipo"] != "marco"
                and alvo in {str(e["id"]) for e in (outro.get("etapas") or [outro.get("etapa")])}
            ),
            None,
        )
        if indice_da_etapa is None or saida.index(bruto) > indice_da_etapa:
            continue
        saida.remove(bruto)
        indice_da_etapa = next(
            i
            for i, outro in enumerate(saida)
            if outro["tipo"] != "marco"
            and alvo in {str(e["id"]) for e in (outro.get("etapas") or [outro.get("etapa")])}
        )
        saida.insert(indice_da_etapa + 1, bruto)
    return saida


def _pontos_do_marco(marco):
    nome = marco.get("name") or "Marco"
    if por_sorteio(marco):
        grupo = f"{GRUPO_DO_SORTEIO} · {nome}"
        pontos = [
            Ponto(RELACAO, "Relação", grupo, marco=marco),
            Ponto(SEMENTE, "Semente", grupo, marco=marco),
            Ponto(SORTEIO, "Sorteio", grupo, marco=marco),
        ]
    else:
        grupo = f"{GRUPO_DA_PONTUACAO} · {nome}"
        pontos = [Ponto(ORDEM, "Ordem", grupo, marco=marco)]
    if marco.get("cutRule"):
        pontos.append(Ponto(CORTE, "Corte", grupo, marco=marco))
    pontos += [
        Ponto(APURACAO, "Apuração", grupo, marco=marco),
        Ponto(RESULTADO, "Resultado", grupo, marco=marco),
        Ponto(CONVOCACAO, "Convocação", grupo, marco=marco),
    ]
    return pontos


def _governadas_antes_da_apuracao(pontos):
    """A Etapa governada entra entre o corte e a apuração do marco que a alimenta (D-014).

    A `jornada()` a põe depois do marco inteiro, porque para ela o marco é um ponto só. Aqui o
    marco se abre em atos, e o que a Etapa governada decide — quem ocupa e quem é chamado — vem
    depois do corte e antes da apuração.
    """
    from processo_seletivo.classificacao.domain import faixa

    saida = list(pontos)
    for ponto in list(saida):
        if ponto.tipo != ETAPA or ponto.grupo != GRUPO_DA_GOVERNADA:
            continue
        eid = str(ponto.etapa.get("id"))
        corte = next(
            (
                p
                for p in saida
                if p.tipo == CORTE and faixa.etapa_governada(p.marco.get("cutRule")) == eid
            ),
            None,
        )
        if corte is None:
            continue
        saida.remove(ponto)
        saida.insert(saida.index(corte) + 1, ponto)
    return saida


# ---------------------------------------------------------------------------------------------
# O andamento (os objetos que a tela desenha)
# ---------------------------------------------------------------------------------------------


@dataclass
class PerfilNoAndamento:
    perfil: dict
    forma: str
    listas: list
    pontos: list
    inscritos: int
    providencias: list = field(default_factory=list)
    resumo: str = ""
    matricula_fora: bool = False
    #: Os destinos que o cartão "Classificação" oferecia, por marco, para quem os abre (FR-4108).
    destinos: list = field(default_factory=list)

    @property
    def nome(self):
        return self.perfil.get("name") or ""

    @property
    def sem_inscricao(self):
        return not self.inscritos

    @property
    def grupos(self):
        """`[(grupo, quantos pontos)]`, na ordem, para o cabeçalho da matriz (FR-4104)."""
        saida = []
        for ponto in self.pontos:
            if saida and saida[-1][0] == ponto.grupo:
                saida[-1] = (ponto.grupo, saida[-1][1] + 1)
            else:
                saida.append((ponto.grupo, 1))
        return saida

    @property
    def linhas(self):
        """`[(rótulo da lista, [Celula por ponto])]` — a matriz aberta do Perfil."""
        return [(rotulo, [p.celula(lista) for p in self.pontos]) for lista, rotulo in self.listas]


@dataclass(frozen=True)
class Atencao:
    etapa: str
    texto: str = SEM_EFEITO_NO_GPS


@dataclass
class Andamento:
    perfis: list
    providencias: list
    atencoes: list
    inscricoes: dict
    #: A matriz por lista mostra o estado da convocação e das Etapas, que só quem conduz ou audita
    #: alcança (`_edital_para_classificar`). Quem só publica resultado vê o Perfil recolhido, com o
    #: resumo, como o cartão "Classificação" lhe mostrava a presença (D-004, item 1 do code review).
    ve_a_matriz: bool = False

    # A apresentação do nível 1 mora em `providencias.py`; estas propriedades só a expõem.
    @property
    def nivel_1(self):
        from processo_seletivo.interface import providencias

        return providencias.Nivel1(self.providencias)


# ---------------------------------------------------------------------------------------------
# A leitura (a única parte que toca o banco)
# ---------------------------------------------------------------------------------------------

ESTADOS_COM_ANDAMENTO = ("PUBLICADO", "ENCERRADO")


@dataclass(frozen=True)
class Alcance:
    """O que a pessoa que olha pratica e abre — as mesmas portas das telas (R-009, FR-4055)."""

    conduz: bool
    consulta: bool
    publica: bool
    julga: bool
    retifica: bool
    #: O Processo aceita atos? Encerrado ou cancelado, todo comando da comissão é recusado
    #: (`ensure_processo_accepts_changes`), e nada do andamento é "seu" — ainda que se leia.
    ativo: bool = True

    @classmethod
    def de(cls, ator, edital):
        from processo_seletivo.comissoes.domain.autorizacao import pode_gerir_comissao
        from processo_seletivo.interface import acoes
        from processo_seletivo.processos.domain.finalizacao import PROCESSO_FINAL
        from processo_seletivo.recursos.application import admitir

        conduz = pode_gerir_comissao(ator, edital.processo) is not None
        return cls(
            conduz=conduz,
            consulta=conduz or ator.can("auditoria:consultar"),
            publica=ator.can("resultado:publicar"),
            julga=ator.can(admitir.PERMISSAO),
            retifica=acoes.pode_retificar(edital, ator),
            ativo=edital.processo.status not in PROCESSO_FINAL,
        )

    def pratica(self, responsavel):
        if not self.ativo:
            return False
        return {
            CONDUZ: self.conduz,
            PUBLICA: self.publica,
            JULGA: self.julga,
            RETIFICA: self.retifica,
        }.get(responsavel, False)


def do_edital(edital, ator, *, agora=None, em_curso=None):
    """O andamento do Edital publicado ou encerrado, para este ator — ou `None` antes disso.

    `em_curso` são as Retificações em curso, que o detalhe já leu (103). Elas **não** viram
    providência (D-017): continuam ditas pelas frases da `104`, e servem aqui só à `104`.
    """
    from processo_seletivo.publicacoes.application.selectors import effective_version
    from processo_seletivo.shared.api.problems import DomainError

    if edital.status not in ESTADOS_COM_ANDAMENTO:
        return None
    agora = agora or timezone.now()
    try:
        conteudo = effective_version(edital_id=edital.id, at=agora).content
    except DomainError:
        return None
    try:
        return _Leitor(edital, ator, conteudo, agora).andamento(em_curso=em_curso)
    except Exception:  # noqa: BLE001 — orientação não derruba a página (item 2 do code review)
        # **A orientação não pode derrubar o detalhe do Edital.** A derivação lê vinte funções de
        # outras features; um conteúdo que uma delas não espere faria o detalhe responder 500 para
        # todo papel. Sem andamento, o cartão volta a ser o de antes da 127 — e o defeito fica no
        # log, com o Edital, para ser corrigido.
        logger.exception("andamento_indisponivel", extra={"edital": str(edital.id)})
        return None


def da_lista(andamento, marco_id, lista_id):
    """`(primeira em aberto desta lista, [(rótulo, célula)] das outras listas do marco)` (R-012)."""
    if andamento is None:
        return None, []
    alvo, marco_id = _chave(lista_id), str(marco_id)
    for perfil in andamento.perfis:
        pontos = [p for p in perfil.pontos if p.marco and str(p.marco.get("id")) == marco_id]
        if not pontos:
            continue
        rotulos = dict(perfil.listas)
        desta = next(
            (
                c
                for p in perfil.pontos
                if p.tipo == ETAPA or p in pontos
                for c in [p.celula(alvo)]
                if c is not None and c.em_aberto
            ),
            None,
        )
        outras = []
        for lista, rotulo in perfil.listas:
            if _chave(lista) == alvo:
                continue
            primeira = next(
                (p.celula(lista) for p in pontos if (p.celula(lista) or _VAZIA).em_aberto), None
            )
            if primeira is not None:
                outras.append((rotulos.get(lista, rotulo), primeira))
        return desta, outras
    return None, []


_VAZIA = Celula(DEPOIS)


class _Leitor:
    """Lê os fatos de um Edital uma vez, e monta o andamento com as regras puras acima."""

    def __init__(self, edital, ator, conteudo, agora):
        self.edital, self.ator, self.agora = edital, ator, agora
        self.conteudo = _com_os_metodos_resolvidos(conteudo)
        self.alcance = Alcance.de(ator, edital)
        self.etapas = [e for e in conteudo.get("stages") or [] if e.get("id")]
        self.etapas_por_id = {str(e["id"]): e for e in self.etapas}
        self.providencias = []
        self.atencoes = []
        self._conferencia = {}

    # --- o todo ----------------------------------------------------------------------------

    def andamento(self, *, em_curso=None):
        from processo_seletivo.inscricoes.domain.periodo import periodo_de_inscricoes

        self.periodo = periodo_de_inscricoes(self.conteudo, self.agora)
        self.perfil_de, self.inscritos_por_perfil = self._perfis_das_inscricoes()
        self.trabalho = self._trabalho_da_104(em_curso)
        expectativa = expectativa_das_etapas(self.conteudo)
        self.expectativa_do_edital = expectativa
        self.etapas_no_edital = self._etapas_no_edital(expectativa)
        perfis = [
            self._perfil(perfil)
            for perfil in self.conteudo.get("profiles") or []
            if perfil.get("classificationMilestones")
        ]
        self._providencias_da_104(em_curso)
        return Andamento(
            perfis=perfis,
            providencias=self.providencias,
            atencoes=self.atencoes,
            ve_a_matriz=self.alcance.consulta,
            inscricoes={
                "estado": self.periodo.estado,
                "fim": self.periodo.fim,
                "cancelado": self.periodo.cancelado,
                "enviadas": sum(self.inscritos_por_perfil.values()),
            },
        )

    def _perfis_das_inscricoes(self):
        """O Perfil de cada inscrição e quantas por Perfil, numa consulta para o Edital (D-013)."""
        from processo_seletivo.inscricoes.models import Inscricao

        perfil_de, quantas = {}, {}
        for inscricao, perfil in Inscricao.objects.filter(
            edital=self.edital, status=Inscricao.Status.SUBMETIDA
        ).values_list("id", "profile_id"):
            perfil_de[str(inscricao)] = str(perfil)
            quantas[str(perfil)] = quantas.get(str(perfil), 0) + 1
        return perfil_de, quantas

    # --- as Etapas (no Edital inteiro, como a distribuição as lê) -------------------------

    def _etapas_no_edital(self, expectativa):
        from processo_seletivo.avaliacoes.application.selectors import resumo_da_etapa
        from processo_seletivo.avaliacoes.domain.conjunto import recusa_por_inscricoes_em_curso
        from processo_seletivo.classificacao.domain import faixa
        from processo_seletivo.resultados.application import prontidao

        em_curso = recusa_por_inscricoes_em_curso(self.conteudo, self.agora)
        governadas = {
            faixa.etapa_governada(m.get("cutRule"))
            for p in self.conteudo.get("profiles") or []
            for m in p.get("classificationMilestones") or []
            if faixa.etapa_governada(m.get("cutRule"))
        }
        minhas = {
            str(objeto.chave[2]): objeto
            for objeto in self.trabalho
            if objeto.natureza == "avaliacao"
        }
        saida = {}
        for etapa in self.etapas:
            eid = str(etapa["id"])
            nome = etapa.get("name") or ""
            fatos = {"nome": nome, "expectativa": expectativa.get(eid, SEM_EFEITO)}
            if fatos["expectativa"] == SEM_EFEITO:
                self.atencoes.append(Atencao(nome))
                resumo, _ = situacoes_da_etapa(fatos)
                # A faixa da Lista (104) diz "Avaliar" a quem tem inscrição atribuída, e o detalhe
                # não pode calar (item 11 da revisão): a Atenção não cobra, mas a mesa existe.
                minha = minhas.get(eid)
                for celula in _avaliar_minhas(
                    {
                        "minhas": _pendentes_do_objeto(minha),
                        "url_da_mesa": minha.url if minha else "",
                    }
                ):
                    self._acrescentar(celula, onde=nome, chave=("etapa", eid, AVALIAR))
                saida[eid] = {"resumo": resumo, "estados": {}, "participantes": set()}
                continue
            url = (
                reverse("interface:distribuicao", args=[self.edital.id, eid])
                if self.alcance.conduz
                else ""
            )
            minha = minhas.get(eid)
            fatos.update(
                url=url,
                governada=eid in governadas,
                inscricoes_em_curso=_frase(em_curso.detail) if em_curso else "",
                fim_das_inscricoes=self.periodo.fim,
                minhas=_pendentes_do_objeto(minha),
                url_da_mesa=minha.url if minha else "",
            )
            panorama = {}
            if not em_curso:
                panorama = prontidao.panorama_da_etapa(
                    edital=self.edital, etapa=etapa, conteudo=self.conteudo
                )
                resumo_da_tela = resumo_da_etapa(edital=self.edital, etapa=etapa, panorama=panorama)
                fatos.update(
                    bloqueio=panorama["bloqueio_da_etapa"],
                    com_faixa=(
                        prontidao.faixas_que_governam(
                            self.edital, eid, conteudo=self.conteudo
                        ).exists()
                        if eid in governadas
                        else True
                    ),
                    participantes=resumo_da_tela.get("participantes", resumo_da_tela["inscricoes"]),
                    carentes=resumo_da_tela["carentes"],
                    sem_conclusao=resumo_da_tela["sem_conclusao"],
                    prontas=resumo_da_tela.get("prontas", 0),
                    consolidadas=resumo_da_tela.get("consolidadas", 0),
                    reavaliacoes=resumo_da_tela.get("reavaliacoes", 0),
                )
            resumo, providencias = situacoes_da_etapa(fatos)
            for celula in providencias:
                self._acrescentar(celula, onde=nome, chave=("etapa", eid))
            saida[eid] = {
                "resumo": resumo,
                "estados": panorama.get("estados") or {},
                "participantes": {str(i) for i in panorama.get("participantes") or ()},
            }
        return saida

    def _etapa_no_perfil(self, eid, perfil_id, expectativa_do_perfil):
        lida = self.etapas_no_edital.get(eid)
        if lida is None:
            return _c(NAO_SE_APLICA, natureza=ETAPA)
        if expectativa_do_perfil.get(eid) == SEM_EFEITO:
            return _c(NAO_SE_APLICA, natureza=ETAPA, nota="sem efeito no GPS")
        do_perfil = [i for i in lida["participantes"] if self.perfil_de.get(i) == perfil_id]
        estados = lida["estados"]
        consolidadas = sum(
            1
            for i in do_perfil
            if (estados.get(_uuid(i)) or estados.get(i) or ("",))[0] == "consolidada"
        )
        reavaliacoes = sum(
            1
            for i in do_perfil
            if (estados.get(_uuid(i)) or estados.get(i) or ("",))[0] == "reavaliacao-determinada"
        )
        return situacao_da_etapa_no_perfil(
            lida["resumo"],
            participantes=len(do_perfil),
            consolidadas=consolidadas,
            reavaliacoes=reavaliacoes,
        )

    # --- um Perfil -------------------------------------------------------------------------

    def _perfil(self, perfil):
        from processo_seletivo.editais.domain.recortes import recortes_do_perfil

        pid = str(perfil.get("id"))
        marcos = list(perfil.get("classificationMilestones") or [])
        expectativa = expectativa_das_etapas(self.conteudo, [perfil])
        # **A Etapa que outro Perfil lê fica fora da matriz deste** (item 3 da revisão do B2): para
        # ele ela não muda nada, mas "sem efeito no GPS" seria falso — o nível 1 a cobra pelo
        # Edital. "Sem efeito" é só a que nada consome no Edital inteiro (D-010).
        citadas = _citadas_pelos_marcos(marcos)
        etapas_do_perfil = [
            e
            for e in self.etapas
            if expectativa.get(str(e["id"])) == ESPERADA
            or self.expectativa_do_edital.get(str(e["id"])) == SEM_EFEITO
            # A que um marco do Perfil cita fica, ainda que sem efeito nele: sem ela a `jornada()`
            # perde a "última Etapa" do marco e o põe no começo (item 4 do code review do B2).
            or str(e["id"]) in citadas
        ]
        pontos = sequencia_do_perfil(etapas_do_perfil, marcos, expectativa)
        listas = recortes_do_perfil(self.conteudo, perfil_id=perfil.get("id"))
        inscritos = self.inscritos_por_perfil.get(pid, 0)
        formas = {"por sorteio" if por_sorteio(m) else "por pontuação" for m in marcos}
        no_perfil = PerfilNoAndamento(
            perfil=perfil,
            forma=" e ".join(sorted(formas, reverse=True)),
            listas=listas,
            pontos=pontos,
            inscritos=inscritos,
        )
        etapas_do_perfil = {}
        for ponto in pontos:
            if ponto.tipo == ETAPA:
                eid = str(ponto.etapa.get("id"))
                celula = self._etapa_no_perfil(eid, pid, expectativa)
                etapas_do_perfil[eid] = celula
                ponto.celulas = {_chave(lista): celula for lista, _ in listas}
        for marco in marcos:
            self._marco(no_perfil, marco, etapas_do_perfil, listas, expectativa)
        if not inscritos:
            # **O Perfil sem inscrição é uma linha só** (FR-4102): nada dele é providência, e o que
            # já existe (a ordem vazia emitida) continua dito como feito.
            self.providencias = [p for p in self.providencias if p.perfil_id != pid]
        # **Só as do Perfil** (item 3 do code review do B2): as das Etapas são do Edital inteiro e
        # entrariam na linha de cada Perfil que as vê; o andamento delas está em "Etapas X de Y".
        no_perfil.providencias = [p for p in self.providencias if p.perfil_id == pid]
        no_perfil.resumo = resumo_do_perfil(no_perfil)
        no_perfil.matricula_fora = matricula_fora(no_perfil)
        return no_perfil

    def _marco(self, no_perfil, marco, etapas_do_perfil, listas, expectativa):
        from processo_seletivo.classificacao.domain import faixa
        from processo_seletivo.classificacao.domain.desempate import etapas_que_a_ordem_le
        from processo_seletivo.interface import conducao_do_marco
        from processo_seletivo.shared.api.problems import DomainError

        perfil = no_perfil.perfil
        pontos = {p.tipo: p for p in no_perfil.pontos if p.marco is marco}
        try:
            indicador = conducao_do_marco.indicador_do_marco(
                self.edital,
                self.conteudo,
                perfil,
                marco,
                pode_classificar=self.alcance.consulta,
                pode_publicar=self.alcance.publica,
            )
        except DomainError as recusa:
            # **A recusa da condução não vira recomendação** (item 6 da revisão): sem células, a
            # ordem cairia em *Pendente*. Cada ponto do marco fica *Impedido*, com a frase dela.
            impedida = _c(
                IMPEDIDO, natureza=ORDEM, ato="Conduzir o marco", razao=_frase(recusa.detail)
            )
            for ponto in pontos.values():
                for lista, _ in listas:
                    ponto.celulas[_chave(lista)] = replace(impedida, natureza=ponto.tipo)
            self._acrescentar(impedida, onde=no_perfil.nome, marco=marco, perfil=perfil)
            return
        por_lista = {_chave(linha["lista_id"]): linha["celulas"] for linha in indicador["linhas"]}
        sorteado = por_sorteio(marco)
        sorteio_lido = self._sorteio(perfil, marco, expectativa) if sorteado else None
        governada_id = faixa.etapa_governada(marco.get("cutRule"))
        governada = etapas_do_perfil.get(str(governada_id)) if governada_id else None
        nome_da_governada = (self.etapas_por_id.get(str(governada_id)) or {}).get("name")
        faltam = [
            (self.etapas_por_id.get(str(e)) or {}).get("name") or str(e)
            for e in ([] if sorteado else etapas_que_a_ordem_le(marco))
            if not feita(etapas_do_perfil.get(str(e)))
        ]
        semente = sorteio_lido["semente"] if sorteado else None
        if semente is not None and SEMENTE in pontos:
            for lista, _ in listas:
                pontos[SEMENTE].celulas[_chave(lista)] = semente
            self._acrescentar(
                semente,
                onde=no_perfil.nome,
                marco=None if sorteio_lido.get("chave_da_semente") else marco,
                perfil=perfil,
                chave=sorteio_lido.get("chave_da_semente"),
            )
        curtos = _rotulos_curtos(perfil)
        for lista, rotulo in listas:
            chave = _chave(lista)
            celulas = por_lista.get(chave) or {}
            onde = f"{no_perfil.nome} · {curtos.get(chave, rotulo)}"
            if sorteado:
                relacao = sorteio_lido["relacoes"].get(chave) or _c(DEPOIS, natureza=RELACAO)
                ordem = situacao_do_sorteio(
                    {
                        "relacao": relacao,
                        "semente": semente,
                        "ordem": celulas.get("ordenar"),
                        "anulavel": sorteio_lido["anulavel"].get(chave, False),
                        "url": sorteio_lido["url"](lista),
                    }
                )
                derivadas = {RELACAO: relacao, SORTEIO: ordem}
            else:
                ordem = situacao_da_ordem({"celula": celulas.get("ordenar"), "faltam": faltam})
                derivadas = {ORDEM: ordem}
            if CORTE in pontos:
                derivadas[CORTE] = situacao_do_corte(
                    {"celula": celulas.get("cortar"), "ordem": ordem}
                )
            derivadas[APURACAO] = situacao_da_apuracao(
                {
                    "celula": celulas.get("apurar"),
                    "ordem": ordem,
                    "corte": derivadas.get(CORTE),
                    "governada": governada,
                    "nome_da_governada": nome_da_governada,
                }
            )
            derivadas[RESULTADO] = self._resultado(marco, lista, celulas.get("publicar"), ordem)
            convocacao, da_convocacao = self._convocacao(
                perfil,
                marco,
                lista,
                derivadas[APURACAO],
                derivadas.get(CORTE),
                governada,
                nome_da_governada or "",
            )
            derivadas[CONVOCACAO] = convocacao
            for tipo, celula in derivadas.items():
                if tipo in pontos:
                    pontos[tipo].celulas[chave] = celula
            for tipo in (RELACAO, SORTEIO, ORDEM, CORTE, APURACAO, RESULTADO):
                if tipo in derivadas:
                    self._acrescentar(
                        derivadas[tipo],
                        onde=onde,
                        marco=marco,
                        perfil=perfil,
                        lista=(lista, curtos.get(chave, rotulo)),
                    )
            for celula in da_convocacao:
                self._acrescentar(
                    celula,
                    onde=onde,
                    marco=marco,
                    perfil=perfil,
                    lista=(lista, curtos.get(chave, rotulo)),
                )

    # --- o sorteio -------------------------------------------------------------------------

    def _sorteio(self, perfil, marco, expectativa):
        from processo_seletivo.shared.api.problems import DomainError
        from processo_seletivo.sorteios.application import previa

        marco_id = str(marco.get("id"))
        base = reverse("interface:sorteio", args=[self.edital.id, marco_id])

        def url(lista):
            if not self.alcance.consulta:
                return ""
            return f"{base}?lista={lista}" if lista else base

        try:
            lido = previa.recortes_do_marco(
                edital=self.edital, perfil_id=perfil.get("id"), marco_id=marco_id, at=self.agora
            )
        except DomainError as recusa:
            impedida = _c(IMPEDIDO, natureza=SEMENTE, razao=_frase(recusa.detail), url=url(None))
            return {
                "semente": impedida,
                "relacoes": {},
                "url": url,
                "anulavel": {},
                "chave_da_semente": None,
            }
        metodo = lido.get("metodo") or {}
        habilitacao_id = str(metodo.get("qualifyingStageId") or "")
        habilitacao = (
            self._etapa_no_perfil(habilitacao_id, str(perfil.get("id")), expectativa)
            if habilitacao_id
            else None
        )
        em_curso = lido.get("inscricoes_em_curso")
        relacoes = {}
        for recorte in lido["recortes"]:
            lista = recorte["lista_id"] or None
            relacoes[_chave(lista)] = situacao_da_relacao(
                {
                    "congelada": recorte["congelada"],
                    "participantes": len(recorte.get("participantes") or []),
                    "projetados": recorte["projetados"],
                    "diagnostico": recorte["diagnostico_da_relacao"],
                    "habilitacao": habilitacao,
                    "inscricoes_em_curso": _frase(em_curso.detail) if em_curso else "",
                    "fim_das_inscricoes": self.periodo.fim,
                    "congelar_inviavel": lido.get("congelar_agora_inviavel"),
                    "url": url(lista),
                }
            )
        semente = situacao_da_semente(
            {
                "alguma_congelada": any(r["congelada"] for r in lido["recortes"]),
                "observada": _ocorrencia_valida(lido.get("ocorrencia")),
                "sem_instante": lido.get("ocorrencia") is not None
                and not _ocorrencia_valida(lido.get("ocorrencia")),
                "recusa": lido.get("recusa_da_ocorrencia"),
                "ocorre_em": lido.get("ocorre_em"),
                "agora": self.agora,
                "referencia": lido.get("proxima_referencia") or "",
                "url": url(None),
            }
        )
        anulavel = {
            _chave(r["lista_id"] or None): bool(
                r.get("relacoes_sucessoras") and r.get("ocorrencias_disponiveis")
            )
            for r in lido["recortes"]
        }
        metodo = lido.get("metodo") or {}
        return {
            "semente": semente,
            "relacoes": relacoes,
            "url": url,
            "anulavel": anulavel,
            # Uma observação serve a todo marco da mesma fonte e referência (item 14 da revisão).
            "chave_da_semente": (SEMENTE, metodo.get("source") or "", semente.nota or ""),
        }

    # --- o resultado -----------------------------------------------------------------------

    def _resultado(self, marco, lista, celula, ordem):
        from processo_seletivo.classificacao.application.selectors import ato_vigente
        from processo_seletivo.divulgacao.domain import publicabilidade
        from processo_seletivo.shared.api.problems import DomainError

        celula = celula or {}
        fatos = {"celula": celula, "ordem": ordem}
        estado, nota = celula.get("estado"), celula.get("nota") or ""
        precisa_do_ato = (
            estado == "obsoleto"
            or (estado == "feito" and "preliminar" in nota)
            or (estado == "falta" and ordem is not None and ordem.situacao in (FEITO, OBSOLETO))
        )
        if not precisa_do_ato:
            return situacao_do_resultado(fatos)
        marco_id = str(marco.get("id"))
        ato = ato_vigente(edital=self.edital, marco_id=marco_id, lista_id=lista)
        if ato is not None and self.alcance.publica:
            fatos["url_da_previa"] = reverse(
                "interface:previa-de-publicacao", args=[self.edital.id, marco_id, ato.id]
            )
        if ato is not None and (ordem is None or ordem.situacao != OBSOLETO):
            # **A mesma aferição da prévia** (item 1 da revisão): sucedido, desatualizado, corte
            # obsoleto e reingresso impedem as duas naturezas, e a prévia não oferece o botão.
            preliminar = estado == "feito"
            try:
                afericao = publicabilidade.aferir(
                    edital=self.edital,
                    marco_id=marco_id,
                    ato=ato,
                    natureza="DEFINITIVA" if preliminar else "",
                    lista_id=lista,
                    at=self.agora,
                )
                lida = {
                    "nivel": afericao.nivel,
                    "codigo": afericao.codigo,
                    "mensagem": afericao.mensagem,
                }
            except DomainError as recusa:
                lida = {
                    "nivel": publicabilidade.IMPEDIMENTO,
                    "codigo": recusa.code,
                    "mensagem": recusa.detail,
                }
            fatos["definitiva" if preliminar else "afericao"] = lida
        return situacao_do_resultado(fatos)

    # --- a convocação ----------------------------------------------------------------------

    def _convocacao(self, perfil, marco, lista, apuracao, corte=None, governada=None, nome=""):
        from processo_seletivo.classificacao.application.corte import linha_do_quadro
        from processo_seletivo.convocacao.application import fluxo
        from processo_seletivo.convocacao.application import selectors as convocacao
        from processo_seletivo.convocacao.domain import nomes
        from processo_seletivo.shared.api.problems import DomainError

        marco_id = str(marco.get("id"))
        base = reverse("interface:convocacao", args=[self.edital.id, marco_id])
        url = (f"{base}?lista={lista}" if lista else base) if self.alcance.consulta else ""
        if corte is not None and not feita(corte):
            # **No marco que corta, a convocação também espera o corte** (D-018): a fila é de quem
            # a faixa alcançou, e a lista apurada sem corte não tem ninguém a chamar.
            return (
                _c(
                    DEPOIS,
                    natureza=CONVOCACAO,
                    razao="a fila é de quem a faixa do corte alcançou, e o corte desta lista ainda "
                    "não está vigente",
                ),
                [],
            )
        if apuracao.situacao != FEITO or (governada is not None and not feita(governada)):
            return situacoes_da_convocacao(
                {
                    "apuracao": apuracao,
                    "url": url,
                    "governada": governada,
                    "nome_da_governada": nome,
                }
            )
        recorte = {
            "edital": self.edital,
            "perfil_id": perfil.get("id"),
            "marco_id": marco_id,
            "lista_id": lista,
            "at": self.agora,
        }
        try:
            leitura = convocacao.leitura_do_recorte(**recorte)
            titulares = fluxo.previa_dos_titulares(**recorte, leitura=leitura)
            vencidos = fluxo.previa_dos_vencidos(**recorte, leitura=leitura)
            pendentes = fluxo.previa_das_pendentes(**recorte, leitura=leitura)
        except DomainError as recusa:
            celula = _c(IMPEDIDO, natureza=CONVOCACAO, razao=_frase(recusa.detail), url=url)
            return celula, [celula]
        linhas = leitura["linhas"]
        em_curso = [lin for lin in linhas if lin["estado"] == nomes.CONVOCADO_PRAZO_EM_CURSO]
        documentos = self._documentos(linhas)
        confere = self.alcance.conduz or self._confere(perfil)
        fatos = {
            "apuracao": apuracao,
            "impedimento": titulares.get("impedimento"),
            "titulares": len(titulares.get("pessoas") or []),
            "pendentes": len(pendentes.get("linhas") or []),
            "por_publicacao": bool(pendentes.get("porPublicacao")),
            "vencidos": len(vencidos.get("linhas") or []),
            "em_curso": len(em_curso),
            "ate": min(
                (lin["convocacao"].vencimento for lin in em_curso if lin["convocacao"].vencimento),
                default=None,
            ),
            "em_aberto": sum(1 for lin in linhas if lin["desfecho"] is None),
            "faltando": (leitura.get("ocupacao") or {}).get("faltando") or 0,
            "fila": len(leitura.get("fila") or []),
            "esgotou": leitura.get("esgotou"),
            "corte_vigente": corte is not None and corte.situacao == FEITO,
            "com_quadro": linha_do_quadro(self.conteudo, perfil_id=perfil.get("id"), lista_id=lista)
            is not None,
            "conferir": documentos["conferir"],
            "decidir": documentos["decidir"],
            "aguardando_documentos": documentos["aguardando"],
            "convocadas": leitura.get("convocadas") or 0,
            "desfechadas": leitura.get("respondidas") or 0,
            "url": url,
            # Quem só confere abre a convocação do Perfil dele (115, FR-3595), e não as outras.
            "url_da_conferencia": (f"{base}?lista={lista}" if lista else base)
            if (self.alcance.consulta or confere)
            else "",
            "url_da_ocupacao": reverse("interface:ocupacao", args=[self.edital.id, marco_id])
            if self.alcance.consulta
            else "",
        }
        return situacoes_da_convocacao(fatos)

    def _documentos(self, linhas):
        """Quantas chamadas têm documento a conferir, quantas estão prontas, e quantas aguardam.

        A mesma leitura que a condução faz por recorte (`_documentos_por_linha` da view), em
        consultas de número fixo, e o estado documental que ela rotula (115, 117).
        """
        from processo_seletivo.convocacao.application import documentos as documentos_app

        contagem = {"conferir": 0, "decidir": 0, "aguardando": 0}
        abertas = [lin for lin in linhas if lin["desfecho"] is None]
        if not abertas:
            return contagem
        raizes = documentos_app.raizes_das(lin["convocacao"] for lin in abertas)
        leituras = documentos_app.leituras_por_chamada(set(raizes.values()))
        for linha in abertas:
            leitura = leituras.get(raizes[linha["convocacao"].id].id)
            if leitura is None or not leitura.pedidos:
                continue
            # **Com pendência é o candidato que age** (item 3 da revisão): a conferência já
            # marcou o item, e ele complementa; não há o que conferir.
            if leitura.estado == "PARA_CONFERIR":
                contagem["conferir"] += 1
            elif leitura.estado == "PRONTA_PARA_DECIDIR":
                contagem["decidir"] += 1
            elif leitura.estado in ("AGUARDANDO_DOCUMENTACAO", "COM_PENDENCIA"):
                contagem["aguardando"] += 1
        return contagem

    def _confere(self, perfil):
        """Se a pessoa confere documentos deste Perfil: uma consulta por Perfil, e não por lista."""
        from processo_seletivo.comissoes.domain.autorizacao import pode_conferir_documentos

        chave = str(perfil.get("id"))
        if chave not in self._conferencia:
            self._conferencia[chave] = (
                pode_conferir_documentos(self.ator, self.edital, perfil.get("id")) is not None
            )
        return self._conferencia[chave]

    # --- os objetos da 104 -----------------------------------------------------------------

    def _trabalho_da_104(self, em_curso):
        """Os objetos de trabalho da pessoa **neste** Edital, pela derivação da `104` (R-010)."""
        from processo_seletivo.interface import trabalho

        return [
            objeto
            for objeto in trabalho.do_ator(
                self.ator, [self.edital], em_curso={self.edital.id: em_curso or []}
            )
            if objeto.edital.id == self.edital.id
        ]

    def _providencias_da_104(self, em_curso):
        """O recurso: da pessoa, pela `104`; de outro papel, pela mesma contagem que a coluna lê."""
        from processo_seletivo.interface import acoes
        from processo_seletivo.interface.providencias import Providencia

        recursos = [o for o in self.trabalho if o.natureza == "recursos"]
        if recursos:
            objeto = recursos[0]
            self.providencias.append(
                Providencia.do_objeto(objeto, natureza=RECURSO, responsavel=JULGA)
            )
        else:
            quantos = acoes.recursos_aguardando_decisao(self.edital)
            if quantos:
                self.providencias.append(
                    Providencia(
                        natureza=RECURSO,
                        chave=("recursos", self.edital.id),
                        onde="Recursos",
                        ato=f"Decidir {_n(quantos, 'recurso', 'recursos')}",
                        situacao=PENDENTE,
                        responsavel=JULGA,
                        contagem=quantos,
                    )
                )
        # **A Retificação não entra aqui** (D-017): ela é trabalho sobre o documento, e o cartão já
        # a diz pelas frases da `104` (FR-2819, FR-2820), logo abaixo das providências. Repeti-la
        # aqui faria o mesmo trabalho aparecer duas vezes no mesmo cartão.

    # --- a providência ---------------------------------------------------------------------

    def _acrescentar(self, celula, *, onde, marco=None, perfil=None, lista=None, chave=None):
        from processo_seletivo.interface.providencias import Providencia

        if not celula.em_aberto:
            return
        if celula.situacao not in A_PRATICAR:
            sua = False
        elif celula.natureza == AVALIAR:
            # O link da mesa só existe para quem tem inscrição pendente nela (a carga da `104`).
            sua = bool(celula.url)
        elif celula.responsavel == CONFERE:
            sua = self._pode_conferir(perfil)
        else:
            sua = self.alcance.pratica(celula.responsavel)
        if celula.quem_resolve == RETIFICA and self.edital.status != "PUBLICADO":
            # Só o Edital publicado se retifica (item 4 da revisão).
            celula = replace(celula, quem_resolve="")
        self.providencias.append(
            Providencia.da_celula(
                celula,
                onde=onde,
                sua=sua,
                url_do_marco=(
                    reverse("interface:marco", args=[self.edital.id, marco.get("id")])
                    if marco and (self.alcance.consulta or self.alcance.publica)
                    else ""
                ),
                pode_resolver=self.alcance.pratica(celula.quem_resolve),
                url_da_saida=(
                    reverse("interface:retificar", args=[self.edital.id])
                    if celula.quem_resolve == RETIFICA and self.alcance.retifica
                    else ""
                ),
                chave=chave
                or (
                    celula.natureza,
                    str(marco.get("id")) if marco else "",
                    celula.situacao,
                    celula.responsavel,
                    celula.ato,
                ),
                marco_id=str(marco.get("id")) if marco else "",
                perfil_id=str(perfil.get("id")) if perfil else "",
                lista=lista,
                lugar=(perfil.get("name") or "") if (perfil and lista) else onde,
            )
        )

    def _pode_conferir(self, perfil):
        return self.alcance.conduz or (perfil is not None and self._confere(perfil))


# ---------------------------------------------------------------------------------------------
# Texto
# ---------------------------------------------------------------------------------------------


def _com_os_metodos_resolvidos(conteudo):
    """O conteúdo com cada marco por sorteio levando o método que o governa (item 7 da revisão).

    O método pode vir do marco ou ser o comum do Edital (029, FR-429), e a forma da ordem é a de
    `marco_ordena_por_sorteio`, que é a que a condução usa. As regras puras daqui leem só o marco;
    resolver uma vez, na entrada, é o que impede a composição (D-011) e a expectativa (D-019) de
    lerem o marco do Edital que declara o método uma vez só como se não sorteasse.
    """
    from processo_seletivo.editais.domain import marcos

    perfis = []
    for perfil in conteudo.get("profiles") or []:
        resolvidos = []
        for marco in perfil.get("classificationMilestones") or []:
            if marco.get("id") and marcos.marco_ordena_por_sorteio(
                conteudo, perfil_id=perfil.get("id"), marco_id=marco["id"]
            ):
                metodo = marcos.metodo_que_governa(
                    conteudo, perfil_id=perfil.get("id"), marco_id=marco["id"]
                )
                marco = {**marco, "orderProduction": "POR_SORTEIO", "drawMethod": metodo or {}}
            resolvidos.append(marco)
        perfis.append({**perfil, "classificationMilestones": resolvidos})
    return {**conteudo, "profiles": perfis}


def _citadas_pelos_marcos(marcos):
    """As Etapas que os marcos citam: enumeradas, governadas, de habilitação ou de desempate."""
    from processo_seletivo.classificacao.domain import faixa
    from processo_seletivo.classificacao.domain.desempate import etapas_do_desempate

    saida = set()
    for marco in marcos:
        saida.update(str(e) for e in marco.get("stages") or [])
        saida.update(etapas_do_desempate(marco))
        governada = faixa.etapa_governada(marco.get("cutRule"))
        if governada:
            saida.add(str(governada))
        habilitacao = (marco.get("drawMethod") or {}).get("qualifyingStageId")
        if habilitacao:
            saida.add(str(habilitacao))
    return saida


def _rotulos_curtos(perfil):
    """`{lista: rótulo}` para o nível 1: "Ampla concorrência" e o código de cada Modalidade (D-020).

    O rótulo da derivação única diz o que o recorte é ("Ampla concorrência (linha geral do
    quadro)", "Pessoa com Deficiência (PcD) (PCD)"), e é o certo na matriz e nas telas de ato. Na
    linha de uma providência, ao lado do nome do Perfil, ele dobrava a linha; o código é o que o
    Edital publica e o que a pessoa reconhece.
    """
    saida = {"": "Ampla concorrência"}
    for modalidade in perfil.get("competitionModalities") or []:
        if isinstance(modalidade, dict) and modalidade.get("id"):
            saida[str(modalidade["id"])] = modalidade.get("code") or modalidade.get("name") or ""
    return saida


def _ocorrencia_valida(ocorrencia):
    """A ocorrência com que a tela do sorteio oferece sortear (item 5 da revisão)."""
    return (
        ocorrencia is not None
        and not ocorrencia.indisponivel
        and ocorrencia.ocorrida_nao_antes_de is not None
    )


def _chave(lista_id):
    return str(lista_id) if lista_id else ""


def _uuid(texto):
    from uuid import UUID

    try:
        return UUID(str(texto))
    except ValueError:
        return texto


def _pendentes_do_objeto(objeto):
    """As pendentes do avaliador, pela quantidade que o objeto da `104` carrega."""
    return (objeto.quantidade or 0) if objeto is not None else 0


def _n(quantos, singular, plural=None):
    quantos = quantos or 0
    if plural is None:
        plural = singular + "s"
    return f"{quantos} {singular if quantos == 1 else plural}"


def _data(instante):
    if instante is None:
        return ""
    if isinstance(instante, datetime):
        return f"{timezone.localtime(instante):%d/%m/%Y}"
    return f"{instante:%d/%m/%Y}"


def _lista_de_nomes(nomes):
    nomes = list(nomes)
    if len(nomes) <= 1:
        return "".join(nomes)
    return ", ".join(nomes[:-1]) + " e " + nomes[-1]


def _sem_marcacao(texto):
    return texto.replace("**", "")


def _frase(texto):
    """A frase da tela do ato, sem o ponto final — a apresentação acrescenta o dela."""
    texto = _sem_marcacao(texto or "").strip()
    return texto[:-1] if texto.endswith(".") else texto


# ---------------------------------------------------------------------------------------------
# O nível 2: o "Andamento da seleção" (B2, FR-4100 a FR-4110) — puro
# ---------------------------------------------------------------------------------------------

#: Como cada ponto de marco se diz no resumo em palavras ("sorteio 3 de 3").
NOMES_NO_RESUMO = {
    RELACAO: "relação",
    SORTEIO: "sorteio",
    ORDEM: "ordem",
    CORTE: "corte",
    APURACAO: "apuração",
}


def resumo_do_perfil(perfil):
    """A linha recolhida do Perfil, em palavras (FR-4101): quantas listas e onde cada ato está.

    **Contagem de feitos sobre os que se aplicam**, como a condução do marco conta (049, FR-814):
    contar o obsoleto faria o Perfil parecer pronto com um ato que o sistema sabe estar para trás. O
    resultado diz a natureza do que foi publicado, e a convocação diz quantas providências tem — a
    contagem que manda olhar, e não um percentual.
    """
    listas = len(perfil.listas)
    partes = [f"{listas} {'lista' if listas == 1 else 'listas'}"]
    etapas = [
        _primeira(p) for p in perfil.pontos if p.tipo == ETAPA and p.grupo != GRUPO_SEM_EFEITO
    ]
    # Sobre as que se aplicam, como os atos do marco (item 9 da revisão do B2): a Etapa em que
    # ninguém do Perfil participa não conta nem como feita nem como falta.
    etapas = [c for c in etapas if c is not None and c.situacao != NAO_SE_APLICA]
    if etapas:
        feitas = sum(1 for c in etapas if c.situacao == FEITO)
        partes.append(f"Etapas {feitas} de {len(etapas)}")
    for tipo, nome in NOMES_NO_RESUMO.items():
        celulas = [c for p in perfil.pontos if p.tipo == tipo for c in _por_lista(p, perfil)]
        aplicaveis = [c for c in celulas if c.situacao != NAO_SE_APLICA]
        if aplicaveis:
            feitas = sum(1 for c in aplicaveis if c.situacao == FEITO)
            partes.append(f"{nome} {feitas} de {len(aplicaveis)}")
    partes.append(_resultado_em_palavras(perfil))
    from processo_seletivo.interface.providencias import agrupar

    # Agrupadas como o nível 1 as agrupa (D-016), inclusive as que esperam; as das Etapas, que são
    # do Edital, ficam no nível 1 e em "Etapas X de Y".
    em_aberto = len(agrupar(perfil.providencias))
    if em_aberto:
        partes.append(
            f"{em_aberto} {'providência' if em_aberto == 1 else 'providências'} em aberto"
        )
    return " · ".join(p for p in partes if p)


def _resultado_em_palavras(perfil):
    """A natureza do que o público lê, sobre as listas em que há o que divulgar (item 1).

    Lê a nota de qualquer situação: o preliminar na janela recursal é *Aguarda*, e continua
    publicado. "Definitivo" só quando todas as listas o têm; publicado em parte, diz quantas.
    """
    resultados = [c for p in perfil.pontos if p.tipo == RESULTADO for c in _por_lista(p, perfil)]
    aplicaveis = [c for c in resultados if c.situacao != NAO_SE_APLICA]
    if not aplicaveis:
        return ""
    publicadas = [c for c in aplicaveis if "resultado" in (c.nota or "") or c.situacao == OBSOLETO]
    definitivas = [c for c in publicadas if "definitivo" in (c.nota or "")]
    if not publicadas:
        return "resultado não publicado"
    if len(publicadas) < len(aplicaveis):
        return f"resultado publicado em {len(publicadas)} de {len(aplicaveis)} listas"
    if len(definitivas) == len(aplicaveis):
        return "resultado definitivo"
    return "resultado preliminar"


def _por_lista(ponto, perfil):
    return [c for lista, _ in perfil.listas for c in [ponto.celula(lista)] if c is not None]


def _primeira(ponto):
    return next(iter(ponto.celulas.values()), None)


def matricula_fora(perfil):
    """FR-4109, D-003: toda convocação do Perfil tem desfecho, e nada falta ocupar."""
    convocacoes = [c for p in perfil.pontos if p.tipo == CONVOCACAO for c in _por_lista(p, perfil)]
    aplicaveis = [c for c in convocacoes if c.situacao != NAO_SE_APLICA]
    # `contagem` da célula feita é quantas convocações seguem sem desfecho (item 5 da revisão).
    return bool(aplicaveis) and all(
        c.situacao == FEITO and c.nota and c.contagem == 0 for c in aplicaveis
    )


def linha_das_inscricoes(inscricoes):
    """ "Inscrições encerradas em 20/10/2026 · 14 enviadas" (FR-4101), do período publicado."""
    from processo_seletivo.inscricoes.domain import periodo

    enviadas = inscricoes.get("enviadas") or 0
    quantas = f"{enviadas} {'enviada' if enviadas == 1 else 'enviadas'}"
    fim = inscricoes.get("fim")
    estado = inscricoes.get("estado")
    if inscricoes.get("cancelado"):
        # O período cancelado é encerrado sem ter terminado (`periodo.Periodo`, item 2 da revisão
        # do B2): "encerradas em" com o término publicado poria uma data que não aconteceu.
        return f"Período de inscrições cancelado · {quantas}"
    if estado == periodo.ENCERRADO:
        quando = f" em {_data(fim)}" if fim else ""
        return f"Inscrições encerradas{quando} · {quantas}"
    if estado == periodo.ABERTO:
        ate = (
            f" até {timezone.localtime(fim):%d/%m/%Y às %H:%M}"
            if fim
            else ", sem término declarado"
        )
        return f"Inscrições abertas{ate} · {quantas} até agora"
    if estado == periodo.FUTURO:
        return "Inscrições ainda não abertas"
    return f"Período de inscrições não designado · {quantas}"


__all__ = [
    "AGUARDA",
    "DEPOIS",
    "FEITO",
    "IMPEDIDO",
    "NAO_SE_APLICA",
    "OBSOLETO",
    "PENDENTE",
    "Andamento",
    "Celula",
    "da_lista",
    "do_edital",
    "expectativa_das_etapas",
    "linha_das_inscricoes",
    "resumo_do_perfil",
    "sequencia_do_perfil",
]
