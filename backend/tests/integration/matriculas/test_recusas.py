"""A geração que se recusa a mentir (`US3`).

**Uma exportação que aproxima é pior do que redigitar: ela erra com autoridade.** É por isso que a
recusa é P1 — e por isso que ela **diz o que falta e de quem** (`UX-061`), em vez de *"não foi
possível gerar"*.
"""

import pytest

from processo_seletivo.matriculas.application.exportar import compor, gerar
from processo_seletivo.matriculas.application.populacao import opcoes
from processo_seletivo.matriculas.domain import nomes
from processo_seletivo.matriculas.models import GeracaoDeArquivo
from processo_seletivo.requerimentos.domain import nomes as requerimento_nomes
from processo_seletivo.shared.api.problems import DomainError
from tests.conftest import ator_institucional
from tests.fixtures.convocacao import convocar
from tests.fixtures.matriculas import (
    MODALIDADE_DIVERGENTE,
    declarar,
    montar_cenario_da_exportacao,
    publicar_com_grafia_divergente,
)

pytestmark = pytest.mark.django_db


def gerar_a_primeira(quem_exporta, edital):
    escolhida = opcoes(edital)[0]
    return gerar(
        ator=quem_exporta,
        edital=edital,
        especie=escolhida.especie,
        referencia=escolhida.referencia,
        # **O que a tela teria mostrado.** Recompor aqui é o que o navegador faz ao abrir a prévia;
        # o teste que prova a recusa por resumo obsoleto está em `test_recusas.py`.
        confirmacao_do_resumo=compor(
            ator=quem_exporta,
            edital=edital,
            especie=escolhida.especie,
            referencia=escolhida.referencia,
        ).assinatura,
    )


def test_sem_populacao_escolhida_nao_ha_geracao(cenario, quem_exporta):
    """`FR-433`: não existe população padrão implícita.

    A recusa é da aplicação, e não da tela: quem montar o `POST` à mão encontra a mesma resposta.
    """
    edital, _ = cenario
    with pytest.raises(DomainError) as recusa:
        compor(ator=quem_exporta, edital=edital, especie="", referencia="")
    assert recusa.value.code == nomes.POPULACAO_NAO_ESCOLHIDA
    assert "Escolha quem entra" in recusa.value.detail


def test_quem_nao_declarou_e_nomeado_e_nada_e_gerado(
    db, gestor, api_client, manager_headers, process_payload, raiz_de_arquivos, quem_exporta
):
    """`FR-435`, `SC-149`: a recusa nomeia quem falta, e o arquivo **não** sai com a linha faltando.

    Um arquivo com a linha faltando é pior que nenhum arquivo: ele parece completo.
    """
    edital, convocadas = montar_cenario_da_exportacao(
        gestor, api_client, manager_headers, process_payload, prefixo="031-sem-declarar", quantos=1
    )
    terceira = _convocar_mais_uma(edital, gestor, "031-sem-declarar")
    with pytest.raises(DomainError) as recusa:
        gerar_a_primeira(quem_exporta, edital)
    assert recusa.value.code == nomes.DECLARACAO_FALTANDO
    assert terceira.protocolo in recusa.value.detail
    assert convocadas[0].protocolo not in recusa.value.detail
    assert not GeracaoDeArquivo.objects.exists()


def test_o_rascunho_nao_conta_como_declaracao(
    db, gestor, api_client, manager_headers, process_payload, raiz_de_arquivos, quem_exporta
):
    """`FR-434`: rascunho é o que alguém começou a preencher, e ninguém o declarou."""
    edital, _ = montar_cenario_da_exportacao(
        gestor, api_client, manager_headers, process_payload, prefixo="031-rascunho", quantos=1
    )
    outra = _convocar_mais_uma(edital, gestor, "031-rascunho")
    declarar(edital, outra, status=requerimento_nomes.RASCUNHO)
    with pytest.raises(DomainError) as recusa:
        gerar_a_primeira(quem_exporta, edital)
    assert recusa.value.code == nomes.DECLARACAO_FALTANDO
    assert outra.protocolo in recusa.value.detail


