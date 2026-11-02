"""A Etapa do desempate é a que o corte da própria ordem governa (114, FR-3562, D-007).

O caso típico do 14/2026: a ordem pela Prova decide quem vai à Entrevista, e o edital desempata
essa mesma ordem pela nota da Entrevista. A nota que separa os empatados só existe depois do corte
que os empatados decidem. A decisão do usuário sobre o valor ausente (D-004) é a que vale aqui: a
ordem sai sem a nota, e fica obsoleta quando ela chega.

Uma ordem sucessora emitida não prova que o percurso funciona. Cada teste o percorre inteiro —
ordem, corte, quem pode fazer a Entrevista, notas, obsolescência, sucessora, geração sucessora — e
pergunta, no fim, quem continua alcançado pela faixa.

```text
empate dentro da faixa                      funciona: os mesmos dois, e nada pendente
empate na fronteira, alvo estrito           o corte recusa; sem corte a regra dorme, e a
                                            Entrevista recebe todos os habilitados
empate na fronteira, admite excedente       os três entram; separados pela Entrevista, a
                                            geração sucessora deixa o terceiro de fora (D-007)
o mesmo, com a sucessora antes da 3ª nota   o terceiro sai da faixa antes de ser entrevistado,
                                            e fica impedido da Etapa que o desempataria (D-007)
```

Os dois últimos são o conflito de regra registrado na D-007: os testes prendem o comportamento de
hoje para que a decisão, quando vier, mude um teste nomeado — e não passe despercebida.
"""

import pytest

from processo_seletivo.classificacao.application.calculo import calcular_ordem
from processo_seletivo.classificacao.application.corte import estado_do_corte, geracao_vigente
from processo_seletivo.classificacao.application.emissao import (
    assinatura_da_proposta,
    emitir_ordem,
)
from processo_seletivo.classificacao.application.selectors import estado_do_marco
from processo_seletivo.classificacao.models import AtoDeOrdenacao, ItemDoCorte, PosicaoNaOrdem
from processo_seletivo.resultados.application.prontidao import (
    impedimento_do_corte,
    participacao,
)
from processo_seletivo.resultados.models import ResultadoEtapa
from processo_seletivo.shared.api.problems import DomainError
from tests.fixtures.corte import (
    CRITERIO_DA_ENTREVISTA,
    ENTREVISTA,
    MARCO,
    entrevistar,
    montar_cenario_do_corte,
    rascunho_com_desempate,
    regra,
)
from tests.fixtures.corte import emitir as emitir_corte
from tests.fixtures.edital import PROFILE_ID

pytestmark = pytest.mark.django_db(transaction=True)


@pytest.fixture
def montar(gestor, api_client, manager_headers, process_payload):
    """Prova com `pontuacoes`, ordem emitida, e o corte governando a Entrevista que desempata."""

    def _montar(prefixo, pontuacoes, *, desfecho):
        edital, _pontuada, inscricoes = montar_cenario_do_corte(
            gestor,
            api_client,
            manager_headers,
            process_payload,
            cut=regra(tieOutcome=desfecho),
            prefixo=prefixo,
            pontuacoes=pontuacoes,
            draft_factory=rascunho_com_desempate,
        )
        return edital, inscricoes

    return _montar


def _emitir_sucessora(edital, gestor, chave):
    return emitir_ordem(
        actor=gestor,
        processo_id=edital.processo_id,
        edital_id=edital.id,
        perfil_id=PROFILE_ID,
        marco_id=MARCO,
        idempotency_key=chave,
        correlation_id="teste-114",
        confirmacao_do_calculo=assinatura_da_proposta(
            calcular_ordem(edital=edital, perfil_id=PROFILE_ID, marco_id=MARCO),
            ato_vigente=_ato_vigente(edital),
        ),
        motivo="Notas da Entrevista consolidadas: o critério de desempate passou a ter valor.",
    )


def _ato_vigente(edital):
    return AtoDeOrdenacao.objects.get(edital=edital, marco_id=MARCO, sucessores__isnull=True)


def _ordem(edital):
    """`{inscricao_id: (posicao, empate residual)}` do ato vigente."""
    return {
        item.inscricao_id: (item.posicao, item.empate_residual)
        for item in PosicaoNaOrdem.objects.filter(ato=_ato_vigente(edital))
    }


def _alcancados(edital):
    """Quem pode fazer a Entrevista agora — a pergunta que a Mesa da Etapa faz."""
    participantes, _, _ = participacao(edital=edital, etapa_id=ENTREVISTA)
    return participantes


