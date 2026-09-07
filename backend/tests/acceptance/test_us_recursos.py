"""O roteiro do quickstart da 018, percorrido pelo canal real e alternando atores.

O quickstart diz o que a auditoria exploratória repete à mão; este módulo é o que a suíte reproduz
sozinha. Ele atravessa as telas de verdade — portal e gestão, HTTP, templates, sessão —, e não os
comandos por baixo: o que se prova aqui é que **o percurso existe**, e não que cada regra vale.
Cada regra tem o seu teste, e é lá que ela é medida.

```text
resultado divulgado
  → Helena vê o próprio Resultado da Etapa            (1)
  → recorre e recebe protocolo                        (2)
  → quem produziu o ato é recusado                    (3)
  → a autoridade elegível admite e julga com motivo   (4, 5)
  → o Resultado é superado, sem alterar nada          (5)
  → o ato fica obsoleto e a publicação é bloqueada    (6)
  → a reabilitação aparece nomeada na Etapa seguinte  (7)
```

**Um teste, e não dez.** O percurso é uma coisa só: quebrá-lo em dez casos independentes exigiria
remontar o cenário inteiro dez vezes — e, pior, deixaria de provar justamente o que ele existe para
provar, que é a **sequência** funcionar de ponta a ponta com os atores se alternando.
"""

import re
from decimal import Decimal

import pytest
from django.urls import reverse

from processo_seletivo.classificacao.application.selectors import estado_do_marco
from processo_seletivo.classificacao.domain.universo import SUPERACAO
from processo_seletivo.divulgacao.domain.publicabilidade import DESATUALIZADO, aferir
from processo_seletivo.recursos.models import DecisaoRecurso, Recurso
from processo_seletivo.resultados.models import ResultadoEtapa
from tests.conftest import ator_institucional
from tests.fixtures.divulgacao import (
    emitir,
    entrar_como_titular,
    montar_marco,
    pontuar,
    publicar_o_ato,
)
from tests.fixtures.recursos_us4 import assinatura_de
from tests.interface.conftest import identificar

pytestmark = [pytest.mark.acceptance, pytest.mark.django_db(transaction=True)]

JULGADORA = "julia.julgadora"
PRESIDENTE = "carlos"


def conteudo(resposta):
    achado = re.search(r"<main[^>]*>(.*)</main>", resposta.content.decode(), re.DOTALL)
    return achado.group(1) if achado else resposta.content.decode()


@pytest.fixture
def certame(gestor, api_client, manager_headers, process_payload):
    """O estado que a 017 já sabe produzir: marco publicado, com uma eliminada na Etapa 1.

    Helena é a eliminada — 55 numa Etapa de mínima 60 —, e é ela que o roteiro segue.
    """
    cenario = montar_marco(
        gestor,
        api_client,
        manager_headers,
        process_payload,
        seed=140,
        codigo="0840",
        com_intermediario=True,
        regra_da_etapa={"minimumScore": "60.0000", "eliminatory": True},
    )
    cenario["inscricoes"] = pontuar(
        cenario,
        gestor,
        ["55.0000", "90.0000"],
        primeiro=1401,
        sufixo="140",
        etapa=cenario["primeira"],
    )
    cenario["ato"] = emitir(
        cenario, gestor, marco=cenario["marco_intermediario"], chave="emitir-roteiro"
    )
    cenario["publicacao"] = publicar_o_ato(cenario, chave="publicar-roteiro", ato=cenario["ato"])
    cenario["helena"], cenario["ana"] = cenario["inscricoes"]
    return cenario


