"""As derivações da visão institucional, lidas sem requisição e sem banco (040).

**Sem banco de propósito.** `linha_do_edital` e `_consolidar` recebem o conteúdo publicado e as
contagens já lidas — é o que permite exercitar a gramática da ausência, a razão recortada e as
marcas sem pagar o custo de publicar um Edital por caso. O que precisa de banco está nos testes de
interface, onde a jornada é a coisa medida.

Os cenários realizados aqui são os `T-01` a `T-10` da §18 da spec.
"""

from dataclasses import dataclass
from datetime import timedelta
from decimal import Decimal

from django.utils import timezone

from processo_seletivo.interface import visao_geral as visao


@dataclass(frozen=True)
class _Processo:
    id: int
    title: str = "Processo"


@dataclass(frozen=True)
class _Edital:
    pk: int
    processo_id: int
    number: str = "1"
    year: int = 2026
    status: str = "PUBLICADO"

    @property
    def processo(self):
        return _Processo(self.processo_id)


def edital(pk=1, processo=1, **extra):
    return _Edital(pk=pk, processo_id=processo, **extra)


def perfil(identidade, vagas, *, reserva="NONE"):
    return {"id": identidade, "immediateVacancies": vagas, "reserveType": reserva}


def conteudo(perfis, *, inicio=None, fim=None, designado=True):
    evento = {
        "id": "ev-1",
        "description": "Inscrições",
        "startAt": (inicio or timezone.now() - timedelta(days=30)).isoformat(),
        "endAt": None if fim is None else fim.isoformat(),
        "order": 1,
        "isRegistrationPeriod": designado,
    }
    return {"profiles": perfis, "schedule": [evento]}


def submetidas(**por_perfil):
    """A contagem de um Edital, na forma que `contagens_por_edital` devolve.

    **Rascunho é dicionário por Perfil desde a `041`** (`FR-610`): a consulta já trazia
    `profile_id` em cada linha e o valor era descartado num contador único.
    """
    return {"submetidas": dict(por_perfil), "rascunhos": {}}


AGORA = timezone.now()
ENCERRADO_ONTEM = AGORA - timedelta(days=1)
FECHA_AMANHA = AGORA + timedelta(days=1)


# ---------------------------------------------------------------------------
# T-01 · T-02 · T-03 — o que o conteúdo publicado diz sobre vagas
# ---------------------------------------------------------------------------


def test_t01_edital_em_elaboracao_tem_vagas_e_razao_ausentes_e_nunca_zero():
    linha = visao.linha_do_edital(edital(), None, submetidas(), AGORA)

    assert not linha.vagas.existe and linha.vagas.valor is None
    assert linha.vagas.ausencia.especie == visao.NAO_PUBLICADO
    assert not linha.razao.existe
    # A contagem de inscrições **existe** mesmo sem conteúdo publicado: ela não depende dele.
    assert linha.submetidas.valor == 0


def test_t02_perfil_so_de_cadastro_reserva_tem_vagas_zero_e_razao_nao_aplicavel():
    publicado = conteudo([perfil("p1", 0, reserva="UNLIMITED")], fim=ENCERRADO_ONTEM)

    linha = visao.linha_do_edital(edital(), publicado, submetidas(p1=200), AGORA)

    # **Zero legítimo**: a fonte publicou `0`, e apagá-lo esconderia a oferta que existe.
    assert linha.vagas.existe and linha.vagas.valor == 0
    # `tem_reserva` saiu na `041`: a espécie mora no Perfil, e as três se distinguem.
    assert linha.perfis[0].reserva.especie == visao.RESERVA_ILIMITADA
    # **Ausência, e não zero nem infinito**: não há denominador.
    assert not linha.razao.existe
    assert linha.razao.ausencia.especie == visao.NAO_APLICAVEL
    assert linha.submetidas.valor == 200


