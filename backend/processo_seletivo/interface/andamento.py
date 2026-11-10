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

#: O que o público lê de uma lista (135, FR-4677).
NADA, PRELIMINAR, DEFINITIVO = "nada", "preliminar", "definitivo"
_DIVULGADO_POR_NATUREZA = {"PRELIMINAR": PRELIMINAR, "DEFINITIVA": DEFINITIVO}

#: A lista em que ninguém concorre, antes da ordem (135, FR-4671, FR-4672). A frase vai no
#: próprio ato porque é o ato que o nível 1 e o "Próximo nesta lista" desenham; a razão só aparece
#: na espera.
#: **"Ninguém concorre", e não "sem inscritos"**: o critério é o universo depois da progressão, e
#: uma lista com inscrições eliminadas numa Etapa anterior também é vazia — "sem inscritos" faria
#: ler que ninguém se inscreveu. É o que a tela da ordenação diz: "Ninguém concorreu por este
#: recorte" (a revisão do PR #441).
NOTA_DA_LISTA_VAZIA = "lista em que ninguém concorre"
ATO_DA_ORDEM_VAZIA = "Emitir a ordem que declara que ninguém concorreu nesta lista"
ATO_DAS_ORDENS_VAZIAS = "Emitir as ordens que declaram que ninguém concorreu nestas listas"
ATO_DA_SUCESSORA_VAZIA = "Emitir a ordem sucessora, que declara que ninguém concorreu nesta lista"
ATO_DAS_SUCESSORAS_VAZIAS = (
    "Emitir as ordens sucessoras, que declaram que ninguém concorreu nestas listas"
)


