"""A página da supervisão: o que ela apresenta, o que ela recusa apresentar, e para onde encaminha.

Os testes de derivação vivem em `tests/integration/supervisao/`; aqui ficam os que só existem no
canal — a região anunciada, o equivalente textual da série, e as proibições de apresentação.
"""

import re

import pytest
from django.urls import reverse

from tests.fixtures.edital import identificador
from tests.fixtures.supervisao import rascunhar, submeter
from tests.interface.conftest import identificar

pytestmark = [pytest.mark.django_db, pytest.mark.integration]


def url(processo):
    return reverse("interface:supervisao", args=[processo.id])


def abrir(client, processo, subject="maria", papeis=()):
    identificar(client, subject, list(papeis))
    resposta = client.get(url(processo))
    assert resposta.status_code == 200, resposta.content
    return resposta.content.decode()


def regiao(corpo, ancora):
    """O trecho de uma das duas regiões, delimitado pelo `<section>` que a anuncia.

    Procurar no documento inteiro faria uma asserção sobre o Pulso passar ou falhar por causa de
    algo escrito na Atenção — e as duas regiões existem justamente porque são coisas diferentes.

    O fechamento é contado, e não procurado: a região do Pulso tem um bloco por Edital, e um
    recorte que parasse no primeiro `</section>` devolveria o cabeçalho e mais nada — passando
    silenciosamente em toda asserção de ausência.
    """
    abertura = re.search(rf'<section[^>]*aria-labelledby="{ancora}"[^>]*>', corpo)
    assert abertura is not None, f"a região {ancora} não foi anunciada como região"
    profundidade, posicao = 0, abertura.start()
    for marca in re.finditer(r"<section\b|</section>", corpo[abertura.start() :]):
        profundidade += 1 if marca.group(0) != "</section>" else -1
        if profundidade == 0:
            return corpo[posicao : posicao + marca.end()]
    raise AssertionError(f"a região {ancora} não foi fechada")


def texto(trecho):
    """O que a região **apresenta**, sem marcação.

    A asserção de "nenhum percentual" precisa disto: a altura de uma barra é `style="height:40%"`,
    e um `%` dentro de atributo é unidade de desenho, não informação. Procurar no HTML cru faria o
    teste falhar por causa da folha de estilo e passar quando o número aparecesse escrito.
    """
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", trecho))


def sem_espacos(trecho):
    """O trecho sem espaço em branco algum — para comparar marcação sem depender de indentação."""
    return re.sub(r"\s+", "", trecho)


def test_as_duas_regioes_sao_anunciadas_com_titulo_proprio(
    client, seletor_ligado, processo_a, edital_a, edital_c, comissao_de_a
):
    """`UX-006`: quem navega por marcos salta de uma para a outra sem varrer a página."""
    corpo = abrir(client, processo_a)

    assert 'id="pulso-titulo"' in corpo
    assert 'id="atencao-titulo"' in corpo


def test_nenhum_percentual_e_apresentado_sobre_inscricao(
    client, seletor_ligado, processo_a, edital_a, edital_c, comissao_de_a
):
    """`FR-017` e `SC-005`: não há denominador normativo para inscrição.

    Um percentual de avanço aqui responderia "quanto falta" a uma pergunta que ninguém pode
    responder — não existe o número de inscrições que o Edital espera receber.
    """
    submeter(edital_a, 7)
    rascunhar(edital_a, 2)
    # Com submissões no Edital que tem período, a série é desenhada — e é justamente aí que um `%`
    # aparece na marcação, como altura de barra. O que a região não pode é **apresentar** um.
    submeter(edital_c, 3, seed=2)

    corpo = abrir(client, processo_a)

    pulso = regiao(corpo, "pulso-titulo")
    assert "barra" in pulso, "sem série desenhada o teste não exercita o caso que ele protege"
    assert "%" not in texto(pulso)


