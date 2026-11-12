# Quickstart: validar "Minhas atividades"

Roteiro de validação depois da implementação. Ele não implementa nada, e não substitui os testes.

## Pré-requisitos

- O ambiente do README e as armadilhas do `CLAUDE.md`: PostgreSQL, `LC_ALL` no macOS, e o
  `INTERFACE_SELETOR_IDENTIDADE=true`.
- Um banco próprio com os cenários de treinamento (C01–C17), como no
  [`validacao/README.md`](../../doc/estudo-minhas-atividades-2026-11-12/validacao/README.md) do
  estudo. Ele pede a autoridade e `ARQUIVOS_CANDIDATOS_RAIZ`.

## 1. A suíte da feature

```bash
cd backend && PYTEST_ADDOPTS="tests/unit/interface/test_atividades.py tests/interface/test_minhas_atividades.py tests/interface/test_minhas_atividades_coerencia.py tests/performance/test_minhas_atividades_em_escala.py" make test-pg PYTEST_WORKERS=0
```

Esperado: tudo verde. O teste de escala imprime as consultas da presidência com 0 e 1 Edital
presidido, e as do membro com 1 e 4 comissões.

## 2. A presidência (US1)

Entre pelo seletor como `treino.presidencia` e abra "Minhas atividades".

Esperado:
- a barra e o título dizem "Minhas atividades";
- "Para fazer agora" tem os atos da presidência dos Editais publicados;
- as ordens de lista vazia de vários Editais aparecem numa linha só, com "Ver os N";
- cada linha diz "Presidência", e o primeiro link abre a tela do ato com o controle habilitado;
- "Em espera" está fechada, e as datas dizem a origem.

## 3. O avaliador (US2)

Entre como `treino.avaliacao1`.

Esperado:
- "Avaliar N inscrições", com "Alocação" e o link da Mesa;
- os cartões da terceira seção;
- nada de condução.

Repita com `treino.avaliacao2`: "Nada depende de você agora no que esta página cobre", com a nota de
cobertura.

## 4. O Gestor (US3)

Entre como `treino.gestao`. Ele não preside: nenhuma linha de condução, e a nota diz que o que ele pode
fazer por permissão de gestão fica no Centro de cada Edital. O caso do Gestor que preside é coberto
pelo teste, que monta a presidência.

## 5. A Lista (US6)

Abra Processos Seletivos como `treino.presidencia`. Esperado:
- a faixa não tem número de atividades;
- a nota tem o link "Minhas atividades";
- "Ver minhas atividades" leva à página.

## 6. A 375 px

`resize_window` em 375 × 812 na página da presidência: sem rolagem horizontal, e "Para fazer agora"
na primeira tela.

## 7. A tarefa com pessoas (SC-2281, humano)

Com os cenários e, quando houver, a comissão real: "sem abrir nenhum Edital, diga o que você tem a
fazer e faça o primeiro". O tempo e os erros se comparam com o percurso de hoje (Processo → Edital →
"O que fazer agora"), pelo método de tarefas do estudo do Centro de Controle.
