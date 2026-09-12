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


def apurar(*, publicadas, dentro_da_faixa, habilitadas, movimentos_lidos=()):
    """`(publicadas, efetivas, ocupadas)` para um recorte.

    `dentro_da_faixa` é o conjunto de inscrições que o corte vigente fez progredir; `habilitadas`
    é o conjunto cujo Resultado da Etapa governada é `HABILITADA`.

    **Ocupada é a interseção dos dois, e nenhum sozinho** (016, `R-001`). A fronteira da `014`
    proíbe, com estas palavras, usar "quantidade de habilitados" como sinônimo de "vagas ocupadas";
    o que a distingue é exigir **também** estar dentro da faixa. Quem é habilitado fora do alvo não
    ocupa nada — é a diferença entre "quantos passaram" e "quantos couberam".

    `movimentos_lidos` são os `(especie, recebida, quantidade)` que **esta** apuração leu, e não os
    movimentos de hoje: é o congelamento que torna a reprodução determinística.
    """
    ocupadas = len(set(dentro_da_faixa) & set(habilitadas))
    recebidas = sum(q for _, recebida, q in movimentos_lidos if recebida)
    cedidas = sum(q for _, recebida, q in movimentos_lidos if not recebida)
    efetivas = int(publicadas) + recebidas - cedidas
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
