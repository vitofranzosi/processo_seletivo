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
demonstrativo; os links "Configurações de exemplo" carregam as três linhas da tabela do achado.

| Faça | Espere |
|---|---|
| "Simular classificação" | o painel abre à direita; o título recebe o foco |
| Cenário "Corte impedido: empate na última posição da faixa", desfecho "Todos os empatados progridem" | 16 progridem; os dois da 15ª com a mesma marca; "com o outro desfecho, o corte não seria emitido" |
| Troque o desfecho para "A faixa para no alvo", **sem salvar** | "O corte não seria emitido", empate de 2 na 15ª, "e não a do alvo (10)"; todas as linhas "Corte não emitido" |
| Exemplo "Achado, linha 1" | o corte sai com 15; aviso âmbar: a apuração das vagas pararia na 10ª |
| Suplentes 0 | "o cenário foi refeito sobre a nova fronteira"; com `STRICT`, corte recusado na 10ª |
| Cenário "Desempate por critérios sucessivos" | três empatados na pontuação; 1º critério não separa (notas iguais), 2º separa um, 3º os outros dois |
| Cenário "Valor ausente" | Bruno sem posição (sem nota na Prova de Títulos), Diego eliminado, Gabriela atrás no 2º critério por não ter a data |
| Apague o alvo | "A prévia ainda não calcula. Falta: Declare o alvo" |
| "Fechar" | painel vazio; foco de volta no botão |
| Viewport 375 px | o painel cobre a tela; cada linha vira bloco; nenhuma rolagem horizontal |
| Console | nenhuma violação de CSP |

As capturas validadas em 19/10 estão em `prototipo/capturas/`.

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
