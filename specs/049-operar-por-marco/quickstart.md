# Quickstart — 049 · validar pelo navegador

## Pré-requisitos

- PostgreSQL local de pé (`LC_ALL=C pg_ctl … start`), banco próprio desta worktree.
- `INTERFACE_SELETOR_IDENTIDADE=true` no servidor (sem ele `/gestao/` devolve 503).
- Um Edital publicado com **dois Perfis**: o primeiro com a ampla e duas cotas (três recortes), o
  segundo só com a ampla; um marco computado por Perfil, com regra de corte no primeiro; Resultados
  consolidados na Etapa que o marco enumera, com inscrições nas três listas e nenhuma numa delas.
  O script de preparação da verificação monta esse Edital pelos helpers dos testes, num banco de
  demonstração próprio.

## Percurso

1. **Página do Edital** (`UX-090`). Cada marco mostra o resumo *"Recortes: 3 · com ordem 0 · …"* e
   o caminho *"conduzir o marco"*.
2. **Tela do marco** (`UX-091`). Tabela com três linhas, na ordem da derivação: a ampla, depois as
   cotas. Todas as células em *falta*; a do corte, no segundo Perfil, *não se aplica*.
3. **Ordenar** (US2). Pedir → a conferência lista os três em *Serão praticados*, um deles *ninguém
   concorreu*. Confirmar *"Emitir 3 ordens"* → desfecho *"3 feitos"*; o indicador em *com ordem 3*.
4. **Recusa parcial** (US5). Emitir pela tela do recorte, por fora, o corte de um deles entre a
   conferência e a confirmação do gesto de cortar → desfecho *"2 feitos, 1 recusado"*, com a razão; o
   indicador mostra os três cortados.
5. **Apurar** (US4). Confirmar → três apurações, ou a recusa do recorte sem linha no quadro já na
   conferência, em *Impedidos*.
6. **Publicar** (US3), com a identidade que tem `resultado:publicar`: natureza preliminar, autoridade
   do catálogo → conferência com três recortes → confirmar → três publicações, três documentos; o
   indicador em *publicados 3 (preliminar)*.
7. **Autoridade** (`FR-829`). Com a presidência sem `resultado:publicar`, a tela do marco não oferece
   publicar e diz a quem pedir. Com quem só publica, não oferece ordenar, cortar nem apurar.

## Suíte

```bash
cd backend && make DB_NAME=ps049 lint check test-pg
```

O arquivo desta feature: `tests/interface/test_conducao_do_marco.py`.
