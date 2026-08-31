"""FR-023 — o documento publicado corresponde integralmente à versão homologada.

A cadeia "dados estruturados → versão homologada → PDF publicado" precisa ser demonstrável:
cada Perfil, vaga, modalidade e Evento do snapshot tem de aparecer no documento, o mesmo
snapshot tem de produzir os mesmos bytes, e qualquer mudança tem de mudar o documento.

**Duas naturezas, tratadas de forma oposta (`008`, D-010).** A `008` muda a composição do
documento em cinco entregas, e a distinção abaixo é o que impede os dois erros simétricos:
quebrar uma garantia achando que era forma, e preservar uma forma achando que era garantia.

*Invariante* — o que a `008` **não pode** quebrar. Se um destes falhar, a entrega está errada:

- `test_the_same_snapshot_always_produces_the_same_bytes` — determinismo
- `test_any_change_in_the_version_changes_the_document` — sensibilidade ao conteúdo
- `test_document_preserves_portuguese_accents` — acentuação
- `test_o_snapshot_basta_para_compor_o_documento` — corpo normativo autossuficiente
- `test_a_declaracao_de_integridade_identifica_sem_expor_uuid` — nenhum identificador técnico
- `test_parentheses_in_content_do_not_corrupt_the_document` — escape do fluxo
- `test_paragrafos_da_secao_textual_sobrevivem_ao_documento` e
  `test_quebra_simples_de_linha_tambem_separa_paragrafo` — parágrafos da `006.1`
- `test_secao_gerada_sem_fonte_nao_aparece_no_documento` — supressão de seção vazia
- `test_perfil_sem_os_campos_institucionais_nao_imprime_rotulo_vazio` — omissão do inexistente
- `test_long_content_paginates_and_every_page_is_numbered` — rodapé e paginação

*Forma da apresentação* — o que a `008` **muda de propósito**. Cada um é atualizado na entrega
que o torna falso, nunca antes e nunca depois:

- `test_etapas_aparecem_com_caracter_peso_e_nota_minima` — a frase corrida vira pares
  rótulo-valor (entrega 3, FR-027)
- `test_document_reproduces_the_schedule_with_institutional_dates` — o parágrafo vira tabela
  (entrega 3, FR-023)
- `test_document_reproduces_every_profile_of_the_homologated_version` e
  `test_document_reproduces_competition_modalities_and_their_normative_rule` — as linhas viram
  quadro e tabela (entrega 2, FR-014 a FR-019)
- `test_documento_segue_a_ordem_das_secoes_do_conteudo` — os títulos ganham numeração
  (entrega 1, FR-010)
- `test_perfil_com_os_campos_institucionais_os_imprime_preservando_paragrafos` — o conteúdo é
  invariante; a disposição é forma (entrega 2)
"""

import re

import pytest

from processo_seletivo.publicacoes.infrastructure.pdf import render_edital_pdf

HASH = "a" * 64
TEXTO_PDF = re.compile(rb"\((.*?)\) Tj", re.DOTALL)


def texto_de(pdf: bytes) -> str:
    """Extrai o texto realmente desenhado, não o que se supõe ter sido escrito."""
    return "\n".join(
        parte.replace(b"\\(", b"(").replace(b"\\)", b")").decode("cp1252")
        for parte in TEXTO_PDF.findall(pdf)
    )


def secoes(edital_id="11111111-1111-1111-1111-111111111111"):
    """As seções do catálogo, como `edital_snapshot` as materializa.

    O documento é composto a partir delas: sem `sections` não há o que compor. Construí-las aqui a
    partir do catálogo, e não à mão, é o que impede que este arquivo e o snapshot real divirjam.
    """
    from processo_seletivo.editais.domain import secoes as catalogo

    return [
        {
            "id": str(catalogo.identidade(edital_id, secao.key)),
            "key": secao.key,
            "title": secao.title,
            "order": secao.order,
            "type": secao.type,
            **(
                {"source": secao.source}
                if secao.gerada
                else {"content": secao.default_text}
            ),
        }
        for secao in catalogo.CATALOGO
    ]


