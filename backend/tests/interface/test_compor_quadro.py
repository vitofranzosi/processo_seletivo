"""A seção do quadro de vagas na tela de composição do Perfil (025, US1 e US4).

O que a tela promete: uma seção **dentro** do cartão do Perfil, linhas oferecidas a partir das
Modalidades já declaradas, e só as quantidades digitadas. É o que faz um Edital de sete polos ser
composto sem redigitar rótulo nenhum — e o que separa a US1 de "possível e insuportável".
"""

import re

import pytest
from django.urls import reverse

from processo_seletivo.editais.domain.validation import (
    blocking_findings,
    validate_for_publication,
)
from processo_seletivo.editais.models.perfis import LinhaDoQuadroDeVagas, PerfilVaga
from processo_seletivo.processos.models import Edital
from processo_seletivo.publicacoes.application.publish_edital import edital_snapshot
from tests.interface.conftest import identificar

pytestmark = [pytest.mark.django_db]


# Identidades por família, e não por sorteio: `2500` é Perfil, `2510` é Modalidade e `2520` é
# linha do quadro. O sufixo é `<sub><indice>`. Famílias separadas porque um identificador repetido
# entre coleções responde 409 `identifier_belongs_to_another_edital` — e a recusa apareceria como
# "a tela não gravou", longe da causa.
def _id(familia, sub=0, indice=0):
    return f"aaaaaaaa-0000-4000-8000-{familia}0000{sub:02d}{indice:02d}"


PERFIL = _id("2500")

# As três Modalidades do Perfil, na ordem em que a tela as desenha.
MODALIDADES = (
    ("AC", "Ampla concorrência"),
    ("PCD", "Pessoa com deficiência"),
    ("PPI", "Pretos, pardos e indígenas"),
)


@pytest.fixture
def edital(api_client, manager_headers, process_payload):
    api_client.post("/api/v1/admin/processos", process_payload, format="json", **manager_headers)
    return Edital.objects.get()


def perfil(indice=0, total="80", quantidades=("56", "4", "20"), **extras):
    """Um Perfil com três Modalidades e as quatro quantidades do quadro — nada mais.

    A tela oferece **quatro** linhas: a geral e uma por Modalidade. A da "Ampla concorrência" vai
    em branco, que é o que a D-004 manda — o número dela mora na linha geral, e em branco não grava
    linha nenhuma.
    """
    campos = {
        f"perfil-{indice}-id": _id("2500", indice=indice),
        f"perfil-{indice}-code": f"C{indice + 1}",
        f"perfil-{indice}-name": f"Curso {indice + 1}",
        f"perfil-{indice}-immediateVacancies": total,
        f"perfil-{indice}-reserveType": "NONE",
        f"linha-{indice}-0-id": _id("2520", indice=indice),
        f"linha-{indice}-0-modalityId": "",
        f"linha-{indice}-0-immediateVacancies": quantidades[0],
    }
    for sub, (codigo, nome) in enumerate(MODALIDADES):
        modalidade = _id("2510", sub=sub + 1, indice=indice)
        campos[f"modalidade-{indice}-{sub}-id"] = modalidade
        campos[f"modalidade-{indice}-{sub}-code"] = codigo
        campos[f"modalidade-{indice}-{sub}-name"] = nome
        campos[f"linha-{indice}-{sub + 1}-id"] = _id("2520", sub=sub + 1, indice=indice)
        campos[f"linha-{indice}-{sub + 1}-modalityId"] = modalidade
        campos[f"linha-{indice}-{sub + 1}-immediateVacancies"] = (
            "" if codigo == "AC" else quantidades[sub]
        )
    return {**campos, **extras}


def compor(client, edital, dados):
    return client.post(reverse("interface:compor-etapa", args=[edital.id, "perfis"]), dados)


def tela(client, edital):
    resposta = client.get(reverse("interface:compor-etapa", args=[edital.id, "perfis"]))
    assert resposta.status_code == 200
    return resposta.content.decode()


@pytest.fixture
def composto(client, seletor_ligado, edital):
    identificar(client, "ana.elaboradora", ["elaborador"])
    resposta = compor(client, edital, perfil())
    assert resposta.status_code == 302, resposta.content
    return edital


def secao_do_quadro(corpo, indice=0):
    """O trecho da seção do quadro daquele Perfil, e nada além dele."""
    inicio = corpo.index(f'<h3 id="quadro-titulo-{indice}">')
    return corpo[inicio : corpo.index("</section>", inicio)]


# --- T018 · a seção mora dentro do cartão do Perfil (UX-020) ---------------------------------


def test_o_quadro_e_secao_do_cartao_do_perfil_e_nao_tela_a_parte(client, seletor_ligado, composto):
    """Tela à parte seria mais fácil de escrever e destruiria o que a outra tivesse gravado.

    O rascunho é substituído inteiro a cada POST: duas telas gravando Perfis significa a segunda
    apagando a primeira. Na mesma seção e no mesmo envio, o problema não existe (UX-020).
    """
    identificar(client, "ana.elaboradora", ["elaborador"])
    corpo = tela(client, composto)

    cartao = corpo[corpo.index('class="linha perfil"') :]
    cartao = cartao[: cartao.index("Remover este Perfil")]
    assert '<h3 id="quadro-titulo-0">Quadro de vagas</h3>' in cartao, (
        "o quadro é seção do cartão do Perfil, e vem antes do fim dele"
    )

    # E o quadro não tem passo próprio no assistente: ele não é etapa, é seção.
    from processo_seletivo.interface.views import CHAVES_ETAPA

    assert "quadro" not in CHAVES_ETAPA


# --- T019 · só quantidades são digitadas (UX-021, SC-048) -----------------------------------


def test_so_as_quantidades_sao_digitaveis_na_secao_do_quadro(client, seletor_ligado, composto):
    """Quatro números, e nenhum rótulo, código ou denominação redigitado (SC-048)."""
    identificar(client, "ana.elaboradora", ["elaborador"])
    quadro = secao_do_quadro(tela(client, composto))

    editaveis = re.findall(r'<input type="(?!hidden)[^"]*"[^>]*name="(linha-[^"]+)"', quadro)
    assert len(editaveis) == 4, editaveis
    assert all(nome.endswith("-immediateVacancies") for nome in editaveis)

    # Os rótulos aparecem como **texto**, e não como campo: nada neles é redigitável.
    assert "Pessoa com deficiência (PCD)" in quadro
    assert "Pretos, pardos e indígenas (PPI)" in quadro
    ocultos = re.findall(r'<input type="hidden"[^>]*name="(linha-[^"]+)"', quadro)
    assert {nome.rsplit("-", 1)[1] for nome in ocultos} == {"id", "modalityId"}


