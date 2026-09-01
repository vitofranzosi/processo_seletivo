"""O comprovante de inscrição como documento gerado pelo servidor.

**Por que deixou de ser página impressa.** O comprovante nasceu como tela: "imprimível pelo
navegador, e não PDF gerado" era decisão registrada, e fazia sentido enquanto ele era entendido
como a última tela de um fluxo. Ele não é. É a única prova que o candidato leva, e é o papel que a
comissão recebe — apresentado numa banca, anexado a um recurso, guardado por um ano.

Três coisas que a impressão pelo navegador não entrega e um documento precisa:

- **um arquivo com nome próprio**, e não o título da aba salvo na pasta de downloads;
- **a página limpa**, sem o endereço `localhost:8009/...` que o navegador escreve no alto da folha
  e que nenhuma regra de CSS alcança;
- **bytes determinísticos** — o mesmo comprovante gera sempre o mesmo arquivo, e é isso que permite
  publicar o resumo do próprio documento e esperar que ele confira.

A infraestrutura é a mesma do Edital (`publicacoes/infrastructure/pdf.py`): sem dependência nova,
sem biblioteca de layout. O que os dois documentos dizem é diferente em tudo; como viram arquivo,
é idêntico.

**Determinismo.** Nada aqui lê o relógio. A data que o documento carrega é a do envio, que é um
fato passado — usar o instante da emissão faria o mesmo comprovante gerar arquivos diferentes a
cada download, e o resumo publicado deixaria de conferir na segunda vez.
"""

from processo_seletivo.publicacoes.infrastructure import humano
from processo_seletivo.publicacoes.infrastructure.pdf import (
    ALTURA_DO_BRASAO,
    ANTES_DE_LINHA,
    CENTRO,
    CORPO_ATO,
    CORPO_NOTA,
    CORPO_SECAO,
    CORPO_TEXTO,
    NEGRITO,
    ORGAO,
    Composicao,
    render_documento,
)

CORPO_PROTOCOLO = 15.0
RECUO_DO_VALOR = 118.0
# O valor sobe para a linha do rótulo. É o preço de compor um par sem tabela: a moldura de uma
# grade traria fios que este documento não precisa, e duas colunas de texto alinhadas resolvem.
SUBIR_PARA_A_LINHA = -11.5
# Uma página é o alvo: um comprovante de duas folhas se separa, e o que ia na segunda era
# justamente o que diz o que ele atesta. Os espaçamentos abaixo são menores que os do Edital
# porque este documento não é lido em sequência — é conferido de relance.
ENTRE_SECOES = 10.0
ENTRE_DOCUMENTOS = 6.0


def render_comprovante_pdf(dados: dict) -> bytes:
    """Um documento de uma página, com o que se confere e o que se prova.

    `dados` é o que a aplicação já reuniu para a tela — nenhuma consulta acontece aqui. O
    renderizador não sabe de banco, de requisição nem de sessão: recebe fatos e devolve bytes, que
    é o que torna o resultado testável byte a byte.
    """
    composicao = Composicao()
    _timbre(composicao)
    _identificacao(composicao, dados)
    _dados_da_inscricao(composicao, dados)
    _documentos(composicao, dados)
    _atestado(composicao, dados)
    return render_documento(
        composicao,
        identificacao=f"{dados['protocolo']} · Verificação {dados['codigo_de_verificacao']}",
    )


def _timbre(composicao):
    composicao.espaco(ALTURA_DO_BRASAO - 10)
    for indice, linha in enumerate(ORGAO):
        composicao.escrever(
            linha, tamanho=CORPO_TEXTO, alinhamento=CENTRO, antes=0.0 if indice else 4.0
        )
    composicao.escrever(
        "COMPROVANTE DE INSCRIÇÃO",
        tamanho=CORPO_ATO,
        fonte=NEGRITO,
        antes=16,
        alinhamento=CENTRO,
    )


def _identificacao(composicao, dados):
    """Protocolo e código de verificação juntos, e antes de tudo.

    São os dois números que alguém compara ao receber o papel: o primeiro identifica a inscrição, o
    segundo prova que o documento não foi alterado. Separá-los obrigaria a procurar o segundo.
    """
    with composicao.bloco(moldura=True):
        composicao.escrever("PROTOCOLO", tamanho=CORPO_NOTA, antes=9.0)
        composicao.escrever(dados["protocolo"], tamanho=CORPO_PROTOCOLO, fonte=NEGRITO, antes=1.0)
        composicao.escrever("CÓDIGO DE VERIFICAÇÃO", tamanho=CORPO_NOTA, antes=6.0)
        composicao.escrever(
            dados["codigo_de_verificacao"], tamanho=CORPO_SECAO, fonte=NEGRITO, antes=1.0
        )
        composicao.espaco(4.0)


