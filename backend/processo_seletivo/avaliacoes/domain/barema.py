"""O total da Etapa com barema, calculado critério a critério — uma função só (146, D-005).

**O total continua sendo o número de hoje.** Esta função recebe o barema publicado e o que o
avaliador afirmou em cada critério, e devolve as parcelas e a soma delas em `decimal(7,4)`; quem
grava o total em `Avaliacao.pontuacao` é o serviço da Mesa, e daí em diante a consolidação, a
classificação e o recurso leem o campo de sempre (FR-5215, FR-5220). O cliente não envia o total:
a tela o mostra ao vivo, e o servidor o refaz.

**Duas formas, deduzidas de `pointsPerUnit`** (D-002, FR-5202): com ele, o avaliador informa a
quantidade e a parcela é `min(quantidade × pontos, máxima)`; sem ele, informa os pontos, de zero à
máxima. Nada de tipo, fórmula ou grupo.

**A justificativa é texto livre, e nunca obrigatória** (D-008, FR-5218). O arquivo ligado não diz
quais dos critérios o candidato reivindicou, e exigir justificativa no zero produziria fundamentação
artificial. A obrigatória continua sendo a do parecer, sobre o total.

**O detalhamento guarda só o `criterionId`** (D-011). Nome, descrição e máxima vêm do conteúdo da
versão que o ato cita — `barema_da_versao` —, e só o rascunho se lê pela vigente (`reconciliar`).
Copiar o texto para o JSON seria a segunda fonte do que a versão já guarda.

**Parcela e marca de limite são gravadas, e não recalculadas na leitura**: a leitura de um ato
antigo não pode depender de refazer a conta sob uma regra que talvez mude.
"""

from decimal import Decimal, InvalidOperation

from processo_seletivo.avaliacoes.domain.pontuacao import CASAS, TETO_DA_PERSISTENCIA
from processo_seletivo.avaliacoes.domain.previsao import etapa_do_conteudo
from processo_seletivo.publicacoes.infrastructure import humano
from processo_seletivo.shared.api.problems import DomainError

# Inteiro de zero a 9999 (FR-5216): "52 meses" num critério de 1 ponto por mês até 40 é resposta
# legítima, e a parcela é limitada; dez mil unidades de qualquer coisa não é título, é erro de
# digitação.
QUANTIDADE_MAXIMA = 9999

CRITERIO_INVALIDO = "criterio_invalido"
CRITERIOS_PENDENTES = "criterios_pendentes"


def criterios_da_etapa(etapa):
    """A lista publicada da Etapa, na ordem da ficha. Vazia na Etapa sem barema — e no acervo."""
    if not isinstance(etapa, dict):
        return []
    return [c for c in etapa.get("criteria") or [] if isinstance(c, dict) and c.get("id")]


def tem_barema(etapa):
    """Se a Mesa pontua esta Etapa critério a critério (FR-5214)."""
    return bool(criterios_da_etapa(etapa))


def barema_da_versao(versao, etapa_id):
    """Os critérios **que aquela versão publicou** para a Etapa (D-011, FR-5233).

    A leitura única de toda tela que mostra o detalhamento de um ato — a Conclusão preservada, o
    Resultado, a Decisão de recurso. Aceita a Versão Consolidada ou o conteúdo dela: quem lê muitas
    conclusões já tem os conteúdos distintos em mão, e não precisa de mil cópias do Edital.
    """
    if versao is None:
        return []
    conteudo = versao if isinstance(versao, dict) else getattr(versao, "content", None)
    return criterios_da_etapa(etapa_do_conteudo(conteudo, etapa_id))


def comprovados_pelo_documento(conteudo, requirement_id):
    """Os critérios que um Documento Exigido comprova, em todas as Etapas do conteúdo (FR-5224).

    É o que a linha do documento diz ao candidato: "Comprova: Diploma de Doutorado (até 20), …". Um
    arquivo só, como hoje, e a linha lista o que ele pode comprovar — sem obrigar o candidato a
    enviar o mesmo título duas vezes nem a comissão a justificar cada critério não comprovado.
    """
    alvo = str(requirement_id)
    return [
        criterio
        for etapa in (conteudo or {}).get("stages") or []
        for criterio in criterios_da_etapa(etapa)
        if str(criterio.get("documentRequirementId") or "") == alvo
    ]


def por_unidade(criterio):
    """Pontua por quantidade? A pergunta que decide qual campo vale (FR-5202)."""
    return criterio.get("pointsPerUnit") not in (None, "")


def _decimal(valor):
    try:
        return Decimal(str(valor))
    except (InvalidOperation, ValueError, TypeError):
        return None


def _recusa(criterio, mensagem, *, codigo=CRITERIO_INVALIDO):
    """Recusa que aponta a linha: o campo é o do critério, e a frase o nomeia."""
    return DomainError(
        codigo,
        f"{_nome(criterio)}: {mensagem}",
        422,
        campo=f"criterio-{criterio.get('id')}",
    )


