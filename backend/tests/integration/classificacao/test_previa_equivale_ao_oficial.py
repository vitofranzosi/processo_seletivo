"""A linha de base do caminho oficial, congelada antes de a preparação do universo sair dele (094).

A spec 094 tira de `calcular_ordem` a parte que decide — quem tem eliminação, quem não tem
pontuação, quem é classificável — para uma função pura que a prévia também chama. A condição do
usuário para autorizar a extração foi que **nenhum resultado oficial mude**, e este arquivo é a
prova: ele foi escrito e passou contra o código de antes da extração, e passa igual depois dela.

**A tabela esperada é absoluta, e não "o que o código produzia".** Uma comparação entre antes e
depois, calculada na hora, passaria do mesmo jeito se os dois lados mudassem juntos. Aqui cada
posição, empate, critério que separou e motivo está escrito à mão; quem precisar mudar um deles
está mudando o resultado oficial, e o teste diz qual.

**Os dados percorrem o caminho normal**: Avaliação concluída e consolidada, e não `ResultadoEtapa`
criado à mão. É o que garante que as eliminações e os motivos são os que o produto grava. Só os
fatos declarados entram por `bulk_create`, que é a única escrita que `ValorDeFato` admite e é a
mesma que o envio da inscrição faz.

A sentinela, no fim, prova que a comparação morde: com o caminho oficial alterado, ela acusa.
"""

import datetime
import re
from decimal import Decimal

import pytest
from django.utils import timezone

from processo_seletivo.classificacao.application import previa
from processo_seletivo.classificacao.application.calculo import calcular_ordem
from processo_seletivo.classificacao.application.corte import calcular_corte
from processo_seletivo.classificacao.domain import cenarios_da_previa as cenarios
from processo_seletivo.classificacao.domain import desempate, faixa
from processo_seletivo.classificacao.models import ItemDoCorte
from processo_seletivo.inscricoes.models import ValorDeFato
from processo_seletivo.interface.previa_da_classificacao import apurar_vagas
from processo_seletivo.publicacoes.application.selectors import effective_version
from processo_seletivo.publicacoes.models_retificacao import VersaoConsolidada
from processo_seletivo.resultados.models import ResultadoEtapa
from processo_seletivo.shared.api.problems import DomainError
from tests.fixtures.divulgacao import emitir, montar_marco, pontuar
from tests.fixtures.edital import PROFILE_ID
from tests.fixtures.recortes import MODALIDADE_PCD, MODALIDADE_PPI, montar_cenario_7_1_2

pytestmark = [pytest.mark.integration, pytest.mark.django_db(transaction=True)]

SEED = 94
EXPERIENCIA = "00000000-0000-4000-8000-0000000094a1"
NASCIMENTO = "00000000-0000-4000-8000-0000000094a2"
POR_EXPERIENCIA = "00000000-0000-4000-8000-0000000094b1"
POR_NASCIMENTO = "00000000-0000-4000-8000-0000000094b2"

FATOS = [
    {"id": EXPERIENCIA, "code": "EXPERIENCIA", "label": "Meses de experiência", "type": "INTEIRO"},
    {"id": NASCIMENTO, "code": "NASCIMENTO", "label": "Data de nascimento", "type": "DATA"},
]
# Os dois sentidos de ausência, um em cada critério: `CRITERIO_NAO_SE_APLICA` desliga o critério
# para o grupo inteiro em que alguém não tem o valor, e `ULTIMO_NO_CRITERIO` põe quem não tem atrás.
CRITERIOS = [
    {
        "id": POR_EXPERIENCIA,
        "order": 1,
        "type": "MAIOR_VALOR_DE_FATO",
        "parameters": {"factId": EXPERIENCIA},
        "whenMissing": "CRITERIO_NAO_SE_APLICA",
    },
    {
        "id": POR_NASCIMENTO,
        "order": 2,
        "type": "MENOR_VALOR_DE_FATO",
        "parameters": {"factId": NASCIMENTO},
        "whenMissing": "ULTIMO_NO_CRITERIO",
    },
]