def _dados_da_inscricao(composicao, dados):
    composicao.escrever(
        "Dados da inscrição", tamanho=CORPO_SECAO, fonte=NEGRITO, antes=ENTRE_SECOES, junto=True
    )
    for rotulo, valor in dados["campos"]:
        if not valor:
            continue
        _par(composicao, rotulo, valor)


def _par(composicao, rotulo, valor):
    """Rótulo e valor na mesma linha, com o valor recuado.

    Duas escritas e não uma tabela: são pares, não uma grade — e uma grade aqui traria fios que o
    documento não precisa para ser lido.
    """
    composicao.escrever(rotulo, tamanho=CORPO_NOTA, antes=4.5)
    composicao.escrever(
        valor, tamanho=CORPO_TEXTO, recuo=RECUO_DO_VALOR, antes=SUBIR_PARA_A_LINHA
    )


def _documentos(composicao, dados):
    composicao.escrever(
        "Documentos apresentados",
        tamanho=CORPO_SECAO,
        fonte=NEGRITO,
        antes=ENTRE_SECOES,
        junto=True,
    )
    if not dados["documentos"]:
        composicao.escrever(
            "Nenhum documento foi exigido para esta vaga.",
            tamanho=CORPO_TEXTO,
            antes=ENTRE_DOCUMENTOS,
        )
        return
    for documento in dados["documentos"]:
        # Cada documento é um bloco coeso: nome, arquivo e resumo pertencem um ao outro, e um
        # SHA-256 sozinho no alto da folha seguinte não permitiria conferir coisa nenhuma.
        with composicao.bloco():
            composicao.escrever(
                documento["requisito"],
                tamanho=CORPO_TEXTO,
                fonte=NEGRITO,
                antes=ENTRE_DOCUMENTOS,
            )
            composicao.escrever(
                f"{documento['arquivo']} · {documento['tamanho']} · recebido em "
                f"{documento['quando']}",
                tamanho=CORPO_NOTA,
                antes=1.0,
            )
            composicao.escrever(
                f"SHA-256: {documento['resumo']}", tamanho=CORPO_NOTA, antes=1.0
            )


def _atestado(composicao, dados):
    """O que o documento prova, e o que não prova.

    A segunda frase evita o mal-entendido mais caro da jornada: recebida não é deferida, e ninguém
    deve chegar à divulgação do resultado achando que o comprovante garantia algo sobre o mérito.
    """
    composicao.espaco(ENTRE_SECOES)
    composicao.regua()
    composicao.escrever(
        "Este comprovante atesta que a inscrição acima foi recebida pelo sistema na data e hora "
        "indicadas, com os documentos listados.",
        tamanho=CORPO_NOTA,
        antes=ANTES_DE_LINHA + 3,
        justificar=True,
    )
    composicao.escrever(
        "O recebimento não implica deferimento: a conferência dos documentos e a análise dos "
        "requisitos são feitas pela comissão, nos prazos do Edital.",
        tamanho=CORPO_NOTA,
        antes=ANTES_DE_LINHA,
        justificar=True,
    )
    composicao.escrever(
        f"Para conferir este comprovante, acesse {dados['endereco']} e identifique-se com o mesmo "
        "CPF. O código de verificação é calculado sobre o conteúdo deste documento: a comissão o "
        "compara com o do sistema para confirmar que nada foi alterado.",
        tamanho=CORPO_NOTA,
        antes=ANTES_DE_LINHA,
        justificar=True,
    )
    composicao.escrever(
        "Para verificar um anexo, calcule o SHA-256 do arquivo e compare com o resumo acima — "
        "shasum -a 256 (macOS e Linux) ou certutil -hashfile (Windows).",
        tamanho=CORPO_NOTA,
        antes=ANTES_DE_LINHA,
        justificar=True,
    )


def instante(valor) -> str:
    """`31/08/2026, às 19h03` — como um ato administrativo escreve, e não como um banco guarda."""
    return humano.instante(valor) if valor else "—"
