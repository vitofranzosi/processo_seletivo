"""Os resultados divulgados na forma da seção Vagas: Perfil, etapa, lista (062).

Duas camadas. A árvore (`leitura.resultados_por_perfil`) é provada em memória, sem banco: é ali que
moram as três ordens e as duas reservas de nome. A página é provada com publicações gravadas, e é
ali que se cobram o contrato da marcação, o nome acessível, o convite e o custo.
"""

import json
import re
import uuid
from datetime import UTC, datetime, timedelta
from types import SimpleNamespace
from urllib.parse import urlencode

import pytest
from django.urls import reverse
from django.utils import timezone

from processo_seletivo.classificacao.models import AtoDeOrdenacao, OrigemDaOrdem
from processo_seletivo.divulgacao.models import Natureza, PublicacaoResultado
from processo_seletivo.inscricoes.models import Inscricao
from processo_seletivo.portal.leitura import resultados_por_perfil
from processo_seletivo.publicacoes.models_retificacao import VersaoConsolidada
from tests.fixtures.comissao import rascunho_com_etapas
from tests.fixtures.edital import complete_draft, marco_minimo
from tests.fixtures.publicacao import publish_original

PERFIL_A = "00000000-0000-4000-8000-0000000062a1"
PERFIL_B = "00000000-0000-4000-8000-0000000062b2"
PERFIL_RETIRADO = "00000000-0000-4000-8000-0000000062c3"
ESCRITA = "00000000-0000-4000-8000-0000000062e1"
FINAL = "00000000-0000-4000-8000-0000000062e2"
PCD = "00000000-0000-4000-8000-0000000062d1"
PPI = "00000000-0000-4000-8000-0000000062d2"
DESCONHECIDA = "00000000-0000-4000-8000-0000000062d9"

INICIO = datetime(2026, 9, 23, 12, 0, tzinfo=UTC)

CONTEUDO = {
    "profiles": [
        {
            "id": PERFIL_A,
            "name": "Professor Substituto — Matemática",
            "competitionModalities": [
                {"id": PPI, "name": "Pessoas pretas, pardas e indígenas"},
                {"id": PCD, "name": "Pessoas com deficiência"},
            ],
        },
        {"id": PERFIL_B, "name": "Técnico de Laboratório — Química"},
    ]
}


def _item(perfil, marco, lista=None, *, lista_nome="", minutos=0, marco_nome="", codigo="", **mais):
    publicacao = SimpleNamespace(
        perfil_id=perfil,
        marco_id=marco,
        lista_id=lista,
        publicado_em=INICIO + timedelta(minutes=minutos),
    )
    return {
        "publicacao": publicacao,
        "natureza_rotulo": "Resultado definitivo",
        "marco": marco_nome,
        "marco_codigo": codigo,
        "lista": lista_nome or ("Ampla concorrência" if lista is None else "?"),
        "perfil": mais.pop("perfil_nome", ""),
        "anteriores": mais.pop("anteriores", []),
        "recurso_ate": None,
    }


def _nomes(arvore):
    return [perfil["nome"] for perfil in arvore]


# --- A árvore, em memória ----------------------------------------------------------------------


def test_os_perfis_seguem_a_ordem_da_secao_vagas_e_nao_a_da_publicacao():
    """FR-1149: o Perfil B foi publicado antes, e o A continua primeiro, como na seção Vagas."""
    vigentes = [_item(PERFIL_B, FINAL, minutos=0), _item(PERFIL_A, FINAL, minutos=5)]

    assert _nomes(resultados_por_perfil(vigentes, CONTEUDO)) == [
        "Professor Substituto — Matemática",
        "Técnico de Laboratório — Química",
    ]


def test_o_perfil_retirado_vem_por_ultimo_com_o_nome_gravado():
    """FR-1149, FR-1152: um resultado publicado não deixa de ser alcançável porque a vaga saiu."""
    vigentes = [
        _item(PERFIL_RETIRADO, FINAL, perfil_nome="Intérprete de Libras"),
        _item(PERFIL_B, FINAL, minutos=5),
    ]

    assert _nomes(resultados_por_perfil(vigentes, CONTEUDO)) == [
        "Técnico de Laboratório — Química",
        "Intérprete de Libras",
    ]


