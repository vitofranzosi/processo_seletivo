"""A tela diz o que **não** alcança, e por quê (026, US6, FR-312, SC-102).

Ausência deliberada e ausência que parece defeito são coisas diferentes. Quem abre a Retificação
procurando corrigir o arredondamento não encontra o campo — e, até aqui, varria a página e concluía
que o sistema tinha esquecido.

A razão exibida é a do contrato, e ela é **normativa**. É por isso que este arquivo confere o
texto e não só a presença: uma razão que dissesse "não há tela para isso" seria decisão errada, e
não redação ruim.
"""

import re

import pytest
from django.urls import reverse

from processo_seletivo.editais.domain.mutabilidade import CONTRATO, Natureza
from processo_seletivo.interface.retificacao import (
    ROTULO_DO_EXCLUIDO,
    agrupar_em_secoes,
    campos_editaveis,
    exclusoes_do_tipo,
)
from processo_seletivo.publicacoes.models_retificacao import VersaoConsolidada
from tests.fixtures.publicacao import publish_original
from tests.fixtures.snapshot import rascunho_completo
from tests.interface.conftest import identificar

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.integration]


@pytest.fixture
def edital(api_client, manager_headers, process_payload):
    return publish_original(
        api_client, manager_headers, process_payload, draft=rascunho_completo(), anexos=1
    )


@pytest.fixture
def vigente(edital):
    return VersaoConsolidada.objects.filter(edital=edital).latest("materialized_at")


def test_o_bloco_do_marco_declara_o_que_nao_se_corrige_ali(client, seletor_ligado, edital):
    identificar(client, "ana.elaboradora", ["elaborador"])
    corpo = client.get(reverse("interface:retificar", args=[edital.id])).content.decode()

    assert "O que não se corrige por Retificação nesta seção" in corpo
    assert "Etapas que o marco mede" in corpo
    assert "Como as pontuações se combinam" in corpo
    assert "é outro marco, sob o mesmo nome e o mesmo código" in corpo


def test_a_razao_exibida_e_a_do_contrato_e_nunca_o_caminho_normativo(
    client, seletor_ligado, edital
):
    """FR-019 continua valendo aqui: o nome técnico do campo não chega a quem lê.

    **Nem o caminho de arquivo do código.** As razões nasceram escritas para quem lê o módulo, e
    duas citavam `classificacao/domain/faixa` e `editais/domain/perfis`. Quando a razão passou a
    ser texto de tela, elas passaram a ser referência de código exibida a um servidor do Cefor —
    a referência voltou para o comentário, e a razão ficou em português.
    """
    identificar(client, "ana.elaboradora", ["elaborador"])
    corpo = client.get(reverse("interface:retificar", args=[edital.id])).content.decode()

    for tecnico in ("appealWindow", "cutRule/", "parameters/", "normativeRule/"):
        assert tecnico not in corpo, f"o caminho normativo chegou à tela: {tecnico}"
    for codigo in ("domain/", ".py", "FR-", "doc/"):
        depois = corpo[corpo.index("O que não se corrige") :]
        assert codigo not in depois, f"referência de código exibida a quem lê: {codigo}"


def test_a_mesma_razao_nao_se_repete_dentro_do_bloco(client, seletor_ligado, edital, vigente):
    """A decisão que reprovou a primeira tentativa disto no PR #113.

    Explicação que não muda de um cartão para o outro não se imprime uma vez por cartão. O Edital
    máximo tem três Perfis e dois critérios de desempate; se a declaração fosse por grupo, cada
    razão apareceria uma vez por entidade.
    """
    identificar(client, "ana.elaboradora", ["elaborador"])
    corpo = client.get(reverse("interface:retificar", args=[edital.id])).content.decode()

    for tipo in ("Marco", "Critério de desempate", "Perfil"):
        for campo in exclusoes_do_tipo(tipo):
            assert corpo.count(campo["razao"]) == 1, (
                f"a razão de '{campo['rotulo']}' aparece {corpo.count(campo['razao'])} vezes"
            )


def test_a_declaracao_so_aparece_para_o_que_a_secao_mostra(client, seletor_ligado, edital, vigente):
    """Declarar o que não se corrige num Marco, para um Edital sem marco nenhum, responderia
    pergunta que ninguém fez."""
    secoes = agrupar_em_secoes(campos_editaveis(vigente.content))
    for secao in secoes:
        tipos_na_tela = {grupo["tipo"] for grupo in secao["grupos"]}
        assert {bloco["tipo"] for bloco in secao["exclusoes"]} <= tipos_na_tela


def test_todo_campo_excluido_tem_rotulo_em_portugues():
    """Sem rótulo, a tela cairia no caminho normativo — que é o que a FR-019 impede.

    Este teste é o que faz a tabela de rótulos envelhecer junto com o contrato: classificar um
    campo novo como não retificável e esquecer o rótulo derruba a suíte aqui.
    """
    excluidos = {
        chave for chave, decisao in CONTRATO.items() if decisao.natureza is Natureza.NAO_RETIFICAVEL
    }
    sem_rotulo = sorted(
        f"({colecao}, {caminho})" for colecao, caminho in excluidos - set(ROTULO_DO_EXCLUIDO)
    )
    assert sem_rotulo == [], "campo excluído sem rótulo em português:\n  " + "\n  ".join(sem_rotulo)


def test_a_tabela_de_rotulos_nao_cita_campo_que_se_corrige():
    """O contrário também: rótulo de exclusão para campo retificável seria lista envelhecida."""
    indevidos = sorted(
        f"({colecao}, {caminho})"
        for colecao, caminho in ROTULO_DO_EXCLUIDO
        if CONTRATO[(colecao, caminho)].natureza is not Natureza.NAO_RETIFICAVEL
    )
    assert indevidos == []


def test_o_bloco_comeca_fechado(client, seletor_ligado, edital):
    """Quem veio corrigir não atravessa a lista do que não se corrige para chegar aos campos."""
    identificar(client, "ana.elaboradora", ["elaborador"])
    corpo = client.get(reverse("interface:retificar", args=[edital.id])).content.decode()

    abertura = re.search(r'<details class="exclusoes"([^>]*)>', corpo)
    assert abertura, "o bloco de exclusões não foi renderizado"
    assert "open" not in abertura.group(1)


def test_nenhuma_razao_carrega_marcacao_de_markdown():
    """As razões nasceram comentário e viraram texto de tela — os asteriscos vêm junto.

    O navegador mostrou `**o que o Edital ofereceu**` literal na página, e nenhum teste pegou: o
    teste anterior recusava caminho de código, e ênfase de Markdown não é caminho de código. É a
    mesma classe de defeito uma segunda vez, e por isso vale uma asserção própria.

    A razão é lida por uma pessoa numa tela HTML. Nada nela é renderizado como marcação.
    """
    sujas = sorted(
        f"({colecao}, {caminho})"
        for (colecao, caminho), decisao in CONTRATO.items()
        if any(marca in decisao.razao for marca in ("**", "`", "](", "##"))
    )
    assert sujas == [], (
        "razão com marcação de Markdown, que a tela imprime literal:\n  " + "\n  ".join(sujas)
    )
