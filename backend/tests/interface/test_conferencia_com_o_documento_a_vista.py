"""A conferência com o documento à vista (157).

O que se prova aqui é o que o servidor faz: a abertura gravada ao fim da entrega, e não antes
(FR-6544, decisão do usuário de 11/11/2026: abertura é o acesso ao arquivo vigente, sem afirmar
exibição nem leitura); a rota que se deixa emoldurar pela própria origem e devolve a recusa legível
no painel; o cartão relido; o registro sem recarga, com a recusa, a confirmação e o passo seguinte;
e o pedido de aviso de uma pessoa ao fim da conferência dela. O que o navegador faz com isso está em
`tests/javascript/visualizador.test.js` e no quickstart.
"""

import re

import pytest
from django.urls import reverse

from processo_seletivo.auditoria.models import RegistroAuditoria
from processo_seletivo.convocacao.application import documentos as servico
from tests.fixtures import documentos_da_convocacao as cenarios
from tests.fixtures.comissao import abrir_arquivo
from tests.fixtures.corte import MARCO
from tests.fixtures.documentos_da_convocacao import (
    CERTIDAO,
    HISTORICO,
    apresentar,
    comunicar,
    conferir,
    item,
)
from tests.interface.conftest import identificar

pytestmark = [pytest.mark.integration, pytest.mark.django_db(transaction=True)]

HX = {"HTTP_HX_REQUEST": "true"}


@pytest.fixture
def chamada(db, gestor, api_client, manager_headers, process_payload, raiz_de_arquivos, settings):
    """Uma convocação com dois documentos apresentados: a certidão e o histórico."""
    settings.INTERFACE_SELETOR_IDENTIDADE = True
    cenario = cenarios.montar(
        gestor,
        api_client,
        manager_headers,
        process_payload,
        documentos=cenarios.documentos_do_aluno(),
        prefixo="vista-157",
    )
    edital, _, _ = cenario
    pessoa, convocacao = cenarios.convocar_primeira(cenario, gestor)
    certidao = apresentar(pessoa, convocacao, CERTIDAO).apresentacao
    historico = apresentar(pessoa, convocacao, HISTORICO, corpo=b"historico").apresentacao

    def rota(nome, *extra):
        return reverse(f"interface:{nome}", args=[edital.id, MARCO, convocacao.id, *extra])

    return {
        "edital": edital,
        "gestor": gestor,
        "pessoa": pessoa,
        "convocacao": convocacao,
        "certidao": certidao,
        "historico": historico,
        "item": item(convocacao, CERTIDAO).id,
        "item_historico": item(convocacao, HISTORICO).id,
        "pagina": rota("documentos-da-convocacao"),
        "arquivo": rota("documento-da-convocacao", certidao.id),
        "cartao": rota("cartao-do-documento-da-convocacao", item(convocacao, CERTIDAO).id),
        "conferir": rota("conferir-documento", item(convocacao, CERTIDAO).id),
        "conferir_historico": rota("conferir-documento", item(convocacao, HISTORICO).id),
        "aviso": rota("pedir-aviso-de-pendencia"),
    }


def _consultas(apresentacao):
    return RegistroAuditoria.objects.filter(
        operation=servico.CONSULTAR_APRESENTACAO, aggregate_id=apresentacao.id
    ).count()


def _registrar(client, chamada, rota="conferir", resultado="CONFORME", chave="k", **campos):
    return client.post(
        chamada[rota],
        {"resultado": resultado, "chave": chave, **campos},
        **HX,
    )


# --- A abertura é o acesso ao arquivo, gravado ao fim da entrega (FR-6544) -----------------------


def test_a_abertura_so_e_gravada_depois_do_ultimo_bloco(chamada, client):
    """Pedido que não termina não é abertura: nem o clique, nem o primeiro byte (SC-2155)."""
    identificar(client, "carlos", ["gestor"])

    resposta = client.get(chamada["arquivo"])
    assert resposta.streaming
    assert _consultas(chamada["certidao"]) == 0, "nada antes da entrega"
    blocos = iter(resposta.streaming_content)
    primeiro = next(blocos)
    assert primeiro.startswith(b"%PDF")
    assert _consultas(chamada["certidao"]) == 0, "nada no meio da entrega"
    list(blocos)
    assert _consultas(chamada["certidao"]) == 1, "uma consulta, ao fim"


