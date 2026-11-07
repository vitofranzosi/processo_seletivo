"""O recorte, a página e as frases da lista de Processos Seletivos (129).

**Por que este módulo existe.** A página inicial da gestão listava a unidade inteira, sem recorte,
busca nem paginação: com 211 Processos, eram 59 telas. Recortar é seguro **pelo Processo**, e só
enquanto a faixa de ações continuar lendo a unidade inteira (D-001, D-006) — a view cuida da faixa;
aqui mora o que se decide sobre o endereço e o que a página diz dele.

Funções puras sobre os parâmetros e as contagens, testáveis sem requisição, como `visao_geral.py`.
Nada aqui guarda o recorte em sessão (D-005): o endereço basta para o voltar do navegador, e uma
memória mudaria em silêncio o que abre quem clica em "Processos Seletivos" esperando o começo.
"""

from dataclasses import dataclass
from urllib.parse import urlencode

from processo_seletivo.processos.application.selectors import (
    ANDAMENTO,
    CANCELADOS,
    ENCERRADOS,
)

#: 20 por página (D-005): com a linha compacta, 3,1 telas no computador; 30 seriam 4,0, com o
#: "Próxima" longe demais da faixa.
POR_PAGINA = 20

#: Até onde se lê o termo — o mesmo corte da Visão Geral.
BUSCA_MAXIMA = 100

#: As abas, na ordem da tela (D-002): o valor no endereço, o rótulo e o grupo do seletor. "Todos"
#: não tem grupo: é a unidade inteira.
ABAS = (
    ("andamento", "Em andamento", ANDAMENTO),
    ("encerrados", "Encerrados", ENCERRADOS),
    ("cancelados", "Cancelados", CANCELADOS),
    ("todos", "Todos", None),
)
GRUPO_DA_ABA = {valor: grupo for valor, _, grupo in ABAS}
PADRAO = "andamento"


@dataclass(frozen=True)
class Recorte:
    situacao: str
    busca: str
    pagina_pedida: int

    @property
    def grupo(self):
        return GRUPO_DA_ABA[self.situacao]


def _pagina_pedida(valor):
    """Inteiro positivo, ou 1: texto, zero e negativo levam à primeira (FR-4315).

    `Paginator.get_page` levaria zero e negativo à **última** — trata-os como página vazia —, e é
    uma das razões de esta página não usá-lo (R-4).
    """
    try:
        numero = int(str(valor or "").strip())
    except ValueError:
        return 1
    return numero if numero >= 1 else 1


def recorte_de(parametros):
    """O recorte que o endereço pede, com o padrão para o que falta ou não vale (FR-4315).

    Busca só com espaços é ausência de busca, e a aba volta a valer (Edge Cases).
    """
    situacao = parametros.get("situacao") or PADRAO
    return Recorte(
        situacao=situacao if situacao in GRUPO_DA_ABA else PADRAO,
        # Sem o NUL: o PostgreSQL recusa o byte em texto, e `?busca=%00` respondia 500.
        busca=(parametros.get("busca") or "").replace("\x00", "").strip()[:BUSCA_MAXIMA],
        pagina_pedida=_pagina_pedida(parametros.get("pagina")),
    )


def _consulta(recorte, pagina=None):
    """A querystring do recorte. A busca descarta a aba; a aba padrão não se escreve (FR-4316)."""
    pares = []
    if recorte.busca:
        pares.append(("busca", recorte.busca))
    elif recorte.situacao != PADRAO:
        pares.append(("situacao", recorte.situacao))
    if pagina and pagina > 1:
        pares.append(("pagina", pagina))
    return "?" + urlencode(pares) if pares else ""


@dataclass(frozen=True)
class Pagina:
    numero: int
    total_de_paginas: int
    total: int
    recorte: Recorte

    @property
    def inicio(self):
        return (self.numero - 1) * POR_PAGINA

    @property
    def fim(self):
        return min(self.inicio + POR_PAGINA, self.total)

    @property
    def mostrando(self):
        """O intervalo da frase, contado a partir de 1: "1–20"."""
        return f"{self.inicio + 1}–{self.fim}"

    @property
    def varias(self):
        return self.total_de_paginas > 1

    @property
    def tem_anterior(self):
        return self.numero > 1

    @property
    def tem_seguinte(self):
        return self.numero < self.total_de_paginas

    @property
    def anterior(self):
        """A querystring da anterior — vazia para a primeira do padrão. O template a escreve depois
        do endereço da lista: `href=""` sozinho repetiria a querystring da página atual."""
        return _consulta(self.recorte, self.numero - 1)

    @property
    def seguinte(self):
        return _consulta(self.recorte, self.numero + 1)


def paginar(recorte, total):
    """A página que se mostra: a pedida, ou a última quando a pedida passa dela (FR-4315)."""
    total_de_paginas = max(1, -(-total // POR_PAGINA))
    return Pagina(min(recorte.pagina_pedida, total_de_paginas), total_de_paginas, total, recorte)


@dataclass(frozen=True)
class Aba:
    valor: str
    rotulo: str
    quantidade: int
    atual: bool
    endereco: str


def abas(recorte, contagem):
    """As quatro abas, cada uma com a contagem de Processos (FR-4303). Com busca, nenhuma é a
    atual (FR-4309), e todas levam à página 1 sem a busca (FR-4314)."""
    return [
        Aba(
            valor,
            rotulo,
            contagem.todos if grupo is None else contagem.por_grupo[grupo],
            not recorte.busca and recorte.situacao == valor,
            _consulta(Recorte(valor, "", 1)),
        )
        for valor, rotulo, grupo in ABAS
    ]


def _processos(quantos):
    return f"{quantos} Processo{'s' if quantos != 1 else ''}"


def frase_do_recorte(pagina):
    """ "61 Processos, mostrando 1–20" (FR-4312), ou a aba vazia."""
    if not pagina.total:
        return "Nenhum Processo nesta situação."
    return f"{_processos(pagina.total)}, mostrando {pagina.mostrando}."


def frase_da_busca(pagina, contagem):
    """O que a busca encontrou, e onde procurou (FR-4309, FR-4310).

    A busca ignora a aba, e a pessoa que veio de "Em andamento" precisa saber disso antes de ler o
    selo "Cancelado" ao lado do nome — por isso a frase vem antes dos resultados.
    """
    termo = pagina.recorte.busca
    if not pagina.total:
        return f"Nenhum Processo encontrado para “{termo}” em nenhuma situação."
    encontrado = "encontrado" if pagina.total == 1 else "encontrados"
    frase = (
        f"{_processos(pagina.total)} {encontrado} para “{termo}”, em todas as situações, "
        f"mostrando {pagina.mostrando}."
    )
    finais = contagem.encontrados_finais
    if finais:
        verbo = "está encerrado ou cancelado" if finais == 1 else "estão encerrados ou cancelados"
        frase += f" {finais} {verbo}: a situação de cada um está ao lado do nome."
    return frase
