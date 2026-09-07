"""O que a sucessão quebra no cálculo, e qual metade da correção cobre cada coisa.

`calcular_ordem` monta, por inscrição, um dicionário indexado por `etapa_id`, e grava no universo
do ato o **conjunto de ids** dos Resultados que o produziram. Antes da 018, a unicidade
incondicional do
par tornava as duas coisas seguras por construção. A sucessão removeu essa garantia, e as duas
quebram de maneiras **diferentes** — coisa que a primeira redação deste arquivo não separava, e a
execução mostrou:

1. **o dicionário de pontuações colapsa**, e as duas linhas caem na mesma chave. Aqui o `order_by`
   determinístico por `consolidado_em` **basta**: o último a entrar é o sucessor, que é justamente o
   vigente. É por isso que a ordenação fica no código mesmo com o filtro — ela não é estilo, é a
   metade da correção que cobre este caminho, e sem ela o colapso passa a depender da ordem em que o
   banco devolveu as linhas;
2. **o universo cita os dois Resultados**, e esta é a que o `order_by` não cobre. Citando o
   superado, `comparar()` não vê diferença alguma quando o deferimento acontece: o ato **não fica
   obsoleto**, a publicação continua sendo oferecida, e a cadeia a jusante fica cega ao recurso. É
   exatamente o defeito pelo qual a alternativa 3 da decisão C foi descartada — e é `vigentes` que o
   impede.

Removido o filtro, é o segundo teste deste arquivo que falha. Vale registrar que o primeiro **não**
falha: o `order_by` o segura sozinho. Um teste que se anunciasse como prova do colapso e passasse
sem a correção seria pior que nenhum (018, T-004).
"""

from decimal import Decimal

import pytest
from django.urls import reverse

from processo_seletivo.classificacao.application.calculo import calcular_ordem
from processo_seletivo.comissoes.domain.funcoes import Funcao
from processo_seletivo.resultados.application.consolidacao import consolidar
from processo_seletivo.resultados.models import ResultadoEtapa
from tests.fixtures.comissao import alocar_em, constituir, inscrever, rascunho_com_etapas
from tests.fixtures.edital import PROFILE_ID
from tests.fixtures.mesa import concluir_como, distribuir_para
from tests.fixtures.publicacao import publish_original
from tests.fixtures.recursos import deferir_corrigindo

pytestmark = [pytest.mark.integration, pytest.mark.django_db(transaction=True)]

MARCO = "00000000-0000-4000-8000-000000000451"


@pytest.fixture
def cenario(gestor, api_client, manager_headers, process_payload):
    rascunho = rascunho_com_etapas(avaliacoes=1, maxima="100.0000", minima="60.0000")
    etapa = rascunho["stages"][1]
    etapa["weight"] = "1.0000"
    rascunho["profiles"][0]["classificationMilestones"] = [
        {
            "id": MARCO,
            "code": "FINAL",
            "name": "Classificação final",
            "stages": [etapa["id"]],
            "operation": "SOMA_PONDERADA",
            "normalization": "NENHUMA",
            "rounding": {"scale": 2, "mode": "MEIO_PARA_CIMA"},
            "tiebreakers": [],
        }
    ]
    edital = publish_original(api_client, manager_headers, process_payload, draft=rascunho)
    membros = constituir(
        gestor,
        edital.processo,
        [("maria", Funcao.PRESIDENTE), ("joao", Funcao.MEMBRO)],
        prefixo="vigencia-018",
    )
    alocar_em(gestor, edital.processo, membros["joao"], edital, etapa["id"])
    contexto = {
        "edital": edital,
        "processo": edital.processo,
        "membros": membros,
        "etapa": etapa["id"],
    }
    inscricoes = inscrever(edital, 2, primeiro=601)
    distribuir_para(contexto, gestor, ["joao"], inscricoes, chave="vigencia-018-lote")
    concluir_como(contexto, "joao", inscricoes[0], pontuacao="70.0000")
    concluir_como(contexto, "joao", inscricoes[1], pontuacao="90.0000")
    consolidar(
        actor=gestor,
        processo_id=edital.processo_id,
        edital_id=edital.id,
        etapa_id=etapa["id"],
        inscricao_ids=[item.id for item in inscricoes],
        idempotency_key="vigencia-018-consolidar",
        correlation_id="teste-vigencia-018",
    )
    return edital, etapa, inscricoes


