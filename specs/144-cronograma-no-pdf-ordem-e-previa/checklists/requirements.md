# Specification Quality Checklist: O Cronograma — visibilidade no PDF, ordenação e prévia

**Purpose**: Validar a completude e a qualidade da spec antes do planejamento
**Created**: 2026-11-10
**Feature**: [spec.md](../spec.md)

## Content Quality

- [x] Sem detalhe de implementação na spec (os nomes de arquivo e função estão no plano e na pesquisa)
- [x] Centrada no que o operador vê e no que o documento publica
- [x] Escrita para quem decide o produto
- [x] Seções obrigatórias completas

## Requirement Completeness

- [x] Nenhum marcador [NEEDS CLARIFICATION]; as duas questões (P-1, P-2) têm recomendação adotada
- [x] Requisitos testáveis e sem ambiguidade
- [x] Critérios mensuráveis, sobre o texto extraído do PDF e não sobre o HTML (SC-1588)
- [x] Cenários de aceitação definidos para as três histórias e para a jornada inteira
- [x] Casos-limite identificados, cada um com linha na rastreabilidade
- [x] Escopo delimitado (Fora do escopo)
- [x] Dependências e premissas identificadas

## Feature Readiness

- [x] Cada requisito funcional tem teste nomeado na rastreabilidade
- [x] As três histórias cobrem os três incrementos
- [x] O que permanece inalterado está dito (FR-5103, FR-5112, FR-5114)

## Notes

- O que esta checklist não detecta: contradição entre requisitos. A leitura cruzada feita foi entre
  "ocultar não é desativar" (FR-5103) e o filtro do PDF (D-002) — resolvida por a frase da Etapa e a do
  período continuarem lendo o Evento oculto (FR-5107, FR-5108).
