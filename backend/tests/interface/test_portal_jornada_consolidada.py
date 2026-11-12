"""A jornada consolidada do convocado, pelas telas do portal (118).

Cada teste monta um cenário da revisão de UX de 04/11/2026 — as letras são as de lá e as do plano —
e lê o acompanhamento, a convocação e, quando há, o Requerimento de Matrícula, como a pessoa os lê.
O que se prova aqui é a ordem dos blocos, o que aparece e o que não aparece, os textos que as telas
compõem e as garantias do caminho de leitura: nenhuma escrita além da leitura da convocação na
trilha, a mesma recusa para inscrição alheia e inexistente, e o custo que não cresce com os itens.

Os textos de cada célula estão provados, um a um, no teste da projeção
(`tests/unit/portal/test_obrigacoes_da_convocacao.py`); aqui eles são lidos na tela.
"""

import re
import uuid

import pytest
from django.db import connection
from django.test.utils import CaptureQueriesContext
from django.urls import reverse

from processo_seletivo.auditoria.models import RegistroAuditoria
from processo_seletivo.portal import obrigacoes, situacao
from processo_seletivo.requerimentos.models import RequerimentoDeMatricula
from tests.fixtures import documentos_da_convocacao as cenarios
from tests.fixtures import jornada_do_convocado as jornada
from tests.fixtures.documentos_da_convocacao import (
    CERTIDAO,
    CERTIFICADO_DO_MEDIO,
    HISTORICO,
    RESIDENCIA,
)
from tests.interface.test_portal_documentos_da_convocacao import entrar_como

pytestmark = [pytest.mark.integration, pytest.mark.django_db(transaction=True)]

DATA_COMO_PRAZO = re.compile(r"até \d\d/\d\d/\d{4}")
FORMATO_UNICO = re.compile(r"\d\d/\d\d/\d{4}, às \d\dh\d\d")


@pytest.fixture
def fx(db, gestor, api_client, manager_headers, process_payload, raiz_de_arquivos):
    return jornada.Montagem(gestor, api_client, manager_headers, process_payload)


def abrir(client, cenario, tela, *, pessoa=None, inscricao_id=None):
    pessoa = pessoa or cenario.pessoa
    with cenario.relogio():
        entrar_como(client, pessoa)
        return client.get(reverse(f"portal:{tela}", args=[inscricao_id or cenario.pessoa.id]))


def main(resposta):
    assert resposta.status_code == 200, resposta.status_code
    corpo = re.sub(r"<style.*?</style>", " ", resposta.content.decode(), flags=re.S)
    return re.search(r"<main[^>]*>(.*)</main>", corpo, re.S).group(1)


def texto(html):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html)).strip()


def nome_acessivel(html):
    """O nome que o leitor de tela lê: o texto visível e o oculto, sem separar o que se cola."""
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", html)).strip()


def topo(pagina):
    (bloco,) = re.findall(r'<section class="situacao-da-inscricao".*?</section>', pagina, re.S)
    return bloco


def o_que_fazer(pagina):
    """O bloco "O que fazer" do topo do acompanhamento, do título ao fim da seção."""
    return topo(pagina).split("<h3>O que fazer</h3>", 1)[1]


def titulos(pagina):
    return [texto(t) for t in re.findall(r"<h2[^>]*>(.*?)</h2>", pagina, re.S)]


def chamada(pagina):
    """A chamada da `121` (FR-3859): o primeiro bloco da tela, com o título de primeiro nível."""
    (secao,) = re.findall(r'<section class="chamada-da-convocacao".*?</section>', pagina, re.S)
    return secao


def titulo_da_pagina(pagina):
    (h1,) = re.findall(r"<h1[^>]*>(.*?)</h1>", pagina, re.S)
    return texto(h1)


def bloco(pagina, titulo):
    """A `<section>` de bloco cujo `h2` é `titulo`."""
    for secao in re.findall(r'<section class="bloco-da-convocacao.*?</section>', pagina, re.S):
        if re.search(rf"<h2[^>]*>\s*{re.escape(titulo)}\s*</h2>", secao):
            return secao
    raise AssertionError(f"sem o bloco {titulo!r}: {titulos(pagina)}")


def links(html):
    return [
        (href, texto(rotulo))
        for href, rotulo in re.findall(r'<a [^>]*href="([^"]*)"[^>]*>(.*?)</a>', html, re.S)
    ]


def formularios(pagina):
    return len(re.findall(r"<form\b", pagina))


def cartao(pagina, nome):
    for li in re.findall(r'<li class="requisito cartao-do-documento.*?</li>', pagina, re.S):
        if f">{nome}<" in li:
            return li
    raise AssertionError(f"sem o cartão {nome!r}")


def ate_o_prazo(cenario):
    return obrigacoes.ate(cenario.convocacao.vencimento)


# --- US1: quem tem documentos e Requerimento sabe que ainda falta -------------------------------


