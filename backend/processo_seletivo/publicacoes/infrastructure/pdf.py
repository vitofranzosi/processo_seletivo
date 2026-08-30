"""Renderizador do documento publicado (FR-023).

O PDF é derivado exclusivamente do snapshot homologado: Perfis, vagas, Cadastro Reserva,
modalidades, Regra Normativa e Cronograma são impressos como estão na versão, sem consultar
o banco. A cadeia "dados estruturados → versão homologada → PDF publicado" fica demonstrável
porque o mesmo snapshot sempre produz os mesmos bytes, e o hash do conteúdo aparece no
documento.

Sem dependência externa. O texto usa `WinAnsiEncoding`, que cobre o português — a versão
anterior codificava em ASCII e destruía todo acento de um documento oficial brasileiro.
"""

import re
from datetime import datetime

from django.utils import timezone

from processo_seletivo.editais.domain.secoes import GERADA

LARGURA, ALTURA = 595, 842  # A4 em pontos
MARGEM = 56
TOPO = ALTURA - 64
RODAPE = 56
# Helvetica tem largura média próxima de 0,5em; 0,52 evita estourar a margem.
FATOR_LARGURA = 0.52

REGULAR, NEGRITO = "F1", "F2"

# O modo do renderizador (FR-015). Um parâmetro, e não condicionais espalhadas pela composição:
# a diferença entre o que se revisa e o que se publica precisa ter **um** lugar onde está
# declarada, ou os dois documentos divergem sem que nada acuse.
MODO_PUBLICADO = "PUBLISHED"
MODO_PREVIA = "PREVIEW"
MODOS = (MODO_PUBLICADO, MODO_PREVIA)

MARCA_DE_PREVIA = "PRÉVIA — documento em elaboração, sem valor de publicação"
RESERVA = {
    "NONE": "não há",
    "LIMITED": "limitado",
    "UNLIMITED": "ilimitado",
}


def _texto_pdf(valor: str) -> bytes:
    """WinAnsi cobre o português; o que não couber vira '?' em vez de quebrar o documento."""
    escapado = str(valor).replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
    return escapado.encode("cp1252", "replace")


def _quebrar(texto: str, tamanho: float, recuo: float) -> list[str]:
    disponivel = LARGURA - 2 * MARGEM - recuo
    limite = max(int(disponivel / (tamanho * FATOR_LARGURA)), 10)
    linhas, atual = [], ""
    for palavra in str(texto).split():
        candidato = f"{atual} {palavra}".strip()
        if len(candidato) <= limite:
            atual = candidato
        else:
            if atual:
                linhas.append(atual)
            atual = palavra
    if atual:
        linhas.append(atual)
    return linhas or [""]


def _paragrafos(texto) -> list[str]:
    """Os parágrafos que a pessoa escreveu.

    `_quebrar` reflui o texto por palavra e descarta toda a estrutura de espaço em branco — o que
    fazia dois parágrafos digitados virarem um bloco corrido no documento, em silêncio, no único
    texto livre do produto. Aqui a quebra de linha é preservada como fronteira de parágrafo antes
    de o refluxo acontecer.

    Qualquer quebra separa; linhas em branco não criam parágrafo vazio. Um Edital escrito em
    linhas curtas — que é como se escreve norma — sai como linhas curtas, e não como um bloco.
    """
    return [
        bloco.strip() for bloco in re.split(r"[\r\n]+", str(texto or "").strip()) if bloco.strip()
    ]


def _instante(valor) -> str:
    if not valor:
        return "—"
    try:
        momento = datetime.fromisoformat(str(valor))
    except ValueError:
        return str(valor)
    if timezone.is_aware(momento):
        momento = timezone.localtime(momento)
    return momento.strftime("%d/%m/%Y %H:%M")


