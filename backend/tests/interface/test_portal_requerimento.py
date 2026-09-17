"""A tela do Requerimento de Matrícula, no canal do candidato (029, `US1`, T029, T032, T038).

**Titularidade, e a recusa indistinguível de inexistente** (`FR-399`, `SC-131`). Quem não é titular
recebe exatamente o que receberia se o requerimento não existisse: distinguir as duas respostas
entregaria, a quem tentar identificadores em sequência, a informação de quais existem.

**E o Edital que não declara devolve 404 inclusive por rota digitada à mão** (`FR-371`, `SC-123`):
onde o certame não pede o requerimento, o recurso não existe — e não existe também para quem
adivinhar o endereço.
"""

import pytest
from django.urls import reverse
from django.utils import timezone

from processo_seletivo.identidade.models import CandidateIdentity
from processo_seletivo.portal.identidade import CHAVE_SESSAO
from processo_seletivo.requerimentos.application import preencher
from processo_seletivo.requerimentos.domain import nomes
from tests.fixtures.candidato import MARIA
from tests.fixtures.requerimento import DECLARACAO, pronta_para_enviar

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.integration]


def entrar_como(client, inscricao):
    registro, _ = CandidateIdentity.objects.get_or_create(
        subject=inscricao.identity_subject, defaults={"created_at": timezone.now()}
    )
    sessao = client.session
    sessao[CHAVE_SESSAO] = str(registro.pk)
    sessao.save()
    return registro


def endereco(inscricao):
    return reverse("portal:requerimento", args=[inscricao.id])


def abrir(client, inscricao):
    return client.get(endereco(inscricao))


class TestATitularidade:
    def test_a_titular_abre(self, client, selecao_na_inscricao, candidatos_registrados):
        inscricao = pronta_para_enviar(selecao_na_inscricao)
        entrar_como(client, inscricao)

        resposta = abrir(client, inscricao)

        assert resposta.status_code == 200
        assert "Requerimento de Matrícula" in resposta.content.decode()

    def test_quem_nao_e_titular_recebe_o_mesmo_que_receberia_se_nao_existisse(
        self, client, selecao_na_inscricao, candidatos_registrados
    ):
        """`SC-131`: a recusa e a inexistência são a mesma resposta, byte a byte no código."""
        import uuid

        inscricao = pronta_para_enviar(selecao_na_inscricao)
        outra, _ = CandidateIdentity.objects.get_or_create(
            subject="cand:outra-pessoa-029", defaults={"created_at": timezone.now()}
        )
        sessao = client.session
        sessao[CHAVE_SESSAO] = str(outra.pk)
        sessao.save()

        alheia = abrir(client, inscricao)
        inexistente = client.get(reverse("portal:requerimento", args=[uuid.uuid4()]))

        assert alheia.status_code == inexistente.status_code == 404

    def test_sem_sessao_nao_entrega_a_tela(
        self, client, selecao_na_inscricao, candidatos_registrados
    ):
        inscricao = pronta_para_enviar(selecao_na_inscricao)

        resposta = abrir(client, inscricao)

        assert resposta.status_code in (302, 404)
        assert "Nome da mãe" not in resposta.content.decode()


class TestOEditalQueNaoDeclara:
    def test_devolve_404_inclusive_por_rota_digitada_a_mao(
        self, client, selecao, candidatos_registrados
    ):
        """`FR-371`: o Edital sem declaração não tem requerimento nenhum a oferecer."""
        from processo_seletivo.inscricoes.application.rascunho import abrir_inscricao
        from tests.fixtures.candidato import PERFIL_DOCENTE

        inscricao = abrir_inscricao(
            identidade=MARIA, edital_id=selecao.id, profile_id=PERFIL_DOCENTE
        )
        entrar_como(client, inscricao)

        assert abrir(client, inscricao).status_code == 404


class TestARespostaEPrivada:
    def test_a_tela_nao_e_armazenavel_pelo_navegador(
        self, client, selecao_na_inscricao, candidatos_registrados
    ):
        """Filiação, documento e endereço numa página que o disco guarda é vazamento por cache."""
        inscricao = pronta_para_enviar(selecao_na_inscricao)
        entrar_como(client, inscricao)

        resposta = abrir(client, inscricao)

        assert "no-store" in resposta.headers.get("Cache-Control", "")


