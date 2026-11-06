"""A sequência de cada Perfil e a expectativa das Etapas, família a família (127, SC-1237, SC-1243).

**Sem colunas fixas** (FR-4103). A sequência vem da `jornada()` da `094`; as colunas são os pontos
dela, abertos em atos. Cada caso abaixo é uma linha da matriz de compatibilidade da spec: S1, S2,
S3, P1, P2, P3, CR e Perfis de famílias diferentes no mesmo Edital. S3 e P3 não existem no banco de
demonstração, e é por isso que a composição é pura: o cenário composto cabe num dicionário.
"""

from processo_seletivo.interface import andamento as a

SEM_GOVERNAR = {"governedStage": "NONE", "targetKind": "FIXED", "targetCount": 2}


def etapa(ident, nome, ordem, *, forma="PONTUADA", eliminatoria=False, **extra):
    base = {
        "id": ident,
        "name": nome,
        "order": ordem,
        "eliminatory": eliminatoria,
        "classificatory": forma == "PONTUADA",
        "evaluationsPerRegistration": 1,
    }
    if forma == "DECISORIA":
        base.update(forma="DECISORIA", rotuloFavoravel="Deferido", rotuloDesfavoravel="Indeferido")
    else:
        base.update(minimumScore="0.0000", maximumScore="10.0000", weight="1.0000")
    base.update(extra)
    return base


def sorteio(ident="m-sorteio", *, stages=(), habilitacao=None, cut=SEM_GOVERNAR):
    metodo = {"source": "LOTERIA_FEDERAL", "occurrence": "6116"}
    if habilitacao:
        metodo["qualifyingStageId"] = habilitacao
    return {
        "id": ident,
        "name": "Sorteio público",
        "orderProduction": "POR_SORTEIO",
        "stages": list(stages),
        "drawMethod": metodo,
        "cutRule": cut,
    }


def pontuacao(ident="m-final", *, stages, cut=SEM_GOVERNAR, desempate=()):
    return {
        "id": ident,
        "name": "Classificação final",
        "orderProduction": "POR_PONTUACAO",
        "stages": list(stages),
        "cutRule": cut,
        "tiebreakers": [
            {"order": n, "type": "MAIOR_PONTUACAO_NA_ETAPA", "parameters": {"stageId": e}}
            for n, e in enumerate(desempate, start=1)
        ],
    }


def conteudo(etapas, *perfis):
    return {
        "stages": etapas,
        "profiles": [
            {"id": f"p{n}", "name": f"Perfil {n}", "classificationMilestones": marcos}
            for n, marcos in enumerate(perfis, start=1)
        ],
    }


def tipos(c, perfil=0):
    perfil = c["profiles"][perfil]
    expectativa = a.expectativa_das_etapas(c, [perfil])
    pontos = a.sequencia_do_perfil(c["stages"], perfil["classificationMilestones"], expectativa)
    return [(p.tipo, p.titulo if p.tipo == a.ETAPA else "") for p in pontos], pontos


def test_s1_as_etapas_que_nada_consome_ficam_sem_efeito_e_o_sorteio_vem_primeiro():
    """S1 (35, 57): sorteio sem Etapa; as duas decisórias não têm ligação."""
    c = conteudo(
        [
            etapa("e1", "Análise da documentação", 1, forma="DECISORIA", eliminatoria=True),
            etapa("e2", "Autodeclaração", 2, forma="DECISORIA", eliminatoria=True),
        ],
        [sorteio()],
    )
    assert a.expectativa_das_etapas(c) == {"e1": a.SEM_EFEITO, "e2": a.SEM_EFEITO}
    sequencia, pontos = tipos(c)
    assert [t for t, _ in sequencia] == [
        "relacao",
        "semente",
        "sorteio",
        "corte",
        "apuracao",
        "resultado",
        "convocacao",
        "etapa",
        "etapa",
    ]
    assert {p.grupo for p in pontos if p.tipo == a.ETAPA} == {a.GRUPO_SEM_EFEITO}


def test_s2_a_etapa_de_visibilidade_nao_puxa_a_progressao():
    """D-019: a enumerada pelo sorteio é esperada, e a anterior a ela não (Prova objetiva, 26)."""
    c = conteudo(
        [etapa("p", "Prova objetiva", 1), etapa("t", "Análise de títulos", 2)],
        [sorteio(stages=["t"])],
    )
    assert a.expectativa_das_etapas(c) == {"p": a.SEM_EFEITO, "t": a.ESPERADA}


def test_s2_a_etapa_enumerada_pelo_sorteio_conta_so_se_consolida():
    """S2 (72): a decisória não eliminatória enumerada não consolida — "sem efeito"."""
    nao_consolida = conteudo(
        [etapa("e1", "Sorteio", 1, forma="DECISORIA", eliminatoria=False)],
        [sorteio(stages=["e1"])],
    )
    assert a.expectativa_das_etapas(nao_consolida) == {"e1": a.SEM_EFEITO}
    consolida = conteudo([etapa("e1", "Análise de títulos", 1)], [sorteio(stages=["e1"])])
    assert a.expectativa_das_etapas(consolida) == {"e1": a.ESPERADA}


def test_s3_a_etapa_de_habilitacao_vem_antes_da_relacao():
    """S3 (cenário composto, D-011): a `jornada()` põe o sorteio no começo; aqui ele vem depois."""
    c = conteudo(
        [etapa("hab", "Habilitação", 1, forma="DECISORIA", eliminatoria=True)],
        [sorteio(habilitacao="hab")],
    )
    assert a.expectativa_das_etapas(c) == {"hab": a.ESPERADA}
    sequencia, _ = tipos(c)
    assert sequencia[:2] == [("etapa", "Habilitação"), ("relacao", "")]


