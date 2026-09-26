"""A página da supervisão: o que ela apresenta, o que ela recusa apresentar, e para onde encaminha.

Os testes de derivação vivem em `tests/integration/supervisao/`; aqui ficam os que só existem no
canal — a região anunciada, o equivalente textual da série, e as proibições de apresentação.
"""

import re

import pytest
from django.urls import reverse

from tests.fixtures.edital import identificador
from tests.fixtures.supervisao import SEGUNDO_SEED, rascunhar, submeter
from tests.interface.conftest import identificar

pytestmark = [pytest.mark.django_db, pytest.mark.integration]


def url(processo):
    return reverse("interface:supervisao", args=[processo.id])


def abrir(client, processo, subject="maria", papeis=()):
    identificar(client, subject, list(papeis))
    resposta = client.get(url(processo))
    assert resposta.status_code == 200, resposta.content
    return resposta.content.decode()


def regiao(corpo, ancora):
    """O trecho de uma das duas regiões, delimitado pelo `<section>` que a anuncia.

    Procurar no documento inteiro faria uma asserção sobre o Pulso passar ou falhar por causa de
    algo escrito na Atenção — e as duas regiões existem justamente porque são coisas diferentes.

    O fechamento é contado, e não procurado: a região do Pulso tem um bloco por Edital, e um
    recorte que parasse no primeiro `</section>` devolveria o cabeçalho e mais nada — passando
    silenciosamente em toda asserção de ausência.
    """
    abertura = re.search(rf'<section[^>]*aria-labelledby="{ancora}"[^>]*>', corpo)
    assert abertura is not None, f"a região {ancora} não foi anunciada como região"
    profundidade, posicao = 0, abertura.start()
    for marca in re.finditer(r"<section\b|</section>", corpo[abertura.start() :]):
        profundidade += 1 if marca.group(0) != "</section>" else -1
        if profundidade == 0:
            return corpo[posicao : posicao + marca.end()]
    raise AssertionError(f"a região {ancora} não foi fechada")


def texto(trecho):
    """O que a região **apresenta**, sem marcação.

    A asserção de "nenhum percentual" precisa disto: a altura de uma barra é `style="height:40%"`,
    e um `%` dentro de atributo é unidade de desenho, não informação. Procurar no HTML cru faria o
    teste falhar por causa da folha de estilo e passar quando o número aparecesse escrito.
    """
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", trecho))


def sem_espacos(trecho):
    """O trecho sem espaço em branco algum — para comparar marcação sem depender de indentação."""
    return re.sub(r"\s+", "", trecho)


def test_as_duas_regioes_sao_anunciadas_com_titulo_proprio(
    client, seletor_ligado, processo_a, edital_a, edital_c, comissao_de_a
):
    """`UX-006`: quem navega por marcos salta de uma para a outra sem varrer a página."""
    corpo = abrir(client, processo_a)

    assert 'id="pulso-titulo"' in corpo
    assert 'id="atencao-titulo"' in corpo


def test_nenhum_percentual_e_apresentado_sobre_inscricao(
    client, seletor_ligado, processo_a, edital_a, edital_c, comissao_de_a
):
    """`FR-017` e `SC-005`: não há denominador normativo para inscrição.

    Um percentual de avanço aqui responderia "quanto falta" a uma pergunta que ninguém pode
    responder — não existe o número de inscrições que o Edital espera receber.
    """
    submeter(edital_a, 7)
    rascunhar(edital_a, 2)
    # Com submissões no Edital que tem período, a série é desenhada — e é justamente aí que um `%`
    # aparece na marcação, como altura de barra. O que a região não pode é **apresentar** um.
    submeter(edital_c, 3, seed=2)

    corpo = abrir(client, processo_a)

    pulso = regiao(corpo, "pulso-titulo")
    assert "barra" in pulso, "sem série desenhada o teste não exercita o caso que ele protege"
    assert "%" not in texto(pulso)


def test_o_pulso_nomeia_o_edital_de_cada_contagem(
    client, seletor_ligado, processo_a, edital_a, edital_c, comissao_de_a
):
    """`FR-011`, `FR-020` e `UX-007`: nenhuma linha do Edital aparece sem dizer de qual Edital é."""
    submeter(edital_a, 3)
    submeter(edital_c, 1, seed=2)

    pulso = regiao(abrir(client, processo_a), "pulso-titulo")

    assert f"{edital_a.number}/{edital_a.year}" in pulso
    assert f"{edital_c.number}/{edital_c.year}" in pulso


