"""A diagramação do relatório do Edital: a qualidade editorial verificável (099, FR-2601 a FR-2607).

O relatório saiu do escritor do Edital, que é texto corrido, para o compositor de blocos da `100`.
Estes casos prendem o que a maquete v2 pede — e o fazem pela paginação, que é o que decide onde cada
bloco cai —, com relatórios sintéticos de 1 a 40 perfis e de 10 a 400 dias de inscrição: o cenário
coerente da fixture tem dois perfis e 26 dias, e não alcança os volumes que quebram a página. A
inspeção a olho das páginas renderizadas está em
`doc/estudo-relatorio-de-execucao-do-edital-2026-10-24/modernizacao/comparacao-visual.md`.
"""

import re
from datetime import date, datetime, timedelta
from types import SimpleNamespace

import pytest

from processo_seletivo.interface import relatorio_do_edital as rel
from processo_seletivo.interface import relatorio_pdf as pdf
from processo_seletivo.interface.diagramacao import (
    BASE,
    LARGURA_UTIL,
    NEGRITO,
    REGULAR,
    TOPO,
    Atencao,
    BarrasVerticais,
    Cartoes,
    Celula,
    Colunas,
    Documento,
    Espaco,
    Nota,
    Subtitulo,
    Tabela,
    Texto,
    TituloDeSecao,
    largura,
)
from processo_seletivo.interface.supervisao import PontoDaSerie
from processo_seletivo.interface.visao_geral import Numero
from tests.interface.test_fluxo import texto_de_pdf_bytes

ZONA = rel.ZONA
INICIO = date(2026, 8, 10)
SELECAO = "https://selecao.ifes.edu.br/selecoes/61/"


def _instante(dia, hora=10):
    return datetime(dia.year, dia.month, dia.day, hora, tzinfo=ZONA)


def _etapa(j):
    return rel.LinhaDaEtapa(
        nome=f"Etapa {j + 1}",
        regra="eliminatória e classificatória; nota mínima 6; peso 2",
        avaliadas=20,
        habilitadas=12,
        eliminadas=8,
        por_ocorrencia=1,
        elimina=True,
        registrada=True,
    )


def _perfil(i, *, omitido=False, etapas=3):
    nome = f"Perfil {i + 1} — Professor de Informática Aplicada"
    listas = (
        rel.LinhaDaLista(
            "Classificação final",
            "Ampla concorrência",
            Numero.de(14),
            Numero.de(1),
            "Resultado definitivo",
        ),
        rel.LinhaDaLista(
            "Classificação final",
            "Pessoas pretas, pardas e indígenas",
            Numero.de(5),
            Numero.de(1),
            "Resultado definitivo",
        ),
    )
    return rel.LinhaDoPerfil(
        id=str(i),
        nome=nome,
        local=f"Campus {i + 1}",
        vagas=Numero.de(2),
        vagas_por_lista=(("Ampla concorrência", 1), ("Pessoas pretas, pardas e indígenas", 1)),
        reserva="sem limite",
        inscricoes=Numero.de(3 if omitido else 26),
        rascunhos=Numero.de(1),
        por_vaga=Numero.de(13),
        classificadas=Numero.de(14),
        natureza_do_resultado="definitivo",
        habilitadas_nas_vagas=Numero.de(2),
        convocacoes=None if omitido else rel.Convocacoes(2, 1, 1, None, 0),
        recursos=None if omitido else rel.Recursos(2, 1, 1, 0, 0),
        situacao_das_vagas="2 de 2 com inscrição classificada e habilitada; 1 convocação aceita",
        etapas=() if omitido else tuple(_etapa(j) for j in range(etapas)),
        listas=listas,
        omitido=omitido,
        motivo_da_omissao=rel.FRASE_DE_PRIVACIDADE if omitido else "",
    )


