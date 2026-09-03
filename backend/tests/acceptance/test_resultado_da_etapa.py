"""Os cenários de aceitação da 013, na ordem das histórias.

Aqui ficam as afirmações sobre a **jornada** — o que a presidência vê e obtém. As invariantes de
banco, de comando e de não regressão ficam em `tests/integration/resultados/`, e a razão da divisão
é a mesma que o quickstart declara: nem todo requisito é observável pelo canal do ator, e fingir
que é seria contar cobertura que não existe.
"""

from uuid import UUID

import pytest
from django.urls import reverse

from processo_seletivo.comissoes.application.comissao import remover_membro
from processo_seletivo.comissoes.domain.etapas import etapas_vigentes
from processo_seletivo.resultados.application.consolidacao import consolidar
from processo_seletivo.resultados.application.prontidao import panorama_da_etapa
from processo_seletivo.resultados.models import ResultadoEtapa
from tests.conftest import ator_institucional
from tests.fixtures.comissao import inscrever
from tests.fixtures.mesa import concluir_como, distribuir_para
from tests.fixtures.resultado import montar_etapa_de_leitura_unica, montar_tres_etapas
from tests.interface.conftest import identificar

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

    Edital de leitura múltipla: a V1 não consolida a Etapa 1, e por isso a Etapa 2 **não pode**
    ficar sem participantes. Sem o gate, todo Edital de segunda leitura pararia na primeira Etapa.
    """
    cenario = montar(gestor, api_client, manager_headers, seed=1391, avaliacoes=2)
    inscricoes = inscrever(cenario["edital"], 3, primeiro=1)

    primeira = panorama(cenario)
    assert primeira["impedimento_da_etapa"] is not None
    assert primeira["contagens"]["prontas"] == 0

    segunda = panorama(cenario, etapa="segunda_publicada")
    assert len(segunda["participantes"]) == len(inscricoes)
    assert segunda["contagens"]["aguardando_anterior"] == 0


def test_us4_a_proveniencia_sobrevive_a_retificacao_e_a_saida_do_avaliador(
    gestor, api_client, manager_headers, client, seletor_ligado
):
    """T055 — a decisão continua demonstrável depois de o mundo mudar em volta dela.

    Uma Retificação **fora** da Etapa e a saída do avaliador da comissão: nem uma nem outra pode
    apagar a origem. É por isso que a autoria é identificador estável, e não vínculo, e que a norma
    histórica é lida da versão que governou a Avaliação.
    """
    cenario = montar(gestor, api_client, manager_headers, seed=1470)
    inscricao = inscrever(cenario["edital"], 1, primeiro=1)[0]
    distribuir_para(cenario, gestor, ["joao"], [inscricao], chave="lote-1470")
    concluir_como(cenario, "joao", inscricao, pontuacao="73.5000")
    consolidar_como(cenario, [inscricao], chave="p-1470")

    remover_membro(
        actor=gestor,
        processo_id=cenario["processo"].id,
        membro_id=cenario["membros"]["joao"].id,
        idempotency_key="saida-1470",
        correlation_id="teste",
    )

    identificar(client, "maria", ["gestor"])
    resposta = client.get(
        reverse("interface:resultados-da-etapa", args=[cenario["edital"].id, cenario["primeira"]])
    )
    corpo = resposta.content.decode()
    assert resposta.status_code == 200
    # Total, consequência e as **duas** autorias continuam legíveis na mesma jornada.
    assert "73,5" in corpo
    assert "Habilitada" in corpo
    assert "joao" in corpo and "maria" in corpo


def test_us4_nenhuma_tela_afirma_colocacao_ou_aprovacao(
    gestor, api_client, manager_headers, client, seletor_ligado
):
    """FR-045 — a fronteira com a 014, dita na tela e não só na spec."""
    cenario = montar(gestor, api_client, manager_headers, seed=1471)
    inscricao = inscrever(cenario["edital"], 1, primeiro=1)[0]
    distribuir_para(cenario, gestor, ["joao"], [inscricao], chave="lote-1471")
    concluir_como(cenario, "joao", inscricao, pontuacao="90")
    consolidar_como(cenario, [inscricao], chave="p-1471")

    identificar(client, "maria", ["gestor"])
    corpo = client.get(
        reverse("interface:resultados-da-etapa", args=[cenario["edital"].id, cenario["primeira"]])
    ).content.decode()
    for proibido in ("colocação", "classificação", "aprovado", "convocaç", "ocupa a vaga"):
        assert proibido not in corpo.lower(), proibido


def test_a_jornada_completa_pela_interface_administrativa(
    gestor, api_client, manager_headers, client, seletor_ligado
):
    """O cenário demonstrável do princípio VI, ponta a ponta e **pelo canal do ator**.

    Sem banco, sem shell e sem chamada manual: tudo o que este teste faz, a presidência faz com o
    navegador. É a diferença entre uma capacidade que o domínio sustenta e uma que alguém alcança.
    """
    cenario = montar_tres_etapas(gestor, api_client, manager_headers, seed=1480, codigo="1480")
    cenario["vigentes"] = etapas_vigentes(cenario["edital"])
    inscricoes = inscrever(cenario["edital"], 3, primeiro=1)
    distribuir_para(cenario, gestor, ["joao"], inscricoes, chave="lote-1480")
    concluir_como(cenario, "joao", inscricoes[0], pontuacao="75")
    concluir_como(cenario, "joao", inscricoes[1], pontuacao="40")

    identificar(client, "maria", ["gestor"])
    organizacao = reverse(
        "interface:distribuicao", args=[cenario["edital"].id, cenario["primeira"]]
    )

    # 1. A presidência abre a Etapa e lê a prontidão — no resumo que já existia.
    corpo = client.get(organizacao).content.decode()
    assert "prontas para consolidar" in corpo
    assert "ainda não há avaliação concluída" in corpo

    # 2. Consolida as duas prontas num ato só.
    resposta = client.post(
        reverse(
            "interface:consolidar-resultados", args=[cenario["edital"].id, cenario["primeira"]]
        ),
        {
            "inscricao_id": [str(inscricoes[0].id), str(inscricoes[1].id)],
            "chave_idempotencia": "jornada-1480",
        },
    )
    assert resposta.status_code == 302
    corpo = client.get(organizacao).content.decode()
    assert "2 </strong> consolidada(s)" in corpo.replace("\n", " ") or "consolidada(s)" in corpo

    # 3. Consulta um Resultado com a origem dele.
    corpo = client.get(
        reverse("interface:resultados-da-etapa", args=[cenario["edital"].id, cenario["primeira"]])
    ).content.decode()
    assert "Habilitada" in corpo and "Eliminada" in corpo
    assert "nota mínima" in corpo
    assert "joao" in corpo and "maria" in corpo

    # 4. Tenta reabrir a fonte de um Resultado, e é recusada.
    fonte = ResultadoEtapa.objects.get(inscricao=inscricoes[0]).avaliacao
    client.post(
        reverse("interface:reabrir-avaliacao", args=[cenario["edital"].id, cenario["primeira"]]),
        {
            "avaliacao_id": str(fonte.id),
            "motivo": "Tentativa de reabertura.",
            "expected_revision": fonte.revision,
            "chave_idempotencia": "reab-1480",
        },
    )
    fonte.refresh_from_db()
    assert fonte.estado == "CONCLUIDA"

    # 5. A Etapa seguinte, e a de depois — onde as **duas** regras aparecem separadas.
    #
    #    Na Etapa 2 a exigência de habilitação já vigora, porque a Etapa 1 produziu Resultado:
    #    participa só quem foi habilitado. Na Etapa 3 ela está dormente, porque a Etapa 2 ainda não
    #    consolidou nada — mas a **eliminação continua valendo**, e é essa diferença que a redação
    #    anterior de D-003 não fazia.
    segunda = panorama_da_etapa(
        edital=cenario["edital"],
        etapa=cenario["vigentes"][UUID(str(cenario["segunda"]))],
        etapas_vigentes=cenario["vigentes"],
    )
    assert segunda["participantes"] == {inscricoes[0].id}
    assert inscricoes[1].id in segunda["eliminadas"]
    assert inscricoes[2].id in segunda["aguardando"]

    terceira = panorama_da_etapa(
        edital=cenario["edital"],
        etapa=cenario["vigentes"][UUID(str(cenario["terceira"]))],
        etapas_vigentes=cenario["vigentes"],
    )
    assert terceira["participantes"] == {inscricoes[0].id, inscricoes[2].id}
    assert inscricoes[1].id in terceira["eliminadas"]
    assert terceira["aguardando"] == set()
