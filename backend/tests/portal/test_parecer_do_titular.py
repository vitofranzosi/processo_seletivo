"""O parecer chega a quem foi avaliado — e só a ele, e só enquanto a regra diz (036, US1).

O sistema **exigia** o texto pela razão de servir ao candidato, **guardava** o texto, e **não o
entregava** a ele. Não era omissão de quem escreveu a regra da `012`: era a regra cumprida pela
metade, e é esta metade que a `US1` fecha.

```text
desfavorável + prazo aberto             →  aparece
desfavorável + peça contra ESSE          →  aparece, mesmo com o prazo fechado
  resultado ainda não decidida
prazo fechado E sem peça contra esse      →  some, E a tela diz por quê        (FR-524)
  resultado — peça contra OUTRO, ou
  contra a publicação, não contam
resultado favorável                       →  nada muda
sem parecer escrito                       →  a tela diz que não há            (FR-525)
```

**A segunda linha é a que o `analyze` acrescentou** (`D-001`), e a quarta é a que ela recorta:
prender só ao prazo tirava o parecer de quem recorreu enquanto o recurso dela corria — a pessoa que
a feature existe para servir, no momento em que ela mais precisa. E "recurso dele" sem recorte
reabriria o parecer de um resultado cujo prazo terminou há semanas, por causa de uma peça que não o
discute.
"""

import re
from datetime import timedelta
from unittest.mock import patch

import pytest
from django.urls import reverse
from django.utils import timezone
from django.utils.html import escape

from processo_seletivo.recursos.application.selectors import (
    NAO_HOUVE_PARECER,
    POR_QUE_SAIU,
    pareceres_do_titular,
)
from processo_seletivo.resultados.application.selectors import resultados_visiveis
from processo_seletivo.resultados.models import ResultadoEtapa
from tests.fixtures.divulgacao import entrar_como_titular
from tests.fixtures.instrucao import PARECER, cenario_instruivel

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.integration]

# Cinco dias corridos, contados da publicação: é a janela que o degrau 8 sabe computar, e a que
# permite a este arquivo exercitar o prazo **fechado** avançando o relógio da leitura.
JANELA = {"admits": True, "durationDays": 5, "unit": "DIAS_CORRIDOS"}


@pytest.fixture
def eliminada(raiz_de_arquivos, gestor, api_client, manager_headers, process_payload):
    """Eliminada por nota abaixo da mínima, com parecer escrito e recurso já interposto."""
    return cenario_instruivel(
        gestor,
        api_client,
        manager_headers,
        process_payload,
        seed=140,
        codigo="0840",
        janela_recursal=JANELA,
    )


def acompanhamento(client, inscricao):
    resposta = client.get(reverse("portal:acompanhamento", args=[inscricao.id]))
    assert resposta.status_code == 200
    corpo = resposta.content.decode()
    achado = re.search(r"<main[^>]*>(.*)</main>", corpo, re.DOTALL)
    return achado.group(1) if achado else corpo


def abrir_como_titular(client, inscricao):
    entrar_como_titular(client, inscricao)
    return acompanhamento(client, inscricao)


# --- O titular lê, e lê ao lado do motivo -------------------------------------------------------


def test_o_titular_le_o_parecer_do_proprio_resultado(client, eliminada):
    """`SC-182`: a frase que o avaliador escreveu, no canal do candidato."""
    corpo = abrir_como_titular(client, eliminada["inscricao"])

    assert PARECER in corpo


def test_o_parecer_vem_ao_lado_do_motivo_e_nao_no_lugar_dele(client, eliminada):
    """`FR-525a`. O motivo é a regra aplicada ao número; o parecer é a razão que a pessoa escreveu.

    As duas ficam, **e nesta ordem**: o número que sustenta a contestação primeiro, e a razão
    que se contesta depois. Substituir um pelo outro tiraria da tela metade do que a pessoa
    precisa para escrever a peça.
    """
    resultado = ResultadoEtapa.vigentes.get(
        inscricao=eliminada["inscricao"], etapa_id=eliminada["cenario"]["etapa_do_recurso"]
    )
    assert resultado.motivo, "o motivo é obrigatório por constraint desde a 013"
    # Escapado, porque o motivo traz `<` — *"55,0000 < 60,0000"* — e o template o escreve como
    # `&lt;`. Procurar o texto cru aqui falharia por causa da aritmética que o motivo cita, que é
    # justamente a parte que esta asserção existe para garantir que continua na tela.
    na_tela = escape(resultado.motivo)

    corpo = abrir_como_titular(client, eliminada["inscricao"])

    assert na_tela in corpo
    assert corpo.index(na_tela) < corpo.index(PARECER)
    # E identificado como o que é: sem rótulo, a segunda frase parece um segundo motivo.
    assert "Fundamentação escrita por quem avaliou" in corpo