def test_t03_dois_perfis_com_vaga_somam_vagas_e_demanda():
    publicado = conteudo([perfil("p1", 30), perfil("p2", 10)], fim=ENCERRADO_ONTEM)

    linha = visao.linha_do_edital(edital(), publicado, submetidas(p1=60, p2=20), AGORA)

    assert linha.vagas.valor == 40
    assert linha.submetidas.valor == 80
    assert linha.razao.valor == Decimal("2.0")
    assert linha.populacao_da_razao == ""


# ---------------------------------------------------------------------------
# T-03b · T-03c — o Edital misto, que é onde a razão fica falsa sem o recorte
# ---------------------------------------------------------------------------


def test_t03b_edital_misto_usa_so_a_demanda_do_perfil_com_vaga():
    publicado = conteudo(
        [perfil("com-vaga", 40), perfil("so-reserva", 0, reserva="UNLIMITED")],
        fim=ENCERRADO_ONTEM,
    )

    linha = visao.linha_do_edital(
        edital(), publicado, submetidas(**{"com-vaga": 80, "so-reserva": 200}), AGORA
    )

    # A demanda total continua sendo a do Edital inteiro.
    assert linha.submetidas.valor == 280
    # E a razão é 80 ÷ 40 — **nunca** 280 ÷ 40, que seria 7,0: aritmeticamente correto e
    # institucionalmente falso.
    assert linha.razao.valor == Decimal("2.0")
    assert "80" in linha.populacao_da_razao


def test_t03c_o_consolidado_concorda_com_a_linha_no_edital_misto():
    um = edital(pk=1)
    publicado = conteudo(
        [perfil("com-vaga", 40), perfil("so-reserva", 0, reserva="UNLIMITED")],
        fim=ENCERRADO_ONTEM,
    )
    contagens = {1: submetidas(**{"com-vaga": 80, "so-reserva": 200})}
    linha = visao.linha_do_edital(um, publicado, contagens[1], AGORA)

    consolidado = visao._consolidar([linha], {1: publicado}, contagens)

    assert consolidado.submetidas.valor == 280
    assert consolidado.razao.valor == linha.razao.valor == Decimal("2.0")
    assert consolidado.vagas.valor == 40
    assert consolidado.perfis_com_vaga == 1


# ---------------------------------------------------------------------------
# T-04 · T-05 · T-06 — demanda, parcialidade e o que a contagem conta
# ---------------------------------------------------------------------------


def test_t04_periodo_aberto_marca_submetidas_como_parcial_e_nao_soma_rascunhos():
    publicado = conteudo([perfil("p1", 10)], fim=FECHA_AMANHA)
    contagem = {"submetidas": {"p1": 40}, "rascunhos": {"p1": 12}}

    linha = visao.linha_do_edital(edital(), publicado, contagem, AGORA)

    assert linha.submetidas.valor == 40 and linha.submetidas.parcial
    assert linha.submetidas.porque
    assert linha.em_preenchimento.valor == 12
    # A soma 52 não existe em lugar nenhum: são duas grandezas.
    assert linha.submetidas.valor + linha.em_preenchimento.valor == 52


def test_fr595_a_razao_do_edital_e_do_perfil_tambem_nascem_parciais():
    """A razão muda enquanto chegam inscrições, e por isso é parcial tanto quanto a contagem.

    O modelo já dizia isto, e a asserção sobre ele sempre passou. A **tela** é que descartava a
    marca, mostrando razão de período aberto como se fosse número fechado — exatamente a leitura
    que a `FR-595` existe para impedir. O par deste teste vive em `tests/interface`, e é lá que o
    defeito aparecia.
    """
    publicado = conteudo([perfil("p1", 20)], fim=FECHA_AMANHA)
    contagem = {"submetidas": {"p1": 40}, "rascunhos": {}}

    linha = visao.linha_do_edital(edital(), publicado, contagem, AGORA)

    assert linha.razao.parcial
    assert linha.perfis[0].razao.parcial


