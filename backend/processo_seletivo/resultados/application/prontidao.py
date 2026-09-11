"""Quem participa da Etapa, e o que impede cada um de ser consolidado.

Uma leitura, um número de consultas **constante**, e uma partição: cada participante ocupa
exatamente um estado, e a soma deles é o total. Sem isso, resumo e detalhe filtrado divergiriam, e
a presidência teria dois números para a mesma Etapa.

**Por que a classificação é Python sobre conjuntos, e não SQL.** A compatibilidade normativa
compara conteúdo publicado de duas Versões Consolidadas; isso não se exprime em agregação. O que
não se pode é pagar uma consulta por inscrição — e não se paga: o conjunto elegível vem numa
consulta só, com a versão junto, e a comparação acontece em memória sobre ele.

**A participação tem duas regras, e elas têm alcances diferentes** (D-003). A eliminação em
qualquer Etapa anterior exclui sempre; a exigência de habilitação é da imediatamente anterior e só
vale depois que ela produz Resultado. Enquanto não produz, a Etapa seguinte conserva o conjunto da
012 — e é isso que impede esta feature de esvaziar permanentemente a Etapa seguinte de um Edital de
leitura múltipla, que a V1 não consolida.
"""

from collections import namedtuple
from uuid import UUID

from django.db.models import BooleanField, Exists, ExpressionWrapper, OuterRef, Q

from processo_seletivo.avaliacoes.application.selectors import avaliacoes_elegiveis

# **Só `classificacao.models`, e nunca `classificacao.application.*`.**
# `classificacao/application/calculo.py` já importa **este** arquivo: o primeiro import do pacote de
# aplicação daquele app fecharia o ciclo, e o erro apareceria na primeira importação de qualquer um
# dos dois, num arquivo sorteado, longe da causa. `classificacao/models.py` não importa
# `resultados`, e é o que mantém o caminho aberto (014, R-005).
from processo_seletivo.classificacao.models import Corte, ItemDoCorte
from processo_seletivo.comissoes.domain.etapas import conteudo_vigente
from processo_seletivo.inscricoes.models import Inscricao
from processo_seletivo.recursos.application.selectors import reavaliacoes_pendentes
from processo_seletivo.resultados.application.selectors import (
    conteudos_das_versoes,
    eliminadas_ate,
    ha_resultado_em,
    habilitadas_em,
    inscricoes_com_resultado,
)
from processo_seletivo.resultados.domain.compatibilidade import incompatibilidade
from processo_seletivo.resultados.domain.progressao import etapa_anterior, etapas_anteriores
from processo_seletivo.resultados.domain.regra import impedimento_da_regra
from processo_seletivo.resultados.models import ResultadoEtapa

# Os cinco estados de prontidão. Formam partição: toda inscrição submetida do Edital ocupa um, e
# apenas um. `PENDENTE` e `CONSOLIDADO` da spec aparecem aqui como ausência e presença de linha —
# não há coluna de workflow, e ela não diria nada que a existência do Resultado já não diga.
ELIMINADA_ANTES = "eliminada-antes"
AGUARDANDO_ANTERIOR = "aguardando-anterior"
CONSOLIDADA = "consolidada"
PRONTA = "pronta"
IMPEDIDA = "impedida"
# O sexto estado, e o único que a 018 acrescenta. Ele existe porque a inscrição com reavaliação
# determinada **tem** Resultado — e por isso a prontidão a chamava de `consolidada`, escondendo
# justamente a pendência que a decisão criou. Quem organiza a Etapa precisa vê-la como trabalho a
# fazer, e não como trabalho feito (FR-067).
REAVALIACAO = "reavaliacao-determinada"

REAVALIACAO_PENDENTE = "reavaliação determinada por recurso, ainda não cumprida"

# O sétimo estado, e o único que a 014 acrescenta. Ele existe porque quem ficou fora da faixa **não
# é** eliminado nem está aguardando a Etapa anterior: ele foi considerado, tem posição na ordem, e a
# norma publicada o deixou de fora. Chamá-lo de qualquer um dos outros seis apagaria a diferença que
# é do candidato — "não fui chamado" contra "não sei por quê" (014, FR-210, UX-026).
FORA_DO_CORTE = "fora-do-corte"

