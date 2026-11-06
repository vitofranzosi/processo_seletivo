"""Qual mensagem de convocação sai, e qual versão do modelo a escreveu (121, R-002, R-009).

**A escolha é função só do que já está gravado** (FR-3889). O envio a chama para montar a mensagem,
e a auditoria a chama de novo, depois, só com os registros relidos do banco: se a função é a mesma
nos dois lugares, o teste de reconstrução prova a afirmação. Com duas funções, um teste só provaria
que elas concordam naquele caso.

**A mensagem da correção cita a última mensagem enviada com sucesso na cadeia** (D-008, decidida
pelo usuário). Com A enviada, a mensagem de B falhada e C sucessora de B, C cita **A**: a pessoa
recebeu A, e precisa saber que aquele prazo deixou de valer. Ler só a imediatamente anterior, como a
redação anterior da D-008 fazia, mandaria C como inicial — uma convocação "nova", sem aviso de que a
de antes caiu. Os dados do ato, no portal, continuam descrevendo **B** (FR-3869): são outra
pergunta, e as duas leituras não se unificam (R-008).

**Uma comunicação que falhou não conta, nem a publicação**: nenhuma das duas é mensagem que chegou à
caixa de saída da pessoa. Sem nenhuma enviada na cadeia, nada há a substituir, e sai a inicial.

**A versão do modelo é o resumo das fontes que renderizaram** (D-009, opção A). Um número escrito à
mão dependeria de alguém lembrar de mudá-lo; o resumo da mensagem renderizada mudaria a cada pessoa
e viraria dado ligado a ela. O resumo das duas fontes, com rótulos, confere-se contra o Git em
qualquer commit, e a regra está escrita na R-009 para que a conferência não dependa deste código.
"""

import hashlib
from dataclasses import dataclass
from datetime import datetime

INICIAL = "inicial"
CORRECAO = "correcao"

# A variante de obrigação (FR-3884). *Documento* é documento obrigatório (D-007): uma chamada só
# com facultativo não pede documento, e "envie seus documentos" convidaria a um envio que não é
# obrigação.
DOCUMENTO_E_REQUERIMENTO = "documento_e_requerimento"
SO_DOCUMENTO = "so_documento"
SO_REQUERIMENTO = "so_requerimento"
NENHUM = "nenhum"

OBRIGATORIO = "OBRIGATORIO"
ENVIADA = "ENVIADA"
POR_PUBLICACAO = "PUBLICATION"


@dataclass(frozen=True)
class Citada:
    """A mensagem que a da correção substitui: quando ela saiu e o prazo que ela informava."""

    enviado_em: datetime
    vencimento: datetime | None


@dataclass(frozen=True)
class EscolhaDaMensagem:
    modelo: str
    variante: str
    #: Na correção, a última mensagem enviada com sucesso na cadeia; na inicial, `None`.
    citada: Citada | None = None

    @property
    def correcao(self):
        return self.modelo == CORRECAO


def variante_de(*, itens, instante, requerimento_na_chamada):
    """O que a chamada pede de fato, lido da lista gravada no ato de convocar (FR-3884).

    **Só os itens gravados até o instante do envio** (data-model): a lista é append-only, e um item
    acrescido depois não mudaria a mensagem que já saiu.
    """
    pede_documento = any(
        item.situacao == OBRIGATORIO and item.gravada_em <= instante for item in itens
    )
    if pede_documento and requerimento_na_chamada:
        return DOCUMENTO_E_REQUERIMENTO
    if pede_documento:
        return SO_DOCUMENTO
    if requerimento_na_chamada:
        return SO_REQUERIMENTO
    return NENHUM


def citada_na_cadeia(anteriores, *, instante):
    """A última comunicação enviada com sucesso entre as convocações anteriores (D-008).

    `anteriores` é a cadeia a partir da imediatamente anterior, em direção à raiz; cada elo traz o
    `vencimento` e as `comunicacoes`. A citada é a `ENVIADA` de maior `enviado_em` até o instante do
    envio — `FALHA` e publicação não contam. O vencimento é o da convocação **a que ela pertence**,
    que não é o da imediatamente anterior quando a desta falhou.
    """
    candidatas = [
        (comunicacao.enviado_em, elo.vencimento)
        for elo in anteriores
        for comunicacao in elo.comunicacoes
        if comunicacao.resultado == ENVIADA
        and comunicacao.forma != POR_PUBLICACAO
        and comunicacao.enviado_em is not None
        and comunicacao.enviado_em <= instante
    ]
    if not candidatas:
        return None
    enviado_em, vencimento = max(candidatas, key=lambda par: par[0])
    return Citada(enviado_em=enviado_em, vencimento=vencimento)


def escolha_da_mensagem(*, itens, instante, requerimento_na_chamada, anteriores):
    """O modelo, a variante e a citada, só de registros gravados (R-002, FR-3884, FR-3885)."""
    variante = variante_de(
        itens=itens, instante=instante, requerimento_na_chamada=requerimento_na_chamada
    )
    citada = citada_na_cadeia(anteriores, instante=instante)
    if citada is None:
        return EscolhaDaMensagem(modelo=INICIAL, variante=variante)
    return EscolhaDaMensagem(modelo=CORRECAO, variante=variante, citada=citada)


def _fonte(modelo):
    """A fonte que o motor compilou (R-009): `template.template.source`, ou o texto já dado."""
    if isinstance(modelo, str):
        return modelo
    return modelo.template.source


def identificacao_do_modelo(nome, html, texto):
    """``<nome>:sha256:<64 hex>`` das duas fontes que renderizaram o envio (R-009, FR-3889).

    **A composição é fixa**: o HTML e depois o texto, cada um precedido do rótulo, separados por
    NUL, em UTF-8 e sem normalizar fim de linha nem espaço. Os rótulos impedem que um trecho movido
    de um arquivo para o outro produza o mesmo resumo.
    """
    conteudo = (
        b"html\0" + _fonte(html).encode("utf-8") + b"\0texto\0" + _fonte(texto).encode("utf-8")
    )
    return f"{nome}:sha256:{hashlib.sha256(conteudo).hexdigest()}"


__all__ = [
    "CORRECAO",
    "DOCUMENTO_E_REQUERIMENTO",
    "INICIAL",
    "NENHUM",
    "SO_DOCUMENTO",
    "SO_REQUERIMENTO",
    "Citada",
    "EscolhaDaMensagem",
    "citada_na_cadeia",
    "escolha_da_mensagem",
    "identificacao_do_modelo",
    "variante_de",
]