def test_t05_periodo_encerrado_sem_ninguem_produz_zero_e_marca_de_atencao():
    publicado = conteudo([perfil("p1", 10)], fim=ENCERRADO_ONTEM)

    linha = visao.linha_do_edital(edital(), publicado, submetidas(), AGORA)

    assert linha.submetidas.existe and linha.submetidas.valor == 0
    especies = {marca.especie for marca in linha.marcas}
    assert visao.SEM_PROCURA in especies
    assert visao.DEMANDA_ABAIXO_DA_OFERTA in especies


def test_t05b_periodo_aberto_sem_ninguem_nao_produz_marca():
    publicado = conteudo([perfil("p1", 10)], fim=FECHA_AMANHA)

    linha = visao.linha_do_edital(edital(), publicado, submetidas(), AGORA)

    assert linha.submetidas.valor == 0
    assert linha.marcas == ()


def test_t06_duas_inscricoes_da_mesma_pessoa_contam_duas():
    """A unicidade é por **Perfil**: a mesma pessoa cabe duas vezes no mesmo Edital.

    A página conta **inscrições**, e por isso o número é 2. Chamá-lo de "candidatos" seria outra
    grandeza, com outra fonte e outra confiabilidade (`FR-593`).
    """
    publicado = conteudo([perfil("p1", 5), perfil("p2", 5)], fim=ENCERRADO_ONTEM)

    linha = visao.linha_do_edital(edital(), publicado, submetidas(p1=1, p2=1), AGORA)

    assert linha.submetidas.valor == 2


# ---------------------------------------------------------------------------
# T-07 — a Retificação move o número, porque a fonte é a versão vigente
# ---------------------------------------------------------------------------


def test_t07_as_vagas_sao_as_da_versao_vigente():
    original = conteudo([perfil("p1", 30)], fim=ENCERRADO_ONTEM)
    retificado = conteudo([perfil("p1", 35)], fim=ENCERRADO_ONTEM)

    assert visao.vagas_do_conteudo(original).total == 30
    assert visao.vagas_do_conteudo(retificado).total == 35


# ---------------------------------------------------------------------------
# T-08 — o consolidado declara os três, e é o cenário que faltava
# ---------------------------------------------------------------------------


def test_t08_o_consolidado_declara_publicados_parciais_e_fora_da_razao():
    aberto = edital(pk=1, processo=1)
    encerrado = edital(pk=2, processo=1)
    so_reserva = edital(pk=3, processo=2)
    elaboracao = edital(pk=4, processo=2, status="EM_ELABORACAO")

    conteudos = {
        1: conteudo([perfil("a", 10)], fim=FECHA_AMANHA),
        2: conteudo([perfil("b", 20)], fim=ENCERRADO_ONTEM),
        3: conteudo([perfil("c", 0, reserva="UNLIMITED")], fim=ENCERRADO_ONTEM),
        4: None,
    }
    contagens = {1: submetidas(a=5), 2: submetidas(b=60), 3: submetidas(c=90), 4: submetidas()}
    linhas = [
        visao.linha_do_edital(e, conteudos[e.pk], contagens[e.pk], AGORA)
        for e in (aberto, encerrado, so_reserva, elaboracao)
    ]

    consolidado = visao._consolidar(linhas, conteudos, contagens)

    assert consolidado.editais == 4
    assert consolidado.processos == 2
    # Quantos publicaram conteúdo (`FR-585`).
    assert consolidado.editais_publicados == 3
    # Quantos somandos são parciais (`FR-595`).
    assert consolidado.parciais == 1
    # Quantos ficaram fora da razão (`FR-590`) — o sem conteúdo e o sem denominador.
    assert consolidado.fora_da_razao == 2
    # E a razão é `Σ numerador ÷ Σ vagas`, nunca a média das razões.
    assert consolidado.razao.valor == visao._razao(65, 30)
    assert consolidado.submetidas.valor == 155


