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
    """Um marco com cota tem dois recortes, e listá-los juntos evita esquecer um (`SC-078`).

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
    # **Acentuado**, e a asserção anterior dizia `"O deficit apurado"`: ela prendia na tela a
    # grafia sem acento que o percurso conduzido encontrou. A varredura de
    # `tests/test_vocabulario_da_ocupacao.py` é quem guarda a regra; aqui fica o caso concreto.
    assert "O déficit apurado de 3 vaga(s) será a causa do ato" in depois


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


def test_o_historico_do_recorte_e_alcancavel_e_lista_as_apuracoes(
    client, seletor_ligado, cenario, gestor
):
    """**`T058`**: a série de um recorte, lida como ela foi emitida.

    A tela existe porque correção é sucessão: a apuração anterior continua dizendo o que apurou, e
    quem audita precisa ver as duas. A rota pende do marco e o recorte vem em `?lista=`, como a da
    leitura — o que se lista é a série de um recorte.
    """
    edital, _, _ = cenario
    apurar(edital, gestor)
    apurar(edital, gestor, chave="hist-016-2", motivo="Reanálise documental")
    identificar(client, "carlos", ["gestor"])

    pagina = client.get(
        reverse("interface:ocupacao-historico", args=[edital.id, MARCO])
    ).content.decode()

    assert "Apuração 1 de 2" in pagina
    assert "Apuração 2 de 2" in pagina
    assert "sucedida" in pagina and "vigente" in pagina
    assert "Reanálise documental" in pagina
    # A proveniência de cada uma: versão lida, linha do quadro, ordem e corte.
    assert "Versão do conteúdo lida" in pagina
    assert "Linha do quadro" in pagina


def test_o_historico_de_recorte_sem_apuracao_diz_que_nada_foi_afirmado(
    client, seletor_ligado, cenario
):
    """Sem apuração não há histórico — e a tela **não** inventa linha vazia."""
    edital, _, _ = cenario
    identificar(client, "carlos", ["gestor"])

    pagina = client.get(
        reverse("interface:ocupacao-historico", args=[edital.id, MARCO])
    ).content.decode()

    assert "ainda não tem apuração emitida" in pagina
    assert "nenhum número foi afirmado" in pagina


def test_o_link_do_historico_so_aparece_onde_ha_apuracao(client, seletor_ligado, cenario, gestor):
    """Oferecer o histórico de um recorte sem apuração levaria a uma tela que diz "não há nada"."""
    edital, _, _ = cenario
    identificar(client, "carlos", ["gestor"])

    antes = abrir(client, edital).content.decode()
    assert "Ver o histórico deste recorte" not in antes

    apurar(edital, gestor)
    depois = abrir(client, edital).content.decode()

    assert "Ver o histórico deste recorte" in depois


def test_o_historico_sobrevive_a_retificacao_que_remove_o_marco(
    client, seletor_ligado, cenario, gestor, api_client
):
    """**`T058` em letras, e a primeira versão desta tela a contrariava.**

    A tarefa pedia o histórico acessível depois de o marco sair da norma, e o precedente é o
    `corte-historico`. Minha primeira view resolvia o Perfil por `_perfil_do_marco`, que lê a versão
    **vigente** e levanta 404 quando o marco não está nela — de modo que uma Retificação que
    removesse o marco faria desaparecer justamente o histórico antigo, o que mais importa.

    As apurações guardam Perfil e marco como **identidades publicadas**. É por elas que a série é
    encontrada, e é isso que este teste prende.
    """
    from tests.fixtures.edital import PROFILE_ID as PERFIL
    from tests.fixtures.publicacao import retify

    edital, _, _ = cenario
    apurar(edital, gestor)
    identificar(client, "carlos", ["gestor"])
    url = reverse("interface:ocupacao-historico", args=[edital.id, MARCO])
    assert "Apuração 1 de 1" in client.get(url).content.decode()

    retify(
        api_client,
        edital,
        [
            {
                "targetPath": f"/profiles/id={PERFIL}/classificationMilestones/id={MARCO}",
                "operation": "REMOVE",
            }
        ],
        suffix="remove-marco-016",
    )

    # **A prova de que o teste não é vácuo**: o marco saiu da versão vigente, e a tela da ocupação
    # — que resolve o marco no snapshot, e deve — passa a dar 404. O histórico, não.
    assert client.get(reverse("interface:ocupacao", args=[edital.id, MARCO])).status_code == 404

    resposta = client.get(url)

    assert resposta.status_code == 200, "o histórico do marco removido continua acessível"
    assert "Apuração 1 de 1" in resposta.content.decode()


def test_as_duas_acoes_da_tela_confirmam_coisas_diferentes(
    client,
    seletor_ligado,
    db,
    gestor,
    api_client,
    manager_headers,
    process_payload,
    raiz_de_arquivos,
):
    """**O aviso diz qual ato aconteceu, e não só que algo deu certo.**

    As duas ações voltam para esta tela, e um aviso único dizia "Apuração emitida" depois de causar
    a faixa seguinte: frase falsa — apuração nenhuma foi emitida ali —, e quem acabara de pedir a
    faixa ficava sem confirmação de que ela saiu, diante de uma ação que não se desfaz. Encontrado
    no percurso conduzido, onde a única pista de que a faixa existia era a tela do corte dizer
    "2 faixas".
    """
    from tests.fixtures.corte import regra
    from tests.fixtures.ocupacao import montar_cenario_da_ocupacao

    # **Um Edital que admite continuação**, senão a segunda ação é recusada pela `014` e o teste
    # mediria a recusa em vez da confirmação.
    edital, _, _ = montar_cenario_da_ocupacao(
        gestor,
        api_client,
        manager_headers,
        process_payload,
        prefixo="tela-016-duas",
        geral=3,
        cut=regra(continuation="ALLOWED"),
    )
    identificar(client, "carlos", ["gestor"])
    apurar(edital, gestor, chave="tela-016-duas-primeira")

    depois_de_apurar = client.post(
        reverse("interface:emitir-apuracao", args=[edital.id, MARCO]),
        {"lista": "", "chave": "tela-016-duas-acoes", "motivo": "Reanálise documental"},
        follow=True,
    ).content.decode()

    assert "Apuração emitida" in depois_de_apurar
    assert "Faixa seguinte emitida" not in depois_de_apurar

    depois_da_faixa = client.post(
        reverse("interface:causar-faixa", args=[edital.id, MARCO]),
        {"lista": "", "chave": "tela-016-faixa"},
        follow=True,
    ).content.decode()

    assert "Faixa seguinte emitida com o déficit apurado como causa" in depois_da_faixa
    assert "Apuração emitida" not in depois_da_faixa, "nenhuma apuração foi emitida nesta ação"