class Composicao:
    """Acumula linhas com estilo e recuo; a paginação acontece depois, em uma passada."""

    def __init__(self):
        self.linhas: list[tuple[str, str, float, float, float]] = []

    def escrever(self, texto, *, tamanho=10, fonte=REGULAR, recuo=0.0, antes=0.0):
        for indice, parte in enumerate(_quebrar(texto, tamanho, recuo)):
            self.linhas.append((parte, fonte, tamanho, recuo, antes if indice == 0 else 0.0))

    def espaco(self, altura=8.0):
        self.linhas.append(("", REGULAR, 0.0, 0.0, altura))

    def paginar(self):
        paginas, atual, y = [], [], TOPO
        for texto, fonte, tamanho, recuo, antes in self.linhas:
            altura = tamanho * 1.45 if tamanho else 0.0
            if y - antes - altura < RODAPE + 24 and atual:
                paginas.append(atual)
                atual, y = [], TOPO
                antes = 0.0
            y -= antes + altura
            if texto:
                atual.append((texto, fonte, tamanho, MARGEM + recuo, y))
        if atual:
            paginas.append(atual)
        return paginas or [[]]


def _cabecalho(composicao, snapshot):
    composicao.escrever("INSTITUTO FEDERAL DO ESPÍRITO SANTO — CEFOR", tamanho=9, fonte=NEGRITO)
    composicao.escrever(
        f"EDITAL {snapshot.get('number', '')}/{snapshot.get('year', '')}",
        tamanho=18,
        fonte=NEGRITO,
        antes=10,
    )
    composicao.escrever(snapshot.get("title", ""), tamanho=13, antes=4)
    if snapshot.get("description"):
        composicao.escrever(snapshot["description"], tamanho=10, antes=10)


def _modalidades(composicao, perfil):
    modalidades = perfil.get("competitionModalities") or []
    if not modalidades:
        return
    composicao.escrever(
        "Modalidades de concorrência:", tamanho=10, fonte=NEGRITO, recuo=18, antes=6
    )
    for modalidade in modalidades:
        composicao.escrever(
            f"{modalidade.get('code', '')} — {modalidade.get('name', '')}",
            tamanho=10,
            recuo=32,
        )
        regra = modalidade.get("normativeRule")
        if not regra:
            continue
        partes = [f"fundamento: {regra.get('foundation', '')}"]
        if regra.get("version"):
            partes.append(f"versão: {regra['version']}")
        if regra.get("percentage"):
            partes.append(f"percentual: {regra['percentage']}%")
        if regra.get("effectiveFrom"):
            partes.append(f"vigência: {_instante(regra['effectiveFrom'])}")
        composicao.escrever("Regra Normativa — " + "; ".join(partes), tamanho=9, recuo=46)


def _perfis(composicao, snapshot):
    for perfil in snapshot.get("profiles") or []:
        composicao.escrever(
            f"{perfil.get('code', '')} — {perfil.get('name', '')}",
            tamanho=11,
            fonte=NEGRITO,
            antes=12,
        )
        if perfil.get("description"):
            composicao.escrever(perfil["description"], tamanho=10, recuo=18, antes=3)
        if perfil.get("locality"):
            composicao.escrever(f"Localidade: {perfil['locality']}", tamanho=10, recuo=18)
        composicao.escrever(
            f"Vagas imediatas: {perfil.get('immediateVacancies', 0)}", tamanho=10, recuo=18
        )
        reserva = RESERVA.get(perfil.get("reserveType"), perfil.get("reserveType", ""))
        if perfil.get("reserveLimit") is not None:
            reserva = f"{reserva} em {perfil['reserveLimit']}"
        composicao.escrever(f"Cadastro Reserva: {reserva}", tamanho=10, recuo=18)
        requisitos = perfil.get("requirements") or []
        if requisitos:
            composicao.escrever("Requisitos:", tamanho=10, fonte=NEGRITO, recuo=18, antes=6)
            for requisito in requisitos:
                composicao.escrever(f"• {requisito}", tamanho=10, recuo=32)
        _modalidades(composicao, perfil)


def _cronograma(composicao, snapshot):
    for evento in snapshot.get("schedule") or []:
        composicao.escrever(
            f"{evento.get('order', '')}. {evento.get('type', '')} — "
            f"{evento.get('description', '')}",
            tamanho=10,
            fonte=NEGRITO,
            antes=8,
        )
        periodo = f"Início: {_instante(evento.get('startAt'))}"
        if evento.get("endAt"):
            periodo += f"    Término: {_instante(evento['endAt'])}"
        composicao.escrever(periodo, tamanho=10, recuo=18)
        if evento.get("status"):
            composicao.escrever(f"Situação: {evento['status']}", tamanho=9, recuo=18)