#: A conclusão elegível, reduzida ao que a prontidão precisa saber sobre ela.
#:
#: Tupla, e não modelo: comparar a norma de mil avaliações exige a pontuação, a identidade e o
#: conteúdo da versão — e materializar mil `Avaliacao` com `select_related("versao")` traria mil
#: cópias do Edital inteiro em JSON para ler quatro campos. Quem precisa do objeto é a
#: consolidação, que o busca para as inscrições selecionadas, e não para a Etapa inteira.
# A conclusão como o Resultado precisa copiá-la: a forma diz qual dos dois campos vale, e o
# outro vem vazio (013, D-008). `versao_id` entra porque o Resultado passou a **guardar** a norma,
# em vez de alcançá-la por `avaliacao__versao` — e ela já vinha na mesma leitura, para resolver o
# conteúdo (D-1).
Conclusao = namedtuple(
    "Conclusao",
    ("avaliacao_id", "forma", "pontuacao", "sentido", "versao_id", "conteudo"),
    defaults=(None, None),
)

SEM_CONCLUSAO = "ainda não há avaliação concluída para esta inscrição"
CONCLUSOES_DEMAIS = (
    "há {quantas} avaliações concluídas onde o Edital prevê uma, e o sistema não escolhe qual vale"
)


def participacao_detalhada(*, edital, etapa_id, vigentes=None, conteudo=None):
    """`(participantes, eliminadas, aguardando)` — as duas regras de D-003, nesta ordem.

    **É a única fonte da participação**, e é por isso que ela vive aqui e não em cada superfície.
    A distribuição, a Mesa, a inscrição de trabalho, o documento e a próxima pendente perguntam
    todas a mesma coisa, e a resposta precisa ser a mesma nas cinco — senão a organização exclui e
    a Mesa entrega, que é a pior combinação possível.

    `vigentes` chega por parâmetro quando quem chama já o resolveu: a tela da Etapa lê o conteúdo
    publicado uma vez e o entrega, em vez de cada seletor relê-lo.
    """
    # **Uma leitura do conteúdo publicado serve às duas perguntas.** As Etapas anteriores e os
    # marcos que governam esta Etapa saem do mesmo documento, e lê-lo duas vezes é a consulta a mais
    # que os orçamentos da 011, da 012 e da 015 não têm.
    if conteudo is None:
        conteudo = conteudo_vigente(edital)
    if vigentes is None:
        vigentes = {UUID(str(etapa["id"])): etapa for etapa in conteudo.get("stages") or []}
    # **A condição do corte entra como anotação da consulta que já ia acontecer**, e não como uma
    # segunda leitura: `fora_do_corte` sozinho custaria a consulta a mais que o orçamento da tela da
    # Etapa não tem — foi o que a primeira redação fazia, e o teste de orçamento a reprovou.
    faixas = faixas_que_governam(edital, etapa_id, conteudo=conteudo)
    linhas = list(
        Inscricao.objects.filter(edital=edital, status=Inscricao.Status.SUBMETIDA)
        .annotate(
            na_faixa=ExpressionWrapper(
                _dentro_da_faixa(
                    faixas, OuterRef("pk"), OuterRef("profile_id"), OuterRef("modality_id")
                ),
                output_field=BooleanField(),
            ),
            # **A segunda anotação sai de graça na mesma consulta**, e é ela que evita a pergunta
            # "existe corte?" custar um round-trip só para decidir se vale conferir a obsolescência.
            ha_corte=ExpressionWrapper(
                Exists(_do_recorte(faixas, OuterRef("profile_id"), OuterRef("modality_id"))),
                output_field=BooleanField(),
            ),
        )
        .values_list("id", "na_faixa", "ha_corte")
    )
    submetidas = {identidade for identidade, _, _ in linhas}
    fora = {identidade for identidade, dentro, _ in linhas if not dentro}
    # **`None` quando não houve linha para perguntar**, e não `False`: com a coleção vazia a
    # anotação não responde nada, e tratar isso como "não há corte" faria a tela de uma Etapa sem
    # inscrição submetida afirmar que está em dia quando o corte dela está obsoleto. Quem precisar
    # da resposta ali pergunta ao banco — é uma consulta, e não há listagem a proteger.
    ha_corte = any(existe for _, _, existe in linhas) if linhas else None
    anteriores = [identidade for identidade, _ in etapas_anteriores(vigentes, etapa_id)]
    eliminadas = eliminadas_ate(edital=edital, etapas_ids=anteriores) & submetidas

    aguardando = set()
    imediata = etapa_anterior(vigentes, etapa_id)
    # O gate, e só ele: a exigência de habilitação fica dormente enquanto a Etapa anterior não
    # produziu Resultado nenhum. A exclusão por eliminação, acima, não tem gate.
    if imediata is not None and ha_resultado_em(edital=edital, etapa_id=imediata[0]):
        habilitadas = habilitadas_em(edital=edital, etapa_id=imediata[0])
        aguardando = submetidas - eliminadas - habilitadas
    # **A terceira regra, da 014, entra aqui pelo mesmo lugar das duas primeiras.** Quem ficou fora
    # da faixa sai de `participantes` — ele não é distribuível, não é avaliável e não conta como
    # pendente —, e quem precisa **nomeá-lo** o pede por `fora_do_corte`, que é o que a tela da
    # Etapa faz. A assinatura não muda, e os quatro consumidores desta função continuam corretos
    # sem tocar em nenhum deles (FR-208, FR-210).
    return submetidas - eliminadas - aguardando - fora, eliminadas, aguardando, fora, ha_corte