# --- T020 · a linha geral é distinguível sem cor (UX-022) -----------------------------------


def test_a_linha_geral_e_distinguivel_sem_cor_e_diz_que_e_a_da_ampla_concorrencia(
    client, seletor_ligado, composto
):
    """Sem depender de cor: o texto do próprio rótulo, e peso tipográfico — não uma pastilha."""
    identificar(client, "ana.elaboradora", ["elaborador"])
    quadro = secao_do_quadro(tela(client, composto))

    assert "<strong>Ampla concorrência</strong>" in quadro
    assert "Esta é a linha" in quadro and "ampla concorrência" in quadro
    # A distinção não é de cor: a linha geral não ganha classe de cor nenhuma.
    primeira = quadro[: quadro.index("</div>")]
    assert 'class="linha-do-quadro"' in primeira


# --- T021 · quantidade em branco não grava linha (FR-159, D-006) ----------------------------


def test_quantidade_em_branco_nao_grava_linha_e_ausencia_nao_vira_zero(composto):
    """A Modalidade "Ampla concorrência" foi oferecida e deixada em branco (D-004)."""
    perfil_gravado = PerfilVaga.objects.get(pk=PERFIL)
    linhas = list(perfil_gravado.quadro_de_vagas.all())

    assert [
        (str(linha.modalidade_id) if linha.modalidade_id else None, linha.vagas_imediatas)
        for linha in linhas
    ] == [
        (None, 56),
        (_id("2510", sub=2), 4),
        (_id("2510", sub=3), 20),
    ]
    assert not perfil_gravado.quadro_de_vagas.filter(modalidade_id=_id("2510", sub=1)).exists()


def test_o_quadro_gravado_volta_a_tela_com_as_quantidades(client, seletor_ligado, composto):
    """Travessia 3 de 4: sem a reexibição, a gravação seguinte apagaria o que já estava lá."""
    identificar(client, "ana.elaboradora", ["elaborador"])
    quadro = secao_do_quadro(tela(client, composto))

    valores = re.findall(r'name="linha-0-\d+-immediateVacancies"\s+value="([^"]*)"', quadro)
    assert valores == ["56", "", "4", "20"]


# --- A recusa da soma chega ancorada na linha, com os três números (UX-023) ------------------


def _achados_do_quadro(edital):
    return [
        item
        for item in blocking_findings(validate_for_publication(edital_snapshot(edital)))
        if item.code.startswith("vacancy_")
    ]


def test_o_rascunho_aceita_o_quadro_que_ainda_nao_fecha(client, seletor_ligado, composto):
    """A conferência é da submissão, e não da gravação.

    Recusá-la na gravação impediria salvar o trabalho pela metade, que é o que compor um Edital de
    sete polos exige. Quem recusa é quem publica.
    """
    identificar(client, "ana.elaboradora", ["elaborador"])
    resposta = compor(client, composto, perfil(quantidades=("55", "4", "20")))

    assert resposta.status_code == 302, resposta.content


def test_a_soma_que_excede_o_total_e_recusada_com_os_numeros(client, seletor_ligado, composto):
    """O limite superior não espera pela completude, e é ele que pega o erro perigoso (FR-177).

    Um `PPI 200` digitado no lugar de `20` é recusado mesmo neste Edital — o que declara uma
    Modalidade chamada "Ampla concorrência" e que, por isso, nunca tem quadro completo.
    """
    identificar(client, "ana.elaboradora", ["elaborador"])
    resposta = compor(client, composto, perfil(quantidades=("56", "4", "200")))
    assert resposta.status_code == 302, resposta.content

    composto.refresh_from_db()
    achados = _achados_do_quadro(composto)
    assert [item.code for item in achados] == ["vacancy_sum_exceeds_total"]
    mensagem = achados[0].message
    assert "260" in mensagem and "80" in mensagem and "excesso de 180" in mensagem


def test_a_igualdade_nao_roda_onde_uma_modalidade_fica_sem_linha(client, seletor_ligado, composto):
    """**A lacuna da R-006, verificada em vez de suposta.**

    Seguir a FR-176 deixa a Modalidade "Ampla concorrência" sem linha reservada, e o quadro nunca
    fica completo: a igualdade da FR-161 não roda neste formato, que a spec diz ser o normal. O
    quadro que soma 79 contra 80 passa, e é o que este teste registra — não como conquista, mas
    para que a lacuna não seja descoberta de novo. Fechá-la pede uma das duas saídas nomeadas na
    `research.md`, e a escolha é do usuário.
    """
    identificar(client, "ana.elaboradora", ["elaborador"])
    resposta = compor(client, composto, perfil(quantidades=("55", "4", "20")))
    assert resposta.status_code == 302, resposta.content

    composto.refresh_from_db()
    assert _achados_do_quadro(composto) == []


def test_a_divergencia_da_soma_e_dita_em_numeros_onde_o_quadro_fecha(
    client, seletor_ligado, edital
):
    """Onde o quadro **é** completo, a diferença é dita em três números (FR-161, UX-023, SC-054).

    Aqui a única Modalidade declarada tem linha, e por isso a igualdade roda: o Perfil declara 80
    vagas e o quadro reparte 79.
    """
    identificar(client, "ana.elaboradora", ["elaborador"])
    dados = {
        "perfil-0-id": _id("2500"),
        "perfil-0-code": "C1",
        "perfil-0-name": "Curso 1",
        "perfil-0-immediateVacancies": "80",
        "perfil-0-reserveType": "NONE",
        "modalidade-0-0-id": _id("2510", sub=1),
        "modalidade-0-0-code": "PPI",
        "modalidade-0-0-name": "Pretos, pardos e indígenas",
        "linha-0-0-id": _id("2520"),
        "linha-0-0-modalityId": "",
        "linha-0-0-immediateVacancies": "59",
        "linha-0-1-id": _id("2520", sub=1),
        "linha-0-1-modalityId": _id("2510", sub=1),
        "linha-0-1-immediateVacancies": "20",
    }
    resposta = compor(client, edital, dados)
    assert resposta.status_code == 302, resposta.content

    edital.refresh_from_db()
    achados = _achados_do_quadro(edital)
    assert [item.code for item in achados] == ["vacancy_sum_mismatch"]
    mensagem = achados[0].message
    assert "79" in mensagem and "80" in mensagem and "diferença de 1" in mensagem


# --- T074–T076 · o Edital grande (US4) -------------------------------------------------------


def sete_polos():
    dados = {}
    for indice in range(7):
        dados.update(perfil(indice=indice))
    return dados


