"""O método do sorteio é declarado na composição do Edital, e não na gestão do sorteio (021, D-013).

**Por que este teste existe, e por que ele olha dois caminhos.** A FR-014 exige que alterar o
método seja Retificação. Isso só é verdade se o método for conteúdo publicado do Edital — e ele só
chega ao conteúdo publicado se sobreviver aos **dois** caminhos do assistente: a coleta do
formulário e o reenvio do rascunho já persistido. A `018` perdeu a janela recursal exatamente aí
(E2E18-005): declarada no passo Classificação, ela sumia ao gravar qualquer passo seguinte, porque
o reenvio não a carregava. Fechar um caminho só deixa o defeito vivo.

A leitura do método pela tela do sorteio — que exibe e **não** edita — é afirmada em
`tests/integration/sorteios/test_metodo_nao_e_escolha.py`, que varre as superfícies do módulo.
"""

import re

import pytest
from django.urls import reverse

from processo_seletivo.editais.models.perfis import MarcoClassificatorio
from tests.interface.test_compor import PERFIL
from tests.interface.test_compor_classificacao import (
    ETAPA_CLASSIFICATORIA,
    MARCO,
    marco_form,
)

pytestmark = [pytest.mark.django_db, pytest.mark.integration]

_METODO_VALIDO = {
    "algorithm": "IFES-SORTEIO-SHA256-v1",
    "source": "Loteria Federal",
    "occurrence": "5900",
    "occurrenceAt": "2026-11-20T20:00:00-03:00",
    "derivation": "a extração de sábado anterior",
    "normalization": {"rule": "DIGITOS_EM_SEQUENCIA", "text": "os cinco números"},
    "substitutionRule": {
        "rule": "OCORRENCIA_SEGUINTE_DA_MESMA_FONTE",
        "text": "vale a seguinte",
    },
}

METODO_NO_FORMULARIO = {
    f"marco-{PERFIL}-0-draw-algorithm": "IFES-SORTEIO-SHA256-v1",
    f"marco-{PERFIL}-0-draw-source": "Loteria Federal",
    f"marco-{PERFIL}-0-draw-occurrence": "5900",
    f"marco-{PERFIL}-0-draw-occurrenceAt": "2026-11-20T20:00:00-03:00",
    f"marco-{PERFIL}-0-draw-derivation": "a extração de sábado anterior à data publicada",
    f"marco-{PERFIL}-0-draw-normalizationRule": "DIGITOS_EM_SEQUENCIA",
    f"marco-{PERFIL}-0-draw-normalizationText": "os cinco números, na ordem dos prêmios",
    f"marco-{PERFIL}-0-draw-substitutionRule": "OCORRENCIA_SEGUINTE_DA_MESMA_FONTE",
    f"marco-{PERFIL}-0-draw-substitutionText": "não havendo extração, vale a seguinte",
}


def _compor(client, edital, **extra):
    return client.post(
        reverse("interface:compor-etapa", args=[edital.id, "classificacao"]),
        marco_form(**extra),
    )


def test_a_tela_oferece_os_seis_campos_do_metodo(client, com_etapas):
    # O fragmento do marco só é desenhado quando existe marco: o passo nasce sem nenhum, e é o
    # `hx-get` que o acrescenta. Gravar um primeiro é o mesmo percurso de quem compõe de verdade.
    #
    # **Com a forma da ordem declarada** desde a `030`: os dez campos do método existem para quem
    # respondeu que a ordem nasce de sorteio, e não para todo mundo (FR-414).
    _compor(client, com_etapas, **{f"marco-{PERFIL}-0-orderProduction": "POR_SORTEIO"})

    resposta = client.get(reverse("interface:compor-etapa", args=[com_etapas.id, "classificacao"]))
    corpo = resposta.content.decode()

    assert "Método do sorteio, se este marco ordena por sorteio" in corpo
    for campo in ("algorithm", "source", "occurrence", "derivation"):
        assert f'name="marco-{PERFIL}-0-draw-{campo}"' in corpo
    assert f'name="marco-{PERFIL}-0-draw-normalizationRule"' in corpo
    assert f'name="marco-{PERFIL}-0-draw-substitutionRule"' in corpo


