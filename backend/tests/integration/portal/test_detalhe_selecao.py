"""A página que responde "essa oportunidade serve para mim?" (US1, FR-014, FR-011)."""

import re

import pytest
from django.urls import reverse

from processo_seletivo.processos.models import Edital
from tests.fixtures.edital import actor_headers
from tests.fixtures.selecao import publicar_selecao, rascunho_de_selecao


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_o_detalhe_apresenta_os_perfis_com_o_que_decide_a_candidatura(
    client, api_client, manager_headers, process_payload
):
    edital = publicar_selecao(api_client, manager_headers, process_payload)

    corpo = client.get(reverse("portal:selecao", args=[edital.id])).content.decode()

    assert "Professor de Informática" in corpo
    assert "Técnico de Laboratório" in corpo
    assert "Campus Serra" in corpo
    assert "Mestrado em Computação ou área afim" in corpo
    assert "Ampla concorrência" in corpo
    assert "Pessoas pretas, pardas e indígenas" in corpo


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_o_detalhe_deriva_da_versao_vigente_e_nao_do_rascunho(
    client, api_client, manager_headers, process_payload
):
    edital = publicar_selecao(api_client, manager_headers, process_payload)
    rascunho = rascunho_de_selecao()
    rascunho["profiles"][0]["name"] = "Nome que ninguém publicou"
    api_client.put(
        f"/api/v1/admin/editais/{edital.id}/rascunho",
        rascunho,
        format="json",
        **{
            **actor_headers("preparador", ["edital:elaborar"], key="rascunho-portal-0001"),
            "HTTP_IF_MATCH": f'"{Edital.objects.get(pk=edital.pk).revision}"',
        },
    )

    corpo = client.get(reverse("portal:selecao", args=[edital.id])).content.decode()

    assert "Nome que ninguém publicou" not in corpo
    assert "Professor de Informática" in corpo


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_selecao_sem_publicacao_nao_tem_pagina(
    client, api_client, manager_headers, process_payload
):
    api_client.post("/api/v1/admin/processos", process_payload, format="json", **manager_headers)
    edital = Edital.objects.get()

    assert client.get(reverse("portal:selecao", args=[edital.id])).status_code == 404


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_o_detalhe_nao_expoe_identificador_tecnico_no_corpo(
    client, api_client, manager_headers, process_payload
):
    """A `007` tirou o UUID do documento pelo mesmo motivo: não prova nada a quem lê.

    O identificador continua no endereço, porque é assim que se chega à página — e identificador
    público não confere autorização (princípio I).
    """
    edital = publicar_selecao(api_client, manager_headers, process_payload)

    corpo = client.get(reverse("portal:selecao", args=[edital.id])).content.decode()
    corpo_visivel = corpo.split("<main")[1]

    assert str(edital.processo_id) not in corpo_visivel


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_ler_o_edital_nao_disputa_a_decisao_com_inscrever_se(
    client, api_client, manager_headers, process_payload
):
    """SC-UX-008: duas chamadas de ação não disputam a mesma decisão.

    Enquanto usava o mesmo verde sólido dos botões de inscrição, `Ler o Edital completo (PDF)` era
    o único botão preenchido na primeira dobra em 375px — a página anunciava "baixe um PDF" onde
    queria anunciar "inscreva-se".
    """
    edital = publicar_selecao(api_client, manager_headers, process_payload)

    corpo = client.get(reverse("portal:selecao", args=[edital.id])).content.decode()

    assert 'class="documento secundaria"' in corpo
    assert ".documento.secundaria{background:var(--branco)" in corpo
    assert corpo.count('class="documento secundaria"') == 1, "só o PDF é secundário"


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_os_documentos_exigidos_aparecem_antes_da_identificacao(
    client, api_client, manager_headers, process_payload
):
    """L7 da auditoria de percurso: saber o que preparar antes de começar.

    A página listava requisitos de titulação e nada sobre arquivos. Descobrir que precisaria do
    diploma digitalizado custava identificar-se e abrir uma inscrição — e quem lê no ônibus, sem
    os arquivos à mão, desiste no meio.
    """
    from datetime import timedelta

    from django.utils import timezone

    from tests.fixtures.selecao import rascunho_aberto_com_documentos

    edital = publicar_selecao(
        api_client,
        manager_headers,
        process_payload,
        rascunho=rascunho_aberto_com_documentos(timezone.now() - timedelta(seconds=1)),
    )

    corpo = client.get(reverse("portal:selecao", args=[edital.id])).content.decode()

    # O resumo conta quantos são: um triângulo com “Documentos que serão pedidos” parece enfeite,
    # e a contagem é o que decide se dá para se inscrever agora ou se é preciso preparar.
    assert "documentos que serão pedidos" in corpo
    assert re.search(r"<summary>\s*\d+ documentos? que ser", corpo), corpo[:0]
    assert "Documento de identificação" in corpo, "o que vale para todo mundo"
    assert "Diploma de graduação" in corpo, "o que vale para o Perfil"
    assert "Se concorrer em" in corpo, "e o que a modalidade reservada acrescenta"
    assert "Autodeclaração étnico-racial" in corpo


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_o_cartao_da_vitrine_e_alvo_inteiro(client, api_client, manager_headers, process_payload):
    """L8: num celular, mirar duas palavras de título é o tipo de precisão que faz errar."""
    publicar_selecao(api_client, manager_headers, process_payload)

    corpo = client.get(reverse("portal:vitrine")).content.decode()

    assert '.selecao a.titulo::after{content:"";position:absolute;inset:0}' in corpo
    assert ".selecao:focus-within{outline:" in corpo, "o teclado continua vendo o foco"


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_o_requisito_vem_antes_do_botao_de_inscrever(
    client, api_client, manager_headers, process_payload
):
    """A ordem do cartão é a ordem da decisão.

    Ele dizia nome → dados → INSCREVER-SE → documentos → requisitos: as duas informações com que a
    pessoa decide — “tenho o título?” e “tenho os arquivos?” — vinham depois do botão que pede a
    decisão. Quem lê de cima para baixo era convidado a se inscrever antes de saber se podia.
    """
    from datetime import timedelta

    from django.utils import timezone

    from tests.fixtures.selecao import rascunho_aberto_com_documentos

    edital = publicar_selecao(
        api_client,
        manager_headers,
        process_payload,
        rascunho=rascunho_aberto_com_documentos(timezone.now() - timedelta(seconds=1)),
    )

    corpo = client.get(reverse("portal:selecao", args=[edital.id])).content.decode()

    requisitos = corpo.index("Requisitos")
    documentos = corpo.index("que serão pedidos")
    botao = corpo.index("Inscrever-se nesta vaga")

    assert requisitos < botao, "o requisito é o primeiro filtro que a pessoa aplica"
    assert documentos < botao, "e saber o que preparar decide se dá para começar agora"


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_o_cartao_da_vaga_nao_empilha_um_dado_por_linha(
    client, api_client, manager_headers, process_payload
):
    """Localidade e concorrência viram uma linha de dados, e não pares empilhados.

    Em 375 px eram seis linhas para três informações, e o cartão inteiro ocupava mais da metade da
    tela — com dois perfis, a página passava de mil e quatrocentos pixels.
    """
    edital = publicar_selecao(api_client, manager_headers, process_payload)

    corpo = client.get(reverse("portal:selecao", args=[edital.id])).content.decode()

    assert 'class="dados-vaga"' in corpo
    assert "<dt>Localidade</dt>" not in corpo
    assert "<dt>Vagas imediatas</dt>" not in corpo
    # O número de vagas continua sendo o dado em destaque, agora ao lado da ação.
    assert 'class="vagas-numero"' in corpo


