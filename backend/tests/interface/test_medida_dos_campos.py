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