CORTE_OBSOLETO = "corte-obsoleto"


def impedimento_do_corte(edital, etapa_id, *, at=None):
    """`(codigo, frase)` enquanto a faixa que governa esta Etapa estiver obsoleta (014, FR-228).

    **É impedimento da Etapa inteira**, na forma que a `013` já usa para "regra insuficiente": a
    presidência o vê na prontidão antes de tentar consolidar, e nenhum estado novo de inscrição
    nasce — a partição continua fechando.

    **O caso que obriga a bloquear é o reingresso.** Deferido o recurso que devolve alguém ao
    universo da ordem, continuar trabalhando sob a faixa antiga é exatamente excluir quem teve o
    direito reconhecido — e o sistema já sabe disso, porque foi ele que marcou a causa. Seguir sem
    bloquear deixaria a operação construir, sobre uma faixa que o próprio sistema sabe estar para
    trás, trabalho que a sucessão invalida.

    **A leitura continua, e o registrado é preservado**: o que fica bloqueado é trabalho **novo**.
    """
    from processo_seletivo.classificacao.application.corte import estado_do_corte

    for corte in faixas_que_governam(edital, etapa_id).filter(raiz__isnull=True):
        estado = estado_do_corte(
            edital=edital,
            perfil_id=corte.perfil_id,
            marco_id=corte.marco_id,
            lista_id=corte.lista_id,
            at=at,
        )
        if estado["obsoleto"]:
            causas = "; ".join(item["descricao"] for item in estado["causas"])
            return (
                CORTE_OBSOLETO,
                "a faixa que governa esta Etapa está para trás, e o caminho é emitir a geração "
                f"sucessora — {causas}",
            )
    return None


def participacao(*, edital, etapa_id, vigentes=None, conteudo=None):
    """`(participantes, eliminadas, aguardando)` — o contrato que os quatro consumidores conhecem.

    A `014` acrescentou duas informações à mesma leitura — quem ficou fora da faixa, e se há corte
    governando —, e elas saem por `participacao_detalhada`. Mudar a aridade desta função obrigaria
    quatro chamadores a mudar para receber o que três deles não usam.
    """
    participantes, eliminadas, aguardando, _fora, _ha_corte = participacao_detalhada(
        edital=edital, etapa_id=etapa_id, vigentes=vigentes, conteudo=conteudo
    )
    return participantes, eliminadas, aguardando


