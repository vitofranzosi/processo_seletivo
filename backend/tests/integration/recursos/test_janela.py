"""A janela aplicada — dentro do prazo interpõe, depois do prazo não, e sem declaração não há prazo.

```text
declarada e aberta    interpõe, e a peça grava os dois instantes
declarada e fechada   recusa citando a norma, a abertura e o encerramento
não declarada         interpõe enquanto o objeto for vigente — e nada é exibido nem aplicado
dois marcos           basta que QUALQUER janela esteja aberta
```

**A janela é gravada na peça, e não recalculada depois** (FR-024): recalcular na leitura responderia
com a norma de hoje sobre um ato de ontem.

**Sem declaração, ninguém inventa prazo** (FR-028). É a degradação que a decisão institucional
escolheu, e não um estado transitório: a tempestividade volta a ser juízo de admissibilidade
motivado, e o candidato conserva o direito de recorrer enquanto o objeto for o vigente.
"""

import json
from datetime import timedelta

import pytest
from django.utils import timezone

from processo_seletivo.recursos.models import Recurso
from processo_seletivo.resultados.models import ResultadoEtapa
from processo_seletivo.shared.api.problems import DomainError
from tests.fixtures.divulgacao import emitir, montar_marco, pontuar, publicar_o_ato

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.integration]

JANELA_DE_CINCO = {"admits": True, "durationDays": 5, "unit": "DIAS_CORRIDOS"}


def montar(gestor, api_client, manager_headers, process_payload, *, seed, codigo, janela=None):
    cenario = montar_marco(
        gestor,
        api_client,
        manager_headers,
        process_payload,
        seed=seed,
        codigo=codigo,
        regra_da_etapa={"minimumScore": "60.0000", "eliminatory": True},
    )
    cenario["inscricoes"] = pontuar(
        cenario, gestor, ["55.0000", "90.0000"], primeiro=seed * 10 + 1, sufixo=str(seed)
    )
    if janela is not None:
        _declarar_janela(cenario, cenario["marco"], janela)
    cenario["ato"] = emitir(cenario, gestor, chave=f"emitir-janela-{seed}")
    cenario["publicacao"] = publicar_o_ato(cenario, chave=f"publicar-janela-{seed}")
    return cenario


def _declarar_janela(cenario, marco_id, janela):
    """Declara a janela **no conteúdo publicado**, que é onde a norma mora.

    Pela via curta, e é deliberado: o que estes testes exercitam é a **aplicação** da janela, e o
    caminho de elaboração já é exercitado por `tests/contract/test_elevacao_degrau_8.py` e pelo
    formulário do marco. Montá-lo aqui de novo tornaria cada caso três vezes mais lento sem provar
    nada a mais.
    """
    versao = cenario["edital"].versoes_consolidadas.latest("materialized_at")
    conteudo = versao.content
    for perfil in conteudo.get("profiles") or []:
        for marco in perfil.get("classificationMilestones") or []:
            if str(marco.get("id")) == str(marco_id):
                marco["appealWindow"] = janela
    _escrever_direto(
        "publicacoes_versaoconsolidada",
        "versao_consolidada_append_only",
        "UPDATE publicacoes_versaoconsolidada SET content = %s WHERE id = %s",
        [json.dumps(conteudo), versao.pk],
    )


def _enumerar_etapa(cenario, marco_id, etapa_id):
    """Faz o marco enumerar também aquela Etapa, no conteúdo publicado."""
    versao = cenario["edital"].versoes_consolidadas.latest("materialized_at")
    conteudo = versao.content
    for perfil in conteudo.get("profiles") or []:
        for marco in perfil.get("classificationMilestones") or []:
            if str(marco.get("id")) == str(marco_id) and str(etapa_id) not in marco["stages"]:
                marco["stages"] = [str(etapa_id), *marco["stages"]]
    _escrever_direto(
        "publicacoes_versaoconsolidada",
        "versao_consolidada_append_only",
        "UPDATE publicacoes_versaoconsolidada SET content = %s WHERE id = %s",
        [json.dumps(conteudo), versao.pk],
    )


