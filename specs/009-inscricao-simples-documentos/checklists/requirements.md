# Specification Quality Checklist: Inscrição Simples e Documentos do Candidato

**Purpose**: Validate specification completeness and quality before proceeding to planning
**Created**: 2026-08-30
**Revalidado**: 2026-08-31, após revisão externa
**Feature**: [spec.md](../spec.md)
**Resultado**: **12 de 16 itens aprovados**, com quatro exceções deliberadas e documentadas nas
notas. Não é "todos passam".

## Content Quality

- [ ] No implementation details (languages, frameworks, APIs)
- [x] Focused on user value and business needs
- [ ] Written for non-technical stakeholders
- [x] All mandatory sections completed

## Requirement Completeness

- [x] No [NEEDS CLARIFICATION] markers remain
- [x] Requirements are testable and unambiguous
- [x] Success criteria are measurable
- [ ] Success criteria are technology-agnostic (no implementation details)
- [x] All acceptance scenarios are defined
- [x] Edge cases are identified
- [x] Scope is clearly bounded
- [x] Dependencies and assumptions identified

## Feature Readiness

- [x] All functional requirements have clear acceptance criteria
- [x] User scenarios cover primary flows
- [x] Feature meets measurable outcomes defined in Success Criteria
- [ ] No implementation details leak into specification

## Notes

Quatro itens ficam deliberadamente sem marca, pelo mesmo motivo registrado na `007`, e nenhum deles
é lacuna a corrigir antes do `/plan`:

- **Detalhes de implementação (itens 1 e 4 de Feature Readiness).** A spec cita caminhos do
  repositório — o rascunho local do assistente, a guarda de configuração de produção, o mecanismo de
  idempotência, a recusa por versão canônica. As citações são **ancoragem de verificação**: cada uma
  sustenta uma afirmação sobre o que já existe, e sem elas o `/plan` reconstruiria premissas que
  esta spec já conferiu — inclusive as quatro premissas falsas que a redação anterior continha. A
  seção `Instruções para o /plan` é técnica por desenho.
- **Redação para público não técnico.** As histórias, os critérios de sucesso e a seção de escopo
  são legíveis por qualquer pessoa da instituição. A seção de requisitos, não inteiramente: ela é o
  contrato com quem implementa.
- **Critérios agnósticos de tecnologia.** `SC-016` nomeia explicitamente Drive, planilha, download
  em lote, banco, shell e API manual. É vocabulário deliberado: é o teste de demonstrabilidade do
  princípio VI da Constituição, e substituí-lo por formulação neutra tiraria o dente do critério.

Três pontos de atenção para o `/plan` e o `/analyze`, registrados aqui para não se perderem:

1. A precondição 2 foi **verificada** contra os artefatos da 008, não presumida: o plano dela
   declara que não toca domínio, snapshot, hash nem migration, e vive em
   `publicacoes/infrastructure/pdf.py` mais dois pontos de chamada. A 008 não incrementa a versão
   canônica; a barreira que resta é o compositor compartilhado.
2. A US1 **não se conclui na entrega 1**: sua parte temporal e o convite por vaga dependem da US2 e
   chegam na entrega 2. A spec declara isso nos dois lugares — na história e na ordem de entrega —
   e a redação anterior, que afirmava independência, foi corrigida.
3. `FR-011` é o requisito com maior chance de ser violado sem que nenhum teste falhe. Merece
   cobertura explícita.

Correções aplicadas nesta revalidação, todas vindas da revisão externa: `FR-053a` (verificar o
resumo, não apenas guardá-lo), `FR-059a` (versão reconhecida pelo rascunho, para o aviso de
Retificação não se repetir), `FR-075a` (nenhuma resposta com dado pessoal armazenada pelo
navegador), `SC-009a` e `SC-014a` correspondentes, mais a correção da US1 e a atualização da
precondição 2 e da premissa sobre a 008.
