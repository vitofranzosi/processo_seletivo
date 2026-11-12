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

**Duas que movem, e uma terceira declaração que não move** (155, FR-6317). A passagem entre cotas
é resposta à mesma pergunta, publicada como as outras, e fica fora das espécies que revertem: a
ordem entre as cotas é do Edital, e o GPS ainda não a aplica.
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
        # Inclui `None`: Edital que não declara reversão não reverte. E inclui a passagem entre
        # cotas (155, FR-6318), que é declaração e não move nada.
        return 0
    saldo = max(int(efetivas) - int(ocupadas), 0)
    if not saldo:
        return 0
    if especie == nomes.REVERSAO_POR_ESGOTAMENTO and ha_quem_ocupar:
        return 0
    return saldo


def ha_quem_ocupar(*, posicoes, ja_ocupadas):
    """Se a ordem do recorte tem mais gente com posição do que vagas ocupadas (095, D-005).

    É a pergunta que separa as duas espécies, e saiu de `movimento.ha_quem_ocupar` para que a
    prévia da classificação a faça igual sobre a ordem fictícia.

    **Conta toda posição da ordem** — inclusive a de quem já ocupa pela ampla e a de quem ficou fora
    da faixa —, como a função de origem contava. Por isso uma reservada cujos autodeclarados todos
    ocupam pela ampla nunca esgota sob esta regra (DP-2 da `095`); a leitura da norma é do usuário,
    e a extração não a muda.
    """
    return sum(1 for posicao in posicoes if posicao is not None) > ja_ocupadas


def declarada(perfil):
    """O que o Perfil publicado declara sobre a vaga reservada não preenchida, ou `None`.

    Objeto `null` significa "este Edital não declara reversão"; objeto pela metade **não** existe,
    porque a publicação o recusa (016, `FR-251`). Aqui, portanto, basta ler `kind`.

    **Devolve as três respostas** (155, FR-6317): as duas que movem vaga e a passagem entre cotas,
    que não move. Quem precisa saber *o que o Edital disse* — a tela, a trilha, o universo congelado
    da apuração — lê esta; quem vai *mover* lê `especie_que_move`. Devolver `None` para a terceira
    faria a tela dizer "este Edital não declara" de um Edital que declarou, e oferecer a declaração
    de vaga não preenchida onde ele manda outra coisa (FR-6327).
    """
    objeto = perfil.get("vacancyReversion")
    if not isinstance(objeto, dict):
        return None
    especie = objeto.get("kind")
    return especie if especie in nomes.DECLARACOES_DE_REVERSAO else None


def especie_que_move(perfil):
    """A espécie que move vaga, das duas, ou `None` — também para a passagem entre cotas.

    É a leitura de quem cede quantidade: com a terceira resposta nada se move (155, FR-6318), porque
    a ordem entre as cotas é do Edital e o GPS ainda não a aplica. `quantidade_a_reverter` já cede
    zero para ela; esta função existe para que o chamador não dependa disso por acaso.
    """
    especie = declarada(perfil)
    return especie if especie in nomes.ESPECIES_DE_REVERSAO else None