def _versao(edital):
    from processo_seletivo.publicacoes.models_retificacao import VersaoConsolidada

    return VersaoConsolidada.objects.filter(edital=edital).latest("valid_from")


def test_o_sucessor_entra_na_ordem_e_o_superado_nao(cenario):
    """Deferido o recurso do último colocado, ele passa a liderar — e por 95, não por 70.

    **Este teste não é o que denuncia o colapso**, e dizer o contrário seria mentir: com o
    `order_by` por `consolidado_em`, o dicionário colapsa no sucessor mesmo sem o filtro, e o
    resultado sai certo por acidente. Ele existe para fixar o comportamento correto de ponta a
    ponta; quem prende a regressão é o teste seguinte.
    """
    edital, _etapa, inscricoes = cenario
    superado = ResultadoEtapa.objects.get(inscricao=inscricoes[0])

    deferir_corrigindo(
        superado,
        versao=_versao(edital),
        pontuacao=Decimal("95.0000"),
        consequencia=ResultadoEtapa.Consequencia.HABILITADA,
    )

    proposta = calcular_ordem(edital=edital, perfil_id=PROFILE_ID, marco_id=MARCO)

    assert [item["inscricao_id"] for item in proposta["posicoes"]] == [
        str(inscricoes[0].id),
        str(inscricoes[1].id),
    ]
    assert [item["pontuacao"] for item in proposta["posicoes"]] == [95, 90]


def test_o_universo_cita_o_sucessor_e_nao_o_superado(cenario):
    """A proveniência do ato precisa citar o Resultado que de fato o produziu.

    Se o universo citasse o superado, `comparar()` não veria diferença nenhuma quando o
    deferimento acontecesse — e o ato **não ficaria obsoleto**. A cadeia inteira a jusante ficaria
    cega ao recurso, que é exatamente o defeito pelo qual a alternativa 3 da decisão C foi
    descartada.
    """
    edital, _etapa, inscricoes = cenario
    superado = ResultadoEtapa.objects.get(inscricao=inscricoes[0])

    _recurso, _decisao, sucessor = deferir_corrigindo(
        superado,
        versao=_versao(edital),
        pontuacao=Decimal("95.0000"),
        consequencia=ResultadoEtapa.Consequencia.HABILITADA,
    )

    proposta = calcular_ordem(edital=edital, perfil_id=PROFILE_ID, marco_id=MARCO)
    citados = {item["id"] for item in proposta["universo"]["stageResults"]}

    assert str(sucessor.id) in citados
    assert str(superado.id) not in citados, (
        "o universo citou o Resultado superado: com ele ali, `comparar()` não veria mudança "
        "nenhuma no deferimento, o ato não ficaria obsoleto, e a publicação continuaria sendo "
        "oferecida sobre uma ordem que já não é a verdadeira"
    )


