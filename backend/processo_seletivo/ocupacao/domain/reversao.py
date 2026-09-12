"""As duas espécies de gatilho da reversão de cota, puras (016, `D-007`).

**Por que são duas, e não uma.** O 28/2026 (4.3) reverte *"havendo ausência de candidatos aprovados
na reserva"*; o 57/2026 (4.3), *"na hipótese do não preenchimento total"*. O primeiro só reverte
quando a lista reservada esvazia; o segundo reverte o saldo ainda que a lista tenha gente. Tratar as
duas redações como o mesmo efeito fixaria, em ato publicado, uma escolha que é de **norma** — e
vaga revertida sob a leitura larga num Edital que manda a estreita é vaga que saiu do recorte
reservado sem fundamento.

**Ausência de declaração significa "não reverte"**, e não "reverte do jeito comum" (016, `D-002`).
O 57/2026 prova por que: o item 4.5 dele proíbe por escrito o remanejamento entre cursos, e um
sistema que revertesse por conta própria produziria ali exatamente o que o Edital veda.
"""

from processo_seletivo.ocupacao.domain import nomes


def quantidade_a_reverter(*, especie, efetivas, ocupadas, ha_quem_ocupar):
    """Quantas vagas a cota cede à ampla concorrência. Zero quando não cede.

    `ha_quem_ocupar` é o que separa as duas espécies, e **não** é a contagem de ocupadas: é se a
    ordem daquela lista ainda tem alguém por analisar. Sob esgotamento, havendo quem ocupar não se
    reverte nada — a vaga continua sendo da cota, esperando análise.

    **O saldo sai das efetivas, e não das publicadas — e é isso que impede a reversão de duplicar.**
    Cedidas todas, a apuração seguinte lê o movimento, chega com `efetivas` já reduzida, e o saldo
    dá zero. Partir de `publicadas` faria cada nova apuração da cota ceder a mesma quantidade outra
    vez, e a aritmética é uma guarda mais barata que uma constraint.
    """
    if especie not in nomes.ESPECIES_DE_REVERSAO:
        # Inclui `None`: Edital que não declara reversão não reverte.
        return 0
    saldo = max(int(efetivas) - int(ocupadas), 0)
    if not saldo:
        return 0
    if especie == nomes.REVERSAO_POR_ESGOTAMENTO and ha_quem_ocupar:
        return 0
    return saldo


def declarada(perfil):
    """A espécie declarada no Perfil publicado, ou `None`.

    Objeto `null` significa "este Edital não declara reversão"; objeto pela metade **não** existe,
    porque a publicação o recusa (016, `FR-251`). Aqui, portanto, basta ler `kind`.
    """
    objeto = perfil.get("vacancyReversion")
    if not isinstance(objeto, dict):
        return None
    especie = objeto.get("kind")
    return especie if especie in nomes.ESPECIES_DE_REVERSAO else None