def snapshot(**alteracoes):
    base = {
        "schemaVersion": 2,
        "editalId": "11111111-1111-1111-1111-111111111111",
        "processoId": "22222222-2222-2222-2222-222222222222",
        "processoCode": "PS-DEMO-2026",
        "processoTitle": "Processo Seletivo Simplificado 2026",
        "number": "07",
        "year": 2026,
        "title": "Edital 07/2026 — Professor Substituto",
        "description": "Seleção simplificada para docência.",
        "profiles": [
            {
                "id": "33333333-3333-3333-3333-333333333333",
                "code": "DOC-INFO",
                "name": "Professor de Informática",
                "description": "Docência em Informática.",
                "requirements": ["Mestrado em Computação"],
                "immediateVacancies": 3,
                "reserveType": "LIMITED",
                "reserveLimit": 6,
                "locality": "Campus Serra",
                "classificationInformation": {},
                "callInformation": {},
                "competitionModalities": [
                    {
                        "id": "44444444-4444-4444-4444-444444444444",
                        "code": "PPP",
                        "name": "Pessoas pretas, pardas e indígenas",
                        "description": "",
                        "normativeRule": {
                            "id": "55555555-5555-5555-5555-555555555555",
                            "foundation": "Lei 12.990/2014",
                            "version": "2014-06-09",
                            "percentage": "20.0000",
                            "calculation": {},
                            "rounding": {},
                            "distribution": {},
                            "callRules": {},
                            "effectiveFrom": None,
                        },
                    }
                ],
            }
        ],
        "schedule": [
            {
                "id": "66666666-6666-6666-6666-666666666666",
                "type": "INSCRICAO",
                "description": "Período de inscrições",
                "startAt": "2026-09-01T09:00:00-03:00",
                "endAt": "2026-09-20T23:59:00-03:00",
                "order": 1,
                "status": "PLANEJADO",
            }
        ],
        "stages": [
            {
                "id": "77777777-7777-7777-7777-777777777777",
                "name": "Prova didática",
                "order": 1,
                "weight": "2.0000",
                "eliminatory": True,
                "classificatory": True,
                "minimumScore": "7.0000",
                "scheduleEventId": "66666666-6666-6666-6666-666666666666",
            }
        ],
        "sections": secoes(),
    }
    return {**base, **alteracoes}


# ---------------------------------------------------------------------------
# 008 — Os cenários que revelam o que o cenário-base esconde
#
# O cenário-base tem tudo preenchido e cabe em duas páginas, e por isso não exibe três defeitos
# que só aparecem em Edital real: numeração com lacuna, Perfil partido entre páginas e conteúdo
# maior que a página. Cada cenário abaixo existe para tornar um deles observável.
# ---------------------------------------------------------------------------


def sem_etapas():
    """Um Edital sem Etapas de Avaliação — a coleção é opcional (T007, FR-011).

    A seção gerada correspondente não é materializada, e é aí que a numeração atribuída durante a
    iteração produziria `5.`, `7.`, `8.`. É o único defeito desta feature que o cenário-base não
    revela: ele só se manifesta no Edital que não tem tudo.
    """
    return snapshot(stages=[])


def dois_perfis():
    """Dois Perfis, o segundo dimensionado para não caber no espaço restante (T008, FR-020).

    O primeiro Perfil recebe texto suficiente para empurrar o segundo para o fim da página. Sem a
    paginação por bloco, o segundo começa no rodapé e continua na página seguinte — que é o
    defeito editorial observado no documento gerado antes desta feature.
    """
    base = snapshot()
    primeiro = {
        **base["profiles"][0],
        "duties": "\n".join(
            f"Ministrar aulas, orientar e participar das atividades de ensino, "
            f"pesquisa e extensão do campus, na área {n}."
            for n in range(1, 9)
        ),
    }
    segundo = {
        **base["profiles"][0],
        "id": "33333333-3333-3333-3333-33333333aaaa",
        "code": "TEC-LAB",
        "name": "Técnico de Laboratório",
        "description": "Apoio técnico aos laboratórios de Informática.",
        "requirements": ["Ensino médio técnico em Informática", "Registro profissional ativo"],
        "duties": "Preparar e manter os laboratórios; apoiar as aulas práticas.",
    }
    return snapshot(profiles=[primeiro, segundo])


