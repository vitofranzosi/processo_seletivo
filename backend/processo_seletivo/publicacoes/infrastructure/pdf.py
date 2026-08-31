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
from contextlib import contextmanager
from datetime import datetime

from django.utils import timezone

from processo_seletivo.editais.domain.secoes import GERADA
from processo_seletivo.publicacoes.infrastructure import humano

LARGURA, ALTURA = 595, 842  # A4 em pontos
MARGEM = 56
TOPO = ALTURA - 64
RODAPE = 56

REGULAR, NEGRITO = "F1", "F2"

# Larguras em milésimos de em, para ASCII 32 a 126, na ordem do código (`008`, D-001).
#
# São as métricas das fontes base-14, que são fixas e não dependem de instalação — a mesma razão
# pela qual o documento pode declarar Helvetica sem embutir arquivo de fonte. Antes desta feature a
# quebra contava **caracteres** e multiplicava por um fator médio de 0,52: conservador o bastante
# para refluir parágrafo, e inservível para centralizar um cabeçalho ou alinhar uma coluna.
_ASCII_REGULAR = (
    278, 278, 355, 556, 556, 889, 667, 191, 333, 333, 389, 584, 278, 333, 278, 278,
    556, 556, 556, 556, 556, 556, 556, 556, 556, 556, 278, 278, 584, 584, 584, 556,
    1015, 667, 667, 722, 722, 667, 611, 778, 722, 278, 500, 667, 556, 833, 722, 778,
    667, 778, 722, 667, 611, 722, 667, 944, 667, 667, 611, 278, 278, 278, 469, 556,
    333, 556, 556, 500, 556, 556, 278, 556, 556, 222, 222, 500, 222, 833, 556, 556,
    556, 556, 333, 500, 278, 556, 500, 722, 500, 500, 500, 334, 260, 334, 584,
)
_ASCII_NEGRITO = (
    278, 333, 474, 556, 556, 889, 722, 238, 333, 333, 389, 584, 278, 333, 278, 278,
    556, 556, 556, 556, 556, 556, 556, 556, 556, 556, 333, 333, 584, 584, 584, 611,
    975, 722, 722, 722, 722, 667, 611, 778, 722, 278, 556, 722, 611, 833, 722, 778,
    667, 778, 722, 667, 611, 722, 667, 944, 667, 667, 611, 333, 278, 333, 584, 556,
    333, 556, 611, 556, 611, 556, 333, 611, 611, 278, 278, 556, 278, 889, 611, 611,
    611, 611, 389, 556, 333, 611, 556, 778, 556, 556, 500, 389, 280, 389, 584,
)

# Em Helvetica o glifo acentuado é composto e **tem o avanço da letra-base**. Derivar daí, em vez
# de transcrever uma segunda tabela, elimina a classe inteira de erro de transcrição — e é o que
# permite medir português sem tabela paralela.
_BASE_ACENTUADA = str.maketrans(
    "ÀÁÂÃÄÅÈÉÊËÌÍÎÏÒÓÔÕÖÙÚÛÜÝÑÇàáâãäåèéêëìíîïòóôõöùúûüýÿñç",
    "AAAAAAEEEEIIIIOOOOOUUUUYNCaaaaaaeeeeiiiiooooouuuuyync",
)

# O punhado de sinais que o documento usa e que não são letras nem ASCII.
_SINAIS = {
    "—": (1000, 1000), "–": (556, 556), "·": (278, 278), "•": (350, 350),
    "§": (556, 556), "°": (400, 400), "º": (365, 330), "ª": (370, 300),
    "“": (333, 500), "”": (333, 500), "‘": (222, 278), "’": (222, 278),
}

# Um caractere fora da tabela é medido como o glifo mais largo possível. É deliberadamente
# conservador: erra fazendo a linha quebrar cedo, nunca fazendo-a estourar a margem — que é o
# único dos dois erros que aparece no documento impresso.
_LARGURA_DESCONHECIDA = 1000


