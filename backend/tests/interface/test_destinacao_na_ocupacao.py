"""A vaga sem quem a ocupe nas três telas, a conferência e a recusa a quem não pode (155, T030).

O cenário é a V-1: o único cotista PPI é chamado e desiste, e a reserva fica sem quem a ocupe.
**O prazo de recurso é dado como encerrado** substituindo a conta da janela: o marco do sorteio
declara prazo computável, e ele corre da publicação — sem isso, toda tela diria, com razão, que o
prazo impede (o caso tem teste próprio, em `test_condicao_do_esgotamento.py`).

**Duas situações, e só uma tem ato.** No Edital silente, a declaração de vaga não preenchida, com
a Retificação ao lado. Onde o Edital declara a reversão, a apuração a aplica pela regra de antes da
`155`, e na V-1 ela não cede: a tela diz por que a vaga não sai e qual é o próximo passo, sem botão
— a destinação por ato próprio ficou para a próxima entrega (`claude/155-destinacao-completa`).

**SC-2101**: nenhuma tela oferece o ato que o comando recusaria — o botão só aparece com a vaga
disponível, e a vaga impedida diz o impedimento no lugar dele.
"""

import pytest
from django.urls import reverse

from processo_seletivo.ocupacao.domain import nomes
from processo_seletivo.ocupacao.models import MovimentoDeVaga, VagaNaoPreenchida
from tests.fixtures.sorteio import MARCO
from tests.integration.ocupacao.test_condicao_do_esgotamento import publicar_definitivo
from tests.interface.conftest import identificar

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.integration]

#: O ato que esta entrega não tem: nenhuma tela o oferece.
DESTINAR = "Destinar à ampla concorrência"
SILENTE = "Este Edital não declara o que acontece com a vaga reservada não preenchida."
DECLARAR = "Declarar a vaga não preenchida"


@pytest.fixture
def prazo_encerrado(monkeypatch):
    monkeypatch.setattr(
        "processo_seletivo.divulgacao.domain.publicabilidade.janela_aberta_ate",
        lambda **_: None,
    )


def pela_desistencia(gestor, api_client, manager_headers, process_payload, prefixo, *, reversao):
    """A V-1 pelo caminho do ator: a cotista é chamada e desiste, e o desfecho emite a apuração.

    **Todos habilitados na Etapa que o corte governa**: com a Etapa por consolidar, o Centro diz que
    a convocação espera por ela, e o ramo da vaga sem quem a ocupe nunca é lido. **A espécie da
    chamada é a que a posição determina** (`especie=None`): supor que a cotista é titular tornaria o
    caso dependente da ordem que o sorteio produz.
    """
    from processo_seletivo.convocacao.domain import nomes as nomes_da_conducao
    from tests.fixtures.ocupacao_sorteada import LISTA_PPI as PPI
    from tests.fixtures.ocupacao_sorteada import certame_sorteado_com_quadro
    from tests.integration.convocacao.test_suplencia import chamar, responder
    from tests.integration.ocupacao.test_concomitancia import apurar, emitir_cortes, habilitar
    from tests.integration.ocupacao.test_condicao_do_esgotamento import sem_concomitancia

    certame = certame_sorteado_com_quadro(
        gestor,
        api_client,
        manager_headers,
        process_payload,
        prefixo=prefixo,
        com_corte=True,
        quantos=8,
        geral=1,
        reversao=reversao,
    )
    cotista = certame["cotista_ppi"]
    emitir_cortes(certame, gestor)
    habilitar(certame, certame["inscricoes"])
    apurar(certame, gestor, chave=f"{prefixo}-ampla")
    sem_concomitancia(certame, cotista)
    apurar(certame, gestor, chave=f"{prefixo}-ampla-2", motivo="Saída da ampla registrada")
    apurar(certame, gestor, lista_id=PPI, chave=f"{prefixo}-ppi")
    chamada = chamar(
        certame, gestor, cotista.id, lista_id=PPI, chave=f"{prefixo}-chamar", especie=None
    )
    responder(
        certame, gestor, chamada["id"], nomes_da_conducao.DESISTENCIA_EXPRESSA, f"{prefixo}-sai"
    )
    return certame


