"""A tela da ocupação: os quatro números, os estados que não são zero, e o GET que não apura (016).

**O que só um teste de interface alcança** é o defeito que nasce no GET: um número regenerado ao
abrir a tela passaria a afirmar ocupação que ato nenhum sustenta. O domínio não o pega, porque lá
ninguém abre tela.
"""

import pytest
from django.urls import reverse

from processo_seletivo.ocupacao.models import ApuracaoDeOcupacao
from tests.fixtures.corte import MARCO
from tests.fixtures.edital import PROFILE_ID
from tests.integration.ocupacao.test_emissao import apurar
from tests.interface.conftest import identificar

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.integration]


def abrir(client, edital):
    return client.get(reverse("interface:ocupacao", args=[edital.id, MARCO]))


def test_a_rota_pende_do_marco_como_a_do_corte():
    """O recorte é o do marco, e a tela lista todas as listas dele juntas."""
    caminho = reverse(
        "interface:ocupacao",
        args=["00000000-0000-4000-8000-000000000001", "00000000-0000-4000-8000-000000000002"],
    )

    assert caminho.endswith("/ocupacao")
    assert "/marcos/" in caminho


def test_as_duas_rotas_da_ocupacao_sao_distintas():
    edital = "00000000-0000-4000-8000-000000000001"
    marco = "00000000-0000-4000-8000-000000000002"

    leitura = reverse("interface:ocupacao", args=[edital, marco])
    emissao = reverse("interface:emitir-apuracao", args=[edital, marco])

    assert leitura != emissao
    assert emissao.endswith("/ocupacao/apurar")


def test_a_tela_diz_os_quatro_numeros_depois_de_apurar(client, seletor_ligado, cenario, gestor):
    """Os quatro juntos, e **nunca um deles sozinho** (`UX-031`)."""
    edital, _, _ = cenario
    apurar(edital, gestor)
    identificar(client, "carlos", ["gestor"])

    pagina = abrir(client, edital).content.decode()

    assert "Publicadas" in pagina
    assert "Efetivas" in pagina
    assert "Ocupadas" in pagina
    assert "A ocupar" in pagina


def test_sem_apuracao_a_tela_diz_que_nao_apurou_e_nao_mostra_zero(client, seletor_ligado, cenario):
    """**`UX-032a`**: a ausência é dita com palavras, e não desenhada como zero.

    O que aparece é a quantidade **publicada** — fato do Edital — e a ação de emitir. As três
    quantidades de apuração não são desenhadas de forma alguma: nem como `0`, nem como traço que
    pareça número.
    """
    edital, _, _ = cenario
    identificar(client, "carlos", ["gestor"])

    pagina = abrir(client, edital).content.decode()

    assert "Ocupação ainda não apurada" in pagina
    assert "Publicadas" in pagina
    # As três de apuração não aparecem enquanto não há ato.
    assert "Ocupadas" not in pagina
    assert "A ocupar" not in pagina
    assert "Efetivas" not in pagina


def test_sem_quadro_publicado_a_tela_o_diz_e_nao_mostra_zero(
    client,
    seletor_ligado,
    db,
    gestor,
    api_client,
    manager_headers,
    process_payload,
    raiz_de_arquivos,
):
    """**`UX-032`**: mostrar `0` aqui afirmaria que o Edital publicou nenhuma vaga."""
    from tests.fixtures.corte import montar_cenario_do_corte

    edital, _, _ = montar_cenario_do_corte(
        gestor, api_client, manager_headers, process_payload, prefixo="ocupacao-016-tela"
    )
    identificar(client, "carlos", ["gestor"])

    pagina = abrir(client, edital).content.decode()

    assert "não publicou quadro de vagas" in pagina
    assert "Publicadas" not in pagina


def test_abrir_a_tela_nao_apura(client, seletor_ligado, cenario):
    """**Ler não ocupa** (`FR-261`), como ler não corta. É o defeito que nasce no GET."""
    edital, _, _ = cenario
    identificar(client, "carlos", ["gestor"])

    for _ in range(3):
        assert abrir(client, edital).status_code == 200

    assert ApuracaoDeOcupacao.objects.count() == 0


def test_a_tela_lista_um_bloco_por_recorte(client, seletor_ligado, cenario, gestor):
    """Um marco com cota tem dois recortes, e listá-los juntos evita esquecer um.

    **O rótulo do recorte sem lista diz o que ele é.** A `021` pagou o preço de não dizer: num
    Edital que declara uma Modalidade chamada "Ampla concorrência", a tela mostrava dois blocos
    homônimos, e quem conduz o certame não sabia em qual agir.
    """
    edital, _, _ = cenario
    identificar(client, "carlos", ["gestor"])

    pagina = abrir(client, edital).content.decode()

    assert "Ampla concorrência (linha geral do quadro)" in pagina
    assert "Pretos, pardos e indígenas (PPI)" in pagina


