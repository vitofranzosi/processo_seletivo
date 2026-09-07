"""Quem pode ler a fundamentação e a decisão — e quem não pode.

Três círculos, e mais nenhum:

```text
o titular    lê o próprio recurso, no portal
o julgador   lê a peça que vai julgar, na gestão
a auditoria  lê a trilha — que registra que houve ato, e não o conteúdo dele
```

**A fundamentação é o conteúdo mais sensível do recurso.** Ela conta o que a pessoa acha que houve
de errado, e às vezes por que ela acha — e circula por engano com facilidade: numa listagem, numa
exportação, num evento de trilha. Os testes abaixo prendem as bordas por onde ela vazaria (FR-102,
FR-103, FR-105).
"""

import re

import pytest
from django.urls import reverse

from processo_seletivo.auditoria.models import RegistroAuditoria
from tests.conftest import ator_institucional
from tests.fixtures.divulgacao import entrar_como_titular
from tests.fixtures.recursos_us4 import JULGADORA, cenario_julgavel
from tests.interface.conftest import identificar

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.integration]


@pytest.fixture
def peca(gestor, api_client, manager_headers, process_payload):
    return cenario_julgavel(
        gestor, api_client, manager_headers, process_payload, seed=132, codigo="0832"
    )


def conteudo(resposta):
    achado = re.search(r"<main[^>]*>(.*)</main>", resposta.content.decode(), re.DOTALL)
    return achado.group(1) if achado else resposta.content.decode()


def test_o_titular_le_a_propria_fundamentacao(client, peca):
    entrar_como_titular(client, peca["inscricao"])

    corpo = conteudo(client.get(reverse("portal:recurso", args=[peca["recurso"].id])))

    assert peca["recurso"].fundamentacao in corpo


def test_o_julgador_le_a_fundamentacao(client, seletor_ligado, peca):
    identificar(client, JULGADORA, ["julgador"])

    corpo = conteudo(client.get(reverse("interface:recurso", args=[peca["recurso"].id])))

    assert peca["recurso"].fundamentacao in corpo


def test_a_listagem_administrativa_nao_traz_a_fundamentacao(client, seletor_ligado, peca):
    """Ela é conteúdo do juízo, e a lista existe para escolher o que abrir.

    Trazê-la aqui a exporia a todo mundo que tem a capacidade, numa tela que ninguém lê com
    atenção — e sem que ninguém tivesse decidido expô-la.
    """
    identificar(client, JULGADORA, ["julgador"])

    corpo = conteudo(client.get(reverse("interface:recursos", args=[peca["cenario"]["edital"].id])))

    assert peca["recurso"].protocolo in corpo
    assert peca["recurso"].fundamentacao not in corpo


def test_quem_so_gere_o_processo_nao_alcanca_a_peca(client, seletor_ligado, peca):
    """Conduzir o certame não concede leitura do recurso: são autoridades distintas (D-005)."""
    identificar(client, "carlos", ["gestor"])

    resposta = client.get(reverse("interface:recurso", args=[peca["recurso"].id]))

    assert resposta.status_code == 403
    assert peca["recurso"].fundamentacao not in resposta.content.decode()


def test_a_trilha_registra_o_ato_e_nao_o_conteudo(peca):
    """A auditoria responde "houve juízo, por quem e quando" — e não "o que ele dizia" (FR-094).

    Copiar a fundamentação para a trilha criaria uma segunda cópia do conteúdo sensível, num lugar
    com outro regime de acesso e outro tempo de retenção.
    """
    registros = RegistroAuditoria.objects.filter(operation__startswith="recurso:")

    assert registros.exists()
    corpo = " ".join(f"{item.previous_state} {item.new_state} {item.reason}" for item in registros)
    assert peca["recurso"].fundamentacao not in corpo


def test_a_resposta_do_portal_nao_e_armazenavel_pelo_navegador(client, peca):
    """Dado pessoal não fica no cache de um computador compartilhado (FR-105)."""
    entrar_como_titular(client, peca["inscricao"])

    resposta = client.get(reverse("portal:recurso", args=[peca["recurso"].id]))

    cache = resposta.headers.get("Cache-Control", "")
    assert "no-store" in cache


def test_a_tela_administrativa_da_peca_tambem_nao_e_armazenavel(client, seletor_ligado, peca):
    identificar(client, JULGADORA, ["julgador"])

    resposta = client.get(reverse("interface:recurso", args=[peca["recurso"].id]))

    assert "no-store" in resposta.headers.get("Cache-Control", "")


def _julgador():
    return ator_institucional(JULGADORA, "recurso:julgar")
