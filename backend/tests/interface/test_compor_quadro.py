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
    existentes = set(re.findall(r'<span class="oculto" id="(ajuda-linha-\d+-\d+)"', quadro))
    assert descritos <= existentes, "todo `aria-describedby` aponta alvo que existe"


# --- E2E25-001 · o Perfil recém-acrescentado já oferece a linha geral ------------------------


def test_o_perfil_acrescentado_pela_tela_ja_oferece_a_linha_geral(client, seletor_ligado, edital):
    """Achado do percurso conduzido: a seção do quadro nascia **vazia** no Perfil novo.

    Título e mais nada. Quem compõe um Edital do zero — que é todo Edital — não tinha onde escrever
    a quantidade da ampla concorrência até salvar e recarregar a tela, e o caminho natural da US1
    começava com um beco. As reservadas continuam nascendo com as Modalidades, uma a uma, porque é
    delas que vêm o rótulo e a identidade que a linha aponta (E2E25-001, UX-021, UX-022).
    """
    identificar(client, "ana.elaboradora", ["elaborador"])
    corpo = client.get(reverse("interface:fragmento-perfil"), {"indice": "0"}).content.decode()

    assert '<h3 id="quadro-titulo-0">Quadro de vagas</h3>' in corpo
    assert "<strong>Ampla concorrência</strong>" in corpo
    campos = re.findall(r'name="(linha-0-\d+-immediateVacancies)"', corpo)
    assert len(campos) == 1, "a geral, e só ela: não há Modalidade declarada ainda"
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