def test_o_pulso_nomeia_o_edital_de_cada_contagem(
    client, seletor_ligado, processo_a, edital_a, edital_c, comissao_de_a
):
    """`FR-011`, `FR-020` e `UX-007`: nenhuma linha do Edital aparece sem dizer de qual Edital é."""
    submeter(edital_a, 3)
    submeter(edital_c, 1, seed=2)

    pulso = regiao(abrir(client, processo_a), "pulso-titulo")

    assert f"{edital_a.number}/{edital_a.year}" in pulso
    assert f"{edital_c.number}/{edital_c.year}" in pulso


def test_o_rascunho_usa_o_termo_que_a_tela_de_inscricoes_ja_usa(
    client, seletor_ligado, processo_a, edital_a, edital_c, comissao_de_a
):
    """`Princípio I`: dois termos para o mesmo conceito é o que a linguagem ubíqua recusa.

    A tela da `009` chama o rascunho de **em preenchimento**. Enquanto não houver decisão de
    vocabulário que valha para as duas telas, a supervisão adota o termo vigente — e não inventa
    um segundo.
    """
    rascunhar(edital_a, 2)

    pulso = regiao(abrir(client, processo_a), "pulso-titulo")

    assert "preenchimento" in pulso.lower()


def test_a_serie_tem_equivalente_textual_com_os_mesmos_valores(
    client, seletor_ligado, processo_a, edital_a, edital_c, comissao_de_a
):
    """`FR-016`, `UX-008` e `SC-015`: o gráfico é desenho; os números vivem na tabela.

    A asserção compara **os mesmos valores** que a derivação produziu, e não uma amostra: um
    equivalente que perdesse um dia seria pior do que nenhum, porque pareceria completo.
    """
    from datetime import timedelta

    from django.utils import timezone

    from processo_seletivo.interface import supervisao as leitura

    agora = timezone.now()
    submeter(edital_c, 2, quando=agora - timedelta(days=2), seed=2)
    submeter(edital_c, 5, primeiro=40, quando=agora - timedelta(days=1), seed=2)

    corpo = abrir(client, processo_a)

    serie = next(
        item.serie for item in leitura.pulso(processo_a).por_edital if item.edital.id == edital_c.id
    )
    assert serie, "o Edital com período declarado precisa ter série"
    pulso = sem_espacos(regiao(corpo, "pulso-titulo"))
    for ponto in serie:
        linha = sem_espacos(
            f'<tr><th scope="row">{ponto.dia.strftime("%d/%m/%Y")}</th>'
            f"<td>{ponto.quantidade}</td></tr>"
        )
        assert linha in pulso, f"o dia {ponto.dia} não aparece no equivalente textual"


def test_as_barras_da_serie_nao_sao_lidas_como_conteudo(
    client, seletor_ligado, processo_a, edital_a, edital_c, comissao_de_a
):
    """`UX-008`: o desenho não pode ser anunciado duas vezes a quem ouve a tela."""
    submeter(edital_c, 1, seed=2)

    pulso = regiao(abrir(client, processo_a), "pulso-titulo")

    assert '<ul class="barras" aria-hidden="true">' in pulso


def test_a_ausencia_de_periodo_em_curso_e_declarada(
    client, seletor_ligado, processo_a, edital_a, comissao_de_a
):
    """`FR-018`: dito, e não deixado como um zero sem qualificação."""
    pulso = regiao(abrir(client, processo_a), "pulso-titulo")

    assert "Nenhum Edital com período de inscrições em curso" in texto(pulso)
    assert "últimas 24 horas" not in texto(pulso)


