"""O Requerimento de Matrícula no dossiê de quem conduz (029, `US4`, T052, T053).

**A mesma permissão da tela que o hospeda**, `inscricao:consultar`. Sem ela, a recusa não revela que
o requerimento existe: é a mesma resposta que quem pergunta por uma inscrição inexistente recebe, e
distinguir as duas entregaria, a quem tentar identificadores em sequência, o mapa do que existe.

**E nenhuma rota de listagem** (`FR-400`). A terceira asserção deste arquivo é sobre **ausência**, e
é a que envelhece mal sem teste: uma listagem de requerimentos de um Edital é a coisa mais natural
do mundo de se acrescentar — e poria cor/raça, filiação, documento e endereço de centenas de pessoas
numa tela só, sem jornada que a peça.
"""

import re

import pytest
from django.urls import reverse

from processo_seletivo.requerimentos.application import preencher
from processo_seletivo.requerimentos.domain import rotulos
from tests.fixtures.requerimento import DECLARACAO, pronta_para_enviar
from tests.interface.conftest import identificar

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.integration]


def enviar_o_requerimento(inscricao, campos):
    from tests.fixtures.candidato import MARIA

    preencher.abrir_rascunho(inscricao=inscricao)
    preencher.gravar(inscricao=inscricao, dados=campos, expected_revision=None)
    return preencher.enviar(
        identidade=MARIA,
        inscricao=inscricao,
        versao_exibida_id=preencher._conteudo(inscricao).id,
        declaracao_exibida=DECLARACAO,
        aceite=True,
    )


def dossie(client, inscricao):
    return client.get(reverse("interface:inscricao-recebida", args=[inscricao.id]))


@pytest.fixture
def inscricao_com_requerimento(selecao_na_inscricao, candidatos_registrados, campos_declarados):
    inscricao = pronta_para_enviar(selecao_na_inscricao)
    enviar_o_requerimento(inscricao, campos_declarados)
    return inscricao


class TestComAPermissao:
    def test_o_bloco_aparece_com_os_campos_declarados(
        self, client, seletor_ligado, inscricao_com_requerimento, campos_declarados
    ):
        identificar(client, "ana.gestora", ["gestor"])

        corpo = dossie(client, inscricao_com_requerimento).content.decode()

        assert "Requerimento de Matrícula" in corpo
        assert campos_declarados["nome_da_mae"] in corpo
        assert campos_declarados["rg"] in corpo

    def test_os_valores_de_lista_aparecem_por_extenso(
        self, client, seletor_ligado, inscricao_com_requerimento, campos_declarados
    ):
        """`PARDA` não diz nada a quem lê um dossiê. **Os rótulos são os mesmos dos dois canais.**

        Eles moram em `requerimentos/domain/rotulos.py` justamente porque o candidato preenche e
        quem conduz lê o mesmo dado: dois textos para o mesmo campo divergiriam na primeira
        correção, numa conversa em que as duas pessoas olham telas diferentes.
        """
        identificar(client, "ana.gestora", ["gestor"])

        corpo = dossie(client, inscricao_com_requerimento).content.decode()

        assert rotulos.COR_RACA[campos_declarados["cor_raca"]] in corpo
        assert campos_declarados["cor_raca"] not in corpo, "o código guardado não vai para a tela"
        assert rotulos.RENDA[campos_declarados["renda_familiar_faixa"]] in corpo

    def test_o_rotulo_da_renda_diz_que_ela_e_somada(
        self, client, seletor_ligado, inscricao_com_requerimento
    ):
        """`FR-412` e `R-7`: a coluna de destino significa valor **por pessoa**, e a faixa não.

        A divergência é conhecida e decidida. Escrever só "Renda familiar" a propagaria por
        ambiguidade de redação — que é o modo de um achado registrado virar defeito silencioso.
        """
        identificar(client, "ana.gestora", ["gestor"])

        corpo = dossie(client, inscricao_com_requerimento).content.decode()

        assert "somada da família" in corpo

    def test_o_instante_e_a_versao_aceita_aparecem(
        self, client, seletor_ligado, inscricao_com_requerimento
    ):
        identificar(client, "ana.gestora", ["gestor"])

        corpo = dossie(client, inscricao_com_requerimento).content.decode()

        assert "Enviado em" in corpo
        assert "sob a versão vigente desde" in corpo

    def test_o_dossie_diz_se_o_endereco_foi_conferido_contra_a_base(
        self, client, seletor_ligado, inscricao_com_requerimento
    ):
        """Quem lê um endereço para expedir documento precisa saber de qual dos dois se trata."""
        identificar(client, "ana.gestora", ["gestor"])

        corpo = dossie(client, inscricao_com_requerimento).content.decode()

        assert "o CEP não foi reconhecido" in corpo, "não há base carregada neste cenário"


