"""As estruturas do piloto do assistente do Edital (071, data-model §2 e §4).

**Ao lado das da 070, e não dentro delas.** As estruturas da `070` são o contrato da Fase A, em PR
próprio; o piloto as consome, e não as muda. Os tipos reaproveitam os códigos de lá — os cinco da
`070` mais três que só a pergunta livre produz (`D-011`) —, e só o rótulo de `RESPONDIDA` muda aqui,
porque a resposta do piloto não sai só dos dados.

Tudo congelado, e nada de Django: o domínio continua testável sem banco.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from processo_seletivo.duvidas.domain.estruturas import (
    DADO,
    DEPENDE_DA_LEITURA,
    DETALHE_EM_ANEXO,
    FONTES_DIVERGENTES,
    NAO_INFORMA,
    ORIGINAL,
    RESPONDIDA,
    ROTULO_DA_NATUREZA,
    TEXTO,
    AtoPublicado,
    Link,
)
from processo_seletivo.shared.tempo import ZONA

# ---- as fontes ------------------------------------------------------------------------------

#: A terceira natureza de fonte: o que o sistema calcula no instante — a situação de calendário, o
#: desfecho, a Retificação futura, os documentos por Perfil e lista (`FR-1475`).
CALCULADA = "CALCULADA"
NATUREZAS_DE_FONTE = (TEXTO, DADO, CALCULADA)
ROTULO_DA_FONTE = {**ROTULO_DA_NATUREZA, CALCULADA: "Calculado pelo sistema no instante"}

# ---- os tipos -------------------------------------------------------------------------------

DECISAO_NAO_TOMADA = "DECISAO_NAO_TOMADA"
OUTRA_SELECAO = "OUTRA_SELECAO"
FORA_DO_ESCOPO = "FORA_DO_ESCOPO"
TIPOS = (
    RESPONDIDA,
    NAO_INFORMA,
    DEPENDE_DA_LEITURA,
    FONTES_DIVERGENTES,
    DETALHE_EM_ANEXO,
    DECISAO_NAO_TOMADA,
    OUTRA_SELECAO,
    FORA_DO_ESCOPO,
)
ROTULO_DO_TIPO_NO_PILOTO = {
    RESPONDIDA: "Respondida pelas fontes",
    NAO_INFORMA: "O Edital não informa",
    DEPENDE_DA_LEITURA: "Depende da leitura do Edital",
    FONTES_DIVERGENTES: "Fontes divergentes",
    DETALHE_EM_ANEXO: "Detalhe em anexo",
    DECISAO_NAO_TOMADA: "Decisão que a consulta não toma",
    OUTRA_SELECAO: "Outra seleção",
    FORA_DO_ESCOPO: "Fora do escopo",
}

# ---- os trechos da resposta -----------------------------------------------------------------

#: O que o assistente **fez** em cada trecho. Os rótulos não repetem os das fontes, para que a tela
#: nunca mostre dois "dado" com sentidos diferentes (contracts/saida-do-modelo.md §2, princípio I).
EXPLICACAO_DO_ASSISTENTE, DADO_SEGUNDO_A_FONTE, CITACAO_LITERAL = "explicacao", "dado", "citacao"
NATUREZAS_DE_TRECHO = (EXPLICACAO_DO_ASSISTENTE, DADO_SEGUNDO_A_FONTE, CITACAO_LITERAL)
ROTULO_DO_TRECHO = {
    EXPLICACAO_DO_ASSISTENTE: "Explicação do assistente",
    DADO_SEGUNDO_A_FONTE: "Dado, segundo a fonte",
    CITACAO_LITERAL: "Citação literal",
}

# ---- os estados de uma troca (data-model §4) ------------------------------------------------

RESPONDIDA_E_CONFERIDA = "RESPONDIDA_E_CONFERIDA"
NAO_PASSOU_NA_CONFERENCIA = "NAO_PASSOU_NA_CONFERENCIA"
INCOMPLETA = "INCOMPLETA"
POSSIVEL_CORTE = "POSSIVEL_CORTE"
MODELO_DIFERENTE = "MODELO_DIFERENTE"
RESPOSTA_MALFORMADA = "RESPOSTA_MALFORMADA"
INDISPONIVEL = "INDISPONIVEL"
TEMPO_ESGOTADO = "TEMPO_ESGOTADO"
LIMITE_DO_SERVICO = "LIMITE_DO_SERVICO"
ORCAMENTO_ESGOTADO = "ORCAMENTO_ESGOTADO"
LIMITE_DE_USO = "LIMITE_DE_USO"
EXCEDE_O_CONTEXTO = "EXCEDE_O_CONTEXTO"
PERGUNTA_RECUSADA = "PERGUNTA_RECUSADA"
SEM_TOKENIZER = "SEM_TOKENIZER"
ESTADOS = (
    RESPONDIDA_E_CONFERIDA,
    NAO_PASSOU_NA_CONFERENCIA,
    INCOMPLETA,
    POSSIVEL_CORTE,
    MODELO_DIFERENTE,
    RESPOSTA_MALFORMADA,
    INDISPONIVEL,
    TEMPO_ESGOTADO,
    LIMITE_DO_SERVICO,
    ORCAMENTO_ESGOTADO,
    LIMITE_DE_USO,
    EXCEDE_O_CONTEXTO,
    PERGUNTA_RECUSADA,
    SEM_TOKENIZER,
)

TELA, AVALIACAO = "TELA", "AVALIACAO"
ORIGENS = (TELA, AVALIACAO)

# ---- os motivos de recusa da conferência (contracts/saida-do-modelo.md §3) -------------------

FORMA = "FORMA"
FONTE_INEXISTENTE = "FONTE_INEXISTENTE"
CITACAO_NAO_LITERAL = "CITACAO_NAO_LITERAL"
VALOR_SEM_FONTE = "VALOR_SEM_FONTE"
TIPO_SEM_FONTE = "TIPO_SEM_FONTE"
NEGATIVA_NAO_DECLARADA = "NEGATIVA_NAO_DECLARADA"


def _ato_em_palavras(ato: AtoPublicado) -> str:
    quando = ato.publicado_em.astimezone(ZONA).strftime("%d/%m/%Y")
    if ato.ato == ORIGINAL:
        return f"Publicação original de {quando}"
    return f"Retificação publicada em {quando}"


@dataclass(frozen=True)
class Fonte:
    """Uma fonte entregue ao modelo, derivada de um cartão da `070` ou calculada (`R-002`).

    `conteudo` é o do cartão, **sem acréscimo**: o texto do Edital continua idêntico ao publicado. A
    Retificação futura não entra aqui; ela é outra fonte, `CALCULADA`, com `altera` apontando esta.
    """

    id: str
    natureza: str
    lugar: str
    conteudo: str
    caminho: str = ""
    posicao: int | None = None
    rotulo: str = ""
    origens: tuple[AtoPublicado, ...] = ()
    links: tuple[Link, ...] = ()
    anexo: bool = False
    altera: str | None = None

    def __post_init__(self):
        if self.natureza not in NATUREZAS_DE_FONTE:
            raise ValueError(f"natureza de fonte desconhecida: {self.natureza}")

    @property
    def ato(self) -> str:
        """Os atos de origem em palavras, como a tela da `070` os escreve, na zona institucional."""
        if not self.origens:
            return "Calculado pelo sistema" if self.natureza == CALCULADA else ""
        return "; ".join(_ato_em_palavras(ato) for ato in self.origens)

    def para_o_modelo(self) -> dict:
        """A linha da fonte, na ordem fixa do contrato (contracts/saida-do-modelo.md §1)."""
        linha = {
            "id": self.id,
            "natureza": ROTULO_DA_FONTE[self.natureza],
            "lugar": self.lugar,
            "ato": self.ato,
            "conteudo": self.conteudo,
        }
        if self.rotulo:
            linha["rotulo"] = self.rotulo
        if self.altera:
            linha["altera"] = self.altera
        return linha

    def como_dict(self) -> dict:
        """A forma gravada na troca, para a análise sem rederivar (data-model §3)."""
        return {
            **self.para_o_modelo(),
            "caminho": self.caminho,
            "posicao": self.posicao,
            "anexo": self.anexo,
            "origens": [ato.como_dict() for ato in self.origens],
            "links": [link.como_dict() for link in self.links],
        }


@dataclass(frozen=True)
class Trecho:
    natureza: str
    texto: str
    fontes: tuple[str, ...] = ()

    def como_dict(self):
        return {"natureza": self.natureza, "texto": self.texto, "fontes": list(self.fontes)}


@dataclass(frozen=True)
class SaidaDoModelo:
    tipo: str
    trechos: tuple[Trecho, ...]

    def citadas(self) -> tuple[str, ...]:
        vistas = []
        for trecho in self.trechos:
            for fonte in trecho.fontes:
                if fonte not in vistas:
                    vistas.append(fonte)
        return tuple(vistas)


@dataclass(frozen=True)
class Motivo:
    regra: str
    trecho: int | None = None
    valor: str = ""

    def como_dict(self):
        return {"regra": self.regra, "trecho": self.trecho, "valor": self.valor}


@dataclass(frozen=True)
class Conferencia:
    """O resultado da conferência da saída (`R-005`). Recusa com o primeiro motivo basta."""

    motivos: tuple[Motivo, ...] = ()
    saida: SaidaDoModelo | None = None

    @property
    def aprovada(self) -> bool:
        return not self.motivos and self.saida is not None


@dataclass(frozen=True)
class Devolucao:
    """O que o serviço devolveu (contracts/servico-de-inferencia.md §1).

    `raciocinio` existe só até ser descartado por quem chamou: não vai à troca, à tela nem ao log
    (`FR-1492`).
    """

    texto: str
    modelo: str
    tokens_de_entrada: int | None = None
    tokens_de_saida: int | None = None
    termino: str = ""
    custo: float | None = None
    provedor: str = ""
    raciocinio: str = field(default="", repr=False)