def test_sete_perfis_de_tres_modalidades_pedem_no_maximo_vinte_e_oito_campos(
    client, seletor_ligado, edital
):
    """7 × (1 geral + 3 reservadas) = 28, e nenhum campo de rótulo, código ou denominação.

    É a medida da SC-052, e ela está num teste em vez de numa impressão de propósito: a pressão de
    autoria do Edital grande é o que faz a US1 ser possível e insuportável sem a US4.
    """
    identificar(client, "ana.elaboradora", ["elaborador"])
    resposta = compor(client, edital, sete_polos())
    assert resposta.status_code == 302, resposta.content

    corpo = tela(client, edital)
    editaveis = re.findall(r'<input type="(?!hidden)[^"]*"[^>]*name="(linha-[^"]+)"', corpo)
    assert len(editaveis) == 28, len(editaveis)
    assert all(nome.endswith("-immediateVacancies") for nome in editaveis)


def test_os_sete_quadros_sao_gravados_numa_submissao_so(client, seletor_ligado, edital):
    identificar(client, "ana.elaboradora", ["elaborador"])
    resposta = compor(client, edital, sete_polos())
    assert resposta.status_code == 302, resposta.content

    assert LinhaDoQuadroDeVagas.objects.filter(perfil__edital=edital).count() == 21
    assert (
        sum(
            linha.vagas_imediatas
            for linha in LinhaDoQuadroDeVagas.objects.filter(perfil__edital=edital)
        )
        == 7 * 80
    )


def test_uma_quantidade_em_branco_entre_sete_perfis_apaga_so_aquela_linha(
    client, seletor_ligado, edital
):
    """As outras vinte permanecem: a ausência é daquela linha, e não do quadro (FR-159, D-006)."""
    identificar(client, "ana.elaboradora", ["elaborador"])
    dados = sete_polos()
    dados["linha-3-3-immediateVacancies"] = ""
    dados["perfil-3-immediateVacancies"] = "60"
    resposta = compor(client, edital, dados)
    assert resposta.status_code == 302, resposta.content

    assert LinhaDoQuadroDeVagas.objects.filter(perfil__edital=edital).count() == 20
    do_perfil = LinhaDoQuadroDeVagas.objects.filter(perfil_id=_id("2500", indice=3))
    assert do_perfil.count() == 2
    assert not do_perfil.filter(modalidade_id=_id("2510", sub=3, indice=3)).exists()


# --- T077/T078 · o Edital grande atravessado pelo teclado ------------------------------------


def test_a_secao_do_quadro_de_um_perfil_e_atravessada_inteira_antes_da_do_seguinte(
    client, seletor_ligado, edital
):
    """A Constituição exige teclado e prevenção de erro, e o Edital grande é onde isso pesa.

    Com sete cartões, a ordem de tabulação é a ordem do documento: as quatro linhas do quadro de
    um Perfil vêm juntas, e nenhuma delas fica alcançável só depois de atravessar o Perfil
    seguinte. Nenhum `tabindex` positivo reordena nada — se houvesse, seria ele a decidir.
    """
    identificar(client, "ana.elaboradora", ["elaborador"])
    resposta = compor(client, edital, sete_polos())
    assert resposta.status_code == 302, resposta.content

    corpo = tela(client, edital)
    assert not re.search(r'tabindex="[1-9]', corpo)

    posicoes = [
        (int(indice), int(sub), lugar.start())
        for lugar in re.finditer(r'name="linha-(\d+)-(\d+)-immediateVacancies"', corpo)
        for indice, sub in [lugar.groups()]
    ]
    assert len(posicoes) == 28
    # Agrupadas por Perfil: a última linha do Perfil N vem antes da primeira do Perfil N+1.
    for perfil_atual in range(6):
        ultimas = [lugar for indice, _, lugar in posicoes if indice == perfil_atual]
        primeiras = [lugar for indice, _, lugar in posicoes if indice == perfil_atual + 1]
        assert max(ultimas) < min(primeiras)


def test_cada_linha_do_quadro_tem_rotulo_ligado_ao_proprio_campo(client, seletor_ligado, composto):
    """Rótulo solto não é anunciado, e o campo vira "caixa de número" para quem ouve a tela."""
    identificar(client, "ana.elaboradora", ["elaborador"])
    quadro = secao_do_quadro(tela(client, composto))

    rotulados = set(re.findall(r'<label for="(linha-\d+-\d+-immediateVacancies)"', quadro))
    campos = set(re.findall(r'id="(linha-\d+-\d+-immediateVacancies)"', quadro))
    assert rotulados == campos

    descritos = set(re.findall(r'aria-describedby="(ajuda-linha-\d+-\d+)"', quadro))
    # `ajuda`, e não `oculto` (027, UX-041). A explicação deixou de ser anunciada só a quem ouve a
    # tela: ela é impressa, porque a microcópia invisível a quem enxerga é metade da causa do
    # achado que a `027` fecha. O `aria-describedby` continua apontando o mesmo alvo.
    existentes = set(re.findall(r'<span class="ajuda" id="(ajuda-linha-\d+-\d+)"', quadro))
    assert descritos <= existentes, "todo `aria-describedby` aponta alvo que existe"


# --- E2E25-001 · o Perfil recém-acrescentado já oferece a linha geral ------------------------


def test_o_perfil_acrescentado_pela_tela_carrega_a_linha_geral_sem_pedir_o_numero_duas_vezes(
    client, seletor_ligado, edital
):
    """O beco da `025` fechado pelo outro lado, e melhor (027, FR-316, E2E25-001).

    A `025` fez a linha nascer com o Perfil porque a seção do quadro aparecia vazia e quem compunha
    do zero não tinha onde escrever a quantidade da ampla concorrência. A `027` nota que esse campo
    **já existe**: um Perfil novo não tem lista reservada, e a quantidade da ampla concorrência é a
    vaga imediata dele. O bloco do quadro não aparece, e a linha viaja oculta — é ela que a gravação
    preserva e que a Retificação alcança depois de publicada.
    """
    identificar(client, "ana.elaboradora", ["elaborador"])
    corpo = client.get(reverse("interface:fragmento-perfil"), {"indice": "0"}).content.decode()

    assert '<h3 id="quadro-titulo-0">Quadro de vagas</h3>' not in corpo, (
        "sem lista reservada não há repartição a pedir, e o bloco não é desenhado"
    )
    visiveis = re.findall(r'<input type="number"[^>]*name="linha-0-\d+-immediateVacancies"', corpo)
    assert visiveis == [], "não existe um segundo campo para a mesma quantidade"

    assert re.search(r'name="linha-0-0-id"\s+value="[0-9a-f-]{36}"', corpo), (
        "a linha geral viaja com identidade própria, ou a gravação seguinte a apagaria"
    )
    assert re.search(r'name="linha-0-0-modalityId"\s+value=""', corpo), "vazio é a linha geral"