def ocupacao(client, certame):
    resposta = client.get(reverse("interface:ocupacao", args=[certame["edital"].id, MARCO]))
    assert resposta.status_code == 200
    return resposta.content.decode()


def assinatura_de(pagina):
    marcador = 'name="leitura" value="'
    inicio = pagina.index(marcador) + len(marcador)
    return pagina[inicio : pagina.index('"', inicio)]


def secao_da_ppi(pagina):
    inicio = pagina.index("Pretos, pardos e indígenas (PPI)</h2>")
    return pagina[inicio : pagina.index("</section>", inicio)]


def centro(client, certame):
    return client.get(
        reverse("interface:pagina-anterior", args=[certame["edital"].id])
    ).content.decode()


def declarar_pela_tela(client, certame, **extra):
    from tests.fixtures.ocupacao_sorteada import LISTA_PPI as PPI

    return client.post(
        reverse("interface:declarar-nao-preenchida", args=[certame["edital"].id, MARCO]),
        {"lista": PPI, "chave": "tela-np-155-chave", **extra},
    )


# --- A reversão declarada que a apuração não aplica: a vaga não sai, e a tela diz por quê ---------


@pytest.fixture
def reversao_que_nao_sai(
    db, gestor, api_client, manager_headers, process_payload, raiz_de_arquivos
):
    """A V-1 sob a reversão por esgotamento: a apuração conta a posição de quem desistiu e não
    cede, e o resultado definitivo está publicado."""
    certame = pela_desistencia(
        gestor,
        api_client,
        manager_headers,
        process_payload,
        "tela-rev-155",
        reversao=nomes.REVERSAO_POR_ESGOTAMENTO,
    )
    publicar_definitivo(certame)
    return certame


class TestAVagaQueNaoSai:
    def test_a_ocupacao_diz_a_regra_e_o_proximo_passo_sem_botao(
        self, client, seletor_ligado, reversao_que_nao_sai, prazo_encerrado
    ):
        """V-1, FR-6303, FR-6327, UX-600: a lista, a quantidade, a frase publicada e a regra da
        reversão que vale nesta entrega — e nenhum ato, nem a destinação, nem a declaração."""
        identificar(client, "carlos", ["gestor"])

        secao = secao_da_ppi(ocupacao(client, reversao_que_nao_sai))

        assert "1 vaga da lista «Pretos, pardos e indígenas" in secao
        assert "ninguém mais na ordem desta lista pode ocupá-la" in secao
        assert "O Edital declara: «" in secao
        assert "A reversão declarada é aplicada pela apuração desta lista" in secao
        assert "fica para uma próxima entrega" in secao
        assert "ON_EXHAUSTION" not in secao
        assert DESTINAR not in secao
        assert DECLARAR + "</button>" not in secao
        assert "Pedir a faixa seguinte" not in secao
        assert MovimentoDeVaga.objects.count() == 0

    def test_o_centro_diz_a_mesma_frase_sem_ato(
        self, client, seletor_ligado, reversao_que_nao_sai, prazo_encerrado
    ):
        identificar(client, "carlos", ["gestor"])

        corpo = centro(client, reversao_que_nao_sai)

        assert "A reversão declarada é aplicada pela apuração desta lista" in corpo
        assert DESTINAR not in corpo
        assert DECLARAR not in corpo

    def test_a_convocacao_cita_a_situacao_com_a_fila_vazia(
        self, client, seletor_ligado, reversao_que_nao_sai, prazo_encerrado
    ):
        from tests.fixtures.ocupacao_sorteada import LISTA_PPI as PPI

        identificar(client, "carlos", ["gestor"])

        corpo = client.get(
            reverse("interface:convocacao", args=[reversao_que_nao_sai["edital"].id, MARCO])
            + f"?lista={PPI}"
        ).content.decode()

        assert "não há mais quem chamar na fila" in corpo
        assert "A reversão declarada é aplicada pela apuração desta lista" in corpo

    def test_a_declaracao_pedida_assim_mesmo_e_recusada(
        self, client, seletor_ligado, reversao_que_nao_sai, prazo_encerrado
    ):
        """FR-6327: o pedido que a tela não oferece volta à ocupação com a razão dita."""
        identificar(client, "carlos", ["gestor"])

        resposta = declarar_pela_tela(client, reversao_que_nao_sai)

        assert resposta.status_code == 302
        pagina = ocupacao(client, reversao_que_nao_sai)
        assert "Não foi possível declarar a vaga não preenchida:" in pagina
        assert "A reversão é aplicada pela apuração da lista" in pagina
        assert VagaNaoPreenchida.objects.count() == 0


