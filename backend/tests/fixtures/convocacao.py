"""O cenário da convocação e os atalhos que os arquivos de teste da `019` usam.

**Funções ficam aqui, e a fixture fica no `conftest.py` de cada pasta.** Importar uma fixture de
outro módulo de teste a redefine no importador, que é o que o `F811` acusa; importar uma função
comum não tem esse problema. É a regra que `tests/fixtures/corte.py` registra.

O cenário é o da ocupação da `016` — Edital publicado com quadro, ordem, corte e Resultados —, mais
a **apuração emitida**: sem ela não há vaga faltante conhecida, e convocar é recusado dizendo isso.
"""

from django.utils import timezone

from processo_seletivo.convocacao.application.convocar import convocar as praticar
from processo_seletivo.ocupacao.application.emissao import emitir_apuracao
from processo_seletivo.publicacoes.application.selectors import effective_version
from processo_seletivo.publicacoes.domain.vocabulario_da_regra import (
    FORMA_POR_MENSAGEM_INDIVIDUAL,
)
from processo_seletivo.resultados.models import ResultadoEtapa
from tests.fixtures.corte import ENTREVISTA, MARCO
from tests.fixtures.edital import PROFILE_ID
from tests.fixtures.ocupacao import montar_cenario_da_ocupacao


def montar_cenario_da_convocacao(
    gestor,
    api_client,
    manager_headers,
    process_payload,
    *,
    prefixo="convocacao-019",
    forma=FORMA_POR_MENSAGEM_INDIVIDUAL,
    indeferidas=(),
    **quadro,
):
    """Edital publicado com quadro, ordem, corte, Resultados **e apuração vigente**.

    **A forma declarada é a mensagem individual**, que é a dos Editais 77, 58 e 59 (item 8.3) — os
    que esta feature existe para conduzir. `forma=None` monta o Edital que **não declarou**, e é o
    que a recusa `forma_de_comunicacao_nao_declarada` existe para proteger.

    Devolve `(edital, etapa_pontuada, inscricoes)` — a mesma forma que a `014` e a `016` usam, para
    que quem leia os três arquivos reconheça o cenário.
    """
    edital, pontuada, inscricoes = montar_cenario_da_ocupacao(
        gestor, api_client, manager_headers, process_payload, prefixo=prefixo, forma=forma, **quadro
    )
    # **Sem a Etapa governada consolidada não há ocupação nenhuma**, e o cenário da `016` para
    # exatamente aqui: a faixa progride e a Entrevista não conclui, de modo que `ocupadas` é zero.
    # Convocar sobre esse recorte não teria quem chamar — todos estariam fora da faixa por não
    # terem habilitado. É o passo que transforma o cenário do corte no cenário da convocação.
    indeferidas = {int(i) for i in indeferidas}
    habilitar_na_etapa_governada(
        edital, [i for n, i in enumerate(inscricoes[:3]) if n not in indeferidas]
    )
    # **O indeferido é a premissa da `US3`**, e ele precisa estar **na faixa**: quem o corte não
    # alcançou não é convocável para regularizar, porque regularizar não contorna a seleção.
    indeferir_na_etapa_governada(
        edital, [i for n, i in enumerate(inscricoes[:3]) if n in indeferidas]
    )
    apurar(edital, gestor, chave=f"{prefixo}-apurar")
    return edital, pontuada, inscricoes


def indeferir_na_etapa_governada(edital, inscricoes):
    """Consolida `ELIMINADA` na Entrevista — o indeferimento que a regularização vem corrigir."""
    _consolidar(
        edital, inscricoes, ResultadoEtapa.Consequencia.ELIMINADA, "Documentação indeferida"
    )


def habilitar_na_etapa_governada(edital, inscricoes):
    """Consolida `HABILITADA` na Entrevista — o fato que torna a vaga ocupada (`R-001`).

    **`OCORRENCIA`, e não `AVALIACAO`**: não houve banca aqui, e a origem tem de dizer a verdade
    sobre de onde o Resultado veio. É o mesmo atalho que a `016` usa no cenário do sorteio.

    A versão consolidada é exigida pelo gatilho `check_stage_result_source`: um Resultado tem de
    citar a versão do próprio Edital, e a recusa é do banco, não da aplicação.
    """
    _consolidar(
        edital,
        inscricoes,
        ResultadoEtapa.Consequencia.HABILITADA,
        "Entrevista concluída com aproveitamento",
    )


def _consolidar(edital, inscricoes, consequencia, motivo):
    versao = effective_version(edital_id=edital.id)
    agora = timezone.now()
    for inscricao in inscricoes:
        ResultadoEtapa.objects.create(
            inscricao=inscricao,
            edital=edital,
            versao=versao,
            etapa_id=ENTREVISTA,
            origem=ResultadoEtapa.Origem.OCORRENCIA,
            consequencia=consequencia,
            motivo=motivo,
            consolidado_em=agora,
            consolidado_por="teste",
        )


def apurar(edital, gestor, *, chave="convocacao-019-apurar", motivo="", lista_id=None):
    """Emite a apuração do recorte da ampla concorrência."""
    return emitir_apuracao(
        actor=gestor,
        processo_id=edital.processo_id,
        edital_id=edital.id,
        perfil_id=PROFILE_ID,
        marco_id=MARCO,
        lista_id=lista_id,
        idempotency_key=chave,
        correlation_id="teste-convocacao-019",
        motivo=motivo,
    )


def convocar(edital, gestor, inscricao, **kwargs):
    """Pratica a convocação com os valores do cenário, e o que o chamador quiser sobrescrever."""
    argumentos = {
        "actor": gestor,
        "processo_id": edital.processo_id,
        "edital_id": edital.id,
        "perfil_id": PROFILE_ID,
        "marco_id": MARCO,
        "inscricao_id": getattr(inscricao, "id", inscricao),
        "especie": "VAGA_INICIAL",
        "fundamento": "No interesse da Administração, item 8.2 do Edital 77/2026.",
        "idempotency_key": "convocacao-019-convocar",
        "correlation_id": "teste-convocacao-019",
    }
    argumentos.update(kwargs)
    return praticar(**argumentos)
