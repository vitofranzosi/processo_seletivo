"""O que o `POST` manda não é o que o banco guarda — a camada que faltava (029).

**O Django não valida `choices` em `save()`.** `gravar` atribuía o `POST` cru aos campos do modelo,
e com isso `sexo="X"`, `cor_raca="QUALQUER"` e `uf="ZZ"` chegavam ao estado *enviado* sem que nada
recusasse. O primeiro chegaria ao Registro Acadêmico como sexo inexistente.

**E o que o banco recusava, recusava feio.** Um valor maior que a coluna virava `DataError` — erro
500 para quem preenchia, em vez da frase que diz o que corrigir. Uma data mal digitada, idem.

**Texto com espaços passava por preenchido.** `faltando_para_enviar` testava apenas veracidade, e
`"   "` é verdadeiro: o envio concluía com um município em branco, e o dossiê exibia endereço vazio
a quem fosse expedir documento de matrícula.

*"Validações no frontend PODEM melhorar a experiência, mas NÃO são fronteira de segurança"*
(Princípio IV) — e estes testes chamam o comando direto, sem tela nenhuma pelo caminho.
"""

import pytest

from processo_seletivo.requerimentos.application import preencher
from processo_seletivo.requerimentos.domain import nomes
from processo_seletivo.requerimentos.models import RequerimentoDeMatricula
from processo_seletivo.shared.api.problems import DomainError
from tests.fixtures.candidato import MARIA
from tests.fixtures.requerimento import DECLARACAO, pronta_para_enviar

pytestmark = [pytest.mark.django_db, pytest.mark.integration]


@pytest.fixture
def rascunho_aberto(selecao_na_inscricao, candidatos_registrados):
    inscricao = pronta_para_enviar(selecao_na_inscricao)
    preencher.abrir_rascunho(inscricao=inscricao)
    return inscricao


def gravar(inscricao, campos, **ajustes):
    return preencher.gravar(
        inscricao=inscricao, dados={**campos, **ajustes}, expected_revision=None
    )


def enviar(inscricao):
    return preencher.enviar(
        identidade=MARIA,
        inscricao=inscricao,
        versao_exibida_id=preencher._conteudo(inscricao).id,
        declaracao_exibida=DECLARACAO,
        aceite=True,
    )


class TestListasFechadas:
    @pytest.mark.parametrize(
        ("campo", "intruso"),
        [
            ("sexo", "X"),
            ("cor_raca", "QUALQUER"),
            ("estado_civil", "AMIGADO"),
            ("renda_familiar_faixa", "MUITA"),
            ("uf", "ZZ"),
            ("uf_natal", "XX"),
        ],
    )
    def test_valor_fora_do_vocabulario_e_recusado(
        self, rascunho_aberto, campos_declarados, campo, intruso
    ):
        """`sexo="X"` **gravava** antes desta camada — conferido contra o banco real."""
        with pytest.raises(DomainError) as recusa:
            gravar(rascunho_aberto, campos_declarados, **{campo: intruso})

        assert recusa.value.code == "field_constraint_violated"
        assert recusa.value.campo == campo

    def test_a_recusa_nao_repete_o_valor_recusado(self, rascunho_aberto, campos_declarados):
        """`FR-401`: mensagem de erro é copiada e colada em chamado de suporte."""
        with pytest.raises(DomainError) as recusa:
            gravar(rascunho_aberto, campos_declarados, cor_raca="SEGREDO-DA-PESSOA")

        assert "SEGREDO-DA-PESSOA" not in recusa.value.detail

    def test_vazio_continua_admitido(self, rascunho_aberto, campos_declarados):
        """Rascunho nasce vazio: a lista fechada recusa o **intruso**, e não a ausência."""
        gravado = gravar(rascunho_aberto, campos_declarados, cor_raca="")

        assert gravado.cor_raca == ""


class TestOTamanhoDaColuna:
    def test_valor_longo_demais_e_recusa_legivel_e_nao_erro_500(
        self, rascunho_aberto, campos_declarados
    ):
        """Antes: `DataError` subindo pela pilha. Agora: a frase que diz o que corrigir."""
        limite = RequerimentoDeMatricula._meta.get_field("rg").max_length

        with pytest.raises(DomainError) as recusa:
            gravar(rascunho_aberto, campos_declarados, rg="9" * (limite + 1))

        assert recusa.value.code == "field_constraint_violated"
        assert str(limite) in recusa.value.detail


