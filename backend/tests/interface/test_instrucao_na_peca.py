"""O que quem julga passa a ver — por **ato**, e não por permissão (036, US2).

A tela do recurso era um beco **honesto**: ela guardava os destinos que o ator não alcança e dizia o
que falta. O que faltava não era uma tela que mentisse — era uma saída, e a saída não pode ser
ampliar o papel de julgar, porque a `FR-105` da `018` proíbe, e na cláusula exata.

```text
sem instrução        → o que falta e a quem pedir
com instrução        → o parecer atacado, e o documento citado por referência
depois de decidido   → que houve instrução, e que o alcance terminou
```

**Nenhuma permissão muda entre o primeiro e o segundo estado**, e é isso que este arquivo prende. O
mesmo ator, com os mesmos papéis, lê coisas diferentes porque alguém com autoridade praticou um ato
sobre **aquela** peça.
"""

import re
from pathlib import Path

import pytest
from django.conf import settings
from django.urls import reverse

from processo_seletivo.recursos.models import AtoDeInstrucao
from tests.fixtures.comissao import abrir_arquivo
from tests.fixtures.instrucao import (
    INSTRUTORA,
    JULGADORA,
    PARECER,
    cenario_instruivel,
    decidir_a_peca,
    outra_peca,
)
from tests.interface.conftest import identificar

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.integration]


@pytest.fixture
def instruivel(raiz_de_arquivos, gestor, api_client, manager_headers, process_payload):
    return cenario_instruivel(
        gestor, api_client, manager_headers, process_payload, seed=150, codigo="0850"
    )


def abrir_a_peca(client, peca, *, papeis=("julgador",), quem=JULGADORA):
    identificar(client, quem, list(papeis))
    resposta = client.get(reverse("interface:recurso", args=[peca.id]))
    assert resposta.status_code == 200
    corpo = resposta.content.decode()
    achado = re.search(r"<main[^>]*>(.*)</main>", corpo, re.DOTALL)
    return achado.group(1) if achado else corpo


def instruir_pela_tela(client, instruivel, *, parecer=True, documentos=True):
    """A instrução praticada **pela interface**, como a autoridade a pratica (`SC-183`)."""
    identificar(client, INSTRUTORA, ["julgador", "gestor"])
    dados = {"razao": "A peça contesta o parecer e cita o documento juntado."}
    if parecer:
        dados["parecer"] = "sim"
    if documentos:
        dados["documento"] = [str(instruivel["documento"].id)]
    resposta = client.post(
        reverse("interface:recurso-instruir", args=[instruivel["recurso"].id]), dados
    )
    assert resposta.status_code == 302, resposta.content.decode()[:600]
    return resposta


# --- Os três estados da FR-532 ------------------------------------------------------------------


def test_sem_instrucao_quem_so_julga_le_o_que_falta_e_a_quem_pedir(
    client, seletor_ligado, instruivel
):
    corpo = abrir_a_peca(client, instruivel["recurso"])

    assert "Nada foi instruído neste recurso" in corpo
    assert "ato de instrução" in corpo
    assert "gerir a comissão" in corpo and "preside este Processo" in corpo
    assert PARECER not in corpo


def test_com_instrucao_quem_so_julga_le_o_parecer_e_alcanca_o_documento(
    client, seletor_ligado, instruivel
):
    """`SC-183`: decide com o parecer atacado à vista, e **sem que nenhuma permissão tenha mudado**.

    O ator é o mesmo, com o mesmo papel único `julgador`. O que mudou entre este teste e o
    anterior é que a autoridade praticou um ato.
    """
    instruir_pela_tela(client, instruivel)

    corpo = abrir_a_peca(client, instruivel["recurso"])

    assert PARECER in corpo
    assert "O parecer atacado, anexado por instrução" in corpo
    caminho = reverse(
        "interface:recurso-documento-instruido",
        args=[instruivel["recurso"].id, instruivel["documento"].id],
    )
    assert caminho in corpo
    # **E nada além daquele recurso**: a tela de documentos da inscrição continua fora, porque
    # `inscricao:consultar` não foi concedido a ninguém.
    assert reverse("interface:inscricao-recebida", args=[instruivel["inscricao"].id]) not in corpo


def test_o_documento_instruido_abre_para_quem_so_julga(client, seletor_ligado, instruivel):
    """Não basta o link estar lá: ele tem de abrir — oferecer o que a outra porta recusa é 403."""
    instruir_pela_tela(client, instruivel)
    identificar(client, JULGADORA, ["julgador"])

    caminho = reverse(
        "interface:recurso-documento-instruido",
        args=[instruivel["recurso"].id, instruivel["documento"].id],
    )
    resposta = abrir_arquivo(client, caminho)

    assert resposta.status_code == 200
    assert resposta.conteudo_servido.startswith(b"%PDF")
    # E a tela de documentos da comissão continua recusando: a instrução alcança **este** documento
    # por causa **desta** peça, e não concede a capacidade de consultar inscrições.
    recebida = reverse("interface:inscricao-recebida", args=[instruivel["inscricao"].id])
    assert client.get(recebida).status_code == 403