def test_a_modalidade_acrescentada_traz_a_linha_do_quadro_com_a_forma_dela(
    client, seletor_ligado, composto
):
    """Achado do percurso: a linha vinha, e vinha **sem forma** (E2E25-002).

    O htmx swapa o *conteúdo* do elemento marcado com `hx-swap-oob`, e não o elemento: marcar a
    própria linha fazia os campos chegarem soltos dentro da seção, sem o `div.linha-do-quadro` que
    a desenha. O envelope existe para ser jogado fora, e o invólucro de dentro é que fica.
    """
    identificar(client, "ana.elaboradora", ["elaborador"])
    corpo = client.get(
        reverse("interface:fragmento-modalidade", args=["0"]), {"indice": "9"}
    ).content.decode()

    assert 'hx-swap-oob="beforeend:#quadro-0"' in corpo
    envelope = corpo[corpo.index("hx-swap-oob") :]
    assert '<div class="linha-do-quadro" id="quadro-de-' in envelope, (
        "o invólucro que desenha a linha vai **dentro** do envelope fora de banda, e traz o `id` "
        "pelo qual o botão da Modalidade a remove junto"
    )
    assert 'name="linha-0-9-immediateVacancies"' in envelope
    assert re.search(r'name="linha-0-9-modalityId"\s+value="[0-9a-f-]{36}"', envelope), (
        "a linha nasce apontando a Modalidade que acabou de nascer"
    )


def test_a_recusa_da_segunda_linha_geral_devolve_o_que_foi_digitado(
    client, seletor_ligado, composto
):
    """Achado do percurso: a linha duplicada **sobrescrevia** a boa na reexibição (E2E25-004).

    Quem tinha `56` na ampla concorrência e enviava uma segunda linha geral recebia de volta a
    quantidade da duplicata, e o número certo sumia — na tela que existe para mostrá-lo. A primeira
    ocorrência vence, porque é a que a pessoa vê primeiro e é a que ela estava corrigindo.
    """
    identificar(client, "ana.elaboradora", ["elaborador"])
    dados = perfil()
    # A linha da PcD perde a referência e vira uma **segunda** linha geral.
    dados["linha-0-2-modalityId"] = ""

    resposta = compor(client, composto, dados)
    assert resposta.status_code == 200, "a recusa devolve a tela, e não redireciona"

    corpo = resposta.content.decode()
    assert "uma linha só" in corpo
    quadro = secao_do_quadro(corpo)
    valores = re.findall(r'name="linha-0-\d+-immediateVacancies"\s+value="([^"]*)"', quadro)
    assert valores[0] == "56", "o número que a pessoa digitou na ampla concorrência sobrevive"

    # E a recusa aparece **ao lado da linha**, e não só no resumo (E2E25-003, FR-033).
    assert 'aria-invalid="true"' in quadro
    assert re.search(
        r'<span class="recusa" role="alert" id="recusa-linha-0-\d+-modalityId"', quadro
    )


# --- Remover a Modalidade leva a linha do quadro junto ---------------------------------------


def test_o_botao_da_modalidade_pede_a_remocao_da_linha_do_quadro_junto(
    client, seletor_ligado, composto
):
    """A linha do quadro vive noutra seção, e `closest fieldset` não a alcança.

    Sem o pedido explícito, ela ficava para trás apontando uma Modalidade que o formulário já não
    envia — e o salvamento seguinte era recusado com uma mensagem sobre uma Modalidade que a pessoa
    acabara de remover e que não aparecia mais em lugar nenhum.
    """
    identificar(client, "ana.elaboradora", ["elaborador"])
    corpo = tela(client, composto)

    pcd = _id("2510", sub=2)
    assert f'id="quadro-de-{pcd}"' in corpo, "a linha reservada é achável pelo id da Modalidade"
    assert f"?junto=quadro-de-{pcd}" in corpo, "e o botão da Modalidade pede a remoção dela junto"
    # **Os dois atributos dizem o mesmo alvo, e o teste não deixa que se afastem.** `junto=` manda
    # o servidor apagar; `data-junto` manda `remocao.js` **contar** aquela quantidade antes de
    # perguntar. Se um mudasse sem o outro, a confirmação subcontaria a perda — e, na Modalidade
    # recém-criada em que só a quantidade foi digitada, deixaria de perguntar (FR-038).
    assert f'data-junto="quadro-de-{pcd}"' in corpo
    assert corpo.count(f"?junto=quadro-de-{pcd}") == corpo.count(f'data-junto="quadro-de-{pcd}"')

    # A linha geral não recebe `id`: não há botão que a remova, porque ela não é de Modalidade
    # nenhuma. Só as três reservadas são endereçáveis assim.
    assert corpo.count('class="linha-do-quadro" id="quadro-de-') == 3


def test_o_fragmento_de_remocao_devolve_o_pedido_de_apagar_o_outro_elemento(client, seletor_ligado):
    identificar(client, "ana.elaboradora", ["elaborador"])
    alvo = f"quadro-de-{_id('2510', sub=2)}"

    resposta = client.get(reverse("interface:fragmento-remover"), {"junto": alvo})

    assert resposta.status_code == 200
    corpo = resposta.content.decode()
    assert f'id="{alvo}"' in corpo
    assert 'hx-swap-oob="delete"' in corpo


def test_sem_o_parametro_o_fragmento_de_remocao_continua_devolvendo_o_vazio(client, seletor_ligado):
    """As demais linhas do assistente não mudaram: o pedido é opcional."""
    identificar(client, "ana.elaboradora", ["elaborador"])

    resposta = client.get(reverse("interface:fragmento-remover"))

    assert resposta.status_code == 200
    assert resposta.content == b""


def test_o_alvo_da_remocao_junto_nao_aceita_marcacao(client, seletor_ligado):
    """O valor é escrito num atributo `id`; só sai daqui um seletor plausível."""
    identificar(client, "ana.elaboradora", ["elaborador"])

    resposta = client.get(
        reverse("interface:fragmento-remover"), {"junto": '"><script>alert(1)</script>'}
    )

    assert resposta.status_code == 404


# --- 027 · uma declaração só, e o bloco que aparece quando há repartição ----------------------


def _do_quadro(edital):
    """Os achados impeditivos **do quadro** no conteúdo que a submissão congelaria.

    A conferência da soma é achado da operação de publicar, e não da gravação do rascunho (`025`):
    quem compõe pode estar no meio do trabalho, e recusar a cada POST prenderia o rascunho pela
    metade. É por aqui que a tela monta as pendências da etapa 9.
    """
    edital.refresh_from_db()
    achados = blocking_findings(validate_for_publication(edital_snapshot(edital)))
    return [item for item in achados if item.code.startswith("vacancy_")]