def largura(texto: str, tamanho: float, fonte: str = REGULAR) -> float:
    """A largura que `texto` ocupa, em pontos, quando desenhado naquele corpo (FR-002)."""
    tabela = _ASCII_NEGRITO if fonte == NEGRITO else _ASCII_REGULAR
    indice = 1 if fonte == NEGRITO else 0
    total = 0
    for caractere in str(texto):
        base = caractere.translate(_BASE_ACENTUADA)
        codigo = ord(base)
        if 32 <= codigo <= 126:
            total += tabela[codigo - 32]
        elif caractere in _SINAIS:
            total += _SINAIS[caractere][indice]
        else:
            total += _LARGURA_DESCONHECIDA
    return total * tamanho / 1000


# Os níveis tipográficos do documento, e apenas estes (FR-009). Nomeá-los é o que impede que a
# hierarquia volte a ser um punhado de números literais espalhados pela composição.
CORPO_INSTITUCIONAL = 9.0
CORPO_ATO = 14.0
CORPO_SECAO = 11.5
CORPO_BLOCO = 10.5
CORPO_TEXTO = 10.0
CORPO_NOTA = 8.5

ESQUERDA, CENTRO, DIREITA = "esquerda", "centro", "direita"

# Quanto o contorno de um bloco abre acima da primeira linha (FR-014).
FOLGA_DA_MOLDURA = 6.0
# E quanto ele desce quando um título veio junto na quebra: o fio precisa passar abaixo das
# descidas do título, não rente a elas.
FOLGA_APOS_TITULO = 16.0

# O modo do renderizador (FR-015). Um parâmetro, e não condicionais espalhadas pela composição:
# a diferença entre o que se revisa e o que se publica precisa ter **um** lugar onde está
# declarada, ou os dois documentos divergem sem que nada acuse.
MODO_PUBLICADO = "PUBLISHED"
MODO_PREVIA = "PREVIEW"
MODOS = (MODO_PUBLICADO, MODO_PREVIA)

MARCA_DE_PREVIA = "PRÉVIA — documento em elaboração, sem valor de publicação"
# A marca vive **fora** do fluxo normativo, numa faixa fixa acima da área útil (`008`, D-011).
# Escrita dentro do fluxo, ela empurrava todo o conteúdo e fazia a prévia quebrar em páginas
# diferentes daquelas em que o documento seria publicado — quem revisava a prévia revisava uma
# paginação que não era a que sai. Fora do fluxo, a igualdade das quebras é garantida por
# construção (FR-042), e a marca passa a aparecer em **todas** as páginas, e não só na primeira.
FAIXA_DE_PREVIA = ALTURA - 40
RESERVA = {
    "NONE": "não há",
    "LIMITED": "limitado",
    "UNLIMITED": "ilimitado",
}


def _texto_pdf(valor: str) -> bytes:
    """WinAnsi cobre o português; o que não couber vira '?' em vez de quebrar o documento."""
    escapado = str(valor).replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
    return escapado.encode("cp1252", "replace")


def _quebrar(texto: str, tamanho: float, recuo: float, fonte: str = REGULAR) -> list[str]:
    """Reflui por largura real, e não por contagem de caracteres (FR-002, FR-032)."""
    disponivel = LARGURA - 2 * MARGEM - recuo
    linhas, atual = [], ""
    for palavra in str(texto).split():
        candidato = f"{atual} {palavra}".strip()
        if largura(candidato, tamanho, fonte) <= disponivel:
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


def _x(texto, fonte, tamanho, recuo, alinhamento):
    """Onde a linha começa. Centralizar e alinhar à direita só é possível por causa de FR-002."""
    if alinhamento == ESQUERDA:
        return MARGEM + recuo
    util = LARGURA - 2 * MARGEM
    sobra = util - largura(texto, tamanho, fonte)
    return MARGEM + (sobra / 2 if alinhamento == CENTRO else sobra)


