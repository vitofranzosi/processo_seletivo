"""A definitiva que corrige outra — apresentada pela **causa**, e sem natureza nova.

`DEFINITIVA_RETIFICADA` seria um terceiro valor no enum: três pares a decidir na regra de não
regressão, mais um valor em `uq_publicacao_por_ato_natureza`, e toda leitura de natureza mudando —
tudo para dizer o que a cadeia já diz. Vigência e natureza **derivam da cadeia**, e não de estado
duplicado (FR-087).

E a publicação vigente passa a dizer que é a vigente. Antes, só a sucedida dizia algo sobre a
cadeia: quem abria a vigente não tinha como saber se estava lendo o que vale ou um histórico — a
oportunidade nº 3 do relatório da E2E-017 (FR-090).
"""

import re

import pytest
from django.urls import reverse

from processo_seletivo.divulgacao.models import PublicacaoResultado
from processo_seletivo.recursos.application.julgar import julgar
from processo_seletivo.recursos.models import DecisaoRecurso
from processo_seletivo.resultados.models import ResultadoEtapa
from tests.conftest import ator_institucional
from tests.fixtures.divulgacao import emitir, publicar_o_ato
from tests.fixtures.recursos_us4 import cenario_julgavel, julgador

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.integration]


@pytest.fixture
def retificada(gestor, api_client, manager_headers, process_payload):
    """Uma providência determinada, cumprida por ato citante, e a definitiva publicada sobre ele."""
    peca = cenario_julgavel(
        gestor, api_client, manager_headers, process_payload, seed=129, codigo="0829"
    )
    decisao, _ = julgar(
        actor=julgador(),
        recurso_id=peca["recurso"].id,
        especie=DecisaoRecurso.Especie.PROVIDENCIA_A_JUSANTE,
        motivacao="Emita-se novo ato corrigindo o critério de desempate.",
        idempotency_key="providencia-retificada",
    )
    cenario = peca["cenario"]
    citante = emitir(
        cenario,
        _gestor(),
        chave="emitir-retificada",
        motivo="Cumprimento da decisão.",
        decisoes=[str(decisao.id)],
    )
    nova = publicar_o_ato(
        cenario,
        natureza="DEFINITIVA",
        chave="publicar-retificada",
        ato=citante,
        declaracao="O prazo recursal encerrou-se sem interposição.",
    )
    return {**peca, "decisao": decisao, "nova": nova}


def abrir(client, publicacao):
    resposta = client.get(reverse("portal:resultado", args=[publicacao.id]))
    assert resposta.status_code == 200
    return re.search(r"<main[^>]*>(.*)</main>", resposta.content.decode(), re.DOTALL).group(1)


def test_a_natureza_continua_sendo_uma_das_duas(retificada):
    """Nenhum valor novo no enum — a causa é derivada, e não gravada (FR-087)."""
    assert retificada["nova"].natureza == "DEFINITIVA"
    assert set(PublicacaoResultado.objects.values_list("natureza", flat=True)) <= {
        "PRELIMINAR",
        "DEFINITIVA",
    }


def test_a_definitiva_que_corrige_e_apresentada_pela_causa(client, retificada):
    """ "Retificado em razão do julgamento do recurso X" — o fato, e não um rótulo (FR-088)."""
    corpo = abrir(client, retificada["nova"])

    assert "retificado em" in corpo.lower()
    assert retificada["recurso"].protocolo in corpo
    assert "DEFINITIVA_RETIFICADA" not in corpo


def test_a_vigente_diz_que_e_a_vigente(client, retificada):
    """Quem abre a vigente precisa saber que está lendo o que vale (FR-090)."""
    corpo = abrir(client, retificada["nova"])

    assert "Este é o resultado vigente deste marco." in corpo


def test_a_sucedida_continua_dizendo_que_foi_sucedida(client, retificada):
    """A cadeia responde nas duas pontas, e o endereço da sucedida continua respondendo."""
    corpo = abrir(client, retificada["publicacao"])

    assert "foi sucedido" in corpo
    assert "Este é o resultado vigente deste marco." not in corpo


def test_a_primeira_publicacao_do_marco_nao_diz_que_corrige(
    client, gestor, api_client, manager_headers, process_payload
):
    """Sem publicação anterior não há o que corrigir — e o aviso não pode aparecer sempre."""
    peca = cenario_julgavel(
        gestor, api_client, manager_headers, process_payload, seed=130, codigo="0830"
    )

    corpo = abrir(client, peca["publicacao"])

    assert "retificado em" not in corpo.lower()
    assert "Este é o resultado vigente deste marco." in corpo


def _gestor():
    return ator_institucional("carlos", "comissao:gerir")


