"""A apresentação por perguntas do Edital (069, FR-1367 a FR-1376, R-002, R-003, R-009, R-010).

Os Editais submetidos depois da `069` levam no snapshot o catálogo dela, e o documento deles se
organiza pelas perguntas do candidato: quem pode se inscrever, quantas vagas há e onde, como se
inscrever, como será a seleção, como recorrer. As seções que respondem à mesma pergunta saem
reunidas, como subseções N.k (FR-1368), e cada regra gerada sai na seção que trata dela (FR-1369).
O documento abre com um resumo feito só de dado (FR-1370) e um sumário (FR-1372).

**Um plano, e não duas contagens.** `plano(snapshot)` decide antes de escrever quais seções saem,
com que número, e o que vai no corpo de cada uma e em que subseção; a composição, a numeração que as
telas leem (`pdf.numeracao`), os itens que a conferência de remissões lê (`pdf.itens_do_documento`)
e a contagem de tabelas leem todos o mesmo plano. É a "regra só" da `054` (FR-985), agora sobre a
apresentação (R-003).

**O conteúdo é o mesmo da apresentação plana.** As frases são as da redação 2, as mesmas do
`pdf.py`; o que muda é onde cada uma sai e o que se diz uma vez em vez de por Perfil (FR-1374,
FR-1375). O agrupamento é por identidade do dado e da frase impressa, nunca por semelhança, e as
unidades indivisíveis da R-009 — o corte com o empate, os suplentes e a continuação; os critérios de
desempate de um marco — saem inteiras em cada grupo quando diferem.

A apresentação plana — a de antes, para os Editais publicados antes e os consolidados deles — é a do
`pdf.py`, com a redação, a tipografia e a navegação novas (R-016).
"""

import re
from dataclasses import dataclass, field

from processo_seletivo.editais.domain import marcos as regras_do_marco
from processo_seletivo.editais.domain import secoes
from processo_seletivo.publicacoes.domain.vocabulario_da_regra import (
    REDACAO_2,
    frase_da_convocacao,
    inicial_minuscula,
    por_identificador,
)
from processo_seletivo.publicacoes.infrastructure import humano
from processo_seletivo.publicacoes.infrastructure import pdf as composicao_pdf

# Natureza dos itens numerados que só esta apresentação tem (R-003): a subseção textual (membro) e
# a gerada (requisitos, atribuições, regras de classificação, dados do sorteio).
ITEM_SUBSECAO = "subsecao"

TITULO_DOS_REQUISITOS = "Requisitos dos Perfis"
TITULO_DAS_ATRIBUICOES = "Atribuições"
TITULO_DOS_DADOS_DO_SORTEIO = "Dados para conferir o sorteio"

# Até quantas localidades o resumo enumera pelo nome; acima disso, só a contagem (R-010).
LOCALIDADES_NOMEADAS = 5
# Até quantos caracteres uma Etapa é dita pelo nome no resumo, sem vírgula nem travessão (R-010).
NOME_CURTO = 40


# ---------------------------------------------------------------------------
# O plano
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Parte:
    """Um pedaço de uma seção: o texto de uma chave, ou um lugar do conteúdo gerado.

    `numero` e `titulo` existem quando a parte sai como subseção N.k; no corpo da seção, são
    vazios. `etapa` é a Etapa, nas subseções de Etapas.
    """

    natureza: str
    chave: str | None = None
    lugar: str | None = None
    numero: str = ""
    titulo: str = ""
    etapa: dict | None = None


@dataclass(frozen=True)
class SecaoDoDocumento:
    numero: str
    titulo: str
    entrada: secoes.SecaoApresentada
    partes: tuple = ()

    @property
    def rotulo(self):
        return f"{self.numero}. {self.titulo}"


@dataclass(frozen=True)
class Plano:
    """O que o documento por perguntas imprime, decidido antes da primeira linha."""

    secoes: tuple
    numeros: dict = field(default_factory=dict)

    def secao(self, titulo):
        return next((secao for secao in self.secoes if secao.titulo == titulo), None)

    def numero_da(self, titulo):
        secao = self.secao(titulo)
        return secao.numero if secao else ""

    def numero_do_lugar(self, lugar):
        for secao in self.secoes:
            for parte in secao.partes:
                if parte.lugar == lugar:
                    return parte.numero or secao.numero
        return ""


def _secao_do_snapshot(snapshot, chave):
    return next(
        (secao for secao in snapshot.get("sections") or [] if secao.get("key") == chave), None
    )


def _tem_texto(snapshot, chave):
    secao = _secao_do_snapshot(snapshot, chave)
    return bool(secao) and bool(composicao_pdf._paragrafos(secao.get("content", "")))


def _perfis(snapshot):
    return snapshot.get("profiles") or []


def _marcos(snapshot):
    return [
        (perfil, marco)
        for perfil in _perfis(snapshot)
        for marco in perfil.get("classificationMilestones") or []
    ]


def _evento_de_inscricao(snapshot):
    return next(
        (
            evento
            for evento in snapshot.get("schedule") or []
            if isinstance(evento, dict) and evento.get("isRegistrationPeriod")
        ),
        None,
    )


def _ha_lembrete(snapshot):
    requerimento = snapshot.get("matriculationRequest")
    return isinstance(requerimento, dict) and requerimento.get("moment") == "AT_ENROLLMENT"


def _metodos_de_sorteio(snapshot):
    return [
        (perfil, marco)
        for perfil, marco in _marcos(snapshot)
        if regras_do_marco.declara_sorteio(marco)
        and composicao_pdf.dados_do_sorteio(snapshot, perfil, marco)
    ]


def _lugar_presente(snapshot, lugar):
    """O lugar tem o que dizer neste snapshot?"""
    perfis = _perfis(snapshot)
    if lugar == secoes.REQUISITOS_DOS_PERFIS:
        return any(perfil.get("requirements") for perfil in perfis)
    if lugar == secoes.VAGAS:
        return bool(perfis)
    if lugar == secoes.ATRIBUICOES:
        return any(composicao_pdf._paragrafos(perfil.get("duties")) for perfil in perfis)
    if lugar == secoes.PERIODO:
        return _evento_de_inscricao(snapshot) is not None
    if lugar == secoes.DADOS_DECLARADOS:
        return any(perfil.get("declaredFacts") for perfil in perfis)
    if lugar == secoes.TETO:
        return composicao_pdf.teto_de_inscricoes(snapshot) is not None
    if lugar == secoes.LEMBRETE_DO_REQUERIMENTO:
        return _ha_lembrete(snapshot)
    if lugar == secoes.REGRAS_DOS_MARCOS:
        return bool(_marcos(snapshot))
    if lugar == secoes.DADOS_DO_SORTEIO:
        return bool(_metodos_de_sorteio(snapshot))
    if lugar == secoes.ETAPAS:
        return bool(snapshot.get("stages"))
    if lugar == secoes.RECURSO_DOS_MARCOS:
        return any(composicao_pdf.frase_do_recurso(marco) for _, marco in _marcos(snapshot))
    if lugar == secoes.FORMA_DE_CONVOCACAO:
        return any(frase_da_convocacao(perfil.get("callForm")) for perfil in perfis)
    if lugar == secoes.REQUERIMENTO:
        return bool(composicao_pdf.requerimento_de_matricula(snapshot))
    return False


