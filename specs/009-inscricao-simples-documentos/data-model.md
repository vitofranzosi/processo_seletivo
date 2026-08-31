# Fase 1 — Modelo de dados: Inscrição Simples e Documentos do Candidato

**Feature**: [spec.md](./spec.md) | **Plano**: [plan.md](./plan.md) | **Decisões**: [research.md](./research.md)

## 1. O que **não** muda

Nada do que já é normativo é redesenhado. `PerfilVaga`, `ModalidadeConcorrencia`, `RegraNormativa`,
`Cronograma`, `EtapaAvaliacao`, `SecaoEdital`, `RevisaoEdital`, `Publicacao`, `DocumentoPublicado`,
`VersaoConsolidada`, `Retificacao`, `AlteracaoNormativa` e `RegistroAuditoria` seguem como estão. A
gramática de endereçamento não muda; o cálculo do hash não muda; o mecanismo de consolidação não
muda.

O candidato **não** ganha entidade de cadastro: não há tabela de pessoa, e a identidade é uma
referência a um provedor externo.

## 2. Extensão do domínio existente

### 2.1 `EventoCronograma` — a designação do período

Um campo:

| Campo | Tipo | Regra |
|---|---|---|
| `is_registration_period` | booleano, padrão falso | No máximo **um** verdadeiro por Cronograma |

Invariante persistente: `UniqueConstraint(fields=["cronograma"], condition=Q(is_registration_period=True))`.
Pertencimento é garantido pela estrutura — a marca vive no Evento, que já pertence ao Cronograma.

O período em si continua sendo `start_at` e `end_at` do Evento marcado. **Nenhuma data é copiada**
para lugar nenhum (`FR-003`).

### 2.2 `DocumentoExigido` — o que o Edital exige do candidato

| Campo | Tipo | Regra |
|---|---|---|
| `id` | UUID | Identidade estável desde a elaboração; é o que o conteúdo publicado carrega |
| `edital` | FK `Edital`, protegido | |
| `key` | texto | Único por Edital |
| `name` | texto | Obrigatório |
| `instructions` | texto | Pode ser vazio, nunca nulo |
| `required` | booleano | |
| `order` | inteiro | Único por Edital |
| `perfil` | FK `PerfilVaga`, anulável | Aplicabilidade |
| `modalidade` | FK `ModalidadeConcorrencia`, anulável | Aplicabilidade |

Invariantes: `UniqueConstraint(edital, key)`, `UniqueConstraint(edital, order)`. Quando `modalidade`
está preenchida e `perfil` também, a modalidade **deve** pertencer àquele Perfil — conferido na
gravação do rascunho, junto das demais recusas de identidade alheia que `replace_draft` já faz.

Como todo o rascunho, a coleção é substituída inteira a cada gravação da etapa.

### 2.3 Catálogo de seções

Uma entrada nova, declarada em código, sem migration: `documentos-exigidos`, gerada, com origem na
coleção `documentRequirements`, posicionada logo após a seção textual `inscricao`.

## 3. Entidades novas

### 3.1 `Inscricao`

| Campo | Tipo | Observação |
|---|---|---|
| `id` | UUID | |
| `identity_subject` | texto | Identificador estável do provedor. **Não** é o nome |
| `edital` | FK `Edital`, protegido | |
| `profile_id` | UUID | Do Perfil no conteúdo publicado, não FK — a inscrição referencia o publicado |
| `modality_id` | UUID, anulável | Idem; nulo quando não há escolha aplicável |
| `status` | `RASCUNHO` \| `SUBMETIDA` | Dois, e nada mais |
| `revision` | inteiro grande | Para `compare_and_swap` e para a auditoria |
| `nome`, `cpf`, `cpf_normalizado`, `email`, `telefone` | texto | `telefone` opcional; `cpf_normalizado` só dígitos |
| `versao_reconhecida` | FK `VersaoConsolidada`, anulável, protegido | O que o candidato viu e confirmou |
| `versao_aceita` | FK `VersaoConsolidada`, anulável, protegido | Sob o que ele se inscreveu; gravada uma vez |
| `declaracoes_aceitas_em` | instante, anulável | |
| `submitted_at` | instante, anulável | Imutável depois de gravado |
| `protocolo` | texto, anulável | Único quando presente |
| `created_at` | instante | |

Invariantes persistentes:

- `UniqueConstraint(identity_subject, edital, profile_id)` — **em qualquer estado** (`FR-028`). É a
  mesma restrição que impede rascunho duplicado e envio duplicado.
- `UniqueConstraint(protocolo)`, condicionada a protocolo presente.
- `CheckConstraint`: `SUBMETIDA` implica `submitted_at`, `protocolo`, `versao_aceita` e
  `declaracoes_aceitas_em` presentes.

Imutabilidade: o `save()` recusa alterar `submitted_at`, `protocolo` e `versao_aceita` depois de
gravados, no mesmo padrão de `Publicacao` e `VersaoConsolidada`. O registro inteiro não é imutável —
`revision` avança até o envio.

**Por que `profile_id` e `modality_id` não são chaves estrangeiras**: o candidato se inscreve para o
Perfil **do conteúdo publicado**, cuja identidade é estável e sobrevive a Retificação. Amarrar à
linha de elaboração faria a inscrição depender de um registro que a Retificação pode alterar depois,
e contradiria `FR-011`.

### 3.2 `DocumentoSubmetido`

