"""A trilha do envio: um evento, sobre o agregado certo, com tudo que a `FR-397` exige.

**A asserção é positiva, e é por isso que este arquivo existe separado da varredura de sigilo.**
Um teste que só afirma *"dado sensível não aparece"* é plenamente satisfeito por zero evento
gravado. É preciso um que afirme que o evento **existe**, antes de o outro afirmar o que ele não
contém.

**O agregado é o requerimento, e não a Inscrição.** `record_event` lê `status` e `revision` do que
recebe: com a Inscrição ali, o registro dizia o estado e a revisão *dela* — que este ato não muda —
e a trilha afirmava em duas colunas algo que não aconteceu.
"""

import pytest

from processo_seletivo.auditoria.models import RegistroAuditoria
from processo_seletivo.requerimentos.application import preencher
from processo_seletivo.requerimentos.domain import nomes
from tests.fixtures.candidato import MARIA
from tests.integration.requerimentos.conftest import DECLARACAO

pytestmark = [pytest.mark.django_db, pytest.mark.integration]


def _preencher_e_enviar(inscricao, campos):
    preencher.abrir_rascunho(inscricao=inscricao)
    preencher.gravar(inscricao=inscricao, dados=campos, expected_revision=None)
    return preencher.enviar(
        identidade=MARIA,
        inscricao=inscricao,
        versao_exibida_id=preencher._conteudo(inscricao).id,
        declaracao_exibida=DECLARACAO,
        aceite=True,
    )


class TestOEnvioGravaUmEvento:
    def test_um_evento_e_um_so(self, inscricao_na_inscricao, campos_declarados):
        antes = RegistroAuditoria.objects.count()

        _preencher_e_enviar(inscricao_na_inscricao, campos_declarados)

        assert RegistroAuditoria.objects.count() == antes + 1
        assert RegistroAuditoria.objects.filter(operation=nomes.OPERACAO_ENVIO).count() == 1

    def test_o_agregado_e_o_requerimento_com_o_estado_dele(
        self, inscricao_na_inscricao, campos_declarados
    ):
        """O que mudou foi o requerimento; a trilha tem de dizer isso, e não o estado da Inscrição.

        A redação anterior passava `aggregate=inscricao`, e então `new_state` vinha `RASCUNHO` — o
        estado da inscrição, num evento cujo assunto acabara de virar `ENVIADO`.
        """
        enviado = _preencher_e_enviar(inscricao_na_inscricao, campos_declarados)

        registro = RegistroAuditoria.objects.get(operation=nomes.OPERACAO_ENVIO)
        assert registro.aggregate_type == "RequerimentoDeMatricula"
        assert str(registro.aggregate_id) == str(enviado.id)
        assert registro.new_state == nomes.ENVIADO
        assert registro.new_revision == enviado.revision

    def test_quem_enviou_e_quando(self, inscricao_na_inscricao, campos_declarados):
        enviado = _preencher_e_enviar(inscricao_na_inscricao, campos_declarados)

        registro = RegistroAuditoria.objects.get(operation=nomes.OPERACAO_ENVIO)
        assert registro.actor_subject == MARIA.subject
        assert registro.occurred_at == enviado.enviado_em

    def test_inscricao_edital_versao_e_declaracao_ficam_reconstituiveis(
        self, inscricao_na_inscricao, campos_declarados
    ):
        """Os quatro que a `FR-397` nomeia e que não cabem em coluna do registro."""
        enviado = _preencher_e_enviar(inscricao_na_inscricao, campos_declarados)

        razao = RegistroAuditoria.objects.get(operation=nomes.OPERACAO_ENVIO).reason
        assert str(inscricao_na_inscricao.id) in razao
        assert str(inscricao_na_inscricao.edital_id) in razao
        assert str(enviado.versao_aceita_id) in razao
        assert enviado.declaracao_hash in razao

    def test_a_declaracao_registrada_e_a_do_texto_publicado(
        self, inscricao_na_inscricao, campos_declarados
    ):
        """`SC-129`: o resumo na trilha é o do texto que o Edital publicou, e de nenhum outro."""
        _preencher_e_enviar(inscricao_na_inscricao, campos_declarados)

        razao = RegistroAuditoria.objects.get(operation=nomes.OPERACAO_ENVIO).reason
        assert preencher.resumo_da_declaracao(DECLARACAO) in razao


class TestOSigiloDaTrilha:
    def test_a_trilha_referencia_e_nao_copia(self, inscricao_na_inscricao, campos_declarados):
        """`FR-401`: trilha que duplica dado sensível multiplica a superfície, não a protege."""
        _preencher_e_enviar(
            inscricao_na_inscricao, {**campos_declarados, "nome_da_mae": "Maria da Silva"}
        )

        registro = RegistroAuditoria.objects.get(operation=nomes.OPERACAO_ENVIO)
        texto = f"{registro.reason}{registro.previous_state}{registro.new_state}"
        for sensivel in ("Maria da Silva", campos_declarados["rg"], campos_declarados["cep"]):
            assert sensivel not in texto


class TestONomeLegivel:
    """**As duas operações têm rótulo**, e a varredura global não as alcança.

    `test_trilha_legivel` coleta todo literal `operation="…"` passado a `record_event`; estas
    chegam como **constante**, e o `ast.Constant` daquela varredura não as vê. Sem a asserção
    abaixo, a trilha exibiria `REQUERIMENTO_ENVIAR` cru para quem responde um questionamento, e
    nada acusaria.
    """

    def test_as_duas_operacoes_tem_rotulo_em_portugues(self):
        from processo_seletivo.interface.views import OPERACOES

        for operacao in (nomes.OPERACAO_ENVIO, nomes.OPERACAO_SUCESSAO):
            assert operacao in OPERACOES, f"apareceria crua na tela: {operacao}"
            assert OPERACOES[operacao] != operacao