def test_o_rascunho_usa_o_termo_que_a_tela_de_inscricoes_ja_usa(
    client, seletor_ligado, processo_a, edital_a, edital_c, comissao_de_a
):
    """`Princípio I`: dois termos para o mesmo conceito é o que a linguagem ubíqua recusa.

    A tela da `009` chama o rascunho de **em preenchimento**. Enquanto não houver decisão de
    vocabulário que valha para as duas telas, a supervisão adota o termo vigente — e não inventa
    um segundo.
    """
    rascunhar(edital_a, 2)

    pulso = regiao(abrir(client, processo_a), "pulso-titulo")

    assert "preenchimento" in pulso.lower()


def test_a_serie_tem_equivalente_textual_com_os_mesmos_valores(
    client, seletor_ligado, processo_a, edital_a, edital_c, comissao_de_a
):
    """`FR-016`, `UX-008` e `SC-015`: o gráfico é desenho; os números vivem na tabela.

    A asserção compara **os mesmos valores** que a derivação produziu, e não uma amostra: um
    equivalente que perdesse um dia seria pior do que nenhum, porque pareceria completo.
    """
    from datetime import timedelta

    from django.utils import timezone

    from processo_seletivo.interface import supervisao as leitura

    agora = timezone.now()
    submeter(edital_c, 2, quando=agora - timedelta(days=2), seed=2)
    submeter(edital_c, 5, primeiro=40, quando=agora - timedelta(days=1), seed=2)

    corpo = abrir(client, processo_a)

    serie = next(
        item.serie for item in leitura.pulso(processo_a).por_edital if item.edital.id == edital_c.id
    )
    assert serie, "o Edital com período declarado precisa ter série"
    pulso = sem_espacos(regiao(corpo, "pulso-titulo"))
    for ponto in serie:
        linha = sem_espacos(
            f'<tr><th scope="row">{ponto.dia.strftime("%d/%m/%Y")}</th>'
            f"<td>{ponto.quantidade}</td></tr>"
        )
        assert linha in pulso, f"o dia {ponto.dia} não aparece no equivalente textual"


def test_as_barras_da_serie_nao_sao_lidas_como_conteudo(
    client, seletor_ligado, processo_a, edital_a, edital_c, comissao_de_a
):
    """`UX-008`: o desenho não pode ser anunciado duas vezes a quem ouve a tela."""
    submeter(edital_c, 1, seed=2)

    pulso = regiao(abrir(client, processo_a), "pulso-titulo")

    assert '<ul class="barras" aria-hidden="true">' in pulso


def test_a_ausencia_de_periodo_em_curso_e_declarada(
    client, seletor_ligado, processo_a, edital_a, comissao_de_a
):
    """`FR-018`: dito, e não deixado como um zero sem qualificação."""
    pulso = regiao(abrir(client, processo_a), "pulso-titulo")

    assert "Nenhum Edital com período de inscrições em curso" in texto(pulso)
    assert "últimas 24 horas" not in texto(pulso)


@pytest.fixture
def processo_limpo(gestor, api_client, manager_headers):
    """Um Processo em que nenhuma condição de atenção se verifica.

    Ele é montado do zero, e não obtido apagando o que sobra de outro: **nada é excluído** neste
    sistema, e um teste que apagasse um Edital estaria provando o contrário do que a Constituição
    garante.
    """
    from tests.fixtures.comissao import constituir
    from tests.fixtures.publicacao import publish_original
    from tests.fixtures.supervisao import etapa_ligada, rascunho_com_periodo

    edital = publish_original(
        api_client,
        {**manager_headers, "HTTP_IDEMPOTENCY_KEY": "supervisao-limpo-0001"},
        {
            "institutionalCode": "PS-2026-090",
            "title": "Processo sem condição de atenção",
            "firstEdital": {"number": "90", "year": 2026, "title": "Edital limpo"},
        },
        draft=rascunho_com_periodo(9, etapas=[etapa_ligada(9)]),
    )
    constituir(gestor, edital.processo, [("maria", "PRESIDENTE")], prefixo="limpo")
    return edital.processo


