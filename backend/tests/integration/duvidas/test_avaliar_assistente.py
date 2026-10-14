"""A rodada da matriz, com a porta falsa e sem rede (071, T052, US6).

A matriz dos testes é pequena e própria, num arquivo temporário: a do pacote fala dos Editais do
banco da equipe, e a suíte só tem o 91/2026, publicado pelo fluxo real com o deslocamento em dias
inteiros que o script do corpus usa.
"""

import csv
import json
import math
from dataclasses import replace
from datetime import datetime, timedelta

import pytest
from django.core.management import call_command

from processo_seletivo.duvidas.domain import fontes as derivacao
from processo_seletivo.duvidas.domain.estruturas_do_piloto import (
    AVALIACAO,
    CALCULADA,
    ORCAMENTO_ESGOTADO,
    Fonte,
)
from processo_seletivo.duvidas.infrastructure.inferencia import FalhaDoServico
from processo_seletivo.duvidas.management.commands import avaliar_assistente
from processo_seletivo.duvidas.models import TrocaDoPiloto
from tests.fixtures.corpus import deslocamento_ate_agora, publicar_do_corpus
from tests.fixtures.inferencia import devolucao, saida
from tests.fixtures.inferencia_corpus import fonte

pytestmark = [pytest.mark.django_db, pytest.mark.integration]

CREDENCIAL = "sk-or-v1-credencial-que-nao-pode-aparecer"
BJN = "Quantas vagas tem o polo de Bom Jesus do Norte?"
MATRIZ = {
    "instante_padrao": "2026-10-20T12:00:00-03:00",
    "casos": [
        {
            "id": "T-01",
            "categoria": "Factual",
            "edital": {"numero": "91", "ano": 2026},
            "instante": None,
            "perguntas": [BJN],
            "esperado": {"tipo": "RESPONDIDA", "valores": ["45", "33"], "nenhum_valor": ["0"]},
            "referencia_070": {"pergunta": "P-03", "perfil": "INF-BJN", "modalidade": None},
        },
        {
            "id": "T-02",
            "categoria": "Continuidade",
            "edital": {"numero": "91", "ano": 2026},
            "instante": None,
            "perguntas": [BJN, "E no polo de Iúna?"],
            "esperado": {"tipo": "RESPONDIDA", "valores": ["45"], "nenhum_valor": []},
        },
        {
            "id": "T-03",
            "categoria": "Sem Edital no banco",
            "edital": {"numero": "92", "ano": 2026},
            "instante": None,
            "perguntas": ["Como tiro dúvidas?"],
            "esperado": {"tipo": "RESPONDIDA", "valores": [], "nenhum_valor": []},
        },
    ],
}


@pytest.fixture
def dias():
    return math.ceil(deslocamento_ate_agora().total_seconds() / 86400)


@pytest.fixture
def edital_91(api_client, dias):
    edital, _ = publicar_do_corpus(
        api_client, "91", chave="avaliacao91", deslocamento=timedelta(days=dias)
    )
    return edital


@pytest.fixture
def matriz(tmp_path, monkeypatch):
    arquivo = tmp_path / "matriz.json"
    arquivo.write_text(json.dumps(MATRIZ, ensure_ascii=False), encoding="utf-8")
    monkeypatch.setattr(avaliar_assistente, "MATRIZ", arquivo)
    return arquivo


@pytest.fixture
def porta(porta_falsa, contador_falso, settings):
    settings.ASSISTENTE_CREDENCIAL = CREDENCIAL
    contador_falso()

    def vagas(mensagens):
        total = fonte(mensagens, lugar="INF-BJN", rotulo="Vagas imediatas")
        ampla = fonte(mensagens, lugar="INF-BJN", rotulo="Vagas da ampla concorrência")
        texto = saida(
            "RESPONDIDA",
            ("dado", "O polo de Bom Jesus do Norte tem 45 vagas.", [total["id"]]),
            ("dado", "Dessas, 33 são de ampla concorrência.", [ampla["id"]]),
        )
        return replace(devolucao(texto), custo=0.001)

    return porta_falsa(*([vagas] * 30))


def _rodar(saida_, dias, *argumentos):
    call_command(
        "avaliar_assistente",
        "--saida",
        str(saida_),
        "--repeticoes",
        "2",
        "--deslocamento-dias",
        str(dias),
        *argumentos,
    )
    return json.loads((saida_ / "rodada.json").read_text(encoding="utf-8"))


def _chaves(valor):
    if isinstance(valor, dict):
        for chave, item in valor.items():
            yield chave
            yield from _chaves(item)
    elif isinstance(valor, list):
        for item in valor:
            yield from _chaves(item)


