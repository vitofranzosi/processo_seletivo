"""Interpor recurso — o ato do candidato, e as quatro recusas que o antecedem.

A peça nasce ou não nasce; não há meio-termo. O que este módulo prende é **o que fica gravado**
quando ela nasce e **o que é recusado antes** de qualquer gravação:

```text
sem fundamentação            →  422, e nada é criado
objeto já sucedido           →  409, com o caminho para o vigente
segundo recurso do mesmo par →  409, nomeando o protocolo do primeiro
mesma chave, mesmo conteúdo  →  a primeira peça, de novo
mesma chave, outro conteúdo  →  409 de idempotência
```

**Publicação e `ResultadoEtapa` percorrem o mesmo fluxo** (D-001, FR-002), e o teste dos dois
objetos existe para que a simetria seja verificada e não apenas afirmada: é a diferença entre uma
capacidade com dois alvos e duas capacidades que se parecem.
"""

from decimal import Decimal

import pytest
from django.utils.timezone import now

from processo_seletivo.divulgacao.application.selectors import vigente_do_marco
from processo_seletivo.portal.identidade import IdentidadeDoCandidato
from processo_seletivo.publicacoes.application.selectors import selecao_publica
from processo_seletivo.recursos.application.interpor import interpor, objetos_recorriveis
from processo_seletivo.recursos.models import Recurso
from processo_seletivo.resultados.models import ResultadoEtapa
from processo_seletivo.shared.api.problems import DomainError
from tests.fixtures.divulgacao import emitir, montar_marco, pontuar, publicar_o_ato
from tests.fixtures.recursos import deferir_corrigindo

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.integration]


@pytest.fixture
def cenario(gestor, api_client, manager_headers, process_payload):
    """Duas pessoas pontuadas, o ato emitido e o marco publicado — o mínimo para haver recurso."""
    cenario = montar_marco(
        gestor, api_client, manager_headers, process_payload, seed=90, codigo="0790"
    )
    cenario["inscricoes"] = pontuar(
        cenario, gestor, ["90.0000", "70.0000"], primeiro=901, sufixo="90"
    )
    cenario["ato"] = emitir(cenario, gestor, chave="emitir-018-us2")
    publicar_o_ato(cenario, chave="publicar-018-us2")
    return cenario


def titular(inscricao):
    """A identidade da sessão que a view montaria — o comando só lê `subject` dela."""
    return IdentidadeDoCandidato(
        inscricao.identity_subject, inscricao.nome, inscricao.cpf_normalizado, "cand@ex.br"
    )


def resultado_de(cenario, inscricao):
    return ResultadoEtapa.vigentes.get(inscricao=inscricao, etapa_id=cenario["etapa"])


def publicacao_de(cenario):
    return vigente_do_marco(edital=cenario["edital"], marco_id=cenario["marco"])


def interponha(cenario, inscricao, *, alvo=None, fundamentacao="A nota não corresponde.", **extra):
    alvo = alvo or resultado_de(cenario, inscricao)
    campo = "publicacao" if alvo.__class__.__name__ == "PublicacaoResultado" else "resultado"
    argumentos = {
        "identidade": titular(inscricao),
        "inscricao": inscricao,
        campo: alvo,
        "fundamentacao": fundamentacao,
        "assinatura_do_objeto": str(alvo.pk),
        "idempotency_key": f"recurso-{inscricao.id}-{alvo.pk}",
    }
    return interpor(**{**argumentos, **extra})


# ---------------------------------------------------------------------------
# T040 — o que fica gravado
# ---------------------------------------------------------------------------