def test_sem_nenhuma_condicao_a_atencao_ocupa_uma_linha(client, seletor_ligado, processo_limpo):
    """`FR-025` e `SC-011`: a região encolhe a uma linha, e não some.

    Sumir não distinguiria *nada a sinalizar* de *a página não carregou*. E não há seção por sinal:
    cinco cabeçalhos vazios diriam cinco vezes que não há nada.
    """
    atencao = regiao(abrir(client, processo_limpo), "atencao-titulo")

    assert "Nenhuma condição de atenção" in texto(atencao)
    assert "<li" not in atencao


@pytest.mark.django_db(transaction=True)
def test_a_mensagem_de_recurso_sem_membro_desimpedido_nao_afirma_impossibilidade(
    client, seletor_ligado, gestor, api_client, manager_headers, process_payload
):
    """`UX-005` e `FR-030a`: a mensagem se limita ao impedimento verificável.

    A titularidade da permissão de julgar não é determinável pelo sistema — os papéis vêm da sessão
    e nada liga identidade a papel —, e alguém de fora da comissão pode detê-la. Dizer que o
    julgamento é impossível seria afirmar o que os dados não sustentam.
    """
    from django.utils import timezone

    from processo_seletivo.avaliacoes.models import Impedimento
    from tests.fixtures.recursos_us4 import cenario_julgavel

    peca = cenario_julgavel(
        gestor, api_client, manager_headers, process_payload, seed=131, codigo="0311"
    )
    Impedimento.objects.create(
        identity_subject="maria",
        inscricao=peca["inscricao"],
        motivo="Parentesco declarado.",
        criado_em=timezone.now(),
        criado_por="carlos",
    )

    atencao = texto(
        regiao(
            abrir(client, peca["cenario"]["processo"], papeis=["julgador"]),
            "atencao-titulo",
        )
    )

    assert "todos os membros da comissão estão impedidos" in atencao
    for proibido in ("impossível", "impossivel", "ninguém pode julgar", "não há quem julgue"):
        assert proibido not in atencao.lower()


def test_os_sinais_do_edital_conduzem_as_telas_donas(
    client, seletor_ligado, processo_a, edital_a, edital_c, comissao_de_a
):
    """`FR-035`: cada sinal leva à feature dona, já no ponto em que a situação se resolve.

    Sem o encaminhamento a supervisão vira aviso sem remédio — e é dali que nasce a pressão para
    replicar a lista dentro dela, que é o que `D-009` recusa.
    """
    from tests.fixtures.supervisao import ETAPA_C1, SEGUNDO_SEED

    submeter(edital_c, 2, seed=SEGUNDO_SEED)

    atencao = regiao(abrir(client, processo_a, papeis=["elaborador"]), "atencao-titulo")

    # **Nenhum sinal de Cronograma, nem para quem pode retificar** (045, `FR-738`, `FR-739`). Os
    # dois que levavam à Retificação — a Etapa sem marco e o estado declarado — saíram: o
    # primeiro é aviso de composição, o segundo não tem mais o que comparar.
    assert reverse("interface:retificar", args=[edital_a.id]) not in atencao
    assert reverse("interface:compor-etapa", args=[edital_a.id, "etapas"]) not in atencao
    assert (
        reverse("interface:distribuicao", args=[edital_c.id, identificador(ETAPA_C1, SEGUNDO_SEED)])
        in atencao
    )


