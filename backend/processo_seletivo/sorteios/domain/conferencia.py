"""A extração declarada já aconteceu? A pergunta feita à fonte antes do compromisso (116).

**O que a fonte afirma.** A Caixa responde, de forma verificável, uma pergunta só: *qual é o último
concurso realizado*. Disso decorre um fato — um número menor ou igual a ele já foi realizado — e é
esse o único fato que esta regra usa para recusar (D-002). A recusa não tem falso positivo: a
extração de um concurso realizado é anterior a qualquer congelamento futuro, e a constituição do
sorteio a recusaria de qualquer jeito, só que com o certame em curso.

**O que a fonte não afirma.** Um número maior que o último **ainda não foi realizado no instante da
consulta**, e é só isso. A API não diz quando ele será: o próximo, o 9999 e o −1 recebem a mesma
resposta HTTP 500. Por isso "ainda não realizado" é informação, e não confirmação (D-003): a
mensagem diz o que foi verificado e o que não foi, e nunca chama a data de confirmada.

**Falha de acesso não vira fato.** Tempo esgotado, rede fora, erro do serviço ou corpo de outra
forma são "inconclusivo": nunca "ainda não realizado", nunca "realizado" (D-004).

**Pura.** O I/O mora no adaptador da fonte e no orquestrador (`sorteios/application/
conferencia.py`), como a granularidade da `102` mora no adaptador e a regra em `viabilidade.py`.
Aqui chegam os números já consultados, e saem a situação, a decisão de cada ato, a mensagem e o
registro. A situação é separada da decisão de propósito (FR-3627): o mesmo "inválido" impede na
publicação e só adverte no congelamento do acervo.
"""

import re
from dataclasses import dataclass
from datetime import date, datetime

from processo_seletivo.shared.tempo import ZONA

REALIZADO = "REALIZADO"
AINDA_NAO_REALIZADO = "AINDA_NAO_REALIZADO"
INCONCLUSIVO = "INCONCLUSIVO"
REFERENCIA_INVALIDA = "REFERENCIA_INVALIDA"

# Os rótulos que quem opera lê na tela. "Ainda não realizado" e nada além: a SC-1095 proíbe
# qualificar o concurso futuro como validado, confirmado ou conferido.
ROTULOS = {
    REALIZADO: "Já realizado",
    AINDA_NAO_REALIZADO: "Ainda não realizado",
    INCONCLUSIVO: "Não foi possível verificar",
    REFERENCIA_INVALIDA: "Número fora da forma",
}

# Os atos que conferem, e a conferência sob demanda da tela, que não é ato (FR-3645).
SUBMISSAO = "submissao"
PUBLICACAO = "publicacao"
RETIFICACAO = "retificacao"
CONGELAMENTO = "congelamento"
SOB_DEMANDA = "sob_demanda"

IMPEDE = "IMPEDE"
ADVERTE = "ADVERTE"
INFORMA = "INFORMA"

# **Os quatro motivos de inconclusão, nas palavras de quem opera, e nada além** (FR-3641,
# FR-3648). Código HTTP, nome de exceção e corpo da resposta ficam de fora: quem lê não tem o que
# fazer com eles, e o registro de auditoria não é lugar de rastro de pilha.
SEM_RESPOSTA_A_TEMPO = "a Caixa não respondeu a tempo"
SEM_CONEXAO = "não foi possível falar com a Caixa"
SEM_O_ULTIMO = "a Caixa respondeu sem o último concurso"
COM_ERRO = "a Caixa respondeu com um erro"
MOTIVOS = (SEM_RESPOSTA_A_TEMPO, SEM_CONEXAO, SEM_O_ULTIMO, COM_ERRO)

# **Um a seis algarismos, e nada mais** (FR-3623). É a forma que a API aceita: `6106-9`, a grafia do
# próprio comunicado da Caixa, recebe HTTP 400, e o defeito só apareceria no dia do sorteio. Seis
# algarismos cobrem o 999999; o concurso de hoje tem quatro.
FORMA_DO_CONCURSO = re.compile(r"^\d{1,6}$")

_DECISAO_REGISTRADA = {
    IMPEDE: "RECUSOU",
    ADVERTE: "PROSSEGUIU_COM_ADVERTENCIA",
    INFORMA: "PROSSEGUIU",
}


@dataclass(frozen=True)
class UltimoConcurso:
    """O último concurso realizado, como a fonte o publicou: número, dia e o próximo anunciado."""

    numero: int
    em: date
    proximo: int | None = None


@dataclass(frozen=True)
class ConsultaDoUltimo:
    """O que a consulta principal trouxe: o último concurso, ou o motivo de não o ter trazido."""

    ultimo: UltimoConcurso | None
    motivo: str = ""


@dataclass(frozen=True)
class Situacao:
    """A referência **no instante da consulta**, com o lastro de onde a situação saiu.

    Valor transitório, nunca persistido como entidade (*Key Entities*). O que se persiste é o
    `registro`, no detalhe do registro de auditoria do ato que a usou.
    """

    estado: str
    fonte: str
    referencia: str
    consultada_em: datetime
    ultimo: int | None = None
    ultimo_em: date | None = None
    realizada_em: date | None = None
    proximo: int | None = None
    motivo: str = ""

    @property
    def numero(self) -> int | None:
        return numero_do_concurso(self.referencia)