def test_c1_e_c2_o_acompanhamento_representa_o_conjunto(fx, client):
    """C1 e C2: a ação diz o que falta, o link leva à convocação, e o enviado é linha secundária."""
    cenario = jornada.montar("C1", fx)
    destino = reverse("portal:convocacao", args=[cenario.pessoa.id])

    fazer = o_que_fazer(main(abrir(client, cenario, "acompanhamento")))
    assert texto(fazer).startswith(
        "Você ainda precisa enviar 4 documentos e preencher o Requerimento de Matrícula."
    )
    assert links(fazer)[0] == (destino, "Ver o que falta na convocação")

    # A chamada da 121 no lugar de "O que fazer agora" e "Prazo" (FR-3735 da 118, revista): um link
    # só, para o primeiro cartão, e os cartões, na ordem da FR-3726, logo depois do andamento.
    pagina = main(abrir(client, cenario, "convocacao"))
    assert titulos(pagina)[:2] == ["Andamento", "O que falta"]
    ((href, rotulo),) = links(chamada(pagina))
    assert rotulo == "Ver o que preciso fazer"
    falta = bloco(pagina, "O que falta")
    assert f'id="{href.lstrip("#")}"' in cartao(falta, "Certidão de nascimento ou casamento")
    assert "Preencher o Requerimento de Matrícula" in texto(falta), "o Requerimento é tarefa"

    jornada.enviar_requerimento(cenario.pessoa)

    fazer = o_que_fazer(main(abrir(client, cenario, "acompanhamento")))
    lido = texto(fazer)
    assert lido.startswith("Você ainda precisa enviar 4 documentos.")
    assert situacao.REQUERIMENTO_ENVIADO not in lido, "sem falsa conclusão (F1, SC-1118)"
    assert "✓ Requerimento de Matrícula enviado." in lido
    assert links(fazer)[0] == (destino, "Ver o que falta na convocação")
    assert (
        reverse("portal:requerimento", args=[cenario.pessoa.id]),
        "Conferir o Requerimento de Matrícula enviado",
    ) in links(fazer)
    assert not [r for _, r in links(fazer) if r.startswith("Enviar")], "D-004"

    pagina = main(abrir(client, cenario, "convocacao"))
    assert "Preencher o Requerimento" not in texto(bloco(pagina, "O que falta"))
    apresentado = bloco(pagina, "O que você já apresentou")
    assert "Requerimento de Matrícula enviado." in texto(apresentado)
    assert "Conferir o Requerimento de Matrícula enviado" in texto(apresentado)

    requerimento = main(abrir(client, cenario, "requerimento"))
    assert "Voltar à convocação" in requerimento
    assert "Se algo mudou, a atualização cria uma nova versão, e esta continua registrada." in (
        texto(requerimento)
    )
    assert "você for convocado" not in requerimento


def test_o_aviso_do_envio_com_documento_aponta_a_convocacao(fx, client):
    """FR-3755: enviado o Requerimento numa chamada com documento, o aviso aponta a convocação."""
    from processo_seletivo.requerimentos.application import preencher
    from tests.fixtures.requerimento import campos_de_exemplo

    cenario = jornada.montar("C1", fx)
    abrir(client, cenario, "requerimento")
    versao = preencher._conteudo(cenario.pessoa)
    resposta = client.post(
        reverse("portal:requerimento", args=[cenario.pessoa.id]),
        {
            **campos_de_exemplo(),
            "enviar": "1",
            "aceite": "1",
            "versao_exibida": str(versao.id),
            "declaracao_exibida": preencher.declaracao_publicada(versao.content),
        },
        follow=True,
    )
    corpo = texto(main(resposta))
    assert (
        "Requerimento de Matrícula enviado. Veja na convocação se ainda falta algum documento."
        in corpo
    )
    assert "Voltar à convocação" in corpo


def test_o_aviso_do_envio_sem_documento_e_o_de_hoje(fx, client):
    from processo_seletivo.requerimentos.application import preencher
    from tests.fixtures.requerimento import campos_de_exemplo

    cenario = jornada.montar("B", fx)
    abrir(client, cenario, "requerimento")
    versao = preencher._conteudo(cenario.pessoa)
    resposta = client.post(
        reverse("portal:requerimento", args=[cenario.pessoa.id]),
        {
            **campos_de_exemplo(),
            "enviar": "1",
            "aceite": "1",
            "versao_exibida": str(versao.id),
            "declaracao_exibida": preencher.declaracao_publicada(versao.content),
        },
        follow=True,
    )
    corpo = texto(main(resposta))
    assert "Requerimento de Matrícula enviado." in corpo
    assert "Veja na convocação" not in corpo


@pytest.mark.parametrize("letra", ["B", "B2"])
def test_b_e_b2_sem_documento_ficam_como_hoje(fx, client, letra):
    """SC-1123: sem documento, a ação e a estrutura são as de hoje, sem a linha informativa."""
    cenario = jornada.montar(letra, fx)
    requerimento = reverse("portal:requerimento", args=[cenario.pessoa.id])

    fazer = texto(o_que_fazer(main(abrir(client, cenario, "acompanhamento"))))
    if letra == "B":
        assert fazer.startswith(situacao.PREENCHER_REQUERIMENTO)
    else:
        assert fazer.startswith(situacao.REQUERIMENTO_ENVIADO)
        assert "✓" not in fazer, "a linha secundária só existe com documento (D-017)"
    assert "Requerimento de Matrícula: não enviado" not in fazer

    pagina = main(abrir(client, cenario, "convocacao"))
    assert "O que fazer agora" not in titulos(pagina)
    # O título de primeiro nível passou a ser o da chamada (121, FR-3868), e "O que fazer" subiu um
    # nível, para não pular do h1 ao h3.
    assert titulo_da_pagina(pagina) == obrigacoes.TITULO_ABERTA
    assert "<h2>O que fazer</h2>" in pagina
    assert situacao.SIGA_AS_INSTRUCOES.rstrip(".") in texto(pagina)
    assert any(href == requerimento for href, _ in links(pagina))
    assert "Requerimento de Matrícula: não enviado" not in texto(pagina)

    if letra == "B":
        # FR-3753: o prazo, no formato único, na página do Requerimento a preencher.
        assert f"Prazo desta convocação: {ate_o_prazo(cenario)}." in texto(
            main(abrir(client, cenario, "requerimento"))
        )


