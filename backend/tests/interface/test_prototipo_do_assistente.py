"""O protótipo do painel de dúvidas (Fase C, avaliação de 14/10).

Prende o que a avaliação pediu e o que o protótipo não pode quebrar:
- o acesso é o do piloto, e nenhuma rota é pública;
- os estados simulados não chamam o modelo nem gravam;
- a sugestão é respondida pela `070`, com o tipo dela, e entra no histórico da pergunta seguinte;
- a espera não diz que confere, nem promete prazo;
- o canal só aparece quando existe;
- e a tela técnica continua com a conversa dela.
"""

import re

import pytest
from django.template.loader import render_to_string
from django.urls import reverse

from processo_seletivo.duvidas.domain.estruturas_do_piloto import RESPOSTA_DA_SUGESTAO
from processo_seletivo.duvidas.models import TrocaDoPiloto
from processo_seletivo.interface import prototipo_do_assistente as prototipo
from tests.fixtures.corpus import publicar_do_corpus
from tests.fixtures.inferencia import devolucao, saida
from tests.fixtures.inferencia_corpus import fonte
from tests.interface.conftest import identificar

pytestmark = [pytest.mark.django_db, pytest.mark.integration]

PILOTO = ["gestor", "participante-piloto-assistente"]


@pytest.fixture(autouse=True)
def _ambiente(seletor_ligado, sem_rede):
    """O seletor de identidade, e nenhum caso alcança a rede."""


@pytest.fixture
def edital_91(api_client):
    edital, _ = publicar_do_corpus(api_client, "91", chave="prototipo91")
    return edital


def _url(edital, nome="interface:assistente-prototipo"):
    return reverse(nome, args=[edital.id])


def _texto(resposta):
    return re.sub(r"\s+", " ", resposta.content.decode())


def _todos(mensagens):
    total = fonte(mensagens, lugar="INF-BJN", rotulo="Vagas imediatas")
    return devolucao(saida("RESPONDIDA", ("dado", "Sim, os quatro obrigatórios.", [total["id"]])))


def test_sem_a_permissao_a_mesma_negativa_e_nada_grava(client, edital_91, porta_falsa):
    porta = porta_falsa()
    identificar(client, "pessoa", ["gestor"])

    assert client.get(_url(edital_91)).status_code == 404
    for nome in ("perguntar", "sugestao", "nova"):
        rota = f"interface:assistente-prototipo-{nome}"
        assert client.post(_url(edital_91, rota), {"sugestao": "P-01"}).status_code == 404
    assert porta.chamadas == []
    assert not TrocaDoPiloto.objects.exists()


def test_com_o_piloto_desligado_a_mesma_negativa(client, edital_91, settings):
    settings.ASSISTENTE_PILOTO = False
    identificar(client, "pessoa", PILOTO)

    assert client.get(_url(edital_91)).status_code == 404


def test_o_fundo_e_a_pagina_publica_e_o_painel_nasce_fechado(client, edital_91):
    identificar(client, "pessoa", PILOTO)

    corpo = _texto(client.get(_url(edital_91)))

    assert edital_91.title in corpo
    assert "Dúvidas sobre este Edital" in corpo
    assert re.search(r'<dialog id="pd-painel"[^>]*>', corpo)
    assert " open>" not in re.search(r'<dialog id="pd-painel"[^>]*>', corpo).group(0)
    assert 'aria-expanded="false"' in corpo
    assert 'aria-expanded="true"' in _texto(client.get(_url(edital_91) + "?painel=1"))


@pytest.mark.parametrize(("estado", "_nome"), prototipo.ESTADOS_SIMULADOS)
def test_os_estados_simulados_nao_chamam_nem_gravam(client, edital_91, porta_falsa, estado, _nome):
    porta = porta_falsa()
    identificar(client, "pessoa", PILOTO)

    resposta = client.get(_url(edital_91) + f"?painel=1&simulacao={estado}")

    assert resposta.status_code == 200
    assert "as respostas do modelo são ilustrativas" in _texto(resposta)
    assert porta.chamadas == []
    assert not TrocaDoPiloto.objects.exists()


