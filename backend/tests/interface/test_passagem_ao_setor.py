"""A passagem ao setor na jornada guiada do Edital (153, US1 a US5).

O que se prova, pela página do Edital (o Centro) e pelas duas confirmações de encerrar:

- cada causa vira uma providência do seu papel, com o link só para quem pratica o ato (FR-6108 a
  FR-6111);
- as três pertencem à fase Conclusão (FR-6115), que ganha o bloco "Disponibilizar ao setor" e a
  frase do limite (FR-6118 a FR-6121);
- a confirmação de encerrar o Edital e a de encerrar o Processo advertem, com o caminho ou a quem
  pedir, e o relatório do Edital traz a mesma pendência (FR-6124 a FR-6128);
- nada disso nomeia pessoa, nem usa "encaminhado", "entregue" ou "recebido" (FR-6116, FR-6123).
"""

import re

import pytest
from django.urls import reverse
from django.utils import timezone

from processo_seletivo.formalizacao.domain import nomes
from processo_seletivo.interface import andamento
from processo_seletivo.interface import conceitos as c
from processo_seletivo.interface import encerramento as e
from processo_seletivo.interface import relatorio_do_edital as rel
from processo_seletivo.processos.application import pendencias_do_edital as p
from processo_seletivo.processos.models import Edital
from processo_seletivo.seguranca.acessos import GERIR
from processo_seletivo.seguranca.domain import Actor
from tests.fixtures.formalizacao import (
    definir_documentos,
    designar_direto,
    montar_cenario_da_formalizacao,
    servido,
)
from tests.integration.formalizacao.apoio import exportar_pessoa
from tests.interface.conftest import identificar
from tests.seguranca.apoio import pessoa, vincular

pytestmark = [pytest.mark.integration, pytest.mark.django_db]

DEFINIR = "Definir os documentos que vão ao setor"
DESIGNAR = "Designar quem recebe os documentos"
EXPORTAR = "Exportar os documentos das pessoas aptas"


@pytest.fixture
def cenario(gestor, api_client, manager_headers, process_payload, raiz_de_arquivos, seletor_ligado):
    """Duas pessoas aptas, e mais nada: a definição vazia e ninguém designado."""
    return montar_cenario_da_formalizacao(
        gestor, api_client, manager_headers, process_payload, aptas=2, prefixo="passagem-153"
    )


@pytest.fixture
def com_papel(db):
    rui = pessoa("rui", nome="Rui Registro", email="rui@ifes.edu.br")
    vincular(rui, "cefor", nomes.PAPEL)
    return rui


def pagina(client, edital, fase=None):
    url = reverse("interface:detalhe", args=[edital.id])
    resposta = client.get(url + (f"?fase={fase}" if fase else ""))
    assert resposta.status_code == 200
    return resposta.content.decode()


def cartao(texto):
    return texto.split('id="agora-titulo"', 1)[1].split("</section>", 1)[0]


def bloco(texto):
    return texto.split('id="passagem-titulo"', 1)[1].split("</section>", 1)[0]


def sem_marcacao(html):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html))


# --- US1: definir ------------------------------------------------------------------------------


def test_sem_definicao_a_providencia_e_de_quem_conduz_com_o_link(client, cenario):
    """US1, cenário 1: a ação é da presidência, e leva à tela da definição."""
    identificar(client, "carlos", ["gestor"])
    agora = cartao(pagina(client, cenario.edital))
    definicao = reverse("interface:formalizacao-definicao", args=[cenario.edital.id])
    assert f'href="{definicao}#documentos-definidos"' in agora
    assert DEFINIR in agora
    assert "2 pessoas aptas para formalização; nenhum documento definido para o setor" in agora