def _indicadores(*, ausente=False):
    habilitadas = Numero.nao_disponivel("ainda não apurada") if ausente else Numero.de(2)
    return [
        rel.Indicador("vagas imediatas", Numero.de(2), "em 1 de 2 perfis"),
        rel.Indicador("inscrições enviadas", Numero.de(38), "outras 4 iniciadas e não enviadas"),
        rel.Indicador("inscrições por vaga", Numero.de(13), "26 inscrições para 2 vagas"),
        rel.Indicador("resultados definitivos publicados", Numero.de(2), "em 06/10/2026", de=2),
        rel.Indicador(
            "vagas com inscrição classificada e habilitada", habilitadas, "Não é matrícula", de=2
        ),
        rel.Indicador("convocações aceitas", Numero.de(1), "1 aguardando resposta", de=2),
    ]


def _relatorio(
    *,
    perfis=2,
    dias=26,
    retificacoes=1,
    alteracoes=1,
    publico=True,
    omitidos=0,
    especie=rel.ACOMPANHAMENTO,
    envios=None,
    ausente=False,
):
    serie = tuple(
        PontoDaSerie(INICIO + timedelta(days=d), (envios or (lambda d: 1 + d % 9))(d))
        for d in range(dias)
    )
    termino = INICIO + timedelta(days=max(dias - 6, 0))
    edital = SimpleNamespace(
        number="61",
        year=2026,
        title="Edital 61/2026 — Professor de Informática e Técnico de Laboratório",
        processo=SimpleNamespace(title="Processo Seletivo Simplificado 2026/2"),
    )
    documentos = [
        rel.Documento("Edital 61/2026", _instante(INICIO), "a" * 64, "", False),
        *(
            rel.Documento(
                f"Resultado definitivo — Perfil {i + 1}, ampla concorrência",
                _instante(date(2026, 10, 6)),
                f"{i:064x}",
                f"https://selecao.ifes.edu.br/selecoes/resultados/{i}/" if publico else "",
                True,
            )
            for i in range(perfis)
        ),
    ]
    datas = [
        rel.Data(_instante(INICIO - timedelta(days=7)), "Edital publicado", "publicação"),
        rel.Data(_instante(INICIO), "Período de inscrições", "previsto", ate=_instante(termino)),
        rel.Data(_instante(date(2026, 10, 20)), "Edital encerrado no GPS", "registrado"),
        rel.Data(_instante(date(2026, 10, 30)), "Fim de prazo de resposta", "prazo"),
    ]
    return rel.Relatorio(
        referencia=datetime(2026, 10, 24, 13, 10, tzinfo=ZONA),
        edital=edital,
        unidade={"nome": "Cefor", "cabecalho": ("Centro de Referência em Formação",), "local": ""},
        especie=especie,
        situacao_no_gps="Encerrado em 20/10/2026",
        providencias="Perfil 1: 1 convocação aguardando resposta, até 30/10/2026",
        pendencias=["Perfil 1: 1 convocação aguardando resposta, até 30/10/2026"],
        posteriores=[],
        frases=["O Edital ofereceu 2 vagas imediatas. " * 4],
        indicadores=_indicadores(ausente=ausente),
        perfis=[_perfil(i, omitido=i < omitidos) for i in range(perfis)],
        serie=serie,
        termino_original=_instante(termino, 23) if dias else None,
        no_periodo_acrescentado=sum(p.quantidade for p in serie if p.dia > termino),
        periodo_aberto=False,
        retificacoes=[
            rel.Retificacao_(
                numero=n + 1,
                publicada_em=_instante(INICIO + timedelta(days=5)),
                justificativa="Prorrogação do período de inscrições.",
                alteracoes=tuple(
                    {"campo": "Término", "onde": f"Evento {k}", "antes": "30/08", "depois": "04/09"}
                    for k in range(alteracoes)
                ),
            )
            for n in range(retificacoes)
        ],
        recursos=rel.Recursos(3, 1, 2, 0, 0),
        datas=datas,
        documentos=documentos,
        endereco_da_selecao=SELECAO if publico else "",
        cronograma=[rel.LinhaDoCronograma("Inscrições", "10/08 a 30/08", "10/08 a 04/09", "—")],
        cadastros_distintos=36,
        desfecho_em=_instante(date(2026, 10, 20)),
        pontos_de_atencao=[
            ("O Edital está encerrado no GPS, mas ainda há providência pendente.", "Texto."),
            ("A trilha de auditoria tem 2 registros depois do encerramento.", "Texto."),
            ("O GPS não registra matrículas.", "Texto."),
        ],
    )


