"""A folha em unidades: cada regra de primeiro nível, ou bloco `@media`, com os comentários que a
precedem (091, R-003).

Uma unidade é o que se move inteiro de um arquivo para outro. O comentário que vem antes de uma regra
a explica (a convenção do repositório), e vai com ela; o bloco `@media` vai inteiro, com as regras de
dentro. Sem dependência: um leitor de chaves que respeita comentário e texto entre aspas basta, porque
a folha não tem aninhamento além do `@media`.
"""

import re
from dataclasses import dataclass, field


@dataclass
class Unidade:
    indice: int
    comentarios: str  # o texto antes da regra: comentários e espaço, como estão no arquivo
    regra: str  # a regra ou o bloco `@media`, do primeiro caractere à chave que o fecha
    linha: int  # a linha da regra no arquivo de origem
    origem: str = ""
    area: str = ""
    extras: dict = field(default_factory=dict)

    @property
    def texto(self):
        return self.comentarios + self.regra

    @property
    def cabeca(self):
        """O seletor, ou a condição do `@media`, sem espaço sobrando."""
        return " ".join(self.regra[: self.regra.index("{")].split())

    @property
    def normalizada(self):
        """A regra sem comentário interno e com espaço normalizado — para achar duplicadas."""
        sem = re.sub(r"/\*.*?\*/", "", self.regra, flags=re.S)
        return re.sub(r"\s+", " ", sem).replace(" {", "{").replace("{ ", "{").replace("; ", ";")


def ler(texto, origem=""):
    """As unidades de `texto`, na ordem, e o que sobra depois da última (comentário final)."""
    unidades = []
    i, n = 0, len(texto)
    inicio_dos_comentarios = 0
    while i < n:
        c = texto[i]
        if texto.startswith("/*", i):
            fim = texto.index("*/", i + 2)
            i = fim + 2
            continue
        if c.isspace():
            i += 1
            continue
        # Começa uma regra: vai até a chave que fecha o nível 0.
        comeco = i
        profundidade = 0
        while i < n:
            if texto.startswith("/*", i):
                i = texto.index("*/", i + 2) + 2
                continue
            c = texto[i]
            if c in "\"'":
                fecho = texto.index(c, i + 1)
                i = fecho + 1
                continue
            if c == "{":
                profundidade += 1
            elif c == "}":
                profundidade -= 1
                if profundidade == 0:
                    i += 1
                    break
            i += 1
        assert profundidade == 0, f"chave sem par perto da linha {texto.count(chr(10), 0, comeco) + 1}"
        unidades.append(
            Unidade(
                indice=len(unidades),
                comentarios=texto[inicio_dos_comentarios:comeco],
                regra=texto[comeco:i],
                linha=texto.count("\n", 0, comeco) + 1,
                origem=origem,
            )
        )
        inicio_dos_comentarios = i
    return unidades, texto[inicio_dos_comentarios:]


def remontar(unidades, resto=""):
    return "".join(u.texto for u in unidades) + resto


@dataclass
class Topico:
    """Um comentário e as regras que ele explica — até o próximo comentário.

    É a unidade que muda de arquivo: separar uma regra do comentário que a explica é o contrário da
    convenção do repositório, e o comentário costuma explicar as regras que vêm logo abaixo dele, em
    grupo. O tópico tem as propriedades e os elementos de todas as regras dele, somados — mais
    grosso, e por isso mais conservador na prova de ordem.
    """

    indice: int
    unidades: list
    area: str = ""

    @property
    def texto(self):
        return "".join(u.texto for u in self.unidades)

    @property
    def linha(self):
        return self.unidades[0].linha

    @property
    def resumo(self):
        primeiro = self.unidades[0].comentarios.strip()
        primeiro = re.sub(r"\s+", " ", primeiro.removeprefix("/*"))[:90]
        return f"{self.linha:5} {primeiro} || " + " ; ".join(u.cabeca[:40] for u in self.unidades[:4])


def topicos(unidades):
    grupos = []
    for u in unidades:
        if not grupos or "/*" in u.comentarios:
            grupos.append(Topico(indice=len(grupos), unidades=[u]))
        else:
            grupos[-1].unidades.append(u)
    return grupos
