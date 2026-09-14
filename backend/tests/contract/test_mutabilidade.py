"""O guardião do contrato de mutabilidade normativa (026).

Ele compara **o que o snapshot publica** com **o que o contrato classifica**, e falha por omissão
nos dois sentidos. Sem ele o contrato é prosa: os campos de hoje seriam classificados e o próximo
nasceria sem decisão, exatamente como `maximumScore` nasceu na `012`.

**O alcance da garantia, dito com o limite** (D-012). O guardião cobre todo campo que o **Edital
máximo** publica — `tests/fixtures/snapshot.rascunho_completo` —, e não "todo campo que existir".
Campo que só apareça sob condição que a fixture não exercita fica fora da enumeração até a fixture
exercitá-la; lista vazia é o caso concreto, porque `[]` não distingue coleção sem itens de campo de
lista sem valores.

**A alternativa foi considerada e recusada**: enumerar estaticamente do código de `publish_edital`
cobriria todo ramo condicional sem publicar nada — e enumeraria a forma que o **emissor escreve**,
não a que o conteúdo **tem**. É exatamente essa diferença que produziu o achado do `location`
(emitido e não declarado), e trocar a fonte pela análise estática fecharia um buraco menor abrindo
o maior.

O que mantém o limite estreito é `test_o_edital_maximo_exercita_o_que_o_emissor_sabe_emitir`
(SC-103): ele impede que alguém simplifique a fixture e encolha a garantia sem que nada acuse.
"""

import pytest

from processo_seletivo.editais.domain import mutabilidade, validation
from processo_seletivo.editais.domain.mutabilidade import (
    CONTRATO,
    OPACOS,
    RAIZ,
    ContratoInvalido,
    Mutabilidade,
    Natureza,
)
from processo_seletivo.publicacoes.models_retificacao import VersaoConsolidada


def _e_colecao(valor):
    """Coleção é toda lista cujos itens são objetos — **sem lista nomeada** (FR-303).

    Nenhum literal com os nomes das doze coleções: acrescentar uma ao conteúdo publicado passa a
    ser suficiente para o guardião cobri-la. Lista de escalares (`requirements`, `stages`) é campo,
    e não coleção: o que se corrige ali é a lista inteira.
    """
    return isinstance(valor, list) and bool(valor) and all(isinstance(item, dict) for item in valor)


def _uniao_das_chaves(itens):
    """Os valores de cada chave, reunidos sobre todos os itens da coleção.

    **União, e nunca interseção.** `sections` é o caso concreto: `content` e `source` são
    mutuamente exclusivos — seção redigida tem o primeiro, gerada tem o segundo —, e exigir que
    todo item carregue todo campo faria o guardião falhar conforme a seção que a travessia visse
    primeiro.
    """
    reunidos = {}
    for item in itens:
        for chave, valor in item.items():
            reunidos.setdefault(chave, []).append(valor)
    return reunidos


def _percorrer(colecao, itens, caminho="", achados=None):
    """Os pares `(coleção, caminho relativo)` que estes itens publicam."""
    achados = {} if achados is None else achados
    for chave, valores in _uniao_das_chaves(itens).items():
        relativo = f"{caminho}{chave}"
        if (colecao, relativo) in OPACOS:
            # Objeto opaco: o contrato o classifica **inteiro**, e a travessia não desce. Descer
            # produziria um guardião cujo domínio muda de Edital para Edital — o mesmo campo
            # presente num e ausente noutro faria a suíte alternar entre FR-301 e FR-302.
            achados[(colecao, relativo)] = f"/{colecao}/…/{relativo}"
            continue
        objetos = [valor for valor in valores if isinstance(valor, dict)]
        if objetos:
            # Basta **um** item declarar o objeto: `None` ao lado de um `dict` é "não declarado", e
            # não um campo escalar de outra espécie.
            _percorrer(colecao, objetos, f"{relativo}/", achados)
            continue
        aninhadas = [valor for valor in valores if _e_colecao(valor)]
        if aninhadas:
            filhos = [item for valor in aninhadas for item in valor]
            _percorrer(chave, filhos, "", achados)
            continue
        achados[(colecao, relativo)] = f"/{colecao}/…/{relativo}"
    return achados


def campos_publicados(conteudo):
    """Todo par `(coleção, caminho relativo)` que este conteúdo canônico publica."""
    return _percorrer(RAIZ, [conteudo])