@pytest.fixture
def processo_limpo(gestor, api_client, manager_headers):
    """Um Processo em que nenhuma das cinco condições se verifica.

    Ele é montado do zero, e não obtido apagando o que sobra de outro: **nada é excluído** neste
    sistema, e um teste que apagasse um Edital estaria provando o contrário do que a Constituição
    garante.
    """
    from tests.fixtures.comissao import constituir
    from tests.fixtures.publicacao import publish_original
    from tests.fixtures.supervisao import etapa_ligada, rascunho_com_periodo

    edital = publish_original(
        api_client,
        {**manager_headers, "HTTP_IDEMPOTENCY_KEY": "supervisao-limpo-0001"},
        {
            "institutionalCode": "PS-2026-090",
            "title": "Processo sem condição de atenção",
            "firstEdital": {"number": "90", "year": 2026, "title": "Edital limpo"},
        },
        draft=rascunho_com_periodo(9, etapas=[etapa_ligada(9)], status_do_periodo="EM_ANDAMENTO"),
    )
    constituir(gestor, edital.processo, [("maria", "PRESIDENTE")], prefixo="limpo")
    return edital.processo


def test_sem_nenhuma_condicao_a_atencao_ocupa_uma_linha(client, seletor_ligado, processo_limpo):
    """`FR-025` e `SC-011`: a região encolhe a uma linha, e não some.

    Sumir não distinguiria *nada a sinalizar* de *a página não carregou*. E não há seção por sinal:
    cinco cabeçalhos vazios diriam cinco vezes que não há nada.
    """
    atencao = regiao(abrir(client, processo_limpo), "atencao-titulo")

    assert "Nenhuma condição de atenção" in texto(atencao)
    assert "<li" not in atencao


@pytest.mark.django_db(transaction=True)
def test_a_mensagem_de_recurso_sem_membro_desimpedido_nao_afirma_impossibilidade(
    client, seletor_ligado, gestor, api_client, manager_headers, process_payload
):
    """`UX-005` e `FR-030a`: a mensagem se limita ao impedimento verificável.

    A titularidade da permissão de julgar não é determinável pelo sistema — os papéis vêm da sessão
    e nada liga identidade a papel —, e alguém de fora da comissão pode detê-la. Dizer que o
    julgamento é impossível seria afirmar o que os dados não sustentam.
    """
    from django.utils import timezone

    from processo_seletivo.avaliacoes.models import Impedimento
    from tests.fixtures.recursos_us4 import cenario_julgavel

    peca = cenario_julgavel(
        gestor, api_client, manager_headers, process_payload, seed=131, codigo="0311"
    )
    Impedimento.objects.create(
        identity_subject="maria",
        inscricao=peca["inscricao"],
        motivo="Parentesco declarado.",
        criado_em=timezone.now(),
        criado_por="carlos",
    )

    atencao = texto(
        regiao(
            abrir(client, peca["cenario"]["processo"], papeis=["julgador"]),
            "atencao-titulo",
        )
    )

    assert "todos os membros da comissão estão impedidos" in atencao
    for proibido in ("impossível", "impossivel", "ninguém pode julgar", "não há quem julgue"):
        assert proibido not in atencao.lower()


@pytest.fixture
def edital_divergente(api_client, manager_headers, processo_a):
    """Um Edital cujo período corre e continua declarado planejado — divergência de `UX-002`."""
    from tests.fixtures.supervisao import publicar_no_processo, rascunho_com_periodo

    return publicar_no_processo(
        api_client,
        manager_headers,
        processo_a,
        number="08",
        title="Período em curso, declarado planejado",
        chave="supervisao-divergente",
        draft=rascunho_com_periodo(8, status_do_periodo="PLANEJADO"),
    )


def test_os_sinais_do_edital_conduzem_as_telas_donas(
    client, seletor_ligado, processo_a, edital_a, edital_c, edital_divergente, comissao_de_a
):
    """`FR-035`: cada sinal leva à feature dona, já no ponto em que a situação se resolve.

    Sem o encaminhamento a supervisão vira aviso sem remédio — e é dali que nasce a pressão para
    replicar a lista dentro dela, que é o que `D-009` recusa.
    """
    from tests.fixtures.supervisao import ETAPA_C1, SEGUNDO_SEED

    submeter(edital_c, 2, seed=SEGUNDO_SEED)

    atencao = regiao(abrir(client, processo_a), "atencao-titulo")

    assert reverse("interface:compor-etapa", args=[edital_a.id, "etapas"]) in atencao
    assert reverse("interface:compor-etapa", args=[edital_divergente.id, "cronograma"]) in atencao
    assert (
        reverse("interface:distribuicao", args=[edital_c.id, identificador(ETAPA_C1, SEGUNDO_SEED)])
        in atencao
    )