# Um candidato por linha: nota na Etapa do marco e os dois fatos. `None` na nota é quem não foi
# avaliado; nos fatos, quem não declarou.
CANDIDATOS = [
    ("90.0000", None, None),
    ("80.0000", 10, datetime.date(1990, 5, 1)),
    ("80.0000", 10, datetime.date(1985, 3, 10)),
    ("80.0000", 5, datetime.date(1970, 1, 1)),
    ("80.0000", 10, None),
    ("70.0000", None, datetime.date(1980, 2, 2)),
    ("70.0000", 3, None),
    ("65.0000", 4, datetime.date(1999, 9, 9)),
    ("65.0000", 4, datetime.date(1999, 9, 9)),
    ("55.0000", 1, datetime.date(2000, 1, 1)),
    (None, 2, datetime.date(2001, 1, 1)),
]

# A ordem que o caminho oficial produz para `CANDIDATOS`, escrita à mão — o índice é o da lista
# acima. `(índice, pontuação, posição, empate residual, critério que separou)`.
ORDEM_COM_CRITERIOS = [
    # Sozinho no grupo dos 90: nenhum critério foi chamado a separar.
    (0, "90.00", 1, False, None),
    # Os quatro de 80 têm todos a experiência: o 1º critério separa o 3 (5 meses) dos demais (10),
    # e o 2º ordena os de 10 pela data — quem não a declarou fica por último.
    (2, "80.00", 2, False, POR_NASCIMENTO),
    (1, "80.00", 3, False, POR_NASCIMENTO),
    (4, "80.00", 4, False, POR_NASCIMENTO),
    (3, "80.00", 5, False, POR_EXPERIENCIA),
    # O 5 não declarou a experiência, e isso desliga o 1º critério para o grupo dos 70 inteiro.
    (5, "70.00", 6, False, POR_NASCIMENTO),
    (6, "70.00", 7, False, POR_NASCIMENTO),
    # Valores iguais em tudo: empate residual, posição compartilhada e a seguinte pulada.
    (7, "65.00", 8, True, None),
    (8, "65.00", 8, True, None),
]


@pytest.fixture
def com_criterios(gestor, api_client, manager_headers, process_payload):
    """O marco da 015 com nota mínima eliminatória, os dois critérios e os onze candidatos."""
    cenario = montar_marco(
        gestor,
        api_client,
        manager_headers,
        process_payload,
        seed=SEED,
        codigo="0940",
        criterios=CRITERIOS,
        fatos=FATOS,
        regra_da_etapa={"minimumScore": "60.0000", "eliminatory": True},
    )
    inscricoes = persistir_cenario(cenario, gestor, CANDIDATOS)
    return cenario, inscricoes


def persistir_cenario(cenario, gestor, candidatos, *, primeiro=9401):
    """Grava cada candidato como Inscrição submetida, Resultado consolidado e fatos congelados."""
    inscricoes = pontuar(
        cenario,
        gestor,
        [nota for nota, *_ in candidatos],
        primeiro=primeiro,
        sufixo=f"094-{primeiro}",
    )
    versao = VersaoConsolidada.objects.filter(edital=cenario["edital"]).latest("materialized_at")
    agora = timezone.now()
    valores = []
    for inscricao, (_, experiencia, nascimento) in zip(inscricoes, candidatos, strict=True):
        if experiencia is not None:
            valores.append((inscricao, EXPERIENCIA, {"valor_inteiro": experiencia}))
        if nascimento is not None:
            valores.append((inscricao, NASCIMENTO, {"valor_data": nascimento}))
    ValorDeFato.objects.bulk_create(
        [
            ValorDeFato(
                inscricao=inscricao,
                fato_id=fato,
                congelado_em=agora,
                versao=versao,
                **valor,
            )
            for inscricao, fato, valor in valores
        ]
    )
    return inscricoes


def retrato(proposta):
    """O que a extração não pode mudar, numa forma que se compara campo a campo."""
    return {
        "posicoes": [
            (
                item["inscricao_id"],
                str(item["pontuacao"]),
                item["posicao"],
                item["empate_residual"],
                (item["separado_por"] or {}).get("id"),
                item["consequencia"],
                item["motivo"],
            )
            for item in proposta["posicoes"]
        ],
        "sem_posicao": [
            (item["inscricao_id"], item["consequencia"], item["motivo"])
            for item in proposta["sem_posicao"]
        ],
        "universo": proposta["universo"],
        "lista_id": proposta["lista_id"],
    }


