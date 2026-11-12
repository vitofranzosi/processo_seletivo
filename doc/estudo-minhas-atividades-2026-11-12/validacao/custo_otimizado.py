"""Leitura só: o custo da página com as reduções da rodada 2, simuladas sem mudar o código (rodada 3).

Roda dentro de `manage.py shell`. Mede, para cada identidade, quatro montagens da mesma página:

- atual: `do_edital` em todo Edital publicado das comissões da pessoa (o que a rodada 2 mediu);
- R1: só nos Editais que a pessoa **preside** (o vínculo lido direto em `MembroComissao`, e não pela
  base de `pode_gerir_comissao`, que devolve a sistêmica primeiro). Para os demais, a avaliação sai
  de `carga_nas_etapas`, que a página já calcula;
- R1+R2: e a versão vigente lida uma vez por Edital na requisição. A simulação troca
  `effective_version` por uma versão memorizada por Edital em todo módulo que a importou;
- R1+R2+R3: e a faixa da 104 lida uma vez, e não dentro de cada `do_edital`. A simulação troca
  `trabalho.do_ator` por um que devolve o resultado da leitura única filtrado pelo Edital.

Confere, em cada montagem, que os itens "seus" são os mesmos da montagem atual: a otimização não pode
mudar o que a pessoa vê.
"""

import sys
import time

from django.db import connection
from django.test.utils import CaptureQueriesContext

from processo_seletivo.avaliacoes.application import selectors as avaliacao_selectors
from processo_seletivo.comissoes.application import selectors as comissao_selectors
from processo_seletivo.comissoes.models import MembroComissao
from processo_seletivo.interface import andamento, atos_retificacao, providencias, trabalho
from processo_seletivo.interface.identidade import permissoes_de
from processo_seletivo.processos.models import Edital
from processo_seletivo.publicacoes.application import selectors as pub
from processo_seletivo.seguranca.domain import Actor
from processo_seletivo.unidades.models import Unidade

escopo = Unidade.objects.get().codigo
ORIGINAL_EV = pub.effective_version
ORIGINAL_DO_ATOR = trabalho.do_ator


def _publicados(processos):
    return list(
        Edital.objects.filter(processo_id__in=processos, status__in=("PUBLICADO", "ENCERRADO"))
        .exclude(processo__status__in=("ENCERRADO", "CANCELADO"))
        .select_related("processo")
        .order_by("processo__institutional_code")
    )


def _suas(editais, ator):
    chaves = set()
    for edital in editais:
        dados = andamento.do_edital(edital, ator, em_curso=atos_retificacao.em_curso(edital, ator))
        if dados:
            for item in dados.nivel_1.itens:
                if item.grupo == providencias.SUA:
                    chaves.add((edital.id, item.natureza, item.ato, item.onde))
    return chaves


def _trocar(nome, original, novo):
    for modulo in list(sys.modules.values()):
        if getattr(modulo, nome, None) is original:
            setattr(modulo, nome, novo)


def _memorizada():
    guardadas = {}

    def effective_version(*, edital_id, at=None):
        if edital_id not in guardadas:
            guardadas[edital_id] = ORIGINAL_EV(edital_id=edital_id, at=at)
        return guardadas[edital_id]

    return effective_version


def _medir(rotulo, montar):
    with CaptureQueriesContext(connection) as cq:
        t0 = time.perf_counter()
        resultado = montar()
        dt = time.perf_counter() - t0
    print(f"  {rotulo:12} {len(cq.captured_queries):5} consultas  {dt:5.2f}s  {len(resultado)} itens")
    return resultado


for subject in ("treino.presidencia", "treino.avaliacao1"):
    ator = Actor(subject, escopo, permissoes_de(()))
    print(f"\n{subject}")
    vinculos = MembroComissao.objects.filter(identity_subject=subject, ativo=True)
    todos = set(vinculos.values_list("processo_id", flat=True))
    presididos = set(vinculos.filter(funcao="PRESIDENTE").values_list("processo_id", flat=True))

    atual = _medir("atual", lambda: _suas(_publicados(todos), ator))

    def r1():
        # Onde preside, a derivação. Nos demais, só a avaliação, pela carga que a página já calcula
        # (e a conferência, que exigiria AlocacaoAConferencia: nenhum cenário tem).
        itens = _suas(_publicados(presididos), ator)
        atribuicoes = comissao_selectors.minhas_etapas(ator)
        carga = avaliacao_selectors.carga_nas_etapas(ator=ator, atribuicoes=atribuicoes)
        for item in atribuicoes:
            c = carga.get((item["edital"].id, str(item["etapa_id"])))
            if c and c.get("pendentes") and item["processo"].id not in presididos:
                itens.add((item["edital"].id, "avaliar", item["nome"], ""))
        return itens

    com_r1 = _medir("R1", r1)

    _trocar("effective_version", ORIGINAL_EV, _memorizada())
    try:
        com_r2 = _medir("R1+R2", r1)

        def r3():
            editais = _publicados(presididos)
            unica = ORIGINAL_DO_ATOR(ator, editais)

            def do_ator(ator_, editais_, **kwargs):
                ids = {e.id for e in editais_}
                return [o for o in unica if o.edital.id in ids]

            _trocar("do_ator", ORIGINAL_DO_ATOR, do_ator)
            try:
                return r1()
            finally:
                _trocar("do_ator", do_ator, ORIGINAL_DO_ATOR)

        _trocar("effective_version", pub.effective_version, _memorizada())
        com_r3 = _medir("R1+R2+R3", r3)
    finally:
        for modulo in list(sys.modules.values()):
            valor = getattr(modulo, "effective_version", None)
            if callable(valor) and valor is not ORIGINAL_EV and valor.__name__ == "effective_version" \
                    and valor.__module__ == __name__:
                setattr(modulo, "effective_version", ORIGINAL_EV)

    # A conferência de que a otimização não muda o que a pessoa vê. Para o avaliador, a montagem R1
    # nomeia a avaliação pela Etapa, e a derivação pelo ato: compara-se a quantidade e a natureza.
    def resumo(itens):
        return sorted((str(e), n) for e, n, *_ in itens)

    mesmo = resumo(atual) == resumo(com_r1) == resumo(com_r2) == resumo(com_r3)
    print(f"  mesmos itens seus nas quatro montagens: {mesmo}")
