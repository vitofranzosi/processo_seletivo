"""As estruturas da resposta (070, data-model §2, contracts/resposta.md §6).

Tudo congelado, e tudo em memória: nada daqui é gravado (`FR-1449`, `D-006`). A forma serializada,
`como_dict()`, é o contrato que as Fases B e C vão consumir, e por isso tem as chaves em ordem fixa
e nenhum valor que dependa da ordem em que o banco devolveu as linhas (`FR-1446`).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

# ---- naturezas, tipos, avisos e pontos ------------------------------------------------------

TEXTO, DADO, EXPLICACAO = "TEXTO", "DADO", "EXPLICACAO"
NATUREZAS = (TEXTO, DADO, EXPLICACAO)

#: O rótulo de cada natureza, em palavras (`FR-1432`, `UX-200`). É o que a tela escreve, e é o
#: que separa o que o Edital diz do que o sistema diz.
ROTULO_DA_NATUREZA = {
    TEXTO: "Texto do Edital",
    DADO: "Dado da versão vigente",
    EXPLICACAO: "Explicação",
}

RESPONDIDA = "RESPONDIDA"
NAO_INFORMA = "NAO_INFORMA"
DEPENDE_DA_LEITURA = "DEPENDE_DA_LEITURA"
FONTES_DIVERGENTES = "FONTES_DIVERGENTES"
#: Declarado na spec (`FR-1421`) e **não produzido na Fase A**: nenhuma pergunta do catálogo pede
#: um detalhe que só um anexo contenha. Na Fase A o anexo vem como aviso (contracts/resposta.md §2).
DETALHE_EM_ANEXO = "DETALHE_EM_ANEXO"

ROTULO_DO_TIPO = {
    RESPONDIDA: "Respondida pelos dados",
    NAO_INFORMA: "O Edital não informa",
    DEPENDE_DA_LEITURA: "Depende da leitura do Edital",
    FONTES_DIVERGENTES: "Fontes divergentes",
    DETALHE_EM_ANEXO: "Detalhe em anexo",
}

AVISO_RETIFICACAO_FUTURA = "RETIFICACAO_FUTURA"
AVISO_DESFECHO = "DESFECHO"
AVISO_DETALHE_EM_ANEXO = "DETALHE_EM_ANEXO"
AVISO_REDACAO_ALCANCA_MAIS = "REDACAO_ALCANCA_MAIS"

PONTO_CANAIS_DIVERGENTES = "CANAIS_DIVERGENTES"
PONTO_EXCLUSIVIDADE_DO_CANAL = "EXCLUSIVIDADE_DO_CANAL"
PONTO_ANEXO_CITADO_INEXISTENTE = "ANEXO_CITADO_INEXISTENTE"
PONTO_RETIFICACAO_FUTURA = "RETIFICACAO_FUTURA"
PONTO_DOCUMENTO_DE_ORIGEM_INCOMPLETO = "DOCUMENTO_DE_ORIGEM_INCOMPLETO"

ORIGINAL, RETIFICACAO = "ORIGINAL", "RETIFICACAO"
CANAL_DO_EDITAL, CANAL_INSTITUCIONAL = "EDITAL", "INSTITUCIONAL"


def _instante(valor: datetime | None) -> str | None:
    return valor.isoformat() if valor is not None else None


# ---- o que a aplicação entrega ao domínio ---------------------------------------------------


@dataclass(frozen=True)
class AtoPublicado:
    """Uma publicação aplicada pela versão: a original ou uma Retificação.

    `contem` são os atos que o **documento** desta publicação incorpora (`R-005`): a original
    contém só a si; uma Retificação contém os da versão-base dela, mais ela. É o que separa o
    documento do ato do conteúdo vigente — o achado de 12/10.
    """

    publicacao_id: str
    ato: str
    ordem: int
    publicado_em: datetime
    vigente_desde: datetime
    documento: str = ""
    contem: tuple[str, ...] = ()

    def como_dict(self):
        return {
            "publicacao": self.publicacao_id,
            "ato": self.ato,
            "publicadoEm": _instante(self.publicado_em),
            "vigenteDesde": _instante(self.vigente_desde),
            "documento": self.documento,
        }


@dataclass(frozen=True)
class VersaoConsultada:
    id: str
    identificador_curto: str
    vigente_desde: datetime
    publicada_em: datetime
    #: `(publicada_em, vigente_desde)` de cada Retificação aplicada, na ordem de aplicação.
    retificacoes: tuple[tuple[datetime, datetime], ...] = ()

    def como_dict(self):
        return {
            "id": self.id,
            "identificador": self.identificador_curto,
            "vigenteDesde": _instante(self.vigente_desde),
            "publicadaEm": _instante(self.publicada_em),
            "retificacoes": [
                {"publicadaEm": _instante(publicada), "vigenteDesde": _instante(vigente)}
                for publicada, vigente in self.retificacoes
            ],
        }


@dataclass(frozen=True)
class VersaoFutura:
    """Uma versão já publicada que ainda não vigora no instante consultado (`FR-1414`)."""

    vigente_desde: datetime
    conteudo: dict
    atos: tuple[AtoPublicado, ...]
    proveniencias: tuple[tuple[str, str], ...] = ()


@dataclass(frozen=True)
class Desfecho:
    """O fim do Edital ou do Processo, já filtrado pelo instante (`R-006`)."""

    alcance: str
    operacao: str
    em: datetime | None
    do_edital: bool


@dataclass(frozen=True)
class Contexto:
    """Tudo o que a resposta pode usar — e nada além disso (`FR-1412`).

    Uma versão, um instante. As futuras entram só para o aviso; o desfecho e o canal da
    implantação são as duas únicas fontes de fora do conteúdo publicado.
    """

    edital_id: str
    numero: str
    ano: int
    titulo: str
    instante: datetime
    versao: VersaoConsultada
    conteudo: dict
    atos: tuple[AtoPublicado, ...]
    proveniencias: tuple[tuple[str, str], ...] = ()
    fonte_da_versao: AtoPublicado | None = None
    futuras: tuple[VersaoFutura, ...] = ()
    desfecho: Desfecho | None = None
    canal_institucional: str = ""
    #: O endereço da página pública da seleção, para os links de conferência (`FR-1438`).
    pagina_publica: str = ""
    #: `artifactId` → endereço público do anexo.
    anexos_publicos: dict = field(default_factory=dict)
    #: A versão em que a consulta anterior se baseou, com os atos que ela aplicava (`FR-1415`).
    versao_anterior: str | None = None
    atos_da_versao_anterior: tuple[AtoPublicado, ...] = ()


# ---- o que a resposta devolve -----------------------------------------------------------------


@dataclass(frozen=True)
class Link:
    rotulo: str
    url: str

    def como_dict(self):
        return {"rotulo": self.rotulo, "url": self.url}


@dataclass(frozen=True)
class ValorFuturo:
    valor: str
    vigente_desde: datetime
    origem: AtoPublicado | None

    def como_dict(self):
        return {
            "valor": self.valor,
            "vigenteDesde": _instante(self.vigente_desde),
            "publicacao": self.origem.publicacao_id if self.origem else None,
        }


@dataclass(frozen=True)
class Referencia:
    """Um cartão: exatamente uma natureza (`FR-1432`).

    `caminho` é o endereço da `004` no conteúdo publicado, para rastreio; o leitor vê a
    `localizacao`. `posicao` é o item de uma coleção atômica (os requisitos), que a gramática da
    `004` não endereça por índice.
    """

    natureza: str
    localizacao: str
    conteudo: str
    caminho: str = ""
    posicao: int | None = None
    rotulo: str = ""
    origens: tuple[AtoPublicado, ...] = ()
    futuro: tuple[ValorFuturo, ...] = ()
    links: tuple[Link, ...] = ()

    def __post_init__(self):
        if self.natureza not in NATUREZAS:
            raise ValueError(f"natureza desconhecida: {self.natureza}")
        if self.natureza == EXPLICACAO and self.origens:
            raise ValueError("a explicação é do sistema, e não tem ato de origem")

    def como_dict(self):
        return {
            "natureza": self.natureza,
            "localizacao": self.localizacao,
            "caminho": self.caminho,
            "posicao": self.posicao,
            "rotulo": self.rotulo or None,
            "conteudo": self.conteudo,
            "origens": [origem.como_dict() for origem in self.origens],
            "futuro": [valor.como_dict() for valor in self.futuro],
            "links": [link.como_dict() for link in self.links],
        }


@dataclass(frozen=True)
class Aviso:
    tipo: str
    texto: str
    links: tuple[Link, ...] = ()

    def como_dict(self):
        return {
            "tipo": self.tipo,
            "texto": self.texto,
            "links": [link.como_dict() for link in self.links],
        }


@dataclass(frozen=True)
class MudancaDeVersao:
    """O que separa a versão da resposta anterior da desta (`FR-1415`), nos dois sentidos.

    `atos`: aplicados agora e não antes. `sem_efeito`: aplicados antes e não agora — a consulta a
    um instante anterior, ou o endereço com a versão de outra consulta.
    """

    anterior: str
    atos: tuple[AtoPublicado, ...]
    sem_efeito: tuple[AtoPublicado, ...] = ()

    def como_dict(self):
        return {
            "anterior": self.anterior,
            "atos": [
                {"publicacao": ato.publicacao_id, "vigenteDesde": _instante(ato.vigente_desde)}
                for ato in self.atos
            ],
            "semEfeito": [
                {"publicacao": ato.publicacao_id, "vigenteDesde": _instante(ato.vigente_desde)}
                for ato in self.sem_efeito
            ],
        }


@dataclass(frozen=True)
class SituacaoDeCalendario:
    instante: datetime
    periodo: str
    desfecho: Desfecho | None = None

    def como_dict(self):
        return {
            "instante": _instante(self.instante),
            "periodo": self.periodo,
            "desfecho": None
            if self.desfecho is None
            else {
                "operacao": self.desfecho.operacao,
                "alcance": self.desfecho.alcance,
                "em": _instante(self.desfecho.em),
            },
        }


@dataclass(frozen=True)
class Canal:
    origem: str
    contatos: tuple[str, ...]
    paragrafos: tuple[Referencia, ...] = ()
    exclusividade: bool = False

    @property
    def divergente(self):
        return self.origem == CANAL_DO_EDITAL and len(self.contatos) > 1


@dataclass(frozen=True)
class PontoParaRevisao:
    tipo: str
    descricao: str
    fontes: tuple[Referencia, ...] = ()

    def como_dict(self):
        return {
            "tipo": self.tipo,
            "descricao": self.descricao,
            "fontes": [fonte.como_dict() for fonte in self.fontes],
        }


@dataclass(frozen=True)
class Resposta:
    pergunta: str
    parametros: tuple[tuple[str, str | None], ...]
    instante: datetime
    versao: VersaoConsultada
    tipo: str
    explicacao: Referencia
    referencias: tuple[Referencia, ...] = ()
    avisos: tuple[Aviso, ...] = ()
    mudanca: MudancaDeVersao | None = None
    situacao: SituacaoDeCalendario | None = None

    def __post_init__(self):
        # **Texto e dado sem ato de origem não saem** (`FR-1437`): o cartão é montado antes de a
        # origem ser resolvida, e esta é a porta que impede a resposta de sair com um esquecido.
        sem_origem = [
            referencia.localizacao
            for referencia in self.referencias
            if referencia.natureza in (TEXTO, DADO) and not referencia.origens
        ]
        if sem_origem:
            raise ValueError(f"cartões sem ato de origem: {sem_origem}")
        if self.explicacao.natureza != EXPLICACAO:
            raise ValueError("a explicação precisa ter a natureza de explicação")

    def como_dict(self):
        return {
            "pergunta": self.pergunta,
            "parametros": dict(self.parametros),
            "instante": _instante(self.instante),
            "versao": self.versao.como_dict(),
            "mudanca": self.mudanca.como_dict() if self.mudanca else None,
            "tipo": self.tipo,
            "avisos": [aviso.como_dict() for aviso in self.avisos],
            "explicacao": self.explicacao.conteudo,
            "referencias": [referencia.como_dict() for referencia in self.referencias],
            "situacao": self.situacao.como_dict() if self.situacao else None,
        }