VOLUMES = {
    "pequeno": {"perfis": 1, "dias": 10, "retificacoes": 0},
    "maquete": {},
    "muitos-perfis": {"perfis": 12, "dias": 60, "retificacoes": 3},
    "muitos-dias": {"perfis": 3, "dias": 200},
    "enorme": {"perfis": 40, "dias": 400, "retificacoes": 6, "alteracoes": 4},
    "com-omissao": {"perfis": 3, "omitidos": 1},
}


def _documento(r, emissao=1):
    documento = pdf.documento(r, emissao=emissao)
    documento.paginar()
    return documento


def _blocos(documento):
    return [c.bloco for pagina in documento.paginas for c in pagina]


def _tipos(pagina):
    return [type(colocacao.bloco) for colocacao in pagina]


@pytest.fixture(params=list(VOLUMES), ids=list(VOLUMES))
def documento(request):
    return _documento(_relatorio(**VOLUMES[request.param]))


def test_a_primeira_pagina_e_o_painel_inteiro(documento):
    """FR-2601: identificação, visão geral, os seis cartões e a atenção, na primeira página."""
    primeira = documento.paginas[0]
    assert Cartoes in _tipos(primeira)
    assert Atencao in _tipos(primeira)
    cartoes = next(c.bloco for c in primeira if isinstance(c.bloco, Cartoes))
    assert len(cartoes.cartoes) == 6
    assert not any(isinstance(c.bloco, Tabela) for c in primeira), "indicador não é tabela"


def test_cartao_atencao_e_colunas_nao_se_partem(documento):
    """FR-2604: cada grupo aparece uma vez só — não se divide entre páginas."""
    todos = _blocos(documento)
    assert sum(isinstance(b, Cartoes) for b in todos) == 1
    assert sum(isinstance(b, Atencao) for b in todos) == 1
    assert sum(isinstance(b, Colunas) for b in todos) <= 1


def test_titulo_nunca_fica_no_pe_e_nota_nunca_abre_pagina(documento):
    """FR-2604: título com o que ele titula; nota com o que ela explica."""
    for pagina in documento.paginas[:-1]:
        ultimo = pagina[-1].bloco
        assert not isinstance(ultimo, TituloDeSecao | Subtitulo), ultimo.trechos
        assert not ultimo.junto_ao_seguinte, ultimo
    for pagina in documento.paginas[1:]:
        assert not pagina[0].bloco.preso_ao_anterior, pagina[0].bloco.trechos


def test_blocos_cabem_na_pagina_e_nao_se_sobrepoem(documento):
    for pagina in documento.paginas:
        anterior = TOPO + 0.01
        for colocacao in pagina:
            assert colocacao.topo <= anterior + 0.01
            assert colocacao.topo - colocacao.altura >= BASE - 0.01
            anterior = colocacao.topo - colocacao.altura


def test_tabela_partida_repete_o_cabecalho_e_nao_deixa_linha_sozinha(documento):
    """FR-2604: as partes de uma tabela levam o mesmo cabeçalho, e duas linhas ao menos."""
    partes = {}
    for pagina in documento.paginas:
        for colocacao in pagina:
            if isinstance(colocacao.bloco, Tabela) and colocacao.bloco.cabecalho:
                partes.setdefault(id(colocacao.bloco.cabecalho), []).append(colocacao.bloco)
    for tabelas in partes.values():
        if len(tabelas) > 1:
            assert all(len(t.linhas) >= Tabela.MINIMO_POR_PARTE for t in tabelas)