def test_o_resultado_favoravel_nao_muda_nada(client, eliminada):
    """Esta feature alcança o desfavorável, que é o recorte que a regra do parecer já descreve."""
    habilitada = eliminada["outra_inscricao"]
    resultado = ResultadoEtapa.vigentes.get(
        inscricao=habilitada, etapa_id=eliminada["cenario"]["etapa_do_recurso"]
    )
    assert resultado.consequencia == ResultadoEtapa.Consequencia.HABILITADA

    corpo = abrir_como_titular(client, habilitada)

    assert "Fundamentação escrita por quem avaliou" not in corpo
    assert POR_QUE_SAIU not in corpo
    assert NAO_HOUVE_PARECER not in corpo


# --- As duas condições da FR-522, e o recorte da segunda (D-001) --------------------------------


def depois_do_prazo():
    """O instante em que a janela de cinco dias já fechou — a leitura, e não o ato.

    O relógio é avançado **na leitura**, e é a mesma técnica que a `021` usa para exercitar prazo
    vencido: a publicação existe no instante em que existiu, e o que muda é quando se pergunta. O
    caminho oposto — reescrever `publicado_em` — exigiria desligar a trigger de um agregado
    append-only para afirmar um fato falso sobre quando a instituição publicou.
    """
    return timezone.now() + timedelta(days=10)


def test_com_o_prazo_fechado_e_a_peca_dele_em_curso_o_parecer_permanece(client, eliminada):
    """A contraprova da segunda condição (`D-001`), e é a que o `analyze` acrescentou.

    Quem recorreu decide se insiste, escreve réplica ou aceita a decisão — e fazer isso sem poder
    reler o texto que está contestando é o defeito desta feature acontecendo um passo adiante. **E
    foi o sistema que o obrigou a recorrer contra aquele texto.**
    """
    assert eliminada["recurso"].resultado_atacado_id is not None
    assert not eliminada["recurso"].decisoes.exists()

    with patch("django.utils.timezone.now", return_value=depois_do_prazo()):
        corpo = abrir_como_titular(client, eliminada["inscricao"])

    assert PARECER in corpo
    assert POR_QUE_SAIU not in corpo


def test_com_as_duas_condicoes_encerradas_o_parecer_sai_e_a_tela_diz_por_que(
    client, raiz_de_arquivos, gestor, api_client, manager_headers, process_payload
):
    """`FR-524` — **o cenário que separa a feature de um defeito.**

    Sumir em silêncio faria a pessoa pensar que perdeu algo que nunca teve, ou que o sistema
    falhou. O custo de perder acesso à razão da própria eliminação está dito por escrito na
    `D-001`; esta frase é o que impede o custo de virar defeito.
    """
    montado = cenario_instruivel(
        gestor,
        api_client,
        manager_headers,
        process_payload,
        seed=141,
        codigo="0841",
        janela_recursal=JANELA,
    )
    from tests.fixtures.instrucao import decidir_a_peca

    inscricao = montado["inscricao"]
    # **A peça do cenário é decidida**, e é o que encerra a segunda condição: com ela viva, o
    # parecer continuaria aparecendo — corretamente, e é o caso do teste anterior.
    decidir_a_peca(montado)

    with patch("django.utils.timezone.now", return_value=depois_do_prazo()):
        corpo = abrir_como_titular(client, inscricao)

    assert PARECER not in corpo
    assert POR_QUE_SAIU in corpo
    # **E não em silêncio**: a frase diz que o texto continua registrado, porque nada foi apagado.
    assert "continua registrado" in corpo


