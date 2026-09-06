"""O comando de publicar: o que ele grava, o que ele recusa e o que ele **não** dispara.

As quatro frentes de concorrência aparecem aqui em três testes, e a quarta — a emissão concorrente
— tem arquivo próprio, porque exige duas transações de verdade.
"""

import json

import pytest
from django.db import connection

from processo_seletivo.divulgacao.application.publicar import (
    PUBLICAR,
    assinatura_da_previa,
    publicar_resultado,
)
from processo_seletivo.divulgacao.domain.conteudo import compor
from processo_seletivo.divulgacao.models import PublicacaoResultado, SituacaoDivulgada
from processo_seletivo.shared.api.problems import DomainError
from tests.fixtures.divulgacao import (
    ator_publicador,
    emitir,
    montar_ato_publicavel,
    publicar_o_ato,
)

pytestmark = [pytest.mark.integration, pytest.mark.django_db(transaction=True)]


@pytest.fixture
def cenario(gestor, api_client, manager_headers, process_payload):
    return montar_ato_publicavel(
        gestor,
        api_client,
        manager_headers,
        process_payload,
        seed=53,
        codigo="0753",
        pontuacoes=("90.0000", "70.0000", None),
        primeiro=401,
    )


def _publicar(cenario, **campos):
    return publicar_o_ato(cenario, **campos)


def test_a_publicacao_nasce_com_autor_instante_e_signatario(cenario):
    """SC-003: o ato registra quem publicou, quando, e quem assinou institucionalmente."""
    publicacao = _publicar(cenario, chave="publicar-0753-a")

    assert publicacao.publicado_por == "paula.publicadora"
    assert publicacao.publicado_em is not None
    assert publicacao.signatario_nome == "Diretora do Cefor"
    assert publicacao.signatario_cargo.startswith("Diretora-Geral")
    assert publicacao.signatario_id is not None
    assert publicacao.publicacao_anterior is None, "a primeira divulgação do marco é a raiz"


def test_nasce_uma_situacao_por_participante_considerado(cenario):
    """Inclusive quem não recebeu posição: é ela que a Área do Candidato lê (FR-059)."""
    publicacao = _publicar(cenario, chave="publicar-0753-b")

    situacoes = list(publicacao.situacoes.all())
    assert len(situacoes) == 3
    assert sorted(item.situacao for item in situacoes) == [
        SituacaoDivulgada.Situacao.CLASSIFICADA,
        SituacaoDivulgada.Situacao.CLASSIFICADA,
        SituacaoDivulgada.Situacao.SEM_POSICAO,
    ]
    classificadas = [item for item in situacoes if item.posicao is not None]
    assert sorted(item.posicao for item in classificadas) == [1, 2]
    assert all(item.pontuacao for item in classificadas)


def test_a_trilha_registra_ator_entidade_instante_e_versao(cenario):
    """Na trilha existente, e sem tabela de eventos própria (FR-066, SC-017).

    **A versão normativa citada pelo ato é dos quatro o que o nome do teste prometia e a asserção
    não cobria.** Sem ela, quem audita sabe que a divulgação aconteceu e não sabe sob qual norma —
    que é justamente o que torna o resultado reproduzível.
    """
    from processo_seletivo.auditoria.models import RegistroAuditoria

    publicacao = _publicar(cenario, chave="publicar-0753-c")

    registro = RegistroAuditoria.objects.get(operation=PUBLICAR, aggregate_id=publicacao.id)
    assert registro.actor_subject == "paula.publicadora"
    assert registro.permission == "resultado:publicar"
    assert registro.aggregate_type == "PublicacaoResultado"
    assert registro.aggregate_id == publicacao.id
    assert registro.occurred_at == publicacao.publicado_em
    assert str(cenario["ato"].versao_id) in registro.reason, (
        "a versão normativa que o ato citava precisa aparecer na trilha (FR-066, SC-017)"
    )
    assert registro.correlation_id == "fixture"