def numero_do_concurso(referencia) -> int | None:
    """O número do concurso, ou `None` quando a referência não tem a forma (FR-3623).

    Zero não é concurso, e por isso `0` e `000` caem fora junto do resto.
    """
    texto = str(referencia if referencia is not None else "")
    if not FORMA_DO_CONCURSO.match(texto):
        return None
    numero = int(texto)
    return numero or None


def normalizar(referencia):
    """Os zeros à esquerda retirados, e nenhuma outra transformação (FR-3623, D-001).

    `006114` e `6114` são o mesmo concurso para a Caixa, e precisam ser a mesma referência aqui:
    `OcorrenciaDaFonte` é única por `(fonte, referência)` em texto, e as duas grafias gravariam duas
    linhas para a mesma extração. Retirar um dígito verificador, aparar espaço ou tirar texto
    **não** é inequívoco — `6106-9` pode ser o 6106 ou um 61069 mal digitado —, e por isso o que não
    tem a forma volta como veio, para a recusa dizer o valor que a pessoa escreveu.
    """
    numero = numero_do_concurso(referencia)
    return str(numero) if numero is not None else referencia


def situacao(*, fonte, referencia, consulta, consultada_em, data_da_referencia=None) -> Situacao:
    """Uma das quatro situações (FR-3627, FR-3628, FR-3629).

    **A decisão sai do último concurso, e não da consulta pelo número**: a de um concurso futuro
    devolve 500, igual a um erro do serviço, e não há como separar os dois por ela. A data da
    própria referência só entra quando ela já foi realizada, e a falta dela não desfaz o fato.
    """
    referencia = str(referencia if referencia is not None else "")
    numero = numero_do_concurso(referencia)
    if numero is None:
        return Situacao(REFERENCIA_INVALIDA, fonte, referencia, consultada_em)
    if consulta is None or consulta.ultimo is None:
        motivo = consulta.motivo if consulta is not None else ""
        return inconclusiva(
            fonte=fonte,
            referencia=referencia,
            consultada_em=consultada_em,
            motivo=motivo if motivo in MOTIVOS else SEM_CONEXAO,
        )
    ultimo = consulta.ultimo
    if numero > ultimo.numero:
        return Situacao(
            AINDA_NAO_REALIZADO,
            fonte,
            referencia,
            consultada_em,
            ultimo=ultimo.numero,
            ultimo_em=ultimo.em,
            proximo=ultimo.proximo,
        )
    return Situacao(
        REALIZADO,
        fonte,
        referencia,
        consultada_em,
        ultimo=ultimo.numero,
        ultimo_em=ultimo.em,
        realizada_em=data_da_referencia,
    )


def inconclusiva(*, fonte, referencia, consultada_em, motivo=SEM_CONEXAO) -> Situacao:
    return Situacao(INCONCLUSIVO, fonte, str(referencia), consultada_em, motivo=motivo)


def decisao(situacao: Situacao, ato: str) -> str:
    """O que cada ato faz com a situação (FR-3634 a FR-3637).

    Realizado impede em todo ato que compromete (D-002). Inconclusivo adverte e deixa prosseguir
    (D-004). Ainda não realizado informa, sem advertir: nada de errado foi encontrado (D-003). A
    forma inválida impede nos atos do Edital e só adverte no congelamento, porque lá ela só existe
    em Edital do acervo, e recusar o congelamento dele deixaria o certame sem saída (D-005).
    """
    if situacao.estado == REALIZADO:
        return IMPEDE
    if situacao.estado == INCONCLUSIVO:
        return ADVERTE
    if situacao.estado == REFERENCIA_INVALIDA:
        return ADVERTE if ato == CONGELAMENTO else IMPEDE
    return INFORMA


def _dia(valor) -> str:
    return valor.strftime("%d/%m/%Y")


def _instante(valor) -> str:
    return valor.astimezone(ZONA).strftime("%d/%m/%Y às %H:%M")


def mensagem_da_forma(valor) -> str:
    """A recusa de forma diz o valor e a correção (FR-3626)."""
    return (
        f'O concurso da Loteria Federal é informado só pelo número, e "{valor}" não é um número de '
        "concurso que a Caixa aceita: informe só o número do concurso, como 6106 — sem dígito "
        "verificador, texto ou ano."
    )


