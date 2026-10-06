"""O custo de "Minhas inscrições" quando a lista passa a falar de convocação (059, `SC-426`).

**A lista ganhou uma leitura, e ela precisa ser uma só.** Mostrar a convocação de cada item é o
desenho exato do defeito que `test_area_do_candidato.py` existe para pegar: uma consulta por
inscrição, invisível com três e fatal com trezentas. O seletor lê por conjunto; este arquivo prova
que a **tela** também — porque um `desfecho_de` chamado no laço sem o prefetch certo desfaria o
seletor sem que o teste dele visse.

**E o requerimento continua fora da lista.** A `029` decidiu que o estado dele se lê na tela dele, e
prende o zero em `test_orcamento_de_consulta.py`; o caso que aquele teste não cobria é o de quem
**tem** convocação, que é justamente quem esta feature faz a lista mostrar.
"""

import pytest
from django.db import connection
from django.test.utils import CaptureQueriesContext
from django.urls import reverse
from django.utils import timezone

from processo_seletivo.convocacao.application import selectors
from processo_seletivo.identidade.models import CandidateIdentity
from processo_seletivo.portal.identidade import CHAVE_SESSAO
from tests.fixtures.convocacao import convocar, montar_cenario_da_convocacao
from tests.fixtures.corte import MARCO
from tests.fixtures.edital import PROFILE_ID

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.performance]


@pytest.fixture
def cenario(db, gestor, api_client, manager_headers, process_payload, raiz_de_arquivos):
    return montar_cenario_da_convocacao(
        gestor, api_client, manager_headers, process_payload, prefixo="portal-059-custo"
    )


def convocada(cenario, gestor):
    edital, _, inscricoes = cenario
    alvo = selectors.contexto_do_recorte(
        edital=edital, perfil_id=PROFILE_ID, marco_id=MARCO, lista_id=None
    )["fila"][0]
    convocar(edital, gestor, alvo, idempotency_key="custo-1")
    return next(i for i in inscricoes if i.id == alvo)


def entrar(client, subject):
    registro, _ = CandidateIdentity.objects.get_or_create(
        subject=subject, defaults={"created_at": timezone.now()}
    )
    sessao = client.session
    sessao[CHAVE_SESSAO] = str(registro.pk)
    sessao.save()


def medir(client):
    """Duas cargas, e só a segunda contada: a primeira aquece o cache do conteúdo publicado."""
    url = reverse("portal:inscricoes")
    client.get(url)
    with CaptureQueriesContext(connection) as capturadas:
        resposta = client.get(url)
    assert resposta.status_code == 200
    return capturadas


def test_a_lista_le_a_convocacao_numa_consulta_so(client, cenario, gestor):
    """**Uma** consulta à tabela das convocações, com `IN`, e as duas dos prefetches — e só.

    O seletor já prova que o custo dele não cresce com as inscrições nem com as convocações
    (`tests/integration/convocacao/test_vigentes_por_inscricao.py`). O que resta provar é que a
    tela não desfaz isso: um `desfecho_de` sem o prefetch, chamado no laço dos itens, seria uma
    consulta por item — e apareceria aqui como uma segunda leitura de `convocacao_`.
    """
    pessoa = convocada(cenario, gestor)
    entrar(client, pessoa.identity_subject)

    capturadas = medir(client)
    da_convocacao = [c["sql"] for c in capturadas if '"convocacao_' in c["sql"]]

    assert "Convocação aberta" in client.get(reverse("portal:inscricoes")).content.decode()
    assert len(da_convocacao) == 3, da_convocacao
    principal = [sql for sql in da_convocacao if 'FROM "convocacao_convocacao"' in sql]
    assert len(principal) == 1 and " IN (" in principal[0], principal


def test_a_lista_de_quem_foi_convocado_nao_toca_o_requerimento(client, cenario, gestor):
    """O zero da `029` vale também para quem tem convocação — e é dela que a lista agora fala."""
    pessoa = convocada(cenario, gestor)
    entrar(client, pessoa.identity_subject)

    capturadas = medir(client)

    assert [c["sql"] for c in capturadas if "requerimentos_" in c["sql"]] == []
    assert any("convocacao_" in c["sql"] for c in capturadas), (
        "a medição precisa enxergar a leitura da convocação, ou o zero acima não diz nada"
    )