def test_a_emissao_pela_tela_grava_e_volta_para_a_leitura(client, seletor_ligado, cenario, gestor):
    """POST-redirect-GET, como o corte: a emissão não deixa a tela num estado de formulário."""
    edital, _, _ = cenario
    identificar(client, "carlos", ["gestor"])

    resposta = client.post(
        reverse("interface:emitir-apuracao", args=[edital.id, MARCO]),
        {"lista": "", "chave": "tela-016-apurar"},
    )

    assert resposta.status_code == 302
    assert ApuracaoDeOcupacao.objects.count() == 1
    apuracao = ApuracaoDeOcupacao.objects.get()
    assert apuracao.perfil_id == PROFILE_ID or str(apuracao.perfil_id) == PROFILE_ID


def test_a_pagina_nao_tem_tabela_horizontal_a_375px(client, seletor_ligado, cenario, gestor):
    """A 375 px nada rola na horizontal: os números vão em `dl`, e não em tabela larga.

    É a mesma verificação que a `013` deixou pendente na `T063` e que a `020` passou a fazer por
    teste: a estrutura é conferida aqui, e não no olho.
    """
    edital, _, _ = cenario
    apurar(edital, gestor)
    identificar(client, "carlos", ["gestor"])

    pagina = abrir(client, edital).content.decode()

    assert "<table" not in pagina
    # `dl.meta` é o vocabulário que as telas irmãs já usam para pares rótulo/valor. Classe nova
    # exigiria regra nova na folha, e a varredura de CSS recusa classe sem desenho.
    assert 'class="meta"' in pagina


def test_a_acao_da_faixa_seguinte_aparece_so_onde_ha_deficit(
    client, seletor_ligado, cenario, gestor
):
    """Sem apuração não há déficit, e sem déficit a ação não é oferecida (`FR-256`).

    Oferecer o botão e recusar no clique seria descobrir a recusa com o cronograma correndo — a
    tela mostra o que ela consegue conferir enquanto a pessoa lê.
    """
    edital, _, _ = cenario
    identificar(client, "carlos", ["gestor"])

    antes = abrir(client, edital).content.decode()
    assert "Pedir a faixa seguinte" not in antes

    apurar(edital, gestor)
    depois = abrir(client, edital).content.decode()

    assert "Pedir a faixa seguinte" in depois
    assert "O deficit apurado de 3 vaga(s)" in depois


def test_as_tres_rotas_da_ocupacao_sao_distintas():
    """Ler, apurar e causar a faixa são três coisas, e cada uma tem a sua rota."""
    edital = "00000000-0000-4000-8000-000000000001"
    marco = "00000000-0000-4000-8000-000000000002"

    rotas = {
        reverse("interface:ocupacao", args=[edital, marco]),
        reverse("interface:emitir-apuracao", args=[edital, marco]),
        reverse("interface:causar-faixa", args=[edital, marco]),
    }

    assert len(rotas) == 3


def test_a_tela_nomeia_a_reversao_e_explica_a_divergencia(
    client,
    seletor_ligado,
    db,
    gestor,
    api_client,
    manager_headers,
    process_payload,
    raiz_de_arquivos,
):
    """**`UX-033`**: o movimento aparece nomeado, com origem, destino e quantidade.

    **Há uma espécie só na tela, e a ausência da segunda é deliberada.** A concorrência
    concomitante não move quantidade nenhuma — ela aparece como ocupação menor na lista reservada,
    e não como movimento, porque nada se moveu. Desenhá-la como movimento foi o defeito que a
    revisão da US4 derrubou.

    O certame é de **sorteio**, porque é o único em que a reversão é alcançável.
    """
    from processo_seletivo.ocupacao.application.emissao import emitir_apuracao
    from processo_seletivo.ocupacao.domain import nomes
    from tests.fixtures.edital import PROFILE_ID as PERFIL
    from tests.fixtures.ocupacao_sorteada import LISTA_PPI, certame_sorteado_com_quadro
    from tests.fixtures.sorteio import MARCO as MARCO_SORT

    certame = certame_sorteado_com_quadro(
        gestor,
        api_client,
        manager_headers,
        process_payload,
        prefixo="tela-mov-016",
        reversao=nomes.REVERSAO_POR_SALDO,
    )
    emitir_apuracao(
        actor=gestor,
        processo_id=certame["processo"].id,
        edital_id=certame["edital"].id,
        perfil_id=PERFIL,
        marco_id=MARCO_SORT,
        lista_id=LISTA_PPI,
        idempotency_key="tela-mov-016-ppi",
        correlation_id="teste-ocupacao-016",
    )
    emitir_apuracao(
        actor=gestor,
        processo_id=certame["processo"].id,
        edital_id=certame["edital"].id,
        perfil_id=PERFIL,
        marco_id=MARCO_SORT,
        idempotency_key="tela-mov-016-ampla",
        correlation_id="teste-ocupacao-016",
    )
    identificar(client, "carlos", ["gestor"])

    pagina = client.get(
        reverse("interface:ocupacao", args=[certame["edital"].id, MARCO_SORT])
    ).content.decode()

    assert "Reversão de cota" in pagina
    assert "da lista reservada para a ampla concorrência" in pagina
    # E a divergência entre publicada e efetiva é explicada, em vez de o número mudar calado.
    assert "As efetivas divergem das publicadas" in pagina