def _principal_presente(snapshot, chave):
    catalogada = secoes.POR_CHAVE.get(chave)
    if catalogada is None:
        return False
    if catalogada.gerada:
        return bool(snapshot.get(catalogada.source))
    return _tem_texto(snapshot, chave)


# Os lugares que saem como subseção, e com que título. Os demais saem no corpo da seção.
_SUBSECAO_DO_LUGAR = {
    secoes.ATRIBUICOES: TITULO_DAS_ATRIBUICOES,
    secoes.DADOS_DO_SORTEIO: TITULO_DOS_DADOS_DO_SORTEIO,
}


def _titulo_das_regras(snapshot):
    """ "Sorteio" quando todo marco sorteia; senão, "Classificação" (contrato do documento §4)."""
    marcos = [marco for _, marco in _marcos(snapshot)]
    if marcos and all(marco.get("orderProduction") == "POR_SORTEIO" for marco in marcos):
        return "Sorteio"
    return "Classificação"


def plano(snapshot):
    """As seções do documento por perguntas, numeradas sobre as que existem (FR-1367, R-003).

    Uma seção sai quando tem o que dizer: o texto de uma das suas chaves, ou um lugar gerado com
    dado. As subseções N.k são contadas dentro de cada seção, na ordem das partes. Uma seção sem
    chave principal e com uma parte só a diz no corpo, sem subtítulo.
    """
    secoes_ = []
    numeros = {secao.get("key"): None for secao in snapshot.get("sections") or []}
    if _tem_texto(snapshot, composicao_pdf.SECAO_DE_PREAMBULO):
        numeros[composicao_pdf.SECAO_DE_PREAMBULO] = 0
    for entrada in secoes.APRESENTACAO:
        partes = []
        for parte in entrada.ordem:
            if parte == entrada.principal:
                if _principal_presente(snapshot, parte):
                    partes.append(Parte("principal", chave=parte))
            elif parte in secoes.POR_CHAVE:
                if _tem_texto(snapshot, parte):
                    titulo = secoes.POR_CHAVE[parte].title
                    partes.append(Parte("membro", chave=parte, titulo=titulo))
            elif parte == secoes.ETAPAS:
                for etapa in snapshot.get("stages") or []:
                    partes.append(
                        Parte("etapa", lugar=parte, titulo=etapa.get("name", ""), etapa=etapa)
                    )
            elif _lugar_presente(snapshot, parte):
                titulo = _SUBSECAO_DO_LUGAR.get(parte, "")
                if parte == secoes.REGRAS_DOS_MARCOS:
                    titulo = _titulo_das_regras(snapshot)
                if parte == secoes.REQUISITOS_DOS_PERFIS:
                    titulo = TITULO_DOS_REQUISITOS
                partes.append(Parte("gerada", lugar=parte, titulo=titulo))
        # O que sai sob a pergunta mas não depende do resto: o lembrete do Requerimento só tem
        # sentido se a seção existir por outra razão.
        substantivas = [p for p in partes if p.lugar != secoes.LEMBRETE_DO_REQUERIMENTO]
        if not substantivas:
            continue
        numero = str(len(secoes_) + 1)
        sozinha = entrada.principal is None and len(partes) == 1
        numeradas, k = [], 0
        for parte in partes:
            vai_em_subsecao = not sozinha and (
                parte.natureza in ("membro", "etapa")
                or (parte.natureza == "gerada" and parte.titulo)
            )
            if vai_em_subsecao:
                k += 1
                numeradas.append(_com_numero(parte, f"{numero}.{k}"))
            else:
                numeradas.append(_com_numero(parte, "", titulo=""))
        secao = SecaoDoDocumento(numero, entrada.titulo, entrada, tuple(numeradas))
        secoes_.append(secao)
        # A principal tem o número da seção mesmo sem texto, quando a seção sai pela norma que o
        # sistema escreve nela — a declaração do Requerimento em "Como será a matrícula?", o
        # recurso dos marcos em "Como recorrer?". É onde o texto dela sairia, e é o que a etapa
        # Conteúdo diz a quem elabora, como a plana faz com a seção de norma (054, UX-132).
        if entrada.principal in numeros:
            numeros[entrada.principal] = numero
        for parte in numeradas:
            if parte.chave:
                numeros[parte.chave] = parte.numero or numero
            if parte.natureza == "etapa":
                numeros[secoes.CHAVE_DAS_ETAPAS] = numero
    return Plano(tuple(secoes_), numeros)


def _com_numero(parte, numero, titulo=None):
    return Parte(
        parte.natureza,
        chave=parte.chave,
        lugar=parte.lugar,
        numero=numero,
        titulo=parte.titulo if titulo is None else titulo,
        etapa=parte.etapa,
    )


def numeracao(snapshot):
    """`{chave: número}` da apresentação por perguntas: "N", "N.k", `0` ou `None` (R-003)."""
    numeros = plano(snapshot).numeros
    return {chave: numeros.get(chave) for chave in numeros}


def membros_no_corpo(snapshot):
    """`{chave: "3. Quem pode se inscrever?"}` do membro que sai como corpo da seção, sem subtítulo.

    É a seção sem principal com uma parte só (`plano`): o número dela é o da seção, e "3.
    Público-alvo" nas telas nomearia um título que o documento não imprime.
    """
    return {
        parte.chave: secao.rotulo
        for secao in plano(snapshot).secoes
        for parte in secao.partes
        if parte.natureza == "membro" and not parte.numero
    }


def faixa_das_etapas(snapshot):
    """Os números das Etapas, que saem como subseções da seleção: "8.3", "8.3 a 8.4" ou vazio.

    As telas — a etapa Conteúdo e a Revisão — dizem com eles onde as Etapas saem (R-003).
    """
    numeros = [
        parte.numero
        for secao in plano(snapshot).secoes
        for parte in secao.partes
        if parte.natureza == "etapa"
    ]
    if not numeros:
        return ""
    return numeros[0] if len(numeros) == 1 else f"{numeros[0]} a {numeros[-1]}"


def itens(snapshot):
    """As seções e subseções que o documento imprime com número (065, R-003)."""
    saida = []
    for secao in plano(snapshot).secoes:
        saida.append(composicao_pdf.ItemDoDocumento(secao.numero, "secao", secao.titulo))
        for parte in secao.partes:
            if not parte.numero:
                continue
            natureza = composicao_pdf.ITEM_ETAPA if parte.natureza == "etapa" else ITEM_SUBSECAO
            saida.append(composicao_pdf.ItemDoDocumento(parte.numero, natureza, parte.titulo))
    return saida


# ---------------------------------------------------------------------------
# O resumo (FR-1370, FR-1371, R-010)
# ---------------------------------------------------------------------------

TITULO_DO_RESUMO = "Resumo deste Edital"
NOTA_DO_RESUMO = (
    "Este resumo repete informações do Edital. As regras completas estão nos itens indicados."
)
# Números ditos por extenso no resumo, no feminino de "localidades" e "vagas".
_EXTENSO_FEMININO = {
    1: "uma",
    2: "duas",
    3: "três",
    4: "quatro",
    5: "cinco",
    6: "seis",
    7: "sete",
    8: "oito",
    9: "nove",
    10: "dez",
}


