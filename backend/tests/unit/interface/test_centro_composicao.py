"""A composição do Centro de Controle (136) — as regras puras, sem banco.

**Por que aqui, e não nos cenários.** As regras de agregação e do destaque valem para toda família
de classificação, e os cenários de treinamento da `134` não têm todas: nenhum tem dois Perfis no
mesmo Edital, nenhum termina com a seleção concluída. Montar o `Andamento` à mão é o que deixa
provar as regras nesses casos — como a `127` prova as sete situações.
"""

import re
from datetime import UTC, datetime
from types import SimpleNamespace

import pytest

from processo_seletivo.interface import andamento as a
from processo_seletivo.interface import centro as cc
from processo_seletivo.interface import conceitos as c
from processo_seletivo.interface.providencias import Providencia

AMPLA, PPP = "ampla", "ppp"
LISTAS = [(AMPLA, "Ampla concorrência (linha geral do quadro)"), (PPP, "Pessoas pretas (PPP)")]
MARCO_SORTEIO = {"id": "m1", "name": "Sorteio", "orderProduction": "POR_SORTEIO", "drawMethod": {}}
MARCO_NOTAS = {"id": "m2", "name": "Classificação", "orderProduction": "POR_PONTUACAO"}
EDITAL = SimpleNamespace(status="PUBLICADO")


def cel(situacao, natureza="", **campos):
    return a.Celula(situacao, natureza=natureza, **campos)


def ponto(tipo, titulo, grupo, situacoes, *, marco=None, etapa=None, natureza=None, listas=LISTAS):
    """Um ponto com uma célula por lista; `situacoes` é uma situação só ou uma por lista."""
    if isinstance(situacoes, str):
        situacoes = [situacoes] * len(listas)
    novo = a.Ponto(tipo, titulo, grupo, marco=marco, etapa=etapa)
    for (lista, _), situacao in zip(listas, situacoes, strict=True):
        novo.celulas[a._chave(lista)] = cel(situacao, natureza or tipo)
    return novo


def perfil(pontos, *, pid="p1", nome="Técnico em Informática", listas=LISTAS):
    return a.PerfilNoAndamento(
        perfil={"id": pid, "name": nome},
        forma="por sorteio",
        listas=listas,
        pontos=pontos,
        inscritos=10,
    )


def prov(
    natureza, *, situacao=a.PENDENTE, sua=True, chave=None, perfil_id="p1", ato=None, ate=None
):
    return Providencia(
        natureza=natureza,
        chave=chave or (natureza, perfil_id),
        onde="Técnico",
        ato=ato or f"Praticar {natureza}",
        situacao=situacao,
        responsavel=a.CONDUZ,
        sua=sua,
        url=f"/ato/{natureza}/" if sua else "",
        perfil_id=perfil_id,
        ate=ate,
    )


def andamento(perfis, providencias, *, inscricoes=None, ve_a_matriz=True):
    from processo_seletivo.inscricoes.domain import periodo

    return a.Andamento(
        perfis=perfis,
        providencias=providencias,
        atencoes=[],
        inscricoes=inscricoes or {"estado": periodo.ENCERRADO, "enviadas": 10},
        ve_a_matriz=ve_a_matriz,
    )


def etapa_titulos(situacao=a.PENDENTE):
    return ponto(
        a.ETAPA,
        "Análise de títulos",
        a.GRUPO_DAS_ETAPAS,
        situacao,
        etapa={"id": "e1", "name": "Análise de títulos"},
        natureza=a.DISTRIBUIR,
    )


def sorteio_antes_do_congelamento():
    """O C06 em miniatura: relação a congelar, a Etapa de títulos que o sorteio não lê."""
    pontos = [
        etapa_titulos(),
        ponto(a.RELACAO, "Relação", a.GRUPO_DO_SORTEIO, a.PENDENTE, marco=MARCO_SORTEIO),
        ponto(a.SEMENTE, "Semente", a.GRUPO_DO_SORTEIO, a.DEPOIS, marco=MARCO_SORTEIO),
        ponto(a.SORTEIO, "Sorteio", a.GRUPO_DO_SORTEIO, a.DEPOIS, marco=MARCO_SORTEIO),
        ponto(a.APURACAO, "Apuração", a.GRUPO_DO_SORTEIO, a.DEPOIS, marco=MARCO_SORTEIO),
        ponto(a.RESULTADO, "Resultado", a.GRUPO_DO_SORTEIO, a.DEPOIS, marco=MARCO_SORTEIO),
        ponto(a.CONVOCACAO, "Convocação", a.GRUPO_DO_SORTEIO, a.DEPOIS, marco=MARCO_SORTEIO),
    ]
    providencias = [
        prov(a.RELACAO, chave=("relacao", "m1")),
        prov(a.DISTRIBUIR, chave=("etapa", "e1"), perfil_id="", ato="Distribuir 10 inscrições"),
    ]
    return andamento([perfil(pontos)], providencias)