class TestAsDatas:
    @pytest.mark.parametrize("valor", ["ontem", "32/13/2020", "2020-13-45", "1994"])
    def test_texto_que_nao_e_data_e_recusa_de_campo(
        self, rascunho_aberto, campos_declarados, valor
    ):
        with pytest.raises(DomainError) as recusa:
            gravar(rascunho_aberto, campos_declarados, data_de_nascimento=valor)

        assert recusa.value.code == "field_constraint_violated"
        assert recusa.value.campo == "data_de_nascimento"

    def test_ano_absurdo_e_recusado(self, rascunho_aberto, campos_declarados):
        """`0001-01-01` é data válida para o Python e absurda para uma pessoa.

        Nenhuma restrição de banco a recusa, e nenhuma conferência humana a aceita: ela fica no
        meio, produzindo um requerimento que ninguém consegue explicar.
        """
        with pytest.raises(DomainError) as recusa:
            gravar(rascunho_aberto, campos_declarados, data_de_nascimento="0001-01-01")

        assert recusa.value.code == "field_constraint_violated"


class TestEspacoEmBrancoEAusencia:
    def test_municipio_com_espacos_conta_como_faltando(self, rascunho_aberto, campos_declarados):
        """`"   "` é verdadeiro, e era assim que ele passava por preenchido."""
        gravado = gravar(rascunho_aberto, campos_declarados, municipio="   ")

        assert gravado.municipio == "", "o espaço não é guardado como se fosse nome"
        assert "o município" in preencher.faltando_para_enviar(gravado)

    def test_o_envio_recusa_em_vez_de_concluir_com_endereco_vazio(
        self, rascunho_aberto, campos_declarados
    ):
        gravar(rascunho_aberto, campos_declarados, logradouro="  ")

        with pytest.raises(DomainError) as recusa:
            enviar(rascunho_aberto)

        assert recusa.value.code == "field_required"
        assert "o logradouro" in recusa.value.detail


class TestOQueContinuaPassando:
    def test_o_preenchimento_valido_conclui(self, rascunho_aberto, campos_declarados):
        """A camada recusa o intruso, e **não** atrapalha quem preenche certo."""
        gravar(rascunho_aberto, campos_declarados)

        assert enviar(rascunho_aberto).status == nomes.ENVIADO

    def test_o_cep_sai_normalizado_da_validacao(self, rascunho_aberto, campos_declarados):
        """`FR-387`: uma forma só, guardada uma vez — e a normalização mora com o resto."""
        gravado = gravar(rascunho_aberto, campos_declarados, cep="29.040-860")

        assert gravado.cep == "29040860"


class TestOsDocumentosEleitorais:
    """Os três campos da `031` (`D-007`), guardados numa forma só e **conferidos** (`FR-451`)."""

    def test_a_pontuacao_do_cartao_e_aceita_e_descartada(self, rascunho_aberto, campos_declarados):
        """`0123 4567 8901` é o título como ele aparece impresso; recusá-lo ensinaria a digitar."""
        gravado = gravar(rascunho_aberto, campos_declarados, titulo_eleitoral="0123 4567 8901")

        assert gravado.titulo_eleitoral == "012345678901"

    def test_a_zona_e_a_secao_nascem_com_os_zeros_a_esquerda(
        self, rascunho_aberto, campos_declarados
    ):
        """A pessoa escreve como fala — *"zona 34"* —, e a coluna guarda uma forma só.

        Sem isto, `34` e `034` seriam duas grafias do mesmo número na mesma coluna.
        """
        gravado = gravar(
            rascunho_aberto, campos_declarados, zona_eleitoral="34", secao_eleitoral="128"
        )

        assert gravado.zona_eleitoral == "034"
        assert gravado.secao_eleitoral == "0128"

    @pytest.mark.parametrize(
        "intruso", ["abc012345678901", "0123-4567-890X", "título 012345678901"]
    )
    def test_letra_e_recusada_em_vez_de_apagada(self, rascunho_aberto, campos_declarados, intruso):
        """**O defeito era silencioso**: os dígitos eram filtrados e o resto, descartado.

        `abc012345678901` virava um título de doze dígitos válido, e quem digitou nunca saberia que
        metade do que escreveu foi jogada fora. Descartar é certo para o separador impresso; para
        letra, o certo é dizer que não serve.
        """
        with pytest.raises(DomainError) as recusa:
            gravar(rascunho_aberto, campos_declarados, titulo_eleitoral=intruso)

        assert recusa.value.code == "field_constraint_violated"
        assert recusa.value.campo == "titulo_eleitoral"
        assert intruso not in recusa.value.detail

    def test_mais_digitos_que_o_documento_tem_e_recusado(self, rascunho_aberto, campos_declarados):
        """Treze dígitos não é um título de eleitor, e completar não é o caso aqui."""
        with pytest.raises(DomainError) as recusa:
            gravar(rascunho_aberto, campos_declarados, titulo_eleitoral="0123456789012")

        assert recusa.value.campo == "titulo_eleitoral"

    def test_vazio_continua_admitido(self, rascunho_aberto, campos_declarados):
        """Nem toda pessoa tem o título em mãos, e nenhum Edital o exige para enviar."""
        gravado = gravar(rascunho_aberto, campos_declarados, titulo_eleitoral="")

        assert gravado.titulo_eleitoral == ""