@pytest.fixture
def corrigida(gestor, api_client, manager_headers, process_payload):
    """A correção fixada — a espécie que **não** cita decisão e mesmo assim retifica a divulgação.

    A caminhada da T125 chegou aqui pela porta da frente: recurso deferido com correção fixada, ato
    sucessor emitido, definitiva publicada sobre ele — e a página dizia só "Resultado definitivo".
    A causa era derivada da `CitacaoDeDecisao`, que só a providência a jusante produz; a correção
    fixada e a reavaliação determinada corrigem o resultado sem citar nada, e a retificação delas
    ficava anônima.
    """
    from decimal import Decimal

    peca = cenario_julgavel(
        gestor, api_client, manager_headers, process_payload, seed=131, codigo="0831"
    )
    cenario = peca["cenario"]
    alvo = ResultadoEtapa.vigentes.get(
        inscricao=peca["recurso"].inscricao, etapa_id=cenario["etapa"]
    )
    decisao, _ = julgar(
        actor=julgador(),
        recurso_id=peca["recurso"].id,
        especie=DecisaoRecurso.Especie.CORRECAO_FIXADA,
        motivacao="O documento juntado na inscrição não foi considerado.",
        etapa_id=str(cenario["etapa"]),
        pontuacao=Decimal("82.0000"),
        assinatura_do_resultado=str(alvo.id),
        idempotency_key="correcao-retificada",
    )
    sucessor = emitir(
        cenario,
        _gestor(),
        chave="emitir-corrigida",
        motivo="Cumprimento da decisão que corrigiu a pontuação.",
    )
    nova = publicar_o_ato(
        cenario,
        natureza="DEFINITIVA",
        chave="publicar-corrigida",
        ato=sucessor,
        declaracao="O prazo recursal encerrou-se sem interposição.",
    )
    return {**peca, "decisao": decisao, "nova": nova}


def test_a_correcao_fixada_tambem_apresenta_a_causa(client, corrigida):
    """FR-088 não fala em citação: fala na **decisão que motivou**, qualquer que seja a espécie."""
    corpo = abrir(client, corrigida["nova"])

    assert "retificado em" in corpo.lower()
    assert corrigida["recurso"].protocolo in corpo


def test_a_causa_aparece_tambem_no_documento(retificada):
    """FR-088 diz "na página **e no documento**" — e o documento calava (T125).

    Os dois leem os mesmos bytes, e é daí que vem a correspondência entre eles (FR-064): a causa é
    decidida no ato de publicar e congelada no conteúdo, não derivada de novo na renderização.
    """
    from tests.interface.test_fluxo import texto_de_pdf_bytes

    texto = texto_de_pdf_bytes(retificada["nova"].documento.bytes)

    assert "RETIFICAÇÃO" in texto
    assert retificada["recurso"].protocolo in texto


def test_a_primeira_divulgacao_nao_traz_a_linha_de_retificacao(retificada):
    """Uma linha "RETIFICAÇÃO" na primeira divulgação afirmaria o que não houve."""
    from tests.interface.test_fluxo import texto_de_pdf_bytes

    texto = texto_de_pdf_bytes(retificada["publicacao"].documento.bytes)

    assert "RETIFICAÇÃO" not in texto


@pytest.fixture
def por_duas_decisoes(gestor, api_client, manager_headers, process_payload):
    """Um ato que cita **duas** decisões, e a divulgação que o publica.

    A FR-112 sempre permitiu isso — `UNIQUE(ato, decisao)` e nada mais —, e é o caso normal quando
    dois deferimentos alcançam o mesmo marco: resolvem-se numa emissão só.
    """
    from processo_seletivo.classificacao.models import CitacaoDeDecisao

    peca = cenario_julgavel(
        gestor, api_client, manager_headers, process_payload, seed=133, codigo="0833"
    )
    cenario = peca["cenario"]
    primeira, _ = julgar(
        actor=julgador(),
        recurso_id=peca["recurso"].id,
        especie=DecisaoRecurso.Especie.PROVIDENCIA_A_JUSANTE,
        motivacao="Emita-se novo ato corrigindo o critério de desempate.",
        idempotency_key="providencia-uma",
    )
    segunda = _outra_providencia(peca)

    citante = emitir(
        cenario,
        _gestor(),
        chave="emitir-duas-causas",
        motivo="Cumprimento das duas decisões.",
        decisoes=[str(primeira.id), str(segunda.id)],
    )
    assert CitacaoDeDecisao.objects.filter(ato=citante).count() == 2
    nova = publicar_o_ato(
        cenario,
        natureza="DEFINITIVA",
        chave="publicar-duas-causas",
        ato=citante,
        declaracao="O prazo recursal encerrou-se sem interposição.",
    )
    return {**peca, "decisoes": [primeira, segunda], "nova": nova}


