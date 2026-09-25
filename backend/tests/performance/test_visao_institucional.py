"""Custo de consulta da visão institucional (040, `SC-209`, `SC-214`).

**A afirmação é de igualdade, e não de teto.** Um teto absoluto envelhece a cada consulta legítima
acrescentada e passa a ser mantido em vez de verificado; a igualdade entre dois tamanhos de recorte
prende a propriedade que a `SC-209` descreve — *o custo não cresce com o número de Editais* — e
continua valendo quando o número absoluto mudar.

O segundo teste conta **snapshots abertos**, e não consultas: é o que prova a `FR-598` e a
`FR-599`, e a contagem de consultas sozinha não o pegaria — abrir sessenta `content` em duas
consultas custaria duas consultas do mesmo jeito.
"""

from datetime import timedelta

import pytest
from django.db import connection
from django.test.utils import CaptureQueriesContext
from django.utils import timezone

from processo_seletivo.interface import visao_geral as visao
from processo_seletivo.processos.models import Edital, ProcessoSeletivo
from processo_seletivo.publicacoes.models import Publicacao
from processo_seletivo.publicacoes.models_retificacao import VersaoConsolidada
from tests.conftest import ator_institucional

pytestmark = [pytest.mark.django_db, pytest.mark.performance]

ANO = 2026
ANO_ANTIGO = 2020


@pytest.fixture
def ator():
    return ator_institucional("carlos", visao.CONSULTAR)


def conteudo(seed):
    agora = timezone.now()
    return {
        "profiles": [
            {
                "id": f"00000000-0000-4000-8000-{seed:012d}",
                "code": f"P{seed}",
                "name": "Perfil",
                "immediateVacancies": 2,
                "reserveType": "NONE",
            }
        ],
        "schedule": [
            {
                "id": f"00000000-0000-4000-9000-{seed:012d}",
                "description": "Inscrições",
                "startAt": (agora - timedelta(days=30)).isoformat(),
                "endAt": (agora - timedelta(days=1)).isoformat(),
                "order": 1,
                "isRegistrationPeriod": True,
            }
        ],
    }


def publicar_direto(quantos, *, ano, primeiro=0, fabrica=None):
    """Editais publicados montados **direto no banco**, e não pela API.

    O que este teste mede é o custo da **leitura**, e atravessar o ciclo de publicação sessenta
    vezes custaria minutos sem acrescentar garantia nenhuma ao que se afirma. As fixtures que
    exercitam o ciclo estão nos testes de interface, onde a jornada é a coisa medida.
    """
    agora = timezone.now()
    fabrica = fabrica or conteudo
    processo = ProcessoSeletivo.objects.create(
        institution_scope="cefor",
        institutional_code=f"PS-CARGA-{ano}-{primeiro}",
        title="Processo de carga",
        status=ProcessoSeletivo.Status.ATIVO,
        created_at=agora,
        created_by="carga",
        last_changed_at=agora,
    )
    for indice in range(primeiro, primeiro + quantos):
        edital = Edital.objects.create(
            processo=processo,
            institution_scope="cefor",
            number=f"{indice:03d}",
            year=ano,
            title=f"Edital {indice}",
            status=Edital.Status.PUBLICADO,
            created_at=agora,
            created_by="carga",
            last_edited_by="carga",
        )
        publicacao = Publicacao.objects.create(
            edital=edital,
            publication_order=1,
            published_at=agora - timedelta(days=40),
            effective_at=agora - timedelta(days=40),
            content_hash=f"hash-{indice}",
            canonical_content=b"{}",
            published_by="carga",
            signatory_id="00000000-0000-4000-a000-000000000001",
            signatory_name="Autoridade",
            signatory_role="Diretora",
        )
        VersaoConsolidada.objects.create(
            edital=edital,
            valid_from=agora - timedelta(days=40),
            materialized_at=agora - timedelta(days=40),
            source_publication=publicacao,
            content=fabrica(indice),
            canonical_content=b"{}",
            content_hash=f"hash-{indice}",
        )
    return processo


def consultas_para(ator, parametros):
    with CaptureQueriesContext(connection) as capturadas:
        visao.ler(ator, parametros)
    return len(capturadas)


# ---------------------------------------------------------------------------
# T-20 · SC-209 — o custo não cresce com o número de Editais
# ---------------------------------------------------------------------------