def _escrever_direto(tabela, gatilho, comando, parametros):
    """Escreve num agregado append-only, com o gatilho desligado pelo tempo da escrita.

    **Não é contorno da garantia**: é o único jeito de exercitar hoje o efeito de uma norma
    publicada há dez dias e de um Edital que declarou janela — sem esperar dez dias, e sem montar o
    caminho de Retificação inteiro, que já tem testes próprios. O que se prova aqui é a
    **aplicação** da janela, e ela lê o que o banco tem.
    """
    from django.db import connection

    with connection.cursor() as cursor:
        cursor.execute(f"ALTER TABLE {tabela} DISABLE TRIGGER {gatilho}")
        cursor.execute(comando, parametros)
        cursor.execute(f"ALTER TABLE {tabela} ENABLE TRIGGER {gatilho}")


def interpor_como_titular(cenario, inscricao, *, chave="interpor-janela"):
    from processo_seletivo.portal.identidade import IdentidadeDoCandidato
    from processo_seletivo.recursos.application.interpor import interpor

    alvo = ResultadoEtapa.vigentes.get(inscricao=inscricao, etapa_id=cenario["etapa"])
    return interpor(
        identidade=IdentidadeDoCandidato(
            inscricao.identity_subject, inscricao.nome, inscricao.cpf_normalizado, "c@ex.br"
        ),
        inscricao=inscricao,
        resultado=alvo,
        fundamentacao="A prova didática entregue não foi considerada.",
        assinatura_do_objeto=str(alvo.pk),
        idempotency_key=chave,
    )


def _envelhecer(publicacao, dias):
    """Empurra a publicação para o passado, para que a janela feche sem esperar o relógio."""
    _escrever_direto(
        "divulgacao_publicacaoresultado",
        "publicacao_resultado_append_only",
        "UPDATE divulgacao_publicacaoresultado SET publicado_em = %s WHERE id = %s",
        [timezone.now() - timedelta(days=dias), publicacao.pk],
    )
    publicacao.refresh_from_db()


# ---------------------------------------------------------------------------
# T115 — dentro e fora do prazo
# ---------------------------------------------------------------------------


def test_dentro_do_prazo_a_peca_nasce_e_grava_os_dois_instantes(
    gestor, api_client, manager_headers, process_payload
):
    cenario = montar(
        gestor,
        api_client,
        manager_headers,
        process_payload,
        seed=133,
        codigo="0833",
        janela=JANELA_DE_CINCO,
    )

    peca = interpor_como_titular(cenario, cenario["inscricoes"][0])

    assert peca.janela_abriu_em is not None
    assert peca.janela_fecha_em is not None
    assert peca.janela_abriu_em <= peca.interposto_em <= peca.janela_fecha_em


def test_depois_do_prazo_a_interposicao_e_recusada_citando_a_norma(
    gestor, api_client, manager_headers, process_payload
):
    """A recusa nomeia o prazo, a abertura e o encerramento — e não só "fora do prazo".

    Quem recebe "não é possível" sem saber qual era o prazo não tem como conferir se o sistema
    acertou, e é justamente a contagem que a pessoa tem direito de auditar.
    """
    cenario = montar(
        gestor,
        api_client,
        manager_headers,
        process_payload,
        seed=134,
        codigo="0834",
        janela=JANELA_DE_CINCO,
    )
    _envelhecer(cenario["publicacao"], dias=10)

    with pytest.raises(DomainError) as recusa:
        interpor_como_titular(cenario, cenario["inscricoes"][0], chave="fora-do-prazo")

    assert recusa.value.code == "appeal_window_closed"
    assert recusa.value.status == 422
    assert "5 dias corridos" in recusa.value.detail
    assert not Recurso.objects.exists()


def test_fora_do_prazo_a_acao_nao_e_oferecida_na_tela(
    client, gestor, api_client, manager_headers, process_payload
):
    """A recusa existe para quem chega por outro caminho, e não como o normal da tela (FR-013)."""
    import re

    from django.urls import reverse

    from tests.fixtures.divulgacao import entrar_como_titular

    cenario = montar(
        gestor,
        api_client,
        manager_headers,
        process_payload,
        seed=135,
        codigo="0835",
        janela=JANELA_DE_CINCO,
    )
    inscricao = cenario["inscricoes"][0]

    entrar_como_titular(client, inscricao)
    aberta = client.get(reverse("portal:acompanhamento", args=[inscricao.id])).content.decode()
    assert "Recorrer de um resultado" in aberta

    _envelhecer(cenario["publicacao"], dias=10)
    fechada = client.get(reverse("portal:acompanhamento", args=[inscricao.id])).content.decode()

    assert "Recorrer de um resultado" not in re.search(
        r"<main[^>]*>(.*)</main>", fechada, re.DOTALL
    ).group(1)