def divergencias(obtido, esperado):
    """As chaves em que o retrato difere do esperado — vazio quando nada mudou."""
    return [
        f"{chave}: esperado {esperado[chave]!r}, obtido {obtido.get(chave)!r}"
        for chave in esperado
        if obtido.get(chave) != esperado[chave]
    ]


def universo_esperado(edital, inscricoes, etapa_id):
    """O universo do ato, montado do banco e não do cálculo: participantes e Resultados vigentes."""
    versao = VersaoConsolidada.objects.filter(edital=edital).latest("materialized_at")
    resultados = ResultadoEtapa.vigentes.filter(
        edital=edital,
        inscricao__in=inscricoes,
        etapa_id=etapa_id,
    )
    return {
        "processoId": str(edital.processo_id),
        "editalId": str(edital.id),
        "versionId": str(versao.id),
        "participants": sorted(str(item.id) for item in inscricoes),
        "stageResults": [
            {
                "id": str(item.id),
                "registrationId": str(item.inscricao_id),
                "stageId": str(item.etapa_id),
                "versionId": str(item.versao_id),
                "consolidatedAt": item.consolidado_em.isoformat(),
            }
            for item in sorted(resultados, key=lambda item: str(item.id))
        ],
    }


def esperado_com_criterios(cenario, inscricoes):
    ids = [str(item.id) for item in inscricoes]
    eliminado = ResultadoEtapa.vigentes.get(inscricao=inscricoes[9], etapa_id=cenario["etapa"])
    return {
        # **Dentro do empate residual, a ordem é a da consulta**, por identificador da inscrição: o
        # motor não ordena empatados, e os identificadores são sorteados a cada execução. Fixar a
        # ordem pelo índice da tabela fazia este caso passar em metade das execuções.
        "posicoes": sorted(
            (
                (ids[indice], pontuacao, posicao, empate, separou, "HABILITADA", "")
                for indice, pontuacao, posicao, empate, separou in ORDEM_COM_CRITERIOS
            ),
            key=lambda linha: (linha[2], linha[0]),
        ),
        # **A ordem de `sem_posicao` é a da consulta**, por identificador da inscrição: é a que o
        # ato grava, e a extração não pode reordená-la.
        "sem_posicao": sorted(
            [
                (ids[9], "ELIMINADA", eliminado.motivo),
                (ids[10], "", "Sem pontuação nas Etapas enumeradas: Prova didática."),
            ]
        ),
        "universo": {
            **universo_esperado(cenario["edital"], inscricoes, cenario["etapa"]),
            "profileId": cenario["perfil"],
            "milestoneId": cenario["marco"],
        },
        "lista_id": None,
    }


def _calcular(cenario, *, lista_id=None):
    return calcular_ordem(
        edital=cenario["edital"],
        perfil_id=cenario["perfil"],
        marco_id=cenario["marco"],
        lista_id=lista_id,
    )


def test_a_ordem_com_criterios_eliminacao_e_ausencia_e_a_da_tabela(com_criterios):
    cenario, inscricoes = com_criterios

    obtido = retrato(_calcular(cenario))

    assert divergencias(obtido, esperado_com_criterios(cenario, inscricoes)) == []


def test_a_eliminacao_carrega_o_motivo_gravado_na_consolidacao(com_criterios):
    """O motivo da eliminação é o do Resultado, e não um texto que a classificação componha."""
    cenario, inscricoes = com_criterios

    (eliminado,) = [
        item
        for item in _calcular(cenario)["sem_posicao"]
        if item["inscricao_id"] == str(inscricoes[9].id)
    ]

    assert eliminado["motivo"]
    assert eliminado["posicao"] is None
    assert eliminado["pontuacao"] is None
    assert eliminado["empate_residual"] is False
    assert eliminado["separado_por"] is None
    assert eliminado["pontuacoes"] == {cenario["etapa"]: Decimal("55.0000")}


