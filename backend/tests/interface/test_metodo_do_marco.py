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

    # O `<input>` inteiro, e não a dupla `name="…" value="…"`: o template quebra os atributos em
    # duas linhas, e uma asserção sobre a vizinhança deles passaria a depender do recuo.
    import re as _re

    def _valor(nome):
        achado = _re.search(rf'<input[^>]*name="{nome}"[^>]*>', corpo, _re.S)
        assert achado, f"a tela não reexibe {nome}"
        return _re.search(r'value="([^"]*)"', achado.group(0)).group(1)

    assert _valor("edital-draw-algorithm") == "IFES-SORTEIO-SHA256-v1"
    assert _valor("edital-draw-occurrence") == "5900"
    assert _valor("edital-draw-derivation") == "a extração de sábado anterior à data publicada"
    assert _valor("edital-draw-substitutionText") == "", "o que faltava continua faltando"
    com_etapas.refresh_from_db()
    assert com_etapas.metodo_de_sorteio_comum == {}, "e nada foi gravado"
