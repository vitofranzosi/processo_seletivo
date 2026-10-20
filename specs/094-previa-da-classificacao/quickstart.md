# Quickstart: Prévia interativa da classificação — fatia 1

Dois roteiros: o do **protótipo**, que existe hoje e se avalia sem banco, e o da **feature**, para quando
ela for implementada.

## 1. O protótipo (hoje)

**Pré-requisito**: `uv sync --extra dev` dentro de `backend/` (uma vez por worktree).

Pelo painel do app: entrada `previa-094` do `.claude/launch.json`. Pelo terminal, de dentro de
`backend/`:

```bash
uv run python ../specs/094-previa-da-classificacao/prototipo/servidor.py 8094
```

Abra <http://localhost:8094/>. A faixa do topo diz o que executa o motor oficial e o que é
demonstrativo; os links "Configurações de exemplo" carregam os três cenários da comparação e as linhas
da tabela do achado.

| Faça | Espere |
|---|---|
| "Simular classificação" | o painel abre à direita, pela **manchete**: "16 de 23 candidatos progridem para a Entrevista, 1 além da faixa pelo empate na 15ª…"; o título recebe o foco |
| Leia o fluxo | Classificação (21 com posição) → Corte (Emitível, faixa de 15 = alvo 10 + 5 suplentes) → Entrevista (16 participam); abaixo, o ramo da continuação |
| Leia o bloco tracejado | "Depois do corte: a apuração das vagas — hipótese": pararia na 10ª |
| Troque o desfecho para "A faixa para no alvo", **sem salvar** | os mesmos 23 candidatos; manchete "O corte não seria emitido"; quadro "O que mudou": corte emitível → impedido na 15ª, progridem 16 → 0 |
| Suplentes 0 | "impedido na 15ª → impedido na 10ª": o empate continuou na 10ª, a regra mudou o desfecho |
| Desfecho de volta para "Todos os empatados progridem" | 11 progridem; João e Karina "Progride pelo empate", marcados "mudou" |
| Alvo 30 | "a faixa passa dos 21 classificados: todos cabem — remonte"; botão "Remontar para esta configuração" |
| Role até "Empates na pontuação" | uma tabela por grupo, critério a critério, com o que separou destacado e a linha que o empate atravessa |
| Seletor "Candidatos fictícios" → um caso-limite | o aviso de que o caso acompanha a fronteira |
| Apague o alvo | "A prévia ainda não calcula. Falta: Declare o alvo" |
| "Fechar" | painel vazio; foco de volta no botão |
| Viewport 375 px | o painel cobre a tela; o fluxo em coluna, com setas para baixo; nenhuma rolagem horizontal |
| Console | nenhuma violação de CSP |

A comparação com a primeira versão, nos três cenários e com as cinco perguntas, está em
[`prototipo/comparacao-v1-v2.md`](prototipo/comparacao-v1-v2.md).

As capturas validadas em 19/10 estão em `prototipo/capturas/v1/` e `prototipo/capturas/v2/`.

## 2. A feature (depois da implementação)

**Pré-requisitos**: banco preparado (`make preparar`), `INTERFACE_SELETOR_IDENTIDADE=true`, um Edital em
elaboração com ao menos uma Etapa classificatória com peso, um Perfil com quadro de vagas e um marco
pela pontuação.

1. Etapa Classificação da composição → cartão do marco → **Simular classificação**. O painel nomeia o
   Perfil e o marco, e os candidatos estão marcados como fictícios.
2. Repita a tabela da seção 1 sobre o cartão real. Os números devem ser os mesmos do protótipo para a
   mesma configuração — os dois chamam o mesmo motor.
3. Recarregue a página: o marco continua como estava gravado. Nada do que foi alterado só para ver a
   prévia foi salvo.
4. Marco por sorteio: o botão não aparece.

**Verificação automática**:

```bash
cd backend && make lint check test-pg
```

Os testes da feature, isolados:

```bash
cd backend && uv run pytest tests/unit/classificacao/test_universo_classificavel.py tests/unit/classificacao/test_ordenar_com_trajetoria.py tests/unit/classificacao/test_cenarios_da_previa.py tests/integration/classificacao/test_previa_equivale_ao_oficial.py tests/integration/classificacao/test_previa_sem_efeito.py tests/interface/test_previa_da_classificacao.py
```

Os de integração e interface pedem PostgreSQL: `TEST_DB_ENGINE=postgresql` **e** `DB_USER` (ver
`CLAUDE.md`).