class Composicao:
    """Acumula itens com estilo, recuo e fronteira de bloco; a paginação acontece depois.

    O item deixou de ser sempre texto: `Traço` é a primitiva gráfica de FR-003, e o bloco é a
    fronteira que FR-004 pede. Nada disso é motor de layout — são três conceitos, e a decisão de
    quebra é uma cascata de cinco degraus que sempre termina em alternativa exequível.
    """

    ESPESSURA_DO_FIO = 0.6

    def __init__(self):
        self.itens: list = []

    def escrever(
        self, texto, *, tamanho=CORPO_TEXTO, fonte=REGULAR, recuo=0.0, antes=0.0,
        alinhamento=ESQUERDA, junto=False,
    ):
        """`junto` é o "não me deixe sozinho no rodapé" de FR-022 e FR-030.

        Um título que fecha a página sem nada abaixo é o defeito que mais denuncia composição
        automática. A regra é local — a linha exige espaço para si **e** para a próxima —, e não
        um algoritmo de viúvas e órfãs.
        """
        partes = _quebrar(texto, tamanho, recuo, fonte)
        for indice, parte in enumerate(partes):
            self.itens.append(
                (
                    "texto", parte, fonte, tamanho, recuo,
                    antes if indice == 0 else 0.0, alinhamento,
                    junto or indice < len(partes) - 1,
                )
            )

    def espaco(self, altura=8.0):
        self.itens.append(("texto", "", REGULAR, 0.0, 0.0, altura, ESQUERDA, False))

    @contextmanager
    def bloco(self, *, moldura=False, coeso=True):
        """Uma fronteira que a paginação enxerga (FR-004).

        `coeso` diz que o bloco prefere não começar sem caber; `moldura` pede o contorno de FR-014.
        Blocos aninham — Perfil contém sub-blocos, sub-blocos contêm unidades —, e é o aninhamento
        que dá os degraus da cascata de FR-021.
        """
        self.itens.append(("abre", moldura, coeso))
        try:
            yield
        finally:
            self.itens.append(("fecha", moldura, coeso))

    # -- medição -------------------------------------------------------------

    @staticmethod
    def _altura(item):
        if item[0] != "texto":
            return 0.0
        _, texto, _, tamanho, _, antes, _, _ = item
        return antes + (tamanho * 1.45 if tamanho else 0.0)

    @classmethod
    def _extensao(cls, itens, inicio):
        """Onde termina o bloco aberto em `inicio`, e quanto ele mede."""
        profundidade, fim = 0, inicio
        for indice in range(inicio, len(itens)):
            if itens[indice][0] == "abre":
                profundidade += 1
            elif itens[indice][0] == "fecha":
                profundidade -= 1
                if profundidade == 0:
                    fim = indice
                    break
        else:
            fim = len(itens) - 1
        return fim, sum(cls._altura(item) for item in itens[inicio : fim + 1])

    # -- paginação -----------------------------------------------------------

    def paginar(self):
        """Duas passadas: mede o bloco, decide se cabe, depois coloca (D-004).

        A cascata, na ordem, parando no primeiro degrau exequível: cabe no que resta → coloca;
        cabe numa página inteira → começa na próxima; não cabe numa página → abre o bloco e repete
        para cada sub-bloco; sub-bloco isolado não cabe → repete para suas unidades; unidade
        isolada não cabe → quebra entre linhas. **O último degrau é o que torna a regra sempre
        cumprível** — foi a ausência dele que tornou impossível a primeira redação da spec.
        """
        util = TOPO - (RODAPE + 24)
        paginas, atual, tracos, y = [], [], [], TOPO
        pilha = []
        indice = 0

        def nova_pagina():
            """Fecha a página — **levando junto** o rastro de linhas que pediram companhia.

            Marcar a linha não basta: o título é colocado e só depois o bloco seguinte descobre que
            não cabe. Quem quebra a página é quem tem de devolver o título, senão ele fica para
            trás sozinho — que é o defeito de composição automática mais visível de todos.
            """
            nonlocal atual, tracos, y
            rastro = []
            while atual and atual[-1][5]:
                rastro.insert(0, atual.pop())
            for aberto in pilha:
                if aberto["moldura"] and aberto["topo"] is not None:
                    tracos.append((aberto["topo"], rastro[0][4] if rastro else y))
            paginas.append((atual, tracos))
            atual, tracos, y = [], [], TOPO
            for texto, fonte, tamanho, x, _, junto in rastro:
                y -= tamanho * 1.45
                atual.append((texto, fonte, tamanho, x, y, junto))
            # Um bloco que já estava aberto reabre a moldura abaixo do rastro, pela mesma razão.
            for aberto in pilha:
                if aberto["moldura"] and aberto["topo"] is not None:
                    aberto["topo"] = (y - FOLGA_APOS_TITULO) if rastro else y

        while indice < len(self.itens):
            item = self.itens[indice]

            if item[0] == "abre":
                _, moldura, coeso = item
                fim, altura = self._extensao(self.itens, indice)
                cabe_aqui = y - altura >= RODAPE + 24
                if coeso and not cabe_aqui and altura <= util and atual:
                    nova_pagina()
                # Não cabendo nem numa página inteira, o bloco é aberto e a mesma decisão desce
                # para os sub-blocos — que é o degrau seguinte da cascata, não um caso especial.
                # Se a última linha da página já ocupa este `y` — é o caso do título que veio
                # junto na quebra —, o contorno precisa começar **abaixo** dela: senão o fio sobe
                # pela altura-x do título que apenas anuncia o quadro.
                ocupado = bool(atual) and atual[-1][4] >= y
                topo = (y - FOLGA_APOS_TITULO) if ocupado else y
                pilha.append({"moldura": moldura, "topo": topo if moldura else None})
                indice += 1
                continue

            if item[0] == "fecha":
                aberto = pilha.pop()
                if aberto["moldura"] and aberto["topo"] is not None:
                    tracos.append((aberto["topo"], y))
                indice += 1
                continue

            _, texto, fonte, tamanho, recuo, antes, alinhamento, junto = item
            altura = self._altura(item)
            # Uma linha "junto" precisa de espaço para si e para a seguinte: é o que impede o
            # título de fechar a página sozinho.
            necessario = altura
            if junto:
                proxima = next(
                    (
                        outro
                        for outro in self.itens[indice + 1 :]
                        if outro[0] == "texto" and outro[1]
                    ),
                    None,
                )
                if proxima is not None:
                    necessario += self._altura(proxima)
            if y - necessario < RODAPE + 24 and atual:
                nova_pagina()
                antes, altura = 0.0, altura - antes
            y -= altura
            if texto:
                x = _x(texto, fonte, tamanho, recuo, alinhamento)
                atual.append((texto, fonte, tamanho, x, y, junto))
            indice += 1

        paginas.append((atual, tracos))
        return [
            ([linha[:5] for linha in linhas], fios) for linhas, fios in paginas
        ] or [([], [])]


