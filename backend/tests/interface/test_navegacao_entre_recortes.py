"""As telas levam quem conduz a cada recorte (034, US2, FR-497 a FR-499, FR-504).

**O caminho é lido da própria página**, e nunca montado à mão pelo teste. Uma navegação que só
existe quando quem a testa já sabe o endereço é o `ACH-40` outra vez, com outra roupa — e este
projeto acabou de pagar por essa lição na `033`. Endereço digitado no teste passa mesmo quando a
tela não oferece caminho nenhum.
"""

import re

import pytest
from django.urls import reverse

from tests.fixtures.corte import MARCO
from tests.fixtures.recortes import (
    MODALIDADE_PCD,
    MODALIDADE_PPI,
    emitir_recorte,
    montar_cenario_7_1_2,
)
from tests.interface.conftest import identificar

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.integration]


@pytest.fixture
def cenario(gestor, api_client, manager_headers, process_payload):
    """Edital 7/1/2, com a ordem da ampla emitida e os dois recortes reservados ainda sem a sua."""
    return montar_cenario_7_1_2(
        gestor,
        api_client,
        manager_headers,
        process_payload,
        prefixo="navegacao-034",
    )


@pytest.fixture
def sem_reserva(gestor, api_client, manager_headers, process_payload):
    return montar_cenario_7_1_2(
        gestor,
        api_client,
        manager_headers,
        process_payload,
        prefixo="navegacao-034-sem-reserva",
        sem_reserva=True,
    )


def abrir(client, edital, *, lista=None, rota="interface:ordenacao"):
    endereco = reverse(rota, args=[edital.id, MARCO])
    if lista:
        endereco = f"{endereco}?lista={lista}"
    return client.get(endereco)


def caminhos_oferecidos(pagina):
    """Os `href` que a navegação entre recortes oferece — lidos da página, e não montados aqui."""
    bloco = re.search(r'<nav aria-label="Recortes deste marco".*?</nav>', pagina, re.S)
    if bloco is None:
        return []
    return re.findall(r'href="([^"]+)"', bloco.group(0))


# --- T031 · a tela nomeia o recorte e oferece os outros ----------------------------------------


def test_a_ordenacao_nomeia_os_tres_recortes_do_marco(client, seletor_ligado, cenario):
    """`FR-497`: a tela diz em qual recorte se está, e oferece caminho para os demais."""
    edital, _, _ = cenario
    identificar(client, "carlos", ["gestor"])

    pagina = abrir(client, edital).content.decode()

    assert "Ampla concorrência (linha geral do quadro)" in pagina
    assert "Pessoas com deficiência (PCD)" in pagina
    assert "Pretos, pardos e indígenas (PPI)" in pagina


def test_o_recorte_em_que_se_esta_nao_e_link_para_si_mesmo(client, seletor_ligado, cenario):
    """E é marcado com `aria-current`: quem lê por voz precisa da mesma informação que quem vê."""
    edital, _, _ = cenario
    identificar(client, "carlos", ["gestor"])

    pagina = abrir(client, edital).content.decode()

    assert 'aria-current="true">Ampla concorrência (linha geral do quadro)</span>' in pagina
    assert len(caminhos_oferecidos(pagina)) == 2, "os outros dois, e não os três"


def test_o_caminho_lido_da_pagina_abre_o_recorte_reservado(client, seletor_ligado, cenario):
    """O `Independent Test` da `US2`, ao pé da letra: o endereço vem do `href`, e não do teste."""
    edital, _, _ = cenario
    identificar(client, "carlos", ["gestor"])
    pagina = abrir(client, edital).content.decode()

    para_ppi = next(caminho for caminho in caminhos_oferecidos(pagina) if MODALIDADE_PPI in caminho)
    resposta = client.get(para_ppi)

    assert resposta.status_code == 200
    corpo = resposta.content.decode()
    assert 'aria-current="true">Pretos, pardos e indígenas (PPI)</span>' in corpo