def test_a_trilha_da_sucessao_diz_o_que_foi_sucedido(cenario):
    """Divulgar e substituir o divulgado são atos diferentes, e a trilha os separa (FR-066)."""
    from processo_seletivo.auditoria.models import RegistroAuditoria

    primeira = _publicar(cenario, chave="publicar-0753-suc1", natureza="PRELIMINAR")
    segunda = _publicar(cenario, chave="publicar-0753-suc2", natureza="DEFINITIVA")

    da_primeira = RegistroAuditoria.objects.get(operation=PUBLICAR, aggregate_id=primeira.id)
    da_segunda = RegistroAuditoria.objects.get(operation=PUBLICAR, aggregate_id=segunda.id)

    assert "sucedendo" not in da_primeira.reason, "a raiz da cadeia não sucede nada"
    assert str(primeira.id) in da_segunda.reason
    assert str(cenario["ato"].versao_id) in da_segunda.reason


def test_publicar_nao_exige_ato_administrativo(cenario):
    """Publicar não exige motivo: a sucessão já carrega o dela no ato de origem (FR-067)."""
    from processo_seletivo.processos.models import AtoAdministrativo

    publicacao = _publicar(cenario, chave="publicar-0753-d")

    assert not AtoAdministrativo.objects.filter(aggregate_id=publicacao.id).exists()


def test_publicar_nao_dispara_mensagem_de_especie_alguma(cenario, mailoutbox):
    """FR-072: divulgar é ato público, e não notificação individual — nada é enviado."""
    _publicar(cenario, chave="publicar-0753-e")

    assert mailoutbox == []


def test_a_mesma_chave_repetida_devolve_a_primeira_publicacao(cenario):
    """SC-013: o duplo submit devolve o desfecho do primeiro pedido, e não cria a segunda.

    O reenvio manda **exatamente** o mesmo formulário — mesma chave, mesma assinatura, mesma
    natureza —, que é o que o navegador faz quando alguém clica duas vezes. Recompor a assinatura
    antes do segundo envio simularia outra coisa: um pedido novo, e não uma repetição.
    """
    pedido = {
        "actor": ator_publicador(),
        "processo_id": cenario["edital"].processo_id,
        "edital_id": cenario["edital"].id,
        "marco_id": cenario["marco"],
        "ato_id": cenario["ato"].id,
        "natureza": "PRELIMINAR",
        "autoridade": "diretoria-cefor",
        "confirmacao_da_previa": assinatura_da_previa(
            ato=cenario["ato"], publicacao_anterior=None, projecao=compor(cenario["ato"])
        ),
        "idempotency_key": "publicar-0753-idem",
        "correlation_id": "teste",
    }
    primeira = publicar_resultado(**pedido)
    segunda = publicar_resultado(**pedido)

    assert primeira.id == segunda.id
    assert PublicacaoResultado.objects.filter(ato=cenario["ato"]).count() == 1


def test_duas_chaves_diferentes_sobre_o_mesmo_ato_e_natureza_sao_recusadas(cenario):
    """SC-021: o caso das duas abas, que a idempotência sozinha **não** pega (FR-039).

    A idempotência responde ao mesmo pedido repetido; este são dois pedidos distintos sobre o mesmo
    ato e a mesma natureza. Quem responde é `uq_publicacao_por_ato_natureza` — garantia de banco, e
    não de aplicação.
    """
    _publicar(cenario, chave="publicar-0753-aba-1")

    with pytest.raises(DomainError) as recusa:
        _publicar(cenario, chave="publicar-0753-aba-2")

    assert recusa.value.code == "publication_already_exists"
    assert recusa.value.status == 409
    assert PublicacaoResultado.objects.filter(ato=cenario["ato"]).count() == 1


def test_o_mesmo_ato_na_outra_natureza_produz_a_segunda_publicacao(cenario):
    """FR-041: o preliminar que ninguém contestou vira definitivo **sem** ato novo a emitir.

    Exigir a emissão de um sucessor idêntico faria a 015 registrar uma sucessão que não sucedeu
    nada. A segunda publicação sucede a primeira, e a cadeia continua sendo uma só.
    """
    preliminar = _publicar(cenario, chave="publicar-0753-p", natureza="PRELIMINAR")
    definitiva = _publicar(cenario, chave="publicar-0753-d2", natureza="DEFINITIVA")

    assert definitiva.publicacao_anterior_id == preliminar.id
    assert PublicacaoResultado.objects.filter(ato=cenario["ato"]).count() == 2