def test_quem_nao_conduz_le_o_papel_e_nao_recebe_o_link(client, cenario):
    """US1, cenário 3; FR-6111: de outro papel, sem link."""
    identificar(client, "ana", ["publicador"])
    agora = sem_marcacao(cartao(pagina(client, cenario.edital)))
    assert f"Quem conduz a seleção: {DEFINIR[:1].lower()}{DEFINIR[1:]}" in agora
    assert "formalizacao/definicao" not in cartao(pagina(client, cenario.edital))


def test_a_definicao_gravada_sem_documento_encerra_a_providencia(client, cenario, gestor):
    """US1, cenário 4; D-003: a versão vazia, com motivo, é decisão."""
    definir_documentos(cenario.edital, gestor, requisitos=[], motivo="O setor não pede documento")
    identificar(client, "carlos", ["gestor"])
    texto = pagina(client, cenario.edital, fase="conclusao")
    assert DEFINIR not in texto and DESIGNAR not in texto and EXPORTAR not in texto
    assert "Nenhum documento vai ao setor neste Edital, por decisão de" in bloco(texto)


# --- US2: designar -----------------------------------------------------------------------------


def test_sem_designacao_a_providencia_e_de_quem_administra_os_acessos(client, cenario, gestor):
    """US2, cenários 1 e 2; FR-6113: sem ninguém com o papel, a frase diz o passo anterior.

    Desde a revisão de 12/11 da `117` (FR-6708), o responsável nomeia também a presidência, e
    `comissao:gerir` sem presidir continua vendo a providência como de outro papel.
    """
    definir_documentos(cenario.edital, gestor)
    identificar(client, "carlos", ["gestor"])
    agora = sem_marcacao(cartao(pagina(client, cenario.edital)))
    assert (
        "A presidência ou quem administra os acessos da unidade: designar quem recebe os documentos"
    ) in agora
    assert "ninguém está designado para receber os documentos deste Edital" in agora
    assert "conceder o papel Formalização a alguém do setor" in agora

    # O administrador de acessos vem do login institucional, e não do seletor: o andamento é lido
    # direto, com o ator que a tela da designação aceita.
    gil = Actor("gil", cenario.edital.institution_scope, frozenset({GERIR}))
    providencia = _da_passagem(andamento.do_edital(cenario.edital, gil))
    destino = f"{reverse('interface:acessos-formalizacao')}?edital={cenario.edital.id}"
    assert (providencia.ato, providencia.sua, providencia.url) == (DESIGNAR, True, destino)


def test_a_presidencia_ve_a_designacao_como_dela(cenario, gestor):
    """FR-6708 da `117` (revisão de 12/11), D-006 desta spec: o link é o da seção da definição."""
    definir_documentos(cenario.edital, gestor)
    maria = Actor("maria", cenario.edital.institution_scope, frozenset())
    providencia = _da_passagem(andamento.do_edital(cenario.edital, maria))
    destino = f"{reverse('interface:formalizacao-definicao', args=[cenario.edital.id])}#quem-acessa"
    assert (providencia.ato, providencia.sua, providencia.url) == (DESIGNAR, True, destino)


def test_sem_definicao_a_designacao_nao_aparece(cenario):
    """US2, cenário 5; FR-6106: a pessoa fica na primeira causa."""
    gil = Actor("gil", cenario.edital.institution_scope, frozenset({GERIR}))
    providencia = _da_passagem(andamento.do_edital(cenario.edital, gil))
    assert (providencia.ato, providencia.sua, providencia.url) == (DEFINIR, False, "")


def _da_passagem(lido):
    """A única providência da passagem no andamento lido."""
    (providencia,) = [x for x in lido.providencias if x.natureza == andamento.FORMALIZACAO]
    return providencia


# --- US3 e US5: exportar, e o bloco da Conclusão ------------------------------------------------


