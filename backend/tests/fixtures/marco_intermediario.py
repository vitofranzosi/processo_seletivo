"""O Edital 900 reduzido: dois marcos ligados pela Entrevista, e as paradas da jornada (133, R-009).

O estudo de convergência de 07/11/2026 reproduziu o Edital 900 fictício inteiro e mediu quatro
defeitos da derivação da `127` (CV-01 a CV-04). A suíte não tinha cenário com **dois marcos ligados
por Etapa governada** — os testes da `127` provam a família P3 só nas funções puras —, e é aqui que
os defeitos aparecem. Este cenário é o 900 com o essencial:

- a Etapa pontuada do cenário do corte (a "prova") e a Entrevista que o corte do marco 1 governa;
- o **marco 1**, *Classificação para a entrevista*: lê a prova, corte fixo de 2 **por lista**,
  governa a Entrevista, recurso de 3 dias corridos;
- o **marco 2**, *Classificação final*: lê a prova e a Entrevista, corte pelo quadro mais 1
  suplente, sem Etapa governada;
- o quadro: ampla 2, PPI 1;
- sete inscrições, duas PPI; a sétima fica sem avaliação até a parada que torna a ordem obsoleta.

As notas, escolhidas para a conta ser lida de cabeça (soma ponderada, pesos 1):

| pos. | modalidade | prova | Entrevista | marco 2 |
|---|---|---|---|---|
| 0 | AC  | 90 | 80 | 170 |
| 1 | AC  | 85 | 90 | 175 |
| 2 | AC  | 80 | —  | (fora da faixa do marco 1) |
| 3 | AC  | 70 | —  | |
| 4 | PPI | 75 | 70 | 145 |
| 5 | PPI | 65 | 65 | 130 |
| 6 | AC  | —  | —  | (sem avaliação) |

Marco 1, ampla: 0, 1 na faixa; PPI: 4, 5. À Entrevista: 0, 1, 4, 5. Marco 2, ampla: 1, 0, 4 (dois
titulares e um suplente); PPI: 4, 5. Titulares da ampla: 1 e 0.

**Funções, e não fixtures** — a regra de `tests/fixtures/corte.py`. Cada parada recebe o cenário
da anterior e o devolve, para que o teste diga até onde quer ir.
"""

from processo_seletivo.classificacao.application.calculo import calcular_ordem
from processo_seletivo.classificacao.application.corte import calcular_corte
from processo_seletivo.classificacao.application.emissao import assinatura_da_proposta, emitir_ordem
from processo_seletivo.classificacao.application.emissao_do_corte import (
    assinatura_da_proposta as assinatura_do_corte,
)
from processo_seletivo.classificacao.application.emissao_do_corte import emitir_corte
from processo_seletivo.classificacao.application.selectors import ato_vigente
from processo_seletivo.ocupacao.application.emissao import emitir_apuracao
from processo_seletivo.publicacoes.domain.vocabulario_da_regra import FORMA_POR_MENSAGEM_INDIVIDUAL
from processo_seletivo.resultados.application.consolidacao import consolidar
from tests.fixtures.autoridades import AUTORIDADE_DO_RESULTADO
from tests.fixtures.corte import ENTREVISTA, MARCO, entrevistar, montar_cenario_do_corte, regra
from tests.fixtures.edital import PROFILE_ID
from tests.fixtures.mesa import concluir_como, distribuir_para
from tests.fixtures.ocupacao import MODALIDADE_PPI, rascunho_com_quadro

MARCO_1 = MARCO
MARCO_2 = "00000000-0000-4000-8000-000000001331"
LISTAS = (None, MODALIDADE_PPI)
CORRELACAO = "teste-133"
PROVA = ("90.0000", "85.0000", "80.0000", "70.0000", "75.0000", "65.0000")
NOTAS_DA_ENTREVISTA = {0: "80.0000", 1: "90.0000", 4: "70.0000", 5: "65.0000"}


def rascunho_do_900(cut=None):  # noqa: ARG001 — o corte do marco 1 é o deste cenário
    # A mensagem individual, como no Edital 900: a comunicação sai pelo correio da suíte, e o
    # prazo corre a partir do envio, sem referência de publicação.
    base, pontuada = rascunho_com_quadro(
        geral=2,
        ppi=1,
        cut=regra(targetCount=2, governedStage=ENTREVISTA),
        forma=FORMA_POR_MENSAGEM_INDIVIDUAL,
    )
    marcos = base["profiles"][0]["classificationMilestones"]
    marcos[0]["name"] = "Classificação para a entrevista"
    marcos[0]["appealWindow"] = {"admits": True, "durationDays": 3, "unit": "DIAS_CORRIDOS"}
    marcos.append(
        {
            "id": MARCO_2,
            "code": "FINAL-900",
            "name": "Classificação final",
            "orderProduction": "POR_PONTUACAO",
            "stages": [pontuada["id"], ENTREVISTA],
            "operation": "SOMA_PONDERADA",
            "normalization": "NENHUMA",
            "rounding": {"scale": 2, "mode": "MEIO_PARA_CIMA"},
            "tiebreakers": [],
            "cutRule": {
                "targetKind": "FROM_VACANCY_TABLE",
                "surplusCount": 1,
                "tieOutcome": "STRICT",
                "governedStage": "NONE",
                "continuation": "NONE",
            },
        }
    )
    return base, pontuada