def test_t08b_recorte_inteiro_sem_denominador_nao_inventa_razao():
    um = edital(pk=1)
    publicado = conteudo([perfil("p1", 0, reserva="UNLIMITED")], fim=ENCERRADO_ONTEM)
    contagens = {1: submetidas(p1=10)}
    linha = visao.linha_do_edital(um, publicado, contagens[1], AGORA)

    consolidado = visao._consolidar([linha], {1: publicado}, contagens)

    assert not consolidado.razao.existe
    assert consolidado.razao.ausencia.especie == visao.NAO_APLICAVEL
    assert consolidado.fora_da_razao == 1


# ---------------------------------------------------------------------------
# T-09 — a ausência vai ao fim nos dois sentidos
# ---------------------------------------------------------------------------


def _linha_com_razao(pk, valor):
    """Uma linha com a razão pedida — e com **vagas e submetidas distintas por linha**.

    As três grandezas variam de propósito: com todas as linhas empatadas numa coluna, ordenar por
    ela devolve a mesma lista nos dois sentidos — `sorted` é estável, e corretamente — e um caso
    que afirmasse a diferença estaria medindo o fixture, não o produto.
    """
    vagas = 10 * pk
    if valor is None:
        publicado = conteudo([perfil("p", 0, reserva="UNLIMITED")], fim=ENCERRADO_ONTEM)
        return visao.linha_do_edital(edital(pk=pk), publicado, submetidas(p=1), AGORA)
    publicado = conteudo([perfil("p", vagas)], fim=ENCERRADO_ONTEM)
    return visao.linha_do_edital(edital(pk=pk), publicado, submetidas(p=valor * vagas), AGORA)


def test_t09_a_ausencia_fica_ao_fim_nos_dois_sentidos():
    linhas = [_linha_com_razao(1, 3), _linha_com_razao(2, None), _linha_com_razao(3, 1)]
    anos = (2026,)

    desc = visao._ordenar(
        linhas, visao.Recorte(ano=2026, ordem="razao", sentido="desc", anos_disponiveis=anos)
    )
    asc = visao._ordenar(
        linhas, visao.Recorte(ano=2026, ordem="razao", sentido="asc", anos_disponiveis=anos)
    )

    assert [linha.edital.pk for linha in desc] == [1, 3, 2]
    assert [linha.edital.pk for linha in asc] == [3, 1, 2]
    # A ausente é a última nas duas — `reverse=True` a teria posto em primeiro numa delas.
    assert desc[-1].edital.pk == asc[-1].edital.pk == 2


def test_o_sentido_vale_tambem_para_a_ordem_padrao():
    """O controle de sentido **não fazia nada** com "Mais recentes" escolhido.

    `_ordenar` devolvia a lista como veio e ignorava `sentido`: o select "Maior / Menor primeiro"
    ficava na tela sem efeito. Controle que não obedece é pior que controle ausente — quem o usa
    conclui que a ordem é aquela, e ela não é.

    A suíte da primeira entrega passava inteira com o defeito: `T-09` só exercitava uma das quatro
    ordens, e era a única que **não** era a padrão.
    """
    linhas = [_linha_com_razao(1, 3), _linha_com_razao(2, 1), _linha_com_razao(3, 2)]
    anos = (2026,)

    desc = visao._ordenar(
        linhas,
        visao.Recorte(ano=2026, ordem=visao.ORDEM_PADRAO, sentido="desc", anos_disponiveis=anos),
    )
    asc = visao._ordenar(
        linhas,
        visao.Recorte(ano=2026, ordem=visao.ORDEM_PADRAO, sentido="asc", anos_disponiveis=anos),
    )

    # A decrescente é a ordem da consulta; a crescente é ela invertida, e **não** a mesma lista.
    assert [linha.edital.pk for linha in desc] == [1, 2, 3]
    assert [linha.edital.pk for linha in asc] == [3, 2, 1]


