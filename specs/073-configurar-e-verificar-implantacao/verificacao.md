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
- os outros 4 já estavam na base desta feature. Entre a medição de referência (`55889d11`) e a base
  (`6fac8189`), a `main` ganhou três funções de teste.

A suíte rodou **antes** do merge do #280 na branch. O #280 não toca nenhum arquivo desta feature, e o
CI do PR roda sobre a `main` de agora.

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

## Estado

**Implementada, com validação operacional pendente.** A implementação e a suíte estão fechadas, e
falta comprovar a §10.4 com quem a vai seguir. Os resultados dos roteiros B e C entram aqui, com
data, e só então o estado muda.

## Pendente

- **SC-620 e o resto do SC-623:** a sessão conduzida com uma pessoa da TI, em homologação
  (quickstart B).
- **A US2 contra a L4 real** (quickstart C), bloqueada até haver acesso, como o roteiro D da `071`.
  Antes dela, confira na máquina que vai rodar o roteiro o grupo de dependências `assistente` e o
  `tokenizer.json`.
- **A release sem a biblioteca do tokenizer**, registrada para decisão em
  [`doc/achado-release-sem-o-grupo-do-assistente.md`](../../doc/achado-release-sem-o-grupo-do-assistente.md).
  A `073` só a documenta, e a correção não é o próximo incremento por estar escrita aqui.
