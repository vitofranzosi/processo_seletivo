"""O catálogo da 069 e o registro das apresentações (FR-1367, R-001, R-002).

O que estes testes protegem: que o catálogo vigente tem a ordem e os títulos do *Catálogo
apresentado* da spec, **sem mudar chave, tipo, origem nem identidade** — é pela chave que o texto
de um rascunho fica na seção em que foi escrito, e que a Retificação confere a topologia —; que as
seções reunidas são as da spec; e que a apresentação de um snapshot sai da assinatura do catálogo
em que ele nasceu, com tudo o que não é a assinatura da `069` caindo na plana.
"""

import uuid

from processo_seletivo.editais.domain import secoes

# A ordem e os títulos do *Catálogo apresentado* (spec, D-001).
CATALOGO_APRESENTADO = [
    ("apresentacao", "Apresentação"),
    ("disposicoes-preliminares", "Disposições preliminares"),
    ("informacoes-gerais", "Informações gerais"),
    ("publico-alvo", "Público-alvo"),
    ("requisitos-gerais", "Requisitos gerais"),
    ("perfis", "Quantas vagas há, e onde?"),
    ("cronograma", "Cronograma"),
    ("inscricao", "Como se inscrever?"),
    ("atendimento-pcd", "Atendimento à pessoa com deficiência"),
    ("documentos-exigidos", "Quais documentos enviar?"),
    ("classificacao", "Como será a seleção?"),
    ("etapas", "Etapas de avaliação"),
    ("verificacao-autodeclaracao", "Verificação da autodeclaração"),
    ("recursos", "Como recorrer?"),
    ("convocacao", "Como será a convocação?"),
    ("matricula", "Como será a matrícula?"),
    ("acesso-ao-curso", "Acesso ao curso"),
    ("homologacao-matricula", "Homologação da matrícula"),
    ("certificado", "Certificado"),
    ("prazo-de-validade", "Prazo de validade"),
    ("anexos", "Anexos"),
    ("disposicoes-finais", "Disposições finais"),
]


def _snapshot(catalogo):
    return {
        "sections": [
            {"key": secao.key, "title": secao.title, "order": secao.order, "type": secao.type}
            for secao in catalogo
        ]
    }


def test_o_catalogo_vigente_tem_a_ordem_e_os_titulos_apresentados():
    assert [(secao.key, secao.title) for secao in secoes.CATALOGO] == CATALOGO_APRESENTADO
    assert [secao.order for secao in secoes.CATALOGO] == list(range(1, 23))


def test_informacoes_gerais_serve_a_todo_edital():
    """Clarify, Q3: "Informações gerais", e não "sobre o curso" — a seleção de bolsista também."""
    assert secoes.POR_CHAVE["informacoes-gerais"].title == "Informações gerais"


def test_chaves_tipos_e_origens_sao_os_da_054():
    """FR-1367: só o título e a ordem mudam; a identidade do texto e da topologia fica."""
    da_054 = {secao.key: secao for secao in secoes.CATALOGO_DA_054}
    assert set(da_054) == set(secoes.POR_CHAVE)
    for secao in secoes.CATALOGO:
        anterior = da_054[secao.key]
        assert (secao.type, secao.source) == (anterior.type, anterior.source), secao.key


def test_a_identidade_uuid5_nao_depende_do_catalogo():
    edital = uuid.UUID("0b8a3c56-7f43-4a54-9a9b-5f0a1c2d3e4f")
    for secao in secoes.CATALOGO_DA_054:
        assert secoes.identidade(edital, secao.key) == uuid.uuid5(
            secoes.NAMESPACE, f"{edital}:{secao.key}"
        )


