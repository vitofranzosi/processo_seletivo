"""O custo da condução quando as convocações pedem documentos (115, FR-3607).

**A condução é a tela que a comissão abre dez vezes por dia**, e a `115` acrescentou a cada linha o
estado documental, a contagem dos itens e o caminho até a página dos documentos. Uma consulta por
linha não aparece com cinco convocações — aparece no 28/2026, com 85. O que se prende aqui é a mesma
propriedade de `test_convocacao.py`: a curva é plana, e o custo é do recorte, não da linha.

**O cenário tem tudo o que a leitura percorre**: a lista gravada em cada chamada, arquivo
apresentado, conferência pendente e chamada corrigida por sucessora — a sucessora é o que faz
`raizes_das` perguntar ao banco, e uma cadeia subida elo a elo seria uma consulta por correção.
"""

import pytest
from django.db import connection
from django.test.utils import CaptureQueriesContext
from django.urls import reverse
from django.utils import timezone

from processo_seletivo.convocacao.application.documentos import gravar_lista_da_chamada
from processo_seletivo.convocacao.models import Convocacao
from processo_seletivo.publicacoes.application.selectors import effective_version
from tests.fixtures import documentos_da_convocacao as cenarios
from tests.fixtures.corte import MARCO
from tests.fixtures.documentos_da_convocacao import CERTIDAO, HISTORICO
from tests.interface.conftest import identificar
from tests.performance.test_convocacao import semear

#: Os três estados que o cenário produz, como a linha da condução os escreve.
ROTULOS = ("Documentos com pendência", "Documentos para conferir", "Aguardando documentação")

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.integration]


@pytest.fixture
def edital(db, gestor, api_client, manager_headers, process_payload, raiz_de_arquivos, settings):
    settings.INTERFACE_SELETOR_IDENTIDADE = True
    edital, _, _ = cenarios.montar(
        gestor,
        api_client,
        manager_headers,
        process_payload,
        documentos=cenarios.documentos_do_aluno(),
        prefixo="perf-115",
    )
    return edital


def com_documentos(edital, gestor, inscricoes):
    """A lista de cada chamada semeada, e trabalho documental em todas as formas que a tela lê.

    **A lista pelo serviço, e não por `bulk_create`**: é ela que decide os itens aplicáveis, e
    gravá-la à mão mediria um cenário que o sistema não produz.
    """
    versao = effective_version(edital_id=edital.id)
    for inscricao in inscricoes:
        # A posição vem do protocolo, e não do laço: as duas levas de `semear` continuam a mesma
        # repartição, e a contagem dos rótulos no fim é a do recorte inteiro.
        posicao = int(inscricao.protocolo.rsplit("P", 1)[1])
        convocacao = Convocacao.objects.get(inscricao=inscricao)
        gravar_lista_da_chamada(convocacao, versao=versao)
        # Um terço com pendência, um terço para conferir, e um terço sem nada enviado.
        if posicao % 3 == 0:
            cenarios.apresentar(
                inscricao, convocacao, CERTIDAO, corpo=f"certidao {posicao}".encode()
            )
            cenarios.conferir(
                gestor, convocacao, CERTIDAO, "CONFORME", chave=f"perf-115-conforme-{posicao}"
            )
            cenarios.apresentar(
                inscricao, convocacao, HISTORICO, corpo=f"historico {posicao}".encode()
            )
            cenarios.conferir(
                gestor,
                convocacao,
                HISTORICO,
                "PENDENTE",
                chave=f"perf-115-pendente-{posicao}",
                motivo="Falta a última página.",
            )
        elif posicao % 3 == 1:
            cenarios.apresentar(
                inscricao, convocacao, CERTIDAO, corpo=f"certidao {posicao}".encode()
            )
        if posicao % 5 == 0:
            Convocacao.objects.create(
                edital=convocacao.edital,
                perfil_id=convocacao.perfil_id,
                marco_id=convocacao.marco_id,
                lista_id=convocacao.lista_id,
                inscricao=inscricao,
                especie=convocacao.especie,
                fundamento=convocacao.fundamento,
                apuracao=convocacao.apuracao,
                ato_de_ordenacao_id=convocacao.ato_de_ordenacao_id,
                corte_id=convocacao.corte_id,
                versao=convocacao.versao,
                criado_por="medicao",
                criado_em=timezone.now(),
                convocacao_anterior=convocacao,
                motivo_da_sucessao="Corrigida para a medição.",
            )


def consultas_da_conducao(client, edital, **parametros):
    caminho = reverse("interface:convocacao", args=[edital.id, MARCO])
    with CaptureQueriesContext(connection) as capturadas:
        resposta = client.get(caminho, parametros)
    assert resposta.status_code == 200
    return len(capturadas), resposta.content.decode()


@pytest.mark.parametrize("ordem", ["", "documentos"])
def test_a_conducao_nao_consulta_por_convocacao_com_documentos(edital, gestor, client, ordem):
    """5 e 45 convocações com documentos custam o mesmo, nas duas ordens da tela.

    **A folga de duas consultas é a de `test_convocacao.py`**, pela mesma razão: o cache de
    permissões e a sessão variam entre a primeira e a segunda leitura sem que o desenho mude. Uma
    consulta por linha faria a segunda medição custar dezenas a mais.
    """
    identificar(client, "carlos", ["gestor"])
    com_documentos(edital, gestor, semear(edital, 5))
    poucas, corpo = consultas_da_conducao(client, edital, ordem=ordem)
    assert "Documentos da convocação" in corpo

    com_documentos(edital, gestor, semear(edital, 40, desde=5))
    muitas, corpo = consultas_da_conducao(client, edital, ordem=ordem)

    # 45 convocações, de 0 a 44: 15 em cada terço.
    assert [corpo.count(rotulo) for rotulo in ROTULOS] == [15, 15, 15]
    assert muitas <= poucas + 2, (
        f"a condução passou de {poucas} para {muitas} consultas ao ir de 5 para 45 convocações "
        "com documentos: há uma consulta por linha em algum ponto"
    )
