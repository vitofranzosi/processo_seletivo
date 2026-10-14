"""As fontes completas que o modelo recebe (071, `R-002`, `FR-1472` a `FR-1476`, `SC-545`).

Sobre o corpus da `070`, em todos os instantes da varredura dela: as fontes são a união das
respostas determinísticas, e por isso herdam as garantias que a `070` já prova — e as que a união
poderia quebrar são as que se conferem aqui.
"""

import re
import time
from collections import defaultdict
from datetime import datetime

from processo_seletivo.duvidas.domain import cobertura
from processo_seletivo.duvidas.domain.estruturas import DADO, TEXTO
from processo_seletivo.duvidas.domain.estruturas_do_piloto import CALCULADA
from processo_seletivo.duvidas.domain.fontes import fontes_completas
from processo_seletivo.duvidas.domain.respostas import no_item
from processo_seletivo.publicacoes.domain.changes import resolve_path
from tests.fixtures.corpus import contexto_do_corpus
from tests.unit.duvidas.conftest import instantes
from tests.unit.duvidas.test_cobertura import _cobre, _generalizar, folhas_do_corpus

NOMES = ("01", "91", "92")


def _todas():
    for nome in NOMES:
        for instante in instantes(nome):
            contexto = contexto_do_corpus(nome, instante)
            yield nome, instante, contexto, fontes_completas(contexto)


def test_nenhum_caminho_aparece_com_dois_conteudos():
    """A colisão: um cartão da `070` que mudasse com o parâmetro daria ao modelo duas versões do
    mesmo campo, sem dizer qual vale para quê. A obrigatoriedade é o caso conhecido, e sai."""
    for nome, instante, _contexto, fontes in _todas():
        conteudos = defaultdict(set)
        for fonte in fontes:
            # Sem caminho são os atos da `P-12`, um por publicação: distintos pelo lugar.
            if fonte.natureza in (TEXTO, DADO) and fonte.caminho:
                conteudos[(fonte.natureza, fonte.caminho, fonte.posicao, fonte.rotulo)].add(
                    fonte.conteudo
                )
        colisoes = {chave: valores for chave, valores in conteudos.items() if len(valores) > 1}
        assert colisoes == {}, (nome, instante, colisoes)


def test_todo_campo_mostrado_pela_070_esta_nas_fontes():
    """`SC-545`: a tabela de cobertura da `070`, conferida contra as fontes, e não as respostas."""
    mostrados = set()
    for _nome, _instante, _contexto, fontes in _todas():
        mostrados.update(_generalizar(fonte.caminho) for fonte in fontes if fonte.caminho)
    presentes = folhas_do_corpus(so_preenchidas=True)
    faltando = []
    for padrao, classe in cobertura.COBERTURA.items():
        if not isinstance(classe, tuple) or not classe or classe[0] == "EXCLUIDO":
            continue
        if padrao in cobertura.CONDICIONAIS:
            continue
        base = padrao[:-3] if padrao.endswith("/**") else padrao
        if not any(p == base or p.startswith(base + "/") for p in presentes):
            continue
        if not any(_cobre(caminho, padrao) for caminho in mostrados):
            faltando.append(padrao)
    assert faltando == []


def test_todo_texto_do_edital_e_identico_ao_publicado():
    """`FR-1472`: inclusive no 01/2026 antes da fronteira, que tem valor futuro."""
    conferidos = 0
    for _nome, _instante, contexto, fontes in _todas():
        for fonte in fontes:
            if fonte.natureza != TEXTO:
                continue
            publicado = no_item(resolve_path(contexto.conteudo, fonte.caminho), fonte.posicao)
            assert publicado == fonte.conteudo, fonte.caminho
            conferidos += 1
    assert conferidos > 500