def compor(dados, **opcoes):
    return cc.compor(opcoes.pop("edital", EDITAL), dados, **opcoes)


# ---------------------------------------------------------------------------------------------
# A primeira leitura: o andamento (FR-4710, FR-4711)
# ---------------------------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("situacoes", "esperado"),
    [
        ([a.FEITO, a.FEITO], c.CONCLUIDA),
        ([a.FEITO, a.NAO_SE_APLICA], c.CONCLUIDA),
        ([a.NAO_SE_APLICA, a.NAO_SE_APLICA], c.NAO_SE_APLICA),
        ([a.DEPOIS, a.DEPOIS], c.NAO_INICIADA),
        ([a.DEPOIS, a.NAO_SE_APLICA], c.NAO_INICIADA),
        ([a.FEITO, a.DEPOIS], c.EM_CURSO),
        ([a.PENDENTE, a.DEPOIS], c.EM_CURSO),
        ([a.OBSOLETO, a.FEITO], c.EM_CURSO),
        ([a.AGUARDA], c.EM_CURSO),
        ([a.IMPEDIDO], c.EM_CURSO),
    ],
)
def test_agregar_segue_a_tabela(situacoes, esperado):
    assert cc.agregar([cel(s) for s in situacoes]) == esperado


def test_agregar_sem_celula_e_nada():
    assert cc.agregar([]) is None
    assert cc.agregar([None]) is None


@pytest.mark.parametrize(
    "situacoes", [list(t) for t in __import__("itertools").product(a.SITUACOES, repeat=2)]
)
def test_concluida_se_e_so_se_tudo_feito_ou_nao_se_aplica_com_algum_feito(situacoes):
    """FR-4710, SC-1473: o "se, e só se", em todas as combinações de duas listas."""
    concluida = cc.agregar([cel(s) for s in situacoes]) == c.CONCLUIDA
    assert concluida == (
        all(s in (a.FEITO, a.NAO_SE_APLICA) for s in situacoes) and a.FEITO in situacoes
    )


@pytest.mark.parametrize(
    ("andamentos", "esperado"),
    [
        ([c.CONCLUIDA, c.CONCLUIDA], c.CONCLUIDA),
        ([c.CONCLUIDA, c.NAO_SE_APLICA], c.CONCLUIDA),
        ([c.NAO_INICIADA, c.NAO_INICIADA], c.NAO_INICIADA),
        ([c.CONCLUIDA, c.NAO_INICIADA], c.EM_CURSO),
        ([c.EM_CURSO, c.CONCLUIDA], c.EM_CURSO),
        ([c.NAO_SE_APLICA, c.NAO_SE_APLICA], c.NAO_SE_APLICA),
        ([None, c.NAO_SE_APLICA], c.NAO_SE_APLICA),
        ([], None),
    ],
)
def test_juntar_segue_a_tabela(andamentos, esperado):
    assert cc.juntar(andamentos) == esperado