def perfil_simples(indice=0, total="2"):
    """Um Perfil sem Modalidade nenhuma — o caso mais comum, e o que produzia o achado.

    Sem lista reservada não há repartição a pedir: a quantidade da ampla concorrência é a vaga
    imediata do Perfil, e é ela que a gravação materializa na linha geral.
    """
    return {
        f"perfil-{indice}-id": _id("2500", indice=indice),
        f"perfil-{indice}-code": f"C{indice + 1}",
        f"perfil-{indice}-name": f"Curso {indice + 1}",
        f"perfil-{indice}-immediateVacancies": total,
        f"perfil-{indice}-reserveType": "NONE",
    }


def test_o_perfil_sem_lista_reservada_nao_desenha_o_bloco_nem_um_segundo_campo(
    client, seletor_ligado, edital
):
    """FR-316 e UX-040: o cartão deixa de ter dois campos numéricos para a mesma quantidade.

    Era daqui que o achado saía. Quem preenchia "Vagas imediatas" — o campo com rótulo em português
    corrente — e deixava "Quadro de vagas › Ampla concorrência" em branco publicava um Edital que
    dizia "2 vagas imediatas" e não tinha quantidade alguma a apurar. O segundo campo não existe
    mais enquanto não houver o que repartir.
    """
    identificar(client, "ana.elaboradora", ["elaborador"])
    assert compor(client, edital, perfil_simples()).status_code == 302

    corpo = tela(client, edital)
    assert '<h3 id="quadro-titulo-0">Quadro de vagas</h3>' not in corpo
    visiveis = re.findall(r'<input type="number"[^>]*name="linha-0-\d+-immediateVacancies"', corpo)
    assert visiveis == [], "não há segundo campo para a mesma quantidade"


def test_a_linha_geral_e_gravada_com_o_total_sem_que_ninguem_a_digite(
    client, seletor_ligado, edital
):
    """FR-318: a linha geral é a projeção do total, e a projeção tem uma direção só."""
    identificar(client, "ana.elaboradora", ["elaborador"])
    compor(client, edital, perfil_simples(total="2"))

    linha = LinhaDoQuadroDeVagas.objects.get()
    assert linha.modalidade_id is None
    assert linha.vagas_imediatas == 2
    assert PerfilVaga.objects.get().immediate_vacancies == 2, "o total continua declarado"


def test_alterar_o_total_reafirma_a_linha_e_a_identidade_dela_nao_muda(
    client, seletor_ligado, edital
):
    """FR-320 e FR-322, e a travessia que já custou quantidade publicável neste repositório.

    A identidade tem de atravessar a gravação: `replace_draft` apaga e recria o rascunho inteiro, e
    uma linha que ganhasse identidade nova a cada POST ficaria inalcançável pela Retificação depois
    de publicada — e o resumo canônico mudaria sem o conteúdo mudar.
    """
    identificar(client, "ana.elaboradora", ["elaborador"])
    compor(client, edital, perfil_simples(total="2"))
    identidade = LinhaDoQuadroDeVagas.objects.get().id

    compor(client, edital, perfil_simples(total="9"))

    linha = LinhaDoQuadroDeVagas.objects.get()
    assert linha.vagas_imediatas == 9
    assert linha.id == identidade


def test_o_bloco_aparece_com_a_primeira_lista_reservada_e_explica_por_que(
    client, seletor_ligado, composto
):
    """FR-321 e UX-041: o bloco chega com a repartição a pedir, e diz por que chegou.

    A frase é **impressa**, e não `.oculto`. A microcópia invisível a quem enxerga é metade da
    causa do achado que esta feature fecha: quem acrescenta a primeira Modalidade precisa entender,
    sem procurar, que o total deixou de ser só da ampla concorrência.
    """
    identificar(client, "ana.elaboradora", ["elaborador"])
    corpo = tela(client, composto)

    assert '<h3 id="quadro-titulo-0">Quadro de vagas</h3>' in corpo
    quadro = secao_do_quadro(corpo)
    # Conferida por trecho que não atravessa a dobra do template: a quebra de linha do HTML é
    # apresentação, e prender o teste a ela quebraria na primeira reformatação.
    assert "Este Perfil declara lista reservada" in quadro
    assert '<p class="explicacao">' in quadro, "impressa, e não `.oculto`"


def test_o_fragmento_da_primeira_modalidade_entrega_a_secao_inteira(client, seletor_ligado, edital):
    """A armadilha 3, e ela não falha em execução: falha em silêncio (027, FR-321).

    Com o bloco condicionado, `#linhas-do-quadro-0` não existe enquanto não há lista reservada. Um
    fragmento que mandasse só a linha para lá não acharia destino, o `hx-swap-oob` **não erraria**,
    e a linha se perderia — invisível a qualquer teste que só confira status 200.
    """
    identificar(client, "ana.elaboradora", ["elaborador"])
    compor(client, edital, perfil_simples(total="2"))

    fragmento = client.get(
        reverse("interface:fragmento-modalidade", args=[0]),
        {"indice": "7", "perfil-0-immediateVacancies": "2"},
    ).content.decode()

    assert 'hx-swap-oob="beforeend:#quadro-0"' in fragmento, "a seção vai para a âncora"
    assert '<h3 id="quadro-titulo-0">Quadro de vagas</h3>' in fragmento
    assert 'id="linhas-do-quadro-0"' in fragmento, "e traz o destino das linhas seguintes"
    quantidades = re.findall(r'name="linha-0-\d+-immediateVacancies"\s+value="([^"]*)"', fragmento)
    assert "2" in quantidades, "a linha geral chega preenchida com o total que está na tela"


def test_o_fragmento_da_segunda_modalidade_entrega_so_a_linha(client, seletor_ligado, composto):
    """E a outra metade: com a seção já desenhada, mandar outra seria desenhá-la duas vezes."""
    identificar(client, "ana.elaboradora", ["elaborador"])
    fragmento = client.get(
        reverse("interface:fragmento-modalidade", args=[0]),
        {
            "indice": "7",
            "modalidade-0-0-id": _id("2510", sub=1),
            "perfil-0-generalCompetitionModalityId": "",
        },
    ).content.decode()

    assert 'hx-swap-oob="beforeend:#linhas-do-quadro-0"' in fragmento
    assert "<h3" not in fragmento, "a seção já está na página"