def test_cada_estado_mostra_o_que_promete(client, edital_91):
    identificar(client, "pessoa", PILOTO)

    def ver(estado):
        """Só o painel: a página pública de fundo tem a palavra "conferir" no estilo dela."""
        pagina = _texto(client.get(_url(edital_91) + f"?painel=1&simulacao={estado}"))
        return re.search(r'<dialog id="pd-painel".*?</dialog>', pagina).group(0)

    inicio = ver("inicio")
    assert "Assistente do edital" in inicio and "Assistente de IA" in inicio
    # Três à vista; as outras, recolhidas em "Mais dúvidas".
    a_vista = re.sub(r'<details class="pd-mais">.*?</details>', "", inicio)
    assert a_vista.count('class="pd-sugestao"') == len(prototipo.SUGERIDAS) == 3
    assert "Mais dúvidas" in inicio
    assert "Polo Bom Jesus do Norte" in ver("escolha") and "Para qual opção?" in ver("escolha")
    assert "Texto do Edital ·" in ver("resposta")
    continuacao = ver("continuacao")
    assert "Que documentos preciso enviar?" in continuacao
    assert "Resposta pronta, montada a partir dos dados do Edital." in continuacao
    assert "Preciso enviar todos?" in continuacao
    # A espera diz que consulta, e nunca que confere: a conferência leva milissegundos.
    espera, longa = ver("espera"), ver("espera-longa")
    assert prototipo.ESPERA in espera and prototipo.ESPERA_LONGA in longa
    assert "conferi" not in espera.lower() and "conferi" not in longa.lower()
    # E não promete prazo: os 5 a 35 segundos do ensaio foram observados, e não são limite.
    assert not re.search(r"\d+\s*(segundos|s)\b", espera + longa)
    falha = ver("falha")
    assert prototipo.NAO_CONFIRMADA in falha and prototipo.INDISPONIVEL_AGORA in falha
    mudanca = ver("mudanca")
    assert "O Edital mudou desde as respostas acima" in mudanca
    # O marco conta a mesma história da linha da versão no topo do painel.
    vigente = re.search(r"versão vigente desde ([^<]+)</p>", mudanca).group(1).strip()
    assert f"vigente desde {vigente}" in re.search(
        r'class="pd-marco"[^>]*>(.*?)</p>', mudanca
    ).group(1)
    assert "Sobre a versão anterior do Edital" in mudanca


def test_a_sugestao_e_respondida_pela_070_sem_o_modelo(client, edital_91, porta_falsa):
    porta = porta_falsa()
    identificar(client, "pessoa", PILOTO)

    resposta = client.post(
        _url(edital_91, "interface:assistente-prototipo-sugestao"),
        {"sugestao": "P-05", "perfil": "INF-BJN"},
    )

    assert resposta.status_code == 302
    assert resposta.url.endswith("?painel=1#troca-1")
    assert porta.chamadas == []
    troca = TrocaDoPiloto.objects.get()
    assert troca.estado == RESPOSTA_DA_SUGESTAO
    assert not troca.chamou_o_servico
    assert troca.tipo == "RESPONDIDA"
    assert troca.pergunta == "Que documentos preciso enviar? — Polo Bom Jesus do Norte"
    corpo = _texto(client.get(_url(edital_91) + "?painel=1"))
    painel = re.search(r'<dialog id="pd-painel".*?</dialog>', corpo).group(0)
    assert "Na opção Polo Bom Jesus do Norte, são obrigatórios:" in painel
    assert "<li>Diploma de graduação" in painel
    # As condições continuam: a instrução do documento, o facultativo e o que a vaga PPI acrescenta.
    assert "declaração de conclusão acompanhada do histórico" in painel
    assert "É facultativo: Requerimento de uso do nome social." in painel
    assert "envia também: Autodeclaração étnico-racial." in painel
    # E a língua da tela de validação não chega ao candidato.
    for jargao in ("INF-BJN", "sem modalidade", "certame", "cartão", "Obrigatoriedade:"):
        assert jargao not in re.sub(r'<details class="pd-fontes">.*?</details>', "", painel)
    assert "Consultar fontes" in painel


