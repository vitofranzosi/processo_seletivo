"""A apuração de ocupação, pura: quadro, ordem e recusas entram; três quantidades saem.

**Nada aqui toca banco nem ORM**, pela mesma razão de `classificacao/domain/faixa.py`: é o que
torna a reprodutibilidade da `FR-244` testável sem migrar nada, e é o que permite reproduzir uma
apuração antiga alimentando a função com o que o ato congelou.

**Três quantidades saem, e a quarta é aritmética.** `publicadas`, `efetivas` e `ocupadas` são
gravadas; `faltando` é `efetivas - ocupadas`, calculado na leitura. Guardar a quarta seria
armazenar o derivável — e `efetivas`, ao contrário, **precisa** ser gravada, porque depende de
somar movimentos e `CHECK` não agrega (016, R-006).
"""

from processo_seletivo.ocupacao.domain import nomes

# **A leitura da linha do quadro NÃO é reimplementada aqui.** `classificacao.application.corte`
# já tem `linha_do_quadro(conteudo, perfil_id=..., lista_id=...)`, e ela faz uma coisa que um
# segundo leitor erraria: quando o `lista_id` é a Modalidade que o Perfil declara como ampla
# concorrência, ela lê a **linha geral** — porque é lá que a quantidade da ampla mora. Escrever a
# regra de novo aqui produziria dois módulos respondendo diferente para o mesmo recorte, e o alvo
# derivado do corte discordaria da apuração no Edital do formato normal.
#
# A aplicação chama aquele leitor e entrega o número pronto a `apurar`. É por isso que esta camada
# não conhece `conteudo` nenhum: ela recebe quantidades.


def mesma_lista(a, b):
    """Dois recortes são o mesmo. `None` é a ampla concorrência, e aqui ele **compara igual**.

    Em SQL `NULL = NULL` não é verdadeiro, e é por isso que a constraint de recortes distintos
    precisa de três metades. Em Python a comparação direta funciona, mas os valores chegam como
    `UUID` de um lado e `str` do outro — normalizar num lugar só evita a divergência silenciosa.
    """
    return (str(a) if a else None) == (str(b) if b else None)


class EmpateNaFronteiraDoAlvo(Exception):
    """O empate residual não julgado atravessa a fronteira do **alvo** (019, `R-002`).

    **Não é a fronteira da `014`, e é por isso que existe uma recusa nova.** Aquela trata o empate
    na última posição **da faixa** — `alvo + excedente` —, e o Edital declara `tieOutcome` para ela.
    Titular inicial é contado até o **alvo**, que é outra fronteira, e para essa a norma publicada
    não diz nada.

    As duas saídas fáceis afirmariam regra que ninguém escreveu: incluir todos os empatados faria
    `ocupadas > efetivas` e a constraint da `016` recusaria o ato; escolher por ordem de chegada
    inventaria desempate. Recusar é o que a `014` já faz quando o Edital publicou alvo estrito e o
    empate cruza a faixa — e o caminho de saída já existe: julgar o desempate na `015`.

    Carrega a posição e o tamanho do empate pela mesma razão da `EmpateAtravessaOCorte`: quem lê a
    mensagem precisa saber onde a ordem parou de separar, e quantos desempates julgar.
    """

    codigo = nomes.EMPATE_NA_FRONTEIRA_DO_ALVO

    def __init__(self, posicao, quantas):
        self.posicao = posicao
        self.quantas = quantas
        super().__init__(
            f"empate residual na posição {posicao}, com {quantas} participantes, "
            "atravessando a fronteira do alvo"
        )


def chave_da_inscricao(identificador):
    """A identidade comparável de uma inscrição.

    **Pública, e não `_chave`**, porque a `019` compara as mesmas identidades ao montar a fila: uma
    segunda normalização lá daria dois critérios de igualdade para o mesmo par de valores, e o modo
    de falha é um conjunto que não intersecta nada — um número que parece certo porque é zero.

    Os identificadores chegam como `UUID` de um lado e `str` do outro — do ORM num caminho, do teste
    ou do JSON congelado noutro. Normalizar num lugar só evita a divergência silenciosa que
    `mesma_lista` já evita para o recorte: um conjunto que não intersecta nada e um número que
    parece certo porque é zero.
    """
    return str(identificador)


def elegiveis_em_ordem(*, progrediram_em_ordem, habilitadas, ocupantes_da_ampla=()):
    """Quem a faixa alcançou e habilitou, **na ordem** — titulares e suplentes, nesta sequência.

    **Existe separada de `titulares_iniciais` porque a `019` precisa da cauda.** Quem chama o
    suplente precisa da lista inteira; quem conta a ocupação só precisa do começo dela. Duas
    implementações da mesma travessia divergiriam na primeira regra nova — e a fronteira entre
    contar e chamar é justamente a que a `UX-035` verifica por varredura.
    """
    habilitadas_de = {chave_da_inscricao(i) for i in habilitadas}
    concomitantes = {chave_da_inscricao(i) for i in ocupantes_da_ampla}
    elegiveis, vistas = [], set()
    for identificador in progrediram_em_ordem:
        chave = chave_da_inscricao(identificador)
        if chave in vistas:
            continue
        vistas.add(chave)
        if chave in habilitadas_de and chave not in concomitantes:
            elegiveis.append(identificador)
    return elegiveis


