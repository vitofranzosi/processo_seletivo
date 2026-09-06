"""O quickstart inteiro, como a suíte o reproduz — o gate da spec, de ponta a ponta.

```text
classificação emitida → prévia → publicação → página pública
                      → candidata vê na própria Inscrição → documento
                      → P1 permanece histórica quando sucedida
```

O percurso alterna atores de propósito, porque é alternando que a feature se prova: a autoridade
publica pela interface, **qualquer pessoa** consulta pelo portal sem autenticar, e a candidata
encontra o resultado dentro da própria Inscrição. Nenhum dos três vê o que os outros veem.
"""

import re

import pytest
from django.test import Client
from django.urls import reverse

from processo_seletivo.divulgacao.models import PublicacaoResultado
from tests.fixtures.divulgacao import (
    emitir,
    entrar_como_titular,
    montar_ato_publicavel,
)
from tests.interface.conftest import identificar

pytestmark = [pytest.mark.acceptance, pytest.mark.django_db(transaction=True)]


def _conteudo(resposta):
    return re.search(r"<main[^>]*>(.*)</main>", resposta.content.decode(), re.DOTALL).group(1)


def _publicar_pela_tela(client, cenario, ato, *, natureza):
    """O caminho real: abre a prévia, tira dela a assinatura e a chave, e confirma."""
    previa = client.get(
        reverse(
            "interface:previa-de-publicacao",
            args=[cenario["edital"].id, cenario["marco"], ato.id],
        )
    )
    assert previa.status_code == 200, previa.content
    corpo = previa.content.decode()
    resposta = client.post(
        reverse(
            "interface:publicar-resultado",
            args=[cenario["edital"].id, cenario["marco"], ato.id],
        ),
        {
            "natureza": natureza,
            "autoridade": "diretoria-cefor",
            "confirmacao_da_previa": re.search(
                r'name="confirmacao_da_previa" value="([^"]+)"', corpo
            ).group(1),
            "chave_idempotencia": re.search(
                r'name="chave_idempotencia" value="([^"]+)"', corpo
            ).group(1),
        },
    )
    assert resposta.status_code == 302, resposta.content
    return corpo


def test_o_percurso_inteiro_da_divulgacao(
    gestor, api_client, manager_headers, process_payload, client, seletor_ligado
):
    cenario = montar_ato_publicavel(
        gestor,
        api_client,
        manager_headers,
        process_payload,
        seed=80,
        codigo="0780",
        pontuacoes=("90.0000", "80.0000", "80.0000", None),
        primeiro=1501,
    )
    ato = cenario["ato"]
    classificada, _, _, sem_posicao = cenario["inscricoes"]

    # ---- 1. A autoridade encontra a ação; quem emitiu, não -------------------------------------
    tela_do_ato = reverse(
        "interface:ato-de-ordenacao", args=[cenario["edital"].id, cenario["marco"], ato.id]
    )
    identificar(client, "paulo.presidente", ["gestor"])
    assert "Publicar resultado" not in client.get(tela_do_ato).content.decode(), (
        "emitir não concede publicar (SC-014)"
    )

    identificar(client, "paula.publicadora", ["publicador", "auditor"])
    assert "Publicar resultado" in client.get(tela_do_ato).content.decode()

    # ---- 2. A prévia: mostra o que será divulgado, e não grava nada ----------------------------
    corpo_da_previa = _publicar_pela_tela(client, cenario, ato, natureza="PRELIMINAR")
    assert "Candidata 1501" in corpo_da_previa
    assert "posição compartilhada" in corpo_da_previa, "1º, 2º, 2º aparecem como tais (SC-015)"
    assert "desempate" not in corpo_da_previa.lower()
    assert sem_posicao.nome not in re.search(
        r"O que será divulgado(.*)$", corpo_da_previa, re.DOTALL
    ).group(1)

    # ---- 3. Publicar: nasce o ato, com autor, instante e signatário ----------------------------
    preliminar = PublicacaoResultado.objects.get()
    assert preliminar.publicado_por == "paula.publicadora"
    assert preliminar.signatario_nome == "Diretora do Cefor"

    # ---- 4. A página pública: sem sessão nenhuma ------------------------------------------------
    publico = Client()
    pagina = _conteudo(publico.get(reverse("portal:resultado", args=[preliminar.id])))
    assert "Resultado preliminar" in pagina
    assert "Candidata 1501" in pagina and "1501" in pagina
    assert preliminar.publicado_em.astimezone().strftime("%d/%m/%Y") in pagina
    assert "Diretora do Cefor" in pagina

    # E quem só conhece o Edital chega até ela (SC-018).
    vitrine = _conteudo(publico.get(reverse("portal:selecao", args=[cenario["edital"].id])))
    assert reverse("portal:resultado", args=[preliminar.id]) in vitrine

    # ---- 5. A candidata, dentro da própria Inscrição --------------------------------------------
    dela = Client()
    entrar_como_titular(dela, classificada)
    area = _conteudo(dela.get(reverse("portal:acompanhamento", args=[classificada.id])))
    assert "1º lugar" in area
    assert "90,00" in area
    assert reverse("portal:resultado", args=[preliminar.id]) in area

    # E a considerada sem posição vê a própria situação — sem estar na lista pública (SC-020).
    outra = Client()
    entrar_como_titular(outra, sem_posicao)
    area_dela = _conteudo(outra.get(reverse("portal:acompanhamento", args=[sem_posicao.id])))
    assert "Você não foi classificado" in area_dela
    assert sem_posicao.nome not in pagina

    # ---- 6. O documento -------------------------------------------------------------------------
    from tests.interface.test_fluxo import texto_de_pdf_bytes

    baixado = publico.get(reverse("portal:resultado-documento", args=[preliminar.id]))
    assert baixado.status_code == 200
    assert baixado["ETag"] == f'"{preliminar.documento.documento_hash}"'
    documento = texto_de_pdf_bytes(baixado.content)
    assert cenario["edital"].number in documento
    assert "Classificação final" in documento
    assert "Resultado preliminar" in documento
    assert preliminar.conteudo_publico_hash in documento, "o resumo torna o papel conferível"
    assert "Candidata 1501" in documento

    # ---- 7. Obsolescência: o mesmo ato não se publica duas vezes na mesma natureza --------------
    identificar(client, "paula.publicadora", ["publicador", "auditor"])
    repetida = client.post(
        reverse(
            "interface:publicar-resultado",
            args=[cenario["edital"].id, cenario["marco"], ato.id],
        ),
        {
            "natureza": "PRELIMINAR",
            "autoridade": "diretoria-cefor",
            "confirmacao_da_previa": "0" * 64,
            "chave_idempotencia": "outra-chave-0780",
        },
    )
    # A recusa devolve o status do contrato, e não um redirect: o ato não aconteceu, e a resposta
    # diz isso (contracts/publicacao.md §4).
    assert repetida.status_code == 409
    assert PublicacaoResultado.objects.count() == 1

    # ---- 7b. A sucessão: o mesmo ato como definitivo, sem a 015 registrar sucessão vazia --------
    _publicar_pela_tela(client, cenario, ato, natureza="DEFINITIVA")
    definitiva = PublicacaoResultado.objects.get(natureza="DEFINITIVA")
    assert definitiva.publicacao_anterior_id == preliminar.id

    # P1 continua exatamente como era, no mesmo endereço, dizendo que foi sucedida.
    historica = _conteudo(publico.get(reverse("portal:resultado", args=[preliminar.id])))
    assert "foi sucedido" in historica
    assert reverse("portal:resultado", args=[definitiva.id]) in historica
    assert "Candidata 1501" in historica

    # E a Área da candidata passa a apontar para a vigente (FR-061).
    area_depois = _conteudo(dela.get(reverse("portal:acompanhamento", args=[classificada.id])))
    assert reverse("portal:resultado", args=[definitiva.id]) in area_depois
    assert "Resultado definitivo" in area_depois

    # ---- 8. A auditora abre o histórico do marco -------------------------------------------------
    auditora = Client()
    identificar(auditora, "aurora.auditora", ["auditor"])
    historico = auditora.get(
        reverse("interface:publicacoes-do-marco", args=[cenario["edital"].id, cenario["marco"]])
    ).content.decode()
    assert "Vigente" in historico and "Sucedida" in historico
    assert "Resultado preliminar" in historico and "Resultado definitivo" in historico
    assert "paula.publicadora" in historico
    assert "Publicar resultado" not in historico, "consultar é de dois; agir é de um"


