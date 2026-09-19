"""O alcance da instrução: nasce com o ato, vale **para uma peça**, e morre com a decisão.

```text
nada instruído       → não há alcance, e não há ato a declarar
instrução praticada  → o alcance abre                              (FR-527)
outro recurso        → nada, ainda que da mesma Etapa              (FR-528)
recurso decidido     → o alcance fecha, e o registro permanece     (FR-529)
```

**A pergunta que este arquivo responde é uma só, e ela é a do desenho:** o que se construiu é um
**ato** ou uma **permissão** com outro nome? A diferença não está no nome da função — está em o
alcance ser derivado do par (aquele recurso, quem o julga) em vez de guardado como lista. Uma
permissão vale para a classe e sobrevive ao ato; este alcance vale para **uma** peça, e morre
com ela.
"""

import pytest
from django.db import connection, transaction

from processo_seletivo.recursos.application.instruir import (
    alcance_da_instrucao,
    ato_alcancado,
    instruir,
)
from processo_seletivo.recursos.models import AtoDeInstrucao, Recurso
from processo_seletivo.shared.api.problems import DomainError
from tests.fixtures.instrucao import (
    INSTRUTORA,
    PARECER,
    autoridade,
    cenario_instruivel,
    decidir_a_peca,
    outra_peca,
)

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.integration]


@pytest.fixture
def instruivel(raiz_de_arquivos, gestor, api_client, manager_headers, process_payload):
    """**`raiz_de_arquivos` não é decoração**: `cenario_instruivel` anexa um documento, e o
    armazenamento privado recusa gravar sem raiz declarada — *"sem raiz declarada, o sistema não
    recebe documentos de candidato"*. A raiz vem do ambiente, e o `.env` de desenvolvimento a
    declara; **o CI não declara nenhuma**, e é de propósito: o repositório entrega a raiz por
    fixture, uma por teste, para que dois testes não escrevam no mesmo lugar.

    Quem monta cenário com documento pede a fixture. Quem esquece passa verde na máquina de quem
    tem `.env` e vermelho no CI — que foi exatamente o que aconteceu aqui.
    """
    return cenario_instruivel(
        gestor, api_client, manager_headers, process_payload, seed=136, codigo="0836"
    )


def recarregar(peca):
    """A peça relida com o que a porta da tela carrega — é sobre ela que o alcance se afere."""
    return (
        Recurso.objects.filter(pk=peca.pk)
        .select_related("resultado_atacado", "resultado_atacado__avaliacao")
        .prefetch_related("juizos", "decisoes", "instrucoes")
        .get()
    )


def instruir_tudo(instruivel, *, chave="instruir-136"):
    return instruir(
        actor=autoridade(),
        recurso_id=instruivel["recurso"].id,
        parecer=True,
        documento_ids=[instruivel["documento"].id],
        razao="A peça contesta o parecer e cita o documento juntado.",
        idempotency_key=chave,
    )


# --- O ato abre o alcance -----------------------------------------------------------------------


def test_sem_instrucao_nao_ha_alcance_e_nao_ha_ato_a_declarar(instruivel):
    alcance = alcance_da_instrucao(recarregar(instruivel["recurso"]))

    assert alcance.houve is False
    assert alcance.aberto is False
    # **E o terceiro estado não é este.** Sem ato praticado não há instrução a declarar, e a decisão
    # não inventa uma — é a distinção que a `FR-532` exige da tela.
    assert alcance.encerrado is False


def test_a_instrucao_abre_o_alcance_com_autor_e_instante(instruivel):
    atos = instruir_tudo(instruivel)

    alcance = alcance_da_instrucao(recarregar(instruivel["recurso"]))
    assert alcance.houve is True
    assert alcance.aberto is True
    assert len(alcance.pareceres) == 1
    assert len(alcance.documentos) == 1
    # Um ato da autoridade, e por isso **um** instante e **um** autor para as duas linhas.
    assert {ato.instruido_por for ato in atos} == {INSTRUTORA}
    assert len({ato.instruido_em for ato in atos}) == 1


def test_o_ato_alcanca_o_documento_por_referencia_e_nao_por_copia(instruivel):
    """`FR-531` e `FR-531a`: a linha aponta para o original, e nada foi duplicado.

    A verificação é no **armazenamento**, e não no caminho que a tela aponta: um segundo arquivo com
    o mesmo conteúdo satisfaria qualquer asserção sobre o caminho e seria exatamente a cópia que a
    `FR-531a` proíbe.
    """
    original = instruivel["documento"]
    caminho = original.arquivo.name

    instruir_tudo(instruivel)

    ato = AtoDeInstrucao.objects.get(especie=AtoDeInstrucao.Especie.DOCUMENTO)
    assert ato.documento_id == original.pk
    assert ato.documento.arquivo.name == caminho
    # **Nenhum campo de arquivo no ato**: não há onde uma cópia caber, e é essa a forma mais forte
    # da `FR-531a` — a ausência é verificada no esquema, e não na disciplina de quem escreve código.
    assert not [
        campo.name
        for campo in AtoDeInstrucao._meta.get_fields()
        if campo.__class__.__name__ in ("FileField", "ImageField")
    ]
    # E nenhum `DocumentoSubmetido` novo: a inscrição continua com o mesmo arquivo de antes.
    assert original.inscricao.documentos.count() == 1


