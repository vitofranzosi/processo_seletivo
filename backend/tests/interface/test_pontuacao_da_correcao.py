"""A pontuação que o julgador fixa chega escrita **em português** — e não pode derrubar a tela.

A caminhada da T125 encontrou o defeito ao digitar o que a própria interface mostra: as telas
exibem "8,5000" e "26,00", e o campo da correção recebia a vírgula e estourava em `InvalidOperation`
— erro 500 na tela de quem julga um recurso, sem recusa, sem motivo e sem o texto que a pessoa já
tinha escrito.

Duas correções, e a segunda é a que importa mais:

```text
vírgula      é o separador decimal do país, e a tela usa exatamente ele — tem de ser aceita
disparate    "abc" recusa com motivo, na página, preservando a motivação escrita — nunca 500
```

**A mensagem é a canônica**, e não uma escrita aqui: desde a convergência do PR a correção fixada
passa pela mesma `avaliacoes.domain.pontuacao.validar` que a conclusão de Avaliação enfrenta. Ter
duas frases para a mesma recusa é o sintoma de ter duas validações — que é o defeito de fundo.
"""

import re
from decimal import Decimal

import pytest
from django.urls import reverse

from processo_seletivo.recursos.models import DecisaoRecurso
from processo_seletivo.resultados.models import ResultadoEtapa
from tests.fixtures.recursos_us4 import JULGADORA, cenario_julgavel
from tests.interface.conftest import identificar

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.integration]


@pytest.fixture
def admitida(client, seletor_ligado, gestor, api_client, manager_headers, process_payload):
    """A peça já admitida — o que falta é julgar, que é onde o defeito morava."""
    peca = cenario_julgavel(
        gestor, api_client, manager_headers, process_payload, seed=132, codigo="0832"
    )
    etapa = peca["cenario"]["etapa"]
    alvo = ResultadoEtapa.vigentes.get(inscricao=peca["inscricao"], etapa_id=etapa)
    return peca["recurso"], str(etapa), alvo, peca["inscricao"]


def conteudo(resposta):
    return re.search(r"<main[^>]*>(.*)</main>", resposta.content.decode(), re.DOTALL).group(1)


def test_a_virgula_decimal_e_aceita(client, admitida):
    """É o separador que o país usa e que a própria tela imprime."""
    peca, etapa, alvo, inscricao = admitida
    identificar(client, JULGADORA, ["julgador"])

    resposta = client.post(
        reverse("interface:recurso-julgar", args=[peca.id]),
        {
            "especie": "CORRECAO_FIXADA",
            "motivacao": "Conferido o acervo, o documento consta e não foi pontuado.",
            "etapa": f"{etapa}|{alvo.id}",
            f"pontuacao-{etapa}": "82,0000",
        },
    )

    assert resposta.status_code == 302, resposta.content[:400]
    assert DecisaoRecurso.objects.get(recurso=peca).especie == (
        DecisaoRecurso.Especie.CORRECAO_FIXADA
    )
    sucessor = ResultadoEtapa.vigentes.get(inscricao=inscricao, etapa_id=etapa)
    assert sucessor.pontuacao == Decimal("82.0000")


def test_pontuacao_que_nao_e_numero_recusa_na_pagina(client, admitida):
    """Recusa com motivo e com o texto preservado — nunca erro de servidor."""
    peca, etapa, alvo, _inscricao = admitida
    identificar(client, JULGADORA, ["julgador"])
    motivacao = "O parecer não enfrentou o documento juntado na inscrição."

    resposta = client.post(
        reverse("interface:recurso-julgar", args=[peca.id]),
        {
            "especie": "CORRECAO_FIXADA",
            "motivacao": motivacao,
            "etapa": f"{etapa}|{alvo.id}",
            f"pontuacao-{etapa}": "oitenta e dois",
        },
    )

    assert resposta.status_code == 422
    corpo = conteudo(resposta)
    assert "A pontuação precisa ser um número." in corpo
    assert motivacao in corpo, "recusar apagando o que foi escrito é pedir para escrever de novo"
    assert not DecisaoRecurso.objects.filter(recurso=peca).exists()