@pytest.mark.django_db(transaction=True)
def test_os_sinais_do_marco_e_do_recurso_conduzem_as_telas_donas(
    client, seletor_ligado, gestor, api_client, manager_headers, process_payload
):
    """A outra metade de `FR-035`: a ordenação do marco e os recursos do Edital."""
    from decimal import Decimal

    from django.utils import timezone

    from processo_seletivo.avaliacoes.models import Impedimento
    from processo_seletivo.recursos.application.julgar import julgar
    from processo_seletivo.recursos.models import DecisaoRecurso
    from processo_seletivo.resultados.models import ResultadoEtapa
    from tests.fixtures.recursos import admitir, interpor
    from tests.fixtures.recursos_us4 import cenario_julgavel, julgador

    peca = cenario_julgavel(
        gestor, api_client, manager_headers, process_payload, seed=141, codigo="0411"
    )
    cenario = peca["cenario"]
    # A segunda peça fica **pendente**, e é ela que produz `UX-005`: a primeira vai ser julgada
    # logo abaixo, e recurso julgado não aguarda julgamento nenhum.
    outra = cenario["inscricoes"][1]
    pendente = interpor(
        inscricao=outra,
        versao=peca["recurso"].versao,
        resultado=ResultadoEtapa.vigentes.get(inscricao=outra, etapa_id=cenario["etapa"]),
        protocolo="REC-2026-PENDENTE1",
    )
    admitir(pendente)
    # João concluiu a Avaliação que fundamentou o Resultado atacado; Maria recebe o impedimento
    # declarado. Com os dois membros ativos impedidos, o conjunto de desimpedidos é vazio.
    Impedimento.objects.create(
        identity_subject="maria",
        inscricao=outra,
        motivo="Parentesco declarado.",
        criado_em=timezone.now(),
        criado_por="carlos",
    )
    julgar(
        actor=julgador(),
        recurso_id=peca["recurso"].id,
        especie=DecisaoRecurso.Especie.CORRECAO_FIXADA,
        motivacao="A prova didática entregue não foi considerada.",
        etapa_id=cenario["etapa"],
        pontuacao=Decimal("82.0000"),
        assinatura_do_resultado=str(peca["superado"].id),
        idempotency_key="deferir-destinos",
    )

    atencao = regiao(abrir(client, cenario["processo"], papeis=["julgador"]), "atencao-titulo")

    assert reverse("interface:ordenacao", args=[cenario["edital"].id, cenario["marco"]]) in atencao
    assert reverse("interface:recursos", args=[cenario["edital"].id]) in atencao


def test_a_supervisao_nao_lista_os_registros_que_conta(
    client, seletor_ligado, processo_a, edital_a, edital_c, comissao_de_a
):
    """`FR-037` e `D-009`: o que a supervisão conta, a dona lista. Nunca as duas.

    E é também `FR-004a`: a página é agregada por construção, e nenhuma identificação de candidato
    aparece nela — nem nome, nem CPF, nem protocolo.
    """
    from tests.fixtures.supervisao import SEGUNDO_SEED

    inscricoes = submeter(edital_c, 3, seed=SEGUNDO_SEED)

    corpo = abrir(client, processo_a)

    for inscricao in inscricoes:
        assert inscricao.protocolo not in corpo
        assert inscricao.nome not in corpo
        assert inscricao.cpf not in corpo
        assert str(inscricao.id) not in corpo
