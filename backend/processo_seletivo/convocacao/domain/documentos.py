"""O estado dos documentos da convocação, derivado — e a guarda dos desfechos que incluem (115).

**Nada aqui é gravado.** O estado do item e o da convocação são lidos das apresentações e das
conferências, que são append-only (FR-3590, FR-3591). Uma coluna de estado exigiria `UPDATE` numa
tabela que o recusa, e seria a segunda máquina de estados que a decisão do usuário proíbe (D-004):
a única consequência da conferência é a guarda do aceite e da regularização (FR-3592).

Funções puras sobre objetos que tenham os atributos dos modelos — a aplicação as alimenta com o que
já leu, numa consulta só por chamada, e o domínio não consulta nada por conta própria.
"""

from processo_seletivo.convocacao.domain import nomes

OBRIGATORIO = "OBRIGATORIO"
FACULTATIVO = "FACULTATIVO"
NAO_SE_APLICA = "NAO_SE_APLICA"


def vigente(linhas):
    """A mais recente — a apresentação de maior número, ou a última conferência."""
    return linhas[-1] if linhas else None


def estado_do_item(apresentacoes, conferencias):
    """Um dos seis estados da FR-3590, pela tabela escrita lá.

    `apresentacoes` em ordem de número; `conferencias` em ordem de registro.
    """
    apresentacao = vigente(apresentacoes)
    conferencia = vigente(conferencias)
    if conferencia is not None and conferencia.resultado == nomes.NAO_SE_APLICA_NA_CONFERENCIA:
        # O "não se aplica" vale mesmo que algo tenha sido apresentado depois: quem conferiu disse
        # que este documento não é pedido a esta pessoa, e uma nova versão não o torna pedido.
        if apresentacao is None or conferencia.apresentacao_id in (None, apresentacao.id):
            return nomes.ITEM_NAO_SE_APLICA
    if apresentacao is None:
        return nomes.ITEM_A_APRESENTAR
    if conferencia is None:
        return nomes.ITEM_RECEBIDO
    if conferencia.apresentacao_id != apresentacao.id:
        # A conferência julgou outra versão. Se ela era pendência, a nova é a resposta; se não, a
        # nova simplesmente chegou e ainda não foi vista.
        if conferencia.resultado == nomes.PENDENTE:
            return nomes.ITEM_COMPLEMENTADO
        return nomes.ITEM_RECEBIDO
    if conferencia.resultado == nomes.CONFORME:
        return nomes.ITEM_CONFORME
    return nomes.ITEM_PENDENTE


#: Os estados de item que contam como atendidos para os desfechos que incluem (FR-3592).
ATENDIDOS = (nomes.ITEM_CONFORME, nomes.ITEM_NAO_SE_APLICA)


def pendencias_para_incluir(itens):
    """Os itens obrigatórios que impedem o aceite e a regularização (FR-3592).

    `itens` são pares `(item, estado)`. Devolve os itens, na ordem recebida.
    """
    return [
        item for item, estado in itens if item.situacao == OBRIGATORIO and estado not in ATENDIDOS
    ]


def facultativos_sem_conferencia(itens):
    """Os facultativos apresentados e ainda não vistos: advertem, e não impedem (FR-3592)."""
    return [
        item
        for item, estado in itens
        if item.situacao == FACULTATIVO
        and estado in (nomes.ITEM_RECEBIDO, nomes.ITEM_COMPLEMENTADO)
    ]


def estado_da_convocacao(itens, *, decidida):
    """Um dos seis estados da FR-3591, na precedência escrita lá.

    `itens` são pares `(item, estado)`; os que não se aplicam pela lista não entram.
    """
    if decidida:
        return nomes.DOCUMENTOS_DECIDIDA
    pedidos = [(item, estado) for item, estado in itens if item.situacao != NAO_SE_APLICA]
    if not pedidos:
        return nomes.DOCUMENTOS_SEM_EXIGENCIA
    estados = {estado for _, estado in pedidos}
    if estados & {nomes.ITEM_RECEBIDO, nomes.ITEM_COMPLEMENTADO}:
        return nomes.DOCUMENTOS_PARA_CONFERIR
    if nomes.ITEM_PENDENTE in estados:
        return nomes.DOCUMENTOS_COM_PENDENCIA
    if any(
        item.situacao == OBRIGATORIO and estado == nomes.ITEM_A_APRESENTAR
        for item, estado in pedidos
    ):
        return nomes.DOCUMENTOS_AGUARDANDO
    return nomes.DOCUMENTOS_PRONTA


def fundamento_das_pendencias(pendentes):
    """O fundamento pré-redigido do indeferimento, a partir das pendências (FR-3594).

    `pendentes` são pares `(nome do documento, motivo)`. O texto é sugestão: quem registra o edita,
    e ele continua obrigatório e de quem o assina.
    """
    if not pendentes:
        return ""
    itens = "; ".join(f"{nome}: {motivo}" if motivo else nome for nome, motivo in pendentes)
    return f"Documentação exigida na convocação não atendida — {itens}."