def test_sem_documento_e_sem_requerimento_a_instrucao_neutra(fx, client):
    cenario = jornada.montar("sem-documento-nem-requerimento", fx)

    fazer = o_que_fazer(main(abrir(client, cenario, "acompanhamento")))
    assert texto(fazer).startswith(situacao.SIGA_AS_INSTRUCOES)
    assert links(fazer)[0][1] == "Ver convocação"
    pagina = main(abrir(client, cenario, "convocacao"))
    assert "O que fazer agora" not in titulos(pagina)
    assert f"Prazo desta convocação {ate_o_prazo(cenario)}" in texto(pagina)


# --- US2: a pendência salta aos olhos -----------------------------------------------------------


def test_f_a_pendencia_vem_primeiro_com_o_motivo_e_o_selo(fx, client):
    cenario = jornada.montar("F", fx)

    fazer = o_que_fazer(main(abrir(client, cenario, "acompanhamento")))
    assert texto(fazer).startswith("Você ainda precisa corrigir 1 documento e enviar 1 documento.")
    assert links(fazer)[0][1] == "Ver e corrigir os documentos pendentes"
    assert "✓ Requerimento de Matrícula enviado." in texto(fazer)

    # A ação da chamada leva à pendente, antes da que falta (121, FR-3863, SC-1151); o motivo está
    # no cartão, e a linha "Com a comissão" saiu (FR-3736 da 118, revista).
    pagina = main(abrir(client, cenario, "convocacao"))
    agora = chamada(pagina)
    ((href, rotulo),) = links(agora)
    assert rotulo == "Ver o que preciso fazer"
    assert "Você ainda precisa corrigir 1 documento e enviar 1 documento." in texto(agora)
    assert "Com a comissão" not in texto(agora)
    assert f'id="{href.lstrip("#")}"' in cartao(pagina, "Histórico escolar do ensino médio")
    assert jornada.MOTIVO_DO_HISTORICO in texto(cartao(pagina, "Histórico escolar do ensino médio"))

    historico = cartao(bloco(pagina, "O que falta"), "Histórico escolar do ensino médio")
    assert "destaque" in historico.split(">", 1)[0]
    assert "Precisa de correção" in texto(historico)
    assert (
        f"Precisa de correção: Falta a página 2. Envie um novo arquivo até "
        f"{ate_o_prazo(cenario)[4:]}." in texto(historico)
    )
    residencia = cartao(bloco(pagina, "O que falta"), "Comprovante de residência")
    assert "Precisa de correção" not in residencia
    assert "Falta enviar." in texto(residencia)

    apresentado = bloco(pagina, "O que você já apresentou")
    assert texto(apresentado).count("Conferido: de acordo com o Edital.") == 2
    assert "Conforme" not in texto(pagina), "nunca 'Conforme' sozinho (FR-3746)"


def test_f_cada_botao_diz_o_nome_do_documento(fx, client):
    """FR-3745, SC-1122: nomes acessíveis únicos, e a descrição do campo com a situação."""
    cenario = jornada.montar("F", fx)
    pagina = main(abrir(client, cenario, "convocacao"))

    enviar = [
        nome_acessivel(b)
        for b in re.findall(r'<button type="submit"[^>]*>(.*?)</button>', pagina, re.S)
    ]
    escolher = [
        nome_acessivel(rotulo)
        for rotulo in re.findall(r'<label class="botao-arquivo"[^>]*>(.*?)</label>', pagina, re.S)
    ]
    # O histórico tem arquivo recebido e correção pedida: o envio dele é a substituição, e o botão
    # o diz (FR-3739 da 118, revista em 12/11/2026). O comprovante nunca recebeu arquivo.
    assert "Enviar novo arquivo: Histórico escolar do ensino médio" in enviar
    assert "Enviar: Comprovante de residência" in enviar
    assert len(enviar) == len(set(enviar)) and len(escolher) == len(set(escolher))
    assert all(":" in rotulo or " para " in rotulo for rotulo in escolher)
    for campo in re.findall(r'<input type="file"[^>]*>', pagina):
        descrito = re.search(r'aria-describedby="([^"]*)"', campo).group(1).split()
        # A situação e o limite; na substituição, também a frase do efeito (FR-3739, revista).
        assert len(descrito) in (2, 3)
        for alvo in descrito:
            assert f'id="{alvo}"' in pagina


def test_j_a_pendencia_sem_envio_diz_envie_o_arquivo(fx, client):
    cenario = jornada.montar("J", fx)

    fazer = o_que_fazer(main(abrir(client, cenario, "acompanhamento")))
    assert texto(fazer).startswith("Você ainda precisa enviar 1 documento.")
    assert links(fazer)[0][1] == "Ver o que falta na convocação"

    pagina = main(abrir(client, cenario, "convocacao"))
    residencia = texto(cartao(pagina, "Comprovante de residência"))
    assert f"Envie o arquivo {ate_o_prazo(cenario)}." in residencia
    assert "outro arquivo" not in residencia and "novo arquivo" not in residencia
    assert "Precisa de correção" in residencia
    ((href, rotulo),) = links(chamada(pagina))
    assert rotulo == "Ver o que preciso fazer"
    assert f'id="{href.lstrip("#")}"' in cartao(pagina, "Comprovante de residência")


