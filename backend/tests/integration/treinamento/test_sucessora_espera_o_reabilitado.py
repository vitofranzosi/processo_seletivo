"""A ordem sucessora e o corte esperam a avaliação do reabilitado, no C08 da `134` (141).

**A cadeia inteira, e não a célula** (o pedido do usuário). O F-2 do estudo de continuidade de 10/11
não era uma célula errada: era o Centro conduzindo por quatro atos seguidos, três dos quais nasciam
para ser sucedidos — a sucessora parcial, o corte sem o reabilitado e a Análise documental dos que
esse corte deixou passar. Por isso o teste principal anda o caminho todo, pelos mesmos comandos que
as telas chamam: recurso deferido que reabilita → Análise de títulos pendente → consolidada → ordem
sucessora → corte → Análise documental. Em cada passo, o andamento oferece só o ato seguinte.

**E o avesso, com teste próprio**: o recurso que só corrige a nota de quem já tinha posição continua
oferecendo a sucessora na hora. Bloquear o legítimo seria trocar um defeito por outro.

As regras puras, sem banco, estão em `tests/unit/interface/test_sucessora_espera_o_reabilitado.py`.
"""

from datetime import timedelta
from decimal import Decimal

import pytest

from processo_seletivo.interface import andamento as a
from processo_seletivo.seguranca.domain import Actor
from processo_seletivo.treinamento import construcao as c
from processo_seletivo.treinamento.models import CenarioDeTreinamento
from tests.fixtures.autoridades import AUTORIDADE_DA_SUITE
from tests.fixtures.treinamento import carregar, retomar

pytestmark = [pytest.mark.integration, pytest.mark.django_db]

#: O candidato 08 do C08: 5,0 na Prova objetiva, com mínima 6,0 — eliminado, e sem títulos.
REABILITADO = 7
#: O candidato 07: 6,5 na prova e 4,0 nos títulos — com posição, e sem nada pendente.
COM_POSICAO = 6

SUCESSORA = "Emitir a ordem sucessora"
CORTES = ("Emitir o corte", "Emitir a geração sucessora do corte")


@pytest.fixture
def c08(treinamento):
    saida = carregar("C08", autoridade=str(AUTORIDADE_DA_SUITE))
    assert "C08  CRIADO" in saida, saida
    return retomar(
        CenarioDeTreinamento.objects.get(codigo="C08"), autoridade=str(AUTORIDADE_DA_SUITE)
    )


# --- os atos, pelos comandos que as telas chamam ------------------------------------------------


def _julgadora(m):
    """Quem julga não avaliou nem consolidou: o impedimento do par (FR-039) recusaria a presidência,
    que consolidou a prova, e a avaliação 1, que a avaliou."""
    return Actor("treino.julgamento", m.unidade, frozenset({"recurso:julgar"}))


def _deferir_correcao_da_prova(m, posicao, nota, passo):
    """O candidato recorre do preliminar, e o recurso é admitido e deferido com a nota fixada."""
    from processo_seletivo.divulgacao.models import PublicacaoResultado
    from processo_seletivo.recursos.application.admitir import admitir
    from processo_seletivo.recursos.application.interpor import interpor
    from processo_seletivo.recursos.application.julgar import julgar
    from processo_seletivo.recursos.models import DecisaoRecurso
    from processo_seletivo.resultados.models import ResultadoEtapa
    from tests.fixtures.recursos_us4 import assinatura_de

    inscricao = m.inscricoes[posicao]
    publicacao = PublicacaoResultado.objects.get(edital=m.edital)
    recurso = interpor(
        identidade=m.identidade(m.pessoas[posicao]),
        inscricao=inscricao,
        publicacao=publicacao,
        fundamentacao="Peço a revisão da nota da prova (teste da 141).",
        assinatura_do_objeto=str(publicacao.pk),
        idempotency_key=m.chave(f"141-{passo}-interpor"),
    )
    admitir(
        actor=_julgadora(m),
        recurso_id=recurso.id,
        admitido=True,
        motivo="Tempestivo.",
        assinatura_do_estado=assinatura_de(recurso),
        idempotency_key=m.chave(f"141-{passo}-admitir"),
    )
    superado = ResultadoEtapa.vigentes.get(inscricao=inscricao, etapa_id=m.id(c.ETAPA_PROVA))
    julgar(
        actor=_julgadora(m),
        recurso_id=recurso.id,
        especie=DecisaoRecurso.Especie.CORRECAO_FIXADA,
        motivacao="A questão 7 admitia a resposta dada (teste da 141).",
        etapa_id=m.id(c.ETAPA_PROVA),
        pontuacao=Decimal(nota),
        assinatura_do_resultado=str(superado.id),
        idempotency_key=m.chave(f"141-{passo}-julgar"),
    )


