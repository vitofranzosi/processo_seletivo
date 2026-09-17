"""O enriquecimento por CEP: o que ele preenche, o que ele nunca aceita, e o que não bloqueia.

**As três situações são distintas, e a do meio é a mais provável.** Base carregada e CEP conhecido
é o caso feliz; base vazia é a instituição que não carregou nada; e **registro incompleto** — sem
bairro, sem logradouro, sem código IBGE — é o que uma base real entrega com mais frequência do que
qualquer um dos outros dois. Tratar os três igual é o que a `FR-390` exige, e é o que prova que
serviço de referência é auxiliar e não porta de entrada (`SC-125`, `SC-126`).

**O código IBGE nunca é digitável** (`FR-388`), nem no caso em que todo o resto do endereço abre.
É a exceção que a própria `FR-390` escreve, porque sem ela a regra mandaria abrir justamente o
campo que a outra proíbe.
"""

import pytest

from processo_seletivo.requerimentos.application import preencher
from processo_seletivo.requerimentos.models import ReferenciaDeCep
from tests.fixtures.candidato import MARIA
from tests.integration.requerimentos.conftest import DECLARACAO

pytestmark = [pytest.mark.django_db, pytest.mark.integration]

CEP = "29040860"


def referencia(**campos):
    return ReferenciaDeCep.objects.create(
        **{
            "cep": CEP,
            "logradouro": "Rua Barão de Mauá",
            "bairro": "Jucutuquara",
            "municipio": "Vitória",
            "uf": "ES",
            "codigo_ibge": "3205309",
            **campos,
        }
    )


def gravar(inscricao, campos, **sobrescreve):
    preencher.abrir_rascunho(inscricao=inscricao)
    return preencher.gravar(
        inscricao=inscricao, dados={**campos, **sobrescreve}, expected_revision=None
    )


def enviar(inscricao):
    return preencher.enviar(
        identidade=MARIA,
        inscricao=inscricao,
        versao_exibida_id=preencher._conteudo(inscricao).id,
        declaracao_exibida=DECLARACAO,
        aceite=True,
    )


class TestCepReconhecido:
    def test_municipio_uf_e_ibge_vem_da_referencia(self, inscricao_na_inscricao, campos_declarados):
        """`SC-125`: a pessoa digita o CEP, e a localidade não é redigitada."""
        referencia()

        gravado = gravar(
            inscricao_na_inscricao,
            campos_declarados,
            municipio="",
            uf="",
        )

        assert gravado.municipio == "Vitória"
        assert gravado.uf == "ES"
        assert gravado.codigo_ibge == "3205309"
        assert gravado.endereco_conferido_por_referencia is True

    def test_o_ibge_do_formulario_e_ignorado(self, inscricao_na_inscricao, campos_declarados):
        """`FR-388`: o código IBGE é **derivado**, e um `POST` montado à mão não o planta."""
        referencia()

        gravado = gravar(inscricao_na_inscricao, campos_declarados, codigo_ibge="9999999")

        assert gravado.codigo_ibge == "3205309"

    def test_municipio_divergente_no_post_nao_prevalece(
        self, inscricao_na_inscricao, campos_declarados
    ):
        """Somente leitura na tela é o valor vindo da referência — inclusive contra um `POST`."""
        referencia()

        gravado = gravar(inscricao_na_inscricao, campos_declarados, municipio="Outra Cidade")

        assert gravado.municipio == "Vitória"

    def test_a_marca_de_conferencia_nao_vem_do_formulario(
        self, inscricao_na_inscricao, campos_declarados
    ):
        """Quem **afirma** que a referência conferiu é quem conferiu, e não quem monta o `POST`."""
        gravado = gravar(
            inscricao_na_inscricao,
            campos_declarados,
            endereco_conferido_por_referencia=True,
        )

        assert gravado.endereco_conferido_por_referencia is False, "não há referência carregada"


class TestBaseVazia:
    def test_os_campos_abrem_e_o_envio_conclui_com_ibge_vazio(
        self, inscricao_na_inscricao, campos_declarados
    ):
        """`SC-126` e `FR-390`: sem base não há enriquecimento, e nada disso impede a matrícula."""
        assert not ReferenciaDeCep.objects.exists()

        gravar(inscricao_na_inscricao, campos_declarados)
        enviado = enviar(inscricao_na_inscricao)

        assert enviado.codigo_ibge == ""
        assert enviado.endereco_conferido_por_referencia is False
        assert enviado.municipio == campos_declarados["municipio"], "o que a pessoa digitou fica"


class TestRegistroIncompleto:
    def test_sem_bairro_nao_bloqueia_e_o_bairro_digitado_fica(
        self, inscricao_na_inscricao, campos_declarados
    ):
        referencia(bairro="")

        gravado = gravar(inscricao_na_inscricao, campos_declarados, bairro="Jucutuquara")
        enviar(inscricao_na_inscricao)

        assert gravado.bairro == "Jucutuquara"
        assert gravado.endereco_conferido_por_referencia is True, "município e UF vieram"

    def test_sem_codigo_ibge_o_campo_fica_vazio_e_nao_digitavel(
        self, inscricao_na_inscricao, campos_declarados
    ):
        """O caso que separa *"base não tem o CEP"* de *"base tem, e não tem o código"*."""
        referencia(codigo_ibge="")

        gravado = gravar(inscricao_na_inscricao, campos_declarados, codigo_ibge="3205309")
        enviado = enviar(inscricao_na_inscricao)

        assert gravado.codigo_ibge == ""
        assert enviado.codigo_ibge == ""

    def test_sem_localidade_a_marca_de_conferencia_nao_e_ligada(
        self, inscricao_na_inscricao, campos_declarados
    ):
        """A marca **afirma conferência**, e sem município e UF ninguém conferiu coisa alguma.

        A redação anterior a ligava pela mera existência da linha: um registro sem localidade dizia
        *"conferido"* sobre um endereço que a referência não confirmou, e a tela fecharia campos
        com base nessa afirmação.
        """
        referencia(municipio="", uf="")

        gravado = gravar(inscricao_na_inscricao, campos_declarados)

        assert gravado.endereco_conferido_por_referencia is False
        assert gravado.municipio == campos_declarados["municipio"]


class TestAFormaDoCep:
    def test_o_cep_e_guardado_normalizado(self, inscricao_na_inscricao, campos_declarados):
        """`FR-387`: uma forma só, para que a comparação nunca dependa de como se digitou."""
        referencia()

        gravado = gravar(inscricao_na_inscricao, campos_declarados, cep="29.040-860")

        assert gravado.cep == CEP
        assert gravado.codigo_ibge == "3205309", "com traço e ponto, a referência é a mesma"

    def test_o_que_nao_e_cep_nao_e_guardado_como_cep(
        self, inscricao_na_inscricao, campos_declarados
    ):
        """Enquanto a normalização vivia só na consulta, a coluna guardava o que viesse.

        `faltando_para_enviar` via campo preenchido — o valor é verdadeiro —, e o envio concluía
        com um CEP que não é CEP.
        """
        from processo_seletivo.shared.api.problems import DomainError

        gravado = gravar(inscricao_na_inscricao, campos_declarados, cep="ABCDEFGH")

        assert gravado.cep == ""
        assert "o CEP" in preencher.faltando_para_enviar(gravado)
        with pytest.raises(DomainError) as recusa:
            enviar(inscricao_na_inscricao)
        assert recusa.value.code == "field_required"