def test_toda_ordem_do_catalogo_responde_ao_sentido():
    """A guarda contra o defeito voltar por outra ordem.

    As quatro do catálogo respondem ao sentido, e nenhuma é exceção: era exatamente uma exceção
    silenciosa — a ordem padrão — que a primeira entrega tinha.
    """
    linhas = [_linha_com_razao(1, 3), _linha_com_razao(2, 1), _linha_com_razao(3, 2)]
    anos = (2026,)

    for ordem in visao.ORDENS:

        def ordenada(sentido, ordem=ordem):
            recorte = visao.Recorte(ano=2026, ordem=ordem, sentido=sentido, anos_disponiveis=anos)
            return [linha.edital.pk for linha in visao._ordenar(linhas, recorte)]

        assert ordenada("desc") != ordenada("asc"), f"a ordem {ordem} ignora o sentido"


def test_sem_conteudo_e_a_diferenca_e_nunca_negativa():
    """O denominador da frase que se contradizia: quantos Editais não publicaram."""
    assert visao.Consolidado(editais=3, editais_publicados=3).sem_conteudo == 0
    assert visao.Consolidado(editais=5, editais_publicados=2).sem_conteudo == 3
    assert visao.Consolidado(editais=0, editais_publicados=0).sem_conteudo == 0


# ---------------------------------------------------------------------------
# T-10 — o recorte vazio não afirma nada sobre o acervo
# ---------------------------------------------------------------------------


def test_t10_recorte_vazio_nao_apresenta_zero_como_resposta_sobre_o_acervo():
    consolidado = visao._consolidar([], {}, {})

    assert consolidado.editais == 0
    # Vagas sai **ausente**, e não `0`: ninguém publicou nada neste recorte, e `0` afirmaria que
    # os Editais do recorte publicaram nenhuma vaga.
    assert not consolidado.vagas.existe
    assert not consolidado.razao.existe


# ---------------------------------------------------------------------------
# A invariante da forma
# ---------------------------------------------------------------------------


def test_numero_e_valor_ou_ausencia_nunca_os_dois_e_nunca_nenhum():
    import pytest

    with pytest.raises(ValueError):
        visao.Numero()
    with pytest.raises(ValueError):
        visao.Numero(valor=1, ausencia=visao.Ausencia(visao.NAO_APLICAVEL, "x"))
    # E zero é valor, não ausência.
    assert visao.Numero.de(0).existe


# ===========================================================================
# 041 — o Perfil de Vaga na visão institucional
# ===========================================================================


def perfil_nomeado(identidade, vagas, *, reserva="NONE", limite=None, nome="", codigo="", onde=""):
    """Um Perfil do conteúdo publicado, com o que a expansão lê dele."""
    declarado = {} if limite is None else {"reserveLimit": limite}
    return {
        "id": identidade,
        "name": nome,
        "code": codigo,
        "locality": onde,
        "immediateVacancies": vagas,
        "reserveType": reserva,
        **declarado,
    }


def linha_com(perfis, submetidas_por_perfil, *, fim=None, rascunhos=None):
    publicado = conteudo(perfis, fim=fim or ENCERRADO_ONTEM)
    contagem = {"submetidas": dict(submetidas_por_perfil), "rascunhos": dict(rascunhos or {})}
    return visao.linha_do_edital(edital(), publicado, contagem, AGORA)


# ---------------------------------------------------------------------------
# T009 — os Perfis saem da versão vigente, com as três espécies de reserva
# ---------------------------------------------------------------------------


def test_os_perfis_saem_da_versao_vigente_com_denominacao_e_codigo():
    linha = linha_com(
        [perfil_nomeado("p1", 10, nome="Técnico de Suporte", codigo="SUP-01", onde="Vitória")],
        {"p1": 4},
    )

    (perfil,) = linha.perfis
    assert perfil.denominacao == "Técnico de Suporte"
    assert perfil.codigo == "SUP-01"
    assert perfil.localidade == "Vitória"


def test_o_perfil_sem_denominacao_cai_no_codigo():
    linha = linha_com([perfil_nomeado("p1", 10, codigo="SUP-01")], {"p1": 1})

    assert linha.perfis[0].denominacao == "SUP-01"