def test_o_futuro_e_fonte_a_parte_e_nao_mistura_versoes():
    """`SC-550`: antes da fronteira de 26/10, a fonte do término diz o vigente, e uma calculada diz
    o que a Retificação já publicada põe no lugar — e nenhuma fonte de texto ou de dado o diz."""
    contexto = contexto_do_corpus("01", datetime.fromisoformat("2026-10-20T12:00:00-03:00"))
    fontes = fontes_completas(contexto)
    por_id = {fonte.id: fonte for fonte in fontes}
    futuras = [fonte for fonte in fontes if fonte.altera]

    assert futuras, "o 01/2026 tem Retificação de vigência futura"
    for futura in futuras:
        assert futura.natureza == CALCULADA
        vigente = por_id[futura.altera]
        assert vigente.natureza in (TEXTO, DADO)
        assert "10/11/2026" not in vigente.conteudo
    assert any("10/11/2026" in fonte.conteudo for fonte in futuras)
    assert not any(
        "10/11/2026" in fonte.conteudo for fonte in fontes if fonte.natureza in (TEXTO, DADO)
    )


def test_os_identificadores_sao_estaveis_e_sequenciais():
    contexto = contexto_do_corpus("92", datetime.fromisoformat("2026-10-20T12:00:00-03:00"))
    primeira, segunda = fontes_completas(contexto), fontes_completas(contexto)

    assert [fonte.para_o_modelo() for fonte in primeira] == [
        fonte.para_o_modelo() for fonte in segunda
    ]
    assert [fonte.id for fonte in primeira] == [f"F{i}" for i in range(1, len(primeira) + 1)]


def test_a_ampla_concorrencia_sai_pela_linha_sem_modalidade():
    """`FR-1427` herdado: 28 em Iúna, e nenhuma lista com zero só por ter "AC" declarada."""
    contexto = contexto_do_corpus("91", datetime.fromisoformat("2026-10-20T12:00:00-03:00"))
    de_iuna = [
        fonte
        for fonte in fontes_completas(contexto)
        if "INF-IUN" in fonte.lugar and fonte.natureza == DADO
    ]
    textos = " | ".join(f"{fonte.rotulo}: {fonte.conteudo}" for fonte in de_iuna)

    assert re.search(r"\b28\b", textos)
    assert not re.search(r"[Aa]mpla concorrência[^|]*: 0\b", textos)


def test_a_obrigatoriedade_e_calculada_por_perfil_e_lista():
    contexto = contexto_do_corpus("91", datetime.fromisoformat("2026-10-20T12:00:00-03:00"))
    documentos = [
        fonte for fonte in fontes_completas(contexto) if fonte.lugar.startswith("Documentos")
    ]
    pcd = next(fonte for fonte in documentos if "INF-BJN" in fonte.lugar and "PcD" in fonte.lugar)

    assert pcd.natureza == CALCULADA
    assert "Laudo médico" in pcd.conteudo
    assert "Laudo médico" not in next(
        fonte.conteudo
        for fonte in documentos
        if "INF-BJN" in fonte.lugar and "sem modalidade" in fonte.lugar
    )


def test_a_montagem_do_maior_edital_e_rapida():
    """O `R-002` manda medir antes de memorizar: acima de 1 s, registrar no research primeiro."""
    contexto = contexto_do_corpus("92", datetime.fromisoformat("2026-10-20T12:00:00-03:00"))
    inicio = time.perf_counter()
    fontes_completas(contexto)
    assert time.perf_counter() - inicio < 1.0


def test_toda_secao_textual_preenchida_esta_inteira_nas_fontes():
    """`FR-1472`: o conteúdo completo, e não só o que as doze perguntas mostram (achado de 13/10).

    Sem esta conferência, uma seção que nenhuma pergunta da `070` trata não chegava ao modelo — e a
    cobertura por padrão não reprovava, porque qualquer seção mostrada a satisfazia.
    """
    for nome, instante, contexto, fontes in _todas():
        inteiras = {
            fonte.caminho: fonte.conteudo
            for fonte in fontes
            if fonte.natureza == TEXTO and fonte.posicao is None
        }
        for secao in contexto.conteudo.get("sections") or []:
            if secao.get("type") == "TEXT" and (secao.get("content") or "").strip():
                caminho = f"/sections/id={secao['id']}/content"
                assert inteiras.get(caminho) == secao["content"], (nome, instante, secao["key"])
