"""O PDF do relatório do Edital, composto em blocos, sobre os cenários coerentes (099, FR-2601+).

Os unitários de `test_diagramacao_do_relatorio_do_edital.py` cobrem o volume com relatórios
sintéticos; aqui são os fatos reais, pelos comandos da aplicação: o encerrado com convocação no
prazo, o encerrado sem pendência, o cancelado, o aberto com Perfil pequeno, a supressão
complementar e o cenário em escala. O que se confere é o que a diagramação não pode perder em
nenhum deles: o painel na primeira página, a regra de grupo, a espécie dita e a ausência de
endereço local.
"""

import pytest
from django.urls import reverse

from processo_seletivo.interface import relatorio_do_edital as rel
from processo_seletivo.interface import relatorio_pdf
from processo_seletivo.interface.diagramacao import (
    BASE,
    TOPO,
    Atencao,
    BarrasVerticais,
    Cartoes,
    Colunas,
    Subtitulo,
    TituloDeSecao,
)
from tests.fixtures.relatorio import REFERENCIA_ABERTA, montar_cenario
from tests.integration.relatorio.conftest import executiva_e_anexo, ler, texto_do_documento
from tests.interface.conftest import identificar
from tests.interface.test_fluxo import texto_de_pdf_bytes

pytestmark = [pytest.mark.django_db, pytest.mark.integration]

CENARIOS = {
    "pendente": ({"final": "pendente"}, None, "relatório de acompanhamento"),
    "sem-pendencia": ({"final": "sem-pendencia"}, None, "relatório de encerramento"),
    "cancelado": ({"final": "cancelado"}, None, "relatório de interrupção"),
    "cancelado-pequeno": ({"final": "cancelado", "maximo": 4}, None, "relatório de interrupção"),
    "aberto": ({"final": "aberto"}, REFERENCIA_ABERTA, "relatório de acompanhamento"),
    "complementar": ({"final": "pendente", "tecnicos": 3}, None, "relatório de acompanhamento"),
}


@pytest.fixture(params=list(CENARIOS), ids=list(CENARIOS))
def lido(request, db):
    argumentos, agora, faixa = CENARIOS[request.param]
    cenario = montar_cenario(**argumentos)
    relatorio = ler(cenario, agora=agora) if agora else ler(cenario)
    return request.param, relatorio, faixa


def _paginado(relatorio):
    documento = relatorio_pdf.documento(relatorio, emissao=1)
    documento.paginar()
    return documento


def test_o_painel_a_paginacao_e_a_especie_em_cada_cenario(lido):
    nome, relatorio, faixa = lido
    documento = _paginado(relatorio)
    primeira = [c.bloco for c in documento.paginas[0]]
    assert any(isinstance(b, Cartoes) for b in primeira), nome
    if relatorio.pontos_de_atencao:
        assert any(isinstance(b, Atencao) for b in primeira), nome
    for pagina in documento.paginas[:-1]:
        assert not isinstance(pagina[-1].bloco, TituloDeSecao | Subtitulo), nome
    for pagina in documento.paginas[1:]:
        assert not pagina[0].bloco.preso_ao_anterior, nome
    for pagina in documento.paginas:
        for colocacao in pagina:
            assert colocacao.topo <= TOPO + 0.01 and colocacao.topo - colocacao.altura >= BASE
    texto = texto_do_documento(relatorio)
    assert faixa in texto
    assert relatorio.especie_por_extenso in texto
    executiva, anexo = executiva_e_anexo(texto)
    assert anexo and "H. Sobre esta emissão" in anexo
    assert "localhost" not in texto


def test_a_procura_do_cenario_e_diaria_com_o_termino_original(pendente):
    """FR-2536: os 26 dias da maquete, a prorrogação marcada e as duas somas na legenda."""
    relatorio = ler(pendente)
    colunas = next(b for b in _paginado(relatorio).blocos if isinstance(b, Colunas))
    barras = next(b for b in colunas.esquerda if isinstance(b, BarrasVerticais))
    assert [rotulo for rotulo, _ in barras.itens] == [
        p.dia.strftime("%d/%m") for p in relatorio.serie
    ]
    assert [n for _, n in barras.itens] == [p.quantidade for p in relatorio.serie]
    assert barras.marca[1] == "término original (30/08)"
    textos = [texto for texto, _ in barras.legenda]
    assert textos[1] == f"no período acrescentado: {relatorio.no_periodo_acrescentado}"
    total = sum(p.quantidade for p in relatorio.serie)
    assert textos[0] == f"até o término original: {total - relatorio.no_periodo_acrescentado}"


def test_em_escala_o_painel_e_os_grupos_continuam(db):
    """Muitas inscrições: os números crescem, a forma não muda."""
    relatorio = ler(montar_cenario(escala=10))
    documento = _paginado(relatorio)
    assert any(isinstance(c.bloco, Cartoes) for c in documento.paginas[0])
    assert any(isinstance(c.bloco, Atencao) for c in documento.paginas[0])
    enviadas = next(i for i in relatorio.indicadores if i.rotulo == "inscrições enviadas")
    assert rel.interpretar(enviadas.numero) in texto_do_documento(relatorio)


@pytest.mark.django_db
def test_emissao_em_host_local_nao_leva_endereco(client, seletor_ligado, pendente):
    """FR-2603: o PDF emitido de `localhost` não tem link nem endereço, e diz por quê."""
    identificar(client, "gustavo.gestor", ["gestor"])
    url = reverse("interface:relatorio-do-edital-pdf", args=[pendente.edital.id])
    resposta = client.post(url)
    assert resposta.status_code == 200
    assert b"/URI" not in resposta.content
    texto = " ".join(texto_de_pdf_bytes(resposta.content).split())
    assert "ambiente local" in texto
    assert "testserver" not in texto


@pytest.mark.django_db
def test_emissao_em_host_publico_leva_os_links(client, seletor_ligado, pendente, settings):
    settings.ALLOWED_HOSTS = ["testserver", "selecao.ifes.edu.br"]
    identificar(client, "gustavo.gestor", ["gestor"])
    url = reverse("interface:relatorio-do-edital-pdf", args=[pendente.edital.id])
    resposta = client.post(url, HTTP_HOST="selecao.ifes.edu.br")
    assert resposta.status_code == 200, resposta.content[:300]
    selecao = reverse("portal:selecao", args=[pendente.edital.id])
    assert f"/URI (http://selecao.ifes.edu.br{selecao})".encode() in resposta.content
    assert "ambiente local" not in " ".join(texto_de_pdf_bytes(resposta.content).split())
