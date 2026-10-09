"""Os modelos da unidade: criados uma vez, editáveis, nunca excluídos, e de uma unidade só (US4).

**"Uma vez" é a garantia que custa.** A sincronização roda a cada `make preparar` e a cada
implantação; se ela recriasse os modelos iniciais, a unidade que os inativou os veria voltar, e a
que os editou perderia o texto dela. Os casos prendem que nada disso acontece — inclusive com duas
sincronizações ao mesmo tempo.
"""

import threading

import pytest
from django.db import connection

from processo_seletivo.avisos.application.modelos import (
    criar,
    editar,
    garantir_modelos_iniciais,
    modelo_da_unidade,
    modelos_da_unidade,
    mudar_situacao,
)
from processo_seletivo.avisos.domain import nomes
from processo_seletivo.avisos.models import Aviso, ModeloDeAviso
from processo_seletivo.shared.api.problems import DomainError
from tests.conftest import ator_institucional
from tests.fixtures.avisos import PUBLICADORA, avisar_resultado
from tests.fixtures.divulgacao import montar_ato_publicavel, publicar_o_ato

pytestmark = [pytest.mark.integration]

OUTRA_UNIDADE = ator_institucional("de-fora", nomes.PERMISSAO, escopo="campus")
PRESIDENCIA = ator_institucional("presidenta")


@pytest.mark.django_db
def test_os_tres_iniciais_nascem_ativos_na_primeira_sincronizacao():
    assert garantir_modelos_iniciais() == 3

    iniciais = ModeloDeAviso.objects.filter(institution_scope="cefor", modelo_inicial=True)
    assert iniciais.count() == 3
    assert all(modelo.ativo for modelo in iniciais)


@pytest.mark.django_db
def test_inativados_continuam_inativos_e_nada_se_recria():
    garantir_modelos_iniciais()
    for modelo in ModeloDeAviso.objects.filter(modelo_inicial=True):
        mudar_situacao(actor=PUBLICADORA, modelo_id=modelo.id, ativo=False)

    assert garantir_modelos_iniciais() == 0
    assert ModeloDeAviso.objects.filter(modelo_inicial=True).count() == 3
    assert not ModeloDeAviso.objects.filter(modelo_inicial=True, ativo=True).exists()


@pytest.mark.django_db
def test_o_texto_editado_nao_e_sobrescrito():
    garantir_modelos_iniciais()
    modelo = ModeloDeAviso.objects.get(nome="Divulgação de resultado")
    editar(
        actor=PUBLICADORA,
        modelo_id=modelo.id,
        nome=modelo.nome,
        assunto="Seleção — nova publicação",
        corpo="Texto da seleção, {nome_do_candidato}.",
    )

    garantir_modelos_iniciais()

    modelo.refresh_from_db()
    assert modelo.corpo == "Texto da seleção, {nome_do_candidato}."


@pytest.mark.django_db(transaction=True)
def test_duas_sincronizacoes_ao_mesmo_tempo_nao_duplicam():
    if connection.vendor != "postgresql":
        pytest.skip("a serialização é do PostgreSQL")
    erros = []

    def sincronizar():
        try:
            garantir_modelos_iniciais()
        except Exception as erro:  # noqa: BLE001 — o caso registra qualquer falha da corrida
            erros.append(erro)
        finally:
            connection.close()

    threads = [threading.Thread(target=sincronizar) for _ in range(2)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    assert erros == []
    assert ModeloDeAviso.objects.filter(modelo_inicial=True).count() == 3


@pytest.mark.django_db
def test_editar_o_modelo_nao_muda_o_aviso_enviado(
    gestor, api_client, manager_headers, process_payload
):
    cenario = montar_ato_publicavel(
        gestor, api_client, manager_headers, process_payload, pontuacoes=("90.0000",)
    )
    publicacao = publicar_o_ato(cenario)
    modelo = criar(actor=PUBLICADORA, nome="Resultado", assunto="Assunto", corpo="Texto original.")
    declarado = avisar_resultado(cenario["edital"], publicacao.marco_id, corpo="Texto original.")
    corpo_enviado = Aviso.objects.get(pk=declarado["aviso"]).corpo

    editar(actor=PUBLICADORA, modelo_id=modelo.id, nome="Resultado", assunto="A", corpo="Outro.")

    assert Aviso.objects.get(pk=declarado["aviso"]).corpo == corpo_enviado


@pytest.mark.django_db
def test_variavel_desconhecida_e_recusada_com_o_nome():
    with pytest.raises(DomainError) as erro:
        criar(actor=PUBLICADORA, nome="Ruim", assunto="Assunto", corpo="Sua {posicao}.")

    assert erro.value.code == nomes.AVISO_VARIAVEL_DESCONHECIDA
    assert "posicao" in erro.value.detail


@pytest.mark.django_db
def test_nome_repetido_e_recusado():
    criar(actor=PUBLICADORA, nome="Único", assunto="Assunto", corpo="Texto.")

    with pytest.raises(DomainError) as erro:
        criar(actor=PUBLICADORA, nome="único", assunto="Assunto", corpo="Texto.")

    assert erro.value.code == nomes.MODELO_COM_NOME_REPETIDO


@pytest.mark.django_db
def test_inativo_fica_na_gestao_e_nao_se_exclui():
    modelo = criar(actor=PUBLICADORA, nome="Velho", assunto="Assunto", corpo="Texto.")
    mudar_situacao(actor=PUBLICADORA, modelo_id=modelo.id, ativo=False)

    assert modelo in modelos_da_unidade(PUBLICADORA)
    with pytest.raises(TypeError):
        ModeloDeAviso.objects.get(pk=modelo.pk).delete()


@pytest.mark.django_db
def test_outra_unidade_nao_ve_o_modelo():
    modelo = criar(actor=PUBLICADORA, nome="Nosso", assunto="Assunto", corpo="Texto.")

    with pytest.raises(DomainError) as erro:
        modelo_da_unidade(OUTRA_UNIDADE, modelo.id)

    assert erro.value.status == 404
    assert modelos_da_unidade(OUTRA_UNIDADE) == []


@pytest.mark.django_db
def test_a_presidencia_nao_administra_modelos():
    with pytest.raises(DomainError) as erro:
        modelos_da_unidade(PRESIDENCIA)

    assert erro.value.status == 404


@pytest.mark.django_db
def test_cada_mudanca_vai_a_trilha_com_antes_e_depois():
    from processo_seletivo.auditoria.models import RegistroAuditoria

    modelo = criar(actor=PUBLICADORA, nome="Trilha", assunto="Assunto", corpo="Texto.")
    editar(actor=PUBLICADORA, modelo_id=modelo.id, nome="Trilha", assunto="Novo", corpo="Texto.")

    eventos = RegistroAuditoria.objects.filter(
        operation=nomes.OPERACAO_MODELO, aggregate_id=str(modelo.id)
    ).order_by("occurred_at", "event_id")
    assert eventos.count() == 2
    assert eventos.last().detalhe["antes"]["assunto"] == "Assunto"
    assert eventos.last().detalhe["depois"]["assunto"] == "Novo"