# --- US3: o que está com a comissão não parece tarefa -------------------------------------------


def test_d_o_aproveitado_nao_parece_pronto_nem_reenviado(fx, client):
    cenario = jornada.montar("D", fx)

    pagina = main(abrir(client, cenario, "convocacao"))
    lido = texto(pagina)
    assert "Você já enviou este documento na inscrição, em " in lido
    assert "Não precisa enviar de novo. A comissão vai conferir." in lido
    assert "Aguardando conferência" in lido
    assert "tendid" not in lido.lower(), "nada de 'atendido' antes da conferência (SC-1118)"
    assert "O que falta" not in titulos(pagina)
    assert obrigacoes.FRASE_DE_CONCLUSAO in lido


def test_e_enviados_aguardando_nada_por_enquanto_e_a_frase_de_conclusao(fx, client):
    cenario = jornada.montar("E", fx)

    fazer = texto(o_que_fazer(main(abrir(client, cenario, "acompanhamento"))))
    assert fazer.startswith(f"Nada por enquanto. {obrigacoes.FRASE_DE_CONCLUSAO}")
    pagina = main(abrir(client, cenario, "convocacao"))
    assert "O que falta" not in titulos(pagina)
    # O que está com a comissão vai para o andamento (121, FR-3865), e a chamada diz a conclusão,
    # sem ação (FR-3862, FR-3863).
    agora = texto(chamada(pagina))
    assert obrigacoes.FRASE_DE_CONCLUSAO in agora and not links(chamada(pagina))
    assert "Aguardando conferência: 4" in texto(bloco(pagina, "Andamento"))
    assert "Siga as instruções do Edital" not in texto(pagina), "E induzia uma ação inexistente"
    assert "enviou tudo" not in texto(pagina)


def test_h_tudo_conferido_diz_conferido_e_nao_diz_tudo_certo(fx, client):
    cenario = jornada.montar("H", fx)

    pagina = main(abrir(client, cenario, "convocacao"))
    lido = texto(pagina)
    assert lido.count("Conferido: de acordo com o Edital.") == 4
    assert obrigacoes.FRASE_DE_CONCLUSAO in lido
    assert not re.search(r"\bConforme\b", lido)
    assert "tudo certo" not in lido.lower() and "aprovad" not in lido.lower()
    fazer = texto(o_que_fazer(main(abrir(client, cenario, "acompanhamento"))))
    assert fazer.startswith(f"Nada por enquanto. {obrigacoes.FRASE_DE_CONCLUSAO}")


def test_l_o_opcional_se_envia_sem_tarefa_nenhuma(fx, client):
    """L, D-018: o bloco existe só com opcionais, com o envio, fora de toda contagem."""
    cenario = jornada.montar("L", fx)

    fazer = texto(o_que_fazer(main(abrir(client, cenario, "acompanhamento"))))
    assert fazer.startswith(f"Nada por enquanto. {obrigacoes.FRASE_DE_CONCLUSAO}")
    assert "Se quiser, você ainda pode enviar o documento opcional" in fazer

    pagina = main(abrir(client, cenario, "convocacao"))
    assert titulos(pagina)[:3] == ["Andamento", "Documentos opcionais", "O que você já apresentou"]
    agora = chamada(pagina)
    assert "Há documento opcional que você pode enviar, se quiser." in texto(agora)
    assert links(agora) == [("#documentos-opcionais", obrigacoes.CONVITE_AO_OPCIONAL)]
    andamento = texto(bloco(pagina, "Andamento"))
    assert "Aguardando conferência: 2" in andamento, "o opcional não entra na contagem"
    opcionais = bloco(pagina, "Documentos opcionais")
    assert formularios(opcionais) == 1
    assert "Opcional: envie se quiser." in texto(opcionais)

    alvo = cenarios.item(cenario.convocacao, jornada.OPCIONAL)
    resposta = client.post(
        reverse("portal:apresentar-documento-da-convocacao", args=[cenario.pessoa.id, alvo.id]),
        {"arquivo": cenarios.pdf(b"opcional")},
    )
    assert resposta.status_code == 302
    pagina = main(abrir(client, cenario, "convocacao"))
    assert "Documentos opcionais" not in titulos(pagina)
    declaracao = cartao(
        bloco(pagina, "O que você já apresentou"), "Declaração de interesse em auxílio estudantil"
    )
    assert "Opcional" in texto(declaracao) and "Aguardando conferência" in texto(declaracao)


# --- US5: o prazo é um só, e o não iniciado não mostra data --------------------------------------