def test_o_marco_que_nao_sorteia_nao_declara_metodo(client, com_etapas):
    """A ausência é a maioria dos casos, e é resposta legítima — nada de valor padrão."""
    resposta = _compor(client, com_etapas)

    assert resposta.status_code == 302, resposta.content
    assert MarcoClassificatorio.objects.get(pk=MARCO).metodo_de_sorteio == {}


def test_o_metodo_declarado_chega_ao_rascunho(client, com_etapas):
    resposta = _compor(client, com_etapas, **METODO_NO_FORMULARIO)

    assert resposta.status_code == 302, resposta.content
    metodo = MarcoClassificatorio.objects.get(pk=MARCO).metodo_de_sorteio
    assert metodo["algorithm"] == "IFES-SORTEIO-SHA256-v1"
    assert metodo["source"] == "Loteria Federal"
    assert metodo["normalization"] == {
        "rule": "DIGITOS_EM_SEQUENCIA",
        "text": "os cinco números, na ordem dos prêmios",
    }
    assert metodo["substitutionRule"]["rule"] == "OCORRENCIA_SEGUINTE_DA_MESMA_FONTE"


def test_o_metodo_volta_para_a_tela_na_reexibicao(client, com_etapas):
    _compor(client, com_etapas, **METODO_NO_FORMULARIO)

    corpo = client.get(
        reverse("interface:compor-etapa", args=[com_etapas.id, "classificacao"])
    ).content.decode()

    assert 'value="Loteria Federal"' in corpo
    assert '<option value="DIGITOS_EM_SEQUENCIA" selected>' in corpo
    assert '<option value="OCORRENCIA_SEGUINTE_DA_MESMA_FONTE" selected>' in corpo


def test_gravar_outro_passo_nao_apaga_o_metodo_declarado(client, com_etapas):
    """**O segundo caminho de perda**, e o que a `018` aprendeu do jeito difícil (E2E18-005).

    Declarar no passo Classificação e gravar o passo seguinte não pode publicar um Edital que nada
    declara sobre sorteio: o reenvio carrega o contrato inteiro do marco, e não só os campos que a
    tela da vez desenha.
    """
    _compor(client, com_etapas, **METODO_NO_FORMULARIO)

    resposta = client.post(
        reverse("interface:compor-etapa", args=[com_etapas.id, "identificacao"]),
        {"title": "Título alterado depois do método", "description": "Descrição qualquer."},
    )

    assert resposta.status_code in (200, 302), resposta.content
    metodo = MarcoClassificatorio.objects.get(pk=MARCO).metodo_de_sorteio
    assert metodo, "o método declarado sumiu ao gravar outro passo do assistente"
    assert metodo["source"] == "Loteria Federal"


def test_metodo_pela_metade_e_recusado_nomeando_o_que_falta(client, com_etapas):
    """Sem regra de substituição, a escolha volta para a mesa no dia do sorteio (FR-015)."""
    from processo_seletivo.editais.domain.perfis import (
        ProfileValidationError,
        validate_classification_milestones,
    )

    incompleto = {
        "id": MARCO,
        "code": "SORTEIO",
        "name": "Sorteio",
        "stages": [ETAPA_CLASSIFICATORIA],
        "operation": "SOMA_PONDERADA",
        "normalization": "NENHUMA",
        "rounding": {"scale": 2, "mode": "MEIO_PARA_CIMA"},
        "tiebreakers": [],
        # Tudo menos a regra de substituição: é ela que o teste cobra, e o método declarado pela
        # metade devolve ao dia do sorteio a escolha que ele existe para eliminar.
        "drawMethod": {k: v for k, v in _METODO_VALIDO.items() if k != "substitutionRule"},
    }

    with pytest.raises(ProfileValidationError, match="substitutionRule"):
        validate_classification_milestones([incompleto])


def test_regra_de_normalizacao_fora_do_vocabulario_e_recusada_na_elaboracao():
    """O defeito aparece no dia em que alguém a escreve, e não ao vivo no dia do sorteio."""
    from processo_seletivo.editais.domain.perfis import (
        ProfileValidationError,
        _validar_metodo_de_sorteio,
    )

    with pytest.raises(ProfileValidationError, match="não publicada por este sistema"):
        _validar_metodo_de_sorteio(
            {**_METODO_VALIDO, "normalization": {"rule": "O_QUE_A_COMISSAO_ACHAR", "text": "z"}}
        )


