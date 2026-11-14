"""O efeito do desfecho desfavorável de uma Etapa, e a gravidade das consequências (164).

Função pura sobre a Etapa **do conteúdo publicado**. Não consulta banco nem conhece modelo, e é por
isso que a tabela-verdade inteira cabe num teste unitário.

**Uma resposta só para cinco perguntadores** (research T-003). A consolidação, a Ocorrência, o
recurso, a Retificação e as telas perguntam todos "o que o desfavorável produz aqui?". Duas tabelas
divergiriam no primeiro Edital atípico, e o candidato leria numa tela um efeito que a consolidação
não aplicou.

**O nulo não é o padrão** (D-002). Na Etapa restrita e eliminatória, a publicação de hoje grava o
efeito sempre explícito; o nulo nela só vem do acervo publicado antes do degrau 23, quando a Etapa
eliminatória eliminava de todas as listas. Lê-lo como "retira da reserva" mudaria, sem Retificação,
o efeito de norma publicada.
"""

from processo_seletivo.editais.domain import alcance

RETIRA_DA_RESERVA = "RETIRA_DA_RESERVA"
ELIMINA = "ELIMINA"

# A grafia do conteúdo publicado, e a do modelo. Duas porque o conteúdo é inglês desde a 001, e a
# coluna é português como o resto do domínio.
PUBLICADO = {RETIRA_DA_RESERVA: "RESERVE_REMOVAL", ELIMINA: "ELIMINATION"}
DO_PUBLICADO = {valor: chave for chave, valor in PUBLICADO.items()}

CAMPO_DESFAVORAVEL = "unfavorableOutcomeEffect"
CAMPO_AUSENCIA = "absenceEffect"

# O vocabulário da consequência, declarado aqui para que o módulo puro não importe modelo; um teste
# prende que estes textos são os de `ResultadoEtapa.Consequencia`.
HABILITADA = "HABILITADA"
RETIRADA_DA_RESERVA = "RETIRADA_DA_RESERVA"
ELIMINADA = "ELIMINADA"

# **A ordem de gravidade** (FR-7028). A vedação de piora da `018` compara por ela: o recurso do
# próprio candidato não produz sucessor mais grave que o superado.
GRAVIDADE = {HABILITADA: 0, RETIRADA_DA_RESERVA: 1, ELIMINADA: 2}

DESFAVORAVEIS = frozenset({RETIRADA_DA_RESERVA, ELIMINADA})


def declara_efeito(etapa) -> bool:
    """A Etapa é das que declaram efeito: restrita a algumas Modalidades e eliminatória."""
    return bool(
        isinstance(etapa, dict) and alcance.restrita(etapa) and etapa.get("eliminatory") is True
    )


def efeito_desfavoravel(etapa) -> str | None:
    """`RETIRA_DA_RESERVA`, `ELIMINA`, ou `None` na Etapa que não declara efeito.

    `None` não quer dizer "não elimina": a Etapa para todas as inscrições, e eliminatória, continua
    eliminando pela regra de hoje. Quer dizer que a pergunta do efeito não se aplica a ela.
    """
    if not declara_efeito(etapa):
        return None
    return DO_PUBLICADO.get(etapa.get(CAMPO_DESFAVORAVEL), ELIMINA)


def efeito_da_ausencia(etapa) -> str | None:
    """O efeito do não comparecimento: o explícito, ou o do desfavorável (FR-7004)."""
    if not declara_efeito(etapa):
        return None
    explicito = DO_PUBLICADO.get(etapa.get(CAMPO_AUSENCIA))
    return explicito or efeito_desfavoravel(etapa)


def pode_retirar(etapa) -> bool:
    """A Etapa produz retirada em algum caso — no desfavorável ou na ausência?"""
    return RETIRA_DA_RESERVA in (efeito_desfavoravel(etapa), efeito_da_ausencia(etapa))


def consequencia_do_efeito(efeito) -> str:
    """A consequência que o efeito produz. Sem efeito declarado, a de hoje: `ELIMINADA`."""
    return RETIRADA_DA_RESERVA if efeito == RETIRA_DA_RESERVA else ELIMINADA


def desfavoravel(consequencia) -> bool:
    return str(consequencia) in DESFAVORAVEIS


def mais_grave(a, b) -> bool:
    """`a` é mais grave que `b`? Consequência desconhecida não é comparável, e não piora."""
    if str(a) not in GRAVIDADE or str(b) not in GRAVIDADE:
        return False
    return GRAVIDADE[str(a)] > GRAVIDADE[str(b)]