@pytest.fixture
def dois_titulares(db, gestor, api_client, manager_headers, process_payload, raiz_de_arquivos):
    """Duas vagas e faixa de três: dois titulares, que se convocam sem disputar vaga."""
    from tests.fixtures.corte import regra

    return montar_cenario_da_convocacao(
        gestor,
        api_client,
        manager_headers,
        process_payload,
        prefixo="portal-059-itens",
        geral=2,
        cut=regra(surplusCount=1),
    )


def test_o_item_da_lista_nao_consulta_nada_em_tabela_nenhuma(dois_titulares, gestor):
    """**Zero consultas por item, qualquer que seja a tabela** — a terceira parcela da garantia.

    O custo da lista é a soma de três coisas: o que ela já lia antes da `059` (fixo), a leitura das
    convocações (constante, provada em `test_vigentes_por_inscricao.py` com uma e duas convocadas)
    e o que cada item custa ao ser montado e desenhado. Se a terceira for zero, a soma não cresce
    com o número de itens — e essa é a garantia contra N+1, sem precisar montar cinco certames.

    O teste acima, que filtra por `convocacao_`, não bastava para a terceira parcela: um item que
    lesse `chamada.inscricao` ou `chamada.apuracao` faria uma consulta por item a **outra** tabela,
    e passaria por ele. Aqui nada passa: a medição conta tudo.

    **Os itens são de várias pessoas**, e não de uma: `_item_da_lista` não olha a identidade, e é
    assim que um cenário só dá itens nos três estados — convocação aberta, concluída e nenhuma —,
    o que a lista de uma pessoa, presa a um Perfil por Edital, não daria sem dois certames.
    """
    from django.template.loader import render_to_string

    from processo_seletivo.convocacao.application.desfechar import desfechar
    from processo_seletivo.convocacao.domain import nomes as nomes_da_convocacao
    from processo_seletivo.inscricoes.models import Inscricao
    from processo_seletivo.portal import views

    edital, _, inscricoes = dois_titulares
    fila = selectors.contexto_do_recorte(
        edital=edital, perfil_id=PROFILE_ID, marco_id=MARCO, lista_id=None
    )["fila"]
    convocar(edital, gestor, fila[0], idempotency_key="itens-aberta")
    concluida = convocar(edital, gestor, fila[1], idempotency_key="itens-concluida")
    desfechar(
        actor=gestor,
        processo_id=edital.processo_id,
        convocacao_id=concluida["id"],
        especie=nomes_da_convocacao.ACEITE,
        fundamento="Manifestação registrada em processo.",
        idempotency_key="itens-concluida-desfecho",
        correlation_id="teste-059",
    )
    # O que a view lê antes do laço, do mesmo jeito que ela lê.
    registros = list(
        Inscricao.objects.filter(id__in=[i.id for i in inscricoes]).select_related("edital")
    )
    conteudos = views._conteudos_publicados(registros)
    convocacoes = views._convocacoes_da_lista(registros)
    agora = timezone.now()

    with CaptureQueriesContext(connection) as capturadas:
        itens = [
            views._item_da_lista(
                registro, conteudos.get(registro.edital_id), agora, convocacoes.get(registro.id)
            )
            for registro in registros
        ]
        html = render_to_string("portal/inscricoes.html", {"inscricoes": itens})

    estados = sorted(
        "aberta"
        if item["convocacao_aberta"]
        else "concluida"
        if item["convocacao_concluida"]
        else "nenhuma"
        for item in itens
    )
    assert estados.count("aberta") == 1 and estados.count("concluida") == 1, estados
    assert "nenhuma" in estados, "os três estados precisam estar no laço medido"
    assert "Convocação aberta" in html and "Convocação: Aceite" in html
    assert [c["sql"] for c in capturadas] == [], (
        f"{len(capturadas)} consulta(s) para {len(itens)} itens: "
        "o custo passou a crescer com a lista"
    )
