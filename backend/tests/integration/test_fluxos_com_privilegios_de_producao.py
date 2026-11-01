"""Fluxos de fumaça com os privilégios da role de produção (A-02 da auditoria de 31/10/2026).

**O que estes casos procuram** é a classe de defeito que passa como superusuário e falha em
produção: travar linha append-only (`FOR UPDATE`/`FOR SHARE` pedem `UPDATE`), escrever em tabela que
a política deixou sem privilégio, `TRUNCATE`, `setval`, desligar gatilho. A suíte inteira roda como
superusuário e nada disso aparece nela; aqui, um ato por fluxo roda sob `SET ROLE` da role de
conformidade, provisionada pela política real (`tests/fixtures/papel_de_producao.py`).

**Não é a suíte em dois perfis.** O cenário é montado como superusuário pelas fixtures de sempre, e
só o ato examinado roda como produção. O domínio de cada ato tem os seus próprios testes; o que
estes afirmam é o mínimo para provar que o ato **se consumou** — e não só que não deu erro.

Os sete fluxos são os que a auditoria nomeou: publicar Edital, consolidar, emitir ordem, julgar com
efeito, convocar e registrar desfecho, conceder e revogar acesso, registrar unidade. O julgamento
tem o arquivo próprio, com as espécies e a concorrência (`recursos/test_julgar_como_producao.py`);
aqui fica o caso de fumaça da correção fixada.
"""

from decimal import Decimal

import pytest
from django.db import connection

from processo_seletivo.auditoria.models import RegistroAuditoria
from processo_seletivo.publicacoes.models import Publicacao
from processo_seletivo.resultados.models import ResultadoEtapa
from tests.conftest import ator_institucional
from tests.fixtures.papel_de_producao import como_producao  # noqa: F401

postgresql_only = pytest.mark.skipif(
    connection.vendor != "postgresql", reason="privilégios validados somente em PostgreSQL"
)

pytestmark = [pytest.mark.django_db, pytest.mark.integration, postgresql_only]


def _travar_um_resultado():
    from django.db import transaction

    with transaction.atomic(), connection.cursor() as cursor:
        cursor.execute("SELECT id FROM resultados_resultadoetapa FOR UPDATE")


@pytest.mark.trava_deliberada
def test_a_fixture_nega_o_que_a_producao_nega(como_producao):  # noqa: F811
    """A fixture prova alguma coisa: sob ela, a trava do A-01 é recusada, e fora dela, não."""
    from django.db.utils import ProgrammingError

    from tests.integration.test_database_permissions import RUNTIME_ROLE

    _travar_um_resultado()
    with como_producao():
        with connection.cursor() as cursor:
            cursor.execute("SELECT current_user, session_user")
            atual, sessao = cursor.fetchone()
        with pytest.raises(ProgrammingError, match="permission denied"):
            _travar_um_resultado()
    assert atual == RUNTIME_ROLE and sessao != RUNTIME_ROLE
    _travar_um_resultado()


@pytest.mark.django_db(transaction=True)
@pytest.mark.trava_deliberada
def test_a_fixture_nega_tambem_nos_casos_transacionais(como_producao):  # noqa: F811
    from django.db.utils import ProgrammingError

    with como_producao(), pytest.raises(ProgrammingError, match="permission denied"):
        _travar_um_resultado()
    _travar_um_resultado()


def test_publicar_edital(api_client, manager_headers, process_payload, como_producao):  # noqa: F811
    """O percurso inteiro, pela API: criar, rascunho, submissão, homologação e publicação."""
    from tests.fixtures.publicacao import publish_original

    with como_producao():
        edital = publish_original(api_client, manager_headers, process_payload)

    assert Publicacao.objects.filter(edital=edital).count() == 1


def test_consolidar_resultado(gestor, api_client, manager_headers, como_producao):  # noqa: F811
    from processo_seletivo.resultados.application.consolidacao import consolidar
    from tests.fixtures.comissao import inscrever
    from tests.fixtures.mesa import concluir_como, distribuir_para
    from tests.fixtures.resultado import montar_etapa_de_leitura_unica

    cenario = montar_etapa_de_leitura_unica(
        gestor, api_client, manager_headers, seed=702, codigo="0702"
    )
    inscricao = inscrever(cenario["edital"], 1, primeiro=1)[0]
    distribuir_para(cenario, gestor, ["joao"], [inscricao], chave="lote-0702")
    concluir_como(cenario, "joao", inscricao, pontuacao="75")

    with como_producao():
        feito = consolidar(
            actor=ator_institucional("maria"),
            processo_id=cenario["processo"].id,
            edital_id=cenario["edital"].id,
            etapa_id=cenario["primeira"],
            inscricao_ids=[inscricao.id],
            idempotency_key="consolidar-como-producao",
            correlation_id="teste",
        )

    assert feito["feitas"] == 1
    assert ResultadoEtapa.vigentes.filter(inscricao=inscricao).count() == 1