def _item_do_resumo(numero):
    return f" (item {numero})" if numero else ""


def linhas_do_resumo(snapshot, plano_):
    """`[(rótulo, valor)]` do resumo — só dado estruturado, cada linha com o item (R-010).

    Nenhuma linha inventa o que o dado não diz: a do cadastro só sai quando ele é igual em todos os
    Perfis; a da seleção, quando todos os marcos têm a mesma forma; a das inscrições, quando há o
    Evento marcado como período de inscrições.
    """
    perfis = _perfis(snapshot)
    linhas = []
    item_das_vagas = plano_.numero_da("Quantas vagas há, e onde?")
    com_vaga = [perfil for perfil in perfis if _total(perfil) > 0]
    total = sum(_total(perfil) for perfil in com_vaga)
    # As vagas por localidade só quando todo Perfil diz a sua: sem ela, o código no lugar da
    # localidade ("1 vaga em P1") se leria como um lugar.
    com_localidade = all(str(perfil.get("locality") or "").strip() for perfil in perfis)
    if perfis and len(com_vaga) == len(perfis) and com_localidade:
        localidades = list(
            dict.fromkeys(perfil.get("locality") or perfil.get("code", "") for perfil in perfis)
        )
        quantas = len(localidades)
        vagas = f"{total} vaga" if total == 1 else f"{total} vagas"
        if quantas == 1:
            valor = f"{vagas} em {localidades[0]}"
        else:
            em = _EXTENSO_FEMININO.get(quantas, str(quantas))
            valor = f"{vagas} em {em} localidades"
            if quantas <= LOCALIDADES_NOMEADAS:
                valor += f": {composicao_pdf._enumerar(localidades)}"
        linhas.append(("Vagas", f"{valor}{_item_do_resumo(item_das_vagas)}."))
    elif com_vaga and len(com_vaga) == len(perfis):
        codigos = faixa_de_codigos(perfil.get("code", "") for perfil in com_vaga)
        vagas = f"{total} vaga" if total == 1 else f"{total} vagas"
        perfil_ = "no Perfil" if len(com_vaga) == 1 else "nos Perfis"
        linhas.append(("Vagas", f"{vagas}, {perfil_} {codigos}{_item_do_resumo(item_das_vagas)}."))
    elif com_vaga:
        codigos = faixa_de_codigos(perfil.get("code", "") for perfil in com_vaga)
        imediatas = "vaga imediata" if total == 1 else "vagas imediatas"
        perfil_ = "no Perfil" if len(com_vaga) == 1 else "nos Perfis"
        valor = f"{total} {imediatas}, {perfil_} {codigos}"
        demais = [perfil for perfil in perfis if _total(perfil) == 0]
        if all(perfil.get("reserveType") not in (None, "", "NONE") for perfil in demais):
            valor += "; os demais formam cadastro de reserva"
        linhas.append(("Vagas", f"{valor}{_item_do_resumo(item_das_vagas)}."))
    elif perfis:
        valor = "não há vaga imediata"
        if all(perfil.get("reserveType") not in (None, "", "NONE") for perfil in perfis):
            valor += "; há cadastro de reserva"
        linhas.append(("Vagas", f"{valor}{_item_do_resumo(item_das_vagas)}."))
    cadastros = {composicao_pdf._reserva(perfil, redacao=REDACAO_2) for perfil in perfis}
    if len(cadastros) == 1:
        cadastro = cadastros.pop()
        if cadastro not in ("—", ""):
            if cadastro.startswith("até"):
                cadastro = f"{cadastro} por Perfil"
            linhas.append(("Cadastro de reserva", f"{cadastro}{_item_do_resumo(item_das_vagas)}."))
    item_da_inscricao = plano_.numero_da("Como se inscrever?")
    if evento := _evento_de_inscricao(snapshot):
        periodo = composicao_pdf._periodo_do_evento(evento)
        linhas.append(("Inscrições", f"{periodo}{_item_do_resumo(item_da_inscricao)}."))
    teto = snapshot.get("maxInscricoesPorCandidato")
    if isinstance(teto, int) and not isinstance(teto, bool):
        quantas = composicao_pdf._numero_por_extenso(teto, feminino=True)
        valor = f"até {quantas} {'inscrição' if teto == 1 else 'inscrições'}"
        linhas.append(("Por candidato", f"{valor}{_item_do_resumo(item_da_inscricao)}."))
    if selecao := _selecao_em_poucas_palavras(snapshot):
        item = plano_.numero_da("Como será a seleção?")
        linhas.append(("Seleção", f"{selecao}{_item_do_resumo(item)}."))
    if item_do_cronograma := plano_.numero_da("Cronograma"):
        linhas.append(("Datas", f"no Cronograma{_item_do_resumo(item_do_cronograma)}."))
    return linhas


def _etapa_em_poucas_palavras(etapa):
    """O nome curto da Etapa, ou a natureza dela — sem reproduzir nome longo (FR-1371, R-010)."""
    nome = str(etapa.get("name") or "").strip()
    if nome and len(nome) <= NOME_CURTO and not re.search(r"[,—–]", nome):
        return nome
    caracteres = composicao_pdf._enumerar(
        [rotulo for chave, rotulo in composicao_pdf.CARATER_DA_ETAPA if etapa.get(chave)]
    )
    return f"uma etapa {caracteres}" if caracteres else "uma etapa"


def _selecao_em_poucas_palavras(snapshot):
    """A forma da ordem e as Etapas, quando todos os marcos têm a mesma forma (R-010)."""
    marcos = [marco for _, marco in _marcos(snapshot)]
    formas = {marco.get("orderProduction") for marco in marcos}
    if len(formas) != 1 or None in formas:
        return ""
    forma = formas.pop()
    etapas = sorted(snapshot.get("stages") or [], key=lambda etapa: etapa.get("order") or 0)
    if forma == "POR_SORTEIO":
        seguintes = [_etapa_em_poucas_palavras(etapa) for etapa in etapas]
        texto = "sorteio"
        # "com", e não "seguido de": a Etapa de habilitação ao sorteio vem antes dele, e o dado
        # não diz a ordem entre o sorteio e as demais (FR-1370, só dado).
        if seguintes:
            texto += f", com {composicao_pdf._enumerar(seguintes)}"
        return texto
    combinadas = {
        str(identificador) for marco in marcos for identificador in marco.get("stages") or []
    }
    nas = [_etapa_em_poucas_palavras(e) for e in etapas if str(e.get("id")) in combinadas]
    depois = [_etapa_em_poucas_palavras(e) for e in etapas if str(e.get("id")) not in combinadas]
    texto = "pontuação"
    if nas:
        texto += f" em {composicao_pdf._enumerar(nas)}"
    if depois:
        texto += f", com {composicao_pdf._enumerar(depois)}"
    return texto