def fora_do_corte(edital, etapa_id, candidatas):
    """Quem a faixa vigente deixou de fora, entre as inscrições dadas (014, FR-210).

    Conjunto **vazio** quando nenhuma regra publicada governa esta Etapa: sem corte não há ninguém
    fora dele, e é isso que preserva o comportamento de todo Edital anterior à feature.
    """
    faixas = faixas_que_governam(edital, etapa_id)
    return set(
        Inscricao.objects.filter(pk__in=candidatas)
        .exclude(
            _dentro_da_faixa(
                faixas, OuterRef("pk"), OuterRef("profile_id"), OuterRef("modality_id")
            )
        )
        .values_list("pk", flat=True)
    )


def marcos_que_governam(edital, etapa_id, *, conteudo=None, at=None):
    """Os marcos que a **norma vigente** declara governando esta Etapa (014, FR-208, FR-224).

    Lista vazia significa dormência, e ela tem duas causas que precisam ser a mesma coisa aqui:
    Edital que nunca declarou regra de corte, e Edital cuja Retificação a **removeu**. No segundo
    caso a faixa emitida continua no banco, e perguntá-la sem consultar a norma faria um corte
    revogado continuar governando a Etapa para sempre (edge case da §*Edge Cases*).

    **A regra é encontrada pela declaração**, nunca pela ordem das Etapas: num marco de sorteio a
    Etapa enumerada não significa nada, e derivar dali moveria em silêncio quem continua no certame.
    """
    from processo_seletivo.classificacao.domain import faixa
    from processo_seletivo.comissoes.domain.etapas import conteudo_vigente

    conteudo = conteudo_vigente(edital, at=at) if conteudo is None else conteudo
    alvo = str(etapa_id)
    return [
        str(marco.get("id"))
        for perfil in conteudo.get("profiles") or []
        if isinstance(perfil, dict)
        for marco in perfil.get("classificationMilestones") or []
        if isinstance(marco, dict) and faixa.etapa_governada(marco.get("cutRule")) == alvo
    ]


def faixas_que_governam(edital, etapa_id, *, marcos=None, conteudo=None, at=None):
    """As faixas da geração vigente dos cortes que governam esta Etapa (014, FR-208).

    **Devolve um queryset preguiçoso, e nunca ids materializados.** Ele entra como subconsulta
    dentro da consulta que já ia acontecer, e não custa round-trip nenhum: materializar custaria uma
    leitura por listagem, e os orçamentos de consulta da `011`, da `012` e da `015` não têm folga
    para isso — eles existem justamente para que uma feature seguinte não os corroa em silêncio.

    `marcos` chega pronto de quem já leu o conteúdo publicado, que é o caso das duas portas quentes.

    Vigente é a geração cuja **raiz** ninguém sucedeu, e vigente é toda faixa dela — a raiz e as
    continuações, juntas. Perguntar pela faixa sem sucessor devolveria só a continuação e esconderia
    a raiz, que continua governando quem progrediu primeiro (FR-227).
    """
    if marcos is None:
        marcos = marcos_que_governam(edital, etapa_id, conteudo=conteudo, at=at)
    return Corte.objects.filter(
        edital=edital, etapa_governada_id=etapa_id, marco_id__in=marcos
    ).filter(
        Q(raiz__isnull=True, sucessores__isnull=True)
        | Q(raiz__isnull=False, raiz__sucessores__isnull=True)
    )


def _do_recorte(faixas, perfil, modalidade):
    """As faixas que alcançam **esta** inscrição: as do Perfil dela, na lista dela.

    O recorte da feature é `(Perfil, marco, lista)`, e não só o Perfil. Um marco de cotas tem três
    atos raiz e três cortes, emitidos em instantes diferentes — e enquanto só o da PPI existisse, um
    filtro por Perfil despertaria o gate para o Perfil **inteiro**: as inscrições de PcD, ausentes
    dos itens da PPI, sairiam da Etapa sem que corte nenhum as tivesse cortado.

    **Corte sem lista alcança o Perfil inteiro**, porque é o recorte da ampla concorrência, de que
    todas as inscrições participam — é o que a cláusula 8.7 do 57 e do 28 manda. Corte **com** lista
    alcança quem declarou aquela Modalidade.
    """
    return faixas.filter(perfil_id=perfil).filter(Q(lista_id__isnull=True) | Q(lista_id=modalidade))