def _avaliar_titulos(m, inscricao, nota):
    """Distribui, conclui e consolida a Análise de títulos de uma inscrição — com chaves próprias,
    porque as de `Montagem.avaliar` são as da carga, e repeti-las devolveria o lote antigo."""
    from processo_seletivo.avaliacoes.application.avaliacao import concluir
    from processo_seletivo.avaliacoes.application.distribuicao import distribuir
    from processo_seletivo.publicacoes.application.selectors import effective_version
    from processo_seletivo.resultados.application.consolidacao import consolidar

    etapa = m.id(c.ETAPA_TITULOS)
    distribuir(
        actor=m.ator(c.GESTAO),
        processo_id=m.processo.id,
        edital_id=m.edital.id,
        etapa_id=etapa,
        membro_ids=[m.membros[c.AVALIACAO_1].id],
        inscricao_ids=[inscricao.id],
        idempotency_key=m.chave("141-titulos-lote"),
        correlation_id=m.correlacao,
    )
    concluir(
        ator=m.ator(c.AVALIACAO_1),
        edital=m.edital,
        etapa_id=etapa,
        inscricao_id=inscricao.id,
        pontuacao=Decimal(nota),
        parecer="Avaliação do reabilitado (teste da 141).",
        expected_revision=1,
        versao_reconhecida=effective_version(edital_id=m.edital.id).id,
        correlation_id=m.correlacao,
    )
    consolidar(
        actor=m.ator(c.PRESIDENCIA),
        processo_id=m.processo.id,
        edital_id=m.edital.id,
        etapa_id=etapa,
        inscricao_ids=[inscricao.id],
        idempotency_key=m.chave("141-titulos-consolidar"),
        correlation_id=m.correlacao,
    )


def _emitir_sucessora(m, passo):
    """A sucessora da ampla, como a tela da ordenação a emite: com o vigente na assinatura e motivo.

    O serviço aceita a parcial (128) — é por isso que o teste pode emiti-la mesmo quando o andamento
    diz que ela espera, e provar que o corte espera também.
    """
    from processo_seletivo.classificacao.application.calculo import calcular_ordem
    from processo_seletivo.classificacao.application.emissao import (
        assinatura_da_proposta,
        emitir_ordem,
    )
    from processo_seletivo.classificacao.application.selectors import ato_vigente

    vigente = ato_vigente(edital=m.edital, marco_id=m.id(c.MARCO), lista_id=None)
    proposta = calcular_ordem(
        edital=m.edital, perfil_id=m.id(c.PERFIL), marco_id=m.id(c.MARCO), lista_id=None
    )
    emitir_ordem(
        actor=m.ator(c.PRESIDENCIA),
        processo_id=m.processo.id,
        edital_id=m.edital.id,
        perfil_id=m.id(c.PERFIL),
        marco_id=m.id(c.MARCO),
        idempotency_key=m.chave(f"141-{passo}-sucessora"),
        correlation_id=m.correlacao,
        confirmacao_do_calculo=assinatura_da_proposta(proposta, ato_vigente=vigente),
        motivo="Recurso deferido (teste da 141).",
    )
    return ato_vigente(edital=m.edital, marco_id=m.id(c.MARCO), lista_id=None)


