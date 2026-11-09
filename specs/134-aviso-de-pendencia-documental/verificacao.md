# Verificação: O aviso de pendência documental por e-mail (134)

Preenchida ao fim da implementação, em 08/11/2026, e de novo depois da revisão do PR, em 09/11/2026.

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

## Depois da revisão do PR (09/11/2026)

| Passo | Resultado |
|---|---|
| `make lint` | verde |
| `make check` | `manage.py check` sem problemas; `makemigrations --check` sem migration pendente |
| `make test-pg` (4 workers, os mesmos grupos) | **17397 passaram, 20 pulados, 0 falhas**, em 1437s |
| Casos novos | oito em `test_aviso_de_pendencia.py`: as três interrupções pelo despacho (pendência resolvida, vencida, lista mudada), o interrompido que não conta no dia, quem continua pendente e recebe, a órfã na trilha, a trilha que falha sem desfazer o resultado e o Processo em estado final |

A revisão trouxe a FR-4623, o SC-1449 e a D-011 (o despacho relê a pendência antes de enviar), a trilha
do envio num ponto de salvamento, a unidade lida uma vez por gesto, os avisos em lote, a raiz por
`documentos.raizes_das` e a prévia sobre a leitura que a tela de condução já fez. O tempo da suíte
subiu porque outras suítes dividiam o cluster na mesma hora; não é medida de custo da mudança.

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
- **A convocação corrigida entre o gesto e o envio** (`CORRIGIDA`, da D-011) não tem caso próprio: a
  correção é o fluxo da `120`, e a releitura a reconhece pela sucessora, como `vigentes` faz.
