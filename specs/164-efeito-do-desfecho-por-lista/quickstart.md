# Quickstart: O efeito do desfecho da Etapa por lista

O roteiro prova as seis histórias. Ele monta o Edital da spec pelos helpers dos testes, sem
`seed_demo`, que não produz Etapa restrita.

## Pré-requisitos

- A branch da `164` sobre a da `163`, com `manage.py migrate --check` limpo.
- PostgreSQL local, com o par `TEST_DB_ENGINE=postgresql` e `DB_USER`, e `DB_NAME` próprio da
  worktree.

## Pela suíte

```bash
cd backend
PYTEST_ADDOPTS="tests/unit/resultados/test_efeito_do_desfecho.py tests/integration/resultados/test_retirada_da_reserva.py tests/integration/classificacao/test_ordem_com_retirada.py tests/integration/ocupacao/test_ocupacao_com_retirada.py tests/integration/recursos/test_recurso_da_retirada.py tests/integration/publicacoes/test_retificacao_do_efeito.py" make test-pg PYTEST_WORKERS=0
```

| Arquivo | O que prova |
|---|---|
| `test_efeito_do_desfecho.py` | a leitura do efeito (acervo, padrão, explícito), a gravidade e as frases |
| `test_retirada_da_reserva.py` | consolidação e Ocorrência com cada efeito; progressão e faixa (US2, US6) |
| `test_ordem_com_retirada.py` | o universo e o sem posição por recorte, nas três posições da Etapa (FR-7012) |
| `test_ocupacao_com_retirada.py` | ocupação, fila e situação da vaga da reserva, com o horizonte (FR-7014, FR-7027) |
| `test_recurso_da_retirada.py` | deferimento, gravidade e reavaliação contra ausência (US4) |
| `test_retificacao_do_efeito.py` | impedimento histórico e serialização (US5) |

## Pela interface (jornada)

1. Compor, pela tela, o Edital de três Perfis da `163`:
   - Heteroidentificação decisória, eliminatória, restrita a `PPI`;
   - conferir que o grupo do efeito aparece, com *"Deixa de concorrer pela reserva"* marcada.
2. Publicar. Conferir a frase do efeito no PDF (redações 1, 2 e 3) e na Revisão.
3. Pelos helpers no shell:
   - inscrever Maria (`PPI`);
   - consolidar a Prova;
   - concluir a Heteroidentificação de Maria em sentido desfavorável e consolidar.
4. Na gestão:
   - a confirmação da consolidação mostra *"1 retirada da reserva"*;
   - a lista de Resultados mostra *"Retirada da reserva"*.
5. Emitir e publicar a ordem do marco. Conferir:
   - Maria sem posição na lista `PPI`, com o motivo, na conferência da ordem;
   - Maria com posição na ampla.
6. No portal, entrar como Maria pelo código de acesso, que sai no terminal do servidor. Conferir:
   - nenhum *"Eliminado"*;
   - a linha da reserva perdida;
   - o cartão da `PPI` com *"Você deixou de concorrer por esta lista."*

A jornada do candidato no navegador é a verificação final, pelo canal do candidato, que a revisão de
14/11 pediu.