def test_emitir_ordem(gestor, api_client, manager_headers, process_payload, como_producao):  # noqa: F811
    from processo_seletivo.classificacao.application.calculo import calcular_ordem
    from processo_seletivo.classificacao.application.emissao import (
        assinatura_da_proposta,
        emitir_ordem,
    )
    from processo_seletivo.classificacao.models import AtoDeOrdenacao
    from tests.fixtures.corte import MARCO, montar_cenario_do_corte
    from tests.fixtures.edital import PROFILE_ID

    edital, _, _ = montar_cenario_do_corte(
        gestor,
        api_client,
        manager_headers,
        process_payload,
        emitir_a_ordem=False,
        prefixo="ordem-como-producao",
    )
    confirmacao = assinatura_da_proposta(
        calcular_ordem(edital=edital, perfil_id=PROFILE_ID, marco_id=MARCO)
    )

    with como_producao():
        emitir_ordem(
            actor=gestor,
            processo_id=edital.processo_id,
            edital_id=edital.id,
            perfil_id=PROFILE_ID,
            marco_id=MARCO,
            idempotency_key="ordem-como-producao",
            correlation_id="teste",
            confirmacao_do_calculo=confirmacao,
        )

    assert AtoDeOrdenacao.objects.filter(edital=edital).count() == 1


def test_julgar_com_efeito(
    gestor,
    api_client,
    manager_headers,
    process_payload,
    como_producao,  # noqa: F811
):
    """O A-01: a correção fixada grava decisão e sucessor como a role de produção."""
    from processo_seletivo.recursos.application.julgar import julgar
    from processo_seletivo.recursos.models import DecisaoRecurso
    from tests.fixtures.recursos_us4 import cenario_julgavel, julgador

    peca = cenario_julgavel(
        gestor, api_client, manager_headers, process_payload, seed=703, codigo="0703"
    )

    with como_producao():
        decisao, sucessor = julgar(
            actor=julgador(),
            recurso_id=peca["recurso"].id,
            especie=DecisaoRecurso.Especie.CORRECAO_FIXADA,
            motivacao="O parecer não enfrentou o documento juntado na inscrição.",
            etapa_id=peca["cenario"]["etapa"],
            pontuacao=Decimal("82.0000"),
            assinatura_do_resultado=str(peca["superado"].id),
            idempotency_key="julgar-fumaca",
        )

    assert sucessor.decisao_id == decisao.id
    assert sucessor.resultado_anterior_id == peca["superado"].id


def test_convocar_e_registrar_desfecho(
    gestor,
    api_client,
    manager_headers,
    process_payload,
    raiz_de_arquivos,
    como_producao,  # noqa: F811
):
    from processo_seletivo.convocacao.application import selectors
    from processo_seletivo.convocacao.application.desfechar import desfechar
    from processo_seletivo.convocacao.domain import nomes
    from processo_seletivo.convocacao.models import DesfechoDaConvocacao
    from tests.fixtures.convocacao import convocar, montar_cenario_da_convocacao
    from tests.fixtures.corte import MARCO
    from tests.fixtures.edital import PROFILE_ID

    edital, _, _ = montar_cenario_da_convocacao(
        gestor, api_client, manager_headers, process_payload, prefixo="convocacao-como-producao"
    )
    primeira = selectors.contexto_do_recorte(
        edital=edital, perfil_id=PROFILE_ID, marco_id=MARCO, lista_id=None
    )["fila"][0]

    with como_producao():
        convocada = convocar(edital, gestor, primeira, idempotency_key="convocar-como-producao")
        desfechar(
            actor=gestor,
            processo_id=edital.processo_id,
            convocacao_id=convocada["id"],
            especie=nomes.DESISTENCIA_EXPRESSA,
            fundamento="Desistiu por escrito.",
            idempotency_key="desfecho-como-producao",
            correlation_id="teste",
        )

    assert DesfechoDaConvocacao.objects.filter(convocacao_id=convocada["id"]).count() == 1


def test_conceder_e_revogar_acesso(como_producao):  # noqa: F811
    """A revogação da `106` foi a primeira desta classe: travava o vínculo, que é append-only."""
    from processo_seletivo.seguranca import acessos as catalogo
    from processo_seletivo.seguranca.application import acessos
    from processo_seletivo.seguranca.domain import Actor
    from processo_seletivo.seguranca.models import RevogacaoDeVinculo
    from tests.seguranca.apoio import AGORA, pessoa, vincular

    administradora = pessoa("admin-cefor")
    vincular(administradora, "cefor", catalogo.ADMINISTRADOR_DE_ACESSOS)
    ator = Actor(
        administradora.username,
        "cefor",
        acessos.permissoes_dos_papeis([catalogo.ADMINISTRADOR_DE_ACESSOS]),
    )
    paulo = pessoa("paulo")

    with como_producao():
        vinculo = acessos.conceder(
            ator, pessoa=paulo, escopo="cefor", papel="elaborador", motivo="Portaria 1", now=AGORA
        )
        acessos.revogar(ator, vinculo=vinculo, motivo="Fim do mandato", now=AGORA)

    assert RevogacaoDeVinculo.objects.filter(vinculo=vinculo).count() == 1


def test_registrar_unidade(como_producao):  # noqa: F811
    from processo_seletivo.seguranca.domain import Actor
    from processo_seletivo.unidades.application import registro
    from processo_seletivo.unidades.models import Unidade

    administradora = Actor(
        "pessoa-administradora",
        "institucional",
        frozenset({"acesso:administrar", "unidade:administrar"}),
    )

    with como_producao():
        registro.registrar(
            administradora,
            campos={
                "codigo": "serra",
                "sigla": "Serra",
                "nome": "Campus Serra",
                "cabecalho": ["Campus Serra"],
                "local": "Serra (ES)",
                "atendimento": "atendimento@serra.example",
            },
            motivo="Portaria nº 1/2026",
        )

    assert Unidade.objects.filter(codigo="serra").exists()
    assert RegistroAuditoria.objects.filter(aggregate_type="Unidade").exists()
