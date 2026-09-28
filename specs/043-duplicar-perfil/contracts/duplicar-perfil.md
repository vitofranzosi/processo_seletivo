# Contrato: o fragmento que duplica um Perfil

**Feature**: [../spec.md](../spec.md) · **Pesquisa**: [../research.md](../research.md)

Contrato de **interface**, e não de API pública: o fragmento é pedaço da tela de composição, e só a
tela o chama. A API de rascunho não muda.

## Pedido

```text
GET /gestao/fragmentos/perfil/<indice>/duplicar?edital=<uuid>&<campos>
```

- `<indice>` — o índice de tela do Perfil de **origem**; os campos dele são `perfil-<indice>-…`,
  `modalidade-<indice>-…`, `linha-<indice>-…`, `fato-<indice>-…`.
- `edital` — **obrigatório**. Ausente: `404`.
- `<campos>` — trazidos por `hx-include`:
  - o `fieldset` inteiro do Perfil de origem, inclusive `perfil-<indice>-marcosEmTransito` quando
    houver;
  - `perfil-*-code` de **todos** os Perfis da tela, para a conferência de colisão;
  - `duplicar-codigo` e `duplicar-localidade` — os dois campos do diálogo, **fora** do formulário
    da etapa (`R-007`).

## Respostas

| Situação | Status | Corpo |
|---|---|---|
| Sem `edital`, ou Edital fora do escopo do ator | `404` | — |
| Edital alcançável, mas o ator não pode compô-lo (sem `edital:elaborar`, ou Edital fora da elaboração) | `403` | — |
| Código vazio, ou igual ao de outro Perfil da tela | `200` + `HX-Retarget` | o diálogo de volta, com a mensagem **no campo** (`FR-635`). Localidade vazia **não** é recusa |
| Perfil de origem com valor ilegível — número que não é número; `ler_perfis` levanta `ValueError` | `200` + `HX-Retarget` | o diálogo de volta, dizendo que o Perfil de origem tem campo a corrigir antes de duplicar |
| Perfil de origem com erro **de regra** (lido, mas inválido) | `200` | **não é recusa**: a cópia é criada com o erro, e a gravação o recusa como para qualquer Perfil |
| Referência interna sem contraparte (`ReferenciaNaoMapeada`) | `200` + `HX-Retarget` | o diálogo de volta, com mensagem genérica; o detalhe vai para o log com o `correlation_id` — defeito determinável, não dado do usuário |
| Sucesso | `200` | o cartão do Perfil novo (`_perfil.html`), com índice novo |

**Recusa é `200`, e não `422`, por causa do htmx 2.0.4**: a configuração padrão dele **não troca**
resposta 4xx, e a tela ficaria muda — o botão não faria nada, sem mensagem. A recusa volta com
`HX-Retarget` apontando o diálogo e `HX-Reswap: outerHTML`: troca-se **o diálogo**, e nenhum cartão é
inserido. Mudar o `responseHandling` global do htmx para aceitar 422 alteraria o comportamento de
todos os fragmentos da interface, e não é escopo desta feature. `404` e `403` continuam sendo
status de verdade: ali não há o que mostrar a quem não deveria ter chegado.

## O cartão devolvido

- Todos os campos de `_perfil.html`, preenchidos pela transformação de [../data-model.md](../data-model.md).
- `perfil-<novo>-marcosEmTransito`, oculto, quando a cópia leva marcos.
- Uma região `role="status"` com:
  - *"Perfil ⟨código novo⟩ criado a partir de ⟨código da origem⟩."*;
  - quando a cópia leva marcos: *"Leva ⟨n⟩ marco(s) de classificação, que se editam na etapa
    Classificação depois de gravar."* (`FR-650`);
  - quando a origem tem documentos recortados: *"⟨n⟩ documento(s) exigido(s) restrito(s) a
    ⟨código da origem⟩ não foram replicados para este Perfil."* (`FR-645`).
- `autofocus` no primeiro campo editável.

O vocabulário das três frases passa por `tests/test_vocabulario_da_composicao.py`.

## O que o fragmento não faz

- **Não grava.** Nenhuma escrita no banco, nenhuma auditoria, nenhuma mudança de revisão do Edital
  (`FR-638`).
- **Não lê Edital alheio.** A origem gravada, os marcos e os documentos são lidos **dentro** do
  Edital resolvido (`FR-648`).
- **Não cria Documento Exigido** (`FR-645`).

## O botão e o diálogo, no cartão de origem

Só desenhados quando a tela está em modo de composição (`editavel`). Um `<details>` *"Duplicar este
Perfil"*, junto de *"Remover este Perfil"*, com:

- `Código do novo Perfil` e `Localidade do novo Perfil`, com `form="duplicar-<indice>"` — atributo
  que os tira do formulário da etapa (`R-007`);
- um botão `type="button"` com `hx-get` para o contrato acima, `hx-include` como descrito,
  `hx-target="closest fieldset"` e `hx-swap="afterend"`.

Operável por teclado de ponta a ponta: `<details>` abre por Enter/Espaço, os campos e o botão são
focáveis na ordem natural.
