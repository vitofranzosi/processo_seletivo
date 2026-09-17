"""Abrir, gravar e enviar — e o que a aplicação recusa **sem passar por tela** (029, `US1`).

**Chamar a aplicação direto é o ponto deste arquivo.** A Constituição diz que validação de frontend
*"NÃO é fronteira de segurança"*; um teste que só exercitasse a tela provaria a tela. O que
se prende aqui é que um `POST` montado à mão encontra a mesma recusa que a tela anuncia.
"""

import pytest
from django.utils import timezone

from processo_seletivo.inscricoes.models import Inscricao
from processo_seletivo.requerimentos.application import preencher
from processo_seletivo.requerimentos.domain import nomes
from processo_seletivo.requerimentos.models import RequerimentoDeMatricula
from processo_seletivo.shared.api.problems import DomainError
from tests.fixtures.candidato import MARIA
from tests.integration.requerimentos.conftest import DECLARACAO, pronta_para_enviar, submeter

pytestmark = [pytest.mark.django_db, pytest.mark.integration]


def _versao(inscricao):
    return preencher._conteudo(inscricao)


def _enviar(inscricao, *, aceite=True, declaracao=DECLARACAO, versao=None):
    return preencher.enviar(
        identidade=MARIA,
        inscricao=inscricao,
        versao_exibida_id=versao or _versao(inscricao).id,
        declaracao_exibida=declaracao,
        aceite=aceite,
    )


class TestAAplicacaoRecusaPorSi:
    def test_edital_que_nao_declara_recusa_a_abertura(self, inscricao_de_maria):
        """`FR-371`: onde o Edital não declara, o requerimento **não existe** — nem por `POST`."""
        with pytest.raises(DomainError) as recusa:
            preencher.abrir_rascunho(inscricao=inscricao_de_maria)

        assert recusa.value.code == nomes.NAO_EXIGIDO

    def test_na_convocacao_sem_chamada_em_aberto_recusa(
        self, selecao_na_convocacao, candidatos_registrados
    ):
        """`FR-373`: a vez da pessoa é a chamada em aberto, e não a classificação."""
        from processo_seletivo.inscricoes.application.rascunho import abrir_inscricao
        from tests.fixtures.candidato import PERFIL_DOCENTE

        inscricao = abrir_inscricao(
            identidade=MARIA, edital_id=selecao_na_convocacao.id, profile_id=PERFIL_DOCENTE
        )

        with pytest.raises(DomainError) as recusa:
            preencher.abrir_rascunho(inscricao=inscricao)

        assert recusa.value.code == nomes.INDISPONIVEL


class TestOPreenchimento:
    def test_abrir_e_idempotente(self, inscricao_na_inscricao):
        """Atualizar a página não cria uma segunda linha — nem um erro que a pessoa não causou."""
        primeiro = preencher.abrir_rascunho(inscricao=inscricao_na_inscricao)
        segundo = preencher.abrir_rascunho(inscricao=inscricao_na_inscricao)

        assert primeiro.id == segundo.id

    def test_o_telefone_vem_da_inscricao(self, inscricao_na_inscricao):
        """`FR-379`: ponto de partida a confirmar, e nunca verdade — ele congelou na submissão."""
        rascunho = preencher.abrir_rascunho(inscricao=inscricao_na_inscricao)

        assert rascunho.telefone_celular == inscricao_na_inscricao.telefone

    def test_o_codigo_ibge_nao_vem_da_tela(self, inscricao_na_inscricao, campos_declarados):
        """`FR-388`: digitável por `POST` montado à mão seria digitável — e ele não é."""
        preencher.abrir_rascunho(inscricao=inscricao_na_inscricao)

        gravado = preencher.gravar(
            inscricao=inscricao_na_inscricao,
            dados={**campos_declarados, "codigo_ibge": "9999999"},
            expected_revision=None,
        )

        assert gravado.codigo_ibge == ""


