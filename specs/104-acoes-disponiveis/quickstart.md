# Quickstart: Ações disponíveis

## Automático

```bash
cd backend
TEST_DB_ENGINE=postgresql DB_USER=$USER DB_NAME=acoes104 uv run pytest \
  tests/interface/test_acoes_disponiveis.py tests/unit/interface/test_trabalho_do_ator.py \
  tests/performance/test_trabalho_em_escala.py -q
```

## Manual

Servidor com `seed_demo` e o seletor de identidade ligado. Prepare uma Retificação em revisão
(Edital 26/2026), uma homologada (01/2026) e uma devolvida (51/2026), como no diagnóstico.

## Roteiro de validação com pessoas (SC-990)

**Participantes**: três pessoas da equipe — uma que homologa, uma que elabora, uma que gere. Sessão
individual de 15 minutos, com a tela compartilhada. Não explique a faixa antes.

**Tarefas**

1. *Homologador*: "Entre no GPS e diga se há algo para você fazer. Se houver, comece."
2. *Elaborador*: "Uma Retificação sua voltou. Encontre-a e diga o que precisa ser corrigido."
3. *Gestor*: "Diga em que situação está o Edital 26/2026 e qual o próximo marco dele."

**Observar e anotar, sem ajudar**

- concluiu sem ajuda (sim / com dica / não);
- tempo até o primeiro clique certo (cronômetro, segundos);
- cliques que não levaram a nada;
- como a pessoa leu "Ações disponíveis para você", "Conferir e submeter", "devolvida", "reenviada";
- se confundiu ação sua com acompanhamento de outra pessoa;
- se soube dizer quem age depois do ato.

**Registrar** em `verificacao.md`, com data e papel, sem nome. Se ninguém estiver disponível, o
roteiro fica e a validação continua pendente.
