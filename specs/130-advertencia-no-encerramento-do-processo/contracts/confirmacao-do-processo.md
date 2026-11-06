# Contrato: a confirmação de "Encerrar Processo"

Rota existente: `interface:processo-ato` com `acao="encerrar"` (`/gestao/processos/<id>/atos/encerrar`). A
view é `praticar_ato_processo`. Nenhuma rota nova. As outras ações (`ativar`, `cancelar`) não mudam
(FR-4364).

## Quando a advertência é lida

Só com `acao == "encerrar"` **e** a tela oferecendo o Confirmar: sem `impedimento` (permissão e Processo
Ativo) e sem `pendentes` (Editais fora de estado final). Nos outros casos o contexto não traz
`advertencia`, e a tela é a de hoje (FR-4357, D-004).

## GET

| Situação | Status | O que a tela mostra, de cima para baixo |
|---|---|---|
| sem permissão ou Processo fora de Ativo | 200 | o impedimento de hoje; sem bloco |
| algum Edital fora de estado final | 200 | "Este ato será recusado." e a lista de hoje; sem bloco; sem Confirmar |
| confirmável, com providência em aberto | 200 | o bloco (UX-275, e UX-276 se houver convocação aguardando); consequências; formulário com `resumo_das_providencias`; Confirmar |
| confirmável, sem nada em aberto | 200 | a frase da UX-277; consequências; formulário com `resumo_das_providencias`; Confirmar |

### O bloco (UX-275)

```text
<div class="aviso" role="status">
  <p><strong>Em aberto nos Editais deste Processo</strong></p>
  <p>Encerrar o Processo não conclui estas providências, e os Editais dele deixam de aceitar alteração.</p>
  [UX-276] <p>Quem foi convocado e ainda está no prazo não poderá mais apresentar documento nem enviar o Requerimento de Matrícula.</p>
  para cada grupo:
    <h3><a href="detalhe do Edital">N/AAAA</a> — título <span class="situacao s-ESTADO">situação</span></h3>
    <ul class="impedimentos">
      <li>mensagem [<a href="url">rótulo</a> | a quem pedir]</li>
    </ul>
</div>
```

As frases dos itens são as de `pendencias_do_edital.frase(s, "encerrar")` e `_frase_da_099`, idênticas
às da confirmação do Edital. O texto acima é a estrutura; as classes são as que a folha já tem (R-8).

## POST

Campos: `chave_idempotencia` e `motivo` (de hoje), mais `resumo_das_providencias` (novo, oculto).

| Situação no envio | Status | Efeito |
|---|---|---|
| não confirmável (impedimento ou pendentes) | o de hoje | segue ao comando, como hoje; sem releitura |
| confirmável, resumo ausente ou diferente do recalculado | **409** | **não chama o comando**; reapresenta com a lista atual, o resumo novo, a mensagem da UX-279 (com foco) e o motivo enviado; a mesma chave de idempotência (FR-4365, FR-4366) |
| confirmável, resumo igual, motivo vazio | 422 | "Motivo do encerramento é obrigatório."; relê e mostra o bloco (FR-4360) |
| confirmável, resumo igual, comando recusa (revisão, Edital que deixou de ser final…) | o do comando | relê `pendentes`, `impedimento` e, se ainda confirmável, a advertência (FR-4360) |
| confirmável, resumo igual, comando aceita | 302 | ao detalhe do Processo, `?ato=encerrar`, como hoje; nada da advertência é gravado (FR-4363) |

**A ordem**: a renovação é conferida antes do motivo (R-6).

**A janela que fica** (FR-4367): entre a releitura do POST e a trava do comando, uma mudança não é vista.
O contrato não promete o contrário.

### A mensagem da renovação (UX-279)

```text
<p class="aviso" role="status" tabindex="-1" autofocus>As providências em aberto mudaram desde que você abriu esta tela. Confira a lista atual e confirme de novo.</p>
```

Vem antes do bloco. Não usa a classe `erro`: não é falha.

## O que o contrato não toca

`close_process` e as recusas dele; `encerramento.da_confirmacao` e a tela do Edital; `pending_editais`;
o detalhe e a lista de Processos; o "Cancelar Processo".
