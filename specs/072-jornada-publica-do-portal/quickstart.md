# Quickstart — verificar a 072

## Preparação

Banco exclusivo desta worktree (já existe `ps_ux_conversao`, com o seed; para recriar do zero, ver
[diagnóstico da auditoria, §3](../../doc/auditoria-ux-conversao-2026-10-12/diagnostico.md#3-metodologia)).

```bash
cd backend && uv run python manage.py migrate --check; echo $?
```

Servidor: a entrada de preview `ux-conversao` (porta 8077), acrescentada ao `.claude/launch.json` só
durante a sessão, com `INTERFACE_SELETOR_IDENTIDADE=true`, `PORTAL_IDENTIDADE_DEMO=true` e e-mail no
console.

## Verificação canônica

```bash
cd backend && make lint check test-pg DB_NAME=ps_072_teste POSTGRES_USER=$USER
```

e o guardião de citações isolado, depois de mexer em spec ou comentário:

```bash
cd backend && uv run pytest -q tests/test_citacoes_de_requisito.py
```

## Jornadas

| Jornada | Automático | No navegador |
|---|---|---|
| **Encontrar** | integração da vitrine (título, oferta, lugares, `open` dos filtros, busca por lugar, estado vazio) | script de medição nas telas do SC-600; 1280 e 1440 com a barra inteira |
| **Começar — identidade nova** | aceitação pelo canal do candidato: e-mail → código lido da caixa de saída de teste → "Seus dados" **postado pelo formulário** → volta com mensagem → nenhum rascunho → confirmação → rascunho (SC-603) | o mesmo percurso; o CPF de "Seus dados" é digitado por uma pessoa (o agente não digita CPF) |
| **Começar — recorrente** | identidade com núcleo: volta sem "Seus dados"; com sessão: rascunho direto; com rascunho: "Continuar inscrição" | candidata do fixture `MARIA` (`m@ex.br`) |
| **Começar — destino inválido** | `?destino=` externo, rota inexistente, Perfil que não é do Edital: nenhuma tela nomeia vaga, a volta segue o caminho de hoje | — |
| **Preparar** | frase do Requerimento com momento "na inscrição"; ausente sem Requerimento e com "na convocação" | Edital 01/2026 do seed |
| **Acompanhar** | resumo com 1, 3 e 5 vigentes: prazos iguais, parciais, diferentes, encerrados; sucedida fora da conta; sem resultado nada; cartão = página no mesmo instante (SC-604) | Edital 51/2026 do seed |
| **Custo** | a vitrine com 1 e com 3 Editais com resultado faz o mesmo número de consultas | — |
| **Sem script** | consulta sem `hx-`/`onclick`; `open` vindo do servidor | página em `iframe` com `sandbox="allow-same-origin"` |
| **Larguras** | — | sem rolagem lateral em 320, 360, 375, 390, 768, 1280, 1440 (SC-607) |

## Validações humanas (não são feitas pelo agente)

- **SC-605** — percurso conduzido com cinco pessoas de fora do projeto: roteiro em
  [validacao-humana.md](validacao-humana.md), produzido na implementação.
- **FR-1627** — validação do texto de finalidade de "Seus dados" por quem responde pela proteção de
  dados: texto proposto no mesmo arquivo.

Enquanto as duas estiverem pendentes, o estado da feature é **implementação técnica concluída**, e não
**validada e pronta para publicação**.
