"""A limpeza dos quatro achados da etapa 4 (090).

A marca "irreversível" descreve o ato também para quem não a vê, nos detalhes do Processo, do Edital
e da Retificação; a trilha das consultas da Etapa não oferece a quem só audita duas portas que o
recusam; o rodapé comum dos formulários quebra a linha entre os botões; e a prévia do aviso aberta
pelos Resultados divulgados volta a eles. O desenho em si é provado no navegador e pelo inventário
visual refeito (quickstart): aqui fica o que a marcação e a folha garantem.
"""

import html
import re

import pytest
from django.db import connection
from django.test.utils import CaptureQueriesContext
from django.urls import reverse

from processo_seletivo.avisos.domain import nomes
from processo_seletivo.processos.models import Edital
from processo_seletivo.publicacoes.models_retificacao import Retificacao, VersaoConsolidada
from tests.fixtures.divulgacao import montar_ato_publicavel, publicar_o_ato
from tests.fixtures.mesa import montar_cenario_da_presidencia
from tests.fixtures.publicacao import publish_original
from tests.interface.conftest import identificar
from tests.interface.folha import FOLHA_COMUM, sem_comentarios
from tests.interface.test_acoes import homologado
from tests.interface.test_retificar import LINHA_GERAL, VAGAS, campos
from tests.interface.test_telas_de_uso_diario import TEMPLATES, conteudo, trilha_unica_no_cabecalho

pytestmark = [pytest.mark.django_db, pytest.mark.integration]


@pytest.fixture(autouse=True)
def _seletor(seletor_ligado):
    """Sem o seletor de identidade, `/gestao/` devolve 503 antes de qualquer autorização."""


def abrir(client, url):
    resposta = client.get(url)
    assert resposta.status_code == 200, url
    return resposta.content.decode()


def links(trecho):
    return re.findall(r'<a href="([^"]+)">([^<]+)</a>', trecho)


# ---- a marca "irreversível" para quem não a vê ------------------------------------------------

#: Um link de ato e o que vem depois dele, até o fim do item da lista.
ITEM = re.compile(r"<li>\s*(?P<link><a [^>]*>(?P<rotulo>[^<]+)</a>)(?P<depois>.*?)</li>", re.S)


def atos_com_marca(pagina):
    """`{rótulo: descrição}` de cada link de ato, e a marca que o segue, se houver.

    A descrição é o texto do elemento que o `aria-describedby` do link aponta — o que o leitor de
    tela anuncia no foco —, ou `None`. Um `aria-describedby` que aponte para `id` inexistente
    reprova aqui, e não passa em branco.
    """
    atos = {}
    for item in ITEM.finditer(pagina):
        alvo = re.search(r'aria-describedby="([^"]+)"', item["link"])
        marcado = 'class="marca-irreversivel"' in item["depois"]
        descricao = None
        if alvo:
            achado = re.search(rf'id="{re.escape(alvo.group(1))}"[^>]*>([^<]*)<', pagina)
            assert achado, f"{item['rotulo']} aponta para {alvo.group(1)}, que não existe"
            descricao = achado.group(1)
        atos[item["rotulo"].strip()] = (marcado, descricao)
    return atos


def confere_a_marca(pagina, irreversiveis):
    """`FR-2060`: cada ato marcado é descrito pela marca; nenhum outro tem descrição."""
    atos = atos_com_marca(pagina)
    marcados = {rotulo for rotulo, (marcado, _) in atos.items() if marcado}
    assert marcados == set(irreversiveis), atos
    for rotulo, (marcado, descricao) in atos.items():
        assert descricao == ("irreversível" if marcado else None), (rotulo, descricao)


def cartao(corpo, titulo_id):
    return conteudo(corpo).split(f'id="{titulo_id}"')[1].split("</section>")[0]


@pytest.fixture
def publicado(api_client, manager_headers, process_payload):
    return publish_original(api_client, manager_headers, process_payload)


