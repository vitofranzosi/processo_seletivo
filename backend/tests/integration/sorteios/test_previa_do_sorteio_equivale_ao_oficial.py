"""A prévia do sorteio contra o caminho oficial, sobre os mesmos participantes (098, T009, R-009).

O caminho oficial corre inteiro, pelos comandos: a relação de cada recorte é publicada, a ocorrência
é observada pela `FonteDeTeste` com o material fictício, o sorteio de cada recorte é constituído, e
o corte e a apuração de cada recorte são emitidos, com a reversão que o Perfil publicou. A prévia
calcula em memória, pela mesma `simular_sorteio` que a interface vai chamar, com os mesmos
participantes, o mesmo material e **os resumos das relações oficiais injetados** — a única entrada
que a prévia não tem como saber, e que só muda *qual* ordem sai (R-002). Ordem, faixa, quem ocupa
pela ampla, as quatro quantidades e o que cada reservada cede precisam coincidir.

**O resumo da relação oficial cobre o `id` dela, que nasce sorteado**: a ordem muda de uma execução
para outra, e o teste não fixa números — fixa a igualdade. É também o que o torna mais forte que uma
tabela: cada execução é um caso novo.

O corte declara não governar Etapa (`NONE`): quem progrediu é quem conta como habilitado, que é a
hipótese da prévia (FR-2320 da `095`), e o caminho oficial a cumpre sem Resultado nenhum a ler.

A sentinela, no fim, prova que a comparação morde.
"""

import pytest

from processo_seletivo.classificacao.application.corte import calcular_corte
from processo_seletivo.classificacao.application.emissao_do_corte import (
    assinatura_da_proposta,
    emitir_corte,
)
from processo_seletivo.classificacao.application.selectors import ato_vigente
from processo_seletivo.classificacao.models import ItemDoCorte, PosicaoNaOrdem
from processo_seletivo.ocupacao.application import selectors as ocupacao
from processo_seletivo.ocupacao.application.emissao import emitir_apuracao
from processo_seletivo.ocupacao.domain import nomes, rodada_da_previa
from processo_seletivo.ocupacao.models import MovimentoDeVaga
from processo_seletivo.publicacoes.application.selectors import effective_version
from processo_seletivo.shared.api.problems import DomainError
from processo_seletivo.sorteios.application import simulacao as aplicacao
from processo_seletivo.sorteios.application.ocorrencia import observar_ocorrencia
from processo_seletivo.sorteios.application.relacao import publicar_relacao
from processo_seletivo.sorteios.application.sorteio import constituir_sorteio
from processo_seletivo.sorteios.domain.simulacao import CandidatoFicticio
from processo_seletivo.sorteios.infrastructure.fontes.loteria_federal import FonteDeTeste
from processo_seletivo.sorteios.models import RelacaoDeHabilitados
from tests.fixtures.corte import MARCO
from tests.fixtures.edital import PROFILE_ID
from tests.fixtures.recortes import (
    MODALIDADE_PCD,
    MODALIDADE_PPI,
    declarar,
    rascunho_7_1_2,
    regra_do_quadro,
)
from tests.fixtures.sorteio import METODO, presidente

pytestmark = [pytest.mark.integration, pytest.mark.django_db(transaction=True)]

#: O material fictício, no formato da Loteria Federal (D-007), que a `FonteDeTeste` devolve.
MATERIAL = "048213 771904 302558 919007 116482"
#: 4 vagas na ampla, 1 na PcD, 2 na PPI; doze inscritos, cinco autodeclarados entremeados.
VAGAS = {None: 4, MODALIDADE_PCD: 1, MODALIDADE_PPI: 2}
AUTODECLARACOES = {
    1: MODALIDADE_PPI,
    4: MODALIDADE_PPI,
    7: MODALIDADE_PPI,
    2: MODALIDADE_PCD,
    9: MODALIDADE_PCD,
}
INSCRITOS = 12
RECORTES = (None, MODALIDADE_PCD, MODALIDADE_PPI)


#: O alvo fixo com suplentes: a regra que vale igual em toda lista, e que a `095` achou ser o caso
#: em que a prévia e o oficial mais podiam divergir. Acrescentado pela revisão do #327.
FIXO_COM_SUPLENTES = regra_do_quadro(
    targetKind="FIXED", targetCount=3, surplusCount=1, governedStage="NONE"
)


def _rascunho(especie, corte=None):
    """O 7/1/2 da `034` com outro quadro, e o marco dele trocado para sorteio."""
    base, _ = rascunho_7_1_2(
        cut=corte or regra_do_quadro(governedStage="NONE"),
        geral=VAGAS[None],
        pcd=VAGAS[MODALIDADE_PCD],
        ppi=VAGAS[MODALIDADE_PPI],
    )
    perfil = base["profiles"][0]
    marco = perfil["classificationMilestones"][0]
    marco.update(orderProduction="POR_SORTEIO", drawMethod=METODO, tiebreakers=[])
    if especie:
        perfil["vacancyReversion"] = {"kind": especie}
    return base