def test_um_algoritmo_que_o_sistema_nao_executa_e_recusado():
    """O manifesto publicaria um nome, e a ordem viria de outro (021, FR-027).

    A validação só conferia que `algorithm` estava preenchido, e a constituição sempre usava
    `IFES-SORTEIO-SHA256-v1`: um Edital podia declarar `SORTEIO-XPTO-v3` e publicar um manifesto
    que ninguém consegue reimplementar. Quem tentasse chegaria a outra ordem — e concluiria,
    corretamente, que o sorteio não confere.
    """
    from processo_seletivo.editais.domain.perfis import (
        ProfileValidationError,
        _validar_metodo_de_sorteio,
    )

    with pytest.raises(ProfileValidationError, match="não publicado por este sistema"):
        _validar_metodo_de_sorteio(
            {
                **{k: v for k, v in _METODO_VALIDO.items()},
                "algorithm": "SORTEIO-XPTO-v3",
            }
        )


def test_uma_regra_de_substituicao_que_o_sistema_nao_executa_e_recusada():
    """Prosa não é aplicável "sem escolha humana no momento da execução" (021, FR-015)."""
    from processo_seletivo.editais.domain.perfis import (
        ProfileValidationError,
        _validar_metodo_de_sorteio,
    )

    with pytest.raises(ProfileValidationError, match="Regra de substituição não publicada"):
        _validar_metodo_de_sorteio(
            {
                **_METODO_VALIDO,
                "substitutionRule": {"rule": "O_QUE_A_COMISSAO_DECIDIR", "text": "…"},
            }
        )


def test_o_algoritmo_declarado_e_o_que_o_dominio_executa():
    """A afirmação positiva: o vocabulário fechado **é** o que `chave.py` implementa."""
    from processo_seletivo.sorteios.domain.chave import ALGORITMO, ALGORITMOS

    assert _METODO_VALIDO["algorithm"] in ALGORITMOS
    assert ALGORITMOS == frozenset({ALGORITMO})


# --- O método declarado uma vez (030, US3, FR-429, FR-430, SC-140) ---------------------------

METODO_COMUM_NO_FORMULARIO = {
    "edital-draw-algorithm": "IFES-SORTEIO-SHA256-v1",
    "edital-draw-source": "Loteria Federal",
    "edital-draw-occurrence": "5900",
    "edital-draw-occurrenceAt": "2026-11-20T20:00:00-03:00",
    "edital-draw-derivation": "a extração de sábado anterior à data publicada",
    "edital-draw-normalizationRule": "DIGITOS_EM_SEQUENCIA",
    "edital-draw-normalizationText": "os cinco números, na ordem dos prêmios",
    "edital-draw-substitutionRule": "OCORRENCIA_SEGUINTE_DA_MESMA_FONTE",
    "edital-draw-substitutionText": "não havendo extração, vale a seguinte",
}


def test_o_metodo_comum_e_declarado_uma_vez_e_os_marcos_o_referenciam(client, com_etapas):
    """SC-140 — sete Perfis de sorteio declaravam a mesma regra sete vezes.

    O sorteio é **um evento**: a mesma extração semeia todas as listas do certame. O que este
    teste mede é que a declaração acontece uma vez e que o marco que não a redigita continua
    ordenando por sorteio — que é a metade que uma leitura da chave do marco não veria.
    """
    from processo_seletivo.editais.domain import marcos
    from processo_seletivo.processos.models import Edital
    from processo_seletivo.publicacoes.application.publish_edital import edital_snapshot

    resposta = _compor(
        client,
        com_etapas,
        **{f"marco-{PERFIL}-0-orderProduction": "POR_SORTEIO", **METODO_COMUM_NO_FORMULARIO},
    )

    assert resposta.status_code == 302, resposta.content
    edital = Edital.objects.get(pk=com_etapas.pk)
    assert edital.metodo_de_sorteio_comum["algorithm"] == "IFES-SORTEIO-SHA256-v1"
    assert MarcoClassificatorio.objects.get(pk=MARCO).metodo_de_sorteio == {}, (
        "o marco referencia o comum, e não o redigita"
    )

    conteudo = edital_snapshot(edital)
    assert conteudo["drawMethod"]["source"] == "Loteria Federal"
    assert conteudo["profiles"][0]["classificationMilestones"][0]["drawMethod"] is None
    assert marcos.marco_ordena_por_sorteio(conteudo, perfil_id=PERFIL, marco_id=MARCO), (
        "o marco que referencia o método comum ordena por sorteio, e quem lesse só a chave dele "
        "concluiria que não"
    )


