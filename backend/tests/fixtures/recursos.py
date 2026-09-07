"""O cenário da 018: uma peça interposta, admitida, julgada — e o Resultado sucessor que dela nasce.

**Estas fixtures montam o efeito pela via mais curta, e é deliberado.** Elas gravam pelo ORM o que
o comando de julgamento vai gravar depois, porque o que a Foundational precisa provar é o
**esquema**: que a cadeia de sucessão existe, que as constraints a protegem, e que as leituras de
efeito passam a ver só o vigente. Quando `julgar` existir, os testes de integração dele usam o
comando — e estas fixtures continuam servindo a quem precisa apenas de um par superado em pé.

Tudo o que se grava aqui atravessa as triggers de coerência: nenhuma delas é contornada, e é por
isso que a fixture é a melhor prova de que a coerência é satisfazível — um esquema que só aceita
linhas impossíveis passa em todos os testes negativos e em nenhum positivo.
"""

from datetime import timedelta

from processo_seletivo.recursos.models import DecisaoRecurso, JuizoDeAdmissibilidade, Recurso
from processo_seletivo.resultados.models import ResultadoEtapa


def interpor(*, inscricao, versao, resultado=None, publicacao=None, protocolo="REC-2026-TESTE001"):
    """A peça. Exatamente um objeto atacado, como `ck_recurso_objeto_unico` exige."""
    return Recurso.objects.create(
        protocolo=protocolo,
        inscricao=inscricao,
        interposto_por="candidato@exemplo.test",
        interposto_em=inscricao.criado_em if hasattr(inscricao, "criado_em") else _agora(),
        fundamentacao="A nota atribuída não corresponde ao que foi entregue.",
        resultado_atacado=resultado,
        publicacao_atacada=publicacao,
        versao=versao,
    )


def admitir(recurso, *, admitido=True, motivo="Tempestivo e regularmente instruído."):
    return JuizoDeAdmissibilidade.objects.create(
        recurso=recurso,
        admitido=admitido,
        motivo=motivo,
        decidido_por="julgadora@exemplo.test",
        decidido_em=_agora(),
    )


def decidir(
    recurso,
    *,
    especie=DecisaoRecurso.Especie.CORRECAO_FIXADA,
    protegido=None,
    consequencia="",
    forma="",
    pontuacao=None,
    sentido="",
    versao=None,
):
    """A decisão. `admitir` precisa ter sido chamada antes — a trigger o exige (FR-036)."""
    return DecisaoRecurso.objects.create(
        recurso=recurso,
        especie=especie,
        motivacao="O parecer não enfrentou o documento juntado na inscrição.",
        versao=versao or recurso.versao,
        decidido_por="julgadora@exemplo.test",
        decidido_em=_agora(),
        resultado_protegido=protegido,
        etapa_id=protegido.etapa_id if protegido is not None else None,
        consequencia=consequencia,
        forma=forma,
        pontuacao=pontuacao,
        sentido=sentido,
    )


def superar(superado, decisao, *, pontuacao=None, consequencia=None, motivo="Recurso deferido."):
    """O Resultado sucessor com origem `RECURSO`: a decisão é a fonte, e não há Avaliação.

    `consolidado_em` é deliberadamente **posterior** ao do superado: a trigger exige a cronologia
    monotônica, sem a qual "o mais recente" e "o vigente" poderiam divergir na auditoria.
    """
    return ResultadoEtapa.objects.create(
        inscricao=superado.inscricao,
        edital=superado.edital,
        etapa_id=superado.etapa_id,
        origem=ResultadoEtapa.Origem.RECURSO,
        avaliacao=None,
        versao=decisao.versao,
        forma=decisao.forma,
        pontuacao=pontuacao if pontuacao is not None else decisao.pontuacao,
        sentido=decisao.sentido,
        consequencia=consequencia or decisao.consequencia,
        motivo=motivo,
        consolidado_em=superado.consolidado_em + timedelta(minutes=1),
        consolidado_por="julgadora@exemplo.test",
        resultado_anterior=superado,
        motivo_da_superacao=motivo,
        decisao=decisao,
    )


def deferir_corrigindo(
    superado, *, versao, pontuacao, consequencia, forma=None, protocolo="REC-2026-TESTE001"
):
    """O caminho inteiro, do jeito que a jornada o percorre: interpor, admitir, julgar, superar.

    **A forma é a que a Etapa publica, e não a do Resultado superado** (FR-059). Corrigir um
    Resultado por Ocorrência — que não tem forma, porque ninguém avaliou — para uma pontuação exige
    declarar `PONTUADA`: a decisão passa a afirmar uma grandeza, e a conclusão precisa ser coerente
    com ela. Foi `ck_decisao_conclusao_por_forma` que apontou o deslize aqui, e é para isso que ela
    existe.
    """
    recurso = interpor(
        inscricao=superado.inscricao,
        versao=versao,
        resultado=superado,
        protocolo=protocolo,
    )
    admitir(recurso)
    if forma is None:
        forma = "PONTUADA" if pontuacao is not None else superado.forma
    decisao = decidir(
        recurso,
        protegido=superado,
        consequencia=consequencia,
        forma=forma,
        pontuacao=pontuacao,
        sentido="" if pontuacao is not None else superado.sentido,
        versao=versao,
    )
    return recurso, decisao, superar(superado, decisao, pontuacao=pontuacao)


def _agora():
    from django.utils import timezone

    return timezone.now()
