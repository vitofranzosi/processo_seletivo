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

from processo_seletivo.publicacoes.infrastructure.pdf import (
    AutoridadeSignataria,
    render_edital_pdf,
)

HASH = "a" * 64

# Depois da `008`, compor em modo publicado **exige** a autoridade signatária do ato (FR-035).
# Ela é contexto de publicação, não conteúdo: repeti-la em quarenta chamadas só faria ruído, e
# esconderia os poucos casos em que ela é o assunto do teste — esses chamam `render_edital_pdf`
# diretamente.
AUTORIDADE_DA_SUITE = AutoridadeSignataria(nome="Reitora do Ifes", cargo="Reitora")


def documento(conteudo, content_hash=HASH, *, modo=None, **kwargs):
    """Compõe como a publicação compõe, com a autoridade que esta suíte usa."""
    if modo is not None:
        return render_edital_pdf(conteudo, content_hash, modo=modo, **kwargs)
    kwargs.setdefault("autoridade", AUTORIDADE_DA_SUITE)
    return render_edital_pdf(conteudo, content_hash, **kwargs)
TEXTO_PDF = re.compile(rb"\((.*?)\) Tj", re.DOTALL)


def texto_de(pdf: bytes) -> str:
    """Extrai o texto realmente desenhado, não o que se supõe ter sido escrito."""
    return "\n".join(
        parte.replace(b"\\(", b"(").replace(b"\\)", b")").decode("cp1252")
        for parte in TEXTO_PDF.findall(pdf)
    )


DESENHADA = re.compile(
    rb"BT /(F\d) ([\d.]+) Tf ([\d.]+) [\d.]+ Td \((.*?)\) Tj ET", re.DOTALL
)