def _celulas(tabela):
    """`(texto, tamanho, fonte)` de cada parte de cada célula, com a coluna dela."""
    colunas = tabela._colunas(LARGURA_UTIL)
    for fonte_da_linha, linha in [
        (NEGRITO, tabela.cabecalho or []),
        *((REGULAR, linha) for linha in tabela.linhas),
    ]:
        for coluna, celula in zip(colunas, linha, strict=True):
            if isinstance(celula, Celula):
                for texto, tamanho, fonte, _, _ in celula.partes:
                    yield coluna, texto, tamanho or tabela.tamanho, fonte
            else:
                yield coluna, str(celula), tabela.tamanho, fonte_da_linha


def test_nenhuma_palavra_e_partida_numa_coluna(documento):
    """Coluna estreita parte palavra no meio — "Convocaçõe / s" foi o que a inspeção achou."""
    for bloco in _blocos(documento):
        if isinstance(bloco, Tabela):
            for coluna, texto, tamanho, fonte in _celulas(bloco):
                for palavra in texto.split():
                    assert largura(palavra, tamanho, fonte) <= coluna - 8 + 0.01, palavra


def test_paginas_seguem_o_volume_e_o_anexo_abre_pagina(documento):
    """FR-2604: a seção 2 começa página, e o anexo também; nenhuma página fica só com a nota."""
    aberturas = [pagina[0].bloco for pagina in documento.paginas]
    titulos = [b.trechos[0].texto for b in aberturas if isinstance(b, TituloDeSecao)]
    assert "Resultados por perfil de vaga" in titulos
    assert "Anexo técnico" in titulos
    for pagina in documento.paginas:
        assert len(pagina) >= 2 or not isinstance(pagina[0].bloco, Texto)


def test_a_serie_e_diaria_quando_cabe_e_semanal_quando_nao():
    """FR-2536: barra por dia na maquete; com 200 dias, barra por semana — e a nota diz qual."""
    diaria = next(b for b in _blocos(_documento(_relatorio())) if isinstance(b, Colunas))
    barras = next(b for b in diaria.esquerda if isinstance(b, BarrasVerticais))
    assert len(barras.itens) == 26
    assert barras.itens[0][0] == "10/08"
    indice, rotulo = barras.marca
    assert barras.itens[indice][0] == "30/08" and "término original (30/08)" == rotulo
    antes, depois = barras.legenda
    total = sum(v for _, v in barras.itens)
    numeros = [int(re.search(r"\d+$", texto).group()) for texto, _ in barras.legenda]
    assert sum(numeros) == total
    assert "10/08, " in barras.alt and "O término original do prazo era 30/08." in barras.alt
    notas = [
        b
        for b in diaria.esquerda
        if isinstance(b, Texto) and "Cada barra é um dia" in str(b.trechos[0].texto)
    ]
    assert notas

    longa = _blocos(_documento(_relatorio(dias=200)))
    semanal = [b for b in longa if isinstance(b, BarrasVerticais)]
    semanal += [
        b
        for c in longa
        if isinstance(c, Colunas)
        for b in c.esquerda
        if isinstance(b, BarrasVerticais)
    ]
    assert len(semanal) == 1 and len(semanal[0].itens) == 29
    assert "semana de 10/08, " in semanal[0].alt
    # O término original cai entre duas barras, e a legenda soma o que as cores mostram.
    indice, _ = semanal[0].marca
    antes = int(re.search(r"\d+$", semanal[0].legenda[0][0]).group())
    assert antes == sum(n for _, n in semanal[0].itens[: indice + 1])
    termino = INICIO + timedelta(days=194)
    assert antes == sum(1 + d % 9 for d in range(200) if INICIO + timedelta(days=d) <= termino)