CARATER_DA_ETAPA = (("eliminatory", "eliminatória"), ("classificatory", "classificatória"))


def _etapas(composicao, snapshot):
    """As Etapas na ordem definida, com o que estiver informado.

    Peso, nota mínima e caráter só aparecem quando existem: imprimir "peso: —" afirmaria uma
    ponderação vazia onde a ausência quer dizer que a Etapa não pondera.
    """
    eventos = {
        evento.get("id"): evento
        for evento in (snapshot.get("schedule") or [])
        if isinstance(evento, dict)
    }
    for etapa in snapshot.get("stages") or []:
        composicao.escrever(
            f"{etapa.get('order', '')}. {etapa.get('name', '')}",
            tamanho=11,
            fonte=NEGRITO,
            antes=10,
        )
        caracteres = [
            rotulo for chave, rotulo in CARATER_DA_ETAPA if etapa.get(chave)
        ]
        partes = []
        if caracteres:
            partes.append("caráter: " + " e ".join(caracteres))
        if etapa.get("weight") is not None:
            partes.append(f"peso: {etapa['weight']}")
        if etapa.get("minimumScore") is not None:
            partes.append(f"nota mínima: {etapa['minimumScore']}")
        if partes:
            composicao.escrever("; ".join(partes), tamanho=10, recuo=18)
        # As datas são do Evento e não são copiadas: o documento as lê de lá, como o domínio.
        evento = eventos.get(etapa.get("scheduleEventId"))
        if evento:
            periodo = f"Início: {_instante(evento.get('startAt'))}"
            if evento.get("endAt"):
                periodo += f"    Término: {_instante(evento['endAt'])}"
            composicao.escrever(
                f"Conforme o Cronograma — {evento.get('type', '')}: {periodo}",
                tamanho=9,
                recuo=18,
            )


# Cada seção gerada nomeia a coleção que a origina; aqui está o que fazer com cada uma. Uma origem
# que não estiver neste mapa não é composta — e a validação de publicação já recusa origem que
# divirja do catálogo, então isso não é silêncio: é a consequência de uma recusa que veio antes.
_CORPO_GERADO = {"profiles": _perfis, "schedule": _cronograma, "stages": _etapas}


def _secoes(composicao, snapshot):
    """O documento é composto **a partir das seções**, na ordem do conteúdo publicado (FR-038).

    Antes desta feature a ordem era a do código: cabeçalho, Perfis, Cronograma, integridade. Agora
    ela é conteúdo normativo, e o documento a respeita.

    Uma seção gerada cuja fonte está vazia não é composta. Um título sobre nada não informa que não
    há nada — informa que alguém esqueceu de preencher, e num Edital sem Etapas de Avaliação isso
    seria falso: a coleção é opcional.
    """
    for secao in sorted(snapshot.get("sections") or [], key=lambda item: item.get("order", 0)):
        titulo = secao.get("title", "")
        if secao.get("type") == GERADA:
            corpo = _CORPO_GERADO.get(secao.get("source"))
            if corpo is None or not (snapshot.get(secao.get("source")) or []):
                continue
            composicao.escrever(titulo.upper(), tamanho=12, fonte=NEGRITO, antes=18)
            corpo(composicao, snapshot)
        else:
            composicao.escrever(titulo.upper(), tamanho=12, fonte=NEGRITO, antes=18)
            for indice, paragrafo in enumerate(_paragrafos(secao.get("content", ""))):
                composicao.escrever(paragrafo, tamanho=10, antes=6 if indice == 0 else 7)


def _integridade(composicao, snapshot, content_hash):
    composicao.escrever("INTEGRIDADE", tamanho=12, fonte=NEGRITO, antes=18)
    composicao.escrever(
        "Este documento deriva integralmente da versão homologada identificada abaixo.",
        tamanho=10,
        antes=6,
    )
    composicao.escrever(f"Identificador do Edital: {snapshot.get('editalId', '')}", tamanho=9)
    composicao.escrever(f"Processo Seletivo: {snapshot.get('processoId', '')}", tamanho=9)
    composicao.escrever(f"Versão do schema: {snapshot.get('schemaVersion', '')}", tamanho=9)
    composicao.escrever(f"SHA-256 do conteúdo: {content_hash}", tamanho=9)