def test_o_marco_divergente_registra_a_divergencia_no_conteudo_normativo(client, com_etapas):
    """FR-430 — a divergência se lê do documento, sem inferência: a chave está lá, preenchida."""
    from processo_seletivo.editais.domain import marcos
    from processo_seletivo.processos.models import Edital
    from processo_seletivo.publicacoes.application.publish_edital import edital_snapshot

    resposta = _compor(
        client,
        com_etapas,
        **{
            f"marco-{PERFIL}-0-orderProduction": "POR_SORTEIO",
            **METODO_COMUM_NO_FORMULARIO,
            **METODO_NO_FORMULARIO,
            f"marco-{PERFIL}-0-draw-source": "Fonte de demonstração",
        },
    )

    assert resposta.status_code == 302, resposta.content
    conteudo = edital_snapshot(Edital.objects.get(pk=com_etapas.pk))
    marco = conteudo["profiles"][0]["classificationMilestones"][0]

    assert conteudo["drawMethod"]["source"] == "Loteria Federal"
    assert marco["drawMethod"]["source"] == "Fonte de demonstração"
    assert (
        marcos.metodo_que_governa(conteudo, perfil_id=PERFIL, marco_id=MARCO)["source"]
        == "Fonte de demonstração"
    ), "quem declarou o próprio método quis o próprio"


def test_a_tela_oferece_o_metodo_comum_no_passo_da_classificacao(client, com_etapas):
    """FR-429 na folha: a declaração é do Edital, e por isso mora no passo, e não no cartão."""
    from tests.interface.conftest import identificar

    identificar(client, "ana.elaboradora", ["elaborador"])

    corpo = client.get(
        reverse("interface:compor-etapa", args=[com_etapas.id, "classificacao"])
    ).content.decode()

    assert "Método do sorteio comum a este Edital" in corpo
    for campo in ("algorithm", "source", "occurrence", "derivation"):
        assert f'name="edital-draw-{campo}"' in corpo
    assert 'name="edital-draw-qualifyingStageId"' not in corpo, (
        "a Etapa de habilitação é do marco: no Edital ela endereçaria Etapa que parte dos marcos "
        "não mede"
    )


def test_o_cartao_diz_que_usa_o_comum_e_diz_quando_diverge(client, com_etapas):
    """A diferença precisa ser legível na tela, e não só no conteúdo publicado."""
    from tests.interface.conftest import identificar

    identificar(client, "ana.elaboradora", ["elaborador"])
    _compor(
        client,
        com_etapas,
        **{f"marco-{PERFIL}-0-orderProduction": "POR_SORTEIO", **METODO_COMUM_NO_FORMULARIO},
    )
    referencia = client.get(
        reverse("interface:compor-etapa", args=[com_etapas.id, "classificacao"])
    ).content.decode()

    assert "usa o <strong>método comum deste" in referencia
    assert "o comum deste Edital" in referencia

    _compor(
        client,
        com_etapas,
        **{
            f"marco-{PERFIL}-0-orderProduction": "POR_SORTEIO",
            **METODO_COMUM_NO_FORMULARIO,
            **METODO_NO_FORMULARIO,
        },
    )
    divergente = client.get(
        reverse("interface:compor-etapa", args=[com_etapas.id, "classificacao"])
    ).content.decode()

    assert "próprio — diverge do comum do Edital" in divergente


def test_gravar_outra_etapa_nao_apaga_o_metodo_comum(client, com_etapas):
    """A travessia, e ela é a razão de `draw_method=None` significar "não veio neste envio".

    `replace_draft` apaga e recria o que recebe, e as demais etapas do assistente não desenham
    este campo. Se a ausência valesse por vazio, declarar o método comum na Classificação e visitar
    o Cronograma o apagaria em silêncio — que é a classe de perda que este assistente já pagou
    quatro vezes.
    """
    from processo_seletivo.processos.models import Edital
    from tests.interface.test_compor import eventos

    _compor(
        client,
        com_etapas,
        **{f"marco-{PERFIL}-0-orderProduction": "POR_SORTEIO", **METODO_COMUM_NO_FORMULARIO},
    )
    com_etapas.refresh_from_db()

    resposta = client.post(
        reverse("interface:compor-etapa", args=[com_etapas.id, "cronograma"]), eventos()
    )

    assert resposta.status_code == 302, resposta.content
    assert Edital.objects.get(pk=com_etapas.pk).metodo_de_sorteio_comum["algorithm"]


