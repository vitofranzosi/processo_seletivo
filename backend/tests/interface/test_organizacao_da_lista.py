"""A organização da lista de Processos Seletivos (129): recorte, busca, página, faixa e linha.

**O invariante que torna o recorte seguro** é a faixa: ela lê a unidade inteira, e é a mesma em
toda aba, busca e página (FR-4323, D-006). Os casos da US2 o prendem com um recurso aguardando
decisão num Edital de Processo **encerrado** — o único ato com providência que o domínio aceita
nesse estado, e que o recorte padrão esconde da lista.
"""

import re

import pytest
from django.test import Client
from django.urls import reverse

from processo_seletivo.interface import trabalho
from processo_seletivo.processos.models import Edital, ProcessoSeletivo
from tests.fixtures.autoridades import CEFOR
from tests.fixtures.lista_de_processos import muitos, processo
from tests.interface.conftest import identificar

pytestmark = [
    pytest.mark.django_db,
    pytest.mark.integration,
    pytest.mark.usefixtures("seletor_ligado"),
]

Status = ProcessoSeletivo.Status
LISTA = reverse("interface:lista")


def sessao(subject="gabi.gestora", papeis=("gestor",)):
    cliente = Client()
    identificar(cliente, subject, list(papeis))
    return cliente


def abrir(cliente, consulta=""):
    resposta = cliente.get(LISTA + consulta)
    assert resposta.status_code == 200, resposta.content
    return resposta


def corpo(cliente, consulta=""):
    return abrir(cliente, consulta).content.decode()


def mostrados(resposta):
    return [p.title for p in resposta.context["processos"]]


def aba_atual(html):
    return re.findall(r'class="aba-da-lista" href="[^"]*" aria-current="page">([^<]+) <', html)


# ---------------------------------------------------------------------------------------------
# US1 — o que está em andamento, 20 por vez
# ---------------------------------------------------------------------------------------------


def test_o_padrao_abre_em_andamento_e_o_selo_diz_a_situacao_real():
    processo("Em elaboração", status=Status.EM_ELABORACAO)
    processo("Ativo com Editais encerrados", editais=[("1", 2026, "ENCERRADO")])
    processo(
        "Encerrado anterior a 28/09", status=Status.ENCERRADO, editais=[("2", 2026, "PUBLICADO")]
    )
    processo("Encerrado de fato", status=Status.ENCERRADO, editais=[("3", 2026, "ENCERRADO")])
    processo("Cancelado de fato", status=Status.CANCELADO)

    resposta = abrir(sessao())
    html = resposta.content.decode()

    assert aba_atual(html) == ["Em andamento"]
    assert set(mostrados(resposta)) == {
        "Em elaboração",
        "Ativo com Editais encerrados",
        "Encerrado anterior a 28/09",
    }
    # O selo do Processo puxado pelo Edital publicado diz "Encerrado", e não "Em andamento".
    cartao = html.split("Encerrado anterior a 28/09</a>")[1].split("</header>")[0]
    assert '<span class="situacao s-ENCERRADO">Encerrado</span>' in cartao
    assert 'Em andamento <span class="contagem-da-aba">(3)</span>' in html
    assert 'Encerrados <span class="contagem-da-aba">(1)</span>' in html
    assert 'Cancelados <span class="contagem-da-aba">(1)</span>' in html
    assert 'Todos <span class="contagem-da-aba">(5)</span>' in html