def _dentro_da_faixa(faixas, referencia, perfil, modalidade):
    """A condição inteira, **incluindo a dormência e o recorte** — sem perguntar antes se há corte.

    **A correlação com o Perfil é o que impede o corte de um alcançar os outros.** A Etapa é do
    Edital e alcança todos os Perfis, mas a inscrição pertence a um só, e o corte também: sem esta
    metade, um Edital de sete polos em que **um** emitiu corte deixaria os outros seis fora da Etapa
    inteira — o `~Exists` global veria faixas existindo e cobraria de todo mundo a presença num item
    que só existe para o polo que cortou.

    `~Exists(...)` não é correlacionado à **linha**, mas é correlacionado ao Perfil dela, e o banco
    o resolve dentro da mesma consulta. A alternativa — um `.exists()` em Python para decidir se
    aplica o filtro — custaria a consulta a mais que os orçamentos não têm. É também o que faz a
    condição ficar dormente onde ela deve ficar: Perfil sem regra, e Perfil com regra e sem corte
    emitido, conduzem a Etapa exatamente como antes desta feature (FR-214).
    """
    # **A correlação entra pelos campos do `corte`, e não filtrando o queryset de faixas antes.**
    # Um queryset já correlacionado, usado como `corte__in=...`, vira subconsulta de subconsulta: o
    # `OuterRef` passaria a resolver contra `ItemDoCorte`, e o Django recusa com `FieldError`. Aqui
    # cada `OuterRef` sobe exatamente um nível, que é o que ele sabe fazer.
    return ~Exists(_do_recorte(faixas, perfil, modalidade)) | Exists(
        ItemDoCorte.objects.filter(
            Q(corte__lista_id__isnull=True) | Q(corte__lista_id=modalidade),
            inscricao_id=referencia,
            corte__in=faixas,
            corte__perfil_id=perfil,
            consequencia=ItemDoCorte.Consequencia.PROGREDIU,
        )
    )


def _anteriores_e_gate(edital, etapa_id, vigentes=None):
    """`(identidades anteriores, identidade da imediata quando a exigência vigora)`.

    Uma leitura do conteúdo publicado e, no máximo, uma pergunta de existência. É todo o custo fixo
    que a progressão impõe às superfícies da 012 — o resto vira junção dentro da consulta que já ia
    acontecer.
    """
    # **O conteúdo publicado é lido aqui, e devolvido a quem chamou.** A condição do corte precisa
    # dos marcos que governam a Etapa, e eles saem do mesmo documento de onde saem as Etapas
    # anteriores: lê-lo duas vezes é a consulta a mais que os orçamentos da 011, da 012 e da 015
    # não têm — e foi o que reprovou três testes de uma vez quando a leitura era separada.
    conteudo = None
    if vigentes is None:
        conteudo = conteudo_vigente(edital)
        vigentes = {UUID(str(etapa["id"])): etapa for etapa in conteudo.get("stages") or []}
    anteriores = [identidade for identidade, _ in etapas_anteriores(vigentes, etapa_id)]
    imediata = etapa_anterior(vigentes, etapa_id)
    exigir = (
        imediata[0]
        if imediata is not None and ha_resultado_em(edital=edital, etapa_id=imediata[0])
        else None
    )
    return anteriores, exigir, conteudo


