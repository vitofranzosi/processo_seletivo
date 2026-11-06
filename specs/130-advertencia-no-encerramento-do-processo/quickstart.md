# Quickstart: validar a advertência no "Encerrar Processo"

Roteiro de validação, e não de implementação. Os detalhes de comportamento estão no
[contrato](contracts/confirmacao-do-processo.md) e no [modelo](data-model.md).

## Pré-requisitos

- PostgreSQL local com `LC_ALL` exportado (macOS com Homebrew).
- Um `DB_NAME` próprio desta worktree (CLAUDE.md, *Um banco de teste por worktree*).
- `uv sync --extra dev` na worktree.

## 1. A suíte da feature

```bash
cd backend
PYTEST_ADDOPTS="tests/unit/interface/test_advertencia_do_processo.py tests/interface/test_advertencia_do_encerramento_do_processo.py tests/performance/test_confirmacao_do_encerramento_do_processo.py tests/interface/test_processo.py" \
  DB_NAME=ps_130 make test-pg PYTEST_WORKERS=0
```

Esperado: tudo passa. O orçamento de consultas é o mesmo com escala 1 e 10 de inscrições.

## 2. Os guardiões que leem a spec, a tela e o código

```bash
cd backend
DB_NAME=ps_130 uv run pytest -q tests/test_citacoes_de_requisito.py tests/test_readme_acompanha_o_codigo.py \
  tests/test_gramatica_das_portas.py tests/interface/test_paineis_e_telas_de_apoio.py
```

## 3. A jornada na tela

Num banco descartável, montar com os helpers dos testes (`tests/fixtures/relatorio.montar_cenario`,
final `pendente`) um Processo **Ativo** com um Edital **Encerrado** e uma convocação no prazo. Subir o
`runserver` com `INTERFACE_SELETOR_IDENTIDADE=true` e entrar como gestor com `processo:encerrar`.

| Passo | O que fazer | O que se espera |
|---|---|---|
| a | abrir "Encerrar Processo" | o bloco "Em aberto nos Editais deste Processo", o Edital, "1 convocação aguardando resposta, até …", e a frase sobre quem está no prazo (UX-276); nenhum nome, CPF ou e-mail |
| b | sem fechar a aba, registrar pelo shell a resposta da convocação | — |
| c | preencher o motivo e confirmar | a tela volta (409) com "As providências em aberto mudaram…", a lista atual sem a convocação e o motivo preenchido; o Processo continua Ativo |
| d | confirmar de novo | 302 ao detalhe; Processo Encerrado |
| e | repetir com o final `sem-pendencia` | a frase da UX-277, com a ressalva do cadastro de reserva; confirmar encerra na primeira tentativa |
| f | abrir "Cancelar Processo" num Processo igual ao de (a) | a tela de hoje, sem bloco |

Capturas de (a), (c) e (e) vão para `capturas/` na fase de implementação.

## 4. A suíte inteira

```bash
cd backend && DB_NAME=ps_130 make lint check test-pg
```

Esperado: sem falha nova em relação à `main` (SC-1326). O teste de tempo da ocupação pode oscilar sob
carga (CLAUDE.md); nesse caso, meça isolado antes de concluir.
