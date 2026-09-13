"""A quinta linha legítima do Resultado, e as quatro que ela não afrouxou (019, `R-005`, `T060`).

**A constraint foi estendida, e não relaxada.** `ck_sucessor_cita_decisao` dizia que a `decisao` é a
fonte jurídica de **todo** sucessor; a regularização não tem decisão recursal, e a saída fácil seria
admitir sucessor sem fonte. Isso destruiria a garantia que aquela constraint existe para dar — e
sucessor sem fonte é um Resultado que muda a vida de alguém sem nada que o sustente.

**Ficam em `integration/` e não em `unit/`**, ao contrário do que o `tasks.md` escreveu: o que se
prende aqui é o comportamento de `CHECK` e de gatilho, e os dois moram no banco.
"""

from datetime import timedelta
from uuid import uuid4

import pytest
from django.db import DatabaseError, IntegrityError, connection, transaction

from processo_seletivo.convocacao.application.desfechar import desfechar
from processo_seletivo.convocacao.domain import nomes
from processo_seletivo.resultados.models import ResultadoEtapa
from tests.fixtures.convocacao import convocar, montar_cenario_da_convocacao
from tests.fixtures.corte import ENTREVISTA

postgresql_only = pytest.mark.skipif(
    connection.vendor != "postgresql", reason="gatilho e CHECK existem só no PostgreSQL"
)
pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.integration, postgresql_only]


@pytest.fixture
def cenario(db, gestor, api_client, manager_headers, process_payload, raiz_de_arquivos):
    """O segundo classificado está **indeferido**, e dentro da faixa: é quem se regulariza."""
    return montar_cenario_da_convocacao(
        gestor,
        api_client,
        manager_headers,
        process_payload,
        prefixo="origem-019",
        indeferidas=(1,),
    )


@pytest.fixture
def indeferido(cenario):
    """O Resultado indeferido vigente, que é o que a regularização sucede."""
    edital, _, inscricoes = cenario
    return ResultadoEtapa.vigentes.get(inscricao=inscricoes[1], edital=edital, etapa_id=ENTREVISTA)


def sucessor(indeferido, **overrides):
    """Um sucessor por regularização, com o que o chamador quiser trocar."""
    campos = {
        "inscricao": indeferido.inscricao,
        "edital": indeferido.edital,
        "etapa_id": indeferido.etapa_id,
        "origem": ResultadoEtapa.Origem.REGULARIZACAO,
        "versao": indeferido.versao,
        "consequencia": ResultadoEtapa.Consequencia.HABILITADA,
        "motivo": "Documentação regularizada no prazo",
        "consolidado_em": indeferido.consolidado_em + timedelta(minutes=1),
        "consolidado_por": "teste",
        "resultado_anterior": indeferido,
        "motivo_da_superacao": "Regularização registrada",
        "desfecho_de_convocacao_id": uuid4(),
    }
    campos.update(overrides)
    return ResultadoEtapa.objects.create(**campos)


class TestAsQuatroLinhasAntigasSeguemValidas:
    def test_a_raiz_por_ocorrencia_continua_entrando(self, cenario):
        """A linha que o cenário monta a cada teste — se ela caísse, tudo cairia junto."""
        edital, _, _ = cenario

        assert ResultadoEtapa.objects.filter(
            edital=edital, origem=ResultadoEtapa.Origem.OCORRENCIA
        ).exists()

    def test_o_sucessor_sem_fonte_juridica_continua_recusado(self, cenario, indeferido):
        """**A garantia que a `R-005` existe para preservar.**

        Sem decisão e sem desfecho, o sucessor é um Resultado que muda a habilitação de alguém e não
        cita nada que o sustente. Afrouxar a constraint para admitir a regularização teria aberto
        exatamente esta porta.
        """
        with pytest.raises((IntegrityError, DatabaseError)), transaction.atomic():
            sucessor(indeferido, desfecho_de_convocacao_id=None)

    def test_o_sucessor_nao_cita_as_duas_fontes_ao_mesmo_tempo(self, cenario, indeferido):
        """Uma fonte, e exatamente uma: citar as duas afirmaria dois fundamentos para um ato só.

        E seria pior que redundante: a *non reformatio in peius* da `018` compara contra o
        Resultado que a decisão protegeu, e um sucessor que cita decisão **e** desfecho poderia
        estar sendo conferido contra o fundamento errado.
        """
        from processo_seletivo.resultados.models import ResultadoEtapa as Resultado
        from tests.fixtures.recursos import admitir, decidir, interpor

        recurso = interpor(
            inscricao=indeferido.inscricao, versao=indeferido.versao, resultado=indeferido
        )
        admitir(recurso)
        decisao = decidir(
            recurso,
            protegido=indeferido,
            consequencia=Resultado.Consequencia.HABILITADA,
            versao=indeferido.versao,
        )

        with pytest.raises((IntegrityError, DatabaseError)), transaction.atomic():
            sucessor(indeferido, decisao=decisao)


