# Quickstart: demonstrar e verificar a 133

## 1. Verificação automática

A partir de `backend/`, com `DB_NAME` próprio da worktree e o PostgreSQL local (`LC_ALL` exportado):

```bash
make lint check
```

```bash
DB_NAME=ps_133 make test-pg
```

Os testes da feature, isolados:

```bash
PYTEST_ADDOPTS="-k 'marco_intermediario or espera_do_corte or proxima_da_fila or jornada_do_edital_900 or frases_do_corte'" DB_NAME=ps_133 make test-pg PYTEST_WORKERS=0
```

## 2. Demonstração no navegador (princípio VI)

Use os bancos de fase do estudo
([doc/estudo-convergencia-ux-2026-11-07/README.md](../../doc/estudo-convergencia-ux-2026-11-07/README.md),
§7), migrados para a branch. O servidor vem do estudo de 07/11
(`doc/estudo-classificacao-demonstrativa-2026-11-07/reproducao/servidor.py`), com `RELOGIO` no
instante de cada banco. Entre como `demo.presidente` pelo seletor da demonstração.

| Banco | Instante | O que conferir | Contrato |
|---|---|---|---|
| `ps_conv_t2` | 2026-12-10T09:00 | "O que fazer agora": o corte das três listas aparece em espera até 12/12, com a marca "recomendação" e a consequência, sem "SUA". Na tela do corte da ampla, o aviso antes do botão e o botão presente | [telas.md](contracts/telas.md), andamento e tela do corte |
| `ps_conv_t3` | 2026-12-13T11:00 | Como `demo.publicador`: a definitiva da ampla em *Depois*, com a razão | andamento |
| `ps_conv_t5` | 2026-12-29T16:00 | Só as convocações do marco final. A ocupação e a convocação do marco 1 abrem com o aviso e sem formulário | andamento, ocupação, convocação |
| `ps_conv_t6` | 2027-01-05T14:10 | "SUA: Chamar a próxima da fila" na ampla, igual à tela da convocação | andamento |
| `ps_conv_ux` | 2027-01-06T12:00 | Nada em aberto no marco 1 | andamento |

Para a recusa pelo caminho direto, use a sonda do estudo (`roteiro/sonda.py apurar-m1`) contra uma
cópia: ela deve imprimir `RECUSADA: DomainError … decide quem participa da Etapa Entrevista`, e o
banco não deve ganhar apuração.

Para a frase, componha um Edital com alvo fixo e reservada: a Revisão mostra "de cada lista de
concorrência". O documento de um Edital publicado antes desta feature continua com o mesmo resumo
criptográfico.

## 3. Registro

Grave as capturas antes e depois em `capturas/` e o resultado de cada passo em `verificacao.md`.
