"""As palavras com que o ato público nomeia a pessoa, gravadas no próprio ato (revisão de 13/11).

**Por que no ato, e não no modelo da página.** A coluna dizia *"Candidato"* no PDF, gravado com o
resumo no ato de publicar, e no modelo da página, que serve a todos os atos — os já publicados e
os que virão. Trocar só o modelo faria a página de um ato antigo dizer uma coisa e o documento
oficial dele outra: a modificação silenciosa que o Princípio II da Constituição proíbe. Gravadas
no `conteudo` do ato, como já se grava `rotulo_nao_constam`, as palavras novas valem para os atos
publicados daqui em diante, e o ato sem elas continua dizendo, na página e no PDF, o que disse.

**"Nome"**, porque é o que a coluna mostra, e é o rótulo que a publicação de convocados (149) já
usa. A decisão é do usuário, de 2026-11-13, na auditoria dos e-mails
(`doc/auditoria-dos-emails-2026-11-13.md`, achado 9): só atos futuros, sem reescrever publicados.
"""

#: Os rótulos que o ato novo grava, e os que o ato gravado antes da revisão diz sem tê-los gravado.
ROTULO_DA_PESSOA = "Nome"
ROTULO_DA_PESSOA_ANTERIOR = "Candidato"
QUEM_CONSULTA = "cada pessoa"
QUEM_CONSULTA_ANTERIOR = "cada candidato"


def para_gravar(*, com_quem_consulta=False):
    """As chaves que o `conteudo` de um ato novo leva. Entram no resumo canônico do ato."""
    chaves = {"rotulo_da_pessoa": ROTULO_DA_PESSOA}
    if com_quem_consulta:
        chaves["quem_consulta"] = QUEM_CONSULTA
    return chaves


def rotulo_da_pessoa(conteudo):
    """O rótulo da coluna do nome, como o ato o gravou — ou o do dia, para o ato anterior.

    `conteudo` é o dicionário onde o ato o grava: o conteúdo inteiro, na publicação das inscrições,
    e o cabeçalho, no resultado, cujo primeiro nível é contrato da `017`.
    """
    return conteudo.get("rotulo_da_pessoa") or ROTULO_DA_PESSOA_ANTERIOR


def quem_consulta(conteudo):
    """*"cada pessoa"* no ato que a gravou; *"cada candidato"* no anterior, como foi publicado."""
    return conteudo.get("quem_consulta") or QUEM_CONSULTA_ANTERIOR


__all__ = [
    "QUEM_CONSULTA",
    "QUEM_CONSULTA_ANTERIOR",
    "ROTULO_DA_PESSOA",
    "ROTULO_DA_PESSOA_ANTERIOR",
    "para_gravar",
    "quem_consulta",
    "rotulo_da_pessoa",
]
