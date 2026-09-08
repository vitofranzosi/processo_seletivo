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