def test_a_entrega_continua_a_mesma(chamada, client):
    """FR-6500, FR-6504: inline, sem cache, emoldurável só pela própria origem."""
    identificar(client, "carlos", ["gestor"])

    resposta = abrir_arquivo(client, chamada["arquivo"])

    assert resposta["Content-Type"] == "application/pdf"
    assert resposta["Content-Disposition"].startswith("inline")
    assert "no-store" in resposta["Cache-Control"]
    assert resposta["X-Frame-Options"] == "SAMEORIGIN"
    assert int(resposta["Content-Length"]) == len(resposta.conteudo_servido)


def test_o_download_tambem_e_abertura_e_fica_dito(chamada, client):
    identificar(client, "carlos", ["gestor"])

    resposta = abrir_arquivo(client, chamada["arquivo"] + "?baixar=1")

    assert resposta["Content-Disposition"].startswith("attachment")
    registro = RegistroAuditoria.objects.get(
        operation=servico.CONSULTAR_APRESENTACAO, aggregate_id=chamada["certidao"].id
    )
    assert "baixado" in registro.reason


def test_a_abertura_ao_fim_autoriza_o_conforme(chamada, client, gestor):
    """A regra do comando não muda: a abertura gravada ao fim é a que a FR-3611 da 115 lê."""
    identificar(client, "carlos", ["gestor"])
    abrir_arquivo(client, chamada["arquivo"])

    resposta = _registrar(client, chamada)

    assert "Conferência registrada: Certidão de nascimento ou casamento, conforme" in (
        resposta.content.decode()
    )


# --- A recusa legível no painel (FR-6510) ---------------------------------------------------------


def _corromper(apresentacao):
    with open(apresentacao.arquivo.path, "wb") as arquivo:
        arquivo.write(b"%PDF-1.4\noutro conteudo")


def test_no_painel_a_recusa_por_integridade_e_um_documento_legivel(chamada, client):
    identificar(client, "carlos", ["gestor"])
    _corromper(chamada["certidao"])

    resposta = client.get(chamada["arquivo"] + "?painel=1")

    assert resposta.status_code == 409
    assert resposta["X-Frame-Options"] == "SAMEORIGIN"
    corpo = resposta.content.decode()
    assert "data-recusa-no-painel" in corpo
    assert "não confere com o que foi recebido" in corpo
    assert _consultas(chamada["certidao"]) == 0, "recusa não é abertura"
    assert RegistroAuditoria.objects.filter(
        operation="INTEGRIDADE", aggregate_id=chamada["certidao"].id
    ).exists()


def test_fora_do_painel_a_recusa_e_a_pagina_da_area(chamada, client):
    identificar(client, "carlos", ["gestor"])
    _corromper(chamada["certidao"])

    resposta = client.get(chamada["arquivo"])

    assert resposta.status_code == 409
    assert "data-recusa-no-painel" not in resposta.content.decode()


def test_no_painel_o_arquivo_indisponivel_e_dito(chamada, client):
    import os

    identificar(client, "carlos", ["gestor"])
    os.remove(chamada["certidao"].arquivo.path)

    resposta = client.get(chamada["arquivo"] + "?painel=1")

    assert resposta.status_code == 409
    assert "Arquivo indisponível" in resposta.content.decode()
    assert RegistroAuditoria.objects.filter(
        operation="ARQUIVO_INDISPONIVEL", aggregate_id=chamada["certidao"].id
    ).exists()


def test_o_painel_nao_muda_a_autorizacao(chamada, client):
    identificar(client, "ninguem", [])

    resposta = client.get(chamada["arquivo"] + "?painel=1")

    assert resposta.status_code in (302, 403, 404)
    assert _consultas(chamada["certidao"]) == 0


# --- A página com o painel (FR-6505 a FR-6512, UX-640, UX-641) -----------------------------------


def test_a_pagina_traz_o_painel_e_os_links_do_visualizador(chamada, client):
    identificar(client, "carlos", ["gestor"])

    corpo = client.get(chamada["pagina"]).content.decode()

    painel = corpo.index('id="painel-documento"')
    assert painel < corpo.index(f'id="item-{chamada["item"]}"'), "o painel vem antes no DOM"
    assert "hidden" in corpo[painel : painel + 60]
    assert "data-identificacao" in corpo and chamada["pessoa"].protocolo in corpo
    assert "data-abrir-documento" in corpo
    assert 'data-rotulo="Certidão de nascimento ou casamento — versão 1, apresentada em' in corpo
    assert 'aria-label="Abrir Certidão de nascimento ou casamento, versão 1"' in corpo
    assert re.search(r'data-tamanho="[\d,]+ (bytes|KB|MB)"', corpo)
    assert "visualizador.js" in corpo and "htmx.min.js" in corpo
    assert "Não comprova que ele foi exibido nem lido." in corpo, "UX-652"
    assert "O arquivo não abre, ou abre em branco?" in corpo, "UX-645"
    assert "style=" not in corpo and "<script>" not in corpo


