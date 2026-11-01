"""A prévia por recorte contra o caminho oficial, sobre os mesmos candidatos (095, T011, FR-2340).

Os candidatos são **gravados** pelo caminho normal — inscrição, avaliação, consolidação e a
autodeclaração —, e o caminho oficial inteiro corre sobre eles: a ordem de cada recorte pelo
comando, o corte de cada recorte sobre o ato, e a apuração de cada recorte por `emitir_apuracao`,
com a reversão que o Perfil publicou. A prévia calcula sobre os mesmos inscritos, em memória, pela
mesma `por_recorte` que `simular` chama, com a rodada da `ocupacao`. Ordem, faixa, quem ocupa pela
ampla, as quatro quantidades e o que a reservada cede precisam coincidir.

O corte declara não governar Etapa (`NONE`): quem progrediu é quem conta como habilitado, que é
a hipótese da prévia (FR-2320), e o caminho oficial a cumpre sem Resultado nenhum a ler.

A sentinela, no fim, prova que a comparação morde.
"""

from decimal import Decimal

import pytest

from processo_seletivo.classificacao.application import previa
from processo_seletivo.classificacao.application.corte import calcular_corte
from processo_seletivo.classificacao.application.emissao_do_corte import (
    assinatura_da_proposta,
    emitir_corte,
)
from processo_seletivo.classificacao.application.selectors import ato_vigente
from processo_seletivo.classificacao.domain import faixa
from processo_seletivo.classificacao.models import ItemDoCorte, PosicaoNaOrdem
from processo_seletivo.ocupacao.application import selectors as ocupacao
from processo_seletivo.ocupacao.application.emissao import emitir_apuracao
from processo_seletivo.ocupacao.domain import apuracao, nomes, rodada_da_previa
from processo_seletivo.ocupacao.models import MovimentoDeVaga
from processo_seletivo.publicacoes.application.selectors import effective_version
from processo_seletivo.shared.api.problems import DomainError
from tests.fixtures.corte import MARCO, montar_cenario_do_corte
from tests.fixtures.edital import PROFILE_ID
from tests.fixtures.recortes import (
    MODALIDADE_PCD,
    MODALIDADE_PPI,
    emitir_recorte,
    rascunho_7_1_2,
    regra_do_quadro,
)

pytestmark = [pytest.mark.integration, pytest.mark.django_db(transaction=True)]

#: Oito avaliados, em ordem decrescente, e o nono sem avaliação (sem posição em todo recorte).
NOTAS = ("95.0000", "90.0000", "85.0000", "80.0000", "75.0000", "70.0000", "65.0000", "62.0000")
#: 3 vagas na ampla, 1 na PcD, 2 na PPI. PPI: o 2º (entre as vagas da ampla), o 5º e o 7º; PcD: o
#: 3º (entre as vagas da ampla) e o 6º.
AUTODECLARACOES = {
    1: MODALIDADE_PPI,
    4: MODALIDADE_PPI,
    6: MODALIDADE_PPI,
    2: MODALIDADE_PCD,
    5: MODALIDADE_PCD,
}
RECORTES = (None, MODALIDADE_PCD, MODALIDADE_PPI)


def _rascunho(especie):
    def monta(cut=None):
        base, pontuada = rascunho_7_1_2(cut=cut, geral=3, pcd=1, ppi=2)
        if especie:
            base["profiles"][0]["vacancyReversion"] = {"kind": especie}
        return base, pontuada

    return monta


@pytest.fixture
def montar(gestor, api_client, manager_headers, process_payload):
    def _montar(prefixo, *, especie=None, notas=NOTAS, desfecho="ADMITS_SURPLUS"):
        edital, pontuada, inscricoes = montar_cenario_do_corte(
            gestor,
            api_client,
            manager_headers,
            process_payload,
            cut=regra_do_quadro(tieOutcome=desfecho, governedStage="NONE"),
            prefixo=prefixo,
            pontuacoes=notas,
            draft_factory=_rascunho(especie),
            modalidades=AUTODECLARACOES,
        )
        for lista in RECORTES[1:]:
            emitir_recorte(edital, gestor, lista_id=lista, chave=f"{prefixo}-ordem-{lista}")
        return edital, pontuada, inscricoes

    return _montar


def _emitir_cortes(edital, gestor, prefixo):
    for lista in RECORTES:
        proposta = calcular_corte(
            edital=edital, perfil_id=PROFILE_ID, marco_id=MARCO, lista_id=lista
        )
        emitir_corte(
            actor=gestor,
            processo_id=edital.processo_id,
            edital_id=edital.id,
            perfil_id=PROFILE_ID,
            marco_id=MARCO,
            lista_id=lista,
            idempotency_key=f"{prefixo}-corte-{lista}",
            correlation_id="teste-095",
            confirmacao_do_calculo=assinatura_da_proposta(proposta),
        )