def test_a_preliminar_nao_sucede_a_definitiva(cenario):
    """A ordem entre naturezas tem sentido único, e a recusa é nomeada (D-007)."""
    _publicar(cenario, chave="publicar-0753-def", natureza="DEFINITIVA")

    with pytest.raises(DomainError) as recusa:
        _publicar(cenario, chave="publicar-0753-pre", natureza="PRELIMINAR")

    assert recusa.value.code == "publication_nature_regresses"


def test_a_confirmacao_calculada_sobre_outra_projecao_e_recusada(cenario):
    """FR-031: a projeção mudou entre ler e confirmar."""
    with pytest.raises(DomainError) as recusa:
        publicar_resultado(
            actor=ator_publicador(),
            processo_id=cenario["edital"].processo_id,
            edital_id=cenario["edital"].id,
            marco_id=cenario["marco"],
            ato_id=cenario["ato"].id,
            natureza="PRELIMINAR",
            autoridade="diretoria-cefor",
            confirmacao_da_previa="0" * 64,
            idempotency_key="publicar-0753-falsa",
            correlation_id="teste",
        )

    assert recusa.value.code == "publication_preview_stale"
    assert recusa.value.status == 409
    assert not PublicacaoResultado.objects.filter(ato=cenario["ato"]).exists()


def test_a_confirmacao_da_outra_ponta_da_cadeia_e_recusada(cenario):
    """O caso que `publicacao_anterior_id` dentro da assinatura existe para cobrir.

    Alguém lê a prévia quando o marco ainda não tinha divulgação; outra pessoa publica; a primeira
    confirma. A cadeia mudou, e a confirmação é recusada **com a mensagem da prévia obsoleta** — e
    não pela constraint de raiz, que diria outra coisa sobre o mesmo fato.
    """
    projecao = compor(cenario["ato"])
    da_leitura_antiga = assinatura_da_previa(
        ato=cenario["ato"], publicacao_anterior=None, projecao=projecao
    )
    _publicar(cenario, chave="publicar-0753-outra", natureza="PRELIMINAR")

    with pytest.raises(DomainError) as recusa:
        publicar_resultado(
            actor=ator_publicador(),
            processo_id=cenario["edital"].processo_id,
            edital_id=cenario["edital"].id,
            marco_id=cenario["marco"],
            ato_id=cenario["ato"].id,
            natureza="DEFINITIVA",
            autoridade="diretoria-cefor",
            confirmacao_da_previa=da_leitura_antiga,
            idempotency_key="publicar-0753-tarde",
            correlation_id="teste",
        )

    assert recusa.value.code == "publication_preview_stale"


def test_a_assinatura_da_previa_nao_contem_o_instante(cenario):
    """Ela é calculada antes de o ato existir, e o instante só existe depois dele (FR-031).

    Ela também não muda com a natureza nem com a autoridade: as duas são escolha do operador,
    submetidas no mesmo pedido, e não têm leitura anterior a comparar.
    """
    projecao = compor(cenario["ato"])
    assinatura = assinatura_da_previa(
        ato=cenario["ato"], publicacao_anterior=None, projecao=projecao
    )
    publicacao = _publicar(cenario, chave="publicar-0753-inst")

    assert assinatura != publicacao.conteudo_publico_hash
    conteudo = json.loads(bytes(publicacao.conteudo_publico).decode())
    assert conteudo["cabecalho"]["publicado_em"], "o conteúdo final **tem** o instante"
    # A mesma assinatura, recalculada agora sobre a mesma leitura, continua a mesma.
    assert assinatura == assinatura_da_previa(
        ato=cenario["ato"], publicacao_anterior=None, projecao=projecao
    )


def test_a_autoridade_fora_do_catalogo_e_recusada(cenario):
    """O identificador nunca é digitado: a escolha vem do catálogo (FR-029)."""
    projecao = compor(cenario["ato"])

    with pytest.raises(DomainError) as recusa:
        publicar_resultado(
            actor=ator_publicador(),
            processo_id=cenario["edital"].processo_id,
            edital_id=cenario["edital"].id,
            marco_id=cenario["marco"],
            ato_id=cenario["ato"].id,
            natureza="PRELIMINAR",
            autoridade="prefeitura-de-outro-lugar",
            confirmacao_da_previa=assinatura_da_previa(
                ato=cenario["ato"], publicacao_anterior=None, projecao=projecao
            ),
            idempotency_key="publicar-0753-autoridade",
            correlation_id="teste",
        )

    assert recusa.value.code == "publication_authority_required"