def _corte(edital):
    return estado_do_corte(edital=edital, perfil_id=PROFILE_ID, marco_id=MARCO)


def _suceder_o_corte(edital, gestor, chave):
    return emitir_corte(
        edital,
        gestor,
        chave=chave,
        motivo="A ordem que o corte leu foi sucedida pelas notas da Entrevista.",
        geracao=geracao_vigente(edital=edital, perfil_id=PROFILE_ID, marco_id=MARCO),
    )


def _com_nota_na_entrevista(edital):
    return set(
        ResultadoEtapa.vigentes.filter(edital=edital, etapa_id=ENTREVISTA).values_list(
            "inscricao_id", flat=True
        )
    )


def test_o_percurso_inteiro_com_o_empate_dentro_da_faixa(montar, gestor):
    """Alvo dois, e os dois empatados cabem nele: o desempate decide a ordem, e não quem entra."""
    edital, inscricoes = montar("a11-gov", ("80.0000", "80.0000", "70.0000"), desfecho="STRICT")
    a, b, c = inscricoes[:3]

    # 1. Sem nota na Entrevista ninguém tem o valor, e o critério não separa: os dois dividem a 1ª.
    assert _ordem(edital)[a.id] == _ordem(edital)[b.id] == (1, True)
    assert _ordem(edital)[c.id] == (3, False)

    # 2. O empate não atravessa a fronteira do alvo, e o corte sai. A Entrevista é só da faixa.
    emitir_corte(edital, gestor, chave="a11-gov-corte")
    assert _alcancados(edital) == {a.id, b.id}
    with pytest.raises(DomainError) as fora:
        entrevistar(edital, gestor, [(c, "95.0000")], chave="a11-gov-fora")
    assert "fora do corte" in fora.value.detail

    # 3. As notas chegam. A ordem fica para trás; o corte ainda não — a ordem que ele leu é a
    #    vigente —, e nada segura a Entrevista.
    entrevistar(edital, gestor, [(a, "70.0000"), (b, "90.0000")], chave="a11-gov-entrevista")
    assert estado_do_marco(edital=edital, marco_id=MARCO)["obsoleto"]
    assert not _corte(edital)["obsoleto"]
    assert impedimento_do_corte(edital, ENTREVISTA) is None

    # 4. A sucessora: a Entrevista separa, e a nota final dos dois continua a da Prova.
    _emitir_sucessora(edital, gestor, "a11-gov-sucessora")
    assert _ordem(edital)[b.id] == (1, False)
    assert _ordem(edital)[a.id] == (2, False)
    gravadas = PosicaoNaOrdem.objects.filter(ato=_ato_vigente(edital), inscricao__in=[a, b])
    assert {item.pontuacao_combinada for item in gravadas} == {80}
    assert gravadas.get(inscricao=b).desempate[0]["criterionId"] == CRITERIO_DA_ENTREVISTA
    assert gravadas.get(inscricao=b).desempate[0]["separated"]

    # 5. O corte fica para trás pela sucessão da ordem, e segura trabalho novo na Entrevista.
    assert {item["tipo"] for item in _corte(edital)["causas"]} == {"ordem_sucedida"}
    assert impedimento_do_corte(edital, ENTREVISTA) is not None

    # 6. A geração sucessora alcança os mesmos dois, e nada mais fica pendente.
    _suceder_o_corte(edital, gestor, "a11-gov-corte-2")
    assert _alcancados(edital) == {a.id, b.id}
    assert not _corte(edital)["obsoleto"]
    assert impedimento_do_corte(edital, ENTREVISTA) is None
    assert not estado_do_marco(edital=edital, marco_id=MARCO)["obsoleto"]