def test_entrar_na_pagina_nao_abre_arquivo(chamada, client):
    identificar(client, "carlos", ["gestor"])
    client.get(chamada["pagina"])
    assert _consultas(chamada["certidao"]) == 0


# --- O cartão relido (FR-6503) --------------------------------------------------------------------


def test_o_cartao_relido_traz_a_marca_da_trilha(chamada, client):
    identificar(client, "carlos", ["gestor"])

    antes = client.get(chamada["cartao"]).content.decode()
    abrir_arquivo(client, chamada["arquivo"])
    depois = client.get(chamada["cartao"]).content.decode()

    assert antes.lstrip().startswith("<article") or "<article" in antes[:400]
    assert "aberto por você" not in antes and "Você ainda não abriu a versão 1" in antes
    assert "aberto por você" in depois and "data-aberto" in depois
    assert _consultas(chamada["certidao"]) == 1, "reler o cartão não é abrir"


# --- O registro sem recarga (FR-6514 a FR-6518) ---------------------------------------------------


def test_registrar_sem_recarga_troca_o_cartao_a_situacao_e_as_pessoas(chamada, client):
    identificar(client, "carlos", ["gestor"])
    abrir_arquivo(client, chamada["arquivo"])

    resposta = _registrar(client, chamada)

    assert resposta.status_code == 200
    corpo = resposta.content.decode()
    assert corpo.lstrip().startswith("<article"), "o cartão é o primeiro elemento"
    assert f'id="item-{chamada["item"]}"' in corpo
    assert 'id="situacao-da-convocacao"' in corpo and 'hx-swap-oob="true"' in corpo
    assert 'id="pessoas-do-recorte"' in corpo
    assert "data-confirmacao" in corpo
    chaves = re.findall(r'name="chave" value="([^"]+)"', corpo)
    assert chaves and all(c != "k" for c in chaves), "o próximo formulário tem chave nova"


def test_o_fragmento_diz_o_que_a_pagina_recarregada_diria(chamada, client):
    """SC-2146: o resumo e a situação trocados são os da página recarregada."""
    identificar(client, "carlos", ["gestor"])
    abrir_arquivo(client, chamada["arquivo"])

    fragmento = _registrar(client, chamada).content.decode()
    pagina = client.get(chamada["pagina"]).content.decode()

    def secao(html):
        inicio = html.index('<section class="situacao-da-convocacao')
        trecho = html[inicio : html.index("</section>", inicio)]
        return re.sub(r"\s+", " ", re.sub(r' hx-swap-oob="true"', "", trecho))

    assert secao(fragmento) == secao(pagina)


def test_sem_abertura_a_recusa_fica_no_cartao_com_o_preenchimento(chamada, client):
    identificar(client, "carlos", ["gestor"])

    corpo = _registrar(client, chamada, motivo="Legível.").content.decode()

    assert corpo.lstrip().startswith("<article")
    assert "A conferência não foi registrada." in corpo
    assert "Abra a versão 1 e registre de novo; o que você marcou continua aqui." in corpo
    assert "Abrir a versão 1" in corpo
    assert 'value="CONFORME" required checked' in corpo
    assert ">Legível.</textarea>" in corpo
    assert "data-confirmacao" not in corpo


def test_o_envio_duplicado_produz_uma_conferencia(chamada, client):
    identificar(client, "carlos", ["gestor"])
    abrir_arquivo(client, chamada["arquivo"])

    _registrar(client, chamada, chave="mesma")
    _registrar(client, chamada, chave="mesma")

    alvo = item(chamada["convocacao"], CERTIDAO)
    assert alvo.conferencias.count() == 1


def test_sem_identidade_so_a_mensagem_do_formulario_muda(chamada, client):
    resposta = _registrar(client, chamada)

    assert resposta.status_code == 200
    assert resposta["HX-Retarget"] == f"#mensagem-{chamada['item']}"
    assert resposta["HX-Reswap"] == "innerHTML"
    assert "Sua sessão terminou" in resposta.content.decode()