def test_o_ato_sucedido_nao_e_publicavel_pelo_comando(cenario, gestor):
    """A aferição corre **dentro** da transação, e não só na tela (FR-004)."""
    antigo = cenario["ato"]
    emitir(cenario, gestor, chave="emitir-0753-b", motivo="Resultado tardio.")
    projecao = compor(antigo)

    with pytest.raises(DomainError) as recusa:
        publicar_resultado(
            actor=ator_publicador(),
            processo_id=cenario["edital"].processo_id,
            edital_id=cenario["edital"].id,
            marco_id=cenario["marco"],
            ato_id=antigo.id,
            natureza="PRELIMINAR",
            autoridade="diretoria-cefor",
            confirmacao_da_previa=assinatura_da_previa(
                ato=antigo, publicacao_anterior=None, projecao=projecao
            ),
            idempotency_key="publicar-0753-sucedido",
            correlation_id="teste",
        )

    assert recusa.value.code == "publication_act_superseded"


@pytest.mark.skipif(
    not connection.features.has_select_for_update,
    reason="`FOR UPDATE` é do PostgreSQL; o backend padrão da suíte o omite da consulta.",
)
def test_o_comando_toma_a_linha_do_processo_antes_de_aferir(cenario):
    """T-005: sem o bloqueio, publicar e emitir correm em paralelo.

    A prova de comportamento está em `test_concorrencia.py`, com duas transações de verdade. Aqui
    se afirma o **mecanismo**: a transação emite um `SELECT ... FOR UPDATE` sobre a linha do
    Processo, e ela é a mesma que `comando_de_comissao` toma.

    **O resto deste arquivo roda nos dois backends; este não.** A cláusula é escrita pelo
    compilador do PostgreSQL, e o SQLite simplesmente a omite — a asserção falharia por ausência da
    cláusula, e não por ausência do bloqueio. A condição é a capacidade do backend, e não o nome
    dele: é ela que a asserção de fato depende.
    """
    from django.test.utils import CaptureQueriesContext

    with CaptureQueriesContext(connection) as consultas:
        _publicar(cenario, chave="publicar-0753-lock")

    travas = [
        item["sql"]
        for item in consultas.captured_queries
        if "processos_processoseletivo" in item["sql"] and "FOR UPDATE" in item["sql"]
    ]
    assert travas, "publicar precisa tomar a linha do Processo, e tomá-la antes de aferir"


def test_o_documento_e_gravado_dentro_do_comando(cenario):
    """FR-062: o documento deriva do conteúdo já composto, na mesma transação."""
    publicacao = _publicar(cenario, chave="publicar-0753-doc")

    assert publicacao.documento.bytes
    assert publicacao.documento.content_type == "application/pdf"
    assert len(publicacao.documento.documento_hash) == 64


def test_retificacao_posterior_nao_altera_os_bytes_nem_regenera_o_documento(cenario, api_client):
    """FR-045 e SC-011: o ato praticado não é alcançado pelo que vem depois dele.

    Não porque alguém o proteja: porque **não há o que alcançar**. O conteúdo está gravado, e não
    recomposto na leitura.
    """
    from tests.fixtures.edital import caminho_perfil
    from tests.fixtures.publicacao import retify

    publicacao = _publicar(cenario, chave="publicar-0753-ret")
    conteudo_antes = bytes(publicacao.conteudo_publico)
    documento_antes = bytes(publicacao.documento.bytes)
    resumo_antes = publicacao.conteudo_publico_hash

    retify(
        api_client,
        cenario["edital"],
        [
            {
                "targetPath": caminho_perfil("immediateVacancies", 53),
                "operation": "REPLACE",
                "newValue": 7,
            }
        ],
        suffix="ret0753",
    )

    publicacao.refresh_from_db()
    assert bytes(publicacao.conteudo_publico) == conteudo_antes
    assert publicacao.conteudo_publico_hash == resumo_antes
    assert bytes(publicacao.documento.bytes) == documento_antes