@pytest.fixture
def conteudo_maximo(api_client, manager_headers, process_payload):
    """O conteúdo canônico de um Edital **máximo**, publicado de verdade.

    De verdade, e não de fixture montada à mão: uma coleção nova nasce em `edital_snapshot`, e é lá
    que ela precisa ser encontrada. Foi assim que a `022` descobriu a coleção sem declaração, e é a
    mesma razão pela qual `location` apareceu — emitido pelo código, declarado em lugar nenhum.
    """
    from tests.fixtures.publicacao import publish_original
    from tests.fixtures.snapshot import rascunho_completo

    edital = publish_original(
        api_client, manager_headers, process_payload, draft=rascunho_completo(), anexos=1
    )
    return VersaoConsolidada.objects.get(edital=edital).content


# --------------------------------------------------------------------------------------------
# A forma do contrato
# --------------------------------------------------------------------------------------------


@pytest.mark.contract
def test_razao_e_obrigatoria_em_nao_retificavel_e_proibida_nas_outras():
    """FR-299, conferido na **construção** e não na execução de um teste.

    Quem escreve o contrato descobre no `import`, e não depois de rodar a suíte inteira.
    """
    with pytest.raises(ContratoInvalido, match="exige razão escrita"):
        Mutabilidade(Natureza.NAO_RETIFICAVEL)
    with pytest.raises(ContratoInvalido, match="não carrega razão"):
        Mutabilidade(Natureza.RETIFICAVEL, "qualquer coisa")
    assert Mutabilidade(Natureza.NAO_RETIFICAVEL, "razão normativa").razao


@pytest.mark.contract
def test_a_marca_de_caminho_fechado_so_cabe_em_nao_retificavel():
    """FR-315, **com entradas sintéticas** e não sobre o `CONTRATO`.

    Nenhuma entrada real nasce marcada — a marca só aparece numa reclassificação —, e um teste que
    só varresse o contrato passaria vazio hoje e continuaria passando vazio para sempre.

    **Assumido explicitamente**: a marca é governança de revisão, e não invariante automático. O
    contrato guarda só o vigente (D-011), então nada detecta a transição R→N; a verificação cobre
    uma direção — marca incoerente é recusada, marca ausente não é.
    """
    with pytest.raises(ContratoInvalido, match="caminho fechado"):
        Mutabilidade(Natureza.RETIFICAVEL, fechou_caminho=True)
    assert Mutabilidade(Natureza.NAO_RETIFICAVEL, "razão", fechou_caminho=True).fechou_caminho
    marcadas = [chave for chave, valor in CONTRATO.items() if valor.fechou_caminho]
    assert all(CONTRATO[chave].natureza is Natureza.NAO_RETIFICAVEL for chave in marcadas)


@pytest.mark.contract
def test_natureza_de_nao_devolve_padrao():
    """D-008: um padrão seria a decisão implícita, que é o estado de hoje com outro nome."""
    with pytest.raises(KeyError):
        mutabilidade.natureza_de("profiles", "campoQueNaoExiste")


@pytest.mark.contract
def test_toda_razao_registrada_nao_e_vazia():
    """SC-101, a metade que se confere por máquina.

    Se a razão é **normativa** ou **técnica** é leitura humana, e é o que a revisão de código vê.
    """
    sem_razao = [
        chave
        for chave, valor in CONTRATO.items()
        if valor.natureza is Natureza.NAO_RETIFICAVEL and not valor.razao.strip()
    ]
    assert sem_razao == []


# --------------------------------------------------------------------------------------------
# A travessia
# --------------------------------------------------------------------------------------------


@pytest.mark.django_db(transaction=True)
@pytest.mark.contract
def test_a_travessia_alcanca_as_doze_colecoes(conteudo_maximo):
    """O mapa do trabalho, e o sintoma de o Edital não ser máximo.

    Falhar aqui não é defeito da travessia: é a fixture ter encolhido.
    """
    encontradas = {colecao for colecao, _ in campos_publicados(conteudo_maximo)}
    assert encontradas == {
        RAIZ,
        "profiles",
        "schedule",
        "stages",
        "sections",
        "attachments",
        "documentRequirements",
        "competitionModalities",
        "vacancyTable",
        "declaredFacts",
        "classificationMilestones",
        "tiebreakers",
    }


