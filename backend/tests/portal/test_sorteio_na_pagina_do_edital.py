"""O sorteio anunciado **antes** de acontecer, na página que qualquer pessoa abre (021, FR-011).

**A promessa da feature era invisível onde precisava ser vista.** A relação de habilitados é
publicada dias antes, é imutável e é o compromisso do universo — e página nenhuma do portal a
apontava: ela só respondia no endereço da própria identidade. Quem se inscreveu não descobria que
participava de um sorteio, com que número, nem que a lista já estava fechada.

A garantia que a `021` existe para produzir — *o universo foi comprometido antes de a semente
existir* — era observável só **depois** do fato, pela divulgação do resultado, e apenas por quem já
tivesse o endereço. Provar depois e não contar antes é a diferença entre um sistema que prova e um
que convence.

**Desde a `145` o sorteio de cada vaga está no cartão dela**, e o bloco "Sorteio público" diz só o
que é do Edital inteiro. Os casos da `021` continuam valendo letra por letra — o que mudou foi onde
a página diz cada coisa, e os casos do fim deste arquivo são os dessa mudança.
"""

import re

import pytest
from django.urls import reverse

from processo_seletivo.sorteios.application.ocorrencia import observar_ocorrencia
from processo_seletivo.sorteios.application.relacao import publicar_relacao
from processo_seletivo.sorteios.application.sorteio import constituir_sorteio
from processo_seletivo.sorteios.models import RelacaoDeHabilitados, Sorteio
from tests.fixtures.sorteio import (
    LISTA_PCD,
    LISTA_PPI,
    METODO,
    certame_com_cotas,
    certame_de_sorteio,
    presidente,
)

pytestmark = [pytest.mark.integration, pytest.mark.django_db(transaction=True)]


@pytest.fixture
def certame(gestor, api_client, manager_headers, process_payload):
    return certame_de_sorteio(gestor, api_client, manager_headers, process_payload)


def _congelar(certame, *, chave="portal-sorteio-relacao", lista_id=None):
    declarado = publicar_relacao(
        actor=presidente(),
        processo_id=certame["processo"].id,
        edital_id=certame["edital"].id,
        perfil_id=certame["perfil"],
        marco_id=certame["marco"],
        lista_id=lista_id,
        idempotency_key=chave,
        correlation_id="teste-portal",
    )
    return RelacaoDeHabilitados.objects.get(pk=declarado["relacao"])


def _sortear(certame, relacao):
    ocorrencia = observar_ocorrencia(
        actor=presidente(),
        processo_id=certame["processo"].id,
        fonte=METODO["source"],
        referencia=METODO["occurrence"],
        idempotency_key="portal-sorteio-ocorrencia",
        correlation_id="teste-portal",
    )
    declarado = constituir_sorteio(
        actor=presidente(),
        processo_id=certame["processo"].id,
        edital_id=certame["edital"].id,
        relacao_id=str(relacao.id),
        ocorrencia_id=ocorrencia["ocorrencia"],
        idempotency_key=f"portal-sorteio-ato-{relacao.id}",
        correlation_id="teste-portal",
    )
    return Sorteio.objects.get(pk=declarado["sorteio"])


def _pagina(client, certame):
    resposta = client.get(reverse("portal:selecao", args=[certame["edital"].id]))
    assert resposta.status_code == 200
    return resposta.content.decode()


def test_sem_relacao_publicada_a_pagina_nao_inventa_bloco_de_sorteio(client, certame):
    """A mesma regra do Cronograma: bloco vazio afirmaria uma omissão que não existe (FR-128)."""
    assert "Sorteio público" not in _pagina(client, certame)


def test_publicada_a_relacao_a_pagina_diz_que_o_sorteio_esta_por_vir(client, certame):
    relacao = _congelar(certame)

    corpo = _pagina(client, certame)

    assert "Sorteio público" in corpo
    assert "Aguardando o sorteio" in corpo
    # **A frase que o cidadão precisa ler**, e que só o sistema pode afirmar: a lista fechou antes.
    assert "antes de existirem os números" in corpo
    assert f"{relacao.quantidade} candidatos habilitados" in corpo
    assert reverse("portal:relacao-de-habilitados", args=[relacao.id]) in corpo


def test_a_tabela_de_participantes_nao_vem_para_esta_pagina(client, certame):
    """O endereço estável da relação é onde ela vive — e é o que manifesto e ofício citam.

    Reproduzir 327 nomes no meio da página do Edital seria duplicar o artefato e poluir a leitura
    de quem veio decidir se participa.
    """
    relacao = _congelar(certame)
    corpo = _pagina(client, certame)

    for participante in relacao.participantes.select_related("inscricao"):
        assert participante.inscricao.nome not in corpo