def perfil_maior_que_a_pagina():
    """Um sub-bloco que sozinho não cabe em uma página inteira (T009, FR-021).

    Atribuições são texto livre e não têm limite de tamanho. É o caso que tornava inexequível a
    primeira redação da spec — "nenhum sub-bloco é partido" — e que a cascata resolve descendo até
    a quebra entre linhas. O que este cenário prova não é elegância: é que a composição **conclui**.
    """
    base = snapshot()
    enorme = {
        **base["profiles"][0],
        "duties": "\n".join(
            f"Atribuição {n}: ministrar, orientar, avaliar, registrar e acompanhar as "
            f"atividades acadêmicas correspondentes, observada a legislação vigente."
            for n in range(1, 61)
        ),
    }
    return snapshot(profiles=[enorme])


def test_document_reproduces_every_profile_of_the_homologated_version():
    texto = texto_de(render_edital_pdf(snapshot(), HASH))
    perfil = snapshot()["profiles"][0]
    assert perfil["code"] in texto
    assert perfil["name"] in texto
    assert perfil["description"] in texto
    assert perfil["locality"] in texto
    assert perfil["requirements"][0] in texto
    assert "Vagas imediatas: 3" in texto
    assert "limitado em 6" in texto


def test_document_reproduces_competition_modalities_and_their_normative_rule():
    """FR-013: a Regra Normativa é conteúdo do Edital e precisa constar do documento."""
    texto = texto_de(render_edital_pdf(snapshot(), HASH))
    assert "PPP" in texto
    assert "Pessoas pretas, pardas e indígenas" in texto
    assert "Lei 12.990/2014" in texto
    assert "2014-06-09" in texto
    # `20%`: a entrada continua `"20.0000"` (linha 83) e é o documento que escreve em português.
    assert "percentual: 20%" in texto
    assert "20.0000" not in texto


def test_document_reproduces_the_schedule_with_institutional_dates():
    texto = texto_de(render_edital_pdf(snapshot(), HASH))
    assert "Período de inscrições" in texto
    assert "INSCRICAO" in texto
    # America/Sao_Paulo, conforme a zona institucional.
    assert "01/09/2026 09:00" in texto
    assert "20/09/2026 23:59" in texto


def test_document_preserves_portuguese_accents():
    """Documento oficial brasileiro não pode trocar acento por interrogação."""
    texto = texto_de(render_edital_pdf(snapshot(), HASH))
    for esperado in ("Informática", "inscrições", "indígenas", "Seleção", "ESPÍRITO"):
        assert esperado in texto, esperado
    # A versão anterior codificava em ASCII e produzia exatamente estas formas mutiladas.
    for mutilado in ("Inform?tica", "inscri??es", "ind?genas", "Sele??o", "ESP?RITO"):
        assert mutilado not in texto, mutilado


def test_a_declaracao_de_integridade_identifica_sem_expor_uuid():
    """FR-004: o SHA-256 fica porque prova; o UUID sai porque não prova nada a quem lê.

    O identificador continua no snapshot — o que muda é o que se **imprime**.
    """
    pdf = render_edital_pdf(snapshot(), HASH)
    texto = texto_de(pdf)

    assert HASH in texto
    assert HASH[:16] in texto  # rodapé de cada página
    assert "deriva integralmente da versão homologada" in texto
    assert "Edital 07/2026" in texto
    assert "PS-DEMO-2026" in texto
    assert "Processo Seletivo Simplificado 2026" in texto

    assert "11111111-1111-1111-1111-111111111111" not in texto
    assert "22222222-2222-2222-2222-222222222222" not in texto