# ---------------------------------------------------------------------------------------------
# Onde cada ponto e cada providência mora (FR-4709, FR-4716)
# ---------------------------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("tipo", "grupo", "fase"),
    [
        (a.RELACAO, a.GRUPO_DO_SORTEIO, c.CLASSIFICACAO),
        (a.SEMENTE, a.GRUPO_DO_SORTEIO, c.CLASSIFICACAO),
        (a.SORTEIO, a.GRUPO_DO_SORTEIO, c.CLASSIFICACAO),
        (a.ORDEM, a.GRUPO_DA_PONTUACAO, c.CLASSIFICACAO),
        (a.CORTE, a.GRUPO_DA_PONTUACAO, c.VAGAS),
        (a.APURACAO, a.GRUPO_DA_PONTUACAO, c.VAGAS),
        (a.RESULTADO, a.GRUPO_DA_PONTUACAO, c.RESULTADO),
        (a.CONVOCACAO, a.GRUPO_DA_PONTUACAO, c.CONVOCACAO),
        (a.ETAPA, a.GRUPO_DAS_ETAPAS, c.AVALIACAO),
        (a.ETAPA, a.GRUPO_SEM_EFEITO, c.AVALIACAO),
        (a.ETAPA, a.GRUPO_DA_GOVERNADA, c.VAGAS),
    ],
)
def test_cada_ponto_tem_a_sua_fase(tipo, grupo, fase):
    assert cc.fase_do_ponto(a.Ponto(tipo, "x", grupo)) == fase


def test_toda_natureza_da_127_tem_fase_propria():
    """Nenhuma natureza cai no padrão: uma nova na `127` reprova aqui antes de sumir na tela."""
    naturezas = {
        a.RELACAO, a.SEMENTE, a.SORTEIO, a.ORDEM, a.CORTE, a.APURACAO, a.RESULTADO,
        a.CONVOCACAO, a.DISTRIBUIR, a.AVALIAR, a.CONSOLIDAR, a.REAVALIAR, a.CONFERIR,
        a.RECURSO, a.ETAPA,
    }  # fmt: skip
    assert naturezas <= cc.NATUREZAS_CONHECIDAS


def test_a_providencia_da_etapa_governada_e_de_vagas_pelo_id_e_nao_pelo_nome():
    """D-004: duas Etapas homônimas; só a governada vai a Vagas."""
    governada = prov(a.DISTRIBUIR, chave=("etapa", "e-gov"))
    homonima = prov(a.DISTRIBUIR, chave=("etapa", "e-outra"))
    assert cc.fase_da_providencia(governada, {"e-gov"}) == c.VAGAS
    assert cc.fase_da_providencia(homonima, {"e-gov"}) == c.AVALIACAO
    assert cc.fase_da_providencia(prov(a.CONFERIR), set()) == c.CONVOCACAO
    assert cc.fase_da_providencia(prov(a.RECURSO), set()) == c.RESULTADO


# ---------------------------------------------------------------------------------------------
# A paralela ao sorteio (D-008)
# ---------------------------------------------------------------------------------------------


def test_a_etapa_que_o_sorteio_nao_le_e_paralela():
    dados = sorteio_antes_do_congelamento()
    assert cc.paralela(dados.perfis) == c.PARALELA


def test_com_etapa_de_habilitacao_nao_ha_paralela():
    marco = {**MARCO_SORTEIO, "drawMethod": {"qualifyingStageId": "e1"}}
    pontos = [etapa_titulos(), ponto(a.RELACAO, "Relação", "g", a.DEPOIS, marco=marco)]
    assert cc.paralela([perfil(pontos)]) == ""


def test_com_um_perfil_de_pontuacao_a_etapa_nao_e_paralela():
    """O protótipo olhava um Perfil só; um marco de pontuação noutro Perfil lê a Etapa."""
    sorteio = perfil(sorteio_antes_do_congelamento().perfis[0].pontos)
    notas = perfil(
        [etapa_titulos(), ponto(a.ORDEM, "Ordem", "g", a.DEPOIS, marco=MARCO_NOTAS)], pid="p2"
    )
    assert cc.paralela([sorteio, notas]) == ""


def test_sem_etapa_nao_ha_paralela():
    pontos = [ponto(a.RELACAO, "Relação", "g", a.PENDENTE, marco=MARCO_SORTEIO)]
    assert cc.paralela([perfil(pontos)]) == ""


# ---------------------------------------------------------------------------------------------
# O destaque (FR-4722 a FR-4725)
# ---------------------------------------------------------------------------------------------


def test_c06_destaca_fixar_os_participantes_e_diz_o_que_espera_por_ela():
    centro = compor(sorteio_antes_do_congelamento())

    assert centro.destaque is not None
    assert centro.destaque.item.titulo == "Fixar os participantes"
    assert centro.destaque.item.no_gps == "Praticar relacao"
    assert centro.destaque.porque == c.PORQUE_DESTRAVA_UMA
    assert centro.destaque.destrava == ["Obter a semente pública", "Realizar o sorteio"]
    assert [i.p.natureza for i in centro.demais_suas] == [a.DISTRIBUIR]
    assert centro.demais_suas[0].paralela == c.PARALELA


