# Quickstart: Sorteio viável desde a publicação

**Feature**: [spec.md](spec.md) | **Mensagens**: [contracts/mensagens.md](contracts/mensagens.md)

Roteiro de validação. Ele prova as quatro histórias pelo canal de cada ator (Princípio VI). Não é
roteiro de implementação.

## Pré-requisitos

- Ambiente de desenvolvimento com `SORTEIO_FONTE_DE_DEMONSTRACAO=true` (o `development` já liga) e
  `INTERFACE_SELETOR_IDENTIDADE=true` para abrir `/gestao/`.
- Banco próprio desta worktree, preparado em três passos com `make preparar`, sem `seed_demo`: os
  Editais da `seed_demo` declaram a fonte com horário e não exercitam nada daqui.
- Um Edital em composição com um Perfil e um marco por sorteio, e o período de inscrições designado.

## Verificação automatizada

```bash
cd backend && make lint check test-pg
```

Os casos desta feature rodam também isolados:

```bash
cd backend && PYTEST_ADDOPTS="-k viabilidade or extracao_inviavel or so_a_data" make test-pg PYTEST_WORKERS=0
```

Esperado: a matriz da SC-954 verde, com zero achados para fonte com horário; o conjunto de sorteios
constituídos da suíte inalterado (SC-957).

## Cenário 1 — a publicação é impedida (US1, SC-955)

1. Na composição, declare o método do marco com `Loteria Federal`, concurso `6113`, e extração em
   28/10/2026 às 20h05. Declare o fim das inscrições em 28/10/2026 às 9h.
2. Abra a revisão e tente publicar.
3. **Esperado**: o achado da seção 1 do contrato, impeditivo, apontando a etapa Classificação. O
   Edital não publica.
4. Mude a extração para 29/10/2026 e confira de novo. **Esperado**: o achado some.

A consulta à Caixa não acontece em nenhum passo: a conferência lê só o que o Edital declara.

## Cenário 2 — a Retificação adverte, o aviso antes de congelar e a recusa (US2, US3, US4, SC-959)

**Por que o caminho passa por uma Retificação.** Um Edital com a extração no dia do fim das inscrições
não publica mais (cenário 1), e um Edital com as inscrições já encerradas também não (FR-346 da
`028`). O estado que o aviso protege só se alcança por uma Retificação, que só adverte. É também o
caminho real de um Edital que tenha prorrogado as inscrições.

1. Componha e publique um Edital com a `Fonte de demonstração (só a data)`, o fim das inscrições
   **daqui a poucos minutos** (o término tem hora e minuto) e a extração **amanhã**. A publicação
   passa.
2. Envie uma inscrição pelo portal antes do fim.
3. Elabore uma Retificação que mude a extração para **hoje**. **Esperado**: a advertência da seção 2
   na confirmação, e a Retificação publica.
4. Passado o fim das inscrições, abra a tela do sorteio do marco. **Esperado**: o aviso da seção 3
   antes de "Publicar e congelar a relação", com o botão disponível.
5. Congele e observe a ocorrência. **Esperado**: o diagnóstico da seção 4 antes de "Realizar o
   sorteio".
6. Realize o sorteio. **Esperado**: a recusa `occurrence_precedes_freeze` com os acréscimos da seção
   5.

## Cenário 3 — a saída em três passos (FR-2661)

1. No Edital do cenário 2, retifique a extração para **amanhã**. **Esperado**: sem advertência. Na tela
   do sorteio, a relação congelada mostra a variante "o método já foi retificado" da seção 4.
2. Publique relação nova, sucedendo a atual, com motivo. **Esperado**: o diagnóstico some.
3. Contraprova da fonte com horário: repita o cenário 2 com a `Fonte de demonstração` atual.
   **Esperado**: nenhuma advertência, nenhum aviso, e o sorteio é constituído no mesmo dia.

O sorteio da relação nova só se constitui amanhã, quando o início do dia corrente for posterior ao
congelamento. Isso é a garantia funcionando, e não uma falha do roteiro.

## Cenário 4 — o Edital 72/2026 do servidor

Reproduza o cronograma do achado num teste de integração com a Loteria Federal e a rede substituída.
**Esperado**: publicação impedida pelo achado da seção 1. Este é o caso que a SC-955 nomeia.