def test_a_peca_nasce_com_protocolo_instante_objeto_e_versao(cenario):
    """O que a peça grava é o que a torna oponível depois: quem, quando, contra o quê, sob qual
    regra. Faltando qualquer um, o recurso vira um texto sem endereço."""
    inscricao = cenario["inscricoes"][1]
    antes = now()

    peca = interponha(cenario, inscricao)

    assert peca.protocolo.startswith("REC-"), peca.protocolo
    assert peca.inscricao_id == inscricao.id
    assert peca.interposto_por == inscricao.identity_subject
    assert antes <= peca.interposto_em <= now()
    assert peca.resultado_atacado_id == resultado_de(cenario, inscricao).id
    assert peca.publicacao_atacada_id is None
    assert peca.versao_id == selecao_publica(edital_id=inscricao.edital_id).id


def test_o_protocolo_e_unico_entre_pecas(cenario):
    """Dois protocolos iguais tornariam a prova de interposição inútil para uma das pessoas."""
    primeira = interponha(cenario, cenario["inscricoes"][0])
    segunda = interponha(cenario, cenario["inscricoes"][1])

    assert primeira.protocolo != segunda.protocolo


def test_fundamentacao_vazia_e_recusada_e_nada_e_gravado(cenario):
    """Peça sem razão escrita não é peça: não há o que admitir nem o que julgar (FR-006).

    Espaço em branco também não é razão — e a recusa acontece **antes** de qualquer gravação, que
    é o que a contagem de peças prova.
    """
    inscricao = cenario["inscricoes"][1]

    with pytest.raises(DomainError) as recusa:
        interponha(cenario, inscricao, fundamentacao="   \n  ")

    assert recusa.value.code == "appeal_reason_required"
    assert recusa.value.status == 422
    assert not Recurso.objects.filter(inscricao=inscricao).exists()


def test_a_versao_gravada_nao_e_recalculada_na_leitura(cenario, api_client):
    """**A regra é a de ontem, e não a de hoje** (FR-024).

    Publicada uma Retificação depois da interposição, a seleção pública já responde outra versão —
    e a peça continua apontando para aquela sob a qual foi interposta. Recalcular na leitura
    responderia com a norma vigente hoje sobre um ato praticado ontem.
    """
    from tests.fixtures.publicacao import retify

    inscricao = cenario["inscricoes"][1]
    peca = interponha(cenario, inscricao)
    versao_da_peca = peca.versao_id

    retify(
        api_client,
        cenario["edital"],
        [{"targetPath": "/title", "operation": "REPLACE", "newValue": "Retificado após o recurso"}],
        suffix="us2",
    )

    peca.refresh_from_db()
    agora = selecao_publica(edital_id=inscricao.edital_id).id
    assert agora != versao_da_peca, "a Retificação precisa ter mesmo produzido outra versão"
    assert peca.versao_id == versao_da_peca


# ---------------------------------------------------------------------------
# T041 — idempotência e duplicidade
# ---------------------------------------------------------------------------


def test_a_mesma_chave_devolve_a_primeira_peca(cenario):
    """O duplo clique é o caso comum, e não o exótico: a segunda chamada devolve a mesma peça."""
    inscricao = cenario["inscricoes"][1]

    primeira = interponha(cenario, inscricao)
    segunda = interponha(cenario, inscricao)

    assert segunda.pk == primeira.pk
    assert Recurso.objects.filter(inscricao=inscricao).count() == 1


def test_a_mesma_chave_com_outro_conteudo_e_conflito(cenario):
    """Chave repetida com conteúdo diferente não é repetição: são dois pedidos disfarçados de um."""
    inscricao = cenario["inscricoes"][1]
    interponha(cenario, inscricao, fundamentacao="A primeira razão.")

    with pytest.raises(DomainError) as recusa:
        interponha(cenario, inscricao, fundamentacao="Outra razão inteiramente.")

    assert recusa.value.code == "idempotency_conflict"
    assert recusa.value.status == 409


