"""Os cenários de aceitação da 013, na ordem das histórias.

Aqui ficam as afirmações sobre a **jornada** — o que a presidência vê e obtém. As invariantes de
banco, de comando e de não regressão ficam em `tests/integration/resultados/`, e a razão da divisão
é a mesma que o quickstart declara: nem todo requisito é observável pelo canal do ator, e fingir
que é seria contar cobertura que não existe.
"""

from uuid import UUID

import pytest

from processo_seletivo.comissoes.domain.etapas import etapas_vigentes
from processo_seletivo.resultados.application.consolidacao import consolidar
from processo_seletivo.resultados.application.prontidao import panorama_da_etapa
from processo_seletivo.resultados.models import ResultadoEtapa
from tests.conftest import ator_institucional
from tests.fixtures.comissao import inscrever
from tests.fixtures.mesa import concluir_como, distribuir_para
from tests.fixtures.resultado import montar_etapa_de_leitura_unica, montar_tres_etapas

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


def consolidar_como(cenario, inscricoes, *, chave, etapa=None):
    return consolidar(
        actor=ator_institucional("maria"),
        processo_id=cenario["processo"].id,
        edital_id=cenario["edital"].id,
        etapa_id=etapa or cenario["primeira"],
        inscricao_ids=[i.id for i in inscricoes],
        idempotency_key=chave,
        correlation_id="teste",
    )


def test_us2_o_lote_produz_habilitada_e_eliminada_pela_regra(gestor, api_client, manager_headers):
    """US2, cenário 1: 75, 60 e 59 sob mínima 60 — e o 60 habilita.

    O caso do meio é o que importa: nota **exatamente igual** à mínima habilita, e é onde o
    arredondamento binário decidiria a vida de alguém.
    """
    cenario = montar(gestor, api_client, manager_headers, seed=1341)
    inscricoes = inscrever(cenario["edital"], 3, primeiro=1)
    distribuir_para(cenario, gestor, ["joao"], inscricoes, chave="lote-1341")
    for inscricao, nota in zip(inscricoes, ("75", "60", "59"), strict=True):
        concluir_como(cenario, "joao", inscricao, pontuacao=nota)

    desfecho = consolidar_como(cenario, inscricoes, chave="a-1341")
    assert desfecho["feitas"] == 3

    consequencias = {
        r.inscricao_id: r.consequencia
        for r in ResultadoEtapa.objects.filter(edital=cenario["edital"])
    }
    assert consequencias[inscricoes[0].id] == ResultadoEtapa.Consequencia.HABILITADA
    assert consequencias[inscricoes[1].id] == ResultadoEtapa.Consequencia.HABILITADA
    assert consequencias[inscricoes[2].id] == ResultadoEtapa.Consequencia.ELIMINADA


def test_us2_um_envio_com_prontas_pendentes_e_consolidadas(gestor, api_client, manager_headers):
    """US2, cenário 2: o lote misto — cria o que dá, recusa o resto com a causa."""
    cenario = montar(gestor, api_client, manager_headers, seed=1342)
    inscricoes = inscrever(cenario["edital"], 3, primeiro=1)
    distribuir_para(cenario, gestor, ["joao"], inscricoes, chave="lote-1342")
    concluir_como(cenario, "joao", inscricoes[0], pontuacao="75")
    concluir_como(cenario, "joao", inscricoes[1], pontuacao="80")
    consolidar_como(cenario, inscricoes[:1], chave="a-1342")

    desfecho = consolidar_como(cenario, inscricoes, chave="b-1342")
    assert desfecho["feitas"] == 1
    assert desfecho["recusadas"] == 2
    causas = {grupo["motivo"] for grupo in desfecho["agrupados"]}
    assert any("já possui Resultado" in c for c in causas)
    assert any("ainda não há avaliação concluída" in c for c in causas)
    # O resumo da Etapa acompanha, e é a mesma fonte: dois consolidados, um impedido.
    assert panorama(cenario)["contagens"]["consolidadas"] == 2


def test_us2_a_pontuacao_e_copia_exata_e_ninguem_a_digita(gestor, api_client, manager_headers):
    """SC-003: não existe arredondamento, média nem edição manual na V1."""
    cenario = montar(gestor, api_client, manager_headers, seed=1343)
    inscricao = inscrever(cenario["edital"], 1, primeiro=1)[0]
    distribuir_para(cenario, gestor, ["joao"], [inscricao], chave="lote-1343")
    avaliacao = concluir_como(cenario, "joao", inscricao, pontuacao="73.5000")

    consolidar_como(cenario, [inscricao], chave="a-1343")
    resultado = ResultadoEtapa.objects.get(inscricao=inscricao)
    assert resultado.pontuacao == avaliacao.pontuacao


def test_us3_a_eliminacao_vale_para_todas_as_etapas_seguintes(gestor, api_client, manager_headers):
    """T043 — a transitividade, e o buraco que a revisão do plano fechou.

    Eliminada na Etapa 1, com a Etapa 2 **sem nenhum Resultado**: ela não pode reaparecer na Etapa
    3. Uma redação anterior consultava só a Etapa imediatamente anterior, e nesse cenário o gate
    ficava dormente — a eliminação simplesmente não produzia efeito duas Etapas adiante.
    """
    cenario = montar_tres_etapas(gestor, api_client, manager_headers, seed=1390, codigo="1390")
    cenario["vigentes"] = etapas_vigentes(cenario["edital"])
    inscricoes = inscrever(cenario["edital"], 2, primeiro=1)
    distribuir_para(cenario, gestor, ["joao"], inscricoes, chave="lote-1390")
    concluir_como(cenario, "joao", inscricoes[0], pontuacao="75")
    concluir_como(cenario, "joao", inscricoes[1], pontuacao="40")
    consolidar_como(cenario, inscricoes, chave="t-1390")

    habilitada, eliminada = inscricoes
    for etapa in ("segunda", "terceira"):
        publicada = cenario["vigentes"][UUID(str(cenario[etapa]))]
        visao = panorama_da_etapa(
            edital=cenario["edital"], etapa=publicada, etapas_vigentes=cenario["vigentes"]
        )
        assert eliminada.id in visao["eliminadas"], etapa
        assert eliminada.id not in visao["participantes"], etapa
    # E a habilitada segue: na Etapa 2 ela participa, e na 3 ela aguarda a 2 — que ainda não fechou.
    segunda = panorama_da_etapa(
        edital=cenario["edital"],
        etapa=cenario["vigentes"][UUID(str(cenario["segunda"]))],
        etapas_vigentes=cenario["vigentes"],
    )
    assert habilitada.id in segunda["participantes"]


def test_us3_a_exigencia_de_habilitacao_fica_dormente_ate_o_primeiro_resultado(
    gestor, api_client, manager_headers
):
    """T044 — o gate, e o que ele impede a 013 de quebrar.

    Edital de leitura múltipla: a V1 não consolida a Etapa 1, e por isso a Etapa 2 **não pode** ficar
    sem participantes. Sem este gate, todo Edital de segunda leitura pararia na primeira Etapa.
    """
    cenario = montar(gestor, api_client, manager_headers, seed=1391, avaliacoes=2)
    inscricoes = inscrever(cenario["edital"], 3, primeiro=1)

    primeira = panorama(cenario)
    assert primeira["impedimento_da_etapa"] is not None
    assert primeira["contagens"]["prontas"] == 0

    segunda = panorama(cenario, etapa="segunda_publicada")
    assert len(segunda["participantes"]) == len(inscricoes)
    assert segunda["contagens"]["aguardando_anterior"] == 0
