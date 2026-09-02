"""A Mesa de quem tem centenas de inscrições — o que ela precisa dizer, e não dizia.

Os quatro defeitos que este arquivo prende foram encontrados percorrendo um Processo de 600
inscritos, e nenhum deles aparece numa Mesa de três: com poucas linhas, "onde eu parei" se responde
olhando, e uma atribuição a menos se percebe.
"""

import re

import pytest
from django.urls import reverse

from processo_seletivo.avaliacoes.application.avaliacao import gravar
from processo_seletivo.avaliacoes.application.impedimento import registrar_impedimento
from tests.conftest import ator_institucional
from tests.fixtures.mesa import concluir_como, distribuir_para, inscricoes_de, montar_banca
from tests.interface.conftest import identificar

pytestmark = [pytest.mark.django_db]


@pytest.fixture
def cenario(gestor, api_client, manager_headers):
    return montar_banca(gestor, api_client, manager_headers, seed=27, codigo="ME")


@pytest.fixture
def cinco(cenario, gestor):
    inscricoes = inscricoes_de(cenario, 5, primeiro=2700)
    distribuir_para(cenario, gestor, ["joao"], inscricoes, chave="me")
    return inscricoes


@pytest.fixture
def como_joao(client, seletor_ligado):
    identificar(client, "joao", [])
    return client


def mesa(cenario, **filtros):
    base = reverse("interface:minha-etapa", args=[cenario["edital"].id, cenario["etapa"]])
    if not filtros:
        return base
    return base + "?" + "&".join(f"{chave}={valor}" for chave, valor in filtros.items())


def rascunhar(cenario, inscricao, pontuacao="82"):
    gravar(
        ator=ator_institucional("joao"),
        edital=cenario["edital"],
        etapa_id=cenario["etapa"],
        inscricao_id=inscricao.id,
        pontuacao=pontuacao,
        parecer="Em análise.",
        expected_revision=1,
        correlation_id="teste",
    )


def test_o_rascunho_nao_se_confunde_com_o_nao_iniciado(como_joao, cenario, cinco):
    """Uma avaliação começada aparecia igual às que ninguém abriu.

    Numa Mesa de centenas, isso faz retomar o trabalho virar memória — e uma avaliação em andamento
    pode ficar esquecida sem que nada indique.
    """
    rascunhar(cenario, cinco[0])

    corpo = como_joao.get(mesa(cenario)).content.decode()

    assert "Em rascunho" in corpo
    assert "Não iniciada" in corpo
    assert "em rascunho" in corpo


def test_o_filtro_de_rascunhos_traz_so_o_que_foi_comecado(como_joao, cenario, cinco):
    rascunhar(cenario, cinco[0])
    concluir_como(cenario, "joao", cinco[1])

    corpo = como_joao.get(mesa(cenario, filtro="rascunhos")).content.decode()

    assert cinco[0].protocolo in corpo
    assert cinco[1].protocolo not in corpo
    assert cinco[2].protocolo not in corpo


def test_a_mesa_diz_o_que_foi_retirado_dela_e_por_que(como_joao, cenario, gestor, cinco):
    """FR-053 registra o ato com autor e motivo; a trilha responde 404 para quem avalia.

    Sem isto, a pessoa cujo trabalho foi retirado era a única sem canal para saber que isso
    aconteceu: a atribuição some da Mesa e a contagem muda, em silêncio.
    """
    registrar_impedimento(
        actor=gestor,
        processo_id=cenario["processo"].id,
        identity_subject="joao",
        inscricao_id=cinco[0].id,
        motivo="Parentesco declarado em reunião.",
        idempotency_key="me-imp",
        correlation_id="teste",
    )

    corpo = como_joao.get(mesa(cenario)).content.decode()

    assert "Atribuições retiradas de você" in corpo
    assert f"Inscrição {cinco[0].protocolo}" in corpo
    assert "Parentesco declarado em reunião." in corpo


def test_a_tela_inicial_diz_quanto_falta_em_cada_etapa(como_joao, cenario, cinco):
    """Listar Etapas e um botão “Abrir” não responde a primeira pergunta de quem trabalha.

    São duas perguntas, e a frase única — "4 pendentes de 5" — respondia só a primeira: o quanto
    já andou ficava para a aritmética de quem lê. Os estados do medidor estão em
    `test_completude_das_etapas`.
    """
    concluir_como(cenario, "joao", cinco[0])

    corpo = como_joao.get(reverse("interface:minhas-etapas")).content.decode()

    assert "pendentes" in corpo and "4</strong>" in corpo
    assert "20%" in corpo
    assert "1 de 5" in corpo


def test_a_inscricao_oferece_a_proxima_pendente(como_joao, cenario, cinco):
    """Com centenas atribuídas, voltar pela trilha a cada uma faz o caminho ser mais longo que o
    trabalho."""
    corpo = como_joao.get(
        reverse(
            "interface:mesa-inscricao",
            args=[cenario["edital"].id, cenario["etapa"], cinco[0].id],
        )
    ).content.decode()

    assert f"Próxima pendente — inscrição {cinco[1].protocolo}" in corpo
    assert "Voltar à Mesa" in corpo