def test_o_segundo_recurso_do_mesmo_par_e_recusado_nomeando_o_protocolo(cenario):
    """Um recurso por titular e objeto (FR-011).

    A mensagem nomeia o protocolo da primeira peça porque "você já recorreu" sem dizer de qual
    recurso se trata obriga a pessoa a procurar o que o sistema já tem na mão.
    """
    inscricao = cenario["inscricoes"][1]
    primeira = interponha(cenario, inscricao)

    with pytest.raises(DomainError) as recusa:
        interponha(
            cenario,
            inscricao,
            fundamentacao="Outra razão inteiramente.",
            idempotency_key="outra-chave-us2",
        )

    assert recusa.value.code == "appeal_already_filed"
    assert recusa.value.status == 409
    assert primeira.protocolo in recusa.value.detail


def test_a_recusa_de_repeticao_vale_tambem_depois_de_decidido(cenario):
    """**Decidido não reabre** (FR-012). O caminho contra a decisão é outro, e não é este.

    Sem esta prova, a unicidade pareceria proteger só o pendente — e a peça decidida abriria a
    porta para recorrer de novo do mesmo objeto, que é exatamente o que a instância única exclui.
    """
    from tests.fixtures.recursos import admitir, decidir

    inscricao = cenario["inscricoes"][1]
    primeira = interponha(cenario, inscricao)
    admitir(primeira)
    decidir(primeira, especie="INDEFERIDO")

    with pytest.raises(DomainError) as recusa:
        interponha(cenario, inscricao, idempotency_key="depois-da-decisao-us2")

    assert recusa.value.code == "appeal_already_filed"
    assert primeira.protocolo in recusa.value.detail


# ---------------------------------------------------------------------------
# T042 — a revalidação do objeto lido
# ---------------------------------------------------------------------------


def test_objeto_superado_entre_a_leitura_e_a_confirmacao_e_recusado(cenario):
    """A página aberta há dez minutos pode estar mostrando um ato que já foi corrigido.

    Interpor sobre ele faria nascer uma peça contra história — e a recusa diz onde está o vigente,
    porque "não é possível" sem caminho é um beco (FR-009, FR-100).
    """
    inscricao = cenario["inscricoes"][1]
    superado = resultado_de(cenario, inscricao)
    versao = selecao_publica(edital_id=inscricao.edital_id)
    deferir_corrigindo(
        superado,
        versao=versao,
        pontuacao=Decimal("95.0000"),
        consequencia=ResultadoEtapa.Consequencia.HABILITADA,
        protocolo="REC-2026-US20001",
    )

    with pytest.raises(DomainError) as recusa:
        interponha(cenario, inscricao, alvo=superado, idempotency_key="superado-us2")

    assert recusa.value.code == "appeal_target_superseded"
    assert recusa.value.status == 409
    assert "resultado atual" in recusa.value.detail


def test_assinatura_divergente_do_objeto_lido_e_recusada(cenario):
    """A assinatura é o que a tela apresentou; divergir dela é ler uma coisa e atacar outra."""
    inscricao = cenario["inscricoes"][1]

    with pytest.raises(DomainError) as recusa:
        interponha(cenario, inscricao, assinatura_do_objeto="outro-identificador-qualquer")

    assert recusa.value.code == "appeal_target_superseded"
    assert not Recurso.objects.filter(inscricao=inscricao).exists()


def test_o_sucessor_e_oferecido_no_lugar_do_superado(cenario):
    """A ação não é oferecida quando a interposição não é possível — e é oferecida quando é.

    A ausência do superado aqui é **duplamente determinada**: ele deixou de ser vigente e já foi
    recorrido, e por isso ela sozinha não prova grande coisa. O que este teste prende é a metade
    que ninguém escreveria sem pensar: corrigido o resultado, é do **novo** que se pode recorrer,
    e a tela precisa dizê-lo. Uma lista que apenas encolhesse deixaria a pessoa sem caminho contra
    a correção que ela recebeu (FR-013).
    """
    inscricao = cenario["inscricoes"][1]
    superado = resultado_de(cenario, inscricao)
    _recurso, _decisao, sucessor = deferir_corrigindo(
        superado,
        versao=selecao_publica(edital_id=inscricao.edital_id),
        pontuacao=Decimal("95.0000"),
        consequencia=ResultadoEtapa.Consequencia.HABILITADA,
        protocolo="REC-2026-US20002",
    )

    oferecidos = {item["id"] for item in objetos_recorriveis(inscricao)}

    assert sucessor.id in oferecidos
    assert superado.id not in oferecidos