def titulares_iniciais(
    *,
    progrediram_em_ordem,
    habilitadas,
    efetivas,
    ocupantes_da_ampla=(),
    empates_residuais=None,
):
    """Quem ocupa as vagas iniciais: as primeiras `efetivas` habilitadas, **na ordem** (`R-001`).

    **Habilitadas, e não "os primeiros da faixa".** Quem foi eliminado na Etapa governada não segura
    vaga nenhuma — desce-se a ordem pulando quem não habilitou, e os primeiros `efetivas` que
    sobram são os titulares. É como o certame de fato funciona, e é o que faz o número não mudar
    onde ninguém desistiu: sem desfecho, `len(titulares)` é exatamente o `min(cabem, efetivas)` que
    esta função substituiu.

    **Contado por pessoa** (`R-001`): a mesma inscrição repetida na sequência conta uma vez. A
    convenção é a de `desempate.py` — o alvo conta pessoas, e não números de posição.

    **`ocupantes_da_ampla` sai antes da janela, e não depois.** O item 8.9 do 28/2026 diz que o
    autodeclarado sorteado dentro das vagas de ampla não é computado no preenchimento da reservada,
    *"abrindo vaga para o próximo suplente autodeclarado"* — quem vem depois **sobe**. Filtrar
    depois de recortar a janela deixaria o buraco no lugar.
    """
    elegiveis = elegiveis_em_ordem(
        progrediram_em_ordem=progrediram_em_ordem,
        habilitadas=habilitadas,
        ocupantes_da_ampla=ocupantes_da_ampla,
    )
    titulares = elegiveis[: max(int(efetivas), 0)]
    _recusar_empate_na_fronteira(
        titulares=titulares, elegiveis=elegiveis, empates_residuais=empates_residuais or {}
    )
    return titulares


def _recusar_empate_na_fronteira(*, titulares, elegiveis, empates_residuais):
    """Recusa quando um grupo de empatados fica metade dentro e metade fora do alvo (`R-002`).

    **Só os elegíveis contam.** Um empate entre eliminados não disputa titularidade nenhuma, e
    recusar por causa dele pararia a apuração por um fato que não muda número algum.
    """
    if not empates_residuais:
        return
    dentro = {chave_da_inscricao(t) for t in titulares}
    disputando = {chave_da_inscricao(e) for e in elegiveis}
    grupos = {}
    for identificador, posicao in empates_residuais.items():
        grupos.setdefault(posicao, set()).add(chave_da_inscricao(identificador))
    for posicao in sorted(grupos, key=lambda p: (p is None, p)):
        competindo = grupos[posicao] & disputando
        if competindo & dentro and competindo - dentro:
            raise EmpateNaFronteiraDoAlvo(posicao, len(competindo))


def ocupantes(*, titulares, efeitos_lidos=()):
    """O conjunto de quem ocupa vaga, depois de aplicados os efeitos que a `019` registrou.

    **Conjunto, e não subtração de contagem** (`R-001`). Duas exclusões da mesma pessoa dariam `−2`
    numa soma, e o número deixaria de ser reproduzível a partir dos atos. E exclusão de quem **não
    era** titular não desconta nada: a suplente só entra na contagem depois de aceitar (`FR-278d`).

    **O último efeito de cada pessoa vence, e a ordem é a que a apuração congelou.** A fórmula da
    `R-001` está escrita como `titulares − excluídos ∪ incluídos`, e em álgebra de conjuntos a
    inclusão venceria a exclusão qualquer que fosse a ordem dos atos. Isso erra num caso real e
    nomeado pela própria feature: a suplente que aceita (inclusão) e tem a matrícula cancelada por
    inércia depois (exclusão) continuaria contada como ocupante. Aplicar em ordem concorda com a
    fórmula em todos os casos que os artefatos descrevem e acerta o que eles não previram — e
    continua determinístico, porque `efeitos_lidos` é lista congelada, como `movimentos_lidos`.
    """
    ocupando = {chave_da_inscricao(t) for t in titulares}
    for especie, inscricao in efeitos_lidos:
        if especie == nomes.EFEITO_INCLUSAO:
            ocupando.add(chave_da_inscricao(inscricao))
        elif especie == nomes.EFEITO_EXCLUSAO:
            ocupando.discard(chave_da_inscricao(inscricao))
    return ocupando