def test_o_roteiro_do_quickstart_de_ponta_a_ponta(client, seletor_ligado, certame):
    helena = certame["helena"]
    etapa = certame["primeira"]

    # ---- 1. Helena finalmente vê o que aconteceu com ela -------------------------------------
    entrar_como_titular(client, helena)
    acompanhamento = reverse("portal:acompanhamento", args=[helena.id])
    corpo = conteudo(client.get(acompanhamento))

    assert "Resultado das etapas" in corpo
    assert "Eliminada" in corpo
    assert "nota mínima" in corpo, "o motivo escrito, e não só a consequência"
    # O que ela **não** vê: Resultado de terceiro (FR-017).
    assert certame["ana"].protocolo not in corpo

    # ---- 2. Helena recorre ------------------------------------------------------------------
    assert "Recorrer de um resultado" in corpo
    alvo = ResultadoEtapa.vigentes.get(inscricao=helena, etapa_id=etapa)
    envio = {
        "objeto": f"resultado:{alvo.id}",
        "fundamentacao": "A prova didática entregue não foi considerada no parecer.",
    }
    recorrer = reverse("portal:recorrer", args=[helena.id])
    assert client.post(recorrer, envio).status_code == 302

    peca = Recurso.objects.get(inscricao=helena)
    assert peca.protocolo.startswith("REC-")
    comprovante = conteudo(client.get(reverse("portal:recurso", args=[peca.id])))
    assert peca.protocolo in comprovante
    assert "Aguardando análise de admissibilidade" in comprovante

    # Reenviar o formulário: um recurso só (SC-003).
    client.post(recorrer, envio)
    assert Recurso.objects.filter(inscricao=helena).count() == 1
    # Recorrer de novo, com outra razão: recusado nomeando o protocolo da primeira (SC-004).
    repetida = client.post(recorrer, {**envio, "fundamentacao": "Outra razão."})
    assert "Você já recorreu" in conteudo(repetida)
    assert peca.protocolo in conteudo(repetida)

    # ---- 3. Quem produziu o ato não julga ---------------------------------------------------
    identificar(client, PRESIDENTE, ["julgador"])
    tela_da_peca = reverse("interface:recurso", args=[peca.id])
    corpo = conteudo(client.get(tela_da_peca))

    assert "Você não pode julgar este recurso" in corpo
    assert "consolidou" in corpo
    assert "Não admitir" not in corpo, "o botão não é oferecido a quem está impedido"

    # Sem a capacidade, não alcança recurso nenhum (SC-006).
    identificar(client, "alice.avaliadora", ["gestor"])
    assert client.get(tela_da_peca).status_code == 403

    # ---- 4. A admissibilidade ---------------------------------------------------------------
    identificar(client, JULGADORA, ["julgador"])
    corpo = conteudo(client.get(tela_da_peca))
    assinatura = re.search(r'name="assinatura" value="([^"]+)"', corpo).group(1)

    admitir = reverse("interface:recurso-admitir", args=[peca.id])
    resposta = client.post(
        admitir,
        {
            "admitido": "sim",
            "motivo": "Tempestivo e regularmente instruído.",
            "assinatura": assinatura,
        },
    )
    assert resposta.status_code == 302

    entrar_como_titular(client, helena)
    corpo = conteudo(client.get(reverse("portal:recurso", args=[peca.id])))
    assert "Admitido, aguardando julgamento" in corpo
    assert "Tempestivo e regularmente instruído." in corpo

    # ---- 5. Deferir fixando a correção ------------------------------------------------------
    identificar(client, JULGADORA, ["julgador"])
    # A opção da tela carrega `etapa|resultado`: a Etapa alcançada e a assinatura do Resultado
    # vigente que ela leu para aquela Etapa (FR-100).
    resposta = client.post(
        reverse("interface:recurso-julgar", args=[peca.id]),
        {
            "especie": "CORRECAO_FIXADA",
            "motivacao": "O parecer não enfrentou o documento juntado na inscrição.",
            "etapa": f"{etapa}|{alvo.id}",
            f"pontuacao-{etapa}": "82.0000",
        },
    )
    assert resposta.status_code == 302

    decisao = DecisaoRecurso.objects.get(recurso=peca)
    sucessor = ResultadoEtapa.vigentes.get(inscricao=helena, etapa_id=etapa)
    assert decisao.especie == DecisaoRecurso.Especie.CORRECAO_FIXADA
    assert sucessor.resultado_anterior_id == alvo.id
    assert sucessor.consequencia == ResultadoEtapa.Consequencia.HABILITADA

    # O anterior permanece **intacto** — superar não é reescrever.
    alvo.refresh_from_db()
    assert alvo.pontuacao == Decimal("55.0000")
    assert alvo.consequencia == ResultadoEtapa.Consequencia.ELIMINADA

    # E a tela da peça mostra os dois lados da correção, numa jornada só (FR-092).
    corpo = conteudo(client.get(tela_da_peca))
    assert "Recurso deferido — o resultado foi corrigido" in corpo
    assert "Efeito sobre o resultado" in corpo

    # ---- 6. A cadeia a jusante reage sozinha ------------------------------------------------
    situacao = estado_do_marco(edital=certame["edital"], marco_id=certame["marco_intermediario"])
    assert situacao["obsoleto"] is True
    assert any(SUPERACAO in item["descricao"] for item in situacao["divergencias"])

    afericao = aferir(
        edital=certame["edital"],
        marco_id=certame["marco_intermediario"],
        ato=certame["ato"],
    )
    assert afericao.codigo == DESATUALIZADO
    assert "ato sucessor" in afericao.mensagem, "a recusa nomeia o caminho"

    # ---- 7. A progressão retroativa aparece -------------------------------------------------
    identificar(client, PRESIDENTE, ["gestor"])
    mesa = reverse("interface:distribuicao", args=[certame["edital"].id, certame["segunda"]])
    corpo = conteudo(client.get(mesa))

    assert "Reabilitada por recurso" in corpo
    assert peca.protocolo in corpo