def _resumo(composicao, snapshot, plano_):
    """O resumo, em bloco destacado, logo depois do preâmbulo (FR-1370, FR-1382)."""
    linhas = linhas_do_resumo(snapshot, plano_)
    if not linhas:
        return
    with composicao.bloco(moldura=composicao_pdf.DESTAQUE):
        composicao.escrever(
            TITULO_DO_RESUMO,
            tamanho=composicao_pdf.CORPO_SUBSECAO,
            fonte=composicao_pdf.NEGRITO,
            recuo=composicao_pdf.RECUO_NO_DESTAQUE,
            antes=composicao_pdf.ANTES_DE_SECAO,
            junto=True,
        )
        composicao_pdf._pares(
            composicao, [list(linha) for linha in linhas], recuo=composicao_pdf.RECUO_NO_DESTAQUE
        )
        composicao.escrever(
            NOTA_DO_RESUMO,
            tamanho=composicao_pdf.CORPO_TEXTO - 1,
            recuo=composicao_pdf.RECUO_NO_DESTAQUE,
            antes=composicao_pdf.ANTES_DE_PARAGRAFO,
        )
        composicao.espaco(4.0)


# ---------------------------------------------------------------------------
# Agrupamento por identidade (R-009)
# ---------------------------------------------------------------------------


def faixa_de_codigos(codigos):
    """Os códigos de um grupo: "TP-01 a TP-16" só quando contíguos, sem lacuna (FR-1375).

    Contíguos são os de mesmo prefixo, mesma largura numérica e números seguidos, na ordem em que
    vêm. "TP-01, TP-03 e TP-04" sai enumerado — uma faixa diria que o TP-02 está no grupo.
    """
    codigos = list(codigos)
    partes = [re.fullmatch(r"(.*?)(\d+)", codigo or "") for codigo in codigos]
    if len(codigos) > 2 and all(partes):
        prefixos = {casado[1] for casado in partes}
        larguras = {len(casado[2]) for casado in partes}
        numeros = [int(casado[2]) for casado in partes]
        if (
            len(prefixos) == 1
            and len(larguras) == 1
            and numeros == list(range(numeros[0], numeros[0] + len(numeros)))
        ):
            return f"{codigos[0]} a {codigos[-1]}"
    return composicao_pdf._enumerar(codigos)


def _agrupar(perfis, chave):
    """Os Perfis de mesma chave, na ordem do primeiro de cada grupo — inclusive o grupo de um."""
    grupos = {}
    for perfil in perfis:
        grupos.setdefault(chave(perfil), []).append(perfil)
    return list(grupos.items())


def rotulo_do_grupo(grupo, total):
    """ "Para todos os Perfis", "Para o Perfil X — nome", "Para os Perfis A a C"."""
    if len(grupo) == total:
        return "Para todos os Perfis"
    if len(grupo) == 1:
        return f"Para o Perfil {composicao_pdf._rotulo_do_perfil(grupo[0])}"
    return f"Para os Perfis {faixa_de_codigos(p.get('code', '') for p in grupo)}"


def rotulo_por_codigos(grupo, total):
    """ "Para todos os Perfis", "Para o Perfil P1", "Para os Perfis TP-01 a TP-16" — sem o nome."""
    if len(grupo) == total:
        return "Para todos os Perfis"
    if len(grupo) == 1:
        return f"Para o Perfil {grupo[0].get('code', '')}"
    return f"Para os Perfis {faixa_de_codigos(p.get('code', '') for p in grupo)}"


# ---------------------------------------------------------------------------
# A composição
# ---------------------------------------------------------------------------


def _titulo_de_secao(composicao, rotulo):
    composicao.escrever(
        rotulo,
        tamanho=composicao_pdf.CORPO_TITULO_DE_SECAO,
        fonte=composicao_pdf.NEGRITO,
        antes=composicao_pdf.ANTES_DE_SECAO,
        junto=True,
    )


def _titulo_de_subsecao(composicao, rotulo):
    composicao.escrever(
        rotulo,
        tamanho=composicao_pdf.CORPO_SUBSECAO,
        fonte=composicao_pdf.NEGRITO,
        antes=composicao_pdf.ANTES_DE_BLOCO + 4,
        junto=True,
    )


def _rotulo_de_grupo(composicao, rotulo, *, antes=composicao_pdf.ANTES_DE_BLOCO):
    composicao.escrever(
        rotulo,
        tamanho=composicao_pdf.CORPO_TEXTO,
        fonte=composicao_pdf.NEGRITO,
        antes=antes,
        junto=True,
    )


def _paragrafo(composicao, texto, *, antes=composicao_pdf.ANTES_DE_PARAGRAFO, recuo=0.0):
    composicao.escrever(texto, recuo=recuo, antes=antes, justificar=True)


def _texto(composicao, snapshot, chave, *, antes=composicao_pdf.ANTES_DE_BLOCO):
    """O texto de quem redigiu, como foi escrito (FR-1395) — sem a norma, que tem lugar próprio."""
    secao = _secao_do_snapshot(snapshot, chave) or {}
    for indice, paragrafo in enumerate(composicao_pdf._paragrafos(secao.get("content", ""))):
        _paragrafo(
            composicao, paragrafo, antes=antes if indice == 0 else composicao_pdf.ANTES_DE_PARAGRAFO
        )


def _par(composicao, rotulo, valor, *, recuo=composicao_pdf.RECUO_NO_DESTAQUE):
    composicao_pdf._pares(composicao, [[rotulo, valor]], recuo=recuo)


def compor(composicao, snapshot, *, paginas=None, unidade=None, fecho=None):
    """O corpo do documento por perguntas: preâmbulo, resumo, sumário e as seções."""
    plano_ = plano(snapshot)
    tabelas = composicao_pdf._Numerador()
    _preambulo(composicao, snapshot)
    _resumo(composicao, snapshot, plano_)
    composicao_pdf.sumario(composicao, [secao.rotulo for secao in plano_.secoes], paginas or {})
    for indice, secao in enumerate(plano_.secoes, 1):
        ultima = indice == len(plano_.secoes)
        with composicao_pdf.com_o_fecho(composicao, fecho if ultima else None):
            _titulo_de_secao(composicao, secao.rotulo)
            for parte in secao.partes:
                if parte.numero:
                    _titulo_de_subsecao(composicao, f"{parte.numero} {parte.titulo}")
                _parte(composicao, snapshot, plano_, secao, parte, tabelas)
    if not plano_.secoes and fecho is not None:
        fecho()
    return plano_


def _preambulo(composicao, snapshot):
    secao = _secao_do_snapshot(snapshot, composicao_pdf.SECAO_DE_PREAMBULO) or {}
    for indice, paragrafo in enumerate(composicao_pdf._paragrafos(secao.get("content", ""))):
        composicao.escrever(
            paragrafo,
            antes=composicao_pdf.ANTES_DE_SECAO
            if indice == 0
            else composicao_pdf.ANTES_DE_PARAGRAFO,
            justificar=True,
        )