@pytest.mark.parametrize("letra", ["K", "K2"])
def test_k_e_k2_nenhuma_data_aparece_como_prazo(fx, client, letra):
    cenario = jornada.montar(letra, fx)

    acompanhamento = main(abrir(client, cenario, "acompanhamento"))
    fazer = texto(o_que_fazer(acompanhamento))
    assert obrigacoes.PRAZO_NAO_INICIADO in fazer
    assert "Você já pode enviar." in fazer
    assert not DATA_COMO_PRAZO.search(fazer)
    assert "Prazo desta convocação" not in fazer

    pagina = main(abrir(client, cenario, "convocacao"))
    antes_dos_dados = pagina.split('id="sobre-esta-convocacao"', 1)[0]
    assert not DATA_COMO_PRAZO.search(texto(antes_dos_dados)), "FR-3749 prevalece"
    # O cartão do prazo diz só a frase da FR-3749 da 118, sem data nem contagem (121, FR-3861).
    assert titulo_da_pagina(pagina) == obrigacoes.TITULO_ABERTA
    prazo = texto(chamada(pagina).split('class="cartao-do-prazo"', 1)[1].split("</div>", 1)[0])
    assert obrigacoes.PRAZO_NAO_INICIADO in prazo and "Você já pode enviar." in prazo
    assert "faltam" not in prazo and "termina" not in prazo
    sobre = texto(bloco(pagina, "Sobre esta convocação"))
    assert obrigacoes.data_e_hora(cenario.convocacao.vencimento) in sobre
    assert "contado do envio da comunicação" in sobre


# --- US4: depois do prazo e depois do resultado -------------------------------------------------


def test_g_o_prazo_terminou_com_o_resumo_e_o_requerimento(fx, client):
    cenario = jornada.montar("G", fx)
    nucleo = obrigacoes.frase_do_prazo_decorrido(cenario.convocacao.vencimento)

    fazer = o_que_fazer(main(abrir(client, cenario, "acompanhamento")))
    assert texto(fazer).startswith(nucleo)
    assert "Até o prazo, ficaram sem envio:" in texto(fazer)
    assert "Requerimento de Matrícula" in texto(fazer).split("ficaram sem envio:")[1]
    assert links(fazer)[0][1] == "Ver como ficou a convocação"

    # O título por estado absorve o do bloco 1 (121, FR-3858, D-005; FR-3741 da 118, revista).
    pagina = main(abrir(client, cenario, "convocacao"))
    assert titulo_da_pagina(pagina) == "O prazo desta convocação terminou"
    assert "O prazo terminou" not in titulos(pagina), "o título não se repete"
    assert formularios(pagina) == 0
    topo_da_tela = texto(chamada(pagina))
    assert nucleo in topo_da_tela
    assert "Até o prazo, ficou assim" in topo_da_tela
    assert obrigacoes.REQUERIMENTO_NAO_ENVIADO_ATE_O_PRAZO in topo_da_tela
    assert "Preencher" not in texto(pagina)
    assert (
        "Precisava de correção: Falta a página 2. Nenhum novo arquivo foi enviado até o prazo."
        in (texto(pagina))
    )
    for proibido in ("Envie ", "Falta enviar", "A comissão vai decidir"):
        assert proibido not in texto(pagina)

    antes = RequerimentoDeMatricula.objects.count()
    requerimento = abrir(client, cenario, "requerimento")
    corpo = texto(main(requerimento))
    assert "O prazo terminou" in corpo and nucleo in corpo
    assert "Voltar à convocação" in corpo
    assert RequerimentoDeMatricula.objects.count() == antes, "o GET não cria rascunho (FR-3754)"


def test_m_o_processo_encerrado_nao_diz_prazo_vencido_nem_promete_conferencia(fx, client):
    cenario = jornada.montar("M", fx)

    fazer = o_que_fazer(main(abrir(client, cenario, "acompanhamento")))
    assert texto(fazer).startswith(
        "Este Processo Seletivo foi encerrado, e não é mais possível enviar documentos nem o "
        "Requerimento de Matrícula pelo portal."
    )
    assert links(fazer)[0][1] == "Ver como ficou a convocação"

    pagina = main(abrir(client, cenario, "convocacao"))
    lido = texto(pagina).lower()
    assert titulo_da_pagina(pagina) == "O envio pelo portal está encerrado"
    assert "O envio pelo portal está encerrado" not in titulos(pagina), "D-005"
    assert formularios(pagina) == 0
    for proibido in ("prazo terminou", "vai conferir", "aguardando conferência", "vai decidir"):
        assert proibido not in lido, proibido
    assert "não foi conferido antes do encerramento do processo" in lido
    assert texto(pagina).count(obrigacoes.REQUERIMENTO_NAO_ENVIADO_ENCERRADO) == 1
    assert obrigacoes.REQUERIMENTO_NAO_ENVIADO_ENCERRADO not in texto(
        bloco(pagina, "O que você já apresentou")
    ), "o não enviado não é dito como apresentado"
    assert "preencher" not in lido
    assert not [h for h, _ in links(pagina) if "/requerimento" in h]

    antes = RequerimentoDeMatricula.objects.count()
    corpo = texto(main(abrir(client, cenario, "requerimento")))
    assert "O envio pelo portal está encerrado" in corpo and "Voltar à convocação" in corpo
    assert RequerimentoDeMatricula.objects.count() == antes