def restringir_a_participantes(
    consulta, *, edital, etapa_id, vigentes=None, prefixo="inscricao", conteudo=None
):
    """Aplica as duas regras de D-003 a um queryset que já fala de inscrições.

    **Restringir a consulta, e não materializar o conjunto.** Devolver ids e passá-los em `__in`
    custaria duas leituras completas de população por listagem, e as superfícies da 012 têm
    orçamento de consulta declarado em teste — a 011 e a 012 os escreveram justamente para que uma
    feature seguinte não os corroesse em silêncio. Dobradas em junção, as duas regras não custam
    round-trip nenhum: o que sobra é a leitura do conteúdo publicado e a pergunta do gate.

    `prefixo` diz como o queryset alcança a inscrição — `"inscricao"` a partir de `Atribuicao`,
    `""` quando a própria linha é a inscrição.

    **Subconsulta correlacionada, e não `exclude()` com dois campos.** A primeira redação usava
    `exclude(rel__etapa_id__in=..., rel__consequencia=ELIMINADA)`, e Django **não** garante que as
    duas condições recaiam sobre a mesma linha relacionada: ele gera dois `EXISTS` independentes.
    O efeito é uma exclusão indevida — quem foi eliminado numa Etapa *posterior* e habilitado numa
    anterior satisfaz as duas metades separadamente, e sairia do conjunto de uma Etapa em que
    deveria estar. `Exists` amarra Etapa e consequência na mesma linha, que é o que a regra diz.
    """
    anteriores, exigir, lido = _anteriores_e_gate(edital, etapa_id, vigentes)
    conteudo = conteudo or lido
    referencia = OuterRef(f"{prefixo}_id") if prefixo else OuterRef("pk")
    # **`vigentes` nos quatro `Exists`, e é aqui que o deferimento produz efeito** (018, T-004).
    # Uma eliminação **superada** por recurso deferido continuaria excluindo a pessoa de toda
    # Etapa seguinte — da distribuição, da Mesa, da prontidão e da próxima pendente. O
    # deferimento seria simbólico exatamente onde ele mais importa. O filtro se dobra nas
    # subconsultas correlacionadas que já existiam: nenhum round-trip a mais, e os orçamentos de
    # consulta da 011, da 012 e da 015 continuam valendo.
    if anteriores:
        # Regra 1, sem gate: eliminada em qualquer Etapa anterior está fora, sempre.
        consulta = consulta.filter(
            ~Exists(
                ResultadoEtapa.vigentes.filter(
                    inscricao_id=referencia,
                    etapa_id__in=anteriores,
                    consequencia=ResultadoEtapa.Consequencia.ELIMINADA,
                )
            )
        )
    if exigir is not None:
        # Regra 2, com gate: só depois que a imediatamente anterior produziu Resultado.
        consulta = consulta.filter(
            Exists(
                ResultadoEtapa.vigentes.filter(
                    inscricao_id=referencia,
                    etapa_id=exigir,
                    consequencia=ResultadoEtapa.Consequencia.HABILITADA,
                )
            )
        )
    # **Regra 3, da 014: o corte se soma, e não revoga** (FR-209). Eliminada em Etapa anterior
    # continua fora ainda que dentro da faixa, e por isso esta condição vem **depois** das duas —
    # ela restringe o que sobrou, e não o substitui. Dormente onde nenhuma regra publicada governa
    # esta Etapa, que é o que preserva o comportamento de todo Edital anterior à feature (FR-214).
    perfil = OuterRef(f"{prefixo}__profile_id") if prefixo else OuterRef("profile_id")
    modalidade = OuterRef(f"{prefixo}__modality_id") if prefixo else OuterRef("modality_id")
    consulta = consulta.filter(
        _dentro_da_faixa(
            faixas_que_governam(edital, etapa_id, conteudo=conteudo),
            referencia,
            perfil,
            modalidade,
        )
    )
    return consulta