def test_o_candidato_le_a_decisao_em_linguagem_institucional(client, seletor_ligado, certame):
    """O fecho do percurso, do lado de quem recorreu: a espécie chega em texto (SC-021).

    Separado do roteiro porque prova outra coisa — não que o percurso funciona, mas que o que sai
    dele é legível. `CORRECAO_FIXADA` na tela do candidato seria a fronteira da FR-048 rompida.
    """
    from processo_seletivo.recursos.application.admitir import admitir
    from processo_seletivo.recursos.application.interpor import interpor
    from processo_seletivo.recursos.application.julgar import julgar

    helena = certame["helena"]
    alvo = ResultadoEtapa.vigentes.get(inscricao=helena, etapa_id=certame["primeira"])
    peca = _interpor(interpor, helena, alvo)
    admitir(
        actor=ator_institucional(JULGADORA, "recurso:julgar"),
        recurso_id=peca.id,
        admitido=True,
        motivo="Tempestivo.",
        assinatura_do_estado=assinatura_de(peca),
        idempotency_key="admitir-roteiro-b",
    )
    julgar(
        actor=ator_institucional(JULGADORA, "recurso:julgar"),
        recurso_id=peca.id,
        especie=DecisaoRecurso.Especie.CORRECAO_FIXADA,
        motivacao="O parecer não enfrentou o documento juntado.",
        etapa_id=certame["primeira"],
        pontuacao=Decimal("82.0000"),
        assinatura_do_resultado=str(alvo.id),
        idempotency_key="julgar-roteiro-b",
    )

    entrar_como_titular(client, helena)
    corpo = conteudo(client.get(reverse("portal:recurso", args=[peca.id])))

    assert "Recurso deferido — o resultado foi corrigido" in corpo
    assert "CORRECAO_FIXADA" not in corpo
    assert str(peca.id) not in corpo

    # E o acompanhamento explica a correção, em vez de mostrar a nota nova sem dizer por quê.
    acompanhamento = conteudo(client.get(reverse("portal:acompanhamento", args=[helena.id])))
    assert "Resultado corrigido" in acompanhamento
    assert peca.protocolo in acompanhamento


def _interpor(interpor, inscricao, alvo):
    from processo_seletivo.portal.identidade import IdentidadeDoCandidato

    return interpor(
        identidade=IdentidadeDoCandidato(
            inscricao.identity_subject, inscricao.nome, inscricao.cpf_normalizado, "h@ex.br"
        ),
        inscricao=inscricao,
        resultado=alvo,
        fundamentacao="A prova didática entregue não foi considerada no parecer.",
        assinatura_do_objeto=str(alvo.pk),
        idempotency_key="interpor-roteiro-b",
    )
