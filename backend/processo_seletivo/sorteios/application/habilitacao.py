"""Quem está habilitado a participar, quando o Edital declara uma Etapa anterior (021, R-012).

**Módulo próprio porque duas leituras precisam da mesma resposta.** A publicação da relação a usa
para projetar quem entra; a prévia da tela a usa para mostrar quantos entrariam. Elas divergiam: a
prévia projetava sem o filtro, e a comissão via um número e congelava outro — sem que nada na tela
explicasse a diferença.

**`None` e conjunto vazio continuam sendo coisas diferentes.** O primeiro diz "não há Etapa de
habilitação antes do sorteio", que é o caso dos quatro Editais lidos; o segundo, "há, e ninguém
passou". Confundi-los esvaziaria um certame inteiro.
"""


def habilitadas_na_etapa(edital, metodo):
    """As identidades com Resultado vigente favorável na Etapa declarada, ou `None`."""
    etapa_de_habilitacao = (metodo or {}).get("qualifyingStageId")
    if not etapa_de_habilitacao:
        return None
    from processo_seletivo.resultados.models import ResultadoEtapa

    return {
        str(identidade)
        for identidade in ResultadoEtapa.vigentes.filter(
            edital=edital,
            etapa_id=etapa_de_habilitacao,
            consequencia=ResultadoEtapa.Consequencia.HABILITADA,
        ).values_list("inscricao_id", flat=True)
    }


def para_o_recorte(edital, metodo, habilitadas, lista_id, *, retiradas=None):
    """As habilitadas que **este** recorte conta: na lista reservada, sem a retirada (164, FR-7030).

    Na Etapa de habilitação, a progressão manda a inscrição retirada da reserva como `HABILITADA`,
    porque ela continua na ampla. A relação da lista reservada não pode incluí-la: ela deixou de
    concorrer por ela antes do sorteio. A da ampla a inclui como incluiria qualquer outra. Sem Etapa
    de habilitação (`None`), nada muda, como nada muda hoje com a eliminação.

    `retiradas` chega pronto de quem percorre vários recortes — a prévia —, para que a consulta e a
    leitura do conteúdo não se repitam a cada um (`retiradas_antes`).
    """
    if habilitadas is None or not lista_id:
        return habilitadas
    return habilitadas - (retiradas if retiradas is not None else retiradas_antes(edital, metodo))


def retiradas_antes(edital, metodo, conteudo=None):
    """As identidades com retirada da reserva vigente numa Etapa anterior à de habilitação.

    Uma consulta; o conteúdo só é lido quando há retirada a situar e quem chama não o passou.
    """
    from processo_seletivo.resultados.models import ResultadoEtapa

    linhas = list(
        ResultadoEtapa.vigentes.filter(
            edital=edital,
            consequencia=ResultadoEtapa.Consequencia.RETIRADA_DA_RESERVA,
        ).values_list("inscricao_id", "etapa_id")
    )
    if not linhas:
        return set()
    from processo_seletivo.comissoes.domain.etapas import conteudo_vigente

    conteudo = conteudo if conteudo is not None else conteudo_vigente(edital)
    ordem = {
        str(etapa.get("id")): etapa.get("order") or 0 for etapa in conteudo.get("stages") or []
    }
    limite = ordem.get(str((metodo or {}).get("qualifyingStageId")), 0)
    return {str(inscricao) for inscricao, etapa in linhas if ordem.get(str(etapa), limite) < limite}


def nome_da_etapa(conteudo, metapa):
    """O nome publicado da Etapa de habilitação, para a frase do critério. `""` quando não há."""
    if not metapa:
        return ""
    for etapa in conteudo.get("stages") or []:
        if str(etapa.get("id")) == str(metapa):
            return etapa.get("name") or ""
    return ""


__all__ = ["habilitadas_na_etapa", "nome_da_etapa", "para_o_recorte", "retiradas_antes"]