def participa_da_etapa(*, edital, etapa_id, inscricao_id, vigentes=None):
    """A mesma pergunta, para **uma** inscrição — na rota individual, onde ela cabe.

    Duas perguntas de existência no pior caso, e nenhuma listagem passa por aqui: o docstring de
    `autorizacao.py` registra que listagem usa a forma em conjunto, e é ela que está acima.
    """
    anteriores, exigir, conteudo = _anteriores_e_gate(edital, etapa_id, vigentes)
    if (
        anteriores
        and ResultadoEtapa.vigentes.filter(
            inscricao_id=inscricao_id,
            etapa_id__in=anteriores,
            consequencia=ResultadoEtapa.Consequencia.ELIMINADA,
        ).exists()
    ):
        return False
    if (
        not Inscricao.objects.filter(pk=inscricao_id)
        .filter(
            _dentro_da_faixa(
                faixas_que_governam(edital, etapa_id, conteudo=conteudo),
                OuterRef("pk"),
                OuterRef("profile_id"),
                OuterRef("modality_id"),
            )
        )
        .exists()
    ):
        return False
    if exigir is None:
        return True
    return ResultadoEtapa.vigentes.filter(
        inscricao_id=inscricao_id,
        etapa_id=exigir,
        consequencia=ResultadoEtapa.Consequencia.HABILITADA,
    ).exists()


def panorama_da_etapa(*, edital, etapa, etapas_vigentes=None, conteudo=None):
    """Participação e prontidão da Etapa inteira, em consultas de número constante.

    Devolve `estados` como `{inscricao_id: (estado, motivo)}` cobrindo **toda** inscrição
    submetida, mais o impedimento da Etapa quando ele existe. É a única fonte dos números: o resumo
    conta a partir daqui, e a listagem filtra a partir daqui, de modo que os dois não podem
    divergir.
    """
    # **O conteúdo publicado, e não só as Etapas.** A condição do corte precisa dos marcos que
    # governam esta Etapa, e `effective_version` custa duas consultas: lê-lo aqui de novo, quando
    # quem chamou já o tinha, é o que reprovou três orçamentos. Quem ainda passa só as Etapas
    # continua funcionando — e pagando a leitura.
    participantes, eliminadas, aguardando, fora, ha_corte = participacao_detalhada(
        edital=edital, etapa_id=etapa["id"], vigentes=etapas_vigentes, conteudo=conteudo
    )
    resultados = inscricoes_com_resultado(edital=edital, etapa_id=etapa["id"])
    impedimento = impedimento_da_regra(etapa)
    # A conferência da obsolescência só é feita onde há corte — e `ha_corte` veio da mesma consulta
    # que já buscou as submetidas, de modo que a Etapa sem corte não paga nada por esta linha.
    if impedimento is None and ha_corte is not False:
        impedimento = impedimento_do_corte(edital, etapa["id"])
    # Duas consultas para a Etapa inteira, e nenhuma por inscrição — o mesmo orçamento que o resto
    # deste módulo respeita.
    reavaliacoes = reavaliacoes_pendentes(edital, etapa_id=etapa["id"])

    elegiveis = {}
    if impedimento is None:
        # `values_list` sobre o contrato herdado: o conjunto é o mesmo, e o que muda é o que vem
        # dentro dele. Os conteúdos das versões são resolvidos **uma vez por versão distinta** —
        # duas ou três por Edital —, e não uma por avaliação.
        linhas = list(
            avaliacoes_elegiveis(edital=edital, etapa_id=etapa["id"]).values_list(
                "inscricao_id", "id", "forma", "pontuacao", "sentido", "versao_id"
            )
        )
        conteudos = conteudos_das_versoes({linha[-1] for linha in linhas})
        for inscricao_id, avaliacao_id, forma, pontuacao, sentido, versao_id in linhas:
            elegiveis.setdefault(inscricao_id, []).append(
                Conclusao(
                    avaliacao_id, forma, pontuacao, sentido, versao_id, conteudos.get(versao_id)
                )
            )

    estados = {}
    for identidade in eliminadas:
        estados[identidade] = (ELIMINADA_ANTES, "eliminada em Etapa anterior")
    for identidade in aguardando:
        estados[identidade] = (AGUARDANDO_ANTERIOR, "aguardando o resultado da Etapa anterior")
    # **Quem ficou fora da faixa é nomeado, e não some da partição** (FR-210, UX-026). Sem esta
    # linha ele não ocuparia estado nenhum, e a soma dos estados deixaria de fechar com o total —
    # que é exatamente o defeito que este módulo existe para não ter.
    for identidade in fora - eliminadas - aguardando:
        estados[identidade] = (FORA_DO_CORTE, "fora da faixa que progride para esta Etapa")
    for identidade in participantes:
        estados[identidade] = _estado_do_participante(
            identidade, etapa, resultados, elegiveis, impedimento, reavaliacoes
        )
    panorama = {
        "participantes": participantes,
        # As decisões pendentes viajam **dentro** do panorama pela mesma razão que as contagens: a
        # consolidação precisa saber qual decisão está cumprindo, e recalculá-la lá seria a segunda
        # leitura do mesmo fato — com risco de as duas discordarem.
        "reavaliacoes": reavaliacoes,
        "eliminadas": eliminadas,
        "aguardando": aguardando,
        "resultados": resultados,
        "elegiveis": elegiveis,
        "impedimento_da_etapa": impedimento,
        "estados": estados,
    }
    # As contagens viajam **dentro** do panorama porque o resumo as lê daqui: um segundo cálculo,
    # em outro lugar, é exatamente o painel paralelo que D-004 recusa.
    panorama["contagens"] = contagens(panorama)
    return panorama