def test_a_ordenacao_do_recorte_reservado_mostra_so_os_autodeclarados(
    client, seletor_ligado, cenario
):
    """A navegação leva ao recorte **e** o recorte é o certo — as duas metades importam."""
    edital, _, inscricoes = cenario
    identificar(client, "carlos", ["gestor"])

    pagina = abrir(client, edital, lista=MODALIDADE_PPI).content.decode()

    assert inscricoes[2].protocolo in pagina
    assert inscricoes[4].protocolo in pagina
    assert inscricoes[0].protocolo not in pagina, "quem não se autodeclarou não está neste recorte"


def test_a_tela_do_corte_tambem_oferece_os_outros_recortes(client, seletor_ligado, cenario):
    """`FR-497` na outra tela: ela já **recebia** o recorte e não oferecia caminho entre eles."""
    edital, _, _ = cenario
    identificar(client, "carlos", ["gestor"])

    pagina = abrir(client, edital, rota="interface:corte").content.decode()

    assert "Pretos, pardos e indígenas (PPI)" in pagina
    caminhos = caminhos_oferecidos(pagina)
    assert len(caminhos) == 2
    assert all("/corte" in caminho for caminho in caminhos), "o caminho fica na mesma tela"


def test_as_duas_telas_nomeiam_o_recorte_em_que_se_esta(client, seletor_ligado, cenario):
    """**As duas metades da `FR-497`**: oferecer os outros e dizer em qual se está.

    *Este caso nasceu de um defeito que o percurso do `quickstart` pegou e teste nenhum pegava:* a
    tela do corte recebia `recortes` e não recebia `recorte_atual`, e o cabeçalho saía com
    *"Recorte:"* seguido de nada — o mecanismo de template trata variável ausente como vazia, e por
    isso não houve erro, exceção nem teste vermelho. O caso anterior passava, porque conferia só a
    lista de caminhos.
    """
    edital, _, _ = cenario
    identificar(client, "carlos", ["gestor"])

    for rota in ("interface:ordenacao", "interface:corte"):
        pagina = abrir(client, edital, lista=MODALIDADE_PPI, rota=rota).content.decode()

        assert "Recorte: <strong>Pretos, pardos e indígenas (PPI)</strong>" in pagina, rota


def test_edital_sem_reserva_nao_ganha_navegacao_nova(client, seletor_ligado, sem_reserva):
    """A contraprova da `FR-493` vista na tela: um recorte só não é uma escolha."""
    edital, _, _ = sem_reserva
    identificar(client, "carlos", ["gestor"])

    pagina = abrir(client, edital).content.decode()

    assert caminhos_oferecidos(pagina) == []
    assert "Recortes deste marco" not in pagina


# --- T031 · o recorte sem ordem diz o que falta, e o inexistente é 404 --------------------------


def test_o_recorte_sem_ordem_diz_o_que_falta_e_onde_se_faz(client, seletor_ligado, cenario):
    """`FR-498`: a ausência de ordem é um estado do percurso, e não um erro."""
    edital, _, _ = cenario
    identificar(client, "carlos", ["gestor"])

    pagina = abrir(client, edital, lista=MODALIDADE_PPI).content.decode()

    assert "ainda não tem ordem própria" in pagina
    assert "Emitir ordem" in pagina, "e a ação que resolve está na mesma tela"


def test_o_corte_do_recorte_sem_ordem_leva_a_classificacao_dele(client, seletor_ligado, cenario):
    """`FR-498` na tela do corte, que é onde a frase *"não há o que cortar"* era o fim da linha."""
    edital, _, _ = cenario
    identificar(client, "carlos", ["gestor"])

    pagina = abrir(client, edital, lista=MODALIDADE_PPI, rota="interface:corte").content.decode()

    assert "ainda não tem ordem emitida" in pagina
    assert "emita a ordem deste recorte" in pagina
    destino = reverse("interface:ordenacao", args=[edital.id, MARCO])
    assert f'href="{destino}?lista={MODALIDADE_PPI}"' in pagina


def test_recorte_que_nao_e_modalidade_do_perfil_responde_404(client, seletor_ligado, cenario):
    """`FR-499`: "não existe" e "existe e está vazio" são coisas diferentes.

    Confundi-las esconde erro de digitação — quem pede o recorte errado veria uma tela legítima e
    vazia, e concluiria que ninguém concorreu ali.
    """
    edital, _, _ = cenario
    identificar(client, "carlos", ["gestor"])

    alheia = "cccccccc-0000-4000-8000-0000000004ff"
    assert abrir(client, edital, lista=alheia).status_code == 404
    assert abrir(client, edital, lista=alheia, rota="interface:corte").status_code == 404