class TestOEstadoAindaIndisponivel:
    def test_na_convocacao_sem_chamada_a_tela_diz_que_ainda_nao_e_a_hora(
        self, client, selecao_na_convocacao, candidatos_registrados
    ):
        """*"Ainda não chegou a sua vez"* ≠ *"este certame não pede"* (`FR-405`, `SC-122`).

        O segundo caso é 404. Colapsá-los diria a quem ainda tem chance que ela não tem.
        """
        inscricao = pronta_para_enviar(selecao_na_convocacao)
        entrar_como(client, inscricao)

        corpo = abrir(client, inscricao).content.decode()

        assert "quando você for convocado" in corpo
        assert "Nome da mãe" not in corpo, "não há o que preencher antes da chamada"


class TestOPreenchimento:
    def test_a_tela_abre_o_rascunho_e_mostra_os_campos(
        self, client, selecao_na_inscricao, candidatos_registrados
    ):
        inscricao = pronta_para_enviar(selecao_na_inscricao)
        entrar_como(client, inscricao)

        corpo = abrir(client, inscricao).content.decode()

        assert 'id="nome_da_mae"' in corpo
        assert 'for="nome_da_mae"' in corpo
        assert preencher.vigente_de(inscricao) is not None, "o GET abriu o rascunho"

    def test_guardar_grava_sem_enviar(
        self, client, selecao_na_inscricao, candidatos_registrados, campos_declarados
    ):
        inscricao = pronta_para_enviar(selecao_na_inscricao)
        entrar_como(client, inscricao)
        abrir(client, inscricao)

        client.post(endereco(inscricao), {**campos_declarados, "guardar": "1"})

        vigente = preencher.vigente_de(inscricao)
        assert vigente.nome_da_mae == campos_declarados["nome_da_mae"]
        assert vigente.status == nomes.RASCUNHO, "guardar não é enviar"

    def test_enviar_sem_aceite_volta_com_a_recusa_e_nao_perde_o_preenchido(
        self, client, selecao_na_inscricao, candidatos_registrados, campos_declarados
    ):
        """`SC-128`: recusar não pode custar o que já estava certo."""
        inscricao = pronta_para_enviar(selecao_na_inscricao)
        entrar_como(client, inscricao)
        abrir(client, inscricao)

        resposta = client.post(
            endereco(inscricao),
            {
                **campos_declarados,
                "enviar": "1",
                "versao_exibida": str(preencher._conteudo(inscricao).id),
                "declaracao_exibida": DECLARACAO,
            },
        )

        corpo = resposta.content.decode()
        assert "aceitar a declaração" in corpo
        assert campos_declarados["nome_da_mae"] in corpo
        assert preencher.vigente_de(inscricao).status == nomes.RASCUNHO

    def test_enviar_com_aceite_conclui(
        self, client, selecao_na_inscricao, candidatos_registrados, campos_declarados
    ):
        inscricao = pronta_para_enviar(selecao_na_inscricao)
        entrar_como(client, inscricao)
        abrir(client, inscricao)

        client.post(
            endereco(inscricao),
            {
                **campos_declarados,
                "enviar": "1",
                "aceite": "1",
                "versao_exibida": str(preencher._conteudo(inscricao).id),
                "declaracao_exibida": DECLARACAO,
            },
        )

        assert preencher.vigente_de(inscricao).status == nomes.ENVIADO


class TestOEstadoEnviado:
    def test_o_enviado_fica_legivel_e_sem_campo_editavel(
        self, client, selecao_na_inscricao, candidatos_registrados, campos_declarados
    ):
        """`FR-406` e T032: a mesma promessa que a inscrição enviada já cumpre."""
        inscricao = pronta_para_enviar(selecao_na_inscricao)
        entrar_como(client, inscricao)
        abrir(client, inscricao)
        client.post(
            endereco(inscricao),
            {
                **campos_declarados,
                "enviar": "1",
                "aceite": "1",
                "versao_exibida": str(preencher._conteudo(inscricao).id),
                "declaracao_exibida": DECLARACAO,
            },
        )

        corpo = abrir(client, inscricao).content.decode()

        assert campos_declarados["nome_da_mae"] in corpo, "o que foi enviado continua legível"
        assert "Recebemos em" in corpo
        assert 'id="nome_da_mae"' not in corpo, "sem campo editável no estado enviado"
        assert "Enviar requerimento" not in corpo


