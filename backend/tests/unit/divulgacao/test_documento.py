"""O documento oficial do resultado: o que ele imprime, e por que os bytes não mudam.

O renderizador é função pura — recebe o conteúdo já composto e devolve bytes —, e é isso que
permite afirmar sobre o texto **desenhado**, e não sobre o que se supõe ter sido escrito.
"""

import json
import re
from datetime import datetime

import pytest
from django.template import Context, Template

from processo_seletivo.divulgacao.infrastructure.documento import render_resultado_pdf
from processo_seletivo.shared.canonical import canonical_sha256
from tests.fixtures.divulgacao import MODALIDADE_NOME, montar_ato_publicavel, publicar_o_ato
from tests.interface.test_fluxo import texto_de_pdf_bytes

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.integration]


@pytest.fixture
def publicada(gestor, api_client, manager_headers, process_payload):
    cenario = montar_ato_publicavel(
        gestor,
        api_client,
        manager_headers,
        process_payload,
        seed=64,
        codigo="0764",
        pontuacoes=("90.0000", "70.0000", "70.0000", None),
        primeiro=1201,
    )
    return cenario, publicar_o_ato(cenario, chave="publicar-0764")


@pytest.fixture
def conteudo(publicada):
    _, publicacao = publicada
    return json.loads(bytes(publicacao.conteudo_publico).decode("utf-8"))


def test_o_documento_traz_tudo_o_que_a_spec_exige(conteudo):
    """SC-010 e SC-019: Processo, Edital, marco, natureza, ato de origem, instante e autoridade."""
    texto = texto_de_pdf_bytes(render_resultado_pdf(conteudo))
    cabecalho = conteudo["cabecalho"]

    assert cabecalho["processo"] in texto
    assert cabecalho["edital"] in texto
    assert cabecalho["marco"] in texto
    assert cabecalho["natureza_rotulo"] in texto
    assert "ATO DE ORIGEM" in texto and "emitido em" in texto
    assert "PUBLICADO EM" in texto
    assert cabecalho["signatario_nome"] in texto
    assert "Diretora-Geral" in texto


def test_o_documento_traz_o_resumo_criptografico_do_conteudo(conteudo):
    """FR-063: é o que torna o papel conferível contra o sistema."""
    texto = texto_de_pdf_bytes(render_resultado_pdf(conteudo))

    assert canonical_sha256(conteudo) in texto


def test_o_resumo_impresso_e_o_mesmo_que_a_publicacao_gravou(publicada, conteudo):
    """Os dois saem do mesmo objeto, e é por isso que conferem (FR-011, SC-004)."""
    _, publicacao = publicada
    texto = texto_de_pdf_bytes(render_resultado_pdf(conteudo))

    assert publicacao.conteudo_publico_hash in texto


def test_o_documento_nao_imprime_o_identificador_da_autoridade(conteudo, publicada):
    """`signatario_id` é dado de vínculo, não de leitura — como na publicação do Edital."""
    _, publicacao = publicada
    texto = texto_de_pdf_bytes(render_resultado_pdf(conteudo))

    assert str(publicacao.signatario_id) not in texto


def test_a_mesma_composicao_produz_os_mesmos_bytes(conteudo):
    """Sem data de criação embutida e sem identificador aleatório.

    É o que permite publicar o resumo de um documento gerado e esperar que ele confira na segunda
    vez — e é o que faz o documento **não** ser regenerado a cada download.
    """
    assert render_resultado_pdf(conteudo) == render_resultado_pdf(conteudo)


def test_os_bytes_gravados_sao_os_que_o_renderizador_produz(publicada, conteudo):
    """O documento entregue é o mesmo que a composição produz — e não outro, gerado depois."""
    _, publicacao = publicada

    assert bytes(publicacao.documento.bytes) == render_resultado_pdf(conteudo)


def test_cada_linha_do_documento_confere_com_a_da_pagina(conteudo):
    """FR-064: os rótulos são os mesmos porque vêm dos mesmos bytes.

    Posição, identificação pública, modalidade e pontuação: os quatro campos que a página mostra,
    conferidos linha a linha no documento.
    """
    texto = texto_de_pdf_bytes(render_resultado_pdf(conteudo))

    for item in conteudo["posicoes"]:
        assert f"{item['posicao']}º" in texto
        assert item["candidato"] in texto
        assert item["protocolo"] in texto
        assert item["modalidade"] in texto
        assert item["pontuacao"] in texto
    assert MODALIDADE_NOME in texto


def test_o_empate_e_dito_em_texto_tambem_no_documento(conteudo):
    """No papel não há cor nem posição relativa a que recorrer: ou se escreve, ou some (FR-014)."""
    texto = texto_de_pdf_bytes(render_resultado_pdf(conteudo))

    assert "compartilhada" in texto
    compartilhadas = [item for item in conteudo["posicoes"] if item["compartilhada"]]
    assert len(compartilhadas) == 2, "o cenário precisa do empate para que o teste valha"


def test_o_documento_nao_nomeia_quem_nao_recebeu_posicao(publicada, conteudo):
    """A fronteira da FR-017 vale para o papel pelo mesmo motivo: ele sai dos bytes divulgados."""
    from processo_seletivo.divulgacao.models import SituacaoDivulgada

    _, publicacao = publicada
    texto = texto_de_pdf_bytes(render_resultado_pdf(conteudo))
    sem_posicao = SituacaoDivulgada.objects.filter(
        publicacao=publicacao, situacao=SituacaoDivulgada.Situacao.SEM_POSICAO
    ).select_related("inscricao")

    assert sem_posicao.exists()
    for linha in sem_posicao:
        assert linha.inscricao.nome not in texto
        assert linha.inscricao.protocolo not in texto