@pytest.mark.django_db(transaction=True)
def test_os_sinais_do_marco_e_do_recurso_conduzem_as_telas_donas(
    client, seletor_ligado, gestor, api_client, manager_headers, process_payload
):
    """A outra metade de `FR-035`: a ordenação do marco e os recursos do Edital."""
    from decimal import Decimal

    from django.utils import timezone

    from processo_seletivo.avaliacoes.models import Impedimento
    from processo_seletivo.recursos.application.julgar import julgar
    from processo_seletivo.recursos.models import DecisaoRecurso
    from processo_seletivo.resultados.models import ResultadoEtapa
    from tests.fixtures.recursos import admitir, interpor
    from tests.fixtures.recursos_us4 import cenario_julgavel, julgador

    peca = cenario_julgavel(
        gestor, api_client, manager_headers, process_payload, seed=141, codigo="0411"
    )
    cenario = peca["cenario"]
    # A segunda peça fica **pendente**, e é ela que produz `UX-005`: a primeira vai ser julgada
    # logo abaixo, e recurso julgado não aguarda julgamento nenhum.
    outra = cenario["inscricoes"][1]
    pendente = interpor(
        inscricao=outra,
        versao=peca["recurso"].versao,
        resultado=ResultadoEtapa.vigentes.get(inscricao=outra, etapa_id=cenario["etapa"]),
        protocolo="REC-2026-PENDENTE1",
    )
    admitir(pendente)
    # João concluiu a Avaliação que fundamentou o Resultado atacado; Maria recebe o impedimento
    # declarado. Com os dois membros ativos impedidos, o conjunto de desimpedidos é vazio.
    Impedimento.objects.create(
        identity_subject="maria",
        inscricao=outra,
        motivo="Parentesco declarado.",
        criado_em=timezone.now(),
        criado_por="carlos",
    )
    julgar(
        actor=julgador(),
        recurso_id=peca["recurso"].id,
        especie=DecisaoRecurso.Especie.CORRECAO_FIXADA,
        motivacao="A prova didática entregue não foi considerada.",
        etapa_id=cenario["etapa"],
        pontuacao=Decimal("82.0000"),
        assinatura_do_resultado=str(peca["superado"].id),
        idempotency_key="deferir-destinos",
    )

    atencao = regiao(abrir(client, cenario["processo"], papeis=["julgador"]), "atencao-titulo")

    assert reverse("interface:ordenacao", args=[cenario["edital"].id, cenario["marco"]]) in atencao
    assert reverse("interface:recursos", args=[cenario["edital"].id]) in atencao


def test_a_supervisao_nao_lista_os_registros_que_conta(
    client, seletor_ligado, processo_a, edital_a, edital_c, comissao_de_a
):
    """`FR-037` e `D-009`: o que a supervisão conta, a dona lista. Nunca as duas.

    E é também `FR-004a`: a página é agregada por construção, e nenhuma identificação de candidato
    aparece nela — nem nome, nem CPF, nem protocolo.
    """
    from tests.fixtures.supervisao import SEGUNDO_SEED

    inscricoes = submeter(edital_c, 3, seed=SEGUNDO_SEED)

    corpo = abrir(client, processo_a)

    for inscricao in inscricoes:
        assert inscricao.protocolo not in corpo
        assert inscricao.nome not in corpo
        assert inscricao.cpf not in corpo
        assert str(inscricao.id) not in corpo


# O encaminhamento do conteúdo publicado à Retificação — e a supressão do caminho a quem não a
# pratica ou onde ela não é possível — era provado aqui sobre o `UX-001`. Ele saiu do catálogo
# (045), e a mesma prova vive sobre o `UX-046`, a única espécie que ainda leva à Retificação:
# `tests/integration/supervisao/test_sinal_do_acervo_sem_quadro.py`.


# ---------------------------------------------------------------------------
# A página do Processo passa a conduzir (038, US1)
#
# **A prova que importa é a da igualdade.** O pulso e a Atenção não são recalculados aqui: são as
# mesmas duas funções, lidas de uma segunda tela. Um teste que só conferisse "aparece" passaria
# igualmente sobre uma segunda derivação — que é exatamente o que a `FR-557` proíbe.
# ---------------------------------------------------------------------------


def url_do_processo(processo):
    return reverse("interface:processo-detalhe", args=[processo.id])


def abrir_o_processo(client, processo, subject="maria", papeis=()):
    identificar(client, subject, list(papeis))
    resposta = client.get(url_do_processo(processo))
    assert resposta.status_code == 200, resposta.content
    return resposta.content.decode()


def test_a_pagina_do_processo_apresenta_o_pulso_e_a_atencao(
    client, seletor_ligado, processo_a, edital_a, edital_c, comissao_de_a
):
    """`FR-556`: o guia não desliga quando o Edital é publicado.

    Antes desta feature a página listava Editais e oferecia encerrar ou cancelar — dois atos
    terminais — e nada dizia sobre o certame em curso.
    """
    submeter(edital_c, 3, seed=SEGUNDO_SEED)

    conducao = regiao(abrir_o_processo(client, processo_a), "conducao-titulo")

    lido = texto(conducao)
    assert "3" in lido
    assert f"Edital {edital_c.number}/{edital_c.year}" in lido
    # A Atenção veio junto, e não só o pulso.
    assert "Atenção" in lido