class TestOCartaoNaTelaDaInscricao:
    """T031 e `UX-054`: o bloqueio **anunciado antes da tentativa**.

    Descobrir no clique de *Revisar inscrição* que faltava um requerimento inteiro é o defeito que
    a auditoria de UX deste repositório já nomeou — e aqui ele custaria vinte campos de surpresa.
    """

    def abrir_a_inscricao(self, client, inscricao):
        return client.get(reverse("portal:inscricao", args=[inscricao.id])).content.decode()

    def test_o_cartao_avisa_que_a_submissao_depende_do_requerimento(
        self, client, selecao_na_inscricao, candidatos_registrados
    ):
        inscricao = pronta_para_enviar(selecao_na_inscricao)
        entrar_como(client, inscricao)

        corpo = self.abrir_a_inscricao(client, inscricao)

        assert "Requerimento de Matrícula" in corpo
        # **A frase é longa de propósito.** `"sem ele"` casava com um comentário da folha de
        # estilo da base — a armadilha que este repositório já registrou: a varredura lê o
        # comentário, e a asserção passa por onde ninguém escreveu a regra.
        assert "não consegue enviar a inscrição sem ele" in corpo
        assert endereco(inscricao) in corpo, "e o cartão leva para onde se preenche"

    def test_enviado_o_cartao_passa_a_oferecer_a_conferencia(
        self, client, selecao_na_inscricao, candidatos_registrados, campos_declarados
    ):
        inscricao = pronta_para_enviar(selecao_na_inscricao)
        entrar_como(client, inscricao)
        abrir(client, inscricao)
        client.post(
            endereco(inscricao),
            {
                **campos_declarados,
                "enviar": "1",
                "aceite": "1",
                "versao_exibida": str(preencher._conteudo(inscricao).id),
                "declaracao_exibida": DECLARACAO,
            },
        )

        corpo = self.abrir_a_inscricao(client, inscricao)

        assert "Conferir o que você enviou" in corpo
        assert "não consegue enviar a inscrição sem ele" not in corpo

    def test_o_edital_que_coleta_na_convocacao_nao_mostra_cartao_nenhum(
        self, client, selecao_na_convocacao, candidatos_registrados
    ):
        """Exigir na inscrição o que só abre na convocação inverteria a ordem do certame."""
        inscricao = pronta_para_enviar(selecao_na_convocacao)
        entrar_como(client, inscricao)

        corpo = self.abrir_a_inscricao(client, inscricao)

        assert "Requerimento de Matrícula" not in corpo


class TestARotaDoCep:
    """T030: a consulta de CEP é do candidato autenticado, e o CEP vai no corpo.

    **Rota aberta seria um serviço de consulta de CEP hospedado por engano** — mantido e pago por
    esta instituição para quem quisesse usá-lo. E o CEP no endereço viajaria para log de servidor,
    histórico de navegador e cabeçalho de referência sem que ninguém decidisse isso (`FR-401`).
    """

    def rota(self):
        return reverse("portal:requerimento-cep")

    def test_o_endereco_e_fixo_e_nao_tem_onde_um_cep_caber(self):
        """A rota não aceita segmento variável: não há como um CEP acabar no caminho."""
        assert self.rota().endswith("/requerimento/cep")

    def test_sem_sessao_de_candidato_a_rota_nao_responde(self, client):
        resposta = client.post(self.rota(), {"cep": "29040860"})

        assert resposta.status_code == 404

    def test_com_sessao_o_cep_reconhecido_devolve_municipio_e_uf(
        self, client, selecao_na_inscricao, candidatos_registrados
    ):
        from processo_seletivo.requerimentos.models import ReferenciaDeCep

        ReferenciaDeCep.objects.create(
            cep="29040860",
            logradouro="Rua Barão de Mauá",
            bairro="Jucutuquara",
            municipio="Vitória",
            uf="ES",
            codigo_ibge="3205309",
        )
        inscricao = pronta_para_enviar(selecao_na_inscricao)
        entrar_como(client, inscricao)

        corpo = client.post(self.rota(), {"cep": "29.040-860"}).json()

        assert corpo == {
            "conferido": True,
            "logradouro": "Rua Barão de Mauá",
            "bairro": "Jucutuquara",
            "municipio": "Vitória",
            "uf": "ES",
        }
        assert "codigo_ibge" not in corpo, (
            "o IBGE é do servidor, e a tela não tem o que fazer com ele"
        )

    def test_cep_desconhecido_nao_e_erro(
        self, client, selecao_na_inscricao, candidatos_registrados
    ):
        """`FR-390`: base vazia é estado válido, e a resposta não é falha."""
        inscricao = pronta_para_enviar(selecao_na_inscricao)
        entrar_como(client, inscricao)

        resposta = client.post(self.rota(), {"cep": "99999999"})

        assert resposta.status_code == 200
        assert resposta.json() == {"conferido": False}