def _lado_oficial(edital, gestor, inscricoes, prefixo):
    """Ordem, faixa e apuração de cada recorte, pelos comandos — e a recusa como desfecho."""
    indice = {str(i.id): n for n, i in enumerate(inscricoes)}
    _emitir_cortes(edital, gestor, prefixo)
    saida = {}
    for lista in RECORTES:
        ato = ato_vigente(edital=edital, marco_id=MARCO, lista_id=lista)
        ordem = sorted(
            (p.posicao, indice[str(p.inscricao_id)])
            for p in PosicaoNaOrdem.objects.filter(ato=ato, posicao__isnull=False)
        )
        dentro = sorted(
            indice[str(i.inscricao_id)]
            for i in ItemDoCorte.objects.filter(
                corte__edital=edital,
                corte__lista_id=lista,
                consequencia=ItemDoCorte.Consequencia.PROGREDIU,
            )
        )
        try:
            apurado = emitir_apuracao(
                actor=gestor,
                processo_id=edital.processo_id,
                edital_id=edital.id,
                perfil_id=PROFILE_ID,
                marco_id=MARCO,
                lista_id=lista,
                idempotency_key=f"{prefixo}-apuracao-{lista}",
                correlation_id="teste-095",
            )
            quantidades = (
                apurado["publicadas"],
                apurado["efetivas"],
                apurado["ocupadas"],
                apurado["faltando"],
            )
        except DomainError as erro:
            quantidades = ("recusada", erro.code)
        except apuracao.EmpateNaFronteiraDoAlvo:
            # O achado da R-002 da 095: na reservada, a recusa da fronteira da ampla escapa crua.
            quantidades = ("recusada", "crua")
        cedidas = sum(
            m.quantidade
            for m in MovimentoDeVaga.objects.filter(apuracao__edital=edital)
            if (str(m.origem_lista_id) if m.origem_lista_id else None) == lista
        )
        saida[lista] = {
            "ordem": ordem,
            "faixa": dentro,
            "quantidades": quantidades,
            "cede": cedidas,
        }
    versao = effective_version(edital_id=edital.id)
    try:
        pela_ampla = ocupacao.ocupantes_da_ampla(
            edital=edital, perfil_id=PROFILE_ID, marco_id=MARCO, versao=versao
        )
        saida["pela_ampla"] = sorted(indice[str(i)] for i in pela_ampla)
    except apuracao.EmpateNaFronteiraDoAlvo:
        saida["pela_ampla"] = "parou"
    return saida


def _lado_da_previa(edital, pontuada, inscricoes, especie, notas=NOTAS):
    """Os mesmos inscritos, em memória, pela `por_recorte` que `simular` chama."""
    conteudo = effective_version(edital_id=edital.id).content
    perfil = conteudo["profiles"][0]
    marco = next(m for m in perfil["classificationMilestones"] if str(m["id"]) == MARCO)
    etapas = {str(e["id"]): e for e in conteudo["stages"]}
    inscritos = []
    for n, inscricao in enumerate(inscricoes):
        nota = notas[n] if n < len(notas) else None
        inscritos.append(
            {
                "inscricao_id": str(inscricao.id),
                "protocolo": inscricao.protocolo,
                "nome": inscricao.nome,
                "identity_subject": inscricao.identity_subject,
                "modalidade_id": AUTODECLARACOES.get(n),
                "fatos": {},
                "resultados": []
                if nota is None
                else [
                    {
                        "id": f"r{n}",
                        "etapa_id": str(pontuada["id"]),
                        "pontuacao": Decimal(nota),
                        "consequencia": "HABILITADA",
                        "motivo": "",
                    }
                ],
            }
        )
    regra = faixa.normalizar(marco["cutRule"])
    vagas = {None: 3, MODALIDADE_PCD: 1, MODALIDADE_PPI: 2}
    comum = {
        "criterios": sorted(marco.get("tiebreakers") or [], key=lambda c: c.get("order") or 0),
        "regra": regra,
        "alvo": None,
        "suplentes": regra["surplusCount"],
    }
    ampla = previa._recorte(
        marco, etapas, inscritos, lista_id=None, vagas_do_recorte=vagas[None], **comum
    )
    ampla["vagas"] = vagas[None]
    r = previa.por_recorte(
        marco,
        etapas,
        inscritos,
        [{"lista_id": lista, "rotulo": str(lista), "vagas": vagas[lista]} for lista in RECORTES],
        ampla=ampla,
        apurar_recortes=lambda e: rodada_da_previa.rodada(e, especie=especie),
        **comum,
    )
    indice = {str(i.id): n for n, i in enumerate(inscricoes)}
    calculados = {None: ampla, **{x["lista_id"]: x for x in r["recortes"]}}
    apurados = r["ocupacao_por_recorte"]["recortes"]
    saida = {}
    for lista in RECORTES:
        calculado, apurado = calculados[lista], apurados[lista]
        if apurado["estado"] == rodada_da_previa.AVALIADA:
            quantidades = (
                apurado["publicadas"],
                apurado["efetivas"],
                apurado["ocupadas"],
                apurado["faltando"],
            )
        else:
            quantidades = ("nao-avaliada", apurado["estado"])
        saida[lista] = {
            "ordem": sorted((i["posicao"], indice[i["inscricao_id"]]) for i in calculado["ordem"]),
            "faixa": sorted(indice[i] for i in calculado["corte"].get("progrediram") or []),
            "quantidades": quantidades,
            "cede": apurado.get("cederia") or 0,
        }
    ampla_apurada = apurados[None]
    saida["pela_ampla"] = (
        sorted(indice[i] for i in ampla_apurada["ocupantes"])
        if ampla_apurada["estado"] == rodada_da_previa.AVALIADA
        else "parou"
    )
    return saida