def _emitir_corte(m, passo, motivo=""):
    from processo_seletivo.classificacao.application.corte import calcular_corte, geracao_vigente
    from processo_seletivo.classificacao.application.emissao_do_corte import (
        assinatura_da_proposta,
        emitir_corte,
    )

    geracao = geracao_vigente(
        edital=m.edital, perfil_id=m.id(c.PERFIL), marco_id=m.id(c.MARCO), lista_id=None
    )
    proposta = calcular_corte(edital=m.edital, perfil_id=m.id(c.PERFIL), marco_id=m.id(c.MARCO))
    return emitir_corte(
        actor=m.ator(c.PRESIDENCIA),
        processo_id=m.processo.id,
        edital_id=m.edital.id,
        perfil_id=m.id(c.PERFIL),
        marco_id=m.id(c.MARCO),
        idempotency_key=m.chave(f"141-{passo}-corte"),
        correlation_id=m.correlacao,
        confirmacao_do_calculo=assinatura_da_proposta(proposta, geracao=geracao),
        motivo=motivo,
    )


# --- a leitura -------------------------------------------------------------------------------


def _ler(m, quem=c.PRESIDENCIA, agora=None):
    andamento = a.do_edital(m.edital, m.ator(quem), agora=agora)
    assert andamento is not None
    [perfil] = andamento.perfis
    ampla = next(lista for lista, rotulo in perfil.listas if "PPP" not in rotulo)

    def celula(tipo):
        return next(p for p in perfil.pontos if p.tipo == tipo).celula(ampla)

    return andamento, celula


def _atos(andamento):
    return [p.ato for p in andamento.providencias]


def _sucessoras(andamento):
    # A da PPP, lista em que ninguém concorre, diz outra frase (135): conta só a da ampla.
    return [ato for ato in _atos(andamento) if ato == SUCESSORA]


def _cortes(andamento):
    return [ato for ato in _atos(andamento) if ato in CORTES]


def _documental(m, andamento):
    """As providências da Análise documental, que o corte governa — a Etapa seguinte."""
    eid = m.id(c.ETAPA_DOCUMENTAL)
    return [p for p in andamento.providencias if p.chave[:2] == ("etapa", eid)]


# --- US3: a cadeia inteira (SC-1510, SC-1511, SC-1513) -----------------------------------------


