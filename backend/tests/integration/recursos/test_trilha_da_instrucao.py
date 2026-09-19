"""A trilha responde *quem viu o quê, quando, e por decisão de quem* — e nunca *o que ele dizia*.

Dois registros, e não um (036, `FR-533`, `FR-534`):

```text
RECURSO_INSTRUIR            houve instrução: quem, quando, qual recurso, o que foi anexado
RECURSO_INSTRUCAO_ACESSAR   alguém exerceu o acesso: quem, quando, e o escopo do que viu
```

**Saber que a prova foi anexada não responde quem a viu**, e é por isso que são dois. Sem o segundo,
a instrução seria uma ampliação de acesso sem rastro — exatamente o que a `FR-105` da `018` existe
para impedir, com outro nome.

**E a contraprova deste arquivo é obrigatória, não de rotina.** A `018` já pratica a regra em
`test_a_trilha_registra_o_ato_e_nao_o_conteudo`, e acrescentar registros é precisamente como ela se
quebra: quem escreve um motivo novo tem o texto do parecer à mão, e copiá-lo para a razão parece
informação útil. Seria a segunda cópia do dado sensível, num lugar com outro regime de acesso e
outro tempo de retenção.
"""

import pytest
from django.urls import reverse

from processo_seletivo.auditoria.models import RegistroAuditoria
from processo_seletivo.recursos.application.instruir import (
    OPERACAO,
    OPERACAO_DE_ACESSO,
    instruir,
)
from tests.fixtures.comissao import abrir_arquivo
from tests.fixtures.instrucao import (
    INSTRUTORA,
    JULGADORA,
    PARECER,
    autoridade,
    cenario_instruivel,
    decidir_a_peca,
)
from tests.interface.conftest import identificar

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.integration]


@pytest.fixture
def instruido(raiz_de_arquivos, gestor, api_client, manager_headers, process_payload):
    montado = cenario_instruivel(
        gestor, api_client, manager_headers, process_payload, seed=160, codigo="0860"
    )
    montado["atos"] = instruir(
        actor=autoridade(),
        recurso_id=montado["recurso"].id,
        parecer=True,
        documento_ids=[montado["documento"].id],
        razao="A peça contesta o parecer e cita o documento juntado.",
        idempotency_key="instruir-160",
    )
    return montado


def registros(operacao):
    return list(RegistroAuditoria.objects.filter(operation=operacao).order_by("occurred_at"))


# --- O ato fica registrado (FR-533) -------------------------------------------------------------


def test_o_ato_aparece_com_autor_instante_recurso_e_o_que_foi_anexado(instruido):
    anotados = registros(OPERACAO)

    assert len(anotados) == 2, "uma linha por item anexado — o parecer e o documento"
    for registro in anotados:
        assert registro.actor_subject == INSTRUTORA
        assert registro.occurred_at is not None
        assert instruido["recurso"].protocolo in registro.reason
    # A espécie, dita em português e não em código: quem audita não aprende o vocabulário interno.
    razoes = " ".join(registro.reason for registro in anotados)
    assert "parecer atacado" in razoes
    assert "documento do requisito" in razoes
    # O agregado é o **ato**, e não o recurso: é ele que nomeia o que foi alcançado.
    assert {registro.aggregate_type for registro in anotados} == {"AtoDeInstrucao"}
    assert {registro.aggregate_id for registro in anotados} == {ato.pk for ato in instruido["atos"]}


def test_o_ato_registra_qual_base_autorizou(instruido):
    """Ato sem base é ato sem autoridade, e a trilha precisa dizer qual das duas serviu."""
    assert {registro.permission for registro in registros(OPERACAO)} == {"comissao:gerir"}


# --- O acesso exercido fica registrado (FR-534, SC-184) -----------------------------------------


def test_o_acesso_a_tela_fica_registrado_com_o_escopo(client, seletor_ligado, instruido):
    identificar(client, JULGADORA, ["julgador"])

    client.get(reverse("interface:recurso", args=[instruido["recurso"].id]))

    anotados = registros(OPERACAO_DE_ACESSO)
    assert len(anotados) == 1
    assert anotados[0].actor_subject == JULGADORA
    assert instruido["recurso"].protocolo in anotados[0].reason
    # **Escopo, e não conteúdo**: a espécie e a quantidade, como a prévia da exportação da `031`.
    assert "o parecer atacado" in anotados[0].reason
    assert "1 documento(s)" in anotados[0].reason
    # Revisão nula porque nada mudou de estado: é leitura.
    assert anotados[0].new_revision is None