class TestAQuintaLinha:
    def test_o_sucessor_por_regularizacao_entra_com_o_desfecho_como_fonte(
        self, cenario, indeferido
    ):
        linha = sucessor(indeferido)

        assert linha.origem == ResultadoEtapa.Origem.REGULARIZACAO
        assert linha.decisao_id is None
        assert linha.desfecho_de_convocacao_id is not None
        assert linha.resultado_anterior_id == indeferido.id

    def test_a_raiz_por_regularizacao_e_recusada(self, cenario, indeferido):
        """Regularizar é **suceder** um indeferimento: sem anterior não há o que regularizar."""
        with pytest.raises((IntegrityError, DatabaseError)), transaction.atomic():
            sucessor(indeferido, resultado_anterior=None, motivo_da_superacao="")

    def test_o_sucessor_por_regularizacao_nao_cita_avaliacao(self, cenario, indeferido):
        """Ninguém avaliou nada aqui: a pessoa entregou o que faltava, e isso foi constatado.

        **A constraint diz isso por forma**, e não só o gatilho: `ck_resultado_origem` exige
        `avaliacao` nula no ramo da regularização, do mesmo modo que exige no ramo do recurso.
        """
        condicao = next(
            c.condition for c in ResultadoEtapa._meta.constraints if c.name == "ck_resultado_origem"
        )

        assert "REGULARIZACAO" in str(condicao)
        assert str(condicao).count("avaliacao__isnull") >= 3

    def test_a_regularizacao_nao_pode_eliminar(self, cenario, indeferido):
        """**Corrigir não pode piorar a situação de ninguém.**

        Um sucessor por regularização que eliminasse afirmaria que a pessoa entregou o que faltava
        e ficou pior — e o Resultado é append-only: o erro entraria uma vez e ficaria.
        """
        with pytest.raises(DatabaseError, match="must habilitate"), transaction.atomic():
            sucessor(indeferido, consequencia=ResultadoEtapa.Consequencia.ELIMINADA)

    def test_o_ramo_da_regularizacao_confere_a_versao_contra_o_edital(self):
        """Sem Avaliação não há de onde a versão vir copiada, e esta é a conferência que sobra.

        Sem ela a proveniência do ramo seria promessa de código — que é o que estes gatilhos
        existem para negar. A asserção é sobre o SQL instalado porque o caso negativo exigiria um
        segundo Edital publicado só para provar uma linha que os outros três ramos já exercitam.
        """
        from pathlib import Path

        sql = Path("processo_seletivo/resultados/migrations/0006_regularizacao.py").read_text(
            encoding="utf-8"
        )
        ramo = sql[sql.index("IF NEW.origem = 'REGULARIZACAO' THEN") :]
        ramo = ramo[: ramo.index("RETURN NEW;")]

        assert "another edital" in ramo
        assert "must habilitate" in ramo
        assert "must not cite an appeal decision" in ramo

    def test_a_regularizacao_nao_apaga_o_indeferimento(self, cenario, indeferido):
        """**Nada é excluído** (Constituição, Princípio II): a linha anterior permanece legível.

        É ela que explica por que houve convocação para regularizar — e sem ela o histórico diria
        que a pessoa sempre esteve habilitada.
        """
        linha = sucessor(indeferido)

        indeferido.refresh_from_db()
        assert indeferido.consequencia == ResultadoEtapa.Consequencia.ELIMINADA
        assert indeferido.motivo
        assert linha.resultado_anterior_id == indeferido.id


def test_o_desfecho_de_regularizacao_produz_o_sucessor_na_mesma_transacao(
    cenario, gestor, indeferido
):
    """`D-008` do começo ao fim: o ato da `019` grava o Resultado pelo mecanismo da `018`.

    **E o indeferido continua existindo, sucedido.** Nada é apagado: a linha anterior permanece
    legível, com o motivo do indeferimento, e é ela que explica por que houve convocação para
    regularizar.
    """
    edital, _, _ = cenario
    convocada = convocar(
        edital,
        gestor,
        indeferido.inscricao_id,
        especie=nomes.PARA_REGULARIZAR,
        idempotency_key="reg-convoca",
    )

    declarado = desfechar(
        actor=gestor,
        processo_id=edital.processo_id,
        convocacao_id=convocada["id"],
        especie=nomes.REGULARIZACAO,
        fundamento="Documentação regularizada no prazo do item 8.2.",
        idempotency_key="reg-desfecho",
        correlation_id="teste-convocacao-019",
    )

    linha = ResultadoEtapa.objects.get(resultado_anterior=indeferido)
    assert linha.origem == ResultadoEtapa.Origem.REGULARIZACAO
    assert linha.consequencia == ResultadoEtapa.Consequencia.HABILITADA
    assert str(linha.desfecho_de_convocacao_id) == declarado["id"]
    assert declarado["efeito"] == "INCLUSAO", "a regularização inclui na contagem"
    indeferido.refresh_from_db()
    assert indeferido.consequencia == ResultadoEtapa.Consequencia.ELIMINADA
