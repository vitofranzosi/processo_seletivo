"""O custo da faixa de ações e da Lista com muitos Editais (104, SC-984, SC-985).

**Por que existe.** A faixa "Ações disponíveis para você" lê o trabalho do ator sobre os Editais
que a Lista já carregou. Se ela consultasse por Edital, a primeira tela da gestão ficaria mais lenta
a cada Edital publicado, e ninguém perceberia num banco de demonstração com quatro. A Lista, por
sua vez, pagava duas consultas por Edital publicado (inscrições e recursos) até a 104: medida em
30/10/2026, 3, 11, 65 e 605 consultas com 0, 3, 30 e 300 Editais; depois, 4, 8, 8 e 8.

Os Editais são montados direto no banco, como na Visão Geral: o que se mede é a leitura, e
atravessar o ciclo de publicação trezentas vezes custaria minutos sem acrescentar garantia.
"""

import pytest
from django.db import connection
from django.test import Client
from django.test.utils import CaptureQueriesContext
from django.urls import reverse

from processo_seletivo.interface import trabalho
from processo_seletivo.interface.identidade import permissoes_de
from processo_seletivo.processos.models import Edital
from processo_seletivo.seguranca.domain import Actor
from tests.interface.conftest import identificar
from tests.performance.test_visao_institucional import publicar_direto

pytestmark = [pytest.mark.django_db, pytest.mark.performance]

#: Quem lê: homologa, publica, gere e julga — o ator que mais ramos da derivação exercita.
PAPEIS = ["homologador", "publicador", "gestor", "julgador"]
TAMANHOS = (0, 3, 30, 300)


def ator():
    return Actor("bruno.homologador", "cefor", permissoes_de(PAPEIS))


def consultas_da_derivacao():
    editais = list(Edital.objects.filter(institution_scope="cefor"))
    with CaptureQueriesContext(connection) as capturadas:
        trabalho.do_ator(ator(), editais)
    return len(capturadas), len(editais)


def consultas_da_lista(cliente):
    with CaptureQueriesContext(connection) as capturadas:
        assert cliente.get(reverse("interface:lista")).status_code == 200
    return len(capturadas)


def _medir(medidor):
    medidas, publicados = {}, 0
    for tamanho in TAMANHOS:
        if tamanho > publicados:
            publicar_direto(tamanho - publicados, ano=2026, primeiro=publicados)
            publicados = tamanho
        medidas[tamanho] = medidor()
    return medidas


def test_a_derivacao_nao_cresce_com_o_numero_de_editais():
    medidas = _medir(consultas_da_derivacao)

    contagens = {tamanho: consultas for tamanho, (consultas, _) in medidas.items()}
    assert {tamanho: editais for tamanho, (_, editais) in medidas.items()} == {
        tamanho: tamanho for tamanho in TAMANHOS
    }
    # Sem Edital nenhum, as leituras por lote nem chegam ao banco; daí em diante, são as mesmas.
    assert contagens[0] <= contagens[3] == contagens[30] == contagens[300], contagens


def test_a_lista_inteira_nao_cresce_com_editais_publicados(client, settings):
    settings.INTERFACE_SELETOR_IDENTIDADE = True
    identificar(client, "bruno.homologador", PAPEIS)

    medidas = _medir(lambda: consultas_da_lista(client))

    assert medidas[3] == medidas[30] == medidas[300], medidas


def test_a_faixa_em_escala_continua_vazia_para_quem_nao_tem_acao(settings):
    """Trezentos Editais publicados sem fluxo nenhum: nada a fazer, e a faixa não aparece."""
    settings.INTERFACE_SELETOR_IDENTIDADE = True
    publicar_direto(300, ano=2026)
    cliente = Client()
    identificar(cliente, "bruno.homologador", PAPEIS)

    resposta = cliente.get(reverse("interface:lista"))

    assert not resposta.context["faixa"]
    assert "Nenhum ato de Edital ou de Retificação, recurso ou avaliação aguarda você agora." in (
        resposta.content.decode()
    )


# ---------------------------------------------------------------------------------------------
# Muitos objetos de trabalho ao mesmo tempo (revisão de 30/10/2026)
# ---------------------------------------------------------------------------------------------


def em_elaboracao(quantos, *, primeiro=0):
    """Editais em elaboração direto no banco: cada um é "Continuar a elaboração" para quem elabora.

    É a forma mais barata de pôr N objetos de trabalho na faixa, e a mais realista para N grande:
    elaborar é o único ato que todo elaborador do escopo tem em todo Edital em elaboração.
    """
    from django.utils import timezone

    from processo_seletivo.processos.models import ProcessoSeletivo

    agora = timezone.now()
    processo = ProcessoSeletivo.objects.create(
        institution_scope="cefor",
        institutional_code=f"PS-FAIXA-{primeiro}",
        title="Processo com muitos Editais em elaboração",
        status=ProcessoSeletivo.Status.ATIVO,
        created_at=agora,
        created_by="carga",
        last_changed_at=agora,
    )
    Edital.objects.bulk_create(
        Edital(
            processo=processo,
            institution_scope="cefor",
            number=f"{indice:03d}",
            year=2027,
            title=f"Edital {indice}",
            status=Edital.Status.EM_ELABORACAO,
            created_at=agora,
            created_by="carga",
            last_edited_by="carga",
        )
        for indice in range(primeiro, primeiro + quantos)
    )


def test_a_faixa_com_1_5_25_e_100_objetos_mostra_cinco_e_nao_cresce_em_consultas(settings):
    settings.INTERFACE_SELETOR_IDENTIDADE = True
    cliente = Client()
    identificar(cliente, "ana.elaboradora", ["elaborador"])
    medidas, criados = {}, 0
    for quantos in (1, 5, 25, 100):
        em_elaboracao(quantos - criados, primeiro=criados)
        criados = quantos
        with CaptureQueriesContext(connection) as capturadas:
            resposta = cliente.get(reverse("interface:lista"))
        faixa = resposta.context["faixa"]
        medidas[quantos] = len(capturadas)
        assert faixa.total == quantos
        assert len(faixa.mostrados) == min(quantos, trabalho.MOSTRADOS)
        assert len(faixa.demais) == max(quantos - trabalho.MOSTRADOS, 0)
        corpo = resposta.content.decode()
        assert (f"Mostrar os outros {quantos - trabalho.MOSTRADOS}" in corpo) is (quantos > 5)

    # Medido em 30/10/2026: 6 consultas com 1, 5, 25 e 100 objetos na faixa.
    assert len(set(medidas.values())) == 1, medidas