# A identificação do órgão é constante do documento, como já era — o que muda é a forma, não a
# origem (FR-005). O Processo e o objeto vêm do conteúdo publicado, que desde a `007` carrega o
# código e o título do Processo justamente para que o documento possa nomeá-lo.
ORGAO = ("MINISTÉRIO DA EDUCAÇÃO", "INSTITUTO FEDERAL DO ESPÍRITO SANTO")
UNIDADE = "CENTRO DE REFERÊNCIA EM FORMAÇÃO E EM EDUCAÇÃO A DISTÂNCIA"


def _cabecalho(composicao, snapshot):
    """A abertura de um ato administrativo (FR-005 a FR-007).

    Calibrado contra os Editais 62/2026 e 73/2026 do Cefor: a hierarquia vem de **peso, caixa alta
    e centralização**, não de corpo grande. Nos dois alvos o ato está em corpo próximo ao do texto,
    e destacar por tamanho produziria um título fora do padrão institucional.
    """
    for linha in ORGAO:
        composicao.escrever(
            linha, tamanho=CORPO_INSTITUCIONAL, fonte=NEGRITO, alinhamento=CENTRO
        )
    composicao.escrever(UNIDADE, tamanho=CORPO_INSTITUCIONAL, alinhamento=CENTRO)
    composicao.escrever(
        f"EDITAL Nº {snapshot.get('number', '')}/{snapshot.get('year', '')}",
        tamanho=CORPO_ATO,
        fonte=NEGRITO,
        antes=22,
        alinhamento=CENTRO,
    )
    if snapshot.get("processoTitle"):
        composicao.escrever(
            snapshot["processoTitle"].upper(),
            tamanho=CORPO_SECAO,
            fonte=NEGRITO,
            antes=4,
            alinhamento=CENTRO,
        )
    composicao.escrever(
        snapshot.get("title", ""), tamanho=CORPO_BLOCO, antes=4, alinhamento=CENTRO
    )
    if snapshot.get("description"):
        composicao.escrever(snapshot["description"], tamanho=CORPO_TEXTO, antes=16)


