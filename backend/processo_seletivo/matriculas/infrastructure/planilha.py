"""O `.xlsx` de uma aba, construído — nunca copiado do modelo (`D-005`, `FR-436`, `FR-437`).

**Por que `openpyxl`, que é a quarta dependência deste projeto.** O projeto tem três, e acrescentar
a quarta precisa de razão escrita. A alternativa é montar o OOXML à mão: um `.xlsx` é um `.zip` com
XML dentro, e gerar um de uma aba cabe em duzentas linhas. **Recusada.** O que se ganharia é a
contagem de dependências; o que se arrisca é produzir um arquivo que o Excel abre — porque o Excel é
tolerante — e que o importador rejeita, num formato cuja única prova é o importador real. O detalhe
que decide é o formato de célula `@`, e é onde implementação caseira erra primeiro.

**Construído, e não copiado.** O binário da amostra carrega formatação residual até `AT1000` e
componentes de extensão do Excel que leitores estritos rejeitam. Aqui saem uma aba, 34 cabeçalhos e
as linhas de dados — e nada mais. A linha `2` da amostra, que traz dados de uma pessoa real, não
entra em lugar nenhum deste repositório (`D-006`).

**`write_only`, e ele custa a mesma linha de código.** Um Edital de porte real tem centenas de
convocados, não milhões — mas o modo de fluxo tira a questão da mesa sem custo nenhum.

**Formato `@` em todas as células, inclusive nos cabeçalhos.** É o que preserva zero à esquerda e
impede o Excel de reinterpretar `dd/mm/aaaa` como número serial: sem ele, `01234567890` vira
`1234567890` e `12/07/1994` vira `34527` — e o que chega ao destino deixa de ser o que a pessoa
declarou.
"""

from io import BytesIO

from openpyxl import Workbook
from openpyxl.cell import WriteOnlyCell
from openpyxl.styles import numbers

from processo_seletivo.matriculas.domain import nomes
from processo_seletivo.matriculas.domain.colunas import CABECALHOS


def _celula(aba, texto: str):
    """Uma célula de texto, com o formato `@` declarado nela.

    **O formato vai célula a célula**, e não por coluna: em modo `write_only` não há objeto de
    coluna a estilizar antes de a linha existir, e um formato aplicado depois não alcança o que já
    foi escrito.
    """
    celula = WriteOnlyCell(aba, value=texto)
    celula.number_format = numbers.FORMAT_TEXT
    return celula


def montar(linhas) -> bytes:
    """Os bytes do arquivo de importação, prontos para a resposta — e **não** para o disco.

    `linhas` é uma sequência de tuplas de 34 textos, na ordem de `colunas.COLUNAS`.

    **Nada é gravado em lugar nenhum** (`FR-456`): o livro é escrito num buffer de memória e os
    bytes são devolvidos. Guardá-los criaria um acervo do artefato mais concentrado de dado pessoal
    deste sistema, com política de retenção própria — e não guardá-los dispensa essa política em vez
    de adiá-la.
    """
    livro = Workbook(write_only=True)
    aba = livro.create_sheet(title=nomes.ABA)
    aba.append([_celula(aba, cabecalho) for cabecalho in CABECALHOS])
    for linha in linhas:
        aba.append([_celula(aba, texto) for texto in linha])
    buffer = BytesIO()
    livro.save(buffer)
    return buffer.getvalue()
