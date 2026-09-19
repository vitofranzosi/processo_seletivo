"""Quando um Evento do Cronograma já venceu, e em que ano ele corre (028).

**Por que um módulo, e não duas linhas em quem pergunta.** A mesma regra é consultada de dois
lugares com entradas de formas diferentes: a conferência de publicação lê `startAt`/`endAt` como
texto ISO do conteúdo, e o selo da etapa do assistente lê `start_at`/`end_at` como `datetime` do
ORM. Escrevê-la duas vezes faria o selo e a Revisão poderem discordar sobre o mesmo cronograma —
que é exatamente a divergência que a `028` existe para não produzir (`T-003`).

Por isso o predicado recebe **instantes**, e não dicionário nem linha de tabela: converter é
trabalho de quem chama, e a regra não conhece nenhuma das duas formas.
"""

from datetime import datetime

from processo_seletivo.shared.tempo import ZONA


def vencido(inicio: datetime | None, termino: datetime | None, *, agora: datetime) -> bool:
    """O Evento já passou inteiro.

    **Havendo término, vence quem terminou; não havendo, vence quem começou** (037, `FR-545`,
    `FR-546`). A régua anterior vencia pelo **ou** dos dois instantes, e com isso chamava de
    vencido o período que estava **em curso**: o Edital que abre inscrições no dia em que é
    publicado ficava com a etapa do Cronograma eternamente pendente — impossível de concluir —, e
    a gestão contradizia o canal do candidato, que lia o mesmo Evento como acontecendo agora.

    **A correção óbvia está errada, e é por isso que o `if` existe.** Trocar a régua por "o
    término passou" é a leitura imediata do defeito, e ela **silenciaria o Evento pontual**: sem
    término, nenhum Evento venceria nunca. Ausência de término não é fim no futuro.

    **O `<` é estrito**, e não é detalhe de estilo: é a mesma régua que
    `inscricoes/domain/periodo.py` aplica com `agora > fim` para decidir se o período de inscrições
    encerrou (FR-347). Escrita aqui com `<=`, o selo da etapa diria "vencido" no mesmo segundo em
    que o impedimento diria "ainda não encerrado", e o sistema discordaria de si mesmo por um
    microssegundo — defeito que não reproduz quando alguém vai olhar.

    **Ausência não vence.** Término nulo é Evento que o Edital não fechou, e inventar-lhe um fim
    seria o sistema criando prazo que ninguém declarou — a recusa que `periodo.py` já registra por
    escrito. Início nulo não deveria existir no conteúdo publicado, e a conferência de forma o
    acusa; aqui ele simplesmente não responde.
    """
    if termino is not None:
        return termino < agora
    return inicio is not None and inicio < agora


def instante_vencido(
    inicio: datetime | None, termino: datetime | None, *, agora: datetime
) -> datetime | None:
    """Qual instante a mensagem nomeia, ou nenhum quando o Evento não venceu (FR-343a).

    **Ela deriva da mesma régua, e não de uma cópia dela** (037, `FR-546a`). Enquanto o predicado
    vencia pelo **ou**, esta função escolhia o instante por conta própria com a mesma condição
    escrita duas vezes — e mudar só o predicado faria as duas funções do mesmo módulo discordarem
    sobre o mesmo Evento: uma diria que ele não venceu, a outra continuaria nomeando o início
    dele. É exatamente a divergência que a `028` criou este módulo para impedir, e por isso as
    duas mudaram no mesmo ato.

    **O término tem precedência.** É o mais tardio dos dois, e é o que diz que o Evento *inteiro*
    acabou; nomear o início faria a frase falar de um prazo que ainda podia estar correndo quando a
    pessoa a leu. O início só aparece quando não há término declarado.

    A precedência é escrita aqui, e não em quem monta a mensagem, porque o **caminho** do achado
    acompanha o instante nomeado — a âncora tem de levar ao campo de que a frase fala —, e duas
    decisões separadas sobre a mesma escolha acabariam divergindo.
    """
    if not vencido(inicio, termino, agora=agora):
        return None
    return termino if termino is not None else inicio


def ano_do_evento(instante: datetime) -> int:
    """O ano em que o Evento corre, lido na zona institucional.

    **Nunca em UTC, e a diferença é real.** Um Evento em 31/12 às 23:30 em Vitória é 1º de janeiro
    em UTC: lido sem converter, um Edital de 2026 que o declare corretamente seria acusado de
    divergir de si mesmo — e só nos últimos horários do ano, que é a forma mais cara de defeito que
    existe, porque some antes de alguém conseguir olhar.

    Não é hipótese. `doc/achado-teste-com-data-em-utc.md` registra a classe, encontrada quando o CI
    do PR #102 reprovou num teste que aquele branch não tocava.

    A Constituição exige a mesma coisa em termos gerais no Princípio II: *"Regras de calendário
    DEVEM usar a zona temporal institucional definida pelo domínio"*.
    """
    return instante.astimezone(ZONA).year