class TestOEnviadoELegivel:
    """O estado enviado mostra **o que a pessoa escolheu**, e não o código guardado.

    **Isto foi encontrado no percurso do `C8`**, e não por teste: a tela do enviado exibia `PARDA`,
    `F` e `DE_0_5_A_1` a quem acabara de escolher *Parda*, *Feminino* e *De meio a 1 salário
    mínimo*. A causa é de uma linha — o estado enviado reusava os grupos do **formulário**, que
    carregam o valor que o controle precisa, e não o que uma pessoa lê.

    É exatamente o defeito que passa em todos os testes de comportamento: o campo está lá, o valor
    está certo, e a tela está ilegível.
    """

    def enviar(self, client, inscricao, campos):
        abrir(client, inscricao)
        client.post(
            endereco(inscricao),
            {
                **campos,
                "enviar": "1",
                "aceite": "1",
                "versao_exibida": str(preencher._conteudo(inscricao).id),
                "declaracao_exibida": DECLARACAO,
            },
        )
        return abrir(client, inscricao).content.decode()

    def test_as_listas_fechadas_aparecem_por_extenso(
        self, client, selecao_na_inscricao, candidatos_registrados, campos_declarados
    ):
        from processo_seletivo.requerimentos.domain import rotulos

        inscricao = pronta_para_enviar(selecao_na_inscricao)
        entrar_como(client, inscricao)

        corpo = self.enviar(client, inscricao, campos_declarados)

        for campo in ("sexo", "cor_raca", "estado_civil", "renda_familiar_faixa"):
            codigo = campos_declarados[campo]
            assert rotulos.VALORES[campo][codigo] in corpo, f"{campo} não aparece por extenso"
            assert f">{codigo}<" not in corpo, f"{campo} vazou o código guardado para a tela"

    def test_data_e_cep_aparecem_na_forma_que_se_le(
        self, client, selecao_na_inscricao, candidatos_registrados, campos_declarados
    ):
        """ISO é o que o controle consome; `dd/mm/aaaa` é o que uma pessoa lê.

        E o CEP é guardado sem pontuação (`FR-387`) e **lido** com ela: a forma única é da coluna,
        e não da leitura.
        """
        inscricao = pronta_para_enviar(selecao_na_inscricao)
        entrar_como(client, inscricao)

        corpo = self.enviar(client, inscricao, campos_declarados)

        assert "14/03/1990" in corpo, "a data de nascimento, como se lê"
        assert "1990-03-14" not in corpo, "e não a forma do controle"
        assert "29040-860" in corpo