def test_no_processo_os_dois_atos_terminais_sao_anunciados_como_irreversiveis(client, publicado):
    """`FR-2060`, `FR-2061`, `SC-801`: "Encerrar Processo" e "Cancelar Processo", e só eles; o
    rótulo, o destino e o desenho não mudam."""
    identificar(client, "marcia.gestora", ["gestor"])
    processo = publicado.processo
    corpo = abrir(client, reverse("interface:processo-detalhe", args=[processo.id]))

    atos = cartao(corpo, "acoes-processo")
    confere_a_marca(atos, ["Encerrar Processo", "Cancelar Processo"])
    encerrar = reverse("interface:processo-ato", args=[processo.id, "encerrar"])
    assert (
        f'<a class="botao secundario" href="{encerrar}" '
        'aria-describedby="irreversivel-encerrar">Encerrar Processo</a>'
    ) in atos
    assert '<span class="marca-irreversivel" id="irreversivel-encerrar">irreversível</span>' in atos


def test_no_edital_publicado_os_atos_terminais_sao_anunciados_como_irreversiveis(client, publicado):
    """`FR-2060`, `SC-801`: "Encerrar" e "Cancelar" do Edital publicado; as ações que se desfazem,
    como as de navegação, não têm descrição."""
    identificar(client, "marcia.gestora", ["gestor"])
    corpo = abrir(client, reverse("interface:detalhe", args=[publicado.id]))

    confere_a_marca(cartao(corpo, "acoes-titulo"), ["Encerrar", "Cancelar"])


def test_no_edital_homologado_publicar_e_anunciado_como_irreversivel(
    client, api_client, manager_headers, process_payload
):
    """`FR-2060`, `SC-801`: "Publicar", o ato de maior consequência do Edital."""
    edital = homologado(api_client, manager_headers, process_payload)
    identificar(client, "paula.publicadora", ["publicador"])
    corpo = abrir(client, reverse("interface:detalhe", args=[edital.id]))

    confere_a_marca(cartao(corpo, "acoes-titulo"), ["Publicar"])


def test_no_edital_o_ato_indisponivel_continua_descrito_pelo_motivo(
    client, api_client, manager_headers, process_payload
):
    """`FR-2061`: o ato indisponível é um `span` desabilitado descrito pelo motivo, sem marca."""
    api_client.post("/api/v1/admin/processos", process_payload, format="json", **manager_headers)
    identificar(client, "ana.elaboradora", ["elaborador"])
    corpo = abrir(client, reverse("interface:detalhe", args=[Edital.objects.get().id]))
    acoes = cartao(corpo, "acoes-titulo")

    indisponivel = re.search(
        r'<span class="botao desabilitado" aria-disabled="true"\s+'
        r'aria-describedby="motivo-submeter">Submeter[^<]*</span>\s*'
        r'<span class="motivo" id="motivo-submeter">',
        acoes,
    )
    assert indisponivel, acoes
    assert "marca-irreversivel" not in acoes
    assert "irreversivel-" not in acoes


def test_na_retificacao_os_dois_atos_sem_volta_sao_anunciados(client, publicado):
    """`FR-2060`, `SC-801`: o mesmo desenho, e o mesmo defeito, no detalhe da Retificação
    (D-001) — "Cancelar Retificação" em elaboração e "Publicar Retificação" homologada."""
    vigente = VersaoConsolidada.objects.filter(edital=publicado).latest("materialized_at")
    identificar(client, "ana.elaboradora", ["elaborador"])
    client.post(
        reverse("interface:retificar", args=[publicado.id]),
        {
            **campos(vigente, **{VAGAS: "9", LINHA_GERAL: "9"}),
            "justificativa": "Ampliação",
            "confirmar": "1",
        },
    )
    retificacao = Retificacao.objects.get()
    identificar(client, "marcia.gestora", ["gestor"])
    corpo = abrir(client, reverse("interface:retificacao-detalhe", args=[retificacao.id]))

    confere_a_marca(cartao(corpo, "acoes-titulo"), ["Cancelar Retificação"])

    # Homologada, "Publicar Retificação" — o ato cheio da tela — tem a mesma descrição.
    def ato(acao, **extra):
        url = reverse("interface:retificacao-ato", args=[retificacao.id, acao])
        chave = client.get(url).context["chave_idempotencia"]
        assert client.post(url, {"chave_idempotencia": chave, **extra}).status_code == 302

    identificar(client, "ana.elaboradora", ["elaborador"])
    ato("submeter")
    identificar(client, "bruno.homologador", ["homologador"])
    ato("homologar", motivo="Conferido")
    identificar(client, "carla.publicadora", ["publicador"])
    corpo = abrir(client, reverse("interface:retificacao-detalhe", args=[retificacao.id]))

    confere_a_marca(cartao(corpo, "acoes-titulo"), ["Publicar Retificação"])


