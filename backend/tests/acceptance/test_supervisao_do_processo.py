"""A jornada demonstrável da `022`: quem preside abre o Processo e sabe onde ele está.

`SC-001` e `FR-005`. A frase que governa a feature é esta, e este teste é ela executada: quem
preside abre o Processo e identifica **o que aconteceu**, **o que deveria acontecer agora** e **se
existe condição que impede o próximo ato** — numa tela só, sem navegar.
"""

import re

import pytest
from django.urls import reverse

from processo_seletivo.comissoes.domain.funcoes import Funcao
from tests.fixtures.comissao import constituir
from tests.fixtures.publicacao import publish_original
from tests.fixtures.supervisao import (
    SEGUNDO_SEED,
    etapa_ligada,
    publicar_no_processo,
    rascunhar,
    rascunho_com_periodo,
    submeter,
)
from tests.interface.conftest import identificar

pytestmark = [pytest.mark.acceptance, pytest.mark.django_db(transaction=True)]


def texto(corpo):
    sem_folha = re.sub(r"(?s)<style>.*?</style>", " ", corpo)
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", sem_folha))


def test_quem_preside_ve_situacao_volume_prazo_e_impedimento_numa_tela_so(
    gestor, api_client, manager_headers, client, seletor_ligado
):
    """O percurso inteiro, pelo canal de quem preside — e nenhum número vindo de lugar nenhum novo.

    Todo valor apresentado é reproduzível a partir dos registros das donas (`FR-005`): a soma é a
    das inscrições de cada Edital, e o prazo é o Evento marcado do cronograma publicado.

    **A Etapa sem marco deixou de ser sinal da condução** (045, `FR-739`): ela é dita onde tem
    remédio, na validação do conteúdo do Edital — e é lá que o percurso a procura.
    """
    primeiro = publish_original(
        api_client,
        {**manager_headers, "HTTP_IDEMPOTENCY_KEY": "aceitacao-022-0001"},
        {
            "institutionalCode": "PS-2026-022",
            "title": "Processo Seletivo de Supervisão",
            "firstEdital": {"number": "11", "year": 2026, "title": "Edital de docentes"},
        },
        draft=rascunho_com_periodo(
            11,
            etapas=[
                etapa_ligada(11, nome="Análise documental"),
                # A segunda Etapa não declara Evento: é publicável e legítimo. Desde a `045` é
                # **aviso** da validação do conteúdo, e não sinal da Atenção.
                {
                    "id": "00000000-0000-0000-0000-000000000560",
                    "name": "Prova didática",
                    "order": 2,
                    "eliminatory": False,
                    "classificatory": True,
                },
            ],
        ),
    )
    processo = primeiro.processo
    segundo = publicar_no_processo(
        api_client,
        manager_headers,
        processo,
        number="12",
        year=2026,
        title="Edital de técnicos",
        chave="aceitacao-022-segundo",
        draft=rascunho_com_periodo(SEGUNDO_SEED, etapas=[etapa_ligada(SEGUNDO_SEED)]),
    )
    constituir(gestor, processo, [("maria", Funcao.PRESIDENTE)], prefixo="aceitacao-022")
    submeter(primeiro, 8, seed=11)
    submeter(segundo, 3, primeiro=100, seed=SEGUNDO_SEED)
    rascunhar(primeiro, 2, seed=11)

    # Preside **e** elabora Retificação: é a combinação que recebe o caminho até onde o sinal de
    # conteúdo publicado se resolve.
    identificar(client, "maria", ["elaborador"])
    # O caminho existe a partir da página do Processo: sem ele a capacidade não é alcançável.
    painel = client.get(reverse("interface:processo-detalhe", args=[processo.id])).content.decode()
    assert reverse("interface:supervisao", args=[processo.id]) in painel

    resposta = client.get(reverse("interface:supervisao", args=[processo.id]))
    assert resposta.status_code == 200
    lido = texto(resposta.content.decode())

    # O que aconteceu: a soma do Processo, desdobrada por Edital nomeado.
    assert "11 inscrições recebidas no Processo" in lido
    assert "2 em preenchimento" in lido
    assert "11/2026" in lido and "12/2026" in lido

    # O que deveria acontecer agora: o prazo de cada Edital, e o volume recente do Processo.
    assert "11 nas últimas 24 horas" in lido
    assert "Inscrições de" in lido
    assert "Encerra em" in lido

    # E a Etapa sem marco **não** é condição de condução (045, `FR-739`): nenhuma Retificação a
    # resolve, e o painel que a mostrava para sempre ensinava a ignorá-lo.
    assert "sem marco no cronograma" not in lido
    assert reverse("interface:retificar", args=[primeiro.id]) not in resposta.content.decode()

    # Ela é dita na validação do conteúdo do Edital publicado, como aviso — e não como impedimento.
    detalhe = texto(client.get(reverse("interface:detalhe", args=[primeiro.id])).content.decode())
    assert "não está vinculada a nenhum Evento do Cronograma" in detalhe


