# Feature Specification: A Visão do Sistema dentro da gestão

**Feature Branch**: `002-inserir-documentacao-sistema` (PR #329, de Vito Franzosi), revisada e
corrigida em `claude/review-pr-329-fd9f1a`, sobre a `main` em `62824816`

**Created**: 2026-10-22 · **Revisada**: 2026-10-30

**Status**: Implementada; merge **não** autorizado.

**Input**: o pedido da PR #329 — *"Disponibilizar na sidebar de toda identidade autenticada o link
'Documentação do Sistema', que abre o manual existente em docs/visao-sistema/index.html"*, e, *"na
parte inferior da sidebar do manual, o link 'Voltar', com destino ao início da área autenticada"*.

> **Numeração.** A PR abriu a pasta como `099`, número que o relatório do Edital já usava na `main`.
> Renumerada para **`105`**, a seguinte livre na `main` e nos PRs abertos em 30/10/2026.
>
> **Faixa de identificadores.** Esta spec abre em **FR-2901** e **SC-991**. Teto medido em 30/10/2026
> na `main` e nos PRs abertos: `FR-2829`, `SC-990`. Nenhum `UX-` é aberto aqui. As decisões
> reiniciam em `D-001`.

---

## Por que esta feature existe

A [Visão do Sistema](../../docs/visao-sistema/index.html) é o material de uso vigente — tutorial,
papéis, configuração, perguntas frequentes —, mas mora só no repositório. Quem opera a gestão não
tem como chegar a ela de dentro do sistema, e quem não clona o repositório não a lê.

O manual é um HTML estático, mantido por PRs de documentação próprias (a `#341` é uma), e o sistema
responde todo HTML sob a política de conteúdo da `091` e da `092`, que recusa estilo e script
embutidos. Servi-lo pela gestão é, portanto, também um compromisso do manual: ele passa a ter de
caber na política, e a suíte passa a cobrar isso dele.

## User Scenarios & Testing

### User Story 1 — Abrir o manual pela barra (Priority: P1)

Quem está identificado na gestão, com qualquer papel ou só com vínculo, vê na barra lateral o grupo
"Ajuda" com o item "Documentação do Sistema", e ao segui-lo lê o manual inteiro, com estilo, busca,
tema e navegação funcionando.

**Acceptance Scenarios**:

1. **Given** uma identidade sem papel, **When** ela abre a barra, **Then** o item está lá e o
   destino responde 200.
2. **Given** ninguém identificado, **When** se pede `/gestao/documentacao/`, **Then** a resposta é a
   identificação, que devolve ao manual depois.

### User Story 2 — Voltar à gestão (Priority: P1)

Lendo o manual, a pessoa encontra no pé da barra dele o link "Voltar", que leva ao início da gestão.

### Edge Cases

- Um arquivo da pasta que o manual não pede — os registros de mudança, por exemplo — é inexistente.
- Um caminho que tenta sair da pasta (`../`) é inexistente, e não um erro.
- O manual passa a pedir um arquivo novo sem que a lista o tenha: a suíte reprova (SC-991).
- Uma PR de documentação devolve um `<script>` embutido ao manual: a suíte reprova (SC-992).
- Aberto do disco, fora do sistema, o "Voltar" leva à pasta `docs/`: o manual continua legível, e
  o link só tem sentido servido pela gestão.

## Requirements

- **FR-2901**: A barra da gestão MUST oferecer, a toda identidade, o item "Documentação do Sistema",
  num grupo próprio, "Ajuda", depois dos de trabalho e da unidade, com ícone que nenhum outro item
  usa.
- **FR-2902**: `/gestao/documentacao/` MUST servir o `index.html` do manual a toda identidade da
  gestão, e MUST pedir a identificação a quem não a tem, com o manual como destino de volta.
- **FR-2903**: Só os arquivos que o manual referencia MUST ser servidos, por lista literal com o tipo
  de cada um; qualquer outro caminho MUST responder 404.
- **FR-2904**: O manual MUST ser servido sob a política de conteúdo vigente, e por isso MUST NOT
  trazer `<style>`, atributo `style`, `<script>` sem `src`, manipulador `on*` nem endereço `data:`.
- **FR-2905**: O pé da barra do manual MUST ter o link "Voltar", relativo, que leva ao início da
  gestão sob qualquer prefixo.
- **FR-2906**: O manual MUST estar na imagem do container e na montagem do compose de
  desenvolvimento, porque a gestão o lê do disco.

## Success Criteria

- **SC-991**: Todo arquivo que o `index.html` referencia está na lista e responde 200 com o tipo
  declarado — conferido pela suíte contra o arquivo do disco.
- **SC-992**: Nenhum conteúdo embutido no manual — conferido pela suíte contra o arquivo do disco.
- **SC-993**: Caminho fora da lista, inclusive com `..`, responde 404.

## Decisões

### D-001 — Toda identidade da gestão lê o manual

O manual não mostra dado de certame, e é o mesmo arquivo que o repositório traz. Pedir capacidade
deixaria de fora quem só tem vínculo, que é quem mais precisa do tutorial — a razão da Agenda.

### D-002 — Lista literal de arquivos, e não a pasta

A PR servia por `django.views.static.serve` com uma lista; a lista fica, porque a pasta tem os
registros de mudança e o diretório-pai é o repositório inteiro. O custo é acrescentar uma linha
quando o manual pedir arquivo novo, e o guardião de SC-991 diz quando.

### D-003 — Os bytes na resposta, e não um `FileResponse`

O `serve` devolve o arquivo aberto; o teste da barra que confere os destinos lê a resposta sem
consumi-la, e o descritor ficava para o coletor de lixo — oito falhas no CI da PR, todas
`ResourceWarning` promovido a erro. Os arquivos são cinco, o maior com ~1 MB.

### D-004 — O manual abre fora da moldura da gestão

A página é o próprio `index.html`, com a barra dele, e não um quadro dentro da gestão: emoldurar
pediria `frame-src` e dois rolamentos na mesma tela. O caminho de volta é o "Voltar" de FR-2905, e
não a barra da gestão. Por isso o item fica em grupo próprio, separado dos lugares de trabalho.
