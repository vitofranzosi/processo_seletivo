"""O alvo, a faixa e o empate que a atravessa — o cálculo do corte, sem banco e sem norma (014).

**O alvo conta pessoas, e não números de posição.** `desempate.py` registra a convenção e já a
explica por causa desta feature: a posição de alguém é o número de participantes à frente dele mais
um, e as posições consumidas por um grupo empatado são puladas — `1, 1, 3`. Logo "os dez primeiros"
pode terminar na posição **nove** com dez pessoas dentro, e contar por número de posição entregaria
nove. As posições gravadas no ato são leitura; quem decide a faixa é a contagem de pessoas.

**A faixa da primeira emissão é `alvo + excedente`** (D-011). A cláusula 6.10 do 77/2026, a 8.13 do
57 e a 8.12 do 28 mandam analisar os documentos dos suplentes **para chamada imediata**: o suplente
precisa estar deferido antes de a desistência acontecer, e não depois. Os dois entram juntos.

**O vocabulário publicado mora aqui**, e não em `editais`, porque é o cálculo que o executa. A
direção `editais → classificacao` já existe — `editais/domain/validation.py` importa
`classificacao.domain.combinacao` pela mesma razão.
"""

#: Espécies de alvo. `FIXO` é o número publicado; `DO_QUADRO` é a quantidade da linha do quadro de
#: vagas do recorte. Uma **não gera a outra**: 30 suplentes não saem de vaga nenhuma, e "até o
#: número de vagas" muda quando o quadro é retificado (D-011, FR-179).
ALVO_FIXO = "FIXED"
ALVO_DO_QUADRO = "FROM_VACANCY_TABLE"
ESPECIES_DE_ALVO = (ALVO_FIXO, ALVO_DO_QUADRO)

#: O desfecho do empate que atravessa a última posição da faixa. Não há padrão: a ausência impede a
#: publicação, porque as duas saídas fáceis afirmariam norma que ninguém escreveu (FR-182).
EMPATE_ADMITE_EXCEDENTE = "ADMITS_SURPLUS"
EMPATE_ESTRITO = "STRICT"
DESFECHOS_DE_EMPATE = (EMPATE_ADMITE_EXCEDENTE, EMPATE_ESTRITO)

#: Se aquele Edital admite continuação além da faixa publicada. O 77 admite — "até que se preencha o
#: número total de vagas" —, e o 14 não: quem não foi convocado para a entrevista não é classificado
#: no resultado final (D-011, FR-226).
CONTINUACAO_ADMITIDA = "ALLOWED"
CONTINUACAO_NENHUMA = "NONE"
POLITICAS_DE_CONTINUACAO = (CONTINUACAO_ADMITIDA, CONTINUACAO_NENHUMA)

#: A declaração explícita de que aquele corte não alimenta Etapa alguma. **Palavra, e não `null`**:
#: a ausência precisa ser afirmada, e `null` é indistinguível de "esqueci" em toda chave anulável do
#: sistema (D-012, FR-224).
SEM_ETAPA_GOVERNADA = "NONE"

CAMPOS_DA_REGRA = (
    "targetKind",
    "targetCount",
    "surplusCount",
    "tieOutcome",
    "governedStage",
    "continuation",
)


class EmpateAtravessaOCorte(Exception):
    """O empate residual cruza a última posição da faixa, e o Edital publicou alvo estrito.

    Carrega as posições empatadas porque a recusa precisa nomeá-las: quem lê a mensagem tem de
    saber onde a ordem parou de separar (FR-195, UX-025).
    """

    def __init__(self, posicao, quantas):
        self.posicao = posicao
        self.quantas = quantas
        super().__init__(f"empate residual na posição {posicao}, com {quantas} participantes")


def normalizar(regra):
    """A forma publicada, com uma grafia só para cada significado (FR-193, I4 da revisão cruzada).

    `surplusCount` sai sempre, inclusive `0`, e `targetCount` sai `None` em alvo derivado — nunca
    ausente. A obsolescência compara o `cutRule` congelado com o da versão vigente: duas regras
    semanticamente idênticas gravadas com bytes diferentes acusariam diferença onde não há, e cada
    falso positivo custa uma geração sucessora emitida à toa, que é ato irreversível.
    """
    if not regra:
        return None
    especie = regra.get("targetKind")
    return {
        "targetKind": especie,
        "targetCount": regra.get("targetCount") if especie == ALVO_FIXO else None,
        "surplusCount": int(regra.get("surplusCount") or 0),
        "tieOutcome": regra.get("tieOutcome"),
        "governedStage": regra.get("governedStage"),
        "continuation": regra.get("continuation"),
    }