def test_o_fragmento_do_marco_sabe_do_metodo_comum(client, com_etapas):
    """O pedaço que o htmx troca não pode saber menos do que a tela que o contém (030).

    Encontrado percorrendo a interface: a tela dizia "o comum deste Edital" e o cartão recomposto
    dizia "ainda não declarado" sobre o mesmo marco, porque o contexto do fragmento não carregava a
    declaração do Edital. Nenhum teste de template pegaria — os dois caminhos renderizam o mesmo
    arquivo, e é o contexto que difere.
    """
    from tests.interface.conftest import identificar

    identificar(client, "ana.elaboradora", ["elaborador"])
    _compor(
        client,
        com_etapas,
        **{f"marco-{PERFIL}-0-orderProduction": "POR_SORTEIO", **METODO_COMUM_NO_FORMULARIO},
    )

    # O cartão recém-criado ainda não respondeu à pergunta de entrada, e por isso não desenha bloco
    # de sorteio nenhum — é o estado correto, e não o que este teste mede.
    acrescentado = client.get(
        reverse("interface:fragmento-marco", args=[PERFIL]),
        {"edital": str(com_etapas.id), "indice": "0"},
    ).content.decode()
    assert f'<input type="hidden" name="marco-{PERFIL}-0-draw-algorithm"' in acrescentado, (
        "sem resposta à pergunta de entrada, o método viaja oculto e não abre bloco nenhum"
    )

    recomposto = client.get(
        reverse("interface:fragmento-marco-recomposto", args=[PERFIL, "0"]),
        {
            "edital": str(com_etapas.id),
            f"marco-{PERFIL}-0-id": MARCO,
            f"marco-{PERFIL}-0-code": "FINAL",
            f"marco-{PERFIL}-0-name": "Classificação final",
            f"marco-{PERFIL}-0-orderProduction": "POR_SORTEIO",
            f"marco-{PERFIL}-0-stages": ETAPA_CLASSIFICATORIA,
            f"marco-{PERFIL}-0-scale": "2",
            f"marco-{PERFIL}-0-mode": "MEIO_PARA_CIMA",
        },
    ).content.decode()

    assert "o comum deste Edital" in recomposto
    assert "ainda não declarado" not in recomposto
    assert "usa o <strong>método comum deste" in recomposto


def test_a_recusa_do_metodo_comum_nao_apaga_o_que_foi_digitado(client, com_etapas):
    """A recusa existe para corrigir o que se errou, e não para apagar o que se acertou (030).

    O método vale inteiro ou não é declarado, e a validação acontece **antes** da gravação. Ler o
    Edital do banco na reexibição devolvia os nove campos vazios a quem esqueceu um deles — e a
    pessoa tinha de redigitar os outros oito para descobrir se acertou o nono.

    É a mesma classe de perda que `_reexibir_marco` já pagou uma vez com a janela recursal, o
    método e a regra de corte do marco.
    """
    from tests.interface.conftest import identificar

    identificar(client, "ana.elaboradora", ["elaborador"])
    sem_substituicao = {
        chave: valor
        for chave, valor in METODO_COMUM_NO_FORMULARIO.items()
        if "substitution" not in chave
    }

    resposta = client.post(
        reverse("interface:compor-etapa", args=[com_etapas.id, "classificacao"]),
        marco_form(**{f"marco-{PERFIL}-0-orderProduction": "POR_SORTEIO", **sem_substituicao}),
    )

    assert resposta.status_code == 200, "método pela metade é recusado inteiro"
    corpo = resposta.content.decode()

    # O controle inteiro, e não a dupla `name="…" value="…"`: o template quebra os atributos em
    # duas linhas, e uma asserção sobre a vizinhança deles passaria a depender do recuo.
    #
    # **E o controle pode ser `<input>` ou `<select>`** desde a `035` (FR-507): o algoritmo e a
    # fonte deixaram de ser digitados. A garantia que este teste prende não é a forma do controle —
    # é que a recusa **não apaga o que se acertou** —, e ela vale igual nos dois. Ler só o `<input>`
    # faria o teste passar a não guardar nada sobre os dois campos que viraram escolha, em silêncio.
    import re as _re

    def _valor(nome):
        escolha = _re.search(rf'<select[^>]*name="{nome}"[^>]*>(.*?)</select>', corpo, _re.S)
        if escolha:
            selecionada = _re.search(r'<option value="([^"]*)"[^>]*selected', escolha.group(1))
            return selecionada.group(1) if selecionada else ""
        achado = _re.search(rf'<input[^>]*name="{nome}"[^>]*>', corpo, _re.S)
        assert achado, f"a tela não reexibe {nome}"
        return _re.search(r'value="([^"]*)"', achado.group(0)).group(1)

    assert _valor("edital-draw-algorithm") == "IFES-SORTEIO-SHA256-v1"
    assert _valor("edital-draw-occurrence") == "5900"
    assert _valor("edital-draw-derivation") == "a extração de sábado anterior à data publicada"
    assert _valor("edital-draw-substitutionText") == "", "o que faltava continua faltando"
    com_etapas.refresh_from_db()
    assert com_etapas.metodo_de_sorteio_comum == {}, "e nada foi gravado"