def test_recorte_que_nem_identidade_e_continua_respondendo_404(client, seletor_ligado, cenario):
    """O que não é identidade é ausência, e nunca lixo para o ORM — a guarda anterior fica de pé."""
    edital, _, _ = cenario
    identificar(client, "carlos", ["gestor"])

    assert abrir(client, edital, lista="abc").status_code == 404


# --- T021 (tela) · o recorte em que ninguém concorreu -------------------------------------------


def test_o_recorte_sem_autodeclarado_diz_que_ninguem_concorreu(
    client, seletor_ligado, gestor, api_client, manager_headers, process_payload
):
    """`FR-492a`: a tela não pode parecer pendência quando não há trabalho a fazer.

    "Ninguém se inscreveu por esta cota" e "ainda não emitiram" são indistinguíveis sem esta frase —
    e a diferença entre as duas é quem tem trabalho a fazer.
    """
    edital, _, _ = montar_cenario_7_1_2(
        gestor,
        api_client,
        manager_headers,
        process_payload,
        prefixo="navegacao-034-vazio",
        autodeclarar=False,
    )
    identificar(client, "carlos", ["gestor"])

    pagina = abrir(client, edital, lista=MODALIDADE_PCD).content.decode()

    assert "Ninguém concorreu por este recorte" in pagina
    assert "ainda não tem ordem própria" not in pagina, "não é a frase da pendência"
    assert "Emitir ordem" in pagina, "e emitir continua sendo ato de quem conduz"


# --- T032 · o Edital que emitiu a ordem única antes desta feature --------------------------------


def test_o_recorte_sem_ordem_explica_a_ordem_unica_que_o_marco_tem(client, seletor_ligado, cenario):
    """`FR-504`: a tela **diz o que aquilo é**, e não oferece correção.

    Comparar conteúdo e resumo prova que nada do acervo foi reescrito; **não** prova que a tela
    explica o que o operador está vendo. É esta metade da `FR-504` que a conferência do acervo não
    alcança.
    """
    edital, _, _ = cenario
    identificar(client, "carlos", ["gestor"])

    pagina = abrir(client, edital, lista=MODALIDADE_PPI).content.decode()

    assert "ordem da ampla concorrência" in pagina
    assert "alcança <em>todos</em> os inscritos do Perfil" in pagina
    assert "continua vigente" in pagina


def test_a_tela_nao_oferece_corrigir_a_ordem_unica(client, seletor_ligado, cenario):
    """Publicação é ato imutável: oferecer conserto que ela não permite é pior do que nada.

    O caminho oferecido é o de **consultar** o ato da ampla, e o de **emitir** a ordem deste
    recorte. Nenhum dos dois altera o que foi emitido.
    """
    edital, _, _ = cenario
    identificar(client, "carlos", ["gestor"])

    pagina = abrir(client, edital, lista=MODALIDADE_PPI).content.decode()

    assert "Consultar a ordem da ampla concorrência" in pagina
    for proibida in ("Corrigir a ordem", "Refazer a ordem", "Substituir a ordem"):
        assert proibida not in pagina


def test_depois_de_emitida_a_ordem_do_recorte_a_explicacao_sai(
    client, seletor_ligado, cenario, gestor
):
    """A frase é de um estado, e não da tela: emitido o ato, ela deixa de ser verdadeira e sai."""
    edital, _, _ = cenario
    emitir_recorte(edital, gestor, lista_id=MODALIDADE_PPI, chave="navegacao-034-emitir")
    identificar(client, "carlos", ["gestor"])

    pagina = abrir(client, edital, lista=MODALIDADE_PPI).content.decode()

    assert "ainda não tem ordem própria" not in pagina
    assert "Ato vigente emitido em" in pagina