def test_instruir_de_novo_acrescenta_e_nao_substitui(instruivel):
    """Append-only na disciplina dos outros atos do produto: a segunda instrução é outra linha."""
    instruir(
        actor=autoridade(),
        recurso_id=instruivel["recurso"].id,
        parecer=True,
        idempotency_key="instruir-so-o-parecer",
    )
    instruir(
        actor=autoridade(),
        recurso_id=instruivel["recurso"].id,
        documento_ids=[instruivel["documento"].id],
        idempotency_key="instruir-o-documento-depois",
    )

    alcance = alcance_da_instrucao(recarregar(instruivel["recurso"]))
    assert len(alcance.atos) == 2
    assert len(alcance.pareceres) == 1 and len(alcance.documentos) == 1


def test_o_ato_e_append_only_nas_tres_camadas(instruivel):
    """`save` recusa, e a trigger recusa **mesmo quem tem privilégio** (Princípio II)."""
    ato = instruir_tudo(instruivel)[0]

    with pytest.raises(TypeError):
        ato.razao = "outra"
        ato.save()
    with pytest.raises(TypeError):
        ato.delete()

    if connection.vendor != "postgresql":
        pytest.skip("a trigger de imutabilidade é verificada somente em PostgreSQL")
    with (
        pytest.raises(Exception, match="append-only"),
        transaction.atomic(),
        connection.cursor() as cursor,
    ):
        cursor.execute(
            "UPDATE recursos_atodeinstrucao SET razao = 'reescrita' WHERE id = %s", [str(ato.pk)]
        )


# --- O alcance é de UMA peça (FR-528) -----------------------------------------------------------


def test_instruir_uma_peca_nao_alcanca_outra_da_mesma_etapa(instruivel):
    """**A contraprova central da feature** (`T021`, `SC-185`, `FR-528`).

    Mesmo Edital, mesma Etapa, mesmo julgador, e a segunda peça não alcança nada. Se alcançasse, o
    que se construiu seria uma permissão com outro nome — e o ponto central da `036` estaria errado.

    A verificação é estrutural, e é isso que a torna forte: o alcance **não tem** como vazar para a
    outra peça, porque ele é lido da relação `recurso → instrucoes`. Não há lista de pessoas a
    consultar, e por isso não há lista que possa estar larga demais.
    """
    instruir_tudo(instruivel)
    segunda = outra_peca(instruivel)

    alcance = alcance_da_instrucao(recarregar(segunda))

    assert alcance.houve is False
    assert alcance.aberto is False
    assert alcance.atos == ()
    # E o caminho do documento também não abre: o ato que autoriza é daquela peça, não desta.
    with pytest.raises(DomainError) as recusa:
        ato_alcancado(recarregar(segunda), documento_id=instruivel["documento"].id)
    assert recusa.value.status == 404


def test_nao_se_instrui_documento_de_outro_candidato(instruivel):
    """`FR-535` e `FR-536`: a resposta é a uniforme, e não uma que confirme que o documento
    existe.
    """
    alheio = instruivel["outra_inscricao"].documentos.first()
    assert alheio is not None

    with pytest.raises(DomainError) as recusa:
        instruir(
            actor=autoridade(),
            recurso_id=instruivel["recurso"].id,
            documento_ids=[alheio.id],
            idempotency_key="instruir-documento-alheio",
        )

    assert recusa.value.status == 404
    assert recusa.value.detail == "Recurso não encontrado."
    assert not AtoDeInstrucao.objects.exists()


def test_a_trigger_recusa_o_documento_de_outro_candidato(instruivel):
    """A segunda camada, para o que não passa pela aplicação: um comando, um shell, um caminho novo.

    A aplicação já recusa; esta guarda vale para o resto. Anexar o documento de **uma** pessoa ao
    recurso de **outra** seria, num só passo, o dado de terceiro que a `FR-535` proíbe e a ampliação
    de acesso que a `FR-105` da `018` proíbe.
    """
    if connection.vendor != "postgresql":
        pytest.skip("a trigger de coerência é verificada somente em PostgreSQL")
    alheio = instruivel["outra_inscricao"].documentos.first()

    with pytest.raises(Exception, match="another registration"), transaction.atomic():
        AtoDeInstrucao.objects.create(
            recurso=instruivel["recurso"],
            especie=AtoDeInstrucao.Especie.DOCUMENTO,
            documento=alheio,
            instruido_por=INSTRUTORA,
            instruido_em=instruivel["recurso"].interposto_em,
        )