def da_coluna(valor) -> str | None:
    """A grafia publicada do valor da coluna, ou `None` para o vazio (rascunho, formulário, API)."""
    return PUBLICADO.get(valor or "")


def para_coluna(valor) -> str:
    """O valor da coluna para a grafia publicada; `""` para `None`, vazio ou desconhecido."""
    return DO_PUBLICADO.get(valor or "", "")


def publicar(etapa_dict, efeito_desfavoravel_do_rascunho, efeito_da_ausencia_do_rascunho):
    """Os dois campos como a publicação os grava (FR-7001, FR-7005, research T-002).

    Explícitos só na Etapa que declara efeito; o vazio do rascunho, no desfavorável, vira "retira
    da reserva". Nas demais, `null` — e por isso o acervo, que só tem Etapas assim ou anteriores ao
    degrau, não muda de significado.
    """
    if not declara_efeito(etapa_dict):
        return {CAMPO_DESFAVORAVEL: None, CAMPO_AUSENCIA: None}
    desfavoravel_ = efeito_desfavoravel_do_rascunho or RETIRA_DA_RESERVA
    return {
        CAMPO_DESFAVORAVEL: PUBLICADO.get(desfavoravel_, PUBLICADO[RETIRA_DA_RESERVA]),
        CAMPO_AUSENCIA: PUBLICADO.get(efeito_da_ausencia_do_rascunho or ""),
    }


_TEXTO = {
    RETIRA_DA_RESERVA: (
        "deixa de concorrer pela reserva de vagas e continua concorrendo pela ampla concorrência"
    ),
    ELIMINA: "é eliminado do processo seletivo",
}


def frase_do_efeito(etapa) -> str:
    """A frase do documento, da Revisão e da página pública (FR-7023, contrato).

    `""` para a Etapa que não declara efeito: é o que faz o acervo se recompor byte a byte
    (SC-2330). Uma frase só quando os dois efeitos coincidem; uma para cada caso quando diferem.
    """
    desfavoravel_ = efeito_desfavoravel(etapa)
    if desfavoravel_ is None:
        return ""
    ausencia = efeito_da_ausencia(etapa)
    if ausencia == desfavoravel_:
        return (
            f"O candidato com resultado desfavorável ou que não comparecer {_TEXTO[desfavoravel_]}."
        )
    return (
        f"O candidato com resultado desfavorável {_TEXTO[desfavoravel_]}. "
        f"O candidato que não comparecer {_TEXTO[ausencia]}."
    )


def nome_da_reserva(conteudo, modality_id) -> str:
    """A denominação da Modalidade da inscrição no conteúdo, ou `""` sem achado."""
    alvo = str(modality_id) if modality_id else ""
    if not alvo:
        return ""
    for perfil in (conteudo or {}).get("profiles") or []:
        for modalidade in perfil.get("competitionModalities") or []:
            if str(modalidade.get("id")) == alvo:
                return modalidade.get("name") or modalidade.get("code") or ""
    return ""


def complemento_da_retirada(conteudo, modality_id) -> str:
    """O fim do motivo do Resultado de retirada (FR-7008): a reserva perdida e a ampla mantida."""
    nome = nome_da_reserva(conteudo, modality_id)
    reserva = f"pela reserva {nome}" if nome else "pela reserva de vagas"
    return f"deixa de concorrer {reserva} e continua na ampla concorrência"


def motivo_com_a_reserva(causa, conteudo, modality_id) -> str:
    """O motivo do Resultado de retirada: a causa, e depois a reserva perdida (FR-7008, FR-7009)."""
    return f"{causa}; {complemento_da_retirada(conteudo, modality_id)}"


__all__ = [
    "CAMPO_AUSENCIA",
    "CAMPO_DESFAVORAVEL",
    "DESFAVORAVEIS",
    "ELIMINA",
    "ELIMINADA",
    "GRAVIDADE",
    "HABILITADA",
    "RETIRADA_DA_RESERVA",
    "RETIRA_DA_RESERVA",
    "complemento_da_retirada",
    "consequencia_do_efeito",
    "da_coluna",
    "declara_efeito",
    "desfavoravel",
    "efeito_da_ausencia",
    "efeito_desfavoravel",
    "frase_do_efeito",
    "mais_grave",
    "motivo_com_a_reserva",
    "nome_da_reserva",
    "para_coluna",
    "pode_retirar",
    "publicar",
]