def _parte(composicao, snapshot, plano_, secao, parte, tabelas):
    antes = composicao_pdf.ANTES_DE_BLOCO if not parte.numero else composicao_pdf.ANTES_DE_PARAGRAFO
    if parte.natureza in ("principal", "membro"):
        catalogada = secoes.POR_CHAVE[parte.chave]
        if catalogada.gerada:
            _gerada_pela_chave(composicao, snapshot, plano_, parte.chave, tabelas)
        else:
            _texto(composicao, snapshot, parte.chave, antes=antes)
        return
    if parte.natureza == "etapa":
        eventos = {
            evento.get("id"): evento
            for evento in snapshot.get("schedule") or []
            if isinstance(evento, dict)
        }
        if frase := composicao_pdf.frase_da_etapa(parte.etapa, eventos):
            _paragrafo(composicao, frase, antes=composicao_pdf.ANTES_DE_PARAGRAFO)
        return
    if parte.lugar == secoes.LEMBRETE_DO_REQUERIMENTO:
        _lembrete(
            composicao,
            snapshot,
            plano_,
            tabelas,
            na_inscricao=secao.entrada.principal == "inscricao",
        )
        return
    COMPOSICAO_DO_LUGAR[parte.lugar](composicao, snapshot, plano_, tabelas)


def _gerada_pela_chave(composicao, snapshot, plano_, chave, tabelas):
    if chave == "perfis":
        return  # as vagas saem pelo lugar `VAGAS`, logo depois
    if chave == "cronograma":
        composicao_pdf._cronograma(composicao, snapshot, 0, tabelas)
    elif chave == "documentos-exigidos":
        composicao_pdf._documentos_exigidos(composicao, snapshot, 0, tabelas)
    elif chave == "anexos":
        composicao_pdf._anexos(composicao, snapshot, 0, tabelas)


# --- Quem pode se inscrever? ------------------------------------------------------------------


def _requisitos_dos_perfis(composicao, snapshot, plano_, tabelas):
    """Os requisitos de cada Perfil, uma vez por lista idêntica (FR-1369, FR-1375)."""
    perfis = [perfil for perfil in _perfis(snapshot) if perfil.get("requirements")]
    grupos = _agrupar(perfis, lambda perfil: tuple(perfil.get("requirements") or ()))
    total = len(_perfis(snapshot))
    for requisitos, grupo in grupos:
        if len(grupos) > 1 or len(grupo) != total:
            _rotulo_de_grupo(composicao, f"{rotulo_do_grupo(grupo, total)}:")
        for posicao, requisito in enumerate(requisitos):
            composicao_pdf._item(
                composicao,
                "•",
                requisito,
                recuo=0.0,
                antes=composicao_pdf.ANTES_DE_LINHA
                if posicao or len(grupos) > 1
                else composicao_pdf.ANTES_DE_PARAGRAFO,
            )


# --- Quantas vagas há, e onde? ------------------------------------------------------------------


def _listas_reservadas(perfis):
    """As listas reservadas, na ordem do documento, com o nome e o código (068, R-005)."""
    ordem = composicao_pdf._ordem_das_listas(perfis)[1:]
    nomes = {}
    for perfil in perfis:
        geral = perfil.get("generalCompetitionModalityId")
        for modalidade in perfil.get("competitionModalities") or []:
            if modalidade.get("id") == geral:
                continue
            nomes.setdefault(composicao_pdf._rotulo_da_lista(modalidade), modalidade)
    return [(rotulo, nomes.get(rotulo, {})) for rotulo in ordem]


def _vagas_por_lista(perfil):
    """`{rótulo da lista: vagas}` do quadro do Perfil, com a ampla concorrência pela linha geral."""
    vagas = {}
    for linha in perfil.get("vacancyTable") or []:
        if not linha.get("modalityId"):
            vagas[composicao_pdf.AMPLA_CONCORRENCIA] = linha.get("immediateVacancies", 0)
    for rotulo, _, linha in composicao_pdf._reservadas_no_quadro(perfil):
        vagas[rotulo] = linha.get("immediateVacancies", 0)
    return vagas


def _total(perfil):
    try:
        return int(perfil.get("immediateVacancies") or 0)
    except (TypeError, ValueError):
        return 0


def _vagas(composicao, snapshot, plano_, tabelas):
    """A seção de vagas pelo dado (FR-1373, FR-1374; contrato do documento §3)."""
    perfis = _perfis(snapshot)
    if not perfis:
        return
    com_vaga = [perfil for perfil in perfis if _total(perfil) > 0]
    listas = [rotulo for rotulo, _ in _listas_reservadas(perfis)]
    nomes = {perfil.get("name") for perfil in perfis}
    if len(com_vaga) == len(perfis):
        _matriz_de_vagas(composicao, perfis, listas, len(nomes) > 1, tabelas)
    else:
        _vagas_em_partes(composicao, perfis, com_vaga, listas, tabelas)
    _caracteristicas(composicao, perfis, tabelas)
    if frase := composicao_pdf.frase_dos_atributos_comuns(perfis):
        _paragrafo(composicao, frase, antes=composicao_pdf.ANTES_DE_BLOCO)
    _reserva_de_vagas(composicao, perfis, tabelas)
    _reversao(composicao, perfis, com_vaga)


def _celulas_das_listas(perfil, listas):
    vagas = _vagas_por_lista(perfil)
    return [
        str(vagas[rotulo]) if rotulo in vagas else "—"
        for rotulo in (composicao_pdf.AMPLA_CONCORRENCIA, *listas)
    ]


def _matriz_de_vagas(composicao, perfis, listas, nomeia, tabelas):
    """Todo Perfil com vaga imediata: uma tabela Perfil × lista × total, com a linha de total."""
    linhas = []
    for perfil in perfis:
        linhas.append(
            [
                perfil.get("code", ""),
                *([perfil.get("name", "")] if nomeia else []),
                perfil.get("locality", "") or "—",
                *_celulas_das_listas(perfil, listas),
                str(_total(perfil)),
            ]
        )
    fixas = 3 if nomeia else 2
    somas = []
    for coluna in range(fixas, len(linhas[0])):
        valores = [linha[coluna] for linha in linhas if linha[coluna] != "—"]
        somas.append(str(sum(int(valor) for valor in valores)) if valores else "—")
    with composicao.bloco():
        composicao_pdf._tabela(
            composicao,
            [
                "Código",
                *(["Perfil"] if nomeia else []),
                "Localidade",
                "Ampla concorrência",
                *listas,
                "Total",
            ],
            linhas,
            recuo=0.0,
            alinhamentos=[
                composicao_pdf.ESQUERDA,
                *([composicao_pdf.ESQUERDA] * (fixas - 1)),
                *([composicao_pdf.CENTRO] * (len(listas) + 2)),
            ],
            legenda=tabelas.legenda("Vagas por Perfil e lista de concorrência"),
            rodape=["Total", *([""] * (fixas - 1)), *somas],
        )


