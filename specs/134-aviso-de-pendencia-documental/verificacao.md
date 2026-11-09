# Verificação: O aviso de pendência documental por e-mail (134)

Preenchida ao fim da implementação, em 08/11/2026.

## Comandos

```bash
cd backend && make lint check test-pg
```

com `DB_NAME=spec134`, `TEST_DB_ENGINE=postgresql` e `DB_USER` do superusuário (CLAUDE.md).

## Resultado (08/11/2026, sobre a `main` em `86cd0ee0`)

| Passo | Resultado |
|---|---|
| `make lint` | `ruff check` e `ruff format --check` verdes |
| `make check` | `manage.py check` sem problemas; `makemigrations --check` sem migration pendente |
| `make test-pg` (4 workers, grupos `dev` e `assistente`, sem `navegador`) | **17389 passaram, 20 pulados, 0 falhas**, em 798s |
| Arquivos novos | `integration/avisos/test_aviso_de_pendencia.py` (24 casos) e `unit/avisos/test_texto_da_pendencia.py` (8) |

**A primeira rodada teve três falhas, todas de guardião, e todas esperadas pela mudança:**

- `test_telas_de_resultado_e_atos.py` (dois casos): a tela de condução tem um botão novo,
  *"Avisar as pessoas com pendência nesta chamada"*. A lista declarada e a contagem de desenhos
  passaram a incluí-lo, com o motivo escrito ao lado.
- `test_trilha_legivel.py`: as operações `AVISO_PENDENCIAS` e `AVISO_PENDENCIA_ENVIO` ganharam
  rótulo na trilha.

**O texto, como sai** (exemplo fictício, composto pela função do domínio):

```text
Ifes · Edital 72/2026: há documento da sua convocação para revisar

Há documentos da sua convocação no Edital 72/2026 que precisam de atenção:

- Comprovante de residência
- um documento da sua modalidade de concorrência

Veja o que fazer na página da sua convocação: https://gps.exemplo/selecoes/inscricoes/0000/convocacao

O prazo continua sendo até quinta-feira, 12/11/2026, às 17h00.

—
Este aviso não é a convocação e não altera o seu prazo.
Em caso de dúvida, fale com selecao@cefor.exemplo.

Cefor/Ifes — Seleções
Esta mensagem é automática; não responda.
```

## O que não foi verificado

- **O percurso no navegador.** A tela foi verificada pelo cliente de teste do Django (o botão, a
  prévia, o POST e a mensagem de resultado), e não num navegador.
- **O envio real.** O despacho foi exercido com o backend de correio em memória da suíte; nenhum
  e-mail saiu. A chave continua desligada em produção (5ª decisão).
- **O Processo em estado final** reusa a recusa da `066`, sem caso novo nesta spec.