def test_o_nome_do_perfil_e_o_vigente_e_nao_o_gravado():
    """FR-1152, D-004: o mesmo Perfil não aparece com dois nomes na mesma página."""
    vigentes = [_item(PERFIL_A, FINAL, perfil_nome="Professor de Matemática (nome antigo)")]

    assert _nomes(resultados_por_perfil(vigentes, CONTEUDO)) == [
        "Professor Substituto — Matemática"
    ]


def test_as_etapas_seguem_a_ordem_do_certame_e_nao_a_da_divulgacao():
    """FR-1150, D-010: a classificação final saiu antes, e a prova escrita continua primeiro."""
    vigentes = [
        _item(PERFIL_A, FINAL, minutos=0, marco_nome="Classificação final", codigo="M2"),
        _item(PERFIL_A, ESCRITA, minutos=5, marco_nome="Prova escrita", codigo="M1"),
    ]

    (perfil,) = resultados_por_perfil(vigentes, CONTEUDO)

    assert [etapa["nome"] for etapa in perfil["etapas"]] == ["Prova escrita", "Classificação final"]


def test_a_ampla_vem_primeiro_e_as_listas_na_ordem_declarada_pelo_perfil():
    """FR-1151, D-008: o Perfil declara PPI antes de PcD, e a desconhecida vai para o fim."""
    vigentes = [
        _item(PERFIL_A, FINAL, DESCONHECIDA, lista_nome="Lista retirada"),
        _item(PERFIL_A, FINAL, PCD, lista_nome="Pessoas com deficiência"),
        _item(PERFIL_A, FINAL, PPI, lista_nome="Pessoas pretas, pardas e indígenas"),
        _item(PERFIL_A, FINAL, None),
    ]

    (perfil,) = resultados_por_perfil(vigentes, CONTEUDO)
    (etapa,) = perfil["etapas"]

    assert [lista["nome"] for lista in etapa["listas"]] == [
        "Ampla concorrência",
        "Pessoas pretas, pardas e indígenas",
        "Pessoas com deficiência",
        "Lista retirada",
    ]


def test_o_titulo_da_etapa_e_o_da_vigente_mais_recente():
    """D-010: duas listas publicadas sob nomes de marco diferentes; vale o mais recente, inteiro."""
    vigentes = [
        _item(PERFIL_A, FINAL, None, minutos=0, marco_nome="Classificação"),
        _item(PERFIL_A, FINAL, PCD, minutos=9, marco_nome="Classificação final — Matemática"),
    ]

    (perfil,) = resultados_por_perfil(vigentes, CONTEUDO)

    assert perfil["etapas"][0]["nome"] == "Classificação final — Matemática"


def test_o_historico_da_etapa_junta_as_listas_sem_misturar_as_cadeias():
    """FR-1157, FR-1159, D-001: um histórico por etapa, na ordem das listas, cada item com a sua."""
    anterior_ampla = {"lista": "Ampla concorrência", "publicacao": "p-ampla"}
    anterior_ppi = [
        {"lista": "Pessoas pretas, pardas e indígenas", "publicacao": "p-ppi-2"},
        {"lista": "Pessoas pretas, pardas e indígenas", "publicacao": "p-ppi-1"},
    ]
    vigentes = [
        _item(PERFIL_A, FINAL, PPI, lista_nome="PPI", anteriores=anterior_ppi),
        _item(PERFIL_A, FINAL, None, anteriores=[anterior_ampla]),
        _item(PERFIL_A, FINAL, PCD, lista_nome="PcD"),
    ]

    (perfil,) = resultados_por_perfil(vigentes, CONTEUDO)
    (etapa,) = perfil["etapas"]

    assert [item["publicacao"] for item in etapa["anteriores"]] == [
        "p-ampla",
        "p-ppi-2",
        "p-ppi-1",
    ]