def test_a_cadeia_do_reabilitado_oferece_um_ato_de_cada_vez(c08):
    m = c08
    reabilitado = m.inscricoes[REABILITADO]
    _, antes = _ler(m)
    resultado_antes = antes(a.RESULTADO)

    # 1. O recurso deferido reabilita o 08, e falta a Análise de títulos dele.
    _deferir_correcao_da_prova(m, REABILITADO, "6.0", "reabilita")
    andamento, celula = _ler(m)

    assert celula(a.ORDEM).situacao == a.DEPOIS
    assert celula(a.ORDEM).vigente_para_tras
    assert "Análise de títulos" in celula(a.ORDEM).razao
    assert "a vigente continua produzindo efeito" in celula(a.ORDEM).razao
    assert _sucessoras(andamento) == [], "a sucessora espera a Análise de títulos do reabilitado"
    assert _cortes(andamento) == []
    assert celula(a.CORTE).situacao == a.DEPOIS
    assert any("Distribuir" in ato for ato in _atos(andamento)), "a Etapa que falta é o próximo"
    assert _documental(m, andamento) == [], "a Etapa seguinte não é distribuível por este caminho"
    # SC-1513: o resultado diz o que dizia com a ordem obsoleta — e não "não há ordem vigente".
    assert celula(a.RESULTADO).situacao == a.DEPOIS
    assert celula(a.RESULTADO).razao == (
        "a ordem vigente está para trás: o ato sucessor vem antes de divulgar"
    )
    assert celula(a.RESULTADO).divulgado == resultado_antes.divulgado == a.PRELIMINAR
    # Para qualquer papel, e não só para quem conduz.
    for quem in (c.GESTAO, c.PUBLICACAO):
        outro, _ = _ler(m, quem)
        assert _sucessoras(outro) == [] and _cortes(outro) == [], quem

    # 2. Consolidada a avaliação, a sucessora aparece — e o corte ainda não.
    _avaliar_titulos(m, reabilitado, "7.0")
    andamento, celula = _ler(m)

    assert celula(a.ORDEM).situacao == a.OBSOLETO
    assert _sucessoras(andamento) == [SUCESSORA]
    assert _cortes(andamento) == []
    assert _documental(m, andamento) == []

    # 3. Emitida a sucessora, completa, o corte segue a regra de hoje: espera o prazo recursal.
    sucessora = _emitir_sucessora(m, "completa")
    assert sucessora.posicoes.filter(inscricao=reabilitado, posicao__isnull=False).exists()
    andamento, celula = _ler(m)

    assert celula(a.ORDEM).situacao == a.FEITO
    assert _sucessoras(andamento) == []
    assert celula(a.CORTE).situacao == a.AGUARDA and celula(a.CORTE).recomendacao
    assert _documental(m, andamento) == []
    # Passado o prazo, o corte é providência de quem conduz.
    fim = celula(a.CORTE).ate
    andamento, celula = _ler(m, agora=fim + timedelta(minutes=1))
    assert celula(a.CORTE).situacao == a.PENDENTE
    assert _cortes(andamento) == ["Emitir o corte"]

    # 4. Emitido o corte, a Etapa seguinte é distribuível.
    _emitir_corte(m, "primeiro")
    andamento, celula = _ler(m)

    assert celula(a.CORTE).situacao == a.FEITO
    assert _cortes(andamento) == []
    assert [p.natureza for p in _documental(m, andamento)] == [a.DISTRIBUIR]


# --- US2: o corte espera o reingresso, mesmo com a sucessora parcial emitida --------------------


def test_com_a_sucessora_parcial_emitida_pela_tela_o_corte_espera_o_reingresso(c08):
    """O caminho do F-2 sem o Centro: a tela aceita a sucessora parcial (128), com aviso. O corte,
    então, já não espera pela ordem — e tem de esperar pelo reingresso."""
    m = c08
    _deferir_correcao_da_prova(m, REABILITADO, "6.0", "reabilita")
    parcial = _emitir_sucessora(m, "parcial")
    assert parcial.posicoes.filter(
        inscricao=m.inscricoes[REABILITADO], posicao__isnull=True
    ).exists(), "a sucessora é parcial: o reabilitado fica sem posição"

    andamento, celula = _ler(m)

    assert celula(a.ORDEM).situacao == a.FEITO
    assert celula(a.CORTE).situacao == a.DEPOIS
    assert celula(a.CORTE).razao == a.REINGRESSO_NO_CORTE
    assert _cortes(andamento) == []
    assert _documental(m, andamento) == []

    # Consolidado o reabilitado, a parcial fica para trás: volta a sucessora, e o corte espera.
    _avaliar_titulos(m, m.inscricoes[REABILITADO], "7.0")
    andamento, celula = _ler(m)
    assert _sucessoras(andamento) == [SUCESSORA]
    assert _cortes(andamento) == []