@pytest.mark.parametrize("rascunho", [False, True], ids=["sem-rascunho", "com-rascunho"])
def test_n_o_pedido_e_nunca_enviado_aparece_como_nao_enviado(fx, client, rascunho):
    cenario = jornada._n(fx, rascunho=rascunho)

    # FR-3742 da 118, revista: "Resultado da sua convocação" no topo, e "Resultado registrado" é o
    # rótulo da linha do desfecho.
    pagina = main(abrir(client, cenario, "convocacao"))
    assert titulo_da_pagina(pagina) == "Resultado da sua convocação"
    assert "Resultado registrado:" in texto(chamada(pagina))
    assert "O que você enviou nesta convocação" in titulos(pagina)
    assert obrigacoes.REQUERIMENTO_NAO_ENVIADO in texto(pagina)
    assert formularios(pagina) == 0

    antes = RequerimentoDeMatricula.objects.count()
    corpo = texto(main(abrir(client, cenario, "requerimento")))
    assert "Requerimento de Matrícula não enviado" in corpo
    assert (
        "Esta convocação já tem resultado registrado, e o Requerimento não foi enviado. Não é "
        "mais possível enviá-lo pelo portal." in corpo
    )
    assert "Ainda não é a hora" not in corpo and "for convocado" not in corpo
    assert "Voltar à convocação" in corpo
    assert RequerimentoDeMatricula.objects.count() == antes


@pytest.mark.parametrize("letra", ["I1", "I2"])
def test_i_depois_do_resultado_a_pagina_e_so_historico(fx, client, letra):
    cenario = jornada.montar(letra, fx)

    pagina = main(abrir(client, cenario, "convocacao"))
    lido = texto(pagina)
    assert titulo_da_pagina(pagina) == "Resultado da sua convocação"
    assert titulos(pagina)[:1] == ["O que você enviou nesta convocação"]
    assert formularios(pagina) == 0
    for proibido in (
        "Envie até",
        "Falta enviar",
        "aguardando conferência",
        "Envie um novo arquivo",
    ):
        assert proibido.lower() not in lido.lower(), proibido

    acompanhamento = main(abrir(client, cenario, "acompanhamento"))
    fazer = o_que_fazer(acompanhamento)
    assert links(fazer)[0][1] == "Ver o que você enviou nesta convocação"
    if letra == "I1":
        assert "Vaga aceita" in lido and obrigacoes.ACEITE in lido
        assert "Vaga aceita" in texto(topo(acompanhamento))
        assert obrigacoes.ACEITE in texto(fazer)
        assert "Conferir o Requerimento de Matrícula enviado" in lido
        # FR-3752: com o resultado registrado não há atualização, e a frase não a promete.
        requerimento = texto(main(abrir(client, cenario, "requerimento")))
        assert "Enviado não é alterado." in requerimento
        assert "Se algo mudou" not in requerimento and "for convocado" not in requerimento
        assert "Voltar à convocação" in requerimento
    else:
        assert "Indeferido na convocação" in lido
        assert obrigacoes.ACEITE not in lido
        assert "Não enviado." in lido
        assert re.search(
            r"Enviado em \d\d/\d\d/\d{4}; não foi conferido antes do resultado\.", lido
        )


# --- Sem documento: a linha estritamente informativa (D-019, D-020) ------------------------------


def _sem_link_de_preenchimento(html, pessoa):
    requerimento = reverse("portal:requerimento", args=[pessoa.id])
    return not [h for h, _ in links(html) if h.startswith(requerimento)]


SEM_DOCUMENTO = {
    "G0": (jornada._g0, obrigacoes.REQUERIMENTO_NAO_ENVIADO_ATE_O_PRAZO),
    "N0": (jornada._n0, obrigacoes.REQUERIMENTO_NAO_ENVIADO),
}


@pytest.mark.parametrize("rascunho", [False, True], ids=["sem-rascunho", "com-rascunho"])
@pytest.mark.parametrize("letra", ["G0", "N0", "M0"])
def test_sem_documento_o_requerimento_nao_enviado_e_dito_sem_acao(fx, client, letra, rascunho):
    """G0, N0 e M0 (SC-1128): a ação de hoje, e a linha sem link nem botão, com e sem rascunho."""
    if letra == "M0":
        c = jornada.certame(fx, prefixo="j118-m0", requerimento=True)
        pessoa, conv = jornada.convocar(c, fx.gestor, letra="m0")
        if rascunho:
            # O rascunho de M0 só pode nascer antes do encerramento: depois, a política o recusa.
            jornada.abrir_rascunho(pessoa)
        jornada.encerrar_o_processo(c[0])
        cenario = jornada.Cenario("M0", c[0], pessoa, conv)
        linha = obrigacoes.REQUERIMENTO_NAO_ENVIADO_ENCERRADO
    else:
        montar, linha = SEM_DOCUMENTO[letra]
        cenario = montar(fx, rascunho=rascunho)

    escritas_antes = RegistroAuditoria.objects.count()
    requerimentos_antes = RequerimentoDeMatricula.objects.count()
    fazer = o_que_fazer(main(abrir(client, cenario, "acompanhamento")))
    principal = texto(fazer)
    esperado = situacao.NADA_POR_ENQUANTO if letra == "N0" else situacao.SIGA_AS_INSTRUCOES
    assert principal.startswith(esperado)
    assert linha in principal
    assert "Preencher" not in principal
    assert _sem_link_de_preenchimento(fazer, cenario.pessoa)

    pagina = main(abrir(client, cenario, "convocacao"))
    assert "O que fazer agora" not in titulos(pagina)
    assert linha in texto(pagina)
    # A data não é mais prazo: é o vencimento registrado (FR-3747, FR-3749).
    assert "Prazo desta convocação" not in texto(pagina) and "Vencimento registrado" in texto(
        pagina
    )
    assert "dentro do prazo acima" not in texto(pagina)
    assert "Preencher" not in texto(pagina)
    assert _sem_link_de_preenchimento(pagina, cenario.pessoa)
    assert RegistroAuditoria.objects.count() == escritas_antes + 1, "só a leitura da convocação"
    assert RequerimentoDeMatricula.objects.count() == requerimentos_antes


