# Quickstart: validar as regras de deliberação

Roteiro de verificação da `165`. As frases esperadas estão em [contracts/](contracts/); o modelo, em
[data-model.md](data-model.md).

## Pré-requisitos

- A worktree com a `163` e a `164` (a base do PR).
- PostgreSQL local com `LC_ALL` exportado, e um `DB_NAME` próprio (ver *As armadilhas caras* no
  `CLAUDE.md`).
- O banco preparado: `make preparar` (papéis, migrate, papéis de novo). O provisionamento deve dizer
  **61** tabelas append-only no total.

## 1. A suíte da feature

```bash
cd backend && DB_NAME=gps_165 make test-pg PYTEST_ADDOPTS="tests/unit/resultados/test_deliberacao.py tests/unit/editais/test_deliberacao_na_publicacao.py tests/integration/resultados/test_consolidacao_deliberada.py tests/integration/resultados/test_gatilhos_da_deliberacao.py tests/integration/avaliacoes/test_parecer_as_cegas.py tests/integration/recursos/test_recurso_da_deliberacao.py tests/integration/publicacoes/test_retificacao_da_deliberacao.py tests/interface/test_composicao_da_deliberacao.py tests/interface/test_conferencia_da_deliberacao.py"
```

Esperado: tudo passa. A tabela-verdade cobre três e cinco pareceres sob as três regras (SC-2351).

## 2. Cenários de aceitação, pelo teste que os prova

| Cenário | Onde | Resultado esperado |
|---|---|---|
| US1, a regra na composição e no documento | `test_composicao_da_deliberacao.py`, `test_deliberacao_na_publicacao.py` | as três opções sem marca; publicação recusa sem regra e com maioria par; frase no documento |
| US2, às cegas | `test_parecer_as_cegas.py` | quem tem parecer pendente não recebe sentido nem texto alheio por tela, fragmento ou link; exposição barra atribuição e reabertura |
| US3, a deliberação | `test_consolidacao_deliberada.py` | 2 «Indeferido» × 1 «Deferido» dá os três desfechos da tabela; o Resultado cita os três pareceres e a versão |
| US4, o candidato | `test_recurso_da_deliberacao.py` | regra, contagem e textos desfavoráveis sem autoria; parte pública sem nada disso |
| US5, o recurso | `test_recurso_da_deliberacao.py` | correção fixada cria o sucessor; reavaliação recusada sem gravar decisão |
| US6, a Retificação | `test_retificacao_da_deliberacao.py` | troca passa antes do primeiro Resultado e é recusada depois, contando os superados |
| SC-2350, o acervo | `test_elevacao_de_versao.py`, `test_composicao_da_deliberacao.py` | mesmo resumo canônico e mesmo documento |
| SC-2353, uma avaliação | `test_consolidacao.py` (existente) | nada muda |

## 3. Pelo navegador (opcional)

1. Compor um Edital com a Heteroidentificação decisória, eliminatória, restrita a `PPI`, com três
   avaliações e a regra *«Deferido» quando a maioria dos pareceres for «Deferido»*; publicar.
2. Alocar três membros e distribuir; concluir dois «Indeferido» e um «Deferido».
3. Como presidência, consolidar: a conferência mostra *Indeferido — 2 de 3 pareceres «Indeferido», por
   maioria*.
4. Publicar o marco e abrir o acompanhamento do titular: a linha diz a regra e a contagem, e o parecer
   mostra os dois textos «Indeferido», sem nome.

## 4. Verificação final

```bash
cd backend && make lint check && DB_NAME=gps_165 make test-pg
```

Mais `tests/test_citacoes_de_requisito.py` e `tests/test_readme_acompanha_o_codigo.py`, que a suíte
inclui.