def test_o_processo_e_a_supervisao_dizem_a_mesma_coisa_do_mesmo_edital(
    client, seletor_ligado, processo_a, edital_a, edital_c, comissao_de_a
):
    """`FR-557` e `SC-197`: **zero divergências** — e elas não podem existir, por construção.

    As duas telas chamam `pulso` e `sinais`; não há segundo cálculo a divergir. Este teste é o que
    tornaria vermelha a tentação de recalcular aqui "para não depender da Supervisão".

    **A comparação é frase a frase, e não por um número solto.** Uma asserção de que o dígito `4`
    aparece nas duas telas passaria com o Pulso pela metade — e passou, até a revisão da `038`
    apontar que a série e os próximos marcos não estavam sendo apresentados.
    """
    submeter(edital_c, 4, seed=SEGUNDO_SEED)

    do_processo = texto(regiao(abrir_o_processo(client, processo_a), "conducao-titulo"))
    do_painel = abrir(client, processo_a)
    pulso_da_supervisao = texto(regiao(do_painel, "pulso-titulo"))
    atencao_da_supervisao = texto(regiao(do_painel, "atencao-titulo"))

    # **O que aconteceu**: a soma do Processo, dita com as mesmas palavras.
    assert "4 inscrições recebidas no Processo" in do_processo
    assert "4 inscrições recebidas no Processo" in pulso_da_supervisao

    # **O que vem**: cada marco que a Supervisão anuncia é anunciado aqui também. O marco se conta
    # pela data depois do travessão — desde a `045` ele não carrega mais *"declarado …"*.
    marcos = re.findall(r"— \d{2}/\d{2}/\d{4}", pulso_da_supervisao)
    assert marcos, "sem marco na Supervisão, este teste não provaria a igualdade"
    assert len(re.findall(r"— \d{2}/\d{2}/\d{4}", do_processo)) == len(marcos)

    # A série tem o mesmo equivalente textual nas duas — é o mesmo parcial, lido do mesmo Pulso.
    for valores in re.findall(r"Valores da série — \d+ dias?", pulso_da_supervisao):
        assert valores in do_processo, f"a Supervisão mostra {valores!r} e o Processo não"

    # **O que pede ação**: as mesmas frases, e não paráfrases.
    for mensagem in re.findall(r"A Etapa [^.]+\.", atencao_da_supervisao):
        assert mensagem in do_processo, f"a Supervisão diz {mensagem!r} e o Processo não"


def test_quem_alcanca_o_processo_le_o_estado_e_nao_recebe_caminho(
    client, seletor_ligado, processo_a, edital_a, edital_c, comissao_de_a
):
    """`FR-556` e o caso-limite da spec: *"lê o estado e não recebe caminho algum"*.

    **Esta era a leitura errada da primeira implementação**, e a revisão a pegou: a região inteira
    pendia de `pode_supervisionar`, de modo que quem alcançava o Processo e não a Supervisão não
    lia estado nenhum — o oposto do que o requisito manda.

    O Pulso é agregado: não carrega destino nem dado pessoal, e esta página já diz que o Processo
    existe e quais são os Editais dele. O que carrega destino é o **sinal**, e é ele que `alcance`
    suprime espécie a espécie (`FR-004`). Quem não alcança espécie nenhuma não recebe a região da
    Atenção — dizer-lhe *"nenhuma condição"* afirmaria que não há nada quando o que há é coisa que
    ela não pode ver.
    """
    submeter(edital_c, 3, seed=SEGUNDO_SEED)

    corpo = abrir_o_processo(client, processo_a, subject="estranho")
    lido = texto(corpo)

    # Lê o estado.
    assert 'aria-labelledby="conducao-titulo"' in corpo
    assert "3 inscrições recebidas no Processo" in lido

    # E não recebe caminho algum: nem sinal, nem a linha que anunciaria a ausência deles.
    assert "Atenção" not in texto(regiao(corpo, "conducao-titulo"))
    assert "Nenhuma condição de atenção" not in lido
    assert 'class="sinal"' not in corpo

    # **E nem o caminho que estava fora da conta.** A redação anterior conferia só os sinais, e
    # por isso afirmava no nome o que não verificava: o link da região continuava sendo oferecido
    # a quem a Supervisão recusa, e 7478 casos passaram com o 404 de pé. O guarda que não segue a
    # região inteira deixa de guardá-la — a mesma lição que a varredura de `test_fronteira`
    # aprendeu quando esta página entrou nela.
    assert url(processo_a) not in corpo, "a página oferece a Supervisão a quem ela recusa"
    assert "Abrir a Supervisão" not in lido