def test_o_snapshot_basta_para_compor_o_documento():
    """SC-002a: nenhuma consulta ao banco — o conteúdo publicado é autossuficiente."""
    conteudo = snapshot()
    texto = texto_de(render_edital_pdf(conteudo, HASH))

    assert conteudo["processoCode"] in texto
    assert conteudo["processoTitle"] in texto


def test_the_same_snapshot_always_produces_the_same_bytes():
    """Determinismo é o que torna a cadeia verificável: o hash do documento não pode variar."""
    assert render_edital_pdf(snapshot(), HASH) == render_edital_pdf(snapshot(), HASH)


@pytest.mark.parametrize(
    "alteracao",
    [
        {"title": "Outro título"},
        {"profiles": []},
        {"schedule": []},
    ],
)
def test_any_change_in_the_version_changes_the_document(alteracao):
    assert render_edital_pdf(snapshot(), HASH) != render_edital_pdf(snapshot(**alteracao), HASH)


def test_long_content_paginates_and_every_page_is_numbered():
    muitos = snapshot(
        profiles=[
            {**snapshot()["profiles"][0], "code": f"P{indice:02d}", "id": str(indice)}
            for indice in range(1, 26)
        ]
    )
    pdf = render_edital_pdf(muitos, HASH)
    paginas = pdf.count(b"/Type /Page ")
    assert paginas >= 3, paginas
    texto = texto_de(pdf)
    for numero in range(1, paginas + 1):
        assert f"Página {numero} de {paginas}" in texto
    for indice in range(1, 26):
        assert f"P{indice:02d}" in texto, f"perfil P{indice:02d} não foi impresso"


def test_secao_gerada_sem_fonte_nao_aparece_no_documento():
    """A regra mudou na `006`, e a razão mudou junto.

    A `002` declarava "Nenhum Perfil registrado nesta versão", porque a alternativa era omitir a
    seção em silêncio. Com o catálogo, a seção passou a ter título próprio, e um título sobre nada
    não informa que não há nada — informa que alguém esqueceu de preencher.

    Para Perfis e Cronograma o caso nem chega ao documento publicado: a validação de publicação
    exige ao menos um de cada. Para Etapas, que são opcionais, um cabeçalho vazio seria falso.
    """
    texto = texto_de(render_edital_pdf(snapshot(profiles=[], schedule=[], stages=[]), HASH))

    assert "PERFIS DE VAGA" not in texto
    assert "CRONOGRAMA" not in texto
    assert "ETAPAS DE AVALIAÇÃO" not in texto
    # As textuais continuam lá: o texto institucional não depende de dado estruturado.
    assert "DISPOSIÇÕES PRELIMINARES" in texto


def test_documento_segue_a_ordem_das_secoes_do_conteudo():
    """FR-038: a ordem do documento é conteúdo normativo, e não a ordem do código."""
    texto = texto_de(render_edital_pdf(snapshot(), HASH))
    posicoes = [
        texto.index(titulo)
        for titulo in (
            "APRESENTAÇÃO",
            "DISPOSIÇÕES PRELIMINARES",
            "REQUISITOS GERAIS DE PARTICIPAÇÃO",
            "DA INSCRIÇÃO",
            "PERFIS DE VAGA",
            "ETAPAS DE AVALIAÇÃO",
            "CRITÉRIOS DE CLASSIFICAÇÃO",
            "CRONOGRAMA",
            "DOS RECURSOS",
            "DISPOSIÇÕES FINAIS",
        )
    ]
    assert posicoes == sorted(posicoes)


