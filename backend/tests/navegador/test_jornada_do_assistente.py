"""Habilitar, conversar e desabilitar o assistente, só pelo navegador (170, SC-2451).

A prova automatizada do percurso que o usuário pediu, **sem nenhuma chave de demonstração ligada**:
o ato na administração institucional basta fora de produção (FR-7508). Três partes, como as
jornadas da `107` e da `110`:

1. **Preparação** — a Administradora institucional e a participante do piloto, designadas como a
   implantação e a unidade as designariam; dois Editais publicados; a configuração do serviço
   completa e o serviço falso da suíte no lugar do modelo;
2. **Ações** — só no navegador: habilitar o piloto e a página pública do 91; conversar pela gestão
   e, sem login, pela página pública; ver o 92 sem o assistente; desabilitar; perguntar de novo;
3. **Verificações** — no serviço falso (quantas chamadas chegaram), no banco e na trilha.

A demonstração com o serviço real é outra coisa, e não está aqui: é o roteiro C do quickstart
(SC-2457).
"""

import pytest
from django.urls import reverse

expect = pytest.importorskip("playwright.sync_api", reason="sem o grupo opcional navegador").expect

from processo_seletivo.auditoria.models import RegistroAuditoria  # noqa: E402
from processo_seletivo.duvidas.models import HabilitacaoDoAssistente  # noqa: E402
from processo_seletivo.seguranca import acessos as catalogo  # noqa: E402
from tests.fixtures.corpus import publicar_do_corpus  # noqa: E402
from tests.fixtures.inferencia import (  # noqa: E402, F401
    configuracao_completa,
    contador_falso,
    devolucao,
    porta_falsa,
    saida,
    sem_rede,
)
from tests.fixtures.inferencia_corpus import fonte  # noqa: E402
from tests.seguranca.apoio import pessoa, vincular  # noqa: E402

pytestmark = pytest.mark.django_db(transaction=True)

INES = {"nome": "Inês Institucional", "email": "ines@ifes.edu.br"}
PAULA = {"nome": "Paula Piloto", "email": "paula@ifes.edu.br"}


def _vagas(mensagens):
    total = fonte(mensagens, lugar="INF-BJN", rotulo="Vagas imediatas")
    return devolucao(saida("RESPONDIDA", ("dado", "O polo tem 45 vagas.", [total["id"]])))