def test_uma_acao_so_e_destacada_por_ser_a_unica():
    dados = sorteio_antes_do_congelamento()
    dados.providencias = dados.providencias[:1]
    centro = compor(dados)
    assert centro.destaque.porque == c.PORQUE_UNICA


def test_duas_acoes_independentes_nao_tem_destaque():
    """O C12 em miniatura: classificar uma lista e conferir documentos noutra."""
    pontos = [
        ponto(a.ORDEM, "Ordem", "g", [a.FEITO, a.PENDENTE], marco=MARCO_NOTAS),
        ponto(a.CONVOCACAO, "Convocação", "g", [a.PENDENTE, a.DEPOIS], marco=MARCO_NOTAS),
    ]
    dados = andamento([perfil(pontos)], [prov(a.ORDEM), prov(a.CONFERIR)])
    centro = compor(dados)

    assert centro.destaque is None
    assert centro.sem_destaque == c.SEM_DESTAQUE.format(n=2)
    assert "o GPS não escolhe a ordem entre elas" in centro.sem_destaque


def test_sem_acao_sua_nao_ha_destaque_nem_frase():
    dados = sorteio_antes_do_congelamento()
    dados.providencias = [prov(a.RELACAO, sua=False)]
    centro = compor(dados)
    assert centro.destaque is None and centro.sem_destaque == ""
    assert not centro.suas and len(centro.de_outros) == 1


def test_o_destaque_e_sempre_uma_providencia_sua():
    centro = compor(sorteio_antes_do_congelamento())
    assert centro.destaque.item.p.sua


# ---------------------------------------------------------------------------------------------
# A composição: as invariantes (data-model, SC-1473)
# ---------------------------------------------------------------------------------------------


def _invariantes(centro, dados):
    assert sum(len(f.providencias) for f in centro.fases) == dados.nivel_1.total
    for fase in centro.fases:
        assert bool(fase.suas) == any(i.p.grupo == "sua" for i in fase.providencias)


def test_cada_providencia_esta_numa_fase_so_e_a_marca_sua_segue_as_providencias():
    dados = sorteio_antes_do_congelamento()
    centro = compor(dados)
    _invariantes(centro, dados)
    fases = {f.chave: f for f in centro.fases}
    assert fases[c.CLASSIFICACAO].suas and fases[c.AVALIACAO].suas
    assert not fases[c.VAGAS].suas


def test_o_mapa_tem_oito_fases_em_tres_grupos():
    centro = compor(sorteio_antes_do_congelamento())
    assert [f.chave for f in centro.fases] == list(c.CHAVES)
    assert [(rotulo, [f.chave for f in fases]) for rotulo, fases in centro.grupos] == [
        ("Abertura", [c.PUBLICACAO, c.INSCRICOES]),
        ("Seleção", [c.AVALIACAO, c.CLASSIFICACAO, c.RESULTADO, c.VAGAS]),
        ("Ocupação", [c.CONVOCACAO, c.CONCLUSAO]),
    ]


def test_varias_fases_em_curso_ao_mesmo_tempo():
    centro = compor(sorteio_antes_do_congelamento())
    assert {f.chave for f in centro.em_curso} == {c.AVALIACAO, c.CLASSIFICACAO}


def test_o_roteiro_diz_por_que_o_passo_ainda_nao_comecou():
    dados = sorteio_antes_do_congelamento()
    semente = dados.perfis[0].pontos[2]
    for lista, _ in LISTAS:
        semente.celulas[a._chave(lista)] = cel(
            a.DEPOIS, a.SEMENTE, razao="nenhuma relação deste marco está congelada"
        )
    centro = compor(dados)
    [classificacao] = [f for f in centro.fases if f.chave == c.CLASSIFICACAO]
    roteiro = classificacao.perfis[0].roteiro
    assert [p.simples for p in roteiro] == [
        "Fixar os participantes",
        "Obter a semente pública",
        "Realizar o sorteio",
    ]
    assert roteiro[0].tem_acao and roteiro[0].termo == "congelar a relação"
    assert roteiro[1].razao == "nenhuma relação deste marco está congelada"
    assert roteiro[1].unico and not roteiro[2].unico


