"""A conferência da submissão não pode envelhecer quando o Edital ganha conteúdo.

A `006` acrescentou Etapas, modalidades e Seções ao conteúdo publicado e a Revisão continuou
mostrando Perfis e Cronograma, porque cada coleção era um bloco escrito à mão no template. Este
teste é o que impede a repetição: a Revisão é lida do snapshot, e todo **campo** do snapshot
precisa estar declarado — lido pela conferência, ou excluído dela com a razão.

**Campo, e não coleção.** O guardião anterior comparava só as listas de entidades da raiz, e dois
formatos escaparam dele por construção: o método comum do sorteio, que é um dicionário da raiz, e
os marcos, que moram dentro do Perfil. A Revisão congelava a Classificação inteira sem mostrá-la
(achado de 27/09, `doc/achado-revisao-nao-mostra-a-classificacao.md`).
"""

import copy
import re
import uuid

import pytest

from processo_seletivo.editais.domain.mutabilidade import CONTRATO
from processo_seletivo.interface import revisao
from processo_seletivo.processos.models import Edital
from processo_seletivo.publicacoes.application.publish_edital import edital_snapshot
from tests.contract.test_mutabilidade import _declarar_requerimento, campos_publicados
from tests.fixtures.publicacao import publish_original
from tests.fixtures.snapshot import rascunho_com_etapas, rascunho_completo


def test_todo_campo_do_contrato_tem_destino_na_conferencia():
    """Todo campo publicado é lido pela conferência, ou excluído dela com a razão.

    A régua é o contrato de mutabilidade, e não uma lista daqui: a `026` já prende o contrato ao
    snapshot, falhando por omissão nos dois sentidos. Um campo novo no conteúdo publicado reprova
    lá até ser classificado, e aqui até ter destino — no mesmo dia em que nasce.
    """
    declarados = revisao.LIDOS | set(revisao.NAO_MOSTRADOS)

    assert not revisao.LIDOS & set(revisao.NAO_MOSTRADOS), (
        "campo ao mesmo tempo lido e excluído: "
        f"{sorted(revisao.LIDOS & set(revisao.NAO_MOSTRADOS))}"
    )
    assert set(CONTRATO) - declarados == set(), (
        "campo do conteúdo publicado sem destino na Revisão — leia-o ou exclua-o com a razão: "
        f"{sorted(set(CONTRATO) - declarados)}"
    )
    assert declarados - set(CONTRATO) == set(), (
        f"a Revisão declara campo que o conteúdo não publica: {sorted(declarados - set(CONTRATO))}"
    )


def test_toda_exclusao_tem_razao():
    """Exclusão sem razão é indistinguível de esquecimento — que é o defeito que ela fecha."""
    assert [par for par, razao in revisao.NAO_MOSTRADOS.items() if not razao.strip()] == []


@pytest.fixture
def snapshot_maximo(api_client, manager_headers, process_payload):
    """O conteúdo de um Edital **máximo**, publicado de verdade — o mesmo da `026`.

    `anexos=1` e o Requerimento de Matrícula vêm por fora do `draft` pela razão de lá: sem eles,
    `attachments` e `matriculationRequest/…` sairiam dos dois lados da comparação.
    """
    edital = publish_original(
        api_client,
        manager_headers,
        process_payload,
        draft=rascunho_completo(),
        anexos=1,
        antes_de_submeter=_declarar_requerimento,
    )
    return edital_snapshot(Edital.objects.get(pk=edital.pk))


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_toda_colecao_do_snapshot_esta_declarada_na_conferencia(snapshot_maximo):
    """O guarda pelo snapshot, e não só pelo contrato — dicionários da raiz e coleções aninhadas.

    A primeira versão deste teste via só as listas de entidades da raiz: `drawMethod`, um
    dicionário, e `classificationMilestones`, uma coleção dentro do Perfil, passavam em silêncio.
    A travessia agora é a da `026`, que desce em objeto e em coleção aninhada. O teste acima
    compara com o contrato; este, com o que um Edital publicado de fato emite — se o contrato
    envelhecer, este acusa sozinho.
    """
    publicados = set(campos_publicados(snapshot_maximo))
    sem_destino = publicados - revisao.LIDOS - set(revisao.NAO_MOSTRADOS)

    assert sem_destino == set(), (
        f"campo publicado que a Revisão não lê nem exclui: {sorted(sem_destino)}"
    )
    assert {
        ("raiz", "drawMethod/algorithm"),
        ("classificationMilestones", "cutRule/targetCount"),
    } <= (publicados), "a travessia deixou de descer no dicionário da raiz ou no marco"