def test_quem_preside_recebe_a_atencao_na_mesma_regiao(
    client, seletor_ligado, processo_a, edital_a, edital_c, comissao_de_a
):
    """O outro lado: quem alcança as espécies recebe os sinais, e não só o Pulso.

    Sem este caso, o teste acima passaria igualmente sobre uma região que nunca mostra Atenção
    nenhuma — e a `US1` teria entregue meia tela para todo mundo.
    """
    submeter(edital_c, 2, seed=SEGUNDO_SEED)
    corpo = abrir_o_processo(client, processo_a)
    conducao = regiao(corpo, "conducao-titulo")

    assert "Atenção" in texto(conducao)
    assert "sem avaliador suficiente" in texto(conducao)

    # **A contraprova do caminho**, pela mesma razão que esta função existe: sem ela, o caso acima
    # passaria sobre uma região que nunca oferece a Supervisão a ninguém — e apagar o link seria
    # uma correção tão verde quanto a certa.
    assert url(processo_a) in corpo
    assert "Abrir a Supervisão" in texto(conducao)


def test_sem_nenhuma_condicao_o_processo_tambem_declara_a_ausencia_em_uma_linha(
    client, seletor_ligado, processo_limpo
):
    """`FR-559`: uma linha declarada, e nunca uma seção vazia por espécie.

    A mesma regra da Supervisão, e pela mesma razão: sumir não distinguiria *nada a sinalizar* de
    *a página não carregou*, e um cabeçalho por espécie diria dez vezes que não há nada.
    """
    conducao = regiao(abrir_o_processo(client, processo_limpo), "conducao-titulo")

    assert "Nenhuma condição de atenção" in texto(conducao)
    assert '<li class="sinal"' not in conducao


# ---------------------------------------------------------------------------
# A ausência respeita o alcance de quem lê (045, US1)
#
# **A frase global era dita a quem só enxerga parte.** A convergência de 20/09 mediu: a publicadora
# lia *"Nenhuma condição de atenção neste Processo"* no mesmo instante em que o gestor via quinze
# condições. Os casos abaixo prendem as duas metades — a relativa para quem alcança parte, a
# global só para quem alcança tudo — e a garantia que torna a correção segura: a frase não muda
# com o que o leitor não alcança.
# ---------------------------------------------------------------------------


def atencao_do_processo(corpo):
    """O trecho da Atenção na página do Processo — do título dela ao fim da região de condução.

    Na página do Processo a Atenção não é `<section>` própria: é um bloco da região de condução,
    depois do pulso. Comparar a região inteira misturaria a Atenção com as contagens do pulso,
    que mudam a cada inscrição — e o teste do vazamento compararia a coisa errada.
    """
    conducao = regiao(corpo, "conducao-titulo")
    assert "<h3>Atenção</h3>" in conducao, "a região da Atenção não foi apresentada"
    return conducao.split("<h3>Atenção</h3>", 1)[1]


def edital_do(processo):
    return processo.editais.get()


@pytest.mark.parametrize(
    ("subject", "papeis"),
    [("pedro", ["publicador"]), ("ana", ["julgador"]), ("maria", [])],
    ids=["publicador", "julgador", "presidencia"],
)
def test_quem_alcanca_parte_das_especies_le_a_ausencia_relativa(
    client, seletor_ligado, processo_limpo, subject, papeis
):
    """`045`, `FR-730` e `UX-084` — o teste 1 da proposta.

    Os três alcançam **parte** do catálogo: a publicadora só a divulgação, o julgador só os
    recursos, e a presidência tudo **menos** esses dois. Nenhum deles leu o Processo inteiro, e a
    frase diz isso sem dizer o que ficou de fora.
    """
    from processo_seletivo.interface.supervisao import AUSENCIA_GLOBAL, AUSENCIA_RELATIVA

    atencao = texto(atencao_do_processo(abrir_o_processo(client, processo_limpo, subject, papeis)))

    assert AUSENCIA_RELATIVA in atencao
    assert AUSENCIA_GLOBAL not in atencao