def apurar(
    *,
    publicadas,
    progrediram_em_ordem,
    habilitadas,
    movimentos_lidos=(),
    ocupantes_da_ampla=(),
    efeitos_lidos=(),
    empates_residuais=None,
):
    """`(publicadas, efetivas, ocupadas)` para um recorte.

    `progrediram_em_ordem` é a **sequência ordenada** das inscrições que o corte vigente fez
    progredir; `habilitadas` é o conjunto cujo Resultado da Etapa governada é `HABILITADA`.

    **A sequência substituiu o conjunto, e a troca do nome do parâmetro é deliberada.** Titular
    inicial depende de ordem, e um conjunto não a tem. Trocar a assinatura sem trocar quem a chama
    produziria um número plausível e errado — e plausível é o que faz passar; com o nome novo, quem
    ainda passa `dentro_da_faixa` recebe `TypeError` na hora.

    **Ocupada deixou de ser "quantos cabem".** O cálculo anterior era
    `min(|faixa ∩ habilitadas|, efetivas)`, e ele conta **capacidade**: enquanto sobrassem
    habilitados na faixa, o número saturava no alvo. Medido em 40 vagas com faixa de 70 e 67
    habilitadas, eram necessárias **28** desistências para o número se mover — e cada uma das 27
    anteriores era uma suplente promovida em silêncio (`R-001`, §1.0 da spec).

    **`ocupantes_da_ampla` é a concorrência concomitante, e é exclusão — não transferência**
    (`FR-252`). O item 8.9 do 28/2026 diz que o autodeclarado sorteado dentro das vagas de ampla
    *"não será computado para efeito do preenchimento das vagas reservadas, isto é, não constará na
    lista de classificados como autodeclarados, abrindo vaga para o próximo suplente
    autodeclarado"*. Quantidade nenhuma muda de lista: a reservada continua com as vagas que
    publicou, e o que muda é que ele não conta como tendo ocupado uma delas.

    *A primeira implementação modelou isso como movimento de quantidade da ampla para a reservada, e
    produzia 1 e 2 efetivas onde o Edital manda 2 e 1. O erro não era de conta — era de leitura.*

    `movimentos_lidos` são os `(especie, recebida, quantidade)` e `efeitos_lidos` os
    `(especie, inscricao_id)` que **esta** apuração leu, e não os de hoje: é o congelamento que
    torna a reprodução determinística.
    """
    recebidas = sum(q for _, recebida, q in movimentos_lidos if recebida)
    cedidas = sum(q for _, recebida, q in movimentos_lidos if not recebida)
    efetivas = int(publicadas) + recebidas - cedidas
    # **Suplente não ocupa vaga, e o teto diz isso.** A faixa pode ser maior que o quadro: no
    # 77/2026 são 40 vagas com 30 suplentes alcançados na mesma faixa (`D-011` da `014`), e se
    # todos habilitarem a interseção dá 70. Ocupar 70 de 40 não é um número grande — é um número
    # falso, e a constraint `ocupadas <= efetivas` recusaria o ato.
    #
    # O excedente **é** o suplente: ele está na faixa, habilitou, e não ocupa vaga nenhuma até que
    # uma vagueie. Quem chama para a vaga vaga é a `019` — e o que ela devolve, quando a suplente
    # aceita, entra por `efeitos_lidos`, e não por uma segunda contagem.
    titulares = titulares_iniciais(
        progrediram_em_ordem=progrediram_em_ordem,
        habilitadas=habilitadas,
        efetivas=efetivas,
        ocupantes_da_ampla=ocupantes_da_ampla,
        empates_residuais=empates_residuais,
    )
    ocupadas = min(
        len(ocupantes(titulares=titulares, efeitos_lidos=efeitos_lidos)), max(efetivas, 0)
    )
    return int(publicadas), efetivas, ocupadas


def faltando(*, efetivas, ocupadas):
    """`efetivas - ocupadas`, nunca abaixo de zero.

    Não é coluna: é aritmética da mesma linha, sem junção e sem agregado. O piso em zero existe
    porque a fronteira do empate pode fazer a faixa alcançar mais gente que o alvo — e nesse caso
    não faltam vagas negativas, faltam zero.
    """
    return max(int(efetivas) - int(ocupadas), 0)


def estado(*, tem_quadro, tem_apuracao, causas_de_obsolescencia):
    """Qual dos quatro estados o recorte exibe (016, contrato).

    A ordem das perguntas é a que impede o defeito que a `UX-032` nomeia: **sem quadro é o
    primeiro**, porque Edital publicado antes do degrau 12 não tem quantidade a apurar, e dizer
    "0 vagas" ali afirmaria o que o Edital não disse.
    """
    if not tem_quadro:
        return nomes.SEM_QUADRO
    if not tem_apuracao:
        return nomes.NAO_APURADO
    if causas_de_obsolescencia:
        return nomes.OBSOLETO
    return nomes.VIGENTE