def linhas_desenhadas(pdf: bytes) -> list[tuple[str, str, float, float]]:
    """Cada linha com a fonte, o corpo e o recuo com que foi desenhada.

    `texto_de` responde "o que está escrito"; a `008` também precisa responder "com que forma" —
    negrito, corpo tipográfico e posição são requisito, não decoração.
    """
    from processo_seletivo.publicacoes.infrastructure.pdf import MARGEM

    return [
        (
            texto.replace(b"\\(", b"(").replace(b"\\)", b")").decode("cp1252"),
            fonte.decode(),
            float(tamanho),
            float(x) - MARGEM,
        )
        for fonte, tamanho, x, texto in DESENHADA.findall(pdf)
    ]


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
    """Dois Perfis, o segundo caindo no rodapé da primeira página (T008, FR-020).

    Os dois são enxutos de propósito: é essa proporção que faz o título do segundo caber no fim da
    página e o corpo dele não. Sem a paginação por bloco, `TEC-LAB` abre no rodapé da página 1 com
    duas linhas abaixo e continua na página 2 — que é o defeito editorial observado no documento
    gerado antes desta feature.
    """
    base = snapshot()
    primeiro = {
        **base["profiles"][0],
        "duties": "",
        "workload": "",
        "compensation": "",
        "requirements": ["Mestrado em Computação ou área afim"],
    }
    segundo = {
        **base["profiles"][0],
        "id": "33333333-3333-3333-3333-33333333aaaa",
        "code": "TEC-LAB",
        "name": "Técnico de Laboratório",
        "description": "Apoio técnico aos laboratórios de Informática.",
        "requirements": ["Ensino médio técnico em Informática"],
        "duties": "",
        "workload": "",
        "compensation": "",
        "competitionModalities": [],
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
    """**Forma atualizada pela `008`/US2**: a identificação virou quadro, e rótulo e valor passaram
    a ser células. O que o teste guarda é o conteúdo, e ele continua todo presente.
    """
    texto = texto_de(documento(snapshot(), HASH))
    perfil = snapshot()["profiles"][0]
    assert perfil["code"] in texto
    assert perfil["name"] in texto
    assert perfil["description"] in texto
    assert perfil["locality"] in texto
    assert perfil["requirements"][0] in texto
    assert "Vagas imediatas" in texto and "3" in texto
    assert "limitado em 6" in texto


def test_document_reproduces_competition_modalities_and_their_normative_rule():
    """FR-013: a Regra Normativa é conteúdo do Edital e precisa constar do documento."""
    texto = texto_de(documento(snapshot(), HASH))
    assert "PPP" in texto
    assert "Pessoas pretas, pardas e indígenas" in texto
    assert "Lei 12.990/2014" in texto
    assert "2014-06-09" in texto
    # **Forma atualizada pela `008`/US2**: a frase corrida `Regra Normativa — fundamento: …;
    # versão: …; percentual: …` virou tabela. O valor continua obrigatório e continua em
    # português — a entrada é `"20.0000"` e é o documento que a escreve.
    assert "20%" in texto
    assert "20.0000" not in texto


def test_document_reproduces_the_schedule_with_institutional_dates():
    texto = texto_de(documento(snapshot(), HASH))
    assert "Período de inscrições" in texto
    assert "INSCRICAO" in texto
    # America/Sao_Paulo, conforme a zona institucional.
    assert "01/09/2026 09:00" in texto
    assert "20/09/2026 23:59" in texto


def test_document_preserves_portuguese_accents():
    """Documento oficial brasileiro não pode trocar acento por interrogação."""
    texto = texto_de(documento(snapshot(), HASH))
    for esperado in ("Informática", "inscrições", "indígenas", "Seleção", "ESPÍRITO"):
        assert esperado in texto, esperado
    # A versão anterior codificava em ASCII e produzia exatamente estas formas mutiladas.
    for mutilado in ("Inform?tica", "inscri??es", "ind?genas", "Sele??o", "ESP?RITO"):
        assert mutilado not in texto, mutilado


def test_a_declaracao_de_integridade_identifica_sem_expor_uuid():
    """FR-004: o SHA-256 fica porque prova; o UUID sai porque não prova nada a quem lê.

    O identificador continua no snapshot — o que muda é o que se **imprime**.
    """
    pdf = documento(snapshot(), HASH)
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
    texto = texto_de(documento(conteudo, HASH))

    assert conteudo["processoCode"] in texto
    assert conteudo["processoTitle"] in texto


def test_the_same_snapshot_always_produces_the_same_bytes():
    """Determinismo é o que torna a cadeia verificável: o hash do documento não pode variar."""
    assert documento(snapshot(), HASH) == documento(snapshot(), HASH)


@pytest.mark.parametrize(
    "alteracao",
    [
        {"title": "Outro título"},
        {"profiles": []},
        {"schedule": []},
    ],
)
def test_any_change_in_the_version_changes_the_document(alteracao):
    assert documento(snapshot(), HASH) != documento(snapshot(**alteracao), HASH)


def test_long_content_paginates_and_every_page_is_numbered():
    muitos = snapshot(
        profiles=[
            {**snapshot()["profiles"][0], "code": f"P{indice:02d}", "id": str(indice)}
            for indice in range(1, 26)
        ]
    )
    pdf = documento(muitos, HASH)
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
    texto = texto_de(documento(snapshot(profiles=[], schedule=[], stages=[]), HASH))

    assert "PERFIS DE VAGA" not in texto
    assert "CRONOGRAMA" not in texto
    assert "ETAPAS DE AVALIAÇÃO" not in texto
    # As textuais continuam lá: o texto institucional não depende de dado estruturado.
    assert "DISPOSIÇÕES PRELIMINARES" in texto


def test_documento_segue_a_ordem_das_secoes_do_conteudo():
    """FR-038: a ordem do documento é conteúdo normativo, e não a ordem do código."""
    texto = texto_de(documento(snapshot(), HASH))
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
    """**Forma da apresentação, atualizada pela `008`/US1**: a Etapa deixou de ter número próprio
    e passou a ser subseção da seção que a contém (FR-013). O que ela afirma — caráter, peso e
    nota mínima presentes — é invariante e continua.
    """
    texto = texto_de(documento(snapshot(), HASH))
    mae = int(re.search(r"^(\d+)\. ETAPAS DE AVALIAÇÃO", texto, re.M).group(1))
    assert f"{mae}.1 Prova didática" in texto
    # **Forma atualizada pela `008`/US3**: a frase corrida virou pares rótulo-valor (FR-027), e a
    # referência ao Cronograma virou a linha "Realização". Os fatos que este teste guarda —
    # caráter, peso, nota mínima presentes, forma canônica ausente e data derivada do Evento —
    # são invariantes e continuam.
    assert "eliminatória e classificatória" in texto
    assert "Peso" in texto and "Nota mínima" in texto
    assert "2.0000" not in texto and "7.0000" not in texto
    assert "INSCRICAO" in texto and "01/09/2026 09:00" in texto


def test_parentheses_in_content_do_not_corrupt_the_document():
    """Parêntese é delimitador de string em PDF: sem escape, o arquivo quebra."""
    pdf = documento(snapshot(title="Edital (retificado) 07/2026"), HASH)
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
    texto = texto_de(documento(snapshot(sections=secoes_editadas), HASH))

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
    linhas = texto_de(documento(snapshot(sections=secoes_editadas), HASH)).splitlines()

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

    texto = texto_de(documento(vazio, HASH))

    assert "Atribuições" not in texto
    assert "Carga horária:" not in texto
    assert "Remuneração:" not in texto


def test_perfil_com_os_campos_institucionais_os_imprime_preservando_paragrafos():
    conteudo = snapshot()
    conteudo["profiles"][0]["duties"] = "Ministrar aulas.\nOrientar projetos."
    conteudo["profiles"][0]["workload"] = "40 horas semanais"
    conteudo["profiles"][0]["compensation"] = "R$ 4.200,00 mensais"

    texto = texto_de(documento(conteudo, HASH))

    # **Forma atualizada pela `008`/US2**: o rótulo perdeu os dois-pontos ao virar cabeçalho de
    # sub-bloco. O que o teste guarda — o conteúdo presente e os parágrafos preservados — é
    # invariante e não mudou.
    assert "Atribuições" in texto
    assert "Ministrar aulas." in texto
    assert "Orientar projetos." in texto
    assert "Carga horária: 40 horas semanais" in texto
    assert "Remuneração: R$ 4.200,00 mensais" in texto


# ---------------------------------------------------------------------------
# 008 / US1 — Identidade institucional, hierarquia e numeração normativa
# ---------------------------------------------------------------------------


def test_a_largura_de_texto_usa_metrica_real_e_nao_estimativa():
    """FR-002: sem largura real não há centralização, coluna nem alinhamento possíveis.

    As larguras conferidas são as métricas das fontes base-14, que são fixas — é a mesma razão
    pela qual o documento pode declarar Helvetica sem embutir arquivo de fonte. Se a tabela for
    transcrita errada, é aqui que se vê: `M` é largo, `i` é estreito, e o espaço fica entre os dois.
    """
    from processo_seletivo.publicacoes.infrastructure.pdf import NEGRITO, REGULAR, largura

    assert largura("M", 1000, REGULAR) == 833
    assert largura("i", 1000, REGULAR) == 222
    assert largura(" ", 1000, REGULAR) == 278
    assert largura("M", 1000, NEGRITO) == 833

    # Acentuação não muda o avanço: em Helvetica o glifo composto tem a largura da base. É o que
    # permite medir português sem uma tabela paralela — e o que uma estimativa por caractere
    # também acertaria por acaso, mas pelas razões erradas.
    assert largura("a", 1000, REGULAR) == largura("á", 1000, REGULAR)
    assert largura("c", 1000, REGULAR) == largura("ç", 1000, REGULAR)

    # A propriedade que interessa ao documento: proporcionalidade ao corpo tipográfico.
    assert largura("Edital", 20, REGULAR) == 2 * largura("Edital", 10, REGULAR)


def test_nenhuma_linha_do_documento_ultrapassa_a_margem():
    """FR-002 e FR-029: a linha mais larga do cenário-base cabe na área útil.

    A estimativa anterior — contar caracteres e multiplicar por um fator médio — errava por
    excesso em texto com muitas letras largas. Este teste é o que torna o erro visível.
    """
    from processo_seletivo.publicacoes.infrastructure.pdf import (
        LARGURA,
        MARGEM,
        largura,
    )

    util = LARGURA - 2 * MARGEM
    for pdf in (documento(snapshot(), HASH), documento(dois_perfis(), HASH)):
        for linha, fonte, tamanho, recuo in linhas_desenhadas(pdf):
            assert largura(linha, tamanho, fonte) + recuo <= util + 0.5, linha


def test_a_primeira_pagina_identifica_a_instituicao_o_ato_e_o_objeto():
    """FR-005 a FR-007, calibrados contra os Editais 62 e 73 do Cefor.

    Nos dois alvos a hierarquia vem da **forma** — negrito, caixa alta, centralização — e não do
    tamanho: o ato está em corpo próximo ao do texto. Exigir "o maior corpo da página" produziria
    um título fora do padrão institucional.
    """
    texto = texto_de(documento(snapshot(), HASH))
    linhas = [linha for linha, _, _, _ in linhas_desenhadas(documento(snapshot(), HASH))]

    assert "MINISTÉRIO DA EDUCAÇÃO" in texto
    assert "INSTITUTO FEDERAL DO ESPÍRITO SANTO" in texto
    assert "EDITAL Nº 07/2026" in texto

    # A ordem: identificação institucional antes do ato, ato antes de qualquer conteúdo normativo.
    ministerio = linhas.index("MINISTÉRIO DA EDUCAÇÃO")
    ato = linhas.index("EDITAL Nº 07/2026")
    primeira_secao = next(i for i, linha in enumerate(linhas) if linha.startswith("1. "))
    assert ministerio < ato < primeira_secao

    # O ato é negrito e caixa alta; a identificação institucional é menor que o corpo do texto.
    assert any(
        linha == "EDITAL Nº 07/2026" and fonte == "F2"
        for linha, fonte, _, _ in linhas_desenhadas(documento(snapshot(), HASH))
    )
    corpo = next(
        tamanho
        for linha, _, tamanho, _ in linhas_desenhadas(documento(snapshot(), HASH))
        if linha.startswith("O Instituto Federal")
    )
    institucional = next(
        tamanho
        for linha, _, tamanho, _ in linhas_desenhadas(documento(snapshot(), HASH))
        if linha == "MINISTÉRIO DA EDUCAÇÃO"
    )
    assert institucional < corpo


def test_as_secoes_normativas_sao_numeradas_em_sequencia_continua():
    """FR-010 e FR-011: a numeração é atribuída **depois** da filtragem.

    O cenário-base tem todas as seções e não revelaria o defeito. O cenário sem Etapas revela: a
    seção gerada não é materializada, e numerar durante a iteração produziria `5.`, `7.`, `8.` —
    no primeiro Edital real que não tivesse tudo preenchido.
    """
    import re as _re

    from processo_seletivo.publicacoes.infrastructure.pdf import CORPO_SECAO

    for conteudo in (snapshot(), sem_etapas()):
        # Título de seção tem forma própria — negrito, no corpo da seção. Casar só pelo texto
        # apanharia o Cronograma, cujos Eventos também abrem com número e caixa alta.
        numeros = [
            int(_re.match(r"(\d+)\. ", linha).group(1))
            for linha, fonte, tamanho, _ in linhas_desenhadas(documento(conteudo, HASH))
            if fonte == "F2" and tamanho == CORPO_SECAO and _re.match(r"\d+\. ", linha)
        ]
        assert numeros == list(range(1, len(numeros) + 1)), numeros
        assert len(numeros) >= 9

    assert "ETAPAS DE AVALIAÇÃO" not in texto_de(documento(sem_etapas(), HASH))


def test_as_subsecoes_derivam_do_numero_da_secao_mae_ja_resolvido():
    """FR-013: `6.1`, `6.2` — e acompanham quando a seção-mãe muda de número.

    A Etapa não tem número próprio: ela tem posição dentro de uma seção cuja numeração só existe
    depois da filtragem. Fixar `6.` seria repetir, uma camada abaixo, o defeito que FR-011 corrige.
    """
    import re as _re

    texto = texto_de(documento(snapshot(), HASH))
    mae = int(_re.search(r"^(\d+)\. ETAPAS DE AVALIAÇÃO", texto, _re.M).group(1))
    assert f"{mae}.1 Prova didática" in texto

    # Suprimir uma seção anterior desloca a seção-mãe, e a subseção acompanha.
    sem_perfis = snapshot(profiles=[])
    outro = texto_de(documento(sem_perfis, HASH))
    nova_mae = int(_re.search(r"^(\d+)\. ETAPAS DE AVALIAÇÃO", outro, _re.M).group(1))
    assert nova_mae == mae - 1
    assert f"{nova_mae}.1 Prova didática" in outro


def test_a_numeracao_nao_e_persistida_no_texto_da_secao():
    """FR-012: o número é da materialização, não do conteúdo homologado."""
    from processo_seletivo.editais.domain import secoes as catalogo

    for secao in catalogo.CATALOGO:
        if not secao.gerada:
            assert not secao.default_text.lstrip().startswith(("1.", "2.", "3.", "4.", "5."))
        assert not secao.title[0].isdigit()


# ---------------------------------------------------------------------------
# 008 / US2 — Perfil como quadro, e paginação que respeita fronteiras
# ---------------------------------------------------------------------------


def paginas_de(pdf: bytes) -> list[list[str]]:
    """O texto de cada página, na ordem — onde a paginação fica observável."""
    fluxos = re.findall(rb"stream\n(.*?)\nendstream", pdf, re.DOTALL)
    return [
        [
            parte.replace(b"\\(", b"(").replace(b"\\)", b")").decode("cp1252")
            for parte in TEXTO_PDF.findall(fluxo)
        ]
        for fluxo in fluxos
    ]


def test_um_perfil_que_cabe_inteiro_na_pagina_seguinte_nao_e_partido():
    """FR-020: mover é melhor que partir, quando mover resolve.

    O documento gerado antes desta feature iniciava o segundo Perfil no rodapé e continuava seus
    dados na página seguinte — o defeito editorial mais visível depois do cabeçalho.
    """
    paginas = paginas_de(documento(dois_perfis(), HASH))
    onde = [
        numero
        for numero, pagina in enumerate(paginas, 1)
        for linha in pagina
        if linha.startswith("TEC-LAB")
    ]
    assert len(onde) == 1, "o título do Perfil aparece em mais de uma página"
    pagina_do_titulo = onde[0]

    # **Tudo** o que é do segundo Perfil está na mesma página do seu título — inclusive o que hoje
    # cai na página seguinte. Conferir só a descrição deixaria o defeito passar: é justamente ela
    # que ainda cabe no rodapé, junto do título, enquanto vagas e requisitos escorregam.
    for marca in (
        "Apoio técnico aos laboratórios",
        "Campus Serra",
        "Vagas imediatas",
        "Ensino médio técnico em Informática",
    ):
        assert any(marca in linha for linha in paginas[pagina_do_titulo - 1]), (
            f"{marca!r} ficou fora da página do seu Perfil"
        )


def test_nenhum_titulo_de_perfil_fecha_a_pagina_sem_conteudo_abaixo():
    """FR-022: título órfão é o defeito que mais denuncia composição automática."""
    for conteudo in (snapshot(), dois_perfis(), perfil_maior_que_a_pagina()):
        for pagina in paginas_de(documento(conteudo, HASH)):
            corpo = [linha for linha in pagina if not linha.startswith("Edital 07/2026 ·")]
            if not corpo:
                continue
            ultima = corpo[-1]
            assert not re.match(r"^[A-Z]{3}-[A-Z]+ — ", ultima), (
                f"título de Perfil sozinho no fim da página: {ultima!r}"
            )


def test_um_subbloco_maior_que_a_pagina_quebra_por_dentro_e_a_composicao_conclui():
    """FR-021: a cascata precisa terminar sempre em alternativa exequível.

    Atribuições são texto livre e não têm limite. A primeira redação da spec exigia que nenhum
    sub-bloco fosse partido — regra que nenhum compositor cumpre quando o sub-bloco sozinho não
    cabe numa página. O que este teste prova não é elegância: é que a composição **termina**.
    """
    pdf = documento(perfil_maior_que_a_pagina(), HASH)
    paginas = paginas_de(pdf)

    assert len(paginas) >= 3, "o cenário extremo deveria ocupar várias páginas"
    texto = texto_de(pdf)
    assert "Atribuição 1:" in texto and "Atribuição 60:" in texto, "conteúdo perdido na quebra"
    assert "INTEGRIDADE" in texto, "a composição não chegou ao fim"


def test_o_quadro_de_modalidades_nao_inventa_celula_nem_perde_informacao():
    """FR-018 e FR-019: tabular não pode virar perder.

    O documento anterior imprimia `Regra Normativa — fundamento: …; versão: …; percentual: …`.
    A frase sai; **os dados não**. E ampla concorrência sem percentual não ganha célula
    construída para preencher a coluna.
    """
    texto = texto_de(documento(snapshot(), HASH))

    assert "Regra Normativa — fundamento:" not in texto
    for esperado in ("PPP", "Lei 12.990/2014", "20%", "2014-06-09"):
        assert esperado in texto, esperado

    # Ampla concorrência: sem regra normativa, e portanto sem percentual.
    ampla = {
        "id": "44444444-4444-4444-4444-4444444444aa",
        "code": "AC",
        "name": "Ampla concorrência",
        "description": "",
        "normativeRule": None,
    }
    perfil = {**snapshot()["profiles"][0], "competitionModalities": [ampla]}
    texto = texto_de(documento(snapshot(profiles=[perfil]), HASH))

    assert "Ampla concorrência" in texto
    # A coluna inteira desaparece quando nenhuma modalidade tem percentual: coluna vazia é
    # informação inexistente ocupando espaço (FR-019).
    assert "Percentual" not in texto
    assert "None" not in texto and "—%" not in texto


def test_a_paginacao_por_bloco_nao_perde_nem_duplica_conteudo():
    """Os modos de falha silenciosa de D-004, no único lugar em que se manifestam juntos.

    Medir com uma métrica e colocar com outra, bloco que cabe medido e não cabe colocado, cascata
    sobre bloco vazio, unidade indivisível maior que a página: nenhum desses quebra o documento —
    todos produzem um documento **errado**. O que os apanha é conservação de conteúdo.
    """
    for conteudo in (snapshot(), dois_perfis(), perfil_maior_que_a_pagina(), sem_etapas()):
        pdf = documento(conteudo, HASH)
        paginas = paginas_de(pdf)

        # Nenhuma página vazia: bloco vazio na cascata produziria uma.
        for numero, pagina in enumerate(paginas, 1):
            corpo = [linha for linha in pagina if not linha.startswith("Edital 07/2026 ·")]
            assert corpo, f"página {numero} saiu vazia"

        # Nada é recolocado ao mover um bloco: no cenário extremo cada atribuição é única, e
        # duplicá-la ou perdê-la é exatamente o que a decisão "cabe / não cabe" erra em silêncio.
        if conteudo is not snapshot():
            atribuicoes = [
                linha
                for pagina in paginas
                for linha in pagina
                if linha.startswith("Atribuição ")
            ]
            assert len(atribuicoes) == len(set(atribuicoes)), "atribuição repetida entre páginas"

        # Todo Perfil do conteúdo aparece exatamente uma vez.
        for perfil in conteudo["profiles"]:
            ocorrencias = sum(
                1
                for pagina in paginas
                for linha in pagina
                if linha.startswith(f"{perfil['code']} — ")
            )
            assert ocorrencias == 1, f"{perfil['code']} apareceu {ocorrencias} vezes"


# ---------------------------------------------------------------------------
# 008 / US3 — Cronograma e Etapas como informação estruturada
# ---------------------------------------------------------------------------


def cronograma_longo():
    """Eventos suficientes para a tabela atravessar a quebra de página (FR-026)."""
    modelo = snapshot()["schedule"][0]
    return snapshot(
        schedule=[
            {
                **modelo,
                "id": f"66666666-6666-6666-6666-6666666666{n:02d}",
                "order": n,
                "type": f"ETAPA{n:02d}",
                "description": f"Evento {n} do cronograma do processo seletivo",
                "endAt": None if n % 2 else modelo["endAt"],
            }
            for n in range(1, 41)
        ]
    )


def test_o_cronograma_e_apresentado_em_tabela_com_colunas_alinhadas():
    """FR-023: Cronograma é informação naturalmente tabular.

    O documento anterior o imprimia como parágrafos numerados. As colunas passam a existir, e
    passam a estar alinhadas — o que só é possível por causa da métrica de FR-002.
    """
    pdf = documento(snapshot(), HASH)
    texto = texto_de(pdf)

    for coluna in ("Evento", "Início", "Término"):
        assert coluna in texto, coluna

    # Alinhamento é uma propriedade de posição, não de texto: as células de uma coluna começam
    # todas no mesmo x. Conferir o texto não distinguiria uma tabela de uma lista.
    inicios = {
        round(recuo, 1)
        for linha, _, _, recuo in linhas_desenhadas(pdf)
        if linha.startswith("01/09/2026") or linha.startswith("05/10/2026")
    }
    assert len(inicios) == 1, f"a coluna de início não está alinhada: {inicios}"


def test_evento_pontual_nao_apresenta_termino_falso():
    """FR-024: a ausência é apresentada como ausência.

    A Prova tem início e não tem término. Inventar uma data para preencher a célula afirmaria ao
    candidato um prazo que o Edital não estabeleceu.
    """
    conteudo = snapshot()
    conteudo["schedule"] = conteudo["schedule"] + [
        {
            "id": "66666666-6666-6666-6666-66666666aaaa",
            "type": "PROVA",
            "description": "Prova didática",
            "startAt": "2026-10-05T14:00:00-03:00",
            "endAt": None,
            "order": 2,
            "status": "PLANEJADO",
        }
    ]
    texto = texto_de(documento(conteudo, HASH))

    assert "05/10/2026 14:00" in texto
    assert "None" not in texto
    # O período que tem término continua exibindo os dois instantes.
    assert "20/09/2026 23:59" in texto


def test_o_cabecalho_da_tabela_se_repete_na_continuacao_e_nunca_fica_orfao():
    """FR-026: uma tabela que vira a página continua legível.

    Sem repetição, a página seguinte mostra números sem dizer de que são. E um cabeçalho sozinho
    no rodapé é o mesmo defeito do título órfão, uma linha abaixo.
    """
    paginas = paginas_de(documento(cronograma_longo(), HASH))
    com_cabecalho = [
        numero for numero, pagina in enumerate(paginas, 1) if "Evento" in pagina
    ]
    com_evento = [
        numero
        for numero, pagina in enumerate(paginas, 1)
        if any(linha.startswith("ETAPA") for linha in pagina)
    ]

    assert len(com_evento) >= 2, "o cenário deveria fazer a tabela atravessar a quebra"
    assert com_cabecalho == com_evento, "o cabeçalho não acompanhou a continuação da tabela"

    for pagina in paginas:
        corpo = [linha for linha in pagina if not linha.startswith("Edital 07/2026 ·")]
        if corpo and corpo[-1] == "Evento":
            raise AssertionError("cabeçalho de tabela sozinho no fim da página")


def test_a_etapa_apresenta_carater_peso_e_nota_em_pares_rotulo_valor():
    """FR-027: a frase corrida sai; os valores ficam.

    `caráter: eliminatória e classificatória; peso: 2; nota mínima: 7` é escrita de banco de
    dados. O que o candidato precisa ler é um quadro.
    """
    texto = texto_de(documento(snapshot(), HASH))

    assert "caráter: eliminatória e classificatória; peso:" not in texto
    for rotulo in ("Caráter", "Peso", "Nota mínima"):
        assert rotulo in texto, rotulo
    assert "eliminatória e classificatória" in texto
    assert "2" in texto and "7" in texto

    # A data continua vindo do Evento vinculado, e não é digitada de novo na Etapa (FR-028).
    assert "01/09/2026 09:00" in texto

    # Etapa sem peso nem nota mínima não ganha rótulo vazio.
    sem_ponderacao = snapshot()
    sem_ponderacao["stages"][0] = {
        **sem_ponderacao["stages"][0], "weight": None, "minimumScore": None
    }
    texto = texto_de(documento(sem_ponderacao, HASH))
    assert "Peso" not in texto
    assert "Nota mínima" not in texto


# ---------------------------------------------------------------------------
# 008 / US4 — O documento sem acidentes editoriais
# ---------------------------------------------------------------------------


def test_nenhum_titulo_fecha_a_pagina_sem_conteudo_abaixo():
    """FR-030: vale para título de seção, de Perfil e de Etapa.

    Um título sozinho no rodapé é o defeito que mais denuncia composição automática — e é o mais
    fácil de deixar passar, porque só aparece em certas combinações de conteúdo.
    """
    for conteudo in (snapshot(), dois_perfis(), perfil_maior_que_a_pagina(), cronograma_longo()):
        for numero, pagina in enumerate(paginas_de(documento(conteudo, HASH)), 1):
            corpo = [linha for linha in pagina if not linha.startswith("Edital 07/2026 ·")]
            if not corpo:
                continue
            ultima = corpo[-1]
            titulo = (
                re.match(r"^\d+\. [A-ZÀ-Ú]", ultima)
                or re.match(r"^\d+\.\d+ ", ultima)
                or re.match(r"^[A-Z]{3}-[A-Z]+ — ", ultima)
            )
            assert not titulo, f"título sozinho no fim da página {numero}: {ultima!r}"


def test_o_espaco_antes_de_secao_bloco_e_paragrafo_e_decrescente():
    """FR-031: espaço semântico, não compactação.

    O leitor distingue seção nova, bloco dentro da seção e parágrafo pelo ar que os separa. Se os
    três forem iguais, o documento vira uma coluna indiferenciada de texto.
    """
    from processo_seletivo.publicacoes.infrastructure.pdf import (
        ANTES_DE_BLOCO,
        ANTES_DE_PARAGRAFO,
        ANTES_DE_SECAO,
    )

    assert ANTES_DE_SECAO > ANTES_DE_BLOCO > ANTES_DE_PARAGRAFO


def test_nenhuma_linha_ultrapassa_a_margem_em_nenhum_cenario():
    """FR-029: inclusive no cenário longo, e inclusive nas células das tabelas."""
    from processo_seletivo.publicacoes.infrastructure.pdf import LARGURA, MARGEM, largura

    util = LARGURA - 2 * MARGEM
    for conteudo in (
        snapshot(), dois_perfis(), perfil_maior_que_a_pagina(), cronograma_longo(), sem_etapas()
    ):
        pdf = documento(conteudo, HASH)
        for linha, fonte, tamanho, recuo in linhas_desenhadas(pdf):
            assert largura(linha, tamanho, fonte) + recuo <= util + 0.5, (
                f"{linha!r} ultrapassa a margem"
            )


# ---------------------------------------------------------------------------
# 008 / US5 — O documento termina como ato, não como relatório
# ---------------------------------------------------------------------------


AUTORIDADE = ("Reitora do Ifes", "Reitora")


def autoridade():
    from processo_seletivo.publicacoes.infrastructure.pdf import AutoridadeSignataria

    return AutoridadeSignataria(nome=AUTORIDADE[0], cargo=AUTORIDADE[1])


def test_o_documento_publicado_exibe_a_autoridade_registrada_na_publicacao():
    """FR-033: nome e cargo como o ato os registrou, sem transformação.

    O catálogo é a origem da escolha, não a fonte de verdade do que foi assinado — e é por isso
    que o compositor imprime o que recebe, e não o que consultaria.
    """
    texto = texto_de(documento(snapshot(), HASH, autoridade=autoridade()))

    assert AUTORIDADE[0] in texto
    assert AUTORIDADE[1] in texto
    # Sem praça e sem data: os dois exigiriam conceitos que o sistema não tem (FR-036).
    assert "Vitória" not in texto
    assert not re.search(r"\bde \d{4}\.", texto)


def test_compor_publicado_sem_autoridade_e_recusado():
    """FR-035: a garantia é do compositor, não de quem o chama.

    Publicar um ato administrativo sem quem o praticou é o erro que nenhum chamador deveria poder
    cometer por esquecimento. Mesmo desenho que a `007` deu ao hash da prévia, e pela mesma razão.
    """
    with pytest.raises(ValueError):
        render_edital_pdf(snapshot(), HASH)


def test_oferecer_autoridade_na_previa_e_recusado():
    """FR-035, o outro sentido: prévia não decorre de Publicação, e não tem quem assine.

    Ignorar em silêncio deixaria passar um chamador confuso; recusar diz o que está errado.
    """
    from processo_seletivo.publicacoes.infrastructure.pdf import MODO_PREVIA

    with pytest.raises(ValueError):
        render_edital_pdf(snapshot(), HASH, modo=MODO_PREVIA, autoridade=autoridade())


def test_a_previa_nao_compoe_bloco_de_autoridade():
    from processo_seletivo.publicacoes.infrastructure.pdf import MODO_PREVIA

    texto = texto_de(documento(snapshot(), HASH, modo=MODO_PREVIA))

    assert AUTORIDADE[0] not in texto
    assert "INTEGRIDADE" not in texto
    assert MARCA_DE_PREVIA_ESPERADA in texto


MARCA_DE_PREVIA_ESPERADA = "PRÉVIA — documento em elaboração, sem valor de publicação"


def test_a_verificacao_vem_depois_da_assinatura_e_nao_e_secao_do_edital():
    """FR-038 a FR-040: o mecanismo fica; a posição e o peso mudam.

    `Versão do schema: 3` como seção normativa era forma interna vazando para o corpo do ato. Ela
    continua no snapshot e no mecanismo — o que muda é o que se imprime como Edital.
    """
    pdf = documento(snapshot(), HASH, autoridade=autoridade())
    texto = texto_de(pdf)
    linhas = [linha for linha, _, _, _ in linhas_desenhadas(pdf)]

    assert "Versão do schema" not in texto
    assert HASH in texto, "o SHA-256 completo permanece"
    assert HASH[:16] in texto, "e o abreviado permanece no rodapé"
    assert "deriva integralmente da versão homologada" in texto

    assert linhas.index(AUTORIDADE[0]) < linhas.index("VERIFICAÇÃO DE INTEGRIDADE")

    # Discreto: o bloco de verificação usa o menor corpo do documento.
    corpos = {
        tamanho
        for linha, _, tamanho, _ in linhas_desenhadas(pdf)
        if linha.startswith("SHA-256")
    }
    from processo_seletivo.publicacoes.infrastructure.pdf import CORPO_NOTA

    assert corpos == {CORPO_NOTA}


def test_o_mesmo_snapshot_com_a_mesma_autoridade_produz_os_mesmos_bytes():
    """SC-013: o corpo normativo continua função pura do conteúdo publicado."""
    um = documento(snapshot(), HASH, autoridade=autoridade())
    outro = documento(snapshot(), HASH, autoridade=autoridade())
    assert um == outro

    from processo_seletivo.publicacoes.infrastructure.pdf import AutoridadeSignataria

    diferente = documento(
        snapshot(), HASH,
        autoridade=AutoridadeSignataria(nome="Diretora do Cefor", cargo="Diretora-Geral"),
    )
    assert diferente != um, "trocar quem assina tem de mudar o documento"
