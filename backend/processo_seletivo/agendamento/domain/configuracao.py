"""O que impede gravar uma configuração — a lista inteira, de uma vez (167, FR-7204, T-005).

**Uma função para três lugares**: a gravação recusa se a lista não for vazia; o simulador a mostra
sem recusar (UX-760); e a conferência da entrega B a relerá contra o Evento vigente (FR-7221). É o
que garante que a conferência recuse exatamente o que a configuração recusaria.

A ordem é a do contrato (`contracts/recusas.md` §1), e não a dos campos na tela: a comissão lê
primeiro o que invalida tudo — duração, intervalo, dia, banca —, e depois o que é de uma linha.
"""

from processo_seletivo.agendamento.domain import recusas
from processo_seletivo.agendamento.domain.horarios import minutos


def problemas(configuracao, *, periodo):
    """`[Recusa, …]`, vazia quando a configuração pode ser gravada.

    `periodo` é `(primeiro dia, último dia)` do Evento vigente da Etapa, em datas locais, ou `None`
    para a Etapa sem Evento no cronograma — e então não há `dia_fora_do_periodo` (Edge Cases): a
    configuração é aceita, e a conferência avisa.
    """
    lista = []
    duracao, intervalo = configuracao.duracao, configuracao.intervalo
    duracao_valida = duracao is not None and duracao > 0
    if not duracao_valida:
        lista.append(recusas.duracao_nao_positiva())
    if intervalo is not None and intervalo < 0:
        lista.append(recusas.intervalo_negativo())
    dias = [(dia, pares) for dia, pares in configuracao.dias if dia is not None]
    if not dias:
        lista.append(recusas.sem_dia())
    if not configuracao.bancas:
        lista.append(recusas.sem_banca())

    if periodo is not None:
        inicio, fim = periodo
        for dia, _ in dias:
            if not inicio <= dia <= fim:
                lista.append(recusas.dia_fora_do_periodo(dia, periodo))

    com_dia = len(dias) > 1
    invertidas, menores, sobrepostas = [], [], []
    for dia, pares in dias:
        validas = []
        for inicio, fim in pares:
            if inicio is None or fim is None:
                continue
            if minutos(fim) <= minutos(inicio):
                invertidas.append(recusas.janela_invertida(dia, inicio, fim))
                continue
            validas.append((inicio, fim))
            if duracao_valida and minutos(fim) - minutos(inicio) < duracao:
                menores.append(
                    recusas.janela_menor_que_a_duracao(dia, inicio, fim, duracao, com_dia=com_dia)
                )
        # A sobreposição nomeia o par (US1, cenário 6). Encostar não é sobrepor: 08:00–12:00 e
        # 12:00–14:00 são dois turnos seguidos.
        validas.sort(key=lambda par: minutos(par[0]))
        for anterior, seguinte in zip(validas, validas[1:], strict=False):
            if minutos(seguinte[0]) < minutos(anterior[1]):
                sobrepostas.append(recusas.janelas_sobrepostas(dia, anterior, seguinte))
    lista += invertidas + menores + sobrepostas

    vistos = {}
    sem_nome = False
    repetidos = []
    for banca in configuracao.bancas:
        nome = (banca.nome or "").strip()
        if not nome:
            sem_nome = True
            continue
        chave = nome.casefold()
        if chave in vistos and chave not in repetidos:
            repetidos.append(chave)
        vistos.setdefault(chave, nome)
    if sem_nome:
        lista.append(recusas.banca_sem_nome())
    lista += [recusas.bancas_com_o_mesmo_nome(vistos[chave]) for chave in repetidos]

    contados = set()
    for dia, _ in dias:
        if dia in contados:
            lista.append(recusas.dia_repetido(dia))
        contados.add(dia)
    # Um dia repetido três vezes não diz a mesma frase duas: a correção é uma só.
    return _sem_repeticao(lista)


def _sem_repeticao(lista):
    vistas, unicas = set(), []
    for recusa in lista:
        if recusa.frase not in vistas:
            vistas.add(recusa.frase)
            unicas.append(recusa)
    return unicas