def test_a_rodada_escreve_os_tres_arquivos(edital_91, matriz, porta, tmp_path, dias):
    rodada = _rodar(tmp_path / "r1", dias)

    # Três casos, duas repetições: 1 + 2 perguntas por repetição, e nenhuma do caso sem Edital.
    assert len(porta.chamadas) == 6
    por_id = {caso["id"]: caso for caso in rodada["casos"]}
    assert [len(por_id[c]["repeticoes"]) for c in ("T-01", "T-02")] == [2, 2]
    assert por_id["T-03"] == {
        **{chave: por_id["T-03"][chave] for chave in ("id", "categoria", "edital")},
        "rodado": False,
        "motivo": "o Edital não está publicado neste banco",
    }
    comparacoes = por_id["T-01"]["repeticoes"][0]["comparacoes"]
    assert comparacoes["valores_presentes"] == ["45", "33"]
    assert comparacoes["proibidos_presentes"] == []
    assert comparacoes["070"]["tipo_coincide"] is True
    assert "10" in comparacoes["070"]["faltando"]  # a 070 dá também as 10 PPI, e a falsa não

    # Cada repetição numa conversa nova, com a origem da avaliação e o instante do caso.
    trocas = TrocaDoPiloto.objects.filter(origem=AVALIACAO)
    assert trocas.count() == 6
    assert trocas.values("conversa").distinct().count() == 4
    esperado = datetime.fromisoformat("2026-10-20T12:00:00-03:00") + timedelta(days=dias)
    assert {troca.instante for troca in trocas} == {esperado}

    # Nada de tokens, tempo nem custo por troca (`FR-1510`), e a configuração sem credencial.
    chaves = set(_chaves(rodada["casos"]))
    assert not {chave for chave in chaves if any(p in chave for p in ("token", "custo", "segundo"))}
    for nome in ("rodada.json", "revisao.csv", "resumo.md"):
        assert CREDENCIAL not in (tmp_path / "r1" / nome).read_text(encoding="utf-8")
    assert "credencial" not in json.dumps(rodada["configuracao"])

    with (tmp_path / "r1" / "revisao.csv").open(encoding="utf-8") as arquivo:
        linhas = list(csv.DictReader(arquivo))
    assert len(linhas) == 12  # dois trechos por troca conferida
    assert {linha["julgamento"] for linha in linhas} == {""}
    assert "45" in linhas[0]["conteudo_das_fontes"]

    resumo = (tmp_path / "r1" / "resumo.md").read_text(encoding="utf-8")
    assert "Custo total informado pelo serviço: 0.006000" in resumo
    assert "chamadas ao serviço: 6" in resumo
    assert "`T-03`: o Edital não está publicado neste banco" in resumo


def test_a_recusa_pelo_limite_de_gasto_para_a_rodada(edital_91, matriz, porta, tmp_path, dias):
    """O limite é o da credencial (`FR-1507`): recusado, nenhuma pergunta a mais sai."""
    vagas = porta.respostas[0]
    porta.respostas = [vagas, vagas, vagas, FalhaDoServico(ORCAMENTO_ESGOTADO, "402")]

    rodada = _rodar(tmp_path / "r", dias)

    # T-01 duas vezes; o T-02 recebe a recusa na segunda pergunta, e a rodada para ali.
    assert len(porta.chamadas) == 4
    por_id = {caso["id"]: caso for caso in rodada["casos"]}
    assert len(por_id["T-02"]["repeticoes"]) == 1
    assert por_id["T-02"]["repeticoes"][0]["trocas"][-1]["estado"] == ORCAMENTO_ESGOTADO
    assert por_id["T-03"]["motivo"] == avaliar_assistente.SEM_GASTO
    assert "por rodar: 1" in (tmp_path / "r" / "resumo.md").read_text(encoding="utf-8")


def test_a_rodada_anterior_marca_a_outra_versao_da_fonte(
    edital_91, matriz, porta, tmp_path, dias, monkeypatch
):
    _rodar(tmp_path / "r1", dias)
    igual = _rodar(tmp_path / "r2", dias, "--rodada-anterior", str(tmp_path / "r1"))
    assert "outra versão da fonte" not in (tmp_path / "r2" / "resumo.md").read_text()

    original = derivacao.fontes_completas

    def com_uma_fonte_a_mais(contexto, respostas=None):
        todas = original(contexto, respostas)
        nova = Fonte(f"F{len(todas) + 1}", CALCULADA, "Teste", "Uma fonte que a 070 passou a dar.")
        return [*todas, nova]

    monkeypatch.setattr(derivacao, "fontes_completas", com_uma_fonte_a_mais)
    outra = _rodar(tmp_path / "r3", dias, "--rodada-anterior", str(tmp_path / "r2"))

    impressoes = {caso["id"]: caso.get("impressoes") for caso in igual["casos"]}
    assert all(
        caso["impressoes"] != impressoes[caso["id"]] for caso in outra["casos"] if caso["rodado"]
    )
    resumo = (tmp_path / "r3" / "resumo.md").read_text(encoding="utf-8")
    assert resumo.count("outra versão da fonte") == 2