# --- FR-3756: o caminho de leitura não escreve, e recusa como antes -----------------------------


def contar_linhas():
    with connection.cursor() as cursor:
        tabelas = connection.introspection.table_names(cursor)
        contagem = {}
        for tabela in tabelas:
            cursor.execute(f'SELECT count(*) FROM "{tabela}"')  # noqa: S608 — nome do catálogo
            contagem[tabela] = cursor.fetchone()[0]
    return contagem


@pytest.mark.parametrize("letra", ["C2", "G", "M"])
def test_nenhum_get_grava_alem_da_leitura_da_convocacao(fx, client, letra):
    cenario = jornada.montar(letra, fx)
    entrar_como(client, cenario.pessoa)
    antes = contar_linhas()

    for tela in ("acompanhamento", "convocacao", "requerimento"):
        assert abrir(client, cenario, tela).status_code == 200

    depois = contar_linhas()
    mudou = {t: depois[t] - antes[t] for t in antes if depois.get(t) != antes[t]}
    assert mudou == {RegistroAuditoria._meta.db_table: 1}, mudou


def test_a_inscricao_alheia_e_a_inexistente_recebem_a_mesma_recusa(fx, client):
    cenario = jornada.montar("C2", fx)
    outra = next(i for i in cenario_inscricoes(cenario) if i.id != cenario.pessoa.id)

    for tela in ("acompanhamento", "convocacao", "requerimento"):
        alheia = abrir(client, cenario, tela, pessoa=outra)
        inexistente = abrir(client, cenario, tela, pessoa=outra, inscricao_id=uuid.uuid4())
        assert alheia.status_code == inexistente.status_code == 404, tela
        # O corpo é o mesmo, salvo o que muda a cada requisição (FR-1101 da `059`).
        assert sem_correlacao(alheia) == sem_correlacao(inexistente), tela

    resposta = abrir(client, cenario, "requerimento")
    assert "no-store" in resposta["Cache-Control"], "a resposta privada continua (FR-3756)"


def sem_correlacao(resposta):
    """O corpo sem o que muda a cada requisição: a correlação e o token de CSRF mascarado."""
    corpo = resposta.content.replace(resposta["X-Correlation-ID"].encode(), b"")
    return re.sub(rb'name="csrfmiddlewaretoken" value="[^"]*"', b"", corpo)


def cenario_inscricoes(cenario):
    from processo_seletivo.inscricoes.models import Inscricao

    return list(Inscricao.objects.filter(edital=cenario.edital))


# --- FR-3734, SC-1125: o custo não cresce com os itens ------------------------------------------


def _consultas(client, pessoa, tela):
    entrar_como(client, pessoa)
    with CaptureQueriesContext(connection) as consultas:
        resposta = client.get(reverse(f"portal:{tela}", args=[pessoa.id]))
    assert resposta.status_code == 200
    return consultas


def test_as_duas_telas_custam_o_mesmo_com_um_e_com_seis_itens(fx, client):
    """FR-3734, SC-1125: o número de consultas não cresce com os itens pedidos.

    **Na mesma chamada, e não em dois certames**: dois cenários de convocação no mesmo teste colidem
    no Processo já publicado. A chamada nasce com um item, é medida, ganha mais cinco na lista — as
    linhas que `gravar_lista_da_chamada` teria gravado —, e é medida de novo.
    """
    from processo_seletivo.convocacao.models import ItemDaListaDaConvocacao

    c = jornada.certame(fx, prefixo="j118-custo", documentos=jornada.documentos_em_numero(1))
    pessoa, conv = jornada.convocar(c, fx.gestor, letra="custo")
    cenarios.apresentar(pessoa, conv, CERTIDAO, corpo=b"custo")
    telas = ("acompanhamento", "convocacao")
    com_um = {tela: len(_consultas(client, pessoa, tela)) for tela in telas}

    modelo = cenarios.servico.raiz_da_chamada(conv).itens_da_lista.get()
    campos = {f.attname: getattr(modelo, f.attname) for f in modelo._meta.concrete_fields}
    for n in range(5):
        ItemDaListaDaConvocacao.objects.create(
            **{**campos, "id": uuid.uuid4(), "requisito_id": uuid.uuid4(), "chave": f"extra-{n}"}
        )
    assert len(cenarios.servico.leitura_da_chamada(conv).pedidos) == 6
    com_seis = {tela: len(_consultas(client, pessoa, tela)) for tela in telas}

    assert com_um == com_seis, (com_um, com_seis)