def test_as_pontuacoes_e_os_fatos_viajam_com_cada_classificavel(com_criterios):
    """O ato grava a proveniência por critério a partir destas duas chaves."""
    cenario, inscricoes = com_criterios
    posicoes = {item["inscricao_id"]: item for item in _calcular(cenario)["posicoes"]}

    segundo = posicoes[str(inscricoes[2].id)]

    assert segundo["pontuacoes"] == {cenario["etapa"]: Decimal("80.0000")}
    assert segundo["fatos"] == {EXPERIENCIA: 10, NASCIMENTO: datetime.date(1985, 3, 10)}
    assert segundo["protocolo"] == inscricoes[2].protocolo
    assert segundo["nome"] == inscricoes[2].nome
    assert segundo["identity_subject"] == inscricoes[2].identity_subject
    assert segundo["modalidade_id"] == cenario["modalidade"]
    assert segundo["resultados"] == [
        str(ResultadoEtapa.vigentes.get(inscricao=inscricoes[2], etapa_id=cenario["etapa"]).id)
    ]


# --- O recorte reservado (034) ------------------------------------------------------------------
#
# A função extraída recebe o recorte e o reaplica sobre o que recebeu. No caminho oficial isso é
# idempotente, porque a consulta já filtrou — e é o que estes casos prendem: a ampla continua sendo
# o Perfil inteiro, e cada reservado só quem se autodeclarou nele.


@pytest.fixture
def com_recortes(gestor, api_client, manager_headers, process_payload):
    edital, pontuada, inscricoes = montar_cenario_7_1_2(
        gestor,
        api_client,
        manager_headers,
        process_payload,
        prefixo="previa-094",
        emitir_a_ordem=False,
    )
    from tests.fixtures.corte import MARCO

    cenario = {"edital": edital, "perfil": PROFILE_ID, "marco": MARCO, "etapa": pontuada["id"]}
    return cenario, inscricoes


def _esperado_do_recorte(cenario, inscricoes, ordem, sem_posicao, lista_id):
    ids = [str(item.id) for item in inscricoes]
    pontuacoes = ["95.00", "90.00", "85.00", "80.00", "75.00"]
    participantes = [inscricoes[indice] for indice in [*ordem, *sem_posicao]]
    return {
        "posicoes": [
            (ids[indice], pontuacoes[indice], posicao, False, None, "HABILITADA", "")
            for posicao, indice in enumerate(ordem, start=1)
        ],
        "sem_posicao": [
            (ids[indice], "", "Sem pontuação nas Etapas enumeradas: Prova didática.")
            for indice in sem_posicao
        ],
        "universo": {
            **universo_esperado(cenario["edital"], participantes, cenario["etapa"]),
            "profileId": PROFILE_ID,
            "milestoneId": cenario["marco"],
        },
        "lista_id": lista_id,
    }


@pytest.mark.parametrize(
    ("lista_id", "ordem", "sem_posicao"),
    [
        (None, [0, 1, 2, 3, 4], [5]),
        (MODALIDADE_PPI, [2, 4], []),
        (MODALIDADE_PCD, [1], []),
    ],
    ids=["ampla", "ppi", "pcd"],
)
def test_cada_recorte_tem_o_universo_e_a_ordem_da_tabela(
    com_recortes, lista_id, ordem, sem_posicao
):
    cenario, inscricoes = com_recortes

    obtido = retrato(_calcular(cenario, lista_id=lista_id))

    esperado = _esperado_do_recorte(cenario, inscricoes, ordem, sem_posicao, lista_id)
    assert divergencias(obtido, esperado) == []


# --- A sentinela: a comparação acusa quando o caminho oficial muda ------------------------------
#
# Uma comparação que nunca reprova não prova nada. Cada caso altera **só o caminho oficial** — o
# vocabulário da eliminação, o sentido de um critério, o texto do motivo — e espera que a tabela
# acuse a diferença na chave certa. A sentinela da equivalência com a prévia está no fim do arquivo.


@pytest.mark.parametrize(
    ("modulo", "atributo", "desvio", "chaves"),
    [
        (
            "processo_seletivo.classificacao.domain.universo_classificavel",
            "ELIMINADA",
            "ELIMINADA_POR_OUTRO_NOME",
            {"posicoes", "sem_posicao"},
        ),
        (
            "processo_seletivo.classificacao.domain.desempate",
            "MAIOR_PRIMEIRO",
            frozenset(),
            {"posicoes"},
        ),
        (
            "processo_seletivo.classificacao.domain.universo_classificavel",
            "_motivo_da_pontuacao_ausente",
            lambda *_: "Sem nota.",
            {"sem_posicao"},
        ),
    ],
    ids=["eliminacao-ignorada", "criterio-invertido", "motivo-reescrito"],
)
def test_a_tabela_acusa_o_caminho_oficial_alterado(
    com_criterios, monkeypatch, modulo, atributo, desvio, chaves
):
    cenario, inscricoes = com_criterios
    esperado = esperado_com_criterios(cenario, inscricoes)
    monkeypatch.setattr(f"{modulo}.{atributo}", desvio)

    obtido = retrato(_calcular(cenario))

    assert {item.split(":")[0] for item in divergencias(obtido, esperado)} == chaves