class TestOEnvio:
    @pytest.fixture
    def preenchido(self, inscricao_na_inscricao, campos_declarados):
        preencher.abrir_rascunho(inscricao=inscricao_na_inscricao)
        preencher.gravar(
            inscricao=inscricao_na_inscricao, dados=campos_declarados, expected_revision=None
        )
        return inscricao_na_inscricao

    def test_sem_aceite_e_recusado(self, preenchido):
        with pytest.raises(DomainError) as recusa:
            _enviar(preenchido, aceite=False)

        assert recusa.value.code == nomes.DECLARACAO_NAO_ACEITA

    def test_o_envio_guarda_versao_instante_e_resumo(self, preenchido):
        enviado = _enviar(preenchido)

        assert enviado.status == nomes.ENVIADO
        assert enviado.enviado_em is not None
        assert enviado.versao_aceita_id == _versao(preenchido).id
        assert enviado.declaracao_hash == preencher.resumo_da_declaracao(DECLARACAO)

    def test_filiacao_com_um_nome_ausente_conclui(self, inscricao_na_inscricao, campos_declarados):
        """`FR-384`: pai não declarado é situação comum, e travar o envio inventaria exigência."""
        preencher.abrir_rascunho(inscricao=inscricao_na_inscricao)
        preencher.gravar(
            inscricao=inscricao_na_inscricao,
            dados={**campos_declarados, "nome_do_pai": ""},
            expected_revision=None,
        )

        assert _enviar(inscricao_na_inscricao).nome_do_pai == ""

    def test_enviado_nao_e_alterado_pela_aplicacao(self, preenchido, campos_declarados):
        _enviar(preenchido)

        with pytest.raises(DomainError) as recusa:
            preencher.gravar(inscricao=preenchido, dados=campos_declarados, expected_revision=None)

        assert recusa.value.code == nomes.JA_ENVIADO

    def test_a_declaracao_exibida_divergente_e_recusada(self, preenchido):
        """O resumo sai do **conteúdo publicado**, e o texto recebido é apenas conferido.

        A redação anterior resumia direto o que o `POST` mandava. Com o identificador de versão
        certo — que é público — dava para gravar o resumo de qualquer texto, e a `SC-129`
        reconstituiria a declaração que o remetente escolheu em vez da que o Edital publicou.
        """
        with pytest.raises(DomainError) as recusa:
            _enviar(preenchido, declaracao="Declaro o que eu quiser.")

        assert recusa.value.code == nomes.EDITAL_ATUALIZADO

    def test_o_resumo_gravado_e_o_do_texto_publicado(self, preenchido):
        """Nem mesmo um texto forjado **com o resumo certo** troca o que se grava (`FR-393`)."""
        enviado = _enviar(preenchido, declaracao=DECLARACAO)

        assert enviado.declaracao_hash == preencher.resumo_da_declaracao(DECLARACAO)


class TestACopiaParaAFrente:
    def test_o_requerimento_novo_nasce_preenchido_e_o_anterior_fica_intacto(
        self, inscricao_na_inscricao, campos_declarados, segunda_inscricao_da_mesma_pessoa
    ):
        """`SC-124` e `D-005`: cópia, nunca referência — o passado continua dizendo o que dizia.

        **Dois Editais, e não dois requerimentos no mesmo.** A cópia é da mesma **identidade**, e é
        isso que a faz atravessar certames e anos — que é o caso real de quem se inscreve de novo.
        """
        preencher.abrir_rascunho(inscricao=inscricao_na_inscricao)
        preencher.gravar(
            inscricao=inscricao_na_inscricao,
            dados={**campos_declarados, "nome_da_mae": "Maria da Silva"},
            expected_revision=None,
        )
        anterior = _enviar(inscricao_na_inscricao)

        novo = preencher.abrir_rascunho(inscricao=segunda_inscricao_da_mesma_pessoa)

        assert novo.nome_da_mae == "Maria da Silva"
        assert novo.rg == anterior.rg
        assert novo.cep == anterior.cep
        assert novo.id != anterior.id

    def test_editar_o_novo_nao_alcanca_o_anterior(
        self, inscricao_na_inscricao, campos_declarados, segunda_inscricao_da_mesma_pessoa
    ):
        preencher.abrir_rascunho(inscricao=inscricao_na_inscricao)
        preencher.gravar(
            inscricao=inscricao_na_inscricao,
            dados={**campos_declarados, "nome_da_mae": "Maria da Silva"},
            expected_revision=None,
        )
        anterior = _enviar(inscricao_na_inscricao)

        preencher.abrir_rascunho(inscricao=segunda_inscricao_da_mesma_pessoa)
        preencher.gravar(
            inscricao=segunda_inscricao_da_mesma_pessoa,
            dados={**campos_declarados, "nome_da_mae": "Maria da Silva Sobrenome Novo"},
            expected_revision=None,
        )

        assert RequerimentoDeMatricula.objects.get(pk=anterior.pk).nome_da_mae == "Maria da Silva"