def test_remover_a_ultima_lista_reservada_diz_que_a_ampla_voltou_a_ser_o_total(
    client, seletor_ligado, composto
):
    """FR-322: a derivação reafirma a linha geral, e a tela conta que reafirmou.

    O Perfil tinha três Modalidades e a ampla repartida em 56 de 80. Removidas todas, não há mais
    repartição: a ampla concorrência volta a ser as 80 vagas imediatas. A derivação está certa —
    com uma lista de concorrência só, os dois são o mesmo número —, mas sobrescrever em silêncio
    seria trocar um defeito por outro.
    """
    identificar(client, "ana.elaboradora", ["elaborador"])
    # Saem as Modalidades **e** as linhas reservadas: é o que a tela envia depois de removê-las.
    # Uma linha que ficasse para trás apontaria Modalidade que o Perfil não tem mais, e a recusa
    # seria outra — correta, e não a que este teste exercita.
    sem_modalidades = {
        chave: valor
        for chave, valor in perfil().items()
        if not chave.startswith("modalidade-") and not re.match(r"linha-0-[123]-", chave)
    }
    # A linha geral continua viajando com o número **antigo**, como o formulário a devolveria.
    resposta = compor(client, composto, sem_modalidades)
    assert resposta.status_code == 302

    corpo = client.get(resposta["Location"]).content.decode()
    assert "não declara mais lista reservada" in corpo
    assert "80 vaga(s) imediata(s)" in corpo
    assert LinhaDoQuadroDeVagas.objects.get().vagas_imediatas == 80


def test_reafirmar_o_mesmo_numero_nao_vira_noticia(client, seletor_ligado, edital):
    """Reafirmar 2 sobre 2 não é notícia: o aviso existe para a mudança, e não para a gravação."""
    identificar(client, "ana.elaboradora", ["elaborador"])
    compor(client, edital, perfil_simples(total="2"))
    resposta = compor(client, edital, perfil_simples(total="2"))

    corpo = client.get(resposta["Location"]).content.decode()
    assert "não declara mais lista reservada" not in corpo


def test_a7_a_soma_que_excede_o_total_e_recusada_em_numeros(client, seletor_ligado, edital):
    """`A7`: repartir mais do que o Perfil oferece é recusado, e a recusa diz os três números.

    Nenhum Edital reserva mais vagas do que oferece, e essa metade da conferência não espera pela
    completude (`025`, FR-177). Dizer "há um erro no quadro" mandaria quem compõe procurar; dizer
    "soma 3, declara 2, excesso de 1" resolve na primeira leitura (UX-023).
    """
    identificar(client, "ana.elaboradora", ["elaborador"])

    # **A gravação aceita, e a submissão recusa**, e a assimetria é da `025`: quem compõe pode estar
    # no meio do trabalho, e recusar a cada POST prenderia o rascunho pela metade. A conferência da
    # soma é achado da operação de publicar, porque precisa valer igualmente sobre o conteúdo que
    # uma Retificação produziria.
    assert compor(client, edital, perfil(total="2", quantidades=("2", "0", "1"))).status_code == 302

    excesso = [item for item in _do_quadro(edital) if item.code == "vacancy_sum_exceeds_total"]
    assert excesso, "somar mais do que o Perfil oferece não é legítimo em quadro algum"
    assert "soma 3" in excesso[0].message
    assert "2 vagas imediatas" in excesso[0].message
    assert "excesso de 1" in excesso[0].message


def test_a8_corrigida_a_reparticao_o_quadro_fecha_e_grava(client, seletor_ligado, edital):
    """`A8`: a mesma tela, com a ampla reduzida, passa — e as três linhas ficam gravadas."""
    identificar(client, "ana.elaboradora", ["elaborador"])

    assert compor(client, edital, perfil(total="2", quantidades=("1", "0", "1"))).status_code == 302

    gravadas = {
        (linha.modalidade.code if linha.modalidade else None): linha.vagas_imediatas
        for linha in LinhaDoQuadroDeVagas.objects.select_related("modalidade")
    }
    assert gravadas == {None: 1, "PCD": 0, "PPI": 1}
    assert sum(gravadas.values()) == PerfilVaga.objects.get().immediate_vacancies


def test_a_igualdade_roda_no_edital_com_ampla_declarada(client, seletor_ligado, edital):
    """A lacuna `R-006` da `025`, fechada — e provada **pela tela**, e não só em unidade.

    O Edital do formato mais comum declara uma Modalidade chamada "Ampla concorrência". Enquanto a
    completude a contava, ela ficava sem linha — por norma, porque a quantidade dela mora na linha
    geral — e o quadro nunca era completo: a igualdade da FR-161 **nunca rodava** justamente no
    Edital que o acervo tem. Declarada qual é a ampla, ela roda.
    """
    identificar(client, "ana.elaboradora", ["elaborador"])
    ampla = _id("2510", sub=1)
    dados = perfil(
        total="80",
        quantidades=("56", "4", "20"),
        **{"perfil-0-generalCompetitionModalityId": ampla},
    )
    # 56 + 4 + 20 = 80 na leitura antiga; com a AC apontada, a linha dela não conta — e a soma
    # verdadeira do quadro é 56 + 4 + 20 mesmo, porque a linha da AC vai em branco.
    dados["linha-0-1-immediateVacancies"] = ""

    assert compor(client, edital, dados).status_code == 302
    # Só os achados do quadro: este Edital ainda não tem Cronograma, e o `schedule_required` não
    # é o que este cenário está conferindo.
    assert _do_quadro(edital) == [], "quadro completo que fecha não produz achado"

    assert (
        compor(client, edital, {**dados, "linha-0-3-immediateVacancies": "19"}).status_code == 302
    )
    edital.refresh_from_db()
    achados = _do_quadro(edital)
    assert [item.code for item in achados] == ["vacancy_sum_mismatch"], (
        "com a ampla apontada, o quadro fica completo e a igualdade finalmente confere"
    )
    assert "diferença de 1" in achados[0].message


# --- 027 · a ampla declarada não recebe caixa (FR-317, e a `025` D-004 antes dela) -------------


def test_a_modalidade_declarada_como_ampla_nao_ganha_caixa_propria(client, seletor_ligado, edital):
    """O segundo campo para o mesmo número, voltando pela porta dos fundos.

    A Modalidade apontada como ampla concorrência **não** recebe linha: a quantidade dela mora na
    geral, e a publicação recusa quem lhe der uma (`general_competition_modality_with_row`).
    Oferecer a caixa era oferecer um campo cujo preenchimento o sistema depois recusa — e, no
    Perfil que declara cota, era de novo pedir a mesma quantidade duas vezes.
    """
    identificar(client, "ana.elaboradora", ["elaborador"])
    ampla = _id("2510", sub=1)
    dados = perfil(**{"perfil-0-generalCompetitionModalityId": ampla})
    dados["linha-0-1-immediateVacancies"] = ""
    assert compor(client, edital, dados).status_code == 302

    quadro = secao_do_quadro(tela(client, edital))
    editaveis = re.findall(r'<input type="(?!hidden)[^"]*"[^>]*name="(linha-[^"]+)"', quadro)
    assert len(editaveis) == 3, (
        "a geral e as duas reservadas; a AC apontada como ampla não tem linha própria"
    )
    assert "Ampla concorrência (AC)" not in quadro, "o rótulo da linha da AC não é desenhado"
    assert "Pessoa com deficiência (PCD)" in quadro
    assert "Pretos, pardos e indígenas (PPI)" in quadro