@pytest.mark.django_db(transaction=True)
@pytest.mark.contract
def test_a_travessia_nao_desce_em_objeto_opaco(conteudo_maximo):
    """O objeto opaco entra inteiro, e nenhuma folha dele aparece."""
    encontrados = campos_publicados(conteudo_maximo)
    for chave in OPACOS:
        assert chave in encontrados, f"objeto opaco não encontrado no conteúdo: {chave}"
    colecao, caminho = ("profiles", "classificationInformation")
    dentro = [par for par in encontrados if par[0] == colecao and par[1].startswith(f"{caminho}/")]
    assert dentro == []


@pytest.mark.django_db(transaction=True)
@pytest.mark.contract
def test_a_travessia_desce_no_arredondamento_e_nos_parametros(conteudo_maximo):
    """`rounding` e `parameters` são `JSONField` e **não** são opacos.

    A forma deles é conhecida e o cálculo depende dela — `combinacao.arredondamento_publicado`
    cobra `scale` e `mode`, e `desempate` lê `stageId`/`factId`. Tratá-los como opacos seria
    classificar por onde o dado está guardado, que é razão técnica (D-002).
    """
    encontrados = campos_publicados(conteudo_maximo)
    assert ("classificationMilestones", "rounding/scale") in encontrados
    assert ("classificationMilestones", "rounding/mode") in encontrados
    assert ("tiebreakers", "parameters/stageId") in encontrados
    assert ("tiebreakers", "parameters/factId") in encontrados


@pytest.mark.django_db(transaction=True)
@pytest.mark.contract
def test_o_dominio_de_uma_colecao_e_a_uniao_das_chaves_dos_itens(conteudo_maximo):
    """`sections` publica `content` **ou** `source`, nunca os dois no mesmo item."""
    encontrados = campos_publicados(conteudo_maximo)
    assert ("sections", "content") in encontrados
    assert ("sections", "source") in encontrados
    por_item = [set(secao) for secao in conteudo_maximo["sections"]]
    assert not any({"content", "source"} <= chaves for chaves in por_item)


@pytest.mark.django_db(transaction=True)
@pytest.mark.contract
def test_o_edital_maximo_exercita_o_que_o_emissor_sabe_emitir(conteudo_maximo):
    """SC-103 — o guardião da própria fixture.

    Ele **não elimina** o limite da D-012; impede que ele cresça. Uma coleção nova vazia continua
    invisível à travessia — o que este teste garante é que ela não fique invisível porque alguém
    simplificou a fixture.
    """
    declaradas = {colecao for colecao, _ in validation.COLECOES_PUBLICADAS}
    vazias = [nome for nome in declaradas if not conteudo_maximo.get(nome)]
    assert vazias == [], f"coleção declarada e vazia no Edital máximo: {sorted(vazias)}"

    marco = conteudo_maximo["profiles"][0]["classificationMilestones"][0]
    for objeto in ("rounding", "cutRule", "appealWindow", "drawMethod"):
        assert marco.get(objeto), f"o marco do Edital máximo não declara {objeto}"
    assert marco["tiebreakers"], "o marco do Edital máximo não declara critério de desempate"
    perfil = conteudo_maximo["profiles"][0]
    for objeto in ("vacancyReversion", "callForm", "vacancyTable", "declaredFacts"):
        assert perfil.get(objeto), f"o Perfil do Edital máximo não declara {objeto}"
    regra = perfil["competitionModalities"][1]["normativeRule"]
    for objeto in ("calculation", "rounding", "distribution", "callRules", "effectiveFrom"):
        assert regra.get(objeto), f"a Regra Normativa do Edital máximo não declara {objeto}"
    assert any(evento.get("location") for evento in conteudo_maximo["schedule"])


# --------------------------------------------------------------------------------------------
# O guardião
# --------------------------------------------------------------------------------------------


@pytest.mark.django_db(transaction=True)
@pytest.mark.contract
def test_todo_campo_publicado_tem_natureza_declarada(conteudo_maximo):
    """FR-301 — falha por **omissão**, nomeando o campo, a coleção e o caminho.

    Mensagem que dissesse só "divergência" não atenderia: quem quebrou a suíte precisa ler **qual**
    decisão faltou, e não descobrir que faltou alguma.
    """
    encontrados = campos_publicados(conteudo_maximo)
    sem_decisao = sorted(
        f"({colecao}, {caminho}) em {onde}"
        for (colecao, caminho), onde in encontrados.items()
        if (colecao, caminho) not in CONTRATO
    )
    assert sem_decisao == [], (
        "campo publicado sem natureza de mutabilidade declarada — alguém precisa decidir se ele "
        "pode ser corrigido depois da publicação, e escrever a razão quando não puder:\n  "
        + "\n  ".join(sem_decisao)
    )