def test_realizado_o_sorteio_a_pagina_muda_de_frase_e_abre_a_verificacao(client, certame):
    relacao = _congelar(certame)
    sorteio = _sortear(certame, relacao)

    corpo = _pagina(client, certame)

    assert "Sorteio realizado" in corpo
    assert "Aguardando o sorteio" not in corpo
    assert reverse("portal:verificar-sorteio", args=[sorteio.id]) in corpo
    # A relação continua alcançável depois: é dela que o resumo se recalcula (R-015).
    assert reverse("portal:relacao-de-habilitados", args=[relacao.id]) in corpo


def test_a_relacao_sucedida_nao_e_anunciada_como_atual(client, certame):
    """Só o vigente aparece: a sucedida continua no endereço dela, dizendo que foi sucedida."""
    primeira = _congelar(certame)
    segunda = publicar_relacao(
        actor=presidente(),
        processo_id=certame["processo"].id,
        edital_id=certame["edital"].id,
        perfil_id=certame["perfil"],
        marco_id=certame["marco"],
        idempotency_key="portal-relacao-nova",
        correlation_id="teste-portal",
        motivo="Resultado de origem sucedido.",
    )

    corpo = _pagina(client, certame)

    assert reverse("portal:relacao-de-habilitados", args=[segunda["relacao"]]) in corpo
    assert reverse("portal:relacao-de-habilitados", args=[primeira.id]) not in corpo


def test_o_bloco_custa_duas_consultas_e_nao_uma_por_recorte(client, certame):
    """Derivada zero, que é a regra que a `024` fixou para esta página.

    Duas consultas — as relações vigentes do Edital e os sorteios vigentes dele —, casadas em
    memória pelo recorte. Um certame com três listas, ou com sete polos, custa exatamente o mesmo:
    o que cresce é o tamanho do resultado, e não o número de idas ao banco.
    """
    from django.db import connection
    from django.test.utils import CaptureQueriesContext

    _congelar(certame)
    endereco = reverse("portal:selecao", args=[certame["edital"].id])

    with CaptureQueriesContext(connection) as consultas:
        client.get(endereco)

    do_sorteio = [
        consulta["sql"]
        for consulta in consultas.captured_queries
        if "sorteios_relacaodehabilitados" in consulta["sql"]
        or "sorteios_sorteio" in consulta["sql"]
    ]

    assert len(do_sorteio) == 2, do_sorteio


# --- 145: o sorteio de cada vaga no cartão dela, e o resumo do Edital antes das vagas -------------


@pytest.fixture
def com_cotas(gestor, api_client, manager_headers, process_payload):
    return certame_com_cotas(gestor, api_client, manager_headers, process_payload)


def _congelar_as_tres(certame):
    return {
        nome: _congelar(certame, chave=f"portal-145-{nome}", lista_id=lista_id)
        for nome, lista_id in (("ampla", None), ("ppi", LISTA_PPI), ("pcd", LISTA_PCD))
    }


def _cartao(corpo, certame):
    """O `<li>` da vaga, do começo dele ao fim — é onde o sorteio dela tem de estar."""
    inicio = corpo.index(f'<li class="perfil" id="vaga-{certame["perfil"]}">')
    seguinte = corpo.find('<li class="perfil"', inicio + 1)
    return corpo[inicio : seguinte if seguinte != -1 else corpo.index("</section>", inicio)]


def _resumo(corpo):
    inicio = corpo.index('<aside class="sorteio-da-selecao"')
    return corpo[inicio : corpo.index("</aside>", inicio)]


def test_a_relacao_da_vaga_esta_no_cartao_dela_e_so_nele(client, certame):
    """FR-5150, FR-5155, SC-1601: um acesso por relação, e ele está na vaga a que ela pertence."""
    relacao = _congelar(certame)
    endereco = reverse("portal:relacao-de-habilitados", args=[relacao.id])

    corpo = _pagina(client, certame)

    assert corpo.count(endereco) == 1
    assert endereco in _cartao(corpo, certame)
    assert endereco not in _resumo(corpo)
    # Uma lista só: o acesso é direto, sem controle para abrir (FR-5157).
    assert '<details class="listas-do-sorteio"' not in corpo
    assert "Ver quem vai participar, e com que número" in _cartao(corpo, certame)
    assert "Lista fechada em" in _cartao(corpo, certame)