| Campo | Tipo | Observação |
|---|---|---|
| `id` | UUID | |
| `inscricao` | FK `Inscricao`, cascata | |
| `requirement_id` | UUID | Do Documento Exigido no conteúdo publicado |
| `arquivo` | campo de arquivo, armazenamento privado | Nome físico opaco (D-006) |
| `nome_original` | texto | Metadado exibível, nunca caminho |
| `tamanho` | inteiro | |
| `content_hash` | texto | Resumo do conteúdo recebido |
| `uploaded_at` | instante | |

Invariante persistente: `UniqueConstraint(inscricao, requirement_id)` — um arquivo por requisito
(`FR-043`). Substituir antes do envio é sobrescrever este registro e remover o arquivo anterior do
armazenamento.

Imutabilidade: depois de a Inscrição ficar `SUBMETIDA`, nem o registro nem o arquivo mudam
(`FR-054`).

## 4. Forma publicada — versão canônica 4

Três mudanças, e só estas três:

1. Cada item de `schedule` ganha `isRegistrationPeriod` (booleano, sempre presente).
2. A raiz ganha `documentRequirements`, lista ordenada de objetos:

```json
{
  "id": "uuid",
  "key": "diploma",
  "name": "Diploma de graduação",
  "instructions": "Frente e verso, em arquivo único.",
  "required": true,
  "order": 2,
  "profileId": "uuid | null",
  "modalityId": "uuid | null"
}
```

3. `sections` passa a conter a seção gerada `documentos-exigidos`.

Registro em `publicacoes/domain/colecoes.py`: `/documentRequirements` entra em `COLECOES_COM_CHAVE`.
Nenhum campo novo entra em `CAMPOS_DE_IDENTIDADE` — todos os três são retificáveis.

Declaração de forma em `editais/domain/validation.py`: `DOCUMENTO_EXIGIDO_PUBLICADO`, transcrito do
contrato, mais um `Campo("isRegistrationPeriod", bool)` em `EVENTO_PUBLICADO`.

## 5. Validações de publicação

Duas conferências novas, no formato das existentes:

| Conferência | Severidade | Motivo |
|---|---|---|
| No máximo um Evento marcado como período | Impeditivo | Duas Retificações sucessivas alcançam o estado; a Publicação é onde ele para |
| Documento exigido referencia Perfil e modalidade existentes no próprio conteúdo, e a modalidade pertence ao Perfil quando os dois estão presentes | Impeditivo | Requisito inaplicável nunca seria pedido a ninguém, e a Retificação pode produzi-lo |
| Nenhum Evento marcado | **Aviso** | `FR-004`: o Edital continua publicável; apenas não recebe inscrições |

## 6. Estados e transições

```text
(inexistente) --abrir--> RASCUNHO --enviar--> SUBMETIDA
```

`abrir` acontece quando o candidato identificado chega à tela da inscrição por um Perfil. `enviar`
revalida tudo (`FR-060`), grava versão aceita, declarações, instante e protocolo, e avança
`revision` por `compare_and_swap`. Não há volta, não há cancelamento, não há terceiro estado.

## 7. Aplicabilidade — as quatro combinações

Função pura sobre o conteúdo publicado, sem consulta ao banco:

| `profileId` | `modalityId` | Aplica-se a |
|---|---|---|
| nulo | nulo | Todos |
| preenchido | nulo | Somente aquele Perfil |
| nulo | preenchido | Somente aquela modalidade |
| preenchido | preenchido | Somente a combinação |

Nenhum operador, nenhuma expressão, nenhuma quinta linha.

## 8. Onde cada invariante é verificada

| Regra | Tela | Envio de arquivo | Envio da inscrição | Banco |
|---|:--:|:--:|:--:|:--:|
| Perfil pertence ao Edital publicado | ✓ | — | ✓ | — |
| Modalidade pertence ao Perfil | ✓ | — | ✓ | — |
| Requisito se aplica àquela inscrição | ✓ | ✓ | ✓ | — |
| PDF e limite de 10 MB | — | ✓ | ✓ | — |
| Obrigatório presente | ✓ | — | ✓ | — |
| Período aberto | ✓ | ✓ | ✓ | — |
| Versão vigente reconhecida | ✓ | — | ✓ | — |
| Declarações aceitas | ✓ | — | ✓ | ✓ |
| Um arquivo por requisito | ✓ | ✓ | — | ✓ |
| Uma inscrição por identidade, Edital e Perfil | ✓ | — | ✓ | ✓ |
| Protocolo único | — | — | ✓ | ✓ |
| Titularidade | ✓ | ✓ | ✓ | — |

A coluna "Tela" nunca é fronteira de segurança; ela existe para não oferecer o que será recusado.

## 9. Auditoria

Três atos, pelo mecanismo existente, com o ator externo como autor e o escopo institucional do
Processo alvo:

| Ato | Operação | Estado anterior |
|---|---|---|
| Abrir a inscrição | `CRIAR` | vazio |
| Substituir ou remover arquivo antes do envio | `ANEXAR` / `REMOVER` | `RASCUNHO` |
| Enviar | `SUBMETER` | `RASCUNHO` |

O registro carrega Inscrição, Edital e versão, Perfil e instante. **Não** carrega CPF completo,
nome do arquivo original nem conteúdo. Consulta pública não é auditada.

## 10. Migrations

Duas, ambas de estrutura, sem conversão de dado:

1. `editais`: campo `is_registration_period` com a constraint parcial; tabela `DocumentoExigido`.
2. `inscricoes`: tabelas `Inscricao` e `DocumentoSubmetido`, com as quatro constraints.

Nenhuma migration de dado: o incremento canônico invalida os dados de demonstração publicados, que
são recriados pela seed (D-005).
