"""A fronteira da `D-005`, contada em gravações — `SC-130` e `FR-398`.

**Por que contar, e não inspecionar.** "Esta feature não escreve na identidade" é uma promessa que
nenhuma leitura de código mantém por muito tempo: basta alguém acrescentar um `update` "para manter
sincronizado", e a promessa cai sem que nada acuse. O que a prende é ler o SQL que saiu e conferir
em quais tabelas ele escreveu.

**A `D-005` é a decisão que isto protege.** A identidade guarda o **atual**; o ato guarda o que
valia no dia. Um requerimento que escrevesse de volta na `CandidateIdentity` faria o passado mudar
junto com o presente — e o requerimento de 2024 deixaria de dizer o que dizia em 2024.

**O requerimento anterior entra na mesma conta**, e pela mesma razão: a cópia-para-a-frente é cópia,
nunca referência. Editar o novo não pode alcançar o de antes.
"""

import pytest
from django.db import connection
from django.test.utils import CaptureQueriesContext

from processo_seletivo.auditoria.models import RegistroAuditoria
from processo_seletivo.identidade.models import CandidateIdentity
from processo_seletivo.inscricoes.models import Inscricao, ItemDaListaExigida, ValorDeFato
from processo_seletivo.requerimentos.application import preencher
from processo_seletivo.requerimentos.models import RequerimentoDeMatricula
from tests.fixtures.candidato import MARIA
from tests.integration.requerimentos.conftest import DECLARACAO

pytestmark = [pytest.mark.django_db, pytest.mark.integration]

# As tabelas que esta feature **lê** e nas quais nunca escreve. **Os nomes saem dos modelos**, e
# não de literais: a primeira redação escrevia `inscricoes_candidateidentity`, e a tabela se chama
# `identidade_candidateidentity` — a asserção passava por não casar com nada, que é o modo de um
# teste de proibição morrer sem avisar.
PROIBIDAS = frozenset(
    modelo._meta.db_table
    for modelo in (CandidateIdentity, Inscricao, ValorDeFato, ItemDaListaExigida)
)
REQUERIMENTO = RequerimentoDeMatricula._meta.db_table
TRILHA = RegistroAuditoria._meta.db_table

ESCRITA = ("insert into ", "update ", "delete from ")


def escritas(consultas):
    """As tabelas em que o SQL capturado escreveu, uma vez cada."""
    alcancadas = set()
    for consulta in consultas:
        sql = consulta["sql"].lower()
        for verbo in ESCRITA:
            if verbo not in sql:
                continue
            # O nome da tabela é a primeira palavra depois do verbo, com ou sem aspas.
            resto = sql.split(verbo, 1)[1].lstrip()
            alcancadas.add(resto.split()[0].strip('"').strip())
    return alcancadas


def _capturar(funcao):
    with CaptureQueriesContext(connection) as consultas:
        resultado = funcao()
    return resultado, escritas(consultas)


class TestNenhumaGravacaoAlcancaOQueEDeOutro:
    def test_abrir_o_rascunho_nao_escreve_fora(self, inscricao_na_inscricao):
        _, tabelas = _capturar(lambda: preencher.abrir_rascunho(inscricao=inscricao_na_inscricao))

        assert REQUERIMENTO in tabelas, (
            "sem esta, o teste passaria por não ter havido gravação nenhuma"
        )
        assert not tabelas & PROIBIDAS

    def test_gravar_nao_escreve_fora(self, inscricao_na_inscricao, campos_declarados):
        preencher.abrir_rascunho(inscricao=inscricao_na_inscricao)

        _, tabelas = _capturar(
            lambda: preencher.gravar(
                inscricao=inscricao_na_inscricao,
                dados=campos_declarados,
                expected_revision=None,
            )
        )

        assert REQUERIMENTO in tabelas
        assert not tabelas & PROIBIDAS

    def test_enviar_escreve_no_requerimento_e_na_trilha_e_em_nada_mais(
        self, inscricao_na_inscricao, campos_declarados
    ):
        """A trilha é gravação legítima — e é a única além do próprio requerimento."""
        preencher.abrir_rascunho(inscricao=inscricao_na_inscricao)
        preencher.gravar(
            inscricao=inscricao_na_inscricao, dados=campos_declarados, expected_revision=None
        )

        _, tabelas = _capturar(
            lambda: preencher.enviar(
                identidade=MARIA,
                inscricao=inscricao_na_inscricao,
                versao_exibida_id=preencher._conteudo(inscricao_na_inscricao).id,
                declaracao_exibida=DECLARACAO,
                aceite=True,
            )
        )

        assert REQUERIMENTO in tabelas
        assert TRILHA in tabelas
        assert not tabelas & PROIBIDAS

    def test_a_copia_para_a_frente_nao_toca_o_requerimento_anterior(
        self, inscricao_na_inscricao, campos_declarados, segunda_inscricao_da_mesma_pessoa
    ):
        """`SC-124`: o novo nasce preenchido **por cópia**, e o de antes fica byte por byte igual.

        A asserção é sobre a linha, e não sobre um campo: comparar `nome_da_mae` deixaria passar
        uma escrita em qualquer dos outros vinte.
        """
        preencher.abrir_rascunho(inscricao=inscricao_na_inscricao)
        preencher.gravar(
            inscricao=inscricao_na_inscricao, dados=campos_declarados, expected_revision=None
        )
        anterior = preencher.enviar(
            identidade=MARIA,
            inscricao=inscricao_na_inscricao,
            versao_exibida_id=preencher._conteudo(inscricao_na_inscricao).id,
            declaracao_exibida=DECLARACAO,
            aceite=True,
        )
        antes = RequerimentoDeMatricula.objects.filter(pk=anterior.pk).values().get()

        preencher.abrir_rascunho(inscricao=segunda_inscricao_da_mesma_pessoa)
        preencher.gravar(
            inscricao=segunda_inscricao_da_mesma_pessoa,
            dados={**campos_declarados, "nome_da_mae": "Outro Nome Completamente"},
            expected_revision=None,
        )

        assert RequerimentoDeMatricula.objects.filter(pk=anterior.pk).values().get() == antes
