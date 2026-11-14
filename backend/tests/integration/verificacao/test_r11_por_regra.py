"""O vídeo só confirma, nas três regras (166, SC-2373, FR-7136 a FR-7139).

Com três pareceres pelo vídeo, todas as combinações de sentido, nas três regras: o número de
Resultados desfavoráveis produzidos é zero. A tabela de cinco pareceres está em
`tests/unit/verificacao/test_r11.py`, sobre a mesma função de deliberação.
"""

import itertools

import pytest

from processo_seletivo.resultados.domain.deliberacao import deliberar, DO_PUBLICADO
from processo_seletivo.resultados.models import ResultadoEtapa
from processo_seletivo.verificacao.application import ganchos
from tests.fixtures.deliberacao import concluir_pareceres, consolidar_na, distribuir_na_hetero
from tests.fixtures.verificacao import enviar_video, montar_com_video
from tests.integration.verificacao.test_mesa_e_r11 import abrir_como

pytestmark = pytest.mark.django_db

COMBINACOES = list(itertools.product(("FAVORAVEL", "DESFAVORAVEL"), repeat=3))


@pytest.mark.parametrize("regra", ["MAJORITY", "UNANIMOUS_FOR_FAVORABLE", "UNANIMOUS_FOR_UNFAVORABLE"])
def test_nenhuma_combinacao_produz_nao_confirmada(
    raiz_de_arquivos, gestor, api_client, manager_headers, regra
):
    seed = {"MAJORITY": 6620, "UNANIMOUS_FOR_FAVORABLE": 6621, "UNANIMOUS_FOR_UNFAVORABLE": 6622}[regra]
    cenario = montar_com_video(
        gestor, api_client, manager_headers, seed=seed, quantas=len(COMBINACOES), regra=regra
    )
    distribuir_na_hetero(cenario, gestor, cenario["inscricoes"], chave=f"dist-{seed}")
    for inscricao, sentidos in zip(cenario["inscricoes"], COMBINACOES, strict=True):
        enviar_video(inscricao, cenario["hetero"])
        for subject in ("ana", "bruno", "carla"):
            abrir_como(cenario, subject, inscricao)
        concluir_pareceres(cenario, inscricao, dict(zip(("ana", "bruno", "carla"), sentidos, strict=True)))
    declarado = consolidar_na(cenario, cenario["hetero"], cenario["inscricoes"], chave=f"c-{seed}")
    resultados = ResultadoEtapa.objects.filter(etapa_id=cenario["hetero"])
    assert not resultados.filter(sentido="DESFAVORAVEL").exists()
    favoraveis = sum(1 for s in COMBINACOES if deliberar(DO_PUBLICADO[regra], s) == "FAVORAVEL")
    assert resultados.filter(sentido="FAVORAVEL").count() == favoraveis
    assert sum(1 for m in declarado["motivos"] if m["motivo"] == ganchos.ENCAMINHAR_AO_VIVO) == (
        len(COMBINACOES) - favoraveis
    )