@pytest.mark.usefixtures("configuracao_completa", "sem_rede")
def test_habilitar_conversar_e_desabilitar(jornada, api_client, settings, request):
    # Preparação: nenhum atalho, e o percurso é o da interface (FR-7508).
    settings.ASSISTENTE_PILOTO = False
    settings.ASSISTENTE_NA_PAGINA_DO_EDITAL = False
    # Os falsos do assistente da suíte, pelo nome: importados acima para que o pytest os ache.
    request.getfixturevalue("contador_falso")()
    porta = request.getfixturevalue("porta_falsa")(_vagas, _vagas)
    edital_91, _ = publicar_do_corpus(api_client, "91", chave="jornada91")
    edital_92, _ = publicar_do_corpus(api_client, "92", chave="jornada92")
    vincular(
        pessoa("ines", **INES), catalogo.ESCOPO_INSTITUCIONAL, catalogo.ADMINISTRADOR_INSTITUCIONAL
    )
    paula_pessoa = pessoa("paula", **PAULA)
    vincular(paula_pessoa, edital_91.institution_scope, "gestor")
    vincular(paula_pessoa, edital_91.institution_scope, "participante-piloto-assistente")
    ines, paula, visitante = jornada.pessoa(), jornada.pessoa(), jornada.pessoa()
    selecao_91 = jornada.servidor.url + reverse("portal:selecao", args=[edital_91.id])
    selecao_92 = jornada.servidor.url + reverse("portal:selecao", args=[edital_92.id])

    # Passo 1 — a Administradora abre a página e vê a configuração completa.
    jornada.entrar(ines, "ines", **INES)
    ines.get_by_role("link", name="Assistente do Edital").click()
    expect(ines.get_by_text("Configuração completa.")).to_be_visible()
    jornada.capturar(ines, "configuracao-completa")

    # Passo 2 — habilita o piloto e a página pública do 91, cada um com motivo.
    ines.get_by_role("link", name="Habilitar o piloto").click()
    ines.get_by_label("Motivo").fill("Sessão acompanhada de 14/11")
    ines.get_by_role("button", name="Confirmar a habilitação").click()
    expect(ines.get_by_text("Assistente habilitado.")).to_be_visible()
    linha_91 = ines.get_by_role("row").filter(has_text=f"{edital_91.number}/{edital_91.year}")
    linha_91.get_by_role("link", name="Habilitar").click()
    ines.get_by_label("Motivo").fill("Teste com visitante no 91")
    ines.get_by_role("button", name="Confirmar a habilitação").click()
    expect(ines.get_by_text("Assistente habilitado.")).to_be_visible()
    jornada.capturar(ines, "habilitados")

    # Passo 3 — quem tem o papel conversa pela gestão.
    jornada.entrar(paula, "paula", **PAULA)
    paula.goto(jornada.servidor.url + reverse("interface:detalhe", args=[edital_91.id]))
    paula.get_by_role("link", name="Conversar com o assistente (piloto)").click()
    paula.get_by_label("Sua pergunta sobre este Edital").fill("Quantas vagas no polo?")
    paula.get_by_role("button", name="Perguntar").click()
    expect(paula.get_by_text("O polo tem 45 vagas.")).to_be_visible()
    jornada.capturar(paula, "piloto-na-gestao")

    # Passo 4 — o visitante, sem login, conversa na página pública do 91; o 92 não tem o assistente.
    visitante.goto(selecao_91)
    visitante.get_by_role("link", name="Dúvidas sobre este Edital").click()
    visitante.get_by_label("Sua pergunta sobre este Edital").fill("Quantas vagas tem o polo?")
    visitante.get_by_role("button", name="Enviar", exact=True).click()
    expect(visitante.get_by_text("O polo tem 45 vagas.")).to_be_visible()
    jornada.capturar(visitante, "visitante-no-91")
    outra_aba = visitante.context.new_page()
    outra_aba.goto(selecao_92)
    expect(outra_aba.get_by_role("link", name="Dúvidas sobre este Edital")).to_have_count(0)
    outra_aba.close()
    assert len(porta.chamadas) == 2

    # Passo 5 — a Administradora desabilita o 91 e o piloto; nada mais chega ao modelo.
    ines.get_by_role("link", name="Assistente do Edital").click()
    linha_91 = ines.get_by_role("row").filter(has_text=f"{edital_91.number}/{edital_91.year}")
    linha_91.get_by_role("link", name="Desabilitar").click()
    ines.get_by_label("Motivo").fill("Fim do teste no 91")
    ines.get_by_role("button", name="Confirmar a desabilitação").click()
    expect(ines.get_by_text("Assistente desabilitado.")).to_be_visible()
    ines.get_by_role("link", name="Desabilitar o piloto").click()
    ines.get_by_label("Motivo").fill("Fim da sessão")
    ines.get_by_role("button", name="Confirmar a desabilitação").click()
    expect(ines.get_by_text("Assistente desabilitado.")).to_be_visible()
    jornada.capturar(ines, "desabilitados")

    # O visitante pergunta no painel que ainda tinha aberto: recebe o aviso, e não a resposta.
    visitante.get_by_label("Sua pergunta sobre este Edital").fill("E as vagas reservadas?")
    visitante.get_by_role("button", name="Enviar", exact=True).click()
    expect(visitante.get_by_text("O assistente desta seleção foi encerrado.")).to_be_visible()
    jornada.capturar(visitante, "encerrado")
    # A participante abre o assistente de novo: a negativa de sempre (a FR-1464 da 071).
    resposta = paula.goto(
        jornada.servidor.url + reverse("interface:assistente", args=[edital_91.id])
    )
    assert resposta.status == 404

    # Verificações.
    assert len(porta.chamadas) == 2, "nenhuma pergunta chegou ao modelo depois da desabilitação"
    atos = list(
        HabilitacaoDoAssistente.objects.order_by("criado_em").values_list("habilitada", flat=True)
    )
    assert atos == [True, True, False, False]
    eventos = RegistroAuditoria.objects.filter(
        operation__in=("HABILITAR_ASSISTENTE", "DESABILITAR_ASSISTENTE")
    )
    assert eventos.count() == 4
    assert set(eventos.values_list("reason", flat=True)) == {
        "Sessão acompanhada de 14/11",
        "Teste com visitante no 91",
        "Fim do teste no 91",
        "Fim da sessão",
    }