def test_o_corte_anterior_ao_recurso_continua_vigente_ate_a_sucessora(c08):
    """O corte emitido antes do recurso **não** fica obsoleto pela reabilitação do 08 (D-004).

    O 08 foi eliminado na prova, e por isso não está no universo que a ordem congelou: o
    `_reingressou` (a FR-218 da `014`) mede só quem estava lá, de propósito. O corte continua
    vigente, e a leitura não o desmente. O que esta spec garante é o resto da cadeia: a sucessora
    espera os títulos dele, e só emitida ela o corte fica para trás e pede a geração sucessora.
    """
    m = c08
    _emitir_corte(m, "antes-do-recurso")
    _deferir_correcao_da_prova(m, REABILITADO, "6.0", "reabilita")

    andamento, celula = _ler(m)
    assert celula(a.CORTE).situacao == a.FEITO
    assert celula(a.ORDEM).situacao == a.DEPOIS
    assert _sucessoras(andamento) == [] and _cortes(andamento) == []

    _avaliar_titulos(m, m.inscricoes[REABILITADO], "7.0")
    andamento, celula = _ler(m)
    assert _sucessoras(andamento) == [SUCESSORA]
    assert _cortes(andamento) == [], "o corte só fica para trás quando a ordem é sucedida"

    _emitir_sucessora(m, "completa")
    andamento, celula = _ler(m)
    assert celula(a.CORTE).situacao == a.OBSOLETO
    assert celula(a.CORTE).ato == "Emitir a geração sucessora do corte"
    # A Análise documental, bloqueada pelo corte obsoleto, diz o mesmo ato como impedimento dela —
    # como antes da `141`. Sem reingresso, os dois concordam.
    assert set(_cortes(andamento)) == {"Emitir a geração sucessora do corte"}


# --- US4: a correção de nota não espera nada (SC-1512) -----------------------------------------


def test_a_correcao_de_nota_sem_reabilitar_oferece_a_sucessora_na_hora(c08):
    m = c08
    _deferir_correcao_da_prova(m, COM_POSICAO, "7.5", "corrige")

    andamento, celula = _ler(m)

    assert celula(a.ORDEM).situacao == a.OBSOLETO
    assert not celula(a.ORDEM).vigente_para_tras
    assert _sucessoras(andamento) == [SUCESSORA], "a correção de nota não deixa nada por fazer"
    [providencia] = [p for p in andamento.providencias if p.ato == SUCESSORA]
    assert providencia.sua and providencia.responsavel == a.CONDUZ

    # Emitida a sucessora, o corte segue o curso normal: o prazo recursal, e depois ele.
    _emitir_sucessora(m, "corrige")
    andamento, celula = _ler(m)
    assert celula(a.CORTE).situacao == a.AGUARDA and celula(a.CORTE).recomendacao
    andamento, celula = _ler(m, agora=celula(a.CORTE).ate + timedelta(minutes=1))
    assert celula(a.CORTE).situacao == a.PENDENTE
    assert _cortes(andamento) == ["Emitir o corte"]


# --- US5: a tela do corte avisa do reingresso (FR-4840, FR-4841) -------------------------------

AVISO = "por recurso está sem resultado numa Etapa deste marco"


@pytest.fixture
def seletor_ligado(settings):
    settings.INTERFACE_SELETOR_IDENTIDADE = True


def _tela_do_corte(client, m):
    from django.urls import reverse

    from tests.interface.conftest import identificar

    identificar(client, c.PRESIDENCIA, [])
    resposta = client.get(reverse("interface:corte", args=[m.edital.id, m.id(c.MARCO)]))
    assert resposta.status_code == 200
    return resposta.content.decode()


def test_a_tela_do_corte_avisa_do_reingresso_e_continua_emitindo(c08, client, seletor_ligado):
    m = c08
    _deferir_correcao_da_prova(m, REABILITADO, "6.0", "reabilita")
    _emitir_sucessora(m, "parcial")

    pagina = _tela_do_corte(client, m)

    assert "1 inscrição reabilitada " + AVISO in pagina
    assert "fora da faixa, porque está sem posição" in pagina
    assert "Conferir antes de emitir</button>" in pagina, "o aviso não tira o botão"
    # E o comando aceita, como antes (FR-4842).
    _emitir_corte(m, "apesar-do-aviso")


def test_sem_reingresso_a_tela_do_corte_nao_avisa(c08, client, seletor_ligado):
    m = c08
    _deferir_correcao_da_prova(m, COM_POSICAO, "7.5", "corrige")
    _emitir_sucessora(m, "corrige")

    assert "reabilitada por recurso" not in _tela_do_corte(client, m)