def test_com_definicao_e_designacao_falta_o_setor_e_o_bloco_diz_cada_passo(
    client, cenario, gestor, com_papel
):
    """US3, cenário 1; US5; FR-6115, FR-6118, FR-6120."""
    definir_documentos(cenario.edital, gestor)
    designar_direto(cenario.edital, com_papel.username)
    identificar(client, "carlos", ["gestor"])
    texto = pagina(client, cenario.edital, fase="conclusao")

    agora = sem_marcacao(cartao(texto))
    assert "O setor da formalização: exportar os documentos das pessoas aptas" in agora
    assert "(Conclusão)" in agora
    linhas = sem_marcacao(bloco(texto))
    assert "2 pessoas aptas para formalização." in linhas
    hoje = timezone.localdate().strftime("%d/%m/%Y")
    assert f"Feito · Documentos que o setor recebe: definidos em {hoje}" in linhas
    assert "Feito · Quem recebe: 1 pessoa designada" in linhas
    assert "Em aberto · Pessoas disponibilizadas: 0 de 2" in linhas
    assert c.LIMITE_DA_PASSAGEM in linhas


def test_com_todas_disponibilizadas_o_bloco_diz_o_ultimo_pacote(client, cenario, gestor, com_papel):
    """FR-6121; SC-1956: depois do pacote, nenhuma providência, e o bloco diz o que aconteceu."""
    definir_documentos(cenario.edital, gestor)
    designar_direto(cenario.edital, com_papel.username)
    identificar(client, com_papel.username, ["formalizacao"])
    for inscricao in cenario.inscricoes_aptas:
        assert servido(exportar_pessoa(client, cenario.edital, inscricao))

    identificar(client, "carlos", ["gestor"])
    texto = pagina(client, cenario.edital, fase="conclusao")
    assert EXPORTAR not in texto
    hoje = timezone.localdate().strftime("%d/%m/%Y")
    linhas = sem_marcacao(bloco(texto))
    assert "Feito · Pessoas disponibilizadas: 2 de 2" in linhas
    assert (
        "Documentos de todas as 2 pessoas aptas disponibilizados ao setor; "
        f"o último pacote em {hoje}."
    ) in linhas


def test_o_bloco_sem_definicao_so_oferece_a_primeira_linha(client, cenario):
    """US5, cenário 2: a linha da definição tem o ato; a de quem recebe espera por ela."""
    identificar(client, "carlos", ["gestor"])
    linhas = bloco(pagina(client, cenario.edital, fase="conclusao"))
    assert "não definidos" in linhas
    assert "ainda depende da definição" in linhas
    assert linhas.count("<a ") == 1


def test_sem_pessoa_apta_nao_ha_bloco_nem_providencia(
    client, gestor, api_client, manager_headers, process_payload, raiz_de_arquivos, seletor_ligado
):
    """US5, cenário 1; FR-6130."""
    cenario = montar_cenario_da_formalizacao(
        gestor,
        api_client,
        manager_headers,
        process_payload,
        aptas=0,
        sem_resposta=1,
        prefixo="passagem-153-vazio",
    )
    identificar(client, "carlos", ["gestor"])
    texto = pagina(client, cenario.edital, fase="conclusao")
    assert 'id="passagem-titulo"' not in texto
    assert DEFINIR not in texto


def test_nada_nomeia_pessoa_nem_diz_que_o_setor_recebeu(client, cenario, gestor, com_papel):
    """FR-6116, FR-6123; SC-1954."""
    definir_documentos(cenario.edital, gestor)
    designar_direto(cenario.edital, com_papel.username)
    identificar(client, "carlos", ["gestor"])
    texto = pagina(client, cenario.edital, fase="conclusao")
    trechos = sem_marcacao(cartao(texto) + bloco(texto))
    for inscricao in cenario.inscricoes_aptas:
        assert inscricao.nome not in trechos
        assert (inscricao.protocolo or "@@") not in trechos
    assert not re.search(r"encaminhad|entregue|recebid|obtid", trechos, re.I)


# --- US4: encerrar -----------------------------------------------------------------------------


