"""A publicação de convocados, sem banco: o efeito de cada convocação e o que é público (149).

**Dois efeitos, e nenhuma forma nova** (D-002). A forma de comunicar continua a que o Perfil
publicado declarou; o que esta feature decide é o que a publicação faz com cada convocação:

- **convoca** — a convocação cita a publicação e ainda não foi comunicada: a publicação **é** o ato
  que a comunica, e grava a comunicação no instante dela (D-003);
- **divulga** — a convocação já foi comunicada, por mensagem enviada ou por publicação registrada
  fora do GPS: a relação é informativa, e nada se grava (D-004).

Tudo aqui recebe dados já lidos e devolve dados: a prévia e a confirmação chamam as mesmas funções,
e é isso que faz a prévia mostrar exatamente o que a confirmação grava (FR-5728).
"""

from dataclasses import dataclass
from datetime import datetime
from zoneinfo import ZoneInfo

from processo_seletivo.publicacoes.domain.vocabulario_da_regra import (
    FORMA_POR_MENSAGEM_INDIVIDUAL,
    FORMA_POR_PUBLICACAO,
)
from processo_seletivo.shared.canonical import canonical_sha256

CONVOCA = "CONVOCA"
DIVULGA = "DIVULGA"

#: A versão do formato de `conteudo_publico`. Lida pela página e pelo documento, para que uma
#: mudança futura do formato não reinterprete em silêncio os bytes de um ato já praticado.
VERSAO_DO_CONTEUDO = 1

# --- Por que uma convocação fica fora ----------------------------------------------------------
# As causas do `comunicar`, ditas em frase de quem conduz, e com o caminho de cada correção
# (FR-5704). Nenhuma diz "erro": são estados legítimos do certame.
FORA_COM_DESFECHO = "com_desfecho"
FORA_VENCIMENTO_PASSADO = "vencimento_passado"
FORA_INDETERMINADA = "emissao_indeterminada"
FORA_SEM_FORMA = "forma_nao_declarada"
FORA_MENSAGEM_PENDENTE = "mensagem_pendente"

MOTIVOS_DE_FORA = {
    FORA_COM_DESFECHO: (
        "já tem desfecho registrado: a publicação diria «você foi convocado» a quem já respondeu"
    ),
    FORA_VENCIMENTO_PASSADO: (
        "o vencimento informado já passou: corrija a convocação, sucedendo-a com motivo, antes de "
        "publicar"
    ),
    FORA_INDETERMINADA: (
        "o registro anterior desta comunicação ficou em estado indeterminado: confira o histórico "
        "da chamada antes de publicar"
    ),
    FORA_SEM_FORMA: (
        "o Perfil publicado não declara como este Edital comunica a convocação: declare a forma "
        "por Retificação"
    ),
    FORA_MENSAGEM_PENDENTE: (
        "a mensagem individual ainda não foi enviada com sucesso: a publicação não substitui o "
        "envio, que é feito na tela da convocação"
    ),
}


@dataclass(frozen=True)
class Avaliada:
    """Uma convocação vigente, com o que a publicação faria com ela agora."""

    efeito: str | None
    motivo: str | None = None


def avaliar(*, forma, desfechada, enviada_em, indeterminada, vencimento, ja_publicada, agora):
    """O efeito da convocação numa publicação feita em `agora`, ou por que ela fica fora.

    `None` sem motivo é a convocação que não tem nada a fazer aqui — já está numa publicação do GPS.

    **A ordem das perguntas é a do `comunicar`**: primeiro o que a convocação é (já comunicada →
    divulga), e só depois o que impediria comunicá-la. A comunicada com desfecho continua
    divulgável: a relação diz quem foi convocado, e não o que respondeu (spec, *Edge Cases*).
    """
    if ja_publicada:
        return Avaliada(None)
    if enviada_em is not None:
        return Avaliada(DIVULGA)
    if desfechada:
        return Avaliada(None, FORA_COM_DESFECHO)
    if forma is None:
        return Avaliada(None, FORA_SEM_FORMA)
    if forma != FORMA_POR_PUBLICACAO:
        # **A publicação não substitui o envio individual** (FR-5706): a mensagem que falhou, ou
        # que ainda não saiu, continua sendo do gesto das pendentes.
        return Avaliada(None, FORA_MENSAGEM_PENDENTE)
    if indeterminada:
        return Avaliada(None, FORA_INDETERMINADA)
    if vencimento is not None and vencimento < agora:
        # A FR-269b da `019`, na pergunta do envio: o prazo que venceria antes de começar.
        return Avaliada(None, FORA_VENCIMENTO_PASSADO)
    return Avaliada(CONVOCA)