@pytest.mark.parametrize(
    ("especie", "cedidas"),
    [
        (None, {MODALIDADE_PCD: 0, MODALIDADE_PPI: 0}),
        # DP-1: a faixa de cada reservada tomada por quem ocupa pela ampla, e o saldo cedido.
        (nomes.REVERSAO_POR_SALDO, {MODALIDADE_PCD: 1, MODALIDADE_PPI: 1}),
        # DP-2: "há quem ocupar" conta quem ocupa pela ampla, e nada é cedido.
        (nomes.REVERSAO_POR_ESGOTAMENTO, {MODALIDADE_PCD: 0, MODALIDADE_PPI: 0}),
    ],
    ids=["sem-reversao", "por-saldo", "por-esgotamento"],
)
def test_ordem_faixa_ocupacao_e_reversao_coincidem(montar, gestor, especie, cedidas):
    prefixo = f"previa-095-{especie or 'nada'}"
    edital, pontuada, inscricoes = montar(prefixo, especie=especie)

    oficial = _lado_oficial(edital, gestor, inscricoes, prefixo)
    da_previa = _lado_da_previa(edital, pontuada, inscricoes, especie)

    assert da_previa == oficial
    # E os números são os da tabela, e não só "iguais": quem ocupa pela ampla são os três
    # primeiros, dois deles autodeclarados.
    assert oficial["pela_ampla"] == [0, 1, 2]
    assert {lista: oficial[lista]["cede"] for lista in RECORTES[1:]} == cedidas


def test_empate_na_ultima_vaga_da_ampla(montar, gestor):
    """A ampla recusa, e as reservadas não apuram — no oficial, a recusa escapa crua (R-002)."""
    notas = ("95.0000", "90.0000", "85.0000", "85.0000", "75.0000", "70.0000", "65.0000", "62.0000")
    prefixo = "previa-095-empate"
    edital, pontuada, inscricoes = montar(prefixo, notas=notas)

    oficial = _lado_oficial(edital, gestor, inscricoes, prefixo)

    assert oficial[None]["quantidades"] == ("recusada", nomes.EMPATE_NA_FRONTEIRA_DO_ALVO)
    assert oficial[MODALIDADE_PPI]["quantidades"] == ("recusada", "crua")
    assert oficial["pela_ampla"] == "parou"

    da_previa = _lado_da_previa(edital, pontuada, inscricoes, None, notas)
    assert da_previa[None]["quantidades"] == ("nao-avaliada", rodada_da_previa.PAROU_NA_FRONTEIRA)
    for lista in RECORTES[1:]:
        assert da_previa[lista]["quantidades"] == (
            "nao-avaliada",
            rodada_da_previa.DEPENDE_DA_AMPLA,
        )
        assert da_previa[lista]["ordem"] == oficial[lista]["ordem"]
        assert da_previa[lista]["faixa"] == oficial[lista]["faixa"]


@pytest.mark.parametrize(
    ("modulo", "atributo", "desvio"),
    [
        (
            "processo_seletivo.ocupacao.domain.apuracao",
            "ocupantes_pela_ampla",
            lambda **_: set(),
        ),
        (
            "processo_seletivo.ocupacao.domain.reversao",
            "ha_quem_ocupar",
            lambda **_: False,
        ),
    ],
    ids=["ocupantes-da-ampla", "ha-quem-ocupar"],
)
def test_a_comparacao_acusa_o_caminho_oficial_alterado(
    montar, gestor, monkeypatch, modulo, atributo, desvio
):
    """A sentinela: com uma das decisões oficiais alterada só no caminho oficial, a igualdade cai.

    O desvio entra **depois** de a prévia calcular, e por isso alcança só o lado oficial.
    """
    especie = nomes.REVERSAO_POR_ESGOTAMENTO
    prefixo = f"previa-095-sentinela-{atributo}"
    edital, pontuada, inscricoes = montar(prefixo, especie=especie)
    da_previa = _lado_da_previa(edital, pontuada, inscricoes, especie)

    monkeypatch.setattr(f"{modulo}.{atributo}", desvio)
    oficial = _lado_oficial(edital, gestor, inscricoes, prefixo)

    assert da_previa != oficial