def test_com_a_vigente_sucedendo_outra_o_custo_continua_o_mesmo(fx, client):
    """121, R-008: a linha da substituída lê a anterior e as comunicações dela do *prefetch*, e o
    custo continua sem crescer com os itens quando a vigente corrige outra."""
    from processo_seletivo.convocacao.models import Convocacao, ItemDaListaDaConvocacao
    from tests.integration.convocacao.test_correcao_da_convocacao import corrigir

    c = jornada.certame(fx, prefixo="j121-custo", documentos=jornada.documentos_em_numero(1))
    pessoa, conv = jornada.convocar(c, fx.gestor, letra="custo121")
    corrigir(c[0], fx.gestor, conv, chave="custo121-corrige")
    assert Convocacao.objects.filter(convocacao_anterior=conv).exists()
    telas = ("acompanhamento", "convocacao")
    com_um = {tela: len(_consultas(client, pessoa, tela)) for tela in telas}

    modelo = cenarios.servico.raiz_da_chamada(conv).itens_da_lista.get()
    campos = {f.attname: getattr(modelo, f.attname) for f in modelo._meta.concrete_fields}
    for n in range(5):
        ItemDaListaDaConvocacao.objects.create(
            **{**campos, "id": uuid.uuid4(), "requisito_id": uuid.uuid4(), "chave": f"extra-{n}"}
        )
    com_seis = {tela: len(_consultas(client, pessoa, tela)) for tela in telas}

    assert com_um == com_seis, (com_um, com_seis)
    assert (
        "Convocação substituída"
        in client.get(reverse("portal:convocacao", args=[pessoa.id])).content.decode()
    )


def test_sem_convocacao_o_acompanhamento_nao_le_documentos_da_convocacao(fx, client):
    c = jornada.certame(fx, prefixo="j118-semconv", documentos=cenarios.documentos_do_aluno())
    _, _, inscricoes = c
    consultas = _consultas(client, inscricoes[-1], "acompanhamento")
    lidas = " ".join(q["sql"] for q in consultas.captured_queries).lower()
    assert "convocacao_itemdalistadaconvocacao" not in lidas
    assert "requerimentos_" not in lidas, "o zero da 029 para quem não foi chamado continua"


def test_a_linha_informativa_nao_acrescenta_consulta(fx, client):
    """SC-1128: G0 custa o mesmo antes do prazo, sem a linha, e depois dele, com ela."""
    cenario = jornada.montar("G0", fx)
    telas = ("acompanhamento", "convocacao")
    antes = {tela: len(_consultas(client, cenario.pessoa, tela)) for tela in telas}
    with cenario.relogio():
        depois = {tela: len(_consultas(client, cenario.pessoa, tela)) for tela in telas}
        assert obrigacoes.REQUERIMENTO_NAO_ENVIADO_ATE_O_PRAZO in texto(
            main(client.get(reverse("portal:acompanhamento", args=[cenario.pessoa.id])))
        )
    assert antes == depois, (antes, depois)


@pytest.mark.parametrize("letra", ["G0", "N0", "M0"])
def test_sem_documento_a_unica_consulta_nova_e_a_lista_da_chamada(fx, client, letra):
    """SC-1128 revista, D-021: no acompanhamento, a lista da chamada é lida uma vez, e só ela.

    A medida contra a linha de base está em `verificacao.md` (o acompanhamento paga uma a mais; a
    convocação, nenhuma). Aqui se prende a forma: a consulta nova é a da lista, uma só, e nada da
    leitura documental além dela — nem apresentações, nem conferências, nem o Processo — roda numa
    chamada sem documento. A convocação já lia a lista antes da `118`, e continua lendo uma vez.
    """
    cenario = jornada.montar(letra, fx)
    with cenario.relogio():
        for tela in ("acompanhamento", "convocacao"):
            lidas = [
                q["sql"].lower() for q in _consultas(client, cenario.pessoa, tela).captured_queries
            ]
            da_lista = [q for q in lidas if 'from "convocacao_itemdalistadaconvocacao"' in q]
            assert len(da_lista) == 1, (tela, da_lista)
            for tabela in ("apresentacaodedocumento", "conferenciadedocumento"):
                assert not [q for q in lidas if f'from "convocacao_{tabela}"' in q], (tela, tabela)


def test_a_retificacao_que_tira_o_documento_nao_apaga_o_que_a_chamada_pediu(fx, client):
    """D-021: a leitura é da lista gravada na chamada, e não do conteúdo vigente do Edital.

    A convocação de A pede quatro documentos. Uma Retificação publicada depois os retira do Edital;
    a chamada continua pedindo os quatro, nas duas telas, com o nome que tinham quando foi feita.
    """
    from processo_seletivo.publicacoes.models_retificacao import VersaoConsolidada
    from tests.fixtures.publicacao import create_retification, publish_retification

    cenario = jornada.montar("A", fx)
    retirados = (CERTIDAO, HISTORICO, CERTIFICADO_DO_MEDIO, RESIDENCIA)
    publish_retification(
        fx.api_client,
        create_retification(
            fx.api_client,
            cenario.edital,
            [
                {"targetPath": f"/documentRequirements/id={req}", "operation": "REMOVE"}
                for req in retirados
            ],
            suffix="j118-retira",
        ),
        suffix="j118-retira",
    )
    vigente = VersaoConsolidada.objects.filter(edital=cenario.edital).latest("materialized_at")
    restantes = {str(d.get("id")) for d in vigente.content.get("documentRequirements") or []}
    assert not restantes & {str(r) for r in retirados}, "a Retificação tirou os documentos"

    fazer = texto(o_que_fazer(main(abrir(client, cenario, "acompanhamento"))))
    assert fazer.startswith("Você ainda precisa enviar 4 documentos.")
    pagina = main(abrir(client, cenario, "convocacao"))
    nomes = re.findall(r"<h3>(.*?)</h3>", bloco(pagina, "O que falta"))
    assert nomes == [
        "Certidão de nascimento ou casamento",
        "Histórico escolar do ensino médio",
        "Certificado de conclusão do ensino médio",
        "Comprovante de residência",
    ]
    assert formularios(bloco(pagina, "O que falta")) == 4