@pytest.fixture
def montar(gestor, api_client, manager_headers, process_payload, monkeypatch):
    from processo_seletivo.comissoes.domain.funcoes import Funcao
    from tests.fixtures.comissao import constituir, inscrever
    from tests.fixtures.publicacao import publish_original

    monkeypatch.setitem(FonteDeTeste.MATERIAL, METODO["occurrence"], MATERIAL)

    def _montar(prefixo, *, especie=None, autodeclaracoes=AUTODECLARACOES, corte=None):
        edital = publish_original(
            api_client, manager_headers, process_payload, draft=_rascunho(especie, corte)
        )
        constituir(gestor, edital.processo, [("maria", Funcao.PRESIDENTE)], prefixo=prefixo)
        inscricoes = inscrever(edital, INSCRITOS, primeiro=981)
        for indice, modalidade in autodeclaracoes.items():
            declarar(inscricoes[indice], modalidade)
        return edital, inscricoes

    return _montar


def _sortear(edital, prefixo):
    """As relações primeiro, a ocorrência depois, e um sorteio por relação.

    A lista sem inscrito nenhum não tem relação: `publicar_relacao` a recusa, e é esse o
    comportamento que a prévia reproduz (FR-2489).
    """
    relacoes = {}
    for lista in RECORTES:
        try:
            relacoes[lista] = publicar_relacao(
                actor=presidente(),
                processo_id=edital.processo_id,
                edital_id=edital.id,
                perfil_id=PROFILE_ID,
                marco_id=MARCO,
                lista_id=lista,
                idempotency_key=f"{prefixo}-relacao-{lista}",
                correlation_id="teste-098",
            )["relacao"]
        except DomainError as recusa:
            assert recusa.code == "relation_would_be_empty"
    ocorrencia = observar_ocorrencia(
        actor=presidente(),
        processo_id=edital.processo_id,
        fonte=METODO["source"],
        referencia=METODO["occurrence"],
        idempotency_key=f"{prefixo}-ocorrencia",
        correlation_id="teste-098",
        fonte_externa=FonteDeTeste(),
    )["ocorrencia"]
    for lista, relacao_id in relacoes.items():
        constituir_sorteio(
            actor=presidente(),
            processo_id=edital.processo_id,
            edital_id=edital.id,
            relacao_id=relacao_id,
            ocorrencia_id=ocorrencia,
            idempotency_key=f"{prefixo}-sorteio-{lista}",
            correlation_id="teste-098",
        )
    return {
        lista: RelacaoDeHabilitados.objects.get(pk=relacao_id).resumo
        for lista, relacao_id in relacoes.items()
    }


def _lado_oficial(edital, gestor, inscricoes, prefixo):
    indice = {str(i.id): n for n, i in enumerate(inscricoes)}
    for lista in RECORTES:
        try:
            proposta = calcular_corte(
                edital=edital, perfil_id=PROFILE_ID, marco_id=MARCO, lista_id=lista
            )
        except DomainError as recusa:
            # Sem relação não há ordem, e sem ordem o corte recusa — `sem_ato_vigente`.
            assert recusa.code == "sem_ato_vigente"
            continue
        emitir_corte(
            actor=gestor,
            processo_id=edital.processo_id,
            edital_id=edital.id,
            perfil_id=PROFILE_ID,
            marco_id=MARCO,
            lista_id=lista,
            idempotency_key=f"{prefixo}-corte-{lista}",
            correlation_id="teste-098",
            confirmacao_do_calculo=assinatura_da_proposta(proposta),
        )
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
                correlation_id="teste-098",
            )
            quantidades = (
                apurado["publicadas"],
                apurado["efetivas"],
                apurado["ocupadas"],
                apurado["faltando"],
            )
        except DomainError as recusa:
            # A recusa, nos termos da prévia: a apuração não sai, e nada é cedido.
            assert recusa.code == "ordem_nao_vigente"
            quantidades = ("nao-avaliada", rodada_da_previa.CORTE_NAO_EMITIDO)
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
    saida["pela_ampla"] = sorted(
        indice[str(i)]
        for i in ocupacao.ocupantes_da_ampla(
            edital=edital, perfil_id=PROFILE_ID, marco_id=MARCO, versao=versao
        )
    )
    return saida