# --- A consequência da ausência de corte, na etapa em que a decisão é tomada (032, FR-462) -----
#
# **Mora aqui porque é o cartão do marco**, que é o que este arquivo já guarda: o método do sorteio
# e o corte são os dois blocos que a composição desenha e que nenhuma tela posterior edita.
#
# A auditoria de 16/09/2026 mediu o silêncio (`ACH-46`). O cartão dizia *"sem corte, a Etapa
# seguinte recebe todos os habilitados"* — verdade, e a metade menos importante. A consequência que
# decide é a outra ponta da cadeia: **sem corte não há convocação**. Dizê-la só na Revisão seria
# dizê-la depois; `SC-162` pede que ela esteja onde a decisão é tomada.


def _tela(client, edital):
    return client.get(
        reverse("interface:compor-etapa", args=[edital.id, "classificacao"])
    ).content.decode()


@pytest.mark.django_db
@pytest.mark.integration
def test_o_cartao_do_marco_declara_que_sem_corte_nao_ha_convocacao(client, com_etapas):
    """`FR-462` e `SC-162`: verificável na composição, sem abrir a Revisão."""
    from tests.interface.conftest import identificar

    identificar(client, "ana.elaboradora", ["elaborador"])
    # O marco atravessa **sem** campo algum de corte: é o estado de quem ainda não decidiu.
    assert _compor(client, com_etapas).status_code in (200, 302)

    corpo = _tela(client, com_etapas)

    ajuda = re.search(r'<span class="oculto" id="ajuda-corte-[^"]*">(.*?)</span>', corpo, re.S)
    assert ajuda, "o cartão precisa continuar descrevendo o que a ausência de corte significa"
    frase = re.sub(r"\s+", " ", ajuda.group(1))
    # `convoca`, e não `convocação`: o cartão é microcópia e escreve a consequência como verbo —
    # *"classifica e não convoca"*. O radical casa com as duas grafias, e prender a substantivada
    # prenderia na tela uma escolha de redação que não é requisito.
    assert "convoca" in frase, (
        "a consequência que decide é a convocação, e era ela que o cartão não dizia"
    )
    assert "faixa" in frase, "a cadeia passa pela faixa: sem faixa não há quem convocar"


@pytest.mark.django_db
@pytest.mark.integration
def test_a_explicacao_longa_do_corte_fica_no_como_preencher_e_nao_no_cartao(client, com_etapas):
    """A rubrica de microcópia deste repositório, e ela é o motivo de a frase do cartão ser curta.

    O cartão declara a consequência; **o porquê inteiro** — o que é faixa, o que é geração, o que
    muda entre continuar e não continuar — mora no `como-preencher` da etapa, que é onde a pessoa
    vai quando quer entender em vez de decidir.
    """
    from tests.interface.conftest import identificar

    identificar(client, "ana.elaboradora", ["elaborador"])
    _compor(client, com_etapas)

    corpo = _tela(client, com_etapas)

    explicacao = re.search(r"cutTargetKind\">Regra de corte</a></dt>\s*<dd>(.*?)</dd>", corpo, re.S)
    assert explicacao, "o `como-preencher` da etapa precisa continuar tratando da regra de corte"
    assert "convocação" in re.sub(r"\s+", " ", explicacao.group(1))