def ordinal(numero):
    """`1ª` — a publicação é feminina, e o número é o da ordem por Edital (D-009)."""
    return f"{numero}ª"


def titulo(numero):
    return f"{ordinal(numero)} publicação de convocados"


def _local(instante):
    from django.conf import settings

    return instante.astimezone(ZoneInfo(settings.TIME_ZONE))


def referencia_nativa(numero, instante):
    """A referência que a publicação grava em cada comunicação que ela convoca (D-002).

    **Lê-se depois de "Publicada em"**, que é o rótulo do portal (FR-3998 da `125`), e diz o lugar,
    a data e a hora e o ato. É também a chave pela qual o aviso da chamada publicada (`066`) agrupa
    os convocados, e por isso inclui o número: duas publicações no mesmo minuto são dois grupos.
    """
    local = _local(instante)
    return (
        f"página pública da seleção no GPS, {local:%d/%m/%Y} às {local:%H}h{local:%M} — "
        f"{titulo(numero)}"
    )


def canal_da_divulgacao(forma, referencia):
    """Como a convocação oficial foi feita, na frase que a relação informativa diz (FR-5705)."""
    if forma == FORMA_POR_PUBLICACAO:
        return f"publicada em {referencia}" if referencia else "publicada fora do GPS"
    if forma == FORMA_POR_MENSAGEM_INDIVIDUAL:
        return "por mensagem individual"
    return "comunicada por outro caminho"


def _iso(instante):
    return instante.isoformat() if instante else None


def compor_grupos(linhas):
    """Os grupos do conteúdo público, das linhas já avaliadas e ordenadas.

    Cada linha é um `dict` com: `chave` (o recorte), `ordem` (a posição do recorte no Edital),
    `perfil`, `lista`, `marco`, `efeito`, `canal` (no divulga), `vencimento`, `nome`, `protocolo`
    e `corrige` (o número da publicação anterior, ou `None`). **Só o que é público entra** (FR-5712,
    D-008): nenhum identificador, nenhuma espécie, nenhum fundamento.

    Um grupo por recorte **e** efeito: um recorte pode ter, na mesma publicação, quem ela convoca e
    quem ela só divulga (a publicação externa registrada antes), e o grupo diz uma coisa só.
    """
    grupos, por_chave = [], {}
    for linha in sorted(linhas, key=lambda item: (item["ordem"], item["efeito"] != CONVOCA)):
        chave = (linha["chave"], linha["efeito"])
        if chave not in por_chave:
            por_chave[chave] = {
                "perfil": linha["perfil"],
                "lista": linha["lista"],
                "marco": linha["marco"],
                "efeito": linha["efeito"],
                "pessoas": [],
            }
            grupos.append(por_chave[chave])
        por_chave[chave]["pessoas"].append(
            {
                "nome": linha["nome"],
                "protocolo": linha["protocolo"],
                "vencimento": _iso(linha["vencimento"]),
                "canal": linha["canal"],
                "corrige": linha["corrige"],
            }
        )
    for grupo in grupos:
        vencimentos = {pessoa["vencimento"] for pessoa in grupo["pessoas"]}
        canais = {pessoa["canal"] for pessoa in grupo["pessoas"]}
        # **O prazo uma vez no grupo, quando é um só** (FR-5715). O mesmo para o canal do divulga:
        # quarenta linhas dizendo "por mensagem individual" não informam mais que uma.
        grupo["vencimentoUnico"] = len(vencimentos) == 1
        grupo["vencimento"] = next(iter(vencimentos)) if len(vencimentos) == 1 else None
        grupo["canalUnico"] = len(canais) == 1
        grupo["canal"] = next(iter(canais)) if len(canais) == 1 else ""
    _distinguir_rotulos_repetidos(grupos)
    return grupos


