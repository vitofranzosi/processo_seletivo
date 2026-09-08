"""Um campo e o campo ao lado têm a mesma medida — e a medida vem do tamanho da fonte.

O cartão de Identificação exibia dois campos da mesma classe terminando **43 px um do outro**. A
largura declarada era a mesma nos dois: `max-width: var(--leitura)`. O que diferia era a fonte.

`--leitura` é `68ch`, e `ch` é a largura do "0" **na fonte do próprio elemento**. O `input`
renderiza a 16px e a `textarea` renderizava a 15px, então "68 caracteres" valia 685 px num e
642 px no outro.

E os 15px não eram escolha: nasciam de duas regras de mesma especificidade disputando desempate por
ordem na folha. `input[type=text]` (0,1,1), mais abaixo, ganhava de `.campo input` (0,1,1); mas
`.campo textarea` (0,1,1) ganhava de `textarea` (0,0,1). Duas regras que discordam sobre o tamanho
produzem um resultado diferente por tipo de controle — e ninguém escreveu isso.

O que estes testes prendem é a concordância, e não o valor: o dia em que a fonte dos campos mudar,
ela muda nos dois lugares ou o teste avisa.
"""

import re

import pytest
from django.urls import reverse

from tests.interface.conftest import identificar

pytestmark = [pytest.mark.django_db]

CONTROLE = re.compile(r"\b(?:input|select|textarea)\b")
# Um seletor é **geral** quando tudo nele é ou o próprio controle ou `.campo`: é o que alcança os
# campos do assistente. `.reabertura input[type=text]` não é — ela veste um componente só, e ter
# medida própria ali é escolha legítima.
COMPOSTO_GERAL = re.compile(r"^(?:input(?:\[[^\]]+\])?|select|textarea|\.campo)$")


@pytest.fixture
def folha(client, seletor_ligado):
    identificar(client, "carlos", ["gestor"])
    corpo = client.get(reverse("interface:lista")).content.decode()
    return corpo[corpo.index("<style>") : corpo.index("</style>")]


def regras(folha):
    """(seletor, corpo) de cada regra, com os comentários fora do caminho."""
    sem_prosa = re.sub(r"/\*.*?\*/", "", folha, flags=re.S)
    return re.findall(r"([^{}]+)\{([^}]*)\}", sem_prosa)


def geral(seletor):
    partes = seletor.strip().split()
    return bool(partes) and all(COMPOSTO_GERAL.match(parte) for parte in partes)


def test_as_regras_gerais_de_controle_concordam_sobre_o_tamanho(folha):
    """Discordar aqui não escolhe um tamanho: escolhe **um por tipo de controle**."""
    tamanhos = {}
    for seletor, corpo in regras(folha):
        for um in seletor.split(","):
            if not (CONTROLE.search(um) and geral(um)):
                continue
            achado = re.search(r"(?:^|;)\s*font-size:\s*([^;]+)", corpo)
            if achado:
                tamanhos.setdefault(achado.group(1).strip(), []).append(" ".join(um.split()))

    assert len(tamanhos) == 1, (
        f"regras gerais de controle declarando tamanhos diferentes: {tamanhos}. "
        "A especificidade decide caso a caso, e campos vizinhos saem de tamanhos distintos."
    )


def test_a_medida_de_leitura_e_em_caracteres(folha):
    """É o que amarra os dois testes: em `ch`, tamanho de fonte **é** largura.

    Se um dia `--leitura` virar `rem`, a concordância acima deixa de governar a largura — e o teste
    de cima deixa de ser sobre alinhamento. Esta guarda existe para que essa mudança seja notada.
    """
    assert "--leitura:68ch" in folha.replace(" ", "")


# ------------------------------------------------ o cartão de Identificação


@pytest.fixture
def identificacao(client, seletor_ligado, edital):
    identificar(client, "ana.elaboradora", ["elaborador"])
    return client.get(
        reverse("interface:compor-etapa", args=[edital.id, "identificacao"])
    ).content.decode()