# --- A prévia contra o caminho oficial, sobre os mesmos candidatos (T034, T035) ----------------
#
# A outra metade da equivalência da spec 094. Os candidatos fictícios de cada caso-limite são
# **gravados** pelo caminho normal — inscrição, avaliação, consolidação, fatos congelados —, e o
# caminho oficial inteiro corre sobre eles: a ordem por `calcular_ordem`, o **ato emitido** pelo
# command, o corte por `calcular_corte` sobre o ato, e a apuração por `titulares_iniciais`. A
# prévia calcula sobre os mesmos candidatos, em memória. Ordem, empates, critério que separou,
# sem posição, corte e apuração precisam coincidir. Dentro de um empate residual a ordem não é
# normativa (o motor não ordena empatados): compara-se por posição.

ALVO, VAGAS = 5, 5
#: A posição e o tamanho do empate, lidos da recusa do corte oficial — ela só os diz no texto.
RECUSA = re.compile(r"empate na posição (\d+), com (\d+) participantes")
CASOS_DA_EQUIVALENCIA = [
    # caso-limite, suplentes, desfecho, o corte que o caso tem de produzir
    ("sem_empate", 2, "ADMITS_SURPLUS", "emitido"),
    ("criterios_sucessivos", 2, "ADMITS_SURPLUS", "emitido"),
    ("empate_na_faixa", 2, "ADMITS_SURPLUS", "emitido"),
    ("empate_na_faixa", 2, "STRICT", "recusado"),
    # Sem suplentes, o empate da última vaga é o da última posição da faixa: o corte admite os
    # dois, e é a apuração das vagas que para — a linha do achado que a prévia antecipa.
    ("empate_nas_vagas", 0, "ADMITS_SURPLUS", "emitido"),
    ("valor_ausente", 2, "ADMITS_SURPLUS", "emitido"),
]


def _regra(suplentes, desfecho):
    return {
        "targetKind": "FIXED",
        "targetCount": ALVO,
        "surplusCount": suplentes,
        "tieOutcome": desfecho,
        "governedStage": "NONE",
        "continuation": "NONE",
    }


def _marco_publicado(cenario):
    """O marco, as Etapas e os fatos como o Edital os publicou — o que as duas pontas leem."""
    conteudo = effective_version(edital_id=cenario["edital"].id).content
    perfil = next(p for p in conteudo["profiles"] if str(p["id"]) == str(cenario["perfil"]))
    marco = next(
        m for m in perfil["classificationMilestones"] if str(m["id"]) == str(cenario["marco"])
    )
    return marco, conteudo["stages"], perfil.get("declaredFacts") or []


def _populacao(caso, marco, etapas, fatos):
    """Os candidatos que `simular` vai gerar — os mesmos argumentos, os mesmos candidatos."""
    por_id = {str(e["id"]): e for e in etapas}
    enumeradas = [por_id[e] for e in marco["stages"] if e in por_id]
    candidatos, _ = cenarios.caso_limite(
        caso,
        etapas_enumeradas=enumeradas,
        etapa_do_marco=max(enumeradas, key=lambda e: e["order"]),
        fatos=fatos,
        alvo=ALVO,
        suplentes=marco["cutRule"]["surplusCount"],
        vagas=VAGAS,
        corta=True,
    )
    return candidatos


