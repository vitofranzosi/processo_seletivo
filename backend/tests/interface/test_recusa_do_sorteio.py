"""A tela do sorteio distingue **a fonte não publicou** de **a declaração não pôde ser lida** (035).

**Duas causas caíam no mesmo `except`, e a tela dizia a mesma frase para as duas.** A frase é
verdadeira para uma e falsa para a outra:

| Causa | O que aconteceu | A frase de antes |
|---|---|---|
| a cadeia esgotou | a fonte esteve indisponível tantas vezes quanto a regra encadeia | verdadeira |
| a regra não soube derivar | a referência declarada não termina em número | **falsa** — a fonte
  nunca foi consultada, e quem lesse ficaria esperando por algo que não viria |

**A frase certa já existia**, específica e correta, e era descartada a uma linha de onde seria
exibida: é o `detail` da recusa que a própria regra de substituição levanta. O trabalho não foi
escrevê-la — foi parar de jogá-la fora.

**Esta é a única das três histórias da `035` que ajuda quem já publicou.** Depois da `US1` e da
`US2` quase nenhum Edital novo chega aqui: a forma é ensinada na composição e conferida ao gravar. O
destinatário é o Edital do acervo, cuja única saída é a Retificação — e é por isso que a frase tem
de dizer **qual campo**, e só então que corrigir exige Retificação. Quem lê precisa saber *o que*
antes de saber *como*.
"""

import pytest
from django.urls import reverse

from processo_seletivo.editais.models.perfis import MarcoClassificatorio
from processo_seletivo.shared.canonical import SCHEMA_VERSION
from processo_seletivo.sorteios.application.ocorrencia import observar_ocorrencia
from processo_seletivo.sorteios.domain.substituicao import LIMITE_DA_CADEIA, cadeia
from processo_seletivo.sorteios.infrastructure.fontes import Observacao
from tests.fixtures.comissao import rascunho_com_etapas
from tests.fixtures.edital import PROFILE_ID
from tests.fixtures.legado import publicar_sem_aferir
from tests.fixtures.sorteio import MARCO, METODO, certame_de_sorteio, marco_com_metodo, presidente
from tests.interface.conftest import identificar

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.integration]

#: A forma que uma pessoa escreve: o número está lá, e só não está onde a regra o procura.
EM_PROSA = "concurso 6100 da Loteria Federal"


class Indisponivel:
    """A fonte responde, e responde que não publicou. É a indisponibilidade **real**."""

    def observar(self, *, fonte, referencia):
        return Observacao(
            indisponivel=True, evidencia=f"Concurso {referencia}: sem extração publicada."
        )


@pytest.fixture
def certame(gestor, api_client, manager_headers, process_payload, seletor_ligado):
    """O certame normal: ocorrência derivável, publicado pelo caminho de hoje."""
    return certame_de_sorteio(gestor, api_client, manager_headers, process_payload)


def _degradar(edital):
    """A ocorrência vira prosa **antes** do congelamento, que é o único ponto em que ela pode.

    `update()` sobre a elaboração, que é editável; a Publicação e a versão consolidada são
    append-only por trigger desde a `002`, e reescrevê-las é exatamente o que a Constituição promete
    nunca fazer.
    """
    marco = MarcoClassificatorio.objects.get(pk=MARCO)
    MarcoClassificatorio.objects.filter(pk=MARCO).update(
        metodo_de_sorteio={**marco.metodo_de_sorteio, "occurrence": EM_PROSA}
    )


@pytest.fixture
def do_acervo(gestor, api_client, manager_headers, process_payload, seletor_ligado):
    """O Edital que **já está** publicado com a ocorrência em prosa — o destinatário da `US3`.

    Ele não pode ser produzido pela composição de hoje: a `US2` a recusa, e é esse o ponto dela. O
    acervo é simulado como ele realmente é, com a Publicação inserida com o conteúdo que teria sido
    publicado antes de a guarda existir.
    """
    from processo_seletivo.comissoes.domain.funcoes import Funcao
    from tests.fixtures.comissao import constituir

    rascunho = rascunho_com_etapas()
    marco_com_metodo(rascunho, perfil_id=PROFILE_ID, etapa_id=rascunho["stages"][1]["id"])
    edital = publicar_sem_aferir(
        api_client,
        manager_headers,
        process_payload,
        draft=rascunho,
        degradar=_degradar,
        versao=SCHEMA_VERSION,
    )
    # A presidência entra porque a tela do sorteio é do certame: sem ela a leitura devolve 403, e o
    # teste passaria a afirmar sobre a página de recusa em vez de sobre a tela.
    constituir(gestor, edital.processo, [("maria", Funcao.PRESIDENTE)], prefixo="recusa-035")
    return {"edital": edital, "processo": edital.processo, "perfil": PROFILE_ID, "marco": MARCO}