def test_a_continuacao_leva_a_sugestao_no_historico(client, edital_91, porta_falsa, contador_falso):
    """ "Que documentos preciso?" e "preciso enviar todos?": o modelo sabe do que se falava."""
    contador_falso()
    porta = porta_falsa(_todos)
    identificar(client, "pessoa", PILOTO)
    client.post(
        _url(edital_91, "interface:assistente-prototipo-sugestao"),
        {"sugestao": "P-05", "perfil": "INF-BJN"},
    )

    resposta = client.post(
        _url(edital_91, "interface:assistente-prototipo-perguntar"),
        {"pergunta": "Preciso enviar todos?"},
    )

    assert resposta.url.endswith("#troca-2")
    mensagens = porta.chamadas[0]["mensagens"]
    papeis = [mensagem["role"] for mensagem in mensagens[2:]]
    assert papeis == ["user", "assistant", "user", "user"]
    assert mensagens[2]["content"].startswith("Que documentos preciso enviar?")
    assert "- Diploma de graduação" in mensagens[3]["content"]
    assert "cartão" not in mensagens[3]["content"]
    # A opção chega explícita, dita pelo sistema; a lista de concorrência, como não informada.
    assert "Polo Bom Jesus do Norte (nas fontes, Perfil INF-BJN)" in mensagens[4]["content"]
    assert "Lista de concorrência: não informada." in mensagens[4]["content"]
    assert "opção escolhida" not in mensagens[3]["content"]
    assert mensagens[5]["content"] == "Preciso enviar todos?"
    assert "Sim, os quatro obrigatórios." in _texto(client.get(_url(edital_91) + "?painel=1"))


def test_a_sugestao_que_nao_vale_para_o_edital_e_recusada(client, edital_91):
    identificar(client, "pessoa", PILOTO)

    resposta = client.post(
        _url(edital_91, "interface:assistente-prototipo-sugestao"), {"sugestao": "P-99"}
    )

    assert resposta.url.endswith("recusa=1")
    assert not TrocaDoPiloto.objects.exists()


def test_a_tela_tecnica_continua_com_a_conversa_dela(client, edital_91):
    identificar(client, "pessoa", PILOTO)
    client.post(
        _url(edital_91, "interface:assistente-prototipo-sugestao"),
        {"sugestao": "P-05", "perfil": "INF-BJN"},
    )

    assert "Que documentos preciso enviar?" not in _texto(
        client.get(reverse("interface:assistente", args=[edital_91.id]))
    )


def test_sem_canal_o_painel_nao_inventa_encaminhamento(rf):
    contexto = {
        "edital": {"number": "01", "year": 2026, "id": "00000000-0000-0000-0000-000000000000"},
        "atendimento": (),
        "mensagens": [],
        "principais": [],
        "simulacao": "inicio",
    }

    requisicao = rf.get("/")
    requisicao.session = {}

    def painel(contatos):
        return render_to_string(
            "interface/prototipo_do_assistente.html",
            {**contexto, "atendimento": contatos},
            requisicao,
        )

    assert "Atendimento oficial" not in painel(())
    assert '<a href="mailto:a@b.br">Atendimento oficial</a>' in painel(
        (("a@b.br", "mailto:a@b.br"),)
    )


def test_a_sugestao_da_opcao_pergunta_qual_quando_ha_mais_de_uma(client, edital_91):
    """Sem seletor na entrada: o painel pergunta a opção, pelo nome que o candidato reconhece."""
    identificar(client, "pessoa", PILOTO)

    resposta = client.post(
        _url(edital_91, "interface:assistente-prototipo-sugestao"), {"sugestao": "P-05"}
    )

    assert resposta.url.endswith("escolher=P-05")
    assert not TrocaDoPiloto.objects.exists()
    painel = _texto(client.get(resposta.url))
    assert "Para qual opção?" in painel
    assert 'name="perfil" value="INF-BJN">Polo Bom Jesus do Norte</button>' in painel