def _distinguir_rotulos_repetidos(grupos):
    """O marco entra no rótulo só quando dois grupos do mesmo efeito teriam o mesmo (D-009)."""
    vistos = {}
    for grupo in grupos:
        vistos.setdefault((grupo["perfil"], grupo["lista"], grupo["efeito"]), []).append(grupo)
    for repetidos in vistos.values():
        if len(repetidos) == 1:
            for grupo in repetidos:
                grupo["marco"] = ""


def assinatura(*, edital_id, numero, itens):
    """A identidade do alcance que a prévia mostrou (FR-5708).

    `itens` são `(convocacao_id, efeito, comunicacao_id)`, e a comunicação do divulga entra porque
    é ela que o vínculo cita. **O número entra**: se outra publicação acontecer entre a prévia e a
    confirmação, o botão que dizia *"Publicar a 1ª"* não pode gravar a 2ª.
    """
    return canonical_sha256(
        {
            "edital": str(edital_id),
            "numero": numero,
            "itens": sorted([str(c), e, str(m) if m else None] for c, e, m in itens),
        }
    )


def conteudo(*, cabecalho, grupos):
    """O conteúdo público inteiro — o que vira `conteudo_publico` e o que o documento lê."""
    return {"versao": VERSAO_DO_CONTEUDO, "cabecalho": cabecalho, "grupos": grupos}


def natureza(grupos):
    """*Convocação oficial*, *Divulgação informativa*, ou as duas (FR-5721)."""
    efeitos = {grupo["efeito"] for grupo in grupos}
    if efeitos == {CONVOCA}:
        return "Convocação oficial"
    if efeitos == {DIVULGA}:
        return "Divulgação informativa"
    return "Convocação oficial e divulgação informativa"


def nota_do_grupo(grupo):
    """O que o grupo é, numa frase — a mesma na página, na prévia e no documento (FR-5702, FR-5705).

    A diferença entre ato oficial e relação informativa é a que o pedido manda não confundir, e por
    isso é dita em cada grupo, e não só no cabeçalho: uma publicação pode ter os dois.
    """
    if grupo["efeito"] == CONVOCA:
        return (
            "Esta publicação é o ato oficial de convocação das pessoas abaixo: o prazo de cada uma "
            "corre a partir dela."
        )
    if grupo.get("canalUnico") and grupo.get("canal"):
        return (
            f"Relação informativa: a convocação oficial destas pessoas foi feita {grupo['canal']}, "
            "e o prazo de cada uma continua contado de lá."
        )
    return (
        "Relação informativa: a convocação oficial destas pessoas foi feita pelo caminho indicado "
        "em cada linha, e o prazo de cada uma continua contado de lá."
    )


SEM_VENCIMENTO = "o estabelecido no Edital"


def orientacoes(*, requerimento_na_convocacao):
    """As orientações gerais, texto do sistema e não da comissão, ditas uma vez (FR-5716).

    **Fixas de propósito**: o texto livre que chega ao candidato é o caminho por onde dado de
    terceiro vaza (`125`), e aqui ele seria público.
    """
    frases = [
        "As providências de cada pessoa convocada — a lista de documentos, o envio deles e o "
        "acompanhamento — estão em Minhas inscrições, a área do candidato, com o acesso pelo "
        "e-mail da inscrição.",
        "Estar nesta relação não significa ter a documentação aceita nem a matrícula concluída: a "
        "conferência e o resultado de cada pessoa são informados a ela na área do candidato.",
    ]
    if requerimento_na_convocacao:
        frases.append(
            "O Requerimento de Matrícula que o Edital pede na convocação também é preenchido na "
            "área do candidato."
        )
    return frases


def instante(valor):
    """O instante gravado como texto ISO, de volta a `datetime` — ou `None`."""
    return datetime.fromisoformat(valor) if valor else None


__all__ = [
    "CONVOCA",
    "DIVULGA",
    "MOTIVOS_DE_FORA",
    "Avaliada",
    "assinatura",
    "avaliar",
    "canal_da_divulgacao",
    "compor_grupos",
    "conteudo",
    "instante",
    "natureza",
    "nota_do_grupo",
    "ordinal",
    "orientacoes",
    "referencia_nativa",
    "titulo",
]