def test_o_resumo_do_edital_vem_antes_das_vagas_e_nao_nomeia_vaga(client, certame):
    """FR-5158, FR-5159: a frase do Edital inteiro, antes de a pessoa procurar a vaga dela."""
    _congelar(certame)

    corpo = _pagina(client, certame)
    resumo = _resumo(corpo)

    assert corpo.index('<aside class="sorteio-da-selecao"') < corpo.index(
        '<section class="vagas-da-selecao"'
    )
    assert "Aguardando o sorteio" in resumo
    assert "antes de existirem os números" in resumo
    # A garantia é dita uma vez na página, e não uma por lista.
    assert corpo.count("antes de existirem os números") == 1
    assert "<h3" not in resumo


def test_a_lista_sem_modalidade_e_dita_ampla_concorrencia(client, certame):
    """FR-5153: o recorte sem lista é a ampla — o nome que a página da própria relação lhe dá."""
    _congelar(certame)

    assert "Ampla concorrência · " in _cartao(_pagina(client, certame), certame)


def test_tres_listas_abrem_sob_um_controle_com_a_ampla_primeiro(client, com_cotas):
    """FR-5152, FR-5157: o controle diz o que abre e quantas são; a ordem é a do Perfil."""
    relacoes = _congelar_as_tres(com_cotas)

    corpo = _pagina(client, com_cotas)
    cartao = _cartao(corpo, com_cotas)

    assert "<summary>Ver quem vai participar, e com que número — 3 listas</summary>" in cartao
    onde = {
        nome: cartao.index(reverse("portal:relacao-de-habilitados", args=[relacao.id]))
        for nome, relacao in relacoes.items()
    }
    # A ordem das reservas é a do conteúdo publicado — a mesma da linha "Concorrência" do cartão.
    concorrencia = cartao[cartao.index("Concorrência:") :]
    declaradas = sorted(
        ("ppi", "pcd"),
        key=lambda nome: concorrencia.index(
            {"ppi": "Pretos, pardos e indígenas", "pcd": "Pessoas com deficiência"}[nome]
        ),
    )
    assert sorted(onde, key=onde.get) == ["ampla", *declaradas]
    for nome in (
        ">Ampla concorrência<",
        ">Pretos, pardos e indígenas<",
        ">Pessoas com deficiência<",
    ):
        assert nome in cartao
    # SC-1601: três relações, três acessos — nenhum repetido fora do cartão.
    assert len(re.findall(r'href="/[^"]*sorteio/relacoes/', corpo)) == 3
    # O estado das três é um só, e é dito uma vez (FR-5154).
    assert cartao.count("Aguardando o sorteio") == 1
    assert "Listas fechadas em" in cartao


def test_sorteada_uma_lista_de_tres_o_cartao_e_o_resumo_dizem_o_andamento(client, com_cotas):
    """FR-5154, FR-5156, FR-5158: o estado misto não cabe numa frase só, e cada linha diz o seu."""
    relacoes = _congelar_as_tres(com_cotas)
    sorteio = _sortear(com_cotas, relacoes["ppi"])

    corpo = _pagina(client, com_cotas)
    cartao = _cartao(corpo, com_cotas)

    assert "Sorteio em andamento.</strong> 1 de 3 listas sorteadas." in cartao
    assert "1 de 3 sorteios realizados." in _resumo(corpo)
    assert "Ver quem participa, e com que número — 3 listas" in cartao
    assert cartao.count("aguardando; lista fechada em") == 2
    assert cartao.count("sorteado em") == 1
    assert corpo.count(reverse("portal:verificar-sorteio", args=[sorteio.id])) == 1
    assert reverse("portal:verificar-sorteio", args=[sorteio.id]) in cartao


def test_o_cartao_com_tres_listas_custa_as_mesmas_duas_consultas(client, com_cotas):
    """FR-5161, SC-1602: a reorganização é em memória; o banco é lido como a `021` o lia."""
    from django.db import connection
    from django.test.utils import CaptureQueriesContext

    _congelar_as_tres(com_cotas)
    endereco = reverse("portal:selecao", args=[com_cotas["edital"].id])

    with CaptureQueriesContext(connection) as consultas:
        client.get(endereco)

    do_sorteio = [
        consulta["sql"]
        for consulta in consultas.captured_queries
        if "sorteios_relacaodehabilitados" in consulta["sql"]
        or "sorteios_sorteio" in consulta["sql"]
    ]
    assert len(do_sorteio) == 2, do_sorteio


def test_a_versao_da_relacao_viaja_na_mesma_consulta(certame, django_assert_num_queries):
    """FR-5161: nomear a lista que o vigente já não diz não custa uma consulta por relação."""
    from processo_seletivo.sorteios.application.selectors import sorteios_do_edital

    _congelar(certame)
    edital = certame["edital"]
    itens = sorteios_do_edital(edital, {})

    with django_assert_num_queries(0):
        assert itens[0]["relacao"].versao.content
