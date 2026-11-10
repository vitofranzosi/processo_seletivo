# Specification Quality Checklist: O barema da Etapa

**Purpose**: Validar a completude e a qualidade da spec antes da implementação
**Created**: 2026-11-10
**Feature**: [spec.md](../spec.md)

## Content Quality

- [x] Sem detalhe de implementação na spec (arquivos e funções estão no plano e na pesquisa)
- [x] Centrada no que operador, avaliador e candidato veem
- [x] Escrita para quem decide o produto
- [x] Seções obrigatórias completas

## Requirement Completeness

- [x] Nenhum marcador [NEEDS CLARIFICATION]; as sete questões (P-1 a P-7) têm recomendação adotada
- [x] Requisitos testáveis e sem ambiguidade
- [x] Critérios mensuráveis, inclusive sobre o texto extraído do PDF e sobre o banco (SC-1630)
- [x] Cenários de aceitação para as quatro histórias e para a jornada inteira
- [x] Casos-limite identificados, cada um com linha na rastreabilidade
- [x] Escopo delimitado (Fora do escopo), com o que ficou fora por proporção
- [x] Dependências e premissas identificadas

## Feature Readiness

- [x] Cada requisito tem tarefa e teste nomeados na rastreabilidade
- [x] Os cinco cenários do pedido têm critério de sucesso próprio
- [x] O que permanece inalterado está dito (FR-5200, FR-5220, FR-5231)
- [x] Proporção verificável (SC-1632)

## Notes

- A correção fixada por recurso (incremento C) é a única mudança fora da Etapa e da Mesa; sem ela o
  total do Resultado de recurso divergiria do detalhamento que o candidato vê.