def _tabela(composicao, cabecalho, linhas, *, recuo=18.0, tamanho=CORPO_TEXTO):
    """Colunas medidas pelo conteúdo, com a folga na coluna mais larga (D-007).

    Proporção fixa quebraria no primeiro dado real — uma localidade longa ou um fundamento
    normativo por extenso estoura a coluna ou deixa metade da página vazia. Medir só é possível
    por causa de FR-002.
    """
    if not linhas:
        return
    colunas = len(linhas[0])
    minimas = [
        max(
            largura(cabecalho[c], tamanho, NEGRITO) if cabecalho else 0,
            *(largura(linha[c], tamanho, REGULAR) for linha in linhas),
        )
        + 12
        for c in range(colunas)
    ]
    disponivel = LARGURA - 2 * MARGEM - recuo
    sobra = disponivel - sum(minimas)
    if sobra > 0:
        minimas[minimas.index(max(minimas))] += sobra

    def escrever_linha(celulas, fonte):
        deslocamento = recuo
        for indice, celula in enumerate(celulas):
            composicao.escrever(
                celula, tamanho=tamanho, fonte=fonte, recuo=deslocamento,
                antes=3.0 if indice == 0 else -(tamanho * 1.45),
            )
            deslocamento += minimas[indice]

    if cabecalho:
        escrever_linha(cabecalho, NEGRITO)
    for linha in linhas:
        escrever_linha(linha, REGULAR)


def _modalidades(composicao, perfil):
    """As modalidades em tabela — sem perder o que a frase corrida dizia (FR-018, FR-019).

    O documento anterior imprimia `Regra Normativa — fundamento: …; versão: …; percentual: …`.
    A frase sai; versão e vigência **permanecem**, porque tabular não pode virar perder. E
    modalidade sem percentual não ganha célula construída para preencher a coluna: a ausência é
    materializada como ausência.
    """
    modalidades = perfil.get("competitionModalities") or []
    if not modalidades:
        return
    linhas = []
    for modalidade in modalidades:
        regra = modalidade.get("normativeRule") or {}
        percentual = regra.get("percentage")
        vigencia = regra.get("effectiveFrom")
        linhas.append(
            [
                f"{modalidade.get('code', '')} — {modalidade.get('name', '')}",
                f"{humano.decimal(percentual)}%" if percentual else "",
                regra.get("foundation", "") or "",
                regra.get("version", "") or (_instante(vigencia) if vigencia else ""),
            ]
        )
    # Coluna em que **nenhuma** modalidade tem valor não é impressa. Um Edital só de ampla
    # concorrência não deve exibir uma coluna de percentual inteira vazia: seria informação
    # inexistente ocupando espaço para preencher a tabela (FR-019).
    cabecalho = ["Modalidade", "Percentual", "Fundamento", "Versão"]
    presentes = [c for c in range(len(cabecalho)) if any(linha[c] for linha in linhas)]
    with composicao.bloco():
        composicao.escrever(
            "Modalidades de concorrência", tamanho=CORPO_TEXTO, fonte=NEGRITO, recuo=18, antes=8
        )
        _tabela(
            composicao,
            [cabecalho[c] for c in presentes],
            [[linha[c] or "—" for c in presentes] for linha in linhas],
        )