def test_os_fatos_fixos_nao_usam_a_grade_de_participantes(identificacao):
    """`dl.participantes` é grade `auto 1fr`, e punha os valores 120 px à direita de tudo.

    Com os rótulos e os campos na margem do cartão, o resultado eram três margens esquerdas na
    mesma caixa. `participantes` continua existindo e servindo às telas que listam quem participa.
    """
    assert 'class="fatos-fixos"' in identificacao
    assert 'class="participantes"' not in identificacao


def test_os_fatos_fixos_continuam_sendo_termo_e_definicao(identificacao):
    """O arranjo mudou; a semântica não. "Processo Seletivo" **é** termo, e o número é definição."""
    assert "<dl" in identificacao
    for termo in ("Processo Seletivo", "Número e ano"):
        assert f"<dt>{termo}</dt>" in identificacao


def test_o_bloco_fixo_respira_antes_do_primeiro_campo(folha):
    """Encostava com zero, contra 12 px entre todos os outros pares do cartão."""
    achado = re.search(r"\.fatos-fixos\{([^}]*)\}", folha)
    assert achado, "a folha não desenha `.fatos-fixos`"
    margem = re.search(r"margin:[^;]*?(\d+(?:\.\d+)?)rem\s*(?:;|$)", achado.group(1))
    assert margem and float(margem.group(1)) > 0, (
        f"`.fatos-fixos` sem margem inferior: {achado.group(1)}"
    )


# ------------------------------------------------ o cartão de Perfil de Vaga


@pytest.fixture
def perfil(client, seletor_ligado, edital):
    identificar(client, "ana.elaboradora", ["elaborador"])
    return client.get(reverse("interface:fragmento-perfil"), {"indice": "0"}).content.decode()


def campos_por_linha(marcacao):
    """Quantos `.campo` cada `div.campos` do cartão carrega, na ordem em que aparecem."""
    return [
        bloco.count('class="campo')
        for bloco in re.findall(
            r'<div class="campos">(.*?)(?=<div class="campos"|<section)', marcacao, re.S
        )
    ]


def test_nenhuma_linha_do_perfil_carrega_um_campo_sozinho(perfil):
    """Campo sozinho na linha deixa um vão do próprio tamanho dele à direita.

    O controle pára em `68ch` e a linha tem a largura do cartão: quatro campos ocupavam uma linha
    cada um, e o Perfil media 1.098 px de altura para dizer o que cabe em 804. Com dois ou três por
    linha, a largura é repartida antes de o teto morder — nada é cortado e nada sobra.
    """
    por_linha = campos_por_linha(perfil)
    assert por_linha, "nenhuma linha de campos encontrada"
    assert all(quantos >= 2 for quantos in por_linha), (
        f"linha com um campo só: {por_linha}. Sozinho, ele deixa metade da linha vazia."
    )


def test_a_denominacao_nao_pede_mais_largura_do_que_cabe(perfil):
    """`largo` é `flex 2`: na linha de três, ela pedia 725 px e o teto de leitura cortava em 685.

    O vão não ficava na ponta da linha, e sim **no meio dela** — entre Denominação e Localidade.
    """
    assert re.search(r'<p class="campo">\s*<label for="perfil-0-name"', perfil)


def test_a_reserva_divide_a_linha_com_as_vagas_imediatas(perfil):
    """São as duas metades da mesma pergunta: quantas agora, e o que acontece depois delas."""
    entre = perfil[perfil.index("immediateVacancies") : perfil.index('<fieldset class="opcoes">')]

    # `</div>`, e não `<div class="campos">`: antes o grupo ficava **fora** de qualquer linha, de
    # modo que nenhuma linha nova começava entre os dois — o que havia era o fechamento da linha
    # das vagas. Procurar a abertura deixava o teste passar com o defeito de pé.
    assert "</div>" not in entre, (
        "a linha das vagas imediatas fecha antes da reserva — elas não dividem a mesma linha"
    )


# ------------------------------------------------ a voz dos rótulos de grupo