# --- O alcance morre com a decisão (FR-529) -----------------------------------------------------


def test_o_alcance_fecha_com_a_decisao_e_o_registro_permanece(instruivel):
    """As duas metades são o ponto: nada se apaga, e a porta fecha (`FR-529`, `SC-185`)."""
    instruir_tudo(instruivel)
    decidir_a_peca(instruivel)

    alcance = alcance_da_instrucao(recarregar(instruivel["recurso"]))

    # O registro permanece — e é o terceiro estado da `FR-532`, não o primeiro.
    assert alcance.houve is True
    assert alcance.encerrado is True
    assert alcance.aberto is False
    assert AtoDeInstrucao.objects.filter(recurso=instruivel["recurso"]).count() == 2
    assert PARECER == instruivel["recurso"].resultado_atacado.avaliacao.parecer


def test_depois_de_decidido_o_documento_nao_abre_e_a_recusa_diz_por_que(instruivel):
    """403 que nomeia a razão, e não 404: o ator sabe que o ato houve — a tela acabou de dizer."""
    instruir_tudo(instruivel)
    decidir_a_peca(instruivel)

    with pytest.raises(DomainError) as recusa:
        ato_alcancado(recarregar(instruivel["recurso"]), documento_id=instruivel["documento"].id)

    assert recusa.value.status == 403
    assert "terminou com a decisão" in recusa.value.detail
    assert "permanece" in recusa.value.detail


def test_nao_se_instrui_peca_ja_decidida(instruivel):
    """A porta fechada não se reabre pela frente: o ato nasceria com alcance encerrado."""
    decidir_a_peca(instruivel)

    with pytest.raises(DomainError) as recusa:
        instruir_tudo(instruivel)

    assert recusa.value.status == 409
    assert not AtoDeInstrucao.objects.exists()


# --- A autoridade, e o que não se instrui -------------------------------------------------------


def test_quem_so_julga_nao_instrui_e_a_recusa_nomeia_as_duas_bases(instruivel):
    """`FR-530`: julgar não concede instruir, e a recusa diz **o que falta e a quem pedir**."""
    from tests.fixtures.instrucao import julgador

    with pytest.raises(DomainError) as recusa:
        instruir(
            actor=julgador(),
            recurso_id=instruivel["recurso"].id,
            parecer=True,
            idempotency_key="instruir-sem-base",
        )

    assert recusa.value.status == 403
    assert "gerir a comissão" in recusa.value.detail
    assert "preside este Processo" in recusa.value.detail
    assert not AtoDeInstrucao.objects.exists()


def test_nao_se_instrui_parecer_de_recurso_contra_a_publicacao(
    raiz_de_arquivos, gestor, api_client, manager_headers, process_payload
):
    """Caso de borda da spec: ali não há parecer a instruir, e a recusa o diz com esta palavra."""
    from processo_seletivo.publicacoes.application.selectors import selecao_publica
    from tests.fixtures.recursos import interpor as interpor_curto

    montado = cenario_instruivel(
        gestor, api_client, manager_headers, process_payload, seed=137, codigo="0837"
    )
    inscricao = montado["inscricao"]
    contra_a_publicacao = interpor_curto(
        inscricao=inscricao,
        versao=selecao_publica(edital_id=inscricao.edital_id),
        publicacao=montado["publicacao"],
        protocolo="REC-2026-INSTR0137",
    )

    with pytest.raises(DomainError) as recusa:
        instruir(
            actor=autoridade(),
            recurso_id=contra_a_publicacao.id,
            parecer=True,
            idempotency_key="instruir-publicacao",
        )

    assert recusa.value.status == 422
    assert "não ataca Resultado individual" in recusa.value.detail


def test_instruir_sem_escolher_nada_e_recusado(instruivel):
    with pytest.raises(DomainError) as recusa:
        instruir(
            actor=autoridade(),
            recurso_id=instruivel["recurso"].id,
            idempotency_key="instruir-vazio",
        )

    assert recusa.value.status == 422
    assert not AtoDeInstrucao.objects.exists()


def test_a_repeticao_da_chave_devolve_os_mesmos_atos(instruivel):
    """Um ato que grava mais de uma linha não tem "o objeto criado": a reserva guarda o desfecho."""
    primeira = instruir_tudo(instruivel)
    segunda = instruir_tudo(instruivel)

    assert {ato.pk for ato in primeira} == {ato.pk for ato in segunda}
    assert AtoDeInstrucao.objects.count() == 2