def _nome(criterio):
    return (criterio.get("name") or "").strip() or "Critério"


def _vazio(valor):
    return valor is None or (isinstance(valor, str) and not valor.strip())


def _quantidade(criterio, bruta):
    """Inteiro de 0 a 9999, ou recusa nomeando o critério."""
    texto = str(bruta).strip()
    try:
        valor = Decimal(texto.replace(",", "."))
    except (InvalidOperation, ValueError) as exc:
        raise _recusa(criterio, "a quantidade precisa ser um número inteiro.") from exc
    if not valor.is_finite() or valor != valor.to_integral_value():
        raise _recusa(criterio, "a quantidade precisa ser um número inteiro.")
    if valor < 0:
        raise _recusa(criterio, "a quantidade não pode ser negativa.")
    if valor > QUANTIDADE_MAXIMA:
        raise _recusa(criterio, f"a quantidade não pode passar de {QUANTIDADE_MAXIMA}.")
    return int(valor)


def _pontos(criterio, bruto, maxima):
    """Decimal de quatro casas, de zero à máxima do critério (FR-5216).

    **A máxima é cobrada também no rascunho**, e não só na conclusão como a pontuação única faz. Lá
    a razão de esperar era não obrigar a concluir para descobrir se o número passa; aqui a máxima
    está escrita na própria linha, e aceitar 16 num critério de 15 faria o rascunho gravar um total
    acima da máxima da Etapa — o que SC-1626 diz que nunca acontece.
    """
    texto = str(bruto).strip().replace(",", ".")
    try:
        valor = Decimal(texto)
    except (InvalidOperation, ValueError) as exc:
        raise _recusa(criterio, "os pontos precisam ser um número.") from exc
    if not valor.is_finite():
        raise _recusa(criterio, "os pontos precisam ser um número.")
    if valor < 0:
        raise _recusa(criterio, "os pontos não podem ser negativos.")
    try:
        if valor != valor.quantize(CASAS):
            raise _recusa(criterio, "os pontos admitem no máximo quatro casas decimais.")
    except InvalidOperation as exc:
        raise _recusa(criterio, "os pontos precisam ser um número.") from exc
    if valor > maxima:
        raise _recusa(
            criterio,
            f"os pontos não podem superar {humano.decimal(maxima)}, que é a máxima do critério.",
        )
    return valor.quantize(CASAS)


def _texto(valor):
    return "" if valor is None else str(valor).strip()


def _por_id(detalhamento, publicados):
    """O que foi afirmado, indexado pelo critério — recusando o desconhecido e o repetido.

    O critério desconhecido é recusado, e não ignorado: ignorar faria a tela de outra versão gravar
    meia ficha em silêncio. O repetido também: duas linhas para o mesmo critério não têm soma certa.
    """
    conhecidos = {str(c["id"]) for c in publicados}
    afirmado = {}
    for linha in detalhamento or []:
        if not isinstance(linha, dict):
            raise DomainError(CRITERIO_INVALIDO, "O detalhamento por critério é inválido.", 422)
        chave = str(linha.get("criterionId") or "")
        if chave not in conhecidos:
            raise DomainError(
                CRITERIO_INVALIDO,
                "O detalhamento cita um critério que o barema publicado não tem. Recarregue a "
                "página e pontue de novo.",
                422,
                campo="criterios",
            )
        if chave in afirmado:
            raise DomainError(
                CRITERIO_INVALIDO,
                "O detalhamento repete um critério do barema.",
                422,
                campo="criterios",
            )
        afirmado[chave] = linha
    return afirmado