# ---- a trilha das consultas da Etapa ----------------------------------------------------------


@pytest.fixture
def cenario(gestor, api_client, manager_headers, raiz_de_arquivos):
    """O da `012`, declarado aqui e não importado de lá (081, `FR-1823`)."""
    return montar_cenario_da_presidencia(gestor, api_client, manager_headers)


CONSULTAS_DA_ETAPA = (
    "interface:resultados-da-etapa",
    "interface:trilha-da-avaliacao",
    "interface:conclusoes-preservadas",
)
#: Quem lê, e se gere a comissão do Processo do cenário. `maria` preside; `carlos` gere pela
#: permissão sistêmica, sem presidir; `ana.auditora` só audita.
LEITORES = {
    "presidencia": ("maria", [], True),
    "gestao": ("carlos", ["gestor"], True),
    "auditoria": ("ana.auditora", ["auditor"], False),
}


def os_dois_niveis(cenario):
    alocacao = reverse("interface:alocacoes", args=[cenario["processo"].id])
    distribuicao = reverse("interface:distribuicao", args=[cenario["edital"].id, cenario["etapa"]])
    return alocacao, distribuicao


@pytest.mark.parametrize("rota", CONSULTAS_DA_ETAPA)
@pytest.mark.parametrize("leitor", LEITORES)
def test_a_alocacao_e_a_etapa_sao_link_so_para_quem_as_abre(client, cenario, rota, leitor):
    """`FR-2062`, `SC-802`: os mesmos níveis, na mesma ordem e com os mesmos rótulos; link só para
    quem gere a comissão (D-002)."""
    quem, papeis, gere = LEITORES[leitor]
    identificar(client, quem, papeis)
    trilha = trilha_unica_no_cabecalho(
        abrir(client, reverse(rota, args=[cenario["edital"].id, cenario["etapa"]]))
    )
    alocacao, distribuicao = os_dois_niveis(cenario)

    rotulos = [rotulo for _, rotulo in links(trilha)]
    assert ("Alocação por Etapa" in rotulos) is gere, trilha
    assert (f'href="{alocacao}"' in trilha) is gere
    assert (f'href="{distribuicao}"' in trilha) is gere
    # O nível continua lá, como texto, para quem não o abre.
    texto = re.sub(r"<[^>]+>", "", trilha)
    niveis = [nivel.strip() for nivel in texto.split("›")]
    assert niveis[2] == cenario["processo"].institutional_code
    assert niveis[3] == "Alocação por Etapa"
    assert niveis[4]
    assert len(niveis) == 6


@pytest.mark.parametrize("rota", CONSULTAS_DA_ETAPA)
def test_quem_audita_le_os_mesmos_niveis_de_quem_preside(client, cenario, rota):
    """`FR-2062`: o texto da trilha é o mesmo para os dois — nada aparece nem some —, e só os dois
    níveis que quem audita não abre deixam de ser link."""
    url = reverse(rota, args=[cenario["edital"].id, cenario["etapa"]])
    identificar(client, "maria", [])
    da_presidencia = trilha_unica_no_cabecalho(abrir(client, url))
    identificar(client, "ana.auditora", ["auditor"])
    da_auditoria = trilha_unica_no_cabecalho(abrir(client, url))

    def texto(trilha):
        return re.sub(r"<[^>]+>", "", trilha)

    assert texto(da_auditoria) == texto(da_presidencia)
    so_da_presidencia = set(links(da_presidencia)) - set(links(da_auditoria))
    assert {destino for destino, _ in so_da_presidencia} == set(os_dois_niveis(cenario))
    assert set(links(da_auditoria)) < set(links(da_presidencia))


@pytest.mark.parametrize("rota", CONSULTAS_DA_ETAPA)
@pytest.mark.parametrize("leitor", LEITORES)
def test_nenhum_link_da_trilha_recusa_quem_a_le(client, cenario, rota, leitor):
    """`FR-2063`, `SC-802`: cada link da trilha, seguido pela mesma pessoa, abre."""
    quem, papeis, _ = LEITORES[leitor]
    identificar(client, quem, papeis)
    trilha = trilha_unica_no_cabecalho(
        abrir(client, reverse(rota, args=[cenario["edital"].id, cenario["etapa"]]))
    )

    destinos = [destino for destino, _ in links(trilha)]
    assert destinos
    for destino in destinos:
        assert client.get(destino).status_code == 200, (leitor, destino)