# O que não é prosa: identidade, instante, número e valor de enumeração. A conferência os traduz
# ou os formata, e por isso eles não aparecem literais na tela — e não há como conferir que foram
# lidos procurando o texto.
_NAO_E_PROSA = re.compile(
    r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}"
    r"|\d{4}-\d{2}-\d{2}T.*"
    r"|-?\d+(\.\d+)?"
    r"|[A-Z0-9_]+"
    # A chave de uma coleção, como `source` a grava: `profiles` é lido "Perfis".
    r"|[a-z][A-Za-z]*"
)


def _valores(colecao, itens, caminho="", achados=None):
    """Os valores de cada par `(coleção, caminho)`, pela mesma travessia de `campos_publicados`."""
    achados = {} if achados is None else achados
    for item in itens:
        for chave, valor in item.items():
            relativo = f"{caminho}{chave}"
            if isinstance(valor, dict):
                _valores(colecao, [valor], f"{relativo}/", achados)
            elif isinstance(valor, list) and valor and all(isinstance(v, dict) for v in valor):
                _valores(chave, valor, "", achados)
            else:
                achados.setdefault((colecao, relativo), []).extend(
                    valor if isinstance(valor, list) else [valor]
                )
    return achados


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_o_que_a_conferencia_diz_ler_aparece_na_tela(snapshot_maximo):
    """A declaração não pode mentir: todo texto livre de um campo lido está na tela.

    `LIDOS` é declaração, e declaração se esquece de cumprir. Este teste a confere pelo único
    caminho que não depende de quem a escreveu: o valor de cada campo em prosa precisa aparecer,
    literal, no que a conferência mostra. Enumeração, instante e número ficam de fora — eles são
    traduzidos, e as asserções dos casos abaixo os cobrem pela frase.
    """
    blocos = revisao.blocos(snapshot_maximo)
    tudo = "\n".join(
        texto
        for bloco in blocos
        for item in bloco["itens"]
        for texto in [item["titulo"], *item["linhas"]]
    )
    faltam = sorted(
        (par, valor)
        for par, valores in _valores("raiz", [snapshot_maximo]).items()
        if par in revisao.LIDOS
        for valor in valores
        if isinstance(valor, str)
        and valor
        and not _NAO_E_PROSA.fullmatch(valor)
        and valor not in tudo
    )

    assert faltam == [], f"campo declarado como lido e ausente da tela: {faltam}"


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_a_conferencia_mostra_cota_etapa_e_texto(api_client, manager_headers, process_payload):
    """O percentual é a informação mais sensível do documento e era a que não aparecia."""
    # O texto da seção é o que alguém escreveu: desde a `054` o catálogo não tem redação padrão.
    rascunho = rascunho_com_etapas()
    rascunho["sections"] = [
        {"key": "disposicoes-preliminares", "content": "O presente Edital estabelece as normas."}
    ]
    edital = publish_original(api_client, manager_headers, process_payload, draft=rascunho)
    blocos = revisao.blocos(edital_snapshot(Edital.objects.get(pk=edital.pk)))
    tudo = "\n".join(
        linha for bloco in blocos for item in bloco["itens"] for linha in item["linhas"]
    )

    # A forma canônica é a do conteúdo publicado; a conferência a escreve como gente (057,
    # FR-1058): sem os zeros que não dizem nada, com vírgula, sem arredondar.
    assert "Modalidade: PPI" in tudo and "20%" in tudo and "20.0000%" not in tudo
    assert "Lei 12.711/2012" in tudo
    assert "Prova didática" in "\n".join(
        item["titulo"] for bloco in blocos for item in bloco["itens"]
    )
    assert "Caráter: eliminatória e classificatória" in tudo
    assert "Peso: 2" in tudo.split("\n"), "sem os zeros que não dizem nada (057, FR-1058)"
    assert "O presente Edital estabelece as normas" in tudo, "o texto da seção, não só o título"
    # E a seção vazia diz que não sai, em vez de mostrar o número do catálogo (054, FR-985).
    assert "Vazia — não sai no documento." in tudo


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_a_conferencia_mostra_o_que_a_012_acrescentou_a_etapa(
    api_client, manager_headers, process_payload
):
    """FR-007 da `012`: o que é congelado precisa aparecer em "o que será congelado".

    A pontuação máxima é o teto contra o qual cada avaliação da Etapa é validada depois, e as
    avaliações por inscrição são o que a distribuição cobra. O formulário coletava as duas e o
    documento publicado as imprimia; a conferência da submissão era o único lugar do caminho que
    as omitia — justamente o que existe para dizer o que está prestes a ficar imutável.
    """
    rascunho = rascunho_com_etapas()
    # Na segunda Etapa, que não é eliminatória e nenhum marco referencia: a dupla leitura ali é
    # aviso, e o Edital publica (046, `FR-748`). Na primeira, eliminatória, seria impeditivo.
    rascunho["stages"][1].update(evaluationsPerRegistration=2, maximumScore="100.0000")
    edital = publish_original(api_client, manager_headers, process_payload, draft=rascunho)
    blocos = revisao.blocos(edital_snapshot(Edital.objects.get(pk=edital.pk)))
    tudo = "\n".join(
        linha for bloco in blocos for item in bloco["itens"] for linha in item["linhas"]
    )

    assert "Pontuação máxima: 100" in tudo.split("\n")
    assert "Avaliações por inscrição: 2" in tudo


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_a_etapa_que_nada_declara_nao_inventa_o_padrao(
    api_client, manager_headers, process_payload
):
    """Ausência é "o Edital não declarou", e não "declarou o padrão" — como no documento."""
    edital = publish_original(
        api_client, manager_headers, process_payload, draft=rascunho_com_etapas()
    )
    blocos = revisao.blocos(edital_snapshot(Edital.objects.get(pk=edital.pk)))
    tudo = "\n".join(
        linha for bloco in blocos for item in bloco["itens"] for linha in item["linhas"]
    )

    assert "Pontuação máxima" not in tudo
    assert "Avaliações por inscrição" not in tudo


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_a_conferencia_mostra_o_documento_exigido_e_de_quem(
    api_client, manager_headers, process_payload
):
    """O que o Edital exigirá do candidato, e de qual candidato.

    A aplicabilidade é o que não se pode omitir por item: um documento restrito a um Perfil, numa
    lista que não diz de quem é, se lê como exigido de todo mundo — e quem homologa homologaria
    uma exigência que não existe.
    """
    edital = publish_original(
        api_client, manager_headers, process_payload, draft=rascunho_completo()
    )
    blocos = revisao.blocos(edital_snapshot(Edital.objects.get(pk=edital.pk)))
    documentos = next(bloco for bloco in blocos if bloco["titulo"] == "Documentos Exigidos")
    tudo = "\n".join(
        f"{item['titulo']}\n" + "\n".join(item["linhas"]) for item in documentos["itens"]
    )

    assert documentos["etapa"] == "inscricao", "o passo do assistente em que se corrige"
    assert "1. Documento de identificação" in tudo
    assert "Exigência: obrigatória" in tudo
    assert "Aplica-se a: todos os candidatos" in tudo
    assert "Instruções: Frente e verso, em arquivo único." in tudo
    assert "Aplica-se a: candidatos ao perfil Perfil A" in tudo, "o restrito não vale para todos"


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_cada_bloco_aponta_para_a_etapa_que_o_corrige(api_client, manager_headers, process_payload):
    from processo_seletivo.interface.views import CHAVES_ETAPA

    edital = publish_original(api_client, manager_headers, process_payload)
    blocos = revisao.blocos(edital_snapshot(Edital.objects.get(pk=edital.pk)))

    assert [bloco["etapa"] for bloco in blocos if bloco["etapa"] not in CHAVES_ETAPA] == []