def test_61_processos_vinte_por_pagina_com_a_navegacao():
    muitos(61)
    gestora = sessao()

    primeira = abrir(gestora)
    html = primeira.content.decode()
    assert "61 Processos, mostrando 1–20." in html
    assert len(mostrados(primeira)) == 20 and html.count('<article class="processo">') == 20
    assert f'<a href="{LISTA}?pagina=2" rel="next">Próxima</a>' in html
    assert "Página 1 de 4" in html and 'rel="prev"' not in html

    segunda = abrir(gestora, "?pagina=2")
    assert "61 Processos, mostrando 21–40." in segunda.content.decode()
    assert f'<a href="{LISTA}" rel="prev">Anterior</a>' in segunda.content.decode()
    assert set(mostrados(primeira)).isdisjoint(mostrados(segunda))

    # O endereço reproduz o recorte: o mesmo pedido, a mesma página (FR-4313).
    assert mostrados(abrir(gestora, "?pagina=2")) == mostrados(segunda)
    # Além da última, a última; inválida, a primeira (FR-4315).
    assert "mostrando 61–61." in corpo(gestora, "?pagina=99")
    assert mostrados(abrir(gestora, "?pagina=0")) == mostrados(primeira)
    assert mostrados(abrir(gestora, "?pagina=abc&situacao=xyz")) == mostrados(primeira)


def test_trocar_de_aba_volta_a_pagina_um_e_os_links_preservam_a_aba():
    muitos(25, status=Status.CANCELADO, situacao_do_edital="CANCELADO")
    gestora = sessao()

    html = corpo(gestora, "?pagina=2")
    assert f'<a class="aba-da-lista" href="{LISTA}?situacao=cancelados">Cancelados' in html

    canceladas = corpo(gestora, "?situacao=cancelados")
    assert aba_atual(canceladas) == ["Cancelados"]
    assert "25 Processos, mostrando 1–20." in canceladas
    assert f'href="{LISTA}?situacao=cancelados&amp;pagina=2" rel="next"' in canceladas


def test_a_aba_vazia_e_a_unidade_vazia():
    gestora = sessao()

    vazia = corpo(gestora)
    assert "Nenhum Processo Seletivo no seu escopo institucional." in vazia
    assert "Nenhum Processo nesta situação." not in vazia
    assert 'Todos <span class="contagem-da-aba">(0)</span>' in vazia

    processo("Só em andamento")
    sem_encerrados = corpo(gestora, "?situacao=encerrados")
    assert "Nenhum Processo nesta situação." in sem_encerrados
    assert "Nenhum Processo Seletivo no seu escopo" not in sem_encerrados


def test_o_processo_sem_edital_e_a_navegacao_sem_memoria():
    processo("Sem Edital", status=Status.EM_ELABORACAO)
    gestora = sessao()

    assert "Nenhum Edital neste Processo." in corpo(gestora)
    # O recorte não fica em sessão (FR-4316): depois de "Cancelados", a lista volta ao padrão.
    corpo(gestora, "?situacao=cancelados")
    assert aba_atual(corpo(gestora)) == ["Em andamento"]
    # A barra lateral leva ao endereço sem parâmetro.
    assert f'href="{LISTA}"' in corpo(gestora, "?situacao=todos")


def test_o_subtitulo_nomeia_a_unidade_e_a_ordem_de_leitura():
    muitos(21)
    html = corpo(sessao())

    assert f"Processos e Editais da unidade <strong>{CEFOR['nome']}</strong>." in html
    marcas = [
        'class="sem-acoes"',
        "Novo Processo Seletivo",
        'class="abas-da-lista"',
        'class="busca-da-lista"',
        'class="frase-do-recorte"',
        '<article class="processo">',
        '<nav class="paginacao"',
    ]
    posicoes = [html.index(marca) for marca in marcas]
    assert posicoes == sorted(posicoes), dict(zip(marcas, posicoes, strict=True))


# ---------------------------------------------------------------------------------------------
# US2 — a faixa não depende da aba, da busca nem da página
# ---------------------------------------------------------------------------------------------

RECORTES = ("", "?situacao=encerrados", "?situacao=cancelados", "?situacao=todos", "?pagina=2")


def faixas(cliente, recortes=RECORTES + ("?busca=Processo", "?busca=nada-casa")):
    return {
        recorte: [
            (objeto.chave, objeto.ato)
            for objeto in abrir(cliente, recorte).context["faixa"].objetos
        ]
        for recorte in recortes
    }