# ---------------------------------------------------------------------------
# O que a 024 acrescentou: o que a vaga é, e a leitura do cadastro reserva.
# ---------------------------------------------------------------------------


def rascunho_aberto():
    """A mesma seleção, com o período de inscrições correndo — é o que faz o convite existir."""
    from datetime import timedelta

    from django.utils import timezone

    agora = timezone.now()
    rascunho = rascunho_de_selecao()
    rascunho["schedule"][0]["startAt"] = (agora - timedelta(days=1)).isoformat()
    rascunho["schedule"][0]["endAt"] = (agora + timedelta(days=9)).isoformat()
    rascunho["schedule"][0]["isRegistrationPeriod"] = True
    return rascunho


ATRIBUICOES = "Ministrar aulas, orientar projetos integradores e participar de bancas."
CARGA = "40 horas semanais"
REMUNERACAO = "R$ 6.180,00 mais auxílio-alimentação"


def rascunho_com_o_que_a_vaga_e():
    """O primeiro Perfil declara os três campos; o segundo não declara nenhum."""
    rascunho = rascunho_de_selecao()
    rascunho["profiles"][0]["duties"] = ATRIBUICOES
    rascunho["profiles"][0]["workload"] = CARGA
    rascunho["profiles"][0]["compensation"] = REMUNERACAO
    return rascunho


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_a_vaga_diz_o_que_e_e_nao_so_o_que_exige(
    client, api_client, manager_headers, process_payload
):
    """FR-134 — atribuições, carga horária e remuneração, publicadas e agora legíveis.

    Estavam no conteúdo publicado desde a `007` e não apareciam em tela nenhuma do portal: quem
    comparava duas vagas sabia o título que precisava ter e não sabia o que ia fazer, por quantas
    horas nem por quanto.
    """
    edital = publicar_selecao(
        api_client, manager_headers, process_payload, rascunho=rascunho_com_o_que_a_vaga_e()
    )

    corpo = client.get(reverse("portal:selecao", args=[edital.id])).content.decode()

    assert ATRIBUICOES in corpo
    assert CARGA in corpo
    assert REMUNERACAO in corpo
    assert "Atribuições" in corpo and "Carga horária" in corpo and "Remuneração" in corpo


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_campo_nao_declarado_nao_vira_rotulo_vazio_nem_nao_informado(
    client, api_client, manager_headers, process_payload
):
    """FR-135, D-009 — `""` é "não declarado", e a linha some.

    O segundo Perfil da fixture não declara nenhum dos três. Escrever "não informado" ali afirmaria
    uma omissão do Edital, e ele pode nunca ter tido o que declarar — um Perfil de bolsa não tem
    remuneração no sentido de vínculo.
    """
    edital = publicar_selecao(
        api_client, manager_headers, process_payload, rascunho=rascunho_com_o_que_a_vaga_e()
    )

    corpo = client.get(reverse("portal:selecao", args=[edital.id])).content.decode()
    segunda_vaga = corpo[corpo.index("Técnico de Laboratório") :]

    assert "não informado" not in corpo.lower()
    assert "Atribuições" not in segunda_vaga
    assert "Carga horária" not in segunda_vaga
    assert "Remuneração" not in segunda_vaga


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_cadastro_reserva_sem_vaga_imediata_e_oferta_e_nao_ausencia(
    client, api_client, manager_headers, process_payload
):
    """FR-136, D-007 — o zero deixa de ser a manchete.

    O segundo Perfil da fixture tem zero vagas imediatas e cadastro reserva ilimitado. A tela punha
    o `0` em corpo 28, com a reserva de legenda: "0 vagas imediatas, com cadastro reserva
    ilimitado" lê-se como contradição, não como oportunidade.

    O que se prende aqui: a oferta é o que salta, o número continua dito, e o convite continua de
    pé — porque a vaga existe e a inscrição é legítima.
    """
    edital = publicar_selecao(
        api_client, manager_headers, process_payload, rascunho=rascunho_aberto()
    )

    corpo = client.get(reverse("portal:selecao", args=[edital.id])).content.decode()
    segunda_vaga = corpo[corpo.index("Técnico de Laboratório") :]

    assert "reserva-primeiro" in segunda_vaga
    assert "<strong>Cadastro reserva</strong>" in segunda_vaga
    # O zero continua na página — em posição secundária, e não como a leitura principal.
    assert "0 vagas imediatas agora" in segunda_vaga
    assert "<strong>0</strong>" not in segunda_vaga, "o zero voltou a ser a manchete"
    # E o convite continua de pé: cadastro reserva recebe inscrição como qualquer outra vaga.
    assert "Inscrever-se nesta vaga" in segunda_vaga


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_havendo_vaga_imediata_o_numero_continua_sendo_a_noticia(
    client, api_client, manager_headers, process_payload
):
    """FR-136 — a mudança vale só onde havia o defeito.

    O primeiro Perfil tem duas vagas imediatas. Ali o numeral **é** a notícia, e a tela continua
    como estava: trocar os dois casos pela mesma forma resolveria um defeito criando outro.
    """
    edital = publicar_selecao(api_client, manager_headers, process_payload)

    corpo = client.get(reverse("portal:selecao", args=[edital.id])).content.decode()
    primeira_vaga = corpo[corpo.index("Professor de Informática") : corpo.index("Técnico de Lab")]

    assert "<strong>2</strong>" in primeira_vaga
    assert "com cadastro reserva" in primeira_vaga
    assert "reserva-primeiro" not in primeira_vaga


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_o_convite_anuncia_a_identificacao_antes_de_ser_acionado(
    client, api_client, manager_headers, process_payload
):
    """FR-137 — toda ação diz o que vai acontecer.

    O convite levava direto à identificação, e a pessoa descobria que precisava de um e-mail depois
    de já ter decidido entrar. Não é obstáculo escondido de propósito; é que ninguém tinha dito.
    """
    edital = publicar_selecao(
        api_client, manager_headers, process_payload, rascunho=rascunho_aberto()
    )

    corpo = client.get(reverse("portal:selecao", args=[edital.id])).content.decode()

    assert "Inscrever-se exige identificação por e-mail." in corpo


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_reserva_limitada_em_zero_nao_e_anunciada_como_sem_limite(
    client, api_client, manager_headers, process_payload
):
    """FR-136 — limite declarado como zero **é** limite declarado.

    O domínio aceita `reserveLimit: 0`: `perfis.py` recusa apenas limite negativo. Testado por
    veracidade em vez de por presença, o zero caía no ramo do ilimitado e a tela dizia "sem limite
    declarado" sobre um Edital que declarou o limite — afirmação sobre o ato, feita pela tela.
    """
    rascunho = rascunho_de_selecao()
    rascunho["profiles"][1]["reserveType"] = "LIMITED"
    rascunho["profiles"][1]["reserveLimit"] = 0
    edital = publicar_selecao(api_client, manager_headers, process_payload, rascunho=rascunho)

    corpo = client.get(reverse("portal:selecao", args=[edital.id])).content.decode()
    segunda_vaga = corpo[corpo.index("Técnico de Laboratório") :]

    assert "até 0 classificados" in segunda_vaga
    assert "sem limite declarado" not in segunda_vaga


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_a_volta_preserva_a_consulta_e_so_ela(client, api_client, manager_headers, process_payload):
    """FR-144, T-007 — a consulta volta; o resto, não.

    A página da seleção não interpreta a consulta: ela só a devolve. Por isso o que ela repassa
    precisa ser conferido — um valor arbitrário ecoado para dentro de um endereço é como se abre
    redirecionamento, e aqui o critério é mais estreito que o de `_destino_seguro`.
    """
    edital = publicar_selecao(api_client, manager_headers, process_payload)

    corpo = client.get(
        reverse("portal:selecao", args=[edital.id]),
        {"busca": "informatica", "ordem": "recentes", "next": "https://exemplo.invalido/"},
    ).content.decode()

    assert "Voltar aos resultados" in corpo
    assert "busca=informatica" in corpo
    assert "ordem=recentes" in corpo
    assert "exemplo.invalido" not in corpo, "um endereço externo atravessou para o link de volta"
    assert "next=" not in corpo


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_sem_consulta_a_volta_leva_ao_catalogo_inteiro(
    client, api_client, manager_headers, process_payload
):
    """Quem chegou pelo endereço direto não tem consulta a preservar, e o link continua servindo."""
    edital = publicar_selecao(api_client, manager_headers, process_payload)

    corpo = client.get(reverse("portal:selecao", args=[edital.id])).content.decode()

    assert f'href="{reverse("portal:vitrine")}"' in corpo


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_a_volta_limita_o_que_repassa(client, api_client, manager_headers, process_payload):
    """T-007 — nome conferido, enumeração conferida, comprimento sempre.

    `unidade` e `perfil` seguem como texto livre porque a vitrine os confere na chegada, contra o
    catálogo. O que ela não faz é limitar o tamanho — e um valor de cem mil caracteres viraria um
    `href` de cem mil caracteres.
    """
    edital = publicar_selecao(api_client, manager_headers, process_payload)

    corpo = client.get(
        reverse("portal:selecao", args=[edital.id]),
        {"busca": "x" * 5000, "situacao": "banana", "ordem": "prazo"},
    ).content.decode()

    volta = corpo[corpo.index('<p class="voltar">') :]
    volta = volta[: volta.index("</p>")]

    assert len(volta) < 500, "o valor atravessou sem limite de tamanho"
    assert "situacao=banana" not in volta, "situação irreconhecível atravessou"
    assert "ordem=prazo" not in volta, "a ordem padrão poluiu o endereço"
