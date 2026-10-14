# Verificação — 073

Medida em 14/10/2026, na branch `claude/073-configurar-e-verificar`, no macOS da equipe, contra o
PostgreSQL local e com banco próprio (`test_073`).

## Controles obrigatórios

| Controle | Resultado |
|---|---|
| `make lint` (`ruff check` e `ruff format --check`) | verde |
| `make check` | verde, sem migration pendente |
| `make test-pg DB_NAME=test_073` | **11294 passando e 12 pulados**, nenhuma falha, em 1294 s |

Os 12 pulados são os deliberados que o `AGENTS.md` reparte. São 31 casos a mais que a medição de
referência, que tinha 11263:

- 21 de `test_guia_configurar_verificar.py`;
- 4 de `test_verificar_servico.py`;
- 2 da recusa nova em `test_configuracao_producao.py`;
- os demais do #280, que entrou na `main` no meio desta feature.

## O que os testes exercitaram

**Nenhum envio real, nenhuma inferência.** Os servidores de correio e o Ollama do teste do guia são
falsos, locais e de vida curta. Os exemplos rodam do próprio Markdown, num processo
`manage.py shell` como a TI os roda. Foram exercitados:

- **a leitura da configuração**, com senha do SMTP, credencial do assistente e chave da aplicação
  plantadas: zero ocorrências na saída (SC-621);
- **a conexão de correio contra o servidor que aceita:** `AUTH` recebido, nenhum `MAIL`, `RCPT` ou
  `DATA` (SC-622);
- **cinco falhas de correio**, cada uma com a última linha na tabela: conta recusada, sem STARTTLS,
  conexão aberta sem saudação, porta fechada e nome que não resolve;
- **o Ollama falso:** versão, modelo presente e ausente, endereço com `/api` e porta fechada. Só
  `/api/version` e `/api/tags`, nunca `/api/chat` (SC-622).

## Medido à mão, fora da suíte

`TimeoutError: timed out` (endereço sem rota) e `URLError … timed out` (Ollama sem rota) foram
medidos contra `10.255.255.1`, em 14/10. Não entram na suíte porque dependem da rede de quem roda.

## Pendente

- **SC-620 e o resto do SC-623:** a sessão conduzida com uma pessoa da TI, em homologação
  (quickstart B).
- **A US2 contra a L4 real** (quickstart C), bloqueada até haver acesso, como o roteiro D da `071`.