def test_o_documento_nao_imprime_enum_canonico(conteudo):
    """O que se lê é "Resultado preliminar", e não `PRELIMINAR` (FR-013).

    O título vem em caixa alta por convenção de documento institucional — a mesma do comprovante —,
    e "RESULTADO PRELIMINAR" contém a grafia canônica por coincidência de letras, não por vazamento.
    A asserção corre sobre o resto do documento, onde uma grafia canônica só apareceria por engano.
    """
    texto = texto_de_pdf_bytes(render_resultado_pdf(conteudo))
    titulo = conteudo["cabecalho"]["titulo"].upper()
    assert titulo in texto, "o título é o rótulo humano em caixa alta, e não o enum"
    fora_do_titulo = texto.replace(titulo, "")

    for enum in ("PRELIMINAR", "DEFINITIVA", "CLASSIFICADA", "HABILITADA", "SEM_POSICAO"):
        assert enum not in fora_do_titulo


def test_o_documento_sem_posicao_alguma_diz_isso_em_vez_de_sair_vazio(conteudo):
    """Uma tabela ausente não informa nada; a frase informa."""
    vazio = {**conteudo, "posicoes": []}

    texto = texto_de_pdf_bytes(render_resultado_pdf(vazio))

    assert "Nenhum participante recebeu posição" in texto


def _leitura_do_relogio_no_documento(texto):
    """A data e a hora que o documento imprime em PUBLICADO EM, como par comparável.

    O rótulo e o valor saem em linhas próprias (`_par`), e o valor é a única coisa que interessa:
    devolvê-lo como `(data, hora, minuto)` permite comparar **o instante** com o da página sem
    exigir que as duas superfícies o escrevam com a mesma pontuação — `às 14h` e `14:00` são a
    mesma leitura de relógio, e é sobre ela que este arquivo afirma.
    """
    linhas = texto.splitlines()
    valor = linhas[linhas.index("PUBLICADO EM") + 1]
    achado = re.fullmatch(r"(\d{2}/\d{2}/\d{4}), às (\d{2})h(\d{2})?", valor)
    assert achado, f"o documento escreveu o instante fora da forma institucional: {valor!r}"
    return achado.group(1), int(achado.group(2)), int(achado.group(3) or 0)


PAGINA = Template('{{ m|date:"d/m/Y" }} {{ m|date:"H:i" }}')


def _leitura_do_relogio_na_pagina(momento):
    """O mesmo par, pelo caminho que a página percorre — o template, e não só o filtro.

    `portal/resultado.html` escreve `{{ publicacao.publicado_em|date:"d/m/Y" }} às
    {{ publicacao.publicado_em|date:"H:i" }}`. Renderizar em vez de transcrever o formato mantém
    o teste preso ao que a página realmente faz — e **chamar `date` direto não bastaria**: quem
    converte o instante para o fuso institucional é o motor de templates, em
    `template_localtime`, não o filtro. Um ajudante que chamasse o filtro fora de um template
    afirmaria UTC e acusaria o documento de errar justamente onde ele acerta.
    """
    data, relogio = PAGINA.render(Context({"m": momento})).split()
    hora, minuto = relogio.split(":")
    return data, int(hora), int(minuto)


@pytest.mark.parametrize(
    ("publicado_em", "por_que"),
    [
        ("2026-10-18T12:39:00+00:00", "09h39 — a hora de um dígito, que a página preenche"),
        ("2026-10-18T03:00:00+00:00", "00h — a meia-noite, que o documento omitia inteira"),
        ("2026-10-18T02:06:00+00:00", "23h06 do dia anterior — a virada, que muda o dia"),
        ("2026-10-18T17:00:00+00:00", "14h — a hora cheia, que o Edital escreve sem os minutos"),
        ("2026-10-18T20:42:00+00:00", "17h42 — a tarde, que já funcionava"),
    ],
)
def test_o_instante_do_documento_e_o_mesmo_que_a_pagina_mostra(conteudo, publicado_em, por_que):
    """A página e o documento não podem discordar sobre **quando** o resultado foi divulgado.

    O conteúdo carrega o instante em UTC. A página passa pelo filtro `date`, que localiza; o
    documento escreve o que recebe. Sem converter para o fuso da instituição antes de formatar, a
    mesma publicação sai `às 11h14` numa e `às 14h14` no outro — três horas de diferença no dado
    que o documento existe para provar. Perto da meia-noite, a divergência muda também o dia.

    É o mesmo defeito que o comprovante da 009 já corrigiu, e pelo mesmo motivo.

    **O instante é congelado, e não lido do relógio.** Enquanto o teste usava o `publicado_em`
    que a publicação acabara de gravar, ele só exercitava a hora em que a suíte rodava: as duas
    horas que o documento escrevia errado — a de um dígito e a meia-noite — passavam despercebidas
    das 10h em diante e reprovavam de madrugada, o que fazia um defeito determinístico parecer
    intermitente. Congelar transforma "às vezes falha" em "sempre cobre", e a parametrização diz
    quais leituras de relógio o documento precisa acertar.
    """
    momento = datetime.fromisoformat(publicado_em)
    congelado = {**conteudo, "cabecalho": {**conteudo["cabecalho"], "publicado_em": publicado_em}}

    texto = texto_de_pdf_bytes(render_resultado_pdf(congelado))

    documento = _leitura_do_relogio_no_documento(texto)

    assert documento == _leitura_do_relogio_na_pagina(momento), por_que


def test_o_documento_continua_deterministico_apesar_da_conversao_de_fuso(conteudo):
    """A conversão é do texto congelado para um fuso fixo, e não uma leitura do relógio."""
    primeiro = render_resultado_pdf(conteudo)

    assert primeiro == render_resultado_pdf(conteudo)