def test_a_caixa_alta_e_do_cartao_e_nao_de_todo_grupo_dentro_dele(folha):
    """`fieldset.linha legend` vestia a faixa de identidade do cartão — e vazava para dentro.

    O resultado era "CADASTRO RESERVA" gritando ao lado de "Vagas imediatas", que rotula um campo
    irmão e se escreve em caixa normal. Descendente virou filho direto.
    """
    achado = re.search(r"fieldset\.linha\s*(>?)\s*legend\{([^}]*)\}", folha)
    assert achado, "a folha não desenha a legenda do cartão"
    assert "uppercase" in achado.group(2), "a faixa do cartão perdeu a caixa alta"
    assert achado.group(1) == ">", (
        "a regra alcança todo `legend` dentro do cartão, inclusive os grupos aninhados"
    )


@pytest.mark.parametrize("grupo", ["fieldset.opcoes>legend", "fieldset.caracter legend"])
def test_os_rotulos_de_grupo_tem_a_voz_do_rotulo_de_campo(folha, grupo):
    """Um grupo que nomeia controles do mesmo nível dos campos ao lado se lê como eles."""
    do_campo = re.search(r"\.campo label\{([^}]*)\}", folha).group(1)
    do_grupo = re.search(re.escape(grupo).replace(r"\>", ">") + r"\{([^}]*)\}", folha)
    assert do_grupo, f"a folha não desenha `{grupo}`"
    for propriedade in ("font-size", "font-weight"):
        esperado = re.search(rf"{propriedade}:([^;]+)", do_campo).group(1).strip()
        achado = re.search(rf"{propriedade}:([^;]+)", do_grupo.group(1))
        assert achado and achado.group(1).strip() == esperado, (
            f"`{grupo}` tem {propriedade} diferente do rótulo de campo"
        )


# ------------------------------------------------ o cartão de Evento do Cronograma


@pytest.fixture
def evento(client, seletor_ligado, edital):
    identificar(client, "ana.elaboradora", ["elaborador"])
    return client.get(reverse("interface:fragmento-evento"), {"indice": "0"}).content.decode()


def test_o_campo_de_data_tem_teto_proprio_e_nao_o_de_leitura(folha):
    """68 caracteres não dizem nada sobre `dd/mm/aaaa, --:--`.

    Fora da lista do teto, o campo esticava com a linha — 647 px para dezesseis caracteres —, e
    eram os dois dele que impediam o Evento de caber numa linha só. O teto é folgado de propósito:
    quem desenha o controle é o navegador, varia por idioma, e cortar um segmento de data é pior
    do que sobrar espaço.
    """
    achado = re.search(r"input\[type=date\],input\[type=datetime-local\]\{([^}]*)\}", folha)
    assert achado, "a folha não dá teto ao campo de data"
    teto = re.search(r"max-width:([^;]+)", achado.group(1))
    assert teto, f"sem `max-width`: {achado.group(1)}"
    assert "--leitura" not in teto.group(1), (
        "o teto da data não é medida de leitura: o conteúdo tem tamanho fixo, e quem o desenha\n"
        "é o navegador"
    )


def test_a_coluna_da_data_nao_reserva_mais_do_que_o_campo_aceita(folha):
    """Teto sem base resolve o campo e não a coluna: o vão só muda de lugar.

    Com o `p` esticando, o espaço que o campo recusa fica **dentro** da linha, entre o campo de
    data e o rótulo seguinte — que é pior de ler do que sobrar na ponta.
    """
    assert re.search(r"\.campo:has\(>input\[type=datetime-local\]\)[^{]*\{[^}]*flex:", folha)


def test_o_evento_cabe_numa_linha(evento):
    """Que evento é, o que é, quando começa, quando termina — a ordem em que se lê e se preenche."""
    linhas = re.findall(r'<div class="campos">', evento)
    assert len(linhas) == 1, f"o Evento ocupa {len(linhas)} linhas de campo"
    for campo in ("-type", "-description", "-startAt", "-endAt"):
        assert f'name="evento-0{campo}"' in evento