def _vagas_em_partes(composicao, perfis, com_vaga, listas, tabelas):
    """Nem todo Perfil tem vaga imediata: os Perfis à parte, e as vagas dos que as têm."""
    total = sum(_total(perfil) for perfil in com_vaga)
    if com_vaga:
        codigos = faixa_de_codigos(perfil.get("code", "") for perfil in com_vaga)
        plural = "vagas imediatas" if total != 1 else "vaga imediata"
        perfil_ = "nos Perfis" if len(com_vaga) > 1 else "no Perfil"
        _paragrafo(
            composicao,
            f"São {total} {plural}, {perfil_} {codigos}.",
            antes=composicao_pdf.ANTES_DE_BLOCO,
        )
    else:
        _paragrafo(composicao, "Não há vagas imediatas.", antes=composicao_pdf.ANTES_DE_BLOCO)
    grupos = _agrupar(perfis, lambda perfil: perfil.get("name", ""))
    avulsos = [grupo[0] for _, grupo in grupos if len(grupo) == 1]
    if avulsos:
        with composicao.bloco():
            composicao_pdf._tabela(
                composicao,
                ["Código", "Perfil", "Localidade", "Vagas imediatas"],
                [
                    [
                        perfil.get("code", ""),
                        perfil.get("name", ""),
                        perfil.get("locality", "") or "—",
                        composicao_pdf.vagas_impressas(perfil, _total(perfil)),
                    ]
                    for perfil in avulsos
                ],
                recuo=0.0,
                alinhamentos=[
                    composicao_pdf.ESQUERDA,
                    composicao_pdf.ESQUERDA,
                    composicao_pdf.ESQUERDA,
                    composicao_pdf.CENTRO,
                ],
                legenda=tabelas.legenda("Perfis"),
                # O Perfil de cadastro de reserva sem vaga sai `CR`, com a nota abaixo (096, D-006):
                # a mesma regra da tabela de Perfis da apresentação plana, pela mesma função.
                nota=composicao_pdf.nota_da_sigla(avulsos),
            )
    for nome, grupo in grupos:
        if len(grupo) == 1:
            continue
        codigos = faixa_de_codigos(perfil.get("code", "") for perfil in grupo)
        with composicao.bloco():
            composicao_pdf._tabela(
                composicao,
                ["Código", "Localidade", "Vagas imediatas"],
                [
                    [
                        perfil.get("code", ""),
                        perfil.get("locality", "") or "—",
                        composicao_pdf.vagas_impressas(perfil, _total(perfil)),
                    ]
                    for perfil in grupo
                ],
                recuo=0.0,
                alinhamentos=[
                    composicao_pdf.ESQUERDA,
                    composicao_pdf.ESQUERDA,
                    composicao_pdf.CENTRO,
                ],
                legenda=tabelas.legenda(f"{nome} — Perfis {codigos}"),
                nota=composicao_pdf.nota_da_sigla(grupo),
            )
    if com_vaga:
        with composicao.bloco():
            composicao_pdf._tabela(
                composicao,
                ["Código", "Ampla concorrência", *listas, "Total"],
                [
                    [
                        perfil.get("code", ""),
                        *_celulas_das_listas(perfil, listas),
                        str(_total(perfil)),
                    ]
                    for perfil in com_vaga
                ],
                recuo=0.0,
                alinhamentos=[composicao_pdf.ESQUERDA]
                + [composicao_pdf.CENTRO] * (len(listas) + 2),
                legenda=tabelas.legenda("Vagas imediatas por lista de concorrência"),
            )


# Os atributos do Perfil que a frase "Em todos os Perfis" diz quando são iguais em todos (FR-1374),
# e que, quando diferem, saem numa tabela, um Perfil por linha.
_ATRIBUTOS = (
    ("Descrição", "description"),
    ("Carga horária", "workload"),
    ("Remuneração", "compensation"),
)


def _caracteristicas(composicao, perfis, tabelas):
    """Os atributos que **diferem** entre os Perfis, numa tabela — os iguais vão na frase P1."""
    if len(perfis) < 2:
        return
    colunas = []
    # A frase P1 só leva a descrição junto do nome comum: com nomes diferentes, a descrição igual
    # em todos vem para a tabela, ou não sairia em lugar nenhum.
    nome_comum = composicao_pdf._igual_em_todos(perfis, "name")
    for rotulo, chave in _ATRIBUTOS:
        valores = {repr(perfil.get(chave) or "") for perfil in perfis}
        sem_lugar_na_frase = (
            chave == "description" and not nome_comum and any(p.get(chave) for p in perfis)
        )
        if len(valores) > 1 or sem_lugar_na_frase:
            colunas.append((rotulo, lambda perfil, chave=chave: perfil.get(chave) or "—"))
    cadastros = {composicao_pdf.frase_do_cadastro(perfil) for perfil in perfis}
    if len(cadastros) > 1:
        colunas.append(
            (
                "Cadastro de reserva",
                lambda perfil: composicao_pdf._reserva(perfil, redacao=REDACAO_2),
            )
        )
    if not colunas:
        return
    with composicao.bloco():
        composicao_pdf._tabela(
            composicao,
            ["Código", *(rotulo for rotulo, _ in colunas)],
            [
                [perfil.get("code", ""), *(valor(perfil) for _, valor in colunas)]
                for perfil in perfis
            ],
            recuo=0.0,
            legenda=tabelas.legenda("Características dos Perfis"),
        )


def _reserva_de_vagas(composicao, perfis, tabelas):
    """As listas reservadas, com percentual e fundamento — uma tabela por grupo idêntico."""

    def linhas_do_perfil(perfil):
        geral = perfil.get("generalCompetitionModalityId")
        linhas = []
        reservadas = [
            modalidade
            for modalidade in perfil.get("competitionModalities") or []
            if modalidade.get("id") != geral and str(modalidade.get("code") or "").upper() != "AC"
        ]
        ordem = composicao_pdf._ordem_das_listas([perfil])
        reservadas.sort(
            key=lambda modalidade: (
                ordem.index(composicao_pdf._rotulo_da_lista(modalidade))
                if composicao_pdf._rotulo_da_lista(modalidade) in ordem
                else len(ordem)
            )
        )
        for modalidade in reservadas:
            regra = modalidade.get("normativeRule") or {}
            percentual = regra.get("percentage")
            linhas.append(
                (
                    f"{modalidade.get('code', '')} — {modalidade.get('name', '')}",
                    f"{humano.decimal(percentual)}%" if percentual else "—",
                    regra.get("foundation") or "—",
                )
            )
        return tuple(linhas)

    grupos = [(linhas, grupo) for linhas, grupo in _agrupar(perfis, linhas_do_perfil) if linhas]
    for linhas, grupo in grupos:
        if len(grupo) == len(perfis):
            legenda = tabelas.legenda("Reserva de vagas")
        else:
            codigos = faixa_de_codigos(perfil.get("code", "") for perfil in grupo)
            rotulo = "Perfil" if len(grupo) == 1 else "Perfis"
            legenda = tabelas.legenda(f"Reserva de vagas — {rotulo} {codigos}")
        with composicao.bloco():
            composicao_pdf._tabela(
                composicao,
                ["Lista", "Percentual", "Fundamento"],
                [list(linha) for linha in linhas],
                recuo=0.0,
                alinhamentos=[
                    composicao_pdf.ESQUERDA,
                    composicao_pdf.CENTRO,
                    composicao_pdf.ESQUERDA,
                ],
                legenda=legenda,
            )


