"""As respostas às perguntas sugeridas (070, `FR-1417` a `FR-1438`, contracts/resposta.md).

**Uma função por pergunta**, e cada uma só monta o que a pergunta pede: os cartões na ordem da
tabela de pertinência, o tipo e a explicação. O resto é comum e vem depois, em `responder`:

1. a origem de cada cartão, pelo último ato aplicado (`origem.py`, `R-004`);
2. o valor que uma Retificação já publicada, de vigência futura, vai pôr no lugar (`FR-1414`);
3. o aviso de anexo citado nos textos mostrados (`FR-1430`);
4. o desfecho, a mudança de versão e a situação de calendário.

**O tipo é uma tabela de decisão, e não um julgamento** (`R-013`): só dado responde → "Respondida";
texto sobre o assunto, sozinho ou com dado → "Depende da leitura"; nada → "O Edital não informa";
canais distintos → "Fontes divergentes". **A lista literal que a pergunta pede é dado**, mesmo
sendo texto: os requisitos do Perfil são a coleção que a `P-04` pede.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace

from processo_seletivo.duvidas.domain import anexos, catalogo, explicacao, leitura, rotulos
from processo_seletivo.duvidas.domain import canal as canais
from processo_seletivo.duvidas.domain.estruturas import (
    AVISO_DESFECHO,
    AVISO_DETALHE_EM_ANEXO,
    AVISO_REDACAO_ALCANCA_MAIS,
    AVISO_RETIFICACAO_FUTURA,
    CANAL_INSTITUCIONAL,
    DADO,
    DEPENDE_DA_LEITURA,
    EXPLICACAO,
    FONTES_DIVERGENTES,
    NAO_INFORMA,
    RESPONDIDA,
    TEXTO,
    Aviso,
    Contexto,
    Link,
    MudancaDeVersao,
    Referencia,
    Resposta,
    SituacaoDeCalendario,
    ValorFuturo,
)
from processo_seletivo.duvidas.domain.origem import origens
from processo_seletivo.editais.domain.documentos import NAO_SE_APLICA, OBRIGATORIO, aplicabilidade
from processo_seletivo.editais.domain.fase_do_evento import marcos_pendentes
from processo_seletivo.inscricoes.domain.periodo import evento_designado, periodo_de_inscricoes
from processo_seletivo.publicacoes.domain.changes import ABSENT
from processo_seletivo.shared.texto import dobrar

ANCORA_DAS_VAGAS = "#vaga-{id}"
ANCORA_DO_CRONOGRAMA = "#cronograma-titulo"
ANCORA_DOS_DOCUMENTOS = "#documentos-titulo"

#: Encaminham ao atendimento: a resposta não se sustenta só nos dados (`FR-1423`).
TIPOS_QUE_ENCAMINHAM = (NAO_INFORMA, DEPENDE_DA_LEITURA, FONTES_DIVERGENTES)


@dataclass
class _Rascunho:
    tipo: str = RESPONDIDA
    explicacao: str = ""
    referencias: list = field(default_factory=list)
    avisos: list = field(default_factory=list)
    situacao: SituacaoDeCalendario | None = None


def _juntar(lista, *referencias):
    lista.extend(referencia for referencia in referencias if referencia is not None)


def _secoes(contexto, chaves):
    return [leitura.secao(contexto.conteudo, chave) for chave in chaves]


def _link(contexto, rotulo, ancora):
    if not contexto.pagina_publica:
        return ()
    return (Link(rotulo, f"{contexto.pagina_publica}{ancora}"),)


def _com_links(referencias, links):
    return [replace(referencia, links=referencia.links + links) for referencia in referencias]


# ---- P-01 e P-02: o calendário -------------------------------------------------------------


def _cartoes_do_evento(evento):
    base, onde = leitura.caminho_do_evento(evento), leitura.onde_evento(evento)
    cartoes = [
        leitura.dado(
            onde, f"{base}/startAt", "Início", leitura.instante_legivel(evento.get("startAt"))
        ),
        leitura.dado(
            onde,
            f"{base}/endAt",
            "Término",
            leitura.instante_legivel(evento.get("endAt"))
            if evento.get("endAt")
            else "não declarado",
        ),
    ]
    _juntar(
        cartoes,
        leitura.texto(onde, f"{base}/description", evento.get("description"), rotulo="Descrição"),
        leitura.texto(onde, f"{base}/location", evento.get("location"), rotulo="Local"),
    )
    if evento.get("status") == "CANCELADO":
        cartoes.append(leitura.dado(onde, f"{base}/status", "Situação declarada", "cancelado"))
    return cartoes


def _p01(contexto, parametros, pergunta, canal):
    conteudo = contexto.conteudo
    evento = evento_designado(conteudo)
    periodo = periodo_de_inscricoes(conteudo, contexto.instante)
    rascunho = _Rascunho()
    rascunho.referencias = _com_links(
        _cartoes_do_evento(evento),
        _link(contexto, "Cronograma na página pública", ANCORA_DO_CRONOGRAMA),
    )
    _juntar(rascunho.referencias, *_secoes(contexto, pergunta.acompanha))
    inicio = leitura.instante_legivel(evento.get("startAt"))
    fim = leitura.instante_legivel(evento.get("endAt")) if evento.get("endAt") else ""
    if contexto.desfecho is not None and contexto.desfecho.do_edital:
        rascunho.explicacao = (
            "As inscrições não estão em curso: o Edital teve desfecho, dito no aviso acima. "
            "O período declarado está abaixo."
        )
    else:
        rascunho.explicacao = explicacao.inscricoes(periodo, inicio, fim)
    rascunho.situacao = SituacaoDeCalendario(contexto.instante, periodo.estado, contexto.desfecho)
    return rascunho


def _p02(contexto, parametros, pergunta, canal):
    rascunho = _Rascunho()
    pendentes = marcos_pendentes(contexto.conteudo, contexto.instante)
    links = _link(contexto, "Cronograma na página pública", ANCORA_DO_CRONOGRAMA)
    em_andamento, por_vir = [], []
    for evento, _inicio, _fim, fase in pendentes:
        rascunho.referencias.extend(_com_links(_cartoes_do_evento(evento), links))
        # Sem o ponto final da descrição: dentro da frase, "“…dia.”." punha ponto duplo.
        nome = f"“{leitura.nome_do_evento(evento).rstrip('.')}”"
        (em_andamento if fase == "EM_ANDAMENTO" else por_vir).append(nome)
    if contexto.desfecho is not None and contexto.desfecho.do_edital:
        # O desfecho prevalece sobre o cronograma (`FR-1429`), como na `P-01`: o Edital cancelado
        # não tem "Em andamento", ainda que o cronograma publicado continue dizendo as datas.
        rascunho.explicacao = (
            "O Edital teve desfecho, dito no aviso acima: as datas abaixo são as que o cronograma "
            "publicado declara, e não etapas em curso."
            if pendentes
            else "O Edital teve desfecho, dito no aviso acima."
        )
    elif not pendentes:
        # Não "já passaram": `marcos_pendentes` também deixa de fora o Evento cancelado e o que não
        # tem início, e dizer que passou o que foi cancelado afirmaria o falso.
        rascunho.explicacao = "Nenhuma data deste cronograma está por vir."
    else:
        partes = []
        if em_andamento:
            partes.append(f"Em andamento: {', '.join(em_andamento)}.")
        if por_vir:
            partes.append(f"Por vir: {', '.join(por_vir)}.")
        rascunho.explicacao = " ".join(partes) + " As datas estão abaixo, na ordem do cronograma."
    rascunho.situacao = SituacaoDeCalendario(
        contexto.instante,
        periodo_de_inscricoes(contexto.conteudo, contexto.instante).estado,
        contexto.desfecho,
    )
    return rascunho


# ---- P-03 e P-04: o Perfil -------------------------------------------------------------------


def _p03(contexto, parametros, pergunta, canal):
    perfil = parametros.perfil
    base, onde = leitura.caminho_do_perfil(perfil), leitura.onde_perfil(perfil)
    modalidades = leitura.por_id(perfil.get("competitionModalities"))
    rascunho = _Rascunho()
    cartoes = [
        leitura.dado(
            onde,
            f"{base}/immediateVacancies",
            "Vagas imediatas",
            leitura.numero_legivel(perfil.get("immediateVacancies")),
        )
    ]
    # **A ampla concorrência é a linha sem modalidade** (`FR-1427`). Uma modalidade "AC" declarada
    # sem linha não entra no quadro: ela existe para que um documento possa apontá-la, e dizê-la
    # aqui com zero vagas afirmaria o falso.
    linhas = []
    for linha in perfil.get("vacancyTable") or []:
        modalidade = (
            modalidades.get(str(linha.get("modalityId"))) if linha.get("modalityId") else None
        )
        if modalidade is None:
            rotulo, curto = "Vagas da ampla concorrência", "de ampla concorrência"
        else:
            rotulo = f"Vagas da modalidade {modalidade.get('code')} — {modalidade.get('name', '')}"
            curto = f"na modalidade {modalidade.get('code')}"
        quantidade = leitura.numero_legivel(linha.get("immediateVacancies"))
        cartoes.append(
            leitura.dado(
                onde,
                f"{base}/vacancyTable/id={linha.get('id')}/immediateVacancies",
                rotulo,
                quantidade,
            )
        )
        linhas.append((curto, quantidade))
    reserva = perfil.get("reserveType")
    cartoes.append(
        leitura.dado(
            onde,
            f"{base}/reserveType",
            "Cadastro de reserva",
            rotulos.em_palavras(rotulos.RESERVA, reserva),
        )
    )
    limite = leitura.numero_legivel(perfil.get("reserveLimit"))
    if reserva == "LIMITED":
        cartoes.append(
            leitura.dado(onde, f"{base}/reserveLimit", "Limite do cadastro de reserva", limite)
        )
    reversao = (perfil.get("vacancyReversion") or {}).get("kind")
    if reversao:
        cartoes.append(
            leitura.dado(
                onde,
                f"{base}/vacancyReversion",
                "Reverter vaga reservada não preenchida para a ampla concorrência",
                rotulos.em_palavras(rotulos.REVERSAO, reversao),
            )
        )
    # O que o Perfil é, ao lado das vagas: quem lê "quantas vagas" quer saber de quê, onde, com que
    # carga e por quanto. Achado pelo guardião de cobertura (`R-015`): sem estas linhas, nenhuma
    # das doze perguntas mostrava carga horária nem remuneração.
    _juntar(
        cartoes,
        leitura.texto(onde, f"{base}/description", perfil.get("description"), rotulo="Descrição"),
        leitura.texto(onde, f"{base}/locality", perfil.get("locality"), rotulo="Localidade"),
        leitura.texto(onde, f"{base}/workload", perfil.get("workload"), rotulo="Carga horária"),
        leitura.texto(
            onde, f"{base}/compensation", perfil.get("compensation"), rotulo="Remuneração"
        ),
    )
    for modalidade in perfil.get("competitionModalities") or []:
        lugar = f"{onde} — modalidade {modalidade.get('code')}"
        caminho = f"{base}/competitionModalities/id={modalidade.get('id')}"
        _juntar(
            cartoes,
            leitura.texto(
                lugar, f"{caminho}/description", modalidade.get("description"), rotulo="Descrição"
            ),
            leitura.texto(
                lugar,
                f"{caminho}/normativeRule/foundation",
                (modalidade.get("normativeRule") or {}).get("foundation"),
                rotulo="Fundamento",
            ),
        )
    rascunho.referencias = _com_links(
        cartoes,
        _link(
            contexto,
            "Vagas do Perfil na página pública",
            ANCORA_DAS_VAGAS.format(id=perfil.get("id")),
        ),
    )
    _juntar(rascunho.referencias, *_secoes(contexto, pergunta.acompanha))
    # Ausente não é zero (`FR-1416`, `FR-1422`): o cartão diz "não declarado", e a explicação não
    # pode afirmar que o Perfil não tem vagas.
    total = perfil.get("immediateVacancies")
    rascunho.explicacao = explicacao.vagas(
        perfil.get("code"), total, leitura.numero_legivel(total), linhas, reserva, limite
    )
    return rascunho


def _p04(contexto, parametros, pergunta, canal):
    perfil = parametros.perfil
    base, onde = leitura.caminho_do_perfil(perfil), leitura.onde_perfil(perfil)
    rascunho = _Rascunho()
    requisitos = [
        leitura.texto(onde, f"{base}/requirements", requisito, posicao=posicao, rotulo="Requisito")
        for posicao, requisito in enumerate(perfil.get("requirements") or [])
    ]
    _juntar(rascunho.referencias, *requisitos)
    rascunho.referencias = _com_links(
        rascunho.referencias,
        _link(
            contexto,
            "Vagas do Perfil na página pública",
            ANCORA_DAS_VAGAS.format(id=perfil.get("id")),
        ),
    )
    tratam = [secao for secao in _secoes(contexto, pergunta.trata) if secao is not None]
    _juntar(rascunho.referencias, *tratam, *_secoes(contexto, pergunta.acompanha))
    if tratam:
        rascunho.tipo = DEPENDE_DA_LEITURA
        rascunho.explicacao = explicacao.depende_da_leitura("requisitos", canal)
        if requisitos:
            rascunho.explicacao = (
                f"Os requisitos do Perfil {perfil.get('code')} estão abaixo, como o Edital os "
                f"escreve. {rascunho.explicacao}"
            )
    else:
        # Sem requisito do Perfil e sem a seção, a pergunta não é oferecida a este Perfil
        # (`catalogo.resolver`, `FR-1417`): aqui sempre há requisito.
        rascunho.explicacao = (
            f"Os requisitos do Perfil {perfil.get('code')} estão abaixo, como o Edital os escreve. "
            "A análise de quem os atende é feita no certame, e não por esta consulta."
        )
    return rascunho


# ---- P-05 e P-06: a inscrição ----------------------------------------------------------------


def _p05(contexto, parametros, pergunta, canal):
    perfil, modalidade = parametros.perfil, parametros.modalidade
    conteudo = contexto.conteudo
    rascunho = _Rascunho()
    anexos_por_id = leitura.por_id(conteudo.get("attachments"))
    vereditos = aplicabilidade(
        conteudo,
        profile_id=str(perfil.get("id")),
        modality_id=str(modalidade.get("id")) if modalidade else None,
    )
    links = _link(contexto, "Edital e documentos na página pública", ANCORA_DOS_DOCUMENTOS)
    divergentes = []
    aplicaveis = 0
    for veredito in vereditos:
        # **O divergente é um "não se aplica"** (`documentos.py`): a regra não o alcança, e o nome
        # publicado do grupo alcança. Pulá-lo junto com os outros deixava o aviso sem cartão — e
        # nunca emitido.
        if veredito.situacao == NAO_SE_APLICA and not veredito.divergente_do_publicado:
            continue
        documento = veredito.requisito
        base, onde = leitura.caminho_do_documento(documento), leitura.onde_documento(documento)
        if veredito.divergente_do_publicado:
            obrigatoriedade = "não se aplica pela regra; o nome publicado alcança esta modalidade"
            divergentes.append(documento.get("name", ""))
        else:
            aplicaveis += 1
            obrigatoriedade = "obrigatório" if veredito.situacao == OBRIGATORIO else "facultativo"
        cartoes = [leitura.dado(onde, f"{base}/required", "Obrigatoriedade", obrigatoriedade)]
        _juntar(
            cartoes,
            leitura.texto(
                onde, f"{base}/instructions", documento.get("instructions"), rotulo="Instruções"
            ),
        )
        anexo = anexos_por_id.get(str(documento.get("attachmentId")))
        if anexo is not None:
            url = contexto.anexos_publicos.get(str(anexo.get("artifactId")), "")
            cartoes.append(
                replace(
                    leitura.dado(
                        onde, f"{base}/attachmentId", "Anexo vinculado", anexo.get("label", "")
                    ),
                    links=(Link(anexo.get("label", ""), url),) if url else (),
                )
            )
        rascunho.referencias.extend(_com_links(cartoes, links))
    secoes = list(pergunta.acompanha) + (
        list(pergunta.acompanha_com_modalidade) if modalidade else []
    )
    _juntar(rascunho.referencias, *_secoes(contexto, secoes))
    lista = f" na modalidade {modalidade.get('code')}" if modalidade else ", sem modalidade"
    if aplicaveis:
        rascunho.explicacao = (
            f"Para o Perfil {perfil.get('code')}{lista}, o Edital pede os documentos abaixo, com "
            "as instruções de cada um; se cada um é obrigatório ou facultativo está no cartão. A "
            "aceitação de cada documento é decidida no certame, e não por esta consulta."
        )
    else:
        rascunho.explicacao = (
            f"Nenhum documento exigido se aplica ao Perfil {perfil.get('code')}{lista}."
        )
    if divergentes:
        rascunho.tipo = DEPENDE_DA_LEITURA
        rascunho.avisos.append(
            Aviso(
                AVISO_REDACAO_ALCANCA_MAIS,
                "O documento publicado nomeia o grupo pelo nome e pode ser lido como exigido "
                "também "
                f"aqui: {', '.join(divergentes)}. {explicacao.encaminhar(canal)}",
            )
        )
    return rascunho


def _p06(contexto, parametros, pergunta, canal):
    conteudo = contexto.conteudo
    rascunho = _Rascunho()
    teto = conteudo.get("maxInscricoesPorCandidato")
    if teto is not None:
        rascunho.referencias.append(
            leitura.dado(
                "Edital — inscrições",
                "/maxInscricoesPorCandidato",
                "Inscrições enviadas por candidato neste Edital, no máximo",
                leitura.numero_legivel(teto),
            )
        )
    tratam = [secao for secao in _secoes(contexto, pergunta.trata) if secao is not None]
    rascunho.referencias.extend(tratam)
    if tratam:
        rascunho.tipo = DEPENDE_DA_LEITURA
        rascunho.explicacao = explicacao.depende_da_leitura("inscrição", canal)
        if teto is not None:
            rascunho.explicacao = (
                f"Cada candidato pode ter no máximo {leitura.numero_legivel(teto)} "
                f"{explicacao.plural(teto, 'inscrição enviada', 'inscrições enviadas')} "
                "neste Edital. " + rascunho.explicacao
            )
    elif teto is not None:
        rascunho.explicacao = (
            f"Cada candidato pode ter no máximo {leitura.numero_legivel(teto)} "
            f"{explicacao.plural(teto, 'inscrição enviada', 'inscrições enviadas')} neste Edital."
        )
    else:
        rascunho.tipo = NAO_INFORMA
        rascunho.explicacao = explicacao.nao_informa("inscrição em mais de um Perfil", canal)
    return rascunho


# ---- P-07, P-08 e P-09: a seleção -------------------------------------------------------------


def _sim_ou_nao(valor):
    # Ausente não é "não" (`FR-1416`): conteúdo de esquema anterior pode não ter o campo.
    return "não declarado" if valor is None else ("sim" if valor else "não")


def _cartoes_da_etapa(etapa):
    base, onde = leitura.caminho_da_etapa(etapa), leitura.onde_etapa(etapa)
    cartoes = []
    _juntar(cartoes, leitura.texto(onde, f"{base}/name", etapa.get("name"), rotulo="Nome"))
    cartoes.append(
        leitura.dado(
            onde,
            f"{base}/forma",
            "Forma",
            rotulos.em_palavras(rotulos.FORMA_DA_ETAPA, etapa.get("forma")),
        )
    )
    if etapa.get("forma") == "DECISORIA":
        # Os rótulos **deste** Edital ("Deferido", "Indeferido"), como o documento os imprime; o
        # genérico "favorável ou desfavorável" só quando o Edital não os declara (`pdf.py`).
        _juntar(
            cartoes,
            leitura.texto(
                onde,
                f"{base}/rotuloFavoravel",
                etapa.get("rotuloFavoravel"),
                rotulo="Resultado favorável",
            ),
            leitura.texto(
                onde,
                f"{base}/rotuloDesfavoravel",
                etapa.get("rotuloDesfavoravel"),
                rotulo="Resultado desfavorável",
            ),
        )
    cartoes.append(
        leitura.dado(
            onde,
            f"{base}/eliminatory",
            "Eliminatória",
            _sim_ou_nao(etapa.get("eliminatory")),
        )
    )
    cartoes.append(
        leitura.dado(
            onde,
            f"{base}/classificatory",
            "Classificatória",
            _sim_ou_nao(etapa.get("classificatory")),
        )
    )
    for campo, rotulo in (
        ("weight", "Peso"),
        ("minimumScore", "Nota mínima"),
        ("maximumScore", "Nota máxima"),
    ):
        if etapa.get(campo) is not None:
            cartoes.append(
                leitura.dado(
                    onde, f"{base}/{campo}", rotulo, leitura.numero_legivel(etapa.get(campo))
                )
            )
    return cartoes


def _nomes_das_etapas(identificadores, etapas):
    return (
        "; ".join(
            (etapas.get(str(identificador)) or {}).get("name") or "Etapa que não existe"
            for identificador in identificadores
        )
        or "nenhuma declarada"
    )


def _cartoes_do_marco(perfil, marco, etapas):
    base, onde = leitura.caminho_do_marco(perfil, marco), leitura.onde_marco(perfil, marco)
    fatos = leitura.por_id(perfil.get("declaredFacts"))
    cartoes = []
    _juntar(cartoes, leitura.texto(onde, f"{base}/name", marco.get("name"), rotulo="Nome"))
    forma = marco.get("orderProduction")
    if forma:
        cartoes.append(
            leitura.dado(
                onde,
                f"{base}/orderProduction",
                "Ordem de classificação",
                rotulos.em_palavras(rotulos.FORMA_DA_ORDEM, forma),
            )
        )
    if forma != "POR_SORTEIO":
        cartoes.append(
            leitura.dado(
                onde,
                f"{base}/stages",
                "Etapas combinadas",
                _nomes_das_etapas(marco.get("stages") or [], etapas),
            )
        )
        if marco.get("operation"):
            cartoes.append(
                leitura.dado(
                    onde,
                    f"{base}/operation",
                    "Combinação",
                    rotulos.em_palavras(rotulos.OPERACAO, marco.get("operation")),
                )
            )
        if marco.get("normalization"):
            cartoes.append(
                leitura.dado(
                    onde,
                    f"{base}/normalization",
                    "Normalização",
                    rotulos.em_palavras(rotulos.NORMALIZACAO, marco.get("normalization")),
                )
            )
        arredondamento = marco.get("rounding") or {}
        if arredondamento:
            casas = arredondamento.get("scale")
            cartoes.append(
                leitura.dado(
                    onde,
                    f"{base}/rounding",
                    "Arredondamento",
                    f"{leitura.numero_legivel(casas)} "
                    f"{explicacao.plural(casas, 'casa decimal', 'casas decimais')}, "
                    f"{rotulos.em_palavras(rotulos.ARREDONDAMENTO, arredondamento.get('mode'))}",
                )
            )
    corte = marco.get("cutRule") or {}
    if corte:
        alvo = (
            leitura.numero_legivel(corte.get("targetCount"))
            if corte.get("targetKind") == "FIXED"
            else rotulos.em_palavras(rotulos.ESPECIE_DO_ALVO, corte.get("targetKind"))
        )
        governada = corte.get("governedStage")
        cartoes.extend(
            [
                leitura.dado(onde, f"{base}/cutRule/targetCount", "Quantidade que progride", alvo),
                leitura.dado(
                    onde,
                    f"{base}/cutRule/surplusCount",
                    "Suplentes além dessa quantidade",
                    leitura.numero_legivel(corte.get("surplusCount")),
                ),
                leitura.dado(
                    onde,
                    f"{base}/cutRule/governedStage",
                    "Etapa para a qual progridem",
                    _nomes_das_etapas([governada], etapas)
                    if governada and governada != "NONE"
                    else "nenhuma",
                ),
                leitura.dado(
                    onde,
                    f"{base}/cutRule/tieOutcome",
                    "Empate na última posição",
                    rotulos.em_palavras(rotulos.EMPATE_NO_CORTE, corte.get("tieOutcome")),
                ),
                leitura.dado(
                    onde,
                    f"{base}/cutRule/continuation",
                    "Continuação",
                    rotulos.em_palavras(rotulos.CONTINUACAO, corte.get("continuation")),
                ),
            ]
        )
    for criterio in sorted(marco.get("tiebreakers") or [], key=lambda item: item.get("order") or 0):
        parametros = criterio.get("parameters") or {}
        if "factId" in parametros:
            alvo = (fatos.get(str(parametros["factId"])) or {}).get("label") or "fato não declarado"
        else:
            alvo = (etapas.get(str(parametros.get("stageId"))) or {}).get("name") or ""
        cartoes.append(
            leitura.dado(
                onde,
                f"{base}/tiebreakers/id={criterio.get('id')}",
                f"{criterio.get('order')}º critério de desempate",
                f"{rotulos.em_palavras(rotulos.TIPO_DO_CRITERIO, criterio.get('type'))} {alvo}; "
                f"{rotulos.em_palavras(rotulos.QUANDO_FALTA, criterio.get('whenMissing'))}",
            )
        )
    return cartoes


def _p07(contexto, parametros, pergunta, canal):
    perfil = parametros.perfil
    conteudo = contexto.conteudo
    etapas = leitura.por_id(conteudo.get("stages"))
    rascunho = _Rascunho()
    usadas = []
    for marco in perfil.get("classificationMilestones") or []:
        for identificador in marco.get("stages") or []:
            if str(identificador) not in usadas:
                usadas.append(str(identificador))
        governada = (marco.get("cutRule") or {}).get("governedStage")
        if governada and str(governada) in etapas and str(governada) not in usadas:
            usadas.append(str(governada))
    marcos = perfil.get("classificationMilestones") or []
    # Perfil sem marco (o Edital sem marco existe, `validation.py`): as Etapas do Edital, todas,
    # porque nada as liga a este Perfil — e não "Respondida" sem cartão nenhum.
    escolhidas = usadas if marcos else list(etapas)
    for etapa in sorted(
        (etapas[identificador] for identificador in escolhidas if identificador in etapas),
        key=lambda item: item.get("order") or 0,
    ):
        rascunho.referencias.extend(_cartoes_da_etapa(etapa))
    for marco in marcos:
        rascunho.referencias.extend(_cartoes_do_marco(perfil, marco, etapas))
    _juntar(rascunho.referencias, *_secoes(contexto, pergunta.acompanha))
    if marcos:
        rascunho.explicacao = (
            f"As Etapas e as regras de classificação do Perfil {perfil.get('code')} estão abaixo, "
            "como o Edital as declara. A classificação de cada pessoa é feita no certame, e não "
            "por esta consulta."
        )
    else:
        rascunho.explicacao = (
            f"O Edital declara as Etapas abaixo e não as liga a um marco de classificação do "
            f"Perfil {perfil.get('code')}. A classificação de cada pessoa é feita no certame, e "
            "não por esta consulta."
        )
    return rascunho


def _p08(contexto, parametros, pergunta, canal):
    perfil = parametros.perfil
    conteudo = contexto.conteudo
    rascunho = _Rascunho()
    janelas = []
    for marco in perfil.get("classificationMilestones") or []:
        janela = marco.get("appealWindow")
        if janela is None:
            continue
        base, onde = leitura.caminho_do_marco(perfil, marco), leitura.onde_marco(perfil, marco)
        nome = marco.get("name") or marco.get("code") or ""
        dias = leitura.numero_legivel(janela.get("durationDays"))
        unidade = janela.get("unit")
        valor = (
            f"cabe, em {dias} {rotulos.em_palavras(rotulos.UNIDADE_DO_PRAZO, unidade)}"
            if janela.get("admits")
            else "não cabe, como o Edital declara"
        )
        rascunho.referencias.append(
            leitura.dado(
                onde, f"{base}/appealWindow", f"Recurso contra o resultado de “{nome}”", valor
            )
        )
        janelas.append((nome, janela.get("admits"), dias, unidade))
    secoes = [secao for secao in _secoes(contexto, pergunta.trata) if secao is not None]
    rascunho.referencias.extend(secoes)
    # **Os Eventos de recurso, pela palavra** (`R-014`): não há vínculo entre Evento e marco, e
    # mostrar pelo que o Evento escreve é seleção do que exibir. Concluir o prazo por ele seria
    # interpretar.
    eventos = [
        evento
        for evento in conteudo.get("schedule") or []
        if "recurs" in dobrar(f"{evento.get('type') or ''} {evento.get('description') or ''}")
    ]
    links = _link(contexto, "Cronograma na página pública", ANCORA_DO_CRONOGRAMA)
    for evento in eventos:
        rascunho.referencias.extend(_com_links(_cartoes_do_evento(evento), links))
    fontes = bool(janelas) + bool(secoes) + bool(eventos)
    if fontes == 0:
        rascunho.tipo = NAO_INFORMA
        rascunho.explicacao = explicacao.nao_informa("recurso para este Perfil", canal)
    elif janelas and not secoes and not eventos:
        rascunho.explicacao = explicacao.recurso_declarado(janelas)
    else:
        rascunho.tipo = DEPENDE_DA_LEITURA
        rascunho.explicacao = (
            explicacao.varias_fontes("recurso", canal)
            if fontes > 1
            else explicacao.depende_da_leitura("recurso", canal)
        )
    return rascunho


def _p09(contexto, parametros, pergunta, canal):
    perfil = parametros.perfil
    conteudo = contexto.conteudo
    etapas = leitura.por_id(conteudo.get("stages"))
    rascunho = _Rascunho()
    sorteios = [
        marco
        for marco in perfil.get("classificationMilestones") or []
        if marco.get("orderProduction") == "POR_SORTEIO"
    ]
    # Perfil sem marco por sorteio não chega aqui: `catalogo.resolver` recusa (`FR-1417`).
    for marco in sorteios:
        proprio = bool(marco.get("drawMethod"))
        metodo = marco.get("drawMethod") or conteudo.get("drawMethod") or {}
        base_do_marco = leitura.caminho_do_marco(perfil, marco)
        base = f"{base_do_marco}/drawMethod" if proprio else "/drawMethod"
        onde = leitura.onde_marco(perfil, marco) + (
            " — método próprio deste marco" if proprio else " — método comum do Edital"
        )
        _juntar(
            rascunho.referencias,
            leitura.texto(
                leitura.onde_marco(perfil, marco),
                f"{base_do_marco}/name",
                marco.get("name"),
                rotulo="Nome",
            ),
        )
        if not metodo:
            rascunho.referencias.append(
                leitura.dado(onde, base, "Método do sorteio", "não declarado")
            )
            continue
        for campo, rotulo in (
            ("algorithm", "Algoritmo"),
            ("source", "Fonte"),
            ("occurrence", "Ocorrência"),
        ):
            if metodo.get(campo):
                rascunho.referencias.append(
                    leitura.dado(onde, f"{base}/{campo}", rotulo, metodo[campo])
                )
        if metodo.get("occurrenceAt"):
            rascunho.referencias.append(
                leitura.dado(
                    onde,
                    f"{base}/occurrenceAt",
                    "Quando",
                    leitura.instante_legivel(metodo["occurrenceAt"]),
                )
            )
        _juntar(
            rascunho.referencias,
            leitura.texto(onde, f"{base}/derivation", metodo.get("derivation"), rotulo="Derivação"),
            leitura.texto(
                onde,
                f"{base}/normalization/text",
                (metodo.get("normalization") or {}).get("text"),
                rotulo="Normalização",
            ),
            leitura.texto(
                onde,
                f"{base}/substitutionRule/text",
                (metodo.get("substitutionRule") or {}).get("text"),
                rotulo="Se faltar",
            ),
        )
        rascunho.referencias.append(
            leitura.dado(
                leitura.onde_marco(perfil, marco),
                f"{base_do_marco}/stages",
                "Etapas que antecedem o sorteio",
                _nomes_das_etapas(marco.get("stages") or [], etapas),
            )
        )
    _juntar(rascunho.referencias, *_secoes(contexto, pergunta.acompanha))
    rascunho.explicacao = (
        f"O Perfil {perfil.get('code')} classifica por sorteio, pelo método abaixo, como o "
        "Edital o "
        "declara. A ordem de cada pessoa sai do sorteio realizado, e não desta consulta."
    )
    return rascunho


# ---- P-10, P-11 e P-12 ----------------------------------------------------------------------


def _p10(contexto, parametros, pergunta, canal):
    perfil = parametros.perfil
    conteudo = contexto.conteudo
    base, onde = leitura.caminho_do_perfil(perfil), leitura.onde_perfil(perfil)
    rascunho = _Rascunho()
    forma = perfil.get("callForm")
    if forma:
        rascunho.referencias.append(
            leitura.dado(
                onde,
                f"{base}/callForm",
                "Como a convocação é comunicada",
                rotulos.em_palavras(rotulos.FORMA_DE_CONVOCACAO, forma),
            )
        )
    requerimento = conteudo.get("matriculationRequest") or {}
    if requerimento:
        rascunho.referencias.append(
            leitura.dado(
                "Edital — Requerimento de Matrícula",
                "/matriculationRequest/moment",
                "Quando o Requerimento de Matrícula é enviado",
                rotulos.em_palavras(rotulos.MOMENTO_DO_REQUERIMENTO, requerimento.get("moment")),
            )
        )
        _juntar(
            rascunho.referencias,
            leitura.texto(
                "Edital — Requerimento de Matrícula",
                "/matriculationRequest/declarationText",
                requerimento.get("declarationText"),
                rotulo="Declaração",
            ),
        )
    tratam = [secao for secao in _secoes(contexto, pergunta.trata) if secao is not None]
    rascunho.referencias.extend(tratam)
    forma_em_palavras = rotulos.em_palavras(rotulos.FORMA_DE_CONVOCACAO, forma) if forma else ""
    if tratam:
        rascunho.tipo = DEPENDE_DA_LEITURA
        rascunho.explicacao = explicacao.depende_da_leitura("convocação e matrícula", canal)
        if forma:
            rascunho.explicacao = (
                f"A convocação do Perfil {perfil.get('code')} é comunicada {forma_em_palavras}. "
                + rascunho.explicacao
            )
    elif forma:
        rascunho.explicacao = (
            f"A convocação do Perfil {perfil.get('code')} é comunicada {forma_em_palavras}."
        )
    else:
        rascunho.tipo = NAO_INFORMA
        rascunho.explicacao = explicacao.nao_informa("convocação deste Perfil", canal)
    return rascunho


def _p11(contexto, parametros, pergunta, canal):
    encontrado = canais.canal(contexto.conteudo, contexto.canal_institucional)
    rascunho = _Rascunho()
    rascunho.referencias.extend(encontrado.paragrafos)
    if encontrado.divergente:
        rascunho.tipo = FONTES_DIVERGENTES
        rascunho.explicacao = (
            "O Edital informa mais de um canal para dúvidas, mostrados abaixo. Esta consulta não "
            "escolhe entre eles."
        )
    elif encontrado.origem == CANAL_INSTITUCIONAL and encontrado.contatos:
        # A única fonte de fora do conteúdo, com o desfecho (`FR-1412`, `FR-1441`): é configuração
        # da implantação, e por isso não tem cartão de texto nem de dado — vai dita como tal.
        rascunho.explicacao = (
            "O Edital não informa um canal específico para dúvidas. O canal institucional é "
            f"{encontrado.contatos[0]}."
        )
    elif not encontrado.contatos:
        rascunho.tipo = NAO_INFORMA
        rascunho.explicacao = "Nem o Edital nem a implantação informam um canal para dúvidas."
    else:
        rascunho.explicacao = (
            f"O Edital informa este canal para dúvidas, no texto abaixo: {encontrado.contatos[0]}."
        )
    return rascunho


def _descricao_do_que_contem(ato, atos_por_id):
    """Singular e plural, e o próprio ato à parte: "as Retificações publicadas em X" para uma só,
    e incluindo a própria, era o que a validação de 12/10 achou."""
    if ato.ato == "ORIGINAL":
        return "contém a publicação original"
    anteriores = [
        atos_por_id[identificador]
        for identificador in ato.contem
        if identificador in atos_por_id
        and identificador != ato.publicacao_id
        and atos_por_id[identificador].ato != "ORIGINAL"
    ]
    datas = [leitura.instante_legivel(item.publicado_em) for item in anteriores]
    if not datas:
        return "contém a publicação original e esta Retificação"
    if len(datas) == 1:
        return f"contém a publicação original, a Retificação publicada em {datas[0]} e esta"
    return (
        f"contém a publicação original, as Retificações publicadas em {', '.join(datas[:-1])} "
        f"e em {datas[-1]}, e esta"
    )


def _p12(contexto, parametros, pergunta, canal):
    rascunho = _Rascunho()
    atos_por_id = {ato.publicacao_id: ato for ato in contexto.atos}
    for ato in contexto.atos:
        localizacao = "Publicação original" if ato.ato == "ORIGINAL" else "Retificação"
        rascunho.referencias.append(
            Referencia(
                natureza=DADO,
                localizacao=localizacao,
                rotulo="Publicado em",
                conteudo=(
                    f"{leitura.instante_legivel(ato.publicado_em)}; vigente desde "
                    f"{leitura.instante_legivel(ato.vigente_desde)}; o documento deste ato "
                    f"{_descricao_do_que_contem(ato, atos_por_id)}"
                ),
                origens=(ato,),
            )
        )
    for anexo in contexto.conteudo.get("attachments") or []:
        url = contexto.anexos_publicos.get(str(anexo.get("artifactId")), "")
        rascunho.referencias.append(
            replace(
                leitura.dado(
                    "Anexos do Edital",
                    f"/attachments/id={anexo.get('id')}",
                    "Anexo",
                    anexo.get("label", ""),
                ),
                links=(Link(anexo.get("label", ""), url),) if url else (),
            )
        )
    rascunho.explicacao = (
        "Cada documento abaixo é o de um ato publicado, e diz quais atos contém. O conteúdo que "
        "vigora é o da versão indicada no topo."
    )
    incompleto = documento_de_origem_incompleto(contexto)
    if incompleto:
        rascunho.avisos.append(Aviso("DOCUMENTO_DE_ORIGEM_INCOMPLETO", incompleto))
    return rascunho


def documento_de_origem_incompleto(contexto) -> str:
    """O texto do achado de 12/10, quando ele se aplica à versão vigente (`R-005`), ou `""`."""
    fonte = contexto.fonte_da_versao
    if fonte is None:
        return ""
    faltantes = [ato for ato in contexto.atos if ato.publicacao_id not in set(fonte.contem)]
    if not faltantes:
        return ""
    datas = ", ".join(
        f"a Retificação publicada em {leitura.instante_legivel(ato.publicado_em)}"
        for ato in faltantes
    )
    return (
        "O documento que a página pública oferece como Edital completo é o do ato publicado em "
        f"{leitura.instante_legivel(fonte.publicado_em)}, e não contém {datas}."
    )


CONSTRUTORES = {
    "P-01": _p01,
    "P-02": _p02,
    "P-03": _p03,
    "P-04": _p04,
    "P-05": _p05,
    "P-06": _p06,
    "P-07": _p07,
    "P-08": _p08,
    "P-09": _p09,
    "P-10": _p10,
    "P-11": _p11,
    "P-12": _p12,
}


# ---- o que é comum a toda resposta ---------------------------------------------------------


def no_item(valor, posicao):
    """O item `posicao` do valor: da lista atômica, ou a linha do texto (o parágrafo, `R-010`)."""
    if posicao is None:
        return valor
    if isinstance(valor, list):
        return valor[posicao] if posicao < len(valor) else ABSENT
    if isinstance(valor, str):
        linhas = valor.split("\n")
        return linhas[posicao] if posicao < len(linhas) else ABSENT
    return ABSENT


def _com_origem(contexto, referencia):
    if referencia.natureza == EXPLICACAO or not referencia.caminho:
        return referencia
    return replace(
        referencia,
        origens=referencia.origens
        or origens(referencia.caminho, contexto.proveniencias, contexto.atos),
    )


def _grupos(referencias):
    """Os cartões citáveis por `(caminho, rótulo)`, na ordem da resposta.

    Um grupo tem mais de um cartão quando o caminho é de coleção atômica (os requisitos, os
    parágrafos de um canal): ali a posição não identifica o item, e um acréscimo no início
    deslocaria todos. Esses grupos se comparam pelo que dizem, e não pela posição.
    """
    grupos = {}
    for indice, referencia in enumerate(referencias):
        if referencia.natureza != EXPLICACAO and referencia.caminho:
            grupos.setdefault((referencia.caminho, referencia.rotulo), []).append(
                (indice, referencia)
            )
    return grupos


def _ato_da_mudanca(caminho, versao, novos):
    """A Retificação que muda `caminho` nesta versão futura, entre as que ela acrescenta."""
    novos_ids = {ato.publicacao_id for ato in novos}
    candidatos = [
        ato
        for ato in origens(caminho, versao.proveniencias, versao.atos)
        if ato.publicacao_id in novos_ids
    ]
    if candidatos:
        return candidatos[-1]
    return novos[-1] if novos else None


def _diferencas(antes, depois):
    """`(chave, removidos, acrescidos)` entre dois conjuntos de cartões, grupo a grupo."""
    grupos_antes, grupos_depois = _grupos(antes), _grupos(depois)
    chaves = list(grupos_antes) + [chave for chave in grupos_depois if chave not in grupos_antes]
    for chave in chaves:
        velhos = grupos_antes.get(chave, [])
        novos = grupos_depois.get(chave, [])
        if [ref.conteudo for _, ref in velhos] == [ref.conteudo for _, ref in novos]:
            continue
        restantes = [ref.conteudo for _, ref in novos]
        removidos = []
        for indice, referencia in velhos:
            if referencia.conteudo in restantes:
                restantes.remove(referencia.conteudo)
            else:
                removidos.append((indice, referencia))
        sobra = [ref.conteudo for _, ref in velhos]
        acrescidos = []
        for indice, referencia in novos:
            if referencia.conteudo in sobra:
                sobra.remove(referencia.conteudo)
            else:
                acrescidos.append((indice, referencia))
        yield chave, removidos, acrescidos


def _nome(referencia):
    return f"{referencia.rotulo or referencia.localizacao} ({referencia.localizacao})"


def _futuro(contexto, codigo, perfil, modalidade, referencias):
    """O que cada Retificação já publicada, de vigência futura, muda nesta resposta (`FR-1414`).

    **A mesma pergunta, respondida pelo mesmo construtor sobre o conteúdo futuro**, e comparada
    cartão a cartão. Ler o valor cru no caminho do cartão — como se fazia — dava "UNLIMITED" onde o
    cartão diz "sem limite", uma identidade onde ele diz o nome da Etapa, e deixava de fora o que a
    Retificação acrescenta: um Evento novo saía como "não altera o que esta resposta cita".

    Cada versão futura se compara com a anterior a ela, e não com a vigente: o valor que uma
    Retificação fixa não se repete na data da seguinte. O valor futuro vai no próprio cartão quando
    o grupo tem um cartão só; acréscimo, retirada e coleção vão no aviso.
    """
    if not contexto.futuras:
        return referencias, None
    futuros = {indice: [] for indice in range(len(referencias))}
    atuais = _grupos(referencias)
    linhas = []
    antes, ja_aplicados = referencias, {ato.publicacao_id for ato in contexto.atos}
    for versao in contexto.futuras:
        novos_atos = [ato for ato in versao.atos if ato.publicacao_id not in ja_aplicados]
        ja_aplicados = {ato.publicacao_id for ato in versao.atos}
        quando = leitura.instante_legivel(versao.vigente_desde)
        futuro = replace(
            contexto,
            conteudo=versao.conteudo,
            atos=versao.atos,
            proveniencias=versao.proveniencias,
            futuras=(),
            versao_anterior=None,
            atos_da_versao_anterior=(),
        )
        try:
            depois = _rascunho(futuro, codigo, perfil, modalidade)[1].referencias
        except catalogo.ParametroRecusado as recusa:
            linhas.append(f"A partir de {quando}, por Retificação já publicada: {recusa}")
            depois = []
        mudou = False
        for chave, removidos, acrescidos in _diferencas(antes, depois):
            mudou = True
            ato = _ato_da_mudanca(chave[0], versao, novos_atos)
            por = (
                f", por Retificação publicada em {leitura.instante_legivel(ato.publicado_em)}"
                if ato
                else ""
            )
            unico = len(removidos) == 1 and len(acrescidos) == 1
            if unico:
                referencia, valor = removidos[0][1], acrescidos[0][1].conteudo
                linhas.append(
                    f"A partir de {quando}{por}, {_nome(referencia)} passa a ser: {valor}."
                )
            else:
                for _, referencia in removidos:
                    linhas.append(
                        f"A partir de {quando}{por}, deixa de constar {_nome(referencia)}: "
                        f"{referencia.conteudo}."
                    )
                for _, referencia in acrescidos:
                    linhas.append(
                        f"A partir de {quando}{por}, passa a constar {_nome(referencia)}: "
                        f"{referencia.conteudo}."
                    )
            # No cartão vigente, só o que o identifica sem ambiguidade: o grupo de um cartão.
            vigentes = atuais.get(chave, [])
            if len(vigentes) == 1:
                valor = acrescidos[0][1].conteudo if unico else ("retirado" if removidos else None)
                if valor is not None:
                    futuros[vigentes[0][0]].append(ValorFuturo(valor, versao.vigente_desde, ato))
        if not mudou:
            linhas.append(
                f"Há Retificação publicada com vigência a partir de {quando}. Ela não altera o que "
                "esta resposta cita."
            )
        antes = depois
    com_futuro = tuple(
        replace(referencia, futuro=tuple(futuros[indice])) if futuros[indice] else referencia
        for indice, referencia in enumerate(referencias)
    )
    return com_futuro, Aviso(AVISO_RETIFICACAO_FUTURA, " ".join(linhas))


#: **As perguntas em que o texto citado é a própria resposta ao enunciado** (`D-011`): os
#: requisitos, as Etapas e os marcos, o método do sorteio. Se esse texto remete a um anexo, parte da
#: resposta está lá. Nas outras, a remissão é contexto, e o aviso `DETALHE_EM_ANEXO` basta:
#:
#: - `P-01`, `P-02` e `P-03` respondem com datas e números, que os cartões trazem inteiros — a
#:   descrição de Evento que cita a ficha do Anexo IV não tira data nenhuma da resposta;
#: - na `P-05` o anexo é o modelo do documento a enviar, e na `P-12` os anexos são a pergunta;
#: - `P-06`, `P-08` e `P-10` já são "Depende da leitura" quando há texto sobre o assunto;
#: - na `P-11` o texto é o canal.
ANEXO_NO_NUCLEO = ("P-04", "P-07", "P-09")


def _remissao_a_anexo(contexto, codigo, referencias):
    """`(onde, anexos)` quando o que responde à pergunta remete a anexo que a consulta não lê.

    **"Respondida" exige cobertura do enunciado** (`D-011`). A `P-07` do 92/2026 dizia "Respondida"
    com os critérios de pontuação da prova de títulos no Anexo IV: resposta parcial apresentada como
    completa (validação de 12/10). Conta só o núcleo da resposta — os cartões que não são seção
    inteira. As seções que acompanham não mudam o tipo (`D-007`), e as que tratam do assunto já o
    mudam.
    """
    if codigo not in ANEXO_NO_NUCLEO:
        return None
    onde, rotulos_dos_anexos = [], []
    publicados = anexos.por_identificador(contexto.conteudo)
    for referencia in referencias:
        if referencia.natureza != TEXTO or referencia.caminho.startswith("/sections/"):
            continue
        citados = anexos.citados(referencia.conteudo)
        if not citados:
            continue
        lugar = referencia.localizacao
        if lugar not in onde:
            onde.append(lugar)
        for identificador in citados:
            anexo = publicados.get(identificador)
            rotulo = (
                anexo.get("label", "")
                if anexo is not None
                else f"Anexo {identificador.upper()}, que não está entre os anexos publicados"
            )
            if rotulo not in rotulos_dos_anexos:
                rotulos_dos_anexos.append(rotulo)
    return (onde, rotulos_dos_anexos) if onde else None


def _explicacao_incompleta(explicacao_atual, remissao, canal):
    onde, rotulos_dos_anexos = remissao
    return (
        f"{explicacao_atual} Esta resposta não está completa: {'; '.join(onde)} "
        f"{'remete' if len(onde) == 1 else 'remetem'} ao {'; ao '.join(rotulos_dos_anexos)}, que "
        f"esta consulta não lê. {explicacao.encaminhar(canal)}"
    )


def _aviso_de_anexos(contexto, referencias):
    textos = [referencia.conteudo for referencia in referencias if referencia.natureza == TEXTO]
    encontrados, _inexistentes = anexos.resolver(textos, contexto.conteudo)
    if not encontrados:
        return None
    links = tuple(
        Link(anexo.get("label", ""), contexto.anexos_publicos[str(anexo.get("artifactId"))])
        for anexo in encontrados
        if str(anexo.get("artifactId")) in contexto.anexos_publicos
    )
    nomes = "; ".join(anexo.get("label", "") for anexo in encontrados)
    return Aviso(
        AVISO_DETALHE_EM_ANEXO,
        f"O texto mostrado cita: {nomes}. O detalhe está no anexo, que esta consulta não lê.",
        links,
    )


def _aviso_de_desfecho(contexto):
    desfecho = contexto.desfecho
    if desfecho is None:
        return None
    o_que = "cancelado" if desfecho.operacao == "CANCELADO" else "encerrado"
    quando = f" em {leitura.instante_legivel(desfecho.em)}" if desfecho.em else ""
    if desfecho.do_edital:
        return Aviso(AVISO_DESFECHO, f"Este Edital foi {o_que}{quando}.")
    return Aviso(AVISO_DESFECHO, f"O Processo Seletivo deste Edital foi {o_que}{quando}.")


def _mudanca(contexto):
    anterior = contexto.versao_anterior
    if not anterior or anterior == contexto.versao.id:
        return None
    ja_aplicados = {ato.publicacao_id for ato in contexto.atos_da_versao_anterior}
    agora = {ato.publicacao_id for ato in contexto.atos}
    novos = tuple(ato for ato in contexto.atos if ato.publicacao_id not in ja_aplicados)
    sem_efeito = tuple(
        ato for ato in contexto.atos_da_versao_anterior if ato.publicacao_id not in agora
    )
    return MudancaDeVersao(anterior, novos, sem_efeito)


def _rascunho(contexto, codigo, perfil, modalidade):
    pergunta = catalogo.POR_CODIGO.get(codigo)
    if pergunta is None:
        raise catalogo.ParametroRecusado("Esta pergunta não está no catálogo.")
    parametros = catalogo.resolver(
        pergunta, contexto.conteudo, perfil=perfil, modalidade=modalidade
    )
    canal = canais.em_palavras(canais.canal(contexto.conteudo, contexto.canal_institucional))
    return parametros, CONSTRUTORES[codigo](contexto, parametros, pergunta, canal)


def responder(contexto: Contexto, codigo: str, *, perfil=None, modalidade=None) -> Resposta:
    """A resposta à pergunta `codigo`, toda ela de `contexto.versao` (`FR-1411`).

    Levanta `catalogo.ParametroRecusado` quando a pergunta não se aplica ou o parâmetro não existe
    na versão vigente (`FR-1418`).
    """
    parametros, rascunho = _rascunho(contexto, codigo, perfil, modalidade)
    referencias = tuple(_com_origem(contexto, item) for item in rascunho.referencias)
    remissao = _remissao_a_anexo(contexto, codigo, referencias)
    if remissao is not None and rascunho.tipo == RESPONDIDA:
        # Sem tipo novo (`D-011`): o que falta está em texto que o sistema não lê, como em
        # "Depende da leitura". A explicação do que há se preserva, e o que falta é nomeado.
        rascunho.tipo = DEPENDE_DA_LEITURA
        canal = canais.em_palavras(canais.canal(contexto.conteudo, contexto.canal_institucional))
        rascunho.explicacao = _explicacao_incompleta(rascunho.explicacao, remissao, canal)
    referencias, aviso_de_futuro = _futuro(contexto, codigo, perfil, modalidade, referencias)
    avisos = []
    for aviso in (
        _aviso_de_desfecho(contexto),
        aviso_de_futuro,
        _aviso_de_anexos(contexto, referencias),
    ):
        if aviso is not None:
            avisos.append(aviso)
    avisos.extend(rascunho.avisos)
    return Resposta(
        pergunta=codigo,
        parametros=parametros.como_pares(),
        instante=contexto.instante,
        versao=contexto.versao,
        tipo=rascunho.tipo,
        explicacao=Referencia(
            natureza=EXPLICACAO,
            localizacao="Explicação produzida pelo sistema a partir das fontes abaixo",
            conteudo=rascunho.explicacao,
        ),
        referencias=referencias,
        avisos=tuple(avisos),
        mudanca=_mudanca(contexto),
        situacao=rascunho.situacao,
    )