def test_populacao_que_esvaziou_recusa_em_vez_de_gerar_zero_linhas(
    db, gestor, api_client, manager_headers, process_payload, raiz_de_arquivos, quem_exporta
):
    """§9, *Edge Cases*: **um arquivo de zero linhas pareceria um arquivo pronto.**

    Quem desistiu sai do conjunto — e tem de sair: quem desistiu nunca vai enviar requerimento, e
    mantê-lo na população recusaria a geração para sempre por uma ausência que é o desfecho
    funcionando. Esvaziada a população, a recusa **diz isso**, e nomeia o conjunto escolhido.
    """
    from processo_seletivo.convocacao.application.desfechar import desfechar
    from processo_seletivo.convocacao.domain import nomes as convocacao_nomes
    from processo_seletivo.convocacao.models import Convocacao

    edital, _ = montar_cenario_da_exportacao(
        gestor, api_client, manager_headers, process_payload, prefixo="031-vazia", quantos=1
    )
    chamada = Convocacao.objects.get(edital=edital)
    desfechar(
        actor=gestor,
        processo_id=edital.processo_id,
        convocacao_id=chamada.id,
        especie=convocacao_nomes.DESISTENCIA_EXPRESSA,
        fundamento="Manifestação da pessoa convocada, registrada em processo.",
        idempotency_key="031-vazia-desfecho",
        correlation_id="teste-matriculas-031",
    )

    with pytest.raises(DomainError) as recusa:
        gerar_a_primeira(quem_exporta, edital)
    assert recusa.value.code == nomes.POPULACAO_VAZIA
    assert "não tem ninguém" in recusa.value.detail
    assert not GeracaoDeArquivo.objects.exists()


def test_grafia_de_modalidade_desconhecida_recusa_a_geracao_inteira(
    db, gestor, api_client, manager_headers, process_payload, raiz_de_arquivos, quem_exporta
):
    """`FR-441`, `SC-147`: a mensagem traz **o código e o Edital**, e a grafia não é reescrita.

    O caso é real: o `seed_demo` declara `PPP` — *"pretas, pardas e indígenas"*, Lei 12.990/2014 —
    onde o comentário da planilha prevê `PPI`. Duas letras, o mesmo instituto jurídico, e nenhuma
    das pontas sabe da outra.
    """
    from processo_seletivo.inscricoes.models import Inscricao

    edital, convocadas = montar_cenario_da_exportacao(
        gestor,
        api_client,
        manager_headers,
        process_payload,
        prefixo="031-grafia",
        quantos=1,
        publicar=publicar_com_grafia_divergente,
    )
    # A escolha da Modalidade entra por gravação direta: o que se exercita aqui é a **saída**, e o
    # caminho de escolha tem os testes dele na `009`.
    Inscricao.objects.filter(pk=convocadas[0].pk).update(modality_id=MODALIDADE_DIVERGENTE)
    with pytest.raises(DomainError) as recusa:
        gerar_a_primeira(quem_exporta, edital)
    assert recusa.value.code == nomes.MODALIDADE_DESCONHECIDA
    assert "PPP" in recusa.value.detail
    assert f"{edital.number}/{edital.year}" in recusa.value.detail
    assert not GeracaoDeArquivo.objects.exists()


def test_o_download_sem_ter_conferido_o_resumo_e_recusado(cenario, quem_exporta):
    """`UX-060`: o resumo vem antes do download — e a regra vale para quem não passou pela tela.

    Uma regra que só a interface cumpre é cumprida enquanto ninguém colar o endereço. Sem a
    assinatura da prévia, não há o que confirmar, e o comando recusa.
    """
    edital, _ = cenario
    escolhida = opcoes(edital)[0]
    with pytest.raises(DomainError) as recusa:
        gerar(
            ator=quem_exporta,
            edital=edital,
            especie=escolhida.especie,
            referencia=escolhida.referencia,
            confirmacao_do_resumo="",
        )
    assert recusa.value.code == nomes.RESUMO_NAO_CONFERIDO
    assert recusa.value.status == 409
    assert not GeracaoDeArquivo.objects.exists()