@pytest.mark.django_db(transaction=True)
def test_o_recurso_de_processo_encerrado_aparece_na_faixa_em_toda_aba(
    gestor, api_client, manager_headers, process_payload
):
    from tests.fixtures.recursos_us4 import cenario_julgavel

    peca = cenario_julgavel(
        gestor, api_client, manager_headers, process_payload, seed=129, codigo="1290"
    )
    edital = peca["cenario"]["edital"]
    Edital.objects.filter(pk=edital.pk).update(status=Edital.Status.ENCERRADO)
    ProcessoSeletivo.objects.filter(pk=edital.processo_id).update(status=Status.ENCERRADO)
    muitos(25)
    marta = sessao("marta.julgadora", ["julgador"])

    padrao = abrir(marta)
    assert edital.processo.title not in mostrados(padrao)
    por_recorte = faixas(marta)
    esperado = [(("recursos", edital.id), "Decidir recursos (1)")]
    assert all(itens == esperado for itens in por_recorte.values()), por_recorte
    assert "Decidir recursos (1)" in padrao.content.decode()


def test_o_edital_em_elaboracao_da_pagina_dois_esta_na_faixa_da_pagina_um():
    muitos(20)
    escondido = processo(
        "Processo da página dois", editais=[("77", 2027, "EM_ELABORACAO")], ha_minutos=900
    )
    ana = sessao("ana.elaboradora", ["elaborador"])

    primeira = abrir(ana)
    assert escondido.title not in mostrados(primeira)
    assert escondido.title in mostrados(abrir(ana, "?pagina=2"))
    [objeto] = primeira.context["faixa"].objetos
    assert (objeto.ato, objeto.edital.processo_id) == ("Continuar a elaboração", escondido.id)


@pytest.mark.parametrize(
    "papeis",
    [["elaborador"], ["homologador", "publicador"], ["gestor"], ["elaborador", "julgador"]],
)
def test_a_faixa_e_identica_em_toda_aba_busca_e_pagina(papeis):
    muitos(22)
    processo("Encerrado em revisão", status=Status.ENCERRADO, editais=[("5", 2026, "EM_REVISAO")])
    processo(
        "Cancelado em elaboração", status=Status.CANCELADO, editais=[("6", 2026, "EM_ELABORACAO")]
    )
    processo("Cancelado final", status=Status.CANCELADO, editais=[("7", 2026, "CANCELADO")])
    cliente = sessao("dora.varios", papeis)

    por_recorte = faixas(cliente)

    assert len({tuple(itens) for itens in por_recorte.values()}) == 1, por_recorte


# ---------------------------------------------------------------------------------------------
# US3 — a busca em todas as situações
# ---------------------------------------------------------------------------------------------


def test_o_cancelado_e_achado_pelo_numero_a_partir_de_em_andamento():
    processo("Ativo qualquer", editais=[("90", 2025, "PUBLICADO")])
    processo("Seleção cancelada", status=Status.CANCELADO, editais=[("90", 2026, "CANCELADO")])
    gestora = sessao()

    resposta = abrir(gestora, "?busca=90%2F2026&situacao=andamento")
    html = resposta.content.decode()

    assert mostrados(resposta) == ["Seleção cancelada"]
    cartao = html.split("Seleção cancelada</a>")[1].split("</header>")[0]
    assert '<span class="situacao s-CANCELADO">Cancelado</span>' in cartao
    assert aba_atual(html) == []
    assert (
        "1 Processo encontrado para “90/2026”, em todas as situações, mostrando 1–1. "
        "1 está encerrado ou cancelado: a situação de cada um está ao lado do nome. "
        f'<a href="{LISTA}">Limpar a busca</a>'
    ) in html
    assert 'name="busca" value="90/2026"' in html
    # A frase vem antes dos resultados (UX-273).
    assert html.index('class="frase-do-recorte"') < html.index('<article class="processo">')

    assert set(mostrados(abrir(gestora, "?busca=90"))) == {"Ativo qualquer", "Seleção cancelada"}