def test_as_secoes_apresentadas_sao_as_da_spec():
    """FR-1368: as seções reunidas sob a pergunta, e cada regra gerada na seção que trata dela."""
    por_titulo = {entrada.titulo: entrada for entrada in secoes.APRESENTACAO}
    assert list(por_titulo) == [
        "Disposições preliminares",
        "Informações gerais",
        "Quem pode se inscrever?",
        "Quantas vagas há, e onde?",
        "Cronograma",
        "Como se inscrever?",
        "Quais documentos enviar?",
        "Como será a seleção?",
        "Como recorrer?",
        "Como será a convocação?",
        "Como será a matrícula?",
        "Certificado",
        "Prazo de validade",
        "Anexos",
        "Disposições finais",
    ]
    quem = por_titulo["Quem pode se inscrever?"]
    assert quem.principal is None
    assert quem.membros == ("publico-alvo", "requisitos-gerais")
    assert secoes.REQUISITOS_DOS_PERFIS in quem.gerados

    inscricao = por_titulo["Como se inscrever?"]
    assert inscricao.principal == "inscricao"
    assert inscricao.membros == ("atendimento-pcd",)
    for lugar in (secoes.PERIODO, secoes.DADOS_DECLARADOS, secoes.TETO):
        assert lugar in inscricao.gerados

    selecao = por_titulo["Como será a seleção?"]
    assert selecao.principal == "classificacao"
    assert selecao.membros == ("verificacao-autodeclaracao",)
    for lugar in (secoes.REGRAS_DOS_MARCOS, secoes.DADOS_DO_SORTEIO, secoes.ETAPAS):
        assert lugar in selecao.gerados

    assert secoes.RECURSO_DOS_MARCOS in por_titulo["Como recorrer?"].gerados
    assert secoes.FORMA_DE_CONVOCACAO in por_titulo["Como será a convocação?"].gerados
    matricula = por_titulo["Como será a matrícula?"]
    assert matricula.membros == ("acesso-ao-curso", "homologacao-matricula")
    assert secoes.REQUERIMENTO in matricula.gerados
    # O lembrete do Requerimento sai em Documentos e na Inscrição (contrato do documento §5).
    assert secoes.LEMBRETE_DO_REQUERIMENTO in por_titulo["Quais documentos enviar?"].gerados
    assert secoes.LEMBRETE_DO_REQUERIMENTO in inscricao.gerados


def test_toda_chave_do_catalogo_tem_lugar_na_apresentacao():
    """Nenhuma seção some: cada chave é principal, membro, o preâmbulo ou as Etapas."""
    com_lugar = {"apresentacao", secoes.CHAVE_DAS_ETAPAS}
    for entrada in secoes.APRESENTACAO:
        if entrada.principal:
            com_lugar.add(entrada.principal)
        com_lugar.update(entrada.membros)
    assert com_lugar == set(secoes.POR_CHAVE)


def test_a_principal_sai_no_comeco_salvo_onde_as_partes_a_poem():
    """Recurso e convocação: a regra do sistema antes do texto de quem redigiu (contrato §5)."""
    por_titulo = {entrada.titulo: entrada for entrada in secoes.APRESENTACAO}
    assert por_titulo["Como recorrer?"].ordem == (secoes.RECURSO_DOS_MARCOS, "recursos")
    assert por_titulo["Como será a convocação?"].ordem == (secoes.FORMA_DE_CONVOCACAO, "convocacao")
    assert por_titulo["Como se inscrever?"].ordem[0] == "inscricao"


def test_a_assinatura_da_069_e_por_perguntas():
    assert secoes.apresentacao_de(_snapshot(secoes.CATALOGO_DA_069)) == secoes.POR_PERGUNTAS


def test_a_assinatura_da_054_e_plana():
    assert secoes.apresentacao_de(_snapshot(secoes.CATALOGO_DA_054)) == secoes.PLANA


def test_assinatura_desconhecida_cai_na_plana():
    """R-001: o registro é explícito, e o que ele não conhece sai como sempre saiu."""
    misturado = _snapshot(secoes.CATALOGO_DA_069)
    misturado["sections"][3]["title"] = "Público-Alvo"
    assert secoes.apresentacao_de(misturado) == secoes.PLANA
    assert secoes.apresentacao_de({}) == secoes.PLANA
    assert secoes.apresentacao_de({"sections": None}) == secoes.PLANA
    sem_uma = _snapshot(secoes.CATALOGO_DA_069)
    del sem_uma["sections"][5]
    assert secoes.apresentacao_de(sem_uma) == secoes.PLANA


def test_o_registro_nao_e_o_catalogo_vigente():
    """Uma mudança futura do catálogo não pode devolver em silêncio os Editais da 069 à plana."""
    assert secoes.APRESENTACOES == {secoes.assinatura(secoes.CATALOGO_DA_069): secoes.POR_PERGUNTAS}


def test_os_destinos_dos_titulos_da_054_apontam_para_secoes_apresentadas():
    """R-013: cada título de antes leva a seções que existem; "Perfis de Vaga" foi repartida."""
    titulos = {entrada.titulo for entrada in secoes.APRESENTACAO}
    da_054 = {secao.title for secao in secoes.CATALOGO_DA_054}
    for antigo, destinos in secoes.DESTINOS_DOS_TITULOS_DA_054.items():
        assert antigo in da_054, antigo
        assert destinos and set(destinos) <= titulos, antigo
    assert len(secoes.DESTINOS_DOS_TITULOS_DA_054["Perfis de Vaga"]) == 3