def _gravar(cenario, gestor, candidatos, primeiro):
    """Nota abaixo da mínima (60) para quem a prévia elimina: é como o produto elimina."""
    etapa = str(cenario["etapa"])
    notas = []
    for candidato in candidatos:
        nota = candidato["notas"].get(etapa)
        if candidato["eliminado_em"] == etapa:
            notas.append("50.0000")
        else:
            notas.append(None if nota is None else f"{nota:.4f}")
    inscricoes = pontuar(cenario, gestor, notas, primeiro=primeiro, sufixo=f"094p-{primeiro}")
    versao = VersaoConsolidada.objects.filter(edital=cenario["edital"]).latest("materialized_at")
    agora = timezone.now()
    valores = []
    for inscricao, candidato in zip(inscricoes, candidatos, strict=True):
        for fato_id, valor in candidato["fatos"].items():
            campo = "valor_data" if isinstance(valor, datetime.date) else "valor_inteiro"
            valores.append(
                ValorDeFato(
                    inscricao=inscricao,
                    fato_id=fato_id,
                    congelado_em=agora,
                    versao=versao,
                    **{campo: valor},
                )
            )
    ValorDeFato.objects.bulk_create(valores)
    return inscricoes


def _apuracao(progrediram_em_ordem, empates):
    parada = apurar_vagas(progrediram_em_ordem, VAGAS, empates)
    return "possivel" if parada is None else ("para", *parada)


def _lado_oficial(cenario, gestor, inscricoes):
    indice = {str(i.id): n for n, i in enumerate(inscricoes)}
    proposta = _calcular(cenario)
    ordem = sorted(
        (
            item["posicao"],
            indice[str(item["inscricao_id"])],
            item["empate_residual"],
            (item["separado_por"] or {}).get("id"),
        )
        for item in proposta["posicoes"]
    )
    sem_posicao = sorted(
        (indice[str(item["inscricao_id"])], item["consequencia"])
        for item in proposta["sem_posicao"]
    )
    emitir(cenario, gestor, chave=f"emitir-094-{cenario['edital'].id}")
    try:
        corte = calcular_corte(
            edital=cenario["edital"], perfil_id=cenario["perfil"], marco_id=cenario["marco"]
        )
    except DomainError as erro:
        assert erro.code == "empate_atravessa_o_corte", erro.detail
        posicao, quantas = map(int, RECUSA.search(erro.detail).groups())
        return {
            "ordem": ordem,
            "sem_posicao": sem_posicao,
            "corte": ("recusado", posicao, quantas),
            "apuracao": "nao-avaliada",
        }
    dentro = [i for i in corte["itens"] if i["consequencia"] == ItemDoCorte.Consequencia.PROGREDIU]
    empates = {
        str(item["inscricao_id"]): item["posicao"]
        for item in proposta["posicoes"]
        if item["empate_residual"]
    }
    return {
        "ordem": ordem,
        "sem_posicao": sem_posicao,
        "corte": (
            "emitido",
            sorted(indice[i["inscricao_id"]] for i in dentro),
            sum(1 for i in corte["itens"] if i["excedente_por_empate"]),
        ),
        "apuracao": _apuracao([i["inscricao_id"] for i in dentro], empates),
    }


def _lado_da_previa(caso, marco, etapas, fatos):
    r = previa.simular(
        marco, etapas, fatos, vagas=VAGAS, modo="caso", caso=caso, apurar_vagas=apurar_vagas
    )

    def indice(ident):
        return int(ident[1:])

    ordem = sorted(
        (
            item["posicao"],
            indice(item["inscricao_id"]),
            item["empate_residual"],
            (item["separado_por"] or {}).get("id"),
        )
        for item in r["ordem"]
    )
    sem_posicao = sorted(
        (indice(item["inscricao_id"]), item["consequencia"]) for item in r["sem_posicao"]
    )
    corte, aviso = r["corte"], r["aviso_das_vagas"]
    if corte.get("recusado"):
        corte = ("recusado", corte["posicao"], corte["quantas"])
    else:
        corte = (
            "emitido",
            sorted(indice(i) for i in corte["progrediram"]),
            len(corte["excedentes"]),
        )
    if not aviso["avaliado"]:
        apuracao = "nao-avaliada"
    else:
        apuracao = ("para", aviso["posicao"], aviso["quantas"]) if aviso["para"] else "possivel"
    return {"ordem": ordem, "sem_posicao": sem_posicao, "corte": corte, "apuracao": apuracao}