def test_a_localidade_ausente_fica_vazia_e_nao_vira_nao_informada():
    """`""` faz a linha sumir: *"não informada"* afirmaria uma omissão que o Edital pode não ter."""
    linha = linha_com([perfil_nomeado("p1", 10, nome="Técnico")], {"p1": 1})

    assert linha.perfis[0].localidade == ""


def test_as_tres_especies_de_reserva_se_distinguem():
    linha = linha_com(
        [
            perfil_nomeado("sem", 10),
            perfil_nomeado("lim", 10, reserva="LIMITED", limite=5),
            perfil_nomeado("ilim", 10, reserva="UNLIMITED"),
        ],
        {},
    )

    especies = {p.identidade: (p.reserva.especie, p.reserva.limite) for p in linha.perfis}
    assert especies["sem"] == (visao.SEM_RESERVA, None)
    assert especies["lim"] == (visao.RESERVA_LIMITADA, 5)
    assert especies["ilim"] == (visao.RESERVA_ILIMITADA, None)


def test_reserva_limitada_sem_limite_legivel_nao_inventa_numero():
    """Conteúdo que o Edital não deveria ter publicado: a tela não adivinha o número."""
    linha = linha_com([perfil_nomeado("p1", 10, reserva="LIMITED")], {})

    assert linha.perfis[0].reserva.limite is None


# ---------------------------------------------------------------------------
# T010 — a gramática da ausência, no Perfil
# ---------------------------------------------------------------------------


def test_o_perfil_sem_vaga_imediata_tem_razao_nao_aplicavel_e_vagas_zero():
    linha = linha_com([perfil_nomeado("p1", 0, reserva="UNLIMITED")], {"p1": 12})

    (perfil,) = linha.perfis
    assert perfil.vagas.existe and perfil.vagas.valor == 0
    assert not perfil.razao.existe
    assert perfil.razao.ausencia.especie == visao.NAO_APLICAVEL


def test_em_preenchimento_e_contado_por_perfil():
    linha = linha_com(
        [perfil_nomeado("p1", 10), perfil_nomeado("p2", 10)],
        {"p1": 3},
        rascunhos={"p1": 2, "p2": 7},
    )

    por_perfil = {p.identidade: p.em_preenchimento.valor for p in linha.perfis}
    assert por_perfil == {"p1": 2, "p2": 7}
    assert linha.em_preenchimento.valor == 9


# ---------------------------------------------------------------------------
# T011 — a razão é recalculada, e nunca somada nem mediada
# ---------------------------------------------------------------------------


def test_a_razao_do_edital_e_recalculada_e_nunca_soma_das_razoes():
    """Dois Perfis de 20 vagas com `1,0` e `3,0` dão `2,0` no Edital — nunca `4,0`, nunca `2,0`
    por média que coincidisse por acaso com denominadores iguais.
    """
    linha = linha_com([perfil_nomeado("a", 20), perfil_nomeado("b", 20)], {"a": 20, "b": 60})

    razoes = [p.razao.valor for p in linha.perfis]
    assert razoes == [Decimal("1.0"), Decimal("3.0")]
    assert linha.razao.valor == Decimal("2.0")
    assert linha.razao.valor != sum(razoes)


def test_a_razao_recalculada_difere_da_media_quando_os_denominadores_diferem():
    """O caso em que média e recálculo divergem — 10 e 40 vagas."""
    linha = linha_com([perfil_nomeado("a", 10), perfil_nomeado("b", 40)], {"a": 30, "b": 40})

    razoes = [p.razao.valor for p in linha.perfis]
    assert razoes == [Decimal("3.0"), Decimal("1.0")]
    media = sum(razoes) / len(razoes)
    assert linha.razao.valor == Decimal("1.4")
    assert linha.razao.valor != media