def _reversao(composicao, perfis, com_vaga):
    """V1 a V3: a reversão dos Perfis com vaga imediata, com o alcance dito quando não é o todo."""
    com_quadro = [perfil for perfil in com_vaga if composicao_pdf._com_vaga_no_quadro(perfil)]
    especies = {(perfil.get("vacancyReversion") or {}).get("kind") for perfil in com_quadro}
    if len(especies) == 1 and (especie := especies.pop()):
        frase = composicao_pdf.frase_da_reversao(especie)
        if frase and len(com_quadro) != len(perfis):
            codigos = faixa_de_codigos(perfil.get("code", "") for perfil in com_quadro)
            frase = frase.replace(
                "de um código", f"de um código com vagas imediatas ({codigos})", 1
            )
        if frase:
            _paragrafo(composicao, frase, antes=composicao_pdf.ANTES_DE_BLOCO)
        return
    composicao_pdf._frases_consolidadas(
        composicao, composicao_pdf._frases_da_reversao(perfis, REDACAO_2)
    )


def _atribuicoes(composicao, snapshot, plano_, tabelas):
    """N.1 Atribuições: uma vez por texto idêntico, com o grupo dito (064)."""
    perfis = [p for p in _perfis(snapshot) if composicao_pdf._paragrafos(p.get("duties"))]
    total = len(_perfis(snapshot))

    def chave(perfil):
        texto = composicao_pdf.grafia.normalizar(perfil.get("duties") or "")
        return tuple(" ".join(p.split()) for p in composicao_pdf._paragrafos(texto))

    grupos = _agrupar(perfis, chave)
    for _, grupo in grupos:
        with composicao.bloco():
            if len(grupos) > 1 or len(grupo) != total:
                _rotulo_de_grupo(composicao, f"{rotulo_do_grupo(grupo, total)}:")
            for indice, paragrafo in enumerate(composicao_pdf._paragrafos(grupo[0].get("duties"))):
                _paragrafo(
                    composicao,
                    paragrafo,
                    antes=composicao_pdf.ANTES_DE_LINHA
                    if indice
                    else composicao_pdf.ANTES_DE_PARAGRAFO,
                )


# --- Como se inscrever? -------------------------------------------------------------------------


def _periodo(composicao, snapshot, plano_, tabelas):
    _paragrafo(
        composicao,
        composicao_pdf.frase_do_periodo_de_inscricoes(_evento_de_inscricao(snapshot)),
        antes=composicao_pdf.ANTES_DE_PARAGRAFO,
    )


def _dados_declarados(composicao, snapshot, plano_, tabelas):
    """V10: os dados que a inscrição pede, uma vez por lista idêntica, e para que servem."""
    perfis = [perfil for perfil in _perfis(snapshot) if perfil.get("declaredFacts")]
    total = len(_perfis(snapshot))

    usados = _fatos_usados_no_desempate(snapshot)

    def usa_no_desempate(perfil):
        return bool({str(fato.get("id")) for fato in perfil["declaredFacts"]} & usados)

    # A identidade é a do que se imprime (R-009): os itens como saem e a frase do uso no desempate.
    # Pelo rótulo e tipo só, o Perfil cujo marco não usa os dados herdava a frase de quem usa, e
    # itens de rótulo vazio e códigos diferentes saíam com o código do primeiro.
    def chave(perfil):
        itens = composicao_pdf.itens_dos_dados_declarados(perfil["declaredFacts"])
        return (tuple(itens), usa_no_desempate(perfil))

    grupos = _agrupar(perfis, chave)
    for _, grupo in grupos:
        with composicao.bloco():
            anuncio = composicao_pdf.ANUNCIO_DOS_DADOS_DECLARADOS
            if len(grupos) > 1 or len(grupo) != total:
                anuncio = f"{rotulo_do_grupo(grupo, total)}, informe também na inscrição:"
            _paragrafo(composicao, anuncio, antes=composicao_pdf.ANTES_DE_PARAGRAFO)
            for item in composicao_pdf.itens_dos_dados_declarados(grupo[0]["declaredFacts"]):
                composicao_pdf._item(composicao, "•", item, recuo=0.0)
            if usa_no_desempate(grupo[0]):
                numero = plano_.numero_do_lugar(secoes.REGRAS_DOS_MARCOS)
                _paragrafo(
                    composicao,
                    composicao_pdf.frase_do_uso_no_desempate(numero),
                    antes=composicao_pdf.ANTES_DE_LINHA,
                )


def _fatos_usados_no_desempate(snapshot):
    usados = set()
    for _, marco in _marcos(snapshot):
        for criterio in marco.get("tiebreakers") or []:
            fato = (criterio.get("parameters") or {}).get("factId")
            if fato:
                usados.add(str(fato))
    return usados


def _teto(composicao, snapshot, plano_, tabelas):
    _paragrafo(
        composicao,
        composicao_pdf.teto_de_inscricoes(snapshot),
        antes=composicao_pdf.ANTES_DE_PARAGRAFO,
    )


def _lembrete(composicao, snapshot, plano_, tabelas, *, na_inscricao):
    numero = plano_.numero_da("Como será a matrícula?")
    if not numero:
        return
    _paragrafo(
        composicao,
        composicao_pdf.lembrete_do_requerimento(numero, na_inscricao=na_inscricao),
        antes=composicao_pdf.ANTES_DE_PARAGRAFO,
    )


# --- Como será a seleção? -----------------------------------------------------------------------


def _unidades_do_perfil(snapshot, perfil, sem_cadastro, rotular):
    """As unidades de regra que o Perfil imprime, comparáveis por identidade (R-009).

    As frases da ordem são uma unidade; o corte com o empate, os suplentes e a continuação é outra;
    os critérios de desempate do marco são a terceira. Com mais de um marco no Perfil — ou marcos
    de nomes diferentes entre Perfis —, cada unidade leva o marco, e duas regras iguais de marcos
    diferentes não se confundem.
    """
    etapas = por_identificador(snapshot.get("stages"))
    fatos = por_identificador(perfil.get("declaredFacts"))
    unidades = []
    for marco in perfil.get("classificationMilestones") or []:
        marco_ = f"{marco.get('code', '')} — {marco.get('name', '')}" if rotular else ""
        # As frases da ordem são uma unidade só: a conta, a normalização ("Depois, o resultado é
        # dividido…") e o arredondamento têm sequência, e partilhadas frase a frase saíam com a
        # divisão depois do arredondamento, sob outro rótulo de grupo.
        if ordem := composicao_pdf.frases_da_ordem(snapshot, perfil, marco):
            unidades.append((marco_, "ordem", tuple(ordem)))
        if corte := composicao_pdf.frases_do_corte(marco, etapas, sem_cadastro=sem_cadastro):
            unidades.append((marco_, "corte", tuple(corte)))
        if desempate := composicao_pdf.frases_do_desempate(marco, etapas, fatos):
            unidades.append((marco_, "desempate", tuple(desempate)))
    return unidades


def _rotular_marcos(snapshot):
    """Os marcos precisam ser nomeados? Quando algum Perfil tem mais de um, ou nomes diferem."""
    perfis = _perfis(snapshot)
    if any(len(perfil.get("classificationMilestones") or []) > 1 for perfil in perfis):
        return True
    nomes = {
        (marco.get("code"), marco.get("name"))
        for perfil in perfis
        for marco in perfil.get("classificationMilestones") or []
    }
    return len(nomes) > 1


