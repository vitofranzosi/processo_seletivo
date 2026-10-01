# O teste da vigência do consolidado depende da largura da data

**Data:** 2026-10-01
**Origem:** a suíte completa da `057`, rodada depois da meia-noite de 30/09 para 01/10.
**Natureza:** teste frágil, alheio à `057` (nenhum arquivo de `publicacoes/` foi tocado).
**Situação:** **aberto** — decidir é do usuário.

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

## O que resolveria, sem decidir aqui

Comparar o texto com as quebras de linha normalizadas (`" ".join(texto.split())`), como os testes
do documento que já não dependem da paginação; ou congelar o relógio do teste.