def test_vagas_e_submetidas_reconciliam_com_a_linha():
    linha = linha_com([perfil_nomeado("a", 20), perfil_nomeado("b", 30)], {"a": 5, "b": 7})

    assert sum(p.vagas.valor for p in linha.perfis) == linha.vagas.valor == 50
    assert sum(p.submetidas.valor for p in linha.perfis) == linha.submetidas.valor == 12


# ---------------------------------------------------------------------------
# T012 — o Perfil que a Retificação removeu
# ---------------------------------------------------------------------------


def test_inscricao_de_perfil_removido_conta_no_edital_e_e_declarada():
    linha = linha_com(
        [perfil_nomeado("vigente", 20)], {"vigente": 5, "removido": 15}, rascunhos={"sumiu": 2}
    )

    assert linha.submetidas.valor == 20
    assert [p.identidade for p in linha.perfis] == ["vigente"]
    assert sum(p.submetidas.valor for p in linha.perfis) == 5
    # A diferença é **contada**, para poder ser declarada — e não acomodada num Perfil inventado.
    assert linha.submetidas_sem_perfil == 15
    assert linha.rascunhos_sem_perfil == 2


def test_sem_perfil_removido_a_diferenca_e_zero():
    linha = linha_com([perfil_nomeado("p1", 10)], {"p1": 4})

    assert linha.submetidas_sem_perfil == 0
    assert linha.rascunhos_sem_perfil == 0


# ---------------------------------------------------------------------------
# T021 · T022 · T023 — a Atenção muda de nível
# ---------------------------------------------------------------------------


def especies(marcas):
    return {m.especie for m in marcas}


def test_t021_edital_com_razao_acima_de_1_e_perfil_vazio_recebe_marca():
    """**É a feature.** Sob a `040` esta linha não receberia marca alguma: a razão do agregado é
    `1,1`, acima de 1, e o Perfil vazio não tinha como aparecer.
    """
    linha = linha_com([perfil_nomeado("a", 20), perfil_nomeado("b", 20)], {"a": 45, "b": 0})

    assert linha.razao.valor > 1
    assert especies(linha.marcas)
    vazio = next(p for p in linha.perfis if p.identidade == "b")
    assert visao.SEM_PROCURA in especies(vazio.marcas)


def test_t022_sem_procura_vale_sem_denominador():
    """Um Perfil só de cadastro de reserva que encerrou sem ninguém **encerrou sem procura**.

    Só *demanda abaixo da oferta* exige denominador; *sem procura* é a contagem em zero.
    """
    linha = linha_com(
        [perfil_nomeado("com", 20), perfil_nomeado("reserva", 0, reserva="UNLIMITED")],
        {"com": 40},
    )

    so_reserva = next(p for p in linha.perfis if p.identidade == "reserva")
    assert visao.SEM_PROCURA in especies(so_reserva.marcas)
    assert visao.DEMANDA_ABAIXO_DA_OFERTA not in especies(so_reserva.marcas)


def test_t023_cada_especie_declara_o_seu_denominador():
    """Cinco Perfis, três com vaga imediata, dois deles abaixo da oferta e um vazio sem vaga.

    *Demanda abaixo* conta sobre os **três** com vaga; *sem procura* sobre os **cinco** vigentes.
    *"2 de 5"* seria aritmeticamente verdadeiro e institucionalmente enganoso.
    """
    linha = linha_com(
        [
            perfil_nomeado("v1", 10),
            perfil_nomeado("v2", 10),
            perfil_nomeado("v3", 10),
            perfil_nomeado("r1", 0, reserva="UNLIMITED"),
            perfil_nomeado("r2", 0, reserva="UNLIMITED"),
        ],
        {"v1": 5, "v2": 3, "v3": 40, "r1": 7},
    )

    resumo = {m.especie: m.mensagem for m in linha.marcas}
    assert (
        "2 de 3 Perfis com vaga imediata abaixo da oferta" in resumo[visao.DEMANDA_ABAIXO_DA_OFERTA]
    )
    assert "1 de 5 Perfis sem nenhuma inscrição" in resumo[visao.SEM_PROCURA]