def _escrever_unidades(composicao, unidades):
    marco_atual = None
    for marco_, natureza, frases in unidades:
        if marco_ and marco_ != marco_atual:
            _rotulo_de_grupo(composicao, marco_, antes=composicao_pdf.ANTES_DE_PARAGRAFO)
        marco_atual = marco_
        if natureza == "desempate":
            with composicao.bloco():
                _rotulo_de_grupo(
                    composicao,
                    composicao_pdf.CABECALHO_DO_DESEMPATE,
                    antes=composicao_pdf.ANTES_DE_LINHA,
                )
                for frase in frases:
                    ordinal, texto = frase.split(" ", 1)
                    composicao_pdf._item(composicao, ordinal, texto, recuo=14.0)
            continue
        # A unidade do corte não se separa (R-009): um bloco, e a paginação a leva inteira.
        with composicao.bloco():
            for frase in frases:
                composicao_pdf._item(composicao, "•", frase, recuo=0.0)


def _regras_dos_marcos(composicao, snapshot, plano_, tabelas):
    """N.1 — as regras de classificação, com a partilha parcial (FR-1375, R-009, §4 do contrato).

    O comum a todos os grupos sai uma vez, sob "Para todos os Perfis:"; depois, cada grupo traz só o
    que é dele. Uma unidade que difere sai inteira no grupo.
    """
    perfis = [perfil for perfil in _perfis(snapshot) if perfil.get("classificationMilestones")]
    total = len(_perfis(snapshot))
    sem_cadastro = composicao_pdf.sem_cadastro_de_reserva(snapshot)
    rotular = _rotular_marcos(snapshot)
    unidades = {
        id(perfil): _unidades_do_perfil(snapshot, perfil, sem_cadastro, rotular)
        for perfil in perfis
    }
    grupos = _agrupar(perfis, lambda perfil: tuple(unidades[id(perfil)]))
    if total > 1:
        _paragrafo(
            composicao,
            composicao_pdf.CLASSIFICACAO_SEPARADA,
            antes=composicao_pdf.ANTES_DE_PARAGRAFO,
        )
    if len(grupos) == 1:
        ((lista, grupo),) = grupos
        if len(grupo) != total:
            _rotulo_de_grupo(composicao, f"{rotulo_do_grupo(grupo, total)}:")
        _escrever_unidades(composicao, list(lista))
        return
    comuns = [
        unidade for unidade in grupos[0][0] if all(unidade in lista for lista, _ in grupos[1:])
    ]
    if comuns:
        # Os Perfis com marco, e não "todos": o Perfil sem marco não tem estas regras.
        _rotulo_de_grupo(composicao, f"{rotulo_do_grupo(perfis, total)}:")
        _escrever_unidades(composicao, comuns)
    for lista, grupo in grupos:
        proprias = [unidade for unidade in lista if unidade not in comuns]
        if not proprias:
            continue
        with composicao.bloco(coeso=False):
            _rotulo_de_grupo(composicao, f"{rotulo_do_grupo(grupo, total)}:")
            _escrever_unidades(composicao, proprias)


def _dados_do_sorteio(composicao, snapshot, plano_, tabelas):
    """N.2 — os dados para conferir o sorteio, uma vez por método (FR-1376, FR-465)."""
    por_metodo = {}
    for perfil, marco in _metodos_de_sorteio(snapshot):
        abertura, pares = composicao_pdf.dados_do_sorteio(snapshot, perfil, marco)
        chave = (abertura, tuple(tuple(par) for par in pares))
        por_metodo.setdefault(chave, []).append(perfil)
    total = len(_perfis(snapshot))
    for (abertura, pares), grupo in por_metodo.items():
        unicos = list({id(perfil): perfil for perfil in grupo}.values())
        # Rotulado também quando o método é um só mas nem todo Perfil sorteia: sem o rótulo, os
        # dados se leriam como de todos.
        rotulado = len(por_metodo) > 1 or len(unicos) != total
        with composicao.bloco(moldura=composicao_pdf.DESTAQUE):
            if rotulado:
                _rotulo_de_grupo(
                    composicao,
                    f"{rotulo_do_grupo(unicos, total)}:",
                    antes=composicao_pdf.ANTES_DE_BLOCO,
                )
            composicao.escrever(
                abertura,
                recuo=composicao_pdf.RECUO_NO_DESTAQUE,
                antes=composicao_pdf.ANTES_DE_LINHA if rotulado else composicao_pdf.ANTES_DE_BLOCO,
                justificar=True,
            )
            composicao_pdf._pares(
                composicao, [list(par) for par in pares], recuo=composicao_pdf.RECUO_NO_DESTAQUE
            )
            composicao.espaco(4.0)


# --- Como recorrer? -----------------------------------------------------------------------------


def _recurso_dos_marcos(composicao, snapshot, plano_, tabelas):
    """R1 a R6 — o recurso de cada marco, por grupo de Perfis de mesma frase (FR-1363, FR-1369)."""
    perfis = _perfis(snapshot)

    def frases(perfil):
        return tuple(
            frase
            for marco in perfil.get("classificationMilestones") or []
            if (frase := composicao_pdf.frase_do_recurso(marco))
        )

    grupos = [(lista, grupo) for lista, grupo in _agrupar(perfis, frases) if lista]
    for lista, grupo in grupos:
        for frase in lista:
            if len(grupos) == 1 and len(grupo) == len(perfis):
                _paragrafo(composicao, frase, antes=composicao_pdf.ANTES_DE_PARAGRAFO)
                continue
            # Só os códigos (R6 do contrato de redação): "Para o Perfil P1 — Perfil A — contra…"
            # empilhava dois travessões na mesma frase.
            rotulo = rotulo_por_codigos(grupo, len(perfis))
            _paragrafo(
                composicao,
                f"{rotulo} — {inicial_minuscula(frase)}",
                antes=composicao_pdf.ANTES_DE_PARAGRAFO,
            )


# --- Como será a convocação? ---------------------------------------------------------------------


def _forma_de_convocacao(composicao, snapshot, plano_, tabelas):
    composicao_pdf._frases_consolidadas(
        composicao, composicao_pdf._frases_da_convocacao(_perfis(snapshot), REDACAO_2)
    )


# --- Como será a matrícula? ---------------------------------------------------------------------


def _requerimento(composicao, snapshot, plano_, tabelas):
    """V11 ou V12, e a declaração em bloco destacado, preso à frase que a anuncia (FR-1391)."""
    composicao_pdf._texto_da_secao(
        composicao,
        {"key": composicao_pdf.SECAO_DA_MATRICULA, "content": ""},
        snapshot,
        antes=composicao_pdf.ANTES_DE_PARAGRAFO,
    )


COMPOSICAO_DO_LUGAR = {
    secoes.REQUISITOS_DOS_PERFIS: _requisitos_dos_perfis,
    secoes.VAGAS: _vagas,
    secoes.ATRIBUICOES: _atribuicoes,
    secoes.PERIODO: _periodo,
    secoes.DADOS_DECLARADOS: _dados_declarados,
    secoes.TETO: _teto,
    secoes.REGRAS_DOS_MARCOS: _regras_dos_marcos,
    secoes.DADOS_DO_SORTEIO: _dados_do_sorteio,
    secoes.RECURSO_DOS_MARCOS: _recurso_dos_marcos,
    secoes.FORMA_DE_CONVOCACAO: _forma_de_convocacao,
    secoes.REQUERIMENTO: _requerimento,
}