# --- A composição ensina a forma que o motor exige (035, US1) -----------------------------------
#
# **Acrescentado ao fim, e não no meio**: o que está acima guarda a `021`, a `026` e a `030`, e
# reescrever qualquer daqueles casos apagaria regressão que ninguém reporia. O que estas quatro
# acrescentam é a outra metade da mesma tela — a que ela **ensina**, e não a que ela grava.
#
# A tela recusava o algoritmo fora do vocabulário desde a `021` e não dizia qual era o vocabulário;
# e não dizia nada sobre a ocorrência, que é o único campo em que errar impede o sorteio de rodar.


def _com_marco_de_sorteio(client, edital):
    """O cartão do método só existe depois de a forma da ordem ser declarada (030, FR-414)."""
    _compor(client, edital, **{f"marco-{PERFIL}-0-orderProduction": "POR_SORTEIO"})
    return client.get(
        reverse("interface:compor-etapa", args=[edital.id, "classificacao"])
    ).content.decode()


def test_o_algoritmo_e_a_fonte_do_marco_sao_escolhidos_e_nao_digitados(client, com_etapas):
    """`FR-507` — a escolha impede que o valor inválido seja **escrito**, e não só gravado."""
    import re as _re

    corpo = _com_marco_de_sorteio(client, com_etapas)

    for campo in ("algorithm", "source"):
        nome = f"marco-{PERFIL}-0-draw-{campo}"
        assert _re.search(rf'<select[^>]*name="{nome}"', corpo), f"{campo} continua digitável"
        assert not _re.search(rf'<input[^>]*name="{nome}"', corpo), f"{campo} ainda é digitável"
    # E as opções saem de quem executa, e não de uma lista escrita no template.
    assert "IFES-SORTEIO-SHA256-v1" in corpo
    assert "Loteria Federal" in corpo and "Fonte de demonstração" in corpo


def test_o_algoritmo_e_a_fonte_do_metodo_comum_tambem_sao_escolhidos(client, com_etapas):
    """`FR-507` nas duas telas: o comum governa todo marco que não declara o próprio."""
    import re as _re

    corpo = client.get(
        reverse("interface:compor-etapa", args=[com_etapas.id, "classificacao"])
    ).content.decode()

    for nome in ("edital-draw-algorithm", "edital-draw-source"):
        assert _re.search(rf'<select[^>]*name="{nome}"', corpo), f"{nome} continua digitável"
        assert not _re.search(rf'<input[^>]*name="{nome}"', corpo)


def test_a_ocorrencia_ensina_forma_exemplo_e_consequencia(client, com_etapas):
    """`FR-508` e `FR-509` — a formulação é a do campo do instante, três linhas abaixo.

    As três frases são testadas uma a uma porque cada uma responde a um pedaço do requisito: a
    forma, o exemplo e a consequência. E a terceira é a que a varredura da amostra real mostrou ser
    a que mais importa — a forma natural de escrever duplica a fonte, e é justamente a que não roda.
    """
    corpo = _com_marco_de_sorteio(client, com_etapas)

    assert f'aria-describedby="ajuda-ocorrencia-{PERFIL}-0"' in corpo
    ajuda = corpo.split(f'id="ajuda-ocorrencia-{PERFIL}-0"', 1)[1].split("</span>", 1)[0]
    assert "terminando" in ajuda and "número" in ajuda, "a forma"
    assert "5900" in ajuda, "o exemplo"
    assert "deriva a ocorrência seguinte" in ajuda, "a consequência"
    assert "A fonte já está declarada" in ajuda, "e que ali vai só a referência"