# ------------------------------------------------------------------ a Classificação na conferência


def _texto(item):
    return "\n".join([item["titulo"], *item["linhas"], item.get("diverge", "")])


def _classificacao(snapshot):
    bloco = next(bloco for bloco in revisao.blocos(snapshot) if bloco["titulo"] == "Classificação")
    assert bloco["etapa"] == "classificacao", "o passo do assistente em que se corrige"
    return bloco["itens"]


def _com_perfis(quantos):
    """O Edital máximo com `quantos` Perfis iguais ao principal — marco, fatos e quadro inclusos.

    Cópias com identidade nova e nome derivado do Perfil, como a duplicação as produz (043): é o
    formato do 28/2026, em que sete Perfis carregam a mesma regra.
    """
    conteudo = rascunho_completo()
    modelo = conteudo["profiles"][0]
    conteudo["profiles"] = []
    for indice in range(1, quantos + 1):
        perfil = copy.deepcopy(modelo)
        perfil.update(id=str(uuid.uuid4()), code=f"LP{indice:02}", name=f"Perfil {indice}")
        marco = perfil["classificationMilestones"][0]
        marco.update(
            id=str(uuid.uuid4()),
            code=perfil["code"],
            name=f"Classificação final — Perfil {indice}",
            # Referencia o método comum do Edital, como no 28/2026.
            drawMethod=None,
        )
        conteudo["profiles"].append(perfil)
    return conteudo