def test_a_etapa_sem_publicacao_sucedida_tem_historico_vazio():
    """FR-1157: sem sucedida, nada a recolher — e o template não desenha o bloco."""
    (perfil,) = resultados_por_perfil([_item(PERFIL_A, FINAL)], CONTEUDO)

    assert perfil["etapas"][0]["anteriores"] == []


def test_sem_vigente_nao_ha_arvore():
    assert resultados_por_perfil([], CONTEUDO) == []


# --- A página, com publicações gravadas --------------------------------------------------------

NOME_A = "Professor Substituto — Matemática"
NOME_B = "Técnico de Laboratório — Química"
PCD_NOME = "Pessoas com deficiência"
PPI_NOME = "Pessoas pretas, pardas e indígenas"
LISTA_PCD = "00000000-0000-4000-8000-0000000062f1"
LISTA_PPI = "00000000-0000-4000-8000-0000000062f2"
# As etapas são por Perfil: o gatilho da `015` recusa ato cujo marco não esteja declarado no Perfil
# que ele ordena, e marco é identidade única no Edital.
ETAPAS = (("escrita", "M1", "Prova escrita"), ("final", "M2", "Classificação final"))


def _marco_do_perfil(perfil_id, etapa):
    return str(uuid.uuid5(uuid.NAMESPACE_URL, f"062/{perfil_id}/{etapa}"))


@pytest.fixture
def certame(api_client, manager_headers, process_payload):
    """Dois Perfis publicados, com os nomes da captura do Edital 72/2026 que motivou a feature."""
    rascunho = rascunho_com_etapas()
    rascunho["profiles"][0]["name"] = NOME_A
    segundo = {**complete_draft(2)["profiles"][0], "code": "P2", "name": NOME_B}
    rascunho["profiles"].append(segundo)
    for perfil in rascunho["profiles"]:
        perfil["classificationMilestones"] = [
            marco_minimo(_marco_do_perfil(perfil["id"], etapa), codigo=codigo, nome=nome)
            for etapa, codigo, nome in ETAPAS
        ]
    edital = publish_original(api_client, manager_headers, process_payload, draft=rascunho)
    return SimpleNamespace(
        edital=edital,
        versao=VersaoConsolidada.objects.filter(edital=edital).latest("materialized_at"),
        perfil_a=rascunho["profiles"][0]["id"],
        perfil_b=segundo["id"],
        relogio=iter(range(10_000)),
    )


def _ato(certame, perfil_id, etapa, lista_id=None):
    marco_id = _marco_do_perfil(perfil_id, etapa)
    return AtoDeOrdenacao.objects.create(
        edital=certame.edital,
        perfil_id=perfil_id,
        marco_id=marco_id,
        lista_id=lista_id,
        origem=OrigemDaOrdem.SORTEIO,
        versao=certame.versao,
        universo={
            "editalId": str(certame.edital.id),
            "profileId": perfil_id,
            "milestoneId": marco_id,
            "versionId": str(certame.versao.id),
            "stageResults": [],
            "origem": "SORTEIO",
        },
        emitido_por="cpf:presidente",
        emitido_em=timezone.now(),
    )


def _publicar(certame, ato, *, natureza=Natureza.DEFINITIVA, anterior=None, **cabecalho):
    """A gravação dos testes da 047, com o cabeçalho que `compor` congela; o teste é da leitura.

    O relógio anda um minuto por publicação, para que a cadeia e a "mais recente" sejam as que o
    teste escreveu, e não as que o instante da máquina sortear.
    """
    cabecalho = {
        "perfil": NOME_A if str(ato.perfil_id) == certame.perfil_a else NOME_B,
        "marco": "Classificação final",
        "marco_codigo": "M2",
        "lista": "",
        **cabecalho,
    }
    return PublicacaoResultado.objects.create(
        edital=certame.edital,
        ato=ato,
        perfil_id=ato.perfil_id,
        marco_id=ato.marco_id,
        lista_id=ato.lista_id,
        natureza=natureza,
        publicacao_anterior=anterior,
        conteudo_publico=json.dumps({"cabecalho": cabecalho, "posicoes": []}).encode(),
        conteudo_publico_hash="0" * 64,
        publicado_por="cpf:publicadora",
        publicado_em=INICIO + timedelta(minutes=next(certame.relogio)),
        signatario_id=uuid.uuid4(),
        signatario_nome="Diretora-Geral",
        signatario_cargo="Diretoria",
    )


