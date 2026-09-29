# Contrato — o que o template entrega ao script da etapa Perfis

O script só lê o que está aqui. Mudar um destes pontos no template exige mudar o script, e o
teste `test_visao_dos_perfis.py` prende cada um.

## A etapa (`compor_perfis.html`)

| Elemento | O que é |
|---|---|
| `#visao-dos-perfis` (vazio, `hidden`) | Onde a tabela entra. Logo depois das ajudas da etapa. |
| `[hx-target="#perfis"]` | *Acrescentar Perfil*, logo depois de `#visao-dos-perfis`. |
| `#declarado-uma-vez`, o botão `preencher_quadro` | Entre `#visao-dos-perfis` e `#perfis` (`UX-120`). |
| `#perfis` | A lista dos cartões, como hoje. Só cartões dentro dela. |
| `p.contadores` | O contador de hoje; o script o oculta quando há tabela. |

## O cartão (`_perfil.html`)

| Atributo ou elemento | Valor |
|---|---|
| `fieldset.linha.perfil` | O cartão, como hoje. |
| `id="cartao-<id do Perfil>"` | Âncora estável: não muda quando o servidor renumera os índices. |
| `data-pendencias="N"` | Pendências da etapa com `/profiles/id=<id>` no campo (R-003). `0` quando nenhuma. |
| `data-nao-salvo` (presente ou ausente) | O servidor devolveu este Perfil diferente do gravado (R-004). |
| `<legend>` | `Perfil <código> — <localidade ou denominação>`, ou `Perfil novo` (R-006). |
| `[name$="-code"]`, `-name`, `-locality`, `-immediateVacancies`, `-reserveLimit` | Lidos pelo valor. |
| `[name$="-reserveType"]` (rádio) com `data-resumo` | Frase curta da reserva. |
| `select[name$="-callForm"]` com `data-resumo-<valor>` (`nenhuma` para o vazio) | Frase curta da convocação; no `select`, porque a 051 prende a marcação das opções. |
| `fieldset.modalidade` com `[name$="-code"]` e `[name$="-percentage"]` | As Modalidades da linha. |

## O que o script cria (e nunca com `name`)

- `table` dentro de `div.tabela-rolavel` em `#visao-dos-perfis`, com `caption`, `th[scope=col]`,
  `th[scope=row]` com o código, e um `button[type=button]` *Editar* por linha.
- O cabeçalho do editor, imediatamente antes de `#perfis`: título com `tabindex="-1"` e três
  `button[type=button]` — *Anterior*, *Próximo*, *Voltar à lista*.
- `hidden` nos cartões fora de vista; `aria-current="true"` na linha em edição.