def test_peca_contra_outro_resultado_nao_reabre_este_parecer(client, eliminada):
    """`D-001`: a segunda condição pende do **resultado atacado**, e não de haver peça qualquer.

    Uma peça sobre outra Etapa reabriria o parecer de um resultado cujo prazo terminou há
    semanas — acesso a dado pessoal concedido por um fato que nada tem a ver com ele, que é
    minimização perdida sem que ninguém decidisse perdê-la.
    """
    from tests.fixtures.instrucao import decidir_a_peca

    inscricao = eliminada["inscricao"]
    atacado = eliminada["superado"]
    decidir_a_peca(eliminada)

    # Uma peça viva da mesma pessoa, contra **outro** objeto: a publicação do marco.
    from processo_seletivo.publicacoes.application.selectors import selecao_publica
    from tests.fixtures.recursos import interpor as interpor_curto

    outra = interpor_curto(
        inscricao=inscricao,
        versao=selecao_publica(edital_id=inscricao.edital_id),
        publicacao=eliminada["publicacao"],
        protocolo="REC-2026-OUTRO0140",
    )
    assert not outra.decisoes.exists()
    assert outra.resultado_atacado_id is None

    with patch("django.utils.timezone.now", return_value=depois_do_prazo()):
        corpo = abrir_como_titular(client, inscricao)

    assert PARECER not in corpo
    assert POR_QUE_SAIU in corpo
    # E a leitura do seletor diz a mesma coisa, sobre aquele Resultado nomeadamente.
    lido = pareceres_do_titular(inscricao, resultados_visiveis(inscricao), agora=depois_do_prazo())
    assert lido[atacado.pk]["estado"] == "encerrado"


# --- A ausência, dita (FR-525) -----------------------------------------------------------------


def test_sem_parecer_escrito_a_tela_diz_que_nao_ha(
    client, gestor, api_client, manager_headers, process_payload
):
    """A ausência é real, e calar sobre ela é pior do que declará-la (`FR-525`).

    **E o caso não é o que a primeira redação deste teste tentou montar.** Concluir avaliação
    eliminatória com nota abaixo da mínima **sem** parecer é recusado pelo domínio desde a `012` —
    o parecer é obrigatório exatamente ali, e é a razão de esta feature existir. O desfavorável sem
    parecer que existe de verdade é o **Resultado por Ocorrência**: a presidência constata a
    ausência, não há Avaliação nenhuma, e não há avaliador a citar.

    Medir isso importa: sem este caso, a `FR-525` estaria escrita para uma situação inalcançável, e
    a frase que a tela mostra nunca apareceria para ninguém.
    """
    from processo_seletivo.resultados.application.ocorrencia import registrar_ocorrencia
    from tests.fixtures.recursos_us4 import cenario_julgavel

    montado = cenario_julgavel(
        gestor,
        api_client,
        manager_headers,
        process_payload,
        seed=142,
        codigo="0842",
        # A terceira inscrição fica **sem Resultado** — é o que `None` produz —, e é sobre ela que a
        # ocorrência é constatada depois.
        pontuacoes=("55.0000", "90.0000", None),
        admitir_a_peca=False,
        parecer=PARECER,
    )
    cenario = montado["cenario"]
    ausente = cenario["inscricoes"][2]
    registrar_ocorrencia(
        actor=gestor,
        processo_id=cenario["processo"].id,
        edital_id=cenario["edital"].id,
        etapa_id=cenario["etapa_do_recurso"],
        inscricao_ids=[ausente.id],
        motivo="Não compareceu à prova didática.",
        idempotency_key="ocorrencia-142",
        correlation_id="teste",
    )
    resultado = ResultadoEtapa.vigentes.get(inscricao=ausente, etapa_id=cenario["etapa_do_recurso"])
    assert resultado.consequencia == ResultadoEtapa.Consequencia.ELIMINADA
    assert resultado.avaliacao_id is None, "por Ocorrência não há Avaliação, logo não há parecer"

    corpo = abrir_como_titular(client, ausente)

    assert NAO_HOUVE_PARECER in corpo
    assert "Fundamentação escrita por quem avaliou" not in corpo
    # E o parecer da **outra** pessoa não atravessa por causa disso.
    assert PARECER not in corpo


# --- Nada de terceiro atravessa (FR-526, FR-535, FR-536, SC-186) --------------------------------


