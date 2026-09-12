# A suíte no modo padrão falha, e o CI não enxerga

**Data:** 2026-09-09
**Origem:** montagem do ambiente containerizado, ao verificar os comandos que o README manda rodar.
**Natureza:** achado registrado, não corrigido. A correção é decisão de escopo, não desta entrega.

## O que acontece

`cd backend && make test`, exatamente como o README manda, numa árvore limpa de `main`
(`895261f`):

```
21 failed, 3755 passed, 182 skipped in 90.12s
```

A mesma suíte apontada para PostgreSQL:

```
3957 passed, 1 skipped in 322.49s
```

## Por que

`config.settings.test` cai para SQLite em memória quando `TEST_DB_ENGINE` não é `postgresql`. A
intenção — declarada no README — é que os testes que dependem de garantias reais do banco sejam
**pulados** nesse modo. 182 são. Outros 21 não: eles executam SQL que só o PostgreSQL entende, e
morrem com `sqlite3.OperationalError: near "DISABLE": syntax error` — `ALTER TABLE ... DISABLE
TRIGGER`, usado para montar cenário.

Os arquivos:

| Arquivo | Falhas |
|---|---|
| `tests/integration/recursos/test_janela.py` | 6 |
| `tests/portal/test_janela_na_tela.py` | 4 |
| `tests/integration/classificacao/test_citacao_de_decisao.py` | 4 |
| `tests/integration/recursos/test_convergencia.py` | 2 |
| `tests/integration/recursos/test_concorrencia.py` | 2 |
| `tests/integration/recursos/test_admitir.py` | 2 |
| `tests/portal/test_definitiva_retificada.py` | 1 |

## Por que ninguém viu

O CI (`.github/workflows/backend.yml`) roda **só** com `TEST_DB_ENGINE=postgresql`. O modo padrão
da suíte — o que qualquer pessoa executa no primeiro dia, e o único que o README apresenta como
ponto de partida — não é exercitado por pipeline nenhum. Ele pode estar quebrado por tempo
indefinido sem que nada acuse.

É o mesmo formato de defeito que motivou o segundo passo do `lint`: verde local que não
corresponde a verde nenhum.

## O que isto custa a quem chega

O primeiro `make test` de quem clona o repositório é vermelho, com 21 erros que não têm relação
com nada que a pessoa fez. Não há como distinguir "o projeto está assim" de "eu montei errado" —
e é exatamente no primeiro dia que essa distinção é mais cara.

## Os caminhos, sem escolher nenhum

1. **Marcar os 21 para pular fora do PostgreSQL**, como os outros 182. Barato, e mantém a promessa
   que o README já faz.
2. **Exigir PostgreSQL para rodar a suíte**, eliminando o modo SQLite. Honesto — o sistema depende
   de triggers e privilégios que o SQLite não tem — e torna o compose ainda mais útil, porque ele
   já entrega o banco pronto. Custa a execução rápida sem banco.
3. **Rodar os dois modos no CI**, para que o padrão pare de apodrecer em silêncio. Complementar a
   qualquer uma das duas.

Enquanto não houver decisão, o README e o `AGENTS.md` dizem o que é verdade: rode contra
PostgreSQL, e o modo padrão está degradado.
