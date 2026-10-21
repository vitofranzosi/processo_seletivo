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
| "Simular classificação" no primeiro cartão | o painel abre na **jornada** (terceira rodada): Prova Escrita + Prova de Títulos → Classificação para a Entrevista (16 avançariam, 5 não, 2 sem posição) → Análise documental (indeterminado) → Entrevista ("Até 16 candidatos poderiam participar") → Classificação final (indeterminado); o título recebe o foco |
| "Simular este marco" na Classificação final | a jornada pelo segundo marco: o primeiro "não calculado aqui", a Entrevista com a nota de que a prévia dá nota fictícia a todos, e "Ficariam dentro da faixa" |
| "Explorar classificação e desempate" | o **detalhe** (a segunda rodada): manchete, fluxo, apuração das vagas como hipótese, fronteira e empates; "Voltar ao processo" volta à jornada com a mesma população |
| No detalhe, leia o bloco tracejado | "Depois do corte: a apuração das vagas — hipótese": pararia na 10ª |
| Troque o desfecho para "A faixa para no alvo", **sem salvar** | os mesmos 23 candidatos; na jornada, "Ninguém avançaria por enquanto" e, na Entrevista, "Ninguém, por enquanto"; quadro "O que mudou": corte emitível → impedido na 15ª, avançam 16 → 0 |
| Suplentes 0 | "impedido na 15ª → impedido na 10ª": o empate continuou na 10ª, a regra mudou o desfecho |
| Desfecho de volta para "Todos os empatados progridem" | 11 avançam; no detalhe, João e Karina "Avança pelo empate", marcados "mudou" |
| Alvo 30 | "a faixa passa dos 21 classificados: todos cabem — remonte"; botão "Remontar para esta configuração" |
| Role até "Empates na pontuação" | uma tabela por grupo, critério a critério, com o que separou destacado e a linha que o empate atravessa |
| Seletor "Candidatos fictícios" → um caso-limite | o aviso de que o caso acompanha a fronteira |
| Apague o alvo | "A prévia ainda não calcula. Falta: Declare o alvo" |
| "Fechar" | painel vazio; foco de volta no botão |
| Viewport 375 px | o painel cobre a tela; o fluxo em coluna, com setas para baixo; nenhuma rolagem horizontal |
| Console | nenhuma violação de CSP |

A comparação com a primeira versão, nos três cenários e com as cinco perguntas, está em
[`prototipo/comparacao-v1-v2.md`](prototipo/comparacao-v1-v2.md).

As capturas validadas em 19/10 estão em `prototipo/capturas/v1/`, `v2/` e `v3/`.

## 2. A feature (implementada em 20/10)

**O ambiente da validação** — o banco próprio, o Edital de demonstração e o servidor na porta 8095. As
senhas são as do `.env.example`, e os papéis são os do cluster local:

```bash
cd backend && createdb ps_094_ui
cd backend && LC_ALL=pt_BR.UTF-8 DB_HOST=localhost DB_NAME=ps_094_ui DB_MIGRATION_USER=processo_seletivo_owner DB_MIGRATION_PASSWORD=change-me DB_RUNTIME_USER=processo_seletivo_runtime DB_RUNTIME_PASSWORD=change-me make preparar POSTGRES_USER=$USER DB_NAME=ps_094_ui
```

```bash
cd backend && LC_ALL=pt_BR.UTF-8 DB_HOST=localhost DB_NAME=ps_094_ui DJANGO_SETTINGS_MODULE=config.settings.development DB_ROLE=runtime DB_RUNTIME_USER=processo_seletivo_runtime DB_RUNTIME_PASSWORD=change-me uv run python manage.py shell < ../specs/094-previa-da-classificacao/ambiente-de-compreensao.py
```

O servidor é a entrada `interface-094` do `.claude/launch.json`. O `make preparar` imprime
`40 de 40` na segunda passada; `0 de 40` é a segunda passada que não rodou. O banco de 20/10 recebeu
também o `seed_demo` (com as mesmas variáveis e `manage.py seed_demo`), antes do script; o roteiro só
usa o Edital 94/2026, e não se conferiu se o ambiente de demonstração abre sem o `seed_demo`.

**O percurso**:

1. Ambiente de demonstração → Elaborador → Edital 94/2026 → Elaborar → **Classificação** → cartão do
   marco → **Simular classificação**. O painel nomeia o Perfil e o marco, abre na jornada, e os
   candidatos estão marcados como fictícios.
2. Mude o desfecho do empate no cartão: o painel recalcula sobre os mesmos 48 candidatos e diz o que
   mudou, sem tirar o foco do campo.
3. **Explorar classificação e desempate** → o detalhe; **Voltar ao processo** → a jornada; **Fechar** → o
   foco volta ao botão do cartão.
4. Recarregue a página: o marco continua como estava gravado. Nada do que foi alterado só para ver a
   prévia foi salvo.
5. Marco por sorteio: o botão não aparece.
6. Repita em 375 px: o painel cobre a tela, e as tabelas viram blocos, sem rolagem lateral.

As capturas de 20/10, em desktop e em 375 px, estão em
[`capturas-da-interface/`](capturas-da-interface/). O roteiro com pessoas é o
[roteiro de compreensão](roteiro-de-compreensao.md).

**Verificação automática**:

```bash
cd backend && make lint check test-pg
```

Os testes da feature, isolados:

```bash
cd backend && uv run pytest tests/unit/classificacao/test_universo_classificavel.py tests/unit/classificacao/test_ordenar_com_trajetoria.py tests/unit/classificacao/test_cenarios_da_previa.py tests/unit/classificacao/test_jornada.py tests/unit/classificacao/test_previa.py tests/integration/classificacao/test_previa_equivale_ao_oficial.py tests/interface/test_previa_da_classificacao.py
```

Os de integração e interface pedem PostgreSQL: `TEST_DB_ENGINE=postgresql` **e** `DB_USER` (ver
`CLAUDE.md`).