def test_abrir_o_documento_instruido_fica_registrado_por_item(client, seletor_ligado, instruido):
    """Aqui a precisão por item é a resposta certa: abrir um arquivo é acessar aquele arquivo."""
    identificar(client, JULGADORA, ["julgador"])

    abrir_arquivo(
        client,
        reverse(
            "interface:recurso-documento-instruido",
            args=[instruido["recurso"].id, instruido["documento"].id],
        ),
    )

    por_documento = [
        registro
        for registro in registros(OPERACAO_DE_ACESSO)
        if str(instruido["documento"].requirement_id) in registro.reason
    ]
    assert por_documento, "a abertura do documento nomeia o requisito aberto"
    assert por_documento[-1].actor_subject == JULGADORA


def test_sem_instrucao_nao_ha_registro_de_acesso(
    client, seletor_ligado, raiz_de_arquivos, gestor, api_client, manager_headers, process_payload
):
    """**Zero** acessos registrados quando não há o que acessar — o `SC-184` do outro lado."""
    montado = cenario_instruivel(
        gestor, api_client, manager_headers, process_payload, seed=161, codigo="0861"
    )
    identificar(client, JULGADORA, ["julgador"])

    client.get(reverse("interface:recurso", args=[montado["recurso"].id]))

    assert registros(OPERACAO_DE_ACESSO) == []


def test_depois_de_decidido_abrir_a_peca_nao_registra_acesso(client, seletor_ligado, instruido):
    """`SC-185`: zero acessos sobrevivem à decisão — e o que não acontece não é registrado."""
    decidir_a_peca(instruido)
    identificar(client, JULGADORA, ["julgador"])

    client.get(reverse("interface:recurso", args=[instruido["recurso"].id]))

    assert registros(OPERACAO_DE_ACESSO) == []


# --- A CONTRAPROVA: o conteúdo não vaza para registro nenhum ------------------------------------


def test_o_conteudo_nao_aparece_em_registro_nenhum_da_trilha(client, seletor_ligado, instruido):
    """**Contraprova obrigatória** (`T024`, `SC-184`).

    Varre a trilha **inteira** — e não só os dois registros desta feature —, porque o que se afere é
    que nada do conteúdo sensível chegou lá por caminho nenhum. Três textos não podem aparecer: o
    parecer que o avaliador escreveu, o conteúdo do documento apresentado, e a fundamentação de quem
    recorreu.

    Se este teste falhar, criou-se a segunda cópia do dado sensível que a `018` existe para impedir.
    """
    identificar(client, JULGADORA, ["julgador"])
    client.get(reverse("interface:recurso", args=[instruido["recurso"].id]))
    abrir_arquivo(
        client,
        reverse(
            "interface:recurso-documento-instruido",
            args=[instruido["recurso"].id, instruido["documento"].id],
        ),
    )

    tudo = " ".join(
        f"{registro.reason} {registro.previous_state} {registro.new_state}"
        for registro in RegistroAuditoria.objects.all()
    )
    assert tudo.strip(), "a trilha não está vazia — a varredura mede alguma coisa"

    assert PARECER not in tudo
    assert instruido["recurso"].fundamentacao not in tudo
    # O conteúdo do arquivo, e também o nome que o candidato lhe deu: os dois são dele (`FR-074`).
    assert "conteudo do documento" not in tudo
    assert instruido["documento"].nome_original not in tudo


def test_a_trilha_do_edital_alcanca_a_instrucao(client, seletor_ligado, instruido):
    """**O registro tem de chegar a uma tela**, ou a `FR-533` estaria cumprida no banco e não no
    canal do ator — que é o que o Princípio VI recusa.

    A reunião é a mesma que a `019` fez com a convocação: os atos que conduzem o certame são
    auditados sob o identificador deles, e a trilha do Edital os junta. Sem esta linha, quem
    pergunta *"quem autorizou quem a ver o quê"* precisaria do banco para responder.
    """
    identificar(client, "ana.auditora", ["auditor"])

    corpo = client.get(
        reverse("interface:auditoria", args=[instruido["inscricao"].edital_id])
    ).content.decode()

    assert "Instrução do recurso praticada" in corpo
    assert INSTRUTORA in corpo
    assert PARECER not in corpo