def test_a_leitura_do_calculo_e_determinstica_mesmo_sem_o_filtro(cenario):
    """A rede sob a rede: sem o filtro, o colapso volta — mas volta reproduzível.

    A ordenação por `(inscricao_id, etapa_id, consolidado_em, id)` não é estilo. Ela garante que,
    se um dia alguém remover o filtro de vigência, o dicionário de pontuações colapse **sempre no
    mesmo lado** — o mais recente — em vez de depender da ordem em que o banco devolveu as linhas.
    Um defeito determinístico é prendível por teste; um irreproduzível some da suíte.
    """
    edital, etapa, inscricoes = cenario
    superado = ResultadoEtapa.objects.get(inscricao=inscricoes[0])
    deferir_corrigindo(
        superado,
        versao=_versao(edital),
        pontuacao=Decimal("95.0000"),
        consequencia=ResultadoEtapa.Consequencia.HABILITADA,
    )

    sem_filtro = list(
        ResultadoEtapa.objects.filter(
            edital=edital, inscricao_id=inscricoes[0].id, etapa_id=etapa["id"]
        )
        .order_by("inscricao_id", "etapa_id", "consolidado_em", "id")
        .values_list("pontuacao", flat=True)
    )

    assert sem_filtro == [Decimal("70.0000"), Decimal("95.0000")], (
        "as duas linhas coexistem, e a ordenação as entrega da mais antiga para a mais nova — "
        "de modo que o colapso, se voltar, colapsa sempre no sucessor"
    )
    assert (
        ResultadoEtapa.vigentes.filter(
            edital=edital, inscricao_id=inscricoes[0].id, etapa_id=etapa["id"]
        ).count()
        == 1
    )


def test_a_pagina_publica_e_o_calculo_continuam_de_pe(cenario, client):
    """Nenhuma regressão de leitura: o Edital publicado continua acessível depois da sucessão."""
    edital, _etapa, inscricoes = cenario
    superado = ResultadoEtapa.objects.get(inscricao=inscricoes[0])
    deferir_corrigindo(
        superado,
        versao=_versao(edital),
        pontuacao=Decimal("95.0000"),
        consequencia=ResultadoEtapa.Consequencia.HABILITADA,
    )

    resposta = client.get(reverse("portal:vitrine"))

    assert resposta.status_code == 200


def test_a_reproducao_historica_nao_regride(cenario, gestor):
    """Um ato emitido **antes** do deferimento reproduz a ordem que constituiu (SC-011, FR-062).

    É a propriedade que separa a superação da alternativa 3 da decisão C, e ela é **por
    construção**: `reproduzir_ato` lê os Resultados por `pk__in` dos ids gravados na proveniência,
    e o superado permanece na tabela, imutável, com a pontuação que tinha quando o ato foi emitido.

    Este teste existe porque a propriedade é frágil de uma maneira específica: bastaria alguém
    acrescentar `vigentes` em `reproducao.py` — parecendo consistência — para que a reprodução
    passasse a recusar com `historical_input_missing` no dia do primeiro deferimento. A varredura
    estrutural declara essa exceção; este teste mostra o que ela protege.
    """
    from processo_seletivo.classificacao.application.emissao import (
        assinatura_da_proposta,
        emitir_ordem,
    )
    from processo_seletivo.classificacao.application.reproducao import (
        divergencias_da_reproducao,
        reproduzir_ato,
    )
    from processo_seletivo.classificacao.models import AtoDeOrdenacao

    edital, _etapa, inscricoes = cenario
    proposta = calcular_ordem(edital=edital, perfil_id=PROFILE_ID, marco_id=MARCO)
    emitir_ordem(
        actor=gestor,
        processo_id=edital.processo_id,
        edital_id=edital.id,
        perfil_id=PROFILE_ID,
        marco_id=MARCO,
        idempotency_key="emitir-vigencia-018",
        correlation_id="teste-vigencia-018",
        confirmacao_do_calculo=assinatura_da_proposta(proposta, ato_vigente=None),
    )
    ato = AtoDeOrdenacao.objects.get()

    superado = ResultadoEtapa.objects.get(inscricao=inscricoes[0])
    deferir_corrigindo(
        superado,
        versao=_versao(edital),
        pontuacao=Decimal("95.0000"),
        consequencia=ResultadoEtapa.Consequencia.HABILITADA,
    )

    reproduzido = reproduzir_ato(ato)

    assert divergencias_da_reproducao(ato, reproduzido=reproduzido) == []
    assert [item["pontuacao"] for item in reproduzido["posicoes"]] == [90, 70], (
        "o ato antigo precisa continuar reproduzindo a ordem que constituiu, com as entradas de "
        "então — 70, e não os 95 que o deferimento fixou depois"
    )