class TestADeclaracaoExibidaEADaVersaoAceita:
    """`FR-393` e `SC-129`: a tela não atribui à pessoa uma declaração que ela nunca leu.

    **O defeito.** *"Declaração aceita"* vinha do conteúdo **vigente**. Depois de uma Retificação no
    texto, a página afirmava que a pessoa aceitou a redação nova — enquanto o resumo guardado
    continuava sendo o da anterior. A tela dizia uma coisa e o registro provava outra, e quem
    conferisse acreditaria na tela.

    O que se exibe para **aceitar** é a norma de hoje; o que se exibe como **aceito** é a norma
    daquele dia. É a mesma distinção que a `Inscricao` já carrega entre `versao_reconhecida` e
    `versao_aceita`.
    """

    def test_apos_retificacao_a_tela_mostra_o_texto_que_foi_aceito(
        self, client, api_client, selecao_na_inscricao, candidatos_registrados, campos_declarados
    ):
        from tests.fixtures.publicacao import retify

        inscricao = pronta_para_enviar(selecao_na_inscricao)
        entrar_como(client, inscricao)
        abrir(client, inscricao)
        client.post(
            endereco(inscricao),
            {
                **campos_declarados,
                "enviar": "1",
                "aceite": "1",
                "versao_exibida": str(preencher._conteudo(inscricao).id),
                "declaracao_exibida": DECLARACAO,
            },
        )
        novo = "Declaro, sob as penas da Lei, TEXTO RETIFICADO DEPOIS DO ACEITE."
        retify(
            api_client,
            selecao_na_inscricao,
            [
                {
                    "targetPath": "/matriculationRequest/declarationText",
                    "operation": "REPLACE",
                    "newValue": novo,
                }
            ],
        )

        corpo = abrir(client, inscricao).content.decode()

        assert DECLARACAO in corpo, "o texto que a pessoa leu e aceitou"
        assert novo not in corpo, "e nunca o que passou a valer depois"

    def test_o_resumo_guardado_continua_sendo_o_do_texto_aceito(
        self, client, selecao_na_inscricao, candidatos_registrados, campos_declarados
    ):
        """A outra metade: a tela e o registro precisam dizer a mesma coisa."""
        inscricao = pronta_para_enviar(selecao_na_inscricao)
        entrar_como(client, inscricao)
        abrir(client, inscricao)
        client.post(
            endereco(inscricao),
            {
                **campos_declarados,
                "enviar": "1",
                "aceite": "1",
                "versao_exibida": str(preencher._conteudo(inscricao).id),
                "declaracao_exibida": DECLARACAO,
            },
        )

        enviado = preencher.vigente_de(inscricao)

        assert enviado.declaracao_hash == preencher.resumo_da_declaracao(DECLARACAO)


class TestOControleOtimistaNoPortal:
    """T026: duas abas da mesma pessoa não se sobrescrevem em silêncio.

    **O defeito.** O comando sempre soube receber `expected_revision`; a view passava `None` — e
    `None` **desliga** o controle. Duas abas abertas, a que gravasse por último vencia, sem que
    nenhuma das duas soubesse que a outra existia.
    """

    def test_a_tela_carrega_a_revisao_que_exibe(
        self, client, selecao_na_inscricao, candidatos_registrados
    ):
        inscricao = pronta_para_enviar(selecao_na_inscricao)
        entrar_como(client, inscricao)

        corpo = abrir(client, inscricao).content.decode()

        vigente = preencher.vigente_de(inscricao)
        assert f'name="revisao" value="{vigente.revision}"' in corpo

    def test_gravar_com_revisao_obsoleta_e_recusado(
        self, client, selecao_na_inscricao, candidatos_registrados, campos_declarados
    ):
        """A segunda aba declara a revisão que **ela** viu, e perde — dizendo por quê."""
        inscricao = pronta_para_enviar(selecao_na_inscricao)
        entrar_como(client, inscricao)
        abrir(client, inscricao)
        da_primeira_aba = preencher.vigente_de(inscricao).revision
        client.post(endereco(inscricao), {**campos_declarados, "revisao": str(da_primeira_aba)})

        corpo = client.post(
            endereco(inscricao),
            {**campos_declarados, "bairro": "Outro", "revisao": str(da_primeira_aba)},
        ).content.decode()

        assert "Alguém alterou este requerimento enquanto você preenchia" in corpo
        assert preencher.vigente_de(inscricao).bairro != "Outro", "a segunda não sobrescreveu"

    def test_gravar_com_a_revisao_corrente_conclui(
        self, client, selecao_na_inscricao, candidatos_registrados, campos_declarados
    ):
        inscricao = pronta_para_enviar(selecao_na_inscricao)
        entrar_como(client, inscricao)
        abrir(client, inscricao)

        client.post(
            endereco(inscricao),
            {
                **campos_declarados,
                "bairro": "Jardim da Penha",
                "revisao": str(preencher.vigente_de(inscricao).revision),
            },
        )

        assert preencher.vigente_de(inscricao).bairro == "Jardim da Penha"