def test_p1_as_etapas_vem_antes_da_ordem_e_a_decisoria_depois_dela_nao_e_cobrada():
    """P1 (91): duas pontuadas enumeradas, e a Entrevista decisória depois do marco."""
    c = conteudo(
        [
            etapa("t", "Prova de Títulos", 1),
            etapa("d", "Desempenho Didático", 2),
            etapa("ent", "Entrevista", 3, forma="DECISORIA", eliminatoria=True),
        ],
        [pontuacao(stages=["t", "d"])],
    )
    assert a.expectativa_das_etapas(c) == {"t": a.ESPERADA, "d": a.ESPERADA, "ent": a.SEM_EFEITO}
    sequencia, _ = tipos(c)
    assert sequencia == [
        ("etapa", "Prova de Títulos"),
        ("etapa", "Desempenho Didático"),
        ("ordem", ""),
        ("corte", ""),
        ("apuracao", ""),
        ("resultado", ""),
        ("convocacao", ""),
        ("etapa", "Entrevista"),
    ]


def test_p2_a_etapa_governada_fica_entre_o_corte_e_a_apuracao():
    """P2 (51): o corte governa a Entrevista, que decide ocupação e convocação."""
    c = conteudo(
        [etapa("t", "Prova", 1), etapa("ent", "Entrevista", 2, eliminatoria=True)],
        [pontuacao(stages=["t"], cut={"governedStage": "ent", "targetKind": "FIXED"})],
    )
    assert a.expectativa_das_etapas(c) == {"t": a.ESPERADA, "ent": a.ESPERADA}
    sequencia, pontos = tipos(c)
    assert [t for t, _ in sequencia] == [
        "etapa",
        "ordem",
        "corte",
        "etapa",
        "apuracao",
        "resultado",
        "convocacao",
    ]
    assert pontos[3].grupo == a.GRUPO_DA_GOVERNADA


def test_p3_dois_marcos_no_perfil_um_grupo_de_colunas_por_marco():
    """P3 (cenário composto): Etapa → marco 1 → corte → Etapa governada → marco 2."""
    c = conteudo(
        [etapa("e1", "Prova escrita", 1), etapa("e2", "Prova oral", 2, eliminatoria=True)],
        [
            pontuacao("m1", stages=["e1"], cut={"governedStage": "e2", "targetKind": "FIXED"}),
            {**pontuacao("m2", stages=["e2"]), "name": "Classificação final"},
        ],
    )
    sequencia, pontos = tipos(c)
    assert [t for t, _ in sequencia] == [
        "etapa",
        "ordem",
        "corte",
        "etapa",
        "apuracao",
        "resultado",
        "convocacao",
        "ordem",
        "corte",
        "apuracao",
        "resultado",
        "convocacao",
    ]
    grupos = [g for g, _ in _grupos(pontos)]
    assert len([g for g in grupos if g.startswith(a.GRUPO_DA_PONTUACAO)]) == 2


def test_a_etapa_lida_so_pelo_desempate_e_esperada():
    """D-012: a ordem a lê (114), e "nada depende dela" seria falso."""
    c = conteudo(
        [etapa("p", "Prova", 1), etapa("ent", "Entrevista", 2)],
        [pontuacao(stages=["p"], desempate=["ent"])],
    )
    assert a.expectativa_das_etapas(c)["ent"] == a.ESPERADA


def test_a_progressao_torna_esperada_a_etapa_anterior_que_consolida():
    c = conteudo(
        [
            etapa("doc", "Análise documental", 1, eliminatoria=True),
            etapa("p", "Prova", 2),
            etapa("nao", "Decisória sem efeito", 0, forma="DECISORIA", eliminatoria=False),
        ],
        [pontuacao(stages=["p"])],
    )
    expectativa = a.expectativa_das_etapas(c)
    assert expectativa["doc"] == a.ESPERADA
    assert expectativa["nao"] == a.SEM_EFEITO, "não consolida, e não filtra ninguém"


def test_perfis_de_familias_diferentes_tem_cada_um_a_sua_sequencia():
    """Mista (51): um Perfil por pontuação e outro por sorteio no mesmo Edital."""
    c = conteudo([etapa("p", "Prova", 1)], [pontuacao(stages=["p"])], [sorteio()])
    pontuado, _ = tipos(c, 0)
    sorteado, _ = tipos(c, 1)
    assert pontuado[0] == ("etapa", "Prova") and ("ordem", "") in pontuado
    assert sorteado[0] == ("relacao", "") and ("ordem", "") not in sorteado
    # A Etapa vale para o Edital, mas não tem efeito no Perfil cujo marco não a lê.
    perfil_sorteado = c["profiles"][1]
    assert a.expectativa_das_etapas(c, [perfil_sorteado]) == {"p": a.SEM_EFEITO}


def test_cr_o_cadastro_de_reserva_nao_muda_a_sequencia():
    """CR: a falta de vaga se diz na célula (sem quadro), e não tirando a coluna."""
    c = conteudo([etapa("p", "Prova", 1)], [pontuacao(stages=["p"])])
    sequencia, _ = tipos(c)
    assert ("apuracao", "") in sequencia and ("convocacao", "") in sequencia


def _grupos(pontos):
    perfil = a.PerfilNoAndamento(perfil={}, forma="", listas=[], pontos=pontos, inscritos=0)
    return perfil.grupos