def test_perfil_que_so_declara_a_ampla_nao_mostra_campo_de_quadro_nenhum(
    client, seletor_ligado, edital
):
    """O caso que a auditoria encontraria primeiro: o Edital sem cota nenhuma.

    Declarada a AC como a da ampla, não há lista reservada — e portanto nem bloco, nem caixa. A
    quantidade foi digitada uma vez, em "Vagas imediatas", e é ela que a apuração usa.

    Antes desta correção a caixa da AC aparecia **fora** do bloco condicionado, solta no cartão e
    sem título nenhum acima dela.
    """
    identificar(client, "ana.elaboradora", ["elaborador"])
    ampla = _id("2510", sub=1)
    dados = {
        f"perfil-0-{campo}": valor
        for campo, valor in (
            ("id", _id("2500")),
            ("code", "C1"),
            ("name", "Curso 1"),
            ("immediateVacancies", "2"),
            ("reserveType", "NONE"),
            ("generalCompetitionModalityId", ampla),
        )
    }
    dados.update(
        {
            "modalidade-0-0-id": ampla,
            "modalidade-0-0-code": "AC",
            "modalidade-0-0-name": "Ampla concorrência",
        }
    )
    assert compor(client, edital, dados).status_code == 302

    corpo = tela(client, edital)
    assert '<h3 id="quadro-titulo-0">Quadro de vagas</h3>' not in corpo
    visiveis = re.findall(r'<input type="number"[^>]*name="linha-0-\d+-immediateVacancies"', corpo)
    assert visiveis == [], "nenhuma caixa de quadro: a quantidade é a de Vagas imediatas"
    assert LinhaDoQuadroDeVagas.objects.get().vagas_imediatas == 2


def test_avancar_mostra_a_noticia_da_rederivacao_na_etapa_seguinte(
    client, seletor_ligado, composto
):
    """FR-322 pelo caminho que quem compõe usa: "Avançar", e não "Salvar rascunho".

    O aviso é notícia do que a gravação **acabou** de fazer. Preso à etapa dos Perfis, ele não
    aparecia para quem avança — e ficava guardado na sessão para surgir numa visita futura, já
    obsoleto, falando de uma gravação que ninguém lembra.
    """
    identificar(client, "ana.elaboradora", ["elaborador"])
    sem_modalidades = {
        chave: valor
        for chave, valor in perfil().items()
        if not chave.startswith("modalidade-") and not re.match(r"linha-0-[123]-", chave)
    }

    resposta = compor(client, composto, {**sem_modalidades, "destino": "cronograma"})

    assert resposta.status_code == 302
    assert resposta["Location"].endswith("/compor/cronograma?salvo=perfis")
    corpo = client.get(resposta["Location"]).content.decode()
    assert "não declara mais lista reservada" in corpo, "quem avança também precisa saber"


def test_a_noticia_nao_sobrevive_para_uma_visita_futura(client, seletor_ligado, composto):
    """E o outro lado: consumida uma vez, ela some. Aviso guardado é aviso que envelhece."""
    identificar(client, "ana.elaboradora", ["elaborador"])
    sem_modalidades = {
        chave: valor
        for chave, valor in perfil().items()
        if not chave.startswith("modalidade-") and not re.match(r"linha-0-[123]-", chave)
    }
    resposta = compor(client, composto, {**sem_modalidades, "destino": "cronograma"})
    client.get(resposta["Location"])

    depois = tela(client, composto)
    assert "não declara mais lista reservada" not in depois


# --- 027 · o quadro reage ao seletor da ampla **durante a edição** (FR-317, FR-321) ------------


def campos_do_perfil(**ajustes):
    """O Perfil como o formulário o envia, pronto para ir no `hx-include` do seletor."""
    return {**perfil(), **ajustes}


def pedir_quadro(client, dados):
    return client.get(reverse("interface:fragmento-quadro", args=[0]), dados).content.decode()


def test_apontar_a_ampla_tira_a_caixa_dela_sem_precisar_salvar(client, seletor_ligado, edital):
    """O caminho que o servidor consertava tarde demais.

    A correção da montagem do formulário só valia na renderização seguinte: escolher a Modalidade
    no seletor deixava a caixa dela na tela até a próxima gravação — e quem digitasse nela levava
    recusa na submissão, porque a quantidade da ampla mora na linha geral.
    """
    identificar(client, "ana.elaboradora", ["elaborador"])
    ampla = _id("2510", sub=1)

    antes = pedir_quadro(client, campos_do_perfil())
    assert "Ampla concorrência (AC)" in antes, "sem apontamento, a AC é lista reservada como outra"

    depois = pedir_quadro(
        client, campos_do_perfil(**{"perfil-0-generalCompetitionModalityId": ampla})
    )
    assert "Ampla concorrência (AC)" not in depois, "apontada, ela deixa de ter caixa na hora"
    assert "Pessoa com deficiência (PCD)" in depois
    assert "Pretos, pardos e indígenas (PPI)" in depois


def test_apontar_a_unica_modalidade_faz_o_bloco_sumir_na_hora(client, seletor_ligado, edital):
    """E o terceiro sintoma: o bloco que já não tem o que pedir continuava na tela."""
    identificar(client, "ana.elaboradora", ["elaborador"])
    ampla = _id("2510", sub=1)
    so_a_ac = {
        "perfil-0-id": _id("2500"),
        "perfil-0-code": "C1",
        "perfil-0-name": "Curso 1",
        "perfil-0-immediateVacancies": "2",
        "perfil-0-reserveType": "NONE",
        "modalidade-0-0-id": ampla,
        "modalidade-0-0-code": "AC",
        "modalidade-0-0-name": "Ampla concorrência",
    }

    com_bloco = pedir_quadro(client, so_a_ac)
    assert '<h3 id="quadro-titulo-0">Quadro de vagas</h3>' in com_bloco

    sem_bloco = pedir_quadro(client, {**so_a_ac, "perfil-0-generalCompetitionModalityId": ampla})
    assert '<h3 id="quadro-titulo-0">Quadro de vagas</h3>' not in sem_bloco
    visiveis = re.findall(
        r'<input type="number"[^>]*name="linha-0-\d+-immediateVacancies"', sem_bloco
    )
    assert visiveis == [], "sem lista reservada não há caixa nenhuma"
    assert 'name="linha-0-0-id"' in sem_bloco, "a linha geral continua viajando, oculta"


