"""A destinação da vaga nas três telas, a conferência e a recusa a quem não pode (155, T030).

O cenário é a V-1: o único cotista PPI desiste, o resultado definitivo está publicado, e a reserva
fica sem quem a ocupe. **O prazo de recurso é dado como encerrado** substituindo a conta da janela:
o marco do sorteio declara prazo computável, e ele corre da publicação — sem isso, toda tela diria,
com razão, que o prazo impede (o caso tem teste próprio, em `test_condicao_do_esgotamento.py`).

**SC-2101**: nenhuma tela oferece o ato que o comando recusaria — o botão só aparece com a vaga
disponível, e a vaga impedida diz o impedimento no lugar dele.
"""

import pytest
from django.urls import reverse

from processo_seletivo.ocupacao.domain import nomes
from processo_seletivo.ocupacao.models import MovimentoDeVaga
from tests.fixtures.sorteio import MARCO
from tests.integration.ocupacao.test_condicao_do_esgotamento import publicar_definitivo
from tests.interface.conftest import identificar

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.integration]

BOTAO = "Destinar à ampla concorrência"


@pytest.fixture
def prazo_encerrado(monkeypatch):
    monkeypatch.setattr(
        "processo_seletivo.divulgacao.domain.publicabilidade.janela_aberta_ate",
        lambda **_: None,
    )