def _fluxo_da_pagina(linhas, rodape):
    partes = []
    for texto, fonte, tamanho, x, y in linhas:
        partes.append(
            b"BT /"
            + fonte.encode()
            + f" {tamanho:.1f} Tf {x:.1f} {y:.1f} Td (".encode()
            + _texto_pdf(texto)
            + b") Tj ET"
        )
    partes.append(
        b"BT /" + REGULAR.encode() + f" 8.0 Tf {MARGEM:.1f} {RODAPE - 16:.1f} Td (".encode()
        + _texto_pdf(rodape)
        + b") Tj ET"
    )
    return b"\n".join(partes)


def render_edital_pdf(snapshot: dict, content_hash: str, modo: str = MODO_PUBLICADO) -> bytes:
    """O mesmo documento, em dois modos.

    Em `MODO_PUBLICADO` o resultado é o de sempre, byte a byte — uma fixture o guarda. Em
    `MODO_PREVIA` a seção de integridade não é composta e `content_hash` **não é lido em lugar
    nenhum**: um documento administrativo que parece publicado sem ter sido é risco normativo, e
    depender de o chamador passar vazio seria deixar a garantia com quem não a tem (FR-014).
    """
    if modo not in MODOS:
        raise ValueError(f"Modo de renderização desconhecido: {modo!r}.")
    previa = modo == MODO_PREVIA

    composicao = Composicao()
    _cabecalho(composicao, snapshot)
    if previa:
        composicao.escrever(MARCA_DE_PREVIA, tamanho=11, fonte=NEGRITO, antes=12)
    _secoes(composicao, snapshot)
    if not previa:
        _integridade(composicao, snapshot, content_hash)
    paginas = composicao.paginar()

    edital = f"Edital {snapshot.get('number', '')}/{snapshot.get('year', '')}"
    identificacao = (
        f"{MARCA_DE_PREVIA} · {edital}" if previa else f"{edital} · SHA-256 {content_hash[:16]}…"
    )
    fluxos = [
        _fluxo_da_pagina(linhas, f"{identificacao} · Página {numero} de {len(paginas)}")
        for numero, linhas in enumerate(paginas, 1)
    ]

    # Objetos: 1 catálogo, 2 páginas, 3 e 4 fontes, depois pares página/conteúdo.
    primeiro_pagina = 5
    ids_paginas = [primeiro_pagina + indice * 2 for indice in range(len(fluxos))]
    objetos = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        (
            b"<< /Type /Pages /Kids ["
            + b" ".join(f"{identificador} 0 R".encode() for identificador in ids_paginas)
            + f"] /Count {len(fluxos)} >>".encode()
        ),
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica /Encoding /WinAnsiEncoding >>",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold /Encoding /WinAnsiEncoding >>",
    ]
    for indice, fluxo in enumerate(fluxos):
        objetos.append(
            f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 {LARGURA} {ALTURA}] ".encode()
            + b"/Resources << /Font << /F1 3 0 R /F2 4 0 R >> >> "
            + f"/Contents {ids_paginas[indice] + 1} 0 R >>".encode()
        )
        objetos.append(
            b"<< /Length " + str(len(fluxo)).encode() + b" >>\nstream\n" + fluxo + b"\nendstream"
        )

    saida = bytearray(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
    deslocamentos = []
    for indice, objeto in enumerate(objetos, 1):
        deslocamentos.append(len(saida))
        saida.extend(f"{indice} 0 obj\n".encode() + objeto + b"\nendobj\n")
    xref = len(saida)
    saida.extend(f"xref\n0 {len(objetos) + 1}\n0000000000 65535 f \n".encode())
    for deslocamento in deslocamentos:
        saida.extend(f"{deslocamento:010d} 00000 n \n".encode())
    saida.extend(
        f"trailer << /Size {len(objetos) + 1} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF\n".encode()
    )
    return bytes(saida)