# ---------------------------------------------------------------------------
# T116 — vários marcos
# ---------------------------------------------------------------------------


def test_com_dois_marcos_basta_uma_janela_aberta(
    gestor, api_client, manager_headers, process_payload
):
    """Prazo que restringe direito interpreta-se a favor de quem recorre (FR-027).

    Dois marcos enumeram a mesma Etapa, e o prazo de um já venceu. Recusar aqui aplicaria contra o
    candidato o prazo mais curto entre dois que a instituição publicou — quando o mais longo também
    é norma dela.
    """
    cenario = montar_marco(
        gestor,
        api_client,
        manager_headers,
        process_payload,
        seed=136,
        codigo="0836",
        com_intermediario=True,
        regra_da_etapa={"minimumScore": "60.0000", "eliminatory": True},
    )
    cenario["inscricoes"] = pontuar(
        cenario,
        gestor,
        ["55.0000", "90.0000"],
        primeiro=1361,
        sufixo="136",
        etapa=cenario["primeira"],
    )
    # **Os dois marcos enumeram a mesma Etapa** — é a hipótese da FR-027. Sem isso o cenário não
    # exercita nada: só um marco teria janela pertinente, e a regra do "qualquer uma" sumiria.
    _enumerar_etapa(cenario, cenario["marco"], cenario["primeira"])
    _declarar_janela(
        cenario, cenario["marco_intermediario"], {**JANELA_DE_CINCO, "durationDays": 1}
    )
    _declarar_janela(cenario, cenario["marco"], {**JANELA_DE_CINCO, "durationDays": 30})

    curto = emitir(cenario, gestor, marco=cenario["marco_intermediario"], chave="emitir-curto")
    publicacao_curta = publicar_o_ato(cenario, chave="publicar-curto", ato=curto)
    _envelhecer(publicacao_curta, dias=5)
    longo = emitir(cenario, gestor, marco=cenario["marco"], chave="emitir-longo")
    publicar_o_ato(cenario, chave="publicar-longo", ato=longo)

    inscricao = cenario["inscricoes"][0]
    contexto = {**cenario, "etapa": cenario["primeira"]}
    peca = interpor_como_titular(contexto, inscricao, chave="dois-marcos")

    assert peca.janela_fecha_em is not None
    assert peca.janela_fecha_em >= peca.interposto_em


# ---------------------------------------------------------------------------
# T117 — a ausência
# ---------------------------------------------------------------------------


def test_sem_declaracao_nenhum_prazo_e_exibido_nem_aplicado(
    gestor, api_client, manager_headers, process_payload
):
    """A ausência é a afirmação certa: o sistema **não inventa prazo** (FR-028, SC-015)."""
    cenario = montar(gestor, api_client, manager_headers, process_payload, seed=137, codigo="0837")
    _envelhecer(cenario["publicacao"], dias=400)

    peca = interpor_como_titular(cenario, cenario["inscricoes"][0], chave="sem-janela")

    assert peca.janela_abriu_em is None
    assert peca.janela_fecha_em is None


def test_sem_declaracao_a_interposicao_segue_possivel_enquanto_o_objeto_for_vigente(
    gestor, api_client, manager_headers, process_payload
):
    """Quatrocentos dias depois, e ainda cabe: é o que "prazo não computável" significa."""
    from processo_seletivo.recursos.application.selectors import SEM_JANELA, recursos_do_edital

    cenario = montar(gestor, api_client, manager_headers, process_payload, seed=138, codigo="0838")
    _envelhecer(cenario["publicacao"], dias=400)

    interpor_como_titular(cenario, cenario["inscricoes"][0], chave="sem-janela-b")

    linha = recursos_do_edital(cenario["edital"])[0]
    assert linha["tempestividade"] == SEM_JANELA
    assert linha["tempestividade_rotulo"] == "Sem prazo computável"