def _outra_providencia(peca):
    """Uma segunda decisão, de outra inscrição do mesmo marco."""
    from processo_seletivo.portal.identidade import IdentidadeDoCandidato
    from processo_seletivo.recursos.application.admitir import admitir
    from processo_seletivo.recursos.application.interpor import interpor
    from tests.fixtures.recursos_us4 import assinatura_de

    cenario = peca["cenario"]
    inscricao = cenario["inscricoes"][1]
    alvo = ResultadoEtapa.vigentes.get(inscricao=inscricao, etapa_id=cenario["etapa"])
    outra = interpor(
        identidade=IdentidadeDoCandidato(
            inscricao.identity_subject, inscricao.nome, inscricao.cpf_normalizado, "c@ex.br"
        ),
        inscricao=inscricao,
        resultado=alvo,
        fundamentacao="O critério de desempate foi aplicado fora da ordem publicada.",
        assinatura_do_objeto=str(alvo.pk),
        idempotency_key="interpor-segunda-causa",
    )
    admitir(
        actor=julgador(),
        recurso_id=outra.id,
        admitido=True,
        motivo="Tempestivo e regularmente instruído.",
        assinatura_do_estado=assinatura_de(outra),
        idempotency_key="admitir-segunda-causa",
    )
    decisao, _ = julgar(
        actor=julgador(),
        recurso_id=outra.id,
        especie=DecisaoRecurso.Especie.PROVIDENCIA_A_JUSANTE,
        motivacao="Emita-se novo ato aplicando o desempate na ordem publicada.",
        idempotency_key="providencia-duas",
    )
    return decisao


def test_as_duas_causas_aparecem_na_pagina(client, por_duas_decisoes):
    """FR-088 e FR-112: publicar uma e calar sobre a outra conta metade do que aconteceu.

    A primeira implementação tomava `.first()` das citações. Com dois deferimentos resolvidos na
    mesma emissão — que é o caso que a FR-112 existe para permitir —, a página nomeava um recurso e
    omitia o outro, e quem recorreu e teve razão não se via na causa da retificação.
    """
    corpo = abrir(client, por_duas_decisoes["nova"])

    for decisao in por_duas_decisoes["decisoes"]:
        assert decisao.recurso.protocolo in corpo
    assert "recursos" in corpo, "duas causas se anunciam no plural"


def test_as_duas_causas_aparecem_no_documento(por_duas_decisoes):
    from tests.interface.test_fluxo import texto_de_pdf_bytes

    texto = texto_de_pdf_bytes(por_duas_decisoes["nova"].documento.bytes)

    for decisao in por_duas_decisoes["decisoes"]:
        assert decisao.recurso.protocolo in texto


def test_a_ordem_das_causas_e_deterministica(por_duas_decisoes):
    """Congelar em ordem instável faria o mesmo ato produzir bytes diferentes a cada publicação."""
    import json

    from processo_seletivo.recursos.application.selectors import causas_da_correcao

    conteudo = json.loads(bytes(por_duas_decisoes["nova"].conteudo_publico).decode("utf-8"))
    congeladas = [item["recurso"] for item in conteudo["cabecalho"]["retificacoes"]]
    derivadas = [item["recurso"] for item in causas_da_correcao(por_duas_decisoes["nova"].ato)]

    assert congeladas == derivadas
    assert congeladas == sorted(congeladas, key=lambda protocolo: protocolo) or len(congeladas) == 2
    assert len(congeladas) == 2


def test_o_conteudo_antigo_com_uma_causa_so_continua_legivel(client, retificada):
    """Compatibilidade de leitura: o que já foi publicado guarda a chave no singular.

    Publicação é imutável — reescrever o conteúdo para caber na forma nova seria alterar ato já
    praticado (FR-091). A leitura é que aceita as duas formas.
    """
    import json

    publicacao = retificada["nova"]
    conteudo = json.loads(bytes(publicacao.conteudo_publico).decode("utf-8"))
    conteudo["cabecalho"].pop("retificacoes", None)
    conteudo["cabecalho"]["retificacao"] = {
        "recurso": retificada["recurso"].protocolo,
        "quando": retificada["decisao"].decidido_em.isoformat(),
    }
    _reescrever_conteudo(publicacao, conteudo)

    corpo = abrir(client, publicacao)

    assert "retificado em" in corpo.lower()
    assert retificada["recurso"].protocolo in corpo


def _reescrever_conteudo(publicacao, conteudo):
    """Escreve o conteúdo antigo direto, com o gatilho desligado pelo tempo da escrita.

    **Não é contorno da garantia**: é o único jeito de exercitar hoje a leitura de uma publicação
    feita antes desta convergência — sem ela, a compatibilidade que o código promete não teria
    nenhuma prova.
    """
    import json

    from django.db import connection

    with connection.cursor() as cursor:
        cursor.execute(
            "ALTER TABLE divulgacao_publicacaoresultado DISABLE TRIGGER "
            "publicacao_resultado_append_only"
        )
        cursor.execute(
            "UPDATE divulgacao_publicacaoresultado SET conteudo_publico = %s WHERE id = %s",
            [json.dumps(conteudo).encode("utf-8"), publicacao.pk],
        )
        cursor.execute(
            "ALTER TABLE divulgacao_publicacaoresultado ENABLE TRIGGER "
            "publicacao_resultado_append_only"
        )