#: Consultas de cada tela, para quem preside e para quem só audita, medidas em 18/10/2026 sobre a
#: `main` em `21e36bd4`, antes desta feature. A trilha nova não pode custar nenhuma (`FR-2064`).
CONSULTAS_ANTES = {
    ("interface:resultados-da-etapa", "presidencia"): 7,
    ("interface:resultados-da-etapa", "auditoria"): 7,
    ("interface:trilha-da-avaliacao", "presidencia"): 13,
    ("interface:trilha-da-avaliacao", "auditoria"): 13,
    ("interface:conclusoes-preservadas", "presidencia"): 7,
    ("interface:conclusoes-preservadas", "auditoria"): 7,
}


@pytest.mark.parametrize("rota", CONSULTAS_DA_ETAPA)
@pytest.mark.parametrize("leitor", ["presidencia", "auditoria"])
def test_a_trilha_nova_nao_custa_consulta(client, cenario, rota, leitor):
    """`FR-2064`: a porta já pergunta se quem lê gere a comissão; a trilha usa a resposta. As
    Conclusões custam uma a menos: a reabertura fazia a mesma pergunta de novo (R-002)."""
    quem, papeis, _ = LEITORES[leitor]
    identificar(client, quem, papeis)
    url = reverse(rota, args=[cenario["edital"].id, cenario["etapa"]])
    client.get(url)  # aquece o que a sessão guarda na primeira leitura
    with CaptureQueriesContext(connection) as consultas:
        assert client.get(url).status_code == 200
    # Igual ao de antes, e não "no máximo": uma consulta a menos fora das Conclusões seria sinal de
    # que a porta deixou de perguntar alguma coisa. Uma mudança futura nestas views que mude a conta
    # muda esta tabela, com a medição nova.
    menos = 1 if rota == "interface:conclusoes-preservadas" else 0
    assert len(consultas) == CONSULTAS_ANTES[(rota, leitor)] - menos


# ---- o rodapé dos formulários -----------------------------------------------------------------


def test_o_rodape_comum_quebra_a_linha_entre_os_botoes():
    """`FR-2065`: a regra comum do rodapé é uma linha flexível que quebra; sem a quebra, a 375 px
    os botões encolhem e o rótulo vai a duas linhas (achado do code review da `086`)."""
    folha = sem_comentarios(FOLHA_COMUM, " ")
    # O seletor sozinho, e não `.filtro .salvar`, que é a variante dentro do filtro.
    regra = re.search(r"(?:^|\})\s*\.salvar\s*\{([^}]*)\}", folha)
    assert regra, "o rodapé comum perdeu a regra própria"
    assert re.search(r"display\s*:\s*flex", regra.group(1))
    assert re.search(r"flex-wrap\s*:\s*wrap", regra.group(1))


# ---- a prévia aberta pelos Resultados divulgados ----------------------------------------------


@pytest.fixture
def divulgado(gestor, api_client, manager_headers, process_payload):
    cenario = montar_ato_publicavel(
        gestor, api_client, manager_headers, process_payload, pontuacoes=("90.0000", "70.0000")
    )
    cenario["publicacao"] = publicar_o_ato(cenario)
    return cenario


def url_da_previa(cenario, **parametros):
    edital, marco = cenario["edital"], cenario["publicacao"].marco_id
    consulta = "&".join(f"{chave}={valor}" for chave, valor in parametros.items())
    url = reverse("interface:aviso-do-resultado", args=[edital.id, marco])
    return url + (f"?{consulta}" if consulta else "")


def publicacoes(cenario):
    return reverse(
        "interface:publicacoes-do-marco",
        args=[cenario["edital"].id, cenario["publicacao"].marco_id],
    )


def avisos(cenario):
    return reverse("interface:avisos-do-edital", args=[cenario["edital"].id])


def cancelar(corpo):
    return re.search(r'<a class="botao secundario" href="([^"]+)">Cancelar</a>', corpo).group(1)