# ------------------------------------------------ o cartão de Etapa de Avaliação


@pytest.fixture
def etapa(client, seletor_ligado, edital):
    identificar(client, "ana.elaboradora", ["elaborador"])
    return client.get(
        reverse("interface:fragmento-etapa", args=[edital.id]), {"indice": "0"}
    ).content.decode()


def test_o_nome_da_etapa_nao_pede_mais_largura_do_que_cabe(etapa):
    """`largo` é `flex 2`: ela pedia 862 px e o teto de leitura cortava em 685.

    Os 151 px que sobravam não ficavam na ponta da linha: ficavam **entre** o campo e o rótulo do
    Evento do Cronograma, que é onde um vão atrapalha a leitura.
    """
    assert re.search(r'<p class="campo">\s*<label for="etapa-0-name"', etapa)


def test_a_conclusao_divide_a_linha_com_o_que_nao_depende_dela(etapa):
    """Sozinha, ela usava 387 px de 1.355 — quase mil vazios à direita.

    Peso, Avaliações por inscrição e Caráter são atributos **independentes** da forma de concluir:
    podem dividir a faixa sem sugerir que dependem dela, e é isso que enche a linha.
    """
    # Do fim do grupo até o Peso não pode haver fechamento de linha nem abertura de outra. Contar
    # profundidade a partir da linha **anterior** ao grupo não servia: no arranjo antigo ela já
    # havia fechado, e a conta dava positivo por causa da linha nova que se abria depois — o teste
    # passava com o defeito de pé.
    fim_do_grupo = etapa.index("</fieldset>", etapa.index('<fieldset class="opcoes">'))
    entre = etapa[fim_do_grupo : etapa.index("-weight")]

    assert "</div>" not in entre and '<div class="campos">' not in entre, (
        "há fronteira de linha entre a conclusão e o Peso — eles não dividem a mesma linha"
    )
    for vizinho in ("-weight", "-evaluationsPerRegistration", "caracter"):
        assert vizinho in etapa


def test_o_grupo_que_divide_a_linha_tem_base_propria(folha):
    """Sem `flex`, o `fieldset` entra como item de largura automática e empurra o vizinho."""
    assert re.search(r"\.campos>fieldset\.opcoes\{[^}]*flex:", folha)


def test_a_coluna_curta_tem_a_largura_do_que_carrega(folha):
    """150 px cravados quebravam o rótulo, e o rótulo quebrado desalinhava a linha inteira.

    "Avaliações por inscrição" precisa de 165 px e tinha 150: o rótulo ia para duas linhas e
    empurrava o seu controle 19 px abaixo do controle de "Peso", ao lado. A ajuda quebrava pela
    mesma razão, e as cinco ajudas da Etapa somavam 198 px — 45% da altura do cartão.

    O `input` continua curto: quem o limita é `.campo.curto>input`, e não a coluna.
    """
    regra = re.search(r"\.campo\.curto\{([^}]*)\}", folha)
    assert regra, "a folha não desenha `.campo.curto`"
    assert "flex:01auto" in regra.group(1).replace(" ", ""), (
        f"a coluna curta voltou a ter largura cravada: {regra.group(1)}"
    )
    do_input = re.search(r"\.campo\.curto>input\{([^}]*)\}", folha)
    assert do_input and "max-width" in do_input.group(1), (
        "sem teto no `input`, soltar a coluna soltaria o campo junto"
    )


# ------------------------------------------------ divulgação progressiva, e não ajuda por cartão


@pytest.fixture
def pagina_de_etapas(client, seletor_ligado, edital):
    identificar(client, "ana.elaboradora", ["elaborador"])
    return client.get(
        reverse("interface:compor-etapa", args=[edital.id, "etapas"])
    ).content.decode()