def identificador_da_etapa(etapa):
    """A identidade da Etapa como as chaves do domínio a guardam — `UUID`, e não texto."""
    from processo_seletivo.comissoes.application.comissao import identificador

    return identificador(etapa["id"])


def _estado_do_participante(identidade, etapa, resultados, elegiveis, impedimento, reavaliacoes):
    if (identidade, identificador_da_etapa(etapa)) in reavaliacoes:
        # **Antes de "já consolidada"**, e é toda a questão: ela tem Resultado, e por isso caía no
        # ramo de baixo e sumia da lista de trabalho. A decisão determinou reavaliar, e enquanto
        # ninguém o fizer a Etapa tem uma pendência nomeada (FR-067).
        return (REAVALIACAO, REAVALIACAO_PENDENTE)
    if identidade in resultados:
        # Já consolidada vem antes de tudo: reconsolidar não é o caminho normal esbarrando numa
        # regra, e apresentá-la como "pronta" convidaria a um ato que será recusado.
        return (CONSOLIDADA, "esta inscrição já possui Resultado nesta Etapa")
    if impedimento is not None:
        return (IMPEDIDA, impedimento[1])
    conclusoes = elegiveis.get(identidade, [])
    if not conclusoes:
        return (IMPEDIDA, SEM_CONCLUSAO)
    if len(conclusoes) > 1:
        # Só alcançável quando a quantidade prevista mudou depois das conclusões. Escolher uma
        # seria o sistema decidindo qual nota vale.
        return (IMPEDIDA, CONCLUSOES_DEMAIS.format(quantas=len(conclusoes)))
    divergencia = incompatibilidade(
        conteudo=conclusoes[0].conteudo, etapa_id=etapa["id"], etapa_vigente=etapa
    )
    if divergencia is not None:
        return (IMPEDIDA, divergencia[1])
    return (PRONTA, "pronta para consolidar")


def contagens(panorama):
    """Os totais da Etapa, derivados do mesmo dicionário que a listagem filtra.

    A partição é verificável por construção: `participantes + eliminadas + aguardando` é o total, e
    os quatro estados dos participantes somam `participantes`.
    """
    por_estado = {estado: 0 for estado in (CONSOLIDADA, PRONTA, IMPEDIDA, REAVALIACAO)}
    for estado, _ in panorama["estados"].values():
        if estado in por_estado:
            por_estado[estado] += 1
    return {
        "participantes": len(panorama["participantes"]),
        "eliminadas_antes": len(panorama["eliminadas"]),
        "aguardando_anterior": len(panorama["aguardando"]),
        "consolidadas": por_estado[CONSOLIDADA],
        "prontas": por_estado[PRONTA],
        "impedidas": por_estado[IMPEDIDA],
        "reavaliacoes": por_estado[REAVALIACAO],
        "total": len(panorama["estados"]),
    }
