# Contratos das telas (128)

## A recusa do comando

| Código | Status | Campo | Frase (UX-260) |
|---|---|---|---|
| `ordering_without_stage_results` | 422 | `marco` | *"Nenhuma das N inscrições deste recorte tem resultado na Etapa X. Para emitir a ordem, distribua as inscrições, avalie e consolide os resultados dessa Etapa."* |

Variações: uma inscrição — *"A inscrição deste recorte não tem resultado na Etapa X."*; mais de uma
Etapa — *"…nas Etapas X e Y… dessas Etapas."* (três ou mais: *"X, Y e Z"*).

## Tela da ordem (`interface:ordenacao`), recorte recusado

- A ordem calculada e os sem posição, como antes (FR-4214).
- No lugar do formulário de emissão e do bloco de sucessão (FR-4212), para todos:

  ```text
  <section class="aviso" aria-labelledby="sem-resultado">
    <h2 id="sem-resultado">A ordem ainda não pode ser emitida</h2>
    <p>{frase}</p>
    <ul> <li><a href="{distribuição da Etapa}">Distribuir {Etapa}</a></li> … </ul>   ← só para quem gere (FR-4213)
  </section>
  ```

- Sem o pedido "Emitir a ordem deste marco… peça a alguém que a emita" (FR-4213).
- Vindo de uma recusa do comando com a mesma frase: o erro não é repetido; o bloco recebe
  `role="alert"`, `tabindex="-1"` e `autofocus`.

## Rota da confirmação (`interface:emitir-ordenacao`), recorte recusado

- Sem `confirmar=1`: `302` para a tela do recorte (`?lista=` preservada), com a frase no erro de sessão;
  a confirmação não é renderizada (FR-4215).
- Com `confirmar=1`: o comando recusa; `302` para a tela, com a frase no erro de sessão.

## Conferência do gesto "Ordenar o marco" (`interface:marco`, operação `ordenar`)

- O recorte recusado é `impedido`, com `razao` = a frase (FR-4216, UX-262), e não entra na contagem do
  verbo da confirmação.
- O recorte de universo vazio continua `praticar`, "ninguém concorreu — a ordem vazia é emitida e
  registra isso".