def test_a_publicacao_e_consultavel_imediatamente_depois_de_confirmada(
    gestor, api_client, manager_headers, process_payload, client, seletor_ligado
):
    """FR-032 e SC-001: entre confirmar e ler não há passo intermediário nem espera.

    Não existe fila de indexação, geração assíncrona nem publicação agendada: quando o POST
    responde, o endereço público já responde também — e o documento também já existe.
    """
    cenario = montar_ato_publicavel(
        gestor,
        api_client,
        manager_headers,
        process_payload,
        seed=81,
        codigo="0781",
        pontuacoes=("90.0000",),
        primeiro=1601,
    )
    identificar(client, "paula.publicadora", ["publicador"])

    _publicar_pela_tela(client, cenario, cenario["ato"], natureza="DEFINITIVA")

    publicacao = PublicacaoResultado.objects.get()
    publico = Client()
    assert publico.get(reverse("portal:resultado", args=[publicacao.id])).status_code == 200
    assert (
        publico.get(reverse("portal:resultado-documento", args=[publicacao.id])).status_code == 200
    )


def test_o_ato_recusado_continua_consultavel_com_a_proveniencia_inteira(
    gestor, api_client, manager_headers, process_payload, client, seletor_ligado
):
    """SC-012 e SC-023: publicar é ato **a mais**, e não retira nada do que a 015 já dava."""
    cenario = montar_ato_publicavel(
        gestor,
        api_client,
        manager_headers,
        process_payload,
        seed=82,
        codigo="0782",
        pontuacoes=("90.0000", "70.0000"),
        primeiro=1701,
    )
    antigo = cenario["ato"]
    emitir(cenario, gestor, chave="emitir-0782-b", motivo="Resultado tardio.")

    identificar(client, "paula.publicadora", ["publicador"])
    recusa = client.get(
        reverse(
            "interface:previa-de-publicacao",
            args=[cenario["edital"].id, cenario["marco"], antigo.id],
        )
    ).content.decode()
    assert "Este ato não pode ser divulgado" in recusa
    assert "ato sucessor" in recusa, "a recusa nomeia o caminho (FR-006)"
    assert "Publicar este resultado" not in recusa

    identificar(client, "aurora.auditora", ["auditor"])
    consulta = client.get(
        reverse(
            "interface:ato-de-ordenacao", args=[cenario["edital"].id, cenario["marco"], antigo.id]
        )
    )
    corpo = consulta.content.decode()
    assert consulta.status_code == 200
    assert "Proveniência do ato" in corpo
    assert "Posições e valores de desempate" in corpo
    assert not PublicacaoResultado.objects.exists()