def mensagem(situacao: Situacao, ato: str, *, declarada_em=None) -> str:
    """A frase de `contracts/mensagens.md` para a situação e o ato (FR-3639 a FR-3642).

    `declarada_em` é o dia de `occurrenceAt`. Ele **não** é conferido contra a fonte — não há contra
    o que conferir —, e por isso a mensagem de "ainda não realizado" diz o que foi e o que não foi
    verificado.
    """
    fonte = situacao.fonte
    if situacao.estado == REFERENCIA_INVALIDA:
        if ato == CONGELAMENTO:
            return (
                f'O Edital declara a ocorrência "{situacao.referencia}", e a Caixa só aceita o '
                "número do concurso. A relação foi publicada, mas a observação da extração vai "
                "falhar com essa referência. Retifique o método antes do dia do sorteio."
            )
        return mensagem_da_forma(situacao.referencia)
    if situacao.estado == REALIZADO:
        quando = (
            f", em {_dia(situacao.realizada_em)}"
            if situacao.realizada_em
            else " (data não informada pela Caixa)"
        )
        ultimo = f"{situacao.ultimo}, de {_dia(situacao.ultimo_em)}"
        if ato == CONGELAMENTO:
            return (
                f"Não é possível congelar a relação: o concurso {situacao.referencia} da {fonte}, "
                f"declarado no Edital, já foi realizado{quando}. Uma relação congelada depois da "
                "extração nunca poderá ser sorteada. Para sortear, retifique o método declarando "
                f"um concurso posterior ao {ultimo}, e só então publique a relação."
            )
        return (
            f"O concurso {situacao.referencia} da {fonte} já foi realizado{quando}. A semente "
            "precisa vir de uma extração que ainda não aconteceu quando a relação de participantes "
            f"for congelada. O último concurso realizado é o {ultimo}: declare um concurso "
            "posterior a ele, que ocorra depois do fim das inscrições, conferindo o número e a "
            "data no calendário oficial da Caixa."
        )
    if situacao.estado == INCONCLUSIVO:
        texto = (
            f"Não foi possível verificar na Caixa se o concurso {situacao.referencia} já foi "
            f"realizado: {situacao.motivo}. Isso não confirma nem recusa o concurso. Confira no "
            f"resultado oficial da {fonte} que ele ainda não foi realizado."
        )
        return f"{texto} A relação foi publicada." if ato == CONGELAMENTO else texto
    numero = situacao.numero
    anuncio = (
        " (o próximo anunciado pela Caixa)"
        if numero is not None and situacao.proximo == numero
        else ""
    )
    texto = (
        f"Concurso {situacao.referencia}{anuncio}: ainda não realizado na consulta de "
        f"{_instante(situacao.consultada_em)}. O último concurso realizado é o {situacao.ultimo}, "
        f"de {_dia(situacao.ultimo_em)}"
    )
    # A distância só existe para o número: a fonte de demonstração aceita texto (FR-3625).
    if numero is not None:
        texto += f"; o declarado está {numero - situacao.ultimo} concurso(s) adiante"
    if declarada_em is None:
        return (
            f"{texto}. A data prevista não é verificada pela Caixa: confira no calendário "
            f"oficial a data do concurso {situacao.referencia}."
        )
    dias = (declarada_em - situacao.ultimo_em).days
    return (
        f"{texto}, e a data declarada, {_dia(declarada_em)}, {dias} dia(s) depois. A data prevista "
        f"não é verificada pela Caixa: confira no calendário oficial que o concurso "
        f"{situacao.referencia} é o de {_dia(declarada_em)}."
    )


def registro(situacao: Situacao, decisao_do_ato: str) -> dict:
    """O que o registro de auditoria do ato guarda da conferência (FR-3647, FR-3648).

    As seis perguntas da SC-1098 — referência e fonte, instante da consulta, último informado,
    situação, se foi conclusiva, decisão — respondidas só com tipos JSON e datas em ISO, no fuso
    institucional. **Nada da resposta da fonte**: nem corpo, nem código, nem exceção. O motivo de
    inconclusão é a frase de quem opera, a mesma da mensagem.

    "Conclusiva" quer dizer que a situação foi determinada. A forma inválida é determinada sem
    consulta, e por isso é conclusiva.
    """
    return {
        "fonte": situacao.fonte,
        "referencia": situacao.referencia,
        "consultadaEm": situacao.consultada_em.astimezone(ZONA).isoformat(),
        "ultimo": situacao.ultimo,
        "ultimoEm": situacao.ultimo_em.isoformat() if situacao.ultimo_em else None,
        "realizadaEm": situacao.realizada_em.isoformat() if situacao.realizada_em else None,
        "situacao": situacao.estado,
        "conclusiva": situacao.estado != INCONCLUSIVO,
        "decisao": _DECISAO_REGISTRADA[decisao_do_ato],
        "motivo": situacao.motivo,
    }


__all__ = [
    "ADVERTE",
    "AINDA_NAO_REALIZADO",
    "CONGELAMENTO",
    "ConsultaDoUltimo",
    "IMPEDE",
    "INCONCLUSIVO",
    "INFORMA",
    "MOTIVOS",
    "PUBLICACAO",
    "REALIZADO",
    "REFERENCIA_INVALIDA",
    "RETIFICACAO",
    "SOB_DEMANDA",
    "SUBMISSAO",
    "Situacao",
    "UltimoConcurso",
    "decisao",
    "inconclusiva",
    "mensagem",
    "mensagem_da_forma",
    "normalizar",
    "numero_do_concurso",
    "registro",
    "situacao",
]