def _tres_listas(certame, perfil_id, *, com_preliminar=False, etapa="final", **cabecalho):
    """Ampla, PcD e PPI de um Perfil numa etapa; com preliminar, cada uma sucedida."""
    publicadas = {}
    for lista_id, nome in ((None, ""), (LISTA_PCD, PCD_NOME), (LISTA_PPI, PPI_NOME)):
        ato = _ato(certame, perfil_id, etapa, lista_id)
        anterior = (
            _publicar(certame, ato, natureza=Natureza.PRELIMINAR, lista=nome, **cabecalho)
            if com_preliminar
            else None
        )
        publicadas[nome or "Ampla concorrência"] = (
            _publicar(certame, ato, anterior=anterior, lista=nome, **cabecalho),
            anterior,
        )
    return publicadas


def _secao(client, edital):
    corpo = client.get(reverse("portal:selecao", args=[edital.id])).content.decode()
    achado = re.search(r'<section class="resultados.*?</section>', corpo, flags=re.S)
    return achado.group(0) if achado else ""


def _links(secao):
    """Cada link do bloco como (destino, texto visível, nome acessível)."""
    return [
        (destino, miolo.split("<span")[0], re.sub(r"<[^>]+>", "", miolo))
        for destino, miolo in re.findall(r'<a [^>]*href="([^"]+)"[^>]*>(.*?)</a>', secao, re.S)
    ]


def _arvore(secao):
    """O bloco sem o convite: o que se conta aqui são os links das publicações."""
    return secao.split('<aside class="convite-da-situacao"')[0]