def test_a_derivacao_em_prosa_continua_texto_livre_nas_duas_telas(client, com_etapas):
    """`FR-510` — o requisito que manda **não** fazer o que a auditoria parecia pedir.

    Ele é prosa normativa: sai no documento com o rótulo *Derivação*, e nenhum caminho de execução
    o lê — quem deriva é a regra de substituição, que já é vocabulário fechado. Trocá-lo por um
    código removeria do Edital a frase que diz a norma em português.
    """
    import re as _re

    corpo = _com_marco_de_sorteio(client, com_etapas)

    for nome in (f"marco-{PERFIL}-0-draw-derivation", "edital-draw-derivation"):
        assert _re.search(rf'<input[^>]*type="text"[^>]*name="{nome}"', corpo), (
            f"{nome} deixou de ser texto livre"
        )
        assert not _re.search(rf'<select[^>]*name="{nome}"', corpo)


def test_valor_fora_do_vocabulario_continua_legivel_e_nao_e_oferecido(client, com_etapas):
    """`FR-511` — o caminho é o rascunho criado a partir de Edital anterior.

    Se o vocabulário encolheu desde a publicação de origem, um `select` que só oferecesse o de hoje
    faria o campo parecer **vazio** num Edital que o declarou — e a gravação seguinte publicaria a
    ausência como se alguém a tivesse escolhido. Aqui ele aparece, identificado como o que veio da
    origem, e `disabled`: continua sendo submetido porque é o que está selecionado, e não pode ser
    escolhido por quem não o herdou.
    """
    from processo_seletivo.interface.templatetags.interface_extras import escolhas_do_metodo

    escolhas = escolhas_do_metodo("drawMethod/algorithm", "IFES-SORTEIO-MD5-v0")

    herdada = [escolha for escolha in escolhas if escolha["de_origem"]]
    assert len(herdada) == 1, "o valor da origem não aparece"
    assert herdada[0]["valor"] == "IFES-SORTEIO-MD5-v0"
    assert herdada[0]["selecionado"] is True, "o campo pareceria vazio num Edital que o declarou"
    assert "veio do Edital de origem" in herdada[0]["rotulo"]
    assert [escolha["valor"] for escolha in escolhas if not escolha["de_origem"]] == [
        "IFES-SORTEIO-SHA256-v1"
    ], "e o vocabulário de hoje continua o que é"


def test_o_valor_de_hoje_nao_e_marcado_como_vindo_da_origem(client, com_etapas):
    """A contraprova da anterior: sem ela, tudo seria 'da origem' e o rótulo não diria nada."""
    from processo_seletivo.interface.templatetags.interface_extras import escolhas_do_metodo

    escolhas = escolhas_do_metodo("drawMethod/source", "Loteria Federal")

    assert not any(escolha["de_origem"] for escolha in escolhas)
    selecionadas = [escolha["valor"] for escolha in escolhas if escolha["selecionado"]]
    assert selecionadas == ["Loteria Federal"]


def test_a_opcao_herdada_nao_e_disabled_porque_disabled_nao_e_submetido(client, com_etapas):
    """A armadilha que a primeira escrita da `FR-511` caiu, medida no navegador.

    `<option selected disabled>` dá `select.value == "HERDADO"` e `FormData.get(campo) == null`: o
    valor **não é submetido**. Desabilitar a opção para impedir que ela fosse escolhida produziria
    exatamente a perda que a `FR-511` existe para impedir — o valor herdado sumiria na gravação
    seguinte, em silêncio, e o Edital publicaria a ausência como se alguém a tivesse escolhido.

    **Nenhum teste de Python pega isso sozinho**: eles afirmam sobre o HTML renderizado, e não sobre
    o que o navegador envia. Este afirma sobre o atributo, que é o que se pode afirmar daqui — e é
    o irmão da asserção que `test_round_trip_do_rascunho.py` já fazia sobre o campo oculto, pela
    mesma razão e com as mesmas palavras.

    O que impede a opção herdada de ser escolha **válida** é outra coisa, e já existia: o rótulo
    diz que o sistema não a executa, e `_validar_algoritmo_publicado` recusa ao gravar.
    """
    import re as _re

    corpo = _com_marco_de_sorteio(client, com_etapas)

    for campo in ("algorithm", "source"):
        nome = f"marco-{PERFIL}-0-draw-{campo}"
        escolha = _re.search(rf'<select[^>]*name="{nome}"[^>]*>(.*?)</select>', corpo, _re.S)
        assert escolha, nome
        assert "disabled" not in escolha.group(1), (
            "opção `disabled` não é submetida pelo navegador: seria a perda da FR-511"
        )