def test_por_saldo_a_apuracao_cede_e_nenhuma_tela_oferece_ato(
    client,
    seletor_ligado,
    db,
    gestor,
    api_client,
    manager_headers,
    process_payload,
    raiz_de_arquivos,
):
    """Sob a reversão por saldo, a apuração cede a vaga, como antes da `155`: o desfecho não a
    emite (FR-885 da `050`), e a reserva não tem vaga sem quem a ocupe a dizer — nem frase, nem
    botão."""
    certame = pela_desistencia(
        gestor,
        api_client,
        manager_headers,
        process_payload,
        "tela-saldo-155",
        reversao=nomes.REVERSAO_POR_SALDO,
    )
    identificar(client, "carlos", ["gestor"])

    secao = secao_da_ppi(ocupacao(client, certame))

    assert DESTINAR not in secao
    assert DECLARAR not in secao
    assert "sem quem a ocupe" not in secao


# --- O Edital silente, a não preenchida e o desfazimento dela (155, T034, T037) ------------------


@pytest.fixture
def silente(db, gestor, api_client, manager_headers, process_payload, raiz_de_arquivos):
    """O C09: sem reversão declarada, a lista PPI esgotada e o resultado definitivo publicado."""
    certame = pela_desistencia(
        gestor, api_client, manager_headers, process_payload, "tela-np-155", reversao=None
    )
    publicar_definitivo(certame)
    return certame


class TestOEditalSilente:
    def test_a_ocupacao_diz_a_frase_e_os_dois_caminhos(
        self, client, seletor_ligado, silente, prazo_encerrado
    ):
        """FR-6321, US2.1: a frase, a Retificação e a declaração — e nenhuma destinação."""
        identificar(client, "carlos", ["gestor", "elaborador"])

        pagina = ocupacao(client, silente)

        assert SILENTE in pagina
        assert DECLARAR in pagina
        assert "abrir a Retificação deste Edital" in pagina
        assert DESTINAR not in pagina, "FR-6320: sem reversão declarada, nada vai à ampla"
        # Só a seção da PPP: a faixa de outra lista depende de quem o sorteio pôs onde.
        assert "Pedir a faixa seguinte" not in secao_da_ppi(pagina)

    def test_quem_nao_retifica_ve_o_caminho_nomeado(
        self, client, seletor_ligado, silente, prazo_encerrado
    ):
        """FR-6321: a fase admite a Retificação, e quem apura sem elaborar vê o caminho nomeado.

        O defeito que este caso prende: a condição lia a permissão de quem olha junto com a fase, e
        a presidência do C09 — que apura e não elabora — via só a declaração de não preenchida,
        como se a Retificação não existisse.
        """
        identificar(client, "carlos", ["gestor"])

        pagina = ocupacao(client, silente)

        assert SILENTE in pagina
        assert "que é ato de quem elabora o Edital" in pagina
        assert "abrir a Retificação deste Edital" not in pagina

    def test_o_centro_tem_um_ato_por_caminho(
        self, client, seletor_ligado, silente, prazo_encerrado
    ):
        identificar(client, "carlos", ["gestor", "elaborador"])

        corpo = centro(client, silente)

        assert DECLARAR in corpo
        assert "Retificar o Edital para declarar a reversão" in corpo
        assert DESTINAR not in corpo
        assert "Ocupar a vaga" not in corpo

    def test_a_convocacao_diz_a_mesma_situacao(
        self, client, seletor_ligado, silente, prazo_encerrado
    ):
        from tests.fixtures.ocupacao_sorteada import LISTA_PPI as PPI

        identificar(client, "carlos", ["gestor"])

        corpo = client.get(
            reverse("interface:convocacao", args=[silente["edital"].id, MARCO]) + f"?lista={PPI}"
        ).content.decode()

        assert SILENTE in corpo
        assert "A declaração de vaga não preenchida é ato da ocupação" in corpo

    def test_sem_o_definitivo_o_impedimento_e_dito(
        self,
        client,
        seletor_ligado,
        db,
        gestor,
        api_client,
        manager_headers,
        process_payload,
        raiz_de_arquivos,
    ):
        certame = pela_desistencia(
            gestor, api_client, manager_headers, process_payload, "tela-np-imp", reversao=None
        )
        identificar(client, "carlos", ["gestor"])

        pagina = ocupacao(client, certame)

        assert "a declaração de vaga não preenchida ainda não cabe" in pagina
        assert "o resultado deste marco ainda não foi divulgado" in pagina
        assert DECLARAR + "</button>" not in pagina, "SC-2101: o impedimento no lugar do ato"