def etapa_governada(regra):
    """A Etapa que o corte alimenta — **lida da declaração**, nunca inferida (D-012, FR-224).

    Devolve `None` quando a regra declara `NONE`, que é o marco terminal: o corte é legítimo, é
    auditável, e não tem efeito de participação.

    **Por que não se deriva.** `editais/domain/perfis.py` exige que todo marco enumere ao menos uma
    Etapa — sem Etapa não há pontuação a combinar. Num marco que ordena por **sorteio**, porém, a
    ordem nasce da semente: a Etapa enumerada não entra em conta nenhuma, e está ali para satisfazer
    a validação. Derivar dela quem progride seria derivar de um campo preenchido para publicar, e
    trocá-lo — por qualquer razão — moveria em silêncio quem continua no certame.
    """
    if not regra:
        return None
    declarada = regra.get("governedStage")
    if not declarada or declarada == SEM_ETAPA_GOVERNADA:
        return None
    return str(declarada)


def admite_continuacao(regra):
    return bool(regra) and regra.get("continuation") == CONTINUACAO_ADMITIDA


def alvo_apurado(regra, *, quantidade_do_quadro=None, linha_do_quadro=None):
    """`(quantidade, origem)` — o alvo efetivamente usado, e de onde ele veio (FR-189).

    A origem viaja no universo do ato junto com a identidade da linha, e não é decoração: sem ela,
    retificado o quadro, não há como dizer se **aquele** corte ficou para trás — a quantidade
    sozinha não identifica a linha de onde veio.
    """
    if regra.get("targetKind") == ALVO_FIXO:
        return int(regra.get("targetCount") or 0), {"source": ALVO_FIXO}
    origem = {"source": "VACANCY_TABLE_ROW", "rowId": linha_do_quadro}
    return int(quantidade_do_quadro or 0), origem


def calcular(posicoes, *, alvo, excedente=0, desfecho, desde=0):
    """Quem progride, a partir da ordem emitida e da regra publicada.

    `posicoes` é a sequência `(identificador, posicao)` do ato, na ordem em que ele a emitiu;
    `posicao` nula é participante considerado sem posição — eliminado na própria Etapa do marco, ou
    não classificável —, que **nunca** entra na faixa, qualquer que seja o alvo (FR-191).

    `desde` é a última posição já alcançada pela faixa anterior, e só a continuação o usa: ela
    começa depois dela, e não recomeça do primeiro.

    Devolve `(progrediram, excedentes_por_empate, primeira, ultima)`, onde `progrediram` é a lista
    de identificadores na ordem e `excedentes_por_empate` o subconjunto que entrou além do alvo por
    `ADMITS_SURPLUS`.
    """
    classificaveis = sorted(
        ((ident, pos) for ident, pos in posicoes if pos is not None),
        key=lambda item: item[1],
    )
    candidatos = [item for item in classificaveis if item[1] > desde]
    tamanho = max(int(alvo) + int(excedente or 0), 0)
    dentro = candidatos[:tamanho]
    excedentes = []
    if tamanho and len(candidatos) > tamanho:
        fronteira = dentro[-1][1]
        empatados = [item for item in candidatos[tamanho:] if item[1] == fronteira]
        if empatados:
            # O empate atravessa a última posição **da faixa emitida** — alvo mais excedente, e não
            # a do alvo. É o que o 57 e o 28 exigem: ninguém analisa o suplente 21 porque o 20
            # empatou.
            if desfecho == EMPATE_ESTRITO:
                raise EmpateAtravessaOCorte(fronteira, len(empatados) + 1)
            excedentes = empatados
            dentro = dentro + empatados
    progrediram = [ident for ident, _ in dentro]
    primeira = dentro[0][1] if dentro else desde + 1
    ultima = dentro[-1][1] if dentro else None
    return progrediram, [ident for ident, _ in excedentes], primeira, ultima


__all__ = [
    "ALVO_DO_QUADRO",
    "ALVO_FIXO",
    "CAMPOS_DA_REGRA",
    "CONTINUACAO_ADMITIDA",
    "CONTINUACAO_NENHUMA",
    "DESFECHOS_DE_EMPATE",
    "EMPATE_ADMITE_EXCEDENTE",
    "EMPATE_ESTRITO",
    "ESPECIES_DE_ALVO",
    "EmpateAtravessaOCorte",
    "POLITICAS_DE_CONTINUACAO",
    "SEM_ETAPA_GOVERNADA",
    "admite_continuacao",
    "alvo_apurado",
    "calcular",
    "etapa_governada",
    "normalizar",
]