def test_o_que_ja_foi_recorrido_sai_da_lista(cenario):
    inscricao = cenario["inscricoes"][1]
    alvo = resultado_de(cenario, inscricao)
    interponha(cenario, inscricao)

    oferecidos = {item["id"] for item in objetos_recorriveis(inscricao)}

    assert alvo.id not in oferecidos


# ---------------------------------------------------------------------------
# T044 — os dois objetos, o mesmo fluxo
# ---------------------------------------------------------------------------


def test_publicacao_e_resultado_produzem_a_mesma_especie_de_peca(cenario):
    """Uma capacidade, dois alvos (D-001, FR-002).

    O que muda entre as duas peças é **qual identidade elas nomeiam** — e mais nada. Se algum dia
    divergirem em espécie, em versão ou em titular, é porque viraram duas máquinas parecidas.
    """
    contra_o_resultado = interponha(cenario, cenario["inscricoes"][0])
    contra_a_publicacao = interponha(
        cenario,
        cenario["inscricoes"][1],
        alvo=publicacao_de(cenario),
        idempotency_key="contra-a-publicacao-us2",
    )

    assert isinstance(contra_a_publicacao, Recurso)
    assert contra_a_publicacao.publicacao_atacada_id == publicacao_de(cenario).id
    assert contra_a_publicacao.resultado_atacado_id is None
    assert contra_o_resultado.publicacao_atacada_id is None
    assert contra_a_publicacao.versao_id == contra_o_resultado.versao_id
    assert contra_a_publicacao.protocolo.startswith("REC-")


def test_a_publicacao_tambem_entra_na_lista_do_que_se_pode_contestar(cenario):
    inscricao = cenario["inscricoes"][1]

    tipos = {item["tipo"] for item in objetos_recorriveis(inscricao)}

    assert tipos == {"publicacao", "resultado"}


def test_resultado_de_etapa_nao_divulgada_nao_e_recorrivel(
    gestor, api_client, manager_headers, process_payload
):
    """Existir no banco não torna contestável (D-003, FR-014).

    O Resultado da primeira Etapa está consolidado e é do próprio titular — e nenhum marco
    publicado a enumera. Recorrer dele seria atacar um número que a instituição ainda não afirmou,
    e a recusa é `404`: dizer "existe, mas você ainda não pode vê-lo" antecipa o resultado.
    """
    from tests.portal.test_resultado_da_etapa import consolidar_na_primeira

    cenario = montar_marco(
        gestor, api_client, manager_headers, process_payload, seed=96, codigo="0796"
    )
    inscricoes = pontuar(cenario, gestor, ["90.0000"], primeiro=961, sufixo="96")
    consolidar_na_primeira(cenario, gestor, inscricoes, pontuacao="88.7700")
    cenario["ato"] = emitir(cenario, gestor, chave="emitir-018-us2-invisivel")
    publicar_o_ato(cenario, chave="publicar-018-us2-invisivel")
    inscricao = inscricoes[0]
    fora = ResultadoEtapa.vigentes.get(inscricao=inscricao, etapa_id=cenario["primeira"])

    with pytest.raises(DomainError) as recusa:
        interponha(cenario, inscricao, alvo=fora, idempotency_key="invisivel-us2")

    assert recusa.value.code == "appeal_not_visible"
    assert recusa.value.status == 404
    assert not Recurso.objects.filter(inscricao=inscricao).exists()