@pytest.fixture
def montar(gestor, api_client, manager_headers, process_payload):
    """Um Edital publicado por caso, com a regra do caso no marco e os candidatos da prévia."""

    def _montar(caso, suplentes, desfecho, numero):
        cenario = montar_marco(
            gestor,
            api_client,
            manager_headers,
            process_payload,
            seed=SEED + 10 + numero,
            codigo=f"09{50 + numero}",
            criterios=CRITERIOS,
            fatos=FATOS,
            regra_da_etapa={"minimumScore": "60.0000", "eliminatory": True},
            regra_de_corte=_regra(suplentes, desfecho),
        )
        marco, etapas, fatos = _marco_publicado(cenario)
        inscricoes = _gravar(
            cenario, gestor, _populacao(caso, marco, etapas, fatos), primeiro=9500 + 50 * numero
        )
        return cenario, inscricoes, marco, etapas, fatos

    return _montar


@pytest.mark.parametrize(
    ("numero", "caso", "suplentes", "desfecho", "esperado"),
    [(n, *linha) for n, linha in enumerate(CASOS_DA_EQUIVALENCIA)],
    ids=[f"{c}-{s}-{d}" for c, s, d, _ in CASOS_DA_EQUIVALENCIA],
)
def test_a_previa_e_o_caminho_oficial_concordam(
    montar, gestor, numero, caso, suplentes, desfecho, esperado
):
    cenario, inscricoes, marco, etapas, fatos = montar(caso, suplentes, desfecho, numero)

    oficial = _lado_oficial(cenario, gestor, inscricoes)
    da_previa = _lado_da_previa(caso, marco, etapas, fatos)

    assert da_previa == oficial
    # O caso tem de exercitar o que o nomeia — senão a igualdade é entre duas ordens triviais.
    assert oficial["corte"][0] == esperado
    assert any(empate for _, _, empate, _ in oficial["ordem"]) == caso.startswith("empate")
    if caso == "criterios_sucessivos":
        # Os três diferem já no primeiro critério deste marco — a experiência —, e a data fica sem
        # uso: é a ordem de critérios deste Edital, e não defeito do caso.
        assert POR_EXPERIENCIA in {separou for *_, separou in oficial["ordem"]}
    if caso == "valor_ausente":
        assert [c for _, c in oficial["sem_posicao"]] == ["", "ELIMINADA"]
    if caso == "empate_nas_vagas":
        assert oficial["apuracao"] == ("para", VAGAS, 2)


class _FaixaComUmAMais:
    """A faixa do corte oficial com uma posição a mais — só onde `corte` a enxerga."""

    def __getattr__(self, nome):
        return getattr(faixa, nome)

    @staticmethod
    def calcular(posicoes, *, alvo, **resto):
        return faixa.calcular(posicoes, alvo=alvo + 1, **resto)


def _criterios_invertidos(participantes, criterios):
    """Os critérios aplicados de trás para a frente — `ordenar` os reordena por `order`."""
    return desempate.ordenar(
        participantes, [{**c, "order": -(c.get("order") or 0)} for c in criterios]
    )


@pytest.mark.parametrize(
    ("caso", "atributo", "desvio"),
    [
        (
            "criterios_sucessivos",
            "processo_seletivo.classificacao.application.calculo.ordenar",
            _criterios_invertidos,
        ),
        (
            "sem_empate",
            "processo_seletivo.classificacao.application.corte.faixa",
            _FaixaComUmAMais(),
        ),
        (
            "valor_ausente",
            "processo_seletivo.classificacao.domain.universo_classificavel.ELIMINADA",
            "ELIMINADA_POR_OUTRO_NOME",
        ),
    ],
    ids=["criterio-invertido", "faixa-com-um-a-mais", "eliminacao-ignorada"],
)
def test_a_equivalencia_acusa_o_caminho_oficial_alterado(
    montar, gestor, monkeypatch, caso, atributo, desvio
):
    """A sentinela da FR-2233: mudado só o caminho oficial, a prévia deixa de concordar com ele.

    A prévia é calculada **antes** do desvio, e o desvio alcança só o nome que o caminho oficial
    enxerga — `calculo.ordenar`, `corte.faixa` —, de modo que o lado da prévia é o de sempre.
    """
    cenario, inscricoes, marco, etapas, fatos = montar(caso, 2, "ADMITS_SURPLUS", 9)
    da_previa = _lado_da_previa(caso, marco, etapas, fatos)
    monkeypatch.setattr(atributo, desvio)

    assert _lado_oficial(cenario, gestor, inscricoes) != da_previa