def test_a_explicacao_conceitual_vive_uma_vez_na_lista(pagina_de_etapas, etapa):
    """Explicação que não muda de uma Etapa para a outra não se imprime uma vez por Etapa.

    Sete ajudas visíveis por cartão disputavam a leitura com os dados, e um Edital de quatro Etapas
    as repetia quatro vezes. Elas passaram para uma ajuda da lista; o cartão ficou com os dados.
    """
    assert 'class="como-preencher"' in pagina_de_etapas
    assert 'class="ajuda"' not in etapa, "o cartão da Etapa voltou a carregar ajuda visível própria"


def test_a_ajuda_da_lista_abre_sem_ponteiro(pagina_de_etapas):
    """`details`/`summary` abre por teclado e por toque.

    É o que separa divulgação progressiva de dica sobre ícone: a segunda só existe para quem tem
    mouse, e foi por confundir as duas que a proposta anterior recusou a ideia inteira.
    """
    bloco = re.search(r"<details class=\"como-preencher\">(.*?)</details>", pagina_de_etapas, re.S)
    assert bloco, "a ajuda da lista não é um `details`"
    assert "<summary>" in bloco.group(1)
    for conceito in ("Como esta Etapa é concluída", "Rótulos do resultado", "Evento do Cronograma"):
        assert conceito in bloco.group(1), conceito


def test_a_frase_do_evento_deixou_de_repetir_a_introducao(pagina_de_etapas):
    """A ajuda do campo repetia, palavra por palavra, a frase que abre a seção — em cada cartão."""
    intro = re.search(r'<p class="ajuda">(.*?)</p>', pagina_de_etapas, re.S).group(1)

    assert "não há data para digitar aqui" not in " ".join(intro.split())


@pytest.mark.parametrize(
    ("campo", "marca"),
    [
        ("minimumScore", "Sem mínimo"),
        ("maximumScore", "Sem limite"),
        ("weight", "Sem ponderação"),
        ("evaluationsPerRegistration", "Padrão: 1"),
    ],
)
def test_a_consequencia_de_deixar_vazio_esta_no_proprio_controle(etapa, campo, marca):
    """O que só se descobre errando fica no campo, e não numa ajuda que se lê antes de errar."""
    controle = re.search(rf'<input[^>]*name="etapa-0-{campo}"[^>]*>', etapa, re.S)
    assert controle, campo
    assert f'placeholder="{marca}"' in controle.group(0), controle.group(0)


@pytest.mark.parametrize("campo", ["minimumScore", "maximumScore", "weight"])
def test_o_campo_que_admite_vazio_se_diz_opcional(etapa, campo):
    """O contrário do asterisco: quem se pergunta se pode deixar em branco lê a resposta no
    próprio rótulo."""
    rotulo = re.search(rf'<label for="etapa-0-{campo}">(.*?)</label>', etapa, re.S)
    assert rotulo and "(opcional)" in rotulo.group(1), campo


def test_nenhuma_descricao_se_perdeu_ao_sair_de_vista(etapa):
    """Esconder da tela não é apagar: o texto continua no documento e o campo continua apontando.

    É a diferença entre divulgação progressiva e remoção — e é o que faz a mudança não custar nada
    a quem usa leitor de tela.
    """
    ocultos = dict(re.findall(r'<span class="oculto" id="([^"]+)">(.*?)</span>', etapa, re.S))
    assert len(ocultos) == 7, f"esperava sete descrições preservadas, achei {len(ocultos)}"

    for nome in ("scheduleEventId", "minimumScore", "maximumScore", "weight"):
        controle = re.search(
            rf'<input[^>]*name="etapa-0-{nome}"[^>]*>|<select[^>]*name="etapa-0-{nome}"[^>]*>',
            etapa,
            re.S,
        )
        apontados = re.search(r'aria-describedby="([^"]*)"', controle.group(0))
        assert apontados, f"{nome} deixou de apontar descrição"
        assert any(alvo in ocultos for alvo in apontados.group(1).split()), nome


# ------------------------------------------------ o mesmo tratamento nas demais parciais