def test_alvo_estrito_com_empate_na_fronteira_o_corte_recusa_e_a_regra_dorme(montar, gestor):
    """Três empatados para duas posições: o corte não escolhe, e sem corte a Entrevista é de todos.

    Ninguém fica impedido: enquanto nenhum corte foi emitido, a Etapa governada recebe todos os
    habilitados — é a dormência da `014`. A Entrevista desfaz o empate, e só então o corte sai. O
    custo é o que a D-007 registra: a restrição "só a faixa vai à Entrevista" não se aplica a esses
    três, porque a faixa só existe depois da nota que eles precisam tirar.
    """
    edital, inscricoes = montar("a11-estrito", ("80.0000", "80.0000", "80.0000"), desfecho="STRICT")
    a, b, c = inscricoes[:3]
    assert {_ordem(edital)[item.id] for item in (a, b, c)} == {(1, True)}

    with pytest.raises(DomainError) as recusa:
        emitir_corte(edital, gestor, chave="a11-estrito-corte")
    assert recusa.value.code == "empate_atravessa_o_corte"
    assert {a.id, b.id, c.id} <= _alcancados(edital)

    entrevistar(
        edital,
        gestor,
        [(a, "90.0000"), (b, "80.0000"), (c, "70.0000")],
        chave="a11-estrito-entrevista",
    )
    _emitir_sucessora(edital, gestor, "a11-estrito-sucessora")
    assert [_ordem(edital)[item.id] for item in (a, b, c)] == [(1, False), (2, False), (3, False)]

    emitir_corte(edital, gestor, chave="a11-estrito-corte-2")
    assert _alcancados(edital) == {a.id, b.id}
    # O terceiro fez a Entrevista e ficou fora pela nota dela — que é o que o edital diz.
    assert c.id in _com_nota_na_entrevista(edital)


def test_excedente_por_empate_entrevistado_sai_na_geracao_sucessora(montar, gestor):
    """D-007 — o conflito, com todas as notas lançadas antes da sucessora.

    O edital admite o excedente no empate da fronteira: os três entram na faixa e fazem a
    Entrevista. A Entrevista os separa, a ordem sucessora já não tem empate, e a geração sucessora
    — que o próprio sistema exige, porque a faixa obsoleta segura trabalho novo — aplica o alvo de
    dois à ordem nova. O terceiro, que entrou pela regra do edital e foi entrevistado, sai da faixa.
    """
    edital, inscricoes = montar(
        "a11-exced", ("80.0000", "80.0000", "80.0000"), desfecho="ADMITS_SURPLUS"
    )
    a, b, c = inscricoes[:3]

    emitir_corte(edital, gestor, chave="a11-exced-corte")
    assert _alcancados(edital) == {a.id, b.id, c.id}
    assert ItemDoCorte.objects.filter(excedente_por_empate=True).count() == 1

    entrevistar(
        edital,
        gestor,
        [(a, "90.0000"), (b, "80.0000"), (c, "70.0000")],
        chave="a11-exced-entrevista",
    )
    _emitir_sucessora(edital, gestor, "a11-exced-sucessora")
    assert impedimento_do_corte(edital, ENTREVISTA) is not None

    _suceder_o_corte(edital, gestor, "a11-exced-corte-2")
    assert _alcancados(edital) == {a.id, b.id}
    assert c.id in _com_nota_na_entrevista(edital)


def test_sucessora_antes_da_ultima_nota_deixa_o_empatado_sem_a_entrevista(montar, gestor):
    """D-007 — o conflito na forma em que alguém fica impedido da Etapa que o desempataria.

    A ordem fica obsoleta com a primeira nota consolidada, e a tela oferece a sucessora. Emitida
    antes da nota do terceiro, o "quando o valor falta" publicado — `ULTIMO_NO_CRITERIO` — o põe
    atrás dos dois já entrevistados; a faixa obsoleta segura a Entrevista dele, e a geração
    sucessora o deixa fora. Ele não chega a fazer a Etapa cuja nota poderia tê-lo posto à frente.
    """
    edital, inscricoes = montar(
        "a11-parcial", ("80.0000", "80.0000", "80.0000"), desfecho="ADMITS_SURPLUS"
    )
    a, b, c = inscricoes[:3]
    emitir_corte(edital, gestor, chave="a11-parcial-corte")
    assert _alcancados(edital) == {a.id, b.id, c.id}

    entrevistar(edital, gestor, [(a, "70.0000"), (b, "65.0000")], chave="a11-parcial-1")
    assert estado_do_marco(edital=edital, marco_id=MARCO)["obsoleto"]
    _emitir_sucessora(edital, gestor, "a11-parcial-sucessora")
    assert _ordem(edital)[c.id] == (3, False)

    # A faixa obsoleta segura trabalho novo — a Entrevista do terceiro inclusive.
    assert impedimento_do_corte(edital, ENTREVISTA) is not None

    _suceder_o_corte(edital, gestor, "a11-parcial-corte-2")
    assert _alcancados(edital) == {a.id, b.id}
    assert c.id not in _com_nota_na_entrevista(edital)
    with pytest.raises(DomainError) as fora:
        entrevistar(edital, gestor, [(c, "95.0000")], chave="a11-parcial-2")
    assert "fora do corte" in fora.value.detail