def test_t20_o_numero_de_consultas_nao_cresce_com_o_numero_de_editais(ator):
    publicar_direto(3, ano=ANO)
    com_tres = consultas_para(ator, {"ano": str(ANO)})

    publicar_direto(57, ano=ANO, primeiro=100)
    com_sessenta = consultas_para(ator, {"ano": str(ANO)})

    assert com_tres == com_sessenta, (
        f"o custo cresceu com o recorte: {com_tres} consultas com 3 Editais e "
        f"{com_sessenta} com 60 — a leitura passou a ser por linha"
    )


# ---------------------------------------------------------------------------
# T-21 · T-22 · SC-214 — o recorte limita os snapshots abertos
# ---------------------------------------------------------------------------


def test_t21_o_recorte_de_um_ano_abre_so_os_snapshots_daquele_ano(ator):
    publicar_direto(3, ano=ANO)
    publicar_direto(57, ano=ANO_ANTIGO, primeiro=200)

    _, linhas, consolidado = visao.ler(ator, {"ano": str(ANO)})

    # **Três, e não sessenta.** É o que a `FR-598` compra ao filtrar antes de materializar, e o que
    # a `FR-599` preserva ao recortar pelo ano corrente por omissão.
    assert len(linhas) == 3
    assert consolidado.editais_publicados == 3


def test_t22_o_seletor_de_anos_nao_abre_snapshot_algum(ator):
    publicar_direto(3, ano=ANO)
    publicar_direto(3, ano=ANO_ANTIGO, primeiro=300)

    with CaptureQueriesContext(connection) as capturadas:
        anos = visao.anos_disponiveis(ator)

    assert set(anos) == {ANO, ANO_ANTIGO}
    # Uma consulta, de **uma coluna**: nenhuma delas toca `VersaoConsolidada`.
    assert len(capturadas) == 1
    assert "versaoconsolidada" not in capturadas[0]["sql"].lower()


def test_o_recorte_de_todos_os_anos_ve_o_acervo_inteiro(ator):
    publicar_direto(3, ano=ANO)
    publicar_direto(2, ano=ANO_ANTIGO, primeiro=400)

    _, linhas, _ = visao.ler(ator, {"ano": visao.TODOS})

    assert len(linhas) == 5


# ---------------------------------------------------------------------------
# 041 — o custo não cresce com o número de Perfis
# ---------------------------------------------------------------------------


def conteudo_com_perfis(seed, quantos):
    """Um conteúdo publicado com `quantos` Perfis, todos com vaga e demanda."""
    base = conteudo(seed)
    base["profiles"] = [
        {
            "id": f"00000000-0000-4000-8000-{seed:09d}{indice:03d}",
            "code": f"P{indice}",
            "name": f"Perfil {indice}",
            "locality": "Vitória",
            "immediateVacancies": 2,
            "reserveType": "NONE",
        }
        for indice in range(quantos)
    ]
    return base


def publicar_com_perfis(quantos, *, ano, primeiro, seed):
    """Publica **já** com os Perfis — `VersaoConsolidada` é append-only.

    A primeira versão deste ajudante criava a versão e a atualizava em seguida, e o gatilho
    `reject_consolidated_mutation` a recusou: *"consolidated versions are append-only"*. As duas
    camadas de imutabilidade estão de pé, e o teste não é exceção a elas.
    """
    return publicar_direto(
        1, ano=ano, primeiro=primeiro, fabrica=lambda _: conteudo_com_perfis(seed, quantos)
    )


def test_o_custo_nao_cresce_com_o_numero_de_perfis(ator):
    """`FR-618`, `SC-216` — a expansão é gratuita porque o dado já está carregado.

    **A redação anterior da `SC-216` pedia "com e sem a expansão"**, e isso não é medição possível:
    ela é renderizada no servidor e não tem um "sem". A propriedade que importa é esta — um Edital
    de 16 polos custa o mesmo que um de 1.
    """
    publicar_com_perfis(1, ano=ANO, primeiro=500, seed=1)
    com_um = consultas_para(ator, {"ano": str(ANO)})

    publicar_com_perfis(12, ano=ANO, primeiro=600, seed=2)
    com_doze = consultas_para(ator, {"ano": str(ANO)})

    assert com_um == com_doze, (
        f"o custo cresceu com os Perfis: {com_um} consultas com 1 e {com_doze} com 12 — "
        "a leitura passou a ser por Perfil"
    )


def test_o_filtro_de_atencao_nao_acrescenta_consulta(ator):
    """`FR-621` — ele opera sobre marca já derivada, depois da materialização (`R-009`)."""
    publicar_com_perfis(3, ano=ANO, primeiro=700, seed=3)

    sem = consultas_para(ator, {"ano": str(ANO)})
    com = consultas_para(ator, {"ano": str(ANO), "atencao": "1"})

    assert sem == com