@pytest.fixture
def fragmentos(client, seletor_ligado, com_etapas):
    """Cada parcial do assistente, renderizada como o htmx a insere."""
    from tests.interface.test_compor import PERFIL

    identificar(client, "ana.elaboradora", ["elaborador"])
    edital = com_etapas
    pedidos = {
        "perfil": (reverse("interface:fragmento-perfil"), {}),
        "evento": (reverse("interface:fragmento-evento"), {}),
        "documento": (reverse("interface:fragmento-documento", args=[edital.id]), {}),
        "marco": (
            reverse("interface:fragmento-marco", args=[PERFIL]),
            {"edital": str(edital.id)},
        ),
        "etapa": (reverse("interface:fragmento-etapa", args=[edital.id]), {}),
    }
    return {
        nome: client.get(url, {**dados, "indice": "0"}).content.decode()
        for nome, (url, dados) in pedidos.items()
    }


@pytest.mark.parametrize("parcial", ["perfil", "evento", "documento", "marco", "etapa"])
def test_nenhum_cartao_do_assistente_carrega_ajuda_visivel(fragmentos, parcial):
    """Explicação que não muda de um cartão para o outro não se imprime uma vez por cartão.

    Um Edital com três Perfis imprimia as duas introduções de subseção três vezes cada; um com
    cinco requisitos, as quatro explicações do documento cinco vezes.
    """
    assert 'class="ajuda"' not in fragmentos[parcial]


@pytest.mark.parametrize("parcial", ["perfil", "evento", "documento", "marco", "etapa"])
def test_toda_descricao_escondida_continua_apontada_por_algum_campo(fragmentos, parcial):
    """Sair de vista não é sair da página — mas só se alguém ainda apontar para ela.

    No marco, seis das oito explicações **não tinham `id`** e não eram anunciadas a leitor de tela
    nenhum. Escondê-las sem ligar teria sido apagá-las; ligá-las melhorou o que se anuncia.
    """
    marcacao = fragmentos[parcial]
    escondidas = set(re.findall(r'<span class="oculto" id="([^"]+)"', marcacao))
    apontadas = {
        alvo
        for atributo in re.findall(r'aria-describedby="([^"]*)"', marcacao)
        for alvo in atributo.split()
    }

    assert escondidas, f"{parcial} não preservou descrição nenhuma"
    assert escondidas <= apontadas, (
        f"descrição escondida e não apontada em {parcial}: {sorted(escondidas - apontadas)}"
    )


@pytest.mark.parametrize("parcial", ["perfil", "evento", "documento", "marco", "etapa"])
def test_nenhum_campo_aponta_para_descricao_que_nao_existe(fragmentos, parcial):
    """O outro lado do mesmo laço: apontar para nada é pior do que não apontar."""
    marcacao = fragmentos[parcial]
    existentes = set(re.findall(r'<span[^>]* id="([^"]+)"', marcacao))
    apontadas = {
        alvo
        for atributo in re.findall(r'aria-describedby="([^"]*)"', marcacao)
        for alvo in atributo.split()
        if alvo.startswith("ajuda-")
    }

    assert apontadas <= existentes, (
        f"{parcial} aponta descrição inexistente: {sorted(apontadas - existentes)}"
    )


@pytest.mark.parametrize(
    ("etapa_do_assistente", "conceitos"),
    [
        ("perfis", ["Modalidades de Concorrência", "Fatos exigidos"]),
        ("classificacao", ["Etapas que entram na ordem", "Recurso contra o resultado"]),
        ("inscricao", ["Chave", "Modelo que o Edital fornece"]),
    ],
)
def test_a_lista_carrega_a_explicacao_que_saiu_dos_cartoes(
    client, seletor_ligado, com_etapas, etapa_do_assistente, conceitos
):
    """O conceito não some: ele passa a viver uma vez, onde a lista inteira o alcança."""
    identificar(client, "ana.elaboradora", ["elaborador"])

    corpo = client.get(
        reverse("interface:compor-etapa", args=[com_etapas.id, etapa_do_assistente])
    ).content.decode()

    # `<details class="como-preencher">`, e não a string solta: o nome da classe também aparece na
    # folha inline, que viaja em **toda** página — inclusive na de identificação.
    bloco = re.search(r'<details class="como-preencher">(.*?)</details>', corpo, re.S)
    assert bloco, f"{etapa_do_assistente} não oferece a ajuda da lista"
    for conceito in conceitos:
        assert conceito in bloco.group(1), conceito


