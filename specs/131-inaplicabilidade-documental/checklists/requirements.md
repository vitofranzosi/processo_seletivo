# Specification Quality Checklist: A inaplicabilidade documental tem fundamento publicado

**Purpose**: Validar a completude e a qualidade da spec antes do planejamento
**Created**: 2026-11-07
**Feature**: [spec.md](../spec.md)

## Content Quality

- [x] Sem detalhe de implementação na spec além dos nomes de contrato que as specs anteriores já
  usam. Arquivos e funções ficam na pesquisa e no plano.
- [x] Focada no valor para quem confere, quem desfecha, quem formaliza e o candidato
- [x] Todas as seções obrigatórias preenchidas

## Requirement Completeness

- [x] Nenhum marcador de esclarecimento pendente. A P-1 e a P-2 foram decididas em 07/11/2026; a P-3
  continua pendente e não impede.
- [x] Requisitos testáveis e sem ambiguidade. Cada um tem teste previsto na matriz
- [x] Critérios de sucesso mensuráveis, e sem tecnologia, exceto a SC-1377, que é de custo
- [x] Cenários de aceite definidos: os treze do pedido, em `contracts/cenarios.md`
- [x] Casos-limite identificados, com teste previsto na matriz
- [x] Escopo delimitado: cobre e fica fora
- [x] Dependências e premissas identificadas: o PR #425, o sistema fora de produção

## Feature Readiness

- [x] Todo requisito funcional tem critério de aceite
- [x] Os cenários cobrem os fluxos primários: compor, conferir, aceitar, formalizar, transicionar
- [x] Decisões de desenho: o comportamento das D-001 a D-016 foi aprovado em 07/11/2026 (10ª decisão).

## Notes

- A correção do estudo de 07/11 está registrada na D-016 e em R-009: ele recomendava levar o motivo à
  formalização, e a FR-3687 da `117` o proíbe.
- A redação inicial desta spec dizia que a duplicação de Perfil (`043`) levava a condição. Não leva
  documento algum, e a spec foi corrigida (R-004).

## Análise de consistência (07/11/2026, depois das decisões 10ª a 12ª)

Conferidos spec, plano, tarefas, modelo, contratos e matriz.

- **Contradição corrigida:** a FR-4453 mandava a composição esconder o campo no facultativo e na
  inscrição, e o UX-302 o mostrava sempre. A tela não tem script (CSP), e a regra passou a ser a do
  momento incoerente: o rascunho recusa e a publicação impede.
- **Duplicidade eliminada:** a antiga P-2 repetia a 2ª decisão. A redação corrigida foi para a D-003.
- **Referências a pendências decididas:** P-1 e P-2 substituídas pelas 11ª e 12ª decisões em todos os
  artefatos.
- **Citação restaurada:** a guarda da lista incompleta volta a ser citada como FR-4401 da `115`, agora
  na `main`.
- **Cobertura:** todo FR-, SC- e UX- tem tarefa e teste previsto na matriz; todo caso-limite tem teste
  previsto; nenhuma tarefa sem requisito.
- **Sem achado de escopo:** nada no plano cria tabela, papel, rota ou serviço; a ciência reutiliza a
  assinatura da `120`.