def test_a_busca_vazia_a_partir_de_uma_aba_volta_a_ela_e_o_nul_nao_derruba():
    processo("Cancelado", status=Status.CANCELADO)
    gestora = sessao()

    html = corpo(gestora, "?situacao=cancelados")
    assert '<input type="hidden" name="situacao" value="cancelados">' in html
    assert aba_atual(corpo(gestora, "?situacao=cancelados&busca=++")) == ["Cancelados"]
    # O termo depois do NUL não pode ser letra solta: o código de `processo()` é "PS-LISTA-" mais
    # letras de um contador do worker, e um "x" casava com o "PS-LISTA-X" do próprio Processo
    # quando casos anteriores no mesmo worker tinham levado o contador até lá.
    assert "Nenhum Processo encontrado" in corpo(gestora, "?busca=%00inexistente")


def test_a_busca_sem_resultado_mantem_o_texto_e_oferece_limpar():
    processo("Qualquer")
    html = corpo(sessao(), "?busca=inexistente")

    assert "Nenhum Processo encontrado para “inexistente” em nenhuma situação." in html
    assert 'value="inexistente"' in html
    assert f'<a href="{LISTA}">Limpar a busca</a>' in html
    assert '<article class="processo">' not in html


def test_a_busca_pagina_e_os_links_preservam_o_termo():
    muitos(25)
    gestora = sessao()

    html = corpo(gestora, "?busca=Processo")
    assert "25 Processos encontrados para “Processo”" in html
    assert f'href="{LISTA}?busca=Processo&amp;pagina=2" rel="next"' in html
    assert "mostrando 21–25." in corpo(gestora, "?busca=Processo&pagina=2")


def test_a_busca_traz_o_processo_com_todos_os_editais():
    processo(
        "Tutoria",
        editais=[
            ("1", 2026, "PUBLICADO", "Tutor de Física"),
            ("2", 2026, "PUBLICADO", "Tutor de Artes"),
        ],
    )
    resposta = abrir(sessao(), "?busca=f%C3%ADsica")
    [achado] = resposta.context["processos"]
    assert [e.title for e in achado.editais_da_linha] == ["Tutor de Física", "Tutor de Artes"]


def test_todo_processo_e_achado_pelo_numero_de_qualquer_edital_de_qualquer_aba():
    """SC-1311: 100% dos casos, nas três situações."""
    cenario = [
        processo("Andamento", editais=[("11", 2026, "PUBLICADO"), ("12", 2026, "ENCERRADO")]),
        processo("Encerrado", status=Status.ENCERRADO, editais=[("21", 2025, "ENCERRADO")]),
        processo(
            "Cancelado",
            status=Status.CANCELADO,
            editais=[("31", 2024, "CANCELADO"), ("32", 2024, "CANCELADO")],
        ),
    ]
    gestora = sessao()
    for alvo in cenario:
        for edital in alvo.editais.all():
            for aba in ("andamento", "encerrados", "cancelados", "todos"):
                consulta = f"?busca={edital.number}%2F{edital.year}&situacao={aba}"
                assert mostrados(abrir(gestora, consulta)) == [alvo.title], consulta


# ---------------------------------------------------------------------------------------------
# US4 — a linha diz fatos, e não ações
# ---------------------------------------------------------------------------------------------


def test_a_linha_do_edital_omite_o_titulo_igual_e_nao_e_tabela():
    processo(
        "Professor substituto",
        editais=[("1", 2026, "PUBLICADO"), ("2", 2026, "PUBLICADO", "Edital 2/2026 — Libras")],
    )
    html = corpo(sessao())

    linhas = html.split('class="editais-do-processo"')[1].split("</ul>")[0]
    assert linhas.count('class="linha-do-edital"') == 2
    assert linhas.count('class="titulo-do-edital"') == 1
    assert "Edital 2/2026 — Libras" in linhas
    assert "<table" not in html and 'scope="col"' not in html
    assert 'aria-label="2 Editais neste Processo"' in html