def test_a_fase_em_curso_sem_providencia_diz_nada_a_fazer():
    """Vagas no C12: uma lista apurada, a outra esperando a ordem."""
    pontos = [
        ponto(a.ORDEM, "Ordem", "g", [a.FEITO, a.PENDENTE], marco=MARCO_NOTAS),
        ponto(a.APURACAO, "Apuração", "g", [a.FEITO, a.DEPOIS], marco=MARCO_NOTAS),
    ]
    centro = compor(andamento([perfil(pontos)], [prov(a.ORDEM)]))
    [vagas] = [f for f in centro.fases if f.chave == c.VAGAS]
    assert vagas.em_curso and vagas.parada
    assert vagas.resumo == "1 de 2 listas concluídas"


def test_a_retificacao_em_curso_poe_o_edital_em_curso():
    centro = compor(sorteio_antes_do_congelamento(), em_curso=[{"meu_ato": False}])
    edital = centro.fases[0]
    assert edital.andamento == c.EM_CURSO and edital.nota == c.RETIFICACAO_EM_CURSO


RETIFICACAO_SUA = {"meu_ato": "Homologar", "passo": {"papel": "quem homologa"}, "parada": ""}
RETIFICACAO_DE_OUTRO = {"meu_ato": "", "passo": {"papel": "quem publica"}, "parada": ""}


def test_a_retificacao_que_aguarda_a_pessoa_e_algo_em_aberto_e_dela():
    """Item 1 da revisão do PR #443: a regra da `104` (FR-2819, FR-2820) vale no Centro.

    Sem providência nenhuma, o Centro dizia "Nada em aberto", "Nenhuma ação é sua agora" e
    "nada a fazer agora" na fase Edital, ao lado de "Retificação em curso — aguarda você".
    """
    pontos = [ponto(a.ORDEM, "Ordem", "g", a.FEITO, marco=MARCO_NOTAS)]
    centro = compor(andamento([perfil(pontos)], []), em_curso=[RETIFICACAO_SUA])
    edital = centro.fases[0]

    assert centro.tem_algo and centro.tem_sua
    assert centro.retificacoes_suas == [RETIFICACAO_SUA]
    assert edital.em_curso and not edital.parada
    assert (edital.quantas_suas, edital.quantas_de_outros) == (1, 0)
    assert centro.onde == "Há algo em aberto em Edital."
    assert centro.onde_detalhe == "1 ação é sua."
    # Não se destaca a si mesma: tem a linha da `104`, e nenhuma frase de "o GPS não escolhe".
    assert centro.destaque is None and centro.sem_destaque == ""
    assert cc.fase_consultada(centro).chave == c.PUBLICACAO


def test_a_retificacao_de_outro_papel_nao_e_sua_nem_parada():
    pontos = [ponto(a.ORDEM, "Ordem", "g", a.FEITO, marco=MARCO_NOTAS)]
    centro = compor(andamento([perfil(pontos)], []), em_curso=[RETIFICACAO_DE_OUTRO])
    edital = centro.fases[0]

    assert centro.tem_algo and not centro.tem_sua
    assert not edital.parada and (edital.quantas_suas, edital.quantas_de_outros) == (0, 1)
    assert centro.onde_detalhe == "1 está com outro papel."


def test_a_retificacao_parada_pelo_desfecho_nao_e_algo_em_aberto():
    parada = {**RETIFICACAO_SUA, "meu_ato": "", "parada": "cancelado"}
    pontos = [ponto(a.ORDEM, "Ordem", "g", a.FEITO, marco=MARCO_NOTAS)]
    centro = compor(andamento([perfil(pontos)], []), em_curso=[parada])
    assert not centro.tem_algo and not centro.tem_sua


def test_com_retificacao_sua_a_unica_providencia_nao_e_a_unica_acao():
    """A regra 1 do destaque mentiria ("É a única ação sua"), e a 2 também ("corre em paralelo")."""
    dados = sorteio_antes_do_congelamento()
    centro = compor(dados, em_curso=[RETIFICACAO_SUA])
    assert centro.destaque is None
    assert centro.sem_destaque == c.SEM_DESTAQUE.format(n=3)

    dados.providencias = dados.providencias[:1]
    centro = compor(dados, em_curso=[RETIFICACAO_SUA])
    assert centro.destaque is None and centro.sem_destaque == c.SEM_DESTAQUE.format(n=2)