class TestARetificacaoEntreOGetEOPost:
    def test_versao_exibida_obsoleta_e_recusada(self, inscricao_na_inscricao, campos_declarados):
        """A versão exibida viaja no formulário e é conferida — senão o par ficaria incoerente."""
        preencher.abrir_rascunho(inscricao=inscricao_na_inscricao)
        preencher.gravar(
            inscricao=inscricao_na_inscricao, dados=campos_declarados, expected_revision=None
        )

        with pytest.raises(DomainError) as recusa:
            _enviar(inscricao_na_inscricao, versao=timezone.now().isoformat())

        assert recusa.value.code == nomes.EDITAL_ATUALIZADO


class TestOBloqueioDaSubmissaoDaInscricao:
    """`FR-370` e `SC-127`: o bloqueio é do **comando**, e a tela apenas o antecipa.

    **Estes testes chamam `enviar_inscricao`, e não um predicado.** A primeira redação desta
    feature exercitava só `inscricao_exige_requerimento_enviado` e dava a tarefa por fechada — com
    a submissão ainda passando reto, porque ninguém a havia ligado. Um teste que chama o auxiliar
    prova o auxiliar; o que prende a regra é chamar o ato.
    """

    def test_na_inscricao_sem_requerimento_a_submissao_e_recusada(
        self, selecao_na_inscricao, candidatos_registrados
    ):
        inscricao = pronta_para_enviar(selecao_na_inscricao)

        with pytest.raises(DomainError) as recusa:
            submeter(inscricao)

        assert recusa.value.code == nomes.REQUERIMENTO_EXIGIDO
        assert inscricao.status == Inscricao.Status.RASCUNHO, (
            "recusar não pode deixar a inscrição pela metade"
        )

    def test_o_rascunho_do_requerimento_nao_basta(
        self, selecao_na_inscricao, candidatos_registrados, campos_declarados
    ):
        """Preencher não é enviar: o que a `FR-372` exige é o ato, e não o começo dele."""
        inscricao = pronta_para_enviar(selecao_na_inscricao)
        preencher.abrir_rascunho(inscricao=inscricao)
        preencher.gravar(inscricao=inscricao, dados=campos_declarados, expected_revision=None)

        with pytest.raises(DomainError) as recusa:
            submeter(inscricao)

        assert recusa.value.code == nomes.REQUERIMENTO_EXIGIDO

    def test_com_o_requerimento_enviado_a_submissao_conclui(
        self, selecao_na_inscricao, candidatos_registrados, campos_declarados
    ):
        inscricao = pronta_para_enviar(selecao_na_inscricao)
        preencher.abrir_rascunho(inscricao=inscricao)
        preencher.gravar(inscricao=inscricao, dados=campos_declarados, expected_revision=None)
        _enviar(inscricao)

        enviada = submeter(inscricao)

        assert enviada.status == Inscricao.Status.SUBMETIDA

    def test_na_convocacao_a_submissao_conclui_sem_requerimento_nenhum(
        self, selecao_na_convocacao, candidatos_registrados
    ):
        """Exigir na inscrição o que só abre na convocação tornaria o Edital impossível de cumprir.

        É a metade da regra que envelhece mal sem teste: quem escrever o bloqueio sem o `if` do
        momento quebra **este** certame, e não o outro — e a suíte do outro fica verde.
        """
        inscricao = pronta_para_enviar(selecao_na_convocacao)

        enviada = submeter(inscricao)

        assert enviada.status == Inscricao.Status.SUBMETIDA