def test_a_classificacao_mostra_o_metodo_comum_e_o_que_o_marco_declara():
    """Tudo o que a etapa Classificação congela, com as frases do documento."""
    itens = _classificacao(rascunho_completo())
    tudo = "\n".join(_texto(item) for item in itens)

    comum = next(
        item for item in itens if item["titulo"] == "Método do sorteio comum a este Edital"
    )
    assert "Algoritmo: IFES-SORTEIO-SHA256-v1" in comum["linhas"]
    assert "Quando: 08/01/2020, às 20h" in comum["linhas"]
    assert "Semente: Os cinco números sorteados, na ordem dos prêmios." in comum["linhas"]

    assert "Ordem: por sorteio" in tudo
    assert "Sorteio: método próprio deste marco — diverge do comum deste Edital" in tudo
    assert "Sorteio — Ocorrência: 5901" in tudo
    assert (
        "Habilitação: participam apenas as inscrições habilitadas na Etapa Prova didática" in tudo
    )
    # A frase do documento, com o resultado nomeado pela denominação, que está na linha de cima
    # (067, FR-1304, D-012): com o nome dentro da frase, cada Perfil viraria um grupo.
    assert "Denominação: Classificação final" in tudo
    assert (
        "Recurso: Caberá recurso contra o resultado deste marco, no prazo de 5 (cinco) dias "
        "corridos, contados da divulgação desse resultado." in tudo
    )
    assert "Corte: Progridem os 3 (três) primeiros desta ordem, mais 1 (um) suplente." in tudo
    # As frases do documento, e não uma redação própria da conferência (014, FR-185). O empate no
    # corte **não** sai sob sorteio declarado, como no documento: a ordem sorteada é total (067,
    # FR-1315). A frase dele sob pontuação está em `test_correcoes_de_norma_na_revisao.py`.
    assert "Empate no corte" not in tudo
    assert "Arredondamento" not in tudo
    assert (
        "Continuação: Poderá haver chamada, nesta ordem, além dos que este corte publicar." in tudo
    )
    assert "Etapa que o corte alimenta: nenhuma" in tudo
    assert (
        "Desempate, 2º: maior valor declarado em Meses de experiência; sem o valor, o critério "
        "não se aplica" in tudo
    )


def test_o_marco_de_pontuacao_mostra_a_combinacao_e_nao_o_sorteio():
    """Sob pontuação, a combinação com os pesos; e nenhuma linha de sorteio (032, FR-468)."""
    conteudo = rascunho_completo()
    # Só o Perfil principal: os outros dois da fixture ordenam por sorteio.
    conteudo["profiles"] = conteudo["profiles"][:1]
    marco = conteudo["profiles"][0]["classificationMilestones"][0]
    marco.update(orderProduction="POR_PONTUACAO", drawMethod=None, cutRule=None, appealWindow=None)
    conteudo.pop("drawMethod")
    tudo = "\n".join(_texto(item) for item in _classificacao(conteudo))

    assert "Combinação: soma ponderada das Etapas Prova didática (peso 2) e" in tudo
    assert "Normalização: nenhuma" in tudo
    assert "Sorteio" not in tudo
    assert "Corte: este marco não corta" in tudo
    assert "Recurso: nada declarado" in tudo, "o silêncio dito como silêncio, e não omitido"