def montar(gestor, api_client, manager_headers, process_payload, *, prefixo="m900"):
    """O Edital publicado, a comissão, a prova consolidada — e nenhuma ordem ainda."""
    edital, pontuada, inscricoes = montar_cenario_do_corte(
        gestor,
        api_client,
        manager_headers,
        process_payload,
        prefixo=prefixo,
        pontuacoes=PROVA,
        draft_factory=rascunho_do_900,
        emitir_a_ordem=False,
        modalidades={4: MODALIDADE_PPI, 5: MODALIDADE_PPI},
    )
    return {
        "edital": edital,
        "gestor": gestor,
        "pontuada": pontuada,
        "inscricoes": inscricoes,
        "prefixo": prefixo,
    }


def _ordenar(cenario, marco, *, motivo="", chave="ordem"):
    edital = cenario["edital"]
    for lista in LISTAS:
        vigente = ato_vigente(edital=edital, marco_id=marco, lista_id=lista)
        proposta = calcular_ordem(
            edital=edital, perfil_id=PROFILE_ID, marco_id=marco, lista_id=lista
        )
        emitir_ordem(
            actor=cenario["gestor"],
            processo_id=edital.processo_id,
            edital_id=edital.id,
            perfil_id=PROFILE_ID,
            marco_id=marco,
            lista_id=lista,
            motivo=motivo,
            idempotency_key=f"{cenario['prefixo']}-{chave}-{marco[-4:]}-{lista}",
            correlation_id=CORRELACAO,
            confirmacao_do_calculo=assinatura_da_proposta(proposta, ato_vigente=vigente),
        )


def _publicar(cenario, marco, natureza, *, chave="pub"):
    from processo_seletivo.divulgacao.application.publicar import (
        assinatura_da_previa,
        publicar_resultado,
    )
    from processo_seletivo.divulgacao.application.selectors import vigente_do_marco
    from processo_seletivo.divulgacao.domain.conteudo import compor
    from tests.fixtures.divulgacao import ator_publicador

    edital = cenario["edital"]
    for lista in LISTAS:
        ato = ato_vigente(edital=edital, marco_id=marco, lista_id=lista)
        anterior = vigente_do_marco(edital=edital, marco_id=marco, lista_id=lista)
        publicar_resultado(
            actor=ator_publicador(),
            processo_id=edital.processo_id,
            edital_id=edital.id,
            marco_id=marco,
            ato_id=ato.id,
            natureza=natureza,
            autoridade=str(AUTORIDADE_DO_RESULTADO),
            confirmacao_da_previa=assinatura_da_previa(
                ato=ato, publicacao_anterior=anterior, projecao=compor(ato)
            ),
            idempotency_key=f"{cenario['prefixo']}-{chave}-{marco[-4:]}-{lista}",
            correlation_id=CORRELACAO,
            declaracao_de_encerramento=(
                "O prazo recursal encerrou-se sem interposição." if natureza == "DEFINITIVA" else ""
            ),
        )


def _cortar(cenario, marco):
    edital = cenario["edital"]
    for lista in LISTAS:
        emitir_corte(
            actor=cenario["gestor"],
            processo_id=edital.processo_id,
            edital_id=edital.id,
            perfil_id=PROFILE_ID,
            marco_id=marco,
            lista_id=lista,
            idempotency_key=f"{cenario['prefixo']}-corte-{marco[-4:]}-{lista}",
            correlation_id=CORRELACAO,
            confirmacao_do_calculo=assinatura_do_corte(
                calcular_corte(edital=edital, perfil_id=PROFILE_ID, marco_id=marco, lista_id=lista)
            ),
        )


def apurar(cenario, marco, lista=None, *, chave="apurar", motivo=""):
    edital = cenario["edital"]
    return emitir_apuracao(
        actor=cenario["gestor"],
        processo_id=edital.processo_id,
        edital_id=edital.id,
        perfil_id=PROFILE_ID,
        marco_id=marco,
        lista_id=lista,
        idempotency_key=f"{cenario['prefixo']}-{chave}-{marco[-4:]}-{lista}",
        correlation_id=CORRELACAO,
        motivo=motivo,
    )