def test_voltar_para_nenhuma_devolve_a_caixa_da_modalidade(client, seletor_ligado, edital):
    """A troca vale nos dois sentidos: desfeito o apontamento, a Modalidade volta a contar."""
    identificar(client, "ana.elaboradora", ["elaborador"])
    ampla = _id("2510", sub=1)

    pedir_quadro(client, campos_do_perfil(**{"perfil-0-generalCompetitionModalityId": ampla}))
    voltou = pedir_quadro(client, campos_do_perfil(**{"perfil-0-generalCompetitionModalityId": ""}))

    assert "Ampla concorrência (AC)" in voltou


def test_o_que_ja_estava_digitado_sobrevive_a_troca(client, seletor_ligado, edital):
    """A reconstrução lê o formulário, e não o banco: quantidade digitada e ainda não salva fica."""
    identificar(client, "ana.elaboradora", ["elaborador"])
    dados = campos_do_perfil(
        **{"perfil-0-generalCompetitionModalityId": _id("2510", sub=1)},
    )
    dados["linha-0-3-immediateVacancies"] = "17"

    corpo = pedir_quadro(client, dados)

    assert 'value="17"' in corpo, "o número digitado na PPI atravessa a troca"


def test_perfil_que_o_formulario_nao_traz_nao_troca_nada(client, seletor_ligado, edital):
    """Pedido que não casa com Perfil algum deixa a tela como está.

    `ler_perfis` é tolerante com o meio do preenchimento — um Perfil só com identidade produz o
    estado sem bloco, que é o certo, porque ele ainda não tem lista reservada. O que não pode
    acontecer é o fragmento montar um quadro para um Perfil que não está no envio: aí a resposta é
    204, e o htmx não troca nada.
    """
    identificar(client, "ana.elaboradora", ["elaborador"])

    resposta = client.get(
        reverse("interface:fragmento-quadro", args=[0]), {"perfil-3-id": _id("2500", indice=3)}
    )

    assert resposta.status_code == 204, "204 faz o htmx deixar a tela como está"
    assert resposta.content == b""


def test_perfil_no_meio_do_preenchimento_devolve_o_estado_sem_bloco(client, seletor_ligado, edital):
    """E o caso tolerado: sem Modalidade nenhuma não há lista reservada, e portanto não há bloco."""
    identificar(client, "ana.elaboradora", ["elaborador"])

    corpo = pedir_quadro(client, {"perfil-0-id": _id("2500")})

    assert '<h3 id="quadro-titulo-0">Quadro de vagas</h3>' not in corpo
    assert 'name="linha-0-0-id"' in corpo, "a linha geral viaja desde o primeiro instante"


def test_o_seletor_declara_a_reacao_no_html(client, seletor_ligado, composto):
    """A reação é do servidor, por `hx-get` — sem `js:{...}`, que a CSP desta tela proíbe."""
    identificar(client, "ana.elaboradora", ["elaborador"])
    corpo = tela(client, composto)

    seletor = corpo[corpo.index('id="perfil-0-generalCompetitionModalityId"') :][:600]
    assert 'hx-trigger="change"' in seletor
    assert 'hx-target="#quadro-0"' in seletor
    assert "hx-include=" in seletor
    assert "js:" not in seletor


# --- A composição que se explica (030, FR-417) ----------------------------------------------


def perfil_sem_modalidade(indice=0):
    """O Perfil do Edital canônico: três vagas, nenhuma Modalidade declarada."""
    return {
        f"perfil-{indice}-id": _id("2500", indice=indice),
        f"perfil-{indice}-code": f"C{indice + 1}",
        f"perfil-{indice}-name": f"Curso {indice + 1}",
        f"perfil-{indice}-immediateVacancies": "3",
        f"perfil-{indice}-reserveType": "NONE",
    }


def test_sem_modalidade_a_tela_nao_pergunta_qual_e_a_ampla_nem_a_reversao(
    client, seletor_ligado, edital
):
    """FR-417 — duas perguntas cuja resposta já está dada, num Perfil sem Modalidade nenhuma.

    A da ampla concorrência ofereceria uma opção só, "nenhuma"; a da reversão fala de vaga
    reservada que não existe, e a própria ajuda dela diz que declará-la exige quadro por recorte.
    """
    identificar(client, "ana.elaboradora", ["elaborador"])
    assert compor(client, edital, perfil_sem_modalidade()).status_code == 302

    corpo = tela(client, edital)

    assert "Qual delas é a ampla concorrência" not in corpo
    assert "Reverter vaga reservada não preenchida" not in corpo
    assert 'name="perfil-0-generalCompetitionModalityId"' in corpo, (
        "o campo sai da tela, e não do envio: `replace_draft` apaga o que não voltar (FR-418)"
    )


def test_a_primeira_modalidade_faz_as_duas_perguntas_aparecerem(client, seletor_ligado, composto):
    """A outra metade: declarada a Modalidade, as perguntas passam a ser pertinentes."""
    identificar(client, "ana.elaboradora", ["elaborador"])

    corpo = tela(client, composto)

    assert "Qual delas é a ampla concorrência" in corpo
    assert "Reverter vaga reservada não preenchida" in corpo


def test_o_que_foi_declarado_sobrevive_a_remocao_da_ultima_modalidade(
    client, seletor_ligado, composto
):
    """FR-418 sobre o Perfil: esconder a pergunta não pode apagar a resposta.

    O cenário é o do caso de borda da spec, ao contrário: um Perfil que já declarou reversão e
    depois fica sem Modalidade alguma. O campo some da tela, e a declaração continua no envio.
    """
    identificar(client, "ana.elaboradora", ["elaborador"])
    assert (
        compor(
            client,
            composto,
            perfil(**{"perfil-0-vacancyReversion": "ON_EXHAUSTION"}),
        ).status_code
        == 302
    )

    # A remoção da última Modalidade, **como o navegador a envia**: os campos ocultos que a tela
    # acabou de renderizar viajam junto. É o ponto inteiro do contrato do rascunho — se o teste
    # postasse sem eles, estaria simulando um formulário que esta feature não produz.
    assert (
        compor(
            client,
            composto,
            {
                **perfil_sem_modalidade(),
                "perfil-0-vacancyReversion": "ON_EXHAUSTION",
                "perfil-0-generalCompetitionModalityId": "",
            },
        ).status_code
        == 302
    )
    corpo = tela(client, composto)

    assert "Reverter vaga reservada não preenchida" not in corpo
    assert 'name="perfil-0-vacancyReversion" value="ON_EXHAUSTION"' in corpo
    assert PerfilVaga.objects.get(pk=PERFIL).especie_de_reversao == "ON_EXHAUSTION"