class TestORascunho:
    def test_o_rascunho_aparece_dito_como_rascunho(
        self,
        client,
        seletor_ligado,
        selecao_na_inscricao,
        candidatos_registrados,
        campos_declarados,
    ):
        """Escondê-lo faria concluir que a pessoa não declarou nada; mostrá-lo sem a marca faria
        tratar como declarado o que ninguém enviou."""
        inscricao = pronta_para_enviar(selecao_na_inscricao)
        preencher.abrir_rascunho(inscricao=inscricao)
        preencher.gravar(inscricao=inscricao, dados=campos_declarados, expected_revision=None)
        identificar(client, "ana.gestora", ["gestor"])

        corpo = dossie(client, inscricao).content.decode()

        assert "Em preenchimento" in corpo
        assert "não foi declarado" in corpo
        assert "Enviado em" not in corpo


class TestOEditalQueNaoColeta:
    def test_sem_requerimento_o_bloco_nao_existe(
        self, client, seletor_ligado, selecao, candidatos_registrados
    ):
        """A ausência não é informação.

        Um bloco dizendo *"não há"* apareceria na maioria dos Editais, alongando uma tela já longa.
        """
        from processo_seletivo.inscricoes.application.rascunho import abrir_inscricao
        from tests.fixtures.candidato import MARIA, PERFIL_DOCENTE

        inscricao = abrir_inscricao(
            identidade=MARIA, edital_id=selecao.id, profile_id=PERFIL_DOCENTE
        )
        identificar(client, "ana.gestora", ["gestor"])

        corpo = dossie(client, inscricao).content.decode()

        assert "Requerimento de Matrícula" not in corpo


class TestSemAPermissao:
    def test_a_recusa_nao_revela_que_o_requerimento_existe(
        self, client, seletor_ligado, inscricao_com_requerimento
    ):
        """`FR-072` e `FR-400`: a resposta é a mesma de quem pergunta por recurso inexistente."""
        identificar(client, "ana.elaboradora", ["elaborador"])

        resposta = dossie(client, inscricao_com_requerimento)

        corpo = resposta.content.decode()
        assert resposta.status_code in (403, 404)
        assert "Requerimento de Matrícula" not in corpo
        assert "Maria da Silva" not in corpo, "nem um campo do requerimento escapa"


class TestNaoHaListagem:
    """`FR-400`: **nenhuma rota** entrega o conjunto de requerimentos de um Edital.

    Asserção sobre ausência é a que envelhece mal sem teste. Basta alguém acrescentar
    `/gestao/editais/<uuid>/requerimentos` "para facilitar a conferência", e cor/raça, filiação,
    documento e endereço de centenas de pessoas passam a caber numa tela — sem jornada que a peça,
    e sem que nada acuse.
    """

    def rotas(self):
        from processo_seletivo.interface import urls as urls_da_gestao
        from processo_seletivo.portal import urls as urls_do_portal

        return [
            str(rota.pattern)
            for modulo in (urls_da_gestao, urls_do_portal)
            for rota in modulo.urlpatterns
        ]

    def test_nenhuma_rota_lista_requerimentos(self):
        plural = [
            rota
            for rota in self.rotas()
            if re.search(r"requerimentos/?$", rota) or rota.endswith("requerimentos")
        ]

        assert plural == [], f"listagem de requerimentos não pode existir: {plural}"

    def test_as_rotas_de_requerimento_pendem_de_uma_inscricao_ou_sao_fixas(self):
        """Cada rota existente ou é do titular de **uma** inscrição, ou não carrega dado nenhum."""
        de_requerimento = [rota for rota in self.rotas() if "requerimento" in rota]

        assert de_requerimento, "o rastreio quebrou: nenhuma rota de requerimento encontrada"
        for rota in de_requerimento:
            assert "inscricoes/<uuid:inscricao_id>" in rota or rota == "requerimento/cep", rota