def test_os_resultados_divulgados_abrem_a_previa_pela_porta_deles(client, divulgado):
    """`FR-2067`: o link "Avisar candidatos" diz a porta no endereço (D-004)."""
    identificar(client, "paula.publicadora", ["publicador"])
    corpo = conteudo(abrir(client, publicacoes(divulgado)))

    previa = html.unescape(
        re.search(r'<a class="botao" href="([^"]+)">Avisar candidatos', corpo).group(1)
    )
    assert previa.startswith(url_da_previa(divulgado) + "?")
    assert "de=marco" in previa.split("?")[1].split("&")


@pytest.mark.parametrize(
    ("papeis", "classificacao_e_link"),
    [(["publicador"], False), (["publicador", "auditor"], True)],
)
def test_a_previa_pelos_resultados_divulgados_volta_a_eles(
    client, divulgado, papeis, classificacao_e_link
):
    """`FR-2067`, `SC-804`: a trilha dos Resultados divulgados e a própria tela; "Cancelar" leva a
    eles. A Classificação é link só para quem a abre, como lá."""
    identificar(client, "paula.publicadora", papeis)
    corpo = abrir(client, url_da_previa(divulgado, natureza=nomes.PRELIMINAR, de="marco"))

    trilha = trilha_unica_no_cabecalho(corpo)
    edital = divulgado["edital"]
    classificacao = reverse(
        "interface:ordenacao", args=[edital.id, divulgado["publicacao"].marco_id]
    )
    assert links(trilha)[-1] == (publicacoes(divulgado), "Resultados divulgados")
    assert (f'<a href="{classificacao}">Classificação</a>' in trilha) is classificacao_e_link
    assert "Classificação ›" in re.sub(r"<[^>]+>", "", trilha)
    assert "Avisos aos candidatos" not in trilha
    assert trilha.rstrip().endswith('<span aria-current="page">Avisar candidatos</span>')
    assert cancelar(corpo) == publicacoes(divulgado)


def test_pelos_avisos_a_previa_continua_como_antes(client, divulgado):
    """`FR-2069`: sem a porta, a trilha e "Cancelar" são os dos Avisos aos candidatos."""
    identificar(client, "paula.publicadora", ["publicador"])
    corpo = abrir(client, url_da_previa(divulgado, natureza=nomes.PRELIMINAR))

    trilha = trilha_unica_no_cabecalho(corpo)
    assert links(trilha)[-1] == (avisos(divulgado), "Avisos aos candidatos")
    assert "Resultados divulgados" not in trilha
    assert cancelar(corpo) == avisos(divulgado)


@pytest.mark.parametrize(
    ("quem", "papeis", "porta"),
    [
        # Quem gere avisa, e não abre os Resultados divulgados: sem `resultado:publicar` nem
        # `auditoria:consultar`, a porta escrita à mão não lhe oferece tela fechada.
        ("marcia.gestora", ["gestor"], "marco"),
        ("paula.publicadora", ["publicador"], "qualquer"),
    ],
)
def test_porta_desconhecida_ou_fechada_da_a_trilha_dos_avisos(
    client, divulgado, quem, papeis, porta
):
    """`FR-2068`: a porta é ignorada quando não existe ou quando quem lê não a abre."""
    identificar(client, quem, papeis)
    corpo = abrir(client, url_da_previa(divulgado, natureza=nomes.PRELIMINAR, de=porta))

    trilha = trilha_unica_no_cabecalho(corpo)
    assert links(trilha)[-1] == (avisos(divulgado), "Avisos aos candidatos")
    assert cancelar(corpo) == avisos(divulgado)