def test_t023b_com_um_perfil_so_a_mensagem_e_a_do_perfil():
    """*"1 de 1 Perfil sem nenhuma inscrição"* é aritmética falando com quem quer português."""
    linha = linha_com([perfil_nomeado("unico", 20)], {})

    assert linha.marcas == linha.perfis[0].marcas
    assert all("de 1" not in m.mensagem for m in linha.marcas)


def test_t023c_edital_com_todos_os_perfis_acima_da_oferta_nao_tem_marca():
    linha = linha_com([perfil_nomeado("a", 10), perfil_nomeado("b", 10)], {"a": 30, "b": 40})

    assert linha.marcas == ()


def test_t023d_periodo_aberto_nao_produz_marca_em_perfil_nenhum():
    linha = linha_com(
        [perfil_nomeado("a", 10), perfil_nomeado("b", 10)], {"a": 1}, fim=FECHA_AMANHA
    )

    assert linha.marcas == ()
    assert all(p.marcas == () for p in linha.perfis)


# ===========================================================================
# 042 — a hierarquia do detalhe do Perfil
# ===========================================================================


def perfil_um(**extra):
    """Um Perfil com os campos que a identidade secundária compõe."""
    return linha_com([perfil_nomeado("p1", 10, **extra)], {"p1": 4}).perfis[0]


# ---------------------------------------------------------------------------
# T006 — a identidade secundária
# ---------------------------------------------------------------------------


def test_a_identidade_secundaria_junta_os_tres_por_ponto_medio():
    perfil = perfil_um(codigo="DOC-INFO", onde="Campus Serra", reserva="LIMITED", limite=6)

    assert perfil.identidade_secundaria == "DOC-INFO · Campus Serra · CR limitado a 6"


def test_a_identidade_secundaria_omite_o_que_nao_existe():
    assert perfil_um(codigo="TEC-LAB").identidade_secundaria == "TEC-LAB"
    assert perfil_um(onde="Vitória").identidade_secundaria == "Vitória"
    assert (
        perfil_um(codigo="TEC-LAB", reserva="UNLIMITED").identidade_secundaria
        == "TEC-LAB · CR ilimitado"
    )


def test_a_ausencia_de_reserva_nao_produz_texto():
    """`FR-626` — o vazio **é** a declaração de que não há, como em `especie_de_reversao`."""
    perfil = perfil_um(codigo="TEC-LAB", onde="Vitória")

    assert perfil.reserva.especie == visao.SEM_RESERVA
    assert "CR" not in perfil.identidade_secundaria
    assert "não há" not in perfil.identidade_secundaria


def test_sem_nenhum_dos_tres_a_identidade_secundaria_e_vazia():
    """E aí a linha some inteira — nunca *"não informado"* (`FR-626`, caso-limite)."""
    assert perfil_um().identidade_secundaria == ""


def test_faltando_parte_a_linha_existe_com_o_que_ha():
    """O caso que a análise cruzada corrigiu: sem código e sem localidade, **mas com** reserva."""
    assert perfil_um(reserva="UNLIMITED").identidade_secundaria == "CR ilimitado"


# ---------------------------------------------------------------------------
# T007 — o rótulo curto
# ---------------------------------------------------------------------------


def test_cada_especie_tem_rotulo_curto_distinto_da_mensagem():
    linha = linha_com([perfil_nomeado("vazio", 10), perfil_nomeado("pouco", 10)], {"pouco": 3})

    por_especie = {m.especie: m for p in linha.perfis for m in p.marcas}
    assert por_especie[visao.SEM_PROCURA].rotulo == "Sem procura"
    assert por_especie[visao.DEMANDA_ABAIXO_DA_OFERTA].rotulo == "Demanda abaixo da oferta"
    for marca in por_especie.values():
        assert marca.rotulo and marca.rotulo != marca.mensagem