def calcular(criterios_publicados, detalhamento, *, exigir):
    """`(linhas, total)` — as parcelas na ordem do barema, e a soma delas.

    `exigir=False` é o rascunho: critério em branco é aceito e fica pendente, e o total é a soma do
    que já foi respondido — `None` se nada foi (FR-5217). `exigir=True` é a conclusão: todo critério
    precisa de resposta — **zero é resposta** —, e a recusa nomeia os pendentes.

    O total é somado em `Decimal` e independe da ordem em que as linhas chegam (SC-1629). Ele nunca
    passa da máxima da Etapa, porque cada parcela é limitada pela sua e a soma das máximas é a
    máxima da Etapa (D-003); o teto da coluna é conferido mesmo assim, porque o conteúdo pode ter
    chegado por caminho que não passou pela validação de publicação.
    """
    publicados = list(criterios_publicados or [])
    afirmado = _por_id(detalhamento, publicados)
    linhas, total, respondidos, pendentes = [], Decimal("0"), 0, []
    for criterio in publicados:
        chave = str(criterio["id"])
        linha = afirmado.get(chave) or {}
        maxima = _decimal(criterio.get("maximumScore"))
        if maxima is None or maxima <= 0:
            raise _recusa(criterio, "o barema publicado não declara a máxima deste critério.")
        quantidade, pontos, parcela, limitada = None, None, None, False
        if por_unidade(criterio):
            # O campo da outra forma é recusado, e não ignorado (o mesmo princípio de FR-122): a
            # tela certa nunca o envia, e ignorá-lo faria o envio forjado decidir em silêncio.
            if not _vazio(linha.get("pontos")):
                raise _recusa(criterio, "este critério se pontua por quantidade, e não por pontos.")
            if not _vazio(linha.get("quantidade")):
                quantidade = _quantidade(criterio, linha.get("quantidade"))
                unidade = _decimal(criterio.get("pointsPerUnit")) or Decimal("0")
                bruta = (unidade * quantidade).quantize(CASAS)
                limitada = bruta > maxima
                parcela = min(bruta, maxima).quantize(CASAS)
        else:
            if not _vazio(linha.get("quantidade")):
                raise _recusa(criterio, "este critério se pontua por pontos, e não por quantidade.")
            if not _vazio(linha.get("pontos")):
                pontos = _pontos(criterio, linha.get("pontos"), maxima)
                parcela = pontos
        if parcela is None:
            pendentes.append(_nome(criterio))
        else:
            respondidos += 1
            total += parcela
        linhas.append(
            {
                "criterionId": chave,
                "quantidade": quantidade,
                "pontos": None if pontos is None else f"{pontos:f}",
                "parcela": None if parcela is None else f"{parcela:f}",
                "limitada": limitada,
                "justificativa": _texto(linha.get("justificativa")),
            }
        )
    if exigir and pendentes:
        raise DomainError(
            CRITERIOS_PENDENTES,
            "Responda todos os critérios do barema antes de concluir — zero também é resposta. "
            "Pendentes: " + "; ".join(pendentes) + ".",
            422,
            campo="criterios",
        )
    if not respondidos:
        return linhas, None
    total = total.quantize(CASAS)
    if total > TETO_DA_PERSISTENCIA:
        raise DomainError(
            CRITERIO_INVALIDO,
            f"O total do barema não pode superar {TETO_DA_PERSISTENCIA:f}, que é o máximo que o "
            "registro comporta.",
            422,
            campo="criterios",
        )
    return linhas, total


def reconciliar(detalhamento, criterios_vigentes):
    """O detalhamento reaberto, lido pelo barema vigente (FR-5222).

    O valor de critério que continua é mantido, para reconfirmação; o de critério removido sai; o
    critério novo fica pendente. Quando o critério continua e mudou de forma — passou de quantidade
    a pontos diretos, ou o contrário —, o valor antigo não responde a pergunta nova e fica pendente
    também. Parcela e limite não se copiam: são refeitos pelo cálculo, contra a máxima de agora.
    """
    anteriores = {
        str(linha.get("criterionId")): linha
        for linha in detalhamento or []
        if isinstance(linha, dict) and linha.get("criterionId")
    }
    reconciliado = []
    for criterio in criterios_vigentes or []:
        chave = str(criterio["id"])
        anterior = anteriores.get(chave) or {}
        quantidade = anterior.get("quantidade") if por_unidade(criterio) else None
        pontos = None if por_unidade(criterio) else anterior.get("pontos")
        reconciliado.append(
            {
                "criterionId": chave,
                "quantidade": quantidade,
                "pontos": pontos,
                "justificativa": _texto(anterior.get("justificativa")),
            }
        )
    return reconciliado


def parcela_exibivel(criterio, linha):
    """A parcela de uma linha do rascunho, para a tela: `(parcela, limitada, erro)`.

    Não recusa: o rascunho reaberto pode trazer um valor que a máxima nova não admite, e a tela
    precisa mostrá-lo **com a razão** — "os pontos não podem superar 10" —, e não como um pendente
    qualquer, para que a avaliadora o corrija antes de gravar. Quem recusa é `calcular`, ao gravar,
    com a mesma frase.
    """
    try:
        linhas, _ = calcular([criterio], [{**linha, "criterionId": criterio["id"]}], exigir=False)
    except DomainError as recusa:
        # A frase do domínio começa pelo nome do critério, que a linha da tela já mostra.
        return None, False, recusa.detail.split(": ", 1)[-1]
    return linhas[0]["parcela"], linhas[0]["limitada"], ""


__all__ = [
    "CRITERIOS_PENDENTES",
    "CRITERIO_INVALIDO",
    "QUANTIDADE_MAXIMA",
    "barema_da_versao",
    "calcular",
    "comprovados_pelo_documento",
    "criterios_da_etapa",
    "parcela_exibivel",
    "por_unidade",
    "reconciliar",
    "tem_barema",
]