def test_a_confirmacao_de_encerrar_adverte_com_o_caminho(client, cenario):
    """US4, cenário 1; FR-6124 a FR-6126."""
    identificar(client, "carlos", ["gestor"])
    resposta = client.get(reverse("interface:ato", args=[cenario.edital.id, "encerrar"]))
    texto = sem_marcacao(resposta.content.decode())
    assert (
        "2 inscrições aptas para formalização ainda sem documentos disponibilizados ao setor "
        "(falta definir os documentos)."
    ) in texto
    assert "Definir os documentos" in texto


def test_a_tela_de_encerrar_diz_a_quem_pedir(client, cenario, gestor):
    """FR-6126: definido, sem designação, e o gestor da sessão não designa — a frase diz a quem."""
    definir_documentos(cenario.edital, gestor)
    identificar(client, "carlos", ["gestor"])
    resposta = client.get(reverse("interface:ato", args=[cenario.edital.id, "encerrar"]))
    texto = sem_marcacao(resposta.content.decode())
    assert (
        "(falta designar quem recebe). Peça à presidência ou a quem administra os acessos da "
        "unidade."
    ) in texto


def test_a_presidencia_recebe_o_caminho_da_designacao_ao_encerrar(cenario):
    """FR-6708 da `117`: a advertência leva a presidência à seção em que ela designa."""
    pendencia = rel.Pendencia(
        p.APTAS_SEM_DISPONIBILIZACAO, None, 2, detalhe=(("sem_quem_receba", 2),)
    )
    maria = Actor("maria", cenario.edital.institution_scope, frozenset())
    item = e._item_da_passagem(pendencia, cenario.edital, maria)
    assert item.url.endswith("#quem-acessa")


def test_a_quem_nao_pode_definir_a_advertencia_diz_a_quem_pedir(cenario):
    """FR-6126; FR-3538 da `113`."""
    pendencia = rel.Pendencia(
        p.APTAS_SEM_DISPONIBILIZACAO, None, 2, detalhe=(("sem_definicao", 2),)
    )
    item = e._item_da_passagem(pendencia, cenario.edital, Actor("ze", "cefor", frozenset()))
    assert item.url == ""
    assert item.a_quem_pedir == "Peça a quem conduz a seleção."


def test_o_relatorio_traz_a_mesma_pendencia(cenario):
    """FR-6127; SC-1952: a contagem do relatório é a do Centro."""
    fatos = rel.fatos_do_edital(cenario.edital, agora=timezone.now())
    pendencias = [x for x in fatos.pendencias if x.tipo == p.APTAS_SEM_DISPONIBILIZACAO]
    assert [(x.quantidade, x.detalhe) for x in pendencias] == [(2, (("sem_definicao", 2),))]


def test_o_encerramento_do_processo_adverte_pela_mesma_regra(cenario, gestor):
    """FR-6128: o Edital encerrado, com a pessoa apta pendente, aparece no "Encerrar Processo"."""
    Edital.objects.filter(pk=cenario.edital.pk).update(status=Edital.Status.ENCERRADO)
    advertencia = e.do_processo(cenario.edital.processo, gestor, agora=timezone.now())
    itens = [item for grupo in advertencia.grupos for item in grupo.itens]
    assert [item.tipo for item in itens if item.tipo == p.APTAS_SEM_DISPONIBILIZACAO] == [
        p.APTAS_SEM_DISPONIBILIZACAO
    ]


def test_no_edital_encerrado_a_providencia_continua(client, cenario):
    """P-3; FR-6117: a exportação não fecha, e o Centro não diz "Nada em aberto"."""
    Edital.objects.filter(pk=cenario.edital.pk).update(status=Edital.Status.ENCERRADO)
    identificar(client, "carlos", ["gestor"])
    texto = pagina(client, cenario.edital)
    assert DEFINIR in texto
    assert "Seleção concluída. Nada em aberto." not in texto