def _grupos(secao):
    return re.findall(
        r'<div class="resultados-do-perfil">.*?'
        r'(?=<div class="resultados-do-perfil">|<aside|</section>)',
        secao,
        re.S,
    )


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
class TestNaPagina:
    def test_um_grupo_por_perfil_na_ordem_da_secao_vagas(self, client, certame):
        """US1 cenário 1, FR-1148, FR-1149: B publicado antes, e A continua primeiro."""
        de_b = _tres_listas(certame, certame.perfil_b)
        de_a = _tres_listas(certame, certame.perfil_a)

        grupos = _grupos(_secao(client, certame.edital))

        assert [re.search(r"<h3>(.*?)</h3>", grupo).group(1) for grupo in grupos] == [
            NOME_A,
            NOME_B,
        ]
        for grupo, publicadas, alheias in ((grupos[0], de_a, de_b), (grupos[1], de_b, de_a)):
            for vigente, _ in publicadas.values():
                assert f"/resultados/{vigente.id}/" in grupo
            for vigente, _ in alheias.values():
                assert f"/resultados/{vigente.id}/" not in grupo

    def test_a_etapa_e_titulo_e_cada_lista_traz_natureza_e_data_na_linha(self, client, certame):
        """US1 cenários 2 e 4, FR-1153, FR-1154, UX-151: a hierarquia sem saltos."""
        _tres_listas(certame, certame.perfil_a, marco="Classificação final — Matemática")

        secao = _secao(client, certame.edital)
        titulos = re.findall(r"<(h[2-6])\b", secao)
        linhas = re.findall(r'<li class="lista-divulgada">.*?</li>', secao, re.S)

        assert titulos == ["h2", "h3", "h4"]
        assert "<h4>Classificação final — Matemática</h4>" in secao
        assert [visivel for _, visivel, _ in _links(_arvore(secao))] == [
            "Ampla concorrência",
            PCD_NOME,
            PPI_NOME,
        ]
        assert len(linhas) == 3
        for linha in linhas:
            assert "Resultado definitivo · publicado em 23/09/2026" in linha

    def test_os_dois_ampla_concorrencia_se_distinguem_pelo_nome_acessivel(self, client, certame):
        """US1 cenário 5, SC-443, SC-444, UX-152, e a decisão de 07/10 (Clarifications)."""
        _tres_listas(certame, certame.perfil_a, com_preliminar=True)
        _tres_listas(certame, certame.perfil_b, com_preliminar=True)

        links = _links(_arvore(_secao(client, certame.edital)))
        por_nome = {}
        for destino, _, acessivel in links:
            por_nome.setdefault(acessivel, set()).add(destino)

        assert len(links) == 12
        assert all(len(destinos) == 1 for destinos in por_nome.values()), por_nome
        assert len(por_nome) == 12
        assert all(acessivel.startswith(visivel) for _, visivel, acessivel in links)
        assert [visivel for _, visivel, _ in links].count("Ampla concorrência") == 4
        amplas = [a for _, v, a in links if v == "Ampla concorrência" and "publicado em" not in a]
        assert amplas == [
            f"Ampla concorrência — Classificação final — {NOME_A}",
            f"Ampla concorrência — Classificação final — {NOME_B}",
        ]

    def test_listas_em_fases_diferentes_dizem_cada_uma_a_sua(self, client, certame):
        """US2 cenário 1, FR-1155, SC-445: a natureza nunca sobe para a etapa nem para o Perfil."""
        for lista_id, nome, natureza in (
            (None, "", Natureza.DEFINITIVA),
            (LISTA_PCD, PCD_NOME, Natureza.DEFINITIVA),
            (LISTA_PPI, PPI_NOME, Natureza.PRELIMINAR),
        ):
            _publicar(
                certame,
                _ato(certame, certame.perfil_a, "final", lista_id),
                natureza=natureza,
                lista=nome,
            )

        secao = _secao(client, certame.edital)
        linhas = {
            re.search(r'">([^<]+)<span', linha).group(1): linha
            for linha in re.findall(r'<li class="lista-divulgada">.*?</li>', secao, re.S)
        }

        assert "Resultado definitivo" in linhas["Ampla concorrência"]
        assert "Resultado definitivo" in linhas[PCD_NOME]
        assert "Resultado preliminar" in linhas[PPI_NOME]
        for titulo in re.findall(r"<h[34]>(.*?)</h[34]>", secao):
            assert "Resultado" not in titulo and "publicado" not in titulo

    def test_mesmo_com_todas_iguais_a_natureza_fica_na_linha(self, client, certame):
        """Decisão recebida 2: a regra condicional foi recusada; nada sobe quando coincidem."""
        _tres_listas(certame, certame.perfil_a)

        secao = _secao(client, certame.edital)

        assert secao.count("Resultado definitivo") == 3
        for titulo in re.findall(r"<h[34]>(.*?)</h[34]>", secao):
            assert "Resultado" not in titulo

    def test_um_historico_por_etapa_com_a_lista_de_cada_item(self, client, certame):
        """US3 cenários 1–3, FR-1157 a FR-1159, SC-446, D-001."""
        publicadas = _tres_listas(certame, certame.perfil_a, com_preliminar=True)

        secao = _secao(client, certame.edital)
        blocos = re.findall(r'<details class="publicacoes-anteriores">.*?</details>', secao, re.S)

        assert len(blocos) == 1, "um bloco por etapa, e não um por lista"
        assert "Publicações anteriores (3)" in blocos[0]
        itens = re.findall(r"<li><a .*?</li>", blocos[0], re.S)
        assert len(itens) == 3
        for nome, (vigente, anterior) in publicadas.items():
            (item,) = [item for item in itens if f"/resultados/{anterior.id}/" in item]
            assert item.split("<span")[0].endswith(f">{nome}")
            assert "Resultado preliminar · publicado em 23/09/2026 · sucedido" in item
            assert f"/resultados/{vigente.id}/" not in blocos[0], "a vigente não é histórico"

    def test_so_a_etapa_com_sucedida_tem_historico(self, client, certame):
        """US3 cenário 4, FR-1150, FR-1157, SC-446: duas etapas, uma sucedida — um bloco."""
        _tres_listas(certame, certame.perfil_a, com_preliminar=True)
        _tres_listas(
            certame,
            certame.perfil_a,
            etapa="escrita",
            marco="Prova escrita",
            marco_codigo="M1",
        )

        secao = _secao(client, certame.edital)
        etapas = re.findall(
            r'<div class="resultados-da-etapa">.*?'
            r'(?=<div class="resultados-da-etapa">|</div>\s*</div>)',
            secao,
            re.S,
        )

        assert re.findall(r"<h4>(.*?)</h4>", secao) == ["Prova escrita", "Classificação final"]
        assert "publicacoes-anteriores" not in etapas[0]
        assert secao.count('<details class="publicacoes-anteriores">') == 1

    def test_o_custo_da_pagina_nao_cresce_com_as_publicacoes(self, client, certame):
        """SC-448, D-011: a árvore reorganiza o que já foi lido, e não lê de novo."""
        from django.db import connection
        from django.test.utils import CaptureQueriesContext

        def consultas():
            with CaptureQueriesContext(connection) as capturadas:
                assert (
                    client.get(reverse("portal:selecao", args=[certame.edital.id])).status_code
                    == 200
                )
            return len(capturadas.captured_queries)

        _tres_listas(certame, certame.perfil_a, com_preliminar=True)
        com_seis = consultas()
        _tres_listas(certame, certame.perfil_b, com_preliminar=True)
        _tres_listas(
            certame,
            certame.perfil_b,
            etapa="escrita",
            marco="Prova escrita",
            marco_codigo="M1",
        )

        assert consultas() == com_seis

    def test_o_destaque_segue_o_recebimento_de_inscricoes(self, client, certame, monkeypatch):
        """FR-1164, decisão recebida 7: o destaque da `024` sobrevive à árvore.

        Nenhum teste prendia a classe antes desta feature; o caso fica aqui porque a reescrita do
        bloco é justamente o momento em que ela poderia se perder.
        """
        from processo_seletivo.portal import views

        _tres_listas(certame, certame.perfil_a)
        url = reverse("portal:selecao", args=[certame.edital.id])

        resposta = client.get(url)
        assert resposta.context["recebe_inscricoes"] is False
        assert '<section class="resultados em-destaque"' in resposta.content.decode()

        monkeypatch.setattr(views, "recebe_inscricoes", lambda **_: True)
        assert '<section class="resultados"' in client.get(url).content.decode()

    # --- O convite (US4) ------------------------------------------------------------------------

    def test_sem_sessao_o_convite_leva_a_entrada_com_volta_ao_edital(self, client, certame):
        """US4 cenários 1 e 4, FR-1160, FR-1161, D-002: depois da árvore, fora dos Perfis."""
        _tres_listas(certame, certame.perfil_a)

        secao = _secao(client, certame.edital)
        convite = re.search(r'<aside class="convite-da-situacao".*?</aside>', secao, re.S)

        assert convite is not None
        assert "Participou deste processo seletivo?" in convite.group(0)
        assert "Consulte sua classificação e situação individual." in convite.group(0)
        aqui = reverse("portal:selecao", args=[certame.edital.id])
        destino, texto, _ = _links(convite.group(0))[0]
        assert texto == "Entrar para ver minha situação"
        assert destino == f"{reverse('portal:acesso')}?{urlencode({'destino': aqui})}"
        assert secao.index("<aside") > secao.rindex('<div class="resultados-do-perfil">')
        for grupo in _grupos(secao):
            assert "convite-da-situacao" not in grupo

    def test_com_uma_enviada_o_convite_leva_direto_ao_acompanhamento(self, client, certame):
        """US4 cenário 2, FR-1162, SC-447: um clique até a própria situação."""
        _tres_listas(certame, certame.perfil_a)
        inscricao = _enviada(client, certame, certame.perfil_a)

        convite = re.search(
            r'<aside class="convite-da-situacao".*?</aside>', _secao(client, certame.edital), re.S
        )

        destino, texto, _ = _links(convite.group(0))[0]
        assert (destino, texto) == (
            reverse("portal:acompanhamento", args=[inscricao.id]),
            "Ver minha situação",
        )

    def test_com_duas_enviadas_o_convite_leva_a_lista(self, client, certame):
        """FR-1162, D-003: o sistema não escolhe qual das inscrições a pessoa quer ver."""
        _tres_listas(certame, certame.perfil_a)
        _enviada(client, certame, certame.perfil_a)
        _enviada(client, certame, certame.perfil_b, protocolo="INS-2026-0622")

        convite = re.search(
            r'<aside class="convite-da-situacao".*?</aside>', _secao(client, certame.edital), re.S
        )

        destino, texto, _ = _links(convite.group(0))[0]
        assert (destino, texto) == (reverse("portal:inscricoes"), "Ver minhas inscrições")

    def test_conectado_sem_enviada_nao_ha_convite(self, client, certame):
        """US4 cenário 3, FR-1163: oferecer a própria situação a quem não concorreu seria vazio."""
        from tests.fixtures.candidato import MARIA, identificar

        _tres_listas(certame, certame.perfil_a)
        identificar(client, MARIA)

        assert "convite-da-situacao" not in _secao(client, certame.edital)


