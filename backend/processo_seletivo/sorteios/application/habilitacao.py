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


def nome_da_etapa(conteudo, metapa):
    """O nome publicado da Etapa de habilitação, para a frase do critério. `""` quando não há."""
    if not metapa:
        return ""
    for etapa in conteudo.get("stages") or []:
        if str(etapa.get("id")) == str(metapa):
            return etapa.get("name") or ""
    return ""


__all__ = ["habilitadas_na_etapa", "nome_da_etapa"]
