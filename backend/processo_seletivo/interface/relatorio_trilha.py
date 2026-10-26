"""Os registros da trilha depois do desfecho do Edital (099, FR-2526, R-008).

**Módulo próprio por causa de uma leitura só**: os Resultados de Etapa do Edital entram aqui
**todos**, superados inclusive, porque um Resultado gravado depois do encerramento e já superado
continua sendo registro posterior — e é isso que a pergunta quer contar. É a leitura que o contrato
de vigência (`tests/test_vigencia_do_resultado.py`) só admite declarada, e a dispensa é deste
módulo, e não da derivação inteira, para que uma leitura de efeito futura em
`relatorio_do_edital.py` não passe calada.

`trilha_do_edital` não serve: não reúne resultado, recurso, ordenação nem corte, e pagina por
cursor.
"""

from collections import Counter

from processo_seletivo.auditoria.models import RegistroAuditoria
from processo_seletivo.auditoria.selectors import _atos_da_conducao
from processo_seletivo.classificacao.models import AtoDeOrdenacao, Corte
from processo_seletivo.convocacao.application import atestar, comunicar
from processo_seletivo.divulgacao.models import PublicacaoResultado
from processo_seletivo.ocupacao.application import acrescimo
from processo_seletivo.publicacoes.models_retificacao import Retificacao
from processo_seletivo.recursos.application import instruir
from processo_seletivo.recursos.models import DecisaoRecurso, JuizoDeAdmissibilidade, Recurso
from processo_seletivo.resultados.models import ResultadoEtapa
from processo_seletivo.sorteios.application import relacao, sorteio
from processo_seletivo.sorteios.models import RelacaoDeHabilitados, Sorteio

#: O que cada operação auditada é, para quem não conhece a trilha. Operação fora daqui vira
#: "outros registros", e não some.
ROTULOS_DAS_OPERACOES = {
    "CONVOCACAO_DESFECHAR": "desfecho de convocação",
    "CONVOCACAO_CONVOCAR": "convocação",
    "OCUPACAO_APURAR": "nova apuração das vagas",
    "RESULTADO_PUBLICAR": "publicação de resultado",
    "CLASSIFICACAO_EMITIR": "nova ordem de classificação",
    "CORTE_EMITIR": "novo limite de chamada",
    "RESULTADO_CONSOLIDAR": "resultado de etapa",
    "RESULTADO_OCORRENCIA": "resultado de etapa",
    "recurso:interpor": "recurso apresentado",
    "recurso:admitir": "juízo de admissibilidade de recurso",
    "recurso:julgar": "julgamento de recurso",
    instruir.OPERACAO: "instrução de recurso",
    comunicar.COMUNICAR: "comunicação de convocação",
    atestar.ATESTAR: "atestado de fato externo",
    acrescimo.ACRESCENTAR: "vaga acrescida",
    acrescimo.DESFAZER: "acréscimo de vaga desfeito",
    relacao.PUBLICAR: "relação do sorteio publicada",
    sorteio.CONSTITUIR: "sorteio realizado",
}
#: A emissão do próprio relatório e o ato de desfecho não são "registro depois do desfecho"; o
#: acesso à instrução de um recurso é leitura registrada, e não ato.
OPERACOES_QUE_NAO_CONTAM = frozenset(
    {"EMITIR_RELATORIO", "ENCERRAR", "CANCELAR", instruir.OPERACAO_DE_ACESSO}
)


def posteriores(edital, desfecho_em, agora):
    """Os registros dos agregados do Edital depois do ato de desfecho (FR-2526, R-008)."""
    ids = {edital.pk}
    ids.update(Retificacao.objects.filter(edital=edital).values_list("id", flat=True))
    ids.update(Recurso.objects.filter(inscricao__edital=edital).values_list("id", flat=True))
    ids.update(
        DecisaoRecurso.objects.filter(recurso__inscricao__edital=edital).values_list(
            "id", flat=True
        )
    )
    ids.update(
        JuizoDeAdmissibilidade.objects.filter(recurso__inscricao__edital=edital).values_list(
            "id", flat=True
        )
    )
    ids.update(PublicacaoResultado.objects.filter(edital=edital).values_list("id", flat=True))
    ids.update(AtoDeOrdenacao.objects.filter(edital=edital).values_list("id", flat=True))
    ids.update(Corte.objects.filter(edital=edital).values_list("id", flat=True))
    # Apuração, vaga acrescida, convocação, desfecho, comunicação, atestado e instrução: a reunião
    # que a trilha do Edital já faz, e não uma segunda lista que esqueceria a próxima espécie.
    ids.update(_atos_da_conducao(edital))
    ids.update(Sorteio.objects.filter(edital=edital).values_list("id", flat=True))
    ids.update(RelacaoDeHabilitados.objects.filter(edital=edital).values_list("id", flat=True))
    ids.update(ResultadoEtapa.objects.filter(inscricao__edital=edital).values_list("id", flat=True))
    contagem = Counter()
    primeira = {}
    for operacao, instante in (
        RegistroAuditoria.objects.filter(
            aggregate_id__in=ids, occurred_at__gt=desfecho_em, occurred_at__lte=agora
        )
        .exclude(operation__in=OPERACOES_QUE_NAO_CONTAM)
        .values_list("operation", "occurred_at")
    ):
        rotulo = ROTULOS_DAS_OPERACOES.get(operacao, "outros registros")
        contagem[rotulo] += 1
        primeira[rotulo] = min(primeira.get(rotulo, instante), instante)
    return sorted(
        ((rotulo, n, primeira[rotulo]) for rotulo, n in contagem.items()),
        key=lambda x: (x[2], x[0]),
    )