# ------------------------------------------------ Identificação e Anexos: o mesmo princípio


@pytest.fixture
def anexos(client, seletor_ligado, edital):
    """A etapa de Anexos com um anexo dentro — é dentro do cartão que a ajuda se repetia."""
    from django.core.files.uploadedfile import SimpleUploadedFile

    from tests.fixtures.anexos import pdf_de_teste

    identificar(client, "ana.elaboradora", ["elaborador"])
    client.post(
        reverse("interface:anexos", args=[edital.id]),
        {
            "acao": "anexar",
            "rotulo": "ANEXO I — REQUERIMENTO",
            "arquivo": SimpleUploadedFile(
                "requerimento.pdf", pdf_de_teste("A"), content_type="application/pdf"
            ),
        },
    )
    return client.get(
        reverse("interface:compor-etapa", args=[edital.id, "anexos"])
    ).content.decode()


def test_a_convencao_do_rotulo_vive_uma_vez_na_lista_de_anexos(anexos):
    """A convenção é a mesma para todo anexo, e a de substituição repetia dentro de cada cartão.

    A amostra real de Editais chega a onze anexos: era onze vezes a mesma frase.
    """
    bloco = re.search(r'<details class="como-preencher">(.*?)</details>', anexos, re.S)
    assert bloco, "a etapa de Anexos não oferece a ajuda da lista"
    assert "não numera nem renumera" in bloco.group(1)
    assert "substitui o atual" in bloco.group(1)


def test_o_cartao_do_anexo_nao_carrega_ajuda_visivel(anexos):
    cartoes = re.findall(r'<fieldset class="linha anexo">(.*?)</fieldset>', anexos, re.S)
    assert cartoes, "nenhum cartão de anexo renderizado"
    for cartao in cartoes:
        assert 'class="ajuda"' not in cartao


def test_a_identificacao_nao_ganha_ajuda_expansivel(identificacao):
    """Sem lista, não há explicação que se repita — e a caixa cobraria um clique por nada.

    Aplicar o padrão onde ele não tem o que carregar seria decalque, e não princípio. O que dava
    para tirar do caminho saiu para dentro do campo.
    """
    assert "como-preencher" not in identificacao.replace(
        identificacao[identificacao.index("<style>") : identificacao.index("</style>")], ""
    )
    campo = re.search(r"<textarea[^>]*id=\"ident-description\"[^>]*>", identificacao, re.S)
    assert campo and 'placeholder="Resumo do objeto do Edital"' in campo.group(0)


def test_a_descricao_do_edital_perdeu_a_frase_que_contava_uma_mudanca(identificacao):
    """ "e agora ela pode ser preenchida aqui" narra a história do produto, não o que o campo é."""
    assert "agora ela pode ser preenchida aqui" not in identificacao


@pytest.mark.parametrize("tela", ["anexos", "identificacao"])
def test_as_duas_telas_preservam_a_descricao_apontada(
    client, seletor_ligado, edital, anexos, identificacao, tela
):
    corpo = anexos if tela == "anexos" else identificacao
    escondidas = set(re.findall(r'<span class="oculto" id="([^"]+)"', corpo))
    apontadas = {
        alvo
        for atributo in re.findall(r'aria-describedby="([^"]*)"', corpo)
        for alvo in atributo.split()
        if alvo.startswith("ajuda-")
    }

    assert escondidas, f"{tela} não preservou descrição nenhuma"
    assert escondidas <= apontadas, sorted(escondidas - apontadas)
    assert apontadas <= set(re.findall(r'id="([^"]+)"', corpo)), sorted(apontadas - escondidas)