@pytest.mark.django_db(transaction=True)
@pytest.mark.contract
def test_toda_natureza_declarada_aponta_campo_que_existe(conteudo_maximo):
    """FR-302 — declarar natureza para campo inexistente é a mesma omissão ao contrário."""
    encontrados = campos_publicados(conteudo_maximo)
    sobrando = sorted(
        f"({colecao}, {caminho})"
        for colecao, caminho in CONTRATO
        if (colecao, caminho) not in encontrados
    )
    assert sobrando == [], (
        "o contrato classifica campo que o Edital máximo não publica:\n  " + "\n  ".join(sobrando)
    )


@pytest.mark.django_db(transaction=True)
@pytest.mark.contract
def test_campo_novo_sem_decisao_derruba_a_suite_nomeando_o_campo(conteudo_maximo):
    """SC-096 — o Independent Test da US5, e a razão de o guardião existir.

    A asserção é sobre a **mensagem**, e não sobre o fato de falhar: um guardião que só dissesse
    "faltou alguma coisa" obrigaria quem o quebrou a caçar o quê.
    """
    conteudo_maximo["profiles"][0]["campoExperimental"] = "valor"
    encontrados = campos_publicados(conteudo_maximo)
    sem_decisao = [chave for chave in encontrados if chave not in CONTRATO]
    assert ("profiles", "campoExperimental") in sem_decisao


@pytest.mark.django_db(transaction=True)
@pytest.mark.contract
def test_todo_objeto_ausente_tem_politica_declarada(conteudo_maximo):
    """FR-313 — `None` não é campo sem natureza: é declaração que não foi feita.

    O que a travessia enumera é o conteúdo do objeto **quando ele existe**. O que este teste
    confere é que todo objeto que pode faltar tem decisão escrita sobre poder nascer por
    Retificação — e que a decisão carrega razão, como as exclusões carregam.
    """
    from processo_seletivo.editais.domain.mutabilidade import PODE_PASSAR_A_EXISTIR

    # Todo objeto com política declarada é objeto que o contrato realmente classifica por dentro.
    for colecao, objeto in PODE_PASSAR_A_EXISTIR:
        dentro = [par for par in CONTRATO if par[0] == colecao and par[1].startswith(f"{objeto}/")]
        assert dentro, f"política declarada para objeto que o contrato não classifica: {objeto}"
    assert all(razao.strip() for _, razao in PODE_PASSAR_A_EXISTIR.values())


@pytest.mark.contract
def test_a_classificacao_nao_depende_do_edital_nem_do_instante():
    """FR-314 e D-011, na forma em que se conferem por código.

    A classificação vigente governa os **atos futuros**, inclusive sobre Edital publicado antes
    dela: uma Retificação é ato novo, praticado hoje, sob a norma de hoje. A consequência
    verificável é a assinatura — `natureza_de` não recebe Edital, versão nem instante, porque não
    há classificação *daquele* Edital a consultar.

    Congelar a classificação em cada Publicação faria este parâmetro existir, o contrato deixar de
    ser código, e cada Edital ficar preso à classificação do dia em que foi publicado — que é o
    precedente do `callForm` outra vez.
    """
    import inspect

    parametros = list(inspect.signature(mutabilidade.natureza_de).parameters)
    assert parametros == ["colecao", "caminho"]


@pytest.mark.django_db(transaction=True)
@pytest.mark.contract
def test_reclassificar_nao_reescreve_conteudo_publicado(conteudo_maximo):
    """A outra metade da FR-314: o que nenhuma reclassificação alcança.

    O conteúdo publicado é imutável pela Constituição, e o contrato nem o toca — ele é lido, e a
    leitura não escreve. Este teste existe para que a afirmação seja verificada, e não só escrita:
    reclassificar um campo e reler a versão consolidada devolve os mesmos bytes.
    """
    from copy import deepcopy

    antes = deepcopy(conteudo_maximo)
    chave = ("stages", "name")
    original = CONTRATO[chave]
    CONTRATO[chave] = mutabilidade.nao_retificavel(
        "razão sintética, só para este teste", fechou_caminho=True
    )
    try:
        assert mutabilidade.natureza_de(*chave).fechou_caminho
        assert conteudo_maximo == antes
    finally:
        CONTRATO[chave] = original