def test_o_rotulo_curto_e_o_do_nivel_1_e_nunca_none():
    """Item 2 da revisão: a Modalidade sem código mostrava "None", recortado do rótulo longo."""
    listas = [
        ("", "Ampla concorrência (linha geral do quadro)"),
        ("m-ppp", "Pessoas pretas (None)"),
    ]
    novo = perfil(
        [ponto(a.ORDEM, "Ordem", "g", a.PENDENTE, marco=MARCO_NOTAS, listas=listas)],
        listas=listas,
    )
    novo.perfil["competitionModalities"] = [{"id": "m-ppp", "name": "Pessoas pretas", "code": None}]
    centro = compor(andamento([novo], [prov(a.ORDEM)]))

    curtos = [lista.curto for lista in centro.perfis[0].listas]
    assert curtos == ["Ampla concorrência", "Pessoas pretas"]
    [classificacao] = [f for f in centro.fases if f.chave == c.CLASSIFICACAO]
    assert [lst.rotulo for lst in classificacao.perfis[0].listas] == curtos


def test_o_titulo_no_meio_da_frase_so_baixa_a_inicial():
    """Item 4 da revisão: o nome da Etapa e o código da lista ficam como o Edital os publica."""
    item = cc._item(
        prov(a.CONSOLIDAR, ato="Consolidar a Prova Prática da PPP", sua=False),
        set(),
        {c.AVALIACAO: cc.Macrofase(c.AVALIACAO, c.EM_CURSO)},
    )
    assert item.titulo_no_meio_da_frase == "consolidar a Prova Prática da PPP"


def test_o_ato_em_jargao_se_traduz_num_lugar_so():
    """Item 7 da revisão: a providência, a tabela da fase e a linha da lista leem a mesma função."""
    assert c.ato_simples(a.ORDEM, "Emitir a ordem") == c.CONCEITOS[a.ORDEM]["simples"]
    assert c.ato_simples(a.CONFERIR, "Conferir 3 documentos") == "Conferir 3 documentos"
    pontos = [ponto(a.ORDEM, "Ordem", "g", a.PENDENTE, marco=MARCO_NOTAS)]
    centro = compor(andamento([perfil(pontos)], [prov(a.ORDEM, ato="Emitir a ordem")]))
    simples = c.CONCEITOS[a.ORDEM]["simples"]
    [item] = centro.itens
    assert (item.titulo, item.no_gps) == (simples, "Emitir a ordem")
    assert {titulo for _, _, titulo in centro.perfis[0].listas[0].atos} == {simples}
    [classificacao] = [f for f in centro.fases if f.chave == c.CLASSIFICACAO]
    assert classificacao.perfis[0].listas[0].celulas[0].ato == simples


def test_a_conclusao_nunca_diz_que_o_edital_pode_ser_encerrado():
    pontos = [ponto(a.ORDEM, "Ordem", "g", a.FEITO, marco=MARCO_NOTAS)]
    centro = compor(andamento([perfil(pontos)], []))
    conclusao = centro.fases[-1]
    assert conclusao.andamento == c.EM_CURSO
    assert conclusao.resumo == c.CONCLUSAO_PRONTA
    assert not conclusao.providencias


def test_selecao_concluida_por_fixture():
    """Nenhum cenário da `134` termina assim: a seleção concluída é montada à mão."""
    pontos = [
        ponto(a.ORDEM, "Ordem", "g", a.FEITO, marco=MARCO_NOTAS),
        ponto(a.APURACAO, "Apuração", "g", a.FEITO, marco=MARCO_NOTAS),
        ponto(a.RESULTADO, "Resultado", "g", a.FEITO, marco=MARCO_NOTAS),
        ponto(a.CONVOCACAO, "Convocação", "g", a.FEITO, marco=MARCO_NOTAS),
    ]
    dados = andamento([perfil(pontos)], [])
    centro = compor(dados, edital=SimpleNamespace(status="ENCERRADO"))
    assert {f.andamento for f in centro.fases[2:]} <= {c.CONCLUIDA, c.NAO_SE_APLICA}
    assert centro.fases[-1].andamento == c.CONCLUIDA
    assert centro.onde == "Seleção concluída. Nada em aberto."
    assert centro.total == 0 and centro.destaque is None