def _lado_da_previa(
    edital,
    inscricoes,
    especie,
    resumos,
    *,
    metodo=None,
    material=MATERIAL,
    autodeclaracoes=AUTODECLARACOES,
):
    """Os mesmos participantes, em memória, na ordem de protocolo — a da relação oficial."""
    conteudo = effective_version(edital_id=edital.id).content
    marco = next(
        m for m in conteudo["profiles"][0]["classificationMilestones"] if str(m["id"]) == MARCO
    )
    candidatos = [
        CandidatoFicticio(
            id=str(inscricao.id),
            nome=inscricao.nome,
            lista_id=autodeclaracoes.get(n),
        )
        for n, inscricao in sorted(enumerate(inscricoes), key=lambda par: par[1].protocolo)
    ]
    previa = aplicacao.simular_sorteio(
        marco,
        perfil_id=PROFILE_ID,
        metodo=metodo if metodo is not None else METODO,
        material=material,
        candidatos=candidatos,
        recortes=[
            {"lista_id": lista, "rotulo": str(lista), "vagas": VAGAS[lista]} for lista in RECORTES
        ],
        apurar_recortes=lambda e: rodada_da_previa.rodada(e, especie=especie),
        resumos_oficiais=resumos,
    )
    indice = {str(i.id): n for n, i in enumerate(inscricoes)}
    apurados = previa["ocupacao_por_recorte"]["recortes"]
    saida = {}
    for calculado in previa["recortes"]:
        lista, apurado = calculado["lista_id"], apurados[calculado["lista_id"]]
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
            "faixa": sorted(indice[i] for i in calculado["corte"]["progrediram"]),
            "quantidades": quantidades,
            "cede": apurado.get("cederia") or 0,
        }
    saida["pela_ampla"] = sorted(indice[i] for i in apurados[None]["ocupantes"])
    return saida


@pytest.mark.parametrize(
    "especie",
    [None, nomes.REVERSAO_POR_SALDO, nomes.REVERSAO_POR_ESGOTAMENTO],
    ids=["sem-reversao", "por-saldo", "por-esgotamento"],
)
def test_ordem_faixa_ocupacao_e_reversao_coincidem(montar, gestor, especie):
    prefixo = f"previa-098-{especie or 'nada'}"
    edital, inscricoes = montar(prefixo, especie=especie)
    resumos = _sortear(edital, prefixo)

    da_previa = _lado_da_previa(edital, inscricoes, especie, resumos)
    oficial = _lado_oficial(edital, gestor, inscricoes, prefixo)

    assert da_previa == oficial
    # E não é igualdade de vazio: cada recorte sorteou todos os seus, e a faixa tem as vagas dele.
    assert [len(oficial[lista]["ordem"]) for lista in RECORTES] == [INSCRITOS, 2, 3]
    assert [len(oficial[lista]["faixa"]) for lista in RECORTES] == [4, 1, 2]


@pytest.mark.parametrize(
    "especie", [None, nomes.REVERSAO_POR_SALDO], ids=["sem-reversao", "por-saldo"]
)
def test_alvo_fixo_com_suplentes_coincide(montar, gestor, especie):
    """O alvo fixo vale em toda lista, e o suplente alonga a faixa sem ocupar vaga."""
    prefixo = f"previa-098-fixo-{especie or 'nada'}"
    edital, inscricoes = montar(prefixo, especie=especie, corte=FIXO_COM_SUPLENTES)
    resumos = _sortear(edital, prefixo)

    da_previa = _lado_da_previa(edital, inscricoes, especie, resumos)
    oficial = _lado_oficial(edital, gestor, inscricoes, prefixo)

    assert da_previa == oficial
    # Alvo 3 + 1 suplente em toda lista: a ampla corta em 4, a PcD (2) e a PPI (3) levam todos.
    assert [len(oficial[lista]["faixa"]) for lista in RECORTES] == [4, 2, 3]


def test_reservada_sem_inscritos_coincide(montar, gestor):
    """A PcD sem ninguém: a relação dela é vazia nos dois lados, e as vagas ficam sem ocupante."""
    sem_pcd = {n: m for n, m in AUTODECLARACOES.items() if m != MODALIDADE_PCD}
    prefixo = "previa-098-pcd-vazia"
    edital, inscricoes = montar(prefixo, especie=nomes.REVERSAO_POR_SALDO, autodeclaracoes=sem_pcd)
    resumos = _sortear(edital, prefixo)

    da_previa = _lado_da_previa(
        edital, inscricoes, nomes.REVERSAO_POR_SALDO, resumos, autodeclaracoes=sem_pcd
    )
    oficial = _lado_oficial(edital, gestor, inscricoes, prefixo)

    assert da_previa == oficial
    # A PcD vazia não é sorteada nem apurada, e por isso não cede vaga nem sob "por saldo": é o
    # comportamento atual, registrado em `doc/achado-reservada-vazia-nao-reverte.md`.
    assert oficial[MODALIDADE_PCD] == {
        "ordem": [],
        "faixa": [],
        "quantidades": ("nao-avaliada", rodada_da_previa.CORTE_NAO_EMITIDO),
        "cede": 0,
    }


def test_a_comparacao_acusa_a_semente_trocada_so_na_previa(montar, gestor):
    """A sentinela: com um dígito do material trocado só na prévia, a igualdade cai.

    Trocar a regra de normalização não serviria: com material no formato da Loteria Federal,
    `DIGITOS_EM_SEQUENCIA` e `TEXTO_LITERAL` dão a mesma semente — medido ao escrever este teste.
    """
    prefixo = "previa-098-sentinela"
    edital, inscricoes = montar(prefixo)
    resumos = _sortear(edital, prefixo)

    da_previa = _lado_da_previa(edital, inscricoes, None, resumos, material=MATERIAL[:-1] + "3")
    oficial = _lado_oficial(edital, gestor, inscricoes, prefixo)

    assert da_previa != oficial