def test_depois_de_decidido_a_tela_diz_que_houve_e_que_o_alcance_terminou(
    client, seletor_ligado, instruivel
):
    """O **terceiro** estado, e o que a primeira redação da spec não tinha (`FR-532`, `FR-529`).

    Dizer "nada foi instruído" a quem viu a prova ontem é falso sobre um ato que aconteceu. As duas
    metades ficam na frase: houve, e o alcance terminou.
    """
    instruir_pela_tela(client, instruivel)
    decidir_a_peca(instruivel)

    corpo = abrir_a_peca(client, instruivel["recurso"])

    assert "Houve instrução neste recurso" in corpo
    assert "terminou com a decisão" in corpo
    assert "nada foi apagado" in corpo
    assert "Nada foi instruído neste recurso" not in corpo
    # E o acesso terminou de verdade: o parecer sai da tela, e o caminho do documento recusa.
    assert PARECER not in corpo
    caminho = reverse(
        "interface:recurso-documento-instruido",
        args=[instruivel["recurso"].id, instruivel["documento"].id],
    )
    assert caminho not in corpo
    identificar(client, JULGADORA, ["julgador"])
    assert client.get(caminho).status_code == 403


# --- A tela não oferece o que aquele ator não alcança (a garantia da 033) ------------------------


def test_quem_so_julga_nao_recebe_o_formulario_de_instrucao(client, seletor_ligado, instruivel):
    corpo = abrir_a_peca(client, instruivel["recurso"])

    assert reverse("interface:recurso-instruir", args=[instruivel["recurso"].id]) not in corpo


def test_a_autoridade_recebe_o_formulario_e_ele_oferece_as_duas_especies(
    client, seletor_ligado, instruivel
):
    corpo = abrir_a_peca(
        client, instruivel["recurso"], papeis=("julgador", "gestor"), quem=INSTRUTORA
    )

    assert reverse("interface:recurso-instruir", args=[instruivel["recurso"].id]) in corpo
    assert "Anexar o parecer" in corpo
    assert "Anexar o documento" in corpo


def test_o_que_ja_foi_anexado_nao_e_oferecido_de_novo(client, seletor_ligado, instruivel):
    """Instruir o mesmo item de novo acrescentaria linha sem alcance, e oferecer isso é ruído."""
    instruir_pela_tela(client, instruivel)

    corpo = abrir_a_peca(
        client, instruivel["recurso"], papeis=("julgador", "gestor"), quem=INSTRUTORA
    )

    assert "Anexar o parecer" not in corpo
    assert "Anexar o documento" not in corpo


def test_depois_de_decidido_a_instrucao_nao_e_oferecida(client, seletor_ligado, instruivel):
    """Um botão que sempre recusa ensina a pessoa a desconfiar da tela."""
    decidir_a_peca(instruivel)

    corpo = abrir_a_peca(
        client, instruivel["recurso"], papeis=("julgador", "gestor"), quem=INSTRUTORA
    )

    assert reverse("interface:recurso-instruir", args=[instruivel["recurso"].id]) not in corpo


# --- O documento é referência, e nada foi duplicado (FR-531, FR-531a) ---------------------------


def arquivos_no_armazenamento():
    """Todo arquivo sob a raiz privada — é **no armazenamento** que a ausência da cópia se confere.

    Conferir só o caminho que a tela aponta não basta: um segundo arquivo com o mesmo conteúdo
    satisfaria qualquer asserção sobre o caminho, e seria exatamente a cópia que a `FR-531a` proíbe.
    """
    raiz = Path(settings.ARQUIVOS_CANDIDATOS_RAIZ)
    if not raiz.exists():
        return set()
    return {caminho for caminho in raiz.rglob("*") if caminho.is_file()}


def test_instruir_nao_duplica_arquivo_no_armazenamento(client, seletor_ligado, instruivel):
    """`FR-531a`: a ausência da cópia é **verificável**, e é verificada onde os bytes moram."""
    antes = arquivos_no_armazenamento()
    assert antes, "o cenário apresentou um documento, e ele está no armazenamento"

    instruir_pela_tela(client, instruivel)

    assert arquivos_no_armazenamento() == antes
    ato = AtoDeInstrucao.objects.get(especie=AtoDeInstrucao.Especie.DOCUMENTO)
    assert ato.documento_id == instruivel["documento"].pk


