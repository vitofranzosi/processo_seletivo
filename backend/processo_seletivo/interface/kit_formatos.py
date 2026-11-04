"""Os formatos da peça do kit de divulgação: post, story e banner (119, FR-3801).

Um formato é só o retângulo e as regras que valem para qualquer família desenhada nele — tamanho,
margem, zonas que a rede social cobre, corpo mínimo e a chamada à ação. O desenho é do template
(família × formato); o formato não sabe de cor nem de fonte.

**O banner está a 1500 × 850 até a resposta da comunicação** (`D-007`, P-3): o dobro dos 750 × 425
do arquivo, para tela de alta densidade sem mudar a proporção. Trocar depois é mudar esta linha e as
referências do banner, e nenhum banner é liberado antes.

**O story tem margem só nas laterais.** No alto e embaixo valem as zonas reservadas, que são
maiores que qualquer margem: o Instagram desenha ali o nome da conta e o campo de resposta, e texto
coberto por eles é texto que não se lê.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Formato:
    chave: str
    largura: int
    altura: int
    margem: int
    #: A margem de cima e de baixo; nula no story, que tem as zonas reservadas no lugar dela.
    margem_vertical: int
    #: `(esquerda, topo, direita, base)` em px, onde nenhum texto entra.
    zonas_reservadas: tuple
    #: O menor corpo legível neste tamanho (FR-3428 da `111`, FR-3819).
    corpo_minimo: int
    chamada_a_acao: str

    @property
    def area_util(self):
        """`(esquerda, topo, direita, base)` dentro das margens; as zonas se descontam à parte."""
        return (
            self.margem,
            self.margem_vertical,
            self.largura - self.margem,
            self.altura - self.margem_vertical,
        )

    @property
    def util(self):
        """A largura entre as margens laterais."""
        return self.largura - 2 * self.margem


POST = Formato(
    chave="post",
    largura=1080,
    altura=1350,
    margem=80,
    margem_vertical=80,
    zonas_reservadas=(),
    corpo_minimo=24,
    chamada_a_acao="Acesse o link na bio",
)
STORY = Formato(
    chave="story",
    largura=1080,
    altura=1920,
    margem=80,
    margem_vertical=0,
    zonas_reservadas=((0, 0, 1080, 250), (0, 1670, 1080, 1920)),
    corpo_minimo=24,
    chamada_a_acao="Acesse o link na bio",
)
BANNER = Formato(
    chave="banner",
    largura=1500,
    altura=850,
    margem=60,
    margem_vertical=60,
    zonas_reservadas=(),
    corpo_minimo=28,
    chamada_a_acao="Acesse o edital",
)

#: Na ordem em que a tela, o ZIP e o manifesto os listam (data-model, D-015).
FORMATOS = {formato.chave: formato for formato in (POST, STORY, BANNER)}