# --- as paradas ---------------------------------------------------------------------------


def ate_a_ordem_m1(cenario):
    """10/12 no estudo, antes da divulgação: a ordem do marco 1 emitida nas duas listas."""
    _ordenar(cenario, MARCO_1)
    return cenario


def ate_a_preliminar_m1(cenario):
    """A preliminar do marco 1 publicada: o prazo de recurso corre (3 dias a partir de agora)."""
    ate_a_ordem_m1(cenario)
    _publicar(cenario, MARCO_1, "PRELIMINAR")
    return cenario


def ate_a_ordem_obsoleta(cenario):
    """13/12 no estudo: a ordem da ampla fica para trás depois de a preliminar sair.

    O estudo chegou aqui por um recurso deferido; o cenário chega pelo caminho mais curto ao mesmo
    estado — um Resultado novo no universo da ordem (a sétima inscrição, avaliada agora). A causa
    da obsolescência muda; o que a derivação lê, não: a ordem vigente está para trás.
    """
    ate_a_preliminar_m1(cenario)
    edital, pontuada = cenario["edital"], cenario["pontuada"]
    from processo_seletivo.comissoes.models import MembroComissao

    contexto = {
        "edital": edital,
        "processo": edital.processo,
        "membros": {
            "joao": MembroComissao.objects.get(processo=edital.processo, identity_subject="joao")
        },
        "etapa": pontuada["id"],
    }
    setima = cenario["inscricoes"][6]
    distribuir_para(
        contexto, cenario["gestor"], ["joao"], [setima], chave=f"{cenario['prefixo']}-lote-7"
    )
    concluir_como(contexto, "joao", setima, pontuacao="88.0000")
    consolidar(
        actor=cenario["gestor"],
        processo_id=edital.processo_id,
        edital_id=edital.id,
        etapa_id=pontuada["id"],
        inscricao_ids=[setima.id],
        idempotency_key=f"{cenario['prefixo']}-consolidar-7",
        correlation_id=CORRELACAO,
    )
    return cenario


def ate_a_apuracao_m2(cenario):
    """29/12 no estudo: cortes do marco 1, Entrevista, ordem, corte e apuração do marco 2."""
    ate_a_ordem_m1(cenario)
    _cortar(cenario, MARCO_1)
    inscricoes = cenario["inscricoes"]
    entrevistar(
        cenario["edital"],
        cenario["gestor"],
        [(inscricoes[n], nota) for n, nota in NOTAS_DA_ENTREVISTA.items()],
        chave=f"{cenario['prefixo']}-entrevista",
    )
    _ordenar(cenario, MARCO_2)
    _cortar(cenario, MARCO_2)
    for lista in LISTAS:
        apurar(cenario, MARCO_2, lista)
    return cenario


def convocar(cenario, inscricao, lista=None, *, marco=MARCO_2, chave="convocar", **extra):
    from processo_seletivo.convocacao.application.convocar import convocar as praticar

    edital = cenario["edital"]
    return praticar(
        actor=cenario["gestor"],
        processo_id=edital.processo_id,
        edital_id=edital.id,
        perfil_id=PROFILE_ID,
        marco_id=marco,
        lista_id=lista,
        inscricao_id=inscricao.id,
        fundamento="Convocação no Edital, na ordem de classificação vigente.",
        idempotency_key=f"{cenario['prefixo']}-{chave}-{inscricao.id}",
        correlation_id=CORRELACAO,
        **extra,
    )


def ate_a_desistencia_com_titular_pendente(cenario):
    """05/01 no estudo: os dois titulares da ampla convocados; o primeiro desiste, o outro não
    respondeu. Fica 1 vaga a ocupar, e a fila tem o suplente."""
    from processo_seletivo.convocacao.application.comunicar import comunicar
    from processo_seletivo.convocacao.application.desfechar import desfechar

    ate_a_apuracao_m2(cenario)
    edital, inscricoes = cenario["edital"], cenario["inscricoes"]
    chamadas = {}
    for n in (1, 0):
        declarado = convocar(cenario, inscricoes[n])
        comunicar(
            actor=cenario["gestor"],
            processo_id=edital.processo_id,
            convocacao_id=declarado["id"],
            idempotency_key=f"{cenario['prefixo']}-comunicar-{n}",
            correlation_id=CORRELACAO,
        )
        chamadas[n] = declarado["id"]
    desfechar(
        actor=cenario["gestor"],
        processo_id=edital.processo_id,
        convocacao_id=chamadas[1],
        especie="DESISTENCIA_EXPRESSA",
        fundamento="Desistência comunicada por e-mail.",
        idempotency_key=f"{cenario['prefixo']}-desistencia",
        correlation_id=CORRELACAO,
    )
    cenario["chamadas"] = chamadas
    return cenario