def test_o_resumo_que_envelheceu_entre_a_previa_e_o_download_e_recusado(cenario, quem_exporta):
    """O caso que a assinatura existe para pegar, e que nenhuma tela pega sozinha.

    Alguém lê o resumo, e **nesse intervalo** a pessoa corrige o requerimento pelo portal. O
    arquivo que sairia não é o que foi conferido — e entregá-lo em silêncio faria a conferência
    valer para um arquivo que ninguém viu.
    """
    from django.utils import timezone

    from processo_seletivo.convocacao.application.selectors import chamada_em_aberto
    from processo_seletivo.publicacoes.application.selectors import effective_version
    from processo_seletivo.requerimentos.models import RequerimentoDeMatricula
    from tests.fixtures.matriculas import campos_declarados

    edital, convocadas = cenario
    escolhida = opcoes(edital)[0]
    argumentos = {
        "ator": quem_exporta,
        "edital": edital,
        "especie": escolhida.especie,
        "referencia": escolhida.referencia,
    }
    conferida = compor(**argumentos).assinatura

    agora = timezone.now()
    anterior = RequerimentoDeMatricula.objects.get(
        inscricao=convocadas[0], requerimento_anterior__isnull=True
    )
    RequerimentoDeMatricula.objects.create(
        inscricao=convocadas[0],
        requerimento_anterior=anterior,
        convocacao_autorizadora=chamada_em_aberto(convocadas[0]),
        status=requerimento_nomes.ENVIADO,
        disponibilizado_em=agora,
        created_at=agora,
        enviado_em=agora,
        versao_aceita=effective_version(edital_id=edital.id),
        declaracao_hash="c" * 64,
        declaracao_aceita_em=agora,
        **campos_declarados(bairro="Praia do Canto"),
    )

    with pytest.raises(DomainError) as recusa:
        gerar(**argumentos, confirmacao_do_resumo=conferida)
    assert recusa.value.code == nomes.RESUMO_NAO_CONFERIDO
    assert "não é o que foi conferido" in recusa.value.detail
    assert not GeracaoDeArquivo.objects.exists()


def test_sem_a_permissao_propria_a_geracao_e_recusada(cenario):
    """`SC-150`, `FR-455`: `inscricao:consultar` **não** autoriza a exportação.

    Ler o dossiê de uma pessoa por vez e baixar o conjunto inteiro são atos distintos.
    """
    edital, _ = cenario
    quem_so_consulta = ator_institucional("gestora", "inscricao:consultar")
    with pytest.raises(DomainError) as recusa:
        gerar_a_primeira(quem_so_consulta, edital)
    assert recusa.value.status == 403


def test_populacao_de_outro_escopo_nao_e_alcancavel(cenario):
    """O identificador público não confere autorização — a recusa é de escopo, e não de rota."""
    edital, _ = cenario
    de_fora = ator_institucional("estranha", nomes.EXPORTAR, escopo="outro-instituto")
    with pytest.raises(DomainError) as recusa:
        gerar_a_primeira(de_fora, edital)
    assert recusa.value.status == 404


def _convocar_mais_uma(edital, gestor, prefixo):
    """Chama a próxima da fila, sem declarar nada por ela."""
    from processo_seletivo.convocacao.models import Convocacao
    from processo_seletivo.inscricoes.models import Inscricao

    ja_chamadas = set(
        Convocacao.objects.filter(edital=edital).values_list("inscricao_id", flat=True)
    )
    proxima = (
        Inscricao.objects.filter(edital=edital, status=Inscricao.Status.SUBMETIDA)
        .exclude(pk__in=ja_chamadas)
        .order_by("protocolo")
        .first()
    )
    convocar(edital, gestor, proxima, idempotency_key=f"{prefixo}-extra")
    return proxima