def test_marcos_iguais_em_perfis_diferentes_aparecem_uma_vez():
    """Sete Perfis com a mesma regra são um item, e não sete (o 28/2026)."""
    itens = _classificacao(_com_perfis(7))
    marcos = [item for item in itens if "Perfis" in item["titulo"] or "Perfil " in item["titulo"]]

    assert len(marcos) == 1
    assert marcos[0]["titulo"] == "7 Perfis: LP01, LP02, LP03, LP04, LP05, LP06 e LP07"
    assert "Sorteio: método comum a este Edital" in marcos[0]["linhas"]
    # O comum aparece uma vez, no alto do bloco — e nenhum campo dele se repete no marco. O
    # instante vazio do PDF é "—", e passava pelo filtro como valor declarado.
    assert not [linha for linha in marcos[0]["linhas"] if linha.startswith("Sorteio —")]
    # A habilitação é do marco, e não do método comum: quem referencia o comum sorteia todos.
    assert "Habilitação: participam todas as inscrições submetidas" in marcos[0]["linhas"]
    assert "Denominação: Classificação final — o nome de cada Perfil" in marcos[0]["linhas"]
    assert "diverge" not in marcos[0]


def test_o_marco_que_diverge_diz_em_que():
    """O grupo mais numeroso é a referência; o outro nomeia o que difere dela, e só isso."""
    conteudo = _com_perfis(4)
    conteudo["profiles"][2]["classificationMilestones"][0]["cutRule"]["targetCount"] = 5
    itens = _classificacao(conteudo)
    marcos = [item for item in itens if "Perfi" in item["titulo"]]

    assert [item["titulo"] for item in marcos] == ["3 Perfis: LP01, LP02 e LP04", "Perfil LP03"]
    assert marcos[1]["diverge"] == "Diverge do marco de 3 Perfis em: Corte."
    assert (
        "Corte: Progridem os 5 (cinco) primeiros desta ordem, mais 1 (um) suplente."
        in (marcos[1]["linhas"])
    )


def test_o_perfil_sem_marco_e_nomeado_na_classificacao():
    conteudo = _com_perfis(3)
    conteudo["profiles"][1]["classificationMilestones"] = []
    itens = _classificacao(conteudo)

    sem = next(item for item in itens if item["titulo"] == "Sem marco classificatório")
    assert sem["linhas"] == ["Perfil LP02 — não produz ordem, e não há o que ocupar."]


def test_o_edital_sem_classificacao_nao_inventa_metodo():
    """Sem marco e sem método comum, só a linha dos Perfis sem marco — e nenhum sorteio."""
    conteudo = rascunho_com_etapas()
    conteudo.pop("drawMethod", None)
    for perfil in conteudo["profiles"]:
        perfil["classificationMilestones"] = []
    titulos = [item["titulo"] for item in _classificacao(conteudo)]

    assert titulos == ["Sem marco classificatório"]


def test_o_perfil_mostra_convocacao_reversao_e_fatos():
    """O que `_perfil` escrevia à mão e esquecia: as declarações que só a Retificação corrige."""
    conteudo = rascunho_completo()
    perfis = next(bloco for bloco in revisao.blocos(conteudo) if bloco["etapa"] == "perfis")
    principal = "\n".join(perfis["itens"][0]["linhas"])

    assert (
        "Como a convocação é comunicada: por publicação no endereço eletrônico do certame"
        in principal
    )
    assert (
        "Reverter vaga reservada não preenchida para a ampla concorrência: só quando a lista "
        "reservada esgota" in principal
    )
    assert (
        "Fato exigido do candidato: Meses de experiência (número inteiro, código EXPERIENCIA)"
        in (principal)
    )
    assert "Ampla concorrência: AC — Modalidade AC" in principal
    assert "vigente desde 09/06/2014" in principal


def test_a_forma_de_convocacao_nao_declarada_e_dita():
    """A `019` recusa convocar sem a forma, e a Revisão é o último lugar barato para declará-la."""
    conteudo = rascunho_completo()
    conteudo["profiles"][0]["callForm"] = None
    perfis = next(bloco for bloco in revisao.blocos(conteudo) if bloco["etapa"] == "perfis")

    assert (
        "Como a convocação é comunicada: forma de convocação não declarada neste Edital"
        in perfis["itens"][0]["linhas"]
    )