def test_dois_perfis_no_mesmo_edital_por_fixture():
    """Nenhum cenário da `134` tem dois Perfis; o detalhe da fase separa os dois, e o destaque
    olha só o roteiro do Perfil da providência (R-006)."""
    primeiro = perfil(sorteio_antes_do_congelamento().perfis[0].pontos, pid="p1", nome="Técnico")
    segundo = perfil(
        [
            ponto(a.RELACAO, "Relação", "g", a.FEITO, marco={**MARCO_SORTEIO, "id": "m9"}),
            ponto(a.SEMENTE, "Semente", "g", a.FEITO, marco={**MARCO_SORTEIO, "id": "m9"}),
            ponto(a.SORTEIO, "Sorteio", "g", a.PENDENTE, marco={**MARCO_SORTEIO, "id": "m9"}),
        ],
        pid="p2",
        nome="Licenciatura",
    )
    providencias = [prov(a.RELACAO, chave=("relacao", "m1"), perfil_id="p1")]
    centro = compor(andamento([primeiro, segundo], providencias))

    [classificacao] = [f for f in centro.fases if f.chave == c.CLASSIFICACAO]
    assert [fp.perfil.nome for fp in classificacao.perfis] == ["Técnico", "Licenciatura"]
    assert [pf.nome for pf in centro.perfis] == ["Técnico", "Licenciatura"]
    assert centro.destaque.destrava == ["Obter a semente pública", "Realizar o sorteio"]


# ---------------------------------------------------------------------------------------------
# "Onde estamos" e o papel (FR-4718 a FR-4721)
# ---------------------------------------------------------------------------------------------


def test_onde_estamos_nomeia_as_fases_e_diz_de_quem_e():
    ate = datetime(2026, 11, 14, 15, tzinfo=UTC)
    dados = sorteio_antes_do_congelamento()
    dados.providencias = [
        *dados.providencias,
        prov(a.RESULTADO, situacao=a.AGUARDA, sua=False, ate=ate, chave=("r",)),
        prov(a.CONVOCACAO, sua=False, chave=("cv",)),
    ]
    centro = compor(dados)
    assert centro.onde == (
        "Há algo em aberto em avaliação, classificação, resultado e recursos e convocação."
    )
    assert centro.onde_detalhe == (
        "2 ações são suas, 1 está com outro papel e 1 aguarda prazo ou resposta "
        "(a primeira até 14/11)."
    )


def test_nada_em_aberto_diz_o_que_esta_em_curso():
    pontos = [ponto(a.ORDEM, "Ordem", "g", [a.FEITO, a.DEPOIS], marco=MARCO_NOTAS)]
    centro = compor(andamento([perfil(pontos)], []))
    assert centro.onde == "Nada em aberto agora. Em curso: classificação."


@pytest.mark.parametrize(
    ("campos", "esperado"),
    [
        ({"conduz": True, "consulta": True}, "Você conduz a seleção."),
        ({"consulta": True, "publica": True}, "Você acompanha a seleção e publica resultados."),
        ({}, "Você acompanha este Edital sem ato a praticar nele."),
        (
            {"conduz": True, "consulta": True, "ativo": False},
            "Você conduz a seleção — mas o Processo está encerrado, e nenhum ato é seu.",
        ),
    ],
)
def test_o_papel_em_palavras(campos, esperado):
    base = dict.fromkeys(("conduz", "consulta", "publica", "julga", "retifica"), False)
    assert cc.papel(a.Alcance(**{**base, **campos})) == esperado


# ---------------------------------------------------------------------------------------------
# A fase consultada (FR-4730)
# ---------------------------------------------------------------------------------------------


def test_a_fase_consultada_e_a_pedida_ou_a_do_destaque():
    centro = compor(sorteio_antes_do_congelamento())
    assert cc.fase_consultada(centro, "vagas").chave == c.VAGAS
    assert cc.fase_consultada(centro, "inexistente").chave == c.CLASSIFICACAO
    assert cc.fase_consultada(centro).chave == c.CLASSIFICACAO