def test_o_requisito_que_fecha_o_catalogo_nomeia_as_especies_que_o_produto_apresenta():
    """`SC-274` e `FR-744` (045): as duas listas são **a mesma**, conferidas contando as duas.

    **Por duas features elas não foram.** A `FR-024` da `022` dizia *"exclusivamente os sinais
    definidos em `UX-001` a `UX-005`"*, e a `027` acrescentou o `UX-046` sem revisá-la: um catálogo
    fechado que não fechava o que existia. A `038` a substituiu pela `FR-565`, com dez espécies; a
    `045` tirou duas, e substituiu a `FR-565` pela `FR-744`, com oito.

    **O teste lê o requisito vigente, e não o mais antigo.** O bloco da `FR-024` guarda o texto
    riscado de 09/09 e a tabela de 19/09 — é o que aquelas decisões decidiram, e não se apaga. Lê-lo
    como catálogo acusaria o `UX-001` riscado como espécie viva. O que continua cobrado dele é que
    diga que foi substituído.

    **Este teste lê a spec, e não uma cópia dela.** Conferir contra uma lista escrita aqui provaria
    que o teste concorda consigo mesmo — que é exatamente o que deixou o requisito envelhecer por
    duas features sem que nada ficasse vermelho.
    """
    from pathlib import Path

    from processo_seletivo.interface import supervisao

    # `parents[3]` é a raiz do repositório: este arquivo está em `backend/tests/acceptance/`.
    raiz = Path(__file__).resolve().parents[3]
    vigente = raiz / "specs" / "045-conducao-confiavel-processo" / "spec.md"
    requisito = re.search(
        r"- \*\*FR-744\*\*:(.+?)(?=\n- \*\*FR-745\*\*)", vigente.read_text(), re.S
    )
    assert requisito is not None, "a FR-744 não foi encontrada onde o catálogo é fechado"

    # **Por extenso, e nunca por faixa.** Aceitar `UX-001` a `UX-005` como cinco nomes faria o
    # teste concordar com uma faixa que cresce sozinha — e foi exatamente assim que o requisito
    # passou a dizer cinco onde havia seis.
    nomeadas = set(re.findall(r"UX-\d{3}", requisito.group(1)))

    assert nomeadas == set(supervisao.ESPECIES), (
        "o requisito e o produto discordam sobre o catálogo: "
        f"só no requisito {sorted(nomeadas - set(supervisao.ESPECIES))}, "
        f"só no produto {sorted(set(supervisao.ESPECIES) - nomeadas)}"
    )

    # E a cadeia de substituição continua legível a partir da origem: quem abre a `022` chega à
    # `038`, e quem abre a `038` chega à `045`.
    origem = (raiz / "specs" / "022-supervisao-do-processo" / "spec.md").read_text()
    bloco = re.search(r"- \*\*FR-024\*\*:(.+?)(?=\n- \*\*FR-025\*\*)", origem, re.S)
    assert bloco is not None, "a FR-024 da 022 não foi encontrada"
    assert "SUBSTITUÍDA" in bloco.group(1), (
        "a FR-024 precisa dizer que foi substituída, e não apenas mudar de conteúdo"
    )
    assert "FR-744" in bloco.group(1), "a FR-024 precisa apontar o requisito vigente"
    intermediaria = (raiz / "specs" / "038-painel-de-conducao" / "spec.md").read_text()
    assert re.search(r"- \*\*FR-565\*\*:.+?SUBSTITUÍDA.+?FR-744", intermediaria, re.S), (
        "a FR-565 da 038 precisa dizer que foi substituída pela FR-744"
    )