def divulgado_da_celula(celula):
    """`NADA`, `PRELIMINAR` ou `DEFINITIVO`, da natureza que a célula da publicação da condução
    carrega (`conducao_do_marco._celula_da_publicacao`) — e nunca da nota (135, FR-4679)."""
    return _DIVULGADO_POR_NATUREZA.get((celula or {}).get("natureza") or "", NADA)


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
    #: A espera é recomendação, e não impedimento: o domínio aceita o ato, e a tela diz por que
    #: esperar (133, FR-4542). Só apresentação — nenhum comando a lê.
    recomendacao: bool = False
    #: Na ordem por pontuação: nenhuma inscrição concorre por esta lista, pelo critério da tela da
    #: ordenação (135, FR-4670). Nunca muda a situação (FR-4676) — muda o que a providência diz.
    lista_vazia: bool = False
    #: No resultado: o que o público lê hoje — `NADA`, `PRELIMINAR` ou `DEFINITIVO` (135, FR-4677).
    #: É o dado que decide; a nota é só o texto (FR-4679).
    divulgado: str = ""
    #: Na ordem *Depois*: há ordem vigente, e ela está para trás — a sucessora é que espera (141,
    #: FR-4833). Sem o dado, o resultado leria "não há ordem vigente a divulgar", o que é falso.
    vigente_para_tras: bool = False

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
    que ainda não estão feitas no Perfil), `vazia` (nenhuma inscrição concorre pela lista).

    ***Depois* enquanto as Etapas não estão feitas** (o `G-01` do estudo): emiti-la antes delas
    grava uma ordem que envelhece quando os resultados chegam, e a sucessão exige motivo. Desde a
    `128`, o comando recusa a ordem sem nenhum Resultado; esta derivação é mais estrita (diz
    *Depois* também para a parcial, que o comando aceita), e por isso nunca diz *Pendente* para o
    que ele recusa (`test_o_andamento_nunca_diz_pendente_para_a_ordem_que_o_comando_recusa`).

    **A lista em que ninguém concorre continua providência, e diz o que ela é** (135, D-001,
    FR-4671). A ordem vazia é ato normativo — emiti-la declara que ninguém concorreu —, e a
    providência igual à de uma lista com quem concorre fazia ler "há uma classificação a fazer" (o
    C08 do estudo de 09/11). A lista vazia só muda o texto e o dado: *Depois* e a recusa continuam
    decidindo (FR-4676).
    """
    celula = f.get("celula") or {}
    estado, url = celula.get("estado"), celula.get("url") or ""
    vazia = bool(f.get("vazia"))
    faltam = f.get("faltam") or []
    if estado == "feito":
        return _c(FEITO, natureza=ORDEM, nota=celula.get("nota") or "", url=url)
    if estado == "obsoleto" and faltam:
        # **A sucessora espera o que a primeira ordem esperaria** (141, FR-4830, D-001, D-002). Este
        # ramo devolvia "Emitir a ordem sucessora" antes de olhar `faltam`: no C08, deferido o
        # recurso que reabilita, o GPS mandava emitir a ordem ao lado da Análise de títulos que
        # faltava ao reabilitado — uma sucessora parcial, que nasce para ser sucedida, e por cima
        # dela o corte que deixava ele fora da faixa. *Depois*, e não *Obsoleto* sem ato: o
        # obsoleto é a praticar, e entraria no nível 1 como providência sem ato.
        return _c(
            DEPOIS,
            natureza=ORDEM,
            razao=(
                f"a ordem sucessora lê {_lista_de_nomes(faltam)}, que ainda "
                f"{'não está feita' if len(faltam) == 1 else 'não estão feitas'}; a vigente "
                "continua produzindo efeito"
            ),
            vigente_para_tras=True,
        )
    if estado == "obsoleto":
        return _c(
            OBSOLETO,
            natureza=ORDEM,
            ato=ATO_DA_SUCESSORA_VAZIA if vazia else "Emitir a ordem sucessora",
            responsavel=CONDUZ,
            razao="a regra ou o universo mudaram depois da emissão",
            url=url,
            nota=NOTA_DA_LISTA_VAZIA if vazia else "",
            lista_vazia=vazia,
        )
    if estado == "nao_se_aplica":
        return _c(NAO_SE_APLICA, natureza=ORDEM, nota=celula.get("nota") or "")
    if faltam:
        return _c(
            DEPOIS,
            natureza=ORDEM,
            razao=f"a ordem lê {_lista_de_nomes(faltam)}, que ainda não está feita"
            if len(faltam) == 1
            else f"a ordem lê {_lista_de_nomes(faltam)}, que ainda não estão feitas",
        )
    if vazia:
        return _c(
            PENDENTE,
            natureza=ORDEM,
            ato=ATO_DA_ORDEM_VAZIA,
            responsavel=CONDUZ,
            url=url,
            nota=NOTA_DA_LISTA_VAZIA,
            lista_vazia=True,
        )
    return _c(PENDENTE, natureza=ORDEM, ato="Emitir a ordem", responsavel=CONDUZ, url=url)


def leitura_da_definitiva(*, edital, marco, ato, lista_id, at, preliminar):
    """A aferição da publicação deste ato, como a célula do resultado e a tela do corte a leem.

    `{"nivel", "codigo", "mensagem", "ate"}`. `ate` é o fim do prazo recursal quando a recusa é a
    janela aberta — a mesma data que a mensagem escreve, que a própria aferição devolve (133,
    FR-4546). Uma leitura só, para que o corte e o resultado não digam prazos diferentes.
    """
    from processo_seletivo.divulgacao.domain import publicabilidade
    from processo_seletivo.shared.api.problems import DomainError

    marco_id = str((marco or {}).get("id"))
    try:
        afericao = publicabilidade.aferir(
            edital=edital,
            marco_id=marco_id,
            ato=ato,
            natureza="DEFINITIVA" if preliminar else "",
            lista_id=lista_id,
            at=at,
        )
        return {
            "nivel": afericao.nivel,
            "codigo": afericao.codigo,
            "mensagem": afericao.mensagem,
            "ate": afericao.ate,
        }
    except DomainError as recusa:
        return {
            "nivel": publicabilidade.IMPEDIMENTO,
            "codigo": recusa.code,
            "mensagem": recusa.detail,
            "ate": None,
        }


def espera_do_corte(marco, *, divulgado, definitiva):
    """`None`, ou `{"ate", "razao"}` quando o corte desta lista deve esperar o prazo de recurso
    (133, FR-4541, FR-4546, D-003). Pura.

    **Recomendação, e não impedimento** (R2 do usuário). O domínio aceita o corte a qualquer
    momento depois da ordem; o que o estudo de 07/11 mediu é o custo de cortar cedo: no Edital 900 o
    recurso deferido em 13/12 tornou obsoleto o corte que o cartão mandara emitir em 09/12, e a
    sucessão exigiu motivo. **Lê a aferição da definitiva**, que a célula do resultado já lê — uma
    segunda conta do prazo divergiria na primeira mudança dele.

    `divulgado`: o resultado da lista já tem publicação. `definitiva`: a aferição da definitiva,
    `{"nivel", "codigo", "mensagem", "ate"}`, quando há preliminar; `None` quando não há.
    """
    from processo_seletivo.divulgacao.domain import publicabilidade as p

    janela = (marco or {}).get("appealWindow") or {}
    if not janela.get("admits"):
        return None
    if not divulgado:
        return {
            "ate": None,
            "razao": (
                "O prazo de recurso começa com a divulgação do resultado; o corte emitido depois "
                "dele evita a sucessão"
            ),
        }
    if not definitiva or definitiva.get("nivel") != p.IMPEDIMENTO:
        return None
    if definitiva.get("codigo") not in (
        p.JANELA_ABERTA,
        p.RECURSO_PENDENTE,
        p.REAVALIACAO_PENDENTE,
        p.PROVIDENCIA_PENDENTE,
    ):
        return None
    ate = definitiva.get("ate")
    return {
        "ate": ate,
        "razao": (
            (
                f"Aguarde o fim do prazo de recurso, até {_data(ate)}"
                if ate
                else "Aguarde os recursos"
            )
            + ": um recurso deferido tornaria o corte obsoleto, com sucessão motivada"
        ),
    }


def espera_da_lista(*, edital, marco, lista_id, at, publicada=None, definitiva=None):
    """A espera do corte de uma lista, lida do banco: a regra única da tela do corte e do andamento
    (133, FR-4546). `None` quando o corte não espera.

    `publicada` é a publicação vigente da lista, quando quem chama já a tem; `definitiva`, a
    aferição da definitiva já lida, para não aferir duas vezes. **A publicação vigente pode ser a de
    um ato anterior** — a preliminar continua sendo do marco depois de a ordem sucessora sair, e o
    prazo recursal continua correndo dela; por isso a aferição é feita sobre o ato vigente, com a
    natureza da definitiva, e não sobre o publicado (o que a revisão do PR #432 acusou).
    """
    from processo_seletivo.classificacao.application.selectors import ato_vigente
    from processo_seletivo.divulgacao.application.selectors import vigente_do_marco

    if not ((marco or {}).get("appealWindow") or {}).get("admits"):
        return None
    marco_id = str(marco.get("id"))
    if publicada is None:
        publicada = vigente_do_marco(edital=edital, marco_id=marco_id, lista_id=lista_id)
    if publicada is None:
        return espera_do_corte(marco, divulgado=False, definitiva=None)
    if publicada.natureza != "PRELIMINAR":
        return None
    if definitiva is None:
        ato = ato_vigente(edital=edital, marco_id=marco_id, lista_id=lista_id)
        if ato is None:
            return None
        definitiva = leitura_da_definitiva(
            edital=edital, marco=marco, ato=ato, lista_id=lista_id, at=at, preliminar=True
        )
    return espera_do_corte(marco, divulgado=True, definitiva=definitiva)


def ordem_para_tras(ordem):
    """A ordem vigente está para trás: obsoleta, ou à espera da sucessora (141, FR-4833).

    A pergunta é de quem lê a ordem para decidir o que vem depois dela — o resultado. A situação
    sozinha não basta desde que a sucessora com Etapa por fazer passou a ser *Depois*.
    """
    return ordem is not None and (ordem.situacao == OBSOLETO or ordem.vigente_para_tras)


#: A razão do corte que espera o reabilitado (141, UX-341).
REINGRESSO_NO_CORTE = (
    "há inscrição reabilitada por recurso ainda sem resultado numa Etapa deste marco: o corte "
    "espera a consolidação dela e a ordem sucessora"
)


def situacao_do_corte(f):
    """O corte de uma lista (FR-4069). `f`: `celula` (do indicador), `ordem` (a célula da ordem ou
    do sorteio, já derivada), `espera` (de `espera_do_corte`, ou `None`), `reingresso` (há inscrição
    reabilitada por recurso sem resultado numa Etapa do marco).

    **O reingresso pendente segura o corte nas duas formas** (141, FR-4835, FR-4836, D-003). É a
    pergunta com que a publicação recusa (`publicabilidade.reingressos_pendentes`), e pela mesma
    razão: emitir agora produziria o mesmo ato incompleto. A ordem à espera já segurava o corte;
    faltavam a sucessora parcial que a tela aceita (128) e o corte que o reingresso tornou obsoleto.
    """
    celula = f.get("celula") or {}
    estado, url = celula.get("estado"), celula.get("url") or ""
    reingresso = bool(f.get("reingresso"))
    if estado == "nao_se_aplica":
        return _c(NAO_SE_APLICA, natureza=CORTE, nota=celula.get("nota") or "")
    if estado == "feito":
        return _c(FEITO, natureza=CORTE, url=url)
    if estado == "obsoleto" and reingresso:
        return _c(
            DEPOIS,
            natureza=CORTE,
            razao=f"o corte vigente está para trás, e {REINGRESSO_NO_CORTE}",
        )
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
    if reingresso:
        return _c(DEPOIS, natureza=CORTE, razao=REINGRESSO_NO_CORTE)
    espera = f.get("espera")
    if espera:
        # Sem responsável: ninguém precisa agir agora, e por isso a espera não é "sua" (FR-4543).
        return _c(
            AGUARDA,
            natureza=CORTE,
            ato="Emitir o corte",
            razao=espera["razao"],
            url=url,
            ate=espera.get("ate"),
            recomendacao=True,
        )
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

    **O que foi divulgado é dado, e decide** (135, FR-4677 a FR-4679): a célula leva `divulgado`
    em toda situação, e o ramo do preliminar é escolhido por ele, e não pela palavra na nota. A
    situação é a de antes em todos os casos (D-002): o preliminar segue a pendência do definitivo.
    """
    divulgado = divulgado_da_celula(f.get("celula"))
    return replace(_situacao_do_resultado(f, divulgado), divulgado=divulgado)


def _situacao_do_resultado(f, divulgado):
    from processo_seletivo.divulgacao.domain import publicabilidade as p

    celula = f.get("celula") or {}
    estado, nota = celula.get("estado"), (celula.get("nota") or "")
    url = celula.get("url") or ""
    previa = f.get("url_da_previa") or url
    ordem = f.get("ordem")
    # **A ordem obsoleta vem antes da publicação feita** (133, FR-4550, CV-04). Com a preliminar
    # publicada, este teste olhava só `estado != "feito"`, e a célula caía em "publicar a
    # definitiva" — que o comando recusa pela mesma ordem obsoleta.
    if ordem_para_tras(ordem):
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
        if divulgado != PRELIMINAR:
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
        # **O preliminar já está publicado: a razão não o oferece de novo** (135, D-003, FR-4681).
        # A mensagem da aferição continua a da prévia e a do comando; aqui vale a segunda redação,
        # quando o código tem uma.
        mensagem = p.mensagem_com_o_preliminar_publicado(
            definitiva.get("codigo"), definitiva.get("ate")
        ) or (definitiva.get("mensagem") or "")
        return _c(
            AGUARDA if espera else IMPEDIDO,
            natureza=RESULTADO,
            ato="Publicar o resultado definitivo",
            responsavel="" if espera else PUBLICA,
            nota=nota,
            razao=_frase(_sem_marcacao(mensagem)),
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
    #: `e_sua(celula, perfil)`: a regra de "sua" do nível 1, para as transições (FR-4090).
    e_sua: object = None
    #: O `Alcance` com que o andamento foi lido. O Centro (136) diz o papel da pessoa por ele, e
    #: recalculá-lo consultaria de novo a comissão e a Retificação.
    alcance: object = None

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


def do_edital(edital, ator, *, agora=None, em_curso=None, perfis=None):
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
        return _Leitor(edital, ator, conteudo, agora).andamento(em_curso=em_curso, perfis=perfis)
    except Exception:  # noqa: BLE001 — orientação não derruba a página (item 2 do code review)
        # **A orientação não pode derrubar o detalhe do Edital.** A derivação lê vinte funções de
        # outras features; um conteúdo que uma delas não espere faria o detalhe responder 500 para
        # todo papel. Sem andamento, o cartão volta a ser o de antes da 127 — e o defeito fica no
        # log, com o Edital, para ser corrigido.
        logger.exception("andamento_indisponivel", extra={"edital": str(edital.id)})
        return None


def da_lista(andamento, marco_id, lista_id, preferir=None, todas_as_listas=False):
    """`(primeira em aberto desta lista, [(rótulo, célula)] das outras listas do marco, Perfil)`.

    É a leitura das transições (R-012). `todas_as_listas` lê o marco inteiro — a semente vale para
    todas as listas, e depois de observá-la o próximo passo é do marco, e não de uma lista (item 4
    do code review das transições); então não há "outras".
    """
    if andamento is None:
        return None, [], None
    alvo, marco_id = _chave(lista_id), str(marco_id)
    for perfil in andamento.perfis:
        pontos = [p for p in perfil.pontos if p.marco and str(p.marco.get("id")) == marco_id]
        if not pontos:
            continue
        rotulos = dict(perfil.listas)
        # **Primeiro o trecho do marco, na ordem da jornada** (FR-4090): depois do corte vem a Etapa
        # governada, se houver, e depois a apuração — e não uma Etapa que corre em paralelo, que só
        # entra se o marco não tiver nada em aberto nesta lista.
        indices = [n for n, p in enumerate(perfil.pontos) if p in pontos]
        trecho = perfil.pontos[min(indices) : max(indices) + 1]
        demais = [p for p in perfil.pontos if p.tipo == ETAPA and p not in trecho]
        listas = [lista for lista, _ in perfil.listas] if todas_as_listas else [lista_id]

        do_marco, paralelas = (
            [
                c
                for p in pontos_
                for lista in listas
                for c in [p.celula(lista)]
                if c is not None and c.em_aberto
            ]
            for pontos_ in (trecho, demais)
        )
        abertas = do_marco + paralelas
        # Quem acabou de praticar um ato lê primeiro o que é dele nesta lista (`preferir`); sem
        # isso, o primeiro em aberto, que pode ser de outro papel.
        # Sem nada da pessoa, primeiro o que alguém pratica **no marco**, e só então o que espera
        # (133, FR-4543): depois da ordem, o que destrava a lista é divulgar, e não o corte em
        # espera. Só do trecho do marco: a Etapa paralela continua entrando só quando o marco não
        # tem nada em aberto (FR-4090 da `127`; a revisão do PR #432 acusou o atalho).
        desta = next(
            (c for c in abertas if preferir and preferir(c, perfil.perfil)),
            next(
                (c for c in do_marco if c.situacao in A_PRATICAR),
                abertas[0] if abertas else None,
            ),
        )
        outras = []
        for lista, rotulo in [] if todas_as_listas else perfil.listas:
            if _chave(lista) == alvo:
                continue
            primeira = next(
                (p.celula(lista) for p in pontos if (p.celula(lista) or _VAZIA).em_aberto), None
            )
            if primeira is not None:
                outras.append((rotulos.get(lista, rotulo), primeira))
        return desta, outras, perfil.perfil
    return None, [], None


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

    def andamento(self, *, em_curso=None, perfis=None):
        """O andamento; `perfis` restringe a leitura dos marcos a esses Perfis.

        A transição de um ato (FR-4090) lê o Perfil do marco, e não o Edital inteiro (item 3 do
        code review). As Etapas continuam lidas no Edital, que é como valem.
        """
        from processo_seletivo.inscricoes.domain.periodo import periodo_de_inscricoes

        self.periodo = periodo_de_inscricoes(self.conteudo, self.agora)
        self.perfil_de, self.inscritos_por_perfil = self._perfis_das_inscricoes()
        self.trabalho = self._trabalho_da_104(em_curso)
        expectativa = expectativa_das_etapas(self.conteudo)
        self.expectativa_do_edital = expectativa
        self.etapas_no_edital = self._etapas_no_edital(expectativa)
        pedidos = {str(p) for p in perfis} if perfis is not None else None
        perfis = [
            self._perfil(perfil)
            for perfil in self.conteudo.get("profiles") or []
            if perfil.get("classificationMilestones")
            and (pedidos is None or str(perfil.get("id")) in pedidos)
        ]
        self._providencias_da_104(em_curso)
        return Andamento(
            perfis=perfis,
            providencias=self.providencias,
            atencoes=self.atencoes,
            ve_a_matriz=self.alcance.consulta,
            e_sua=self.e_sua,
            alcance=self.alcance,
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
        vazias = None
        # O reingresso é do marco, e não da lista: perguntado uma vez, na primeira que precisar.
        reingresso = None
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
                ordenar = celulas.get("ordenar") or {}
                # **Só pergunta quem vai ler a resposta** (a revisão do PR #441): com Etapa por
                # fazer, a ordem é *Depois* — a primeira e, desde a `141`, a sucessora —, e
                # `situacao_da_ordem` nem olha a lista vazia.
                estado = ordenar.get("estado")
                vazia = False
                if estado in ("obsoleto", "falta") and not faltam:
                    if vazias is None:
                        vazias = self._listas_vazias(perfil, marco)
                    vazia = chave in vazias
                ordem = situacao_da_ordem({"celula": ordenar, "faltam": faltam, "vazia": vazia})
                derivadas = {ORDEM: ordem}
            # **O resultado antes do corte** (133, FR-4541): a espera do corte lê a mesma aferição
            # da definitiva que a célula do resultado leu.
            resultado, definitiva = self._resultado(marco, lista, celulas.get("publicar"), ordem)
            if CORTE in pontos:
                corte = celulas.get("cortar") or {}
                # **Só pergunta quando o corte seria providência** (141, FR-4843): com a ordem à
                # espera, o corte já é *Depois* por ela, e a resposta não seria lida.
                if (
                    reingresso is None
                    and not sorteado
                    and (
                        corte.get("estado") == "obsoleto"
                        or (corte.get("estado") == "falta" and ordem.situacao == FEITO)
                    )
                ):
                    reingresso = self._reingresso_pendente(marco)
                derivadas[CORTE] = situacao_do_corte(
                    {
                        "celula": corte,
                        "ordem": ordem,
                        "reingresso": bool(reingresso),
                        "espera": self._espera_do_corte(
                            marco, lista, celulas.get("publicar") or {}, definitiva
                        )
                        if corte.get("estado") == "falta" and ordem.situacao == FEITO
                        else None,
                    }
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
            derivadas[RESULTADO] = resultado
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

    # --- o reingresso pendente (141) ---------------------------------------------------------

    def _reingresso_pendente(self, marco):
        """Há inscrição reabilitada por recurso sem resultado numa Etapa que o marco enumera?

        **A função da publicação, e não uma cópia** (D-003): é ela que recusa divulgar, e uma
        segunda conta diria "o corte espera" num dia e "pode publicar" no outro. Custa uma consulta
        quando ninguém foi reabilitado no Edital, e uma por Etapa enumerada quando alguém foi.
        """
        from processo_seletivo.divulgacao.domain.publicabilidade import reingressos_pendentes

        return bool(reingressos_pendentes(edital=self.edital, marco=marco, at=self.agora))

    # --- a lista em que ninguém concorre ----------------------------------------------------

    def _listas_vazias(self, perfil, marco):
        """As chaves das listas reservadas em que ninguém concorre, perguntadas **uma vez por
        marco**, e só quando alguma lista lê a resposta (135, FR-4670, FR-4686): o marco já
        ordenado, e o que ainda espera Etapas, não pagam nada.

        O critério é o da tela da ordenação, numa função ao lado do cálculo dela (R-001).
        """
        from processo_seletivo.classificacao.application.calculo import listas_sem_concorrente

        return {
            _chave(lista)
            for lista in listas_sem_concorrente(
                edital=self.edital,
                conteudo=self.conteudo,
                perfil_id=perfil.get("id"),
                marco_id=marco.get("id"),
            )
        }

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

    # --- a espera do corte ------------------------------------------------------------------

    def _espera_do_corte(self, marco, lista, publicar, definitiva):
        """A leitura única (`espera_da_lista`), sem consulta quando a célula da publicação já diz.

        Sem publicação, a espera é a da divulgação; com a preliminar do ato vigente, a aferição que
        o resultado já leu. Só a publicação obsoleta (a de um ato anterior) ou a definitiva pedem a
        leitura do banco.
        """
        if not (marco.get("appealWindow") or {}).get("admits"):
            return None
        estado = publicar.get("estado")
        if estado not in ("feito", "obsoleto"):
            return espera_do_corte(marco, divulgado=False, definitiva=None)
        if estado == "feito" and divulgado_da_celula(publicar) != PRELIMINAR:
            return None
        return espera_da_lista(
            edital=self.edital, marco=marco, lista_id=lista, at=self.agora, definitiva=definitiva
        )

    # --- o resultado -----------------------------------------------------------------------

    def _resultado(self, marco, lista, celula, ordem):
        """`(célula do resultado, aferição da definitiva ou None)` — a segunda é o que a espera do
        corte lê (133, FR-4546)."""
        from processo_seletivo.classificacao.application.selectors import ato_vigente

        celula = celula or {}
        fatos = {"celula": celula, "ordem": ordem}
        estado = celula.get("estado")
        precisa_do_ato = (
            estado == "obsoleto"
            or (estado == "feito" and divulgado_da_celula(celula) == PRELIMINAR)
            or (estado == "falta" and ordem is not None and ordem.situacao == FEITO)
            or (estado == "falta" and ordem_para_tras(ordem))
        )
        if not precisa_do_ato:
            return situacao_do_resultado(fatos), None
        marco_id = str(marco.get("id"))
        ato = ato_vigente(edital=self.edital, marco_id=marco_id, lista_id=lista)
        if ato is not None and self.alcance.publica:
            fatos["url_da_previa"] = reverse(
                "interface:previa-de-publicacao", args=[self.edital.id, marco_id, ato.id]
            )
        if ato is not None and not ordem_para_tras(ordem):
            # **A mesma aferição da prévia** (item 1 da revisão): sucedido, desatualizado, corte
            # obsoleto e reingresso impedem as duas naturezas, e a prévia não oferece o botão.
            preliminar = estado == "feito"
            lida = leitura_da_definitiva(
                edital=self.edital,
                marco=marco,
                ato=ato,
                lista_id=lista,
                at=self.agora,
                preliminar=preliminar,
            )
            fatos["definitiva" if preliminar else "afericao"] = lida
            return situacao_do_resultado(fatos), (lida if preliminar else None)
        return situacao_do_resultado(fatos), None

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
            # **Só a chamada que ainda não ocupa** (133, FR-4547, CV-03): o titular conta como
            # ocupado desde a apuração, e descontá-lo de novo de `faltando` escondia a próxima da
            # fila depois de uma desistência. A chamada para a vaga que vagou, ou para regularizar,
            # ainda não ocupa — ela responde pela vaga, e chamar outra pessoa a dobraria.
            "em_aberto": sum(
                1
                for lin in linhas
                if lin["desfecho"] is None
                and getattr(lin.get("convocacao"), "especie", None) != nomes.VAGA_INICIAL
            ),
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
        sua = self.e_sua(celula, perfil)
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

    def e_sua(self, celula, perfil=None):
        """Se a pessoa pratica o ato desta célula agora — a regra única do nível 1 e das transições.

        As transições (FR-4090) a leem daqui, e não refazem a pergunta: a confirmação de "sua" tem
        três formas (a porta do papel, a mesa da `104`, a alocação à conferência), e uma cópia dela
        na view divergiria na primeira mudança (item 1 do code review das transições).
        """
        if celula.situacao not in A_PRATICAR:
            return False
        if celula.natureza == AVALIAR:
            # O link da mesa só existe para quem tem inscrição pendente nela (a carga da `104`).
            return bool(celula.url)
        if celula.responsavel == CONFERE:
            return self._pode_conferir(perfil)
        return self.alcance.pratica(celula.responsavel)

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
    # do Edital, ficam no nível 1 e em "Etapas X de Y". **E a frase diz isso** (135, D-004,
    # FR-4684): ao lado do "2 providências em aberto" do cartão, um "1 providência em aberto" sem
    # escopo parecia contradição (A-07 do estudo de 09/11). Somar as Etapas contaria duas vezes a
    # mesma providência num Edital de dois Perfis.
    em_aberto = len(agrupar(perfil.providencias))
    if em_aberto:
        providencias = "providência" if em_aberto == 1 else "providências"
        partes.append(f"{em_aberto} {providencias} em aberto nos marcos")
    return " · ".join(p for p in partes if p)


def _resultado_em_palavras(perfil):
    """A natureza do que o público lê, sobre as listas em que há o que divulgar (item 1).

    Lê o `divulgado` de qualquer situação (135, FR-4679): o preliminar na janela recursal é
    *Aguarda*, e continua publicado. "Definitivo" só quando todas as listas o têm; publicado em
    parte, diz quantas. Lia a palavra na nota, e por isso a célula *Depois* do preliminar com a
    ordem obsoleta, que não tem nota, contava como não publicada (research R-006).

    **O *Obsoleto* conta como publicado e nunca como definitivo**, como antes: o definitivo de um
    ato anterior não é o definitivo da lista.
    """
    resultados = [c for p in perfil.pontos if p.tipo == RESULTADO for c in _por_lista(p, perfil)]
    aplicaveis = [c for c in resultados if c.situacao != NAO_SE_APLICA]
    if not aplicaveis:
        return ""
    publicadas = [
        c for c in aplicaveis if c.divulgado in (PRELIMINAR, DEFINITIVO) or c.situacao == OBSOLETO
    ]
    definitivas = [c for c in publicadas if c.divulgado == DEFINITIVO and c.situacao != OBSOLETO]
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
    "REINGRESSO_NO_CORTE",
    "Andamento",
    "Celula",
    "da_lista",
    "do_edital",
    "expectativa_das_etapas",
    "linha_das_inscricoes",
    "resumo_do_perfil",
    "sequencia_do_perfil",
]