def test_a_recusa_sem_cartao_recarrega_a_pagina_com_a_recusa_no_alto(chamada, client):
    from processo_seletivo.processos.models import ProcessoSeletivo

    identificar(client, "carlos", ["gestor"])
    abrir_arquivo(client, chamada["arquivo"])
    ProcessoSeletivo.objects.filter(pk=chamada["edital"].processo_id).update(
        status=ProcessoSeletivo.Status.ENCERRADO
    )

    resposta = _registrar(client, chamada)

    assert resposta["HX-Refresh"] == "true"
    corpo = client.get(chamada["pagina"]).content.decode()
    assert "A conferência não foi registrada." in corpo


def test_sem_htmx_o_caminho_de_sempre(chamada, client):
    identificar(client, "carlos", ["gestor"])
    abrir_arquivo(client, chamada["arquivo"])

    resposta = client.post(chamada["conferir"], {"resultado": "CONFORME", "chave": "k"})

    assert resposta.status_code == 302
    assert resposta["Location"].endswith(f"#item-{chamada['item']}")


# --- A confirmação e o passo seguinte (FR-6519 a FR-6522) -----------------------------------------


def test_a_confirmacao_oferece_o_proximo_documento_sem_abrilo(chamada, client):
    identificar(client, "carlos", ["gestor"])
    abrir_arquivo(client, chamada["arquivo"])

    corpo = _registrar(client, chamada).content.decode()
    confirmacao = corpo[corpo.index("data-confirmacao") :]

    assert "Próximo a conferir: Histórico escolar do ensino médio" in confirmacao
    assert f'data-alvo="item-{chamada["item_historico"]}"' in confirmacao
    assert _consultas(chamada["historico"]) == 0, "oferecer não é abrir"


def test_ao_fim_da_pessoa_com_pendencia_oferece_o_pedido_de_aviso(chamada, client, gestor):
    identificar(client, "carlos", ["gestor"])
    comunicar(chamada["edital"], gestor, chamada["convocacao"])
    abrir_arquivo(client, chamada["arquivo"])
    _registrar(client, chamada, chave="c1")

    corpo = _registrar(
        client,
        chamada,
        rota="conferir_historico",
        resultado="PENDENTE",
        chave="c2",
        motivo="Faltam páginas.",
    ).content.decode()

    assert "Histórico escolar do ensino médio, pendente." in corpo, "UX-647"
    assert f"Nenhum aviso foi pedido; {chamada['pessoa'].nome} vê a pendência no portal." in corpo
    assert f"Não há outro documento de {chamada['pessoa'].nome} a conferir." in corpo
    assert f"Pedir aviso para {chamada['pessoa'].nome}" in corpo
    assert "O aviso não muda o prazo e não é a convocação." in corpo


def test_registrar_a_pendencia_nao_grava_aviso(chamada, client, gestor):
    """FR-6534, FR-4604 da 134: o pedido de aviso é sempre um gesto à parte."""
    from processo_seletivo.avisos.models import Aviso

    identificar(client, "carlos", ["gestor"])
    comunicar(chamada["edital"], gestor, chamada["convocacao"])

    _registrar(client, chamada, resultado="PENDENTE", motivo="Ilegível.")

    assert not Aviso.objects.exists()


def test_pedir_aviso_grava_e_diz_que_aguarda_o_envio(chamada, client, gestor, settings):
    from processo_seletivo.avisos.models import Aviso

    settings.AVISOS_AOS_CANDIDATOS = True
    identificar(client, "carlos", ["gestor"])
    comunicar(chamada["edital"], gestor, chamada["convocacao"])
    conferir(gestor, chamada["convocacao"], CERTIDAO, "PENDENTE", chave="p", motivo="Ilegível.")

    resposta = client.post(chamada["aviso"], {"chave": "aviso-1"}, **HX)

    corpo = resposta.content.decode()
    assert "Aviso solicitado; aguardando envio." in corpo
    assert 'id="situacao-da-convocacao"' in corpo
    assert Aviso.objects.count() == 1

    segundo = client.post(chamada["aviso"], {"chave": "aviso-2"}, **HX).content.decode()
    assert "já foi avisada hoje nesta chamada" in segundo
    assert "poderá ser feito a partir de" in segundo
    assert Aviso.objects.count() == 1, "nem exceção ao limite, nem agendamento"