def test_etapas_aparecem_com_caracter_peso_e_nota_minima():
    texto = texto_de(render_edital_pdf(snapshot(), HASH))
    assert "1. Prova didática" in texto
    assert "eliminatória e classificatória" in texto
    assert "peso: 2" in texto
    assert "nota mínima: 7" in texto
    # A entrada carrega `"2.0000"` e `"7.0000"`; a forma canônica não chega ao papel (FR-003).
    assert "2.0000" not in texto and "7.0000" not in texto
    # A data vem do Evento vinculado, e não é digitada de novo na Etapa.
    assert "Conforme o Cronograma — INSCRICAO" in texto


def test_parentheses_in_content_do_not_corrupt_the_document():
    """Parêntese é delimitador de string em PDF: sem escape, o arquivo quebra."""
    pdf = render_edital_pdf(snapshot(title="Edital (retificado) 07/2026"), HASH)
    assert b"%%EOF" in pdf
    assert "Edital (retificado) 07/2026" in texto_de(pdf)


def test_paragrafos_da_secao_textual_sobrevivem_ao_documento():
    """O defeito que a demonstração navegável da `006` encontrou e a suíte não pegava.

    `_quebrar` reflui o texto por palavra e descartava toda a estrutura de espaço em branco: dois
    parágrafos digitados viravam um bloco corrido, em silêncio, no único texto livre do produto.
    """
    secoes_editadas = [
        {**s, "content": "Caberá recurso em dois dias úteis.\n\nO recurso será fundamentado."}
        if s["key"] == "recursos"
        else s
        for s in secoes()
    ]
    texto = texto_de(render_edital_pdf(snapshot(sections=secoes_editadas), HASH))

    linhas = texto.splitlines()
    assert "Caberá recurso em dois dias úteis." in linhas
    assert "O recurso será fundamentado." in linhas
    # A prova do defeito: antes, as duas frases saíam refluídas na mesma linha.
    assert not any(
        "dois dias úteis. O recurso" in linha for linha in linhas
    ), "os parágrafos foram colados de novo"


def test_quebra_simples_de_linha_tambem_separa_paragrafo():
    """Norma se escreve em linhas curtas; exigir linha em branco seria armadilha."""
    secoes_editadas = [
        {**s, "content": "I — ser brasileiro;\nII — estar em dia com as obrigações eleitorais;"}
        if s["key"] == "requisitos" or s["key"] == "recursos"
        else s
        for s in secoes()
    ]
    linhas = texto_de(render_edital_pdf(snapshot(sections=secoes_editadas), HASH)).splitlines()

    assert "I — ser brasileiro;" in linhas
    assert "II — estar em dia com as obrigações eleitorais;" in linhas


def test_perfil_sem_os_campos_institucionais_nao_imprime_rotulo_vazio():
    """T025/FR-015: um rótulo sobre nada não informa que não há nada.

    Informa que alguém esqueceu de preencher — e num Edital publicado isso seria falso, porque os
    três são opcionais por decisão (FR-012).
    """
    vazio = snapshot()
    for perfil in vazio["profiles"]:
        perfil["duties"] = ""
        perfil["workload"] = ""
        perfil["compensation"] = ""

    texto = texto_de(render_edital_pdf(vazio, HASH))

    assert "Atribuições:" not in texto
    assert "Carga horária:" not in texto
    assert "Remuneração:" not in texto


def test_perfil_com_os_campos_institucionais_os_imprime_preservando_paragrafos():
    conteudo = snapshot()
    conteudo["profiles"][0]["duties"] = "Ministrar aulas.\nOrientar projetos."
    conteudo["profiles"][0]["workload"] = "40 horas semanais"
    conteudo["profiles"][0]["compensation"] = "R$ 4.200,00 mensais"

    texto = texto_de(render_edital_pdf(conteudo, HASH))

    assert "Atribuições:" in texto
    assert "Ministrar aulas." in texto
    assert "Orientar projetos." in texto
    assert "Carga horária: 40 horas semanais" in texto
    assert "Remuneração: R$ 4.200,00 mensais" in texto