def _perfis(composicao, snapshot, secao=0):
    """Cada Perfil como bloco delimitado, com a identificação em disposição tabular.

    A estrutura é a da cascata de FR-021: o Perfil é um bloco coeso com moldura; dentro dele,
    identificação, descrição, atribuições, requisitos e modalidades são sub-blocos que só quebram
    entre si — e, quando um deles sozinho não cabe numa página, por dentro.

    Nenhum rótulo sobre nada: um campo ausente não é impresso. Um rótulo vazio não informa que não
    há informação, informa que alguém esqueceu de preencher.
    """
    for perfil in snapshot.get("profiles") or []:
        with composicao.bloco(moldura=True):
            with composicao.bloco():
                composicao.escrever(
                    f"{perfil.get('code', '')} — {perfil.get('name', '')}",
                    tamanho=CORPO_BLOCO,
                    fonte=NEGRITO,
                    antes=14,
                    junto=True,
                )
                identificacao = [["Localidade", perfil.get("locality", "") or "—",
                                  "Vagas imediatas", str(perfil.get("immediateVacancies", 0))]]
                reserva = RESERVA.get(perfil.get("reserveType"), perfil.get("reserveType", ""))
                if perfil.get("reserveLimit") is not None:
                    reserva = f"{reserva} em {perfil['reserveLimit']}"
                identificacao.append(["Cadastro Reserva", reserva, "", ""])
                # Sem cabeçalho de coluna: aqui o rótulo **é** a primeira célula. Um cabeçalho
                # sobre pares rótulo-valor não nomearia nada.
                _tabela(composicao, None, identificacao)

            if perfil.get("description"):
                with composicao.bloco():
                    composicao.escrever(perfil["description"], tamanho=CORPO_TEXTO, recuo=18,
                                        antes=6)
            if perfil.get("duties"):
                with composicao.bloco():
                    composicao.escrever("Atribuições", tamanho=CORPO_TEXTO, fonte=NEGRITO,
                                        recuo=18, antes=8)
                    for paragrafo in _paragrafos(perfil["duties"]):
                        composicao.escrever(paragrafo, tamanho=CORPO_TEXTO, recuo=32, antes=3)
            for rotulo, chave in (("Carga horária", "workload"), ("Remuneração", "compensation")):
                if perfil.get(chave):
                    composicao.escrever(f"{rotulo}: {perfil[chave]}", tamanho=CORPO_TEXTO,
                                        recuo=18, antes=3)
            requisitos = perfil.get("requirements") or []
            if requisitos:
                with composicao.bloco():
                    composicao.escrever("Requisitos", tamanho=CORPO_TEXTO, fonte=NEGRITO,
                                        recuo=18, antes=8)
                    for requisito in requisitos:
                        composicao.escrever(f"• {requisito}", tamanho=CORPO_TEXTO, recuo=32)
            _modalidades(composicao, perfil)


def _cronograma(composicao, snapshot, secao=0):
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
        # O estado do Evento **não é composto**, e não recebe mapa de tradução (FR-002).
        # Existe o precedente de `RESERVA` logo acima, e a tentação de imitá-lo aqui: mas os dois
        # casos são distintos. O tipo de cadastro reserva descreve a vaga e interessa a quem se
        # inscreve; `PLANEJADO`, `EM_ANDAMENTO` e `CONCLUIDO` descrevem a execução do certame e são
        # informação de gestão. Um Edital publicado não diz que suas inscrições estão "planejadas" —
        # ele as anuncia. Traduzir o rótulo produziria uma frase correta dizendo ao candidato algo
        # que não é matéria de Edital.


CARATER_DA_ETAPA = (("eliminatory", "eliminatória"), ("classificatory", "classificatória"))