def test_a_proxima_pula_o_que_ja_foi_concluido(como_joao, cenario, cinco):
    concluir_como(cenario, "joao", cinco[1])

    corpo = como_joao.get(
        reverse(
            "interface:mesa-inscricao",
            args=[cenario["edital"].id, cenario["etapa"], cinco[0].id],
        )
    ).content.decode()

    assert f"inscrição {cinco[2].protocolo}" in corpo
    assert f"Próxima pendente — inscrição {cinco[1].protocolo}" not in corpo


def test_o_foco_comeca_no_campo_de_pontuacao(como_joao, cenario, cinco):
    """Um clique por inscrição só para poder digitar é caminho, e não trabalho."""
    corpo = como_joao.get(
        reverse(
            "interface:mesa-inscricao",
            args=[cenario["edital"].id, cenario["etapa"], cinco[0].id],
        )
    ).content.decode()

    assert re.search(r'id="pontuacao"[^>]*autofocus', corpo, re.S) or re.search(
        r'autofocus[^>]*id="pontuacao"', corpo, re.S
    )


def test_o_aviso_tem_prioridade_sobre_o_foco_do_campo(como_joao, cenario, cinco):
    """Quando há recusa para ler, é ela que precisa do foco — e não o campo."""
    como_joao.post(
        reverse(
            "interface:mesa-avaliacao-concluir",
            args=[cenario["edital"].id, cenario["etapa"], cinco[0].id],
        ),
        {"pontuacao": "50", "parecer": "", "expected_revision": "1", "versao_reconhecida": "x"},
    )
    corpo = como_joao.get(
        reverse(
            "interface:mesa-inscricao",
            args=[cenario["edital"].id, cenario["etapa"], cinco[0].id],
        )
    ).content.decode()

    assert 'class="erro"' in corpo
    assert not re.search(r'id="pontuacao"[^>]*autofocus', corpo, re.S)


def test_concluir_leva_a_proxima_pendente(como_joao, cenario, cinco):
    """Concluir e seguir eram dois cliques, cobrados uma vez por inscrição.

    Numa Mesa de 230 são 230 cliques para dizer “continuo trabalhando”.
    """
    from processo_seletivo.publicacoes.application.selectors import effective_version

    versao = effective_version(edital_id=cenario["edital"].id)
    resposta = como_joao.post(
        reverse(
            "interface:mesa-avaliacao-concluir",
            args=[cenario["edital"].id, cenario["etapa"], cinco[0].id],
        ),
        {
            "pontuacao": "88",
            "parecer": "Atende.",
            "expected_revision": "1",
            "versao_reconhecida": str(versao.id),
        },
    )

    assert resposta.status_code == 302
    assert str(cinco[1].id) in resposta["Location"]

    corpo = como_joao.get(resposta["Location"]).content.decode()
    assert f"Avaliação da inscrição {cinco[0].protocolo} concluída" in corpo
    assert f"Inscrição {cinco[1].protocolo}" in corpo


def test_a_ultima_conclusao_diz_que_o_trabalho_acabou(como_joao, cenario, cinco):
    """Sem próxima, a tela não finge que há: ela diz que não há mais pendente."""
    from processo_seletivo.publicacoes.application.selectors import effective_version

    for inscricao in cinco[1:]:
        concluir_como(cenario, "joao", inscricao)
    versao = effective_version(edital_id=cenario["edital"].id)

    resposta = como_joao.post(
        reverse(
            "interface:mesa-avaliacao-concluir",
            args=[cenario["edital"].id, cenario["etapa"], cinco[0].id],
        ),
        {
            "pontuacao": "88",
            "parecer": "Atende.",
            "expected_revision": "1",
            "versao_reconhecida": str(versao.id),
        },
        follow=True,
    )

    assert "Não há mais inscrições pendentes suas nesta Etapa." in resposta.content.decode()


def test_salvar_rascunho_nao_leva_a_lugar_nenhum(como_joao, cenario, cinco):
    """Só concluir avança. Quem salva sem concluir está no meio do trabalho, e fica onde está."""
    resposta = como_joao.post(
        reverse(
            "interface:mesa-avaliacao-gravar",
            args=[cenario["edital"].id, cenario["etapa"], cinco[0].id],
        ),
        {"pontuacao": "70", "parecer": "Em análise.", "expected_revision": "1"},
    )

    assert str(cinco[0].id) in resposta["Location"]


def test_concluir_nao_empilha_duas_faixas_dizendo_o_mesmo(como_joao, cenario, cinco):
    """“Avaliação concluída.” e “Avaliação concluída em …” apareciam uma sobre a outra."""
    concluir_como(cenario, "joao", cinco[0])

    corpo = como_joao.get(
        reverse(
            "interface:mesa-inscricao",
            args=[cenario["edital"].id, cenario["etapa"], cinco[0].id],
        )
    ).content.decode()

    assert corpo.count("Avaliação concluída") == 1
