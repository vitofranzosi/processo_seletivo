"""Os cenários de aceitação da 013, na ordem das histórias.

Aqui ficam as afirmações sobre a **jornada** — o que a presidência vê e obtém. As invariantes de
banco, de comando e de não regressão ficam em `tests/integration/resultados/`, e a razão da divisão
é a mesma que o quickstart declara: nem todo requisito é observável pelo canal do ator, e fingir
que é seria contar cobertura que não existe.
"""

from uuid import UUID

import pytest

from processo_seletivo.comissoes.domain.etapas import etapas_vigentes
from processo_seletivo.resultados.application.prontidao import panorama_da_etapa
from tests.fixtures.comissao import inscrever
from tests.fixtures.mesa import concluir_como, distribuir_para
from tests.fixtures.resultado import montar_etapa_de_leitura_unica

pytestmark = [pytest.mark.acceptance, pytest.mark.django_db]


def montar(gestor, api_client, manager_headers, *, seed, avaliacoes=1):
    cenario = montar_etapa_de_leitura_unica(
        gestor, api_client, manager_headers, seed=seed, codigo=str(seed), avaliacoes=avaliacoes
    )
    cenario["vigentes"] = etapas_vigentes(cenario["edital"])
    cenario["etapa_publicada"] = cenario["vigentes"][UUID(str(cenario["primeira"]))]
    cenario["segunda_publicada"] = cenario["vigentes"][UUID(str(cenario["segunda"]))]
    return cenario


def panorama(cenario, etapa="etapa_publicada"):
    return panorama_da_etapa(
        edital=cenario["edital"], etapa=cenario[etapa], etapas_vigentes=cenario["vigentes"]
    )


def test_us1_a_presidencia_ve_prontas_pendentes_e_impedidas(gestor, api_client, manager_headers):
    """US1, cenário 1: um mesmo resumo, três grupos, sem dupla contagem."""
    cenario = montar(gestor, api_client, manager_headers, seed=1340)
    inscricoes = inscrever(cenario["edital"], 3, primeiro=1)
    distribuir_para(cenario, gestor, ["joao"], inscricoes[:2], chave="lote-1340")
    concluir_como(cenario, "joao", inscricoes[0], pontuacao="75")

    contagens = panorama(cenario)["contagens"]
    assert contagens["participantes"] == 3
    assert contagens["prontas"] == 1
    assert contagens["impedidas"] == 2
    assert contagens["consolidadas"] == 0
    # A partição fecha, e é isso que impede resumo e detalhe filtrado de divergirem.
    assert contagens["prontas"] + contagens["impedidas"] + contagens["consolidadas"] == 3
