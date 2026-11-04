"""Os nomes dentro do pacote e as células do manifesto, seguros por construção (117, D-023).

O ZIP é aberto no computador do setor, e o manifesto numa planilha. Os dois recebem texto que veio,
em algum ponto, de uma pessoa: o nome do candidato e a chave do requisito que a elaboração digitou.
Por isso:

- **só valores do sistema** entram no caminho — protocolo, nome e chave —, e nunca o nome do arquivo
  que o candidato enviou (FR-3712);
- **cada componente é normalizado** para que nenhum caminho saia da pasta da pessoa, nenhum nome
  seja reservado no Windows e nenhum passe de 80 caracteres;
- **as colisões recebem sufixo determinístico**, na ordem do identificador do requisito, para que
  duas exportações iguais deem os mesmos nomes (SC-1108);
- **nenhuma célula começa com caractere de fórmula** (FR-3713).

Puro, sem banco e sem Django: é testado com nomes hostis em `tests/unit/formalizacao/`.
"""

import re
import unicodedata

LIMITE = 80
SEM_NOME = "sem-nome"
EXTENSAO = ".pdf"

#: Os nomes que o Windows recusa como arquivo ou pasta, com ou sem extensão.
RESERVADOS = frozenset(
    {"CON", "PRN", "AUX", "NUL"}
    | {f"COM{numero}" for numero in range(1, 10)}
    | {f"LPT{numero}" for numero in range(1, 10)}
)

_PROIBIDOS = re.compile(r'[/\\:*?"<>|]')
_ESPACOS = re.compile(r"\s+")
#: O que uma planilha lê como fórmula quando abre a célula (FR-3713).
_FORMULA = ("=", "+", "-", "@", "\t", "\r")


def _sem_controle(texto):
    # `Cc` são os de controle e `Cf` os de formatação invisível — o "zero-width" e a marca de
    # direção, que fariam dois nomes iguais na tela serem diferentes no disco.
    return "".join(c for c in texto if unicodedata.category(c) not in ("Cc", "Cf"))


def _aparar(texto):
    return texto.strip(" .")


def componente(texto, *, limite=LIMITE):
    """Um nome de pasta ou de arquivo, sem separador, sem controle e sem nome reservado."""
    texto = unicodedata.normalize("NFC", str(texto or ""))
    texto = _sem_controle(texto)
    texto = _PROIBIDOS.sub("-", texto)
    texto = _ESPACOS.sub(" ", texto)
    texto = _aparar(texto)
    if texto.split(".", 1)[0].upper() in RESERVADOS:
        texto = f"_{texto}"
    texto = _aparar(texto[:limite])
    return texto or SEM_NOME


def pasta_da_pessoa(protocolo, nome):
    """`‹protocolo› ‹nome›`: o protocolo primeiro, e por isso a pasta é única mesmo cortada."""
    return componente(f"{protocolo} {nome}")


def arquivos_da_pessoa(requisitos):
    """`{requisito_id: nome do arquivo}` de uma pessoa, com as colisões resolvidas.

    `requisitos` é uma lista de `(requisito_id, chave)`. A ordem dos sufixos é a do identificador do
    requisito, e não a da lista, para que o mesmo conjunto dê sempre os mesmos nomes. A comparação
    ignora caixa, porque o Windows e o macOS a ignoram: `CPF.pdf` e `cpf.pdf` seriam o mesmo
    arquivo.
    """
    nomes = {}
    usados = set()
    for requisito_id, chave in sorted(requisitos, key=lambda par: str(par[0])):
        base = componente(chave, limite=LIMITE - len(EXTENSAO))
        candidato = base
        numero = 1
        while candidato.casefold() in usados:
            numero += 1
            sufixo = f"-{numero}"
            candidato = _aparar(base[: LIMITE - len(EXTENSAO) - len(sufixo)]) + sufixo
        usados.add(candidato.casefold())
        nomes[str(requisito_id)] = candidato + EXTENSAO
    return nomes


def caminho(pasta, arquivo):
    """O caminho da entrada: um nível só, relativo, com `/` como único separador."""
    return f"{pasta}/{arquivo}"


def nome_do_download_individual(protocolo, chave):
    """`‹protocolo›-‹requisito›.pdf`, nunca o nome enviado (FR-3677)."""
    return componente(f"{protocolo}-{chave}", limite=LIMITE - len(EXTENSAO)) + EXTENSAO


def nome_do_pacote(numero_do_edital, instante, *, parcial):
    """`formalizacao-‹edital›-‹AAAAMMDD-HHMM›[-parcial].zip`, sem dado pessoal (FR-3686)."""
    edital = componente(numero_do_edital or "edital").replace(" ", "-")
    final = "-parcial" if parcial else ""
    return f"formalizacao-{edital}-{instante:%Y%m%d-%H%M}{final}.zip"


def neutralizar(celula):
    """A célula com apóstrofo à frente quando ela começaria uma fórmula (FR-3713)."""
    texto = "" if celula is None else str(celula)
    return f"'{texto}" if texto.startswith(_FORMULA) else texto
