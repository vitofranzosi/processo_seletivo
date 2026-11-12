"""O custo de "Minhas atividades" (160, SC-2272, SC-2274, R-012).

**Quem não preside paga o que pagava** (FR-6877): a página não roda a derivação para ele, e o número
de consultas não depende de quantas comissões ele integra. **Quem preside paga por Edital**
(FR-6878, 8ª decisão do estudo): a derivação roda uma vez por Edital presidido, e o termo linear é o
que se prende aqui — a diferença entre a página de quem preside o Edital do cenário e a de quem não
tem vínculo nenhum, no mesmo banco.

Um cenário por teste: a idempotência da publicação faz dois colidirem.
"""

import pytest
from django.db import connection
from django.test.utils import CaptureQueriesContext
from django.urls import reverse

from processo_seletivo.interface import andamento as a
from tests.fixtures.andamento import certame_p1, certame_s1
from tests.interface.conftest import identificar

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.performance]

#: Medidos em 12/11/2026 (T034): 23, 29 e 163 consultas por Edital presidido; ver
#: `specs/160-minhas-atividades/verificacao.md`. A folga é de ~20%, como os tetos de
#: `test_andamento_em_escala.py`.
TETO_POR_EDITAL_NO_SORTEIO = 28
TETO_POR_EDITAL_NA_PONTUACAO = 35
TETO_POR_EDITAL_NA_CONVOCACAO = 196


def consultas_da_pagina(client):
    client.get(reverse("interface:minhas-etapas"))  # aquece a sessão
    with CaptureQueriesContext(connection) as capturadas:
        resposta = client.get(reverse("interface:minhas-etapas"))
    assert resposta.status_code == 200
    return len(capturadas)


def por_edital(client, presidente):
    identificar(client, "zeca.sem.vinculo", [])
    sem_vinculo = consultas_da_pagina(client)
    identificar(client, presidente, [])
    presidindo = consultas_da_pagina(client)
    return presidindo - sem_vinculo


@pytest.fixture
def base(gestor, api_client, manager_headers, process_payload, seletor_ligado):
    return gestor, api_client, manager_headers, process_payload


def test_o_membro_paga_o_mesmo_com_uma_e_com_onze_comissoes(client, base, monkeypatch):
    from processo_seletivo.comissoes.domain.funcoes import Funcao
    from processo_seletivo.processos.models import ProcessoSeletivo
    from tests.fixtures.comissao import constituir

    gestor, api_client, manager_headers, process_payload = base
    certame_p1(*base)
    chamadas = []
    original = a.do_edital

    def espiao(edital, ator, **kwargs):
        chamadas.append(edital.id)
        return original(edital, ator, **kwargs)

    monkeypatch.setattr(a, "do_edital", espiao)
    identificar(client, "joao", [])
    com_uma = consultas_da_pagina(client)

    # Dez comissões a mais, em Processos cujo Edital ainda está em elaboração.
    for n in range(2, 12):
        payload = {
            **process_payload,
            "institutionalCode": f"PS-2026-{n:03d}",
            "firstEdital": {"number": f"{n:02d}", "year": 2026, "title": f"Edital {n}"},
        }
        cabecalhos = {**manager_headers, "HTTP_IDEMPOTENCY_KEY": f"160-escala-processo-{n}"}
        criado = api_client.post("/api/v1/admin/processos", payload, format="json", **cabecalhos)
        assert criado.status_code == 201, criado.content
        processo = ProcessoSeletivo.objects.get(pk=criado.json()["id"])
        constituir(gestor, processo, [("joao", Funcao.MEMBRO)], prefixo=f"160-escala-{n}")
    com_onze = consultas_da_pagina(client)

    assert com_uma == com_onze, (com_uma, com_onze)
    assert chamadas == [], "quem não preside não paga a derivação (FR-6856)"


def test_a_presidencia_paga_um_teto_por_edital_no_sorteio(client, base):
    from tests.fixtures.comissao import inscrever

    certame = certame_s1(*base, quantos=3)
    com_poucas = por_edital(client, "maria")

    inscrever(certame["edital"], 27, primeiro=900)
    com_muitas = por_edital(client, "maria")

    print(f"\nsorteio: {com_poucas} e {com_muitas} consultas por Edital presidido")
    assert com_poucas == com_muitas, (com_poucas, com_muitas)
    assert com_muitas <= TETO_POR_EDITAL_NO_SORTEIO, com_muitas


def test_a_presidencia_paga_um_teto_por_edital_na_pontuacao(client, base):
    certame_p1(*base)
    custo = por_edital(client, "maria")
    print(f"\npontuação: {custo} consultas por Edital presidido")
    assert custo <= TETO_POR_EDITAL_NA_PONTUACAO, custo


def test_a_presidencia_paga_um_teto_por_edital_na_convocacao(client, base):
    """A convocação é o caso caro do Centro (`TETO_DA_CONVOCACAO`, 240): cada lista apurada relê a
    leitura do recorte e as prévias. A página paga o mesmo, e só por quem preside."""
    from tests.fixtures.convocacao import montar_cenario_da_convocacao

    montar_cenario_da_convocacao(*base, prefixo="160-escala-conv")
    custo = por_edital(client, "maria")
    print(f"\nconvocação: {custo} consultas por Edital presidido")
    assert custo <= TETO_POR_EDITAL_NA_CONVOCACAO, custo
