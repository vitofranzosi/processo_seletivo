"""CENÁRIO B na 069: o texto corrigido pelo que as conferências da 065 dizem, na numeração apresentada.

Lê o cenario_b.py e troca, nas seções, só os números: 2.x→2.1.x (Requisitos gerais é a subseção
2.1), 4.x→7.4.x (a verificação é a subseção 7.4), 11.x→9.x (convocação), 14.x→12.x (disposições
finais). Na Inscrição, que sai como 5 e imprime a subseção 5.1 (atendimento), o número digitado é
retirado: "5.1" seria o item da subseção. Os Recursos já saem como 8, e ficam.
"""
import re

# O roteiro da auditoria, com os caminhos do scratchpad ajustados (ver o Anexo da auditoria).
ORIGEM = "cenario_b.py"
fonte = open(ORIGEM).read()
TROCAS = {
    "requisitos-gerais": ("2.", "2.1."),
    "verificacao-autodeclaracao": ("4.", "7.4."),
    "convocacao": ("11.", "9."),
    "disposicoes-finais": ("14.", "12."),
}
linhas = []
for linha in fonte.split("\n"):
    casada = re.match(r'    \("([\w-]+)", "', linha)
    if casada and casada[1] in TROCAS:
        de, para = TROCAS[casada[1]]
        corpo = linha[casada.end() - 1:]
        corpo = re.sub(r'(?<=["n])' + re.escape(de) + r"(\d)", para + r"\1", corpo)
        linha = linha[: casada.end() - 1] + corpo
    elif casada and casada[1] == "inscricao":
        corpo = linha[casada.end() - 1:]
        corpo = re.sub(r'(?<=["n])3\.\d ', "", corpo)
        linha = linha[: casada.end() - 1] + corpo
    linhas.append(linha)
fonte = "\n".join(linhas).replace('previa(edital, "B-previa")', 'previa(edital, "B-069-previa")').replace('publicar(edital, aut.pk, "B-publicado")', 'publicar(edital, aut.pk, "B-069-publicado")')
assert 'publicar(edital, aut.pk, "B-069-publicado")' in fonte
exec(compile(fonte, "cenario_b_069", "exec"))