def _abrir(client, certame):
    identificar(client, "maria", ["elaborador"])
    return client.get(
        reverse("interface:sorteio", args=[certame["edital"].id, certame["marco"]])
    ).content.decode()


def test_a_referencia_nao_derivavel_nomeia_a_declaracao_e_nao_a_fonte(do_acervo, client):
    """`FR-516` e `FR-517` — o campo, o que ele precisa conter, e só então a Retificação."""
    corpo = _abrir(client, do_acervo)

    assert "não pôde ser lida pela regra de substituição publicada" in corpo
    assert EM_PROSA in corpo, "a referência que está declarada"
    assert "<strong>Ocorrência</strong>" in corpo, "qual campo"
    assert "a ocorrência concreta que fixará a semente" in corpo, "e o que ele é"
    assert "precisa terminar no número da ocorrência" in corpo, "o que ele precisa conter"
    assert "A fonte não foi consultada" in corpo, "e que não há o que esperar dela"
    assert "exige Retificação" in corpo, "e só então o como"


def test_a_frase_da_indisponibilidade_nao_sai_quando_a_causa_e_a_declaracao(do_acervo, client):
    """A contraprova: sem ela as duas frases poderiam sair juntas, e nada estaria distinto."""
    corpo = _abrir(client, do_acervo)

    assert "todas as substitutas previstas pela regra publicada estão" not in corpo


def test_a_cadeia_esgotada_de_verdade_continua_dizendo_o_que_dizia(certame, client):
    """`FR-518` — a causa é outra, e para ela a frase de hoje está certa.

    Esta feature não mexe no que já está certo. A cadeia é esgotada **de verdade**: a fonte é
    consultada para cada referência e responde que não publicou, e cada resposta vira linha
    append-only. É o caminho real, e não um estado forjado.
    """
    for numero, referencia in enumerate(cadeia(METODO)):
        observar_ocorrencia(
            actor=presidente(),
            processo_id=certame["processo"].id,
            fonte=METODO["source"],
            referencia=referencia,
            idempotency_key=f"esgotar-{numero}",
            correlation_id="teste-035",
            fonte_externa=Indisponivel(),
        )

    corpo = _abrir(client, certame)

    assert "A ocorrência declarada e todas as substitutas previstas pela regra publicada estão" in (
        corpo
    )
    assert "não pôde ser lida pela regra de substituição publicada" not in corpo
    assert len(cadeia(METODO)) == LIMITE_DA_CADEIA + 1, "a declarada mais as substitutas"


def _recusa_lida(qual):
    """A recusa como a **leitura** a devolve — e é ela que decide, não a prosa do template."""
    from processo_seletivo.sorteios.application.previa import recortes_do_marco

    return recortes_do_marco(
        edital=qual["edital"], perfil_id=qual["perfil"], marco_id=qual["marco"]
    )["recusa_da_ocorrencia"]


def test_a_leitura_nomeia_a_declaracao_como_causa(do_acervo):
    """O `FR-516` dito onde ele é decidido: no código da recusa, e não na frase."""
    da_declaracao = _recusa_lida(do_acervo)

    assert da_declaracao["causa"] == "declaracao"
    assert da_declaracao["referencia"] == EM_PROSA
    assert da_declaracao["campo"] == "Ocorrência"
    assert da_declaracao["o_que_e"] == "a ocorrência concreta que fixará a semente"


def test_sem_recusa_alguma_a_leitura_devolve_nada(certame):
    """A contraprova: com ocorrência derivável e fonte disponível não há recusa nenhuma.

    Sem ela, uma leitura que devolvesse sempre uma causa faria a tela mostrar a recusa no percurso
    normal — e os testes acima continuariam verdes.
    """
    assert _recusa_lida(certame) is None