class TestADeclaracaoPelaTela:
    def test_sem_fundamento_a_conferencia_volta_com_a_recusa(
        self, client, seletor_ligado, silente, prazo_encerrado
    ):
        """US2.2: o fundamento é obrigatório, e nada é gravado."""
        identificar(client, "carlos", ["gestor"])
        conferencia = declarar_pela_tela(client, silente).content.decode()
        assert "Conferir a declaração de 1 vaga não preenchida" in conferencia
        assert 'name="fundamento" rows="3"' in conferencia

        resposta = declarar_pela_tela(
            client, silente, confirmar="1", leitura=assinatura_de(conferencia), fundamento=" "
        )

        assert resposta.status_code == 200
        assert "exige fundamento escrito" in resposta.content.decode()
        assert VagaNaoPreenchida.objects.count() == 0

    def test_com_fundamento_grava_e_o_centro_nao_tem_mais_providencia(
        self, client, seletor_ligado, silente, prazo_encerrado
    ):
        """US2.3, SC-2100: um estado final com uma confirmação, e a fase sem providência da PPP."""
        identificar(client, "carlos", ["gestor"])
        conferencia = declarar_pela_tela(client, silente).content.decode()

        resposta = declarar_pela_tela(
            client,
            silente,
            confirmar="1",
            leitura=assinatura_de(conferencia),
            fundamento="O Edital não declara reversão, e ninguém concorre pela cota.",
        )

        assert resposta.status_code == 302
        assert VagaNaoPreenchida.objects.count() == 1
        pagina = ocupacao(client, silente)
        assert "Vaga declarada não preenchida: 1 vaga." in pagina
        assert "1 vaga declarada não preenchida. Fundamento: O Edital não declara" in pagina
        assert "Desfazer esta declaração" in pagina
        assert DECLARAR + "</button>" not in pagina
        corpo = centro(client, silente)
        assert DECLARAR not in corpo and "Ocupar a vaga" not in corpo


class TestQuemNaoApura:
    def test_le_a_situacao_e_nao_recebe_o_ato(
        self, client, seletor_ligado, silente, prazo_encerrado
    ):
        identificar(client, "aud", ["auditor"])

        pagina = ocupacao(client, silente)

        assert SILENTE in pagina
        assert DECLARAR + "</button>" not in pagina
        assert "é ato de quem apura a ocupação deste marco" in pagina

    def test_e_recusado_e_nada_e_gravado(self, client, seletor_ligado, silente, prazo_encerrado):
        """FR-6341: a mesma autoridade da emissão, negada por padrão."""
        identificar(client, "aud", ["auditor"])

        resposta = declarar_pela_tela(
            client, silente, confirmar="1", leitura="qualquer", fundamento="Sem autoridade."
        )

        assert resposta.status_code == 403
        assert VagaNaoPreenchida.objects.count() == 0


