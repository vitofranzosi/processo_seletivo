# Verificação — Novidades do GPS

*14/11/2026, sobre a `main` em `cf6327c8`, sem commit.*

## Suíte

- `ruff check` e `ruff format --check`: limpos.
- Suíte inteira contra PostgreSQL, 4 workers: **20 185 passando e 24 pulados, sem falha** (549s).
- Novos: `tests/novidades/test_catalogo.py`, `tests/novidades/test_rascunho.py` e
  `tests/interface/test_novidades.py`.

## Conteúdo inicial (SC-2502)

- 45 notas, de 18/10 a 13/11, conferidas contra as seções da Documentação do Sistema.
- Todos os PRs citados foram conferidos no GitHub: estão mergeados na `main`. A data de cada nota é a
  do último merge, no horário de Brasília; três datas foram corrigidas na conferência.
- **Ficaram de fora, para a próxima curadoria:** os PRs 534, 537, 539, 540, 542, 543 e 545 (a
  `162` a `165`, a moldura dos e-mails e a redação 3 do Edital). Estão mergeados, mas a
  Documentação do Sistema ainda os descreve como "Previsto", e não houve conferência na tela.

## Navegador (SC-2504, UX-804, UX-805)

Entrada `novidades-168` do `.claude/launch.json`, banco `ps_novidades`, como `demo.gestor`:

- primeira entrada: a barra mostra "9+"; a página diz que é a primeira visita, e o número some;
- com três notas desmarcadas no banco: a barra mostra "3", e a página abre com "Desde sua última
  visita", listando as três;
- console sem erro; sem rolagem horizontal a 375, 1.280 e 1.440 px; barra recolhida mostra o ponto
  no canto do ícone.

## Não verificado

- A entrada institucional e a troca de unidade chamam o mesmo gancho, mas não foram exercitadas pelo
  provedor simulado.
- SC-2501 é validação humana.