def _etapas(composicao, snapshot, secao=0):
    """As Etapas na ordem definida, com o que estiver informado.

    Peso, nota mínima e caráter só aparecem quando existem: imprimir "peso: —" afirmaria uma
    ponderação vazia onde a ausência quer dizer que a Etapa não pondera.

    A subseção é numerada a partir do número da seção-mãe **já resolvido** (FR-013). Fixar `6.`
    repetiria, uma camada abaixo, o defeito que a numeração em dois passos corrige.
    """
    eventos = {
        evento.get("id"): evento
        for evento in (snapshot.get("schedule") or [])
        if isinstance(evento, dict)
    }
    for ordem, etapa in enumerate(snapshot.get("stages") or [], 1):
        composicao.escrever(
            f"{secao}.{ordem} {etapa.get('name', '')}",
            tamanho=CORPO_BLOCO,
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
            partes.append(f"peso: {humano.decimal(etapa['weight'])}")
        if etapa.get("minimumScore") is not None:
            partes.append(f"nota mínima: {humano.decimal(etapa['minimumScore'])}")
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


def _materializaveis(snapshot):
    """As seções que **serão** compostas, na ordem do conteúdo publicado (FR-038).

    Uma seção gerada cuja fonte está vazia não é composta. Um título sobre nada não informa que não
    há nada — informa que alguém esqueceu de preencher, e num Edital sem Etapas de Avaliação isso
    seria falso: a coleção é opcional.
    """
    materializaveis = []
    for secao in sorted(snapshot.get("sections") or [], key=lambda item: item.get("order", 0)):
        if secao.get("type") == GERADA:
            corpo = _CORPO_GERADO.get(secao.get("source"))
            if corpo is None or not (snapshot.get(secao.get("source")) or []):
                continue
            materializaveis.append((secao, corpo))
        else:
            materializaveis.append((secao, None))
    return materializaveis


def _secoes(composicao, snapshot):
    """O documento numerado, em dois passos: selecionar, depois enumerar (FR-010 a FR-012).

    **A ordem dos dois passos é o requisito.** Numerar durante a iteração produziria `5.`, `7.`,
    `8.` no primeiro Edital sem Etapas de Avaliação — um defeito que o cenário de demonstração não
    revela, porque nele está tudo preenchido. O número é da materialização: ele não existe no
    conteúdo homologado e não sobrevive a uma mudança de ordem (FR-012).
    """
    for numero, (secao, corpo) in enumerate(_materializaveis(snapshot), 1):
        titulo = f"{numero}. {secao.get('title', '').upper()}"
        composicao.escrever(titulo, tamanho=CORPO_SECAO, fonte=NEGRITO, antes=18, junto=True)
        if corpo is not None:
            corpo(composicao, snapshot, numero)
        else:
            for indice, paragrafo in enumerate(_paragrafos(secao.get("content", ""))):
                composicao.escrever(
                    paragrafo, tamanho=CORPO_TEXTO, antes=6 if indice == 0 else 7
                )


def _integridade(composicao, snapshot, content_hash):
    composicao.escrever("INTEGRIDADE", tamanho=12, fonte=NEGRITO, antes=18)
    composicao.escrever(
        "Este documento deriva integralmente da versão homologada identificada abaixo.",
        tamanho=10,
        antes=6,
    )
    # Identificação **institucional**, não técnica (FR-004). O SHA-256 permanece porque é o que a
    # declaração prova; o UUID sai porque não prova nada a quem lê e era a forma interna vazando
    # para a apresentação. Os identificadores continuam no snapshot — o que muda é o que se imprime.
    composicao.escrever(
        f"Edital {snapshot.get('number', '')}/{snapshot.get('year', '')}", tamanho=9
    )
    processo = " — ".join(
        parte
        for parte in (snapshot.get("processoCode", ""), snapshot.get("processoTitle", ""))
        if parte
    )
    composicao.escrever(f"Processo Seletivo {processo}", tamanho=9)
    composicao.escrever(f"Versão do schema: {snapshot.get('schemaVersion', '')}", tamanho=9)
    composicao.escrever(f"SHA-256 do conteúdo: {content_hash}", tamanho=9)


def _fluxo_da_pagina(linhas, rodape, marca="", tracos=()):
    partes = []
    # Os fios primeiro: no PDF, o que é emitido depois cobre o que veio antes. Emitir contorno
    # antes de letra garante que nenhum fio passe por cima de um glifo — sem precisar de camada,
    # z-index ou qualquer conceito de composição gráfica (D-002).
    for topo, base in tracos:
        largura_util = LARGURA - 2 * MARGEM
        altura = topo - base + FOLGA_DA_MOLDURA + 4
        partes.append(
            f"{Composicao.ESPESSURA_DO_FIO} w "
            f"{MARGEM - 6:.1f} {base - 4:.1f} {largura_util + 12:.1f} {altura:.1f} re S".encode()
        )
    if marca:
        partes.append(
            b"BT /" + NEGRITO.encode()
            + f" 9.0 Tf {MARGEM:.1f} {FAIXA_DE_PREVIA:.1f} Td (".encode()
            + _texto_pdf(marca)
            + b") Tj ET"
        )
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
    _secoes(composicao, snapshot)
    if not previa:
        _integridade(composicao, snapshot, content_hash)
    paginas = composicao.paginar()

    edital = f"Edital {snapshot.get('number', '')}/{snapshot.get('year', '')}"
    identificacao = (
        f"{MARCA_DE_PREVIA} · {edital}" if previa else f"{edital} · SHA-256 {content_hash[:16]}…"
    )
    fluxos = [
        _fluxo_da_pagina(
            linhas,
            f"{identificacao} · Página {numero} de {len(paginas)}",
            marca=MARCA_DE_PREVIA if previa else "",
            tracos=tracos,
        )
        for numero, (linhas, tracos) in enumerate(paginas, 1)
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