def test_sem_destaque_a_paralela_vem_por_ultimo():
    dados = sorteio_antes_do_congelamento()
    dados.providencias = [dados.providencias[1], prov(a.CONFERIR, chave=("cf",))]
    centro = compor(dados)
    assert centro.destaque is None
    assert cc.fase_consultada(centro).chave == c.CONVOCACAO


def test_sem_providencia_a_consultada_e_a_primeira_em_curso():
    pontos = [ponto(a.ORDEM, "Ordem", "g", [a.FEITO, a.DEPOIS], marco=MARCO_NOTAS)]
    centro = compor(andamento([perfil(pontos)], []))
    assert cc.fase_consultada(centro).chave == c.CLASSIFICACAO


# ---------------------------------------------------------------------------------------------
# Os conceitos (FR-4742, FR-4743, R-002)
# ---------------------------------------------------------------------------------------------


def test_todo_tipo_de_ponto_tem_conceito_completo():
    for tipo in (a.RELACAO, a.SEMENTE, a.SORTEIO, a.ORDEM, a.CORTE, a.APURACAO, a.RESULTADO,
                 a.CONVOCACAO, a.ETAPA, a.CONFERIR, a.RECURSO):  # fmt: skip
        dados = c.CONCEITOS[tipo]
        assert set(dados) == {"simples", "termo", "curta", "porque", "ao_confirmar"}, tipo
        assert all(texto.strip() for texto in dados.values()), tipo


def test_nenhum_texto_dos_conceitos_usa_termo_que_a_tela_nao_define():
    """A varredura de vocabulário lê o template; o texto que chega por variável escaparia dela."""
    import inspect

    fonte = inspect.getsource(c)
    textos = re.findall(r'"([^"]*)"', fonte.split('"""', 2)[2])
    proibidos = re.compile(r"\b(recorte|faixa|gera[cç])", re.I)
    assert [t for t in textos if proibidos.search(t)] == []


def test_os_conceitos_se_declaram_provisorios():
    assert "provisórios" in c.__doc__


@pytest.mark.parametrize(
    ("inscricoes", "andamento_"),
    [
        ({"estado": "encerrado", "enviadas": 1}, c.CONCLUIDA),
        ({"estado": "aberto", "enviadas": 3}, c.EM_CURSO),
        ({"estado": "futuro", "enviadas": 0}, c.NAO_INICIADA),
        ({"estado": "encerrado", "cancelado": True, "enviadas": 2}, c.CONCLUIDA),
        ({"cancelado": True, "enviadas": 2}, c.CONCLUIDA),
        ({"enviadas": 0}, c.NAO_INICIADA),
    ],
)
def test_a_fase_inscricoes_segue_o_periodo(inscricoes, andamento_):
    """FR-4713: o período que o andamento já lê — e o resumo é a linha da `127`, e não outra.

    A primeira versão tinha uma ramificação própria, com outro texto para o mesmo estado, e a
    página mostrava os dois (item 5 da revisão do PR #443).
    """
    from processo_seletivo.inscricoes.domain import periodo

    estado = {
        "encerrado": periodo.ENCERRADO,
        "aberto": periodo.ABERTO,
        "futuro": periodo.FUTURO,
    }.get(inscricoes.get("estado"), periodo.NAO_DESIGNADO)
    dados = {**inscricoes, "estado": estado}
    fase = cc._fase_inscricoes(dados)
    assert (fase.andamento, fase.resumo) == (andamento_, a.linha_das_inscricoes(dados))


def test_o_impedimento_fica_na_espera_com_quem_resolve():
    """Caso-limite: a providência impedida não é ação de ninguém, e diz quem a resolve."""
    from dataclasses import replace

    dados = sorteio_antes_do_congelamento()
    impedida = replace(
        prov(a.ORDEM, situacao=a.IMPEDIDO, sua=False, chave=("o",)), quem_resolve=a.RETIFICA
    )
    dados.providencias = [impedida]
    centro = compor(dados)
    assert [i.p for i in centro.impedidas] == [impedida]
    assert not centro.suas and not centro.de_outros
    assert centro.onde_detalhe == "1 está impedida."
    assert centro.impedidas[0].p.texto_de_quem_resolve == a.PAPEIS[a.RETIFICA]
    [classificacao] = [f for f in centro.fases if f.chave == c.CLASSIFICACAO]
    assert classificacao.impedidas