def test_o_historico_da_tela_e_o_do_recorte_e_nao_o_do_marco(
    client, seletor_ligado, cenario, gestor
):
    """Três cadeias num histórico só mostrariam três raízes e três sucessões como se fossem uma.

    A frase "primeiro ato do marco" apareceria três vezes, e nenhuma delas explicaria as outras.
    """
    edital, _, _ = cenario
    emitir_recorte(edital, gestor, lista_id=MODALIDADE_PPI, chave="navegacao-034-hist-ppi")
    emitir_recorte(edital, gestor, lista_id=MODALIDADE_PCD, chave="navegacao-034-hist-pcd")
    identificar(client, "carlos", ["gestor"])

    do_ppi = abrir(client, edital, lista=MODALIDADE_PPI).content.decode()

    historico = re.search(r'<section aria-labelledby="titulo-historico".*?</section>', do_ppi, re.S)
    assert historico is not None
    assert historico.group(0).count("<li>") == 1, "um ato — o deste recorte, e não os três"


# --- A confirmação não troca de recorte pelo caminho (034, FR-490, FR-497) ----------------------
#
# **Os três casos abaixo vieram de revisão, e não de spec.** Uma tela de confirmação de ato
# imutável que perde o recorte no caminho de volta, ou que afirma ser o primeiro ato do marco
# quando é o primeiro daquele recorte, não produz erro nenhum: produz uma pessoa decidindo sobre
# outra coisa. É o mesmo defeito silencioso que a `FR-502` descreve, entrando pela porta do texto.


def confirmar(client, edital, *, lista=None):
    """O primeiro passo da emissão: o POST sem `confirmar=1`, que devolve a tela de conferência."""
    dados = {"chave_idempotencia": "navegacao-034-confirmar"}
    if lista:
        dados["lista"] = lista
    return client.post(reverse("interface:emitir-ordenacao", args=[edital.id, MARCO]), dados)


def test_a_confirmacao_volta_para_o_recorte_que_se_esta_confirmando(
    client, seletor_ligado, cenario
):
    """Cancelar numa conferência de PPI não pode devolver a pessoa à ampla concorrência.

    A tela que abriria seria **legítima** — uma ordem verdadeira, de um recorte verdadeiro —, e é
    isso que torna o desvio silencioso: nada avisa que se trocou de lista.
    """
    edital, _, _ = cenario
    identificar(client, "carlos", ["gestor"])

    pagina = confirmar(client, edital, lista=MODALIDADE_PPI).content.decode()

    destino = reverse("interface:ordenacao", args=[edital.id, MARCO])
    assert pagina.count(f'href="{destino}?lista={MODALIDADE_PPI}"') == 2, (
        "a trilha e o «Cancelar e voltar», os dois preservando o recorte"
    )
    assert f'href="{destino}"' not in pagina, "e nenhum dos dois cai na ampla"


def test_a_confirmacao_do_recorte_novo_nao_diz_ser_o_primeiro_ato_do_marco(
    client, seletor_ligado, cenario
):
    """`FR-490`: o vigente é lido por recorte, e a frase tem de acompanhar.

    O marco já tem a ordem da ampla — o cenário a emite. Ao confirmar a primeira ordem de PPI,
    `ato_vigente` vem vazio **porque é vazio naquele recorte**, e dizer "primeiro ato deste marco"
    afirmaria, numa confirmação de ato imutável, que o marco não tem ato nenhum.
    """
    edital, _, _ = cenario
    identificar(client, "carlos", ["gestor"])

    pagina = confirmar(client, edital, lista=MODALIDADE_PPI).content.decode()

    assert "é o primeiro ato deste recorte" in pagina
    assert "primeiro ato deste marco" not in pagina


def test_o_historico_do_recorte_nomeia_a_raiz_como_do_recorte(
    client, seletor_ligado, cenario, gestor
):
    """A mesma frase, na tela que fica: a raiz listada é a daquela cadeia, e não a do marco."""
    edital, _, _ = cenario
    emitir_recorte(edital, gestor, lista_id=MODALIDADE_PPI, chave="navegacao-034-raiz")
    identificar(client, "carlos", ["gestor"])

    pagina = abrir(client, edital, lista=MODALIDADE_PPI).content.decode()

    assert "primeiro ato deste recorte" in pagina
    assert "primeiro ato do marco" not in pagina