def _enviada(client, certame, perfil_id, *, protocolo="INS-2026-0621"):
    """Uma inscrição enviada de Maria, gravada direto: o que se testa é o convite, e não o envio."""
    from tests.fixtures.candidato import MARIA, identificar

    registro = identificar(client, MARIA)
    agora = timezone.now()
    return Inscricao.objects.create(
        identity_subject=registro.subject,
        edital=certame.edital,
        profile_id=perfil_id,
        status=Inscricao.Status.SUBMETIDA,
        nome="Maria Silva",
        cpf="123.456.789-09",
        cpf_normalizado="12345678909",
        versao_aceita=certame.versao,
        declaracoes_aceitas_em=agora,
        submitted_at=agora,
        protocolo=protocolo,
        created_at=agora,
    )


# --- A volta depois da identificação (D-007) ----------------------------------------------------


def test_o_destino_na_pagina_do_edital_volta_ao_bloco_de_resultados():
    from processo_seletivo.portal.views import _de_volta_a_vaga

    edital_id = uuid.uuid4()
    aqui = reverse("portal:selecao", args=[edital_id])

    assert _de_volta_a_vaga(aqui) == f"{aqui}#resultados-titulo"
    assert _de_volta_a_vaga("/selecoes/sair") == reverse("portal:inscricoes")


@pytest.mark.django_db
@pytest.mark.integration
def test_voltar_ao_edital_nao_pede_nome_e_cpf_e_a_vaga_continua_pedindo(rf):
    """FR-1161: nome e CPF só a caminho de uma vaga; voltar a uma página pública não é ato."""
    from django.contrib.sessions.middleware import SessionMiddleware

    from processo_seletivo.identidade.application import associacao
    from processo_seletivo.portal.views import CHAVE_DO_DESTINO, _entrar

    def entrar_com(destino):
        request = rf.get("/")
        SessionMiddleware(lambda r: None).process_request(request)
        request.session[CHAVE_DO_DESTINO] = destino
        identidade = associacao.criar_identidade_com(
            f"{uuid.uuid4().hex}@exemplo.test", "x@exemplo.test"
        )
        return _entrar(request, identidade)["Location"]

    edital_id = uuid.uuid4()
    aqui = reverse("portal:selecao", args=[edital_id])
    vaga = reverse("portal:inscrever", args=[edital_id, uuid.uuid4()])

    assert entrar_com(aqui) == f"{aqui}#resultados-titulo"
    assert entrar_com(vaga) == reverse("portal:meus-dados")