def test_a_porta_sobrevive_aos_dois_formularios_da_previa(client, divulgado):
    """`FR-2068`: "Usar este modelo" (GET) e o envio (POST) repetem a porta; recusado o envio, a
    prévia volta com a mesma trilha."""
    identificar(client, "paula.publicadora", ["publicador"])
    corpo = abrir(client, url_da_previa(divulgado, natureza=nomes.PRELIMINAR, de="marco"))
    envio = re.search(r'<form method="post" action="[^"]*">.*?</form>', conteudo(corpo), re.S)
    assert '<input type="hidden" name="de" value="marco">' in envio.group(0)
    # O de "Usar este modelo" só aparece com modelo ativo na unidade; no modelo, os dois formulários
    # da prévia repetem a porta, como repetem a natureza.
    modelo = (TEMPLATES / "aviso_previa.html").read_text()
    formularios = re.findall(r"<form method=\"(?:get|post)\".*?</form>", modelo, re.S)
    assert len(formularios) == 2
    for formulario in formularios:
        assert (
            '{% if de %}<input type="hidden" name="de" value="{{ de }}">{% endif %}' in formulario
        )

    recusada = client.post(
        url_da_previa(divulgado),
        {
            "acao": "confirmar",
            "de": "marco",
            "natureza": nomes.PRELIMINAR,
            "assinatura": "assinatura-vencida",
            "chave": "previa-recusada-090",
            "assunto": "Processo Seletivo Ifes — Nova publicação disponível",
            "corpo": "Olá, {nome_do_candidato}. Saiu o resultado: {area_do_candidato}",
        },
    )
    assert recusada.status_code >= 400
    trilha = trilha_unica_no_cabecalho(recusada.content.decode())
    assert links(trilha)[-1] == (publicacoes(divulgado), "Resultados divulgados")


def test_a_porta_nao_muda_o_aviso(client, divulgado):
    """`FR-2069`: pelas duas portas, o mesmo universo e o mesmo texto; confirmado, o histórico."""
    from processo_seletivo.avisos.models import Aviso

    identificar(client, "paula.publicadora", ["publicador"])
    pelos_avisos = abrir(client, url_da_previa(divulgado, natureza=nomes.PRELIMINAR))
    pelo_marco = abrir(client, url_da_previa(divulgado, natureza=nomes.PRELIMINAR, de="marco"))

    def miolo(corpo):
        """A prévia sem o que muda a cada leitura (o token e a chave) e sem a porta."""
        pagina = conteudo(corpo)
        pagina = re.sub(r'name="(?:csrfmiddlewaretoken|chave)" value="[^"]*"', "", pagina)
        pagina = pagina.replace('<input type="hidden" name="de" value="marco">', "")
        return pagina.split('<p class="imutavel">')[1].split('<a class="botao secundario" href=')[0]

    assert miolo(pelo_marco) == miolo(pelos_avisos)

    assinatura = re.search(r'name="assinatura" value="([^"]+)"', pelo_marco).group(1)
    resposta = client.post(
        url_da_previa(divulgado),
        {
            "acao": "confirmar",
            "de": "marco",
            "natureza": nomes.PRELIMINAR,
            "assinatura": assinatura,
            "chave": "previa-confirmada-090",
            "assunto": "Processo Seletivo Ifes — Nova publicação disponível",
            "corpo": "Olá, {nome_do_candidato}. Saiu o resultado: {area_do_candidato}",
        },
    )
    aviso = Aviso.objects.get()
    assert resposta.status_code == 302
    assert resposta["Location"] == reverse("interface:aviso", args=[aviso.id])


#: Consultas da prévia pelos Avisos, medidas em 18/10/2026 sobre a `main` em `21e36bd4`, antes desta
#: feature — quando `de=marco` ainda não significava nada, e as duas portas custavam o mesmo.
CONSULTAS_DA_PREVIA_ANTES = {"publicador": 10, "publicador+auditor": 10}


@pytest.mark.parametrize(
    ("papeis", "a_mais"),
    [
        # Sem auditoria, a Classificação pergunta à presidência: uma consulta, só nesta porta.
        (["publicador"], 1),
        # Com auditoria, a resposta sai da identidade, em memória, antes da presidência.
        (["publicador", "auditor"], 0),
    ],
)
def test_a_porta_custa_no_maximo_uma_consulta_e_so_pelo_marco(client, divulgado, papeis, a_mais):
    """`FR-2069`, R-004: pelos Avisos, nada a mais; pelos Resultados divulgados, só a pergunta da
    Classificação, a mesma que eles fazem — e nenhuma para quem audita."""
    identificar(client, "paula.publicadora", papeis)

    def contar(url):
        client.get(url)
        with CaptureQueriesContext(connection) as consultas:
            assert client.get(url).status_code == 200
        return len(consultas)

    pelos_avisos = contar(url_da_previa(divulgado, natureza=nomes.PRELIMINAR))
    pelo_marco = contar(url_da_previa(divulgado, natureza=nomes.PRELIMINAR, de="marco"))
    antes = CONSULTAS_DA_PREVIA_ANTES["+".join(papeis)]
    assert pelos_avisos == antes
    assert pelo_marco == antes + a_mais