def test_quem_gere_ve_comissao_e_alocacao_e_quem_nao_gere_nao_ve():
    alvo = processo("Com comissão", editais=[("1", 2026, "PUBLICADO")])
    comissao = reverse("interface:comissao", args=[alvo.id])
    alocacao = reverse("interface:alocacoes", args=[alvo.id])

    gestora = corpo(sessao())
    assert comissao in gestora and alocacao in gestora
    elaboradora = corpo(sessao("ana", ["elaborador"]))
    assert comissao not in elaboradora and alocacao not in elaboradora


# ---------------------------------------------------------------------------------------------
# US5 — a nota de cobertura antes dos itens
# ---------------------------------------------------------------------------------------------

FAMILIAS = (
    "Classificação",
    "sorteio",
    "resultado",
    "convocação",
    "documentos e formalização",
    "Requerimento de Matrícula",
    "avisos aos candidatos",
    "encerramento",
    "“O que fazer agora”, no detalhe de cada Edital",
)


def test_a_nota_vem_antes_do_primeiro_item_e_nomeia_as_familias():
    processo("Em elaboração", editais=[("1", 2026, "EM_ELABORACAO")])
    html = corpo(sessao("ana", ["elaborador"]))

    faixa = html[html.index('class="acoes-disponiveis"') : html.index("</section>")]
    assert faixa.index("</h2>") < faixa.index('class="cobertura-da-faixa"')
    assert faixa.index('class="cobertura-da-faixa"') < faixa.index('class="item-de-trabalho"')
    nota = faixa.split('class="cobertura-da-faixa">')[1].split("</p>")[0]
    assert nota.startswith(trabalho.COBERTURA)
    # Desde a `160`, a nota leva à página pessoal, sem número (FR-6880, FR-6881).
    assert 'class="para-minhas-atividades" href="/gestao/minhas-etapas"' in nota
    for familia in FAMILIAS:
        assert familia in nota, familia


def test_a_frase_vazia_nomeia_as_mesmas_familias_da_mesma_fonte():
    processo("Publicado", editais=[("1", 2026, "PUBLICADO")])
    html = corpo(sessao("ana", ["elaborador"]))

    vazia = html.split('class="sem-acoes">')[1].split("</p>")[0]
    assert vazia.startswith(
        "Nenhum ato de Edital ou de Retificação, recurso ou avaliação aguarda você agora."
    )
    assert trabalho.FORA_DA_FAIXA in vazia
    assert trabalho.FORA_DA_FAIXA in trabalho.COBERTURA
    assert 'class="para-minhas-atividades" href="/gestao/minhas-etapas"' in vazia


def test_a_nota_diz_onde_esta_cada_familia_e_nao_conta_atividades():
    """160, FR-6880 e FR-6881: o que é da presidência ou de alocação está em "Minhas atividades";
    o resultado continua no detalhe, porque publicar é papel da unidade (D-004 da `160`)."""
    assert "no detalhe de cada Edital" in trabalho.FORA_DA_FAIXA
    # As famílias continuam no detalhe; a página reúne só o que é da comissão da pessoa, e por isso
    # a frase não promete nela o resultado, que é papel da unidade.
    assert trabalho.FORA_DA_FAIXA.endswith("o que é da sua comissão está reunido em")
    # Só o que fica fora, numa frase (revisão de 12/11): o que a faixa reúne é dito antes, e a
    # enumeração não se repete na frase vazia.
    assert "." not in trabalho.FORA_DA_FAIXA
    assert "Edital e de Retificação" not in trabalho.FORA_DA_FAIXA
