"""Duas primeiras gravações **de verdade simultâneas**, na mesma Atribuição.

A Avaliação nasce no primeiro salvamento, e o `OneToOne` com a Atribuição é único. "Consultar e
depois criar" perde essa corrida: as duas transações não veem a linha da outra, as duas tentam
inserir, e uma recebe `IntegrityError` — erro interno onde a pessoa deveria ler que a revisão
ficou obsoleta.

O teste roda em duas threads reais, com `transaction=True` para que cada uma tenha a sua conexão e
o seu commit. Sem isso, a corrida não acontece: o `django_db` comum compartilha uma transação, e
as duas gravações seriam sequenciais no mesmo snapshot.
"""

import threading

import pytest
from django.db import connection

from processo_seletivo.avaliacoes.application.avaliacao import gravar
from processo_seletivo.avaliacoes.application.distribuicao import distribuir
from processo_seletivo.avaliacoes.models import Avaliacao
from processo_seletivo.comissoes.domain.funcoes import Funcao
from processo_seletivo.shared.api.problems import DomainError
from tests.conftest import ator_institucional, encerrar_conexoes_da_thread
from tests.fixtures.comissao import ETAPA_A1, alocar_em, constituir, inscrever
from tests.fixtures.edital import identificador

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.integration]

# Estas corridas exigem PostgreSQL, e a marca não é burocracia: `select_for_update` é inócuo em
# SQLite, e o banco em memória serializa as threads com "database table is locked". Sem a marca o
# teste não prova o invariante em SQLite — ele quebra, e por um motivo que não tem relação nenhuma
# com o que ele existe para proteger.
postgresql_only = pytest.mark.skipif(
    connection.vendor != "postgresql", reason="a corrida exige as travas do PostgreSQL"
)

SEED = 7


@pytest.fixture
def cenario(gestor, api_client, manager_headers):
    from tests.fixtures.comissao import publicar_processo_com_etapas

    edital = publicar_processo_com_etapas(
        api_client,
        {**manager_headers, "HTTP_IDEMPOTENCY_KEY": "mvp-test-key-0071"},
        {
            "institutionalCode": "PS-2026-071",
            "title": "Processo concorrente",
            "firstEdital": {"number": "71", "year": 2026, "title": "Edital concorrente"},
        },
        seed=SEED,
        maxima="100.0000",
    )
    etapa = identificador(ETAPA_A1, SEED)
    processo = edital.processo
    membros = constituir(
        gestor, processo, [("maria", Funcao.PRESIDENTE), ("joao", Funcao.MEMBRO)], prefixo="cc"
    )
    alocar_em(gestor, processo, membros["joao"], edital, etapa)
    inscricao = inscrever(edital, 1, primeiro=700)[0]
    distribuir(
        actor=gestor,
        processo_id=processo.id,
        edital_id=edital.id,
        etapa_id=etapa,
        membro_ids=[membros["joao"].id],
        inscricao_ids=[inscricao.id],
        idempotency_key="cc",
        correlation_id="teste",
    )
    return {"edital": edital, "etapa": etapa, "inscricao": inscricao}


@postgresql_only
def test_duas_primeiras_gravacoes_simultaneas_nao_produzem_erro_interno(cenario):
    """Uma vence; a outra recebe **recusa por revisão obsoleta**, e não `IntegrityError`."""
    partida = threading.Barrier(2)
    desfechos = []

    def gravar_como(parecer):
        partida.wait(timeout=5)
        try:
            gravar(
                ator=ator_institucional("joao"),
                edital=cenario["edital"],
                etapa_id=cenario["etapa"],
                inscricao_id=cenario["inscricao"].id,
                pontuacao="80",
                parecer=parecer,
                expected_revision=1,
                correlation_id="teste",
            )
            desfechos.append(("ok", parecer))
        except DomainError as recusa:
            desfechos.append(("recusa", recusa.code))
        except Exception as erro:  # noqa: BLE001 — é justamente o que não pode acontecer
            desfechos.append(("erro", type(erro).__name__))
        finally:
            encerrar_conexoes_da_thread()

    fios = [threading.Thread(target=gravar_como, args=(texto,)) for texto in ("A", "B")]
    for fio in fios:
        fio.start()
    for fio in fios:
        fio.join(timeout=10)

    tipos = [tipo for tipo, _ in desfechos]
    assert "erro" not in tipos, desfechos
    assert tipos.count("ok") == 1, desfechos
    # A que perdeu perdeu por revisão — que é a recusa que a pessoa entende e sabe corrigir.
    assert [codigo for tipo, codigo in desfechos if tipo == "recusa"] == ["stale_revision"]
    assert Avaliacao.objects.filter(atribuicao__inscricao=cenario["inscricao"]).count() == 1