def test_semanas_alinhadas_ao_termino_original():
    pontos = [PontoDaSerie(INICIO + timedelta(days=d), 1) for d in range(20)]
    grupos, marca = pdf._grupos(pontos, 7, INICIO + timedelta(days=9))
    assert [len(g) for g in grupos] == [3, 7, 7, 3]
    assert grupos[marca][-1].dia == INICIO + timedelta(days=9)
    sem_termino, nenhuma = pdf._grupos(pontos, 7, None)
    assert [len(g) for g in sem_termino] == [7, 7, 6] and nenhuma is None


def test_sem_inicio_declarado_ou_sem_envio_a_ausencia_e_dita():
    sem_serie = " ".join(texto_de_pdf_bytes(pdf.compor(_relatorio(dias=0), emissao=1)).split())
    assert "não tem início declarado" in sem_serie
    sem_envio = _relatorio(envios=lambda d: 0)
    texto = " ".join(texto_de_pdf_bytes(pdf.compor(sem_envio, emissao=1)).split())
    assert "Nenhuma inscrição enviada no período." in texto


def test_alteracoes_longas_saem_do_lado_do_grafico():
    """Colunas não se partem: muitas Retificações descem para depois do gráfico, em sequência."""
    blocos = _blocos(_documento(_relatorio(retificacoes=6, alteracoes=4)))
    assert not any(isinstance(b, Colunas) for b in blocos)
    assert any(isinstance(b, BarrasVerticais) for b in blocos)


def test_links_so_com_endereco_publico():
    """FR-2603: emissão local não imprime endereço nem link; pública, a seleção e cada resultado."""
    local = pdf.compor(_relatorio(publico=False), emissao=1)
    assert b"/URI" not in local
    assert b"localhost" not in local
    assert "ambiente local" in " ".join(texto_de_pdf_bytes(local).split())
    publico = pdf.compor(_relatorio(perfis=3), emissao=1)
    assert publico.count(b"/S /URI") == 1 + 3
    assert f"/URI ({SELECAO})".encode() in publico


def test_ausencia_no_cartao_e_traco_com_o_motivo_e_nao_zero():
    cartoes = pdf.cartoes(_indicadores(ausente=True), pdf.COMPLEMENTOS_DO_DE)
    cartao = cartoes.cartoes[4]
    assert cartao.valor == "—" and cartao.de == ""
    assert cartao.base.startswith("Ainda não apurada")
    aceitas = cartoes.cartoes[5]
    assert (aceitas.valor, aceitas.de) == ("1", "de 2 realizadas")


def test_perfil_omitido_nao_mostra_numero_nao_publico():
    """FR-2551: a linha do Perfil pequeno diz a omissão, sem número de recurso ou convocação."""
    documento = _documento(_relatorio(perfis=3, omitidos=1))
    recursos = next(
        b
        for b in _blocos(documento)
        if isinstance(b, Tabela)
        and (b.cabecalho or [None])[0] == "Perfil"
        and "Recursos" in b.cabecalho
    )
    omitida = recursos.linhas[0]
    assert omitida[1:] == ["—"] * 6
    assert rel.FRASE_DE_PRIVACIDADE in omitida[0].partes[1][0].lower()


def test_toda_pagina_diz_o_edital_a_data_e_a_emissao():
    bytes_ = pdf.compor(_relatorio(perfis=12, dias=60), emissao=7)
    paginas = re.findall(rb"<< /Length \d+ >>\nstream\n(.*?)\nendstream", bytes_, re.DOTALL)
    paginas = [p for p in paginas if b"Tj" in p]
    assert len(paginas) >= 4
    for numero, conteudo in enumerate(paginas, 1):
        texto = texto_de_pdf_bytes(b"<< /Length 1 >>\nstream\n" + conteudo + b"\nendstream")
        assert "Relatório do Edital 61/2026 · relatório de acompanhamento" in texto
        assert "dados até 24/10/2026, 13h10 · emissão nº 7" in texto
        assert f"página {numero} de {len(paginas)}" in texto
        assert "não é ato administrativo" in texto