def test_outro_candidato_nao_alcanca_o_parecer_alheio(client, eliminada):
    """`FR-526`: identificador não concede acesso, e a resposta é a mesma de recurso inexistente."""
    entrar_como_titular(client, eliminada["outra_inscricao"])

    resposta = client.get(reverse("portal:acompanhamento", args=[eliminada["inscricao"].id]))

    assert resposta.status_code == 404
    assert PARECER not in resposta.content.decode()


def test_nada_de_terceiro_atravessa_a_tela_do_titular(client, eliminada):
    """`SC-186`: nenhum nome alheio, nenhum protocolo alheio, nenhuma nota alheia."""
    alheia = eliminada["outra_inscricao"]

    corpo = abrir_como_titular(client, eliminada["inscricao"])

    assert alheia.nome not in corpo
    assert alheia.protocolo not in corpo


def test_escopo_institucional_divergente_recebe_a_resposta_uniforme(client, eliminada):
    """`FR-536`: o portal do candidato responde por titularidade, e a negativa não distingue causas.

    A pessoa de outra unidade e a pessoa que não é titular recebem **a mesma** resposta: dizer
    "existe, mas não é seu" já entregaria que existe.
    """
    from processo_seletivo.identidade.models import CandidateIdentity
    from processo_seletivo.portal import identidade as identidade_do_candidato

    estranha = CandidateIdentity.objects.create(
        subject="cpf:candidata-de-outra-unidade",
        nome="Candidata de outra unidade",
        cpf_normalizado="52998224725",
        created_at=timezone.now(),
    )
    sessao = client.session
    sessao[identidade_do_candidato.CHAVE_SESSAO] = str(estranha.pk)
    sessao.save()

    resposta = client.get(reverse("portal:acompanhamento", args=[eliminada["inscricao"].id]))

    assert resposta.status_code == 404
    assert PARECER not in resposta.content.decode()


# --- Qual parecer (FR-523) ---------------------------------------------------------------------


def test_o_parecer_lido_e_o_da_conclusao_que_fundamenta_o_resultado(eliminada):
    """`FR-523`: *vale o que o ato citou* — a conclusão preservada, e não o campo corrente.

    A `012` grava uma `ConclusaoAvaliacao` a cada conclusão, e é dela que a leitura sai. O campo da
    Avaliação é a queda para dado anterior àquele registro, e não a fonte.
    """
    from processo_seletivo.avaliacoes.models import ConclusaoAvaliacao
    from processo_seletivo.recursos.application.selectors import parecer_que_fundamenta

    resultado = eliminada["superado"]
    conclusoes = list(
        ConclusaoAvaliacao.objects.filter(avaliacao_id=resultado.avaliacao_id).order_by("-ordem")
    )
    assert conclusoes, "a 012 preserva a conclusão de cada avaliação concluída"
    assert conclusoes[0].parecer == PARECER

    assert parecer_que_fundamenta(resultado, conclusoes) == PARECER


def test_peca_inadmitida_nao_mantem_o_parecer_visivel(
    client, raiz_de_arquivos, gestor, api_client, manager_headers, process_payload
):
    """**O outro desfecho terminal**, e o que a primeira redação desta feature não viu (`FR-524`).

    Juízo negativo encerra a peça **sem mérito**, e o banco o garante: a trigger
    `decisao_recurso_coerente` recusa decisão sobre recurso não admitido. Enquanto "pendente"
    significava só *"sem decisão"*, a peça inadmitida contava como em curso **para sempre** — e o
    parecer nunca saía da tela do titular.

    Não era uma janela generosa demais: era uma janela sem fechadura sobre dado pessoal, e a
    `FR-524` deixava de ter quando acontecer.
    """
    from tests.fixtures.instrucao import inadmitir_a_peca

    # Sem juízo no cenário: cabe **um** por recurso, e o do cenário padrão já é positivo.
    montado = cenario_instruivel(
        gestor,
        api_client,
        manager_headers,
        process_payload,
        seed=143,
        codigo="0843",
        admitir_a_peca=False,
        janela_recursal=JANELA,
    )
    inadmitir_a_peca(montado)

    with patch("django.utils.timezone.now", return_value=depois_do_prazo()):
        corpo = abrir_como_titular(client, montado["inscricao"])

    assert PARECER not in corpo
    assert POR_QUE_SAIU in corpo
