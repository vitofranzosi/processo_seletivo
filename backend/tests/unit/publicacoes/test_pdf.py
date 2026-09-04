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
# Só os fluxos de conteúdo das páginas. Desde que o documento embute o brasão, varrer o arquivo
# inteiro alcançaria os bytes da imagem — que não são texto e não decodificam como tal.
CONTEUDO_DA_PAGINA = re.compile(rb"<< /Length \d+ >>\nstream\n(.*?)\nendstream", re.DOTALL)


def conteudo_das_paginas(pdf: bytes) -> bytes:
    return b"\n".join(CONTEUDO_DA_PAGINA.findall(pdf))


def texto_de(pdf: bytes) -> str:
    """Extrai o texto realmente desenhado, não o que se supõe ter sido escrito."""
    return "\n".join(
        parte.replace(b"\\(", b"(").replace(b"\\)", b")").decode("cp1252")
        for parte in TEXTO_PDF.findall(conteudo_das_paginas(pdf))
    )


DESENHADA = re.compile(
    rb"BT (?:[\d.]+ Tw )?/(F\d) ([\d.]+) Tf ([\d.]+) [\d.]+ Td \((.*?)\) Tj", re.DOTALL
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
        for fonte, tamanho, x, texto in DESENHADA.findall(conteudo_das_paginas(pdf))
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
            **({"source": secao.source} if secao.gerada else {"content": secao.default_text}),
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
    # **Materialização atualizada**: a versão da Regra Normativa saiu do ato. É proveniência, e
    # sai pela mesma razão que `schemaVersion` e os UUIDs saíram — o candidato lê o fundamento,
    # não a data de cadastro da regra. Continua no conteúdo publicado.
    assert "2014-06-09" not in texto
    # **Forma atualizada pela `008`/US2**: a frase corrida `Regra Normativa — fundamento: …;
    # versão: …; percentual: …` virou tabela. O valor continua obrigatório e continua em
    # português — a entrada é `"20.0000"` e é o documento que a escreve.
    assert "20%" in texto
    assert "20.0000" not in texto


def test_document_reproduces_the_schedule_with_institutional_dates():
    texto = texto_de(documento(snapshot(), HASH))
    # **Materialização atualizada**: o rótulo humano vai ao papel; a chave do tipo, não.
    # `INSCRICAO` é enumeração — no documento publicado ela não diz nada que a descrição já não
    # diga, e denuncia o sistema por trás do ato. Mesma decisão que tirou `PLANEJADO` na `007`.
    assert "Período de inscrições" in texto
    assert "INSCRICAO" not in texto
    # America/Sao_Paulo, conforme a zona institucional.
    assert "01/09/2026, às 9h" in texto
    assert "20/09/2026, às 23h59" in texto


def test_document_preserves_portuguese_accents():
    """Documento oficial brasileiro não pode trocar acento por interrogação."""
    texto = texto_de(documento(snapshot(), HASH))
    # **Forma atualizada pela calibração contra o Edital 146/2025**: a identificação do órgão
    # passou a caixa mista, como nos três alvos. O que este teste guarda é a **acentuação**, e
    # `Espírito` a exercita igualmente bem.
    for esperado in ("Informática", "inscrições", "indígenas", "Seleção", "Espírito"):
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
            # **Forma atualizada pela `008`**: a Apresentação virou preâmbulo — sem número e
            # sem cabeçalho —, como o ato enunciativo dos Editais de referência. O que ela diz
            # continua no documento; o que sai é o título dela.
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
    assert "INSCRICAO" not in texto
    assert "01/09/2026, às 9h" in texto


def test_parentheses_in_content_do_not_corrupt_the_document():
    """Parêntese é delimitador de string em PDF: sem escape, o arquivo quebra."""
    pdf = documento(snapshot(title="Edital (retificado) 07/2026"), HASH)
    assert b"%%EOF" in pdf
    # O ato vai em caixa alta, como nos alvos; o parêntese é que não pode corromper o fluxo.
    assert "EDITAL (RETIFICADO) 07/2026" in texto_de(pdf)


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
    assert not any("dois dias úteis. O recurso" in linha for linha in linhas), (
        "os parágrafos foram colados de novo"
    )


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

    assert "Ministério da Educação" in texto
    assert "Instituto Federal do Espírito Santo" in texto
    # O ato e o objeto são **uma** sentença, como nos três alvos: o título do cenário já abre por
    # "Edital", então é ele que anuncia o ato — imprimir os dois anunciaria o mesmo ato duas vezes.
    assert "EDITAL 07/2026 — PROFESSOR SUBSTITUTO" in texto
    assert texto.count("EDITAL") == 1

    # A ordem: identificação institucional antes do ato, ato antes de qualquer conteúdo normativo.
    ministerio = linhas.index("Ministério da Educação")
    ato = linhas.index("EDITAL 07/2026 — PROFESSOR SUBSTITUTO")
    primeira_secao = next(i for i, linha in enumerate(linhas) if linha.startswith("1. "))
    assert ministerio < ato < primeira_secao

    # O ato é negrito e caixa alta; a identificação do órgão é o **maior** texto da página.
    assert any(
        linha.startswith("EDITAL 07/2026") and fonte == "F2"
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
        if linha == "Ministério da Educação"
    )
    # **Calibração corrigida pelo Edital 146/2025**: a primeira redação tinha isto ao contrário, e
    # era o que fazia a abertura parecer nota de rodapé sob um título de relatório.
    assert institucional > corpo


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
        # Nove numeradas: as dez do catálogo menos a Apresentação, que é preâmbulo.
        assert len(numeros) >= 8

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
    fluxos = CONTEUDO_DA_PAGINA.findall(pdf)
    return [
        [
            parte.replace(b"\\(", b"(").replace(b"\\)", b")").decode("cp1252")
            for parte in TEXTO_PDF.findall(fluxo)
        ]
        for fluxo in fluxos
    ]


ALTURA_DA_LINHA = re.compile(
    rb"BT (?:[\d.]+ Tw )?/F\d [\d.]+ Tf [\d.]+ ([\d.]+) Td \(.*?\) Tj", re.DOTALL
)


def alturas_por_pagina(pdf: bytes) -> list[list[float]]:
    """As alturas em que cada página desenhou texto — onde a densidade fica observável."""
    return [
        [float(y) for y in ALTURA_DA_LINHA.findall(fluxo)]
        for fluxo in CONTEUDO_DA_PAGINA.findall(pdf)
    ]


def test_o_titulo_do_perfil_nunca_se_separa_do_que_ele_apresenta():
    """FR-020, na granularidade que a auditoria pediu.

    Manter o Perfil **inteiro** indivisível era proteção demais: com um Perfil longo, a seção
    inteira era empurrada e a página anterior terminava com um terço em branco. A unidade coesa é
    o título com o que ele apresenta; atribuições, requisitos e modalidades são fronteiras
    semânticas por onde a quebra pode passar.
    """
    paginas = paginas_de(documento(dois_perfis(), HASH))
    onde = [
        numero
        for numero, pagina in enumerate(paginas, 1)
        for linha in pagina
        if "TEC-LAB — " in linha and re.match(r"^\d+\.\d+ ", linha)
    ]
    assert len(onde) == 1, "o título do Perfil aparece em mais de uma página"
    assert any("Apoio técnico aos laboratórios" in linha for linha in paginas[onde[0] - 1]), (
        "o título ficou separado da descrição que ele apresenta"
    )


def test_a_paginacao_nao_deixa_um_terco_da_pagina_em_branco():
    """O critério de densidade da auditoria.

    `keep-together` protege o bloco; protegendo demais, ele deixa a página anterior quase vazia
    para preservar uma unidade que poderia ter sido quebrada numa fronteira semântica. Um Edital
    ocupa a página.
    """
    from processo_seletivo.publicacoes.infrastructure.pdf import RODAPE, TOPO

    util = TOPO - (RODAPE + 24)
    for conteudo in (snapshot(), dois_perfis(), cronograma_longo()):
        paginas = alturas_por_pagina(documento(conteudo, HASH))
        for numero, ys in list(enumerate(paginas, 1))[:-1]:
            corpo = [y for y in ys if y > RODAPE]
            if not corpo:
                continue
            ocupado = TOPO - min(corpo)
            assert ocupado >= util * 2 / 3, (
                f"a página {numero} usou só {ocupado / util:.0%} da área útil"
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
    assert "Verificação de integridade" in texto, "a composição não chegou ao fim"


def test_o_quadro_de_modalidades_nao_inventa_celula_nem_perde_informacao():
    """FR-018 e FR-019: tabular não pode virar perder.

    O documento anterior imprimia `Regra Normativa — fundamento: …; versão: …; percentual: …`.
    A frase sai; **os dados não**. E ampla concorrência sem percentual não ganha célula
    construída para preencher a coluna.
    """
    texto = texto_de(documento(snapshot(), HASH))

    assert "Regra Normativa — fundamento:" not in texto
    for esperado in ("PPP", "Lei 12.990/2014", "20%"):
        assert esperado in texto, esperado
    assert "2014-06-09" not in texto, "a versão da regra é proveniência, não matéria de Edital"

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
                linha for pagina in paginas for linha in pagina if linha.startswith("Atribuição ")
            ]
            assert len(atribuicoes) == len(set(atribuicoes)), "atribuição repetida entre páginas"

        # Todo Perfil do conteúdo aparece exatamente uma vez.
        for perfil in conteudo["profiles"]:
            ocorrencias = sum(
                1
                for pagina in paginas
                for linha in pagina
                # O código aparece duas vezes de propósito — no quadro de vagas e no
                # subtítulo. O que não pode repetir é o subtítulo, onde o Perfil é descrito.
                if re.match(rf"^\d+\.\d+ {perfil['code']} — ", linha)
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
    from processo_seletivo.publicacoes.infrastructure.pdf import largura

    # Uma coluna só se prova alinhada com várias células nela: o cenário-base tem um Evento, e
    # `01/09` e `20/09` são de colunas diferentes — início e término.
    centros = {
        round(recuo + largura(linha, tamanho, fonte) / 2)
        for linha, fonte, tamanho, recuo in linhas_desenhadas(documento(cronograma_longo(), HASH))
        if linha == "01/09/2026, às 9h"
    }
    assert len(centros) == 1, f"a coluna de início não está alinhada: {centros}"


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

    assert "05/10/2026, às 14h" in texto
    assert "None" not in texto
    # O período que tem término continua exibindo os dois instantes.
    assert "20/09/2026, às 23h59" in texto


def test_o_cabecalho_da_tabela_se_repete_na_continuacao_e_nunca_fica_orfao():
    """FR-026: uma tabela que vira a página continua legível.

    Sem repetição, a página seguinte mostra números sem dizer de que são. E um cabeçalho sozinho
    no rodapé é o mesmo defeito do título órfão, uma linha abaixo.
    """
    paginas = paginas_de(documento(cronograma_longo(), HASH))
    com_cabecalho = [numero for numero, pagina in enumerate(paginas, 1) if "Evento" in pagina]
    # A célula do evento reflui dentro da sua coluna, então a continuação de uma linha da tabela
    # não começa por `ETAPA`. O que identifica uma página com tabela é ter célula de qualquer
    # coluna — inclusive a continuação, que é justamente quem precisa do cabeçalho repetido.
    com_evento = [
        numero
        for numero, pagina in enumerate(paginas, 1)
        if any(
            linha.startswith("ETAPA") or linha.startswith("01/09/2026") or linha == "seletivo"
            for linha in pagina
        )
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
    for rotulo in ("Caráter:", "Peso:", "Nota mínima:"):
        assert rotulo in texto, rotulo
    assert "eliminatória e classificatória" in texto
    assert "2" in texto and "7" in texto

    # A data continua vindo do Evento vinculado, e não é digitada de novo na Etapa (FR-028).
    assert "01/09/2026, às 9h" in texto

    # Etapa sem peso nem nota mínima não ganha rótulo vazio.
    sem_ponderacao = snapshot()
    sem_ponderacao["stages"][0] = {
        **sem_ponderacao["stages"][0],
        "weight": None,
        "minimumScore": None,
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
        snapshot(),
        dois_perfis(),
        perfil_maior_que_a_pagina(),
        cronograma_longo(),
        sem_etapas(),
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

    # **O bloco se anuncia como registro, não como assinatura.** Um nome centralizado sozinho ao
    # pé de um Edital lê-se como rubrica, e este documento não tem rubrica (FR-036).
    assert "Autoridade responsável pelo ato" in texto
    assert AUTORIDADE[0] in texto
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

    # **Forma atualizada**: o bloco deixou de ser um título em caixa alta seguido de quatro
    # linhas e passou a três linhas de nota abaixo de um fio. Ele precisa estar presente e
    # precisa estar **abaixo** — em corpo de texto, lia-se como a décima primeira seção.
    verificacao = next(
        indice
        for indice, linha in enumerate(linhas)
        if linha.startswith("Verificação de integridade")
    )
    assert linhas.index(AUTORIDADE[0]) < verificacao

    # Discreto: o bloco de verificação usa o menor corpo do documento.
    corpos = {
        tamanho for linha, _, tamanho, _ in linhas_desenhadas(pdf) if linha.startswith("SHA-256")
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
        snapshot(),
        HASH,
        autoridade=AutoridadeSignataria(nome="Diretora do Cefor", cargo="Diretora-Geral"),
    )
    assert diferente != um, "trocar quem assina tem de mudar o documento"


# ---------------------------------------------------------------------------
# 008 — Regressões de composição encontradas em revisão
#
# Os três casos abaixo são entrada **válida**: descrição de Evento, conteúdo de seção e
# atribuições são texto livre sem limite de tamanho. Nenhum deles quebrava o documento — os três
# produziam um documento errado, que é o modo de falha que a tabela de interações de D-004 previa
# e que nenhum cenário anterior exercitava.
# ---------------------------------------------------------------------------


def test_uma_celula_longa_nao_empurra_as_colunas_para_fora_da_pagina():
    """Coluna medida pelo conteúdo precisa de teto (FR-002, FR-023).

    Sem limite, a largura natural de uma descrição de quinhentos caracteres soma além da área
    útil e joga as colunas seguintes para fora do papel: o Edital publicado perde início e
    término sem que nada acuse.
    """
    from processo_seletivo.publicacoes.infrastructure.pdf import LARGURA, MARGEM, largura

    conteudo = snapshot()
    conteudo["schedule"] = [{**conteudo["schedule"][0], "description": "D" * 500}]
    pdf = documento(conteudo)

    util = LARGURA - 2 * MARGEM
    for linha, fonte, tamanho, recuo in linhas_desenhadas(pdf):
        assert recuo >= 0, f"{linha!r} começa antes da margem esquerda"
        assert largura(linha, tamanho, fonte) + recuo <= util + 0.5, (
            f"{linha!r} ultrapassa a margem direita"
        )

    # E o conteúdo continua lá: limitar a coluna quebra a célula, não a descarta.
    texto = texto_de(pdf)
    assert "01/09/2026, às 9h" in texto and "20/09/2026, às 23h59" in texto
    assert "DDDDD" in texto


def test_um_paragrafo_maior_que_a_pagina_quebra_entre_linhas_sem_criar_pagina_vazia():
    """O quinto degrau da cascata: quando nada mais cabe, quebra-se entre linhas (FR-021).

    Manter unidas as linhas de um parágrafo é cortesia; quando o parágrafo é maior que a página,
    a cortesia vira laço — o paginador devolvia a cadeia inteira à página nova, ela não cabia de
    novo, e o documento crescia em páginas vazias.
    """
    secoes_longas = [dict(secao) for secao in snapshot()["sections"]]
    for secao in secoes_longas:
        if secao.get("key") == "apresentacao":
            secao["content"] = " ".join(["palavra"] * 1200)

    paginas = paginas_de(documento(snapshot(sections=secoes_longas)))

    assert len(paginas) < 12, f"{len(paginas)} páginas para um parágrafo longo"
    for numero, pagina in enumerate(paginas, 1):
        corpo = [linha for linha in pagina if not linha.startswith("Edital 07/2026 ·")]
        assert corpo, f"página {numero} saiu vazia"


def test_o_cabecalho_de_uma_tabela_nao_vaza_para_o_que_vem_depois_dela():
    """O cabeçalho repetível vale enquanto a tabela existir, e nem um bloco a mais (FR-026).

    O quadro de modalidades fecha dentro do Perfil; o Cronograma, páginas adiante, não é
    continuação dele. Repetir ali `Modalidade / Percentual / Fundamento / Versão` seria anunciar
    uma tabela que acabou.
    """
    paginas = paginas_de(documento(dois_perfis()))
    for numero, pagina in enumerate(paginas, 1):
        cabecalhos = [linha for linha in pagina if linha == "Modalidade"]
        modalidades = [linha for linha in pagina if linha.startswith("PPP — ")]
        assert len(cabecalhos) <= len(modalidades), (
            f"cabeçalho de modalidades sem tabela na página {numero}"
        )


def test_o_fechamento_do_ato_nao_se_parte_entre_paginas():
    """Autoridade e verificação são um bloco só (FR-033, FR-038).

    Quem assinou e a prova do que assinou não se separam por acidente de paginação. O cenário de
    referência cabia e escondia o caso; um Edital com dois Perfis termina perto do fim da página e
    deixava o SHA-256 sozinho na seguinte.
    """
    conteudo = dois_perfis()
    conteudo["profiles"][1]["duties"] = "\n".join(
        f"Preparar, manter e acompanhar os laboratórios da área {n}." for n in range(1, 12)
    )
    paginas = paginas_de(documento(conteudo))

    fechamento = [
        numero
        for numero, pagina in enumerate(paginas, 1)
        for linha in pagina
        if linha == AUTORIDADE[0] or linha.startswith(("VERIFICAÇÃO", "SHA-256 do conteúdo"))
    ]
    assert len(set(fechamento)) == 1, (
        f"o fechamento do ato ficou espalhado pelas páginas {sorted(set(fechamento))}"
    )


def test_uma_linha_de_tabela_com_celula_refluida_nao_se_parte_entre_paginas():
    """FR-021 define a linha da tabela como unidade segura de quebra.

    Transformar cada linha visual da célula em item independente fazia a linha lógica escorregar:
    sete linhas de uma modalidade ficavam numa página e a última, sozinha, na seguinte — mesmo
    cabendo inteira lá. `foundation` é texto livre, então é entrada válida.
    """
    curtas = [
        {
            "id": f"44444444-4444-4444-4444-4444444444{n:02d}",
            "code": f"M{n:02d}",
            "name": f"Modalidade {n}",
            "description": "",
            "normativeRule": {
                "id": f"55555555-5555-5555-5555-5555555555{n:02d}",
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
        for n in range(1, 34)
    ]
    longa = {
        **curtas[0],
        "id": "44444444-4444-4444-4444-4444444444ff",
        "code": "MLONGA",
        "name": "Modalidade de fundamento extenso",
        "normativeRule": {
            **curtas[0]["normativeRule"],
            "id": "55555555-5555-5555-5555-5555555555ff",
            "foundation": (
                "Lei nº 12.990, de 9 de junho de 2014, combinada com a Portaria Normativa "
                "que dispõe sobre a reserva de vagas e com as demais normas aplicáveis ao "
                "certame, observado o disposto neste Edital e na legislação vigente"
            ),
        },
    }
    perfil = {**snapshot()["profiles"][0], "competitionModalities": curtas + [longa]}
    paginas = paginas_de(documento(snapshot(profiles=[perfil])))

    onde = [
        numero
        for numero, pagina in enumerate(paginas, 1)
        for linha in pagina
        if "MLONGA" in linha or "reserva de vagas" in linha or "certame, observado" in linha
    ]
    assert len(set(onde)) == 1, (
        f"a linha da tabela ficou dividida entre as páginas {sorted(set(onde))}"
    )


JUSTIFICADA = re.compile(
    rb"BT ([\d.]+) Tw /(F\d) ([\d.]+) Tf ([\d.]+) [\d.]+ Td \((.*?)\) Tj", re.DOTALL
)


def test_o_texto_normativo_alcanca_as_duas_margens():
    """A justificação dos Editais de referência (FR-002, FR-029).

    Só é possível porque a largura é real: a folga da linha é distribuída entre os seus espaços,
    e sem medir não há folga a distribuir.
    """
    from processo_seletivo.publicacoes.infrastructure.pdf import LARGURA, MARGEM, largura

    pdf = documento(snapshot())
    util = LARGURA - 2 * MARGEM
    justificadas = [
        (
            texto.replace(b"\\(", b"(").replace(b"\\)", b")").decode("cp1252"),
            fonte.decode(),
            float(corpo),
            float(x) - MARGEM,
            float(espaco),
        )
        for espaco, fonte, corpo, x, texto in JUSTIFICADA.findall(conteudo_das_paginas(pdf))
    ]

    assert justificadas, "nenhuma linha foi justificada"
    for texto, fonte, corpo, recuo, espaco in justificadas:
        alcancado = largura(texto, corpo, fonte) + espaco * texto.count(" ") + recuo
        assert abs(alcancado - util) < 0.5, f"{texto!r} não alcançou a margem: {alcancado:.1f}"

    # A última linha de um parágrafo não é esticada, e título, célula e assinatura também não.
    ultimas = [
        linha
        for linha, _, _, _ in linhas_desenhadas(pdf)
        if linha.startswith(("Distância, torna pública", "aplicável e os princípios"))
    ]
    assert ultimas, "o cenário deveria ter parágrafos de duas linhas"
    for ultima in ultimas:
        assert not any(ultima == texto for texto, _, _, _, _ in justificadas)


def test_a_medicao_de_um_bloco_atravessa_os_quadros_que_ele_contem():
    """Um Perfil com quadros dentro é medido inteiro — senão ele é partido (FR-021).

    O quadro abre um bloco e fecha com o mesmo marcador dos demais. Não contá-lo como abertura
    fazia a profundidade zerar cedo: a extensão do Perfil terminava no seu primeiro quadro, a
    altura medida saía muito menor que a real, e a cascata o colocava numa página onde não cabia.
    """
    base = snapshot()
    completo = {
        **base["profiles"][0],
        "duties": "Ministrar aulas nos cursos técnicos e de graduação.\n"
        "Participar das atividades de ensino, pesquisa e extensão do campus.",
        "workload": "40 horas semanais",
        "compensation": "R$ 4.200,00 mensais, acrescidos de auxílio-alimentação",
        "requirements": ["Mestrado em Computação ou área afim", "Registro profissional ativo"],
    }
    segundo = {
        **completo,
        "id": "33333333-3333-3333-3333-33333333aaaa",
        "code": "TEC-LAB",
        "name": "Técnico de Laboratório",
    }
    paginas = paginas_de(documento(snapshot(profiles=[completo, segundo])))

    for codigo in ("DOC-INFO", "TEC-LAB"):
        onde = {
            numero
            for numero, pagina in enumerate(paginas, 1)
            for linha in pagina
            if linha.startswith(f"{codigo} — ")
            or (codigo == "DOC-INFO" and linha == "Mestrado em Computação ou área afim")
        }
        assert len(onde) == 1, f"o Perfil {codigo} ficou partido entre as páginas {sorted(onde)}"


def test_o_documento_abre_com_o_brasao_da_republica():
    """FR-008, reaberto: um asset institucional fixo, e nada além.

    O brasão foi recortado do cabeçalho do Edital 146/2025 do Cefor — mesmo símbolo, mesma
    resolução, mesmo tamanho que os Editais publicados usam. Não há branding configurável, imagem
    por Processo nem engine de assets: o documento tem um símbolo, e ele é o da República.
    """
    from processo_seletivo.publicacoes.infrastructure import brasao

    pdf = documento(snapshot(), HASH)

    # A imagem existe como objeto do documento, com as dimensões do arquivo versionado.
    assert b"/Subtype /Image" in pdf
    assert f"/Width {brasao.LARGURA} /Height {brasao.ALTURA}".encode() in pdf
    assert brasao.FLUXO in pdf, "o fluxo da imagem não foi embutido"

    # E é desenhada **só na primeira página**: repeti-la seria papel timbrado, não ato.
    fluxos = CONTEUDO_DA_PAGINA.findall(pdf)
    assert b"Do" in fluxos[0]
    for seguinte in fluxos[1:]:
        assert b"Do" not in seguinte

    # O órgão começa abaixo do brasão, e não por baixo dele.
    from processo_seletivo.publicacoes.infrastructure.pdf import ALTURA_DO_BRASAO, TOPO

    altura_do_ministerio = next(
        y
        for linha, y in zip(
            [texto for texto, _, _, _ in linhas_desenhadas(pdf)],
            alturas_por_pagina(pdf)[0],
            strict=False,
        )
        if linha == "Ministério da Educação"
    )
    assert altura_do_ministerio < TOPO - ALTURA_DO_BRASAO


def test_o_brasao_nao_torna_o_documento_indeterministico():
    """A imagem é constante, e comprimida uma vez na importação (SC-013)."""
    assert documento(snapshot(), HASH) == documento(snapshot(), HASH)


def test_a_apresentacao_e_preambulo_e_nao_a_primeira_secao():
    """FR-010: o ato enunciativo abre o Edital, sem número e sem cabeçalho.

    Nos três Editais de referência a abertura — "A Diretora [...] faz saber [...]" — vem logo
    abaixo do título do ato, e a numeração começa nas disposições preliminares. Numerá-la como
    `1.` faz o documento anunciar uma seção onde há uma abertura.
    """
    pdf = documento(snapshot(), HASH)
    texto = texto_de(pdf)
    linhas = [linha for linha, _, _, _ in linhas_desenhadas(pdf)]

    # O conteúdo da Apresentação continua no documento; o que sai é o cabeçalho dela.
    assert "O Instituto Federal do Espírito Santo, por meio do Centro de Referência" in texto
    assert "APRESENTAÇÃO" not in texto
    assert "1. APRESENTAÇÃO" not in texto

    # A numeração começa na seção seguinte, e o preâmbulo vem antes dela.
    assert "1. DISPOSIÇÕES PRELIMINARES" in texto
    preambulo = next(i for i, linha in enumerate(linhas) if linha.startswith("O Instituto Federal"))
    assert preambulo < linhas.index("1. DISPOSIÇÕES PRELIMINARES")

    # E o preâmbulo é texto normativo: justificado como o resto do corpo.
    justificadas = {
        texto_da_linha.replace(b"\\(", b"(").decode("cp1252")
        for _, _, _, _, texto_da_linha in JUSTIFICADA.findall(conteudo_das_paginas(pdf))
    }
    assert any(linha.startswith("O Instituto Federal") for linha in justificadas)


def test_suprimir_o_preambulo_nao_abre_lacuna_na_numeracao():
    """A regra de FR-011 continua valendo com o preâmbulo fora da contagem."""
    import re as _re

    sem_apresentacao = [
        secao for secao in snapshot()["sections"] if secao.get("key") != "apresentacao"
    ]
    texto = texto_de(documento(snapshot(sections=sem_apresentacao), HASH))
    numeros = [int(m.group(1)) for m in _re.finditer(r"^(\d+)\. [A-ZÀ-Ú]", texto, _re.M)]
    assert numeros == list(range(1, len(numeros) + 1)), numeros


def test_o_cargo_nao_e_repetido_quando_ja_esta_no_nome_registrado():
    """O catálogo de demonstração traz cargo no campo de nome (FR-033).

    `Reitora do Ifes / Reitora` faria o documento parecer defeituoso onde ele apenas reflete o
    dado que existe. Quando o cargo acrescenta informação, ele é composto.
    """
    from processo_seletivo.publicacoes.infrastructure.pdf import AutoridadeSignataria

    repetido = texto_de(
        documento(
            snapshot(),
            HASH,
            autoridade=AutoridadeSignataria(nome="Reitora do Ifes", cargo="Reitora"),
        )
    )
    assert repetido.count("Reitora") == 1

    distinto = texto_de(
        documento(
            snapshot(),
            HASH,
            autoridade=AutoridadeSignataria(
                nome="Aline Freitas da Silva de Carvalho",
                cargo="Diretora do Centro de Referência em Formação e em Educação a Distância",
            ),
        )
    )
    assert "Aline Freitas da Silva de Carvalho" in distinto
    assert "Diretora do Centro de Referência" in distinto


def test_a_etapa_decisoria_imprime_os_rotulos_e_nao_imprime_nota():
    """Jornada 1: quem lê o Edital descobre que aquela Etapa produz deferimento, e não nota."""
    conteudo = snapshot(stages=[
            {
                "id": "00000000-0000-0000-0000-0000000000b1",
                "name": "Análise documental",
                "order": 1,
                "weight": None,
                "eliminatory": True,
                "classificatory": False,
                "minimumScore": None,
                "maximumScore": None,
                "evaluationsPerRegistration": 1,
                "forma": "DECISORIA",
                "rotuloFavoravel": "Deferido",
                "rotuloDesfavoravel": "Indeferido",
                "scheduleEventId": None,
            }
        ]
    )

    texto = texto_de(documento(conteudo))

    assert "Deferido ou Indeferido" in texto
    assert "Nota mínima" not in texto and "Pontuação máxima" not in texto