def pela_desistencia(gestor, api_client, manager_headers, process_payload, prefixo, *, reversao):
    """A V-1 pelo caminho do ator: a cotista é chamada e desiste, e o desfecho emite a apuração.

    **Todos habilitados na Etapa que o corte governa**: com a Etapa por consolidar, o Centro diz que
    a convocação espera por ela, e o ramo da vaga sem quem a ocupe nunca é lido.
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
    chamada = chamar(certame, gestor, cotista.id, lista_id=PPI, chave=f"{prefixo}-chamar")
    responder(
        certame, gestor, chamada["id"], nomes_da_conducao.DESISTENCIA_EXPRESSA, f"{prefixo}-sai"
    )
    return certame


@pytest.fixture
def esgotada(db, gestor, api_client, manager_headers, process_payload, raiz_de_arquivos):
    return pela_desistencia(
        gestor,
        api_client,
        manager_headers,
        process_payload,
        "tela-155",
        reversao=nomes.REVERSAO_POR_ESGOTAMENTO,
    )


@pytest.fixture
def disponivel(esgotada, prazo_encerrado):
    publicar_definitivo(esgotada)
    return esgotada


def ocupacao(client, certame):
    resposta = client.get(reverse("interface:ocupacao", args=[certame["edital"].id, MARCO]))
    assert resposta.status_code == 200
    return resposta.content.decode()


def conferir(client, certame, **extra):
    from tests.fixtures.ocupacao_sorteada import LISTA_PPI as PPI

    return client.post(
        reverse("interface:destinar-vaga", args=[certame["edital"].id, MARCO]),
        {"lista": PPI, "chave": "tela-155-chave", **extra},
    )


def assinatura_de(pagina):
    marcador = 'name="leitura" value="'
    inicio = pagina.index(marcador) + len(marcador)
    return pagina[inicio : pagina.index('"', inicio)]


class TestOcupacao:
    def test_a_situacao_diz_a_lista_a_quantidade_e_o_que_o_edital_declara(
        self, client, seletor_ligado, disponivel
    ):
        """UX-600, em palavras e sem código de espécie."""
        identificar(client, "carlos", ["gestor"])

        pagina = ocupacao(client, disponivel)

        assert "1 vaga da Pretos, pardos e indígenas" in pagina
        assert "sem quem a ocupe" in pagina
        assert "O Edital declara: «" in pagina
        assert "ON_EXHAUSTION" not in pagina
        assert BOTAO in pagina

    def test_quem_audita_le_a_situacao_e_nao_recebe_o_ato(self, client, seletor_ligado, disponivel):
        identificar(client, "aud", ["auditor"])

        pagina = ocupacao(client, disponivel)

        assert "sem quem a ocupe" in pagina
        assert BOTAO not in pagina
        assert "é ato de quem apura a ocupação deste marco" in pagina

    def test_impedida_diz_o_impedimento_e_nao_oferece_o_ato(self, client, seletor_ligado, esgotada):
        """SC-2101, FR-6303: sem o definitivo, o impedimento no lugar do botão."""
        identificar(client, "carlos", ["gestor"])

        pagina = ocupacao(client, esgotada)

        assert "a destinação à ampla concorrência ainda não cabe" in pagina
        assert "o resultado deste marco ainda não foi divulgado" in pagina
        assert BOTAO not in pagina


class TestConferencia:
    def test_a_conferencia_diz_tudo_antes_e_nao_grava(self, client, seletor_ligado, disponivel):
        """FR-6309 e UX-601: origem, destino, quantidade, gatilho, frase, versão e efeito."""
        identificar(client, "carlos", ["gestor"])

        pagina = conferir(client, disponivel).content.decode()

        assert "Conferir a destinação de 1 vaga à ampla concorrência" in pagina
        assert "por esgotamento" in pagina
        assert "O que o Edital declara" in pagina and "Versão do Edital lida" in pagina
        assert "Efetivas na ampla concorrência depois" in pagina
        assert "passar antes por outras cotas" in pagina, "o lembrete da FR-6309"
        assert MovimentoDeVaga.objects.count() == 0

    def test_confirmar_grava_e_volta_a_ocupacao(self, client, seletor_ligado, disponivel):
        identificar(client, "carlos", ["gestor"])
        conferencia = conferir(client, disponivel).content.decode()

        resposta = conferir(client, disponivel, confirmar="1", leitura=assinatura_de(conferencia))

        assert resposta.status_code == 302
        assert MovimentoDeVaga.objects.count() == 1
        pagina = ocupacao(client, disponivel)
        assert "Vaga destinada à ampla concorrência: 1 vaga." in pagina
        assert "já foi destinada à ampla concorrência" in pagina
        assert BOTAO not in pagina, "nenhum ato destina de novo"

    def test_a_recusa_volta_a_ocupacao_dita(self, client, seletor_ligado, esgotada):
        identificar(client, "carlos", ["gestor"])

        resposta = conferir(client, esgotada)

        assert resposta.status_code == 302
        pagina = ocupacao(client, esgotada)
        assert "Não foi possível destinar a vaga:" in pagina
        assert MovimentoDeVaga.objects.count() == 0

    def test_quem_nao_apura_e_recusado_e_nada_e_gravado(self, client, seletor_ligado, disponivel):
        """FR-6341: a mesma autoridade da emissão, negada por padrão."""
        identificar(client, "aud", ["auditor"])

        resposta = conferir(client, disponivel, confirmar="1", leitura="qualquer")

        assert resposta.status_code == 403
        assert MovimentoDeVaga.objects.count() == 0


class TestOutrasTelas:
    def test_o_centro_leva_ao_caminho_disponivel(self, client, seletor_ligado, disponivel):
        """UX-602: no lugar de "Ocupar a vaga — impedida", o caminho disponível, com link."""
        identificar(client, "carlos", ["gestor"])

        corpo = client.get(
            reverse("interface:pagina-anterior", args=[disponivel["edital"].id])
        ).content.decode()

        assert BOTAO in corpo
        assert "Ocupar a vaga" not in corpo

    def test_o_centro_nomeia_o_impedimento(self, client, seletor_ligado, esgotada):
        identificar(client, "carlos", ["gestor"])

        corpo = client.get(
            reverse("interface:pagina-anterior", args=[esgotada["edital"].id])
        ).content.decode()

        assert "o resultado deste marco ainda não foi divulgado" in corpo
        assert "Ocupar a vaga" not in corpo

    def test_a_convocacao_cita_a_situacao_com_a_fila_vazia(
        self, client, seletor_ligado, disponivel
    ):
        from tests.fixtures.ocupacao_sorteada import LISTA_PPI as PPI

        identificar(client, "carlos", ["gestor"])

        corpo = client.get(
            reverse("interface:convocacao", args=[disponivel["edital"].id, MARCO]) + f"?lista={PPI}"
        ).content.decode()

        assert "não há mais quem chamar na fila" in corpo
        assert "A destinação à ampla concorrência é ato da ocupação" in corpo


def test_por_saldo_nenhuma_tela_muda(
    client,
    seletor_ligado,
    db,
    gestor,
    api_client,
    manager_headers,
    process_payload,
    raiz_de_arquivos,
):
    """R-010: sob a reversão por saldo, nada novo — nem frase, nem botão."""
    certame = pela_desistencia(
        gestor,
        api_client,
        manager_headers,
        process_payload,
        "tela-saldo-155",
        reversao=nomes.REVERSAO_POR_SALDO,
    )
    identificar(client, "carlos", ["gestor"])

    pagina = ocupacao(client, certame)

    assert BOTAO not in pagina
    assert "sem quem a ocupe" not in pagina
    assert "destinação" not in pagina.lower()


# --- O Edital silente, a não preenchida e os desfazimentos (155, T034, T037) ---------------------

SILENTE = "Este Edital não declara o que acontece com a vaga reservada não preenchida."
DECLARAR = "Declarar a vaga não preenchida"


@pytest.fixture
def silente(db, gestor, api_client, manager_headers, process_payload, raiz_de_arquivos):
    """O C09: sem reversão declarada, a lista PPI esgotada e o resultado definitivo publicado."""
    certame = pela_desistencia(
        gestor, api_client, manager_headers, process_payload, "tela-np-155", reversao=None
    )
    publicar_definitivo(certame)
    return certame


def declarar_pela_tela(client, certame, **extra):
    from tests.fixtures.ocupacao_sorteada import LISTA_PPI as PPI

    return client.post(
        reverse("interface:declarar-nao-preenchida", args=[certame["edital"].id, MARCO]),
        {"lista": PPI, "chave": "tela-np-155-chave", **extra},
    )


def secao_da_ppi(pagina):
    inicio = pagina.index("Pretos, pardos e indígenas (PPI)</h2>")
    return pagina[inicio : pagina.index("</section>", inicio)]


def centro(client, certame):
    return client.get(
        reverse("interface:pagina-anterior", args=[certame["edital"].id])
    ).content.decode()


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
        assert BOTAO not in pagina, "FR-6320: sem reversão declarada, nada vai à ampla"
        # Só a seção da PPP: a faixa de outra lista depende de quem o sorteio pôs onde.
        assert "Pedir a faixa seguinte" not in secao_da_ppi(pagina)

    def test_o_centro_tem_um_ato_por_caminho(
        self, client, seletor_ligado, silente, prazo_encerrado
    ):
        identificar(client, "carlos", ["gestor", "elaborador"])

        corpo = centro(client, silente)

        assert DECLARAR in corpo
        assert "Retificar o Edital para declarar a reversão" in corpo
        assert BOTAO not in corpo
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
        from processo_seletivo.ocupacao.models import VagaNaoPreenchida

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
        from processo_seletivo.ocupacao.models import VagaNaoPreenchida

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


def chamar_na_ampla(certame, gestor, prefixo):
    """Chama quem a ampla alcança com a vaga recebida: a chamada lê o movimento (R-005)."""
    from processo_seletivo.convocacao.application import fluxo
    from tests.fixtures.edital import PROFILE_ID
    from tests.integration.convocacao.test_suplencia import chamar
    from tests.integration.ocupacao.test_concomitancia import apurar

    apurar(certame, gestor, chave=f"{prefixo}-ampla-recebe", motivo="Vaga recebida")
    pessoas = fluxo.previa_dos_titulares(
        edital=certame["edital"], perfil_id=PROFILE_ID, marco_id=MARCO
    )["pessoas"]
    assert pessoas, "a ampla tem quem chamar para a vaga recebida"
    return chamar(certame, gestor, pessoas[-1]["id"], lista_id=None, chave=f"{prefixo}-chamar-a")


class TestOsDesfazimentosPelaTela:
    def destinar(self, client, certame):
        conferencia = conferir(client, certame).content.decode()
        conferir(client, certame, confirmar="1", leitura=assinatura_de(conferencia))
        return MovimentoDeVaga.objects.get()

    def desfazer(self, client, certame, movimento, **extra):
        return client.post(
            reverse("interface:desfazer-destinacao", args=[certame["edital"].id, MARCO]),
            {"ato": str(movimento.id), "chave": "tela-desf-155", **extra},
        )

    def test_sem_chamada_dependente_desfaz_e_os_dois_ficam(
        self, client, seletor_ligado, disponivel
    ):
        identificar(client, "carlos", ["gestor"])
        movimento = self.destinar(client, disponivel)
        assert "Desfazer esta destinação" in ocupacao(client, disponivel)
        conferencia = self.desfazer(client, disponivel, movimento).content.decode()
        assert "Desfazer a destinação de 1 vaga" in conferencia
        assert "pessoa chamada para esta vaga" not in conferencia

        resposta = self.desfazer(
            client,
            disponivel,
            movimento,
            confirmar="1",
            leitura=assinatura_de(conferencia),
            motivo="Destinada por engano.",
        )

        assert resposta.status_code == 302
        assert MovimentoDeVaga.objects.count() == 2
        pagina = ocupacao(client, disponivel)
        assert "Destinação desfeita: 1 vaga volta à lista de origem." in pagina
        assert "desfazendo a destinação de" in pagina
        assert "Desfazer esta destinação" not in pagina

    def test_com_chamada_dependente_a_tela_nomeia_e_a_trilha_registra(
        self, client, seletor_ligado, disponivel, gestor
    ):
        """US6.2, FR-6335: a chamada nomeada, o desfecho antes, e o pedido recusado na trilha."""
        from processo_seletivo.auditoria.models import RegistroAuditoria

        identificar(client, "carlos", ["gestor"])
        movimento = self.destinar(client, disponivel)
        chamar_na_ampla(disponivel, gestor, "tela-desf-dep")
        conferencia = self.desfazer(client, disponivel, movimento).content.decode()
        assert "Há pessoa chamada para esta vaga" in conferencia
        assert "a chamada precisa do seu desfecho antes" in conferencia

        resposta = self.desfazer(
            client,
            disponivel,
            movimento,
            confirmar="1",
            leitura=assinatura_de(conferencia),
            motivo="Destinada por engano.",
        )

        assert resposta.status_code == 302
        pagina = ocupacao(client, disponivel)
        assert "Não foi possível desfazer a destinação:" in pagina
        assert "precisa do seu desfecho antes" in pagina
        assert MovimentoDeVaga.objects.count() == 1, "nada desfeito"
        evento = RegistroAuditoria.objects.get(operation="OCUPACAO_DESFAZIMENTO_IMPEDIDO")
        assert len(evento.detalhe["chamadas"]) == 1