def test_abrir_o_documento_instruido_tambem_nao_duplica(client, seletor_ligado, instruivel):
    """A leitura serve os bytes do original, e não uma cópia guardada em algum lugar."""
    instruir_pela_tela(client, instruivel)
    antes = arquivos_no_armazenamento()

    identificar(client, JULGADORA, ["julgador"])
    abrir_arquivo(
        client,
        reverse(
            "interface:recurso-documento-instruido",
            args=[instruivel["recurso"].id, instruivel["documento"].id],
        ),
    )

    assert arquivos_no_armazenamento() == antes


# --- Nada de outro candidato, e a resposta uniforme (FR-535, FR-536) ----------------------------


def test_o_mesmo_julgador_em_outro_recurso_nao_alcanca_nada(client, seletor_ligado, instruivel):
    """**A contraprova que mais importa**, pela interface (`T021`, `SC-185`, `FR-528`).

    Mesma Etapa, mesmo Edital, mesmo julgador. Se a segunda peça mostrasse a prova, o que se
    construiu seria uma permissão com outro nome — e a feature estaria errada no seu ponto central.
    """
    instruir_pela_tela(client, instruivel)
    segunda = outra_peca(instruivel)

    corpo = abrir_a_peca(client, segunda)

    assert "Nada foi instruído neste recurso" in corpo
    assert PARECER not in corpo
    caminho = reverse(
        "interface:recurso-documento-instruido",
        args=[segunda.id, instruivel["documento"].id],
    )
    assert caminho not in corpo
    identificar(client, JULGADORA, ["julgador"])
    assert client.get(caminho).status_code == 404


def test_nada_de_outro_candidato_atravessa_a_tela_instruida(client, seletor_ligado, instruivel):
    """`SC-186`: a prova é de **uma** inscrição, e nenhuma outra aparece."""
    instruir_pela_tela(client, instruivel)
    alheia = instruivel["outra_inscricao"]

    corpo = abrir_a_peca(client, instruivel["recurso"])

    assert alheia.nome not in corpo
    assert alheia.protocolo not in corpo


def test_escopo_institucional_divergente_recebe_recurso_nao_encontrado(
    client, seletor_ligado, instruivel
):
    """`FR-536`: a resposta uniforme, e ela vale também para as duas rotas novas."""
    instruir_pela_tela(client, instruivel)
    identificar(client, JULGADORA, ["julgador"], escopo="outra-unidade")

    peca = reverse("interface:recurso", args=[instruivel["recurso"].id])
    documento = reverse(
        "interface:recurso-documento-instruido",
        args=[instruivel["recurso"].id, instruivel["documento"].id],
    )
    instruir = reverse("interface:recurso-instruir", args=[instruivel["recurso"].id])

    assert client.get(peca).status_code == 404
    assert client.get(documento).status_code == 404
    assert client.post(instruir, {"parecer": "sim"}).status_code == 404


# --- O orçamento de consulta da tela instruída --------------------------------------------------


def test_a_tela_instruida_custa_uma_leitura_a_mais_e_ela_nao_cresce(
    client, seletor_ligado, instruivel, django_assert_num_queries
):
    """O orçamento da tela **sem** instrução não mudou; o da instruída é constante (`T020`).

    A tela **sem** ato custa as mesmas oito consultas de antes, e o caso que as prende em
    `test_proveniencia_do_recurso.py` continua verde sem alteração. Esta paga cinco a mais, e cada
    uma tem nome:

    ```text
    +1  as linhas do ato de instrução
    +1  as conclusões preservadas de onde o parecer sai (FR-523)
    +1  o registro do acesso exercido (FR-534)
    +2  o par savepoint/release da transação que o grava
    ```

    **E nenhuma delas cresce com o número de atos** — é essa a propriedade que importa, e é o que a
    segunda metade deste teste afere. Um registro de acesso **por item** faria o número subir com a
    quantidade instruída, que é exatamente o custo que o orçamento desta tela existe para impedir.
    """
    instruir_pela_tela(client, instruivel)
    identificar(client, JULGADORA, ["julgador"])
    caminho = reverse("interface:recurso", args=[instruivel["recurso"].id])
    client.get(caminho)

    with django_assert_num_queries(13) as contexto:
        client.get(caminho)
    com_dois_atos = len(contexto)

    # Um terceiro ato na mesma peça, e o número **não** se move.
    identificar(client, INSTRUTORA, ["julgador", "gestor"])
    client.post(
        reverse("interface:recurso-instruir", args=[instruivel["recurso"].id]),
        {"documento": [str(instruivel["documento"].id)], "razao": "de novo"},
    )
    identificar(client, JULGADORA, ["julgador"])
    client.get(caminho)
    with django_assert_num_queries(com_dois_atos):
        client.get(caminho)
