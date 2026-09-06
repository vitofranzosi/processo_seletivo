"""Os nomes que uma versão normativa dá àquilo que se cita por identidade.

A versão entra sempre como argumento e nunca é deduzida aqui, porque é justamente ela que separa
duas leituras que a tela apresenta lado a lado: **o ato histórico lê-se com os nomes da versão que
ele congelou** — resolver pela vigente faria uma Retificação que renomeia uma modalidade reescrever
retroativamente como um ato antigo é lido —, e a proposta calculada agora, com os da versão sob a
qual ela foi calculada.

O módulo mora no domínio da classificação porque é dela que o ato é: a divulgação (017) o lê para
compor as projeções do que vai a público, e a leitura da 015 o lê para nomear a proveniência do
próprio ato. A direção da dependência continua única.
"""

from processo_seletivo.classificacao.domain.universo import por_identidade


def nomes_do_marco(conteudo, *, perfil_id, marco_id):
    """Processo, perfil, marco e modalidades como **esta** versão os nomeia.

    `perfil` e `marco` saem inteiros, e não reduzidos ao nome, porque quem chama também lê regra
    deles — a escala do arredondamento, o código que ordena os marcos no certame — e reabrir o
    conteúdo para isso seria percorrer duas vezes o mesmo JSON.

    O que a versão não conhece sai vazio, nunca como identificador: um nome ausente é dito como
    ausência, e imprimir o UUID no lugar dele é o defeito que este módulo existe para não repetir.
    """
    perfil = por_identidade(conteudo.get("profiles"), perfil_id) or {}
    marco = por_identidade(perfil.get("classificationMilestones"), marco_id) or {}
    return {
        "processo": conteudo.get("processoTitle", "") or "",
        "perfil": perfil,
        "marco": marco,
        "modalidades": {
            str(item.get("id")): item.get("name") or ""
            for item in perfil.get("competitionModalities") or []
        },
    }


def edital_por_extenso(conteudo, edital):
    """`Edital 14/2026` — o Edital nomeado como um ato o nomeia, e nunca por identificador."""
    numero = conteudo.get("number") or edital.number
    ano = conteudo.get("year") or edital.year
    return f"Edital {numero}/{ano}"


__all__ = ["edital_por_extenso", "nomes_do_marco"]
