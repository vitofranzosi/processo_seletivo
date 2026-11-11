"""A ficha do barema como as telas a desenham — a Mesa, as conclusões, o julgamento, o portal (146).

Leitura, e não regra: quem calcula e recusa é `avaliacoes.domain.barema`. Aqui se juntam o barema
de uma versão, o detalhamento afirmado e a comprovação esperada, linha a linha, no formato que o
`_ficha_do_barema.html` e o acompanhamento do candidato leem.

**Módulo próprio, e não dentro da Mesa**: resultados, recursos e o portal leem a mesma ficha, e
importar a Mesa para isso os faria depender da autorização e da lista exigida dela.
"""

from decimal import Decimal

from processo_seletivo.avaliacoes.domain import barema
from processo_seletivo.shared.decimais import no_campo


def ficha_da_avaliacao(avaliacao, etapa_vigente, etapa_id, documentos, conteudo_vigente):
    """A ficha que a Mesa mostra, ou `None` quando a Etapa não tem barema.

    **Concluída, pela versão que ela cita** (D-011, FR-5233): uma Retificação posterior que
    renomeie um critério não muda o que a conclusão afirmou. **Rascunho, pela vigente** — é o que a
    avaliadora vai concluir, e a conclusão recusa versão mudada —, com o detalhamento reconciliado:
    o valor do critério que continua fica para reconfirmação, o do removido sai e o novo fica
    pendente (FR-5222).
    """
    if avaliacao is not None and avaliacao.estado == "CONCLUIDA" and avaliacao.versao_id:
        criterios = barema.barema_da_versao(avaliacao.versao, etapa_id)
        if not criterios:
            return None
        return ficha_do_barema(
            criterios,
            avaliacao.criterios,
            documentos,
            avaliacao.versao.content,
            total=avaliacao.pontuacao,
            concluida=True,
        )
    criterios = barema.criterios_da_etapa(etapa_vigente)
    if not criterios:
        return None
    anterior = avaliacao.criterios if avaliacao is not None else []
    return ficha_do_barema(
        criterios, barema.reconciliar(anterior, criterios), documentos, conteudo_vigente
    )


def ficha_do_barema(
    criterios,
    detalhamento,
    documentos,
    conteudo,
    *,
    total=None,
    concluida=False,
    titulo="Barema",
    chave="do-barema",
    na_mesa=True,
):
    """As linhas da ficha, com a comprovação resolvida — o que o template desenha (UX-422).

    `documentos` é a lista que a Mesa já mostra; o critério ligado a um deles ganha o "Abrir" do
    mesmo painel. O documento que a inscrição não apresentou aparece como "não apresentado", e zero
    é a resposta esperada. A parcela de cada linha do rascunho é refeita sem recusar: o valor que a
    máxima nova não admite precisa aparecer para ser corrigido, e quem recusa é a gravação.

    É o mesmo componente na tela de julgamento de recurso (146, FR-5227), com `na_mesa=False`: lá o
    "Abrir" da Mesa não vale — ele passa pela Atribuição de quem avalia —, e a comprovação é só o
    nome do documento. `titulo` e `chave` distinguem duas fichas na mesma página.
    """
    from processo_seletivo.publicacoes.infrastructure.pdf import pontuacao_do_criterio

    por_requisito = {str(item["id"]): item for item in documentos or []}
    nomes = {
        str(item.get("id")): item.get("name", "")
        for item in (conteudo or {}).get("documentRequirements") or []
        if isinstance(item, dict)
    }
    afirmado = {
        str(linha.get("criterionId")): linha
        for linha in detalhamento or []
        if isinstance(linha, dict)
    }
    linhas, soma, respondidos = [], Decimal("0"), 0
    for criterio in criterios:
        chave = str(criterio["id"])
        linha = afirmado.get(chave) or {}
        if concluida:
            parcela, limitada, erro = linha.get("parcela"), bool(linha.get("limitada")), ""
        else:
            parcela, limitada, erro = barema.parcela_exibivel(criterio, linha)
        if parcela is not None:
            respondidos += 1
            soma += Decimal(str(parcela))
        requisito = criterio.get("documentRequirementId")
        documento = None
        if requisito:
            listado = por_requisito.get(str(requisito))
            documento = {
                "id": str(requisito),
                "nome": (listado or {}).get("nome") or nomes.get(str(requisito), ""),
                "enviado": bool(listado and listado.get("enviado")),
                "tamanho": (listado or {}).get("tamanho"),
            }
        linhas.append(
            {
                "id": chave,
                "nome": criterio.get("name", ""),
                "descricao": (criterio.get("description") or "").strip(),
                "maxima": criterio.get("maximumScore"),
                "pontos_por_unidade": criterio.get("pointsPerUnit"),
                "por_unidade": barema.por_unidade(criterio),
                "unidade": (criterio.get("unitLabel") or "").strip(),
                "frase": pontuacao_do_criterio(criterio),
                "quantidade": no_campo(linha.get("quantidade")),
                "pontos": no_campo(linha.get("pontos")),
                "justificativa": linha.get("justificativa") or "",
                "parcela": None if parcela is None else Decimal(str(parcela)),
                "limitada": limitada,
                # O valor informado que a regra recusa não é pendente: está respondido, e errado.
                "pendente": parcela is None and not erro,
                "erro": erro,
                "documento": documento,
            }
        )
    if total is None and respondidos:
        total = soma
    return {
        "linhas": linhas,
        "total": total,
        "maxima": sum((Decimal(str(c.get("maximumScore") or 0)) for c in criterios), Decimal("0")),
        "pendentes": [linha["nome"] for linha in linhas if linha["pendente"]],
        "com_erro": [linha["nome"] for linha in linhas if linha["erro"]],
        "concluida": concluida,
        "titulo": titulo,
        "chave": chave,
        "na_mesa": na_mesa,
    }
