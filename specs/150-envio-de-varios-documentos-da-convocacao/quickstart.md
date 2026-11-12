# Quickstart: verificar o envio de vários documentos da convocação (150)

Roteiro de verificação da implementação. Não é a implementação.

## Pré-requisitos

- Banco de teste próprio da worktree (`DB_NAME`) e o par `TEST_DB_ENGINE=postgresql` e `DB_USER`
  (ver CLAUDE.md); `uv sync --extra dev --extra navegador` e `uv run playwright install chromium` para
  a jornada no navegador.
- Para ver na tela: um banco de demonstração com uma convocação que pede ao menos quatro documentos,
  e o acesso do candidato pelo código impresso no terminal do `runserver`.

## 1. Os testes

```bash
cd backend && node --test tests/javascript/varios.test.js tests/javascript/arquivo.test.js tests/javascript/envio.test.js
```

```bash
cd backend && PYTEST_ADDOPTS="tests/interface/test_portal_documentos_da_convocacao.py tests/integration/portal/test_envio_de_varios.py tests/test_armazenamento_no_navegador.py tests/test_vocabulario_dos_documentos_da_convocacao.py" make test-pg
```

```bash
cd backend && PYTEST_ADDOPTS="tests/navegador/test_jornada_dos_documentos_da_convocacao.py" make test-pg PYTEST_WORKERS=0
```

## 2. Os cenários na tela

| # | Faça | Espere | Prova de |
|---|---|---|---|
| 1 | Escolha um arquivo no 1º cartão | Botão "Enviar"; os outros cartões iguais | US1-1 |
| 2 | Escolha outro no 3º | Os dois botões dizem "Enviar os 2 documentos escolhidos" | US1-2, FR-5601 |
| 3 | Escolha os quatro e envie pelo 2º | "Enviando k de 4…"; volta à confirmação com os quatro, com data e hora | SC-1800, FR-5608 |
| 4 | Quatro escolhidos, o 2º uma imagem | "Recebemos 3 de 4 documentos", link para o 2º; a recusa de foto no cartão dele | SC-1802 |
| 5 | Dois acima do limite | Volta ao cartão do 1º, foco na recusa; a do 2º no cartão dele | FR-5609 |
| 6 | Quatro escolhidos; corte a rede (DevTools, *Offline*) depois do 2º | A tela fica; diz os recebidos e os não; os dois restantes continuam escolhidos | FR-5610 |
| 7 | Quatro escolhidos; saia noutra aba; envie | Nenhum recebido; frase de acesso expirado; escolhas no lugar | US2-4 |
| 8 | Dois escolhidos; envie por um cartão vazio | "Escolha um arquivo PDF antes de enviar." no vazio; escolhas no lugar | FR-5604 |
| 9 | Três escolhidos; "Remover a escolha" em dois | O terceiro volta a "Enviar"; envia só ele | US3 |
| 10 | Desligue o script | A frase do `<noscript>` antes do 1º cartão; envio de um, como hoje | SC-1803 |
| 11 | O mesmo PDF, renomeado, no 1º e no 2º | Aviso nos dois, cada um nomeando o outro; botão inalterado; envio possível | SC-1806, FR-5617 |
| 12 | Envie o 1º; escolha o mesmo PDF no 2º | "…que você já enviou para ‹1º›"; envio possível | FR-5615 |
| 13 | Dois PDFs diferentes, mesmo nome | Nenhum aviso | SC-1807 |
| 14 | Reenvie o mesmo arquivo ao mesmo cartão | "Este arquivo já tinha sido recebido."; sem aviso do achado 11 | SC-1807 |
| 15 | A 375 px, com leitor de tela, cenários 3 e 11 | Sem rolagem horizontal; contagem, progresso e aviso anunciados | SC-1804, UX-501, UX-504 |

## 3. O que fica para pessoas

- **SC-1805**: a sessão de validação com três pessoas que nunca viram a tela.
- O leitor de tela real (VoiceOver ou NVDA) do SC-1804; a jornada automatizada prova o nome acessível
  e as regiões vivas, não a fala.