def test_a_frase_nao_muda_com_o_que_o_leitor_nao_alcanca(client, seletor_ligado, processo_limpo):
    """`045`, `FR-731` — o teste 9 da proposta: **nenhum vazamento entre papéis**.

    A publicadora lê o Processo; depois aparece uma condição que só a gestão alcança — inscrição
    sem avaliador, o `UX-003` —; ela lê de novo. **O trecho da Atenção precisa ser o mesmo, letra
    por letra.** Se a frase variasse com o que existe fora do alcance, ela seria o canal por onde
    a supressão se revela: *"há algo que você não vê"* é exatamente o que a supressão silenciosa
    existe para não dizer.

    A contraprova vem da presidência: sem ela, o teste passaria igualmente sobre um cenário em que a
    condição nunca chegou a existir.
    """
    antes = atencao_do_processo(abrir_o_processo(client, processo_limpo, "pedro", ["publicador"]))

    submeter(edital_do(processo_limpo), 2, seed=9)

    presidencia = texto(atencao_do_processo(abrir_o_processo(client, processo_limpo)))
    assert "sem avaliador suficiente" in presidencia, "a condição fora do alcance não existe"

    depois = atencao_do_processo(abrir_o_processo(client, processo_limpo, "pedro", ["publicador"]))
    assert depois == antes


def test_quem_alcanca_todas_as_especies_le_a_ausencia_global(
    client, seletor_ligado, processo_limpo
):
    """`045`, `FR-730`: a frase global continua existindo — e é de quem leu tudo.

    Nenhum papel sozinho alcança o catálogo; a presidência que também julga recurso e publica
    resultado alcança. Na equipe inicial de duas ou três pessoas isso vai acontecer, e está certo:
    essa pessoa de fato leu cada espécie.
    """
    from processo_seletivo.interface.supervisao import AUSENCIA_GLOBAL

    atencao = texto(
        atencao_do_processo(
            abrir_o_processo(client, processo_limpo, "maria", ["gestor", "julgador", "publicador"])
        )
    )

    assert AUSENCIA_GLOBAL in atencao


def test_na_supervisao_a_presidencia_sozinha_le_a_ausencia_relativa(
    client, seletor_ligado, processo_limpo
):
    """`045`, `FR-730`: a mesma escolha vale na Supervisão, que só abre para a gestão.

    E a gestão sozinha **não** alcança o catálogo inteiro — recursos e divulgação têm porta
    própria. Antes desta feature, esta era a tela que mais dizia *"tudo em dia"* a quem não via
    tudo.
    """
    from processo_seletivo.interface.supervisao import AUSENCIA_GLOBAL, AUSENCIA_RELATIVA

    atencao = texto(regiao(abrir(client, processo_limpo), "atencao-titulo"))

    assert AUSENCIA_RELATIVA in atencao
    assert AUSENCIA_GLOBAL not in atencao


def test_o_edital_parado_nao_torna_parcial_a_leitura_de_quem_alcanca_tudo(
    client, seletor_ligado, processo_limpo
):
    """`045`, caso-limite *"O alcance muda com o estado do Edital"*.

    Encerrado o Edital, as espécies de trabalho pendente deixam de ser lidas nele (`038`). Isso é o
    **estado** respondendo, e não o leitor deixando de ver: quem alcança tudo continua lendo a
    frase global. A escolha olha o alcance do leitor, e só ele.
    """
    from processo_seletivo.interface.supervisao import AUSENCIA_GLOBAL
    from processo_seletivo.processos.models import Edital

    Edital.objects.filter(pk=edital_do(processo_limpo).pk).update(status=Edital.Status.ENCERRADO)

    atencao = texto(
        atencao_do_processo(
            abrir_o_processo(client, processo_limpo, "maria", ["gestor", "julgador", "publicador"])
        )
    )

    assert AUSENCIA_GLOBAL in atencao
