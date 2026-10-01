# O teste da vigência do consolidado depende da largura da data

**Data:** 2026-10-01
**Origem:** a suíte completa da `057`, rodada depois da meia-noite de 30/09 para 01/10.
**Natureza:** teste frágil, alheio à `057` (nenhum arquivo de `publicacoes/` foi tocado).
**Situação:** **corrigido** no mesmo PR da `057`, a pedido do usuário.

## O que se viu

`tests/integration/publicacoes/test_consolidado_datado.py::test_a_vigencia_em_outro_dia_e_declarada`
procura no texto extraído do PDF a frase inteira:

```
com vigência a partir de 4 de outubro de 2026.
```

O PDF tem a frase, mas a quebra de linha cai no meio dela:

```
Versão consolidada. Publicado em 1 de outubro de 2026; retificado em 1 de outubro de 2026, com
vigência a partir de 4 de outubro de 2026.
```

A linha anterior carrega duas datas por extenso, e a largura delas muda com o dia: em 30/09 a
quebra caía em outro ponto, e o teste passava. A suíte da `057` passou inteira às 23h e falhou às
8h do dia seguinte com o mesmo código, e o teste reprova sozinho, isolado, no mesmo commit.

## A correção

`_documentos` passou a devolver o texto de cada PDF em linha corrida (`" ".join(texto.split())`),
como `test_pdf_classificacao.py` já fazia e como um dos testes do próprio arquivo fazia à mão. O que
se prova continua sendo a frase inteira, com as datas certas; o que deixou de importar é onde o
compositor quebra a linha. Os outros testes que comparam datas por extenso no PDF
(`test_fecho_publicado.py`) leem o fecho "Vitória (ES), …", que ocupa uma linha só, e não precisaram
mudar.