def test_a4_marcado_e_deterministico():
    r = _relatorio()
    primeira, segunda = pdf.compor(r, emissao=2), pdf.compor(r, emissao=2)
    assert primeira == segunda
    assert primeira != pdf.compor(r, emissao=3)
    assert b"/MediaBox [0 0 595 842]" in primeira
    for marca in (
        b"/StructTreeRoot",
        b"/MarkInfo << /Marked true >>",
        b"/Lang (pt-BR)",
        b"/S /Figure",
        b"/S /H1",
        b"/S /Table",
        b"/S /TH",
        b"/Alt ",
        b"/Title ",
    ):
        assert marca in primeira, marca
    assert b"/Artifact BMC" in primeira, "faixa, fios e fundos são artefatos"


@pytest.mark.parametrize(
    ("especie", "faixa"),
    [
        (rel.ENCERRAMENTO, "relatório de encerramento"),
        (rel.INTERRUPCAO, "relatório de interrupção"),
    ],
)
def test_a_especie_esta_na_faixa_e_no_subtitulo(especie, faixa):
    texto = " ".join(texto_de_pdf_bytes(pdf.compor(_relatorio(especie=especie), emissao=1)).split())
    assert faixa in texto
    assert _relatorio(especie=especie).especie_por_extenso in texto


# --- As regras de paginação que a 099 acrescentou à diagramação compartilhada ------------------

UTIL = TOPO - BASE


def _paginas(*blocos):
    documento = Documento(list(blocos), "faixa", "direita", "pé", "título")
    return [[c.bloco for c in pagina] for pagina in documento.paginar()]


def _tabela(n):
    return Tabela(["A", "B"], [[f"linha {i}", str(i)] for i in range(n)], larguras=[3, 1])


def test_titulo_subtitulo_e_tabela_descem_juntos():
    """A cadeia: com o título e o subtítulo cabendo e a tabela não, os três vão para a seguinte."""
    titulo, subtitulo, tabela = TituloDeSecao("T", antes=0.0), Subtitulo("S", antes=0.0), _tabela(3)
    w = LARGURA_UTIL
    sobra = titulo.medir(w) + subtitulo.medir(w) + 10
    paginas = _paginas(Espaco(UTIL - sobra), titulo, subtitulo, tabela)
    assert [type(b) for b in paginas[1]] == [TituloDeSecao, Subtitulo, Tabela]


def test_a_nota_desce_com_a_tabela_que_nao_se_parte():
    tabela, nota = _tabela(3), Nota("Explica a tabela.")
    assert nota.preso_ao_anterior
    paginas = _paginas(Espaco(UTIL - tabela.antes - tabela.medir(LARGURA_UTIL) - 2), tabela, nota)
    assert paginas[1] == [tabela, nota]


def test_tabela_partida_deixa_duas_linhas_de_cada_lado():
    tabela = _tabela(5)
    # Cabem o cabeçalho e quatro linhas: sem a regra, a quinta desceria sozinha.
    altura = tabela.antes + tabela._altura_do_cabecalho(LARGURA_UTIL) + 4 * 17.2
    paginas = _paginas(Espaco(UTIL - altura - 1), tabela)
    primeira, segunda = paginas[0][-1], paginas[1][0]
    assert (len(primeira.linhas), len(segunda.linhas)) == (3, 2)
    assert segunda.cabecalho == primeira.cabecalho


def test_paragrafo_curto_nao_se_parte_e_leva_o_titulo():
    titulo = TituloDeSecao("T", antes=0.0)
    paragrafo = Texto("palavra " * 36, antes=0.0)
    w = LARGURA_UTIL
    assert len(paragrafo.linhas(w)) == 3
    sobra = titulo.medir(w) + 2 * paragrafo.altura_da_linha + 1
    paginas = _paginas(Espaco(UTIL - sobra), titulo, paragrafo)
    assert paginas[1] == [titulo, paragrafo]