class TestODesfazimentoPelaTela:
    FUNDAMENTO = "O Edital não declara reversão, e ninguém concorre pela cota."

    def declarar(self, client, certame):
        conferencia = declarar_pela_tela(client, certame).content.decode()
        declarar_pela_tela(
            client,
            certame,
            confirmar="1",
            leitura=assinatura_de(conferencia),
            fundamento=self.FUNDAMENTO,
        )
        return VagaNaoPreenchida.objects.get()

    def desfazer(self, client, certame, declaracao, **extra):
        return client.post(
            reverse("interface:desfazer-nao-preenchida", args=[certame["edital"].id, MARCO]),
            {"ato": str(declaracao.id), "chave": "tela-desf-np-155", **extra},
        )

    def test_sem_chamada_dependente_desfaz_e_os_dois_ficam(
        self, client, seletor_ligado, silente, prazo_encerrado
    ):
        """FR-6334, FR-6336: o ato contrário cita o original, e os dois continuam legíveis."""
        identificar(client, "carlos", ["gestor"])
        declaracao = self.declarar(client, silente)
        assert "Desfazer esta declaração" in ocupacao(client, silente)
        conferencia = self.desfazer(client, silente, declaracao).content.decode()
        assert "Desfazer a declaração de 1 vaga não preenchida" in conferencia
        assert "pessoa chamada para esta vaga" not in conferencia

        resposta = self.desfazer(
            client,
            silente,
            declaracao,
            confirmar="1",
            leitura=assinatura_de(conferencia),
            motivo="Declarada por engano.",
        )

        assert resposta.status_code == 302
        assert VagaNaoPreenchida.objects.count() == 2
        pagina = ocupacao(client, silente)
        assert "Declaração de vaga não preenchida desfeita: 1 vaga volta a contar" in pagina
        assert "declaração desfeita: 1 vaga volta a contar como a ocupar" in pagina
        assert "Desfazer esta declaração" not in pagina

    def test_com_chamada_dependente_a_tela_nomeia_e_a_trilha_registra(
        self, client, seletor_ligado, silente, prazo_encerrado, monkeypatch
    ):
        """US6.2, FR-6335: a tela mostra o impedimento, sem a ação; o pedido direto é recusado e
        fica na trilha.

        **A chamada dependente chega pela composição da interface**, que é o que a tela e o ato
        perguntam; a declaração deixa a reserva sem vaga a ocupar, e uma chamada que a lesse de
        verdade pediria outro cenário. O caminho da condução até a pergunta tem o caso dele no
        comando (`test_desfazimento_da_nao_preenchida.py`).

        A primeira versão deixava o botão visível para que a recusa acontecesse; o usuário recusou
        esse desenho em 12/11/2026 — ação oferecida só para ser negada contraria a FR-6302.
        """
        from processo_seletivo.auditoria.models import RegistroAuditoria
        from processo_seletivo.interface import destinacao_da_vaga
        from processo_seletivo.ocupacao.application import destinacao

        identificar(client, "carlos", ["gestor"])
        declaracao = self.declarar(client, silente)
        chamada = {"id": "00000000-0000-4000-8000-00000000c155", "rotulo": "P-0701 — Fulana"}

        def dependentes(**pergunta):
            return [{**chamada, "ocupa": False}] if pergunta.get("nao_preenchida_id") else []

        monkeypatch.setattr(destinacao_da_vaga, "chamadas_dependentes", dependentes)

        pagina = ocupacao(client, silente)
        assert "Esta declaração não se desfaz agora" in pagina
        assert "P-0701 — Fulana foi chamada para ela" in pagina
        assert "Desfazer esta declaração" not in pagina, (
            "FR-6302: sem ação que terminaria em recusa"
        )

        conferencia = self.desfazer(client, silente, declaracao).content.decode()
        assert "O desfazimento não cabe agora" in conferencia
        assert "a chamada precisa do seu desfecho antes" in conferencia
        assert 'name="confirmar"' not in conferencia, "a conferência não oferece o ato"

        # **O pedido enviado direto**, sem a tela: o comando recusa e registra (FR-6335).
        leitura = destinacao.previa_do_desfazimento_da_nao_preenchida(
            edital=silente["edital"],
            declaracao_id=str(declaracao.id),
            chamadas_dependentes=dependentes,
        )["assinatura"]
        resposta = self.desfazer(
            client,
            silente,
            declaracao,
            confirmar="1",
            leitura=leitura,
            motivo="Declarada por engano.",
        )

        assert resposta.status_code == 302
        pagina = ocupacao(client, silente)
        assert "Não foi possível desfazer a declaração de vaga não preenchida:" in pagina
        assert "precisa do seu desfecho antes" in pagina
        assert VagaNaoPreenchida.objects.count() == 1, "nada desfeito"
        evento = RegistroAuditoria.objects.get(operation="OCUPACAO_DESFAZIMENTO_IMPEDIDO")
        assert evento.detalhe["chamadas"] == [{**chamada, "ocupa": False}]
